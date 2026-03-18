---
remarp: true
block: security-platform
---
@type: cover
@background: common/pptx-theme/images/Picture_13.png
@badge: common/pptx-theme/images/Picture_8.png

# ECS → EKS Migration Deep Dive

Security & Platform Engineering (20 min)

**오준석 (Junseok Oh)**
Sr. Solutions Architect, AWS
화해 글로벌

:::notes
{timing: 1min}
Block 04에서는 EKS 보안과 Platform Engineering을 다룹니다.
IAM 통합, Secret 관리, Network Policy를 학습하고, 개발자 Self-Service 환경 구축 방안을 살펴봅니다.

💬 예상 질문:
• ECS에서는 Task Role로 권한 관리했는데 EKS는 어떻게 다른가요? → EKS는 IRSA/Pod Identity로 Pod 단위 IAM Role을 부여합니다. Task Role과 개념은 유사하지만, OIDC 기반 인증이 추가됩니다.
:::

---
@type: content

## EKS Security Architecture

**보안 계층**:

1. **IAM Layer**: OIDC Provider → IRSA/Pod Identity → AWS 서비스 접근 {.fragment}
2. **Cluster Layer**: RBAC, Access Entries, Cluster Endpoint 접근 제어 {.fragment}
3. **Workload Layer**: Pod Security Standards, Network Policy {.fragment}
4. **Data Layer**: Secrets Manager, KMS 암호화 {.fragment}

:::notes
{timing: 2.5min}
EKS 보안 아키텍처의 4개 계층입니다.
IAM Layer에서는 OIDC Provider를 통해 Pod가 AWS 서비스에 안전하게 접근합니다.
Cluster Layer에서는 RBAC과 Access Entries로 클러스터 접근을 제어합니다.
Workload Layer에서는 Pod Security Standards와 Network Policy로 워크로드를 격리합니다.
Data Layer에서는 Secrets Manager와 KMS로 민감 정보를 보호합니다.

💬 예상 질문:
• Pod Security Standards는 ECS Security Group과 어떻게 다른가요? → PSS는 컨테이너 런타임 수준 보안(privileged 모드, 호스트 네트워크 등)을 제어하고, Security Group은 네트워크 수준 접근 제어입니다. EKS에서는 둘 다 사용합니다.
:::

---
@type: compare

## aws-auth vs Access Entries

### aws-auth ConfigMap (Legacy)

<div class="card compare-highlight">
<h3 style="color:var(--text-accent);margin-bottom:.2rem;">aws-auth ConfigMap (Legacy)</h3>

- ConfigMap 기반 IAM 매핑
- 수동 편집 필요 (오류 시 접근 불가)
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
    - rolearn: arn:aws:iam::role/NodeRole
      username: system:node:{{...}}
      groups:
        - system:bootstrappers
        - system:nodes
```
</div>

### Access Entries (권장)

<div class="card">
<h3 style="color:var(--text-accent);margin-bottom:.2rem;">Access Entries (권장)</h3>

- EKS API 기반 IAM 매핑
- AWS CLI/Console/IaC로 관리
- CloudTrail 감사 로그 자동 기록
- Terraform/CDK 완벽 지원
- **장점**: ConfigMap 삭제해도 접근 유지

```bash
# Access Entry 생성
aws eks create-access-entry \
  --cluster-name my-cluster \
  --principal-arn arn:aws:iam::role/DevRole \
  --type STANDARD
```
</div>

:::notes
{timing: 2.5min}
aws-auth ConfigMap과 Access Entries의 비교입니다.
aws-auth는 ConfigMap을 직접 편집해야 하는데, 실수로 삭제하면 클러스터에 접근할 수 없게 됩니다.
Access Entries는 EKS 1.23부터 지원되며, AWS API로 관리되어 더 안전하고 감사 추적이 용이합니다.
신규 클러스터는 Access Entries를, 기존 클러스터는 점진적 마이그레이션을 권장합니다.

💬 예상 질문:
• 기존 aws-auth를 사용 중인데 Access Entries로 마이그레이션하려면? → 병렬 운영이 가능합니다. Access Entries를 먼저 추가하고 테스트한 후, aws-auth에서 해당 항목을 제거하면 됩니다.
• Access Entries 설정 실수하면 클러스터 잠금되나요? → 아닙니다. AWS API 기반이라 클러스터 생성자의 IAM은 항상 접근 가능합니다.
:::

---
@type: code

## Access Entries 설정

```bash {highlight="1-4,7-9"}
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

