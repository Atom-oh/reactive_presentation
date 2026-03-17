---
remarp: true
block: scaling-strategy
---

# Scaling Strategy — Karpenter & KEDA
Block 03 (25 min)

@type: cover
@background: ../common/pptx-theme/images/Picture_13.png
@badge: ../common/pptx-theme/images/Picture_8.png

오준석 (Junseok Oh)
Sr. Solutions Architect | AWS

:::notes
{timing: 30s}
Block 03에서는 EKS 환경의 스케일링 전략을 다룹니다.
Karpenter를 통한 노드 프로비저닝과 KEDA를 통한 이벤트 기반 Pod 스케일링을 학습합니다.
:::

---

## Scaling Pain Point

@type: content
@class: pain-quote

> "노드/Pod 스케일링 전략 수립이 어려움"
>
> — ECS에서는 Auto Scaling이 간단했는데, EKS는 노드 그룹, HPA, VPA, Cluster Autoscaler 등 옵션이 너무 많습니다. 어떤 조합이 최적인지 모르겠습니다.

**화해 현황**:
- Cluster Autoscaler 사용 중 — 스케일 아웃에 5-7분 소요
- 노드 그룹 10개 이상 관리 복잡성
- Spot Instance 활용률 낮음 (비용 최적화 기회 상실)

:::notes
{timing: 2min}
화해 팀이 겪고 있는 스케일링 관련 Pain Point입니다.
Cluster Autoscaler는 노드 그룹 기반으로 동작하기 때문에 스케일링 속도가 느리고, 인스턴스 유형 선택이 제한적입니다.
오늘 다룰 Karpenter와 KEDA를 도입하면 이러한 문제를 대부분 해결할 수 있습니다.
:::

---

## Cluster Autoscaler vs Karpenter

@type: compare

### Cluster Autoscaler
- 노드 그룹 기반 스케일링
- ASG(Auto Scaling Group) 의존
- 스케일링 속도: **분 단위** (5-10분)
- 인스턴스 유형: 노드 그룹별 고정
- Bin-packing 효율: 중간
- 구성 복잡도: 노드 그룹 수에 비례

### Karpenter
- 워크로드 요구사항 기반 스케일링
- EC2 Fleet API 직접 호출
- 스케일링 속도: **초 단위** (30-60초)
- 인스턴스 유형: 동적 선택 (최적 매칭)
- Bin-packing 효율: 높음 (비용 30-50% 절감)
- 구성 복잡도: NodePool 1-2개로 단순화

:::notes
{timing: 2min}
Karpenter는 AWS에서 개발한 차세대 노드 오토스케일러입니다.
가장 큰 차이점은 노드 그룹 없이 Pod 요구사항을 직접 분석해서 최적의 인스턴스를 선택한다는 점입니다.
예를 들어 GPU Pod가 pending 상태가 되면, Karpenter는 해당 Pod의 리소스 요청, tolerations, node selectors를 분석해서 적합한 GPU 인스턴스를 즉시 프로비저닝합니다.
:::

---

## Karpenter Architecture

@type: canvas
@canvas-id: karpenter-arch

:::canvas
# Step 1: Pending Pod 발생
box pending "Pending Pod" at 50,180 size 100,50 color #f44336 step 1
icon pod "Pod" at 90,120 size 40 step 1

# Step 2: Karpenter Controller 감지
box controller "Karpenter Controller" at 220,180 size 140,50 color #FF9900 step 2
arrow pending -> controller "Watch" step 2

# Step 3: NodePool 평가
box nodepool "NodePool" at 420,100 size 120,50 color #6c5ce7 step 3
box ec2class "EC2NodeClass" at 420,180 size 120,50 color #6c5ce7 step 3
arrow controller -> nodepool "Evaluate" step 3
arrow controller -> ec2class "" step 3

# Step 4: EC2 Fleet API 호출
box ec2api "EC2 Fleet API" at 620,180 size 120,50 color #FF9900 step 4
arrow nodepool -> ec2api "Launch" style dashed step 4

# Step 5: Node 생성 및 Pod 스케줄링
box node "New Node" at 820,180 size 100,50 color #4CAF50 step 5
icon ec2 "EC2" at 860,120 size 40 step 5
arrow ec2api -> node "Provision" step 5
arrow node -> pending "Schedule" color #4CAF50 style dashed step 5
:::

