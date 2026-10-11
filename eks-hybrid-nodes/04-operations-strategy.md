---
remarp: true
block: 04-operations-strategy
---

---
<!-- Slide 1: Block 4 커버 -->
@type: cover
@title: 운영·워크로드·보안 & 전략

# 운영·워크로드·보안 & 전략

## Block 4 — 배치, GPU, 관측성, 망분리 검토, 비용과 도입 판단

:::notes
{timing: 0.5min}
[요약]
• Block 4는 "붙인 다음 어떻게 운영하고 판단할 것인가"를 다룸
• 배치 → GPU → 관측성 → 외부 트래픽 → 보안·규제 → 비용·도입 판단 순서
• 마지막에 4개 블록 전체 핵심 요약과 퀴즈

앞선 세 블록에서 Hybrid Nodes를 붙이는 방법을 봤다면, 이번 블록은 붙인 뒤의 이야기입니다.
워크로드를 어디에 놓을지, GPU는 어떻게 나눌지, 어떻게 관측하고, 보안팀에는 무엇을 설명해야 하는지, 마지막으로 비용과 도입 판단까지 30분 안에 훑어보겠습니다.
{cue: transition}
먼저 워크로드 배치 원칙부터 시작합니다.
:::

---
<!-- Slide 2: 워크로드 배치 원칙 -->
@type: tabs
@title: 배치는 label 하나에서 시작한다

## 배치는 label 하나에서 시작한다

### nodeSelector
Hybrid 노드에는 `eks.amazonaws.com/compute-type=hybrid` label이 자동으로 붙습니다. 위치 label(`example.com/location`)은 노드 소유자가 직접 부여합니다.

```yaml
nodeSelector:
  eks.amazonaws.com/compute-type: hybrid
  example.com/location: onprem
tolerations:            # hybrid taint를 쓰는 경우에만 필요
  - key: eks.amazonaws.com/compute-type
    operator: Equal
    value: hybrid
    effect: NoSchedule
```

### nodeAffinity
```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:          # term끼리 OR, term 안은 AND
        - matchExpressions:
            - {key: eks.amazonaws.com/compute-type, operator: In, values: [hybrid]}
            - {key: example.com/location, operator: In, values: [onprem]}
        - matchExpressions:
            - {key: example.com/location, operator: In, values: [cloud]}
            - {key: karpenter.sh/nodepool, operator: In, values: [cloud-burst-pool]}
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        preference:
          matchExpressions:
            - {key: example.com/location, operator: In, values: [onprem]}
```

### Taint (선택)
Hybrid taint는 **선택 사항**입니다. 자동으로 붙지 않으며, 추가 전에 CNI·DNS·GPU 인프라 Pod의 toleration부터 확인합니다.

```bash
kubectl taint node "$NODE_NAME" \
  eks.amazonaws.com/compute-type=hybrid:NoSchedule
```

`NoSchedule`은 새 스케줄링에만 영향을 줍니다. label이나 required affinity를 바꿔도 이미 실행 중인 Pod는 자동으로 이동하지 않습니다.

### topologySpread
```yaml
topologySpreadConstraints:
  - maxSkew: 2
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: ScheduleAnyway
    labelSelector:
      matchLabels:
        app: hybrid-burst-app
```

`ScheduleAnyway`는 점수 선호이며 `maxSkew`를 넘을 수 있습니다. zone label은 실제 장애 도메인에만 부여하고, 모든 Hybrid 호스트를 AWS AZ로 표시하지 않습니다.

:::notes
{timing: 2min}
[요약]
• compute-type=hybrid label만 자동, 위치 label은 노드 소유자가 부여
• nodeAffinity에서 term끼리는 OR, term 안 expression은 AND
• taint는 선택 사항이며 자동 부여되지 않음
• topologySpread의 ScheduleAnyway는 선호도일 뿐 보장이 아님

가장 먼저 기억하실 것은 Hybrid 노드에 자동으로 붙는 label이 compute-type=hybrid 하나뿐이라는 점입니다. 온프레미스, 클라우드 같은 위치 구분은 노드 소유자가 직접 label로 붙여야 합니다.
nodeAffinity 탭의 예제는 "승인된 온프레미스 집합 또는 승인된 클라우드 풀"이라는 OR 조건을 만들고, 온프레미스를 선호하도록 weight를 줍니다. 다만 weight는 스케줄링 점수이지 용량 비율이 아닙니다.
{cue: pause}
taint 탭에서 중요한 건, Hybrid taint가 자동으로 붙지 않는다는 점입니다. 필요하면 직접 붙이되 CNI나 DNS 같은 인프라 Pod의 toleration을 먼저 확인하세요.
{cue: question}
혹시 지금 운영 중인 클러스터에서 "클라우드 노드 = compute-type label 없음"이라고 가정하는 셀렉터가 있나요? 그건 안전하지 않은 가정입니다.

[출처]
• D/06 워크로드 배치 전략 (배치 제약과 허용, 토폴로지와 데이터 locality)
:::

---
<!-- Slide 3: 클라우드 버스팅 -->
@type: content
@title: 버스팅은 Pending Pod가 트리거

## 버스팅은 Pending Pod가 트리거

:::html
<style>
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.flow-h { margin: 0 0 var(--space-4); }
.flow-h .flow-box { min-width: min-content; overflow-wrap: normal; }
.hn-flow-sub { display: block; color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: break-word; }
</style>
<div class="flow-h">
  <div class="flow-box fragment fade-right" data-fragment-index="1">온프레미스 용량 부족<br><span class="hn-flow-sub">스케줄 불가 Pod</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="2">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="2">Pod = Pending<br><span class="hn-flow-sub">toleration 보유</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="3">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="3">Karpenter NodePool<br><span class="hn-flow-sub">requirements 매칭</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="4">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="4">EC2 노드 생성<br><span class="hn-flow-sub">cloud-burst-pool</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="5">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="5">Pod 스케줄</div>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="6">
  <div class="callout callout-warning"><strong class="text-warning">자동 복귀 없음</strong><div class="on-surface-muted">온프레미스 용량이 돌아와도 실행 중인 cloud Pod는 자동으로 돌아오지 않습니다.</div></div>
  <div class="callout callout-info"><strong class="text-info">포화 감지기가 아님</strong><div class="on-surface-muted">Karpenter는 조건에 맞는 Pending Pod에 반응합니다. 온프레미스 슬롯을 먼저 채우는 것도 보장하지 않습니다.</div></div>
  <div class="callout callout-danger"><strong class="text-danger">버전 요구</strong><div class="on-surface-muted">Kubernetes 1.36은 Karpenter 1.13 이상이 필요합니다.</div></div>
  <div class="callout callout-info"><strong class="text-info">막힐 수 있는 곳</strong><div class="on-surface-muted">AWS quota, 인스턴스 가용성, subnet IP, IAM, 노드 bootstrap, 워크로드 의존성.</div></div>
</div>
:::


:::notes
{timing: 1.5min}
[요약]
• Karpenter는 Pending Pod에 반응해 EC2 용량을 만들며, 온프레미스 서버를 추가하지 않음
• 클라우드 풀은 opt-in taint와 toleration으로 범위를 제한
• 클라우드 Pod의 자동 복귀는 없고 별도 통제된 재배치가 필요
• Kubernetes 1.36에는 Karpenter 1.13 이상 필요

