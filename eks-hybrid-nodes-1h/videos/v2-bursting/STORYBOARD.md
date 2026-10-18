---
mode: autonomous
message: "Kyverno만으로 온프렘 Pod를 지키고, Karpenter 게이트는 EC2 정리를 조금 더 빠르게 한다"
audience: 아키텍트와 의사결정자
duration: 216
canvas: 1920x1080
---

Single-file build (monolithic `index.html`), same structure as V1. Recording scenes play `assets/r2-bursting.mp4` (symlink to `../../rec/r2-bursting.mp4`) as framework-owned muted `<video>` clips inside an untimed window `#recwin` (shown 56 to 128 s). The reconstruction footer is hidden during recording scenes.

## Frame 0
status: built
src: index.html#s0-title
time: 0 to 6s
beat: 제목과 메시지

## Frame 1
status: built
src: index.html#s1
time: 5.5 to 30s
beat: 1/7 ReplicaSet 스케일 인 순서(위치를 보지 않음), 실험 환경(hybrid 2대 4 vCPU, 8개, 930m 10-15, 910m 10-18 녹화, burst NodePool 32 vCPU), 시나리오 A/B/C

## Frame 2
status: built
src: index.html#s2
time: 30 to 56s
beat: 2/7 녹화 회차 기준 그림: 3 → 15, hybrid 8개(4, 4), Pending 7개, NodeClaim 3개(m6i.large 1, m6i.xlarge 2, 약 5초 뒤 첫 화면), burst Pod 1/3/3, 15개 Ready 35초

## Frame 3
status: built
src: index.html#recA, #vA
time: 56 to 92s (media 0.8 to 18.8s at 0.5x)
beat: 3/7 녹화: 3개 시작, scale 15, Pending, NodeClaim, 15개 Running (8 hybrid / 7 burst)

## Frame 4
status: built
src: index.html#recB, #vB
time: 92 to 128s (media 18.8 to 36.8s at 0.5x; window panned up 94px from 92.7 to 100.7s)
beat: 4/7 녹화: scale 10 → 8 hybrid / 2 burst, scale 3 → 3개 모두 mi-*, COST 1

## Frame 5
status: built
src: index.html#s3, #say, #ph
time: 128 to 174s
beat: 5/7 2026-10-15 A/B/C: A hybrid Pod 2개가 먼저 빠짐(6/4, EC2 3), B 8/2 EC2 4, C 8/2 EC2 3, 3개(A 2/1, B 3/0, C 3/0), 정리 123/118/87초

## Frame 6
status: built
src: index.html#s4
time: 174 to 194s
beat: 6/7 비교표와 각주

## Frame 7
status: built
src: index.html#s5
time: 194 to 216s
beat: 7/7 메시지, 카드 3개(온프렘 보호 10-15, EC2 정리 10-15, 녹화 회차 B 10-18), best-effort와 1회 실행 주의
