---
title: EKS Hybrid Nodes 딥다이브
subtitle: 이제는 Amazon EKS를 온프레미스에서도
speaker: Junseok Oh
role: Sr. Solutions Architect
company: Amazon Web Services
duration: 40min
blocks: 4
slides: 52
---

<!-- Block 1: 개요 & 아키텍처 (10분) -->

---

# EKS Hybrid Nodes

이제는 Amazon EKS를 온프레미스에서도

- Junseok Oh
- Sr. Solutions Architect
- Amazon Web Services

---

## Agenda

총 40분 세션

| # | 주제 | 시간 |
|---|------|------|
| 1 | **개요 & 아키텍처** | 10분 |
| 2 | **네트워킹 & 트래픽** | 10분 |
| 3 | **노드 구성 & 운영** | 10분 |
| 4 | **고급 패턴 & 전략적 가치** | 10분 |

질문은 각 Block 종료 시에 받겠습니다.

---

## 온프레미스 Kubernetes 운영의 현실

### Control Plane 관리 부담
> "버전 업그레이드, etcd 백업/복구, 인증서 갱신... 운영팀의 야근이 끊이지 않습니다"

### 보안 패치 & 컴플라이언스
> "CVE 대응, CIS 벤치마크 준수, 감사 대응에 수개월이 소요됩니다"

### 모니터링 사일로
> "온프렘과 클라우드 환경 간 통합 관측이 어렵습니다"

### 최신 AI 서비스 접근의 한계
> "온프렘 단독 환경에서 최신 AI 모델 활용과 Agent 개발이 어렵습니다"

---

## EKS Hybrid/Edge 포트폴리오

<!-- tab: EKS Anywhere -->
- Control Plane + Worker 모두 온프레미스
- VMware vSphere, Bare Metal, CloudStack 지원
- AWS와 독립적으로 실행 가능 (Air-gapped 환경)
- EKS Connector로 콘솔 통합 관리 가능

<!-- tab: EKS Hybrid Nodes -->
- Control Plane은 AWS, Worker는 온프레미스
- AWS 관리형 CP + 고객 관리 Worker
- VPN 또는 Direct Connect 연결 필수
- AWS 서비스 (Bedrock, SageMaker 등) 즉시 연계 가능

<!-- tab: EKS on Outposts -->
- AWS 하드웨어를 고객 데이터센터에 설치
- AWS가 하드웨어까지 관리 (완전 관리형)
- 로컬 Kubernetes + AWS 서비스 일체형
- 초기 투자 비용 및 공간 요구사항 있음

---

## EKS Hybrid Nodes란?

**EKS Control Plane(AWS 완전 관리) + Worker Node(온프레미스)**

연결 방식: VPN | Direct Connect | Private Endpoint

### 적합한 사용 사례
- 온프레미스 GPU/특수 하드웨어 활용
- 규제 준수를 위한 데이터 지역성 요구
- 지연 시간에 민감한 Edge 워크로드
- 클라우드 마이그레이션 전환기

### 부적합한 사용 사례
- 순수 클라우드 네이티브 워크로드 → EKS managed node group 또는 Fargate 권장
- 온프레미스 인프라가 없는 환경

---

## 아키텍처 개요: 노드 등록 흐름

<!-- canvas: archCanvas, 1100x450 -->
<!-- interactive: ↑↓ 키로 단계를 이동하세요 -->

4단계 애니메이션:
1. 기본 구성 (AWS VPC + On-Prem)
2. VPN/DX 연결
3. nodeadm init (노드 등록)
4. Node Ready

---

## IaaS를 넘어서는 가치

**Hybrid Nodes = AWS Managed Services Gateway**

<!-- canvas: servicesCanvas -->

| 카테고리 | 서비스 |
|----------|--------|
| AI/ML | Bedrock, SageMaker |
| Database | RDS, ElastiCache |
| Analytics | OpenSearch, Kinesis |

---

## 책임 공유 모델

### AWS 관리 영역
- EKS Control Plane 가용성
- etcd 백업 및 복구
- API Server 고가용성
- Kubernetes 버전 업그레이드
- Control Plane 보안 패치

### 고객 관리 영역
- Worker 노드 (HW, OS, 런타임)
- 온프레미스 네트워크 연결
- CNI 구성 (Cilium/Calico)
- 모니터링 에이전트 배포
- 워크로드 배포 및 관리

