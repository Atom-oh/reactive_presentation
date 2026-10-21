# V4 수치 대조표 (영상에 쓰는 값만)

출처

- R: `videos/rec/RECORDINGS.md` 공통 절과 "D4: Spot 중단" 절 (2026-10-20 녹화, akd-karp 1회 실행)
- REC: 녹화 화면 `videos/rec/d4-spot.mp4` 자체 (화면에 보이는 그대로의 값)
- CFN: `~/eks-automode-karpenter-demo/02-karpenter/cloudformation.yaml` (EventBridge 규칙 5개)
- DF: `~/eks-automode-karpenter-demo/docs/FACTS.md` 2.11, 3.7 절

| 값 | 영상 위치 | 출처 |
|---|---|---|
| Auto Mode는 FIS EC2 액션을 지원하지 않아 Karpenter 클러스터(akd-karp)에서만 실행 | 제목, 1/4 Auto Mode 카드, 4/4 주의 | R D4 첫 항목, DF 2.11 |
| Auto Mode: Spot 중단 알림을 AWS가 처리, 사용자가 SQS, EventBridge를 구성하지 않음 | 1/4 Auto Mode 카드, 4/4 주의 | DF 2.11 |
| Karpenter controller 1.15.0, EKS 1.37 | 1/4 lane 표기, 녹화 하단 표기 | R 공통 |
| Spot 중단 알림 2분 전 (FIS durationBeforeInterruption PT2M) | 1/4 EC2 상자, 3/4 콜아웃 | R D4 |
| EventBridge 규칙 5개: ScheduledChangeRule, SpotInterruptionRule, RebalanceRule, InstanceStateChangeRule, CapacityReservationInterruptionRule, 대상은 모두 SQS 큐 | 1/4 규칙 카드, 녹화 A 강조 | CFN 412 to 466행, REC(list-rules 출력) |
| 규칙 설명(Spot 중단 경고, Rebalance 권고, AWS Health 이벤트, 인스턴스 상태 변경, 용량 예약 인스턴스 중단 경고) | 1/4 규칙 카드 | CFN `detail-type` 번역 |
| Helm `settings.interruptionQueue: akd-karp` | 1/4 lane 표기, 녹화 A 강조 | REC(helm get values 출력), DF 3.7 |
| Rebalance Recommendation은 이벤트만 기록 | 3/4 14:23:28 행 | DF 3.7 |
| FIS 실험 14:23:15 시작, 14:23:28 완료 | 3/4 타임라인, 녹화 A 태그 | R D4 |
| 대상 `spot-89g4w` m7i.xlarge spot (2b), spot-app Pod 3개 모두 이 노드 | 녹화 A 강조, 3/4, 3/4 공백 장면 | R D4, REC |
| 14:23:28 SpotRebalanceRecommendation | 3/4 | R D4 |
| 14:23:29 SpotInterrupted, TerminatingOnInterruption, Pod 3개 Evicted (Forceful Termination), 대체 NodeClaim `spot-cx877` 지명 | 3/4, 공백 장면 | R D4 |
| 14:23:33 Launched | 3/4, 공백 장면 | R D4 |
| 14:23:35 기존 인스턴스 InstanceTerminating | 3/4 | R D4 |
| 14:24:00 대체 노드 Ready, c7i-flex.xlarge spot (2b) | 3/4, 공백 장면, 4/4 카드 | R D4, REC(NodeClaims 표 `2b`) |
| 2분을 기다리지 않고 경고 직후 기존 노드를 비우고 종료 | 녹화 B 자막, 3/4 콜아웃 | R D4 |
| 약 30초 Running 0개 (Evicted 14:23:29 에서 Ready 14:24:00) | 3/4 공백 장면 제목, 막대 | R D4 |
| 3/3 Running 회복 +65초 (FIS 시작 기준, 녹화 driver) | 녹화 B 마지막 태그, 4/4 주의 | R D4, REC 마지막 줄 |
| 1회 실행 결과, 벤치마크 아님 | 4/4 주의 | R 머리 문단 |
| 교훈: replica 분산(topology spread) | 4/4 카드 1 | R D4 교훈 |
| 녹화 B 자막: `ip-10-0-49-93` Registered, not-ready, Pending 유지, `spot-89g4w` Drained | 녹화 B 자막 | REC (Karpenter events, taints 표) |

## 예시 표기와 압축

- PDB, 여러 인스턴스 유형 허용 카드는 BRIEF의 정리 항목입니다. 수치는 없고, "이번 Spot 중단은 Forceful Termination"과 "m7i.xlarge 대신 c7i-flex.xlarge"만 녹화 값입니다. PDB 카드는 Karpenter 문서(https://karpenter.sh/docs/concepts/disruption/ "Automated Forceful Methods": interruption은 NodePool budget으로 늦출 수 없지만 drain은 Eviction API라 PDB로 애플리케이션 중단 속도를 제한할 수 있음) 근거입니다. 이번 시험에는 PDB를 두지 않았습니다(2026-10-21 수정, 이전 문구 "자발적 중단만"은 부정확).
- 공백 장면의 막대 길이와 노드 그림은 시간 축이 비례하지 않는 재구성입니다. 화면의 시각(14:23:29, 14:23:33, 14:24:00)만 실측입니다.
- 원본 녹화는 1 fps mp4(agg 변환, 2초 넘는 무출력 구간은 2초로 줄임)입니다. 1 fps 원본은 seek 때 프레임이 어긋나므로 `ffmpeg -vf fps=30 -c:v libx264 -crf 14 -g 30`으로 만든 `assets/d4-spot-30fps.mp4`(내용 동일, 프레임만 복제, .gitignore 예외로 커밋)를 0.6배속으로 재생합니다. 녹화 A는 media 2.05 to 14.95초, 녹화 B는 15.05 to 31.95초. 녹화 A에서 `aws events list-rules` 줄이 창 아래로 내려가는 시점(41.9초)에 창을 326px 위로 옮깁니다.
- 녹화 화면의 `SQS msgs 0`, `tainted node ... at +17s`는 화면에 보이지만 영상 텍스트로 인용하지 않습니다.
- 계정 ID는 녹화와 화면 어디에도 없습니다(R: 4개 녹화 모두 치환 0건). 노드 이름, private IP, Pod 이름, FIS 실험 ID는 녹화에 그대로 보입니다.
