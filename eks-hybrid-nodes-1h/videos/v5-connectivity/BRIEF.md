---
workflow: general-video
flow: automation
storyboard: no
message: "overlay와 SNAT 없이 Pod IP가 그대로 보이고, 온프렘 Pod도 PrivateLink로 AWS API를 쓴다"
destination: presentation-embed
aspect: 1920x1080
language: ko
audience: 아키텍트, 네트워크와 보안 담당자 (L300)
length: 150s
angle: 실측 결과 재구성과 실제 터미널 녹화
---

## Intent

Deep Dive 세션 `eks-hybrid-nodes` 5부(라이브 데모)에 들어가는 무음 영상입니다. 연결 검증 데모(Cilium native routing, SNAT 없음, PrivateLink)를 대신합니다. 발표자가 영상 위에서 설명하므로 화면 텍스트(한국어, 기술 용어는 영어)만으로 흐름이 읽혀야 합니다. 시리즈 다섯 번째 영상으로 V1~V4와 같은 레이아웃, 색, 머리글("N / 8" 칩과 제목), 하단 표기를 씁니다.

## Customizations

- 장면 8개(제목 장면 별도):
  1. 질문("방화벽이 온프렘 Pod를 Pod IP로 구분할 수 있나?")과 구성도: 클라우드 VPC 10.0.0.0/16(VPC CNI Pod, NAT, STS/S3 endpoint) ── TGW ── 온프렘 172.18.0.0/16(hybrid 노드, Pod 172.17.0.0/16). Cilium native routing, VXLAN 없음, masquerade 끔. 온프렘 라우터(시뮬레이션은 route table)가 노드별 Pod 블록을 노드로 보냄.
  2. 녹화 A: Pod 표와 변수 (영상 0~9.4초 구간).
  3. 녹화 B: 1) h1a → c1, 2) c1 → h2, 서버 로그의 출발지 (9.4~23초). 강조: `server saw 172.17.0.244`, `server saw 10.0.63.165`.
  4. 녹화 C: 3) 온프렘 socat 서버가 본 주소, 4) 인터넷 NAT (23~29.8초).
  5. 녹화 D: 5) DNS가 endpoint ENI로, 6) IRSA STS와 S3 (29.8~43.8초).
  6. 녹화 E: 7) endpoint SG가 Pod IP만 허용: 302 대 타임아웃(exit 28) (43.8~57.6초). 설명 상자: "같은 노드에서 나가도 출발지가 Pod IP(172.17)면 허용, 노드 IP(172.18)면 차단: SNAT이 없다는 증거". 타임아웃은 대기 구간 줄임으로 짧게 보인다는 표기.
  7. 38개 매트릭스 카드(10:50 측정): 11개 절, 절별 항목 수와 핵심 값(FACTS 실행 1 표). 모두 PASS.
  8. 메시지와 정리: 고친 세 가지(hostNetwork DNS용 SG 53, VPC CNI SNAT 제외 172.18.0.0/16, `/livez`), 주의 2개(S3 interface endpoint DnsOptions `AllResolvers`, CoreDNS가 클라우드 노드에만 있음 → 링크 단절 시 hybrid Pod 이름 해석 불가, 다음 데모).
- 녹화 장면은 `assets/r5-conn.mp4`(심볼릭 링크, 1920x1412)를 씁니다. 배속은 V3처럼 0.6~0.75배로 읽을 시간을 줍니다. 머리글 오른쪽에 "실제 터미널 녹화, 대기 구간 줄임, N배속", 하단 "실측 터미널 녹화 (2026-10-19, 시뮬레이션 환경)".
- 다른 장면 하단: 왼쪽 "실측 결과 재구성 (2026-10 시뮬레이션 환경)", 오른쪽 "데모 5: 연결 검증, SNAT 없음과 PrivateLink".
- 두 실행(10:50 측정, 녹화 회차 13:18)의 숫자를 섞지 않습니다. 장면 7은 10:50 값이며 머리글 배지로 회차를 표시합니다.
- 덱 테마 색: 배경 #161D26, accent #41B3FF, warning #FBD332, success #00E500, danger #FF5C85.
- 직접 쓴 텍스트는 36px 이상(1080p).

## Notes

- 수치는 FACTS.md에 있는 값만 사용합니다.
- 계정 ID, 비밀 값은 표시하지 않습니다(녹화의 계정 ID는 가려져 있음).
- em dash와 가운데 점을 쓰지 않습니다. 구분자는 ":" 또는 ",".
- 비대화형 실행: 인터뷰와 승인 게이트는 `check` 통과와 프레임 샘플 검토로 대체합니다.
