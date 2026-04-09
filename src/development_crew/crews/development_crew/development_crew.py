from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class DevelopmentCrew:
    """Development crew with a single Developer agent."""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def developer(self) -> Agent:
        return Agent(
            config=self.agents_config["developer"],
        )

    @task
    def development_task(self) -> Task:
        return Task(
            config=self.tasks_config["development_task"],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
