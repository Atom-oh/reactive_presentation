---
marp: true
title: "Block 4: VPA & Resource Optimization - EKS Auto Mode"
theme: default
paginate: true
---

<!-- block: resource-optimization -->

<!-- type: title -->
# Vertical Pod Autoscaler & Auto Mode
## VPA와 Auto Mode의 시너지 효과

<!-- notes: VPA가 Pod의 리소스 요청을 최적화하면, Auto Mode가 그에 맞는 최적의 인스턴스를 선택합니다. 이 두 가지를 조합하면 리소스 낭비 감소와 노드 비용 절감을 동시에 달성할 수 있습니다. -->

---

<!-- type: content -->
# VPA + Auto Mode 시너지

### VPA
- Pod 리소스 사용량 분석
- 최적 requests/limits 추천
- CPU/Memory 자동 조정
- 14일 히스토리 기반 분석

### Auto Mode
- 실제 Pod requests 기반 선택
- 최적 인스턴스 타입 매칭
- Bin-packing 최적화
- Consolidation 자동 수행

### Key Points
| VPA | Auto Mode | Synergy |
|-----|-----------|---------|
| Pod의 CPU/Memory 요청을 자동으로 최적화 | 최적화된 요청 기반으로 적합한 인스턴스 자동 선택 | 리소스 낭비 감소 + 노드 비용 절감 |

<!-- notes: VPA는 Pod 레벨의 최적화, Auto Mode는 노드 레벨의 최적화를 담당합니다. 두 가지가 함께 작동하면 시너지 효과가 발생합니다. -->

---

<!-- type: tabs -->
# VPA 모드 비교
## updateMode별 동작 방식과 권장 사용 사례

### Off
**Off 모드**: 추천값만 제공하고, Pod를 변경하지 않습니다. 가장 안전한 분석 모드입니다.

**장점**: Pod 재시작 없음, 안전하게 분석 가능, 프로덕션에서 먼저 테스트

**단점**: 자동 적용되지 않음, 수동 업데이트 필요

**권장 사용 사례**: 신규 워크로드 분석, 프로덕션 사전 검증, 리소스 패턴 파악

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: "Off"
```

### Initial
**Initial 모드**: Pod 생성 시에만 추천값을 적용하고, 실행 중인 Pod는 변경하지 않습니다.

**장점**: 실행 중 Pod 안정성 보장, 롤링 업데이트 시 자연스럽게 적용

**단점**: 즉시 적용되지 않음, 새 Pod 생성까지 대기 필요

**권장 사용 사례**: Stateful 워크로드, 긴 실행 배치 작업, 재시작에 민감한 서비스

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: "Initial"
```

### Recreate
**Recreate 모드**: 추천값이 변경되면 Pod를 재생성하여 적용합니다. 잠시 다운타임이 발생할 수 있습니다.

**장점**: 즉시 최적화 적용, 리소스 효율성 극대화, 자동화된 관리

**단점**: Pod 재시작 발생, PDB 설정 필요, 잠재적 다운타임

**권장 사용 사례**: Stateless 워크로드, 개발/스테이징 환경, 다중 레플리카 서비스

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: "Recreate"
```

### Auto
**Auto 모드**: VPA가 자동으로 최적의 방식(Initial 또는 Recreate)을 선택합니다.

**장점**: 최소 개입, 상황에 맞는 자동 선택, 편리한 관리

**단점**: 예측 어려움, 세밀한 제어 불가, 현재는 Recreate와 동일

**권장 사용 사례**: 일반적인 웹 서비스, 마이크로서비스, 유연한 운영 환경

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: "Auto"
```

<!-- notes: VPA 모드 선택은 워크로드 특성에 따라 결정합니다. 프로덕션에서는 Off 모드로 먼저 분석한 후, 안정적인 추천값이 나오면 다른 모드로 전환하는 것을 권장합니다. -->

---

<!-- type: canvas -->
# VPA 추천값 시뮬레이터
## 리소스 사용량 기반 VPA 추천값 시각화

슬라이더로 CPU/Memory의 현재 요청(Request)과 실제 사용량(Usage)을 조정하면 VPA 추천값이 계산됩니다.

**시각화 내용**:
- 파란색 바: 현재 Request 값
- 초록색 바: 실제 Usage 값
- 노란색 점선: VPA 추천값 (Usage의 115% 기준)
- 우측에 절감률(%) 표시

**VPA Recommendation 예시**:
```
target: CPU 345m, Memory 589Mi
lowerBound: CPU 300m, Memory 512Mi
upperBound: CPU 400m, Memory 700Mi
```