```terraform {filename="terraform/access-entries.tf"}
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
{timing: 2.5min}
Access Entries 설정 방법입니다.
먼저 create-access-entry로 IAM Role을 등록하고, associate-access-policy로 권한을 부여합니다.
access-scope를 namespace로 제한하면 특정 네임스페이스에만 권한을 부여할 수 있습니다.
Terraform으로 관리하면 GitOps 워크플로우와 완벽하게 통합됩니다.

💬 예상 질문:
• AmazonEKSClusterAdminPolicy와 AmazonEKSAdminPolicy 차이는? → ClusterAdminPolicy는 cluster-admin 수준 전체 권한, AdminPolicy는 네임스페이스 범위로 제한 가능한 관리자 권한입니다.
• SSO 사용자도 Access Entries로 관리 가능한가요? → 네, IAM Identity Center(SSO) Role ARN을 principal-arn으로 등록하면 됩니다.
:::

---
@type: content

## RBAC & OIDC 워크플로우

<div style="background:linear-gradient(135deg,#1e3a5f,#1e40af); border-radius:12px; padding:0.5rem 0.8rem; position:relative; overflow:hidden; margin-bottom:8px;">
  <div style="font-size:0.6rem; font-weight:700; letter-spacing:0.08em; color:#93c5fd; margin-bottom:4px;">STEP 1: External Identity Provider (OIDC)</div>
  <div style="display:flex; align-items:center; gap:12px;">
    <div style="background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.15); border-radius:8px; padding:0.35rem 0.5rem; flex:1;">
      <div style="font-size:0.55rem; font-family:monospace; color:#93c5fd; margin-bottom:2px;">// ID Token (JWT) Claims</div>
      <div style="font-size:0.55rem; font-family:monospace; color:#e0e0e0; line-height:1.5;">
        <span style="color:#93c5fd;">"sub":</span> "alice-id"<br>
        <span style="color:#93c5fd;">"email":</span> "alice@company.com"<br>
        <span style="color:#4ade80;">"groups":</span> ["dev-team", "admin-group"]
      </div>
    </div>
    <div style="font-size:1.2rem; color:#60a5fa;">→</div>
    <div style="flex:1; font-size:0.6rem; color:#bfdbfe; font-style:italic; line-height:1.5;">
      K8s API 서버는 이 토큰을 읽어 <b style="color:#fff;">Alice</b>라는 유저와 <b style="color:#fff;">dev-team</b>이라는 그룹이 요청을 보냈음을 인식합니다.
    </div>
  </div>
</div>

**STEP 2: SUBJECTS** → User, Group, ServiceAccount

**STEP 3: BINDING** → RoleBinding (Namespace Level) / ClusterRoleBinding (Cluster Level)

**STEP 4: PERMISSIONS** → Role / ClusterRole → Allowed Actions (get, list, watch, update...)

<div style="background:var(--bg-secondary); border:1px solid var(--border-color); border-radius:8px; padding:0.35rem 0.5rem; margin-top:8px;">
  <div style="font-size:0.6rem; font-weight:700; color:var(--text-primary); margin-bottom:3px;">OIDC와 K8s 그룹 매핑</div>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; font-size:0.55rem; color:var(--text-secondary); line-height:1.4;">
    <div><b style="color:#60a5fa;">토큰이 곧 신분증:</b> JWT 안의 <code>groups</code> 필드로 Subject 매핑</div>
    <div><b style="color:#60a5fa;">설정:</b> <code>--oidc-groups-claim=groups</code></div>
    <div><b style="color:#2dd4bf;">ServiceAccount:</b> Pod/프로세스용 내부 계정, OIDC 불필요</div>
    <div><b style="color:#60a5fa;">RBAC 활용:</b> RoleBinding의 subjects에 <code>kind: Group</code> 지정</div>
  </div>
</div>

:::notes
{timing: 2min}
RBAC & OIDC 워크플로우 전체 흐름입니다. Play 버튼을 눌러 애니메이션을 확인하세요.
1단계: EKS OIDC Provider가 JWT 토큰을 발급하고 검증합니다.
2단계: IAM Role(Access Entry), ServiceAccount(IRSA/Pod Identity), Group/User가 인증 주체로 동작합니다.
3단계: ClusterRoleBinding/RoleBinding과 Access Policy Association으로 주체와 권한을 연결합니다.
4단계: ClusterRole, Role, EKS Access Policy, Pod Identity를 통해 실제 리소스 접근 권한이 부여됩니다.

💬 예상 질문:
• IRSA와 Pod Identity 중 어떤 걸 써야 하나요? → 신규는 Pod Identity 권장(설정이 더 간단), 기존 IRSA도 계속 지원됩니다. Pod Identity는 cross-account 접근도 더 쉽습니다.
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

```yaml {filename="ClusterRole: namespace-viewer"}
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
```

```yaml {filename="Role: deployer"}
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

```yaml {filename="RoleBinding"}
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
```

```yaml {filename="ClusterRoleBinding"}
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
```

