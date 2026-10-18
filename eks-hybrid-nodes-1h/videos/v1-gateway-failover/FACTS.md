# V1 수치 대조표 (영상에 쓰는 값만)

## 이전 측정 3회 (2026-10-15), 결과 장면 카드 1~3

| 값 | 영상 위치 | 출처 |
|---|---|---|
| Lease 전환 3초, 5초, 5초 | 8/8 카드 1~3 | ~/eks-hybrid-demo/RUNBOOK.md 1절 마지막 문단; eks-hybrid-nodes/05-live-demo.md 표 |
| 1초 간격 요청 실패 60개 중 1, 60개 중 1, 45개 중 2 | 8/8 카드 1~3 | RUNBOOK.md 1절(실패 1, 1, 2회); 분모 60/60/45는 eks-hybrid-nodes/05-live-demo.md 표 (Deep Dive 5부) |
| 3회차는 최소 권한 IAM | 8/8 카드 3 | RUNBOOK.md 1절; KNOWN-ISSUES.md "게이트웨이 IAM 권한을 최소화했습니다" |
| AWS 문서 예상 전환 3~5초, 보장값 아님 | 제목, 8/8 | eks-hybrid-nodes/05-live-demo.md 노트 출처 (hybrid-nodes-gateway-overview) |

## 녹화 회차 (2026-10-18, R1), 녹화 장면과 구성도 장면 3~6, 카드 4

| 값 | 영상 위치 | 출처 |
|---|---|---|
| 전환 전 리더 Pod `...-nlbfq`, 노드 ip-10-0-41-152, 라우트 `172.17.0.0/16 -> eni-0dbc9737395c577e6` | 2/8 녹화, 3/8 노트 1 | videos/rec/RECORDINGS.md R1 관찰 결과 |
| 리더 Pod 삭제 06:28:09 (T0) | 4/8 녹화, 5/8 노트 1, T0 배지 | RECORDINGS.md R1 |
| 새 리더 `...-tkwcb`, 노드 ip-10-0-57-129, Lease 인계 5초 | 4/8 녹화, 6/8 배지 "T0 + 5초", 노트 1, 카드 4 | RECORDINGS.md R1 |
| 실패한 probe 2 / 60 (1초 간격), 첫 실패부터 마지막 실패까지 5초 | 4/8 녹화, 5~6/8 요청 격자와 노트, 카드 4 | RECORDINGS.md R1 |
| 라우트 ENI `eni-0dbc9737395c577e6 -> eni-021433ec3aa9dbb0f`, 새 리더 ENI와 일치: yes | 4/8 녹화, 6/8 라우트 교체 | RECORDINGS.md R1 |
| 전환 후 Lease HOLDER ip-10-0-57-129..._uuid, Deployment rolled out, Pod 2개 Running (새 Pod `...-5hvsz`) | 7/8 녹화 | RECORDINGS.md R1 |
| 대기 구간 줄임 (출력 없는 2초 넘는 구간을 2초로) | 녹화 장면 표시 | RECORDINGS.md 공통 사항 |
| 계정 ID는 `************`로 가려짐, ENI ID와 Pod 이름은 실제 값 | 녹화 장면 | RECORDINGS.md 공통 사항 |

## 공통 (구성도)

| 값 | 영상 위치 | 출처 |
|---|---|---|
| namespace `eks-hybrid-nodes-gateway`, Lease `hybrid-gateway-leader`, Gateway Pod 2개 | 1/8 노트, 녹화 | demo1-gateway/lib.sh `NS=`; eks-hybrid-nodes/02-networking-gateway.md 717, 854행; 녹화 화면 |
| Lease HOLDER 형식 노드이름_uuid | 3/8 노트 2 | demo1-gateway/lib.sh 3행; 녹화 화면 |
| 리더 삭제 전 10초 동안 요청 (`sleep 10`), 측정 60초 (`DURATION=60`) | 3/8 격자 10칸, 격자 60칸 | demo1-gateway/failover.sh 5, 13행 |
| VPC 10.0.0.0/16, 온프레미스 노드 172.18.0.0/16, Hybrid Pod 172.17.0.0/16 | 1~6/8 구성도 | ~/eks-hybrid-demo/env/demo.env.example 4~6행 |
| 시뮬레이션: 온프레미스는 TGW로 연결한 두 번째 VPC (실환경 DX/VPN) | 1/8 노트 3 | RUNBOOK.md 머리말 |

## 재구성 화면의 한계

- 요청 격자에서 실패 칸의 위치(11번째, 15번째)는 실측 위치가 아닙니다. 화면에 따로 "예시" 표시를 하지 않았으므로, 개수(2 / 60)와 간격(첫 실패부터 마지막 실패까지 5초)만 실측값이고 위치는 그 값에 맞춘 배치라는 점을 발표 노트에서 설명합니다. (이전 버전 FACTS.md는 이 위치가 화면에 "예시"로 표시된다고 적었는데, 실제로 화면에 그런 표시는 없었습니다.)
- 구성도 장면의 시간은 압축되어 있습니다. 배지는 T0와 T0 + 5초만 보여 주고 흐르는 시계는 없습니다.
- 구성도에는 더 이상 예시 Pod/ENI 이름이 없습니다. 실제 이름과 ENI ID는 녹화 장면에서 보입니다.
