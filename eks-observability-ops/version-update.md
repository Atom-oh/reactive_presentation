# EKS Auto Mode · Karpenter 버전 검토

확인일: **2026-10-07 (UTC)**. AWS 공식 문서와 Karpenter 공식 릴리스·호환성 표를 조회한 결과입니다. 이 문서는 `01-architecture`와 `02-node-lifecycle`의 버전·설정 기준입니다.

**2026-10-12 재확인**: Karpenter **v1.15.0**이 2026-10-10에 출시되었고, 공식 호환성 표가 Kubernetes **1.37 → Karpenter 1.15.x**로 갱신되었습니다. 슬라이드의 Karpenter 설명은 v1.14 계열 기준이며, 1.37 클러스터에 직접 설치한다면 아래 "Karpenter v1.15.0 업그레이드 시 주의"를 먼저 확인합니다.

처음 학습한다면 [쉬운 설명과 슬라이드 바로가기](quick-guide.md)부터 읽으세요. 아래는 적용 범위·전체 설정·공식 출처를 확인할 때 사용하는 상세 참고입니다.

이번 재검토에서는 최신 버전을 다시 조회하고 **학습자가 실제로 판단할 질문**에 맞춰 설명을 줄였습니다. `Balanced`는 “절감할 가치가 있나?”, 버퍼는 “앱이 기다릴 자리를 미리 둘까?”, 업그레이드는 “Controller와 설정 형식(CRD)을 함께 준비했나?”로 읽으면 됩니다.

## 최신 버전과 적용 범위

| 대상 | 확인 결과 | 적용 시 주의점 |
|---|---|---|
| Amazon EKS Kubernetes | **1.37**, EKS 출시일 **2026-10-01** | 표준 지원: 1.34–1.37. 대상 리전의 가용 버전도 확인 |
| EKS Auto Mode | AWS가 관리형 구성 요소를 업데이트 | 사용자가 설치할 별도 Karpenter 버전을 지정하지 않음. EKS 버전과 Auto Mode 릴리스 노트를 함께 확인 |
| 직접 설치한 Karpenter AWS provider | **v1.14.1**, **2026-08-21** 릴리스 | 2026-10-07 기준 GitHub `releases/latest` 안정 릴리스. 해당 릴리스는 **2027-07까지 LTS 지원**으로 표기. 2026-10-12 기준 최신은 **v1.15.0** (2026-10-10) |

### Kubernetes 호환성

| Kubernetes | 직접 설치한 Karpenter의 공식 최소 버전 |
|---|---|
| 1.34 | ≥ 1.6 |
| 1.35 | ≥ 1.9 |
| 1.36 | ≥ 1.13 |
| 1.37 | **1.15.x** (2026-10-12 확인) |

Kubernetes 1.37 클러스터에서 직접 설치한 Karpenter를 운영하려면 공식 호환성 표 기준 1.15.x가 필요합니다. v1.14.1은 1.36까지 해당합니다. 직접 설치한 Karpenter를 운영하는 클러스터는 Karpenter를 먼저 1.15.x로 올리고 테스트 결과를 확인한 후 Kubernetes를 업그레이드합니다. 위 최소 버전은 최신 보안 패치 권장 버전을 의미하지 않습니다.

## Auto Mode의 주요 변경 사항

- **2026-10-01 / EKS 1.37**: 새 Auto Mode NodePool의 기본 `consolidationPolicy`가 `Balanced`로 변경되었습니다. 비용 절감과 Pod 중단 비용을 함께 평가합니다. 기존 커스텀 NodePool은 생성 시 기본값을 적용받으므로, 단순 업그레이드와 삭제 후 재생성을 구분해야 합니다. GitOps에서는 정책을 명시해 재생성 시 동작 변화를 방지합니다.
- **기본 제공 NodePool**: EKS 1.37의 `general-purpose`와 `system`도 `Balanced`를 사용합니다. EKS가 관리·재조정하므로 직접 수정하지 않고, 다른 정책이 필요하면 커스텀 NodePool을 만듭니다.
- **2026-09-14 공지**: EBS 볼륨 변경용 `volume-modifier-for-k8s` annotation 지원은 **2026-10-31 이후 종료**됩니다. 볼륨 속성 변경은 Kubernetes `VolumeAttributesClass`로 전환합니다.
- **2026-08-12**: Auto Mode 로드 밸런서 컨트롤러는 AWS Load Balancer Controller v3.4까지의 기능을 지원한다고 공지했습니다. **Gateway API는 아직 미지원**으로 명시되어 있습니다. 이를 사용자가 설치하는 컨트롤러 버전과 동일시하지 않습니다.
- **Static capacity NodePool**: `spec.replicas`로 고정 노드 수를 유지할 수 있습니다. 이 노드는 Consolidation 대상에서 제외되지만 Drift와 만료에 따른 교체는 계속됩니다. AZ별 균등 분포가 필요하면 AZ별 NodePool을 구성합니다.

