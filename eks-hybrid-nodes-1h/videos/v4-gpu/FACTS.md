# V4 수치 대조표 (hybrid GPU 추론)

실행은 두 번입니다. 두 회차의 값은 섞지 않고, 화면과 이 표에서 회차를 붙여 씁니다.

- 실행 1: 2026-10-15, 녹화 없음. 출처 ~/eks-hybrid-demo/RUNBOOK.md 3절, KNOWN-ISSUES.md 데모 3
- 실행 2: 2026-10-18 녹화 회차(R4, 11:21:29 UTC 시작). 출처 videos/rec/RECORDINGS.md R4, task-4c-report.md. GPU 호스트는 녹화를 위해 다시 만들고 조인했으며 녹화 뒤 바로 제거

녹화 장면(3/7, 5/7)은 `assets/r4-gpu.mp4`(심볼릭 링크, `../../rec/r4-gpu.mp4`)를 그대로 보여 주며 하단에 "실측 터미널 녹화 (2026-10-18, 시뮬레이션 환경)", 머리글 오른쪽에 "실제 터미널 녹화, 대기 구간 줄임, 0.75배속"을 표기합니다. 나머지 장면은 "실측 결과 재구성 (2026-10 시뮬레이션 환경)"입니다.

## 공통(구성, 두 회차 같음)

| 값 | 출처 |
|---|---|
| GPU 호스트 g6.xlarge, NVIDIA L4 23 GB, 시뮬레이션 온프렘 VPC | RUNBOOK.md 3절, demo3-gpu/README.md, RECORDINGS.md R4 |
| EC2를 hybrid 노드로 쓰는 것은 프로덕션 미지원 | RUNBOOK.md 3절 |
| taint `nvidia.com/gpu=Exists:NoSchedule`, label `node-role/gpu=true` | RUNBOOK.md 3절, demo3-gpu/README.md, task-4c-report.md(녹화 회차에서도 확인) |
| NVIDIA device plugin v0.17.1, hybrid GPU 노드에만 배포 | demo3-gpu/device-plugin.yaml 19행 |
| vLLM v0.19.1, 모델 Qwen/Qwen2.5-0.5B-Instruct | RUNBOOK.md 3절, RECORDINGS.md R4 |
| toleration, nodeSelector, limits nvidia.com/gpu 1, 모델 캐시 hostPath | demo3-gpu/inference.yaml |
| 드라이버와 container toolkit은 호스트에 직접 설치(AWS 블로그는 이미지 포함 가정), 실서버는 OS 이미지 또는 GPU Operator | RUNBOOK.md 3절, KNOWN-ISSUES.md 데모 3, demo3-gpu/README.md |

## 실행 1: 2026-10-15 (녹화 없음)

| 값 | 화면 | 출처 |
|---|---|---|
| vLLM 이미지 첫 다운로드 4분 28초(NAT 경로) | 6/7 카드 보조 줄 "2026-10-15 실행: 4분 28초", 7/7 주의 "(10-15)" | RUNBOOK.md 3절, KNOWN-ISSUES.md 데모 3 |
| 응답 elapsed 약 1초(모델 로드 후) | 영상에서는 쓰지 않음(덱 노트에서만 2026-10-15 값으로 표기) | RUNBOOK.md 3절 |

## 실행 2: 2026-10-18 녹화 회차 (R4)

| 값 | 화면 | 출처 |
|---|---|---|
| 드라이버와 toolkit 설치 2분 59초(재부팅 포함, 녹화 밖) | 6/7 카드 | RECORDINGS.md R4 녹화 전 준비 |
| nodeadm 조인 50초, Ready까지 약 20초 더(녹화 밖) | 영상에 없음, 덱 노트 | RECORDINGS.md R4 |
| vLLM 이미지 다운로드 4분 35초(9.6 GB, NAT 경로), 컨테이너 시작 뒤 Ready까지 약 2분(녹화 밖) | 6/7 카드와 막대(275초) | RECORDINGS.md R4 |
| GPU 노드 `mi-01c761bc7d91d2da3`만 GPU 1, 다른 hybrid 2대와 클라우드 4대는 `<none>` | 3/7 녹화 | RECORDINGS.md R4 관찰 결과 |
| taint `nvidia.com/gpu=Exists:NoSchedule`, Capacity/Allocatable 1, 할당 1/1 | 3/7 녹화 | RECORDINGS.md R4 |
| inference Pod 1개 Running, IP 172.17.1.161, 컨테이너 `server` 1개, `istio-proxy` 없음, `hostNetwork=false` | 3/7 녹화, 2/7과 7/7 카드 | RECORDINGS.md R4 |
| nvidia-smi `NVIDIA L4, 580.178.04, 18722 MiB / 23034 MiB` | 3/7 녹화, 7/7 카드 "NVIDIA L4" | RECORDINGS.md R4 |
| Service ClusterIP 172.16.250.14:80, EndpointSlice 172.17.1.161:8000 | 5/7 녹화 | RECORDINGS.md R4 |
| verify.sh OK 4개, `elapsed_seconds=0` = 1초 미만(busybox `date +%s` 초 단위) | 5/7 녹화, 4/7 카드 "1초 미만", 6/7 막대 "1초 미만", 7/7 카드 | RECORDINGS.md R4, task-4c-report.md |
| client Job Pod는 클라우드 노드 ip-10-0-40-102에서 실행 | 4/7 상자 "클라우드 노드" | RECORDINGS.md R4 |
| 응답 문장(실행마다 다름, max_tokens 32, 이모지 일부만 그려짐) | 5/7 녹화 | RECORDINGS.md R4 |

## 화면 구성 메모

- 녹화 3/7: media 0.5~17.9초를 0.75배속(영상 40~63.2초). 녹화 5/7: media 17.9~34.925초를 0.75배속(영상 79~101.7초). 녹화 원본은 1920x1506이며 창(1800x850)에 0.9375배로 넣고 최신 출력이 보이도록 위로 이동합니다(녹화 글자 약 26px).
- 녹화 첫 줄의 "# Demo 3: hybrid GPU inference"는 데모 저장소의 이름(demo3-gpu)입니다. 덱과 영상에서는 네 번째 영상이라 "데모 4"로 부릅니다.
- 4/7 호출 흐름은 개념도입니다. 응답 카드는 2026-10-18 녹화 회차 값(1초 미만)입니다.
- 6/7 두 막대는 4분 35초(275초)와 1초 미만의 길이 비례이며 둘 다 2026-10-18 녹화 회차 값입니다(화면에 표시).
- 화면에 계정 ID(녹화에서 `************`로 가림), 인스턴스 ID, 비밀 값 없음. mi ID, Pod 이름, private IP, ClusterIP는 녹화 그대로입니다.
