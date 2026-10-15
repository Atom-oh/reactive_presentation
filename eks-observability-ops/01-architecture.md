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

확인: **2026-10-15** · EKS **1.37** · 직접 설치 Karpenter **v1.15.0**

[버전 호환성·변경 사항·공식 출처](version-update.md): 직접 설치한 Karpenter는 공식 호환성 표 기준 Kubernetes 1.37에 **1.15.x** 필요 (v1.14.1은 1.36까지). Auto Mode는 AWS가 관리하므로 Karpenter 버전을 고르지 않습니다.

<!-- notes: EKS Auto Mode의 내부 아키텍처를 깊이 있게 살펴보는 시간입니다. Karpenter 기반의 관리형 노드 프로비저닝과 자동 스케일링에 대해 학습합니다. -->

---

<!-- type: content -->

# 노드는 자동으로, 앱 정책은 우리가

| 구분 | 쉬운 설명 |
|---|---|
| Karpenter | 배치되지 못한 Pod에 맞는 노드를 골라 추가하고, 조건이 맞으면 정리 |
| Auto Mode에서 AWS | 노드 관리 기능, OS, 주요 인프라 구성 요소 관리 |
| 우리 팀 | CPU·메모리 요청량, 배치 조건, 중단 허용 범위 설계 |

**Pod = 앱 실행 단위 · Node = Pod가 실행되는 서버.**

최신 버전 상세는 접어서 제공: EKS 1.37, 직접 설치한 Karpenter v1.15.0. Auto Mode는 별도 Helm 버전을 지정하지 않습니다. [공식 검토 결과](version-update.md)

<!-- notes: {timing: 2min} [요약] Karpenter는 Pod에 맞는 노드를 고르는 역할입니다. Auto Mode에서는 AWS가 이 기능과 노드 OS·주요 인프라 구성 요소를 관리합니다. 팀은 Pod 요청량, 배치 조건, 서비스 가용성을 설계합니다. Pod는 애플리케이션 실행 단위, Node는 Pod가 실행되는 서버라고 먼저 설명하세요. 오늘의 기준은 EKS 1.37과 직접 설치한 Karpenter v1.15.0입니다. Karpenter 공식 호환성 표는 Kubernetes 1.37에 Karpenter 1.15.x를 요구합니다. v1.14.1에서 올라온다면 v1.15 업그레이드 안내의 메트릭 label 변경과 Node Repair 동작 변경을 먼저 확인합니다. {cue: transition} 다음에는 팀이 직접 운영할 범위를 비교합니다. -->

---

<!-- type: compare -->

# 어디까지 직접 운영할까요?

**Auto Mode와 직접 설치한 Karpenter부터 비교**

### 직접 설치한 Karpenter

- 팀이 Controller·CRD·IAM·AMI를 관리
- NodePool + EC2NodeClass로 노드를 제어
- AMI·노드 구성을 직접 제어해야 할 때 검토
- v1.15.0: Controller와 CRD를 함께 업데이트 (Kubernetes 1.37은 1.15.x 필요)


### Auto Mode

| 항목 | 내용 |
|------|------|
| 특징 | Karpenter 기반, AWS 관리형, 인스턴스 다양화 |
| 스케일링 | Balanced 기본 정책 (EKS 1.37 신규 풀), 수요 기반 프로비저닝 |
| 비용 | EC2 비용 + Auto Mode 관리 비용 (2026-07부터 GPU 계열 인하), 커스텀 풀에서 Spot 활용 |
| 2026 추가 기능 | NodeClass `advancedCompute`, EFA 인터페이스, ARC zonal shift 대응, EC2 상태 검사 실패 노드 자동 교체 |
| 적합 워크로드 | 가변적 워크로드, 다양한 인스턴스 요구사항 |

### Managed Node Group

| 항목 | 내용 |
|------|------|
| 특징 | ASG 기반, Launch Template, 수동 설정 |
| 스케일링 | Cluster Autoscaler 등으로 노드 그룹 용량 조절 |
| 비용 | 노드 그룹 단위로 인스턴스 타입·Spot 구성 |
| 적합 워크로드 | 예측 가능한 워크로드, 특정 인스턴스 요구 |

