---
marp: true
title: "Block 2: 노드 라이프사이클 & 모니터링"
theme: default
paginate: true
---

<!-- block: node-lifecycle -->

<!-- type: title -->

# 노드가 바뀌는 이유는 다릅니다

**Block 2 · 먼저 종료 원인과 앱 영향을 나눠 봅니다.**

| 이름 | 쉬운 설명 |
|---|---|
| Consolidation | Pod를 재배치하고 불필요한 노드 정리 |
| Drift | 새 설정을 반영하기 위해 노드 교체 |
| Expiration | expireAfter에 도달해 교체 시작 |
| Spot interruption | EC2가 Spot 용량 회수 |

**진단 순서:** 앱 영향 → 노드 준비 상태 → 이벤트의 원인.

[최신 버전·공식 출처](version-update.md)

<!-- notes: {timing: 2min} [요약] 노드가 바뀌면 먼저 이유를 네 가지로 분류합니다. Consolidation은 재배치 후 정리, Drift는 새 설정 적용, Expiration은 설정한 수명 만료, Spot은 인스턴스 회수입니다. 이름만 외우지 말고 앱이 영향을 받았는지와 이벤트를 함께 확인합니다. 모든 종료를 CPU 사용량이나 Spot 탓으로 단정하지 않게 안내하세요. {cue: transition} 대시보드를 본 뒤 Pod·NodeClaim·이벤트 순서로 확인합니다. -->

---

<!-- type: canvas -->

# 예약량과 실제 사용량을 구분합니다

**Requests = 스케줄링 예약 · Usage = 실제 사용량**

표의 수치와 임계값은 교육용 예시입니다. 실제 Karpenter는 특정 CPU 사용률 하나로 노드 삭제를 결정하지 않습니다.

학습용 대시보드:
- HTML로 읽는 요약: Active Nodes, Ready, CPU Requests avg, CPU Usage avg, Cost/hr. 금액은 교육용 예시입니다.
- Canvas는 Requests와 Usage의 시계열 차트 한 개만 표시
- HTML 표로 읽는 노드 상태·용량 유형·Requests·Usage
- 최근 이벤트 세 개만 표시하는 HTML 목록
- **버튼:**
  - "노드 추가": 빈 슬롯에 새 노드 프로비저닝
  - "워크로드 추가": Ready 노드들의 CPU Requests/Usage 증가
  - "워크로드 삭제": 1-2개 랜덤 노드에서 Pods 제거 (20-40% Requests 감소) → Consolidation 대상 생성
  - "Spot 인터럽트": 직접 설치한 Karpenter의 EventBridge→SQS→Controller 흐름 (Auto Mode는 AWS 관리) — Cordon→PDB→Drain→Reschedule→Terminate
  - "Consolidation": Low Req 노드 Cordon→Drain→Redistribute→Remove
  - "Reset": 초기 상태 복원

<!-- notes: {timing: 2min} [요약] Requests는 스케줄링 예약량, Usage는 실제 사용량입니다. 여러 작은 노드 그림 대신 표에서 두 열을 비교합니다. 요약 지표와 최근 이벤트를 HTML로 읽고, Canvas에서는 추세만 봅니다. 수치와 비용은 교육용 시뮬레이션입니다. 실제 Karpenter는 요청량·배치 조건·비용·PDB·예산을 함께 고려합니다. 워크로드 추가와 삭제 버튼으로 값이 변하는 것을 보여주세요. {cue: transition} 이상을 발견하면 Pod→노드→이벤트 순서로 확인합니다. -->

---

<!-- type: code -->

# Pod → 노드 → 이벤트 순서로 봅니다

### 1. 앱 상태 — Pod가 어디서 멈췄나요?

```bash
kubectl get pods -A --field-selector=status.phase=Pending
kubectl describe pod <pod> -n <namespace>
```

Events에 FailedScheduling이 있으면 CPU·메모리 요청량, taint, 배치 조건부터 확인합니다. 이미 노드에 배치됐다면 이미지 다운로드·볼륨·앱 시작 문제도 확인합니다. Pending이 곧 노드 부족은 아닙니다.

### 2. 노드 상태 — 요청한 노드가 준비됐나요?

```bash
kubectl get nodepools
kubectl get nodeclaims -o wide
kubectl describe nodeclaim <nodeclaim>
```

NodeClaim의 Conditions·Events에서 생성, 등록, 준비 단계가 어디까지 진행됐는지 확인합니다. NodePool·NodeClass 조건이 맞는지, IAM·subnet·EC2 용량에 문제가 있는지 이벤트를 보고 좁힙니다.

