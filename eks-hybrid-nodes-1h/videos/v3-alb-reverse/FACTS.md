# V3 수치 대조표 (ALB ip 타깃과 역방향)

두 실행이 있습니다. 숫자를 섞지 않고, 화면에서는 회차를 표시합니다("02:11 측정" 또는 "녹화 회차").

## 실행 1: 02:11 측정 (`run-tests.sh`, 2026-10-18 02:11 UTC 시작, 02:15 생성)

출처: `~/eks-hybrid-demo/results/lb-20261018-0211.json`, `~/eks-hybrid-demo/RUNBOOK.md` 5절, `KNOWN-ISSUES.md` "LB 데모 확인 사항", 덱 `eks-hybrid-nodes/05-live-demo.md` Slide 10, 11

| 값 | 출처 |
|---|---|
| T1: hybrid 타깃 172.17.0.202, 172.17.0.48 healthy, AZ `all` | json `t1_registration`, RUNBOOK 5절 |
| T2: 리전 Pod → ALB → hybrid Pod 20/20 | json `t2_alb_to_hybrid` |
| T3: rollout restart 후 새 IP 172.17.0.230, 172.17.0.76, 54초에 수렴, 276건 중 실패 0 | json `t3_rollout`, RUNBOOK 5절 |
| T4: gateway 리더 Pod 삭제, 인계 4초, 191건 중 실패 1 (공백 약 1초), 이후 타깃 .230, .76 healthy | json `t4_gateway_failover`, RUNBOOK 5절 |
| T4 클라이언트 busybox `wget`은 재시도하지 않음: 실제 공백에 가까움 | KNOWN-ISSUES.md, 덱 Slide 10 노트 |
| B1: 온프렘 호스트 172.18.38.77 → internal ALB(10.0.46.5, 10.0.51.70) → 클라우드 Pod 20/20, gateway 안 거침 | json `t5_reverse`, RUNBOOK 5절 |
| B1': 같은 ALB로 hybrid Pod 20/20, hairpin(DX 두 번) | json `alb_hybrid_ok`, RUNBOOK 5절 |
| B2: 온프렘 → hybrid NodePort 172.18.51.209:30080 → 클라우드 Pod 실패, 노드 IP로 SNAT 후 underlay, 클라우드 노드 SG가 172.18.0.0/16에 443만 허용 | json `nodeport_cloud_ok: 0`, RUNBOOK 5절, KNOWN-ISSUES.md |

## 실행 2: 녹화 회차 (2026-10-18 06:36:29 UTC 녹화 시작)

출처: `eks-hybrid-nodes-1h/videos/rec/RECORDINGS.md` R3, `~/eks-hybrid-demo/.work/rec/r3-alb.plain.txt`, `r3-converged.txt`, `r3-load.txt`

| 값 | 출처 |
|---|---|
| 시작 타깃 172.17.0.132, 172.17.0.26 healthy, AZ `all` | R3, plain.txt |
| 부하: 클라우드 Pod → internal ALB → /hybrid, 0.5초 간격, 90초 | plain.txt (driver 주석) |
| 폴링(약 6초 간격) +1s .101 initial, +7s .101 healthy, +20s .171 initial와 .26 draining, +26s .171 healthy, +32s .26 사라짐, +38s .132 draining, +50s .101, .171만 healthy | plain.txt |
| 새 Pod IP만 healthy로 남은 시점: rollout restart 후 50초 | r3-converged.txt, R3 |
| 부하 174건, ERR 0 (.101 65, .132 36, .171 51, .26 22) | r3-load.txt, R3 |
| 수렴 직후 Pod 표: 옛 Pod `...-k2fch` Running, `...-svhhr` Failed(종료 중), 몇 초 뒤 사라짐 | R3 |
| onprem-curl 3: 출발 172.18.38.77, ALB → 10.0.46.5, 10.0.51.70, /cloud 3/3, /hybrid 3/3, NodePort 172.18.51.209:30080 FAIL 3회 | plain.txt, R3 |

## 화면 구성 메모

- 경로도(장면 1)와 역방향 3경로(장면 7)는 개념도입니다. 숫자는 위 표의 값만 씁니다.
- 장면 4 타임라인 칸은 녹화의 폴링 출력 그대로입니다(칸 경계 = 폴링 시점).
- 장면 6 요청 막대: 191건과 실패 1건은 실측, 실패 칸의 위치는 예시입니다(화면에 표시).
- 시뮬레이션 환경: 온프렘은 TGW로 연결(실환경은 DX/VPN). 실환경에서 온프렘 DNS가 internal ALB 이름을 풀려면 Route 53 Resolver inbound endpoint가 필요합니다(RUNBOOK 5절).
- 화면에 계정 ID, 비밀 값 없음(녹화의 계정 ID는 `************`로 가려져 있음).
