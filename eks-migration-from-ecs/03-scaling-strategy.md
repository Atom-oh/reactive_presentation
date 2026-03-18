---
remarp: true
block: scaling-strategy
---
@type: cover
@background: common/pptx-theme/images/Picture_13.png
@badge: common/pptx-theme/images/Picture_8.png

# ECS → EKS Migration Deep Dive

Scaling Strategy — Karpenter & KEDA (25 min)

**오준석 (Junseok Oh)**
Sr. Solutions Architect, AWS
화해 글로벌

:::notes
{timing: 1min}
Block 03에서는 EKS 환경의 스케일링 전략을 다룹니다.
Karpenter를 통한 노드 프로비저닝과 KEDA를 통한 이벤트 기반 Pod 스케일링을 학습합니다.

💬 예상 질문:
• Karpenter와 KEDA를 동시에 도입해야 하나요? → 아니요, Karpenter(노드 스케일링)부터 도입하고 안정화 후 KEDA(Pod 스케일링)를 추가하는 것을 권장합니다.
:::

---
@type: content

## Scaling Pain Point

> "노드/Pod 스케일링 전략 수립이 어려움"

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

💬 예상 질문:
• Cluster Autoscaler에서 5-7분 걸리는 이유가 뭔가요? → ASG 스케일링 → EC2 프로비저닝 → 노드 등록 → Pod 스케줄링 단계를 거치기 때문입니다. 각 단계에서 polling interval과 대기 시간이 누적됩니다.
:::

---
@type: compare

## Cluster Autoscaler vs Karpenter

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
{timing: 3min}
{cue: pause}
Karpenter는 AWS에서 개발한 차세대 노드 오토스케일러입니다.
가장 큰 차이점은 노드 그룹 없이 Pod 요구사항을 직접 분석해서 최적의 인스턴스를 선택한다는 점입니다.

💬 예상 질문:
• 왜 Usage가 아닌 Requests 기준인가요? → Requests는 예약된 리소스이므로 다른 Pod가 사용할 수 없습니다. Usage가 낮아도 Requests가 높으면 실제로 활용할 수 있는 용량이 없습니다.
:::

---
@type: canvas

## Grafana: EKS Node Monitoring

CPU Requests vs Usage — Karpenter 판단 기준 시각화

<canvas id="dashboard-canvas"></canvas>

<div class="btn-group" style="justify-content: center; position: absolute; bottom: 4px; left: 0; right: 0; z-index: 10;">
  <button class="btn" id="btn-add-node">노드 추가</button>
  <button class="btn" id="btn-add-workload">워크로드 추가</button>
  <button class="btn" style="border-color: #f39c12; color: #f39c12;" id="btn-remove-workload">워크로드 삭제</button>
  <button class="btn" style="border-color: #e17055; color: #e17055;" id="btn-spot-interrupt">Spot 인터럽트</button>
  <button class="btn" style="border-color: #fdcb6e; color: #fdcb6e;" id="btn-consolidation">Consolidation</button>
  <button class="btn btn-sm" id="btn-reset">Reset</button>
</div>

:::notes
{timing: 3min}
Grafana Node Monitoring 대시보드입니다. Karpenter가 노드 스케일링 결정을 내리는 기준을 시각화합니다.

버튼별 시나리오:
• 노드 추가: 새 EC2 인스턴스가 프로비저닝되어 클러스터에 추가됩니다.
• 워크로드 추가: 모든 노드에 Pod가 배포되어 CPU Requests가 증가합니다. Usage보다 Requests가 더 많이 증가하는 over-allocation 패턴을 보여줍니다.
• 워크로드 삭제: 일부 노드의 워크로드가 감소하여 Low Req 상태가 됩니다.
• Spot 인터럽트: Spot 노드에 ITN(Interruption Notice)이 발생하고, Karpenter가 자동으로 Cordon → Drain → 새 노드 프로비저닝 → Pod 재스케줄링 과정을 진행합니다.
• Consolidation: Low Req 노드를 감지하여 Pod를 다른 노드로 이동시키고 해당 노드를 종료합니다.

핵심 포인트: Karpenter는 CPU Usage가 아닌 CPU Requests를 기준으로 Consolidation을 결정합니다. 차트의 gap(Requests - Usage)이 클수록 리소스 낭비가 발생하고 있다는 의미입니다.

