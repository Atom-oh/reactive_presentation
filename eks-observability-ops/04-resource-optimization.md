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
- Pod CPU/Memory 사용량 관찰
- requests 추천 (limits는 기존 비율 유지)
- Recreate 또는 InPlaceOrRecreate로 적용
- CPU: 24h 반감기, Memory: 일별 피크 8일 (기본값)

### Auto Mode
- Pod requests 합계로 노드 선택
- NodePool 조건 안에서 인스턴스 매칭
- requests가 줄면 노드에 빈자리 발생
- Consolidation이 삭제 또는 교체 판단

### Key Points
| VPA | Auto Mode | 주의 |
|-----|-----------|---------|
| Pod의 CPU/Memory requests를 사용량에 맞게 조정 | 줄어든 requests로 빈 노드를 정리 (EKS 1.37 신규 풀은 Balanced 기본) | 같은 CPU/Memory 메트릭으로 HPA와 함께 쓰지 않기 |

<!-- notes: {timing: 1.5min} [요약] VPA는 Pod requests를, Auto Mode는 노드를 다룹니다. requests가 줄면 노드에 빈자리가 생기고 Consolidation이 삭제나 교체를 판단합니다. 같은 CPU, Memory 메트릭으로 HPA와 함께 쓰지 않습니다. -->

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
**Recreate 모드**: 추천값과 차이가 크면 Updater가 Pod를 evict하고, Admission Controller가 새 Pod에 추천값을 넣습니다. VPA 1.5부터 기본 모드입니다.

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

### InPlaceOrRecreate
**InPlaceOrRecreate 모드 (VPA 1.6 GA)**: Pod를 재시작하지 않고 `resize` subresource로 requests를 바꿉니다. in-place가 불가능하면 evict로 전환합니다.

**장점**: 재시작 없이 조정, Kubernetes 1.35부터 in-place resize GA

**단점**: QoS class는 바꿀 수 없음, 노드 여유가 없으면 결국 evict

**권장 사용 사례**: 재시작 비용이 큰 서비스, EKS 1.35 이상. evict 없는 `InPlace` 모드는 VPA 1.8에서도 alpha

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
    updateMode: "InPlaceOrRecreate"
```

### Auto (deprecated)
**Auto 모드**: VPA 1.5부터 deprecated이며 현재 Recreate와 같게 동작합니다. 향후 API 버전에서 제거될 예정이므로 Recreate 또는 InPlaceOrRecreate를 명시합니다.

**권장 사용 사례**: 신규 설정에는 사용하지 않음. 기존 Auto 설정은 명시적 모드로 전환

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

<!-- notes: {timing: 2.5min} [요약] Off로 관찰, Initial은 새 Pod에만, Recreate는 evict 후 재생성(VPA 1.5부터 기본), InPlaceOrRecreate는 resize를 먼저 시도합니다. Auto는 deprecated입니다. -->

---

<!-- type: canvas -->
# VPA 추천값 시뮬레이터
## 리소스 사용량 기반 VPA 추천값 시각화

슬라이더로 CPU/Memory의 현재 요청(Request)과 실제 사용량(Usage)을 조정하면 VPA 추천값이 계산됩니다.

**시각화 내용**:
- 파란색 바: 현재 Request 값
- 초록색 바: 실제 Usage 값
- 노란색 점선: VPA target (사용량 P90 × 1.15, VPA 1.8 기본값)
- 우측에 절감률(%) 표시

**VPA Recommendation 예시**:
```
target: CPU 345m, Memory 589Mi
lowerBound: CPU 173m, Memory 353Mi   # P50 기반, 교육용 근사
upperBound: CPU 863m, Memory 1178Mi  # P95 기반, 교육용 근사
```

Request가 Usage보다 훨씬 크면 리소스 낭비가 발생하고, VPA는 적정 수준으로 낮춰줍니다.

<!-- notes: {timing: 2min} [요약] VPA 1.8 기본 target은 CPU, Memory 모두 P90 사용량에 15% 여유를 더한 값입니다. lowerBound는 P50, upperBound는 P95 기반이며 화면의 bound는 교육용 근사입니다. 최소 추천값은 CPU 25m, Memory 250Mi입니다. -->

---

<!-- type: timeline -->
# VPA + Auto Mode 연동 패턴
## 리소스 최적화에서 노드 비용 절감까지의 자동화 흐름

1. **VPA 리소스 모니터링**: CPU 24h 반감기 histogram, Memory 일별 피크 8일
2. **추천값 생성**: target = P90 × 1.15, CPU 300m, Memory 512Mi
3. **Pod Requests 업데이트**: InPlaceOrRecreate는 먼저 in-place, 불가하면 evict. limits는 기존 비율 유지
4. **노드에 빈자리 발생**: 노드는 그대로이고 requests 합계만 줄어듦. 직접 설치 Karpenter v1.14+는 spec과 status.allocatedResources 중 큰 값으로 계산
5. **Consolidation 판단**: 빈 노드 삭제 또는 더 저렴한 노드로 교체. Balanced는 절감액 대비 Pod 중단 비용 평가
6. **결과 확인**: 예시(us-east-1 On-Demand 가정) 3x c6g.large → 2x c6g.large, 약 33%. 재시작, Pending, 지연을 함께 측정

> **Tip**: VPA Off 모드로 최소 8일 이상 관찰한 후, Recreate 또는 InPlaceOrRecreate를 명시해 적용하세요.

<!-- notes: {timing: 2.5min} [요약] VPA가 requests를 줄여도 노드는 바로 바뀌지 않습니다. 빈자리가 생기면 Consolidation이 판단합니다. Auto Mode 내부 동작은 AWS 문서에 따로 설명이 없으므로 단정하지 않습니다. -->

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
- **Memory**: request == limit, 다른 Pod의 메모리 압박으로 인한 eviction 위험 감소
- **권장 패턴**: CPU request only + Memory request == limit (Pod QoS는 Burstable)

```yaml
resources:
  requests:
    cpu: "500m"        # CPU request only
    memory: "512Mi"    # Memory request == limit
  limits:
    # cpu: (no limit)  # Allows bursting
    memory: "512Mi"    # Same as request
