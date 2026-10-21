---
workflow: general-video
flow: automation
storyboard: no
message: "정책을 비워 두면 Auto Mode는 Balanced, Karpenter는 WhenEmptyOrUnderutilized가 된다. 이번 스케일 인에서는 둘 다 같은 교체를 했고, Balanced는 점수 0.50으로 승인했다"
destination: presentation-embed
aspect: 1920x1080
language: ko
audience: 플랫폼 엔지니어, SRE, 아키텍트 (L300)
length: 170s
angle: 실제 터미널 녹화 + 실측 결과 재구성
---
## Intent
데모 영상 2/4. 1.37의 기본 consolidation 정책 차이(라이브 값), 10 → 4 스케일 인 후 두 클러스터의 동작, Balanced 점수 이벤트를 보여 줍니다.
## Scenes (안)
(1) 제목, (2) 정책을 지정하지 않은 NodePool의 라이브 값 비교(Balanced/336h vs WhenEmptyOrUnderutilized/720h, 둘 다 consolidateAfter 30s, budget 1), (3) 실제 터미널 녹화 d2-consolidation.mp4, (4) 결과: 둘 다 c7i-flex.4xlarge → c7i-flex.2xlarge replace, Pod 4개 이동, 이벤트 순서 Launch → Ready → Terminate → Evict, (5) Balanced 점수: savings 50.0%, disruption 100.0%, score 0.50 >= threshold 0.50, savings $0.38, (6) 주의와 정리: 앞선 회차에서는 실행 시점이 달랐으므로(Karpenter 약 1분, Auto Mode 약 5분 30초) 속도 차이로 해석하지 않음, GitOps에서는 정책을 명시.
## Notes
- 수치는 ../rec/RECORDINGS.md "D2" 절과 공통 사항의 값만 사용합니다. 녹화 회차와 앞선 회차의 숫자를 섞지 않고 구분 표기합니다.
