"""创作 Crew — 装配逻辑"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class NightshiftCrew:
    """三角色创作团队 + 自动总管"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def screenwriter(self) -> Agent:
        return Agent(config=self.agents_config["screenwriter"])

    @agent
    def visual_consultant(self) -> Agent:
        return Agent(config=self.agents_config["visual_consultant"])

    @agent
    def story_auditor(self) -> Agent:
        return Agent(config=self.agents_config["story_auditor"])

    @task
    def creative_task(self) -> Task:
        return Task(config=self.tasks_config["creative_task"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_llm="openrouter/anthropic/claude-opus-4-6",
            memory=True,
            verbose=True,
        )
