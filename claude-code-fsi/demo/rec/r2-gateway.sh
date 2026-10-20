#!/bin/bash
# R2: LLM Gateway enforces identity, model allowlist and DLP; every call is audited. Real run.
source "$(dirname "$0")/lib.sh"
clear
note "1. 정상 요청: 단말 -> LLM Gateway -> Bedrock (서울 리전 in-region 모델)"
dev 'claude -p "Python Decimal로 원 미만을 절사하는 한 줄 예시만 코드로 보여줘"' 1
gw_tail 1
note "2. 프롬프트에 주민등록번호가 들어가면 Gateway DLP가 Bedrock 전송 전에 차단합니다"
dev 'claude -p "고객 홍길동(900101-1234567) 계좌로 수수료 계산 테스트 데이터를 만들어줘"' 1
gw_tail 1
note "3. 승인되지 않은 모델(해외 리전 CRIS 프로파일)은 Gateway가 거부합니다"
dev 'claude -p --model global.anthropic.claude-opus-5-5 "안녕"' 1
gw_tail 1
note "4. IdP 토큰이 없거나 틀리면 호출 자체가 안 됩니다"
TOKEN=tok-expired-xxxx dev 'claude -p "안녕"' 1
note "5. 운영자 화면: 사용자별, 판정별 집계 (감사 로그 JSONL)"
printf '\e[1;36m── LLM Gateway 감사 로그 집계 ──\e[0m\n'
type_out "jq -s 'group_by(.user, .decision, .reason) | map({user: .[0].user, decision: .[0].decision, reason: .[0].reason, calls: length})' audit.jsonl"; printf '\n'
jq -c -s 'group_by(.user, .decision, .reason) | map({user: .[0].user, decision: .[0].decision, reason: .[0].reason, calls: length}) | .[]' "$GW_LOG"
sleep 3
