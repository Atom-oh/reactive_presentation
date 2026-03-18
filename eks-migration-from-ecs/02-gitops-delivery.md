---
remarp: true
block: gitops-delivery
---

# ECS → EKS Migration Deep Dive
GitOps & Progressive Delivery

@type: cover
@background: common/pptx-theme/images/Picture_13.png
@badge: common/pptx-theme/images/Picture_8.png

오준석 (Junseok Oh)
Sr. Solutions Architect, AWS
화해 글로벌

:::notes
{timing: 1.5min}
Block 02에서는 GitOps와 Progressive Delivery에 대해 다룹니다. ArgoCD를 활용한 선언적 배포와 Argo Rollouts + Istio를 통한 안전한 Canary 배포 전략을 살펴보겠습니다.

{cue: question}
예상 질문:
- "GitOps 도입 시 기존 Jenkins 파이프라인은 어떻게 되나요?" → CI(빌드/테스트)는 Jenkins 유지, CD(배포)만 ArgoCD로 전환하는 것이 일반적입니다.
:::

---

@type: content

## CI/CD Pain Point

> "CI/CD 파이프라인과 EKS 배포 연동이 미흡하고, 배포 실패 시 롤백이 수동으로 진행됩니다."

::: left
### 현재 문제점
- Jenkins/CodePipeline 기반 Push 모델
- 배포 상태 추적 어려움
- 롤백 시 수동 개입 필요
- 환경별 설정 일관성 부족
:::

::: right
### GitOps 도입 효과
- Git = Single Source of Truth
- 자동화된 Drift Detection
- 메트릭 기반 자동 롤백
- 환경별 설정 코드화
:::

:::notes
{timing: 2.5min}
{cue: pause}
현재 Push 기반 배포의 문제점입니다. 배포 파이프라인이 클러스터에 직접 kubectl apply를 실행하는 방식은 배포 상태 추적이 어렵고, 실패 시 롤백도 수동입니다. GitOps는 이 문제를 Pull 모델로 해결합니다.

{cue: question}
예상 질문:
- "Pull 모델이면 배포 지연이 생기지 않나요?" → ArgoCD의 기본 Sync 간격은 3분이지만, Webhook으로 즉시 Sync를 트리거할 수 있어 Push 모델과 속도 차이가 거의 없습니다.
:::

---

@type: content

## IaC 전략: Terraform + ArgoCD

@img: diagrams/iac-terraform-argocd.svg center 100%

:::notes
{timing: 2min}
인프라와 애플리케이션 배포를 분리하는 전략입니다. Terraform은 EKS 클러스터, VPC, IAM 등 인프라를 관리하고, ArgoCD는 Kubernetes 워크로드를 관리합니다. 이 분리를 통해 인프라 변경과 애플리케이션 배포의 책임을 명확히 구분합니다.

{cue: question}
예상 질문:
- "Terraform과 ArgoCD 중 하나만 쓰면 안 되나요?" → 둘의 강점이 다릅니다. Terraform은 AWS 리소스 상태 관리에 최적화, ArgoCD는 K8s 워크로드 지속 동기화에 최적화되어 있습니다.
:::

---

@type: tabs

## Terraform vs ArgoCD vs ACK 의사결정

### 의사결정 매트릭스
| 리소스 특성 | Terraform | ArgoCD | ACK |
|------------|-----------|--------|-----|
| EKS 클러스터, VPC, Subnet | **✅ 권장** | ❌ | ❌ |
| EKS Add-on (VPC CNI, CoreDNS) | **✅ 권장** | △ 가능 | △ 가능 |
| K8s Controller (ALB, ExternalDNS) | △ 가능 | **✅ 권장** | ❌ |
| 앱 Deployment, Service | ❌ | **✅ 권장** | ❌ |
| 앱 전용 S3 Bucket | △ 가능 | △ 가능 | **✅ 권장** |
| 앱 전용 SQS Queue | △ 가능 | △ 가능 | **✅ 권장** |
| 앱 전용 IAM Role | **✅ 권장** | ❌ | △ 가능 |
| 공용 RDS/Aurora | **✅ 권장** | ❌ | △ 가능 |
| 공용 ElastiCache | **✅ 권장** | ❌ | △ 가능 |

