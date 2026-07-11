#!/usr/bin/env bash
# Pure curl — OpenAI-compat shim on api.ainfera.ai (no client library).
#
# Usage:
#   ./curl-example.sh
#   AINFERA_API_KEY=ainfera_... ./curl-example.sh

set -euo pipefail

BASE="${AINFERA_BASE_URL:-https://api.ainfera.ai}"

if [[ -z "${AINFERA_API_KEY:-}" ]]; then
  echo "── 1 · Sign up a fresh Agent (public endpoint) ──"
  HANDLE="openai-compat-$(date +%s)"
  SIGNUP=$(curl -fsS -X POST "$BASE/v1/agents/signup" \
    -H "Content-Type: application/json" \
    -d "{\"agent_handle\":\"$HANDLE\",\"owner_source\":\"anonymous\"}")
  AINFERA_API_KEY=$(echo "$SIGNUP" | python3 -c 'import sys,json; print(json.load(sys.stdin)["api_key"])')
  AGENT_ID=$(echo "$SIGNUP" | python3 -c 'import sys,json; print(json.load(sys.stdin)["agent_id"])')
  echo "  agent_id=$AGENT_ID"
else
  echo "── 1 · Re-using AINFERA_API_KEY from env ──"
  AGENT_ID=""
fi

echo
echo "── 2 · POST /v1/chat/completions ──"
curl -fsS -X POST "$BASE/v1/chat/completions" \
  -H "Authorization: Bearer ${AINFERA_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"model":"ainfera-inference","messages":[{"role":"user","content":"Say hello in one sentence."}]}' \
  | python3 -m json.tool

if [[ -n "${AGENT_ID:-}" ]]; then
  echo
  echo "── 3 · Audit verify ──"
  curl -fsS "$BASE/v1/audit/$AGENT_ID/verify" | python3 -m json.tool
fi
