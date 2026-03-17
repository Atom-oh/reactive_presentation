---
remarp: true
block: security-platform
---

# Security & Platform Engineering
Block 04 (20 min)

@type: cover
@background: ../common/pptx-theme/images/Picture_13.png
@badge: ../common/pptx-theme/images/Picture_8.png

오준석 (Junseok Oh)
Sr. Solutions Architect | AWS

:::notes
{timing: 30s}
Block 04에서는 EKS 보안과 Platform Engineering을 다룹니다.
IAM 통합, Secret 관리, Network Policy를 학습하고, 개발자 Self-Service 환경 구축 방안을 살펴봅니다.
:::

---

## EKS Security Architecture

@type: content
@img: diagrams/eks-security-arch.svg center 90%

**보안 계층**:
1. **IAM Layer**: OIDC Provider → IRSA/Pod Identity → AWS 서비스 접근
2. **Cluster Layer**: RBAC, Access Entries, Cluster Endpoint 접근 제어
3. **Workload Layer**: Pod Security Standards, Network Policy
4. **Data Layer**: Secrets Manager, KMS 암호화

:::notes
{timing: 2min}
EKS 보안 아키텍처의 4개 계층입니다.
IAM Layer에서는 OIDC Provider를 통해 Pod가 AWS 서비스에 안전하게 접근합니다.
Cluster Layer에서는 RBAC과 Access Entries로 클러스터 접근을 제어합니다.
Workload Layer에서는 Pod Security Standards와 Network Policy로 워크로드를 격리합니다.
Data Layer에서는 Secrets Manager와 KMS로 민감 정보를 보호합니다.
:::

---

## aws-auth vs Access Entries

@type: compare

### aws-auth ConfigMap (Legacy)
- ConfigMap 기반 IAM 매핑
- 수동 편집 필요 (오류 발생 시 클러스터 접근 불가)
- 변경 이력 추적 어려움
- GitOps와 충돌 가능성
- **단점**: ConfigMap 삭제 시 클러스터 잠금

```yaml
# aws-auth ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::123456789012:role/NodeRole
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:bootstrappers
        - system:nodes
```

### Access Entries (권장)
- EKS API 기반 IAM 매핑
- AWS CLI/Console/IaC로 관리
- CloudTrail 감사 로그 자동 기록
- Terraform/CDK 완벽 지원
- **장점**: ConfigMap 삭제해도 클러스터 접근 유지

```bash
# Access Entry 생성
aws eks create-access-entry \
  --cluster-name my-cluster \
  --principal-arn arn:aws:iam::123456789012:role/DevRole \
  --type STANDARD
```

:::notes
{timing: 2min}
aws-auth ConfigMap과 Access Entries의 비교입니다.
aws-auth는 ConfigMap을 직접 편집해야 하는데, 실수로 삭제하면 클러스터에 접근할 수 없게 됩니다.
Access Entries는 EKS 1.23부터 지원되며, AWS API로 관리되어 더 안전하고 감사 추적이 용이합니다.
신규 클러스터는 Access Entries를, 기존 클러스터는 점진적 마이그레이션을 권장합니다.
:::

---

## Access Entries 설정

@type: code

```bash {highlight="2-5,10-14"}
# 1. Access Entry 생성
aws eks create-access-entry \
  --cluster-name hwahae-prod \
  --principal-arn arn:aws:iam::123456789012:role/DevOpsRole \
  --type STANDARD

# 2. Access Policy 연결 (RBAC 권한 부여)
aws eks associate-access-policy \
  --cluster-name hwahae-prod \
  --principal-arn arn:aws:iam::123456789012:role/DevOpsRole \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy \
  --access-scope type=cluster

# 사용 가능한 Policy:
# - AmazonEKSClusterAdminPolicy (전체 관리자)
# - AmazonEKSAdminPolicy (네임스페이스 관리자)
# - AmazonEKSEditPolicy (편집 권한)
# - AmazonEKSViewPolicy (읽기 권한)
```

```hcl {filename="terraform/access-entries.tf"}
# Terraform으로 Access Entry 관리
resource "aws_eks_access_entry" "devops" {
  cluster_name  = aws_eks_cluster.main.name
  principal_arn = aws_iam_role.devops.arn
  type          = "STANDARD"
}

resource "aws_eks_access_policy_association" "devops" {
  cluster_name  = aws_eks_cluster.main.name
  principal_arn = aws_iam_role.devops.arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSAdminPolicy"

  access_scope {
    type       = "namespace"
    namespaces = ["production", "staging"]
  }
}
```

