#!/bin/bash
# PostToolUse hook (SENSORS): run the test suite after every edit.
# Failure -> exit 2, stderr goes back to Claude so it fixes the code. Success -> message to the developer.
cd "$CLAUDE_PROJECT_DIR" || exit 0
out=$(python3 -m pytest -q 2>&1)
if [ $? -ne 0 ]; then
  { echo "[SENSORS] pytest 실패, 고친 뒤 다시 확인하세요:"; echo "$out" | grep -E "FAILED|assert|passed|failed" | tail -8; } >&2
  exit 2
fi
printf '{"systemMessage": "[SENSORS] pytest 통과: %s"}\n' "$(echo "$out" | tail -1)"