흔한 오해가 "온프레미스가 가득 차면 Karpenter가 감지해서 클라우드로 넘긴다"는 설명입니다. 실제로는 스케줄되지 못해 Pending이 된 Pod, 그것도 NodePool 조건과 toleration이 맞는 Pod에 반응하는 것입니다.
{cue: pause}
그리고 온프레미스 용량이 다시 생겨도 이미 뜬 클라우드 Pod는 돌아오지 않습니다. 되돌리려면 데이터와 가용성을 고려한 별도의 rollout이나 eviction 정책이 필요합니다.
버전도 확인하세요. 문서 기준으로 Kubernetes 1.36은 Karpenter 1.13 이상이 필요하고, 예제 CRD는 1.14.1로 확인했다고 되어 있습니다. 또 EC2NodeClass의 instance profile은 SSM이나 Roles Anywhere용 Hybrid 역할이 아니라 별도로 준비한 EC2 노드 profile입니다.
{cue: transition}
다음은 반대 방향, 줄일 때 어떤 Pod가 먼저 사라지는지 보겠습니다.

[출처]
• D/06 "Cloud burst pool 준비" (Karpenter 호환성 1.36 → ≥1.13, 예제 1.14.1)
:::

---
<!-- Slide 4: 스케일-인 순서 -->
@type: content
@title: 스케일-인 순서는 선호일 뿐

## 스케일-인 순서는 선호일 뿐

:::html
<style>
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="card-grid fragment" data-reveal="stagger" data-reveal-anim="right" data-reveal-pace="slow" data-fragment-index="1">
  <div class="metric-card"><strong class="text-accent">1. 할당 상태</strong><div class="on-surface-muted">미할당 Pod가 할당된 Pod보다 먼저</div></div>
  <div class="metric-card"><strong class="text-accent">2. Pod 단계</strong><div class="on-surface-muted">Pending, Unknown, Running 순서</div></div>
  <div class="metric-card"><strong class="text-accent">3. Ready 여부</strong><div class="on-surface-muted">NotReady가 Ready보다 먼저</div></div>
  <div class="metric-card"><strong class="text-success">4. deletion cost</strong><div class="on-surface-muted">그 뒤에야 낮은 값이 먼저 제거</div></div>
</div>
<div class="card-grid">
  <div class="callout callout-danger fragment fade-up" data-fragment-index="2"><strong class="text-danger">CREATE webhook은 비권장</strong><div class="on-surface-muted">CREATE 시점의 Pod에는 최종 노드(spec.nodeName)가 아직 없어 위치를 신뢰성 있게 알 수 없습니다.</div></div>
  <div class="callout callout-success fragment zoom-in" data-fragment-index="3"><strong class="text-success">대안: 스케줄 후 패치</strong><div class="on-surface-muted">바인딩 뒤 소유한 Pod 한 개에 annotation을 부여하고, UID, resourceVersion, nodeName을 test로 검사합니다.</div></div>
</div>
:::


:::notes
{timing: 1.5min}
[요약]
• pod-deletion-cost는 ReplicaSet 축소 시 best-effort 선호도
• 할당, 단계, Ready 여부가 먼저 비교되고 그 뒤에 cost를 비교
• 비정상 온프레미스 Pod가 정상 cloud Pod보다 먼저 제거될 수 있음
• CREATE 시점 mutating webhook 방식은 운영 해법이 아님

controller.kubernetes.io/pod-deletion-cost annotation은 ReplicaSet을 줄일 때 낮은 값을 best-effort로 먼저 지우는 선호도입니다. 기본값은 0이고 음수도 됩니다.
하지만 비교 순서에서 deletion cost는 네 번째입니다. 그래서 cost 1000을 준 온프레미스 Pod라도 NotReady 상태라면 cost 0인 정상 클라우드 Pod보다 먼저 제거될 수 있습니다. cost 1000은 eviction이나 노드 장애로부터의 보호가 아닙니다.
{cue: pause}
그럼 "Pod가 만들어질 때 webhook으로 노드 위치를 보고 cost를 자동으로 넣자"는 아이디어는 어떨까요? CREATE 요청 시점에는 아직 spec.nodeName이 없습니다. 최종 노드를 알 수 없으니 운영 해법으로 설치하지 않는다는 것이 문서의 결론입니다.
대안은 스케줄링 이후에 소유한 Pod 하나씩 patch하는 방식입니다. 문서의 예제는 Pod UID, resourceVersion, nodeName을 test로 걸어서 동시 변경 시 안전하게 실패하도록 합니다. Karpenter 1.14.1도 pod-deletion-cost를 eviction-cost 계산에 쓰지만 이는 휴리스틱이지 금지 규칙은 아닙니다.
{cue: transition}
이제 GPU 쪽으로 넘어가겠습니다.

[출처]
• D/06 "Pod deletion cost는 선호도" (L311-320), "Binding 후 소유한 Pod 하나에 cost 부여" (L328)
:::

---
<!-- Slide 5: GPU 할당 방식 -->
@type: content
@title: GPU마다 할당 관리자는 하나

## GPU마다 할당 관리자는 하나

| 경로 | 할당 방식 |
|---|---|
| 독립 NVIDIA device plugin | `nvidia.com/gpu` 등 확장 리소스 게시 |
| 독립 DRA driver | ResourceSlice 게시, DeviceClass/ResourceClaim으로 할당 |
| GPU Operator + `ClusterPolicy` | Operator가 관리하는 device-plugin 방식 |
| GPU Operator 26.7 + `GPUCluster` | 신규 설치용 Operator 관리 DRA, `ClusterPolicy`와 상호 배타적 |

:::html
<style>
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="callout callout-success"><strong class="text-success">DRA 권고</strong><div class="on-surface-muted">AWS는 신규 EKS 1.34 이상에 DRA를 권고합니다.</div></div>
  <div class="callout callout-danger"><strong class="text-danger">Auto Mode는 DRA 미지원</strong><div class="on-surface-muted">Auto Mode는 GPU device plugin을 자체 관리합니다.</div></div>
  <div class="metric-card"><strong class="text-accent">확인한 버전</strong><div class="on-surface-muted">GPU Operator 26.7.0, DRA driver 0.5.0, device plugin 0.20.0</div></div>
  <div class="metric-card"><strong class="text-accent">DRA 0.5.0 요구</strong><div class="on-surface-muted">K8s 1.34.2+, driver 565+, toolkit 1.18+, CDI. Operator 관리 DRA는 driver 580+</div></div>
</div>
:::


:::notes
{timing: 2min}
[요약]
• 같은 물리 GPU를 게시하는 할당 관리자는 하나만 선택
• 신규 EKS 1.34 이상은 DRA 권고, Auto Mode는 DRA 미지원
• GPUCluster와 ClusterPolicy는 같은 클러스터에서 공존 불가
• 표의 버전은 호환성 하한이며 현재 권장 패치가 아님

