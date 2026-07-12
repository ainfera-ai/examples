# ainfera-openai-compatible — OpenAI SDK + Ainfera Routing

**OpenAI-compatible chat-completions endpoint + Ainfera Routing.** Works with any client that speaks OpenAI's API — 2 env vars.

## Two env-var change

```bash
# Before
export OPENAI_API_KEY=sk-...
export OPENAI_BASE_URL=https://api.openai.com/v1

# After
export OPENAI_API_KEY=ainfera_...                  # Ainfera key
export OPENAI_BASE_URL=https://api.ainfera.ai/v1   # Ainfera endpoint
```

Your existing code keeps working. You now have:

- One Agent Card across providers (L1)
- Routed inference with per-call budget caps (L3)
- Hash-chained audit per call (L4)
- 200+ models via one key — Claude Opus 4.7 · GPT-5.5 · Gemini 3.1 Pro · Grok 4 · Mistral Large 3 and more (see `GET /v1/models`)
- Quality scored by [Artificial Analysis](https://artificialanalysis.ai) per call

> EU AI Act Annex IV ready — every call hash-chained, signed, exportable.

## Quickstart

```bash
git clone https://github.com/ainfera-ai/ainfera-openai-compatible
cd ainfera-openai-compatible
pip install -r requirements.txt
export AINFERA_API_KEY=ainfera_...  # https://app.ainfera.ai/signup
python main.py
```

Or with `curl` only — no Python client needed:

```bash
AINFERA_API_KEY=ainfera_... ./curl-example.sh
```

## What this proves

Ainfera works with **any** client that speaks OpenAI's API:

- LangChain → [ainfera-langchain](https://github.com/ainfera-ai/ainfera-langchain)
- CrewAI → [ainfera-crewai](https://github.com/ainfera-ai/ainfera-crewai)
- Google ADK → [ainfera-google-adk](https://github.com/ainfera-ai/ainfera-google-adk)
- AutoGen, LlamaIndex, Haystack — same pattern
- Your own custom client — same pattern
- `curl` — same pattern (see `curl-example.sh`)

## OpenAI API surface coverage

The wedge proxies the **chat completions** surface — the high-value
path for agent frameworks. Other OpenAI surfaces are not exposed by
the shim; integrators needing them should call Ainfera's native
endpoints (`/v1/inference`, `/v1/audit`, etc.) directly.

| Surface | Status | Notes |
| --- | --- | --- |
| `POST /v1/chat/completions` | ✅ Supported | The chat-completions path. Strings + text content blocks. |
| `model`, `messages`, `max_tokens`, `temperature` | ✅ Supported | Proxied to `/v1/inference`. |
| `top_p`, `n`, `presence_penalty`, `frequency_penalty`, `user` | ⚠️ Accepted, ignored | Field parsed so SDKs don't 422; Ainfera's L2 router decides routing. |
| `Idempotency-Key` header | ✅ Supported | Pass-through to `/v1/inference`. |
| `x-ainfera-audit-url` response header | ✅ Supported | Pointer to `/v1/audit/{inference_id}` for hash-chain verification. |
| `stream=true` (SSE) | ❌ 501 | `streaming_not_supported`. Same on `/v1/inference` today. |
| `tools` / function calling | ❌ 422 | `tool_calling_not_supported_on_shim`. Use `/v1/inference` directly for `tool_use`. |
| Vision (`image_url` blocks) | ❌ 422 | Flatten to text or use `/v1/inference`. |
| Structured Outputs (`response_format`) | ⚠️ Accepted, ignored | Pydantic accepts the field; not currently translated. |
| Assistants API | — Not exposed | Use Ainfera-native agent endpoints. |
| Batch API | — Not exposed | — |
| Audio (Whisper / TTS) | — Not exposed | — |
| Embeddings | — Not exposed | — |
| Files API | — Not exposed | — |
| Images (DALL-E) | — Not exposed | — |
| Moderation | — Not exposed | — |
| Fine-tuning | — Not exposed | — |

Errors above return OpenAI-shape JSON so existing SDK error handlers
work unchanged. The table above is the canonical translation reference;
see the API reference at [api.ainfera.ai](https://api.ainfera.ai) for full
request/response details.

## MCP clients

If you want to call Ainfera from Claude Desktop or Cursor directly, see
[ainfera-mcp](https://github.com/ainfera-ai/ainfera-mcp).

Apache 2.0. © Ainfera Inc. 2026.
