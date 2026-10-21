# V1 수치 대조표 (영상에 쓰는 값만)

출처는 하나입니다: `videos/rec/RECORDINGS.md`(2026-10-20 녹화) "공통 사항"과 "D1: 스케일 아웃" 절, 그리고 녹화 화면 `videos/rec/d1-scaleout.mp4` 자체. 1회 실행 결과이며 벤치마크가 아닙니다. 새 숫자를 만들지 않았고, 두 값의 차이(예: 25초, 19초)도 화면에 쓰지 않았습니다.

## 공통 (환경)

| 값 | 영상 위치 | 출처 |
|---|---|---|
| 클러스터 `akd-auto`(EKS Auto Mode), `akd-karp`(직접 설치 Karpenter) | 1/4 카드, 전 장면 하단 표기 | RECORDINGS.md 머리 문단 |
| EKS 1.37, ap-northeast-2, fsi-demo-vpc private 서브넷 2개(2a, 2b) | 1/4 공통 카드, 녹화 하단 표기 "EKS 1.37" | RECORDINGS.md 머리 문단 |
| Karpenter controller 1.15.0 | 1/4 akd-karp 카드 | 공통 사항 "환경 값" |
| 노드 OS: Auto Mode Bottlerocket, Karpenter Amazon Linux 2023 (AL2023) | 1/4 카드, 4/4 주의 | 공통 사항 "환경 값" |
| `demo` NodePool: on-demand, c/m/r, generation > 5, amd64 (두 클러스터 같음) | 1/4 공통 카드, 녹화 1구간(jsonpath 출력) | 공통 사항 "NodePool 설정"; 녹화 화면 |
| 워크로드: pause 이미지, replica당 requests 1 vCPU / 1.5Gi | 1/4 칩 | 공통 사항 "워크로드" |
| 녹화 날짜 2026-10-20 | 하단 표기 | RECORDINGS.md 제목, 녹화 첫 줄 |
| 2초 넘는 무출력 구간을 2초로 줄임 (화면의 elapsed, +Ns는 실제 시간) | 녹화 표시 "대기 구간 줄임" | 공통 사항 "변환" |

## D1

| 값 | 영상 위치 | 출처 |
|---|---|---|
| 두 클러스터에 동시에 replicas 0 → 10 | 1/4 칩, 2/4 제목 | D1 첫 항목 |
| 두 클러스터 모두 NodeClaim 1개, c7i-flex.4xlarge on-demand, 2b | 2/4 자막, 3/4 칩, 4/4 카드 | D1 둘째 항목; 녹화 화면 NodeClaim 표 |
| NodeClaim 생성 13:54:15 (두 클러스터 같음) | 2/4 자막, 3/4 패널 A 머리글과 칩 | D1 셋째 항목; 녹화 CREATED 열 |
| 노드 Ready: Auto Mode 13:54:30 (15초), Karpenter 13:54:55 (40초), NodeClaim 생성 기준 | 2/4 자막, 3/4 패널 A, 4/4 카드 | D1 셋째 항목; 녹화 READY 열 |
| Pod 10개 모두 Ready: Auto Mode +28초, Karpenter +47초, scale 명령 기준 | 2/4 자막, 3/4 패널 B, 4/4 카드 | D1 넷째 항목; 녹화 둘째 줄과 "# both clusters" 줄 |

## 녹화 화면 표시와 압축

- 녹화 장면은 `assets/d1-scaleout.mp4`(심볼릭 링크, 1fps, 1920x1358)를 같은 내용 그대로 30fps CFR로 다시 인코딩한 `assets/d1-scaleout-30fps.mp4`를 씁니다. 원본은 1fps에 keyframe이 2개뿐이라 프레임 추출 시점이 어긋났기 때문입니다(화면 내용, 시간 축 변경 없음).
- 녹화 media 2초부터 29초까지를 0.5배속으로 재생합니다(영상 34초부터 88초). 화면에 "실제 터미널 녹화, 대기 구간 줄임, 0.5배속"을 표시합니다.
- 녹화 창 안 확대: media 2 to 15초 0.955배(NodePool 조건 확인 출력 전체), 15 to 25초 1.3배(첫 주석 줄을 위로 잘라 냄, 상태 블록만 보임), 25 to 29초 1.0배(요약 줄과 NodeClaim 표). 잘라 낸 첫 줄의 정보(10 replicas, 1 vCPU, 1.5Gi, EKS 1.37)는 1/4에 있습니다.
- 녹화 자막 "Auto Mode 노드가 먼저 R=True", "Auto Mode Pod 10/10 Running, Karpenter는 아직 10개 Pending"은 녹화 화면에 보이는 상태를 그대로 옮긴 것이며 새 수치가 아닙니다.
- 3/4 막대 길이는 측정 초에 비례(23px/초)하고, 막대가 자라는 속도는 측정 초 x 0.12초(시각화용 압축)입니다.
- 계정 ID는 녹화와 화면 어디에도 없습니다(RECORDINGS.md: 가린 값 0건). 노드 이름(demo-p8nrs, demo-c9ks5)은 녹화에 그대로 보입니다.
