# 실제 터미널 녹화 (V1~V3용)

2026-10-18, 클러스터 `hybrid-demo`(ap-northeast-2)에서 데모를 실제로 다시 실행하며 녹화했습니다. 재구성 화면이 아니라 실행 중인 터미널 출력 그대로입니다.

공통 사항

- 녹화: asciinema 2.4.0 (`asciinema rec -c 'bash <driver>.sh' --cols 120 -i 2`). 명령은 driver 스크립트가 프롬프트(`~/eks-hybrid-demo $`)와 함께 먼저 출력한 뒤 실행합니다.
- 변환: agg 1.9.0 (`--theme asciinema --font-family "Source Code Pro" --font-size 28 --idle-time-limit 2`) 후 ffmpeg로 h264 mp4 (1920 폭, yuv420p, 무음, faststart).
- 대기 구간 줄임: 출력이 2초 넘게 없는 구간은 2초로 줄였습니다(idle time limit). 영상 길이는 실제 경과 시간보다 짧습니다. 영상에는 "대기 구간 줄임" 표시를 넣어야 합니다. 화면에 찍힌 시각(`[06:28:09]`, `elapsed 44s`, `[+20s]`)은 실제 시각입니다.
- 가린 값: AWS 계정 ID(12자리)를 `.cast`에서 `************`로 바꾼 뒤 변환했습니다(R1 1곳, R2 0곳, R3 1곳, `check_identity` 로그 줄). `AKIA`, `ActivationCode`, `activation`, `secret`, `token`, `arn:aws`는 가린 뒤의 `.cast`에서 검색되지 않았습니다. ENI ID, Pod 이름, private IP, internal ALB 이름은 그대로 두었습니다.
- 표 너비: 120열에 맞추려고 `get pods -o wide` 대신 `-o custom-columns=NAME,STATUS,IP,NODE`를 썼습니다(명령이 화면에 그대로 보입니다).
- 원본 `.cast`와 driver 스크립트는 저장소 밖 `~/eks-hybrid-demo/.work/rec/`에 있습니다.

| 파일 | 녹화 시작(UTC) | 실제 길이 | 영상 길이 | 크기 | 해상도 |
|---|---|---|---|---|---|
| `r1-failover.mp4` | 2026-10-18 06:27:44 | 93.6초 | 34.5초 | 2.0 MB | 1920x1138 |
| `r2-bursting.mp4` | 2026-10-18 06:30:57 | 77.5초 | 37.3초 | 1.7 MB | 1920x1284 |
| `r3-alb.mp4` | 2026-10-18 06:36:29 | 125.0초 | 61.5초 | 4.3 MB | 1920x1284 |

## R1: gateway 리더 전환 (V1)

명령

```bash
kubectl -n eks-hybrid-nodes-gateway get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,IP:.status.podIP,NODE:.spec.nodeName
kubectl -n eks-hybrid-nodes-gateway get lease
aws ec2 describe-route-tables --route-table-ids ${ROUTE_TABLE_IDS%%,*} \
  --query "RouteTables[0].Routes[?DestinationCidrBlock=='$REMOTE_POD_CIDR'].[DestinationCidrBlock,NetworkInterfaceId]" --output text
./demo1-gateway/failover.sh
kubectl -n eks-hybrid-nodes-gateway get lease
kubectl -n eks-hybrid-nodes-gateway rollout status deploy/eks-hybrid-nodes-gateway
kubectl -n eks-hybrid-nodes-gateway get pods -o custom-columns=...
```

관찰 결과

- 전환 전 리더: `eks-hybrid-nodes-gateway-f4bf6c595-nlbfq`(ip-10-0-41-152), 라우트 `172.17.0.0/16 -> eni-0dbc9737395c577e6`
- 리더 Pod 삭제 06:28:09, 새 리더 `...-tkwcb`(ip-10-0-57-129), **Lease 인계 5초**
- **실패한 probe 2 / 60**(1초 간격), 첫 실패부터 마지막 실패까지 5초
- 라우트 ENI `eni-0dbc9737395c577e6 -> eni-021433ec3aa9dbb0f`, 새 리더 ENI와 일치: yes
- 끝난 뒤 gateway Deployment 2/2 Running(새 Pod `...-5hvsz`)

## R2: bursting과 pod-deletion-cost, 시나리오 B (V2)

녹화 전 준비(녹화에 포함하지 않음): `mesh-demo`, `plain-demo` 없음 확인, `./demo2-burst/kyverno/install.sh apply-policy`, `karpenter-gate.sh status`가 `false`, `calc-requests.sh` 결과 `CPU_REQ=910m`(hybrid 여유 CPU 3700m, 3640m), burst-demo Deployment 삭제 후 `envsubst`로 3개 재배치, rollout 완료, burst NodeClaim 없음.