```

<!-- notes: CPU는 throttling만 발생하지만, Memory는 OOM Kill이 발생할 수 있으므로 더 보수적으로 설정합니다. 이 패턴이 대부분의 프로덕션 워크로드에 적합합니다. -->

---

<!-- type: content -->

# KEDA: Event-Driven Autoscaling

**HPA를 넘어서: 이벤트 기반 스케일링과 Scale-to-Zero**

### 아키텍처 플로우

Event Sources (SQS / MSK / Prometheus) → **KEDA (ScaledObject)** → HPA (자동 생성/관리) → Deployment (0 ~ N Replicas)

### HPA vs KEDA 비교

| 항목 | HPA (기본) | KEDA |
|------|-----------|------|
| 메트릭 소스 | CPU / Memory만 | **70+ 스케일러** (SQS, Kafka, Prometheus 등) |
| 최소 레플리카 | min: 1 | **min: 0** (Scale-to-Zero → 비용 절감) |
| 설정 방식 | HPA 리소스 직접 관리 | ScaledObject → HPA 자동 생성/관리 |
| Prometheus 연동 | Prometheus Adapter 필요 | 네이티브 PromQL 지원 |
| AWS 통합 | CloudWatch Adapter 별도 설치 | SQS, MSK, CloudWatch 스케일러 내장 |

### 핵심 장점
- **Scale-to-Zero**: 트래픽 없을 때 0으로 축소, 비용 절감
- **70+ Scalers**: AWS, GCP, Azure, Kafka, Redis 등

KEDA v2.21(2026-09-23)의 테스트 범위는 Kubernetes 1.34 ~ 1.36입니다. EKS 1.37은 공식 테스트 범위 밖이므로 스테이징에서 먼저 검증합니다. KEDA는 EKS add-on이 아니며 Helm으로 설치합니다.
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

- `aws-sqs-queue`: Prometheus 불필요
- `queueLength: "5"`: 메시지 5개당 Pod 1개
- **Scale-to-Zero**: 큐 비어있으면 Pod 0
- IRSA 기반 인증 (`TriggerAuthentication`, `podIdentity.provider: aws`. `aws-eks`는 deprecated)

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
- 대안: `kafka` 스케일러 + `sasl: aws_msk_iam` (KEDA에 `aws-msk` 타입은 없음)

> **주의:** Scale-to-Zero는 0에서 다시 뜰 때 consumer group rebalance와 첫 처리 지연이 생깁니다. 지연에 민감하면 minReplicaCount: 1을 유지합니다.

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

- `aws-cloudwatch` 스케일러: Prometheus 불필요
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
# 비용 절감 계산 예시 (Before/After)
## 가정: us-east-1 On-Demand, 730시간/월, 사용량 불변, Spot 미반영. 실제 고객 결과가 아닙니다

### Before (최적화 전)
- **Nodes**: 20개 m5.xlarge (80 vCPU, 320GiB), $0.192/h
- **CPU 활용률**: 25% (20 vCPU 사용)
- **Memory 활용률**: 30% (96GiB 사용)
- **월 비용**: $2,803

### After (최적화 후)
- **Nodes**: 8개 m6g.xlarge (32 vCPU, 128GiB), $0.154/h
- **CPU 활용률**: 약 63% (20/32 vCPU)
- **Memory 활용률**: 75%
- **월 비용**: $899

---

<!-- type: content -->
# 예시 절감률: 약 68%

### 절감 요인

| 항목 | 이 예시에서 |
|------------|--------|
| requests 적정화 | 노드 20 → 8 |
| Graviton 단가 | $0.192 → $0.154/h |
| Spot | 이 예시에 미반영 |
| 측정할 것 | 재시작, Pending, 지연 |

<!-- notes: {timing: 1.5min} [요약] 실제 고객 사례가 아닌 계산 예시입니다. 20대 m5.xlarge는 월 약 $2,803, 8대 m6g.xlarge는 월 약 $899로 약 68%입니다. 절감률은 환경마다 다르므로 수치를 약속하지 않습니다. -->

---

<!-- type: checklist -->
# Best Practices 체크리스트
## 리소스 최적화를 위한 운영 가이드

### VPA 설정
- [ ] VPA를 Off 모드로 먼저 분석 (메모리 기본 창 8일 이상)
- [ ] 핵심 워크로드부터 VPA 적용
- [ ] CPU는 request만, Memory는 request=limit
- [ ] 적용은 Recreate 또는 InPlaceOrRecreate 명시 (Auto 사용 안 함)
- [ ] CPU/Memory는 VPA와 HPA 중 하나만 사용

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

- **Karpenter 공식 문서** - 직접 설치한 Karpenter의 설정, 호환성 (Kubernetes 1.37은 1.15.x 필요). Auto Mode NodeClass와 구분.
  - https://karpenter.sh/docs/
  - [2026-10-15 버전 검토와 공식 출처](version-update.md)

### Observability
- **Grafana 상관분석 가이드** - Logs, Metrics, Traces 연동을 위한 Grafana 데이터소스 설정 가이드.
  - https://grafana.com/docs/grafana/latest/datasources/tempo/configure-tempo-data-source/

- **OpenTelemetry 공식 문서** - 분산 추적 및 관측성 표준. SDK, Collector, 계측 가이드.
  - https://opentelemetry.io/docs/

- **VPA GitHub Repository** - VPA 1.8.0 (Kubernetes 1.36 ~ 1.38). 설치, updateMode, Recommender flag.
  - https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler

<!-- notes: 이 리소스들을 통해 더 깊이 있는 학습을 할 수 있습니다. 특히 GitBook의 한국어 자료가 실습에 유용합니다. -->

---

<!-- type: content -->
# 전체 과정 요약
## Key Takeaways

### BLOCK 01: EKS Auto Mode 내부 아키텍처
Auto Mode는 AWS가 관리하는 Karpenter 기반 노드 관리. NodePool과 NodeClass로 제어하고, 직접 설치한 Karpenter(v1.15.0)와 API와 운영 책임이 다릅니다.

### BLOCK 02: 노드 라이프사이클 모니터링
Pod, 노드, 이벤트 순서로 진단. Spot 회수 대응, expireAfter와 Disruption Budget으로 Day-2 운영 안정화.

### BLOCK 03: 3-Signal Correlation
Exemplars, Derived Fields, tracesToLogsV2로 Logs, Metrics, Traces 상관분석. 근본 원인 분석 가속화.

### BLOCK 04: VPA + KEDA + Auto Mode 최적화
VPA(InPlaceOrRecreate)로 requests 조정, KEDA로 이벤트 기반 스케일링, Auto Mode Consolidation으로 빈 노드 정리.

<!-- notes: 4개 블록의 핵심 내용을 정리했습니다. 각 블록의 내용이 서로 연결되어 있으며, 종합적으로 적용하면 EKS 운영을 크게 개선할 수 있습니다. -->

---

<!-- type: title -->
# Q&A
## 질문과 답변

오늘 교육이 도움이 되셨나요?

**피드백은 더 나은 콘텐츠를 만드는 데 큰 힘이 됩니다.**

Session: EKS Auto Mode & Karpenter 운영 (2 Hours)

<!-- notes: 질문을 받고, 추가 설명이 필요한 부분을 다룹니다. -->
