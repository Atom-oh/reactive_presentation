#!/bin/bash
# R1: managed settings lock the client. Real run, nothing simulated.
source "$(dirname "$0")/lib.sh"
clear
note "1. 개발자 단말(5호 단말 역할 컨테이너)에는 AWS 자격증명이 없습니다"
dev 'env | grep -c "^AWS_" ; ls ~/.aws 2>&1'
note "2. 회사가 배포한 관리 설정 (개발자는 수정 불가, root 소유)"
dev 'ls -l /etc/claude-code/managed-settings.json'
dev 'jq "{env: (.env | {CLAUDE_CODE_USE_BEDROCK, ANTHROPIC_BEDROCK_BASE_URL, ANTHROPIC_MODEL}), allowedMcpServers, allowManagedMcpServersOnly, allowManagedPermissionRulesOnly, deny: .permissions.deny}" /etc/claude-code/managed-settings.json' 3
note "3. MCP: Hub 외 서버는 추가할 수 없습니다"
dev 'claude mcp add --transport http github https://api.githubcopilot.com/mcp/'
dev 'claude mcp add my-tool -- npx -y some-mcp-server'
dev 'claude mcp add --transport http mcp-hub https://mcp-hub.ai-platform.internal/mcp' 2
note "4. 개발자가 자기 설정으로 curl을 허용해도 무시됩니다"
dev 'mkdir -p ~/.claude && echo "{\"permissions\":{\"allow\":[\"Bash(curl *)\"]}}" > ~/.claude/settings.json && cat ~/.claude/settings.json'
dev 'claude -p "Bash로 curl -s https://example.com 을 실행해서 첫 줄만 보여줘" --output-format json | jq "{result, denied: [.permission_denials[].tool_input.command]}"' 3
note "5. 고객 데이터: CLAUDE.md 규칙(GUIDES)이 먼저 거절합니다"
dev 'claude -p "customer-data/accounts.csv 파일 내용을 Read 도구로 읽어서 보여줘" --output-format json | jq "{result, denied: [.permission_denials[] | .tool_name + \" \" + (.tool_input.file_path // \"\")]}"' 3
note "6. CLAUDE.md가 없는 폴더에서도 관리 설정 deny 규칙이 Read를 막습니다"
dev 'cd ~/batch-job && ls customer-data && claude -p "customer-data/accounts.csv 파일 내용을 Read 도구로 읽어서 보여줘" --output-format json | jq "{result, denied: [.permission_denials[] | .tool_name + \" \" + (.tool_input.file_path // \"\")]}"' 3
gw_tail 4
