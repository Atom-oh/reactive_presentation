# V2 수치 대조표 (영상에 쓰는 값만)

출처가 두 개입니다. 두 실행의 숫자를 섞지 않습니다.

- 출처 1 (비교 실행): 2026-10-15, `~/eks-hybrid-demo/results/compare-20261015-1239.md`, `~/eks-hybrid-demo/RUNBOOK.md` 2절. 시나리오 A, B, C 각 1회. Pod 요청 930m.
- 출처 2 (녹화 실행): 2026-10-18, `videos/rec/r2-bursting.mp4`, `videos/rec/RECORDINGS.md` R2 절, 원본 `~/eks-hybrid-demo/.work/rec/r2-bursting.plain.txt`, `r2-timing.txt`. 시나리오 B 1회. Pod 요청 910m. 12개 warm-up 단계 없음(3 → 15 → 10 → 3).

## 공통 (환경)

| 값 | 영상 위치 | 출처 |
|---|---|---|
| hybrid 호스트 2대, 각 4 vCPU | 1/7 실험 환경, 2/7 노드 상자 | RUNBOOK.md 2절 "비교 결과" 첫 문단 |
| burst NodePool m7i/m6i large, xlarge, 한도 32 vCPU | 1/7, 2/7 클라우드 영역 | 같은 곳 |
| ReplicaSet 스케일 인 순서: cost 낮은 Pod, 복제본이 더 많은 노드의 Pod, 최근 생성 Pod. 배치 위치는 보지 않음 | 1/7 | RUNBOOK.md 2절 "설명할 내용" |
| 시나리오: A 정책 없음, 게이트 끔 / B Kyverno, 게이트 끔 / C Kyverno, 게이트 켬 | 1/7, 5/7, 6/7 | compare-20261015-1239.md "정책" 열 |
| B: Kyverno가 hybrid 노드 Pod에 pod-deletion-cost 부여 / C: Karpenter가 burst 노드 Pod에도 순위(cost) 기록 | 1/7 시나리오 카드 | RUNBOOK.md 2절 설명, 측정 결과 C |
| pod-deletion-cost는 best-effort, 노드 장애나 축출에는 적용 안 됨 | 7/7 | RUNBOOK.md 2절 "설명할 내용" |

## 출처 2: 녹화 실행 (2026-10-18, 시나리오 B, 910m)

| 값 | 영상 위치 | 출처 |
|---|---|---|
| Pod 요청 910m, hybrid에 Pod 8개 | 1/7 환경, 2/7 하단 표기, 녹화 화면 첫 줄 `CPU_REQ=910m` | RECORDINGS.md R2 준비, plain.txt |
| 시작 3개 모두 hybrid(mi-*), COST 1 | 2/7 시작 상태, 3/7 녹화 | plain.txt elapsed 1s |
| 15개로 늘린 뒤 첫 화면(약 5초 뒤)에 NodeClaim 3개(m6i.large 1, m6i.xlarge 2), hybrid 8 Running, 7 Pending | 2/7 칩, 3/7 녹화 | RECORDINGS.md R2 관찰 결과 1 |
| burst Pod 7개 배치: m6i.large(ip-10-0-54-55)에 1, m6i.xlarge(ip-10-0-42-222)에 3, m6i.xlarge(ip-10-0-36-192)에 3 | 2/7 burst 노드 상자 | plain.txt elapsed 40s 표에서 셈 |
| hybrid 노드별 4개, 4개 | 2/7 hybrid 노드 | plain.txt elapsed 13s 표에서 셈 (mi-01c0... 4, mi-067a... 4) |
| 스케일 명령 후 35초에 15개 모두 Ready (hybrid 8 / burst 7) | 2/7 칩, 7/7 녹화 카드 | RECORDINGS.md R2; r2-timing.txt "15 ready at +35s" |
| 10개: hybrid 8 / cloud 2 (ip-10-0-54-55, ip-10-0-36-192), 6초 안에 반영 | 4/7 녹화, 7/7 녹화 카드 | RECORDINGS.md R2; r2-timing.txt "10 reached at +6s" |
| 3개: 모두 hybrid(mi-*), COST 1 | 4/7 녹화, 7/7 녹화 카드 | RECORDINGS.md R2 |
| burst NodeClaim은 3개로 줄인 뒤 약 104초에 모두 사라짐 (녹화 밖에서 확인) | 7/7 녹화 카드 | RECORDINGS.md R2 마지막 항목 |
| burst Pod의 COST는 `<none>` (게이트 끔) | 4/7 머리글 | plain.txt |