:::notes
{timing: 2min}
Access Entries 설정 방법입니다.
먼저 create-access-entry로 IAM Role을 등록하고, associate-access-policy로 권한을 부여합니다.
access-scope를 namespace로 제한하면 특정 네임스페이스에만 권한을 부여할 수 있습니다.
Terraform으로 관리하면 GitOps 워크플로우와 완벽하게 통합됩니다.
:::

---

@type: tabs

## RBAC — ClusterRole, Role, RoleBinding

### RBAC 계층 구조
```
IAM Role (AWS)
  ↓ Access Entries
EKS Cluster
  ↓ ClusterRoleBinding / RoleBinding
Kubernetes RBAC
  ├─ ClusterRole    → 클러스터 전체 범위
  ├─ Role           → 네임스페이스 범위
  ├─ ClusterRoleBinding → ClusterRole ↔ Subject 연결
  └─ RoleBinding    → Role ↔ Subject 연결
```

| 리소스 | 범위 | 용도 |
|--------|------|------|
| **ClusterRole** | 클러스터 전체 | 노드 조회, CRD 관리, 전체 네임스페이스 읽기 |
| **Role** | 네임스페이스 | 특정 네임스페이스 내 Pod/Service/ConfigMap 관리 |
| **ClusterRoleBinding** | 클러스터 전체 | ClusterRole을 사용자/그룹에 바인딩 |
| **RoleBinding** | 네임스페이스 | Role 또는 ClusterRole을 네임스페이스 범위로 바인딩 |

**핵심**: RoleBinding은 ClusterRole도 참조 가능 → 네임스페이스 범위로 축소 적용

### 팀별 RBAC 설계
```yaml
# 1. ClusterRole — 공통 읽기 권한 (전체 팀 공유)
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: namespace-viewer
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "configmaps", "events"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets", "statefulsets"]
    verbs: ["get", "list", "watch"]
# ---
# 2. Role — 네임스페이스별 배포 권한
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: deployer
  namespace: backend
rules:
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets"]
    verbs: ["get", "list", "watch", "create", "update", "patch"]
  - apiGroups: [""]
    resources: ["pods", "pods/log", "pods/exec"]
    verbs: ["get", "list", "watch", "create"]
  - apiGroups: [""]
    resources: ["configmaps", "secrets"]
    verbs: ["get", "list", "watch", "create", "update"]
```

### RoleBinding 설정
```yaml
# 3. RoleBinding — 팀별 네임스페이스 권한 부여
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: backend-deployer
  namespace: backend
subjects:
  # IAM Role → Access Entry → Kubernetes Group 매핑
  - kind: Group
    name: backend-team
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: deployer
  apiGroup: rbac.authorization.k8s.io
# ---
# 4. ClusterRoleBinding — 전체 읽기 권한
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: all-teams-viewer
subjects:
  - kind: Group
    name: all-developers
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: namespace-viewer
  apiGroup: rbac.authorization.k8s.io
# ---
# 5. RoleBinding으로 ClusterRole 범위 축소
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: frontend-viewer
  namespace: frontend
subjects:
  - kind: Group
    name: frontend-team
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole        # ClusterRole이지만
  name: namespace-viewer    # 이 네임스페이스만 적용됨
  apiGroup: rbac.authorization.k8s.io
```

### Access Entries + RBAC 통합
```bash
# IAM Role → Kubernetes Group 매핑
aws eks create-access-entry \
  --cluster-name hwahae-prod \
  --principal-arn arn:aws:iam::123456789012:role/BackendDevRole \
  --type STANDARD \
  --kubernetes-groups backend-team,all-developers
```

```
IAM Role: BackendDevRole
  ↓ Access Entry (kubernetes-groups: backend-team, all-developers)
  ├─ ClusterRoleBinding: all-teams-viewer → 전체 읽기
  └─ RoleBinding: backend-deployer → backend NS 배포 권한
```

**화해 권장 패턴**:
- **Platform Team**: `cluster-admin` ClusterRoleBinding
- **Backend Team**: 자기 네임스페이스 `deployer` Role + 전체 `viewer` ClusterRole
- **Frontend Team**: 자기 네임스페이스 `deployer` Role + 전체 `viewer` ClusterRole
- **CI/CD (ARC)**: 대상 네임스페이스별 `deployer` RoleBinding

