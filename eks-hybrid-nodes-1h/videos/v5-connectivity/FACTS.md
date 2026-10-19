# V5 수치 대조표 (연결 검증: native routing, SNAT 없음, PrivateLink)

두 실행이 있습니다. 숫자를 섞지 않고, 화면에서는 회차를 표시합니다("10:50 측정" 또는 "녹화 회차").

## 환경 (두 실행 공통)

출처: `~/eks-hybrid-demo/env/demo.env`, `02-cilium/values-native.yaml`, `02-cilium/native-routes.sh`, `KNOWN-ISSUES.md`

| 값 | 출처 |
|---|---|
| 클러스터 `hybrid-demo`, ap-northeast-2, Kubernetes 1.36 | demo.env |
| 클라우드 VPC 10.0.0.0/16 (VPC CNI), 시뮬레이션 온프렘 VPC 172.18.0.0/16 (= remote node CIDR), TGW로 연결 | demo.env, network.yaml |
| hybrid Pod CIDR 172.17.0.0/16 (Cilium cluster-pool), Service CIDR 172.16.0.0/16 | demo.env |
| Cilium native routing: `routingMode: native`, VXLAN 없음, `enableIPv4Masquerade: false` (SNAT 없음) | values-native.yaml |
| 온프렘 라우터 역할: 온프렘 route table에 노드별 Pod 블록 → 해당 hybrid 노드 ENI (실환경: BGP 또는 정적 라우트) | native-routes.sh |
| VPC CNI `AWS_VPC_K8S_CNI_EXCLUDE_SNAT_CIDRS=172.17.0.0/16,172.18.0.0/16`: 클라우드 Pod가 온프렘으로 갈 때도 Pod IP 유지 | native-routes.sh |
| 인터넷: 모든 Pod가 클라우드 NAT gateway 43.200.92.63으로 나감(온프렘 0.0.0.0/0 → TGW) | network.yaml, 결과 7절 |
| PrivateLink: STS, S3 interface endpoint (클라우드 VPC, 2 AZ, private DNS). endpoint SG는 443을 10.0.0.0/16과 172.17.0.0/16에서만 허용(172.18.0.0/16 노드 CIDR은 없음) | `demo-connectivity/privatelink.yaml` |
| 버킷 정책: 테스트 역할은 `aws:SourceVpce`가 S3 endpoint일 때만 허용 | privatelink.yaml |
| **AWS 지원 범위 밖 구성**: AWS 문서(hybrid-nodes-cni)가 지원하는 Cilium 네트워킹 모드는 "VXLAN encapsulation"뿐. native routing은 지원 범위 밖 | `~/eks-hybrid-demo/RUNBOOK.md` 0.1, KNOWN-ISSUES.md (native 라우팅 전환 확인 사항) |
| masquerade 끄기는 문서에 있는 설정이며, 그 경우 Pod CIDR이 온프렘 네트워크에서 라우팅 가능해야 함 | RUNBOOK.md 0.1 |
| Hybrid Nodes gateway는 VTEP(VXLAN)가 필요해 native 모드와 함께 쓸 수 없음(이 모드에서 gateway 제거) | RUNBOOK.md 0.1, KNOWN-ISSUES.md |
| VXLAN 유지 + masquerade만 끄면: 클라우드와 온프렘 방향은 Pod IP로 나가지만, hybrid 노드 사이 구간은 노드 IP만 보임 (개념, 이 데모에서 측정하지 않음) | RUNBOOK.md 0.1 |
| S3 interface endpoint는 gateway endpoint 없이 만들 때 `DnsOptions.PrivateDnsOnlyForInboundResolverEndpoint: AllResolvers` 필요(첫 시도 실패 원인) | privatelink.yaml 주석 |

## 실행 1: 10:50 측정 (`demo-connectivity/run-tests.sh`, 2026-10-19 10:50:55 UTC)

출처: `~/eks-hybrid-demo/results/connectivity-20261019-1050.md`. **38 PASS, 0 FAIL, 0 SKIP**

| 절 | 항목 수 | 핵심 값 |
|---|---|---|
| 1. Pod 간 직접 통신 | 7 | 같은 hybrid 노드, hybrid 노드 1 ↔ 2, hybrid ↔ cloud 양방향, cloud ↔ cloud. 모두 서버가 클라이언트 Pod IP를 그대로 기록 |
| 2. ClusterIP Service | 3 | h1a → svc-h2, h1a → svc-c1, c1 → svc-h2, 서버가 본 출발지 = 클라이언트 Pod IP (kube-proxy는 목적지만 바꿈) |
| 3. DNS | 4 | h1a, h2, hostnet-h1이 svc-c1 → 172.16.47.167, 공용 이름 aws.amazon.com 해석. CoreDNS는 클라우드 노드에만 있음 |
| 4. hybrid Pod → Kubernetes API | 2 | `/livez` 200, SA 토큰으로 403(인증됨, 권한 없음) |
| 5. control plane → hybrid | 3 | API server proxy → h1a, nginx가 본 출발지 10.0.36.52(EKS 관리 ENI), exec/logs(kubelet 10250), metrics-server → kubelet |
| 6. 일반 온프렘 서버(쿠버네티스 밖) | 2 | h1a → 172.18.51.209:18080, 서버가 172.17.0.244를 봄. c1 → 같은 서버, 10.0.63.165를 봄 |
| 7. 인터넷 | 3 | h1a, h2, c1 모두 43.200.92.63(클라우드 NAT)으로 나감 |
| 8. Cilium 정책 | 3 | h2에 `fromCIDR 10.0.0.0/16` 정책: h1a 차단, c1 허용, 정책 삭제 후 h1a 다시 허용 |
| 9. MTU, 대용량 | 2 PASS + info 4 | MTU 9001, 32 MiB 양방향 sha256 일치, DF ping 1472, 8472 바이트 통과 (TGW 한도 8500) |
| 10. ALB ip 타깃 | 1 | 172.17.0.101, 172.17.0.171 healthy |
| 11. PrivateLink | 8 | sts → 10.0.58.187, 10.0.45.43, s3와 버킷 호스트 → 10.0.61.174, 10.0.36.16, irsa-h1 STS AssumeRoleWithWebIdentity, PutObject, irsa-c1 GetObject, SG: Pod IP는 HTTP 302, 같은 노드 hostNetwork(172.18.38.77)는 타임아웃, 워크스테이션에서 같은 역할은 `aws:SourceVpce`로 거부 |

