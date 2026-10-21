---
workflow: general-video
flow: automation
storyboard: no
message: "Karpenter는 Spot 중단 경고를 받자마자 노드를 비우고 대체 노드를 띄운다. Pod가 한 노드에 몰려 있으면 그 사이 서비스가 비어 있다"
destination: presentation-embed
aspect: 1920x1080
language: ko
audience: 플랫폼 엔지니어, SRE, 아키텍트 (L300)
length: 150s
angle: 실제 터미널 녹화 + 실측 결과 재구성
---
## Intent
데모 영상 4/4. AWS FIS로 Spot 중단 알림(2분 전)을 보내 직접 설치 Karpenter의 interruption 처리를 보여 줍니다. Auto Mode는 FIS EC2 액션을 지원하지 않아 Karpenter 클러스터에서만 실행했다는 점을 명시합니다.
## Scenes (안)
(1) 제목, (2) 경로 그림: FIS → EC2 Spot 중단 알림 → EventBridge 규칙 → SQS(interruption queue) → Karpenter, Auto Mode는 AWS가 처리, (3) 실제 터미널 녹화 d4-spot.mp4, (4) 타임라인: 14:23:15 FIS 시작, 14:23:28 Rebalance, 14:23:29 SpotInterrupted + Pod 3개 Evicted + 대체 NodeClaim, 14:23:33 Launched, 14:23:35 기존 인스턴스 종료, 14:24:00 대체 노드 Ready, (5) 약 30초 Running 0개(Pod 3개가 한 노드), (6) 정리: replica 분산(topology spread), PDB, 여러 인스턴스 유형 허용.
## Notes
- 수치는 ../rec/RECORDINGS.md "D4" 절만 사용합니다.