## 출처 1: 비교 실행 (2026-10-15, A/B/C 각 1회, 930m)

| 값 | 영상 위치 | 출처 |
|---|---|---|
| Pod 요청 930m, hybrid 8개에서 포화 | 1/7 환경 | compare-20261015-1239.md 제목, 머리 문단 |
| 진행 순서 3, 15, 12(warm-up), 10, 3 | 5/7 부제 | RUNBOOK.md 2절 표 아래 문단 |
| A: 10개일 때 hybrid 6 / cloud 4 / EC2 3, 최종 hybrid 2 / cloud 1, 정리 123초 | 5/7 A행, 6/7 표, 7/7 | compare-20261015-1239.md A행 |
| B: 10개일 때 hybrid 8 / cloud 2 / EC2 4, 최종 hybrid 3 / cloud 0, 정리 118초 | 5/7 B행, 6/7 표, 7/7 | compare-20261015-1239.md B행 |
| C: 10개일 때 hybrid 8 / cloud 2 / EC2 3, 최종 hybrid 3 / cloud 0, 정리 87초 | 5/7 C행, 6/7 표, 7/7 | compare-20261015-1239.md C행 |
| NodeClaim 1초, 1초, 2초 / 15개 Ready 37초, 38초, 37초 | 6/7 표 | compare-20261015-1239.md |
| A에서 온프렘(hybrid) Pod가 먼저 제거됨 | 5/7 A행 강조 | RUNBOOK.md 2절 측정 결과 A |
| EC2 대수는 스케일 인 20초 후 살아 있는 NodeClaim 기준 | 6/7 각주 | RUNBOOK.md 2절 표 아래 문단 |
| 시나리오별 1회 실행, 작은 차이는 오차, 인용 전 반복 측정 필요 | 6/7 각주, 7/7 | RUNBOOK.md 2절 |

## 예시 표기와 압축

- 5/7 A/B/C 행: Pod 수(hybrid/cloud)와 10개일 때 EC2 대수만 실측입니다. 15개일 때 burst 노드 4대와 노드별 Pod 위치(2, 2, 2, 1), 어느 노드에서 Pod가 빠졌는지는 예시이며 화면 부제에 "노드별 위치는 예시"로 표시합니다. 4대는 B의 10개 시점 EC2 4대와 모순되지 않는 최소 대수입니다. 2026-10-15 실행의 실제 노드 구성은 기록되지 않았습니다.
- 2/7 스케일 아웃 그림은 녹화 실행의 실제 배치(노드 3대, 1/3/3)를 따릅니다. 시간 축은 압축했고, 화면의 초 값(약 5초, 35초)만 실측입니다.
- 녹화 장면은 0.5배속으로 재생하고 "대기 구간 줄임, 0.5배속"을 표시합니다. 녹화 화면의 `elapsed Ns`는 실제 경과 시간입니다. 4/7에서 `--replicas=10` 입력 줄이 화면 아래에 있는 약 8초 동안 녹화 화면을 위로 89px 옮깁니다(머리 두 줄이 잠시 가려짐).
- 계정 ID, 비밀 값은 녹화와 화면 어디에도 없습니다(RECORDINGS.md: R2 가린 값 0곳). Pod 이름, 노드 이름(mi-*, ip-*)은 녹화에 그대로 보입니다.