```yaml {filename="RoleBinding with ClusterRole"}
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
RBAC 설계입니다. 탭을 전환하며 각 패턴을 설명하세요.
핵심 패턴은 ClusterRole로 공통 권한을 정의하고, RoleBinding으로 네임스페이스별로 바인딩하는 것입니다.
ClusterRole을 RoleBinding에서 참조하면, 해당 네임스페이스 범위로 축소 적용됩니다.
이렇게 하면 ClusterRole 하나로 여러 팀에 동일한 권한을 네임스페이스별로 부여할 수 있습니다.
Access Entries의 kubernetes-groups 파라미터로 IAM Role과 Kubernetes Group을 매핑하면, IAM 인증과 RBAC 인가가 자연스럽게 통합됩니다.

💬 예상 질문:
• 개발자가 다른 팀 네임스페이스 Pod 로그를 봐야 할 때는? → ClusterRoleBinding으로 전체 viewer 권한을 주거나, 필요한 네임스페이스에 RoleBinding을 추가합니다.
• RBAC 권한 문제 디버깅은 어떻게? → kubectl auth can-i 명령으로 특정 사용자/SA의 권한을 확인할 수 있습니다.
:::

---
@type: content

## External Secrets Operator 흐름

**동작 흐름**:

1. ExternalSecret CR 생성 → ESO Controller 감지 {.fragment}
2. SecretStore 참조 → IRSA로 AWS 인증 {.fragment}
3. Secrets Manager에서 값 조회 {.fragment}
4. Kubernetes Secret 자동 생성/갱신 {.fragment}
5. Pod에서 Secret 사용 {.fragment}

:::notes
{timing: 2min}
External Secrets Operator의 동작 흐름입니다.
ExternalSecret을 정의하면 ESO가 AWS Secrets Manager에서 값을 가져와 Kubernetes Secret을 자동 생성합니다.
refreshInterval을 설정하면 Secret이 자동으로 동기화되어 로테이션도 지원됩니다.
IRSA를 통해 인증하므로 AWS 자격 증명을 클러스터에 저장할 필요가 없습니다.

💬 예상 질문:
• ECS에서 Secrets Manager 직접 참조하던 것과 차이점은? → ECS는 Task Definition에서 직접 참조, EKS는 ESO가 K8s Secret으로 변환해서 Pod에서 일반 Secret처럼 사용합니다. 애플리케이션 코드 변경 없이 마이그레이션 가능합니다.
• Secret 로테이션 시 Pod 재시작 필요한가요? → refreshInterval로 Secret은 자동 갱신되지만, Pod가 이미 마운트한 값은 재시작해야 반영됩니다. Reloader 같은 도구로 자동화 가능합니다.
:::

---
@type: tabs

## Network Policy 구현

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
```

:::notes
{timing: 2min}
Network Policy 구현 옵션입니다.
VPC CNI Native: EKS 기본 CNI에서 NetworkPolicy를 지원합니다. 추가 설치 없이 활성화만 하면 됩니다.
Calico: GlobalNetworkPolicy로 클러스터 전체 정책을 정의할 수 있습니다.
대부분의 경우 VPC CNI Native로 충분합니다.

💬 예상 질문:
• ECS Security Group과 Network Policy 차이는? → Security Group은 ENI 수준(IP 기반), Network Policy는 Pod Label 기반입니다. Network Policy가 더 세밀한 제어가 가능합니다.
• VPC CNI Network Policy와 Calico 중 어떤 걸 선택? → VPC CNI가 관리 오버헤드가 적고 AWS 지원을 받을 수 있어 권장합니다. GlobalNetworkPolicy가 꼭 필요하면 Calico를 고려하세요.
:::

---
@type: code

## 2. DNS 허용 (필수)

```yaml {filename="allow-dns.yaml"}
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
```

:::notes
{timing: 1.5min}
DNS 허용 정책입니다. Default Deny 패턴 적용 시 DNS를 허용하지 않으면 Pod가 서비스 이름을 resolve할 수 없습니다.
kube-system 네임스페이스의 UDP 53 포트를 반드시 허용해야 합니다.

💬 예상 질문:
• DNS 허용 안 하면 어떤 증상이 나타나나요? → Pod에서 서비스 이름으로 접근 시 name resolution failed 에러가 발생합니다. IP로는 통신 가능하지만 서비스 디스커버리가 안 됩니다.
• CoreDNS 대신 외부 DNS 사용하면? → 해당 DNS 서버 IP와 포트를 Egress에 추가로 허용해야 합니다.
:::

---
@type: canvas

## Platform Engineering — Self-Service 아키텍처

@canvas: platform
@width: 960
@height: 380