합계: 7+3+4+2+3+2+3+3+2+1+8 = 38

이번 작업에서 고친 것 (첫 실행 FAIL의 원인, `results/connectivity-20261019-0851.md`)

- hostNetwork Pod의 DNS 실패: 노드 IP(172.18.x)에서 CoreDNS로 가는 UDP/TCP 53이 클러스터 SG에 없었음 → 172.18.0.0/16 허용 추가
- 클라우드 Pod → 온프렘 서버가 노드 IP로 SNAT됨: VPC CNI 제외 목록에 172.18.0.0/16이 없었음 → 추가
- `/version` 401: EKS 1.36은 익명 접근을 health endpoint만 허용 → `/livez`로 확인

## 실행 2: 녹화 회차 (2026-10-19 13:18:37 UTC 녹화 시작)

출처: `eks-hybrid-nodes-1h/videos/rec/RECORDINGS.md` R5, `~/eks-hybrid-demo/.work/rec/r5-conn.plain.txt`

녹화 파일 `../rec/r5-conn.mp4`: 1920x1412, 57.6초(원본 61.5초, 2초 넘는 대기는 2초로 줄임). 아래 시각은 **영상 기준 초**입니다.

| 영상 초 | 화면 |
|---|---|
| 0 ~ 2.0 | 제목 줄 "Connectivity test ... (recorded 2026-10-19 13:18 UTC)" |
| 3.2 | `k get pods` 표: c1 10.0.63.165, c2 10.0.40.126 (클라우드 노드 ip-10-0-*), h1a 172.17.0.244, h1b 172.17.0.215 (mi-01c0d4f2de39dab64), h2 172.17.0.50 (mi-067a83f4fd29491d9), hostnet-h1 172.18.38.77, irsa-c1 10.0.57.98, irsa-h1 172.17.0.186, onprem-srv 172.18.51.209 |
| 6.7 | 변수: C1=10.0.63.165 H2=172.17.0.50 SRV=172.18.51.209 STS_IP=10.0.58.187, BUCKET, KEY |
| 9.4 ~ 16.0 | 1) h1a → c1 200, c1의 nginx 로그 `server saw 172.17.0.244` (14.8초) |
| 16.3 ~ 22.8 | 2) c1 → h2 200, h2 로그 `server saw 10.0.63.165` (21.5초) |
| 23.0 ~ 26.0 | 3) h1a → 온프렘 socat 172.18.51.209:18080, 응답 `172.17.0.244` (24.8초) |
| 26.3 ~ 29.5 | 4) h1a → checkip.amazonaws.com, `43.200.92.63` (28.3초) |
| 29.8 ~ 33.0 | 5) dig sts, s3 → 10.0.58.187, 10.0.45.43, 10.0.61.174, 10.0.36.16 |
| 33.1 ~ 43.5 | 6) irsa-h1 `get-caller-identity` → `arn:aws:sts::************:assumed-role/hybrid-demo-privatelink-TestRole-.../botocore-session-...`(계정 ID 가림), irsa-h1 PutObject, irsa-c1 GetObject → `hello-from-irsa-h1` (42.2초) |
| 43.8 ~ 53.0 | 7) h1a(Pod IP) → STS ENI 10.0.58.187:443 → `302` (48.3초), hostnet-h1(노드 IP 172.18.38.77) → `command terminated with exit code 28`(타임아웃, 51.8초. 실제 대기 약 5초가 2초로 줄어 보임) |
| 53.3 ~ 57.6 | `tail -1 results/connectivity-20261019-1050.md` → `38 PASS, 0 FAIL, 0 SKIP` (54.5초) |

## 화면 구성 메모

- 경로도는 개념도입니다. 숫자는 위 표의 값만 씁니다.
- "SNAT 없음"의 증거는 서버 로그의 출발지 IP입니다. 비교 대상(VXLAN overlay + masquerade였다면 노드 IP 172.18.x가 보였을 것)은 개념 설명이며 측정값이 아니라고 표시합니다.
- 계정 ID, 비밀 값은 표시하지 않습니다.
