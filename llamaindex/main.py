"""LlamaIndex + Ainfera — OpenAI-compat inference (LlamaIndex apps use the same transport)."""

import os

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["AINFERA_API_KEY"],
    base_url="https://api.ainfera.ai/v1",
)

response = client.chat.completions.create(
    model="ainfera-inference",
    messages=[
        {"role": "user", "content": "Reply with exactly one word: index"},
    ],
)

print(response.choices[0].message.content)
print(f"\nModel:  {response.model}")
print(f"Tokens: {response.usage.total_tokens}")
print("Audit:  https://app.ainfera.ai or GET /v1/audit/{agent_id}/verify")