:::notes
{timing: 3min}
{cue: question}
RBAC 설계입니다. 핵심 패턴은 ClusterRole로 공통 권한을 정의하고, RoleBinding으로 네임스페이스별로 바인딩하는 것입니다. ClusterRole을 RoleBinding에서 참조하면, 해당 네임스페이스 범위로 축소 적용됩니다. 이렇게 하면 ClusterRole 하나로 여러 팀에 동일한 권한을 네임스페이스별로 부여할 수 있습니다. Access Entries의 kubernetes-groups 파라미터로 IAM Role과 Kubernetes Group을 매핑하면, IAM 인증과 RBAC 인가가 자연스럽게 통합됩니다.
:::

---

## External Secrets Operator 흐름

@type: content
@img: diagrams/eso-flow.svg center 90%

**동작 흐름**:
1. ExternalSecret CR 생성 → ESO Controller 감지
2. SecretStore 참조 → IRSA로 AWS 인증
3. Secrets Manager에서 값 조회
4. Kubernetes Secret 자동 생성/갱신
5. Pod에서 Secret 사용

:::notes
{timing: 1.5min}
External Secrets Operator의 동작 흐름입니다.
ExternalSecret을 정의하면 ESO가 AWS Secrets Manager에서 값을 가져와 Kubernetes Secret을 자동 생성합니다.
refreshInterval을 설정하면 Secret이 자동으로 동기화되어 로테이션도 지원됩니다.
IRSA를 통해 인증하므로 AWS 자격 증명을 클러스터에 저장할 필요가 없습니다.
:::

---

## ESO 설정

@type: code

```yaml {filename="external-secret.yaml" highlight="8-10,17-21,26-33"}
# 1. SecretStore (AWS Secrets Manager 연결)
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: aws-secrets-manager
spec:
  provider:
    aws:
      service: SecretsManager
      region: ap-northeast-2
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
            namespace: external-secrets
---
# 2. ExternalSecret (Secret 동기화 정의)
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-credentials
  namespace: production
spec:
  refreshInterval: 1h        # 1시간마다 동기화
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: db-secret          # 생성될 K8s Secret 이름
  data:
    - secretKey: DB_HOST
      remoteRef:
        key: production/database
        property: host
    - secretKey: DB_PASSWORD
      remoteRef:
        key: production/database
        property: password
```

:::notes
{timing: 2min}
ESO 설정 예시입니다.
ClusterSecretStore는 AWS Secrets Manager 연결을 정의합니다. IRSA를 통해 인증합니다.
ExternalSecret은 어떤 Secret을 어떻게 가져올지 정의합니다.
refreshInterval: 1h는 1시간마다 Secret을 동기화한다는 의미입니다.
remoteRef.property로 JSON Secret의 특정 필드만 추출할 수 있습니다.
:::

---

## Network Policy 구현

@type: tabs

### VPC CNI Native (권장)
```yaml
# VPC CNI v1.14+ 에서 NetworkPolicy 지원
# 활성화 명령:
# kubectl set env daemonset aws-node -n kube-system \
#   ENABLE_NETWORK_POLICY=true

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api-server
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: database
      ports:
        - port: 5432
```

### Calico
```yaml
# Calico 추가 기능: GlobalNetworkPolicy
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: default-deny-all
spec:
  selector: all()
  types:
    - Ingress
    - Egress
  # 규칙 없음 = 모든 트래픽 차단

# ---
# DNS 허용
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: allow-dns
spec:
  selector: all()
  egress:
    - action: Allow
      protocol: UDP
      destination:
        selector: k8s-app == 'kube-dns'
        ports: [53]
```

### Cilium
```yaml
# Cilium L7 Policy (HTTP 메서드/경로 제어)
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: api-l7-policy
spec:
  endpointSelector:
    matchLabels:
      app: api-server
  ingress:
    - fromEndpoints:
        - matchLabels:
            app: frontend
      toPorts:
        - ports:
            - port: "8080"
          rules:
            http:
              - method: GET
                path: "/api/v1/.*"
              - method: POST
                path: "/api/v1/orders"
```

