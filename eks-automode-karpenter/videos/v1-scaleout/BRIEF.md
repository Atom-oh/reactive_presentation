---
workflow: general-video
flow: automation
storyboard: no
message: "같은 Pending Pod 10개에 두 클러스터 모두 같은 인스턴스 1대를 골랐고, 이 1회 측정에서는 Auto Mode 노드가 더 빨리 Ready가 되었다"
destination: presentation-embed
aspect: 1920x1080
language: ko
audience: 플랫폼 엔지니어, SRE, 아키텍트 (L300)
length: 150s
angle: 실제 터미널 녹화 + 실측 결과 재구성
---
## Intent
60분 세션 `eks-automode-karpenter` 4부 데모 영상 1/4. 같은 NodePool 조건, 같은 워크로드(replica 10개, 각 1 vCPU / 1.5Gi)를 EKS Auto Mode(akd-auto)와 직접 설치 Karpenter 1.15.0(akd-karp)에 동시에 배포했을 때 무엇이 같고 무엇이 다른지 보여 줍니다. 발표자가 영상 위에서 말하므로 화면 텍스트만으로 흐름이 읽혀야 합니다.
## Scenes (안)
(1) 제목과 메시지, (2) 실험 조건: EKS 1.37, fsi-demo-vpc, 두 NodePool 조건 동일(on-demand, c/m/r, generation > 5, amd64), 워크로드, (3) 실제 터미널 녹화 d1-scaleout.mp4, (4) 타임라인 비교: NodeClaim 생성 13:54:15 동시, 노드 Ready +15초 vs +40초, Pod 10개 Ready +28초 vs +47초, 둘 다 c7i-flex.4xlarge 1대, (5) 해석과 주의: 1회 측정, 노드 OS 다름(Bottlerocket vs AL2023), 벤치마크 아님.
## Notes
- 수치는 ../rec/RECORDINGS.md "D1" 절과 공통 사항의 값만 사용합니다.
