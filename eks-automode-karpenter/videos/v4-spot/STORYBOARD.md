---
mode: autonomous
message: "Karpenter는 Spot 중단 경고를 받자마자 노드를 비우고 대체 노드를 띄운다. Pod가 한 노드에 몰려 있으면 그 사이 서비스가 비어 있다"
audience: 플랫폼 엔지니어, SRE, 아키텍트 (L300)
duration: 150
canvas: 1920x1080
---

Single-file build (monolithic `index.html`), same structure as the eks-hybrid-nodes-1h V2. Recording scenes play `assets/d4-spot.mp4` (symlink to `../../rec/d4-spot.mp4`, 1920x1284, 1 fps) via the 30 fps re-encode `assets/d4-spot-30fps.mp4` as framework-owned muted `<video>` clips at 0.6x inside an untimed window `#recwin` (1800x830, video scaled to 1800x1204), shown 34 to 83.6 s. The reconstruction footer is hidden during recording scenes. Color: akd-karp (Karpenter) = warning, Auto Mode = accent.

## Frame 0
status: built
src: index.html#s0-title
time: 0 to 7s
beat: 제목, 메시지, akd-karp에서만 실행(Auto Mode는 FIS EC2 액션 미지원)

## Frame 1
status: built
src: index.html#s1
time: 7 to 34s
beat: 1/4 경로: FIS, EC2 Spot(2분 전 알림), EventBridge 규칙 5개, SQS interruption queue, Karpenter. 알림 점이 경로를 따라 이동. 규칙 5개 목록(Spot, Rebalance 강조), Auto Mode 카드(AWS가 처리)

## Frame 2
status: built
src: index.html#recA, #vA
time: 34 to 55.5s (media 2.05 to 14.95s at 0.6x; window panned up 326px at 41.9s)
beat: 2/4 녹화: Pod 3개 모두 한 노드, helm settings.interruptionQueue, EventBridge 규칙 5개, fis.sh start

## Frame 3
status: built
src: index.html#recB, #vB, #capstrip
time: 55.5 to 83.6s (media 15.05 to 31.95s at 0.6x)
beat: 2/4 녹화: Evicted, Pending, spot-cx877 Launched, spot-89g4w Drained/Terminating, 새 노드 Registered, 3개 Running, 3/3 회복 +65초. 하단 자막 5개는 1 fps 프레임 경계에 맞춤

## Frame 4
status: built
src: index.html#s3
time: 83.6 to 112s
beat: 3/4 타임라인 7행: 14:23:15 FIS 시작부터 14:24:00 대체 노드 Ready까지, 콜아웃 "2분을 기다리지 않음"

## Frame 5
status: built
src: index.html#s4
time: 112 to 132s
beat: 3/4 공백: spot-89g4w의 Pod 3개 Evicted, Running 카운터 3, 0, 3, 막대 "약 30초 Running 0개", spot-cx877 Ready 후 Pod 3개

## Frame 6
status: built
src: index.html#s5
time: 132 to 150s
beat: 4/4 메시지, 카드 3개(replica 분산, PDB, 여러 인스턴스 유형), 주의(1회 실행, +65초, Auto Mode는 같은 실험 불가)
