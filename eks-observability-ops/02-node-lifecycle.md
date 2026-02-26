---
marp: true
title: "Block 2: 노드 라이프사이클 & 모니터링"
theme: default
paginate: true
---

<!-- block: node-lifecycle -->

<!-- type: title -->

# 노드 가용성 모니터링이 어려운 이유

**Block 2: 노드 라이프사이클 & 모니터링**

> "Auto Mode에서 노드가 갑자기 사라지는데, 왜 사라졌는지 파악하기 어렵습니다"

> "Spot 인터럽트인지, Consolidation인지, Drift 교체인지 구분이 안 됩니다"

### 핵심 과제

- **노드 종료 원인 가시성 부족** - 왜 이 노드가 사라졌는지 로그 추적 필요
- **Karpenter 이벤트 추적 어려움** - Consolidation, Drift, Expiry 구분 필요
- **Spot 인터럽트 사전 감지 필요** - 2분 경고 내에 Pod 안전 이동

> **이 블록에서 학습할 내용:** 노드 상태 시각화, kubectl 진단, Prometheus 쿼리, Spot 대응, expireAfter 전략, AlertManager 알림 구성

<!-- notes: 노드 라이프사이클 관리의 어려움을 설명하고, 이번 블록에서 다룰 내용을 소개합니다. -->

---

<!-- type: canvas -->

# Grafana: EKS Node Monitoring

**CPU Requests vs Usage — Karpenter 판단 기준 시각화**

Canvas 애니메이션:
- Grafana 스타일 대시보드 — 상단에 Active Nodes, Ready, CPU Requests avg, CPU Usage avg, Cost/hr 메트릭
- 시계열 차트: Requests(파란) vs Usage(초록) 트렌드
- Node Status 패널: 노드별 Requests/Usage 바, SPOT 뱃지, Low Req 뱃지
- Karpenter Events 패널: 실시간 이벤트 로그
- **버튼:**
  - "노드 추가": 빈 슬롯에 새 노드 프로비저닝
  - "워크로드 추가": Ready 노드들의 CPU Requests/Usage 증가
  - "워크로드 삭제": 1-2개 랜덤 노드에서 Pods 제거 (20-40% Requests 감소) → Consolidation 대상 생성
  - "Spot 인터럽트": EventBridge→SQS→Karpenter 흐름 — Cordon→PDB→Drain→Reschedule→Terminate
  - "Consolidation": Low Req 노드 Cordon→Drain→Redistribute→Remove
  - "Reset": 초기 상태 복원

<!-- notes: 대시보드 시뮬레이터에서 워크로드 추가/삭제로 노드 활용률을 조절하고, Spot 인터럽트와 Consolidation의 전체 흐름을 확인할 수 있습니다. -->

---

<!-- type: code -->

# kubectl 진단 명령어

**노드 상태 및 Karpenter 이벤트 확인**

### NodePool 상태 확인

```bash
$ kubectl get nodepools
NAME              NODECLASS   NODES   READY   AGE
general-purpose   default     8       8       5d
system            default     2       2       5d
gpu-workload      gpu         0       0       5d
```

### NodeClaim 상세 정보

```bash
$ kubectl get nodeclaims -o wide
NAME          TYPE          ZONE         CAP-TYPE   NODE          READY   AGE
nc-abc123     m5.xlarge     ap-ne-2a     on-demand  ip-10-0-1-5   True    2h
nc-def456     c5.2xlarge    ap-ne-2b     spot       ip-10-0-2-8   True    45m
nc-ghi789     m5.2xlarge    ap-ne-2c     on-demand  ip-10-0-3-2   True    3h
nc-jkl012     r5.xlarge     ap-ne-2a     spot       ip-10-0-1-9   True    1h
```

<!-- notes: NodePool과 NodeClaim 리소스를 통해 Karpenter가 관리하는 노드 상태를 확인할 수 있습니다. -->

---

<!-- type: code -->

# kubectl 진단 명령어 (계속)

### 노드 라벨 확인

```bash
$ kubectl get nodes -L karpenter.sh/nodepool,karpenter.sh/capacity-type
NAME          STATUS   ROLES    AGE   NODEPOOL          CAPACITY-TYPE
ip-10-0-1-5   Ready    <none>   2h    general-purpose   on-demand
ip-10-0-2-8   Ready    <none>   45m   general-purpose   spot
ip-10-0-3-2   Ready    <none>   3h    general-purpose   on-demand
ip-10-0-1-9   Ready    <none>   1h    general-purpose   spot
```

### Karpenter 이벤트 추적

```bash
$ kubectl get events --sort-by='.lastTimestamp' | grep karpenter
12m   Normal   Launched         nodeclaim/nc-abc123   Launched node ip-10-0-1-5
10m   Normal   Registered       nodeclaim/nc-abc123   Registered node
5m    Normal   Consolidating    nodeclaim/nc-xyz789   Consolidating node (underutilized)
3m    Warning  SpotInterrupted  nodeclaim/nc-old123   Spot instance interrupted
2m    Normal   Drifted          nodeclaim/nc-def456   NodeClass changed
```

### Pending Pods 확인

