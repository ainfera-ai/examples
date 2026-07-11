"""Minimum viable Ainfera example — pure OpenAI SDK, no other deps."""

import os

from openai import OpenAI

# SP-9 PR-A family-fix · standardized env-var contract across the
# adapter family:
#   AINFERA_API_KEY  — required, starts with `ainfera_`
#   AINFERA_API_URL  — defaults to https://api.ainfera.ai/v1
# Same shape as ainfera-microsoft-agent-framework + ainfera-pydantic +
# ainfera-langchain + ainfera-crewai + ainfera-langgraph.
client = OpenAI(
    api_key=os.environ["AINFERA_API_KEY"],
    base_url=os.environ.get("AINFERA_API_URL", "https://api.ainfera.ai/v1"),
)

# `ainfera-inference` is the routing-engine canonical alias — exercises
# the q_empirical-compounding routing decision per call. Use a specific
# slug (e.g. "claude-opus-4-7") to pin a backend.
response = client.chat.completions.create(
    model=os.environ.get("AINFERA_MODEL", "ainfera-inference"),
    messages=[
        {"role": "user", "content": "Say hello in one sentence."},
    ],
)

print(response.choices[0].message.content)
print(f"\nModel:  {response.model}")
print(f"Tokens: {response.usage.total_tokens}")
print("Audit:  see x-ainfera-audit-url response header, or https://app.ainfera.ai")
