---
mode: autonomous
message: "타깃은 Load Balancer Controller가 따라가고, 온프렘에서 들어올 때는 internal LB가 기본 경로다"
audience: 아키텍트와 의사결정자
duration: 192
canvas: 1920x1080
---

Single-file build (monolithic `index.html`), same structure as V1 and V2. Recording scenes play `assets/r3-alb.mp4` (symlink to `../../rec/r3-alb.mp4`) as framework-owned muted `<video>` clips inside an untimed window `#recwin` (1613x850, scale 0.84). Recording A is top aligned; from recording B on the window shows the bottom of the terminal (pan -229px). The reconstruction footer is hidden during recording scenes.

## Frame 0
status: built
src: index.html#s0-title
time: 0 to 6s
beat: 제목과 메시지

## Frame 1
status: built
src: index.html#s1
time: 6 to 28s
beat: 1/9 질문, 정방향 경로도와 패킷, LBC(Endpoints 보고 타깃 등록, 해제, AZ all), Gateway(경로만), 답

## Frame 2
status: built
src: index.html#recA, #vA
time: 28 to 48s (media 0.4 to 12.4s at 0.6x)
beat: 2/9 녹화: ALB 이름, Pod .132/.26 Running, 타깃 healthy, 부하 시작

## Frame 3
status: built
src: index.html#recB, #vB
time: 48 to 80s (media 12.4 to 36.4s at 0.75x)
beat: 3/9 녹화: rollout restart, +1s부터 +50s까지 폴링, 50초 수렴

## Frame 4
status: built
src: index.html#s4
time: 80 to 98s
beat: 4/9 녹화 회차 폴링 격자(4 IP x 10 시점), 50초, 174건 ERR 0, draining 후 해제

## Frame 5
status: built
src: index.html#recC, #vC, #cnote
time: 98 to 116.5s (media 36.4 to 47.5s at 0.6x)
beat: 5/9 녹화: rollout status, Pod 표(Failed 행 설명 상자 107.8s부터), 부하 174건 ERR 0 (113.7s부터)

## Frame 6
status: built
src: index.html#s6
time: 116.5 to 131.5s
beat: 6/9 02:11 측정: 요청 191칸 중 1칸 실패(위치 예시), 인계 4초, 타깃 .230/.76 healthy 유지, wget 재시도 없음

## Frame 7
status: built
src: index.html#s7
time: 131.5 to 155.5s
beat: 7/9 02:11 측정: ① internal ALB → 클라우드 Pod 20/20, ② hybrid Pod 20/20 hairpin, ③ NodePort 실패(SNAT, underlay, SG 443만)

## Frame 8
status: built
src: index.html#recD, #vD, #dnote
time: 155.5 to 174s (media 47.5 to 61.375s at 0.75x)
beat: 8/9 녹화: onprem-curl 3, ALB → 10.0.46.5 10.0.51.70, /cloud 3/3, /hybrid 3/3, NodePort FAIL x3 (Failed 행 설명 156s부터)

## Frame 9
status: built
src: index.html#s9
time: 174 to 192s
beat: 9/9 메시지, 녹화 회차 카드, 02:11 측정 카드, 주의 2개
