#!/usr/bin/env bash
# 녹화용 공통 함수: 프롬프트와 명령을 먼저 타이핑하듯 출력한 뒤 실제로 실행합니다.
export PYTHONWARNINGS=ignore
PY=${PY:-python3}
cd "$(dirname "${BASH_SOURCE[0]}")/.."
type_out() { local s="$1" i; for (( i=0; i<${#s}; i++ )); do printf '%s' "${s:$i:1}"; sleep 0.03; done; }
show() { printf '\033[1;32m~/ontology-demo $\033[0m '; type_out "$1"; printf '\n'; sleep 0.6; }
run()  { show "$1"; eval "${1/python/$PY}"; printf '\n'; sleep 2.5; }
note() { printf '\033[1;36m# %s\033[0m\n' "$1"; sleep 2; }
