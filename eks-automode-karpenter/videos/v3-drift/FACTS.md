# V3 수치 대조표 (영상에 쓰는 값만)

출처는 하나입니다: `videos/rec/RECORDINGS.md` 공통 절과 "D3: Drift 교체" 절 (2026-10-20, 녹화 시작 14:19:52 UTC, 1회 실행). 녹화 화면 자체는 `assets/d3-drift.mp4`(`../rec/d3-drift.mp4` 심볼릭 링크)를 그대로 재생합니다.

## 공통 (환경)

| 값 | 영상 위치 | 출처 |
|---|---|---|
| 클러스터 akd-auto (EKS Auto Mode), akd-karp (직접 설치 Karpenter), EKS 1.37 | 하단 표기, 1/5 카드 | RECORDINGS.md 머리 문단 |
| Karpenter controller 1.15.0 | 1/5 akd-karp 카드 | RECORDINGS.md 공통, 환경 값 |
| Auto Mode 노드 OS Bottlerocket (AMI는 사용자가 고르지 않음) | 1/5 akd-auto 카드, 5/5 카드 3 | RECORDINGS.md 공통, 환경 값; BRIEF.md Scenes (2) |
| demo NodePool budget `nodes: "1"` (두 클러스터) | 1/5 하단 문장, 2/5 녹화 콜아웃 1, 3/5 제목, 5/5 카드 2 | RECORDINGS.md 공통, NodePool 설정; 녹화 화면 `[{"nodes":"1"}]` |
| 모든 측정은 1회 실행 결과, 벤치마크 아님 | 5/5 주의 막대 | RECORDINGS.md 머리 문단 |
| 2초 넘는 무출력 구간은 2초로 줄임 (화면의 elapsed, +Ns는 실제 시간) | 2/5 "대기 구간 줄임" 표시 | RECORDINGS.md 공통, 변환 |

## D3

| 값 | 영상 위치 | 출처 |
|---|---|---|
| 시작: 클러스터마다 demo 노드 2대 (2a, 2b), Pod 6개, zone topology spread, minDomains 2 | 1/5 시작 상태 패널 | RECORDINGS.md D3 첫 항목 |
| akd-karp: EC2NodeClass `amiSelectorTerms` alias `al2023@v20261003` 에서 `al2023@v20261012` 로 | 1/5 akd-karp 카드 | RECORDINGS.md D3 둘째 항목 |
| akd-auto: NodeClass `advancedCompute.kubelet.maxPods: 64` 추가 | 1/5 akd-auto 카드 | 같은 곳 |
| 패치 직후 두 클러스터 모두 기존 NodeClaim 2개 `Drifted=True` | 1/5 노드 상자와 하단 문장, 2/5 콜아웃 2 | RECORDINGS.md D3 셋째 항목 |
| 교체 순서 Launch, Terminate, Launch, Terminate (budget 1) | 2/5 콜아웃 3, 3/5 타임라인 | RECORDINGS.md D3 넷째 항목 |
| akd-auto 14:20:12 / 14:20:30 / 14:20:45 / 14:21:00 | 3/5 akd-auto 레인 | 같은 곳 |
| akd-karp 14:20:10 / 14:20:46 / 14:20:57 / 14:21:27 | 3/5 akd-karp 레인 | 같은 곳 |
| 완료 (기존 NodeClaim 0, 6/6 Running): akd-auto +98초, akd-karp +127초 | 2/5 콜아웃 4, 3/5 완료 상자, 5/5 주의 막대 | RECORDINGS.md D3 다섯째 항목; 녹화 화면 `done +98s`, `done +127s` |
| akd-karp 새 노드 AMI `amazon-eks-node-al2023-x86_64-standard-1.37-v20261012` | 4/5 첫 카드 | RECORDINGS.md D3 여섯째 항목 |
| akd-karp 시작 시 AMI v20261003 | 4/5 첫 카드 오른쪽 | RECORDINGS.md 공통, 환경 값 |
| akd-auto 새 노드 `capacity.pods` 56, 설정 64, 실제값 = min(설정값, 인스턴스 IP 수, 110) | 4/5 akd-auto 카드 | RECORDINGS.md D3 여섯째 항목 |
| 같은 EC2NodeClass를 쓰는 spot NodePool 노드도 Drift 교체 (spot-8wplw 에서 spot-89g4w) | 4/5 spot 카드 | RECORDINGS.md D3 마지막 항목 |

## 표기와 압축

- 1/5의 노드 상자는 zone(2a, 2b)만 표시합니다. 인스턴스 타입과 노드별 Pod 수는 재구성 화면에 쓰지 않습니다(녹화 화면에는 그대로 보임).
- 3/5 타임라인의 시간 축은 14:20:00부터 14:21:30까지(UTC)이고, 점 위치는 RECORDINGS.md의 시각 그대로입니다. 완료(+98초, +127초)는 축 위에 찍지 않고 별도 상자로 둡니다. 녹화 화면 머리줄에 `patched at +11s`와 `done +98s`가 함께 나오므로 +N초의 기준점을 화면에서 따로 설명하지 않습니다.
- 녹화 장면(29 to 98.8초)은 media 2 to 36.9초를 0.5배속으로 재생합니다. 녹화는 1 fps이므로 한 화면이 2초씩 보입니다. 패치 명령 줄이 창 아래로 내려가는 media 6 to 13초 동안 녹화 화면을 위로 230px 옮기고, 이벤트 표가 출력되는 media 34, 35초에 200px, 410px 옮깁니다(머리 몇 줄이 잠시 가려짐).
- 4/5의 "maxPods는 상한" 문장과 5/5의 권고(버전 고정, budget과 PDB)는 해석 문장이며 새 숫자가 없습니다.
- 계정 ID는 녹화와 화면 어디에도 없습니다(RECORDINGS.md: 12자리 계정 ID 패턴 0건). 노드 이름, 인스턴스 ID, private IP는 녹화에 그대로 보입니다.
