#!/usr/bin/env bash
# D1: 온톨로지 Grounding 효과 실측 (Bedrock, Claude Haiku 4.5, 가상 ETF 데이터)
source "$(dirname "$0")/rec-lib.sh"
clear
note "D1: 같은 모델, 같은 질문 12개. 온톨로지를 설명할 때와 값으로 확정할 때"
note "DB 원장은 코드값으로 저장되어 있습니다 (가상 데이터)"
run "python d1_grounding.py peek"
note "어휘(SKOS): 사람이 쓰는 말을 DB 값으로 잇는 사전"
run "grep -A3 'ex:BdUSGov ' etf_ontology.ttl"
note "질문 하나를 A, B, C 세 방식으로 실행"
run "python d1_grounding.py one --idx 0"
note "질문 12개 전체 실행 (질문마다 모드별 1회 호출, temperature 0)"
run "python d1_grounding.py all --out results/d1-run.json"
note "사전에 없는 말이 나오면: SQL을 만들지 않고 되묻기"
run "python d1_grounding.py clarify"
sleep 4
