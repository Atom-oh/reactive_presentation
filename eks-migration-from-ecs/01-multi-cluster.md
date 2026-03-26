---
remarp: true
block: multi-cluster
---

# ECS → EKS Migration Deep Dive
Multi-Cluster Active-Active Architecture (30min)

@type: cover
@background: common/pptx-theme/images/Picture_13.png
@badge: common/pptx-theme/images/Picture_8.png

@speaker: Junseok Oh
@title: Sr. Solutions Architect, AWS
:::notes
{timing: 2min}
안녕하세요, AWS 솔루션즈 아키텍트 오준석입니다. 오늘은 ECS에서 EKS로의 마이그레이션 여정 중 첫 번째 세션으로, Multi-Cluster Active-Active 아키텍처에 대해 다루겠습니다. 네트워크 구성의 복잡성과 IP 고갈 문제를 해결하는 방법을 중점적으로 살펴보겠습니다.

Q&A:
- Q: 이 세션은 ECS 운영 경험이 없어도 이해할 수 있나요?
  → 네, EKS 관점에서 설명하므로 ECS 경험 없이도 Multi-Cluster 설계를 이해할 수 있습니다.
:::

---

@type: content

## ECS에서 EKS로 — 왜 전환을 고려하는가?

> "ECS로 잘 운영하고 있었는데, 서비스 규모가 커지면서 한계가 보이기 시작했습니다."

::: left
### 규모가 커지면서 발생하는 ECS 한계
- **멀티클러스터** 구성이 네이티브로 불가 — Blast Radius 관리 어려움
- **네트워크 제어**가 제한적 — Pod 레벨 Security Group, Network Policy 부재
- **IP 고갈** — awsvpc 모드에서 Task당 ENI IP 점유, 서브넷 고갈
- **에코시스템** — Helm, Karpenter, Argo, Istio 등 CNCF 생태계 활용 불가
:::

::: right
### EKS 전환 시 기대효과
- **Multi-Cluster Active-Active**로 Blast Radius 최소화
- **Prefix Delegation**으로 IP 효율성 6배 향상
- **Gateway API + Istio**로 표준화된 트래픽 관리
- **Karpenter + KEDA**로 지능형 오토스케일링
:::

:::notes
{timing: 4min}
{cue: pause}
ECS로 잘 운영하다가도 서비스 규모가 커지면 자연스럽게 한계에 부딪히게 됩니다. 특히 멀티클러스터 구성이 네이티브로 안 되는 점, awsvpc 모드에서 Task당 ENI IP를 점유해서 서브넷이 고갈되는 점이 대표적입니다. EKS로 전환하면 Kubernetes 생태계의 강력한 도구들 — Karpenter, Argo, Istio, Gateway API 등을 활용할 수 있습니다. 오늘 세션에서 이 전환을 어떻게 설계하는지 상세히 다루겠습니다.

Q&A:
- Q: ECS Anywhere나 ECS Service Connect로도 해결 가능하지 않나요?
  → Service Connect는 서비스 메시 기능을 제공하지만, 멀티클러스터 Active-Active나 CNCF 생태계 활용에는 한계가 있습니다.
- Q: IP 고갈 문제는 ECS에서도 해결 가능한가요?
  → awsvpc 모드의 구조적 한계로, ECS에서는 Prefix Delegation 같은 솔루션이 없습니다.
:::

---

@type: content

## Target: Active-Active Multi-Cluster

<img src="diagrams/target-active-active.svg" style="width:100%;max-height:70vh;">

:::notes
{timing: 3min}
{cue: transition}
목표 아키텍처입니다. 두 개의 EKS 클러스터를 A-Zone과 C-Zone에 각각 배치하고, NLB를 통해 50:50 가중치 라우팅을 수행합니다. 각 클러스터는 독립적으로 운영되며, 한 클러스터 장애 시에도 다른 클러스터가 전체 트래픽을 처리할 수 있습니다.

Q&A:
- Q: 왜 A-Zone과 C-Zone인가요? B-Zone은요?
  → 서울 리전에서 A/C가 가장 많은 인스턴스 타입과 서비스를 지원합니다. B-Zone은 제약이 있어 제외하는 경우가 많습니다.
- Q: Cross-AZ 트래픽 비용은 어떻게 되나요?
  → AZ 간 데이터 전송 비용(GB당 $0.01)이 발생하지만, Active-Active 가용성 확보 비용으로 감수합니다.
