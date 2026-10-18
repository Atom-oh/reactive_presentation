---
mode: autonomous
message: "Gateway 리더가 죽어도 3~5초 안에 스탠바이가 경로를 넘겨받는다"
audience: 아키텍트와 의사결정자
duration: 178
canvas: 1920x1080
---

Single-file build (monolithic `index.html`). One persistent diagram clip serves the diagram scenes; it, the probe grid and the reconstruction footer are set to opacity 0 while a recording scene is on screen. Recording scenes play `assets/r1-failover.mp4` (symlink to `../rec/r1-failover.mp4`) as framework-owned muted `<video>` clips with `data-media-start` and a constant `data-playback-rate`.

## Frame 1
status: built
src: index.html#s1-title, #h1, #diagram, #s1-notes
time: 0 to 24s
beat: 제목과 메시지, 환경 구성도 (VPC, Gateway 2개, TGW, 시뮬레이션 온프레미스, Hybrid Pod)

## Frame 2
status: built
src: index.html#recA, #vA
time: 24 to 43.6s (media 0 to 9.8s at 0.5x, top aligned)
beat: 녹화: Pod 2개, Lease HOLDER, VPC 라우트 172.17.0.0/16 -> eni-0dbc9737395c577e6

## Frame 3
status: built
src: index.html#h2, #diagram, #s2-notes, #probe-clip
time: 43.6 to 66s
beat: 평상시 경로, 리더 Gateway A (ip-10-0-41-152), 요청 격자 10칸 OK

## Frame 4
status: built
src: index.html#recB, #vB
time: 66 to 91.8s (media 9.8 to 22.7s at 0.5x, bottom aligned)
beat: 녹화: failover.sh 실행, T0 06:28:09, 새 리더 after 5s, 결과 블록 (5s, 2 / 60, traffic gap 5s, ENI 교체, yes)

## Frame 5
status: built
src: index.html#h3, #tm0, #diagram, #s3-notes
time: 91.8 to 108s
beat: 리더 Pod 삭제, 요청 2개 실패 (2 / 60)

## Frame 6
status: built
src: index.html#h4, #tm5, #diagram, #s4-notes
time: 108 to 128s
beat: T0 + 5초 Lease 전환, Gateway B 새 리더, 라우트가 새 리더 ENI로, 요청 정상

## Frame 7
status: built
src: index.html#recC, #vC
time: 128 to 147.5s (media 22.7 to 34.4s at 0.6x, bottom aligned)
beat: 녹화: 전환 후 Lease HOLDER ip-10-0-57-129, rollout 완료, Pod 2개 Running

## Frame 8
status: built
src: index.html#s5
time: 147.5 to 178s
beat: 이전 측정 3회 카드(3초 1/60, 5초 1/60, 5초 2/45 최소 권한 IAM)와 녹화 회차 카드(5초 2/60), 메시지
