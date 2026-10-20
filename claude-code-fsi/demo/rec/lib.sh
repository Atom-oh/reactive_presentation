# Shared helpers for recording drivers. Commands run inside the dev-PC container as dev01.
DEV_PROMPT=$'\e[32mdev01@5ho-pc\e[0m:\e[34m~/fee-calc\e[0m$ '
GW_LOG=~/claude-code-fsi-demo/gateway/logs/audit.jsonl
type_out() { local s="$1"; for ((i=0;i<${#s};i++)); do printf '%s' "${s:i:1}"; sleep 0.025; done; }
note() { printf '\n\e[1;33m# %s\e[0m\n' "$1"; sleep 1.2; }
dev() {  # dev "<command>": show the prompt, type the command, run it in the container
  printf '%s' "$DEV_PROMPT"; type_out "$1"; sleep 0.4; printf '\n'
  docker exec -u dev01 -w /home/dev01/fee-calc -e ANTHROPIC_AUTH_TOKEN="${TOKEN:-tok-dev01-demo}" -e COLUMNS=118 ccfsi bash -c "$1"
  sleep "${2:-1.5}"
}
gw_tail() {  # show the newest gateway audit records as the gateway operator sees them
  printf '\e[1;36m── LLM Gateway 감사 로그 (전산실 운영자 화면) ──\e[0m\n'
  tail -n "${1:-1}" "$GW_LOG" | jq -c '{ts: .ts[11:19], user, model, decision, reason, in: .input_tokens, out: .output_tokens}'
  sleep 2
}