> Control Plane 운영 부담이 AWS로 이전되어, 팀은 워크로드와 비즈니스 로직에 집중할 수 있습니다.

---

## 주요 제약 사항

도입 전 반드시 확인해야 할 사항

- **IPv4 전용** - IPv6 네트워크는 현재 미지원
- **Remote Network CIDR** - 클러스터당 최대 15개까지 등록 가능
- **VPC CNI 미지원** - Cilium 또는 Calico 사용 필수
- **vCPU 기반 과금** - Hybrid Node당 $0.02/vCPU/시간
- **엔드포인트 모드 제한** - "Public and Private" 동시 사용 불가

> 네트워크 설계 시 CIDR 제한과 CNI 요구사항을 미리 검토하세요.

---

## 지원 환경

| 항목 | 지원 사양 |
|------|-----------|
| 운영 체제 | Ubuntu 20.04/22.04/24.04, RHEL 8/9, Amazon Linux 2023, Bottlerocket |
| 아키텍처 | x86_64, arm64 (ARMv8.2+) |
| EKS 버전 | 1.31+ |
| 리전 | 대부분의 AWS 상용 리전 지원 |
| CNI | Cilium (공식 지원), Calico (공식 미지원) |
| Container Runtime | containerd 1.6+ |
| 최소 하드웨어 | 1 vCPU, 1 GiB Memory, 50 GB Disk |

권장: 4코어 / 8GB / 100GB NVMe

---

## 크리덴셜 프로바이더

노드 인증 방식 선택

<!-- toggle: SSM Hybrid Activations | IAM Roles Anywhere -->

### SSM Hybrid Activations
- PKI 인프라 불필요, 빠른 설정
- Activation Code + ID로 간편 등록
- 자동 자격 증명 갱신
- 세션 지속 시간: 최대 1시간

```yaml
# nodeadm 설정 예시 (SSM)
spec:
  hybrid:
    ssm:
      activationCode: xxxxxxxx
      activationId: xxxxxxxx-xxxx-xxxx
```

### IAM Roles Anywhere
- 기존 PKI 인프라 활용 가능
- X.509 인증서 기반 인증
- 세션 지속 시간: 최대 12시간
- 에어갭(Air-gapped) 환경에 적합

```yaml
# nodeadm 설정 예시 (IAM RA)
spec:
  hybrid:
    iamRolesAnywhere:
      trustAnchorArn: arn:aws:rolesanywhere:...
      profileArn: arn:aws:rolesanywhere:...
      roleArn: arn:aws:iam::...:role/...
```

---

## Block 1 Quiz

<!-- quiz -->

**Q1.** EKS Hybrid Nodes에 적합하지 않은 사용 사례는?
- A. 온프레미스 GPU 서버 활용
- B. 규제 준수를 위한 데이터 지역성
- **C. 순수 클라우드 네이티브 워크로드 실행** <!-- correct -->
- D. 지연 시간 민감한 Edge 워크로드

**Q2.** EKS Hybrid Nodes가 지원하는 운영 체제 조합은?
- A. Windows Server 2019, Ubuntu 22.04
- **B. Ubuntu 20.04/22.04, Amazon Linux 2023, RHEL 8/9** <!-- correct -->
- C. CentOS 7, Debian 11, Fedora 38
- D. macOS Ventura, Ubuntu 18.04

**Q3.** EKS Hybrid Nodes의 최소 하드웨어 요구 사항(AWS 공식)은?
- **A. CPU 1 vCPU, Memory 1 GiB** <!-- correct -->
- B. CPU 2 vCPU, Memory 4 GiB
- C. CPU 4 vCPU, Memory 8 GiB
- D. CPU 8 vCPU, Memory 16 GiB

---

## Q&A

Block 1 핵심 요약:
- EKS CP는 AWS 관리형 / 온프렘 인프라 활용
- VPN/DX로 안전한 하이브리드 네트워킹
- nodeadm으로 간편한 노드 부트스트랩
- SSM 또는 IAM RA 인증 프로바이더

---

<!-- Block 2: 네트워킹 심층분석 (10분) -->

# 네트워킹 심층분석

CIDR 설계, 6가지 트래픽 패턴, 방화벽 규칙