:::

---

@type: compare

## Single Cluster vs Multi-Cluster

::: left
### Single Cluster
- 관리 포인트 단일화
- 클러스터 내 Pod 간 통신 빠름
- **단점**: 클러스터 장애 시 전체 서비스 중단
- **단점**: 업그레이드 시 다운타임 발생
- **Blast Radius**: 전체 서비스
:::

::: right
### Multi-Cluster (Active-Active)
- Zone별 독립 운영
- 클러스터 업그레이드 시 무중단 가능
- **장점**: Blast Radius 50% 감소
- **장점**: Zone 장애 대응 가능
- **트레이드오프**: 운영 복잡성 증가
:::

:::notes
{timing: 3min}
{cue: question}
Multi-Cluster가 항상 정답은 아닙니다. 관리 복잡성이 증가하므로, 팀의 운영 역량과 서비스의 가용성 요구사항을 고려해서 결정해야 합니다. 높은 가용성이 필요한 커머스 서비스에서는 Multi-Cluster가 적합합니다.

Q&A:
- Q: 서비스가 몇 개 정도일 때 Multi-Cluster를 고려해야 하나요?
  → 서비스 수보다는 가용성 요구사항이 중요합니다. SLA 99.99% 이상이 필요하면 서비스 10개라도 Multi-Cluster를 고려하세요.
- Q: Multi-Cluster 운영에 필요한 최소 인력은?
  → GitOps + IaC가 잘 갖춰져 있다면 2-3명의 플랫폼 엔지니어로 운영 가능합니다.
:::

---

@type: tabs

## 멀티 클러스터 분리 전략

### 분리 기준 의사결정
| 기준 | Single Cluster | Multi-Cluster |
|------|---------------|---------------|
| 서비스 수 | < 50개 서비스 | 50+ 서비스 |
| 보안 격리 | Namespace RBAC 충분 | 컴플라이언스/규제 요구 |
| 팀 독립성 | 공유 리소스 가능 | 팀별 독립 릴리스 필요 |
| Blast Radius | 전체 서비스 영향 허용 | 장애 범위 제한 필수 |
| 업그레이드 | 다운타임 허용 가능 | 무중단 필수 |

**판단**: 전체 서비스 EKS 이관 + 무중단 업그레이드 필요 → **Multi-Cluster 권장**

### 계정별 분리 패턴
| 패턴 | 구조 | 적합한 경우 |
|------|------|------------|
| 환경별 분리 | Dev Account / Staging Account / Prod Account | 환경 간 완전 격리 필요 |
| 워크로드별 분리 | Frontend Account / Backend Account / Data Account | 팀별 비용 분리, 독립 운영 |
| **하이브리드** | Prod-Service / Prod-Data / NonProd | **권장** — 서비스와 데이터 분리 + 환경 분리 |

**핵심**: AWS Organizations + OU 구조로 계정 표준화, 신규 계정은 Control Tower로 자동 프로비저닝

### 클러스터 분리 패턴
| 패턴 | 클러스터 수 | 장점 | 단점 |
|------|-----------|------|------|
| 환경별 | Dev + Staging + Prod | 간단, 명확한 격리 | Prod 클러스터 비대화 |
| 도메인별 | 서비스A + 서비스B + Platform | 팀 자율성 | 클러스터 관리 부담 |
| 기능별 | Service Plane + Data Plane | 워크로드 특성 최적화 | 서비스 간 통신 복잡 |
| **AZ 기반** | Zone-A + Zone-C | 고가용성 극대화 | 데이터 동기화 고려 |

**권장**: AZ 기반 Active-Active + Service/Data Plane 분리 조합

:::notes
{timing: 2min}
멀티 클러스터 분리 전략을 결정하는 기준입니다. 서비스 수, 보안 격리 요구사항, 팀 독립성, Blast Radius 허용 범위, 업그레이드 정책에 따라 Single vs Multi-Cluster를 결정합니다. 탭을 전환하면서 계정별 분리 패턴과 클러스터 분리 패턴도 함께 살펴보세요.

Q&A:
- Q: 환경별 분리(Dev/Staging/Prod)와 AZ별 분리 중 어떤 것이 우선인가요?
  → 환경 분리가 우선입니다. Prod 환경 내에서 AZ별 Active-Active를 구성하는 것이 일반적입니다.
:::

---

@type: interactive
@interactive-id: multi-plane-arch

## Service Plane vs Data Plane 분리