```bash
$ kubectl get pods -A --field-selector=status.phase=Pending
NAMESPACE     NAME                      READY   STATUS    AGE
default       web-app-7d9f8b6c5-xyz    0/1     Pending   2m
production    api-server-5c8d7e-abc    0/1     Pending   1m
monitoring    prometheus-0             0/1     Pending   30s
```

<!-- notes: 이벤트 로그를 통해 노드 종료 원인(Consolidation, SpotInterruption, Drift)을 파악할 수 있습니다. -->

---

<!-- type: tabs -->

# Prometheus 쿼리: 노드 모니터링

**핵심 Karpenter 메트릭 쿼리**

### 총 노드 수

```promql
karpenter_nodes_total
```

NodePool별 총 노드 수 추적

| NodePool | 노드 수 |
|----------|---------|
| general-purpose | 8 |
| system | 2 |
| gpu-workload | 0 |

### Pending Pods

```promql
karpenter_pods_pending
```

스케줄 대기 중인 Pod 수 (프로비저닝 필요 신호)

> **Alert 조건:** `karpenter_pods_pending > 10 for 5m`

### Spot 비율

```promql
sum(karpenter_nodes_total{capacity_type="spot"}) / sum(karpenter_nodes_total) * 100
```

전체 노드 중 Spot 인스턴스 비율: **40%**

- On-Demand: 60%
- Spot: 40%

### 프로비저닝 P99

```promql
histogram_quantile(0.99, karpenter_nodeclaims_startup_duration_seconds)
```

노드 프로비저닝 지연 시간:
- P50: 45s
- P90: 72s
- P99: 98s

<!-- notes: Prometheus 쿼리를 통해 노드 수, Pending Pods, Spot 비율, 프로비저닝 지연 시간 등을 모니터링합니다. -->

---

<!-- type: canvas -->

# Spot 인터럽트 시뮬레이션

**EventBridge → SQS → Karpenter → Pod 퇴거 → 재스케줄링 전체 플로우**

Canvas 애니메이션:
- 상단: EventBridge → SQS → Karpenter 파이프라인 플로우
- 하단: Node 3개 (On-Demand ×2, Spot ×1) + Pod 이동 시각화

시퀀스 (10단계):
1. **EC2 Spot ITN** — 2분 경고 발생
2. **EventBridge Rule** 매칭
3. **SQS 큐** 메시지 전달
4. **Karpenter** 이벤트 수신
5. **Node Cordon** — SchedulingDisabled
6. **PDB 확인** — minAvailable 체크
7. **Pod Terminating** — gracefulTermination
8. **Pod 재스케줄링** — 다른 노드로 이동
9. **새 노드 프로비저닝** (필요 시)
10. **Node Terminated** — 인스턴스 종료

<!-- notes: AWS EventBridge → SQS → Karpenter 파이프라인을 통해 Spot 인터럽트가 처리되는 전체 흐름을 시뮬레이션합니다. -->

---

<!-- type: compare -->

# Spot Overprovisioning 전략

**Pause 컨테이너로 사전 용량 확보 — 즉시 스케줄링**

### 동작 흐름

| Phase | 단계 | 설명 |
|-------|------|------|
| Phase 1 | **Buffer Ready** | Dummy pods가 용량 예약 (PriorityClass: -1) |
| Phase 2 | **Real Workload 도착** | Dummy 삭제 → 워크로드 즉시 스케줄링 (Preempt) |
| Phase 3 | **Karpenter 보충** | Pending dummy (AntiAffinity) → 새 노드 프로비저닝 → 버퍼 복원 |

### PriorityClass YAML

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: overprovisioning
value: -1              # 가장 낮은 우선순위
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
  template:
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

> **핵심 원리:** `value: -1` → 가장 낮은 우선순위. 실제 워크로드 도착 시 Dummy pod가 즉시 Preempt → 노드 대기 없이 스케줄링

<!-- notes: Overprovisioning은 Spot 인터럽트 대비 전략입니다. Pause 컨테이너로 사전 용량을 확보하여 워크로드가 노드 프로비저닝을 기다리지 않고 즉시 스케줄링됩니다. -->

---

<!-- type: compare -->

# expireAfter 전략 비교

**환경별 노드 최대 수명 설정**

### 환경별 권장값

| 값 | 환경 | 설명 | 보안 패치 속도 | 안정성 |
|----|------|------|----------------|--------|
| 24h | 개발/테스트 | 빠른 교체, 최신 AMI 적용 | 높음 | 낮음 |
| 48h | 보안 중요 환경 | 보안 패치 빠른 적용 우선 | 높음 | 중간 |
| 72h | 스테이징 | 프로덕션 전 테스트 환경 | 중간 | 중간 |
| **168h** | **프로덕션 권장** | 안정성과 보안 패치 속도의 균형 | 중간 | 높음 |
| 240h | 안정성 우선 | 장기 실행 워크로드 | 낮음 | 높음 |
| 336h | GPU 워크로드 | 프로비저닝 비용이 높은 노드 | 낮음 | 매우 높음 |

### NodePool YAML

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: general-purpose
spec:
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 1m
    # 프로덕션 권장 값
    expireAfter: 168h  # 7일