**핵심 원칙**: 리소스의 생명주기가 앱과 같으면 → ACK/ArgoCD, 인프라 수준이면 → Terraform

### ACK 개요
**AWS Controllers for Kubernetes (ACK)**
- Kubernetes CR로 AWS 리소스를 선언적 관리
- `kubectl apply`로 S3, SQS, RDS 등 생성/삭제
- ArgoCD와 자연스럽게 통합 (GitOps)

```yaml {filename="sqs-queue.yaml"}
# ACK로 SQS Queue 생성
apiVersion: sqs.services.k8s.aws/v1alpha1
kind: Queue
metadata:
  name: order-queue
  namespace: production
spec:
  queueName: hwahae-order-queue
  visibilityTimeout: "30"
  tags:
    - key: team
      value: backend
```

**장점**: 앱과 AWS 리소스를 동일한 GitOps 워크플로우로 관리
**제한**: IAM, VPC 등 인프라 리소스는 지원 제한적

### ACK vs Terraform 선택 기준
```
앱 전용 AWS 리소스인가?
  ├─ Yes → 리소스 생명주기가 앱과 동일한가?
  │         ├─ Yes → ACK (GitOps 통합)
  │         └─ No  → Terraform
  └─ No (공용 리소스) → Terraform

보안 민감 리소스인가? (IAM Role, SG)
  ├─ Yes → Terraform (변경 이력 + Plan 검증)
  └─ No  → ACK 또는 Terraform
```

**화해 현재 구조와 매핑**:
- `terraform/`: EKS, VPC, 공용 RDS, IAM → 유지
- `terraform/applications/<app>/`: 앱 전용 SG, IAM → 유지 (보안상 Terraform 권장)
- **신규**: 앱 전용 S3, SQS, SNS → ACK로 전환 검토

### EKS Capabilities 의사결정
**EKS Capabilities** (관리형 Add-on, Auto Mode 등)

| 항목 | EKS Add-on (Terraform) | ArgoCD | 판단 기준 |
|------|------------------------|--------|-----------|
| VPC CNI | **✅** | △ | EKS API 통합, 자동 업그레이드 |
| CoreDNS | **✅** | △ | EKS 버전 호환성 자동 관리 |
| kube-proxy | **✅** | △ | EKS 버전 연동 |
| AWS LB Controller | △ | **✅** | Helm values 커스터마이징 필요 |
| External DNS | ❌ | **✅** | K8s 네이티브 설정 |
| Cert Manager | ❌ | **✅** | K8s 네이티브 설정 |
| Karpenter | △ | **✅** | NodePool CRD는 ArgoCD가 적합 |
| ADOT/CloudWatch Agent | **✅** | △ | EKS Add-on으로 간편 관리 |

**원칙**: EKS API로 관리되는 핵심 네트워킹/시스템 컴포넌트는 Terraform, 나머지 Controller는 ArgoCD

:::notes
{timing: 3.5min}
Terraform, ArgoCD, ACK의 역할 분담 의사결정 가이드입니다. 핵심은 리소스의 생명주기입니다. 앱과 함께 생성/삭제되는 리소스는 ACK로 GitOps 통합하고, 인프라 수준의 장기 리소스는 Terraform으로 관리합니다. 화해의 현재 Terraform + ArgoCD 구조는 잘 설계되어 있으며, 여기에 ACK를 추가하면 앱 전용 S3, SQS 등을 더 효율적으로 관리할 수 있습니다. EKS Capabilities 중 VPC CNI, CoreDNS 등은 EKS Add-on으로, ALB Controller, Karpenter 등은 ArgoCD로 관리하는 것이 적합합니다.