### Fargate

| 항목 | 내용 |
|------|------|
| 특징 | 서버리스, Pod 단위 격리, 노드 관리 없음 |
| 스케일링 | Pod 단위 용량 제공 · 실제 시간은 환경에 따라 다름 |
| 비용 | vCPU/메모리 기반 과금, 유휴 비용 없음 |
| 적합 워크로드 | 배치 작업, 간헐적 워크로드, 보안 격리 |

<!-- notes: {timing: 2min} [요약] 같은 노드 자동화라도 운영 책임이 다릅니다. Auto Mode는 AWS가 노드 OS와 관리형 구성 요소를 운영합니다. 직접 설치한 Karpenter는 팀이 Controller·CRD·IAM·AMI를 관리하므로 자유도와 운영 부담이 함께 커집니다. 기존 MNG와 Fargate 비교는 추가 탭에서만 다룹니다. 어느 방식이 무조건 빠르다고 단정하지 말고 필요한 제어 수준을 물어보세요. {cue: transition} 이제 앱이 노드에 배치되는 흐름을 따라갑니다. -->

---

<!-- type: content -->

# Pod가 기다리면 누가 움직일까요?

1. **앱이 대기 — FailedScheduling 확인**: 이 예시는 Pod Events에서 배치 실패가 확인된 경우입니다. 일반적인 Pending 전체를 노드 부족으로 단정하지 않습니다.

2. **노드를 계획 — Karpenter**: Karpenter는 스케줄되지 못한 Pod를 관찰합니다. NodePool·NodeClass 조건과 요청 리소스를 확인해 추가 용량을 계획합니다.

3. **두 설정을 확인 — NodePool + NodeClass**: NodePool은 어떤 노드를 허용할지, NodeClass는 AWS에서 어떻게 만들지를 정합니다. NodeClaim은 생성할 노드 한 대의 요청·상태를 나타냅니다.

4. **노드가 준비 — EC2 → Ready**: 인스턴스가 시작되고 클러스터에 등록됩니다. Auto Mode에서는 AWS가 노드 OS와 필요한 구성 요소를 관리합니다.

5. **앱을 배치 — Scheduler → Pod**: 준비된 노드에 Kubernetes Scheduler가 Pod를 배치합니다. 이후 이미지 다운로드와 앱 시작이 완료되어야 요청을 처리할 수 있습니다.

인터랙션: 전체 흐름을 먼저 표시하고 다음/이전/처음부터 또는 ↑ ↓로 설명을 한 단계씩 확인합니다.

**Karpenter는 노드를 준비하고, Scheduler는 Pod를 배치합니다.**

<!-- notes: {timing: 3min} [요약] Pod가 대기하고, Karpenter가 조건을 확인해 노드를 준비한 뒤, Scheduler가 Pod를 배치합니다. 첫 화면에서 전체 흐름을 보여주고 다음 단계로 한 번씩 진행하세요. 세 번째 단계에서 NodePool은 허용 조건, NodeClass는 AWS 생성 설정, NodeClaim은 한 대의 생성 요청이라는 역할만 익힙니다. Scheduler가 Karpenter를 직접 호출하거나 EC2가 Pod를 배치하는 구조로 설명하지 마세요. {cue: transition} 다음은 두 설정 중 먼저 NodePool입니다. -->

---

<!-- type: tabs -->

# NodePool: 어떤 노드를 허용할까요?

**NodePool은 노드의 허용 조건입니다.** CPU 종류·인스턴스 계열·Spot 사용 여부를 정합니다.

HTML에서는 먼저 일반 앱 자리(`general-purpose`)와 시스템 Pod 자리(`system`)를 비교합니다. 아래 YAML은 접어서 제공합니다. `system`의 taint를 허용하는 toleration이 있어야 배치 후보가 되며, toleration만으로 해당 풀에 반드시 배치되는 것은 아닙니다.

기본 풀 비교 — YAML은 읽기 전용 설정 발췌입니다.

기본 풀은 수정할 수 없습니다. Spot·별도 정책은 커스텀 NodePool로 구성합니다.

### general-purpose

