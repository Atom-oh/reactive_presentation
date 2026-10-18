# V1 수치 대조표 (영상에 쓰는 값만)

| 값 | 영상 위치 | 출처 |
|---|---|---|
| Lease 전환 3초, 5초, 5초 (3회) | 장면 4 타이머(1회차 3초), 장면 5 결과 카드 | ~/eks-hybrid-demo/RUNBOOK.md 1절 마지막 문단; eks-hybrid-nodes/05-live-demo.md 표 |
| 1초 간격 요청 실패 60개 중 1, 60개 중 1, 45개 중 2 | 장면 2~4 요청 격자(1회차 60개 중 1개), 장면 5 결과 카드 | RUNBOOK.md 1절(실패 1, 1, 2회); 분모 60/60/45는 eks-hybrid-nodes/05-live-demo.md 표 (Deep Dive 5부) |
| 3회차는 최소 권한 IAM(라우트 쓰기를 gateway 라우팅 테이블로 제한) | 장면 5 | RUNBOOK.md 1절; KNOWN-ISSUES.md "게이트웨이 IAM 권한을 최소화했습니다" |
| 라우트 172.17.0.0/16 → 리더 ENI, 전환 후 새 리더 ENI | 장면 2~4 라우트 테이블, 장면 4 터미널 | RUNBOOK.md 1절; demo1-gateway/failover.sh (`route ENI: OLD -> NEW`, `route target matches new leader ENI: yes`) |
| Lease HOLDER 형식 노드이름_uuid | 장면 2 터미널, 장면 4 | demo1-gateway/lib.sh 3행 주석; eks-hybrid-nodes/05-live-demo.md 알아 둘 점 |
| namespace `eks-hybrid-nodes-gateway` | 장면 2~3 터미널 | demo1-gateway/lib.sh `NS=` |
| Lease `hybrid-gateway-leader`, Gateway Deployment 2 replica | 장면 1, 2 | eks-hybrid-nodes/02-networking-gateway.md 717, 854행 |
| 리더 삭제 전 10초 동안 요청 (`sleep 10` 후 delete) | 장면 2 요청 격자 10칸 | demo1-gateway/failover.sh 13행 |
| 기본 측정 60초 (`DURATION=60`) | 요청 격자 60칸 | demo1-gateway/failover.sh 5행 |
| VPC 10.0.0.0/16, 온프레미스 노드 172.18.0.0/16, Hybrid Pod 172.17.0.0/16 | 장면 1~4 구성도 | ~/eks-hybrid-demo/env/demo.env.example 4~6행 |
| 시뮬레이션: 온프레미스는 TGW로 연결한 두 번째 VPC (실환경 DX/VPN) | 장면 1 | RUNBOOK.md 머리말 |
| AWS 문서 예상 전환 3~5초 | 장면 5 | eks-hybrid-nodes/05-live-demo.md 노트 출처 (hybrid-nodes-gateway-overview) |

예시 표기(실측값 아님, 화면에 "예시"로 표시): Pod 이름 `gateway-…a1`, `gateway-…b2`, ENI `eni-…a1`, `eni-…b2`, 노드 `gw-node-a`, `gw-node-b`, `<uuid>`. 요청 격자에서 실패 칸의 위치(11번째)는 삭제 직후라는 의미의 예시이며, 실패 개수만 실측값입니다.
계정 ID, 실제 ENI ID, 비밀 값은 쓰지 않습니다.