---

## 네트워크 전제 조건

EKS Hybrid Nodes를 위한 네트워크 아키텍처 요구사항

1. VPC에 EKS Control Plane ENI가 배치됨
2. Transit Gateway 또는 Virtual Private Gateway로 온프렘 연결
3. Remote Node/Pod CIDR을 클러스터 생성 시 지정
4. 권장 네트워크 지연시간: 100ms 이하 (Direct Connect 시 <10ms, 200ms 초과 시 연결 불안정)

---

## CIDR 설계 체크리스트

IP 충돌 없는 하이브리드 네트워크 설계

<!-- checklist -->
- [ ] Remote Node CIDR: 온프렘 노드 IP 범위 (예: 10.80.0.0/16)
- [ ] Remote Pod CIDR: 온프렘 파드 IP 범위 (예: 10.85.0.0/16)
- [ ] VPC CIDR과 겹치지 않을 것
- [ ] Service CIDR과 겹치지 않을 것
- [ ] RFC-1918 범위 내에 있을 것
- [ ] 최대 15개 CIDR 블록 제한 준수

> 권장: Pod CIDR은 라우팅 가능하게 설계 (BGP 사용) — Admission Webhook 등 CP->Pod 통신에 필수

---

## Pattern 1: Kubelet -> EKS Control Plane

Kubelet이 API 서버에 연결하는 경로

<!-- toggle: Public Endpoint Route | Private Endpoint Route -->

> 권장: 프로덕션 환경에서는 Private 엔드포인트 사용 권장

```bash
aws eks update-cluster-config --name <cluster> \
  --resources-vpc-config endpointPrivateAccess=true
```

---

## Pattern 2: Control Plane -> Kubelet

API Server가 Kubelet에 연결 (port 10250)

- 용도: Webhook 호출, kubectl exec/logs 명령 처리
- 방화벽에서 TCP 10250 허용 필요

---

## Pattern 3: Pod -> EKS Control Plane

Pod가 CoreDNS를 경유하여 API Server에 접근

- CNI 동작: Pod IP (10.85.x.x)를 Node IP (10.80.x.x)로 SNAT 처리 후 전송

```bash
cilium status --verbose  # NAT 정책 확인
```

---

## Pattern 4: Control Plane -> Pod (Webhooks)

Admission Webhook 호출 — **Routable Pod CIDR 필수**

> 중요: Remote Pod CIDR이 라우팅 가능해야만 동작합니다. BGP 또는 Static Route 필수.

---

## Pattern 5: Pod <-> Pod (Hybrid Nodes 간)

VXLAN 캡슐화를 통한 노드 간 Pod 통신

- Cilium VXLAN: Port 8472/UDP 사용
- 방화벽에서 양방향 허용 필요

```bash
# UDP 8472 양방향 허용:
iptables -A INPUT -p udp --dport 8472 -j ACCEPT
```

---

## Pattern 6: Cloud Pod <-> Hybrid Pod

EC2 Pod와 Hybrid Node Pod 간 Cross-boundary 통신

- 필수 설정: Pod CIDR 라우팅 + VPC 라우트 테이블에 온프렘 CIDR 추가

```bash
aws ec2 create-route --route-table-id rtb-xxx \
  --destination 10.85.0.0/16 --transit-gateway-id tgw-xxx
```

---

## 방화벽 규칙 요약

네트워크 팀과 사전 조율이 필요한 포트 목록

| 포트 | 프로토콜 | 방향 | 용도 |
|------|----------|------|------|
| 443 | TCP | On-Prem -> AWS | Kubelet -> API Server |
| 10250 | TCP | AWS -> On-Prem | API Server -> Kubelet |
| 8472 | UDP | 양방향 | Cilium VXLAN |
| 4240 | TCP | 양방향 | Cilium Health Check |
| 53 | TCP/UDP | 양방향 | CoreDNS |

> Tip: 초기 테스트 시에는 넓은 범위로 열고, 안정화 후 최소 권한으로 제한

---

## VPC 엔드포인트 구성

Private Link를 통한 AWS 서비스 접근

