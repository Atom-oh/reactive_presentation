---
remarp: true
block: observability-next
---

---
@type: cover
@background: ../common/pptx-theme/images/Picture_13.png
@badge: ../common/pptx-theme/images/Picture_8.png

# Observability & Next Steps
Block 05 — 관측성 전략과 업그레이드 로드맵 (20 min)

오준석 (Junseok Oh)
Sr. Solutions Architect
AWS

:::notes
{timing: 1min}
마지막 블록입니다. 관측성(Observability)의 3가지 축과 EKS 업그레이드 전략, 그리고 마이그레이션 이후 로드맵을 다룹니다.
이 블록을 마치면 ECS에서 EKS로의 마이그레이션 전체 여정이 완료됩니다.
:::

---
@type: canvas
@canvas-id: observability-pillars

## Observability 3 Pillars

:::canvas
# Step 1: Logs pillar
box logs "Logs" at 150,180 size 160,100 color #F8B52A step 1
box logs-desc "이벤트 기록\n구조화된 데이터\n컨텍스트 정보" at 150,300 size 160,80 color #333 step 1

# Step 2: Metrics pillar
box metrics "Metrics" at 450,180 size 160,100 color #E6522C step 2
box metrics-desc "시계열 데이터\n수치 측정값\n집계 가능" at 450,300 size 160,80 color #333 step 2

# Step 3: Traces pillar
box traces "Traces" at 750,180 size 160,100 color #326CE5 step 3
box traces-desc "요청 경로 추적\n서비스 간 흐름\n지연 시간 분석" at 750,300 size 160,80 color #333 step 3

# Step 4: Correlation arrows
arrow logs -> metrics "Label 매칭" step 4
arrow metrics -> traces "Exemplar" step 4
arrow traces -> logs "TraceID" step 4
:::

:::notes
{timing: 3min}
관측성의 3가지 축 — Logs, Metrics, Traces를 설명합니다.

1. Logs: 개별 이벤트의 불변 기록. 디버깅과 감사에 필수
2. Metrics: 시계열 수치 데이터. CPU, 메모리, 요청 수 등 집계 가능
3. Traces: 분산 시스템에서 요청의 전체 경로 추적

핵심은 세 가지가 **상호 연결**된다는 점입니다:
- TraceID로 로그와 트레이스 연결
- Exemplar로 메트릭에서 특정 트레이스로 점프
- Label 매칭으로 로그와 메트릭 상관분석

{cue: question}
현재 화해에서는 이 세 가지 중 어떤 것을 가장 많이 활용하고 계신가요?
:::

---
@type: tabs

## 현재 vs 목표 관측성 스택

### 현재 (ECS)
| 영역 | 도구 | 한계 |
|------|------|------|
| **Logs** | CloudWatch Logs, OpenSearch | 비용 증가, 쿼리 복잡 |
| **Metrics** | CloudWatch Metrics | 커스텀 메트릭 비용, 15개월 보존 |
| **Traces** | X-Ray (부분 적용) | 샘플링 제한, 컨텍스트 전파 어려움 |
| **Dashboard** | CloudWatch Dashboards | 제한된 시각화 |

### 목표 (EKS)
| 영역 | 도구 | 장점 |
|------|------|------|
| **Logs** | ClickHouse + Fluent Bit | 고성능 SQL 쿼리, 컬럼 기반 압축, 비용 효율 |
| **Metrics** | Prometheus (AMP) + Grafana | PromQL, 무제한 커스텀 메트릭 |
| **Traces** | ClickHouse + OpenTelemetry | SQL 기반 트레이스 분석, 전체 샘플링, 로그와 동일 백엔드 |
| **Dashboard** | Grafana (AMG) | 통합 시각화, 알림, 상관분석 |

