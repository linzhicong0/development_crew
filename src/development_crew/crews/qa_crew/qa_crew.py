from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class QACrew:
    """QA crew with Test Writer and Test Runner."""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def qa_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["qa_writer"],
        )

    @agent
    def qa_runner(self) -> Agent:
        return Agent(
            config=self.agents_config["qa_runner"],
        )

    @task
    def test_writing_task(self) -> Task:
        return Task(
            config=self.tasks_config["test_writing_task"],
        )

    @task
    def test_execution_task(self) -> Task:
        return Task(
            config=self.tasks_config["test_execution_task"],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
