"""《夜班守则》创作 Crew — 装配逻辑"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class NightshiftCrew:
    """三角色创作团队 + 自动总管（hierarchical模式）"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # ── Agents ──────────────────────────────────

    @agent
    def screenwriter(self) -> Agent:
        return Agent(config=self.agents_config["screenwriter"])

    @agent
    def visual_consultant(self) -> Agent:
        return Agent(config=self.agents_config["visual_consultant"])

    @agent
    def story_auditor(self) -> Agent:
        return Agent(config=self.agents_config["story_auditor"])

    # ── Tasks ───────────────────────────────────

    @task
    def game_mechanism_design(self) -> Task:
        return Task(config=self.tasks_config["game_mechanism_design"])

    @task
    def visual_breakdown(self) -> Task:
        return Task(config=self.tasks_config["visual_breakdown"])

    @task
    def story_audit(self) -> Task:
        return Task(config=self.tasks_config["story_audit"])

    @task
    def scene_creation(self) -> Task:
        return Task(config=self.tasks_config["scene_creation"])

    @task
    def worldbuilding_discuss(self) -> Task:
        return Task(config=self.tasks_config["worldbuilding_discuss"])

    # ── Crew ────────────────────────────────────

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