### 3. 교체 원인 — 무슨 이유로 바뀌었나요?

```bash
kubectl get events -A \
  --field-selector involvedObject.kind=NodeClaim \
  --sort-by='.lastTimestamp'
```

같은 노드·같은 시간의 교체 이벤트를 앱 장애 시각과 비교합니다. NodeClaim 이벤트만으로 부족하면 관련 Node·Pod 이벤트도 확인합니다. 종료 원인은 메트릭 하나로 단정하지 않습니다.

<!-- notes: {timing: 3min} [요약] Pod → NodeClaim → 이벤트 순서로 원인을 좁힙니다. 첫 탭에서는 Pending과 FailedScheduling을 구분하고, 두 번째는 노드 요청의 생성·등록·Ready 상태, 세 번째는 교체 시각과 이유를 봅니다. 결과를 먼저 보지 않고 인스턴스 수부터 늘리면 다른 원인을 놓칠 수 있습니다. 명령어를 외우기보다 오른쪽의 무엇을 읽어야 하는지를 먼저 설명하세요. {cue: transition} 반복해서 볼 질문을 대시보드로 옮겨봅니다. -->

---

<!-- type: code -->

# 필요할 때 노드 라벨을 더 확인합니다

```bash
kubectl get nodes -L karpenter.sh/nodepool,karpenter.sh/capacity-type
```

어느 NodePool 소속인지, Spot인지 On-Demand인지 확인합니다. 기본 general-purpose는 On-Demand이며 Spot은 커스텀 풀에서 구성합니다. HTML에서는 진단 탭을 먼저 보고 이 명령은 추가 참고로 사용합니다.

<!-- notes: {timing: 1min} [요약] 라벨은 노드를 묶어서 보는 기준입니다. 종료 이유 자체를 증명하지는 않습니다. {cue: transition} 이 분류를 메트릭 집계에도 사용할 수 있습니다. -->

---

<!-- type: tabs -->

# 대시보드는 질문에 답하게 만듭니다

**공통: kube-state-metrics / Pod 시작 P99: 직접 설치한 Karpenter**

