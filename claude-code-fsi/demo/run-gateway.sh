#!/bin/bash
# LLM Gateway on the host, bound to the docker bridge only. Holds the AWS role; developers never do.
set -euo pipefail
cd "$(dirname "$0")/gateway"
mkdir -p logs
exec env AWS_PROFILE=${AWS_PROFILE:-samples-atomoh} GW_BIND=172.17.0.1 python3 gateway.py