Request가 Usage보다 훨씬 크면 리소스 낭비가 발생하고, VPA는 적정 수준으로 낮춰줍니다.

<!-- notes: VPA는 실제 사용량에 15% 정도의 여유(headroom)를 두고 추천값을 계산합니다. 이 시뮬레이터를 통해 리소스 절감 효과를 미리 확인할 수 있습니다. -->

---

<!-- type: timeline -->
# VPA + Auto Mode 연동 패턴
## 리소스 최적화에서 노드 비용 절감까지의 자동화 흐름

1. **VPA 리소스 모니터링** - 14일간 Pod CPU/Memory 사용 패턴 분석
2. **추천값 생성** - 분석 결과: CPU 300m, Memory 512Mi 권장
3. **Pod Requests 업데이트** - VPA가 Pod spec 자동 수정 (Recreate/Auto 모드)
4. **Auto Mode 변경 감지** - 새로운 Pod requests를 기반으로 스케줄링 재평가
5. **최적 인스턴스 선택** - c6g.large에서 c6g.medium으로 다운사이징
6. **Consolidation 수행** - 오버프로비저닝된 노드 통합, 빈 노드 제거

> **Tip**: VPA Off 모드로 먼저 분석한 후, 안정적인 추천값이 나오면 Recreate 또는 Auto 모드로 전환하세요.

<!-- notes: 이 흐름은 완전 자동화되어 있습니다. VPA가 리소스를 최적화하면 Auto Mode가 이를 감지하고 노드 구성을 자동으로 조정합니다. -->

---

<!-- type: content -->
# 리소스 요청 최적화 전략
## QoS Class와 Request/Limit 설정 가이드

### QoS Classes

| Class | 조건 | 설명 |
|-------|------|------|
| **Guaranteed** | request == limit | 리소스 보장, OOM 우선순위 높음 |
| **Burstable** | request < limit | 필요시 추가 리소스 사용 가능 |
| **BestEffort** | no request/limit | 리소스 보장 없음, OOM 우선 대상 |

### Production Best Practices

- **CPU**: request만 설정, limit 없음 - Burstable로 CPU throttling 방지
- **Memory**: request == limit - Guaranteed로 OOM 방지
- **권장 패턴**: CPU request only + Memory guaranteed

```yaml
resources:
  requests:
    cpu: "500m"        # CPU request only
    memory: "512Mi"    # Memory guaranteed
  limits:
    # cpu: (no limit)  # Allows bursting
    memory: "512Mi"    # Same as request
```

<!-- notes: CPU는 throttling만 발생하지만, Memory는 OOM Kill이 발생할 수 있으므로 더 보수적으로 설정합니다. 이 패턴이 대부분의 프로덕션 워크로드에 적합합니다. -->

---

<!-- type: content -->

# KEDA — Event-Driven Autoscaling

**HPA를 넘어서: 이벤트 기반 스케일링과 Scale-to-Zero**

### 아키텍처 플로우

Event Sources (SQS / MSK / Prometheus) → **KEDA (ScaledObject)** → HPA (자동 생성/관리) → Deployment (0 ~ N Replicas)

### HPA vs KEDA 비교

| 항목 | HPA (기본) | KEDA |
|------|-----------|------|
| 메트릭 소스 | CPU / Memory만 | **60+ 외부 스케일러** (SQS, MSK, Prometheus 등) |
| 최소 레플리카 | min: 1 | **min: 0** (Scale-to-Zero → 비용 절감) |
| 설정 방식 | HPA 리소스 직접 관리 | ScaledObject → HPA 자동 생성/관리 |
| Prometheus 연동 | Prometheus Adapter 필요 | 네이티브 PromQL 지원 |
| AWS 통합 | CloudWatch Adapter 별도 설치 | SQS, MSK, CloudWatch 스케일러 내장 |

### 핵심 장점
- **Scale-to-Zero**: 트래픽 없을 때 0으로 축소, 비용 절감
- **60+ Scalers**: AWS, GCP, Azure, Kafka, Redis 등
- **PromQL Native**: 기존 Prometheus 인프라 재활용
- **CRD 기반**: GitOps 친화적 선언형 관리

<!-- notes: KEDA는 Kubernetes Event-Driven Autoscaler로, HPA를 감싸서 외부 이벤트 소스 기반 스케일링과 Scale-to-Zero를 지원합니다. -->

---

<!-- type: tabs -->

# AWS 메트릭 기반 스케일링

**SQS Queue Depth / MSK Consumer Lag / ALB Request Count**