NodePool·Spot 쿼리에는 node 라벨 allowlist가 필요합니다. [설정 전제](version-update.md#메트릭-예제의-전제)를 확인하세요. 아래 표시 수치는 설명용 예시입니다.

### 노드 수가 바뀌었나?

```promql
count by (label_karpenter_sh_nodepool) (kube_node_labels{label_karpenter_sh_nodepool!=""})
```

NodePool별 노드 수. 예: workload 8개, system 2개.

### 앱이 기다리나?

```promql
sum(kube_pod_status_phase{phase="Pending"})
```

Pending Pod 전체 개수이며 Unschedulable과 동일하지 않습니다. 알림 예: 10개 초과가 5분 지속.

### Spot 의존도는?

```promql
(count(kube_node_labels{label_karpenter_sh_capacity_type="spot"}) or vector(0)) / count(kube_node_labels{label_karpenter_sh_nodepool!=""}) * 100
```

Pod 개수가 아닌 NodePool 소속 **노드 수**를 기준으로 계산합니다.

### 시작이 느린가? (직접 설치한 Karpenter)

```promql
max(karpenter_pods_startup_duration_seconds{quantile="0.99"})
```

Controller 메트릭 수집이 필요합니다. Summary 타입이라 `_bucket` 대신 `quantile` label로 조회합니다. Pod 시작 시간이며 Node Ready 시간과 동일하지 않습니다. Auto Mode에서 동일 endpoint를 가정하지 않습니다.

<!-- notes: 앞의 세 쿼리는 kube-state-metrics를 사용합니다. Node 라벨 allowlist와 복수 클러스터 수집 시 cluster 필터를 준비합니다. 마지막 쿼리는 직접 설치한 Karpenter의 Pod 시작 시간 Summary에서 quantile="0.99" 값을 읽습니다. -->

---

<!-- type: timeline -->

# Spot 회수 통지가 오면?

**Pod 종료 처리와 대체 노드 준비를 함께 시작합니다.**

| 단계 | 기존 Spot 노드 | 대체 용량과 앱 |
|---|---|---|
| 1. 평상시 | 앱 실행 중 | 추가 요청 없음 |
| 2. 회수 통지 | 종료 기한 확인 | 통지를 받아 대응 시작 |
| 3. 동시에 대응 | 새 배치를 막고 PDB를 확인하며 drain | drain과 병행해 대체 노드 준비 |
| 4. 결과 확인 | 기존 노드 종료 | 제때 준비되면 새 Pod Ready, 늦으면 Pending·시작 대기 가능 |

HTML에서는 네 단계 버튼 또는 ↑ ↓로 이동합니다. **용량·앱 준비가 제때 완료 / 준비가 늦어짐**을 선택해 결과를 비교합니다.

통지 경로는 상세 설명으로 접어 둡니다. 직접 설치한 Karpenter는 **EC2 → EventBridge → SQS → Controller**이며 interruption queue 구성이 필요합니다. Auto Mode는 AWS가 관리합니다.

이 예시는 stop/terminate 회수 통지입니다. 통상 2분 전 알림이지만 노드와 앱의 준비 완료를 보장하지 않습니다. hibernate는 같은 2분 유예 없이 시작됩니다. **PDB는 EC2 회수 기한을 늘리지 못합니다.**

[공식 근거와 적용 범위](version-update.md#spot-회수와-여유-용량을-읽는-기준)

<!-- notes: {timing: 3min} [요약] Spot 회수 대응은 종료 처리와 대체 용량 준비가 겹쳐 진행됩니다. 3단계에서 두 영역을 함께 짚으세요. 직접 설치한 Karpenter는 interruption queue 구성이 필요하며 Auto Mode는 AWS가 관리합니다. 4단계에서 준비 지연을 선택해 Pending이 남을 수 있음을 보여줍니다. 앱은 기존 프로세스가 이동하는 대신 새 Pod로 다시 실행됩니다. PDB와 NodePool 예산으로 EC2 회수를 취소할 수 없습니다. {cue: transition} 노드 대기를 줄이려면 여유 자리를 미리 준비할 수 있습니다. -->

---

<!-- type: compare -->

# 여유 자리를 미리 준비하면?

**버퍼 용량은 노드 대기를 줄이지만, 그만큼 비용이 듭니다.**

### 동작 흐름

| Phase | 단계 | 설명 |
|-------|------|------|
| Phase 1 | **미리 자리 확보** | 낮은 우선순위 더미 Pod가 예약 (PriorityClass: -1) |
| Phase 2 | **실제 앱이 자리 사용** | 우선순위와 배치 조건이 맞으면 더미 Pod를 축출하고 배치 |
| Phase 3 | **여유 자리 다시 확보** | 이 예시는 기존 노드에 여유가 없어 새 노드를 준비. 더미 두 개는 서로 다른 노드에 배치 |

**먼저 이해하기 / PriorityClass / Deployment** 탭으로 개념과 YAML을 나눕니다. 단계 버튼은 앞뒤로 이동하고, 처음부터 버튼은 예약 상태로 되돌립니다.

- 이 예시는 더미 Pod 방식입니다. Spot뿐 아니라 On-Demand 용량에도 적용할 수 있습니다.
- 직접 설치한 Karpenter **v1.14**에서는 **Capacity Buffers API가 v1beta1로 승격**됐습니다. 별도 방식이며 Controller와 CRD 업데이트를 함께 확인합니다. Auto Mode 지원을 의미하지 않습니다.
- 노드가 있어도 이미지 다운로드·앱 초기화는 필요합니다. 버퍼 자체가 Spot이면 함께 회수될 수도 있습니다.

[최신 기능의 적용 범위](version-update.md#spot-회수와-여유-용량을-읽는-기준)

### PriorityClass YAML

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: overprovisioning
value: -1              # 기본값 0보다 낮은 우선순위
globalDefault: false
description: "Overprovisioning placeholder pods"
```

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: overprovisioning
spec:
  replicas: 2
  selector:
    matchLabels:
      app: overprovisioning
  template:
    metadata:
      labels:
        app: overprovisioning
    spec:
      priorityClassName: overprovisioning
      terminationGracePeriodSeconds: 0
      affinity:
        podAntiAffinity:       # 같은 노드 배치 방지
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: overprovisioning
            topologyKey: kubernetes.io/hostname
      containers:
      - name: pause
        image: registry.k8s.io/pause:3.9
        resources:
          requests:
            cpu: "1"
            memory: "2Gi"
```

> **핵심 원리:** `value: -1` → 기본값 0보다 낮은 우선순위. 더 높은 우선순위 Pod가 필요하면 Dummy Pod를 축출(Preemption)할 수 있습니다. 배치 조건이 맞을 때 노드 대기를 줄입니다.

<!-- notes: {timing: 3min} [요약] 버퍼는 앱에 내줄 여유 용량이며 유지 비용이 듭니다. 더미보다 앱의 우선순위가 높고 배치 조건이 맞아야 선점할 수 있습니다. 세 버튼으로 자리 확보, 앱 배치, 버퍼 복원을 보여줍니다. 기존 노드에 남은 자리가 없다는 예시이며 required podAntiAffinity 때문에 복원된 더미 두 개는 서로 다른 노드에 둡니다. v1.14 Capacity Buffers API는 직접 설치 환경의 별도 방식으로 구분합니다. {cue: transition} 이제 여유 용량과 별개인 노드 수명을 봅니다. -->

---

<!-- type: compare -->

# 14일·24시간·21일은 서로 다릅니다

| 숫자 | 의미 |
|---|---|
| 14일(336h) | Auto Mode 기본 expireAfter. 교체를 시작할 시점 |
| 24시간 | terminationGracePeriod 미지정 시 기본값. 노드 종료 시작 후 유예 |
| 21일 | Auto Mode 노드의 최대 수명. 앞의 두 숫자를 더한 값이 아님 |

**선택해 보기:** 1일(짧은 주기), 7일(사용자 정책), 14일(기본값).

Drift·Spot·노드 정리로 더 일찍 교체될 수 있습니다. PDB와 교체 예산은 모든 종료를 막지 못합니다.

### 펼쳐 보는 전체 YAML

default NodeClass가 존재하는 환경의 커스텀 풀 예제입니다.

```yaml
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
        name: default
      expireAfter: 336h
      terminationGracePeriod: 24h
  disruption:
    consolidationPolicy: Balanced
    consolidateAfter: 1m
```

<!-- notes: {timing: 3min} [요약] 14일은 기본 만료 설정, 24시간은 노드 종료 시작 후 기본 유예, 21일은 서비스의 최대 수명입니다. 세 값을 더해서 교체 일정을 계산하지 않습니다. 세 정책 버튼을 눌러 expireAfter만 바뀌는 것을 확인하세요. 7일을 모든 프로덕션의 권장값으로 설명하지 않습니다. 전체 YAML은 질문이 있을 때 펼치고 spec.template.spec 위치만 짚습니다. {cue: transition} 만료 전에 노드가 바뀌는 대표 사례인 Drift를 봅니다. -->

---

<!-- type: timeline -->

# Drift: 새 설정을 새 노드에 반영합니다

1. 현재 노드는 AMI rev A (교육용 표기)
2. 원하는 설정이 AMI rev B로 바뀌어 Drift 감지
3. 새 노드 준비
4. Pod 이동
5. 이전 노드 종료

**AWS는 관리형 AMI를 준비하고, 팀은 Pod 이동 영향을 설계합니다.**

그림에서는 Pod 하나씩 그리는 대신 노드별 **Pod 개수**를 표시합니다. 단계 버튼을 누르면 이전 노드의 수가 줄고 새 노드의 수가 늘어나는 것을 확인합니다.

- PDB: 동시에 중단할 Pod 제한
- NodePool 예산: 동시에 교체할 노드 제한
- FHD·4K에서 같은 비율로 표시되는 단계형 Canvas. 각 단계 버튼으로 앞뒤 이동

<!-- notes: {timing: 3min} [요약] Drift는 원하는 설정과 기존 노드의 차이를 반영하는 교체 과정입니다. rev A/B는 실제 Kubernetes 버전이 아닌 교육용 AMI 구분입니다. 초기→감지→새 노드→Pod 이동→완료 순서로 시연하세요. AWS가 AMI를 관리하는 것과 팀이 앱의 중단 영향을 설계하는 일을 구분합니다. {cue: transition} 이 상태를 알림으로 연결합니다. -->

---

<!-- type: compare -->

# OS 선택이 필요하면 운영 방식을 다시 봅니다

Auto Mode의 AMI는 AWS가 관리합니다. AMI를 직접 선택해야 하는 요구가 있다면 직접 설치한 Karpenter/MNG 등 다른 운영 방식을 검토합니다. 이 비교는 Block 1의 운영 책임 탭에서 다룹니다.

<!-- notes: {timing: 0.5min} [요약] Auto Mode 운영 설명에 직접 설치 환경의 OS 선택 예제를 섞지 않습니다. {cue: transition} 노드 상태를 관측하는 방법으로 돌아갑니다. -->

---

<!-- type: code -->

# AlertManager 알림 규칙

**kube-state-metrics 기반 공통 노드·Pod 알림**

Prometheus Operator의 PrometheusRule CRD와 kube-state-metrics 수집을 전제로 합니다. 임계값은 예시입니다. 복수 클러스터는 cluster 필터를 추가합니다. Spot 원인은 NodeClaim 이벤트와 함께 조사합니다.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: node-alerts
spec:
  groups:
  - name: nodes
    rules:
    - alert: HighPendingPods
      expr: sum(kube_pod_status_phase{phase="Pending"}) > 10
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "{{ $value }} pods pending"

    - alert: KubeNodeNotReady
      expr: kube_node_status_condition{condition="Ready",status="true"} == 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Node is not Ready"

    - alert: UnschedulablePods
      expr: sum(kube_pod_status_unschedulable) > 0
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Pods cannot be scheduled"

    - alert: NodeAgeExceeded
      expr: time() - kube_node_created > 1209600
      labels:
        severity: info
      annotations:
        summary: "Node older than 14 days; inspect replacement"

    - alert: HighCPURequests
      expr: (sum(kube_pod_container_resource_requests{resource="cpu"}) / sum(kube_node_status_allocatable{resource="cpu"})) > 0.7
      for: 1h
      labels:
        severity: info
      annotations:
        summary: "CPU requests exceed 70% of allocatable"
```

<!-- notes: 없는 Karpenter 메트릭이나 termination counter의 가정한 reason 라벨을 사용하지 않습니다. NotReady와 Unschedulable은 증상이며 프로비저닝 실패나 Spot 중단 원인을 단정하지 않습니다. HighCPURequests는 CPU 예약 비율로 실제 CPU 사용률이나 낭비를 의미하지 않습니다. -->

---

<!-- type: checklist -->

# Day-2 운영 체크리스트

**EKS Auto Mode 운영 준비 상태 점검**

### Disruption & 안정성

- [ ] Disruption Budget 설정 완료
- [ ] PodDisruptionBudget 적용
- [ ] Spot 중단 관련 이벤트 확인
- [ ] expireAfter 정책 설정
- [ ] 노드 모니터링 대시보드 구축

### 최적화 & 비용

- [ ] AWS 관리 AMI 교체 상태 확인
- [ ] 비용 태깅 (CostCenter, Team)
- [ ] Multi-AZ 배포 확인
- [ ] Topology Spread Constraints 적용
- [ ] 정기 비용 리뷰 스케줄

> **Tip:** 체크리스트 항목을 점검 후 프로덕션 배포를 진행하세요.

<!-- notes: 프로덕션 배포 전 모든 체크리스트 항목을 확인합니다. -->

---

<!-- type: quiz -->

# 장애 상황에서 무엇부터 볼까요?

한 상황씩 탭으로 열고 선택 후 해설을 읽습니다. **다시 풀기**로 재도전할 수 있습니다.

### Pending Pod가 보입니다. 가장 먼저 할 일은?

- [ ] 바로 노드를 늘린다
- [x] Pod Events에서 FailedScheduling 여부와 이유를 확인한다
- [ ] CPU 사용량이 낮은 노드를 삭제한다

**해설:** Pending에는 이미 배치된 Pod의 시작 대기도 포함됩니다. Pod → NodeClaim → 이벤트 순서로 원인을 좁힙니다.

### expireAfter가 14일이면 그동안 노드가 유지될까요?

- [x] Drift·Spot·노드 정리로 더 일찍 바뀔 수 있다
- [ ] 반드시 14일 동안 유지된다
- [ ] PDB가 있으면 영구 유지된다

**해설:** expireAfter는 최소 유지 시간의 보장이 아닙니다. 만료 전에 다른 이유로 교체될 수 있습니다.

### Spot 회수 통지가 왔습니다. PDB가 해주는 일은?

- [ ] EC2의 인스턴스 회수를 취소한다
- [ ] Spot 인스턴스를 On-Demand로 바꾼다
- [x] Pod 중단을 제어하지만 회수 기한을 늘리지는 못한다

**해설:** PDB는 Pod 중단을 제어합니다. Spot 회수 자체를 막지 못하므로 여유 용량·분산 배치·재시작 전략이 함께 필요합니다.

<!-- notes: {timing: 3min} [요약] 정답은 두 번째, 첫 번째, 세 번째 선택지입니다. 진단 순서와 교체 조건, PDB의 범위를 이해했는지 확인합니다. 숫자를 암기했는지보다 판단 이유를 설명하도록 유도하세요. {cue: transition} 다음은 앱·노드·관측성의 상관분석입니다. -->
