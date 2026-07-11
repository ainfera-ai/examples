"""SP-9 PR-C · config-resolution + Pydantic AI wiring tests (no live calls).

Same shape as `ainfera-microsoft-agent-framework`'s test_client_config:
proves the family contract holds (env > default, fail-CLOSED on
missing/non-ainfera key) + the Pydantic AI Provider + Model wire-up
gets the right kwargs.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ainfera_pydantic import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    ainfera_model,
    ainfera_provider,
)
from ainfera_pydantic._model import _resolve_config

# ── _resolve_config (the family contract) ────────────────────────


def test_resolve_uses_explicit_args_first(monkeypatch: pytest.MonkeyPatch) -> None:
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


def test_resolve_falls_back_to_env_then_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AINFERA_API_KEY", "ainfera_envkey")
    monkeypatch.delenv("AINFERA_API_URL", raising=False)
    cfg = _resolve_config()
    assert cfg.api_key == "ainfera_envkey"
    assert cfg.base_url == DEFAULT_BASE_URL == "https://api.ainfera.ai/v1"
    assert cfg.model == DEFAULT_MODEL == "ainfera-inference"


def test_resolve_raises_on_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AINFERA_API_KEY", raising=False)
    with pytest.raises(ValueError) as exc_info:
        _resolve_config()
    assert "AINFERA_API_KEY" in str(exc_info.value)


def test_resolve_raises_on_non_ainfera_key_prefix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Defense against an sk-* slipping in and bypassing the gateway."""
    monkeypatch.setenv("AINFERA_API_KEY", "sk-1234567890abcdef")
    with pytest.raises(ValueError) as exc_info:
        _resolve_config()
    assert "ainfera_" in str(exc_info.value)


def test_resolve_rejects_legacy_ai_infera_prefix_after_legacy_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AIN-368 P3 (legacy-off): the legacy `ai_infera_*` prefix is no longer
    accepted — the fleet was re-minted to `ainfera_*`."""
    monkeypatch.setenv("AINFERA_API_KEY", "ai_infera_legacy_key")
    with pytest.raises(ValueError) as exc_info:
        _resolve_config()
    assert "ainfera_" in str(exc_info.value)


# ── Pydantic AI wiring (mocked; no live calls) ───────────────────


def test_ainfera_provider_passes_base_url_and_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AINFERA_API_KEY", "ainfera_test")
    fake_provider = MagicMock(name="OpenAIProvider")
    with patch("pydantic_ai.providers.openai.OpenAIProvider", return_value=fake_provider) as ctor:
        provider = ainfera_provider()
    assert provider is fake_provider
    _, kwargs = ctor.call_args
    assert kwargs["base_url"] == DEFAULT_BASE_URL
    assert kwargs["api_key"] == "ainfera_test"


def test_ainfera_model_wires_provider_into_chat_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AINFERA_API_KEY", "ainfera_test")
    fake_provider = MagicMock(name="OpenAIProvider")
    fake_model = MagicMock(name="OpenAIChatModel")
    with (
        patch("pydantic_ai.providers.openai.OpenAIProvider", return_value=fake_provider),
        patch("pydantic_ai.models.openai.OpenAIChatModel", return_value=fake_model) as model_ctor,
    ):
        model = ainfera_model()
    assert model is fake_model
    args, kwargs = model_ctor.call_args
    assert args[0] == "ainfera-inference"  # the default routing-engine alias
    assert kwargs["provider"] is fake_provider


def test_ainfera_model_uses_explicit_model_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AINFERA_API_KEY", "ainfera_test")
    with (
        patch("pydantic_ai.providers.openai.OpenAIProvider", return_value=MagicMock()),
        patch("pydantic_ai.models.openai.OpenAIChatModel", return_value=MagicMock()) as model_ctor,
    ):
        ainfera_model(model="claude-opus-4-7")
    args, _ = model_ctor.call_args
    assert args[0] == "claude-opus-4-7"


def test_ainfera_model_forwards_extra_kwargs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Caller-supplied Pydantic AI model kwargs pass through verbatim."""
    monkeypatch.setenv("AINFERA_API_KEY", "ainfera_test")
    with (
        patch("pydantic_ai.providers.openai.OpenAIProvider", return_value=MagicMock()),
        patch("pydantic_ai.models.openai.OpenAIChatModel", return_value=MagicMock()) as model_ctor,
    ):
        ainfera_model(settings={"temperature": 0.0})
    _, kwargs = model_ctor.call_args
    assert kwargs.get("settings") == {"temperature": 0.0}