:::interactive
component: multi-plane-diagram
sections:
  - id: overview
    title: EKS Multi-Plane 아키텍처 개요
    desc: Service Plane과 Data Plane을 분리하여 비용 최적화 + 데이터 안정성 극대화
    features:
      - 리소스 분리로 Noisy Neighbor 문제 방지
      - 워크로드 특성별 인스턴스 타입 (Spot vs On-Demand)
      - 명확한 네트워크 격리 및 스토리지 할당 전략
  - id: alb
    title: Application Load Balancer (ALB)
    desc: 외부 트래픽을 EKS 클러스터 내부로 라우팅합니다.
    features:
      - AWS Load Balancer Controller를 통해 프로비저닝
      - Service Plane의 Ingress/Service로 트래픽 전달
      - Data Plane으로의 직접 외부 접근 차단
  - id: servicePlane
    title: Service Plane (Stateless)
    desc: 트래픽 변화에 유연하게 대응하는 API, Web, Mobile BFF 영역
    features:
      - "<strong>컴퓨팅</strong>: Spot 70% + On-Demand 30% 또는 Fargate"
      - "<strong>스케일링</strong>: HPA + Karpenter (RPS 기반 병렬 확장)"
      - "<strong>스토리지</strong>: EFS (ReadWriteMany) 또는 Ephemeral"
      - "<strong>가용성</strong>: Multi-AZ에 자유롭게 Pod 배치"
  - id: dataPlane
    title: Data Plane (Stateful)
    desc: 데이터 영속성·정합성이 필수인 DB, 메시지 큐, Batch 영역
    features:
      - "<strong>컴퓨팅</strong>: On-Demand 90% (안정성 우선)"
      - "<strong>스케일링</strong>: StatefulSet + KEDA (Queue depth/Lag)"
      - "<strong>스토리지</strong>: EBS 1:1 매핑 (Pod 재생성 시 동일 볼륨)"
      - "<strong>격리</strong>: Taints/Tolerations로 일반 Pod 침범 방지"
  - id: networkPolicy
    title: 네트워크 격리 (Network Policies)
    desc: Service ↔ Data Plane 간 통신을 제어하여 보안 강화
    features:
      - "<strong>Default Deny</strong>: Data Plane 인바운드 기본 차단"
      - "<strong>Targeted Allow</strong>: 허용된 Pod만 DB 포트 접근"
      - "<strong>Namespace 격리</strong>: service-ns ↔ data-ns 분리"
:::

:::notes
{timing: 2min}
Service/Data Plane 분리의 구체적인 이점입니다. 워크로드 특성에 맞는 노드 타입, 스케일링 전략, 배포 방식을 적용할 수 있습니다.

Q&A:
- Q: Kafka Consumer는 왜 Data Plane인가요?
  → Consumer Lag 기반 스케일링, 메시지 처리 순서 보장 등 Stateful 특성이 있어 Data Plane에 배치합니다.
:::

---

@type: canvas
@canvas-id: lifecycle

## 워크로드 생명주기 — Stateless vs Stateful

:::canvas
# Phase 0: 초기 구조
text phase-label "초기 구조 — ↓ 키로 단계 진행" at 480,350 color #94a3b8 step 0

# Phase 1: 배포
text phase-label "Phase 1: 배포 — Stateless 동시, Stateful 순차" at 480,350 color #94a3b8 step 1

# Phase 2: 정상 서비스
text phase-label "Phase 2: 정상 서비스 — ALB 트래픽 분산" at 480,350 color #94a3b8 step 2

# Phase 3: 장애 발생
text phase-label "Phase 3: 장애 발생 — Pod/노드 장애 + 소멸" at 480,350 color #94a3b8 step 3

# Phase 4: 자가 치유
text phase-label "Phase 4: 자가 치유 — 새 ID(Stateless) / 동일 ID+EBS 재연결(Stateful)" at 480,350 color #94a3b8 step 4
:::

:::notes
{timing: 2.5min}
워크로드 생명주기 애니메이션입니다. Play를 눌러 5단계를 관찰하세요.
Phase 1: Stateless(Deployment)는 3개 Pod가 동시에 생성되고, Stateful(StatefulSet)은 db-0 → db-1 → db-2 순서로 순차 생성됩니다.
Phase 2: ALB가 트래픽을 정상 분산합니다.
Phase 3: 노드 장애로 Stateless Pod 1개와 Stateful Pod 1개가 동시에 죽습니다.
Phase 4: 핵심 차이! Stateless는 완전히 새로운 랜덤 ID로 생성되고, Stateful은 동일한 이름(db-0)으로 재생성되며 기존 EBS를 다시 연결합니다.
Phase 5: 복구 후 서비스가 재개됩니다.
이것이 Deployment와 StatefulSet을 구분하는 가장 중요한 이유입니다.

