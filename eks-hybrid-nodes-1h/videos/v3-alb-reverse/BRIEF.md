---
workflow: general-video
flow: automation
storyboard: no
message: "타깃은 Load Balancer Controller가 따라가고, 온프렘에서 들어올 때는 internal LB가 기본 경로다"
destination: presentation-embed
aspect: 1920x1080
language: ko
audience: 아키텍트와 의사결정자 (L200)
length: 192s
angle: 실측 결과 재구성과 실제 터미널 녹화
---

## Intent

60분 L200 세션 `eks-hybrid-nodes-1h` 5부에서 LB 데모(ALB ip 타깃과 역방향 경로)를 대신하는 무음 영상입니다. 발표자가 영상 위에서 설명하므로 화면 텍스트(한국어, 기술 용어는 영어)만으로 흐름이 읽혀야 합니다. 시리즈 세 번째 영상으로 V1, V2와 같은 레이아웃, 색, 머리글("N / 9" 칩과 제목), 하단 표기를 씁니다.

## Customizations

- 장면 9개: (1) 질문과 정방향 경로(리전 클라이언트 → internal ALB → VPC 라우트 → Gateway 리더 → VXLAN → hybrid Pod, LBC와 Gateway의 역할), (2) 녹화: 시작 상태, (3) 녹화: rollout restart와 타깃 폴링, (4) 타깃 교체 타임라인(녹화 폴링 값: initial, healthy, draining), (5) 녹화: 수렴 직후(Pod 표의 Failed 행은 "이전 Pod 종료 중"으로 설명), (6) Gateway 리더 전환 중 요청 막대(02:11 측정, 녹화에 없음), (7) 역방향 3경로(성공, hairpin, NodePort 실패와 원인), (8) 녹화: 온프렘에서 호출, (9) 메시지와 회차별 요약 카드.
- 녹화 장면은 `../rec/r3-alb.mp4`를 씁니다: 2/9 0.6배속, 3/9 0.75배속, 5/9 0.6배속, 8/9 0.75배속. 머리글 오른쪽에 "실제 터미널 녹화, 대기 구간 줄임, N배속", 하단 "실측 터미널 녹화 (2026-10-18, 시뮬레이션 환경)".
- 다른 장면 하단: 왼쪽 "실측 결과 재구성 (2026-10 시뮬레이션 환경)", 오른쪽 "데모 3: ALB ip 타깃과 역방향".
- 두 실행(02:11 측정, 녹화 회차 06:36)의 숫자를 섞지 않습니다. 장면 4와 녹화 장면은 녹화 회차 값, 장면 6과 7은 02:11 값이며 머리글 배지로 회차를 표시합니다. 정리 장면은 회차별 카드 두 개입니다.
- 덱 테마 색: 배경 #161D26, accent #41B3FF, warning #FBD332, success #00E500, danger #FF5C85.
- 직접 쓴 텍스트는 36px 이상(1080p). 녹화 글자는 원본 비율(약 0.84배, 약 24px)입니다.

## Notes

- 수치는 FACTS.md에 있는 값만 사용합니다. 장면 6의 실패 칸 위치는 예시이며 화면에 표시합니다.
- 계정 ID, 비밀 값은 표시하지 않습니다(녹화의 계정 ID는 가려져 있음).
- em dash와 가운데 점을 쓰지 않습니다. 구분자는 ":" 또는 ",".
- 비대화형 실행: 인터뷰와 승인 게이트는 controller 지시에 따라 `check` 통과와 프레임 샘플 검토로 대체했습니다.
