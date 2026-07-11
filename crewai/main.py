"""CrewAI + Ainfera — researcher + writer crew, all calls auditable."""

import os

from crewai import LLM, Agent, Crew, Task

# SP-9 PR-A family-fix · standardized env-var contract across the
# adapter family: AINFERA_API_KEY + AINFERA_API_URL + AINFERA_MODEL.
# CrewAI's LLM expects an `openai/<slug>` prefix; we prepend it when
# the env var doesn't already carry one so callers can pass plain
# `ainfera-inference` without the litellm-style prefix.
_raw_model = os.environ.get("AINFERA_MODEL", "ainfera-inference")
_model = _raw_model if "/" in _raw_model else f"openai/{_raw_model}"
llm = LLM(
    model=_model,
    api_key=os.environ["AINFERA_API_KEY"],
    base_url=os.environ.get("AINFERA_API_URL", "https://api.ainfera.ai/v1"),
)

researcher = Agent(
    role="Researcher",
    goal="Find three short, surprising facts on a topic",
    backstory="You are a precise, fact-driven researcher who cites sources.",
    llm=llm,
)

writer = Agent(
    role="Writer",
    goal="Compress facts into a haiku",
    backstory="You write spare, evocative verse.",
    llm=llm,
)

research_task = Task(
    description="Find three short, surprising facts about Indonesian coffee.",
    agent=researcher,
    expected_output="Three bullet points.",
)

haiku_task = Task(
    description="Turn those three facts into a single haiku (5-7-5).",
    agent=writer,
    expected_output="A haiku.",
)

crew = Crew(agents=[researcher, writer], tasks=[research_task, haiku_task])
result = crew.kickoff()

print(result)
print("\nAudit chain: https://app.ainfera.ai (every call from this run is signed and hash-chained)")