:::notes
{timing: 2min}
현재 CloudWatch 중심 스택에서 ClickHouse(Logs+Traces) + Prometheus(Metrics) + Grafana(Dashboard) 기반 스택으로 전환을 권장합니다. ClickHouse 단일 백엔드로 로그와 트레이스를 모두 처리하면 운영 복잡도가 크게 줄어듭니다.

AWS 관리형 서비스:
- AMP (Amazon Managed Service for Prometheus): Prometheus 호환 메트릭 저장소
- AMG (Amazon Managed Grafana): 완전 관리형 Grafana

오픈소스 vs 관리형 선택은 운영 역량과 비용을 고려해서 결정하세요.
:::

---
@type: canvas
@canvas-id: prometheus-architecture

## Prometheus + Grafana 아키텍처

:::canvas
# Step 1: Prometheus (AMP or Self-hosted)
icon prometheus "CloudWatch" at 450,120 size 64 step 1
box prom-label "Prometheus\n(AMP/Self-hosted)" at 400,200 size 160,50 color #E6522C step 1

# Step 2: ServiceMonitor discovers targets
box sm "ServiceMonitor" at 150,280 size 140,50 color #326CE5 step 2
box app1 "App Pod" at 100,380 size 80,40 color #4CAF50 step 2
box app2 "App Pod" at 220,380 size 80,40 color #4CAF50 step 2
arrow sm -> app1 "discover" style dashed step 2
arrow sm -> app2 "discover" style dashed step 2

# Step 3: Scrape metrics
arrow app1 -> prom-label "scrape /metrics" step 3
arrow app2 -> prom-label "scrape /metrics" step 3

# Step 4: Grafana dashboard
box grafana "Grafana (AMG)" at 700,280 size 140,50 color #F8B52A step 4
arrow prom-label -> grafana "PromQL" step 4
:::

:::notes
{timing: 3min}
Prometheus 기반 모니터링 아키텍처입니다.

1. **Prometheus**: 메트릭 수집 및 저장. AMP 사용 시 운영 부담 감소
2. **ServiceMonitor**: Prometheus Operator CRD. 라벨 셀렉터로 스크래핑 대상 자동 발견
3. **Scrape**: 애플리케이션의 /metrics 엔드포인트에서 Pull 방식으로 수집
4. **Grafana**: PromQL로 쿼리하여 대시보드 시각화

{cue: demo}
실제 ServiceMonitor 설정과 Grafana 대시보드 예시를 보여드리겠습니다.
:::

---
@type: code

## Prometheus + Grafana 셋업

```yaml {filename="servicemonitor.yaml" highlight="8-12"}
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: hwahae-api
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: hwahae-api      # 이 라벨을 가진 Service 자동 발견
  endpoints:
    - port: metrics        # Service의 metrics 포트
      interval: 30s        # 30초마다 스크래핑
      path: /metrics
  namespaceSelector:
    matchNames:
      - production
      - staging
```

```yaml {filename="grafana-dashboard-cm.yaml"}
apiVersion: v1
kind: ConfigMap
metadata:
  name: hwahae-dashboard
  labels:
    grafana_dashboard: "1"  # Grafana sidecar가 자동 로드
data:
  hwahae.json: |
    {
      "title": "Hwahae API Dashboard",
      "panels": [...]
    }
```

:::notes
{timing: 2min}
ServiceMonitor와 Grafana Dashboard ConfigMap 예시입니다.

**ServiceMonitor 핵심 설정:**
- `selector.matchLabels`: 모니터링할 Service 선택
- `endpoints.interval`: 스크래핑 주기 (30s 권장)
- `namespaceSelector`: 여러 네임스페이스 지원

**Grafana Dashboard:**
- ConfigMap에 JSON 대시보드 정의
- `grafana_dashboard: "1"` 라벨로 sidecar가 자동 로드
- GitOps로 대시보드 버전 관리 가능
:::

---
@type: compare

## Datadog vs OSS Stack