{cue: question}
💬 예상 질문:
• "ACK가 Terraform을 완전히 대체할 수 있나요?" → 아니요. IAM, VPC 등 보안 민감 리소스는 Terraform의 Plan/Apply 워크플로우가 더 안전합니다. ACK는 앱 전용 리소스에만 권장합니다.
• "ACK 도입 시 러닝 커브가 크나요?" → K8s에 익숙하다면 낮습니다. CRD 형태로 AWS 리소스를 정의하므로 kubectl로 관리할 수 있습니다.
:::

---

@type: code

## ACK 실전 설정

```yaml {filename="ack-setup.yaml"}
# 1. ACK S3 Controller 설치 (ArgoCD Application)
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ack-s3-controller
  namespace: argocd
spec:
  source:
    chart: s3-chart
    repoURL: public.ecr.aws/aws-controllers-k8s
    targetRevision: v1.0.15
    helm:
      values: |
        serviceAccount:
          annotations:
            eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/ACK-S3-Role
  destination:
    server: https://kubernetes.default.svc
    namespace: ack-system
```

:::notes
{timing: 2min}
ACK 실전 설정 예시입니다. ACK Controller는 ArgoCD Application으로 설치하고, IRSA로 AWS 권한을 부여합니다.

💬 예상 질문:
• "ACK Controller 설치가 복잡한가요?" → Helm Chart로 ArgoCD Application 하나만 등록하면 됩니다. IRSA 설정만 주의하면 됩니다.
:::

---

@type: code

## ACK 리소스 매니페스트

:::col-2
```yaml {filename="s3-bucket.yaml"}
# 앱 전용 S3 Bucket
apiVersion: s3.services.k8s.aws/v1alpha1
kind: Bucket
metadata:
  name: hwahae-user-uploads
  namespace: production
spec:
  name: hwahae-user-uploads-prod
  versioning:
    status: Enabled
  encryption:
    rules:
      - applyServerSideEncryptionByDefault:
          sseAlgorithm: aws:kms
```
:::

:::col-2
```yaml {filename="sqs-queue.yaml"}
# 앱 전용 SQS Queue
apiVersion: sqs.services.k8s.aws/v1alpha1
kind: Queue
metadata:
  name: order-processing
  namespace: production
spec:
  queueName: hwahae-order-processing
  visibilityTimeout: "60"
  messageRetentionPeriod: "345600"
  redrivePolicy: |
    {
      "deadLetterTargetArn": "...-dlq",
      "maxReceiveCount": 3
    }
```
:::

**효과**: K8s 매니페스트로 AWS 리소스 관리 → 앱팀 셀프서비스, ArgoCD GitOps 일원화

:::notes
{timing: 1.5min}
ACK로 관리하는 앱 전용 AWS 리소스 매니페스트입니다. S3 Bucket과 SQS Queue를 Kubernetes CR로 정의하면, ArgoCD가 앱 배포와 함께 AWS 리소스도 자동으로 생성합니다. 라이프사이클이 앱과 일치합니다.

💬 예상 질문:
• "ACK로 만든 리소스 삭제 시 실제 AWS 리소스도 삭제되나요?" → 기본적으로 예. 하지만 deletionPolicy를 retain으로 설정하면 CR 삭제 시에도 AWS 리소스는 유지됩니다.
:::

---

@type: compare

## ArgoCD Sync vs Argo Rollouts

::: left
### ArgoCD Sync (일반 배포)
- Git 변경 감지 → 자동/수동 Sync
- Deployment의 기본 RollingUpdate 사용
- **장점**: 설정 간단, 빠른 배포
- **단점**: 세밀한 트래픽 제어 불가
- **적합**: 내부 서비스, 개발 환경

```yaml
syncPolicy:
  automated:
    prune: true
    selfHeal: true
```
:::

::: right
### Argo Rollouts (Progressive Delivery)
- Canary / Blue-Green 배포 지원
- 트래픽 가중치 단계별 조정
- **장점**: 메트릭 기반 자동 롤백
- **장점**: Istio VirtualService 연동
- **적합**: 프로덕션, 고객 대면 서비스

```yaml
strategy:
  canary:
    steps:
      - setWeight: 10
      - analysis: {templates: [success-rate]}
      - setWeight: 50
```
:::

