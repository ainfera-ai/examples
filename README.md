# Ainfera Examples

Consolidated integration examples for the Ainfera inference routing API.

## Integrations

| Example | Framework | Status |
|---|---|---|
| [`openai-compatible/`](./openai-compatible) | OpenAI-compatible API | 🟢 Active |
| [`langchain/`](./langchain) | LangChain | 🟢 Active |
| [`langgraph/`](./langgraph) | LangGraph | 🟢 Active |
| [`crewai/`](./crewai) | CrewAI | 🟢 Active |
| [`google-adk/`](./google-adk) | Google ADK | 🟢 Active |
| [`pydantic-ai/`](./pydantic-ai) | Pydantic AI | 🟢 Active |
| [`microsoft-agent-framework/`](./microsoft-agent-framework) | Microsoft Agent Framework | 🟢 Active |
| [`llamaindex/`](./llamaindex) | LlamaIndex | 🟢 Active |
| [`letta/`](./letta) | Letta | 🟢 Active |
| [`hermes/`](./hermes) | Hermes Agent | 🟢 Active |
| [`openclaw/`](./openclaw) | OpenClaw | 🟢 Active |

## Usage

Each subfolder contains a self-contained example with:
- Pinned dependency versions
- Minimal working example
- Tool calling
- Streaming behavior
- Audit receipt output
- Retry/error handling
- Integration test against the Ainfera API

## Setup

```bash
# Set your Ainfera API key
export AINFERA_API_KEY="your-key-here"

# Navigate to an example
cd langchain

# Install dependencies
pip install -r requirements.txt

# Run the example
python main.py
```

## License

Apache 2.0