### 필수 (Required)
| 서비스 | 엔드포인트 |
|--------|-----------|
| EKS | eks.\<region\> |
| ECR API | api.ecr.\<region\> |
| ECR DKR | \<acct\>.dkr.ecr.\<region\> |
| S3 | Gateway Endpoint |
| STS | sts.\<region\> |

### 선택 (Optional)
| 서비스 | 엔드포인트 |
|--------|-----------|
| SSM | ssm.\<region\> |
| CloudWatch Logs | logs.\<region\> |
| EC2 | ec2.\<region\> |

> 에어갭 환경: 모든 엔드포인트가 필수이며, ECR 미러링 또는 프라이빗 레지스트리 구성 필요

---

## Block 2 Quiz

<!-- quiz -->

**Q1.** 온프레미스와 AWS 간 네트워크 연결 권장 방법은?
- A. 공용 인터넷 연결
- **B. AWS Direct Connect 또는 Site-to-Site VPN** <!-- correct -->
- C. SSH 터널링
- D. HTTP 프록시

**Q2.** Kubelet -> API Server 통신에 필수인 방화벽 포트는?
- A. 80/TCP
- **B. 443/TCP** <!-- correct -->
- C. 8080/TCP
- D. 22/TCP

**Q3.** Pod CIDR 설계 시 고려사항이 아닌 것은?
- A. VPC CIDR과 겹치지 않을 것
- B. RFC-1918 범위 내에 있을 것
- **C. /8 범위로 설정해야 함** <!-- correct -->
- D. Service CIDR과 겹치지 않을 것

**Q4.** EKS Hybrid Nodes 권장 네트워크 지연시간은?
- A. 10ms 이하
- B. 50ms 이하
- **C. 100ms 이하** <!-- correct -->
- D. 제한 없음

---

## Q&A

Block 2 핵심 요약:
- CIDR 겹침 방지 / 사전 설계 필수
- 6가지 트래픽 패턴 이해 & 방화벽 설정
- Private Endpoint 권장 (보안 강화)
- VPC 엔드포인트 / 에어갭 환경 핵심

---

## Deep Dive & References

### 공식 문서
- **EKS Hybrid Nodes - Networking**: 네트워크 전제조건, CIDR 설계, 트래픽 패턴 가이드
- **VPC Endpoints for EKS**: Private 연결을 위한 VPC 엔드포인트 설정 가이드
- **EKS Hybrid Nodes - Firewall**: 필수 방화벽 포트 및 네트워크 요구사항

### 추가 리소스
- **Cilium Documentation**: VXLAN 터널링, IPAM, 네트워크 정책 심층 가이드
- **AWS Blog - EKS Hybrid Nodes**: 실전 사례와 아키텍처 패턴 블로그

---

<!-- Block 3: 노드 구성 & 운영 (10분) -->

# 노드 구성 & 운영

nodeadm CLI, Bootstrap, Cilium CNI, 업그레이드

---

## nodeadm CLI

Hybrid Node 부트스트랩을 위한 핵심 도구

```bash
# nodeadm 다운로드
curl -OL 'https://hybrid-assets.eks.amazonaws.com/releases/latest/bin/linux/amd64/nodeadm'
chmod +x nodeadm && sudo mv nodeadm /usr/local/bin/

# 의존성 설치
sudo nodeadm install 1.31 --credential-provider ssm

# 노드 초기화
sudo nodeadm init --config-source file://nodeconfig.yaml

# 노드 업그레이드
sudo nodeadm upgrade 1.32 --config-source file://nodeconfig.yaml

# 디버그
sudo nodeadm debug
```

주요 명령어: `install`, `init`, `upgrade`, `debug`

---

## Bootstrap 워크플로우

온프레미스 노드가 EKS 클러스터에 조인되는 8단계

<!-- canvas: bootstrap-canvas, interactive -->

1. nodeadm install
2. NodeConfig 로드
3. 크리덴셜 획득 (SSM/IAM RA)
4. kubelet 설정 생성
5. containerd 시작
6. kubelet 시작
7. CSR 제출
8. Node Ready

---

## NodeConfig YAML

노드 설정의 핵심 - 4가지 주요 섹션

<!-- tabs: cluster | hybrid | kubelet | containerd -->