:::notes
{timing: 2.5min}
ArgoCD의 기본 Sync와 Argo Rollouts의 차이입니다. 일반 배포는 Kubernetes의 RollingUpdate를 사용하고, Rollouts는 트래픽 가중치를 단계별로 조정하며 메트릭 분석을 통해 자동 롤백할 수 있습니다.

{cue: question}
예상 질문:
- "모든 서비스에 Argo Rollouts를 적용해야 하나요?" → 아니요. 내부 서비스나 개발 환경은 기본 RollingUpdate로 충분합니다. 고객 대면 프로덕션 서비스에만 Rollouts를 적용하는 것이 효율적입니다.
:::

---

@type: canvas
@canvas-id: argo-rollouts-canary

## Argo Rollouts + Istio Canary Architecture

:::canvas
# Step 1: 서비스 구성요소 표시
icon rollout "Argo-Rollouts" at 100,80 size 48 step 1
box stable "Stable Pods (v1)" at 300,50 size 140,50 color #00C7B7 step 1
box canary "Canary Pods (v2)" at 300,130 size 140,50 color #FF9900 step 1

# Step 2: Istio VirtualService
icon istio "Istio" at 100,180 size 48 step 2
box vs "VirtualService" at 220,170 size 120,40 color #326CE5 step 2
box dr "DestinationRule" at 380,170 size 120,40 color #326CE5 step 2

# Step 3: 트래픽 가중치 표시
arrow vs -> stable "90%" color #00C7B7 step 3
arrow vs -> canary "10%" color #FF9900 step 3

# Step 4: Analysis 연동
icon prometheus "Prometheus" at 550,80 size 48 step 4
box analysis "AnalysisRun" at 520,150 size 100,40 color #FFA726 step 4
arrow canary -> prometheus "metrics" style dashed step 4
arrow analysis -> rollout "pass/fail" style dashed step 4

# Step 5: Promote 또는 Rollback
box promote "Promote → 100%" at 100,280 size 120,40 color #4CAF50 step 5
box rollback "Rollback → 0%" at 280,280 size 120,40 color #f44336 step 5
:::

:::notes
{timing: 3min}
Argo Rollouts와 Istio 통합 아키텍처입니다. Rollouts 컨트롤러가 VirtualService의 가중치를 자동으로 조정하고, AnalysisRun이 Prometheus 메트릭을 조회하여 성공/실패를 판단합니다. 성공률이 임계값 미만이면 자동으로 롤백됩니다.

GitBook 참고: https://atomoh.gitbook.io/kubernetes-docs/service-mesh/istio/advanced/08-argo-rollouts

{cue: question}
예상 질문:
- "AnalysisTemplate에서 어떤 메트릭을 주로 사용하나요?" → 에러율(5xx), 레이턴시(p99), 성공률이 기본입니다. 비즈니스 메트릭(주문 성공률 등)을 추가하면 더 정교한 판단이 가능합니다.
:::

---

@type: timeline

## Canary Deployment Flow

1. **10%** — 초기 트래픽 전환, 2분 대기 후 메트릭 분석
2. **30%** — 성공 시 트래픽 증가, 에러율 모니터링
3. **50%** — 절반 전환, 5분간 안정성 검증
4. **80%** — 대부분 전환, 최종 검증
5. **100%** — 완전 전환, Stable로 Promote

:::notes
{timing: 2.5min}
Canary 배포의 각 단계입니다. 작은 트래픽부터 시작하여 점진적으로 증가시키며, 각 단계에서 메트릭을 분석합니다. 문제 발생 시 즉시 롤백하여 사용자 영향을 최소화합니다.

{cue: question}
예상 질문:
- "각 단계의 대기 시간은 어떻게 정하나요?" → 서비스 특성에 따라 다릅니다. 트래픽이 많은 서비스는 2-3분이면 충분하고, 트래픽이 적으면 5-10분으로 늘려야 의미 있는 메트릭을 수집할 수 있습니다.
:::

---

@type: tabs

## Zone-Aware PDB 방어 시나리오