:::notes
{timing: 2min}
Internal Developer Platform 아키텍처입니다. Play 버튼을 눌러 애니메이션을 확인하세요.
개발자가 Service Catalog에서 템플릿을 선택하면, GitOps를 통해 Namespace, RBAC, ResourceQuota, NetworkPolicy, ServiceMonitor가 자동으로 프로비저닝됩니다.
개발자는 인프라 세부사항을 알 필요 없이 서비스를 배포할 수 있습니다.
Backstage나 Port 같은 IDP 도구를 도입하면 개발자 경험을 더욱 향상시킬 수 있습니다.

💬 예상 질문:
• Platform Engineering 도입 시 가장 먼저 해야 할 것은? → 반복되는 작업(네임스페이스 생성, RBAC 설정 등)을 파악하고, GitOps 기반 자동화부터 시작하세요. IDP 도구는 그 다음입니다.
• Backstage 도입 비용/난이도는? → 오픈소스라 라이선스 비용은 없지만, 커스터마이징에 개발 리소스가 필요합니다. 소규모 팀은 ArgoCD + Git PR 워크플로우로 시작하는 것을 권장합니다.
:::

---
@type: code

## ApplicationSet으로 팀별 자동 배포

```yaml {filename="appset-team-onboarding.yaml"}
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
ApplicationSet Git Directory Generator를 활용한 팀별 자동 배포입니다.
teams/ 디렉토리 아래에 팀 폴더를 추가하기만 하면 ArgoCD가 자동으로 네임스페이스, RBAC, ResourceQuota, NetworkPolicy, ServiceMonitor를 생성합니다.
새 팀 온보딩이 Git PR 하나로 완료됩니다.

💬 예상 질문:
• 팀별로 다른 ResourceQuota를 적용하려면? → 각 팀 디렉토리의 resource-quota.yaml을 다르게 설정하거나, Kustomize overlay로 팀별 값을 오버라이드합니다.
• ApplicationSet이 너무 많은 권한을 가지는 것 아닌가요? → ArgoCD Project로 ApplicationSet이 생성할 수 있는 리소스 종류와 네임스페이스를 제한할 수 있습니다.
:::

---
@type: code

## Namespace Provisioner 번들

:::left

```yaml {filename="namespace-bundle.yaml"}
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
```

```yaml {filename="limit-range.yaml"}
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
```

:::right

```yaml {filename="network-policy.yaml"}
# 3. Default NetworkPolicy — Ingress Deny
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}
  policyTypes:
    - Ingress
```

```yaml {filename="allow-dns.yaml"}
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

:::

**Self-Service 흐름**: 개발자 `teams/my-team/` 생성 → PR → Platform Team 리뷰 → ArgoCD 자동 Namespace + 번들 생성

:::notes
{timing: 2min}
Namespace Provisioner 번들입니다.
ResourceQuota로 팀별 리소스 상한을 설정하고, LimitRange로 개발자가 리소스 설정을 빠뜨려도 기본값이 적용됩니다.
NetworkPolicy는 Default Deny + DNS Allow 패턴을 적용하여 Zero Trust를 기본으로 합니다.
이 번들이 ApplicationSet과 결합되면, 팀 온보딩이 완전 자동화됩니다.

💬 예상 질문:
• ResourceQuota 초과하면 어떻게 되나요? → 새 Pod 생성이 거부됩니다. kubectl describe quota로 현재 사용량을 확인하고, Platform Team에 증설을 요청하는 프로세스를 만드세요.
• LimitRange 기본값이 너무 작으면? → 개발자가 Pod spec에 명시적으로 resources를 설정하면 LimitRange 기본값을 오버라이드합니다. 기본값은 설정 누락 시에만 적용됩니다.
:::

---
@type: quiz

## Block 04 Quiz

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
퀴즈 시간입니다. 참석자들이 직접 답을 선택하도록 유도하세요.
Q1: Access Entries는 EKS API로 관리되어 ConfigMap 삭제 위험이 없고, CloudTrail로 변경 이력을 추적할 수 있습니다.
Q2: ESO는 AWS Secrets Manager 등 외부 저장소의 Secret을 Kubernetes Secret으로 자동 동기화합니다.
Q3: Default Deny 정책 적용 시 DNS를 허용하지 않으면 Pod가 서비스 이름을 resolve할 수 없습니다.
Q4: IRSA는 ServiceAccount별로 IAM Role을 할당하여 Pod 단위 최소 권한 원칙을 구현합니다.

💬 예상 질문:
• 실제 마이그레이션 시 보안 설정 순서는? → 1) Access Entries로 팀 접근 권한 설정 → 2) IRSA/Pod Identity로 AWS 서비스 접근 → 3) ESO로 Secret 마이그레이션 → 4) Network Policy 적용 순서를 권장합니다.
:::