### SQS Queue

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: sqs-consumer-scaler
spec:
  scaleTargetRef:
    name: sqs-consumer
  minReplicaCount: 0    # Scale-to-Zero!
  maxReplicaCount: 20
  triggers:
  - type: aws-sqs-queue
    authenticationRef:
      name: keda-aws-credentials
    metadata:
      queueURL: https://sqs.ap-northeast-2.amazonaws.com/...
      queueLength: "5"  # 메시지 5개당 1 Pod
      awsRegion: ap-northeast-2
```

- `aws-sqs-queue` — Prometheus 불필요
- `queueLength: "5"` — 메시지 5개당 Pod 1개
- **Scale-to-Zero**: 큐 비어있으면 Pod 0
- IRSA 기반 인증 (`TriggerAuthentication`)

### MSK Kafka

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: msk-consumer-scaler
spec:
  scaleTargetRef:
    name: kafka-consumer
  minReplicaCount: 1
  maxReplicaCount: 30
  triggers:
  - type: prometheus
    metadata:
      serverAddress: http://prometheus:9090
      query: |
        sum(kafka_consumergroup_lag{
          group="my-consumer",
          topic="orders"
        })
      threshold: "1000"  # Lag 1000당 1 Pod
```

- `prometheus` 스케일러로 Consumer Lag 모니터링
- `kafka_consumergroup_lag` 메트릭 활용

> **주의:** MSK는 Scale-to-Zero 비권장 — Consumer가 0이면 Lag 감지 불가 → minReplicaCount: 1 유지

### ALB

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: alb-scaler
spec:
  scaleTargetRef:
    name: web-app
  minReplicaCount: 2
  maxReplicaCount: 50
  triggers:
  - type: aws-cloudwatch
    authenticationRef:
      name: keda-aws-credentials
    metadata:
      namespace: AWS/ApplicationELB
      dimensionName: TargetGroup
      dimensionValue: targetgroup/my-tg/...
      metricName: RequestCountPerTarget
      targetMetricValue: "100"  # Pod당 100 req
      metricStatPeriod: "60"
```

- `aws-cloudwatch` 스케일러 — Prometheus 불필요
- `RequestCountPerTarget` 메트릭

<!-- notes: AWS 네이티브 메트릭(SQS, MSK, ALB)을 KEDA 스케일러로 직접 사용하여 Prometheus Adapter 없이 정확한 스케일링이 가능합니다. -->

---

<!-- type: canvas -->

# Istio Gateway RPS 기반 스케일링

**PromQL + KEDA로 Istio 메트릭 기반 자동 스케일링**

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: istio-rps-scaler
spec:
  scaleTargetRef:
    name: my-app
  minReplicaCount: 0
  maxReplicaCount: 10
  cooldownPeriod: 120
  triggers:
  - type: prometheus
    metadata:
      serverAddress: http://prometheus:9090
      query: |
        sum(rate(istio_requests_total{
          destination_service=~"my-app.*",
          reporter="destination"
        }[1m]))
      threshold: "50"  # Pod당 50 RPS
```

Canvas 애니메이션:
- 슬라이더로 RPS 조절 (0 ~ 500)
- Gateway → Prometheus 화살표: RPS + Latency P99 표시
- Prometheus → KEDA 화살표: query 레이블
- KEDA → Deployment 화살표: scale 레이블, Pod 수 표시
- Gateway 하단 상태 뱃지: Idle / Healthy / Slow / Error
- RPS 연동 Latency: ≤100 → 5-50ms, 100-300 → 50-200ms, >300 → 200-800ms

### 확장 패턴

| 패턴 | 설명 |
|------|------|
| Error Rate | 5xx 비율 > 5% → 즉시 스케일아웃 |
| Latency P99 | P99 > 500ms → Pod 추가 |
| Circuit Breaker | outlierDetection과 연동 |
| Cron + RPS | 피크타임 사전 확보 + RPS 보정 |

<!-- notes: Istio의 istio_requests_total 메트릭을 PromQL로 쿼리하여 RPS 기반 자동 스케일링을 구현합니다. 화살표에 RPS와 Latency P99가 동시에 표시됩니다. -->

---

<!-- type: compare -->
# 비용 절감 사례 (Before/After)
## VPA + Auto Mode 최적화 실제 적용 결과

### Before (최적화 전)
- **Nodes**: 20개 (m5.xlarge)
- **CPU 활용률**: 25%
- **Memory 활용률**: 30%
- **월 비용**: $5,840

### After (최적화 후)
- **Nodes**: 8개 (m6g.large, c6g.xlarge 혼합)
- **CPU 활용률**: 65%
- **Memory 활용률**: 70%
- **월 비용**: $1,752

---

<!-- type: content -->
# Total Savings: 70%

### 절감 요소 분석

