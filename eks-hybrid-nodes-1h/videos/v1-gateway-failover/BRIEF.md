---
workflow: general-video
flow: automation
storyboard: no
message: "Gateway 리더가 죽어도 3~5초 안에 스탠바이가 경로를 넘겨받는다"
destination: presentation-embed
aspect: 1920x1080
language: ko
audience: 아키텍트와 의사결정자 (L200)
length: 150s
angle: 실측 결과 재구성
---

## Intent

60분 L200 세션 `eks-hybrid-nodes-1h`에서 라이브 데모 1(Gateway 리더 장애 조치)을 대신하는 무음 영상입니다. 발표자가 영상 위에서 설명하므로 소리와 내레이션이 없고, 화면 텍스트(한국어, 기술 용어는 영어)만으로 흐름이 읽혀야 합니다. 청중은 아키텍트와 의사결정자이므로 명령 세부보다 "무엇이 바뀌고 얼마나 걸렸는가"가 보여야 합니다.

## Customizations

- 장면 5개: (1) 환경 구성도, (2) 평상시 경로, (3) 리더 Pod 삭제, (4) Lease와 라우트 교체, (5) 결과 카드 3회 측정.
- 모든 장면 하단 고정 표기: "실측 결과 재구성 (2026-10 시뮬레이션 환경)".
- 덱 테마 색: 배경 #161D26, 텍스트 #FFFFFF / #F3F3F7(흐리게), accent #41B3FF, warning #FBD332, success #00E500, danger #FF5C85.
- 프로젝터 가독성: 본문 36px 이상(1080p).

## Notes

- 수치는 FACTS.md에 있는 값만 사용합니다. 새 숫자를 만들지 않습니다.
- 계정 ID, 실제 ENI ID, 비밀 값은 표시하지 않습니다. 리소스 이름과 ID는 예시 표기(`eni-…a1`)로 흐리게 표시합니다.
- em dash와 가운데 점을 쓰지 않습니다. 구분자는 ":" 또는 ",".
- 비대화형 실행: 인터뷰와 승인 게이트는 controller 지시에 따라 `check` 통과와 프레임 샘플 검토로 대체했습니다.