:::notes
{timing: 2.5min}
Karpenter의 동작 흐름입니다.
Step 1: 스케줄링할 수 없는 Pending Pod가 발생합니다.
Step 2: Karpenter Controller가 이를 감지합니다.
Step 3: NodePool과 EC2NodeClass를 평가하여 요구사항을 분석합니다.
Step 4: EC2 Fleet API를 직접 호출하여 최적의 인스턴스를 선택합니다. ASG를 거치지 않아서 빠릅니다.
Step 5: 노드가 프로비저닝되고 Pending Pod가 스케줄링됩니다.
전체 과정이 30-60초 내에 완료됩니다.
:::

---

## NodePool 설정

@type: code

```yaml {filename="nodepool.yaml" highlight="8-16,21-23"}
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: default
spec:
  template:
    spec:
      requirements:
        # Spot + On-Demand 혼합
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]
        # 다양한 인스턴스 패밀리
        - key: karpenter.k8s.aws/instance-family
          operator: In
          values: ["m5", "m6i", "m6a", "c5", "c6i", "r5", "r6i"]
        # 아키텍처
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64"]
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: default
  # 리소스 제한
  limits:
    cpu: 1000
    memory: 1000Gi
  # Disruption 정책
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 1m
```

:::notes
{timing: 2min}
NodePool 설정 예시입니다.
핵심 포인트:
1. capacity-type에 spot과 on-demand를 모두 포함하여 Spot 우선, On-Demand 폴백 전략을 구현합니다.
2. instance-family를 다양하게 지정하면 Karpenter가 가용성과 가격을 고려해 최적의 인스턴스를 선택합니다.
3. disruption.consolidationPolicy를 WhenEmptyOrUnderutilized로 설정하면 유휴 노드를 자동으로 정리합니다.
:::

---

## Karpenter Consolidation

@type: canvas
@canvas-id: consolidation

:::canvas
# Step 1: 3개의 저활용 노드
box node1 "Node 1\n30% used" at 80,150 size 120,80 color #FF9900 step 1
box node2 "Node 2\n25% used" at 250,150 size 120,80 color #FF9900 step 1
box node3 "Node 3\n20% used" at 420,150 size 120,80 color #FF9900 step 1

# Step 2: Consolidation 트리거
box trigger "Consolidation\nTrigger" at 250,280 size 120,50 color #6c5ce7 step 2
arrow node1 -> trigger "" style dashed step 2
arrow node2 -> trigger "" style dashed step 2
arrow node3 -> trigger "" style dashed step 2

# Step 3: Pod 마이그레이션
box migrate "Pod Migration" at 550,280 size 120,50 color #3B48CC step 3
arrow trigger -> migrate "drain" step 3

# Step 4: 1개의 최적화된 노드
box optnode "Optimized Node\n85% used" at 700,150 size 140,80 color #4CAF50 step 4
arrow migrate -> optnode "schedule" step 4
:::

**비용 절감 효과**: 노드 3개 → 1개 = **67% 비용 절감**

:::notes
{timing: 2min}
Karpenter의 Consolidation 기능입니다.
저활용 노드들을 자동으로 감지하고, Pod를 마이그레이션한 후 빈 노드를 종료합니다.
이 예시에서는 30%, 25%, 20% 활용률의 노드 3개가 85% 활용률의 노드 1개로 통합됩니다.
중요한 점은 PDB(PodDisruptionBudget)를 준수하면서 안전하게 마이그레이션한다는 것입니다.
:::

---

## Spot Instance 전략

@type: tabs

### Spot 중단 처리
```yaml
# Karpenter가 자동으로 처리
# 1. Spot 중단 알림 감지 (2분 전)
# 2. 새 노드 프로비저닝 시작
# 3. Pod graceful 마이그레이션
# 4. 서비스 영향 최소화

# EC2NodeClass에서 interruption 처리 설정
apiVersion: karpenter.k8s.aws/v1
kind: EC2NodeClass
spec:
  # Spot 중단 처리 자동 활성화
  # Node Termination Handler 불필요
```

