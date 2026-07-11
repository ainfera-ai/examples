"""ainfera-pydantic — point Pydantic AI at Ainfera Routing.

Pydantic AI's strength is **typed agent outputs** — declare a Pydantic
result_type and the framework guarantees the model's return matches.
Routing that through Ainfera means: typed agent outputs + signed audit
+ per-call cost-plus margin + `routing_outcomes` capture per turn.

## The two env vars

  AINFERA_API_KEY   — your `ainfera_*` key from app.ainfera.ai/signup
  AINFERA_API_URL   — defaults to https://api.ainfera.ai/v1 (override for staging)

## Usage (minimal — typed result)

    from pydantic import BaseModel
    from pydantic_ai import Agent
    from ainfera_pydantic import ainfera_model

    class City(BaseModel):
        name: str
        country: str
        population_millions: float

    agent = Agent(
        model=ainfera_model(),
        result_type=City,
        system_prompt="Extract the city the user asks about.",
    )
    result = await agent.run("Tell me about Singapore.")
    print(result.data)  # City(name='Singapore', country='Singapore', population_millions=5.9)

The default model is `ainfera-inference` — Ainfera's routing engine
picks the right backend per request. Pass `model="claude-opus-4-7"`
(or any catalog slug) to pin a specific one.

## What this adapter does NOT do

- Does NOT bypass the Ainfera gateway. Every Pydantic AI call goes
  through `api.ainfera.ai`, gets a signed receipt, lands a
  `routing_outcomes` row.
- Does NOT touch Manwë / Modal / fenced surfaces.
- Does NOT carry payment logic — billing is on the Ainfera side via
  the dormant payment rails (SP-8).
"""

from ainfera_pydantic._model import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    AinferaConfig,
    ainfera_model,
    ainfera_provider,
)

__version__ = "0.1.0"

__all__ = [
    "DEFAULT_BASE_URL",
    "DEFAULT_MODEL",
    "AinferaConfig",
    "ainfera_model",
    "ainfera_provider",
]
