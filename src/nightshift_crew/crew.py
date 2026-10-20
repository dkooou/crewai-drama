"""Dream Team Crew — 13 specialized agents for AI short drama production."""

import os

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import TavilySearchTool

from nightshift_crew.tools.tikhub_tool import TikHubSearchTool


@CrewBase
class NightshiftCrew:
    """13-agent dream team + auto-manager."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # ── Tier 1: Story Core ──────────────────────────────

    @agent
    def story_architect(self) -> Agent:
        return Agent(config=self.agents_config["story_architect"])

    @agent
    def scene_writer(self) -> Agent:
        return Agent(config=self.agents_config["scene_writer"])

    # ── Tier 2: Pacing & Emotion ────────────────────────

    @agent
    def hook_engineer(self) -> Agent:
        return Agent(config=self.agents_config["hook_engineer"])

    @agent
    def sound_architect(self) -> Agent:
        return Agent(config=self.agents_config["sound_architect"])

    # ── Tier 3: Visual Pipeline ─────────────────────────

    @agent
    def visual_director(self) -> Agent:
        return Agent(config=self.agents_config["visual_director"])

    @agent
    def storyboard_master(self) -> Agent:
        return Agent(config=self.agents_config["storyboard_master"])

    @agent
    def prompt_alchemist(self) -> Agent:
        return Agent(config=self.agents_config["prompt_alchemist"])

    # ── Tier 4: Quality Control ─────────────────────────

    @agent
    def audience_gut_check(self) -> Agent:
        return Agent(config=self.agents_config["audience_gut_check"])

    @agent
    def logic_auditor(self) -> Agent:
        return Agent(config=self.agents_config["logic_auditor"])

    @agent
    def cultural_bridge(self) -> Agent:
        return Agent(config=self.agents_config["cultural_bridge"])

    # ── Tier 5: Operations ──────────────────────────────

    @agent
    def viral_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config["viral_strategist"],
            tools=[TavilySearchTool()],
        )

    # ── Tier 6: Intelligence ────────────────────────────

    @agent
    def creative_intel(self) -> Agent:
        return Agent(
            config=self.agents_config["creative_intel"],
            tools=[TavilySearchTool(), TikHubSearchTool()],
        )

    # ── Task ────────────────────────────────────────────

    @task
    def creative_task(self) -> Task:
        return Task(config=self.tasks_config["creative_task"])

    # ── Crew Assembly ───────────────────────────────────

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_llm="openrouter/anthropic/claude-opus-4-6",
            memory=True,
            embedder={
                "provider": "huggingface",
                "config": {
                    "model": "sentence-transformers/all-MiniLM-L6-v2",
                    "api_url": "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2",
                    "api_key": os.getenv("CHROMA_HUGGINGFACE_API_KEY", ""),
                },
            },
            verbose=True,
        )
