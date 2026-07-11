#!/usr/bin/env bash
# ainfera-hermes — point hermes-agent at Ainfera in 2 env vars.
#
# Prereqs: hermes-agent (NousResearch) installed locally + an Ainfera API key.
# Get a key at https://app.ainfera.ai/signup (free $5 launch credit).

set -euo pipefail

: "${AINFERA_API_KEY:?Set AINFERA_API_KEY first (see README)}"

# Hermes reads CUSTOM_BASE_URL for the custom provider — NOT OPENAI_BASE_URL /
# HERMES_*; the wrong var silently falls back to the default provider and sends
# your key to the wrong endpoint.
export CUSTOM_BASE_URL="https://api.ainfera.ai/v1"
export OPENAI_API_KEY="$AINFERA_API_KEY"   # auth fallback for the custom endpoint

# Always send the canonical wire string; routing selects the model.
hermes chat --provider custom --model ainfera-inference \
  -q "${1:-Plan a 3-day trip to Lisbon in under 80 words.}"
