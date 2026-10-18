# V4 수치 대조표 (hybrid GPU 추론)

실행은 2026-10-15 한 번뿐이며 GPU 호스트는 그 뒤 제거했습니다. 녹화가 없어 영상 전체가 실측 결과 재구성입니다. 화면의 모든 장면 하단에 "실측 결과 재구성 (2026-10 시뮬레이션 환경)"을 표기하고, 결과 장면 머리글에 "실행 결과 재구성, 2026-10-15 실행"을 표기합니다.

| 값 | 출처 |
|---|---|
| GPU 호스트 g6.xlarge, NVIDIA L4 23 GB, 시뮬레이션 온프렘 VPC, 2026-10-15 한 번 실행 후 제거 | ~/eks-hybrid-demo/RUNBOOK.md 3절, demo3-gpu/README.md, 덱 05-live-demo.md Slide 7 |
| EC2를 hybrid 노드로 쓰는 것은 프로덕션 미지원 | RUNBOOK.md 3절 |
| taint `nvidia.com/gpu=Exists:NoSchedule`, label `node-role/gpu=true` | RUNBOOK.md 3절, demo3-gpu/README.md |
| NVIDIA device plugin v0.17.1, hybrid GPU 노드에만 배포 | demo3-gpu/device-plugin.yaml 19행, 덱 Slide 7 |
| allocatable `nvidia.com/gpu` 1 | RUNBOOK.md 3절 기대 결과, demo3-gpu/verify.sh, 덱 Slide 7 |
| vLLM v0.19.1, 모델 Qwen/Qwen2.5-0.5B-Instruct | RUNBOOK.md 3절 측정값 |
| inference Pod 컨테이너 1개(istio-proxy 없음), hostNetwork 꺼짐, toleration, nodeSelector, limits nvidia.com/gpu 1 | demo3-gpu/inference.yaml, verify.sh, RUNBOOK.md 3절 |
| 클라우드 Pod(system 노드 Job)가 `inference.gpu-demo.svc` 호출, gateway 경로, elapsed 약 1초(모델 로드 후) | demo3-gpu/client.yaml, RUNBOOK.md 3절 기대 결과, 덱 Slide 7 |
| vLLM 이미지 다운로드 4분 28초(NAT 경로, 첫 시작) | RUNBOOK.md 3절, KNOWN-ISSUES.md 데모 3 |
| 드라이버와 container toolkit은 호스트에 직접 설치(AWS 블로그는 이미지 포함 가정) | RUNBOOK.md 3절, KNOWN-ISSUES.md 데모 3 |
| 모델 캐시는 hostPath(재시작 시 재다운로드 방지) | demo3-gpu/inference.yaml |

## 화면 구성 메모

- 장면 1(왜 온프렘 GPU)과 장면 3(호출 흐름)은 개념도입니다. 숫자는 위 표의 값만 씁니다.
- 장면 5의 두 막대는 4분 28초(268초)와 약 1초의 길이 비례입니다(화면에 표시).
- 가짜 터미널은 쓰지 않습니다. 결과는 카드로만 보여 줍니다.
- 화면에 계정 ID, 인스턴스 ID, 비밀 값 없음.
