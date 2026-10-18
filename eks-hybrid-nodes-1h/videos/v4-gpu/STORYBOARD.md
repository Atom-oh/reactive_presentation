---
mode: autonomous
message: "온프렘 GPU 노드도 같은 클러스터의 Service로 클라우드에서 호출된다"
audience: 아키텍트와 의사결정자
duration: 130
canvas: 1920x1080
---

Single-file build (monolithic `index.html`), same layout system as V1 to V3. No recording: every scene is a reconstruction and keeps the reconstruction footer.

## Frame 0
status: built
src: index.html#s0-title
time: 0 to 6s
beat: 제목과 메시지

## Frame 1
status: built
src: index.html#s1
time: 6 to 26s
beat: 1/6 왜 온프렘 GPU: 데이터 위치, 기존 GPU, 이 데모의 GPU 호스트(g6.xlarge, L4 23 GB, 2026-10-15 실행 후 제거)

## Frame 2
status: built
src: index.html#s2
time: 26 to 50s
beat: 2/6 구성: taint, label, device plugin v0.17.1(allocatable 1), 추론 Pod(vLLM v0.19.1, Qwen2.5-0.5B-Instruct, 컨테이너 1개, hostNetwork 끔)

## Frame 3
status: built
src: index.html#s3
time: 50 to 74s
beat: 3/6 호출 흐름: 클라우드 Job → Service inference.gpu-demo.svc → gateway 경로 → vLLM Pod, 응답 약 1초

## Frame 4
status: built
src: index.html#s4
time: 74 to 96s
beat: 4/6 결과 카드 4개(실행 결과 재구성, 2026-10-15 실행)

## Frame 5
status: built
src: index.html#s5
time: 96 to 114s
beat: 5/6 준비할 것: 드라이버와 toolkit 호스트 설치, 이미지 4분 28초 사전 다운로드, 268초 대 1초 막대

## Frame 6
status: built
src: index.html#s6
time: 114 to 130s
beat: 6/6 메시지, 구성 카드, 결과 카드, 주의 2개