### 다각화 전략
```yaml
# 다양한 인스턴스 패밀리로 Spot 가용성 확보
requirements:
  - key: karpenter.k8s.aws/instance-family
    operator: In
    values:
      - m5    # 범용 5세대
      - m6i   # 범용 6세대 Intel
      - m6a   # 범용 6세대 AMD
      - c5    # 컴퓨팅 최적화
      - c6i   # 컴퓨팅 최적화 6세대
      - r5    # 메모리 최적화
```

### Capacity Type 우선순위
```yaml
# Spot 우선, On-Demand 폴백
requirements:
  - key: karpenter.sh/capacity-type
    operator: In
    values: ["spot", "on-demand"]

# Karpenter 동작:
# 1. Spot 인스턴스 먼저 시도
# 2. Spot 용량 부족 시 On-Demand로 자동 전환
# 3. 비용: Spot 평균 60-70% 할인
```

:::notes
{timing: 2min}
Spot Instance 전략의 핵심 3가지입니다.
첫째, Karpenter는 Spot 중단 알림을 자동으로 처리합니다. 별도의 Node Termination Handler가 필요 없습니다.
둘째, 다양한 인스턴스 패밀리를 지정하면 Spot 용량 풀이 넓어져서 중단 확률이 낮아집니다.
셋째, capacity-type에 spot과 on-demand를 함께 지정하면 Spot 우선, On-Demand 폴백 전략이 자동으로 적용됩니다.
:::

---

## PDB 설정

@type: code

```yaml {filename="pdb-topology.yaml" highlight="6-8,19-27"}
# PodDisruptionBudget
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb
spec:
  minAvailable: 2          # 최소 2개 Pod 유지
  # 또는 maxUnavailable: 1  # 동시 1개만 중단
  selector:
    matchLabels:
      app: api-server
# ---
# Topology Spread Constraints
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      topologySpreadConstraints:
        # AZ 분산 (Hard)
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: api-server
          minDomains: 2    # 최소 2개 AZ
```

:::notes
{timing: 2min}
PDB와 TopologySpreadConstraints는 함께 사용해야 효과적입니다.
PDB는 Karpenter consolidation이나 노드 업그레이드 시 최소 가용 Pod 수를 보장합니다.
TopologySpreadConstraints는 Pod가 여러 AZ에 분산되도록 강제합니다.
minDomains: 2는 최소 2개 AZ에 Pod가 배포되어야 스케줄링된다는 의미입니다.
이 조합으로 단일 AZ 장애 시에도 서비스 연속성을 보장합니다.
:::

---

## KEDA Architecture

@type: canvas
@canvas-id: keda-arch

:::canvas
# Step 1: ScaledObject 정의
box scaleobj "ScaledObject" at 50,180 size 120,50 color #6c5ce7 step 1

# Step 2: KEDA가 HPA 생성
box keda "KEDA Operator" at 230,180 size 120,50 color #FF9900 step 2
box hpa "HPA" at 230,280 size 120,50 color #326CE5 step 2
arrow scaleobj -> keda "define" step 2
arrow keda -> hpa "create" step 2

# Step 3: External Metrics 수집
box metrics "External Metrics\nServer" at 430,180 size 140,50 color #FF9900 step 3
box trigger "Triggers\n(SQS, Prometheus...)" at 430,280 size 140,50 color #3B48CC step 3
arrow hpa -> metrics "query" step 3
arrow trigger -> metrics "poll" step 3

# Step 4: Deployment 스케일링
box deploy "Deployment" at 650,180 size 120,50 color #326CE5 step 4
arrow hpa -> deploy "scale" step 4
:::

**핵심 차별점**: HPA는 CPU/Memory만, KEDA는 **50+ 이벤트 소스** 기반 스케일링

:::notes
{timing: 2min}
KEDA(Kubernetes Event-driven Autoscaling) 아키텍처입니다.
KEDA는 Kubernetes HPA를 확장하여 다양한 이벤트 소스 기반 스케일링을 지원합니다.
ScaledObject를 정의하면 KEDA가 자동으로 HPA를 생성하고, External Metrics Server를 통해 외부 메트릭을 수집합니다.
가장 큰 장점은 HPA가 지원하지 않는 SQS 큐 길이, Kafka lag, Prometheus 메트릭 등을 스케일링 트리거로 사용할 수 있다는 점입니다.
:::

---

## KEDA Scalers

