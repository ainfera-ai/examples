"""SP-9 PR-B · config-resolution + key-validation tests (no live calls).

These tests cover the contract this package exposes:
  - env var resolution (AINFERA_API_KEY + AINFERA_API_URL)
  - default model = `ainfera-inference`
  - fail-CLOSED on missing key
  - fail-CLOSED on non-Ainfera key (defense against accidentally
    using an `sk-*` key here, which would silently bypass the
    Ainfera gateway and the §16 capture).

No actual MAF / OpenAI calls fire — we patch the MAF client
constructors and assert they're invoked with the right Ainfera-
shaped kwargs.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ainfera_maf import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    ainfera_chat_client,
    ainfera_chat_completion_client,
)
from ainfera_maf._client import _resolve_config

# ── _resolve_config (the contract) ────────────────────────────────


def test_resolve_uses_explicit_args_first(monkeypatch: pytest.MonkeyPatch) -> None:
    """Explicit args always win over env vars."""
    monkeypatch.setenv("AINFERA_API_KEY", "ainfera_envkey")
    monkeypatch.setenv("AINFERA_API_URL", "https://env.example/v1")
    cfg = _resolve_config(
        api_key="ainfera_explicit",
        base_url="https://explicit.example/v1",
        model="claude-opus-4-7",
    )
    assert cfg.api_key == "ainfera_explicit"
    assert cfg.base_url == "https://explicit.example/v1"
    assert cfg.model == "claude-opus-4-7"


def test_resolve_falls_back_to_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AINFERA_API_KEY", "ainfera_envkey")
    monkeypatch.setenv("AINFERA_API_URL", "https://env.example/v1")
    cfg = _resolve_config()
    assert cfg.api_key == "ainfera_envkey"
    assert cfg.base_url == "https://env.example/v1"
    assert cfg.model == DEFAULT_MODEL == "ainfera-inference"


def test_resolve_falls_back_to_defaults_for_url_and_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AINFERA_API_KEY", "ainfera_envkey")
    monkeypatch.delenv("AINFERA_API_URL", raising=False)
    cfg = _resolve_config()
    assert cfg.base_url == DEFAULT_BASE_URL == "https://api.ainfera.ai/v1"


def test_resolve_raises_when_key_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail-CLOSED — no silent unauthenticated calls."""
    monkeypatch.delenv("AINFERA_API_KEY", raising=False)
    with pytest.raises(ValueError) as exc_info:
        _resolve_config()
    assert "AINFERA_API_KEY" in str(exc_info.value)


def test_resolve_raises_on_non_ainfera_key_prefix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An `sk-*` key in AINFERA_API_KEY slot would silently bypass
    the Ainfera gateway + the §16 capture. Catch + raise.
    """
    monkeypatch.setenv("AINFERA_API_KEY", "sk-1234567890abcdef")
    with pytest.raises(ValueError) as exc_info:
        _resolve_config()
    assert "ainfera_" in str(exc_info.value)


# ── client construction (patches MAF; no live calls) ──────────────


def test_chat_client_passes_ainfera_kwargs_to_maf(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AINFERA_API_KEY", "ainfera_test")
    fake_client = MagicMock(name="OpenAIChatClient")
    with patch("agent_framework.openai.OpenAIChatClient", return_value=fake_client) as ctor:
        client = ainfera_chat_client()
    assert client is fake_client
    ctor.assert_called_once()
    _, kwargs = ctor.call_args
    assert kwargs["api_key"] == "ainfera_test"
    assert kwargs["base_url"] == DEFAULT_BASE_URL
    assert kwargs["model"] == "ainfera-inference"


def test_chat_completion_client_passes_ainfera_kwargs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AINFERA_API_KEY", "ainfera_test")
    fake = MagicMock(name="OpenAIChatCompletionClient")
    with patch("agent_framework.openai.OpenAIChatCompletionClient", return_value=fake) as ctor:
        client = ainfera_chat_completion_client(model="claude-opus-4-7")
    assert client is fake
    _, kwargs = ctor.call_args
    assert kwargs["api_key"] == "ainfera_test"
    assert kwargs["base_url"] == DEFAULT_BASE_URL
    assert kwargs["model"] == "claude-opus-4-7"


def test_chat_client_forwards_extra_kwargs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Caller-supplied MAF kwargs (timeouts, headers, etc.) should
    pass through verbatim — adapter doesn't drop them.
    """
    monkeypatch.setenv("AINFERA_API_KEY", "ainfera_test")
    with patch("agent_framework.openai.OpenAIChatClient", return_value=MagicMock()) as ctor:
        ainfera_chat_client(timeout=30.0, default_headers={"X-Test": "1"})
    _, kwargs = ctor.call_args
    assert kwargs["timeout"] == 30.0
    assert kwargs["default_headers"] == {"X-Test": "1"}
