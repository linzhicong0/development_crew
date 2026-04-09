import os
from typing import Optional, Type

import requests
from pydantic import BaseModel, Field

from crewai.tools import BaseTool


class JiraCreateIssueInput(BaseModel):
    """Input schema for creating a Jira issue."""

    summary: str = Field(
        ..., description="Summary/title of the Jira issue (e.g. the user story title)."
    )
    description: str = Field(
        ...,
        description="Detailed description including user story, acceptance criteria, and any additional context. Use plain text or Jira wiki markup.",
    )
    issue_type: str = Field(
        default="Story",
        description="Jira issue type, e.g. 'Story', 'Task', 'Bug', 'Epic'. Defaults to 'Story'.",
    )
    labels: Optional[str] = Field(
        default=None,
        description="Comma-separated list of labels to apply to the issue.",
    )
    priority: Optional[str] = Field(
        default=None,
        description="Priority name, e.g. 'Highest', 'High', 'Medium', 'Low', 'Lowest'.",
    )
    epic_key: Optional[str] = Field(
        default=None,
        description="Epic issue key to link this issue to, e.g. 'PROJ-1'.",
    )


class JiraGetIssueInput(BaseModel):
    """Input schema for getting a Jira issue."""

    issue_key: str = Field(
        ..., description="The Jira issue key, e.g. 'PROJ-123'."
    )


class JiraSearchIssuesInput(BaseModel):
    """Input schema for searching Jira issues."""

    jql: str = Field(
        ...,
        description="JQL query string, e.g. 'project = PROJ AND type = Story ORDER BY created DESC'.",
    )
    max_results: int = Field(
        default=10,
        description="Maximum number of results to return. Defaults to 10.",
    )


class JiraUpdateIssueInput(BaseModel):
    """Input schema for updating a Jira issue."""

    issue_key: str = Field(
        ..., description="The Jira issue key to update, e.g. 'PROJ-123'."
    )
    summary: Optional[str] = Field(
        default=None, description="New summary/title for the issue."
    )
    description: Optional[str] = Field(
        default=None, description="New description for the issue."
    )
    labels: Optional[str] = Field(
        default=None,
        description="Comma-separated list of labels to set on the issue.",
    )
    priority: Optional[str] = Field(
        default=None,
        description="Priority name, e.g. 'Highest', 'High', 'Medium', 'Low', 'Lowest'.",
    )
    status: Optional[str] = Field(
        default=None,
        description="Target status name to transition the issue to, e.g. 'In Progress', 'Done'.",
    )


def _get_jira_config():
    """Read Jira connection settings from environment variables."""
    url = os.environ.get("JIRA_URL", "").rstrip("/")
    email = os.environ.get("JIRA_EMAIL", "")
    api_token = os.environ.get("JIRA_API_TOKEN", "")
    project_key = os.environ.get("JIRA_PROJECT_KEY", "")
    return url, email, api_token, project_key