### Spot 중단 시 PDB 동작
```
Initial State: Zone A (3 Pods), Zone C (3 Pods)
               PDB: maxUnavailable=2

Step 1: Spot 중단 알림 (Zone A 전체)
        → Karpenter가 3개 Pod 동시 퇴거 시도

Step 2: PDB가 개입
        → 최대 2개만 동시 Terminating 허용
        → 1개는 대기 (Pending Termination)

Step 3: 새 노드 프로비저닝 (30-60초)
        → Zone A 또는 Zone C에 새 노드 생성

Step 4: Pod 1개 재스케줄링
        → Running 상태 확인

Step 5: 대기 중이던 Pod Termination 허용
        → 다시 최대 2개 Terminating

Step 6-7: 반복하여 모든 Pod 안전하게 마이그레이션
```

**핵심**: PDB 없이는 모든 Pod가 동시 Terminating → 서비스 중단

### PDB 설정 예시
```yaml {filename="pdb.yaml" highlight="6-8"}
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb
  namespace: production
spec:
  maxUnavailable: 2          # 동시 2개만 중단 허용
  # 또는 minAvailable: 4     # 최소 4개 유지
  selector:
    matchLabels:
      app: api-server
```

**maxUnavailable vs minAvailable**:
- maxUnavailable: 수평 확장되는 워크로드에 직관적
- minAvailable: 절대적 최소 가용성이 중요할 때

:::notes
{timing: 3.5min}
Zone-Aware PDB 방어 시나리오입니다. Spot Instance 회수 시 PDB가 Pod를 2개씩만 순차적으로 퇴거시키는 과정을 7단계로 보여줍니다. maxUnavailable=2 설정으로 한 번에 2개만 중단되어 서비스 가용성을 유지합니다.

{cue: question}
예상 질문:
- "PDB 없이 Spot이 회수되면 어떻게 되나요?" → 모든 Pod가 동시에 Terminating 되어 서비스 중단이 발생합니다. PDB는 이를 방지하는 안전장치입니다.
- "maxUnavailable vs minAvailable 어떤 것을 쓰나요?" → 둘 다 가능하지만, 수평 확장되는 워크로드는 maxUnavailable이 더 직관적입니다.
:::

---

@type: canvas
@canvas-id: zone-aware-rollouts

## Zone-Aware Rollouts

:::canvas
# Step 1: Zone별 클러스터 표시
box zoneA "Zone A Cluster" at 50,50 size 200,180 color #232F3E step 1
box zoneC "Zone C Cluster" at 300,50 size 200,180 color #232F3E step 1

# Step 2: Zone별 Rollout
box rolloutA "Rollout A" at 80,80 size 80,30 color #E6522C step 2
box stableA "Stable" at 70,120 size 60,25 color #00C7B7 step 2
box canaryA "Canary" at 140,120 size 60,25 color #FF9900 step 2

box rolloutC "Rollout C" at 330,80 size 80,30 color #E6522C step 2
box stableC "Stable" at 320,120 size 60,25 color #00C7B7 step 2
box canaryC "Canary" at 390,120 size 60,25 color #FF9900 step 2

# Step 3: 독립적 PDB
box pdbA "PDB: minAvailable=2" at 70,160 size 140,25 color #9C27B0 step 3
box pdbC "PDB: minAvailable=2" at 320,160 size 140,25 color #9C27B0 step 3

# Step 4: Locality Failover
icon nlb "NLB" at 250,270 size 48 step 4
arrow nlb -> zoneA "50%" step 4
arrow nlb -> zoneC "50%" step 4
box failover "Zone 장애 시 자동 Failover" at 180,320 size 200,30 color #f44336 step 4
:::

:::notes
{timing: 3min}
Zone-Aware Rollouts 아키텍처입니다. 각 Zone의 Rollout이 독립적인 PDB를 관리하여, 한 Zone의 Spot Instance 중단이 다른 Zone에 영향을 주지 않습니다. Istio의 locality-aware 라우팅으로 Zone 장애 시 자동 Failover됩니다.