:::notes
{timing: 2min}
Network Policy 구현 옵션 3가지입니다.
VPC CNI Native: EKS 기본 CNI에서 NetworkPolicy를 지원합니다. 추가 설치 없이 활성화만 하면 됩니다.
Calico: GlobalNetworkPolicy로 클러스터 전체 정책을 정의할 수 있습니다.
Cilium: L7 Policy로 HTTP 메서드와 경로까지 세밀하게 제어할 수 있습니다.
대부분의 경우 VPC CNI Native로 충분하며, L7 제어가 필요하면 Cilium을 고려하세요.
:::

---

## Network Policy 예시

@type: code

```yaml {filename="zero-trust-policies.yaml" highlight="7-9,20-28,37-44"}
# 1. Default Deny (Zero Trust 기본)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}           # 모든 Pod에 적용
  policyTypes:
    - Ingress
    - Egress
# ---
# 2. DNS 허용 (필수)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
# ---
# 3. Frontend → API 허용
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-api
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api-server
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - port: 8080
```

:::notes
{timing: 2min}
Zero Trust Network Policy 예시입니다.
첫 번째로 default-deny-all로 모든 트래픽을 차단합니다.
두 번째로 DNS 트래픽을 허용합니다. 이게 없으면 Pod가 서비스를 찾지 못합니다.
세 번째로 필요한 통신만 명시적으로 허용합니다.
이 패턴을 적용하면 마이크로세그멘테이션이 구현되어 lateral movement를 방지할 수 있습니다.
:::

---

## Platform Engineering — Self-Service 아키텍처

@type: canvas
@canvas-id: platform-engineering

:::canvas
# Step 1: Developer Experience Layer
box idp "Internal Developer Platform" at 250,50 size 300,60 color #6c5ce7 step 1

# Step 2: Self-Service 인터페이스
box portal "Service Catalog\n(Backstage/Port)" at 100,140 size 160,50 color #FF9900 step 2
box templates "App Templates\n(Helm/Kustomize)" at 320,140 size 160,50 color #FF9900 step 2
box cli "Platform CLI\n(kubectl plugin)" at 540,140 size 160,50 color #FF9900 step 2

# Step 3: GitOps Automation Layer
box argocd "ArgoCD\nApplicationSet" at 200,230 size 140,50 color #E6522C step 3
box ack "ACK\nAWS Resources" at 450,230 size 140,50 color #E6522C step 3
arrow portal -> argocd "Git Push" step 3
arrow portal -> ack "" step 3

# Step 4: Auto-Provisioned Resources
box ns "Namespace\n+ RBAC" at 80,330 size 120,40 color #4CAF50 step 4
box quota "ResourceQuota\n+ LimitRange" at 230,330 size 120,40 color #4CAF50 step 4
box netpol "NetworkPolicy" at 380,330 size 120,40 color #4CAF50 step 4
box monitor "ServiceMonitor\n+ Alerts" at 530,330 size 120,40 color #4CAF50 step 4
arrow argocd -> ns "" step 4
arrow argocd -> quota "" step 4
arrow argocd -> netpol "" step 4
arrow argocd -> monitor "" step 4
:::

:::notes
{timing: 2min}
Internal Developer Platform 아키텍처입니다. 개발자가 Service Catalog에서 템플릿을 선택하면, GitOps를 통해 Namespace, RBAC, ResourceQuota, NetworkPolicy, ServiceMonitor가 자동으로 프로비저닝됩니다. 개발자는 인프라 세부사항을 알 필요 없이 서비스를 배포할 수 있습니다. Backstage나 Port 같은 IDP 도구를 도입하면 개발자 경험을 더욱 향상시킬 수 있습니다.
:::

---

## ApplicationSet으로 팀별 자동 배포

@type: code

```yaml {filename="appset-team-onboarding.yaml" highlight="8-10,17-29"}
# 1. ApplicationSet — Git Directory Generator
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: team-onboarding
  namespace: argocd
spec:
  generators:
    - git:
        repoURL: https://github.com/hwahae/platform-config
        revision: main
        directories:
          - path: "teams/*"       # teams/backend, teams/frontend, ...
  template:
    metadata:
      name: "team-{{path.basename}}"
    spec:
      project: "{{path.basename}}"
      source:
        repoURL: https://github.com/hwahae/platform-config
        path: "{{path}}"
        targetRevision: main
      destination:
        server: https://kubernetes.default.svc
        namespace: "{{path.basename}}"
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
```

```yaml {filename="teams/backend/kustomization.yaml"}
# 팀 디렉토리 구조: teams/backend/
resources:
  - namespace.yaml        # Namespace + Labels
  - rbac.yaml             # Role + RoleBinding
  - resource-quota.yaml   # CPU/Memory 제한
  - limit-range.yaml      # Pod 기본 리소스
  - network-policy.yaml   # Default Deny + DNS Allow
  - service-monitor.yaml  # Prometheus 자동 수집
```