@type: tabs

### SQS Scaler
```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: sqs-scaler
spec:
  scaleTargetRef:
    name: order-processor
  minReplicaCount: 0      # Zero scaling 가능!
  maxReplicaCount: 50
  triggers:
    - type: aws-sqs-queue
      metadata:
        queueURL: https://sqs.ap-northeast-2.amazonaws.com/123456789/orders
        queueLength: "5"  # 메시지 5개당 Pod 1개
        awsRegion: ap-northeast-2
```

### Prometheus Scaler
```yaml
triggers:
  - type: prometheus
    metadata:
      serverAddress: http://prometheus:9090
      metricName: http_requests_per_second
      threshold: "100"      # RPS 100 초과 시 스케일 아웃
      query: |
        sum(rate(http_requests_total{
          service="api-gateway"
        }[1m]))
```

### Cron Scaler
```yaml
triggers:
  - type: cron
    metadata:
      timezone: Asia/Seoul
      start: 0 9 * * 1-5   # 평일 09:00
      end: 0 18 * * 1-5    # 평일 18:00
      desiredReplicas: "10" # 업무시간 10개 유지
```

### CloudWatch Scaler
```yaml
triggers:
  - type: aws-cloudwatch
    metadata:
      namespace: AWS/ApplicationELB
      dimensionName: LoadBalancer
      dimensionValue: app/my-alb/1234567890
      metricName: RequestCount
      targetValue: "1000"
      awsRegion: ap-northeast-2
```

:::notes
{timing: 2min}
KEDA가 지원하는 주요 Scaler들입니다.
SQS Scaler: 큐에 쌓인 메시지 수에 따라 Consumer Pod를 스케일링합니다. minReplicaCount: 0으로 Zero Scaling도 가능합니다.
Prometheus Scaler: PromQL 쿼리 결과를 기반으로 스케일링합니다. RPS, Latency 등 커스텀 메트릭 활용이 가능합니다.
Cron Scaler: 예측 가능한 트래픽 패턴에 맞춰 미리 스케일 아웃할 수 있습니다.
CloudWatch Scaler: AWS 메트릭을 직접 활용한 스케일링이 가능합니다.
:::

---

## KEDA + Istio Metrics

@type: code

```yaml {filename="keda-istio.yaml" highlight="11-17"}
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: istio-rps-scaler
spec:
  scaleTargetRef:
    name: api-server
  minReplicaCount: 2
  maxReplicaCount: 20
  triggers:
    - type: prometheus
      metadata:
        serverAddress: http://prometheus.istio-system:9090
        metricName: istio_requests_per_second
        threshold: "50"    # Pod당 RPS 50 유지
        query: |
          sum(rate(istio_requests_total{
            destination_service="api-server.production.svc.cluster.local",
            response_code!~"5.*"
          }[1m])) /
          count(kube_pod_info{
            namespace="production",
            pod=~"api-server-.*"
          })
```

**장점**: Istio 메트릭으로 **실제 트래픽 기반** 스케일링 (CPU 기반보다 정확)

:::notes
{timing: 2min}
Istio 메트릭을 활용한 KEDA 스케일링 예시입니다.
istio_requests_total 메트릭에서 5xx 에러를 제외한 성공 요청만 카운트합니다.
현재 Pod 수로 나누어 Pod당 RPS를 계산하고, 이를 threshold와 비교하여 스케일링합니다.
CPU 기반 스케일링보다 실제 트래픽을 반영하므로 더 정확한 스케일링이 가능합니다.
:::

---

## Batch & Schedule 워크로드 패턴

@type: tabs

### Kubernetes CronJob
**기본 패턴: CronJob으로 배치 스케줄링**
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-report
  namespace: batch
spec:
  schedule: "0 2 * * *"        # 매일 02:00 KST
  timeZone: "Asia/Seoul"
  concurrencyPolicy: Forbid     # 중복 실행 방지
  jobTemplate:
    spec:
      backoffLimit: 3
      activeDeadlineSeconds: 3600
      template:
        spec:
          serviceAccountName: batch-runner
          containers:
            - name: report
              image: hwahae/daily-report:latest
              resources:
                requests:
                  cpu: "1"
                  memory: "2Gi"
          restartPolicy: Never
          nodeSelector:
            karpenter.sh/capacity-type: spot