💬 예상 질문:
• 왜 Usage가 아닌 Requests 기준인가요? → Requests는 예약된 리소스이므로 다른 Pod가 사용할 수 없습니다. Usage가 낮아도 Requests가 높으면 실제로 활용할 수 있는 용량이 없습니다.
:::

---
@type: code

## NodePool 설정

```yaml {filename="nodepool.yaml" highlight="7-15,20-22"}
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
{timing: 2.5min}
NodePool 설정 예시입니다.
핵심 포인트:
1. capacity-type에 spot과 on-demand를 모두 포함하여 Spot 우선, On-Demand 폴백 전략을 구현합니다.
2. instance-family를 다양하게 지정하면 Karpenter가 가용성과 가격을 고려해 최적의 인스턴스를 선택합니다.
3. disruption.consolidationPolicy를 WhenEmptyOrUnderutilized로 설정하면 유휴 노드를 자동으로 정리합니다.

💬 예상 질문:
• NodePool을 여러 개 만들어야 하나요? → 대부분의 경우 1-2개면 충분합니다. GPU 워크로드나 특수 요구사항이 있을 때만 별도 NodePool을 만드세요.
• limits에서 cpu: 1000은 무슨 의미인가요? → 이 NodePool이 프로비저닝할 수 있는 총 vCPU 상한입니다. 예상치 못한 비용 폭증을 방지하는 안전장치입니다.
:::

---
@type: canvas

## Karpenter Consolidation

<canvas id="consolidation"></canvas>

:::notes
{timing: 2.5min}
Karpenter의 Consolidation 기능입니다.
저활용 노드들을 자동으로 감지하고, Pod를 마이그레이션한 후 빈 노드를 종료합니다.
이 예시에서는 30%, 25%, 20% 활용률의 노드 3개가 85% 활용률의 노드 1개로 통합됩니다.
중요한 점은 PDB(PodDisruptionBudget)를 준수하면서 안전하게 마이그레이션한다는 것입니다.

💬 예상 질문:
• Consolidation이 너무 자주 발생하면 서비스에 영향이 없나요? → consolidateAfter 값을 조절하여 빈도를 제어할 수 있습니다. 또한 PDB를 통해 최소 가용 Pod 수를 보장합니다.
:::

---
@type: canvas

## KEDA RPS 기반 오토스케일링

<canvas id="keda-rps-canvas"></canvas>

<div class="canvas-controls" style="margin-top:6px; display:flex; align-items:center; gap:12px;">
  <label style="font-size:.8rem; color:var(--text-secondary);">RPS:</label>
  <input type="range" id="rps-slider" min="0" max="500" value="100" step="10" style="flex:1;">
  <span id="rps-value" style="font-size:.85rem; font-weight:600; color:var(--accent-light,var(--text-accent)); min-width:36px;">100</span>
</div>

:::notes
{timing: 2.5min}
KEDA RPS 기반 오토스케일링 데모입니다. 슬라이더를 조작하며 Pod 스케일링을 시뮬레이션합니다.

핵심 개념:
• threshold: 50 RPS/pod — Pod 1개가 처리할 수 있는 요청 수입니다.
• 공식: desiredReplicas = ceil(currentRPS / threshold)
• RPS 0: Scale to Zero — 트래픽이 없으면 Pod를 0개로 줄여 비용을 절감합니다.
• RPS 100: 2개 Pod (100/50 = 2)
• RPS 500: 10개 Pod (maxReplicaCount 도달)

시나리오 시연:
1. RPS를 0으로 → Scale to Zero 상태 (보라색 상태바)
2. RPS를 점진적으로 올리며 Pod 증가 확인
3. RPS를 300 이상으로 → Gateway Slow/Error 상태와 높은 P99 Latency 확인
4. RPS를 500으로 → MAX CAPACITY 도달

실제 구현 시에는 Prometheus에서 RPS 메트릭을 수집하고, KEDA ScaledObject에서 해당 쿼리를 트리거로 설정합니다.

💬 예상 질문:
• threshold 값은 어떻게 정하나요? → 부하 테스트로 Pod당 처리 가능한 RPS를 측정 후 70-80% 수준으로 설정합니다.
• Scale to Zero의 cold start 문제는? → minReplicaCount: 1로 최소 1개는 유지하거나, Knative의 activator 패턴을 사용합니다.
:::

---
@type: canvas

## KEDA Architecture

<canvas id="keda-arch"></canvas>

:::notes
{timing: 2min}
KEDA(Kubernetes Event-driven Autoscaling) 아키텍처입니다. 단계별로 클릭하며 설명합니다.
KEDA는 Kubernetes HPA를 확장하여 다양한 이벤트 소스 기반 스케일링을 지원합니다.
ScaledObject를 정의하면 KEDA가 자동으로 HPA를 생성하고, External Metrics Server를 통해 외부 메트릭을 수집합니다.
가장 큰 장점은 HPA가 지원하지 않는 SQS 큐 길이, Kafka lag, Prometheus 메트릭 등을 스케일링 트리거로 사용할 수 있다는 점입니다.

💬 예상 질문:
• 기존 HPA가 있으면 KEDA와 충돌하나요? → 네, 같은 Deployment에 HPA와 ScaledObject를 동시에 적용하면 안 됩니다. KEDA가 HPA를 자동 생성하므로 기존 HPA는 제거하세요.
• KEDA 설치가 복잡한가요? → Helm으로 간단히 설치됩니다. helm install keda kedacore/keda 한 줄이면 됩니다.
:::

---
@type: tabs

## KEDA Scalers

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
{timing: 2.5min}
KEDA가 지원하는 주요 Scaler들입니다. 각 탭을 클릭하며 설명합니다.
SQS Scaler: 큐에 쌓인 메시지 수에 따라 Consumer Pod를 스케일링합니다. minReplicaCount: 0으로 Zero Scaling도 가능합니다.
Prometheus Scaler: PromQL 쿼리 결과를 기반으로 스케일링합니다. RPS, Latency 등 커스텀 메트릭 활용이 가능합니다.
Cron Scaler: 예측 가능한 트래픽 패턴에 맞춰 미리 스케일 아웃할 수 있습니다.
CloudWatch Scaler: AWS 메트릭을 직접 활용한 스케일링이 가능합니다.

💬 예상 질문:
• SQS Scaler에서 queueLength: 5의 의미는? → 메시지 5개당 Pod 1개를 유지한다는 의미입니다. 큐에 50개 메시지가 있으면 10개 Pod가 됩니다.
• Zero Scaling 시 cold start 문제는 없나요? → 있습니다. 첫 메시지 처리까지 Pod 시작 시간(보통 10-30초)이 걸립니다. 민감한 서비스는 minReplicaCount: 1로 설정하세요.
:::

---
@type: code

## KEDA + Istio Metrics

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

:::notes
{timing: 2min}
Istio 메트릭을 활용한 KEDA 스케일링 예시입니다.
istio_requests_total 메트릭에서 5xx 에러를 제외한 성공 요청만 카운트합니다.
현재 Pod 수로 나누어 Pod당 RPS를 계산하고, 이를 threshold와 비교하여 스케일링합니다.
CPU 기반 스케일링보다 실제 트래픽을 반영하므로 더 정확한 스케일링이 가능합니다.

💬 예상 질문:
• Istio 없이도 RPS 기반 스케일링이 가능한가요? → 네, 애플리케이션에서 Prometheus 메트릭을 직접 노출하거나, Ingress Controller 메트릭을 사용할 수 있습니다.
• threshold 값은 어떻게 정하나요? → 부하 테스트로 Pod당 처리 가능한 RPS를 측정한 후, 70-80% 수준으로 설정하세요. 너무 높으면 스케일 아웃이 늦어집니다.
:::

---
@type: tabs

## Batch & Schedule 워크로드 패턴

### Kubernetes CronJob

**기본 패턴: CronJob으로 배치 스케줄링**

```yaml {filename="cronjob.yaml"}
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