**결과**: `teams/` 디렉토리에 폴더만 추가하면 → 네임스페이스 + 모든 기본 정책 자동 생성

:::notes
{timing: 2min}
ApplicationSet Git Directory Generator를 활용한 팀별 자동 배포입니다. teams/ 디렉토리 아래에 팀 폴더를 추가하기만 하면 ArgoCD가 자동으로 네임스페이스, RBAC, ResourceQuota, NetworkPolicy, ServiceMonitor를 생성합니다. 새 팀 온보딩이 Git PR 하나로 완료됩니다.
:::

---

## Namespace Provisioner 번들

@type: code

```yaml {filename="namespace-bundle.yaml" highlight="7-8,18-22,30-33"}
# 1. ResourceQuota — 팀별 리소스 상한
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-quota
spec:
  hard:
    requests.cpu: "20"
    requests.memory: "40Gi"
    limits.cpu: "40"
    limits.memory: "80Gi"
    pods: "100"
    services: "20"
    persistentvolumeclaims: "10"
# ---
# 2. LimitRange — Pod 기본값 및 최대값
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
spec:
  limits:
    - type: Container
      default:
        cpu: "200m"
        memory: "256Mi"
      defaultRequest:
        cpu: "100m"
        memory: "128Mi"
      max:
        cpu: "4"
        memory: "8Gi"
# ---
# 3. Default NetworkPolicy — Ingress Deny
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}
  policyTypes:
    - Ingress
# ---
# 4. DNS 허용
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
```

**Self-Service 흐름**:
1. 개발자: `teams/my-team/` 디렉토리 생성 → PR 제출
2. Platform Team: PR 리뷰 → Merge
3. ArgoCD: 자동으로 Namespace + 위 번들 전체 생성
4. 개발자: 해당 Namespace에 자유롭게 배포 시작

:::notes
{timing: 2min}
Namespace Provisioner 번들입니다. ResourceQuota로 팀별 리소스 상한을 설정하고, LimitRange로 개발자가 리소스 설정을 빠뜨려도 기본값이 적용됩니다. NetworkPolicy는 Default Deny + DNS Allow 패턴을 적용하여 Zero Trust를 기본으로 합니다. 이 번들이 ApplicationSet과 결합되면, 팀 온보딩이 완전 자동화됩니다.
:::

---

## Block 04 Quiz

@type: quiz

**Q1: Access Entries가 aws-auth ConfigMap보다 좋은 이유는?**
- [ ] 더 빠른 인증 속도
- [x] API 기반 관리로 안전하고 CloudTrail 감사 지원
- [ ] 더 많은 IAM Role 지원
- [ ] 비용이 저렴함

**Q2: External Secrets Operator의 역할은?**
- [ ] Kubernetes Secret을 암호화
- [ ] Pod 간 Secret 공유
- [x] 외부 Secret 저장소(AWS SM)와 K8s Secret 동기화
- [ ] Secret 접근 로깅

**Q3: Network Policy의 Default Deny 패턴에서 반드시 허용해야 하는 것은?**
- [ ] HTTP 트래픽
- [ ] HTTPS 트래픽
- [x] DNS 트래픽 (UDP 53)
- [ ] SSH 트래픽

**Q4: IRSA(IAM Roles for Service Accounts)의 장점은?**
- [ ] IAM Role 생성이 자동화됨
- [ ] 모든 Pod가 동일한 권한을 가짐
- [x] Pod별로 최소 권한 AWS 접근이 가능함
- [ ] AWS 자격 증명을 Secret으로 저장함

:::notes
{timing: 3min}
Q1: Access Entries는 EKS API로 관리되어 ConfigMap 삭제 위험이 없고, CloudTrail로 변경 이력을 추적할 수 있습니다.
Q2: ESO는 AWS Secrets Manager 등 외부 저장소의 Secret을 Kubernetes Secret으로 자동 동기화합니다.
Q3: Default Deny 정책 적용 시 DNS를 허용하지 않으면 Pod가 서비스 이름을 resolve할 수 없습니다.
Q4: IRSA는 ServiceAccount별로 IAM Role을 할당하여 Pod 단위 최소 권한 원칙을 구현합니다.
:::
