---
mode: autonomous
message: "Gateway 리더가 죽어도 3~5초 안에 스탠바이가 경로를 넘겨받는다"
audience: 아키텍트와 의사결정자
duration: 150
canvas: 1920x1080
---

Single-file build (monolithic `index.html`): scenes 1 to 4 share one persistent diagram, so they are inline clips, not sub-compositions.

## Frame 1
status: built
src: index.html#s1
time: 0 to 24s
rules: title card fade-up, staggered build of diagram boxes
beat: 제목과 메시지, 이어서 VPC, Gateway 2개, TGW, 시뮬레이션 온프레미스, Hybrid Pod 구성도가 차례로 나타남

## Frame 2
status: built
src: index.html#s2
time: 24 to 52s
rules: packet flow loop, terminal type-in, grid fill
beat: 라우트 172.17.0.0/16 → 리더 ENI, 패킷이 리더를 지나 Hybrid Pod로, kubectl 출력(Lease HOLDER 노드이름_uuid), 요청 격자 10칸 OK

## Frame 3
status: built
src: index.html#s3
time: 52 to 80s
rules: danger state change, timer count
beat: 리더 Pod 삭제(T0), 패킷이 라우트에서 막힘, 요청 1칸 FAIL, 타이머 T0 + 0~3초

## Frame 4
status: built
src: index.html#s4
time: 80 to 115s
rules: badge crossfade, route row swap highlight, packet flow resumes
beat: 스탠바이가 Lease 획득(3초), 라우트가 새 리더 ENI로, 요청 복구, failover.sh 결과(3s, 1 / 60)

## Frame 5
status: built
src: index.html#s5
time: 115 to 150s
rules: staggered result cards, message line
beat: 3회 측정 카드(3초 1/60, 5초 1/60, 5초 2/45 최소 권한 IAM)와 메시지