def _jira_headers(email: str, api_token: str) -> dict:
    """Return common headers for Jira REST API calls."""
    import base64

    credentials = base64.b64encode(f"{email}:{api_token}".encode()).decode()
    return {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


class JiraCreateIssueTool(BaseTool):
    name: str = "jira_create_issue"
    description: str = (
        "Create a Jira issue (user story, task, bug, or epic). "
        "Use this to create user stories with acceptance criteria in Jira. "
        "The description should include the full user story, acceptance criteria, and any relevant details."
    )
    args_schema: Type[BaseModel] = JiraCreateIssueInput

    def _run(
        self,
        summary: str,
        description: str,
        issue_type: str = "Story",
        labels: Optional[str] = None,
        priority: Optional[str] = None,
        epic_key: Optional[str] = None,
    ) -> str:
        url, email, api_token, project_key = _get_jira_config()

        if not all([url, email, api_token, project_key]):
            return (
                "Error: Jira is not configured. Set JIRA_URL, JIRA_EMAIL, "
                "JIRA_API_TOKEN, and JIRA_PROJECT_KEY environment variables."
            )

        fields = {
            "project": {"key": project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type},
        }

        if labels:
            fields["labels"] = [label.strip() for label in labels.split(",")]

        if priority:
            fields["priority"] = {"name": priority}

        if epic_key:
            # Link to epic via the standard epic link field or the new parent field
            fields["parent"] = {"key": epic_key}

        response = requests.post(
            f"{url}/rest/api/2/issue",
            headers=_jira_headers(email, api_token),
            json={"fields": fields},
            timeout=30,
        )

        if response.status_code == 201:
            data = response.json()
            return (
                f"Created {issue_type} {data['key']}: {summary}\n"
                f"URL: {url}/browse/{data['key']}"
            )

        return f"Error creating Jira issue: {response.status_code} - {response.text}"


class JiraGetIssueTool(BaseTool):
    name: str = "jira_get_issue"
    description: str = (
        "Retrieve details of a Jira issue by its key. "
        "Returns the issue summary, description, status, priority, labels, and other fields."
    )
    args_schema: Type[BaseModel] = JiraGetIssueInput

    def _run(self, issue_key: str) -> str:
        url, email, api_token, _ = _get_jira_config()

        if not all([url, email, api_token]):
            return "Error: Jira is not configured. Set JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN environment variables."

        response = requests.get(
            f"{url}/rest/api/2/issue/{issue_key}",
            headers=_jira_headers(email, api_token),
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            fields = data["fields"]
            return (
                f"Key: {data['key']}\n"
                f"Summary: {fields['summary']}\n"
                f"Type: {fields['issuetype']['name']}\n"
                f"Status: {fields['status']['name']}\n"
                f"Priority: {fields.get('priority', {}).get('name', 'None')}\n"
                f"Labels: {', '.join(fields.get('labels', [])) or 'None'}\n"
                f"Description:\n{fields.get('description', 'No description')}"
            )

        return f"Error getting Jira issue: {response.status_code} - {response.text}"


class JiraSearchIssuesTool(BaseTool):
    name: str = "jira_search_issues"
    description: str = (
        "Search for Jira issues using JQL (Jira Query Language). "
        "Useful for finding existing user stories, checking for duplicates, "
        "or reviewing the current backlog. Example JQL: 'project = PROJ AND type = Story ORDER BY created DESC'"
    )
    args_schema: Type[BaseModel] = JiraSearchIssuesInput

    def _run(self, jql: str, max_results: int = 10) -> str:
        url, email, api_token, _ = _get_jira_config()

        if not all([url, email, api_token]):
            return "Error: Jira is not configured. Set JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN environment variables."

        response = requests.post(
            f"{url}/rest/api/2/search",
            headers=_jira_headers(email, api_token),
            json={"jql": jql, "maxResults": max_results, "fields": ["summary", "status", "priority", "issuetype"]},
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            issues = data.get("issues", [])
            if not issues:
                return "No issues found matching the query."

            results = []
            for issue in issues:
                fields = issue["fields"]
                results.append(
                    f"- {issue['key']}: {fields['summary']} "
                    f"[{fields['issuetype']['name']}] [{fields['status']['name']}]"
                )
            return "\n".join(results)

        return f"Error searching Jira issues: {response.status_code} - {response.text}"


class JiraUpdateIssueTool(BaseTool):
    name: str = "jira_update_issue"
    description: str = (
        "Update an existing Jira issue. Can change summary, description, labels, priority, "
        "or transition the issue to a new status. Only the fields you provide will be changed."
    )
    args_schema: Type[BaseModel] = JiraUpdateIssueInput

    def _run(
        self,
        issue_key: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
    ) -> str:
        url, email, api_token, _ = _get_jira_config()

        if not all([url, email, api_token]):
            return "Error: Jira is not configured. Set JIRA_URL, JIRA_EMAIL, and JIRA_API_TOKEN environment variables."

        headers = _jira_headers(email, api_token)

        # Update fields
        fields = {}
        if summary:
            fields["summary"] = summary
        if description:
            fields["description"] = description
        if labels:
            fields["labels"] = [label.strip() for label in labels.split(",")]
        if priority:
            fields["priority"] = {"name": priority}

        if fields:
            edit_response = requests.put(
                f"{url}/rest/api/2/issue/{issue_key}",
                headers=headers,
                json={"fields": fields},
                timeout=30,
            )
            if edit_response.status_code not in (200, 204):
                return f"Error updating Jira issue: {edit_response.status_code} - {edit_response.text}"

        # Transition status (separate API call)
        if status:
            # Get available transitions
            trans_response = requests.get(
                f"{url}/rest/api/2/issue/{issue_key}/transitions",
                headers=headers,
                timeout=30,
            )
            if trans_response.status_code == 200:
                transitions = trans_response.json().get("transitions", [])
                transition_id = None
                for t in transitions:
                    if t["to"]["name"].lower() == status.lower():
                        transition_id = t["id"]
                        break

                if transition_id:
                    requests.post(
                        f"{url}/rest/api/2/issue/{issue_key}/transitions",
                        headers=headers,
                        json={"transition": {"id": transition_id}},
                        timeout=30,
                    )
                else:
                    available = [t["to"]["name"] for t in transitions]
                    return (
                        f"Updated fields, but could not transition to '{status}'. "
                        f"Available transitions: {', '.join(available) or 'None'}"
                    )

        return f"Updated {issue_key} successfully."