GPU를 Kubernetes에 노출하는 길은 네 가지입니다. 중요한 원칙은 하나의 GPU에 할당 관리자도 하나라는 것입니다. device plugin과 DRA driver, 혹은 Operator가 같은 물리 GPU를 동시에 게시하지 않도록 노드 집합을 label로 나눕니다.
AWS는 신규 EKS 1.34 이상 배포에 DRA를 권고합니다. 단, EKS Auto Mode는 아직 DRA를 지원하지 않습니다.
{cue: pause}
숫자 몇 가지를 주의해서 읽어주세요. DRA 0.5.0은 Kubernetes 1.34.2 이상, 드라이버 565 이상, toolkit 1.18 이상이 필요하고 Operator 관리 DRA는 드라이버 580 이상입니다. 이건 호환성 하한이지 권장 버전이 아닙니다. 그리고 문서 작성 시점에 실제 GPU 실행이나 벤치마크는 수행하지 않았다고 명시되어 있습니다.

[약어]
• DRA: Dynamic Resource Allocation, ResourceClaim 기반 장치 할당
• CDI: Container Device Interface

[출처]
• D/05 "GPU마다 할당 관리자 하나 선택", 호스트 구성 조합 (확인 기준 2026-09)
:::

---
<!-- Slide 6: MIG와 time-slicing -->
@type: tabs
@title: MIG는 격리, time-slicing은 공유

## MIG는 격리, time-slicing은 공유

### MIG
MIG는 GPU를 하드웨어 기반 compute·memory 인스턴스로 나눕니다. 아래는 **A100 40 GB** profile입니다.

| Profile | 명목 메모리 | 최대 인스턴스 |
|---|---|---|
| `1g.5gb` | 5 GB | 7 |
| `2g.10gb` | 10 GB | 3 |
| `3g.20gb` | 20 GB | 2 |
| `4g.20gb` | 20 GB | 1 |
| `7g.40gb` | 40 GB | 1 |

`4g.40gb`는 A100 80 GB의 profile입니다. MIG 활성화·재구성은 GPU 워크로드를 중단할 수 있는 유지보수 작업이며, Pod 요청만 `nvidia.com/mig-1g.5gb`로 바꿔도 인스턴스가 생기지 않습니다.

### time-slicing
```yaml
# device-plugin 설정 조각 (Kubernetes 리소스가 아님)
version: v1
sharing:
  timeSlicing:
    renameByDefault: true
    failRequestsGreaterThanOne: true
    resources:
      - name: nvidia.com/gpu
        replicas: 4
```

`renameByDefault: true`이면 `nvidia.com/gpu.shared`로 게시됩니다. replica 4개는 독립 메모리 영역 4개가 아니며, replica 사이에 메모리·장애 격리가 없습니다.

### H100 vs H200
| NVIDIA 사양 | H100 **SXM** | H200 **SXM** |
|---|---|---|
| GPU 메모리 | 80 GB HBM3 | 141 GB HBM3e |
| 메모리 대역폭 | 3.35 TB/s | 4.8 TB/s |
| MIG | 최대 7개 | 최대 7개 |

공급자 사양이며 이 환경의 실측값이 아닙니다. NVL/PCIe variant는 값이 다르므로 SXM 행을 모든 H100에 일반화하지 않습니다.

:::notes
{timing: 1.5min}
[요약]
• MIG는 하드웨어 분할로 time-slicing보다 강한 격리, 단 재구성은 중단 작업
• A100 40GB와 80GB의 profile 집합이 다르므로 표를 섞지 않음
• time-slicing은 논리적 슬롯이며 메모리·장애 격리 없음
• H100/H200 수치는 SXM 사양이며 실측이 아님

MIG와 time-slicing은 "GPU를 나눠 쓴다"는 같은 목적이지만 성격이 다릅니다. MIG는 하드웨어 파티션이라 격리가 강하고, time-slicing은 여러 논리 슬롯을 게시할 뿐입니다.
MIG 탭의 표는 A100 40GB 기준입니다. 4g.40gb는 A100 80GB의 profile 집합에 속하니 두 SKU 표를 섞지 마세요.
{cue: pause}
time-slicing 탭의 replicas 4는 메모리를 4등분한다는 뜻이 아닙니다. 경합이 생기면 지연이 달라질 수 있으니 측정하셔야 합니다.
H100과 H200 비교는 NVIDIA가 공개한 SXM 사양입니다. 메모리 용량이 늘면 수용 가능한 모델이 달라질 수 있지만 실제 성능은 모델, 정밀도, 배치, interconnect에 따라 달라집니다.

[출처]
• D/05 "MIG와 time-slicing", "H100/H200 사양의 범위" (NVIDIA 공개 사양)
:::

---
<!-- Slide 7: 관측성 -->
@type: tabs
@title: hybrid 지표는 relabel로 구분

## hybrid 지표는 relabel로 구분

### ServiceMonitor
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: hybrid-node-exporter
  namespace: monitoring
  labels:
    release: kube-prom
spec:  # selector, namespaceSelector 생략
  attachMetadata:
    node: true
  endpoints:
  - port: http-metrics
    relabelings:
    - sourceLabels: [__meta_kubernetes_node_label_eks_amazonaws_com_compute_type]
      regex: hybrid
      action: keep
    - targetLabel: compute_type
      replacement: hybrid
```

### DCGM 쿼리
```promql
# GPU utilization (이미 percent)
DCGM_FI_DEV_GPU_UTIL{compute_type="hybrid"}

# GPU framebuffer 사용률: used / (used + free)
100 * DCGM_FI_DEV_FB_USED{compute_type="hybrid"} /
(DCGM_FI_DEV_FB_USED{compute_type="hybrid"} + DCGM_FI_DEV_FB_FREE{compute_type="hybrid"})
```

`node_cpu_seconds_total` 등 호스트 지표는 kubelet이 아니라 Node Exporter가 제공합니다. DCGM exporter는 별도로 설치되어 있어야 합니다.

### Container Insights
Hybrid에서는 cluster, workload, Pod, container 지표를 지원합니다. node-level 지표는 EC2 IMDS에 의존하는데 Hybrid 호스트에는 없어서 **제공되지 않습니다.** 호스트 CPU·메모리는 Node Exporter와 Prometheus로 보완합니다.

### CloudWatch agent
Pod Identity 환경에서도 Hybrid 호환을 위해 `RUN_WITH_IRSA` 변수가 필요합니다. 기존 `AmazonCloudWatchAgent`의 `spec.env` 목록에 추가하고 기존 항목은 보존합니다.

```yaml
# 기존 AmazonCloudWatchAgent.spec.env 목록에 항목 추가
- name: RUN_WITH_IRSA
  value: "True"