**특징:**
- 범용 워크로드용 기본 NodePool
- amd64 아키텍처 지원
- On-Demand 인스턴스만 사용
- Balanced Consolidation

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: general-purpose
spec:
  template:
    spec:
      nodeClassRef:
        group: eks.amazonaws.com
        kind: NodeClass
        name: default
      requirements:
        - key: kubernetes.io/arch
          operator: In
          values: [amd64]
        - key: karpenter.sh/capacity-type
          operator: In
          values: [on-demand]
  disruption:
    consolidationPolicy: Balanced
```

### system

**특징:**
- 시스템 컴포넌트 전용 NodePool
- amd64 및 arm64 아키텍처 지원
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
      nodeClassRef:
        group: eks.amazonaws.com
        kind: NodeClass
        name: default
      requirements:
        - key: kubernetes.io/arch
          operator: In
          values: [amd64, arm64]
        - key: karpenter.sh/capacity-type
          operator: In
          values: [on-demand]
      taints:
        - key: CriticalAddonsOnly
          effect: NoSchedule
```

<!-- notes: 기본 제공되는 두 가지 NodePool을 비교합니다. general-purpose는 amd64, system은 amd64/arm64를 지원하며 두 풀 모두 On-Demand만 사용합니다. EKS 1.37에서 두 풀의 정책은 Balanced이며 직접 수정할 수 없습니다. -->

---

<!-- type: content -->

# NodeClass: AWS에서 어떻게 만들까요?

먼저 세 질문만 읽습니다: **어디에 연결하나?** (subnet·보안 그룹), **어떤 권한을 쓰나?** (노드 IAM 역할), **얼마나 저장하나?** (로컬 스토리지).

Auto Mode는 `NodeClass`, 직접 설치한 Karpenter는 `EC2NodeClass`를 사용합니다. HTML에서는 옵션과 전체 YAML을 접어 두고, 필요할 때 디스크 크기·subnet 선택을 바꿉니다. 아래 `workload` NodeClass를 뒤의 커스텀 NodePool 예제가 참조합니다.

**NodeClass는 AWS에서 노드를 만드는 설정입니다.** NodePool이 “어떤 서버를 허용하나”라면, NodeClass는 “어느 네트워크·역할·디스크로 만드나”입니다.

Subnet과 스토리지를 바꾸며 생성된 YAML을 비교하세요.

- **AMI·IMDS 보안**: AWS 관리 — AL2023/AMI 선택·IMDSv2 해제 옵션 없음
- **Subnet**: Private / Public (예제의 network-type 태그로 선택)
- **노드 로컬 스토리지**: 80Gi / 100Gi / 200Gi
- **IAM 역할·Security Group**: 환경별 역할과 검색 태그 준비
- **고급 노드 설정 (2026-10 추가)**: `advancedCompute`로 kubelet, kernel sysctl, hugepages를 조정. 바꾸면 기존 노드는 Drift로 교체

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
```

```yaml
# 선택: advancedCompute (2026-10 추가). 필요한 항목만 지정
spec:
  advancedCompute:
    kubelet:
      maxPods: 60            # 1-110, IP 수와 110 중 작은 값이 상한
    kernel:
      sysctl:
        net.core.somaxconn: 4096
    hugepages:
      pages:
        - size: "2Mi"
          count: 512         # Pod는 hugepages-2Mi를 요청해야 사용