Q&A:
- Q: StatefulSet이 EBS를 다시 연결하는 메커니즘은?
  → PVC(PersistentVolumeClaim)가 Pod 이름에 바인딩되어 있어, 같은 이름의 Pod가 재생성되면 기존 PVC를 자동으로 마운트합니다.
- Q: Stateless Pod가 새 ID로 생성되면 로드밸런서 설정은?
  → Service가 Label Selector로 매칭하므로 Pod 이름이 바뀌어도 자동으로 트래픽이 라우팅됩니다.
:::

---

@type: compare

## Service/Data Plane 분리의 이점

::: left
### Service Plane
- **워크로드**: API, Web, Mobile BFF
- **특성**: Stateless, 수평 확장 용이
- **노드**: Spot Instance 70% + On-Demand 30%
- **스케일링**: HPA + Karpenter (RPS 기반)
- **업그레이드**: Canary/Rolling (빠른 반영)
- **장애 영향**: 서비스 일시 지연 (복구 빠름)
:::

::: right
### Data Plane
- **워크로드**: Kafka Consumer, Batch, ML Inference
- **특성**: Stateful/Long-running, 데이터 정합성 중요
- **노드**: On-Demand 90% + Spot 10% (비중요 배치만)
- **스케일링**: KEDA (Queue depth/Lag 기반)
- **업그레이드**: Blue/Green (안전 우선)
- **장애 영향**: 데이터 유실 가능 (복구 시간 필요)
:::

:::notes
{timing: 2min}
{cue: question}
Service Plane과 Data Plane의 운영 전략 차이입니다. 가장 큰 차이는 Spot Instance 비율과 스케일링 전략입니다. Service Plane은 Stateless라서 Spot 중단에 강하지만, Data Plane은 데이터 정합성이 중요하므로 On-Demand 위주로 운영합니다.

Q&A:
- Q: Service Plane과 Data Plane을 같은 클러스터에 두면 안 되나요?
  → 가능하지만 Spot 비율, 노드 타입, 업그레이드 정책이 달라 운영 복잡성이 증가합니다. 규모가 크면 분리를 권장합니다.
:::

---

@type: content

## 멀티 계정 네트워크 토폴로지

::: columns
:::: col
**Prod Service Account**
EKS Service Cluster
::::
:::: col
**Prod Data Account**
EKS Data Cluster
::::
:::: col
**NonProd Account**
EKS Dev/Staging
::::
:::

**Transit Gateway** (VPC Peering)

::: columns
:::: col
**Shared VPC**
ArgoCD, Monitoring
::::
:::: col
**Route 53**
Private Hosted Zone / DNS Resolution
::::
:::

:::notes
{timing: 2min}
멀티 계정 네트워크 토폴로지입니다. Transit Gateway를 중심으로 Prod Service, Prod Data, NonProd 계정을 연결합니다. Shared VPC에서 ArgoCD와 모니터링을 중앙 관리합니다.

Q&A:
- Q: VPC Peering 대신 Transit Gateway를 쓰는 이유는?
  → 3개 이상의 VPC를 연결할 때 Peering은 Full Mesh가 필요하지만, TGW는 Hub-Spoke로 관리가 간편합니다.
:::

---

@type: content

## NLB Weighted Routing Deep Dive

<img src="diagrams/nlb-weighted-routing.svg" style="width:100%;max-height:70vh;">

:::notes
{timing: 3min}
NLB의 가중치 기반 라우팅 상세 구조입니다. Target Group별로 가중치를 설정하여 트래픽을 분산합니다. 평상시에는 50:50, 한 클러스터 점검 시에는 0:100으로 조정합니다. Health Check 실패 시 자동으로 트래픽이 정상 클러스터로 전환됩니다.

Q&A:
- Q: ALB 대신 NLB를 사용하는 이유는?
  → NLB는 L4에서 동작하여 지연시간이 낮고, 가중치 라우팅이 Target Group 레벨에서 가능합니다. 클러스터 내부에서 Gateway API로 L7 라우팅을 처리합니다.