GitBook 참고: https://atomoh.gitbook.io/kubernetes-docs/service-mesh/istio/advanced/09-zone-aware-argo-rollouts

{cue: question}
예상 질문:
- "Zone별 Rollout을 따로 관리하면 복잡도가 높아지지 않나요?" → 초기 설정은 복잡하지만, ApplicationSet으로 템플릿화하면 관리 부담이 줄어듭니다. Spot 사용률이 높은 환경에서는 이 복잡도가 가용성 향상으로 충분히 보상됩니다.
:::

---

@type: tabs

## GitHub Self-Hosted Runner (ARC)

### ARC 개요
**Actions Runner Controller (ARC)**
- GitHub Actions Self-Hosted Runner를 EKS에서 실행
- Runner Pod 자동 스케일링 (HRA)
- 워크로드별 Runner 격리 가능

**장점**:
- VPC 내부 리소스 접근 (RDS, ElastiCache)
- ECR Push 시 IAM Role 활용
- 빌드 캐시 PVC로 속도 향상

### 아키텍처
```
GitHub Actions Workflow
        ↓
  Webhook Event (workflow_job)
        ↓
  ARC Controller (EKS)
        ↓
  Runner Pod 생성 (ephemeral)
        ↓
  Job 실행 → ECR Push → ArgoCD Sync
        ↓
  Runner Pod 삭제
```

### 리소스 설정
```yaml
# Runner Pod 리소스
resources:
  requests:
    cpu: "500m"
    memory: "1Gi"
  limits:
    cpu: "2000m"
    memory: "4Gi"

# Runner 스케일링
minRunners: 1
maxRunners: 10
```

:::notes
{timing: 2.5min}
GitHub Actions Runner Controller(ARC)를 EKS에서 운영하는 방법입니다. Self-Hosted Runner를 사용하면 VPC 내부 리소스에 접근할 수 있고, IRSA를 통해 안전하게 ECR에 이미지를 Push할 수 있습니다.

{cue: question}
예상 질문:
- "GitHub-hosted runner 대비 비용 절감 효과가 있나요?" → Runner 자체는 무료이지만 EC2 비용이 발생합니다. 빌드가 많고 VPC 접근이 필요한 경우에만 비용 대비 효과가 있습니다.
:::

---

@type: code

## HorizontalRunnerAutoscaler - 자동 스케일링

```yaml {filename="arc-config.yaml" highlight="6-8,17-23,30-35"}
# 1. RunnerDeployment - Runner Pool 정의
apiVersion: actions.summerwind.dev/v1alpha1
kind: RunnerDeployment
metadata:
  name: hwahae-runners
  namespace: arc-runners
spec:
  replicas: 2
  template:
    spec:
      repository: hwahae/backend
      labels:
        - self-hosted
        - linux
        - eks
      serviceAccountName: arc-runner
      resources:
        requests:
          cpu: "500m"
          memory: "1Gi"
        limits:
          cpu: "2000m"
          memory: "4Gi"
      # Docker-in-Docker 설정
      dockerEnabled: true
      dockerMTU: 1400
# ---
# 2. HorizontalRunnerAutoscaler - 자동 스케일링
apiVersion: actions.summerwind.dev/v1alpha1
kind: HorizontalRunnerAutoscaler
metadata:
  name: hwahae-runners-autoscaler
  namespace: arc-runners
spec:
  scaleTargetRef:
    kind: RunnerDeployment
    name: hwahae-runners
  minReplicas: 1
  maxReplicas: 10
  metrics:
    - type: TotalNumberOfQueuedAndInProgressWorkflowRuns
      repositoryNames:
        - hwahae/backend
        - hwahae/frontend
# ---
# 3. ServiceAccount with IRSA
apiVersion: v1
kind: ServiceAccount
metadata:
  name: arc-runner
  namespace: arc-runners
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/ARC-Runner-Role
```

:::notes
{timing: 2min}
ARC 설정 예시입니다. RunnerDeployment로 Runner Pool을 정의하고, HorizontalRunnerAutoscaler로 대기 중인 Job 수에 따라 자동 스케일링합니다. IRSA를 통해 Runner Pod가 ECR, S3 등 AWS 리소스에 접근할 수 있습니다.

