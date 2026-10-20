# 데모 녹화 기록 (V1~V3)

2026-10-19, AWS 서울 리전(ap-northeast-2)의 Amazon Bedrock을 실제로 호출하며 녹화했습니다. 재구성 화면이 아니라 실행 중인 터미널 출력 그대로입니다.

## 환경

- 개발자 단말 역할: Docker 컨테이너 `ccfsi`(호스트 이름 `5ho-pc`)(이미지 `demo/docker/Dockerfile`, Claude Code 2.1.303). **AWS 자격증명 없음.** 공개 포트 없음.
- LLM Gateway: 호스트에서 실행하는 데모용 Python 구현(`demo/gateway/gateway.py`). docker 브리지 주소(172.17.0.1:8787)에만 바인딩. Gateway만 AWS 역할을 가지고 SigV4로 다시 서명해 `bedrock-runtime.ap-northeast-2`를 호출.
- 관리 설정: 컨테이너의 `/etc/claude-code/managed-settings.json`(`demo/scenarios/etc/managed-settings.json`).
- 모델 allowlist: `anthropic.claude-sonnet-5`(서울 in-region) 하나.
- Gateway 토큰: 데모용 고정 문자열(`tok-dev01-demo`). 운영에서는 IdP가 발급하는 단기 토큰.

## 녹화와 변환

- asciinema 2.4.0 `--cols 120 --rows 40 -i 2`, agg `--font-size 28 --idle-time-limit 2`, ffmpeg h264 mp4(1920x1506, yuv420p, 무음, faststart).
- 출력이 2초 넘게 없는 구간은 2초로 줄였습니다. 영상 길이는 실제 경과 시간보다 짧습니다. 화면의 시각 값은 실제 시각입니다.
- R3 첫 녹화(14:01)는 tmux가 `;`를 명령 구분자로 읽어 `clear; cat CLAUDE.md`가 깨져 다시 녹화했습니다(드라이버에서 `\;`로 전달).
- 각 영상은 mp4(H.264)와 webm(VP9) 두 가지로 넣었습니다. H.264를 못 읽는 Chromium 빌드에서도 재생됩니다.
- 녹화 원본 `.cast`에서 12자리 계정 ID, `AKIA`, `aws_secret`, `SessionToken`을 검색해 0건임을 확인했습니다.

| 파일 | 녹화 시작(UTC) | 영상 길이 | 드라이버 |
|---|---|---|---|
| `r1-managed.mp4` | 2026-10-19 13:59:36 | 70.7초 | `demo/rec/r1-managed.sh` |
| `r2-gateway.mp4` | 2026-10-19 14:01:06 | 32.7초 | `demo/rec/r2-gateway.sh` |
| `r3-harness.mp4` | 2026-10-19 14:52:23 | 75.6초 | `demo/rec/r3-inner.sh`, `r3-controller.sh` (tmux로 대화형 화면 녹화) |

## 관찰 결과

V1 관리 설정
- 단말: `env | grep -c "^AWS_"` 0, `~/.aws` 없음
- `claude mcp add` github, 로컬 npx 서버: `not allowed by enterprise policy`. Hub URL(`https://mcp-hub.ai-platform.internal/mcp`)만 추가됨
- 사용자 `~/.claude/settings.json`의 `Bash(curl *)` allow는 무시됨(`allowManagedPermissionRulesOnly`), curl 시도가 `permission_denials`에 기록
- `fee-calc`에서 고객 파일 읽기 요청은 CLAUDE.md 규칙으로 모델이 거절(denials 0). CLAUDE.md 없는 `batch-job`에서는 deny 규칙이 Read 차단(denials 1)

V2 LLM Gateway (`r2-audit.jsonl`)
- ALLOW 1건: in 28,950 / out 87 토큰
- BLOCK 6건: `dlp:주민등록번호` 2, `model_not_allowed`(global.anthropic.claude-opus-5-5) 2, `auth` 2. Claude Code가 400 응답을 한 번 재시도해 프롬프트당 2건

V3 하네스 (`r3-audit.jsonl`)
- 레거시 테스트 1 failed, 2 passed. Claude Code 작업 후 PostToolUse hook 메시지 `[SENSORS] pytest 통과: 3 passed`, 보고 `Cogitated for 32s`
- Gateway: 세션 시작 시 apac 프로파일 11개 확인 호출 BLOCK(`model_not_allowed`), 작업 호출 6건 ALLOW
