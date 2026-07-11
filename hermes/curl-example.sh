#!/usr/bin/env bash
# ainfera-hermes — minimal curl-only flow, no hermes-agent install needed.
#
# Shows what hermes-agent does under the hood when pointed at Ainfera:
# sign up an Agent → run a signed Inference via the OpenAI-compat shim
# → verify the audit chain.
#
# Endpoints used here mirror the production /v1/* surface as of api#54
# (OpenAI-compat shim shipped 2026-05-19):
#   - POST /v1/agents/signup       (public — no api_key needed)
#   - POST /v1/chat/completions    (OpenAI-compat shim)
#   - GET  /v1/audit/{agent_id}/verify

set -euo pipefail

BASE="${AINFERA_BASE_URL:-https://api.ainfera.ai}"

if [[ -z "${AINFERA_API_KEY:-}" ]]; then
  echo "── 1 · Sign up a fresh Agent (public endpoint, returns one-time key) ──"
  HANDLE="my-hermes-agent-$(date +%s)"
  SIGNUP=$(curl -fsS -X POST "$BASE/v1/agents/signup" \
    -H "Content-Type: application/json" \
    -d "{\"agent_handle\":\"$HANDLE\",\"owner_source\":\"anonymous\"}")
  AINFERA_API_KEY=$(echo "$SIGNUP" | python3 -c 'import sys,json; print(json.load(sys.stdin)["api_key"])')
  AGENT_ID=$(echo "$SIGNUP" | python3 -c 'import sys,json; print(json.load(sys.stdin)["agent_id"])')
  echo "  agent_id=$AGENT_ID  api_key=ainfera_… (save it — shown once)"
else
  echo "── 1 · Re-using AINFERA_API_KEY from env (skipping signup) ──"
  AGENT_ID=""
fi

echo
echo "── 2 · Run a signed Inference via the OpenAI-compat shim ──"
curl -fsS -X POST "$BASE/v1/chat/completions" \
  -H "Authorization: Bearer $AINFERA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"ainfera-inference","messages":[{"role":"user","content":"Plan a 3-day trip to Lisbon in under 80 words."}]}' \
  | python3 -m json.tool

if [[ -n "$AGENT_ID" ]]; then
  echo
  echo "── 3 · Verify the audit chain for this agent (public, no auth) ──"
  curl -fsS "$BASE/v1/audit/$AGENT_ID/verify" | python3 -m json.tool
fi
