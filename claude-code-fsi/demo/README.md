# Claude Code for FSI 데모 소스

덱 3부, 4부 영상(V1~V3)을 만든 실제 소스입니다. 녹화 기록은 `../media/RECORDINGS.md`.

- `docker/Dockerfile`: 개발자 단말 역할 컨테이너(Claude Code, tmux, pytest). AWS 자격증명을 넣지 않습니다.
- `gateway/gateway.py`, `policy.json`: 데모용 LLM Gateway. 토큰 인증, 모델 allowlist, DLP 정규식, SigV4 재서명, 스트리밍 그대로 전달, JSONL 감사 로그. 운영용이 아닙니다.
- `scenarios/etc/managed-settings.json`: 관리 설정 예시(Bedrock, Gateway 주소, 모델 고정, MCP 허용 목록, deny 규칙).
- `scenarios/fee-calc`: 하네스 예시(CLAUDE.md, PostToolUse hook, 테스트, 가짜 고객 데이터).
- `run-gateway.sh`, `run-container.sh`, `reset-project.sh`, `rec/*.sh`: 실행과 녹화 드라이버.

실행 순서: `docker build -t ccfsi-demo docker/` → `./run-gateway.sh`(별도 터미널, AWS 프로필 필요) → `./run-container.sh` → `./reset-project.sh` → `bash rec/r1-managed.sh`.
Gateway는 docker 브리지 주소에만 바인딩하며, 공개 포트를 열지 않습니다.