- Q: Health Check 간격은 어떻게 설정하나요?
  → 10초 간격, 2회 실패 시 Unhealthy로 설정하면 약 20-30초 내 자동 전환됩니다.
:::

---

@type: tabs

## Gateway API 소개

### GatewayClass
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: nginx
spec:
  controllerName: gateway.nginx.org/nginx-gateway-controller
```
**역할**: 인프라 제공자가 정의하는 Gateway 템플릿
**담당**: Platform Team

### Gateway
```yaml {filename="production-gateway.yaml"}
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: production-gateway
spec:
  gatewayClassName: nginx
  listeners:
    - name: https
      protocol: HTTPS
      port: 443
```
```yaml {filename="hwahae-gateway.yaml"}
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: hwahae-gateway
  namespace: gateway-system
spec:
  gatewayClassName: nginx
  listeners:
    - name: https
      protocol: HTTPS
      port: 443
      tls:
        mode: Terminate
        certificateRefs:
          - kind: Secret
            name: hwahae-tls
      allowedRoutes:
        namespaces:
          from: All
```
**역할**: 실제 로드밸런서 인스턴스
**담당**: Cluster Admin

### HTTPRoute
```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: api-route
spec:
  parentRefs:
    - name: production-gateway
  rules:
    - matches:
        - path: {type: PathPrefix, value: /api}
      backendRefs:
        - name: api-service
          port: 8080
```
**역할**: 애플리케이션 라우팅 규칙
**담당**: Application Developer

:::notes
{timing: 3min}
Gateway API는 Kubernetes의 차세대 인그레스 API입니다. 기존 Ingress API의 한계인 역할 분리 불가, Annotation 남용 문제를 해결합니다. GatewayClass, Gateway, HTTPRoute의 3계층 구조로 인프라 팀, 플랫폼 팀, 개발 팀의 책임을 명확히 분리합니다.

GitBook 참고: https://atomoh.gitbook.io/kubernetes-docs/networking/04-gateway-api

Q&A:
- Q: 기존 Ingress를 Gateway API로 마이그레이션해야 하나요?
  → 당장은 아닙니다. Ingress도 계속 지원되지만, 신규 구축 시 Gateway API를 권장합니다.
- Q: Istio VirtualService와 Gateway API 중 뭘 써야 하나요?
  → Gateway API가 Kubernetes 표준이므로 벤더 락인 없이 사용 가능합니다. Istio도 Gateway API를 지원합니다.
:::

---

@type: tabs

## VPC CNI & Prefix Delegation

### IP 고갈 문제
| 인스턴스 | 최대 ENI | ENI당 IP | **최대 Pod** |
|---------|---------|---------|-------------|
| t3.medium | 3 | 6 | **17** |
| t3.large | 3 | 12 | **35** |
| m5.xlarge | 4 | 15 | **58** |

**문제**: ENI당 할당 가능한 Secondary IP 수 제한
**결과**: 노드당 Pod 수 제한 → 수평 확장 비용 증가

### Prefix Delegation 솔루션
| 모드 | 할당 단위 | t3.medium 최대 Pod |
|------|----------|-------------------|
| Secondary IP | 개별 IP | 17 |
| **Prefix Delegation** | /28 (16 IPs) | **110** |

**/28 Prefix = 16개 IP 한 번에 할당**
- IP 할당 속도 향상 (1 API call → 16 IPs)
- 노드당 Pod 밀도 **6배 이상** 증가
- Nitro 인스턴스에서 최적 성능

### 적용 시 고려사항
**요구사항**:
- EKS 1.21+ / VPC CNI 1.9+
- Nitro 기반 인스턴스 권장
- 서브넷 /28 prefix 여유 확인

**주의사항**:
- 기존 노드 재시작 필요
- Windows 노드 미지원
- Custom Networking과 함께 사용 권장

:::notes
{timing: 3min}
{cue: demo}
IP 고갈 문제의 핵심은 ENI당 할당 가능한 Secondary IP 수 제한입니다. Prefix Delegation을 활성화하면 개별 IP 대신 /28 prefix(16개 IP)를 할당받아 노드당 Pod 밀도를 대폭 높일 수 있습니다.

GitBook 참고: https://atomoh.gitbook.io/kubernetes-docs/networking/01-vpc-cni

Q&A:
- Q: Prefix Delegation 활성화 시 기존 Pod에 영향이 있나요?
  → 기존 노드는 재시작이 필요합니다. 신규 노드부터 적용되므로 Rolling Update로 점진적 전환이 가능합니다.
- Q: /28이면 16개인데, 왜 t3.medium이 110개 Pod를 수용하나요?
  → ENI당 여러 개의 /28 prefix를 할당받을 수 있습니다. 인스턴스 타입별 최대 prefix 수가 다릅니다.
- Q: Karpenter를 쓰면 IP 고갈이 완화되나요?
  → 간접적으로 도움됩니다. Karpenter가 큰 인스턴스 타입을 자동 선택하면 노드당 ENI/IP 수용량이 증가하고, bin-packing 효율화로 노드 수가 줄어 낭비 IP가 감소합니다. 하지만 Pod당 1 IP 할당 구조는 동일하므로 Prefix Delegation이 근본 해결책입니다. Karpenter + Prefix Delegation 조합이 가장 효과적입니다.
:::

---

@type: code

## Custom Networking - ENIConfig (AZ별 Pod 서브넷)

```yaml {filename="eniconfig.yaml"}
apiVersion: crd.k8s.amazonaws.com/v1alpha1
kind: ENIConfig
metadata:
  name: ap-northeast-2a
