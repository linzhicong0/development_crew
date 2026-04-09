from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool


@CrewBase
class DesignCrew:
    """Technical design crew with Technical Lead."""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def technical_lead(self) -> Agent:
        return Agent(
            config=self.agents_config["technical_lead"],
            tools=[SerperDevTool()],
        )

    @task
    def technical_design_task(self) -> Task:
        return Task(
            config=self.tasks_config["technical_design_task"],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
