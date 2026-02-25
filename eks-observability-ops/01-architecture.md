---
marp: true
title: "Block 1: EKS Auto Mode 아키텍처"
theme: default
paginate: true
---

<!-- block: architecture -->

<!-- type: title -->

# EKS Auto Mode Deep Dive

**Block 1: 내부 아키텍처 이해 (35분)**

`Karpenter 기반` `관리형 노드` `자동 스케일링`

<!-- notes: EKS Auto Mode의 내부 아키텍처를 깊이 있게 살펴보는 시간입니다. Karpenter 기반의 관리형 노드 프로비저닝과 자동 스케일링에 대해 학습합니다. -->

---

<!-- type: content -->

# Auto Mode란?

**AWS 관리형 Karpenter로 노드 프로비저닝 자동화**

### 핵심 특징

- AWS가 Control Plane 내에서 **Karpenter를 관리형으로 운영**
- **NodePool/NodeClass**로 노드 프로비저닝 제어
- Managed Node Group 대비: **노드 관리 오버헤드 제거**
- **빠른 스케일링**: 40-90초 내 Pod 실행

### 기본 NodePool

| NodePool | 설명 |
|----------|------|
| **general-purpose** | 범용 워크로드용, amd64/arm64, On-Demand + Spot 지원 |
| **system** | 시스템 컴포넌트 전용, CriticalAddonsOnly taint 적용 |

> Karpenter를 직접 설치/관리할 필요 없이, EKS가 모든 것을 자동 처리합니다.

<!-- notes: Auto Mode는 AWS가 Karpenter를 Control Plane 내에서 관리형으로 운영하는 방식입니다. NodePool과 NodeClass를 통해 노드 프로비저닝을 제어하며, 기존 Managed Node Group 대비 관리 오버헤드가 크게 줄어듭니다. -->

---

<!-- type: compare -->

# Auto Mode vs MNG vs Fargate

**노드 관리 방식 비교**

### Auto Mode

| 항목 | 내용 |
|------|------|
| 특징 | Karpenter 기반, AWS 관리형, 인스턴스 다양화 |
| 스케일링 | 자동 Consolidation, 40-90초 프로비저닝 |
| 비용 | Spot 인스턴스 자동 활용, 최적화된 bin-packing |
| 적합 워크로드 | 가변적 워크로드, 다양한 인스턴스 요구사항 |

### Managed Node Group

| 항목 | 내용 |
|------|------|
| 특징 | ASG 기반, Launch Template, 수동 설정 |
| 스케일링 | Cluster Autoscaler 필요, 2-5분 소요 |
| 비용 | 인스턴스 타입 고정, 수동 Spot 설정 |
| 적합 워크로드 | 예측 가능한 워크로드, 특정 인스턴스 요구 |

### Fargate

| 항목 | 내용 |
|------|------|
| 특징 | 서버리스, Pod 단위 격리, 노드 관리 없음 |
| 스케일링 | Pod 단위 자동, 30-60초 소요 |
| 비용 | vCPU/메모리 기반 과금, 유휴 비용 없음 |
| 적합 워크로드 | 배치 작업, 간헐적 워크로드, 보안 격리 |

<!-- notes: 세 가지 노드 관리 방식을 비교합니다. Auto Mode는 Karpenter 기반으로 가장 유연하고 빠른 스케일링을 제공합니다. MNG는 전통적인 ASG 기반으로 예측 가능한 워크로드에 적합하며, Fargate는 서버리스로 노드 관리가 전혀 필요 없습니다. -->

---

<!-- type: canvas -->

# 내부 아키텍처

**Karpenter가 Control Plane 내에서 동작하는 방식**

아키텍처 애니메이션:

1. EKS Control Plane 영역 표시
2. Control Plane 내부에 Karpenter Controller와 Scheduler 컴포넌트 표시
3. Data Plane 영역에 NodePool, NodeClass, EC2 Instances, Pods 표시
4. Pod Pending 발생 시 Scheduler가 Karpenter에 알림
5. Karpenter가 NodePool/NodeClass 평가
6. EC2 RunInstances API 호출로 인스턴스 생성
7. 새 노드에 Pod 스케줄링

**흐름**: Pod Pending -> Scheduler -> Karpenter -> NodePool -> EC2 API -> Node Register -> Pod Running

<!-- notes: 이 애니메이션은 EKS Auto Mode의 내부 아키텍처를 보여줍니다. Karpenter Controller가 Control Plane 내에서 동작하며, Pod가 Pending 상태가 되면 Scheduler를 통해 Karpenter에 알림이 전달되고, NodePool과 NodeClass를 평가하여 최적의 인스턴스를 프로비저닝합니다. -->

