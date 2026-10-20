#!/bin/bash
# Developer PC stand-in: a container with Claude Code and NO AWS credentials.
# It reaches only the LLM Gateway on the docker bridge (172.17.0.1:8787). No published ports.
set -euo pipefail
cd "$(dirname "$0")"
docker rm -f ccfsi >/dev/null 2>&1 || true
docker run -d --name ccfsi --hostname 5ho-pc \
  -v "$PWD/scenarios:/opt/scenarios:ro" ccfsi-demo sleep infinity >/dev/null
echo "container ccfsi started (no AWS credentials inside)"