spec:
  subnet: subnet-0abc123def456789a  # Pod 전용 서브넷
  securityGroups:
    - sg-0123456789abcdef0
```

:::notes
{timing: 2min}
ENIConfig를 사용한 Custom Networking 설정입니다. AZ별로 Pod 전용 서브넷을 지정하여 노드 서브넷과 Pod 서브넷을 분리합니다.

Q&A:
- Q: ENIConfig를 AZ별로 만들어야 하는 이유는?
  → Pod IP가 해당 AZ의 서브넷에서 할당되어야 Cross-AZ 트래픽을 최소화할 수 있습니다.
:::

---

@type: content

## Security Group for Pods — 선택지 비교

::: columns
:::: col
**SGP (Branch ENI)**
- Pod별 Security Group 적용 가능
- Branch ENI 소모 → **Pod 밀도 낮음**
- 기존 SG 규칙 재활용
- m5.large: 최대 9 Branch ENI

[badge-red] Pod 밀도 제한
::::
:::: col
**Prefix Delegation + Network Policy**
- 노드 SG 공유, Pod 격리는 Network Policy
- /28 prefix 단위 할당 → **Pod 밀도 6배↑**
- Cilium L3/L4/L7 필터링
- 대부분의 격리 요구사항 충족

[badge-green] 권장 조합
::::
:::: col
**Fargate**
- Task별 SG 적용 가능 (서버리스)
- ENI 제한 무관
- DaemonSet 미지원
- EKS 제어 영역 비용 별도

[badge-yellow] 특수 워크로드용
::::
:::

**권장**: SGP 필요 Pod만 선별 적용, 나머지는 Prefix Delegation + Network Policy 조합. 기존 SGP Pod → 대부분 Network Policy로 전환 가능

:::notes
{timing: 2min}
SGP(Security Group for Pods)와 대안 비교입니다. SGP는 Branch ENI를 사용하여 Pod별 SG를 적용하지만, 노드당 Branch ENI 수가 제한적입니다(m5.large 기준 최대 9개). Pod 밀도 부족 문제의 원인이 바로 이것입니다.

Prefix Delegation + Network Policy 조합이 대부분의 워크로드에 적합합니다. RDS나 ElastiCache 등 AWS 리소스 접근 제어가 필요한 경우만 SGP를 선별 적용하세요.

Fargate는 SGP 대안이지만 DaemonSet 미지원, 로그 수집기나 모니터링 에이전트를 사이드카로 전환해야 하는 트레이드오프가 있습니다.

Q&A:
- Q: Network Policy로 RDS 접근 제어가 가능한가요?
  → Network Policy는 IP/Port 기반 제어만 가능합니다. RDS Security Group에서 Pod 서브넷 CIDR을 허용하는 방식으로 대체합니다.
:::

---

@type: tabs

## SGP Branch ENI 제약과 대안

### Branch ENI 동작 원리
**Security Group for Pods(SGP) 아키텍처**:
```
Node ENI (Primary)     → 노드 자체 통신
Trunk ENI              → Branch ENI 관리 (노드당 1개)
Branch ENI             → SGP Pod 전용 (VLAN 태깅)
```

**제약 사항**:
| 인스턴스 | Branch ENI 최대 | SGP Pod 최대 |
|---------|---------------|-------------|
| t3.medium | 6 | 6 |
| m5.large | 9 | 9 |
| m5.xlarge | 18 | 18 |

- Prefix Delegation과 **병행 불가** (Branch ENI는 개별 IP 할당)
- SGP Pod는 Branch ENI 수에 제한됨 → 노드당 Pod 밀도 급감

### 해결 방안
**방안 1: SGP 최소화 + NetworkPolicy 활용 (권장)**
```yaml {filename="network-policy.yaml"}
# NetworkPolicy로 L3/L4 트래픽 제어 (SGP 불필요한 경우)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-access-only
spec:
  podSelector:
    matchLabels:
      app: api-server
  egress:
    - to:
        - ipBlock:
            cidr: 10.0.100.0/24  # RDS 서브넷
      ports:
        - port: 5432