## Karpenter v1.14 계열의 주요 변경 사항

v1.14.1은 패치 릴리스이며, 다음 기능은 v1.14.0 업그레이드 안내에 명시되어 있습니다.

- Capacity Buffers API가 `v1beta1`로 승격되며 `autoscaling.x-k8s.io_capacitybuffers` CRD가 추가됩니다.
- Dynamic Resource Allocation(DRA)의 consumable capacity·partitionable device 지원이 추가됩니다. 이는 직접 설치한 Karpenter의 변경 사항이며 Auto Mode 기능 지원은 AWS 문서에서 별도 확인합니다.
- `Balanced` Consolidation 정책이 추가됩니다. 기존 `WhenEmptyOrUnderutilized` 설정은 명시적으로 바꾸기 전까지 유지됩니다.
- Preview instance type 지원은 `NodeOverlay` feature gate를 사용하는 선택 기능입니다.

### Karpenter v1.15.0 업그레이드 시 주의 (2026-10-10 출시)

공식 업그레이드 안내 "Upgrading to 1.15.0+"에 명시된 항목입니다. 대시보드와 알림 규칙에 영향을 주는 변경이 포함되어 있습니다.

- **Breaking**: Node Auto Repair(alpha, `NodeRepair` feature gate)가 voluntary disruption으로 바뀌었습니다. 대체 노드를 먼저 만들고, NodePool Disruption Budget의 새 `Unhealthy` reason과 PDB를 지키며 drain합니다. CRD에 `Unhealthy` reason이 추가되므로 CRD를 Controller와 함께 업그레이드합니다.
- **Breaking**: `karpenter_nodepool_allowed_disruptions`, `karpenter_nodepool_nodes_consuming_budgets`의 `reason` label이 소문자(`underutilized`)로 바뀝니다.
- **Breaking**: `karpenter_voluntary_disruption_queue_failures_total`의 `consolidation_type` label이 consolidation 종류(`empty`, `single`, `multi`)를 나타냅니다. decision으로 거르려면 `decision` label을 사용합니다.
- **Breaking**: `karpenter_cloudprovider_errors_total`의 분류되지 않은 `error` label이 빈 문자열 대신 `unknown`이 됩니다.
- **Deprecation**: Consolidation 대상 선택에는 `karpenter.sh/disruption-cost` annotation을 사용합니다. `controller.kubernetes.io/pod-deletion-cost`로 Consolidation을 조정하는 방식은 deprecated입니다.
- Bottlerocket 기본 root volume이 6Gi로 커졌습니다. `blockDeviceMappings`를 직접 지정하고 Kubernetes 1.37 Bottlerocket NVIDIA AMI를 쓴다면 `/dev/xvda`를 6Gi 이상으로 지정합니다.

### 직접 설치한 Karpenter 업그레이드 점검

1. 현재 Kubernetes·Karpenter 버전과 중간 마이너 릴리스의 업그레이드 안내를 확인합니다. `NodePool`·`EC2NodeClass`는 `v1` API를 사용합니다. 이 두 리소스의 구 `v1beta1` 설정은 마이그레이션 가이드를 먼저 따릅니다.
2. Controller와 **`karpenter-crd` 차트를 같은 버전으로 관리**합니다 (Kubernetes 1.36 이하는 1.14.1, 1.37은 1.15.x). Controller 차트의 일반 Helm upgrade만으로 기존 CRD가 갱신된다고 가정하지 않습니다. 기존 CRD 소유권과 새 CapacityBuffer CRD를 확인합니다.
3. 1.12 이전 버전에서 올라오면 CA bundle hashing 변경으로 인한 Drift, `ec2:DescribeInstanceStatus` 권한 추가를 검토합니다. Zonal Shift를 사용한다면 선택 기능의 `arc-zonal-shift:GetManagedResource` 권한도 확인합니다.
4. 테스트 환경에서 NodePool·NodeClass Ready 상태, 신규 노드 프로비저닝, PDB·Disruption Budget, Consolidation·Drift·Spot 중단 대응과 메트릭을 검증합니다.

