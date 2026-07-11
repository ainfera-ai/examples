"""Minimal Pydantic AI agent with a typed result, routed through Ainfera.

Run:
    export AINFERA_API_KEY=ainfera_...
    pip install ainfera-pydantic
    python examples/typed_city.py
"""

from __future__ import annotations

import asyncio

from pydantic import BaseModel
from pydantic_ai import Agent

from ainfera_pydantic import ainfera_model


class City(BaseModel):
    """Typed result — Pydantic AI guarantees this shape."""

    name: str
    country: str
    population_millions: float


async def main() -> None:
    agent = Agent(
        model=ainfera_model(),  # default → "ainfera-inference"
        result_type=City,
        system_prompt=(
            "Extract the city the user asks about. Reply only with the "
            "typed JSON; do not include any prose."
        ),
    )
    result = await agent.run("Tell me about Singapore.")
    print(result.data)


if __name__ == "__main__":
    asyncio.run(main())
