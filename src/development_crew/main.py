#!/usr/bin/env python
from pathlib import Path

from pydantic import BaseModel

from crewai.flow import Flow, listen, router, start
from crewai.flow.human_feedback import human_feedback

from development_crew.crews.requirements_crew.requirements_crew import RequirementsCrew
from development_crew.crews.design_crew.design_crew import DesignCrew
from development_crew.crews.development_crew.development_crew import DevelopmentCrew
from development_crew.crews.qa_crew.qa_crew import QACrew


class DevTeamState(BaseModel):
    """State shared across all phases of the development workflow."""

    project_name: str = ""
    project_description: str = ""
    requirements: str = ""
    requirements_feedback: str = ""
    technical_design: str = ""
    source_code: str = ""
    test_code: str = ""
    test_report: str = ""
    issues_found: bool = False
    iteration: int = 0
    max_iterations: int = 3


class DevTeamFlow(Flow[DevTeamState]):
    """Development Team Flow — orchestrates the full software development lifecycle."""

    @start()
    def gather_requirements(self):
        print(f"=== Phase 1: Requirements Analysis for {self.state.project_name} ===")

        feedback_section = ""
        if self.state.requirements_feedback:
            feedback_section = (
                f"The user reviewed the previous requirements and provided this feedback. "
                f"Incorporate it into the revised requirements:\n\n{self.state.requirements_feedback}"
            )

        result = (
            RequirementsCrew()
            .crew()
            .kickoff(
                inputs={
                    "project_name": self.state.project_name,
                    "project_description": self.state.project_description,
                    "feedback_section": feedback_section,
                }
            )
        )
        self.state.requirements = result.raw
        print("Requirements analysis complete.")
        print(f"\n{'='*60}")
        print("REQUIREMENTS DRAFT:")
        print(f"{'='*60}")
        print(self.state.requirements)
        print(f"{'='*60}\n")

    @human_feedback(
        message="Review the requirements above. Do they capture what you want to build? "
                "Provide feedback for revision, or say 'approved' to proceed.",
        emit=["requirements_approved", "requirements_needs_revision"],
        default_outcome="requirements_approved",
    )
    @listen(gather_requirements)
    def review_requirements(self):
        return self.state.requirements

    @listen("requirements_approved")
    def design_solution(self):
        print("=== Phase 2: Technical Design ===")
        result = (
            DesignCrew()
            .crew()
            .kickoff(
                inputs={
                    "project_name": self.state.project_name,
                    "requirements": self.state.requirements,
                }
            )
        )
        self.state.technical_design = result.raw
        print("Technical design complete.")

    @listen("requirements_needs_revision")
    def refine_requirements(self):
        print("=== Revising requirements based on your feedback ===")
        self.state.requirements_feedback = self.last_human_feedback.feedback_text
        self.gather_requirements()

    @listen(design_solution)
    def develop_code(self):
        print("=== Phase 3: Development ===")
        result = (
            DevelopmentCrew()
            .crew()
            .kickoff(
                inputs={
                    "project_name": self.state.project_name,
                    "requirements": self.state.requirements,
                    "technical_design": self.state.technical_design,
                }
            )
        )
        self.state.source_code = result.raw
        print("Development complete.")

    @listen(develop_code)
    def quality_assurance(self):
        print("=== Phase 4: QA Testing ===")
        result = (
            QACrew()
            .crew()
            .kickoff(
                inputs={
                    "project_name": self.state.project_name,
                    "requirements": self.state.requirements,
                    "technical_design": self.state.technical_design,
                    "source_code": self.state.source_code,
                }
            )
        )
        self.state.test_report = result.raw
        self.state.iteration += 1
        print("QA testing complete.")

    @router(quality_assurance)
    def check_test_results(self):
        report = self.state.test_report.lower()
        issue_indicators = ["critical", "fail", "error", "bug", "broken"]
        has_issues = any(indicator in report for indicator in issue_indicators)

        if has_issues and self.state.iteration < self.state.max_iterations:
            self.state.issues_found = True
            print(f"=== Issues found. Iteration {self.state.iteration}/{self.state.max_iterations}. Routing back for fixes. ===")
            return "fix_issues"
        print("=== All tests passed or max iterations reached. Project complete! ===")
        return "complete"

    @listen("fix_issues")
    def fix_and_retest(self):
        print(f"=== Fixing issues (iteration {self.state.iteration}) ===")
        result = (
            DevelopmentCrew()
            .crew()
            .kickoff(
                inputs={
                    "project_name": self.state.project_name,
                    "requirements": self.state.requirements,
                    "technical_design": self.state.technical_design,
                }
            )
        )
        self.state.source_code = result.raw

        qa_result = (
            QACrew()
            .crew()
            .kickoff(
                inputs={
                    "project_name": self.state.project_name,
                    "requirements": self.state.requirements,
                    "technical_design": self.state.technical_design,
                    "source_code": self.state.source_code,
                }
            )
        )
        self.state.test_report = qa_result.raw
        self.state.iteration += 1
        print(f"Fix and retest complete (iteration {self.state.iteration}).")

    @listen("complete")
    def save_outputs(self):
        print("=== Saving all outputs ===")
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        (output_dir / "requirements.md").write_text(self.state.requirements)
        (output_dir / "technical_design.md").write_text(self.state.technical_design)
        (output_dir / "source_code.md").write_text(self.state.source_code)
        (output_dir / "test_report.md").write_text(self.state.test_report)

        # Check for additional structured output files generated by crews
        extra_files = ["user_stories.md"]
        saved = []
        for filename in extra_files:
            filepath = output_dir / filename
            if filepath.exists():
                saved.append(filename)

        print(f"All outputs saved to {output_dir}/")
        if saved:
            print(f"Additional files: {', '.join(saved)}")
        print(f"Total iterations: {self.state.iteration}")
        if self.state.issues_found:
            print("Note: Issues were found during QA. Review the test report for details.")


def kickoff():
    dev_flow = DevTeamFlow()
    dev_flow.kickoff(
        inputs={
            "project_name": "My Project",
            "project_description": "A sample project to demonstrate the development team workflow.",
        }
    )


def plot():
    dev_flow = DevTeamFlow()
    dev_flow.plot()


if __name__ == "__main__":
    kickoff()
