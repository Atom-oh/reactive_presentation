---
mode: autonomous
message: "NodeClass를 바꾸면 기존 노드는 Drift로 표시되고, budget 1대 기준으로 새 노드를 먼저 띄운 뒤 하나씩 교체된다"
audience: 플랫폼 엔지니어, SRE, 아키텍트 (L300)
duration: 160
canvas: 1920x1080
---

Single-file build (monolithic `index.html`), same structure as `eks-hybrid-nodes-1h/videos/v2-bursting`. The recording scene plays `assets/d3-drift.mp4` (symlink to `../../rec/d3-drift.mp4`, 1920x1212, 1 fps) as one framework-owned muted `<video>` inside an untimed window `#recwin` (shown 29 to 98.8 s, scaled 1.125x, left 1600 source px visible). Colors: akd-auto accent, akd-karp warning, Launch success, Terminate danger. Reconstruction footer clips `#fA` and `#fB` are absent during the recording; recording clips carry their own footer.

## Frame 0
status: built
src: index.html#s0-title
time: 0 to 6s
beat: 제목 "Drift 교체"와 메시지

## Frame 1
status: built
src: index.html#s1
time: 5.5 to 29s
beat: 1/5 무엇을 바꿨나: akd-auto NodeClass maxPods 64 추가(AMI는 사용자가 고르지 않음), akd-karp alias v20261003 에서 v20261012, 시작 상태 노드 2대(2a, 2b), Pod 6개, 패치 직후 Drifted=True, budget nodes 1

## Frame 2
status: built
src: index.html#recA, #recB, #vD3, #callouts
time: 29 to 98.8s (media 2 to 36.9s at 0.5x)
beat: 2/5 녹화: 시작 상태와 패치(29 to 51), Drift 교체 진행(51 to 98.8). 콜아웃: budget nodes 1, 기존 노드 DRIFTED, 새 노드 먼저 Launch, 완료 +98초 / +127초

## Frame 3
status: built
src: index.html#s3
time: 98.8 to 124s
beat: 3/5 교체 순서 타임라인(UTC 14:20:00 to 14:21:30): 양쪽 Launch, Terminate, Launch, Terminate 시각, 완료 상자 +98초 vs +127초

## Frame 4
status: built
src: index.html#s4
time: 124 to 144s
beat: 4/5 결과: akd-karp 새 AMI v20261012, akd-auto capacity.pods 56(설정 64, min 규칙), spot NodePool도 교체(spot-8wplw 에서 spot-89g4w)

## Frame 5
status: built
src: index.html#s5
time: 144 to 160s
beat: 5/5 정리: 메시지, AMI 버전 고정 후 의도적으로 올림, budget과 PDB로 속도 조절, Auto Mode도 NodeClass 변경이 Drift, 1회 실행 주의