위 절차는 직접 설치한 Karpenter용입니다. Auto Mode에는 Helm으로 Karpenter를 업그레이드하지 않습니다.

## Spot 회수와 여유 용량을 읽는 기준

- **종료 처리와 대체 준비는 병행합니다.** Karpenter는 Spot interruption warning을 받으면 drain과 새 노드 프로비저닝을 함께 시작합니다. `Pod 종료 → Pending → 그제야 새 노드 요청`이라는 고정 순서로 설명하지 않습니다.
- **2분은 복구 보장이 아닙니다.** EC2의 stop/terminate interruption notice는 통상 2분 전 알림이며, hibernate는 같은 2분 유예 없이 시작됩니다. 노드·이미지·앱 준비가 늦으면 회수 후에도 Pending 또는 시작 대기가 남을 수 있습니다.
- **더미 Pod 버퍼는 조건부로 대기를 줄입니다.** 실제 Pod의 우선순위가 높고 스케줄링 제약이 맞아야 예약된 용량을 선점할 수 있습니다. Spot뿐 아니라 On-Demand에도 적용할 수 있으며 추가 용량 비용이 듭니다. 슬라이드의 `required` hostname anti-affinity 예제는 더미 두 개를 서로 다른 노드에 배치합니다. 여유가 있는 기존 노드를 활용할 수도 있지만 그림은 기존 노드에 남은 자리가 없는 경우입니다.
- **Capacity Buffers API와 더미 Pod는 다른 방식입니다.** v1.14 업그레이드 안내는 API의 `v1beta1` 승격과 새 CRD를 명시합니다. 직접 설치한 Karpenter의 변경 사항이며, 이를 Auto Mode 지원으로 해석하지 않습니다. 강의에서는 개념만 소개하고 확인하지 않은 API YAML은 제공하지 않습니다.
- **Static capacity도 구분합니다.** `spec.replicas`는 노드 수를 유지하는 기능입니다. 워크로드가 이미 그 노드를 사용한다면 여유 자리가 보장되는 것은 아닙니다.