| 최적화 항목 | 절감률 |
|------------|--------|
| VPA 리소스 적정화 | 20-40% |
| Graviton (ARM) 전환 | 20% |
| Spot 활용 | 60-70% |
| Consolidation | 10-30% |

<!-- notes: 이 사례에서는 VPA로 리소스를 적정화하고, Auto Mode가 Graviton 인스턴스와 Spot을 활용하여 70%의 비용 절감을 달성했습니다. -->

---

<!-- type: checklist -->
# Best Practices 체크리스트
## 리소스 최적화를 위한 운영 가이드

### VPA 설정
- [ ] VPA를 Off 모드로 먼저 분석 (2주)
- [ ] 핵심 워크로드부터 VPA 적용
- [ ] CPU는 request만, Memory는 request=limit
- [ ] Disruption Budget으로 안전한 교체

### NodePool 전략
- [ ] NodePool 분리: 웹/배치/GPU
- [ ] Graviton 인스턴스 허용 (arm64)
- [ ] Spot 혼합 전략 (Stateless 워크로드)
- [ ] Pod Priority로 중요 워크로드 보호

### 비용 관리
- [ ] 정기적 비용 리뷰 (월 1회)
- [ ] Cost Allocation Tags 적용

### 모니터링
- [ ] VPA 추천값 대시보드 구성
- [ ] 노드 활용률 알림 설정

<!-- notes: 이 체크리스트를 기준으로 점진적으로 최적화를 적용하세요. 한 번에 모든 것을 적용하기보다 단계적으로 검증하며 진행하는 것이 안전합니다. -->

---

<!-- type: content -->
# 추가 학습 리소스
## 심화 학습을 위한 참고 자료

### 공식 문서
- **GitBook: EKS Auto Mode 가이드** - 한국어로 작성된 EKS Auto Mode 및 Kubernetes 학습 자료. 실습 예제 포함.
  - https://atomoh.gitbook.io/kubernetes-docs/

- **AWS 공식 문서: EKS Auto Mode** - EKS Auto Mode의 공식 문서. 설정 방법 및 모범 사례 안내.
  - https://docs.aws.amazon.com/eks/latest/userguide/automode.html

- **Karpenter 공식 문서** - Auto Mode의 기반이 되는 Karpenter의 상세 문서. NodePool, NodeClass 설정.
  - https://karpenter.sh/docs/

### Observability
- **Grafana 상관분석 가이드** - Logs, Metrics, Traces 연동을 위한 Grafana 데이터소스 설정 가이드.
  - https://grafana.com/docs/grafana/latest/datasources/tempo/configure-tempo-data-source/

- **OpenTelemetry 공식 문서** - 분산 추적 및 관측성 표준. SDK, Collector, 계측 가이드.
  - https://opentelemetry.io/docs/

- **VPA GitHub Repository** - Vertical Pod Autoscaler 공식 리포지토리. 설치, 구성, FAQ.
  - https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler

<!-- notes: 이 리소스들을 통해 더 깊이 있는 학습을 할 수 있습니다. 특히 GitBook의 한국어 자료가 실습에 유용합니다. -->

---

<!-- type: content -->
# 전체 과정 요약
## Key Takeaways

### BLOCK 01: EKS Auto Mode 내부 아키텍처
Auto Mode는 Karpenter 기반 - NodePool/NodeClass로 세밀한 제어 가능. 인스턴스 선택, Consolidation, Drift 처리 자동화.

### BLOCK 02: 노드 라이프사이클 모니터링
Prometheus 쿼리 + AlertManager로 노드 가시성 확보. Spot 인터럽트 대응, expireAfter 전략으로 Day-2 운영 안정화.

### BLOCK 03: 3-Signal Correlation
Exemplars + Derived Fields + tracesToLogs로 Logs/Metrics/Traces 상관분석. MTTR 단축 및 근본 원인 분석 가속화.

### BLOCK 04: VPA + Auto Mode 최적화
VPA로 리소스 requests 최적화, Auto Mode가 최적 노드 선택. 조합하면 70%+ 비용 절감 가능.

<!-- notes: 4개 블록의 핵심 내용을 정리했습니다. 각 블록의 내용이 서로 연결되어 있으며, 종합적으로 적용하면 EKS 운영을 크게 개선할 수 있습니다. -->

---

<!-- type: title -->
# Q&A
## 질문과 답변

오늘 교육이 도움이 되셨나요?

**피드백은 더 나은 콘텐츠를 만드는 데 큰 힘이 됩니다.**

Session: EKS Auto Mode & Observability (2 Hours)

<!-- notes: 질문을 받고, 추가 설명이 필요한 부분을 다룹니다. -->