{cue: question}
예상 질문:
- "Runner Pod가 ephemeral인데 빌드 캐시는 어떻게 처리하나요?" → PVC를 마운트하여 Maven/npm 캐시를 유지하거나, S3 기반 원격 캐시를 사용합니다. Docker layer 캐시는 Kaniko + registry cache 조합이 효과적입니다.
:::

---

@type: compare

## NGINX Gateway Fabric vs Istio Gateway

::: left
### NGINX Gateway Fabric
**역할**: North-South 트래픽 (외부 → 클러스터)

- L4/L7 로드밸런싱
- TLS 종료
- Rate Limiting
- WAF 통합 가능
- **Gateway API 네이티브**

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: external-gateway
spec:
  gatewayClassName: nginx
  listeners:
    - name: https
      port: 443
      protocol: HTTPS
```
:::

::: right
### Istio Gateway
**역할**: East-West 트래픽 (Pod ↔ Pod)

- Service Mesh (mTLS)
- 트래픽 미러링
- Circuit Breaker
- Canary 배포 (Argo Rollouts 연동)
- **VirtualService/DestinationRule**

```yaml
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata:
  name: internal-routing
spec:
  hosts:
    - api-service
  http:
    - route:
        - destination:
            host: api-service
            subset: stable
          weight: 90
