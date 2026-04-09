from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class RequirementsCrew:
    """Requirements analysis crew with Product Manager and Business Analyst."""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def product_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["product_manager"],
        )

    @agent
    def business_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["business_analyst"],
        )

    @task
    def product_definition_task(self) -> Task:
        return Task(
            config=self.tasks_config["product_definition_task"],
        )

    @task
    def requirements_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["requirements_analysis_task"],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