```

**장점**: 단순, K8s 네이티브, CronJob 내장 스케줄러
**적합**: 단일 작업, 의존성 없는 배치

### Airflow + KubernetesExecutor
**패턴: Airflow UI + Pod 런타임**
```
Airflow Webserver (Deployment)
    ↓
Airflow Scheduler (Deployment)
    ↓ DAG 트리거
KubernetesExecutor
    ↓ Pod 생성
Task Pod (Ephemeral)
    ↓ 실행 완료
Pod 삭제 → 리소스 회수
```

**핵심 설정**:
```yaml
# airflow.cfg (Helm values)
executor: KubernetesExecutor
kubernetes_executor:
  namespace: airflow-tasks
  worker_container_image_pull_policy: Always
  delete_worker_pods: True
  delete_worker_pods_on_failure: False  # 실패 시 디버깅용
```

**장점**: DAG 의존성 관리, UI 제공, 복잡한 워크플로우
**적합**: ETL 파이프라인, ML 학습, 다단계 배치

### Jenkins + Kubernetes Plugin
**패턴: Jenkins UI + 동적 Agent Pod**
```groovy
// Jenkinsfile
pipeline {
  agent {
    kubernetes {
      yaml '''
        apiVersion: v1
        kind: Pod
        spec:
          containers:
          - name: gradle
            image: gradle:8-jdk17
            resources:
              requests:
                cpu: "2"
                memory: "4Gi"
          nodeSelector:
            karpenter.sh/capacity-type: spot
      '''
    }
  }
  stages {
    stage('Build') {
      steps {
        container('gradle') {
          sh 'gradle build'
        }
      }
    }
  }
}
```

**장점**: 기존 Jenkins 파이프라인 재활용, 동적 리소스 할당
**적합**: CI/CD 빌드, 기존 Jenkins 사용 팀

### KEDA + Batch 조합
**패턴: KEDA Cron Scaler로 예측 스케일링**
```yaml
# 업무시간에 배치 처리 Worker 미리 확보
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: batch-worker-scaler
spec:
  scaleTargetRef:
    name: batch-worker
  minReplicaCount: 0           # 비업무시간 Zero Scale
  maxReplicaCount: 20
  triggers:
    # SQS 기반 동적 스케일링
    - type: aws-sqs-queue
      metadata:
        queueURL: https://sqs.../batch-jobs
        queueLength: "3"
    # 업무시간 최소 Pod 확보
    - type: cron
      metadata:
        timezone: Asia/Seoul
        start: 0 9 * * 1-5
        end: 0 22 * * 1-5
        desiredReplicas: "3"
```

**장점**: SQS 큐 기반 + 시간 기반 하이브리드, Zero Scaling으로 비용 최적화

:::notes
{timing: 3min}
EKS에서 Batch/Schedule 워크로드를 운영하는 4가지 패턴입니다. CronJob은 단순 배치에 적합하고, Airflow는 복잡한 DAG 워크플로우에 적합합니다. Jenkins는 기존 파이프라인을 재활용할 때 유용합니다. KEDA + Batch 조합은 SQS 큐 기반 동적 스케일링과 Zero Scaling을 결합하여 비용을 최적화합니다. 화해의 경우 현재 Jenkins를 CI에 사용하고 있으므로, 빌드는 Jenkins + Kubernetes Plugin으로, ETL 배치는 Airflow KubernetesExecutor로, 단순 스케줄 작업은 CronJob으로 분류하면 됩니다.
:::

---

## Batch 전용 Karpenter NodePool

@type: code

```yaml {filename="batch-nodepool.yaml" highlight="8-14,22-25"}
# Batch 전용 NodePool — Spot 최적화
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: batch
spec:
  template:
    metadata:
      labels:
        workload-type: batch
    spec:
      requirements:
        # Batch는 Spot Only (비용 최적화)
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot"]
        # 컴퓨팅 최적화 패밀리
        - key: karpenter.k8s.aws/instance-family
          operator: In
          values: ["c5", "c5a", "c6i", "c6a", "c7i", "c7a"]
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64", "arm64"]
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: batch
      # Batch Pod 완료 후 빠른 노드 회수
      expireAfter: 2h
  limits:
    cpu: 200
  disruption:
    consolidationPolicy: WhenEmpty
    consolidateAfter: 30s       # 빈 노드 30초 후 즉시 정리