```
:::

:::notes
{timing: 2.5min}
{cue: question}
NGF와 Istio의 역할 분담입니다. 둘 다 사용할 필요가 있는지 질문을 많이 받는데요, 외부 트래픽 관리(NGF)와 내부 서비스 메시(Istio)는 다른 문제를 해결합니다. 화해처럼 Canary 배포가 필요한 경우 Istio가 필수입니다.

예상 질문:
- "Istio 없이 Canary 배포를 할 수 있는 방법은?" → NGINX Ingress나 ALB의 가중치 기반 라우팅으로 가능하지만, 메트릭 기반 자동 롤백은 Istio + Argo Rollouts 조합이 가장 성숙합니다.
:::

---

@type: checklist

## GitOps Best Practices

- [ ] **Repository 구조**
  - 모노레포 vs 폴리레포 결정
  - `base/` + `overlays/` Kustomize 구조
  - 환경별 브랜치 또는 디렉토리 분리

- [ ] **Sync 전략**
  - Dev/Staging: `automated` + `selfHeal: true`
  - Production: `manual` 또는 Sync Window 설정
  - `prune: true` 신중하게 적용

- [ ] **보안**
  - Sealed Secrets 또는 External Secrets Operator
  - RBAC: AppProject별 네임스페이스 제한
  - SSO 통합 (OIDC)

- [ ] **운영**
  - Notification 설정 (Slack, PagerDuty)
  - Application 상태 대시보드 구성
  - 정기적 Diff 리포트 검토

:::notes
{timing: 2.5min}
GitOps 도입 시 베스트 프랙티스입니다. 특히 프로덕션에서는 자동 동기화를 신중하게 설정해야 합니다. Sync Window를 활용하여 업무 시간 외에만 자동 배포가 되도록 제한하는 것을 권장합니다.

GitBook 참고: https://atomoh.gitbook.io/kubernetes-docs/gitops/argocd/09-best-practices

{cue: question}
예상 질문:
- "Sealed Secrets vs External Secrets Operator 중 어떤 것을 추천하나요?" → AWS 환경이면 ESO + Secrets Manager 조합을 권장합니다. 시크릿 로테이션이 자동화되고, 기존 AWS 시크릿을 재사용할 수 있습니다.
:::

---

@type: content

## AWS 리소스 관리: Terraform vs ArgoCD vs ACK

| 리소스 유형 | 관리 도구 | 예시 | 변경 빈도 |
|------------|----------|------|----------|
| **인프라 기반** | Terraform | VPC, EKS Cluster, RDS, IAM Role | 낮음 |
| **EKS 핵심 애드온** | Terraform (EKS Add-on) | VPC CNI, CoreDNS, kube-proxy, EBS CSI | 낮음 |
| **클러스터 컨트롤러** | ArgoCD | ALB Controller, External DNS, ESO, Cert Manager | 중간 |
| **App 전용 AWS 리소스** | ArgoCD or ACK | App별 SQS Queue, S3 Bucket, IAM Policy | 높음 |

:::callout-info
**화해 현재 원칙과 일치**: "EKS 내 리소스는 ArgoCD, 공용 AWS 리소스는 Terraform"
:::

:::callout-warning
**ACK 도입 시점**: App팀이 K8s 매니페스트로 SQS, S3 등 AWS 리소스를 직접 관리해야 할 때. 현재 단계에서는 Terraform + ArgoCD 이원화로 충분
:::

:::notes
{timing: 2.5min}
AWS 리소스를 어떤 도구로 관리할지에 대한 의사결정 매트릭스입니다.

핵심 원칙:
1. 인프라 기반(VPC, EKS, RDS)은 Terraform — 변경이 드물고, 상태 관리가 중요
2. EKS 핵심 애드온(VPC CNI, CoreDNS)도 Terraform의 EKS Add-on으로 — 클러스터 업그레이드와 함께 관리
3. 클러스터 내 컨트롤러(ALB Controller, ESO 등)는 ArgoCD — Helm Chart 기반 GitOps
4. App 전용 AWS 리소스는 상황에 따라 ArgoCD 또는 ACK

ACK(AWS Controllers for Kubernetes)는 K8s CRD로 AWS 리소스를 관리하는 도구입니다. App팀이 자율적으로 SQS Queue나 S3 Bucket을 생성해야 할 때 유용하지만, 현재 단계에서는 Terraform + ArgoCD 이원화로 충분합니다.

{cue: question}
💬 예상 질문:
• "EKS Add-on과 ArgoCD로 같은 컴포넌트를 관리하면 충돌나지 않나요?" → 네, 동일 컴포넌트를 두 곳에서 관리하면 안 됩니다. VPC CNI 같은 핵심 시스템은 EKS Add-on으로, ALB Controller 같은 확장 컴포넌트는 ArgoCD로 명확히 분리해야 합니다.
:::

---

@type: quiz

## Block 02 Quiz

**Q1: GitOps의 핵심 원칙은?**
- [ ] CI 파이프라인이 직접 kubectl apply 실행
- [x] Git이 Single Source of Truth
- [ ] 수동 배포로 변경 통제
- [ ] 환경별 설정을 별도 DB에 저장

**Q2: Argo Rollouts에서 Canary 배포 실패 시 동작은?**
- [ ] 수동으로 kubectl rollback 실행
- [ ] 배포가 그대로 유지됨
- [x] AnalysisRun 실패 시 자동 롤백
- [ ] 알림만 발송하고 대기

**Q3: Zone-Aware Rollouts의 주요 장점은?**
- [ ] 배포 속도가 빨라진다
- [x] Zone별 독립적 PDB로 Spot 중단 대응
- [ ] 단일 Rollout으로 모든 Zone 관리
- [ ] Istio 없이 Canary 배포 가능

**Q4: ArgoCD에서 프로덕션 환경 권장 Sync 정책은?**
- [ ] automated + selfHeal: true
- [x] manual 또는 Sync Window 설정
- [ ] prune: true + allowEmpty: true
- [ ] 자동 동기화 + 3분 간격

:::notes
{timing: 3min}
{cue: question}
Block 02 퀴즈입니다. GitOps와 Progressive Delivery의 핵심 개념을 확인합니다. 특히 프로덕션 환경에서의 안전한 배포 전략에 대해 복습해보세요.

예상 질문:
- "실제 마이그레이션 시 GitOps 도입 순서는?" → 1) ArgoCD 설치 및 기존 앱 등록 (manual sync), 2) Dev 환경에서 automated sync 테스트, 3) Staging에 Argo Rollouts 적용, 4) Production에 점진적 적용 순서를 권장합니다.
:::
