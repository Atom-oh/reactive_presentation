---
mode: autonomous
message: "overlay와 SNAT 없이 Pod IP가 그대로 보이고, 온프렘 Pod도 PrivateLink로 AWS API를 쓴다"
audience: 아키텍트, 네트워크와 보안 담당자 (L300)
duration: 152
canvas: 1920x1080
---

Single-file build (monolithic `index.html`), same structure as V3 and V4. Recording scenes play `assets/r5-conn.mp4` (symlink to `../../rec/r5-conn.mp4`, 1920x1412) as framework-owned muted `<video>` clips inside an untimed window `#recwin` (inner 1800x850 at 60,146; scale 0.9375, video 1800x1324). Recording A is top aligned; from recording B on the window shows the bottom of the terminal (pan -474px), where the latest output appears. The terminal scroll was measured per recording frame (row-profile shift, table `SCROLL` in the script) so the note labels next to the highlighted lines move up with the terminal. The reconstruction footer is hidden during recording scenes (30 to 108.8 s, contiguous).

## Frame 0
status: built
src: index.html#s0-title
time: 0 to 6s
beat: 제목과 메시지

## Frame 1
status: built
src: index.html#s1
time: 6 to 30s
beat: 1/8 질문, 구성도(클라우드 VPC 10.0.0.0/16: VPC CNI Pod, NAT, STS/S3 endpoint, TGW, 온프렘 172.18.0.0/16: 라우터 route table, hybrid 노드, Pod 172.17.x), 패킷, 답, AWS 지원 범위 밖 경고, VXLAN 유지 시 개념 비교(측정 아님)

## Frame 2
status: built
src: index.html#recA, #vA, #abox
time: 30 to 42.5s (media 0 to 9.375s at 0.75x)
beat: 2/8 녹화: Pod 표(10.0.x 클라우드, 172.17.x hybrid, 172.18.x 노드 IP 설명 상자)와 변수

## Frame 3
status: built
src: index.html#recB, #vB, #lb1, #lb2
time: 42.5 to 60.5s (media 9.4 to 22.9s at 0.75x)
beat: 3/8 녹화: 1) h1a → c1 `server saw 172.17.0.244` (49.7s), 2) c1 → h2 `server saw 10.0.63.165` (58.6s)

## Frame 4
status: built
src: index.html#recC, #vC, #lc1, #lc2
time: 60.5 to 72s (media 22.9 to 29.8s at 0.6x)
beat: 4/8 녹화: 3) 온프렘 socat 서버가 172.17.0.244를 봄, 4) 인터넷은 NAT 43.200.92.63

## Frame 5
status: built
src: index.html#recD, #vD, #ld1, #ld2
time: 72 to 90.4s (media 29.8 to 43.6s at 0.75x)
beat: 5/8 녹화: 5) dig sts, s3 → endpoint ENI 4개, 6) IRSA get-caller-identity(계정 ID 가림), PutObject, GetObject hello-from-irsa-h1

## Frame 6
status: built
src: index.html#recE, #vE, #le1, #le2, #le3, #enote
time: 90.4 to 108.8s (media 43.7 to 57.5s at 0.75x)
beat: 6/8 녹화: 7) h1a → STS ENI 302 허용, hostnet-h1 exit 28 차단, 설명 상자(SNAT 없음 증거, 타임아웃은 대기 줄임으로 짧게 보임), 38 PASS 줄은 10:50 측정 결과 파일로 표시

## Frame 7
status: built
src: index.html#s7
time: 108.8 to 130.8s
beat: 7/8 10:50 측정: 11개 절, 절별 항목 수와 핵심 값, 모두 PASS, 합계 38 PASS 0 FAIL 0 SKIP

## Frame 8
status: built
src: index.html#s8
time: 130.8 to 152s
beat: 8/8 메시지, 고친 세 가지(SG 53, VPC CNI SNAT 제외 172.18.0.0/16, /livez), 주의 3개(AWS 지원 범위 밖, CoreDNS 클라우드에만, S3 DnsOptions AllResolvers)
