"""ainfera-microsoft-agent-framework — point MAF at Ainfera Routing.

Microsoft Agent Framework (the 2026 merged successor to AutoGen + Semantic
Kernel) ships with `OpenAIChatClient` + `OpenAIChatCompletionClient` that
wrap the underlying `openai` SDK. This package supplies a pre-configured
chat client whose underlying `AsyncOpenAI` instance points at
`api.ainfera.ai/v1` with an `ainfera_*` key, so MAF agents route through
the Ainfera gateway with two env vars instead of bespoke wiring.

## The two env vars

  AINFERA_API_KEY   — your `ainfera_*` key from app.ainfera.ai/signup
  AINFERA_API_URL   — defaults to https://api.ainfera.ai/v1 (override for staging)

## Usage (minimal)

    from agent_framework import ChatAgent
    from ainfera_maf import ainfera_chat_client

    agent = ChatAgent(
        chat_client=ainfera_chat_client(model="ainfera-inference"),
        instructions="You are a helpful assistant.",
    )
    result = await agent.run("Say hello in one sentence.")
    print(result)

The default `model="ainfera-inference"` exercises Ainfera's routing
engine (which picks the right backend per request). Pass a specific
provider slug (`claude-opus-4-7`, `gpt-5-5`, etc.) to pin a model.

## What this adapter does NOT do

- Does NOT bypass the Ainfera gateway. The one-router invariant holds:
  every MAF call goes through `api.ainfera.ai`, gets a signed receipt,
  and lands a row in `routing_outcomes` (§16 capture).
- Does NOT carry payment/billing logic. Per-call cost is metered on
  the Ainfera side via the dormant payment rails (SP-8).
- Does NOT touch Manwë / Modal / fenced surfaces.
"""

from ainfera_maf._client import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    AinferaConfig,
    ainfera_chat_client,
    ainfera_chat_completion_client,
)

__version__ = "0.1.0"

__all__ = [
    "DEFAULT_BASE_URL",
    "DEFAULT_MODEL",
    "AinferaConfig",
    "ainfera_chat_client",
    "ainfera_chat_completion_client",
]
