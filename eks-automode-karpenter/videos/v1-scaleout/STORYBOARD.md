---
mode: autonomous
message: "같은 Pending Pod 10개에 두 클러스터 모두 같은 인스턴스 1대를 골랐고, 이 1회 측정에서는 Auto Mode 노드가 더 빨리 Ready가 되었다"
audience: 플랫폼 엔지니어, SRE, 아키텍트 (L300)
duration: 150
canvas: 1920x1080
---

Single-file build (monolithic `index.html`), same structure as `eks-hybrid-nodes-1h/videos/v2-bursting`. The recording scene plays `assets/d1-scaleout-30fps.mp4` (30fps CFR re-encode of `assets/d1-scaleout.mp4`) as a framework-owned muted `<video>` clip inside an untimed window `#recwin` (shown 34 to 88 s); the inner `#recpan` is scaled per phase. The reconstruction footer is hidden during the recording scene. Color: akd-auto accent #41B3FF, akd-karp warning #FBD332.

## Frame 0
status: built
src: index.html#s0-title
time: 0 to 6s
beat: 제목과 메시지

## Frame 1
status: built
src: index.html#s1
time: 5.5 to 34s
beat: 1/4 실험 조건: akd-auto(Auto Mode, Bottlerocket), akd-karp(Karpenter 1.15.0, AL2023), 공통(EKS 1.37, fsi-demo-vpc 2a/2b, demo NodePool on-demand c/m/r gen > 5 amd64), 워크로드(pause, 0 → 10, 1 vCPU / 1.5Gi)

## Frame 2
status: built
src: index.html#recA, #vA, #recov
time: 34 to 88s (media 2 to 29s at 0.5x)
beat: 2/4 녹화: NodePool 조건 확인(34 to 60, 0.955x), 상태 블록 확대(60 to 80, 1.3x, 자막 5개: Pending, c7i-flex.4xlarge, Auto R=True, Auto 10/10, Karpenter 10/10), 요약과 NodeClaim 표(80 to 88, 1.0x, 강조 상자 3개, 자막 +28초/+47초, CREATED 13:54:15, READY 13:54:30 vs 13:54:55)

## Frame 3
status: built
src: index.html#s3
time: 88 to 124s
beat: 3/4 타임라인 비교: 패널 A 노드 Ready(NodeClaim 13:54:15 기준) 15초 vs 40초, 패널 B Pod 10개 Ready(scale 기준) +28초 vs +47초, 칩(NodeClaim 각 1개, c7i-flex.4xlarge, on-demand 2b)

## Frame 4
status: built
src: index.html#s4
time: 124 to 150s
beat: 4/4 메시지, 같았던 것 / 달랐던 것 카드, 주의(1회 측정 벤치마크 아님, 노드 OS 다름)
