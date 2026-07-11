"""Pre-configured MAF chat clients pointed at Ainfera.

The shared family contract (see also `ainfera-pydantic`, `ainfera-langchain`,
`ainfera-crewai`, `ainfera-langgraph` — all standalone adapter repos):

  - Base URL: `AINFERA_API_URL` env var, default `https://api.ainfera.ai/v1`
  - Key: `AINFERA_API_KEY` env var (an `ainfera_*` value)
  - Default model: `ainfera-inference` (the routing-engine alias; exercises
    the moat) — caller can override to any catalog slug from
    `GET /v1/models` (e.g. `claude-opus-4-7`).

The clients are thin wrappers: we construct an `AsyncOpenAI`/`OpenAI`
client with the Ainfera base_url + key and pass it into MAF's
`OpenAIChatClient` (Responses API) or `OpenAIChatCompletionClient`
(Chat Completions API). MAF's client classes accept either an
already-configured `openai` client or the underlying constructor kwargs;
we expose both helpers so the caller picks the surface.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

# Default Ainfera gateway. Override via AINFERA_API_URL env (e.g. staging).
DEFAULT_BASE_URL = "https://api.ainfera.ai/v1"

# Routing-engine canonical alias. The engine picks the right backend per
# request, exercising the routing-decision capture (§16) that compounds
# Ainfera's q_empirical moat data. Override to a specific slug to pin.
DEFAULT_MODEL = "ainfera-inference"


@dataclass(frozen=True)
class AinferaConfig:
    """Resolved configuration for an Ainfera-backed MAF client.

    Returned by `_resolve_config(...)` so callers + tests inspect the
    exact values used. Frozen so the values can't be mutated mid-run.
    """

    api_key: str
    base_url: str
    model: str


def _resolve_config(
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
) -> AinferaConfig:
    """Resolve config from explicit args + env vars + defaults.

    Precedence (per arg): explicit arg > env var > default.

    Raises `ValueError` if no api_key is resolvable — fail-CLOSED, never
    silently fall through to an unauthenticated call.
    """
    resolved_key = api_key or os.environ.get("AINFERA_API_KEY", "")
    if not resolved_key:
        raise ValueError(
            "ainfera_chat_client requires AINFERA_API_KEY (env var) or an "
            "explicit api_key= argument. Get a key at https://app.ainfera.ai/signup; "
            "it starts with `ainfera_`."
        )
    if not resolved_key.startswith("ainfera_"):
        # Defense in depth — sanity-check the prefix. An OpenAI sk-* key
        # in this slot would silently round-trip to OpenAI directly and
        # bypass Ainfera (no audit chain, no §16 row). Catch + raise.
        raise ValueError(
            "AINFERA_API_KEY value does not start with `ainfera_`. "
            "If you intend to call OpenAI directly, use the OpenAI client "
            "directly — this package's contract is Ainfera routing."
        )

    resolved_base = base_url or os.environ.get("AINFERA_API_URL", "") or DEFAULT_BASE_URL
    resolved_model = model or DEFAULT_MODEL

    return AinferaConfig(
        api_key=resolved_key,
        base_url=resolved_base,
        model=resolved_model,
    )


def ainfera_chat_client(
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
    **maf_kwargs: Any,
) -> Any:
    """Return a MAF `OpenAIChatClient` (Responses API) pointed at Ainfera.

    `OpenAIChatClient` is MAF's Responses-API surface — the modern choice
    when the framework supports it. Falls back via the caller's own
    construction if Responses isn't available.

    `maf_kwargs` are forwarded to the MAF constructor for any extra
    options (timeouts, headers, etc.).

    Example:
        from agent_framework import ChatAgent
        from ainfera_maf import ainfera_chat_client

        agent = ChatAgent(
            chat_client=ainfera_chat_client(model="ainfera-inference"),
            instructions="You are helpful.",
        )
        result = await agent.run("Hello!")
    """
    from agent_framework.openai import OpenAIChatClient

    cfg = _resolve_config(api_key=api_key, base_url=base_url, model=model)
    return OpenAIChatClient(
        api_key=cfg.api_key,
        base_url=cfg.base_url,
        model=cfg.model,
        **maf_kwargs,
    )


def ainfera_chat_completion_client(
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
    **maf_kwargs: Any,
) -> Any:
    """Return a MAF `OpenAIChatCompletionClient` (Chat Completions API)
    pointed at Ainfera.

    Use this when you specifically need the Chat Completions API surface
    (e.g. a tool that expects `chat.completions.create(...)` shape on the
    wire). The Responses API helper above is preferred for new code.
    """
    from agent_framework.openai import OpenAIChatCompletionClient

    cfg = _resolve_config(api_key=api_key, base_url=base_url, model=model)
    return OpenAIChatCompletionClient(
        api_key=cfg.api_key,
        base_url=cfg.base_url,
        model=cfg.model,
        **maf_kwargs,
    )