```yaml {filename="airflow.cfg (Helm values)"}
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

```groovy {filename="Jenkinsfile"}
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

```yaml {filename="keda-batch.yaml"}
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
{timing: 2.5min}
Batch 및 Schedule 워크로드 운영 패턴입니다. 4개 탭을 순서대로 설명합니다.

K8s CronJob: 단순 주기적 작업에 적합합니다. 6시간마다 DB 정리, 일일 리포트 생성 등. 복잡한 의존관계가 필요하면 한계가 있습니다.

Airflow + KubernetesExecutor: DAG 기반으로 복잡한 파이프라인을 정의하고, UI에서 실행 상태를 모니터링할 수 있습니다. ETL이나 ML 파이프라인에 적합합니다.

Jenkins + Kubernetes Plugin: 기존 Jenkins 파이프라인을 유지하면서 Agent를 동적 Pod로 운영합니다.

KEDA + Batch: SQS 기반 동적 스케일링과 Cron 기반 예측 스케일링을 조합하여 비용 최적화합니다.

💬 예상 질문:
• 기존 ECS Scheduled Task를 어떻게 마이그레이션하나요? → 단순 작업은 CronJob으로, 복잡한 워크플로우는 Airflow나 Argo Workflows로 마이그레이션하세요.
• Batch 작업이 Spot에서 중단되면 어떻게 하나요? → Job의 backoffLimit을 설정하고, 멱등성 있게 설계하세요. 체크포인트를 저장하면 재시작 시 이어서 처리 가능합니다.
:::

---
@type: code

## Batch 전용 Karpenter NodePool

```yaml {filename="batch-nodepool.yaml"}
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
Batch 전용 Karpenter NodePool 설정입니다.
Batch 워크로드는 Spot Only로 구성하여 비용을 최대한 절감합니다.
컴퓨팅 최적화(c5, c6i 등) 인스턴스 패밀리를 지정하고, arm64도 포함하여 Graviton 활용이 가능합니다.
expireAfter: 2h로 장시간 유휴 노드를 자동 정리하고, consolidateAfter: 30s로 빈 노드를 빠르게 회수합니다.

