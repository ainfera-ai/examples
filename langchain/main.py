"""LangChain + Ainfera Routing — inference via the OpenAI-compatible endpoint."""

import os

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from ainfera_callback import AinferaCallbackHandler

handler = AinferaCallbackHandler()
# SP-9 PR-A family-fix · standardized env-var contract across the
# adapter family:
#   AINFERA_API_KEY  — required, starts with `ainfera_`
#   AINFERA_API_URL  — defaults to https://api.ainfera.ai/v1
#   AINFERA_MODEL    — defaults to ainfera-inference (routing-engine alias)
chat = ChatOpenAI(
    model=os.environ.get("AINFERA_MODEL", "ainfera-inference"),
    openai_api_key=os.environ["AINFERA_API_KEY"],
    openai_api_base=os.environ.get("AINFERA_API_URL", "https://api.ainfera.ai/v1"),
    callbacks=[handler],
)

response = chat.invoke([HumanMessage(content="What's 2+2? Reply in one word.")])

print(response.content)

rm = response.response_metadata or {}
ainfera = rm.get("ainfera") if isinstance(rm.get("ainfera"), dict) else {}
audit_url = (
    handler.last_audit_url
    or ainfera.get("audit_verify_url")
    or rm.get("audit_url")
)
if audit_url:
    print(f"\nAudit: {audit_url}")
elif handler.last_agent_id:
    print(
        f"\nAudit: https://api.ainfera.ai/v1/audit/{handler.last_agent_id}/verify"
    )
else:
    print("\nAudit: see your Ainfera dashboard at https://app.ainfera.ai")