```

> 사전 조건: 노드 역할에 EC2 유형 Access Entry와 AmazonEKSAutoNodePolicy 연결. 예제 태그가 있는 subnet·security group과 필요한 네트워크 경로 준비.

<!-- notes: Auto Mode는 eks.amazonaws.com/v1의 NodeClass를 사용합니다. AMI와 OS 보안은 AWS가 관리합니다. 직접 설치한 Karpenter의 EC2NodeClass, amiFamily, blockDeviceMappings, metadataOptions 예제와 혼용하지 않습니다. workload NodeClass와 같은 IAM 역할의 EC2 Access Entry 및 AmazonEKSAutoNodePolicy를 먼저 준비합니다. 2026-10부터 advancedCompute로 kubelet(maxPods, eviction, 로그 회전), 지원 목록의 kernel sysctl, hugepages를 조정할 수 있습니다. 실행 중인 노드에 바로 적용되지 않고 Drift로 교체된 새 노드부터 반영됩니다. static hugepages와 EFA는 같은 NodeClass에 함께 쓸 수 없습니다. -->

---

<!-- type: code -->

# 커스텀 NodePool 패턴 (1/2)

**목적을 먼저 고르고 YAML을 펼쳐 확인합니다.** HTML은 Compute / Spot / Graviton / GPU 탭이며, 아래 Memory 예제는 추가 참고입니다. 모든 예제는 앞에서 만든 `workload` NodeClass를 사용합니다.

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
        - key: eks.amazonaws.com/instance-category
          operator: In
          values: [c]
        - key: eks.amazonaws.com/instance-generation
          operator: Gt
          values: ["6"]
        - key: karpenter.sh/capacity-type
          operator: In
          values: [on-demand]
      nodeClassRef:
        group: eks.amazonaws.com
        kind: NodeClass
        name: workload
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
        - key: eks.amazonaws.com/instance-category
          operator: In
          values: [r]
        - key: eks.amazonaws.com/instance-generation
          operator: Gt
          values: ["6"]
      nodeClassRef:
        group: eks.amazonaws.com
        kind: NodeClass
        name: workload
  limits:
    memory: 2000Gi
```

### Spot

Spot을 우선 사용하고 가용 용량에 따라 On-Demand를 사용합니다. 두 유형을 허용한다고 혼합 비율이나 절감률이 보장되지는 않습니다.

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: spot-mixed
spec:
  template:
    spec:
      nodeClassRef:
        group: eks.amazonaws.com
        kind: NodeClass
        name: workload
      requirements:
        - key: eks.amazonaws.com/instance-category
          operator: In
          values: [m, c, r]
        - key: eks.amazonaws.com/instance-generation
          operator: Gt
          values: ["5"]
        - key: karpenter.sh/capacity-type
          operator: In
          values: [spot, on-demand]
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
```

### Graviton

arm64 이미지 또는 multi-arch 이미지가 필요합니다. 라이브러리 호환성과 앱의 비용·성능을 측정합니다.

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: graviton
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
          values: [arm64]
        - key: eks.amazonaws.com/instance-category
          operator: In
          values: [m, c, r]
        - key: eks.amazonaws.com/instance-generation
          operator: Gt
          values: ["6"]
  limits:
    cpu: 2000
```

<!-- notes: {timing: 2min} [요약] 앱 요구를 먼저 고르고 조건을 읽습니다. Compute는 CPU 중심, Spot은 중단을 감수할 수 있는 작업, Graviton은 arm64 호환성을 확인합니다. 모두 workload NodeClass를 참조하며 실제 절감률이나 성능은 측정합니다. HTML에서는 YAML을 필요할 때만 펼칩니다. {cue: transition} 가속기가 필요하면 GPU 요청과 배치 조건도 확인합니다. -->

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
        - key: eks.amazonaws.com/instance-category
          operator: In
          values: [g, p]
        - key: karpenter.sh/capacity-type
          operator: In
          values: [on-demand]
      taints:
        - key: nvidia.com/gpu
          effect: NoSchedule
      nodeClassRef:
        group: eks.amazonaws.com
        kind: NodeClass
        name: workload
  limits:
    nvidia.com/gpu: 100
  disruption:
    consolidationPolicy: WhenEmpty
