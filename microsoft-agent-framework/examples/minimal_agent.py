"""Minimal MAF agent routed through Ainfera.

Run:
    export AINFERA_API_KEY=ainfera_...
    pip install ainfera-microsoft-agent-framework
    python examples/minimal_agent.py
"""

from __future__ import annotations

import asyncio

from agent_framework import ChatAgent

from ainfera_maf import ainfera_chat_client


async def main() -> None:
    agent = ChatAgent(
        chat_client=ainfera_chat_client(model="ainfera-inference"),
        instructions=("You are a helpful assistant. Reply in one concise sentence."),
    )
    result = await agent.run("What's the capital of France?")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