근거: [Karpenter v1.14 Interruption](https://karpenter.sh/v1.14/concepts/disruption/#interruption), [EC2 Spot interruption notice](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-instance-termination-notices.html), [AWS의 Pod priority·overprovisioning 설명](https://aws.amazon.com/blogs/containers/eliminate-kubernetes-node-scaling-lag-with-pod-priority-and-over-provisioning/), [Karpenter v1.14 업그레이드 안내](https://karpenter.sh/docs/upgrading/upgrade-guide/#upgrading-to-1140), [Auto Mode Static capacity](https://docs.aws.amazon.com/eks/latest/userguide/auto-static-capacity.html).

## 기존 설명에서 바로잡은 부분

| 기존 표현·예시 | 이번 설명 |
|---|---|
| Spot + On-Demand면 60–70% 절감 | 두 유형 허용은 비율·절감률 보장이 아님. 실제 비용과 앱 영향을 측정 |
| Graviton을 항상 최종 선택 | 조건에 맞는 후보를 먼저 좁히고, 리소스·가용 용량·가격도 확인 |
| NodePool·NodeClass가 바뀌면 모두 Drift | 기존 노드와 원하는 설정이 맞지 않을 때 검토. `limits`, `weight`, `disruption.*`는 Drift를 유발하지 않음 |
| 더미 Pod 두 개를 새 노드 한 대에 복원 | 예제의 required anti-affinity에 맞게 서로 다른 노드에 복원 |
| NodeClass는 workload를 만들고 NodePool은 default를 참조 | 커스텀 예제들을 `workload` NodeClass에 연결 |

근거: [Karpenter NodePool capacity type](https://karpenter.sh/v1.14/concepts/nodepools/), [Karpenter Drift](https://karpenter.sh/v1.14/concepts/disruption/#drift), [Auto Mode NodeClass 참조](https://docs.aws.amazon.com/eks/latest/userguide/create-node-class.html).

## 두 환경의 설정 차이

| 항목 | EKS Auto Mode | 직접 설치한 Karpenter |
|---|---|---|
| NodePool API | `karpenter.sh/v1` | `karpenter.sh/v1` |
| NodeClass | `eks.amazonaws.com/v1`, `NodeClass` | `karpenter.k8s.aws/v1`, `EC2NodeClass` |
| `nodeClassRef.group` / `kind` | `eks.amazonaws.com` / `NodeClass` | `karpenter.k8s.aws` / `EC2NodeClass` |
| EC2 관련 요구 라벨 | `eks.amazonaws.com/instance-*` | `karpenter.k8s.aws/instance-*` |
| 공통 라벨 | `karpenter.sh/capacity-type`, `kubernetes.io/arch`, `topology.kubernetes.io/zone` | 동일 |
| OS·AMI | AWS 관리 Bottlerocket 계열, 직접 AMI 선택 없음 | `amiSelectorTerms` 등으로 선택·관리 |
| 노드 접근 | SSH·SSM 직접 접근 불가 | 선택한 AMI와 접근 정책에 따라 구성 |
| 노드 로컬 스토리지 | `ephemeralStorage` | `blockDeviceMappings` |
| Spot 중단 처리 | AWS 관리 | Interruption queue와 EventBridge·SQS 구성 필요 |
| 관측성 | Kubernetes Node·NodeClaim·이벤트, kube-state-metrics 등 | 여기에 Controller 로그와 `karpenter_*` 메트릭 추가 가능 |

### 기본 제공 NodePool의 실제 설정

| NodePool | 아키텍처 | 용량 | 특성 |
|---|---|---|---|
| `general-purpose` | `amd64` | On-Demand | 범용 워크로드 |
| `system` | `amd64`, `arm64` | On-Demand | `CriticalAddonsOnly:NoSchedule` taint |

두 풀 모두 C/M/R 계열, 5세대 이상 인스턴스와 `default` NodeClass를 사용합니다. Spot이나 다른 요구사항은 **커스텀 NodePool**에서 설정합니다. 기본 풀은 활성화·비활성화만 가능하며, 비활성화하면 관리 노드가 drain·종료되므로 용량 이전을 먼저 계획합니다.

### Auto Mode 커스텀 NodeClass와 NodePool 예제

아래는 환경별 IAM 역할과 subnet/security group 태그를 준비한 뒤 적용하는 예제입니다. 사용자 정의 NodeClass의 노드 IAM 역할에는 **`EC2` 유형 EKS Access Entry**와 **`AmazonEKSAutoNodePolicy`** 연결이 필요합니다. 노드 역할의 IAM 정책도 별도로 구성합니다.

```yaml
apiVersion: eks.amazonaws.com/v1
kind: NodeClass
metadata:
  name: workload
spec:
  role: MyAutoModeNodeRole
  subnetSelectorTerms:
    - tags:
        karpenter.sh/discovery: my-cluster
        network-type: private
  securityGroupSelectorTerms:
    - tags:
        karpenter.sh/discovery: my-cluster
  ephemeralStorage:
    size: 80Gi
---
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: workload
spec:
  template:
    spec:
      nodeClassRef:
        group: eks.amazonaws.com
        kind: NodeClass
        name: workload
      requirements:
        - key: kubernetes.io/arch
          operator: In
          values: [amd64]
        - key: eks.amazonaws.com/instance-category
          operator: In
          values: [c, m, r]
        - key: karpenter.sh/capacity-type
          operator: In
          values: [on-demand, spot]
      expireAfter: 336h
      terminationGracePeriod: 24h
  disruption:
    consolidationPolicy: Balanced
    consolidateAfter: 1m
    budgets:
      - nodes: "10%"
  limits:
    cpu: "1000"
```

`karpenter.sh/discovery`와 `network-type`은 이 예제의 리소스 검색용 사용자 태그입니다. NodePool 요구 라벨의 API 접두사와 구분합니다. Private subnet에는 필요한 AWS 서비스로의 NAT 또는 VPC endpoint 연결도 준비합니다.

### 노드 수명과 안전한 교체

- `expireAfter`의 위치는 **`spec.template.spec.expireAfter`**입니다. `spec.disruption` 하위에 두지 않습니다.
- Auto Mode 기본 `expireAfter`는 **336h(14일)**, 최대 노드 수명은 **21일**입니다. `terminationGracePeriod` 미지정 시 NodeClaim에 기본 **24h**가 적용됩니다. 7일은 사용자 정책 예시이며 AWS 공통 권장값이 아닙니다.
- NodePool Disruption Budget의 `nodes`는 중단 가능한 노드의 상한입니다. 비율은 올림하고 삭제 중·NotReady 노드를 차감하며, 여러 예산은 최솟값을 적용합니다. `schedule`과 `duration`은 각 `budgets[]` 항목 안에 두고 시간대는 UTC입니다.
- NodePool Disruption Budget은 자발적 교체의 속도를 제어합니다. 만료·Spot 중단 같은 강제 종료를 막는 보장은 아니며, PDB도 Spot 회수나 termination grace 기한을 무기한 늦출 수 없습니다.
- Auto Mode가 AMI를 관리합니다. 사용자는 PDB, 교체 예산, 워크로드 종료 시간과 관측성을 관리합니다. 프로비저닝 시간은 인스턴스·네트워크·이미지에 따라 달라지며 슬라이드의 타임라인 수치는 시뮬레이션 예시입니다.

## 메트릭 예제의 전제

공통 노드·Pod 쿼리는 kube-state-metrics 수집을 전제로 합니다. NodePool·Spot 라벨을 쿼리하려면 kube-state-metrics에 다음 allowlist를 설정합니다.

```text
--metric-labels-allowlist=nodes=[karpenter.sh/nodepool,karpenter.sh/capacity-type,eks.amazonaws.com/compute-type]
```

복수 클러스터를 함께 수집한다면 각 쿼리에 `cluster` 필터를 적용합니다. `kube_pod_status_phase{phase="Pending"}`는 전체 Pending Pod이며, Unschedulable과 구분합니다. `karpenter_pods_startup_duration_seconds`는 직접 설치한 Controller가 노출하는 **Pod 시작 시간** 메트릭입니다. Prometheus **Summary** 타입이라 `_bucket` series가 없으므로 `histogram_quantile` 대신 `quantile` label로 조회합니다. 이 값은 Node Ready 시간과 동일하지 않습니다. Auto Mode에서 동일 endpoint가 제공된다고 가정하지 않습니다.

## 공식 출처

- [EKS 지원 버전과 출시 일정](https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html)
- [EKS Auto Mode 개요](https://docs.aws.amazon.com/eks/latest/userguide/automode.html)
- [EKS Auto Mode 릴리스 노트](https://docs.aws.amazon.com/eks/latest/userguide/auto-change.html)
- [Auto Mode 기본 NodePool](https://docs.aws.amazon.com/eks/latest/userguide/set-builtin-node-pools.html)
- [Auto Mode 커스텀 NodePool·Disruption·종료 유예](https://docs.aws.amazon.com/eks/latest/userguide/create-node-pool.html)
- [Auto Mode NodeClass·Access Entry](https://docs.aws.amazon.com/eks/latest/userguide/create-node-class.html)
- [Auto Mode Static capacity NodePool](https://docs.aws.amazon.com/eks/latest/userguide/auto-static-capacity.html)
- [Karpenter 최신 릴리스 API](https://api.github.com/repos/aws/karpenter-provider-aws/releases/latest)
- [Karpenter v1.14.1 릴리스·LTS 표기](https://github.com/aws/karpenter-provider-aws/releases/tag/v1.14.1)
- [Karpenter v1.15.0 릴리스](https://github.com/aws/karpenter-provider-aws/releases/tag/v1.15.0), [업그레이드 안내](https://karpenter.sh/docs/upgrading/upgrade-guide/), [호환성 표](https://karpenter.sh/docs/upgrading/compatibility/)
- [Karpenter 메트릭 레퍼런스](https://karpenter.sh/docs/reference/metrics/)
- [Karpenter Kubernetes 호환성](https://karpenter.sh/docs/upgrading/compatibility/)
- [Karpenter 업그레이드 가이드](https://karpenter.sh/docs/upgrading/upgrade-guide/)
- [Karpenter v1.14 Disruption·Budget](https://karpenter.sh/v1.14/concepts/disruption/)
- [Karpenter v1.14 메트릭](https://karpenter.sh/v1.14/reference/metrics/)
- [kube-state-metrics Node 메트릭](https://github.com/kubernetes/kube-state-metrics/blob/main/docs/metrics/cluster/node-metrics.md)
- [kube-state-metrics Pod 메트릭](https://github.com/kubernetes/kube-state-metrics/blob/main/docs/metrics/workload/pod-metrics.md)

검증 범위: 공식 문서 대조, Markdown YAML·인라인 JavaScript 구문 검사, 브라우저의 학습용 인터랙션·화면 검증 통과. FHD(1920×1080)·4K(3840×2160)에서 슬라이드와 Canvas 단계 전환을 확인했습니다. 실제 AWS 클러스터에 리소스를 배포하거나 업그레이드하지 않았습니다.