```

### GPU NodePool 특징

| 항목 | 설명 |
|------|------|
| **인스턴스** | G/P 계열 중 리소스·드라이버 요구에 맞게 선택 |
| **Capacity** | 이 예제는 On-Demand 선택 (Spot 자체가 금지된 것은 아님) |
| **Taint** | 배치하려면 toleration 필요. 앱의 GPU 리소스 요청도 함께 설정 |
| **Consolidation** | WhenEmpty: 빈 노드의 정리를 검토 |

> GPU 인스턴스는 비용이 높으므로 limits 설정이 중요합니다.

<!-- notes: {timing: 2min} [요약] G/P 계열을 후보로 허용하는 예시입니다. 모델 메모리·GPU 요청·지원 드라이버·가용 용량을 함께 확인합니다. On-Demand는 이 예제의 선택이며 GPU에서 Spot이 금지된 것은 아닙니다. Taint만으로 GPU 사용 앱을 식별하지 않으므로 toleration과 리소스 요청을 함께 설정합니다. {cue: transition} 선택한 조건으로 노드가 준비되는 과정을 봅니다. -->

---

<!-- type: canvas -->

# Pod Pending에서 Node Ready까지

**프로비저닝 타임라인 시뮬레이션 — 시간은 설명용 예시, SLA 아님**

타임라인 애니메이션 (0초 ~ 90초):

| 단계 | 시간 | 설명 |
|------|------|------|
| 배치 조건 확인 | 0-7초 | 스케줄되지 못한 Pod와 NodePool 조건 확인 |
| EC2 용량 요청 | 7-22초 | 조건에 맞는 노드 생성 요청 |
| 노드 준비 | 22-72초 | 부팅·초기화·kubelet 등록·Node Ready |
| 앱 실행 | 72-90초 | Scheduler가 배치한 Pod의 시작 |

**교육용 90초 예시이며 실제 시간을 보장하지 않습니다.** 개별 API 이름을 Auto Mode의 내부 구현으로 단정하지 않습니다.

<!-- notes: {timing: 2min} [요약] 배치 조건 확인, EC2 용량 요청, 노드 준비, 앱 실행의 네 단계만 따라갑니다. 부팅과 kubelet 등록은 노드 준비 안에 포함했습니다. 90초는 교육용 예시이며 실제 시간은 네트워크, 용량, 이미지 등에 따라 달라집니다. Auto Mode 내부의 특정 EC2 API 호출을 단정하지 않습니다. {cue: transition} 이제 허용 조건으로 후보를 좁혀봅니다. -->

---

<!-- type: content -->

# 조건에 맞는 후보부터 좁힙니다

**12개 이름으로 보는 필터 연습 — 실제 가격·용량 계산은 생략합니다.**

### 필터링 단계

1. **Category 필터**: m, c, r 계열만 선택
2. **Generation 필터**: 6세대 초과만 선택
3. **Size 필터**: xlarge 이상만 선택
4. **남은 후보 확인**: m7i.xlarge, m7g.xlarge, c7i.xlarge, r7i.xlarge

### 인스턴스 목록

```
t3.micro  t3.large  m5.xlarge  m6i.xlarge
m7i.large  m7i.xlarge  m7g.xlarge  c6i.large
c7i.xlarge  r7i.xlarge  g5.xlarge  p5.48xlarge
```

> 정답이 항상 Graviton 한 종류는 아닙니다. 이 예시는 amd64·arm64 모두 호환되는 앱을 가정합니다. 실제 선택은 Pod 요청량·배치 조건·가용 용량·가격도 함께 반영합니다.

<!-- notes: {timing: 2min} [요약] 후보를 좁히는 단계만 보여주는 예시이며 EC2 배치 전략을 재현하지 않습니다. 순서대로 누르면 마지막에 서로 다른 네 후보가 남습니다. arm64와 amd64 호환을 가정했으며 실제 앱은 아키텍처·리소스 요구도 확인합니다. {cue: transition} 생성한 노드를 줄일 때도 Pod가 들어갈 자리가 있어야 합니다. -->

---

<!-- type: canvas -->

# Pod를 옮길 자리가 있어야 줄입니다

**Consolidation = Pod를 재배치하고 불필요한 노드 정리**

이 예시는 모든 Pod가 남은 노드 한 대에 들어가며 PDB·교체 예산도 허용한다고 가정합니다. 실제 CPU 사용량이 낮다는 이유만으로 삭제하지 않습니다.

Consolidation 애니메이션:

개별 Pod 상자 대신 각 노드의 **Pod 개수**를 크게 표시합니다. 노드 네 대 안의 숫자가 바뀌는 순서로 재배치와 정리를 따라갑니다.

**초기 상태:**
- Node 1: 4개 Pod (40% CPU Requests) - $0.10/hr
- Node 2: 1개 Pod (10% CPU Requests) - $0.10/hr
- Node 3: 2개 Pod (20% CPU Requests) - $0.10/hr
- Node 4: 0개 Pod (0% 사용률) - $0.10/hr

**Consolidation 후:**
- Node 1: 7개 Pod (모든 Pod 통합) - $0.10/hr
- Node 2, 3, 4: 제거됨

**절감 효과: $0.30/hr**

<!-- notes: Consolidation은 저사용률 노드의 Pod를 다른 노드로 이동시키고 빈 노드를 제거하여 비용을 최적화합니다. 이 애니메이션은 4개 노드에서 1개 노드로 통합되는 과정을 보여줍니다. -->

---

<!-- type: compare -->

# 조금 싸져도 Pod를 옮길까요?

| 정책 | 판단 관점 |
|---|---|
| WhenEmpty | 실행 중인 일반 워크로드가 없는 노드를 정리 |
| WhenEmptyOrUnderutilized | Pod를 옮겨 더 저렴하게 운영할 수 있으면 통합 검토 |
| Balanced | 비용 절감과 Pod 중단 비용을 함께 평가 |

**상황 선택:** 빈 노드 / 작은 절감·큰 중단 / 큰 절감·작은 중단.

작은 절감·큰 중단에서는 Balanced가 유지하는 방향으로 판단합니다. 이는 교육용 정성 예시이며 실제 점수 계산기가 아닙니다. 실제 결정에는 배치 가능성, PDB, 교체 예산 등도 영향을 줍니다.

EKS 1.37 신규 Auto Mode 풀은 Balanced가 기본입니다. 직접 설치한 Karpenter v1.15도 기본값이 WhenEmptyOrUnderutilized이므로 명시적으로 선택합니다.

<!-- notes: {timing: 3min} [요약] WhenEmpty는 빈 노드, WhenEmptyOrUnderutilized는 가능한 비용 절감, Balanced는 절감과 중단 비용을 함께 봅니다. 작은 절감·큰 중단 버튼부터 시작해 정책 간 판단 관점을 비교하세요. 이어서 빈 노드, 큰 절감·작은 중단을 선택합니다. 이 화면은 실제 점수 계산기를 재현한 것이 아니라 판단 관점을 설명하는 정성 예시입니다. 실제 스케줄링 제약과 PDB·예산 확인은 여전히 필요합니다. {cue: transition} 비용 정리와 별도로 새 설정을 반영하는 Drift를 살펴봅니다. -->

---

<!-- type: timeline -->

# Drift 감지와 교체

**기존 노드가 원하는 설정과 맞지 않으면 교체를 검토합니다.**

모든 변경이 Drift를 유발하지는 않습니다. `limits`, `weight`, `disruption.*` 변경은 Drift 대상이 아니며, 요구사항의 허용 범위를 넓혀도 기존 노드가 계속 맞을 수 있습니다.

### Drift 교체 흐름

1. **NodePool/NodeClass 변경** - 설정 변경 적용
2. **Drift 감지** - Karpenter가 변경 감지
3. **신규 노드 프로비저닝** - 새 설정으로 노드 생성
4. **Pod 이동** - 기존 노드에서 새 노드로 이동
5. **구 노드 종료** - 이전 노드 정리

### Drift 발생 조건

- AWS 관리 AMI 업데이트 또는 NodeClass 설정 변경
- 인스턴스 타입 요구사항 변경
- Subnet/SecurityGroup 변경
- ephemeralStorage 설정 변경

### 교체 중단 제어

- PodDisruptionBudget 준수
- Disruption Budget 적용
- 점진적 롤링: 설정한 예산 범위에서 교체
- 만료·Spot 회수와 종료 유예 기한은 PDB·예산만으로 막을 수 없음

<!-- notes: {timing: 2min} [요약] Drift는 기존 노드와 원하는 설정의 차이입니다. AMI 변경을 예로 들되 limits, weight, disruption 같은 정책 변경은 Drift를 유발하지 않는다고 구분합니다. 요구사항을 넓혀도 기존 노드가 계속 맞을 수 있습니다. 교체가 필요한 경우 PDB와 NodePool 예산을 확인합니다. {cue: transition} 다음에서 동시에 바꿀 수 있는 노드 수를 계산합니다. -->

---

<!-- type: content -->

# 한 번에 몇 대까지 바꿀까요?

**NodePool 예산은 노드 수, PDB는 앱의 Pod 중단을 제어합니다.** Drift 교체 예시에서 10대 × 10% = 한 번에 최대 1대입니다.

**안전한 노드 교체를 위한 제한 설정**

### 설정 파라미터

- **Total Nodes**: 전체 노드 수
- **Budget Percentage**: 동시 교체 가능한 노드 비율 (예: 10%)
- **Min Retained (시뮬레이터 입력)**: 유지할 노드 수를 중단 상한으로 환산
- 비율 예산은 올림(ceil), 여러 예산은 최솟값 적용. 실제로는 삭제 중·NotReady 노드 수도 차감

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
      # 업무 시간 예시: 평일 09:00–17:00 UTC에 자발적 교체 중지
      - nodes: "0"
        schedule: "0 9 * * 1-5"
        duration: 8h
```

