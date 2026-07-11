"""LangChain callback handler for Ainfera audit URLs."""

from __future__ import annotations

from typing import Any

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

_API_BASE = "https://api.ainfera.ai"


def _abs_audit_url(url: str) -> str:
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if url.startswith("/"):
        return f"{_API_BASE}{url}"
    return url


class AinferaCallbackHandler(BaseCallbackHandler):
    """Surface Ainfera audit metadata after each LLM call."""

    def __init__(self) -> None:
        self.last_audit_url: str | None = None
        self.last_model: str | None = None
        self.last_inference_id: str | None = None
        self.last_receipt_id: str | None = None
        self.last_agent_id: str | None = None

    def _record(
        self,
        *,
        audit_url: str | None = None,
        model: str | None = None,
        inference_id: str | None = None,
        receipt_id: str | None = None,
        agent_id: str | None = None,
    ) -> None:
        if audit_url:
            self.last_audit_url = _abs_audit_url(audit_url)
        if model:
            self.last_model = model
        if inference_id:
            self.last_inference_id = inference_id
        if receipt_id:
            self.last_receipt_id = receipt_id
        if agent_id:
            self.last_agent_id = agent_id

    def _from_ainfera_block(self, block: Any) -> None:
        if not isinstance(block, dict):
            return
        self._record(
            audit_url=block.get("audit_verify_url") or block.get("audit_url"),
            inference_id=block.get("inference_id"),
            receipt_id=block.get("receipt_id"),
            agent_id=block.get("agent_id"),
        )

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        llm_output = response.llm_output or {}
        if isinstance(llm_output, dict):
            self._from_ainfera_block(llm_output.get("ainfera"))
            headers = llm_output.get("headers")
            if isinstance(headers, dict):
                self._record(
                    audit_url=headers.get("x-ainfera-audit-url"),
                    inference_id=headers.get("x-ainfera-inference-id"),
                    receipt_id=headers.get("x-ainfera-receipt-id"),
                    agent_id=headers.get("x-ainfera-agent-id"),
                )

        for gen_list in response.generations:
            for gen in gen_list:
                meta = getattr(gen, "message", None)
                if meta is None:
                    continue
                rm = getattr(meta, "response_metadata", None) or {}
                if isinstance(rm, dict):
                    self._from_ainfera_block(rm.get("ainfera"))
                    self._record(
                        audit_url=rm.get("audit_url") or rm.get("audit_verify_url"),
                        model=rm.get("model") or rm.get("model_name"),
                        inference_id=rm.get("inference_id"),
                        receipt_id=rm.get("receipt_id"),
                        agent_id=rm.get("agent_id"),
                    )
