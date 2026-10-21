---
mode: autonomous
message: "정책을 비워 두면 Auto Mode는 Balanced, Karpenter는 WhenEmptyOrUnderutilized가 된다. 이번 스케일 인에서는 둘 다 같은 교체를 했고, Balanced는 점수 0.50으로 승인했다"
audience: 플랫폼 엔지니어, SRE, 아키텍트 (L300)
duration: 170
canvas: 1920x1080
---

Single-file build (monolithic `index.html`), same structure as `eks-hybrid-nodes-1h/videos/v2-bursting`. The recording scene plays `assets/d2-consolidation.mp4` (symlink to `../../rec/d2-consolidation.mp4`, 1920x1212, 1 fps) as one framework-owned muted `<video>` inside an untimed window `#recwin` (1800x840 at 60,150; video scaled to 1800x1136, bottom cropped; shown 30 to 99 s). The reconstruction footer is hidden during the recording scene. Header chips show per-scene progress over the five content scenes ("1 / 5" to "5 / 5"); the title has no chip. Auto Mode (akd-auto) uses accent, Karpenter (akd-karp) uses warning.

## Frame 0
status: built
src: index.html#s0-title
time: 0 to 6s
beat: 제목과 메시지

## Frame 1
status: built
src: index.html#s1
time: 5.5 to 30s
beat: 정책을 지정하지 않은 demo NodePool 라이브 값: Auto Mode Balanced / 336h, Karpenter WhenEmptyOrUnderutilized / 720h, 공통 consolidateAfter 30s, budget nodes "1", on-demand c/m/r, replica당 1 vCPU / 1.5Gi, built-in NodePool도 Balanced 30s 336h budget 10%

## Frame 2
status: built
src: index.html#recS, #vR
time: 30 to 99s (media 2 to 36.5s at 0.5x)
beat: 녹화: 기본 정책 확인 (30 to 52), 10 → 4 스케일 인 (52 to 86), 결과와 이벤트 (86 to 99). 헤더 제목만 바뀌고 녹화는 한 클립

## Frame 3
status: built
src: index.html#s3
time: 99 to 123s
beat: 녹화 회차 결과: 두 클러스터 모두 c7i-flex.4xlarge에서 c7i-flex.2xlarge로 replace, Pod 4개 이동, 첫 이동 관찰 +67초 / +75초, 이벤트 순서 Launching, Ready, Terminating, Evicted (양쪽 같음)

## Frame 4
status: built
src: index.html#s4
time: 123 to 147s
beat: Auto Mode 이벤트 원문(ConsolidationCandidate, ConsolidationApproved)과 타일: savings 50.0%, disruption 100.0%, score 0.50 / threshold 0.50 승인, savings $0.38

## Frame 5
status: built
src: index.html#s5
time: 147 to 170s
beat: 메시지, 카드 3개(녹화 회차 14:05, 앞선 회차 13:55 별도 카드, GitOps에서 정책 명시), 주의(시점이 달라 속도 차이로 해석하지 않음, 1회 실행)