---

<!-- type: tabs -->

# NodePool 구조

**기본 제공 NodePool 비교**

### general-purpose

**특징:**
- 범용 워크로드용 기본 NodePool
- amd64 및 arm64 아키텍처 지원
- On-Demand + Spot 인스턴스 혼합
- WhenEmptyOrUnderutilized Consolidation

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: general-purpose
spec:
  template:
    spec:
      requirements:
        - key: kubernetes.io/arch
          operator: In
          values: [amd64, arm64]
        - key: karpenter.sh/capacity-type
          operator: In
          values: [on-demand, spot]
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
```

### system

**특징:**
- 시스템 컴포넌트 전용 NodePool
- amd64 아키텍처만 지원
- On-Demand 인스턴스만 사용 (안정성)
- CriticalAddonsOnly taint로 일반 워크로드 차단

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: system
spec:
  template:
    spec:
      requirements:
        - key: kubernetes.io/arch
          operator: In
          values: [amd64]
        - key: karpenter.sh/capacity-type
          operator: In
          values: [on-demand]
      taints:
        - key: CriticalAddonsOnly
          effect: NoSchedule
```

<!-- notes: 기본 제공되는 두 가지 NodePool을 비교합니다. general-purpose는 범용 워크로드용으로 다양한 아키텍처와 용량 타입을 지원하며, system은 시스템 컴포넌트 전용으로 안정성을 위해 On-Demand만 사용합니다. -->

---

<!-- type: content -->

# NodeClass 설정

**인터랙티브 NodeClass 빌더**

### 설정 옵션

- **AMI**: AL2023 / Bottlerocket
- **Subnet**: Private / Public
- **EBS**: 50Gi / 100Gi / 200Gi gp3
- **IMDSv2**: Required / Optional

### 생성된 NodeClass

```yaml
apiVersion: karpenter.k8s.aws/v1
kind: EC2NodeClass
metadata:
  name: default
spec:
  amiFamily: AL2023
  subnetSelectorTerms:
    - tags:
        karpenter.sh/discovery: my-cluster
        kubernetes.io/role/internal-elb: "1"
  blockDeviceMappings:
    - deviceName: /dev/xvda
      ebs:
        volumeSize: 50Gi
        volumeType: gp3
  metadataOptions:
    httpTokens: required
```

<!-- notes: NodeClass는 노드의 AWS 리소스 설정을 정의합니다. AMI Family, Subnet 선택, EBS 볼륨 크기, IMDSv2 설정 등을 구성할 수 있습니다. 프로덕션 환경에서는 보안을 위해 IMDSv2 required 설정을 권장합니다. -->

---

<!-- type: code -->

# 커스텀 NodePool 패턴 (1/2)

**Compute-optimized & Memory-optimized**

### Compute-optimized

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: compute-optimized
spec:
  template:
    spec:
      requirements:
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: [c]
        - key: karpenter.k8s.aws/instance-generation
          operator: Gt
          values: ["6"]
      nodeClassRef:
        name: default
  limits:
    cpu: 1000
```

### Memory-optimized

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: memory-optimized
spec:
  template:
    spec:
      requirements:
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: [r]
        - key: karpenter.k8s.aws/instance-generation
          operator: Gt
          values: ["6"]
      nodeClassRef:
        name: default
  limits:
    memory: 2000Gi
```

<!-- notes: 워크로드 특성에 맞는 커스텀 NodePool을 생성할 수 있습니다. Compute-optimized는 CPU 집약적 워크로드용으로 c 계열 인스턴스를 사용하고, Memory-optimized는 메모리 집약적 워크로드용으로 r 계열 인스턴스를 사용합니다. -->

---

<!-- type: code -->

# 커스텀 NodePool 패턴 (2/2)

**GPU NodePool for ML/AI Workloads**

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: gpu
spec:
  template:
    spec:
      requirements:
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: [g, p]
        - key: karpenter.k8s.aws/instance-family
          operator: In
          values: [g5, p5]
        - key: karpenter.sh/capacity-type
          operator: In
          values: [on-demand]
      taints:
        - key: nvidia.com/gpu
          effect: NoSchedule
      nodeClassRef:
        name: gpu-nodeclass
  limits:
    nvidia.com/gpu: 100
  disruption:
    consolidationPolicy: WhenEmpty