<!-- notes: Disruption Budget은 노드 교체 시 동시에 중단될 수 있는 노드 수를 제한합니다. 비율 또는 고정 수로 설정할 수 있으며, Business Hours 동안은 교체를 제한하는 스케줄도 설정할 수 있습니다. -->

---

<!-- type: checklist -->

# 스케일링 속도 최적화 팁

**프로비저닝 시간 단축을 위한 Best Practices**

- [x] **관리형 AMI 교체 확인** - AWS가 AMI 선택·패치 관리
- [x] **ephemeralStorage 크기 설정** - 이미지·로그 용량에 맞게 구성
- [x] **다양한 인스턴스 타입 허용** - 가용성 향상, 빠른 프로비저닝
- [x] **Pod Topology Spread 설정** - 워크로드 분산, 안정성 향상
- [x] **PriorityClass로 중요 워크로드 우선** - Preemption 활용
- [x] **Disruption Budget으로 안전한 교체** - 서비스 중단 최소화

<!-- notes: 스케일링 속도를 최적화하기 위한 Best Practice입니다. Auto Mode의 AMI는 AWS가 관리하며 임의 선택하지 않습니다. ephemeralStorage 크기는 이미지와 로그 용량에 맞춰 정합니다. 다양한 인스턴스 타입을 허용하면 가용성이 높아져 빠르게 프로비저닝됩니다. -->