```

:::notes
{timing: 2min}
[요약]
• ServiceMonitor와 PodMonitor의 relabel로 compute_type=hybrid label을 부여
• 호스트 지표는 Node Exporter, GPU 지표는 DCGM exporter가 제공
• Container Insights는 Hybrid에서 node-level 지표를 제공하지 않음
• CloudWatch agent는 Pod Identity에서도 RUN_WITH_IRSA 필요

Prometheus에서는 attachMetadata.node를 켜고, node label을 기준으로 keep relabel을 걸어서 실제 hybrid 노드만 수집하고 compute_type 라벨을 붙입니다. 이 label이 있어야 Grafana에서 hybrid만 따로 볼 수 있습니다. SSM 노드 이름의 접두사로 hybrid 여부를 추측하지 않는 것이 문서의 지침입니다.
{cue: pause}
ServiceMonitor는 Prometheus 2.37 이상, PodMonitor는 2.35 이상이 필요하고, Prometheus ServiceAccount에 Node list/watch 권한이 있어야 합니다.
Container Insights는 EC2 IMDS를 쓰기 때문에 Hybrid 호스트의 node-level 지표를 얻을 수 없습니다. 이 빈칸을 Node Exporter가 채웁니다.
CloudWatch agent는 이름과 달리 Pod Identity 환경에서도 RUN_WITH_IRSA가 필요하다는 점이 헷갈리는 부분입니다. 문서의 쿼리와 YAML은 로컬 검증 수준이며 이 환경에서 수집을 실행한 결과는 아닙니다.

[출처]
• D/08 "Prometheus 메트릭 수집", "CloudWatch Observability Agent" (kube-prometheus-stack 90.0.0 기준 예시)
:::

---
<!-- Slide 8: 애드온 배치와 CoreDNS -->
@type: tabs
@title: CoreDNS는 양쪽에 최소 1개

## CoreDNS는 양쪽에 최소 1개

### 애드온 배치
| 애드온 | 이 설계의 배치 |
|---|---|
| AWS Load Balancer Controller | cloud node (webhook 접근, routable Hybrid IP target) |
| CloudWatch agent/operator | agent는 지원 노드, operator webhook은 cloud 권장 |
| cert-manager | webhook cloud 권장, routable이면 Hybrid 가능 |
| Metrics Server | cloud 또는 도달 가능한 Hybrid Pod endpoint |
| Cilium/Calico | Hybrid Node (cloud node는 VPC CNI 유지) |

### 최소 버전
호환 기준이며 설치 target 버전이 아닙니다.

| Add-on | Hybrid 호환 기준 |
|---|---|
| Node monitoring agent | 1.2.0-eksbuild.1 |
| External DNS | 0.19.0-eksbuild.1 |
| FSx CSI | 1.7.0-eksbuild.1 |
| Secrets Store provider | 2.1.1-eksbuild.1 |
| Pod Identity Agent | 1.3.3-eksbuild.1 (Bottlerocket 1.3.7-eksbuild.2) |

### CoreDNS 분산
```yaml
# CoreDNS Deployment.spec.template.spec 조각
nodeSelector:
  infrastructure.example.com/dns-eligible: "true"
topologySpreadConstraints:
- maxSkew: 1
  minDomains: 2
  topologyKey: example.com/location
  whenUnsatisfiable: DoNotSchedule
  labelSelector:
    matchLabels:
      k8s-app: kube-dns
```

적격 노드에 `location` 값 `cloud` 또는 `onprem`을 부여합니다. 한 도메인에 용량이 없으면 새 replica가 Pending일 수 있어 가용성 절충이며 failover 보장이 아닙니다.

:::notes
{timing: 1.5min}
[요약]
• 웹훅·operator류는 cloud node 배치를 권장, 모든 Pod를 cloud에 둘 필요는 없음
• 애드온 최소 버전은 호환 기준이지 설치 target이 아님
• AWS는 CoreDNS를 cloud와 Hybrid 양쪽에 각 1개 이상 권장
• minDomains 2와 DoNotSchedule은 엄격하지만 Pending 위험이 있음

애드온은 어디에 놓을지가 핵심입니다. 컨트롤 플레인이 호출하는 webhook은 Hybrid Pod CIDR에 접근할 수 없다면 cloud node에 두는 것이 안전합니다. 하지만 이것이 "모든 것을 클라우드에"라는 뜻은 아닙니다.
최소 버전 탭의 숫자는 Hybrid 호환 기준입니다. 이 버전을 설치하라는 말이 아니라 이보다 낮으면 안 된다는 하한입니다.
{cue: pause}
CoreDNS는 cloud와 Hybrid 양쪽에 최소 하나씩 두는 것을 AWS가 권장합니다. maxSkew 1만으로는 두 도메인이 생기지 않기 때문에 minDomains 2를 함께 씁니다. 단, 한쪽 용량이 없으면 Pending이 되니 DNS 해석을 실제로 시험하세요.

[출처]
• D/08 "CoreDNS 배치", "애드온별 배치 가이드"; D/01 Add-on 표
:::

---
<!-- Slide 9: 외부 트래픽 -->
@type: tabs
@title: 외부 노출은 IP target과 BGP로

## 외부 노출은 IP target과 BGP로

### ALB/NLB (IP target)
자체 관리형 AWS Load Balancer Controller는 도달 가능한 Hybrid Pod IP를 target으로 등록할 수 있습니다. ALB는 `alb.ingress.kubernetes.io/target-type: ip`, NLB는 `service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: ip`와 `loadBalancerClass: service.k8s.aws/nlb`를 사용합니다.

route, 반환 경로, security group/firewall, remote Pod network 구성이 맞아야 합니다. 컨트롤러는 cloud node에 두는 설계를 권장합니다.

```yaml
nodeSelector:
  example.com/location: cloud
```

### Cilium LB IPAM
```yaml
apiVersion: cilium.io/v2
kind: CiliumLoadBalancerIPPool
metadata:
  name: on-prem-pool
spec:
  blocks:
  - cidr: "10.90.0.0/24"
  serviceSelector:
    matchLabels:
      exposure: onprem-bgp
```

예시 CIDR은 인벤토리에서 예약한 비중복 대역으로 바꿉니다. IP 할당이 라우터 광고나 통신 성공을 보장하지는 않습니다.

### BGP 광고
```yaml
apiVersion: cilium.io/v2
kind: CiliumBGPAdvertisement
metadata:
  name: hybrid-service-advertisement
  labels:
    advertise: hybrid-services
spec:
  advertisements:
  - advertisementType: Service
    service:
      addresses: [LoadBalancerIP]
    selector:
      matchLabels:
        exposure: onprem-bgp