### Datadog
| 항목 | 내용 |
|------|------|
| **비용** | 호스트당 $15-23/월 + 로그/APM 추가 비용 |
| **기능** | 올인원 (Logs, Metrics, APM, RUM) |
| **운영 부담** | 낮음 (SaaS) |
| **장점** | 빠른 도입, 통합 UI, AI 기반 분석 |
| **단점** | 벤더 종속, 비용 예측 어려움, 데이터 소유권 |

### OSS Stack (Prometheus + ClickHouse)
| 항목 | 내용 |
|------|------|
| **비용** | 인프라 비용만 (AMP: GB당 $0.03) |
| **기능** | 조합 필요 (각 도구 역할 명확) |
| **운영 부담** | 중간 (AWS 관리형 사용 시 낮음) |
| **장점** | 비용 투명성, 벤더 중립, 커스터마이징 |
| **단점** | 초기 학습 곡선, 통합 설정 필요 |

:::notes
{timing: 2min}
Datadog과 OSS 스택 비교입니다.

**Datadog 추천 상황:**
- 빠른 도입이 필요할 때
- DevOps 전담 인력이 부족할 때
- 비용보다 시간이 중요할 때

**OSS Stack 추천 상황:**
- 장기적 비용 최적화가 중요할 때
- 이미 Kubernetes 운영 역량이 있을 때
- 데이터 소유권과 벤더 독립성이 중요할 때

화해 규모(수십 개 서비스)에서는 OSS Stack + AWS 관리형(AMP, AMG)을 권장합니다.
월 비용이 Datadog 대비 50-70% 절감 가능합니다.
:::

---
@type: timeline

## 기존 OpenSearch와 공존 전략

1. **Phase 1: 메트릭 우선 (Month 1-2)** — 기존 OpenSearch 유지, Prometheus(AMP) + Grafana(AMG) 추가, CloudWatch Container Insights 병행
2. **Phase 2: 듀얼 로그 파이프라인 (Month 3-4)** — Fluent Bit 듀얼 아웃풋: OpenSearch + ClickHouse, 신규 서비스는 ClickHouse 전용, 기존 서비스 로그는 양쪽 모두 전송
3. **Phase 3: 트레이싱 도입 (Month 5-6)** — OpenTelemetry Collector 설치, ClickHouse에 트레이스 저장 (로그와 동일 백엔드), Grafana에서 Logs ↔ Metrics ↔ Traces 상관분석
4. **Phase 4: 통합 완료 (Month 7+)** — OpenSearch 트래픽 모니터링 후 단계적 축소, ClickHouse로 완전 전환 또는 공존 유지 결정, 비용 비교 후 최종 판단

:::notes
{timing: 2min}
기존 OpenSearch 스택과의 공존 전략입니다. 핵심은 빅뱅 전환이 아니라 점진적 마이그레이션입니다. Phase 1에서 메트릭부터 Prometheus로 전환하고, Phase 2에서 Fluent Bit 듀얼 아웃풋으로 로그를 양쪽에 전송합니다. Phase 3에서 트레이싱을 추가하고, Phase 4에서 비용과 운영 효율을 비교한 후 최종 결정합니다. OpenSearch에 이미 구축된 대시보드와 알림이 있다면, 급하게 전환할 필요 없이 공존하면서 점진적으로 이동하는 것이 안전합니다.
:::

---
@type: code

## Fluent Bit 듀얼 아웃풋 설정