```yaml
apiVersion: node.eks.aws/v1alpha1
kind: NodeConfig
spec:
  cluster:
    name: my-hybrid-cluster
    region: ap-northeast-2
    apiServerEndpoint: https://XXXXX.gr7.ap-northeast-2.eks.amazonaws.com
    certificateAuthority: |
      -----BEGIN CERTIFICATE-----
      MIIDxxxx...
      -----END CERTIFICATE-----
    cidr: 10.100.0.0/16
```

---

## CNI 선택 가이드

왜 Cilium인가?

### Cilium (공식 지원)
- eBPF 기반 데이터 플레인 - iptables 불필요
- AWS ECR Public에서 공식 빌드 제공
- VXLAN 오버레이 내장
- Hubble로 네트워크 observability
- BGP, Ingress, LB IPAM, kube-proxy replacement

### Calico (공식 미지원)
- iptables 기반 데이터 플레인
- AWS 공식 문서에서 제거됨
- AWS 기술 지원 범위 밖

> Calico는 더 이상 AWS 공식 지원 대상이 아닙니다. 신규 배포는 반드시 Cilium을 사용하세요.

---

## Cilium CNI 설치

AWS ECR Public 공식 빌드 + Helm 배포

```bash
helm install cilium oci://public.ecr.aws/eks/cilium/cilium \
  --version 1.18.3-0 \
  --namespace kube-system \
  --values cilium-values.yaml
```

설치 후 확인:
```bash
cilium status
kubectl get pods -n kube-system -l k8s-app=cilium
cilium connectivity test
```

> Cilium은 Hybrid Nodes 전용입니다. 클라우드 노드의 VPC CNI와 독립 운영됩니다.

---

## Cilium Values & Pod CIDR

cilium-values.yaml 핵심 설정과 Pod CIDR 설계

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: eks.amazonaws.com/compute-type
              operator: In
              values: ["hybrid"]
ipam:
  mode: cluster-pool
  operator:
    clusterPoolIPv4MaskSize: 25
    clusterPoolIPv4PodCIDRList: ["10.85.0.0/16"]
```

> Pod CIDR은 배포 후 변경 불가! /25: 노드당 126 Pod, /24: 254 Pod

---

## 노드 등록 확인

kubectl 명령으로 Hybrid Node 상태 확인

```bash
$ kubectl get nodes
NAME              STATUS   ROLES    AGE   VERSION
hybrid-node-001   Ready    <none>   5m    v1.31.2-eks
hybrid-node-002   Ready    <none>   3m    v1.31.2-eks

$ kubectl describe node hybrid-node-001 | grep -A5 Labels
Labels:
  eks.amazonaws.com/compute-type=hybrid
  kubernetes.io/arch=amd64