---

<!-- type: quiz -->

# 세 가지 상황으로 확인해 봅시다

한 상황씩 탭으로 열고 선택 후 해설을 읽습니다. **다시 풀기**로 재도전할 수 있습니다.

### Auto Mode에서 팀이 직접 정해야 하는 것은?

- [x] 앱의 CPU·메모리 요청량과 중단 허용 범위
- [ ] 관리형 Karpenter의 Helm 버전
- [ ] 노드의 AL2023 AMI 선택

**해설:** AWS가 노드를 관리해도 앱의 요청량, 배치 조건, PDB 같은 가용성 정책은 팀이 설계합니다.

### Spot을 허용하는 조건과 subnet 설정은 어디에 둘까요?

- [ ] 둘 다 Pod 이미지에 설정
- [x] Spot 조건은 NodePool, subnet은 NodeClass
- [ ] Spot 조건은 NodeClass, subnet은 NodePool

**해설:** NodePool은 어떤 노드를 허용할지, NodeClass는 AWS에서 어떻게 만들지를 정합니다.

### 절감은 작은데 Pod 재시작 영향은 큽니다. 무엇을 검토할까요?

- [x] Balanced로 절감과 중단 비용을 함께 평가
- [ ] CPU 사용량만 보고 모든 노드를 삭제
- [ ] PDB를 삭제해 강제로 비용 절감

**해설:** Balanced의 판단 관점에 맞는 상황입니다. 실제 결정은 배치 가능성과 PDB·교체 예산 등도 확인해야 합니다.

<!-- notes: {timing: 3min} [요약] 정답은 1번, 2번, 1번 선택지입니다. 버전 숫자를 외웠는지보다 운영 책임, NodePool/NodeClass의 역할, Balanced의 판단 관점을 확인합니다. 한 상황씩 탭을 열고 먼저 이유를 말하게 한 뒤 답을 고르세요. {cue: transition} 이제 운영 중 노드가 바뀌었을 때 확인하는 순서로 넘어갑니다. -->