```

<!-- notes: expireAfter 값은 보안 패치 속도와 안정성 사이의 트레이드오프입니다. 프로덕션에서는 168h(7일)을 권장합니다. -->

---

<!-- type: timeline -->

# AMI 업데이트 & Drift 감지

**NodeClass 변경 시 자동 노드 교체 흐름**

1. **NodeClass 변경** - AMI 업데이트
2. **Drift 감지** - 자동
3. **신규 노드 프로비저닝**
4. **Pod 안전 이동** - PDB 준수
5. **구 노드 종료**

---

<!-- type: compare -->

# AL2023 vs Bottlerocket 비교

### AL2023

| 특성 | 값 |
|------|-----|
| 부팅 시간 | 40-60초 |
| 보안 | 표준 |
| SSH 접근 | 가능 |
| 패키지 관리 | yum/dnf |
| 권장 사용처 | 디버깅 필요 환경 |

### Bottlerocket

| 특성 | 값 |
|------|-----|
| 부팅 시간 | **20-30초** |
| 보안 | **강화 (immutable)** |
| SSH 접근 | 제한적 |
| 패키지 관리 | API 기반 업데이트 |
| 권장 사용처 | **프로덕션, 보안 중요** |

<!-- notes: Bottlerocket은 빠른 부팅과 강화된 보안을 제공하며, 프로덕션 환경에 권장됩니다. -->

---

<!-- type: code -->

# AlertManager 알림 규칙

**Karpenter 및 노드 상태 알림 구성**

### PrometheusRule YAML

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: karpenter-alerts
spec:
  groups:
  - name: karpenter
    rules:
    - alert: HighPendingPods
      expr: karpenter_pods_pending > 10
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "{{ $value }} pods pending"

    - alert: NodeProvisioningFailed
      expr: increase(karpenter_nodeclaims_terminated{reason="ProvisioningFailed"}[10m]) > 0
      labels:
        severity: critical
      annotations:
        summary: "Node provisioning failed"

    - alert: SpotInterruptionRate
      expr: increase(karpenter_nodeclaims_terminated{reason="SpotInterruption"}[1h]) > 3
      labels:
        severity: warning
      annotations:
        summary: "High Spot interruption rate"

    - alert: NodeAgeExceeded
      expr: time() - kube_node_created > 604800
      labels:
        severity: info
      annotations:
        summary: "Node older than 7 days"

    - alert: CPUOverProvisioned
      expr: (sum(kube_pod_container_resource_requests{resource="cpu"}) / sum(kube_node_status_allocatable{resource="cpu"})) > 0.7
      for: 1h
      labels:
        severity: info
      annotations:
        summary: "CPU over-provisioned"
```

<!-- notes: AlertManager 규칙을 통해 Pending Pods, 프로비저닝 실패, Spot 인터럽트 비율 등을 모니터링합니다. -->

---

<!-- type: checklist -->

# Day-2 운영 체크리스트

**EKS Auto Mode 운영 준비 상태 점검**

### Disruption & 안정성

- [ ] Disruption Budget 설정 완료
- [ ] PodDisruptionBudget 적용
- [ ] Spot 인터럽트 알림 구성
- [ ] expireAfter 정책 설정
- [ ] 노드 모니터링 대시보드 구축

### 최적화 & 비용

- [ ] AMI 업데이트 자동화
- [ ] 비용 태깅 (CostCenter, Team)
- [ ] Multi-AZ 배포 확인
- [ ] Topology Spread Constraints 적용
- [ ] 정기 비용 리뷰 스케줄

> **Tip:** 체크리스트 항목을 점검 후 프로덕션 배포를 진행하세요.

<!-- notes: 프로덕션 배포 전 모든 체크리스트 항목을 확인합니다. -->

---

<!-- type: quiz -->

# Block 2 요약 & 퀴즈

**노드 라이프사이클 & 모니터링 핵심 내용 정리**

### 핵심 요약

| 영역 | 내용 |
|------|------|
| 노드 모니터링 | kubectl, Prometheus 쿼리로 노드 상태 및 이벤트 추적 |
| Spot 대응 | 2분 경고 내 Pod 안전 이동, PDB 준수 |
| 운영 전략 | expireAfter, Drift, AlertManager 알림 |

### Quiz 1: Spot 인스턴스 종료 전 경고 시간은?

- [ ] A) 30초
- [x] B) 2분
- [ ] C) 5분
- [ ] D) 10분

### Quiz 2: 프로덕션 환경의 권장 expireAfter 값은?

- [ ] A) 24h
- [ ] B) 48h
- [x] C) 168h (7일)
- [ ] D) 336h (14일)

### Quiz 3: 노드 종료 원인을 파악할 수 있는 kubectl 명령은?

- [ ] A) kubectl get nodes
- [ ] B) kubectl top nodes
- [x] C) kubectl get events --sort-by='.lastTimestamp' | grep karpenter
- [ ] D) kubectl describe pod

<!-- notes: Block 2의 핵심 내용을 퀴즈를 통해 복습합니다. 정답: B, C, C -->
