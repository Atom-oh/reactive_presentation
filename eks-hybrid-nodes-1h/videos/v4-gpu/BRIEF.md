---
workflow: general-video
flow: automation
storyboard: no
message: "온프렘 GPU 노드도 같은 클러스터의 Service로 클라우드에서 호출된다"
destination: presentation-embed
aspect: 1920x1080
language: ko
audience: 아키텍트와 의사결정자 (L200)
length: 130s
angle: 실측 결과 재구성 (녹화 없음)
---

## Intent

60분 L200 세션 `eks-hybrid-nodes-1h`에서 hybrid GPU 추론 데모를 대신하는 무음 영상입니다. 발표자가 영상 위에서 설명하므로 화면 텍스트(한국어, 기술 용어는 영어)만으로 흐름이 읽혀야 합니다. 시리즈 네 번째 영상으로 V1부터 V3와 같은 레이아웃, 색, 머리글("N / 6" 칩과 제목), 하단 표기를 씁니다.

## Customizations

- 장면 6개: (1) 왜 온프렘 GPU(데이터 위치, 기존 GPU, 이 데모의 GPU 호스트), (2) 구성(taint와 label, device plugin, 추론 Pod), (3) 추론 호출 흐름(클라우드 Job → Service → gateway 경로 → vLLM Pod, 응답), (4) 결과 카드 4개(2026-10-15 실행 결과 재구성), (5) 준비할 것(드라이버와 toolkit 호스트 설치, 이미지 사전 다운로드, 길이 비례 막대), (6) 메시지와 요약.
- GPU 호스트는 2026-10-15에 한 번 실행 후 제거되어 녹화가 없습니다. 모든 장면 하단 왼쪽 "실측 결과 재구성 (2026-10 시뮬레이션 환경)", 오른쪽 "데모 4: hybrid GPU 추론". 가짜 터미널은 쓰지 않고 결과 카드와 흐름도로만 보여 줍니다.
- 덱 테마 색: 배경 #161D26, accent #41B3FF, warning #FBD332, success #00E500, danger #FF5C85.
- 직접 쓴 텍스트는 36px 이상(1080p).

## Notes

- 수치는 FACTS.md에 있는 값만 사용합니다.
- 계정 ID, 인스턴스 ID, 비밀 값은 표시하지 않습니다.
- em dash와 가운데 점을 쓰지 않습니다. 구분자는 ":" 또는 ",".
- 비대화형 실행: 인터뷰와 승인 게이트는 controller 지시에 따라 `check` 통과와 프레임 샘플 검토로 대체했습니다.