```yaml {filename="fluent-bit-dual-output.yaml" highlight="10-14,22-30,32-42"}
# Fluent Bit ConfigMap — 듀얼 아웃풋
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit-config
  namespace: logging
data:
  output.conf: |
    # Output 1: 기존 OpenSearch (기존 대시보드 유지)
    [OUTPUT]
        Name            opensearch
        Match           kube.*
        Host            vpc-hwahae-logs.ap-northeast-2.es.amazonaws.com
        Port            443
        TLS             On
        AWS_Auth        On
        AWS_Region      ap-northeast-2
        Index           k8s-logs
        Type            _doc

    # Output 2: 신규 ClickHouse (Grafana 통합)
    [OUTPUT]
        Name            http
        Match           kube.*
        Host            clickhouse.monitoring.svc
        Port            8123
        URI             /?query=INSERT+INTO+k8s_logs+FORMAT+JSONEachRow
        Format          json_stream
        Json_date_key   timestamp
        Json_date_format iso8601

    # Output 3: 특정 네임스페이스는 ClickHouse 전용
    [OUTPUT]
        Name            http
        Match           kube.var.log.containers.*_new-service_*
        Host            clickhouse.monitoring.svc
        Port            8123
        URI             /?query=INSERT+INTO+k8s_logs+FORMAT+JSONEachRow
        Format          json_stream
```

**전환 전략**:
- 기존 서비스 → OpenSearch + ClickHouse 듀얼 전송
- 신규 서비스 → ClickHouse 전용
- 2-3개월 병행 후 OpenSearch 의존도 확인 → 축소 판단

:::notes
{timing: 2min}
Fluent Bit 듀얼 아웃풋 설정입니다. 동일한 로그를 OpenSearch와 ClickHouse 양쪽에 전송하여, 기존 대시보드를 유지하면서 Grafana 통합을 준비합니다. ClickHouse는 HTTP 인터페이스로 INSERT하며, 컬럼 기반 압축으로 Loki 대비 쿼리 성능이 월등합니다. 신규 서비스는 ClickHouse 전용으로 설정하여 점진적으로 전환합니다.
:::

---
@type: tabs

## 핵심 메트릭 모니터링 팁

### EKS 필수 대시보드
**Cluster Overview**:
```promql
# 노드 CPU 사용률
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Pod Restart 알림 (5분 내 3회 이상)
increase(kube_pod_container_status_restarts_total[5m]) > 3

# Pending Pod 감지 (Karpenter 스케일링 지연)
kube_pod_status_phase{phase="Pending"} > 0
```

**Application RED Metrics**:
```promql
# Rate: 초당 요청 수
sum(rate(istio_requests_total{reporter="destination"}[5m])) by (destination_service)

# Error: 5xx 에러율
sum(rate(istio_requests_total{response_code=~"5.*"}[5m])) / sum(rate(istio_requests_total[5m]))

# Duration: P99 레이턴시
histogram_quantile(0.99, sum(rate(istio_request_duration_milliseconds_bucket[5m])) by (le, destination_service))
```

### Karpenter 모니터링
```promql
# 노드 프로비저닝 시간
karpenter_provisioner_scheduling_duration_seconds

# Spot 중단 횟수
karpenter_interruption_received_messages_total

# 노드 Consolidation 이벤트
karpenter_disruption_pods_disrupted_total

# 노드당 Pod 밀도
count(kube_pod_info) by (node)
```

**알림 규칙**:
- Spot 중단 빈도 > 5회/일 → 인스턴스 다각화 검토
- Pending Pod > 0 for 2분 → Karpenter 또는 리소스 제한 확인
- Consolidation 실패 → PDB 설정 확인

### SQS/KEDA 모니터링
```promql
# SQS 큐 깊이 (KEDA CloudWatch Scaler)
aws_sqs_approximate_number_of_messages_visible_average

# KEDA 스케일링 상태
keda_scaledobject_ready

# Worker Pod vs 큐 메시지 비율
count(kube_pod_info{pod=~"order-worker.*"})
/ aws_sqs_approximate_number_of_messages_visible_average
```

**핵심**: 큐 깊이 대비 Worker Pod 수의 비율을 모니터링하여 스케일링이 적절한지 확인

:::notes
{timing: 2min}
EKS 운영에 필수적인 모니터링 쿼리들입니다. Cluster Overview에서는 노드 상태와 Pod Restart를 감시하고, Application RED Metrics로 서비스 건강도를 확인합니다. Karpenter 메트릭으로 노드 프로비저닝과 Spot 중단을 추적하고, SQS/KEDA 메트릭으로 배치 워크로드의 스케일링 효율을 모니터링합니다. 이 쿼리들을 Grafana 대시보드에 구성하면 운영 가시성을 크게 높일 수 있습니다.
:::

