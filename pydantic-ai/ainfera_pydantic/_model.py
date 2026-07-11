"""Pre-configured Pydantic AI Model + Provider pointed at Ainfera.

The construction shape (verified against the current Pydantic AI docs):

    from pydantic_ai.providers.openai import OpenAIProvider
    from pydantic_ai.models.openai import OpenAIChatModel

    provider = OpenAIProvider(base_url=..., api_key=...)
    model = OpenAIChatModel("ainfera-inference", provider=provider)
    agent = Agent(model=model, ...)

This module's `ainfera_model(...)` / `ainfera_provider(...)` build
the same shape with Ainfera's defaults — `AINFERA_API_URL` + an
`ainfera_*` key + the routing-engine canonical model. Shares the
family contract with `ainfera-microsoft-agent-framework`,
`ainfera-langchain`, `ainfera-crewai`, etc.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

DEFAULT_BASE_URL = "https://api.ainfera.ai/v1"
DEFAULT_MODEL = "ainfera-inference"


@dataclass(frozen=True)
class AinferaConfig:
    """Resolved configuration for an Ainfera-backed Pydantic AI model.

    Returned alongside the constructed objects so callers + tests can
    introspect the exact values used.
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

    Precedence per arg: explicit > env var > default.

    Fail-CLOSED on missing key; fail-CLOSED on a non-`ainfera_*`
    prefix (defense against an `sk-*` key silently bypassing the
    Ainfera gateway + the §16 capture). AIN-368 P3: only `ainfera_*` is
    accepted; the legacy `ai_infera_*` prefix is now rejected.
    """
    resolved_key = api_key or os.environ.get("AINFERA_API_KEY", "")
    if not resolved_key:
        raise ValueError(
            "ainfera_model requires AINFERA_API_KEY (env var) or an "
            "explicit api_key= argument. Get a key at "
            "https://app.ainfera.ai/signup; it starts with `ainfera_`."
        )
    if not resolved_key.startswith("ainfera_"):
        raise ValueError(
            "AINFERA_API_KEY value does not start with `ainfera_`. "
            "If you intend to call OpenAI directly, use Pydantic AI's "
            "OpenAIProvider with the OpenAI key directly — this package's "
            "contract is Ainfera routing (which would silently get "
            "bypassed by an sk-* key here)."
        )

    resolved_base = base_url or os.environ.get("AINFERA_API_URL", "") or DEFAULT_BASE_URL
    resolved_model = model or DEFAULT_MODEL

    return AinferaConfig(
        api_key=resolved_key,
        base_url=resolved_base,
        model=resolved_model,
    )


def ainfera_provider(
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    **provider_kwargs: Any,
) -> Any:
    """Return a Pydantic AI `OpenAIProvider` configured for Ainfera.

    Use this when you want to construct the `OpenAIChatModel` yourself
    (e.g. to pass extra Pydantic AI model kwargs). Most callers want
    `ainfera_model(...)` instead, which wires Model + Provider in one
    call.
    """
    from pydantic_ai.providers.openai import OpenAIProvider

    cfg = _resolve_config(api_key=api_key, base_url=base_url)
    return OpenAIProvider(
        base_url=cfg.base_url,
        api_key=cfg.api_key,
        **provider_kwargs,
    )


def ainfera_model(
    *,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    **model_kwargs: Any,
) -> Any:
    """Return a Pydantic AI `OpenAIChatModel` pointed at Ainfera.

    The returned object is what you pass to `Agent(model=...)`. The
    Provider underneath carries the Ainfera base_url + key; the Model
    name defaults to `ainfera-inference` (the routing-engine alias).

    Example:
        from pydantic import BaseModel
        from pydantic_ai import Agent
        from ainfera_pydantic import ainfera_model

        class City(BaseModel):
            name: str
            country: str

        agent = Agent(model=ainfera_model(), result_type=City)
        result = await agent.run("Tell me about Singapore.")
        print(result.data.name)  # "Singapore"
    """
    from pydantic_ai.models.openai import OpenAIChatModel

    cfg = _resolve_config(api_key=api_key, base_url=base_url, model=model)
    provider = ainfera_provider(api_key=cfg.api_key, base_url=cfg.base_url)
    return OpenAIChatModel(cfg.model, provider=provider, **model_kwargs)
