"""Google ADK + Ainfera — LlmAgent driven by InMemoryRunner.

ADK's `LlmAgent` is the unit of configuration; `Runner` is what
actually executes a turn. The model is wrapped in `LiteLlm` so the
under-the-hood OpenAI-compat call lands on Ainfera at
`https://api.ainfera.ai/v1/chat/completions` (shipped api#54).
"""

import asyncio
import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from google.genai import types

APP_NAME = "ainfera-adk-smoke"
USER_ID = "smoke"

model = LiteLlm(
    model="openai/ainfera-inference",
    api_key=os.environ["AINFERA_API_KEY"],
    api_base="https://api.ainfera.ai/v1",
)

agent = LlmAgent(
    name="research_assistant",
    model=model,
    instruction="You are a research assistant. Be brief and cite sources.",
)


async def main() -> None:
    runner = InMemoryRunner(agent=agent, app_name=APP_NAME)
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )
    prompt = "What is the EU AI Act enforcement date for general-purpose AI models?"
    content = types.Content(
        role="user", parts=[types.Part.from_text(text=prompt)]
    )
    async for event in runner.run_async(
        user_id=USER_ID, session_id=session.id, new_message=content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="")
    print()
    print(
        "\nAudit chain: https://app.ainfera.ai "
        "(this run is signed and hash-chained)"
    )


if __name__ == "__main__":
    asyncio.run(main())