---
@type: timeline

## Blue/Green 클러스터 업그레이드

1. **준비** — 새 버전 클러스터 프로비저닝, 애드온 호환성 검증
2. **배포** — GitOps로 워크로드 동기화, Smoke 테스트
3. **트래픽 전환** — Route 53 가중치 10% → 50% → 100%
4. **검증** — 메트릭/로그 모니터링, 7일 안정화
5. **정리** — 이전 클러스터 종료, 비용 절감

:::notes
{timing: 2min}
EKS 클러스터 업그레이드는 Blue/Green 방식을 권장합니다.

**왜 Blue/Green인가?**
- EKS 컨트롤 플레인은 롤백 불가
- 인플레이스 업그레이드 시 장애 복구 어려움
- 새 클러스터로 점진적 전환이 안전

**핵심 포인트:**
1. 준비: eksctl 또는 Terraform으로 새 클러스터 생성
2. 배포: ArgoCD ApplicationSet으로 동일 워크로드 배포
3. 트래픽 전환: Route 53 가중치 라우팅으로 점진적 이동
4. 검증: 최소 7일 안정화 기간
5. 정리: 이전 클러스터 삭제로 비용 절감

{cue: question}
현재 EKS 버전은 몇 버전인가요? 업그레이드 주기는 어떻게 관리하시나요?
:::

---
@type: checklist

## 30/60/90일 마이그레이션 로드맵

- [ ] **Day 1-30: 기반 구축**
  ```
  - EKS 클러스터 프로비저닝 (Terraform/eksctl)
  - GitOps 파이프라인 구성 (ArgoCD)
  - Karpenter 노드 오토스케일링 설정
  - 네트워크 정책 및 보안 기본 설정
  ```
- [ ] **Day 31-60: 워크로드 마이그레이션**
  ```
  - Stateless 서비스 먼저 마이그레이션
  - Canary 배포로 트래픽 점진적 전환
  - Observability 스택 구축 (Prometheus, ClickHouse)
  - KEDA 이벤트 기반 스케일링 적용
  ```
- [ ] **Day 61-90: 최적화 및 안정화**
  ```
  - Stateful 서비스 마이그레이션 (DB 연동)
  - 비용 최적화 (Spot, Savings Plans)
  - 운영 자동화 (업그레이드 파이프라인)
  - ECS 클러스터 종료 및 정리
  ```

:::notes
{timing: 2min}
30/60/90일 마이그레이션 로드맵입니다.

**Day 1-30 (기반 구축):**
- 인프라 자동화, GitOps, 스케일링 기본 설정
- 이 단계에서 IaC와 GitOps 패턴을 확립하는 것이 중요

**Day 31-60 (워크로드 마이그레이션):**
- Stateless 서비스부터 시작 (위험도 낮음)
- Canary 배포로 안전하게 트래픽 전환
- Observability 필수 — 문제 발생 시 빠른 롤백

**Day 61-90 (최적화 및 안정화):**
- Stateful 서비스는 신중하게 마이그레이션
- 비용 최적화로 ECS 대비 TCO 절감 확인
- ECS 종료로 이중 운영 비용 제거

{cue: transition}
다음 슬라이드에서 더 깊이 학습할 수 있는 Deep Dive 자료를 안내드립니다.
:::

---

## Deep Dive 참조 링크