```

```yaml {filename="batch-pod-example.yaml"}
# Batch Pod에 Toleration + NodeSelector 추가
spec:
  nodeSelector:
    workload-type: batch
  tolerations:
    - key: workload-type
      value: batch
      effect: NoSchedule
```

**효과**: Batch 완료 후 노드 자동 회수 → 유휴 비용 0원

:::notes
{timing: 2min}
Batch 워크로드 전용 Karpenter NodePool 설정입니다. Spot Instance만 사용하여 비용을 최적화하고, expireAfter: 2h로 장기 실행 방지, consolidateAfter: 30s로 빈 노드를 즉시 정리합니다. Batch Pod에는 nodeSelector와 toleration을 추가하여 전용 노드에만 스케줄링되도록 합니다. 이렇게 하면 Batch 워크로드가 Service 워크로드의 리소스를 침범하지 않고, 완료 후 노드가 자동으로 회수되어 비용이 최적화됩니다.
:::

---

## HPA → Karpenter → KEDA 도입 로드맵

@type: timeline

### Phase 1 (Week 1-2)
Karpenter 설치 및 NodePool 구성
기존 Cluster Autoscaler와 병행 운영
테스트 워크로드로 검증

### Phase 2 (Week 3-4)
Cluster Autoscaler 제거
Karpenter Consolidation 활성화
Spot Instance 비율 확대

### Phase 3 (Week 5-6)
KEDA 설치
SQS 기반 워커 스케일링 적용
Prometheus 메트릭 연동

### Phase 4 (Week 7-8)
Istio 메트릭 기반 스케일링
Cron 스케일러로 예측 스케일링
Zero Scaling 적용 (비용 최적화)

:::notes
{timing: 2min}
단계적 도입 로드맵입니다.
Phase 1-2에서 Karpenter를 도입하고 기존 Cluster Autoscaler를 제거합니다.
Phase 3-4에서 KEDA를 도입하여 이벤트 기반 스케일링을 구현합니다.
각 단계에서 충분한 검증 기간을 두고, 문제 발생 시 롤백할 수 있도록 합니다.
전체 8주 소요되며, 완료 후 30-50% 비용 절감을 기대할 수 있습니다.
:::

---

## Block 03 Quiz

@type: quiz

**Q1: Karpenter가 Cluster Autoscaler보다 빠른 이유는?**
- [ ] 더 많은 CPU를 사용해서
- [x] ASG를 거치지 않고 EC2 Fleet API를 직접 호출해서
- [ ] 미리 노드를 프로비저닝해두기 때문에
- [ ] AWS 전용 서비스이기 때문에

**Q2: Karpenter Consolidation의 목적은?**
- [ ] 노드 수를 최대화하여 가용성 확보
- [ ] Pod를 균등하게 분산
- [x] 저활용 노드를 통합하여 비용 절감
- [ ] Spot Instance 중단 방지

**Q3: KEDA의 가장 큰 장점은?**
- [ ] HPA보다 빠른 스케일링 속도
- [x] 50+ 이벤트 소스 기반 스케일링과 Zero Scaling 지원
- [ ] Kubernetes 기본 내장 기능
- [ ] 노드 레벨 스케일링 지원

**Q4: Spot Instance 다각화 전략이 중요한 이유는?**
- [ ] 비용을 더 절감하기 위해
- [ ] 성능을 향상시키기 위해
- [x] Spot 용량 풀을 넓혀 중단 확률을 낮추기 위해
- [ ] 관리를 단순화하기 위해

:::notes
{timing: 3min}
Q1: Karpenter는 ASG 없이 EC2 Fleet API를 직접 호출하므로 30-60초 내 프로비저닝이 가능합니다.
Q2: Consolidation은 저활용 노드를 통합하여 리소스 활용률을 높이고 비용을 절감합니다.
Q3: KEDA는 SQS, Kafka, Prometheus 등 다양한 이벤트 소스 기반 스케일링과 Zero Scaling을 지원합니다.
Q4: 다양한 인스턴스 패밀리를 사용하면 Spot 용량 풀이 넓어져 중단 위험이 분산됩니다.
:::
