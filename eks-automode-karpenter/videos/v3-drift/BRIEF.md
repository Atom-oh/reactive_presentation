---
workflow: general-video
flow: automation
storyboard: no
message: "NodeClass를 바꾸면 기존 노드는 Drift로 표시되고, budget 1대 기준으로 새 노드를 먼저 띄운 뒤 하나씩 교체된다"
destination: presentation-embed
aspect: 1920x1080
language: ko
audience: 플랫폼 엔지니어, SRE, 아키텍트 (L300)
length: 160s
angle: 실제 터미널 녹화 + 실측 결과 재구성
---
## Intent
데모 영상 3/4. Karpenter는 AMI alias 변경(al2023@v20261003 → al2023@v20261012), Auto Mode는 NodeClass advancedCompute.kubelet.maxPods 64 추가. 두 클러스터에서 Drift 교체가 budget nodes 1로 순차 진행되는 모습.
## Scenes (안)
(1) 제목, (2) 무엇을 바꿨나(두 패치, AMI는 Auto Mode에서 사용자가 고르지 않음), 시작 상태 노드 2대(2a, 2b), Pod 6개, (3) 실제 터미널 녹화 d3-drift.mp4, (4) 교체 타임라인: Launch, Terminate, Launch, Terminate 시각(양쪽), 완료 +98초 vs +127초, (5) 결과 확인: 새 AMI v20261012, Auto Mode capacity.pods 56(설정 64, 실제값 = min(설정값, 인스턴스 IP 수, 110)), 같은 EC2NodeClass를 쓰는 spot 풀도 함께 교체됨, (6) 정리: AMI는 버전 고정 후 의도적으로 올림, budget과 PDB로 속도 조절.
## Notes
- 수치는 ../rec/RECORDINGS.md "D3" 절만 사용합니다.