::: left
### Networking
- [Gateway API](https://atomoh.gitbook.io/kubernetes-docs/networking/gateway-api)
- [VPC CNI 심화](https://atomoh.gitbook.io/kubernetes-docs/networking/vpc-cni)
- [Network Policy](https://atomoh.gitbook.io/kubernetes-docs/security/network-policies)

### Service Mesh
- [Istio 가이드](https://atomoh.gitbook.io/kubernetes-docs/service-mesh/istio)
- [Argo Rollouts](https://atomoh.gitbook.io/kubernetes-docs/service-mesh/istio/advanced/argo-rollouts)
:::

::: right
### Autoscaling
- [Karpenter](https://atomoh.gitbook.io/kubernetes-docs/autoscaling/karpenter)
- [KEDA](https://atomoh.gitbook.io/kubernetes-docs/autoscaling/keda)

### Security & Observability
- [EKS Security](https://atomoh.gitbook.io/kubernetes-docs/eks/eks-security)
- [Observability](https://atomoh.gitbook.io/kubernetes-docs/observability)
- [External Secrets](https://atomoh.gitbook.io/kubernetes-docs/security/secrets-management)
:::

:::notes
{timing: 1min}
Kubernetes Deep Dive GitBook 링크입니다.

왼쪽은 네트워킹과 서비스 메시 관련 자료:
- Gateway API: 차세대 Ingress 표준
- VPC CNI: Pod 네트워킹 심화
- Istio + Argo Rollouts: Progressive Delivery

오른쪽은 오토스케일링, 보안, 관측성:
- Karpenter: 노드 오토스케일링
- KEDA: 이벤트 기반 Pod 스케일링
- External Secrets: 시크릿 관리 모범 사례

모든 자료는 한글로 작성되어 있어 팀 내 공유에 용이합니다.
:::

---
@type: quiz

## Block 05 Quiz

**Q1: Observability의 3가지 축이 아닌 것은?**
- [ ] Logs
- [ ] Metrics
- [x] Alerts
- [ ] Traces

**Q2: Prometheus가 메트릭을 수집하는 방식은?**
- [ ] Push — 애플리케이션이 메트릭을 전송
- [x] Pull — Prometheus가 /metrics 엔드포인트 스크래핑
- [ ] Streaming — 실시간 스트리밍
- [ ] Batch — 배치로 일괄 수집

**Q3: EKS 클러스터 업그레이드 시 권장되는 전략은?**
- [ ] In-place 업그레이드
- [x] Blue/Green 클러스터 교체
- [ ] Rolling 노드 업그레이드만
- [ ] 다운타임 후 재생성

:::notes
{timing: 2min}
정답:
1. Alerts — Alerts는 Observability의 결과물이지 축이 아닙니다
2. Pull — Prometheus는 Pull 기반 아키텍처
3. Blue/Green — 컨트롤 플레인 롤백 불가하므로 새 클러스터로 전환이 안전

{cue: question}
퀴즈 풀이 후 질문 있으시면 말씀해주세요.
:::

---
@type: thankyou

## 수고하셨습니다!

ECS → EKS Migration Deep Dive 전체 과정을 마쳤습니다.

### 오늘 다룬 내용
- Multi-Cluster Active-Active Architecture
- GitOps & Progressive Delivery
- Scaling Strategy — Karpenter & KEDA
- Security & Platform Engineering
- Observability & Upgrade Strategy

[← 목차로 돌아가기](index.html)

---

### Contact & Deep Dive
- **Speaker**: 오준석 (Junseok Oh)
- **Email**: junseoko@amazon.com
- **GitBook**: [atomoh.gitbook.io/kubernetes-docs](https://atomoh.gitbook.io/kubernetes-docs)

:::notes
{timing: 2min}
전체 세션을 마쳤습니다. 수고하셨습니다!

오늘 다룬 5개 블록:
1. Multi-Cluster Active-Active
2. GitOps & Progressive Delivery
3. Karpenter & KEDA 스케일링
4. Security & Platform Engineering
5. Observability & Upgrade Strategy

{cue: question}
Q&A 시간입니다. 마이그레이션 관련 궁금한 점이 있으시면 질문해주세요.

Deep Dive가 필요하시면 GitBook 자료를 참고하시거나, 별도 워크샵을 요청해주세요.
감사합니다!
:::