```

`CiliumBGPClusterConfig`, `CiliumBGPPeerConfig`와 함께 구성합니다. 세션, 수락된 라우트, next hop, 반환 경로를 확인해야 완성입니다.

### 제약
Cilium Ingress와 Gateway API는 L7 proxy가 필요합니다. 그러나 Hybrid Nodes Gateway의 필수 설정은 `vtep.enabled=true`, `l7Proxy=false`이므로 **같은 Cilium 설치에 함께 적용할 수 없습니다.** 기능을 켜기 전에 네트워크 설계를 먼저 선택합니다.

:::notes
{timing: 1.5min}
[요약]
• ALB/NLB IP target은 Hybrid Pod IP가 도달 가능해야 동작
• Cilium LB IPAM은 주소 할당, BGP는 그 주소를 광고하는 별개의 단계
• Advertisement의 selector와 Service label, peer 설정이 일치해야 함
• Cilium Ingress/Gateway API(L7 proxy)와 Hybrid Nodes Gateway(l7Proxy=false)는 같은 설치에서 충돌

외부에서 들어오는 트래픽은 두 가지 길이 있습니다. 하나는 AWS Load Balancer Controller로 ALB나 NLB를 만들고 IP target으로 Hybrid Pod를 직접 등록하는 방식입니다. 이때 Pod IP에 AWS에서 도달할 수 있어야 합니다.
다른 하나는 온프레미스에서 Cilium LB IPAM으로 주소를 할당하고 BGP로 광고하는 방식입니다. IPPool만으로는 광고가 일어나지 않고, Advertisement의 selector와 Service label, PeerConfig까지 맞아야 합니다.
{cue: pause}
마지막 탭이 함정입니다. Cilium Ingress나 Gateway API는 L7 proxy가 켜져 있어야 하는데, Hybrid Nodes Gateway는 l7Proxy=false를 요구합니다. 두 기능은 같은 Cilium 설치에서 같이 쓸 수 없으니 설계 단계에서 선택하세요.

[출처]
• D/08 "Ingress 구성", "LoadBalancer IPAM", "로드 밸런싱" (L200-282), Cilium 1.18.3 CRD 기준 예시
:::

---
<!-- Slide 10: Pod Identity 체크리스트 -->
@type: checklist
@title: Pod Identity는 6단계 체크

## Pod Identity는 6단계 체크

- [ ] (Ubuntu·RHEL·AL2023) 호스트 NodeConfig에 credentials file 활성화
  ```yaml
  spec:
    hybrid:
      enableCredentialsFile: true
  ```
- [ ] 호스트마다 계획된 `nodeadm init`을 다시 실행 (한 호스트씩 검증)
- [ ] Pod Identity Agent add-on에 Hybrid DaemonSet 활성화
  ```json
  {"daemonsets": {"hybrid": {"create": true}}}
  ```
- [ ] add-on 버전 확인: 일반 OS 1.3.3-eksbuild.1 이상. Bottlerocket은 add-on 1.3.7-eksbuild.2 + OS 1.39.0 이상이며, 1–3 대신 bootstrap 명령에 `--enable-credentials-file=true`, DaemonSet 키는 `hybrid-bottlerocket`
- [ ] `eks-auth` 서비스 경로 + 노드 역할의 `eks-auth:AssumeRoleForPodIdentity` 권한
- [ ] 워크로드별 Pod Identity association (namespace, ServiceAccount, IAM role 신뢰·권한)

:::notes
{timing: 1.5min}
[요약]
• Hybrid에서 Pod Identity는 credentials file, init 재실행, add-on 설정이 모두 필요
• Bottlerocket은 nodeadm이 아니라 OS 설정 경로를 사용
• 프라이빗 구성에는 eks-auth 엔드포인트와 AssumeRoleForPodIdentity 권한 필요
• 에이전트 설치만으로 워크로드 association이 생기지 않음

Hybrid에서 Pod Identity를 쓰려면 단계가 몇 가지 있습니다. 먼저 NodeConfig에 enableCredentialsFile을 켜고, 이미 가입한 노드도 nodeadm init을 다시 돌려야 합니다. 운영 노드를 한꺼번에 재초기화하지 말고 한 호스트씩 검증하라는 것이 문서의 지침입니다.
add-on 쪽에서는 daemonsets.hybrid.create를 true로 설정합니다. 임시 자격 증명 파일 위치는 일반 OS는 /eks-hybrid/.aws/credentials, Bottlerocket은 /var/eks-hybrid/.aws/credentials로 다릅니다.
{cue: pause}
마지막으로 많이 놓치는 부분이, 에이전트가 떠 있다고 해서 애플리케이션용 association이 자동 생성되지 않는다는 점입니다. namespace, ServiceAccount, 역할 신뢰 정책까지 확인해야 실제로 인가가 성공합니다.

[출처]
• D/08 "EKS Pod Identity Agent"; D/04 "애드온 배치와 Pod Identity" (L400-415)
:::

---
<!-- Slide 11: 망분리 1 — endpoint 세 가지 -->
@type: content
@title: 'endpoint'는 세 가지를 뜻한다

## 'endpoint'는 세 가지를 뜻한다

:::html
<style>
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="card-grid" data-reveal="stagger" data-reveal-anim="zoom">
  <div class="metric-card"><strong class="text-accent">Kubernetes API private endpoint</strong><div class="on-surface-muted">kubelet, Pod, 운영자가 TCP 443으로 접근하는 사설 진입점. control plane의 온프레미스행 연결을 없애지 않습니다.</div></div>
  <div class="metric-card"><strong class="text-accent">EKS control-plane ENI</strong><div class="on-surface-muted">API server와 VPC, remote node/Pod network 사이의 연결 지점. DLP나 망연계 장비가 아닙니다.</div></div>
  <div class="metric-card"><strong class="text-accent">interface VPC endpoint (PrivateLink)</strong><div class="on-surface-muted">eks, ssm, rolesanywhere 등 AWS 서비스 API용. kubelet 연결의 중계 서비스가 아닙니다.</div></div>
</div>
<div class="flow-v">
  <div class="callout callout-info fragment fade-right" data-fragment-index="1"><strong class="text-info">세션 A: 노드가 시작</strong> kubelet → API (TCP 443)</div>
  <div class="callout callout-warning fragment fade-right" data-fragment-index="2"><strong class="text-warning">세션 B: API server가 시작</strong> API → kubelet (TCP 10250), 사용 시 webhook 포트도 온프레미스 inbound</div>
</div>
<div class="callout callout-danger fragment zoom-in" data-fragment-index="3"><strong class="text-danger">private endpoint ≠ 망분리 준수</strong> 노드가 먼저 연결했다는 이유로 control plane발 연결이 사라지지 않습니다.</div>
:::


:::notes
{timing: 2min}
[요약]
• endpoint는 API private endpoint, 클러스터 ENI, PrivateLink 세 가지로 구분
• 세션 A는 노드 시작(443), 세션 B는 API server 시작(10250)
• com.amazonaws.region.eks endpoint는 kubelet 연결과 무관
• private endpoint를 쓴다고 망분리를 준수하는 것은 아님

보안팀과 이야기할 때 가장 먼저 정리해야 할 것이 "endpoint"라는 말입니다. Kubernetes API의 private endpoint, 클러스터 VPC에 생기는 EKS ENI, 그리고 eks나 ssm 같은 AWS 서비스용 PrivateLink는 서로 다른 것입니다. endpoint policy로 TCP 10250 연결을 통제하고 있다고 착각하면 안 됩니다.
{cue: pause}
세션 방향도 구분하세요. 노드에서 API로 가는 443은 온프레미스에서 시작합니다. 반면 logs나 exec에 쓰이는 API server에서 kubelet 10250으로의 연결은 AWS 쪽에서 시작하는 별개의 세션이고, 온프레미스 방화벽에서는 inbound입니다. 노드가 먼저 연결했다고 해서 outbound-only 터널이 되는 것은 아닙니다.
그래서 결론은 단순합니다. private endpoint를 쓰니까 망분리를 준수한다는 주장은 성립하지 않습니다. 무엇이 어떤 방향으로 허용되는지를 설명해야 합니다.

[출처]
• D/11 "Endpoint라는 말로 묶으면 안 되는 세 가지", "실제로 누가 연결을 시작하는가"
:::

---
<!-- Slide 12: 망분리 2 — 요구사항 매핑 -->
@type: tabs
@title: 망분리는 요건별로 따진다

## 망분리는 요건별로 따진다

### 요구사항 → 설계
| 고객 요구 | 이 설계의 판단 |
|---|---|
| 인터넷 비노출, 승인된 사설 관리 통신 허용 | 검토 가능한 후보 (증명 필요) |
| 물리 단절, 외부 CP와 실시간 연결 불가 | 연결 전제와 충돌 |
| 클라우드발 신규 연결 전면 금지 | kubelet·webhook 흐름과 충돌 |
| 업무 영역별 관리 주체·권한 독립 | 공통 cluster 관리자 범위 심사, 필요 시 cluster 분리 |
| K8s 객체·Secret·로그까지 온프레미스에만 | AWS control plane 구성과 충돌 가능 |

### 전송 구간 암호화
Direct Connect는 **기본적으로 전송 중 암호화를 제공하지 않습니다.** Kubernetes API·kubelet의 TLS와 인증을 유지하고, 회선 구간 암호화가 필요하면 IPsec over DX 또는 MACsec 적용 범위를 검토합니다.

MACsec은 지원 DX 연결의 링크 보호이며 종단 간 TLS와 범위가 다릅니다. Hybrid Nodes Gateway(VXLAN)도 자체 암호화가 없습니다.

### nodes/proxy RBAC
`get nodes/proxy`를 단순 조회 권한으로 분류하지 않습니다. kubelet API를 통한 컨테이너 명령 실행이 가능할 수 있고, Kubernetes audit·admission 경로를 우회할 수 있습니다.

`pods/log`, `pods/exec`, `pods/attach`, `pods/portforward`, `nodes/proxy`와 workload 생성 권한을 함께 검토합니다.

### 증빙 체크리스트
다음은 **준비할 증거 목록**이며 점검 결과가 아닙니다.

| 심사 질문 | 증거 |
|---|---|
| private-only가 실제 적용됐는가 | endpoint 설정, DNS 응답, DX 경로, 경계 flow 기록 |
| AWS에서 어디까지 접근 가능한가 | ENI/subnet, remote CIDR, route, SG·firewall 대응표 |
| 누가 어떤 API 작업을 했는가 | EKS audit 로그, CloudTrail |
| 무엇이 망을 통과했는가 | VPC Flow Logs, 방화벽 기록 |

:::notes
{timing: 2min}
[요약]
• 망분리 요구 문장을 먼저 확정한 뒤 설계 적합성을 요건별로 판단
• 완전 단절이나 클라우드발 신규 연결 전면 금지 요구와는 충돌
• DX는 기본 암호화가 없으므로 MACsec 또는 IPsec 검토
• nodes/proxy는 단순 조회 권한이 아니며 증빙은 준비 목록으로 제시

표의 첫 행처럼 "승인된 사설 경로의 관리 통신을 허용한다"는 정책이라면 검토 가능한 후보가 됩니다. 반대로 물리 단절이나 클라우드발 신규 연결 전면 금지처럼 Hybrid Nodes의 연결 전제와 충돌하는 요구도 있습니다. 이 표는 법령 해석이 아니라 기술 요구와 설계의 일치 여부를 보는 기준입니다.
{cue: pause}
암호화 탭에서, Direct Connect는 기본으로 암호화하지 않습니다. 필요하면 MACsec이나 IPsec을 검토하되, 범위가 종단 간 TLS와 다르다는 점을 설명하셔야 합니다.
RBAC 탭의 nodes/proxy는 특히 강조하고 싶습니다. 조회 권한처럼 보이지만 kubelet을 통해 명령 실행으로 이어질 수 있고 audit을 우회할 수도 있습니다.
증빙 체크리스트는 제출 전 준비 항목이지 점검이 끝났다는 뜻이 아닙니다. 실제 검증은 비운영 환경과 합성 데이터로 하시길 권합니다.

[출처]
• D/11 "망분리 요구를 설계 조건으로 바꾸기" (L73-80), "암호화와 신원·권한", nodes/proxy (L108), 증거 표 (L116-123)
:::

---
<!-- Slide 13: 규제 대응 -->
@type: content
@title: 규제 대응은 증거로 말한다

## 규제 대응은 증거로 말한다

:::html
<style>
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="callout callout-info"><strong class="text-info">AWS에 있는 것</strong><div class="on-surface-muted">Kubernetes API 객체 (Pod 사양, ConfigMap, Secret) 와 control-plane metadata. 노드 임시 자격 증명 발급도 AWS 서비스를 거칩니다.</div></div>
  <div class="callout callout-success"><strong class="text-success">온프레미스에 있는 것</strong><div class="on-surface-muted">워크로드 실행과 Pod가 처리하는 대용량 업무 데이터. 자동으로 AWS에 복제되지 않습니다.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">경계를 넘을 수 있는 것</strong><div class="on-surface-muted">앱이 출력한 logs, 허가된 exec/cp/port-forward, 애플리케이션 egress, SSM 관리 경로.</div></div>
</div>
<div class="callout callout-danger fragment zoom-in" data-fragment-index="2"><strong class="text-danger">"충족" 대신 "검토 범위와 조건"</strong> node selector나 label만으로 데이터 주권·규정 준수가 입증되지 않습니다. 업무 데이터, API 객체, 로그, 이미지, 자격 증명을 각각 분류해 저장 위치와 조회 권한을 기록합니다.</div>
:::


:::notes
{timing: 1.5min}
[요약]
• control plane의 K8s 객체는 AWS, 워크로드와 업무 데이터는 온프레미스
• Secret이나 민감 데이터를 Pod 사양·ConfigMap에 넣으면 API 객체로 AWS에서 관리됨
• logs, exec, egress, SSM 경로도 데이터 경계에 포함해 분류
• 규정 "충족"을 선언하지 않고 검토 범위와 조건을 기록

데이터 레지던시를 말할 때 정직하게 구분해야 할 것이 있습니다. Kubernetes API 객체는 AWS가 관리하는 control plane에 저장됩니다. 그래서 ConfigMap이나 Secret에 민감한 값을 넣으면 그 내용도 관리 대상 데이터가 됩니다. 반면 온프레미스 Pod가 처리하는 대용량 업무 데이터가 저절로 AWS로 복제되지는 않습니다.
{cue: pause}
그렇다고 control traffic이라서 업무 데이터가 절대 지나가지 않는다고 말하면 안 됩니다. logs는 애플리케이션이 출력한 내용을 전달하고, exec나 cp는 허가된 사용자의 데이터 접근 경로가 될 수 있습니다.
그래서 "금융권 가이드라인을 충족한다" 같은 문구는 쓰지 않습니다. 정책이 허용하는 범위와 증거가 있을 때 그 검토 범위와 조건을 함께 기록하는 방식으로 말씀하세요.

[출처]
• D/11 "데이터와 관리자 권한의 경계" (L104-110), "최종적으로 망분리 위반이 아니라는 문구" FAQ; D/README "사용 사례와 데이터 경계"
:::

---
<!-- Slide 14: 비용 모델 -->
@type: content
@title: 비용은 vCPU-hour 구간 과금

## 비용은 vCPU-hour 구간 과금

::::left
| 월 사용량 구간 (vCPU-hour) | 요금 |
|---|---|
| 처음 576,000 | $0.020 |
| 다음 576,000 | $0.014 |
| 다음 4,608,000 | $0.010 |
| 다음 5,760,000 | $0.008 |
| 11,520,000 초과 | $0.006 |
::::

::::right
| 노드 | 월 vCPU-h | 연환산 노드 요금 | + 클러스터 1개 |
|---|---|---|---|
| 10 | 233,600 | $56,064 | $56,940 |
| 50 | 1,168,000 | $236,928 | $237,804 |
| 100 | 2,336,000 | $377,088 | $377,964 |
::::

가정: 노드당 32 vCPU, 월 730시간, 같은 월을 12번 반복, 표준 지원 클러스터 1개($0.10/시간) 포함. 청구서나 실측이 아닌 계산 모델입니다.

:::html
<style>
.text-info { color: var(--info); font-weight: var(--weight-bold); }
</style>
<div class="callout callout-info fragment zoom-in" data-fragment-index="1"><strong class="text-info">경쟁 솔루션 비교는 의도적으로 싣지 않았습니다</strong> 출처를 확인하지 못한 과거 추정치는 폐기했습니다. 하드웨어, 전력, OS 구독, 인력, 이전 비용이 포함된 자체 TCO 모델로 비교하세요.</div>
:::


:::notes
{timing: 2min}
[요약]
• 과금은 노드가 보고한 vCPU-hour 기준의 월별 구간 요금
• 노드가 조인된 시점부터 제거 시까지 과금되며 idle이어도 계속됨
• 표는 32 vCPU·730시간 가정의 계산 모델이지 청구서가 아님
• 경쟁 솔루션 수치는 출처 불명이라 의도적으로 제외

요금은 노드가 보고한 vCPU-hour에 대한 월별 구간 요금입니다. 처음 576,000 vCPU-hour는 0.020달러, 이후 구간이 내려가는 구조이고 모든 사용량에 고정 0.01달러가 붙는 것이 아닙니다. 하이퍼스레딩된 코어는 vCPU 2개로 보고될 수 있고, 머신당 32 vCPU를 넘으면 account team과 상의하라고 안내되어 있습니다.
{cue: pause}
오른쪽 표는 문서의 계산 모델입니다. 50노드를 예로 검증해 보면 1,168,000 vCPU-hour에서 첫 576,000은 0.020, 다음 576,000은 0.014, 남은 16,000은 0.010이라 월 19,744달러가 되고, 열두 번 반복한 연환산이 236,928달러입니다. 여기에 클러스터 요금 876달러를 더하면 237,804달러입니다.
다른 서비스, 할인, 세금, 하드웨어, 전력, OS 구독, 인력은 모두 제외된 숫자입니다. 그래서 경쟁 솔루션과의 비교표는 일부러 빼고, 여러분 조직의 TCO 모델에 이 숫자를 넣으시라고 권합니다.

[출처]
• D/09 비용 계산 모델 (L40-53), EKS pricing https://aws.amazon.com/eks/pricing/ (확인일 2026-09-16)
:::

---
<!-- Slide 15: 도입 판단 -->
@type: content
@title: 도입 판단은 제약 확인부터

## 도입 판단은 제약 확인부터

:::html
<style>
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="card-grid fragment" data-reveal="stagger" data-reveal-pace="slow" data-fragment-index="1">
  <div class="callout callout-success"><strong class="text-success">Hybrid Nodes가 맞는 신호</strong><div class="on-surface-muted">온프레미스 GPU, 대규모 로컬 데이터, edge 처리, 기존 하드웨어 활용. AWS와 안정적인 사설 양방향 연결을 유지할 수 있는 경우.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">먼저 확인할 제약</strong><div class="on-surface-muted">IPv4만 지원. 간헐적·단절(DDIL) 환경용이 아님. GovCloud(US)와 중국 리전 제외. OS·아키텍처·CNI 조합 확인.</div></div>
  <div class="callout callout-danger"><strong class="text-danger">맞지 않는 경우</strong><div class="on-surface-muted">완전 단절이 필요하거나 클라우드발 신규 연결이 전면 금지된 정책. AWS Region, Local Zone, Outposts, 타사 클라우드를 hybrid 인프라로 쓰는 것은 미지원.</div></div>
  <div class="callout callout-info"><strong class="text-info">운영 책임</strong><div class="on-surface-muted">Control plane은 AWS가 관리하지만 host, OS, 연결, workload 운영은 계속 사용자 책임입니다.</div></div>
</div>
<div class="callout callout-info fragment fade-up" data-fragment-index="2"><strong class="text-info">대안과의 비교</strong> 동등한 가용성·지원 범위로 자체 TCO 모델을 만들어 비교하세요. 이 자료는 특정 대안의 우열을 주장하지 않습니다.</div>
:::


:::notes
{timing: 1.5min}
[요약]
• 온프레미스 GPU, 로컬 데이터, edge가 대표적인 선택 이유
• 사설 양방향 연결 필요, IPv4 전용, DDIL 용도 아님
• 완전 단절이나 클라우드발 연결 금지 정책과는 충돌
• 대안 비교는 조직의 TCO 기준으로, 이 자료는 우열을 주장하지 않음

도입 판단은 장점 나열보다 제약 확인에서 시작하는 것이 안전합니다. 문서가 꼽는 선택 이유는 온프레미스 GPU, 대규모 로컬 데이터, edge 처리, 기존 하드웨어입니다. 다만 data locality에는 애플리케이션, 스토리지, egress, 로깅 통제도 함께 필요합니다.
{cue: pause}
반대로 IPv4만 지원하고, AWS와의 안정적인 사설 양방향 연결이 필수이며, 단절·간헐 연결 환경용이 아닙니다. AWS Region이나 Outposts 같은 AWS 인프라를 hybrid 노드로 등록하는 것도 지원 대상이 아닙니다.
대안과의 비교는 일부러 숫자를 싣지 않았습니다. 동등한 가용성과 지원 범위로 직접 계산하시기 바랍니다.
{cue: transition}
이제 네 블록 전체를 정리하겠습니다.

[출처]
• D/README "계획에 반영할 제약", "사용 사례와 데이터 경계"; D/09 TCO 고려 사항
:::

---
<!-- Slide 16: 핵심 요약 -->
@type: content
@title: 핵심 요약: 4개 블록, 6가지

## 핵심 요약: 4개 블록, 6가지

:::html
<style>
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="card-grid fragment" data-reveal="stagger" data-reveal-anim="zoom" data-reveal-pace="slow" data-fragment-index="1">
  <div class="metric-card"><strong class="text-accent">1. 구조와 전제</strong><div class="on-surface-muted">AWS가 control plane을, 사용자가 host·연결·workload를 운영합니다. AWS와의 사설 양방향 연결이 필수입니다.</div></div>
  <div class="metric-card"><strong class="text-accent">2. 네트워크</strong><div class="on-surface-muted">kubelet 10250과 webhook은 AWS에서 시작하는 inbound입니다. Gateway는 선택이며 직접 라우팅도 유효합니다.</div></div>
  <div class="metric-card"><strong class="text-accent">3. 라이프사이클</strong><div class="on-surface-muted">nodeadm으로 설치·join·업그레이드합니다. rollback 명령이 없으므로 업그레이드·복구 모두 in-place보다 호스트 교체를 우선합니다.</div></div>
  <div class="metric-card"><strong class="text-success">4. 워크로드 배치</strong><div class="on-surface-muted">compute-type label로 배치하고, 버스팅은 Pending Pod가 트리거하며 자동 복귀는 없습니다.</div></div>
  <div class="metric-card"><strong class="text-success">5. GPU와 관측성</strong><div class="on-surface-muted">GPU마다 할당 관리자는 하나, 신규 1.34 이상은 DRA 권고. hybrid 지표는 relabel로 구분합니다.</div></div>
  <div class="metric-card"><strong class="text-warning">6. 보안과 비용</strong><div class="on-surface-muted">private endpoint는 망분리 준수의 증거가 아닙니다. 비용은 보고된 vCPU-hour 구간 과금입니다.</div></div>
</div>
:::


:::notes
{timing: 1.5min}
[요약]
• 구조: AWS control plane + 사용자 운영 host, 사설 양방향 연결 필수
• 네트워크: 세션 방향과 포트를 설명할 수 있어야 함
• 라이프사이클: nodeadm, 호스트 교체 우선
• 배치·GPU·관측성·보안·비용은 각각 "보장하지 않는 것"까지 기억

네 개 블록을 여섯 가지로 압축했습니다. 첫째, Hybrid Nodes는 AWS 관리형 control plane에 사용자가 운영하는 노드를 붙이는 구조이고 연결이 끊기는 환경용이 아닙니다.
둘째, 네트워크에서는 세션 방향을 설명할 수 있어야 합니다. 셋째, nodeadm으로 노드를 다루되 in-place 업그레이드를 롤백 수단으로 보지 않습니다.
넷째에서 여섯째가 이번 블록 내용입니다. 배치는 label과 affinity, 버스팅은 Pending 트리거, GPU는 할당 관리자 하나, 보안은 private endpoint가 곧 준수는 아니라는 것, 비용은 구간 과금이라는 점입니다.
{cue: transition}
간단한 퀴즈로 확인해 보겠습니다.
:::

---
<!-- Slide 17: Quiz 1/2 -->
@type: quiz
@title: Knowledge Check 1

## Knowledge Check (1/2)

**Q1: Karpenter 클라우드 버스팅의 트리거는 무엇인가요?**
- [ ] 온프레미스 CPU 사용률이 임계값을 넘을 때
- [x] 조건에 맞는 Pod가 Pending일 때
- [ ] 온프레미스 용량이 돌아왔을 때

**Q2: 하나의 물리 GPU에 대한 설명으로 맞는 것은?**
- [ ] device plugin과 DRA driver를 함께 설치한다
- [x] 할당 관리자(device plugin, DRA, GPU Operator)는 하나만 선택한다
- [ ] time-slicing replica는 메모리를 독립적으로 보장한다

:::notes
{timing: 1.5min}
[요약]
• Q1 Pending Pod가 버스팅 트리거
• Q2 GPU마다 할당 관리자는 하나
• 오답이면 슬라이드 3, 5로 돌아가 확인

두 문제를 먼저 풀어보겠습니다. 이번 블록에서 오해하기 쉬운 지점에서 냈습니다.
{cue: poll}
1번은 Pending Pod, 2번은 할당 관리자 하나입니다. 온프레미스 CPU 사용률 같은 임계값은 트리거가 아니고, time-slicing replica는 메모리 격리를 보장하지 않습니다.
:::

---
<!-- Slide 18: Quiz 2/2 -->
@type: quiz
@title: Knowledge Check 2

## Knowledge Check (2/2)

**Q3: pod-deletion-cost에 대한 설명으로 맞는 것은?**
- [ ] 값이 큰 Pod는 절대 삭제되지 않는다
- [x] best-effort 선호도이며 할당·단계·Ready 여부가 먼저 비교된다
- [ ] CREATE 시점 webhook으로 신뢰성 있게 부여할 수 있다

**Q4: "private endpoint를 쓰므로 망분리를 준수한다"는 주장은?**
- [ ] 맞다. 모든 통신이 사설 주소를 쓰기 때문이다
- [x] 성립하지 않는다. 세션 방향·권한·데이터 경계의 증거가 필요하다
- [ ] 맞다. DX가 기본 암호화를 제공하기 때문이다

:::notes
{timing: 1.5min}
[요약]
• Q3 deletion cost는 best-effort이고 앞선 비교 기준이 있음
• Q4 private endpoint는 망분리 준수의 증거가 아님
• DX는 기본 암호화가 없음

3번은 deletion cost가 네 번째 비교 기준이라는 점, 4번은 private endpoint와 망분리 준수가 다른 이야기라는 점입니다. Direct Connect는 기본 암호화를 제공하지 않으므로 세 번째 보기도 틀립니다.
{cue: pause}
틀린 문항은 슬라이드 4와 11을 다시 확인하세요.
:::

---
<!-- Slide 19: References + Q&A -->
@type: content
@title: 참고 자료 & Q&A

## 참고 자료 & Q&A

:::html
<style>
.text-accent { color: var(--accent); font-weight: var(--weight-bold); }
.text-info   { color: var(--info);   font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="card-grid" data-reveal="static">
  <div class="metric-card"><strong class="text-accent">AWS 공식 문서</strong><div class="on-surface-muted">docs.aws.amazon.com/eks/latest/userguide/<br>hybrid-nodes-overview.html<br>hybrid-nodes-networking.html<br>hybrid-nodes-add-ons.html<br>hybrid-nodes-webhooks.html<br>hybrid-nodes-gateway-cni.html</div></div>
  <div class="metric-card"><strong class="text-accent">GPU</strong><div class="on-surface-muted">docs.aws.amazon.com/eks/latest/userguide/<br>device-management-nvidia.html<br>NVIDIA GPU Operator 문서 (platform-support)</div></div>
  <div class="metric-card"><strong class="text-accent">비용·스케줄링</strong><div class="on-surface-muted">aws.amazon.com/eks/pricing/<br>karpenter.sh/docs/upgrading/compatibility/<br>kubernetes.io ReplicaSet pod-deletion-cost</div></div>
</div>
<div class="callout callout-info fragment zoom-in" data-fragment-index="1"><strong class="text-info">Q&A</strong> 이 자료의 예제는 검토 기준(EKS 1.36, nodeadm 1.0.20)이며 대부분 실제 클러스터에서 실행한 결과가 아닙니다. 적용 전 최신 AWS 문서로 지원 조합을 확인하세요.</div>
:::


:::notes
{timing: 1min}
[요약]
• 버전·가격·한도는 모두 공식 문서로 재확인 필요
• 예제는 로컬 검증 수준이며 운영 실행 결과가 아님
• 질문은 배치, GPU, 보안 검토, 비용 순으로 받음

참고 자료는 AWS 공식 문서와 NVIDIA, Karpenter, Kubernetes 문서입니다. 오늘 보여드린 버전과 가격은 2026년 9월 기준 검토 자료이므로 적용 전에 다시 확인해 주세요. 문서 스스로도 많은 예제를 실제 클러스터에서 실행하지 않았다고 밝히고 있습니다.
{cue: question}
질문 있으시면 말씀해 주세요. 배치, GPU, 망분리 검토, 비용 중 어디부터 이야기할까요?

[출처]
• D/README 지원 버전·검토 범위, 각 D 문서의 "공식 참고 자료"
:::

---
<!-- Slide 20: Thank You -->
@type: thankyou
@toc: toc.html
@message: 운영·워크로드·보안 & 전략 — 감사합니다

# Thank You

:::notes
{timing: 0.5min}
[요약]
• 4개 블록 전체 마무리
• 목차로 돌아가 필요한 블록을 다시 확인

오늘 세션 들어주셔서 감사합니다. 필요한 부분은 목차로 돌아가 다시 확인하시기 바랍니다.
:::
