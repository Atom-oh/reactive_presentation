#!/bin/bash
# Drives the tmux session inside the container: types like a developer, waits for Claude Code to finish.
T() { docker exec -u dev01 ccfsi tmux "$@"; }
type_keys() {  # send one character at a time; a bare ";" would be read by tmux as a command separator
  local s="$1" c; for ((i=0;i<${#s};i++)); do c="${s:i:1}"; [ "$c" = ";" ] && c="\\;"; T send-keys -t demo -l "$c"; sleep 0.03; done; }
run() { type_keys "$1"; sleep 0.4; T send-keys -t demo Enter; sleep "${2:-2}"; }
wait_for() { for _ in $(seq 1 ${2:-240}); do T capture-pane -p -t demo | grep -qE "$1" && return 0; sleep 1; done; return 1; }
sleep 2
run 'clear; cat CLAUDE.md' 5
run 'python3 -m pytest -q 2>&1 | tail -3' 4
run 'claude' 1
wait_for 'accept edits on' 30; sleep 2
type_keys 'src/fee.py를 사내 표준(CLAUDE.md)에 맞게 리팩토링하고, 실패하는 테스트의 원인도 찾아서 고쳐줘.'
sleep 1; T send-keys -t demo Enter
sleep 5
wait_for 'done [0-9]+:[0-9]+' 300; sleep 5
type_keys '/exit'; sleep 0.5; T send-keys -t demo Enter; sleep 3
run 'clear; git diff --stat; python3 -m pytest -q 2>&1 | tail -2' 4
run 'grep -nE "Decimal|ROUND_DOWN|class Side|FEE_RATE" src/fee.py | head -12' 5
T kill-session -t demo