$ kubectl get nodes -l eks.amazonaws.com/compute-type=hybrid
```

---

## 업그레이드 전략

안전한 Kubernetes 버전 업그레이드

### Rolling Upgrade (권장)
```bash
# 1. 노드 drain
kubectl drain hybrid-node-001 --ignore-daemonsets
# 2. 업그레이드
sudo nodeadm upgrade 1.32 --config-source file://nodeconfig.yaml
# 3. uncordon
kubectl uncordon hybrid-node-001
```

### Canary Upgrade (안전)
1. 1개 노드만 먼저 업그레이드
2. 24시간 모니터링 후 검증
3. 문제없으면 나머지 순차 진행

### Rollback
```bash
sudo nodeadm uninstall
sudo nodeadm install 1.31 --credential-provider ssm
sudo nodeadm init --config-source file://nodeconfig.yaml
```

---

## 에어갭 환경

인터넷 연결 없이 Hybrid Nodes 운영하기

### Step 1: 사전 준비 (인터넷 호스트)
- hybrid-assets.eks.amazonaws.com에서 아티팩트 다운로드
- nodeadm, kubelet, containerd 바이너리 + S3 업로드
- Cilium 컨테이너 이미지 미러링

### Step 2: 런타임 (에어갭 환경)
- Route 53 PHZ: hybrid-assets DNS override
- S3 VPC Endpoint: Private S3 접근
- ECR VPC Endpoint: 컨테이너 이미지 풀

---

## 트러블슈팅

자주 발생하는 문제와 해결 방법

<!-- tabs: NotReady | ImagePull | DNS -->

### NotReady
- 원인: CNI 미설치, kubelet 설정 오류, 네트워크 연결 실패
- 해결: `sudo nodeadm debug`, Cilium 상태 확인, 방화벽 포트 확인

### ImagePullBackOff
- 원인: ECR 접근 불가, VPC Endpoint 미설정, 크리덴셜 만료
- 해결: ECR 연결 테스트, VPC Endpoint 확인

### DNS
- 원인: CoreDNS Pod 미배포, toleration 누락
- 해결: CoreDNS tolerations 확인, topologySpreadConstraints로 분산 배치

---

## Block 3 퀴즈

<!-- quiz -->

**Q1.** nodeadm의 주요 역할은?
- A. EKS 클러스터 생성 및 관리
- **B. kubelet, containerd 등 노드 컴포넌트 설치 및 부트스트랩** <!-- correct -->
- C. Pod 스케줄링 및 로드 밸런싱
- D. 모니터링 메트릭 수집

**Q2.** nodeadm init 실행에 필요한 3가지 클러스터 정보는?
- A. VPC ID, Subnet ID, Security Group ID
- **B. 클러스터 이름, API 서버 엔드포인트, CA 인증서** <!-- correct -->
- C. IAM Role ARN, Instance Type, AMI ID
- D. Region, Availability Zone, Instance ID

**Q3.** NodeConfig YAML에서 유효하지 않은 kubelet 설정은?
- A. maxPods
- B. shutdownGracePeriod
- C. node-labels
- **D. podScheduler** <!-- correct -->

---

## Deep Dive & References

### 공식 문서
- **nodeadm CLI Reference**: nodeadm 부트스트랩 가이드
- **NodeConfig YAML Reference**: cluster, hybrid, kubelet, containerd 4개 섹션 상세 스펙
- **Credential Providers**: SSM vs IAM Roles Anywhere 비교

### 추가 리소스
- **Cilium Install Guide for EKS**: Helm values, IPAM, VXLAN 설정
- **Air-Gapped Environment Setup**: 오프라인 설치 가이드

---

<!-- Block 4: 고급 패턴 & 전략적 가치 (10분) -->

# 고급 패턴 & 전략적 가치

Cloud Bursting, 규제 대응, AI Agent, 비용 최적화

---

## Taint/Toleration으로 워크로드 격리

하이브리드 노드에 특정 Pod만 스케줄링

```yaml
# 노드 Taint (자동 부여)
--register-with-taints=eks.amazonaws.com/compute-type=hybrid:NoSchedule

# Pod Toleration + NodeAffinity (둘 다 필요!)
tolerations:
  - key: eks.amazonaws.com/compute-type
    operator: Equal
    value: hybrid
    effect: NoSchedule
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: eks.amazonaws.com/compute-type
              operator: In
              values: ["hybrid"]
```

> Toleration: 스케줄링 허용 | NodeAffinity: 배치 강제. 둘 다 설정해야 완전한 격리.

---

## Cloud Bursting with Karpenter

온프레미스 용량 초과 시 클라우드로 자동 확장

<!-- canvas: bursting-canvas, interactive -->

- **Scale-out**: 온프렘 가득 차면 Karpenter가 클라우드 노드 프로비저닝
- **Scale-in**: pod-deletion-cost로 클라우드 Pod 먼저 제거

---

## Pod Deletion Cost 전략

스케일다운 시 클라우드 Pod 우선 제거

```yaml
# 온프렘 Pod - 높은 deletion cost (보존)
metadata:
  annotations:
    controller.kubernetes.io/pod-deletion-cost: "1000"
---
# 클라우드 Pod - 낮은 deletion cost (먼저 제거)
metadata:
  annotations:
    controller.kubernetes.io/pod-deletion-cost: "-100"
```

> 적용 방법: MutatingWebhook으로 노드 레이블 기반 자동 주입 또는 Kyverno/OPA 정책

---

## MutatingAdmissionWebhook 자동 주입

Pod Deletion Cost / Tolerations 자동 설정

```yaml
# WebhookConfiguration
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: hybrid-pod-mutator
webhooks:
  - name: hybrid.mutate.pods
    namespaceSelector:
      matchLabels:
        hybrid-inject: "enabled"
    rules:
      - apiGroups: [""]
        resources: ["pods"]
        operations: ["CREATE"]