```

**방안 2: SGP 필수 Pod는 Fargate로 전환**
- Fargate Pod는 자체 ENI → Branch ENI 제약 없음
- RDS 직접 접근 등 SG 필수 케이스에 적합

**방안 3: VPC CNI v1.15+ `POD_SECURITY_GROUP_ENFORCING_MODE=standard`**
- Standard 모드에서 SGP + Prefix Delegation 동시 사용 가능
- 단, NetworkPolicy와 SGP 간 우선순위 주의

### 권장 전략
::: columns
:::: col
**대부분의 Pod**
- Prefix Delegation (높은 Pod 밀도)
- NetworkPolicy로 L3/L4 트래픽 제어
- Spot Instance 활용 가능
::::
:::: col
**SG 필수 Pod (RDS 직접 접근 등)**
- **옵션 A**: Fargate (SGP 제약 없음)
- **옵션 B**: 전용 노드 그룹 (SGP 활성화)
- **옵션 C**: standard 모드 (v1.15+)
::::
:::

**권장**: 대부분 NetworkPolicy로 전환하고, RDS 직접 접근 등 SG가 반드시 필요한 Pod만 Fargate 또는 전용 노드 그룹으로 분리

:::notes
{timing: 2min}
SGP Branch ENI의 구체적인 제약과 해결 방안입니다. VPC CNI v1.15+에서는 standard 모드로 SGP와 Prefix Delegation을 동시에 사용할 수 있습니다.

Q&A:
- Q: standard 모드의 단점은 없나요?
  → NetworkPolicy와 SGP 규칙이 둘 다 적용되므로 우선순위를 명확히 이해해야 합니다. SGP가 더 제한적이면 NetworkPolicy가 무시될 수 있습니다.
:::

---

@type: compare

## 서브넷 IP 고갈 — 초기 설계 vs 후적용

::: left
### 초기 설계 시 적용 (권장)
- VPC 생성 시 Secondary CIDR 추가
- Pod 전용 서브넷 (/19 이상) 미리 구성
- ENIConfig AZ별 매핑 설정
- **장점**: 무중단 적용
- **장점**: 서브넷 사이징 자유도 높음
- **비용**: 추가 비용 없음
:::

::: right
### 운영 중 후적용
- Secondary CIDR 추가 → 가능 (VPC 설정)
- Pod 전용 서브넷 생성 → 가능
- Custom Networking 활성화 → **노드 롤링 재시작 필요**
- **주의**: 기존 Pod IP가 변경됨
- **주의**: ENIConfig 적용 후 신규 노드부터 적용
- **권장**: Blue/Green 노드 그룹 교체
:::

**결론**: 클러스터 초기 설계 시 `100.64.0.0/16` Secondary CIDR + Custom Networking을 적용하는 것이 **강력히 권장**됩니다. 후적용도 가능하지만 노드 롤링 재시작이 필요하며, Blue/Green 노드 그룹 교체 방식이 안전합니다.

:::notes
{timing: 2min}
서브넷 IP 고갈 문제를 초기 설계 시 적용하는 것과 운영 중 후적용하는 것의 차이입니다. 초기 설계 시 적용이 훨씬 수월하지만, 운영 중에도 Blue/Green 노드 그룹 교체로 적용 가능합니다.

Q&A:
- Q: 기존 클러스터에 Secondary CIDR을 추가하면 기존 서비스에 영향이 있나요?
  → CIDR 추가 자체는 영향 없습니다. Custom Networking 활성화 시 신규 노드부터 적용되므로 기존 서비스는 유지됩니다.
:::

---

@type: timeline

## ECS → EKS 마이그레이션 로드맵

1. **Phase 1: 기반 구축** — VPC 설계, EKS 클러스터 프로비저닝, Gateway API 설치 (2주)
2. **Phase 2: 파일럿 서비스** — 단일 서비스 마이그레이션, CI/CD 파이프라인 구축, 모니터링 설정 (2주)
3. **Phase 3: 점진적 전환** — 서비스별 순차 마이그레이션, 트래픽 가중치 조정, ECS 축소 (4주)
4. **Phase 4: 완전 전환** — ECS 종료, Multi-Cluster 활성화, 운영 안정화 (2주)

:::notes
{timing: 2min}
{cue: transition}
총 10주 마이그레이션 로드맵입니다. Phase 1에서 기반을 구축하고, Phase 2에서 파일럿 서비스로 검증합니다. Phase 3에서 점진적으로 서비스를 전환하며, Phase 4에서 완전한 전환과 Multi-Cluster 활성화를 완료합니다.

Q&A:
- Q: 10주가 현실적인 일정인가요?
  → IaC/GitOps가 준비되어 있다면 가능합니다. 준비 안 된 경우 Phase 1에 2-4주 추가를 권장합니다.
- Q: 파일럿 서비스 선정 기준은?
  → 트래픽이 적고, 장애 영향이 작으며, 팀이 적극적으로 협조하는 서비스를 선택합니다.
:::

---

@type: checklist

## 마이그레이션 사전 체크리스트

- [ ] **네트워크 준비**
  - VPC Secondary CIDR 추가 (100.64.0.0/16)
  - Pod 전용 서브넷 생성 (/19 이상)
  - Security Group 정리 및 표준화

- [ ] **IAM 준비**
  - EKS 클러스터 역할 생성
  - 노드 그룹 역할 생성
  - IRSA용 OIDC Provider 설정
  - Pod Identity 정책 준비

- [ ] **GitOps 준비**
  - Git 저장소 구조 설계
  - ArgoCD 설치 계획
  - Helm Chart / Kustomize 선택

- [ ] **모니터링 준비**
  - CloudWatch Container Insights 활성화
  - Prometheus/Grafana 스택 계획
  - 기존 ECS 메트릭 대시보드 매핑

:::notes
{timing: 2min}
마이그레이션 전 반드시 확인해야 할 체크리스트입니다. 특히 네트워크 준비가 가장 중요합니다. Secondary CIDR과 Pod 서브넷을 미리 준비하지 않으면 마이그레이션 중간에 IP 고갈 문제가 재발할 수 있습니다.

Q&A:
- Q: IRSA와 Pod Identity 중 어떤 것을 써야 하나요?
  → 신규 구축이면 Pod Identity를 권장합니다. 설정이 간편하고 OIDC Provider 없이 동작합니다.
:::

---

@type: quiz

## Block 01 Quiz

**Q1: Multi-Cluster Active-Active 아키텍처의 주요 장점은?**
- [ ] 관리 포인트가 단일화된다
- [x] Blast Radius를 줄여 장애 영향을 최소화한다
- [ ] 클러스터 간 Pod 통신이 빨라진다
- [ ] 비용이 절감된다

**Q2: Gateway API에서 애플리케이션 개발자가 관리하는 리소스는?**
- [ ] GatewayClass
- [ ] Gateway
- [x] HTTPRoute
- [ ] DestinationRule

**Q3: Multi-Cluster 환경에서 클러스터 간 워크로드 동기화에 사용하는 도구는?**
- [ ] Cluster Autoscaler
- [x] ArgoCD ApplicationSet
- [ ] kubectl apply
- [ ] Helm install

**Q4: NLB 가중치 라우팅에서 한 클러스터 점검 시 권장 설정은?**
- [ ] 50:50 유지
- [ ] Health Check로 자동 전환
- [x] 0:100으로 수동 조정
- [ ] 클러스터 삭제

:::notes
{timing: 3min}
{cue: question}
Block 01 내용을 복습하는 퀴즈입니다. 각 질문에 대해 잠시 생각해보시고, 정답을 확인해보세요. 이해가 안 되는 부분이 있으면 질문해주세요.

Q&A:
- Q: 다음 Block에서는 어떤 내용을 다루나요?
  → Block 02에서는 Karpenter를 활용한 노드 오토스케일링과 Spot Instance 전략을 다룹니다.
:::
