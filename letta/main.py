"""Letta + Ainfera — OpenAI-compat inference layer (what Letta routes under the hood)."""

import os

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["AINFERA_API_KEY"],
    base_url="https://api.ainfera.ai/v1",
)

response = client.chat.completions.create(
    model="ainfera-inference",
    messages=[
        {"role": "user", "content": "Reply with exactly one word: memory"},
    ],
)

print(response.choices[0].message.content)
print(f"\nModel:  {response.model}")
print(f"Tokens: {response.usage.total_tokens}")
print("Audit:  https://app.ainfera.ai or GET /v1/audit/{agent_id}/verify")