```

주입 결과: pod-deletion-cost annotation + hybrid toleration 자동 추가

---

## 규제 대응 & 컴플라이언스

데이터 주권 보장과 감사 추적

- **데이터 위치 선택권**: 데이터를 온프레미스에 유지하면서 CP만 AWS
- **감사 추적**: IAM Roles Anywhere의 x509Subject/CN으로 노드별 감사 추적
- **네트워크 격리**: VPN/DX + Private Endpoint로 퍼블릭 인터넷 경유 없음
- **컴플라이언스 자동화**: AWS Config, CloudTrail로 CP 컴플라이언스 모니터링

적용 규제:
- 금융권 클라우드 이용가이드라인 충족
- 개인정보보호법 데이터 위치 선택권
- 내부 보안 정책 유연한 배치 선택

---

## AWS Managed Services 연계

온프레미스에서 AWS AI/ML 서비스 직접 활용

<!-- canvas: agent-canvas, interactive -->

Pod Identity -> STS -> Bedrock/S3 연동 5단계:
1. Pod에 ServiceAccount 연결
2. EKS Pod Identity Agent가 임시 자격증명 발급
3. STS AssumeRole
4. Bedrock/S3/SageMaker API 호출
5. 응답 수신

> 핵심: Pod Identity를 통해 온프렘 Pod가 AWS IAM Role을 직접 Assume

---

## AI Agent 개발 가속화

LLM Gateway: 모델 실험 / GPU Bursting / PII 라우팅

<!-- svg: llm-gateway diagram -->

### UC1: 모델 실험 -> 온프렘 전환
AWS GPU에서 모델 실험 -> 적절한 GPU 선정 -> 온프렘 장비 구매 -> Hybrid Node 등록

### UC2: GPU Bursting (확장)
온프렘 GPU 부족 시 Bedrock/SageMaker로 버스팅

### UC3: PII 라우팅
- 개인정보 포함 -> 온프렘 GPU
- 개인정보 미포함 -> Bedrock Claude

AgentCore Runtime + MCP Servers가 클라우드에서 오케스트레이션

---

## 비용 최적화 전략

기존 인프라 활용 + 필요 시 클라우드 확장

| 항목 | 내용 |
|------|------|
| **$0.02/vCPU/hr** | EKS Hybrid Nodes 추가 비용 |
| **$0.10/hr** | EKS 클러스터 비용 (CP 관리) |
| **100%** | 기존 하드웨어 활용, GPU 투자 보존 |
| **On-Demand** | 피크 시에만 클라우드 버스팅 |

> 비용 철학: 기존 인프라 투자를 보존하면서 AWS Managed Services의 가치를 더하는 접근
> CapEx는 유지, OpEx는 최적화

---

## 왜 EKS Hybrid Nodes인가?

Tanzu(VKS) / OpenShift 대비 전략적 장점

| 축 | Tanzu/VKS | OpenShift | EKS Hybrid Nodes | 핵심 수치 |
|----|-----------|-----------|-------------------|-----------|
| 성능 | vGPU 오버헤드 10-20% | CRI-O+SELinux 5-10% | 베어메탈 0-2% | 처리량 23%UP |
| 유연성 | 온프렘 고정, 수동 확장 | ROSA 별도 구독 | 피크 시 자동 확장 | Cloud Burst |
| 운영 | etcd 직접 운영 | CP 자체 관리 | AWS 관리형 99.95% SLA | 인력 60% 절감 |
| 비용 | vSphere 라이센스 | $13K+/yr per node | $0.02/vCPU/hr | CapEx->OpEx |
| 최신기술 | vSphere 버전 락인 | K8s 3-6개월 지연 | 최신 드라이버 즉시 | TensorRT-LLM |

---

## 핵심 요약

- EKS CP는 AWS가 관리 / 온프렘 인프라 활용
- VPN/DX로 안전한 하이브리드 네트워킹
- nodeadm으로 간편한 노드 부트스트랩
- Bedrock/AgentCore 등 AWS AI 서비스 즉시 연동
- 데이터 주권 유지 + 관리형 서비스 활용

### 참고 자료
- EKS Hybrid Nodes 공식 문서
- AWS re:Invent 2024 세션
- EKS Best Practices Guide

---

## Thank You

감사합니다

추가 질문이나 PoC 논의가 필요하시면 언제든 연락 주세요.
