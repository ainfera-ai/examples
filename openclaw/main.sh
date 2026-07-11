#!/usr/bin/env bash
# ainfera-openclaw — point OpenClaw (openclaw) at Ainfera as the
# inference backend. Two config lines, full L1-L4 instrumentation.
#
# Prereqs: openclaw CLI installed + an Ainfera API key.
# Get a key at https://app.ainfera.ai/signup (free $5 launch credit).

set -euo pipefail

: "${AINFERA_API_KEY:?Set AINFERA_API_KEY first (see README)}"

openclaw config inference.backend=ainfera
openclaw config inference.api_key="$AINFERA_API_KEY"
openclaw config inference.default_model=ainfera-inference

# Run a sample OpenClaw skill. Replace with your own.
openclaw skill run "${1:-research-bot}"