```

### GPU NodePool 특징

| 항목 | 설명 |
|------|------|
| **인스턴스** | g5 (추론), p5 (학습) |
| **Capacity** | On-Demand만 (Spot 불가) |
| **Taint** | GPU 워크로드만 스케줄링 |
| **Consolidation** | WhenEmpty (비용 절감) |

> GPU 인스턴스는 비용이 높으므로 limits 설정이 중요합니다.

<!-- notes: ML/AI 워크로드를 위한 GPU NodePool입니다. g5는 추론용, p5는 학습용으로 사용됩니다. GPU 인스턴스는 Spot 중단 시 학습이 중단될 수 있어 On-Demand만 사용하며, Taint를 통해 GPU 워크로드만 스케줄링되도록 합니다. -->

---

<!-- type: canvas -->

# Pod Pending에서 Node Ready까지

**프로비저닝 타임라인 시뮬레이션**

타임라인 애니메이션 (0초 ~ 90초):

| 단계 | 시간 | 설명 |
|------|------|------|
| Pod Created | 0-1초 | Pod 생성 요청 |
| Pending Detected | 1-3초 | 스케줄러가 Pending 감지 |
| NodePool Eval | 3-7초 | NodePool 요구사항 평가 |
| EC2 RunInstances | 7-22초 | EC2 인스턴스 생성 API 호출 |
| AMI Boot | 22-52초 | AMI 부팅 및 초기화 |
| kubelet Register | 52-72초 | kubelet 등록 및 노드 Ready |
| Pod Running | 72-90초 | Pod 스케줄링 및 실행 |

**총 소요 시간: 약 40-90초**

<!-- notes: Pod Pending 상태에서 Node가 Ready 상태가 되기까지의 전체 프로비저닝 타임라인을 보여주는 애니메이션입니다. EC2 인스턴스 생성과 AMI 부팅이 가장 많은 시간을 차지합니다. -->

---

<!-- type: content -->

# 인스턴스 선택 알고리즘

**필터링 과정 시각화**

### 필터링 단계

1. **Category 필터**: m, c, r 계열만 선택
2. **Generation 필터**: 6세대 초과만 선택
3. **Size 필터**: large 이상만 선택
4. **Best Select**: 최적 인스턴스 선택 (예: m7i.2xlarge)

### 인스턴스 목록

```
t3.micro  t3.small  t3.medium  t3.large
m5.large  m5.xlarge  m5.2xlarge
m6i.large  m6i.xlarge  m6i.2xlarge  m6i.4xlarge
m7i.large  m7i.xlarge  m7i.2xlarge  <- 최종 선택
c5.large  c5.xlarge  c5.2xlarge
c6i.large  c6i.xlarge  c6i.2xlarge
c7i.large  c7i.xlarge  c7i.2xlarge
r5.large  r5.xlarge  r5.2xlarge
r6i.large  r6i.xlarge  r6i.2xlarge
r7i.large  r7i.xlarge  r7i.2xlarge
g5.xlarge  g5.2xlarge  p5.48xlarge
```

> Karpenter는 Pod 요구사항과 NodePool 제약을 기반으로 최적의 인스턴스를 자동 선택합니다.

<!-- notes: Karpenter의 인스턴스 선택 알고리즘을 시각화합니다. NodePool에 정의된 요구사항에 따라 인스턴스 카테고리, 세대, 크기를 필터링하고 최적의 인스턴스를 선택합니다. -->

---

<!-- type: canvas -->

# Consolidation 동작 원리

**노드 통합으로 비용 최적화**

Consolidation 애니메이션:

**초기 상태:**
- Node 1: 4개 Pod (80% 사용률) - $0.10/hr
- Node 2: 1개 Pod (15% 사용률) - $0.10/hr
- Node 3: 2개 Pod (30% 사용률) - $0.10/hr
- Node 4: 0개 Pod (0% 사용률) - $0.10/hr

**Consolidation 후:**
- Node 1: 7개 Pod (모든 Pod 통합) - $0.10/hr
- Node 2, 3, 4: 제거됨

**절감 효과: $0.30/hr**

<!-- notes: Consolidation은 저사용률 노드의 Pod를 다른 노드로 이동시키고 빈 노드를 제거하여 비용을 최적화합니다. 이 애니메이션은 4개 노드에서 1개 노드로 통합되는 과정을 보여줍니다. -->

---

<!-- type: compare -->

# Consolidation 정책 비교

**WhenEmpty vs WhenEmptyOrUnderutilized**

### WhenEmpty

- Pod가 0개인 노드만 제거
- 안전하지만 비효율적일 수 있음
- GPU 워크로드에 적합

**동작 예시:**
- Node (0 pods, 0%) -> 제거
- Node (1 pod, 15%) -> 유지
- Node (2 pods, 25%) -> 유지

### WhenEmptyOrUnderutilized

- 저사용률 노드도 통합
- 더 공격적인 비용 최적화
- 일반 워크로드에 권장

**동작 예시:**
- Node (0 pods, 0%) -> 제거
- Node (1 pod, 15%) -> Pod 이동 후 제거
- Node (2 pods, 25%) -> Pod 이동 후 제거

<!-- notes: 두 가지 Consolidation 정책을 비교합니다. WhenEmpty는 완전히 빈 노드만 제거하여 안전하지만 비효율적일 수 있습니다. WhenEmptyOrUnderutilized는 저사용률 노드도 통합하여 더 공격적으로 비용을 최적화합니다. -->

---

<!-- type: timeline -->

# Drift 감지와 교체

**NodePool/NodeClass 변경 시 자동 롤링 업데이트**

### Drift 교체 흐름

1. **NodePool/NodeClass 변경** - 설정 변경 적용
2. **Drift 감지** - Karpenter가 변경 감지
3. **신규 노드 프로비저닝** - 새 설정으로 노드 생성
4. **Pod 이동** - 기존 노드에서 새 노드로 이동
5. **구 노드 종료** - 이전 노드 정리

### Drift 발생 조건

- AMI Family 변경
- 인스턴스 타입 요구사항 변경
- Subnet/SecurityGroup 변경
- Block Device 설정 변경

### 안전한 교체 보장

- PodDisruptionBudget 준수
- Disruption Budget 적용
- 점진적 롤링 (한 번에 모든 노드 교체하지 않음)

<!-- notes: Drift는 NodePool이나 NodeClass가 변경되었을 때 기존 노드를 새 설정으로 교체하는 기능입니다. PodDisruptionBudget을 준수하며 점진적으로 롤링 업데이트를 수행합니다. -->

---

<!-- type: content -->

# Disruption Budget

**안전한 노드 교체를 위한 제한 설정**

### 설정 파라미터

- **Total Nodes**: 전체 노드 수
- **Budget Percentage**: 동시 교체 가능한 노드 비율 (예: 10%)
- **Budget Fixed**: 최소 가용 노드 수

### 계산 결과

| 메트릭 | 값 |
|--------|-----|
| Max Simultaneous | 1 (10개 노드의 10%) |
| Min Available | 9 |
| Business Hours | ON |

### 생성된 설정

```yaml
spec:
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    budgets:
      - nodes: "10%"
    # Business hours protection
    schedules:
      - cron: "0 9 * * 1-5"  # 09:00 Mon-Fri
        duration: 8h