녹화 내용: driver가 2초마다 아래 두 명령을 실행하고, 내용이 바뀔 때만 화면을 다시 그립니다(`watch`와 같은 화면). 스케일 명령은 실행 전에 화면에 출력합니다.

```bash
kubectl -n burst-demo get pods -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName,COST:.metadata.annotations.controller\.kubernetes\.io/pod-deletion-cost,STATUS:.status.phase
kubectl get nodeclaims -l karpenter.sh/nodepool=burst
kubectl -n burst-demo scale deploy/burst-demo --replicas=15   # 15개 Ready까지 대기
kubectl -n burst-demo scale deploy/burst-demo --replicas=10   # 10개까지 대기
kubectl -n burst-demo scale deploy/burst-demo --replicas=3    # 3개까지 대기
```

`pods: N total, H on hybrid (mi-*), B on burst EC2 (ip-*)` 줄은 driver가 같은 표에서 센 값입니다.

관찰 결과

- 스케일 아웃 직후 첫 화면(약 5초 뒤)에 NodeClaim 3개(m6i.large 1, m6i.xlarge 2)가 이미 생성됨, hybrid 8개 Running, 7개 Pending
- 스케일 명령 후 **35초에 15개 모두 Ready**(hybrid 8 / burst 7)
- 10개로 줄인 결과: **hybrid 8 / 클라우드 2**(burst 노드 ip-10-0-54-55, ip-10-0-36-192), 6초 안에 반영
- 3개로 줄인 결과: **3개 모두 hybrid(mi-*)**, COST 1. burst NodeClaim 3개는 녹화 끝에도 남아 있음(정리는 녹화하지 않음)
- 녹화 뒤 burst NodeClaim은 06:33:53에 모두 사라짐(3개로 줄인 06:32:09부터 약 104초). burst-demo는 3개로 둠

## R3: ALB ip 타깃과 역방향 경로 (V3)

명령(SCENARIO.md 6절 기준)

```bash
ALB=...; LB_ARN=...; TG_HYBRID=...; echo $ALB
kubectl -n lb-demo get pods -l app=web-hybrid -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,IP:.status.podIP,NODE:.spec.nodeName
aws elbv2 describe-target-health --target-group-arn $TG_HYBRID --query 'TargetHealthDescriptions[].[Target.Id,Target.AvailabilityZone,TargetHealth.State]' --output text
kubectl -n lb-demo exec deploy/web-cloud -- sh -c "<90초 부하 루프>" | awk '{print ($1=="ERR") ? "ERR" : $2" "$3}' | sort | uniq -c > $TMPDIR/load.txt &
kubectl -n lb-demo rollout restart deploy/web-hybrid
# 약 6초마다 describe-target-health 출력, 새 Pod IP만 healthy로 남을 때까지
kubectl -n lb-demo rollout status deploy/web-hybrid --timeout=180s
kubectl -n lb-demo get pods -l app=web-hybrid -o custom-columns=...
wait; cat $TMPDIR/load.txt
./demo-lb/onprem-curl.sh 3
```

SCENARIO.md와 다른 점: 타깃 교체가 끝날 때까지 부하가 이어지도록 부하 시간을 60초에서 90초로 늘렸고, 응답 Pod별 합계가 보이도록 `uniq -c` 앞에 `sort`를 넣었습니다.

관찰 결과

- 시작 타깃 `172.17.0.132`, `172.17.0.26`(AZ `all`, healthy)
- 새 타깃 `172.17.0.101`, `172.17.0.171`이 `initial`에서 `healthy`로, 옛 타깃은 `draining`을 거쳐 빠짐
- **새 Pod IP만 healthy로 남은 시점: rollout restart 후 50초**(폴링 간격 약 6초)
- 부하 **174건, ERR 0**(응답 Pod: .101 65건, .132 36건, .171 51건, .26 22건)
- 수렴 직후 Pod 표에는 종료 중인 옛 Pod 2개가 아직 보임(`...-k2fch` Running, `...-svhhr` Failed). 둘 다 몇 초 뒤 사라졌고, 최종 상태는 새 Pod 2개 Running
- `onprem-curl.sh 3`: 출발 호스트 172.18.38.77, ALB 이름이 private IP `10.0.46.5`, `10.0.51.70`으로 풀림, `/cloud` 3/3(10.0.x 클라우드 Pod), `/hybrid` 3/3(새 hybrid Pod), **NodePort 172.18.51.209:30080 3회 모두 FAIL**(의도한 결과, 화면에 그대로 남김)

첫 번째 시도(06:33:46, 사용하지 않음): 수렴 판정이 종료 중인 옛 Pod까지 기다려 "75s"로 표시됐고(타깃 자체는 55초에 새 IP만 남음), `uniq -c` 출력이 115줄이라 읽기 어려워 판정 조건과 요약을 고쳐 다시 녹화했습니다. 이 시도도 부하 174건 중 ERR 0이었습니다. 이 때문에 web-hybrid rollout restart는 두 번 실행됐습니다.
