# EKS Capabilities 데모 녹화 기록

2026-10-21, 클러스터 `eks-cap-demo`(EKS 1.36.4, ap-northeast-2)에서 실제로 실행하며 녹화했습니다. 재구성 화면이 아니라 실행 중인 터미널과 브라우저 화면 그대로입니다. 블로그 글: https://blog.atomai.click/eks-capabilities-argocd/ , /eks-capabilities-kro/ , /eks-capabilities-ack/

공통 사항

- 터미널(V1, V3, V4): asciinema(`asciinema rec -c 'bash <driver>.sh' --cols 120 --rows 36 -i 2`)로 녹화했습니다. driver 스크립트가 프롬프트(`~/eks-capabilities-demo $`)와 함께 명령을 먼저 출력한 뒤 실행합니다. 녹화할 때 출력이 2초 넘게 없는 구간은 2초로 줄였으므로(`-i 2`), 영상 길이는 실제 경과 시간보다 짧습니다. 화면의 측정값(`push_to_synced_s` 등)은 실제 값입니다.
- 변환: agg(`--theme asciinema --font-family "Source Code Pro" --font-size 28 --idle-time-limit 2`) 후 ffmpeg로 h264 mp4(1920 폭, yuv420p, 무음, faststart)로 만들고, 오른쪽 아래에 "실제 터미널 녹화 · 대기 구간 2초로 줄임" 표시를 넣었습니다.
- UI(V2): Playwright(Chromium headless, 1600x960)로 녹화한 webm을 같은 규격의 mp4로 변환했습니다. 토큰은 파일에서 읽어 쿠키로만 넣었고, 화면에 출력하지 않았습니다. 커밋 작성자 이메일은 페이지 스크립트로 렌더링 전에 지웠습니다.
- 가린 값: AWS 계정 ID(12자리)는 명령 출력 단계에서 `sed`로 `************`로 바꿨습니다. 변환 전 `.cast`에서 계정 ID, `AKIA`, `token`, capability 서버 URL을 검색해 남은 것이 없음을 확인했습니다. capability UUID, IAM 역할 이름, ClusterIP는 그대로 두었습니다.

| 파일 | 녹화 시작(UTC) | 영상 길이 | 크기 | 해상도 | 내용 |
|---|---|---|---|---|---|
| `v1-argocd.mp4` | 2026-10-21 09:50:26 | 36.9초 | 2.1 MB | 1920x1358 | 관리형 Argo CD: capability 목록, 노드의 Pod, ARN 클러스터 등록, git push → webhook Synced 7.0초, drift 복구 3.0초 |
| `v2-argocd-ui.mp4` | 2026-10-21 13:33 | 34.0초 | 2.3 MB | 1920x1152 | 관리형 Argo CD UI: argocd-cm 배너, 앱 목록, demo-web 트리와 수동 Sync, kro 인스턴스(Lua health), ACK Queue(내장 health) |
| `v3-kro.mp4` | 2026-10-21 10:08:00 | 46.4초 | 3.3 MB | 1920x1358 | 관리형 kro(2회차 생성 직후): 버전, access entry 그룹과 바인딩, 인스턴스 생성과 변경, kro+ACK ConfigMap, 삭제 |
| `v4-ack.mp4` | 2026-10-21 12:27:29 | 31.3초 | 1.4 MB | 1920x1358 | 관리형 ACK(2회차 생성 후): CRD 267개, Pod 0개, IAMRoleSelector, team-b Queue 성공과 Bucket AccessDenied, eks: 태그 |

V1 화면의 `kro-system` Pod는 2편 비교용 self-managed kro입니다.
