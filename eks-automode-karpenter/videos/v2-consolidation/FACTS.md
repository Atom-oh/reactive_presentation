# V2 수치 대조표 (영상에 쓰는 값만)

출처: `../rec/RECORDINGS.md` "공통 사항"과 "D2: 스케일 인 후 consolidation" 절, 그리고 녹화 파일 `../rec/d2-consolidation.mp4` 화면 자체. 새 숫자를 만들지 않습니다. 계정 ID는 화면 어디에도 없습니다(RECORDINGS.md: 4개 녹화 모두 치환 0건).

두 실행을 섞지 않습니다.
- 녹화 회차: 2026-10-20 14:05 UTC 시작(녹화 시작 14:04:59). 영상의 3, 4, 5번째 장면과 녹화 장면의 모든 숫자.
- 앞선 회차: 13:55, 녹화 중단으로 미사용. 정리 장면의 점선 카드 한 곳에만 표시.

## 공통 (환경, 라이브 확인)

| 값 | 영상 위치 | 출처 |
|---|---|---|
| EKS 1.37, akd-auto(EKS Auto Mode), akd-karp(직접 설치 Karpenter) | 하단 녹화 표기, 1장 카드 제목 | RECORDINGS.md 머리 문단 |
| Karpenter controller 1.15.0 | 1장 akd-karp 카드 제목 | 공통 사항 "환경 값" |
| 두 클러스터 모두 demo NodePool에 consolidationPolicy 지정 안 함 | 1장 부제, 녹화 | 공통 사항 "NodePool 설정"; 녹화 주석 `policy was not set in either manifest` |
| Auto Mode: Balanced, expireAfter 336h | 1장, 3장 lane, 제목, 정리 | 공통 사항 "NodePool 설정" |
| Karpenter: WhenEmptyOrUnderutilized, expireAfter 720h | 1장, 3장 lane, 제목, 정리 | 같은 곳 |
| 둘 다 consolidateAfter 30s, budget nodes: "1", on-demand, c/m/r | 1장 칩 | 같은 곳 (generation > 5, amd64는 화면에서 생략) |
| Auto Mode built-in general-purpose, system도 Balanced, 30s, 336h, budget 10% | 1장 하단 | 같은 곳 |
| 워크로드 replica당 requests 1 vCPU / 1.5Gi | 1장 칩 | 공통 사항 "워크로드" |
| 대기 구간 줄임(2초 넘는 무출력은 2초로), 화면 elapsed는 실제 시간 | 녹화 장면 표기 | 공통 사항 "변환" |
| 모든 측정은 1회 실행 결과, 벤치마크 아님 | 정리 주의 | RECORDINGS.md 머리 문단 |

## 녹화 회차 (2026-10-20 14:05 UTC)

| 값 | 영상 위치 | 출처 |
|---|---|---|
| replicas 10 → 4 | 3장 부제, 녹화 헤더 | D2 첫 항목 |
| 시작 시 두 클러스터 모두 c7i-flex.4xlarge 1대 | 3장 lane 기존 노드 | D2 첫 항목 |
| 두 클러스터 모두 c7i-flex.2xlarge로 replace, Pod 4개 이동 | 3장 lane, 정리 녹화 카드 | D2 "녹화 회차(14:05)" |
| 처음 이동한 Pod 관찰 Auto Mode +67초, Karpenter +75초 | 3장 lane 오른쪽 | D2 "녹화 회차(14:05)" |
| 이벤트 순서(양쪽 같음): DisruptionLaunching(새 NodeClaim), 새 노드 Ready, DisruptionTerminating(기존), Evicted 4개 | 3장 이벤트 상자 4개 | D2 "이벤트 순서" |
| `ConsolidationCandidate ... replace ... -> [1 replacement] (savings: $0.38)` | 4장 이벤트 카드, $0.38 타일 | D2 "Auto Mode 이벤트" |
| `ConsolidationApproved score 0.50 >= threshold 0.50 (k: 2, savings 50.0%, disruption 100.0%)` | 4장 이벤트 카드, 타일 3개, 제목, 정리 | D2 "Auto Mode 이벤트" |

## 앞선 회차 (13:55, 미사용)

| 값 | 영상 위치 | 출처 |
|---|---|---|
| 같은 결과(4xlarge → 2xlarge, 4개 이동) | 정리 점선 카드 "결과는 같음" | D2 "앞선 회차" |
| Karpenter는 scale-in 약 1분 뒤, Auto Mode는 약 5분 30초 뒤 실행 | 정리 점선 카드 | D2 "앞선 회차" |
| 두 회차의 시점이 달라 정책 간 속도 차이로 해석하지 않음 | 정리 주의 첫 줄 | D2 "앞선 회차" 굵은 글씨 |

## 표기와 압축

- 3장 그림의 노드 상자와 Pod 점 이동은 재구성입니다. 노드 종류, Pod 수, 이벤트 순서만 실측이고 애니메이션 시간 축은 압축했습니다.
- 4장 막대는 이벤트 값(50.0%, 100.0%, 0.50 / 0.50)을 길이로 옮긴 것입니다. 점수 계산식은 화면에 쓰지 않았습니다. $0.38의 단위(시간당 등)는 기록에 없으므로 표기하지 않습니다.
- "점수 표기는 Auto Mode 이벤트": RECORDINGS.md는 점수 이벤트를 Auto Mode 쪽에서만 기록합니다. Karpenter에 점수 이벤트가 없다고 단정하지 않았습니다.
- 녹화 장면은 media 2초부터 36.5초까지 0.5배속(69초)으로 재생합니다. 녹화 mp4는 1 fps라 화면이 2초 단위로 바뀝니다. 창 높이 840px에서 원본 하단 빈 영역(약 300px)이 잘립니다.
- 녹화의 akd-karp 이벤트 목록 첫 줄(14:02:38 demo-5b7t7)은 녹화 회차 이전 이벤트로 보이며 화면에서 따로 설명하지 않습니다.
- 노드 이름(demo-*, ip-*), 인스턴스 ID는 녹화에 그대로 보입니다(RECORDINGS.md 방침).
