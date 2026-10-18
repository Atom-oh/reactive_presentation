---
mode: autonomous
message: "온프렘 GPU 노드도 같은 클러스터의 Service로 클라우드에서 호출된다"
audience: 아키텍트와 의사결정자
duration: 134
canvas: 1920x1080
---

Single-file build (monolithic `index.html`), same structure as V1 to V3. Recording scenes play `assets/r4-gpu.mp4` (symlink to `../../rec/r4-gpu.mp4`, 1920x1506) as framework-owned muted `<video>` clips inside an untimed window `#recwin` (1800x850 at 60,146, scale 0.9375). The inner pan div moves up as output grows so the latest lines stay visible. The reconstruction footer is hidden during recording scenes.

## Frame 0
status: built
src: index.html#s0-title
time: 0 to 6s
beat: 제목과 메시지

## Frame 1
status: built
src: index.html#s1
time: 6 to 22s
beat: 1/7 왜 온프렘 GPU: 데이터 위치, 기존 GPU, 이 데모의 GPU 호스트(g6.xlarge, L4 23 GB, 2026-10-15 실행, 2026-10-18 다시 조인해 녹화, 녹화 뒤 제거)

## Frame 2
status: built
src: index.html#s2
time: 22 to 40s
beat: 2/7 구성: taint, label, device plugin v0.17.1(allocatable 1), 추론 Pod(vLLM v0.19.1, Qwen2.5-0.5B-Instruct, 컨테이너 1개, hostNetwork 끔)

## Frame 3
status: built
src: index.html#recA, #vA
time: 40 to 63.2s (media 0.5 to 17.9s at 0.75x)
beat: 3/7 녹화: 노드별 GPU(GPU 노드만 1), taint와 allocatable, Pod Running 172.17.1.161, 컨테이너 server 1개와 hostNetwork false, nvidia-smi L4 580.178.04

## Frame 4
status: built
src: index.html#s3
time: 63.2 to 79s
beat: 4/7 호출 흐름: 클라우드 Job → Service inference.gpu-demo.svc → gateway 경로 → vLLM Pod, 응답 1초 미만(2026-10-18 녹화 회차)

## Frame 5
status: built
src: index.html#recB, #vB
time: 79 to 101.7s (media 17.9 to 34.925s at 0.75x)
beat: 5/7 녹화: Service와 EndpointSlice, verify.sh OK 4개와 elapsed_seconds=0, client Job 로그(응답 JSON)

## Frame 6
status: built
src: index.html#s5
time: 101.7 to 118s
beat: 6/7 준비할 것: 드라이버와 toolkit 호스트 설치(10-18 2분 59초), 이미지 4분 35초(10-18, 9.6 GB)와 4분 28초(10-15), 275초 대 1초 미만 막대

## Frame 7
status: built
src: index.html#s6
time: 118 to 134s
beat: 7/7 메시지, 구성 카드, 결과(2026-10-18 녹화) 카드, 주의 2개
