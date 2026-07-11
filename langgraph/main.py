"""LangGraph + Ainfera — minimal StateGraph; inference via OpenAI-compatible API."""

from __future__ import annotations

import os
from typing import Annotated

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class State(TypedDict):
    messages: Annotated[list, add_messages]


def main() -> None:
    # SP-9 PR-A family-fix · standardized env-var contract across the
    # adapter family: AINFERA_API_KEY + AINFERA_API_URL + AINFERA_MODEL.
    llm = ChatOpenAI(
        model=os.environ.get("AINFERA_MODEL", "ainfera-inference"),
        api_key=os.environ["AINFERA_API_KEY"],
        base_url=os.environ.get("AINFERA_API_URL", "https://api.ainfera.ai/v1"),
    )

    def chat(state: State) -> dict:
        msg = llm.invoke(state["messages"])
        return {"messages": [msg]}

    graph_builder = StateGraph(State)
    graph_builder.add_node("chat", chat)
    graph_builder.add_edge(START, "chat")
    graph_builder.add_edge("chat", END)
    app = graph_builder.compile()

    result = app.invoke(
        {"messages": [HumanMessage(content="Reply with exactly one word: graph")]},
    )
    last = result["messages"][-1]
    print(last.content)
    usage = getattr(last, "usage_metadata", None)
    if usage and isinstance(usage, dict) and usage.get("total_tokens") is not None:
        print(f"\nTokens: {usage['total_tokens']}")
    meta = getattr(last, "response_metadata", None) or {}
    if meta.get("model_name"):
        print(f"Model:  {meta['model_name']}")
    print("Audit:  https://app.ainfera.ai or GET /v1/audit/{agent_id}/verify")


if __name__ == "__main__":
    main()