💬 예상 질문:
• Batch NodePool과 일반 NodePool을 어떻게 분리하나요? → nodeSelector와 Toleration을 사용합니다. Batch Pod에 workload-type: batch를 지정하면 해당 NodePool에만 스케줄링됩니다.
• arm64(Graviton) 사용 시 주의점은? → 컨테이너 이미지가 multi-arch로 빌드되어야 합니다. docker buildx로 amd64/arm64 모두 지원하는 이미지를 만드세요.
:::

---
@type: timeline

## HPA → Karpenter → KEDA 도입 로드맵

1. **Phase 1 (Week 1-2)**: Karpenter 설치 및 NodePool 구성 / 기존 Cluster Autoscaler와 병행 운영 / 테스트 워크로드로 검증
2. **Phase 2 (Week 3-4)**: Cluster Autoscaler 제거 / Karpenter Consolidation 활성화 / Spot Instance 비율 확대
3. **Phase 3 (Week 5-6)**: KEDA 설치 / SQS 기반 워커 스케일링 적용 / Prometheus 메트릭 연동
4. **Phase 4 (Week 7-8)**: Istio 메트릭 기반 스케일링 / Cron 스케일러로 예측 스케일링 / Zero Scaling 적용 (비용 최적화)

:::notes
{timing: 2min}
단계적 도입 로드맵입니다. 타임라인을 클릭하며 각 Phase를 설명합니다.
Phase 1-2에서 Karpenter를 도입하고 기존 Cluster Autoscaler를 제거합니다.
Phase 3-4에서 KEDA를 도입하여 이벤트 기반 스케일링을 구현합니다.
각 단계에서 충분한 검증 기간을 두고, 문제 발생 시 롤백할 수 있도록 합니다.
전체 8주 소요되며, 완료 후 30-50% 비용 절감을 기대할 수 있습니다.

💬 예상 질문:
• Cluster Autoscaler에서 Karpenter로 마이그레이션 시 다운타임이 있나요? → 병행 운영 기간을 두면 다운타임 없이 마이그레이션 가능합니다. 새 워크로드부터 Karpenter로 전환하고 점진적으로 확대하세요.
• 8주가 너무 긴 것 같은데 단축 가능한가요? → 테스트 환경이 잘 갖춰져 있다면 4-6주로 단축 가능합니다. 단, 프로덕션 적용 전 충분한 부하 테스트는 필수입니다.
:::

---
@type: quiz

## Block 03 Quiz

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

💬 예상 질문:
• 퀴즈 관련 추가 질문이 있으면 자유롭게 물어보세요. 실제 환경에서의 적용 경험이나 트러블슈팅 사례도 공유해 드릴 수 있습니다.
:::