```

<!-- notes: Disruption Budget은 노드 교체 시 동시에 중단될 수 있는 노드 수를 제한합니다. 비율 또는 고정 수로 설정할 수 있으며, Business Hours 동안은 교체를 제한하는 스케줄도 설정할 수 있습니다. -->

---

<!-- type: checklist -->

# 스케일링 속도 최적화 팁

**프로비저닝 시간 단축을 위한 Best Practices**

- [x] **Bottlerocket AMI 사용** - 부팅 시간 10-20초 단축
- [x] **작은 EBS 볼륨** - 볼륨 초기화 5-10초 단축
- [x] **다양한 인스턴스 타입 허용** - 가용성 향상, 빠른 프로비저닝
- [x] **Pod Topology Spread 설정** - 워크로드 분산, 안정성 향상
- [x] **PriorityClass로 중요 워크로드 우선** - Preemption 활용
- [x] **Disruption Budget으로 안전한 교체** - 서비스 중단 최소화

<!-- notes: 스케일링 속도를 최적화하기 위한 Best Practice입니다. Bottlerocket AMI는 AL2023보다 부팅이 빠르고, 작은 EBS 볼륨은 초기화 시간을 줄입니다. 다양한 인스턴스 타입을 허용하면 가용성이 높아져 빠르게 프로비저닝됩니다. -->

---

<!-- type: quiz -->

# Block 1 요약 & 퀴즈

**학습 내용 확인**

### Q1. EKS Auto Mode의 기반 기술은?

- [x] Karpenter
- [ ] Cluster Autoscaler
- [ ] AWS Fargate
- [ ] Custom Controller

### Q2. Consolidation 정책 중 저사용률 노드도 통합하는 것은?

- [x] WhenEmptyOrUnderutilized
- [ ] WhenEmpty
- [ ] WhenIdle
- [ ] WhenUnderutilized

### Q3. Auto Mode에서 Pod Pending에서 Node Ready까지 일반적 소요 시간은?

- [ ] 5-10초
- [x] 40-90초
- [ ] 2-5분
- [ ] 10분 이상

<!-- notes: Block 1에서 학습한 내용을 확인하는 퀴즈입니다. Auto Mode는 Karpenter 기반이며, WhenEmptyOrUnderutilized 정책이 저사용률 노드도 통합합니다. 프로비저닝 시간은 일반적으로 40-90초입니다. -->
