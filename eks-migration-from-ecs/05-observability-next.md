---
remarp: true
block: observability-next
---

@type: cover
@background: common/pptx-theme/images/Picture_13.png
@badge: common/pptx-theme/images/Picture_8.png

# ECS → EKS Migration Deep Dive
Observability & Next Steps (20 min)

오준석 (Junseok Oh)
Sr. Solutions Architect, AWS

:::notes
{timing: 1.5min}
마지막 블록입니다. 관측성(Observability)의 3가지 축과 EKS 업그레이드 전략, 그리고 마이그레이션 이후 로드맵을 다룹니다.
이 블록을 마치면 ECS에서 EKS로의 마이그레이션 전체 여정이 완료됩니다.

💬 예상 질문:
• "이 블록에서 가장 중요한 내용은?" → Observability 스택 선택과 Blue/Green 업그레이드 전략이 핵심입니다. 운영 안정성에 직접 영향을 미치는 부분입니다.
:::

---
@type: content

## Observability 3 Pillars

:::col-3
<div class="card" style="border:2px solid #F8B52A;text-align:center">
  <div style="font-size:2rem;margin-bottom:0.5rem">📋</div>
  <h3 style="color:#F8B52A">Logs</h3>
  <p>개별 이벤트의 불변 기록<br>디버깅 & 감사 추적</p>
  <div style="margin-top:0.8rem;font-size:0.75rem;color:var(--text-muted)">Loki / CloudWatch</div>
</div>
:::

:::col-3
<div class="card" style="border:2px solid #E6522C;text-align:center">
  <div style="font-size:2rem;margin-bottom:0.5rem">📊</div>
  <h3 style="color:#E6522C">Metrics</h3>
  <p>시계열 수치 데이터<br>집계 & 알람 기반</p>
  <div style="margin-top:0.8rem;font-size:0.75rem;color:var(--text-muted)">Prometheus / CloudWatch</div>
</div>
:::

:::col-3
<div class="card" style="border:2px solid #326CE5;text-align:center">
  <div style="font-size:2rem;margin-bottom:0.5rem">🔍</div>
  <h3 style="color:#326CE5">Traces</h3>
  <p>분산 요청 경로 추적<br>지연 구간 분석</p>
  <div style="margin-top:0.8rem;font-size:0.75rem;color:var(--text-muted)">X-Ray / Tempo</div>
</div>
:::

<div style="text-align:center;margin-top:0.8rem">
  <div style="display:inline-block;background:var(--bg-secondary);border:1px solid var(--border);border-radius:8px;padding:0.4rem 1.5rem;font-size:0.85rem;color:var(--text-secondary)">
    TraceID로 Logs ↔ Traces 연결 | Exemplar로 Metrics → Traces 점프
  </div>
</div>

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

현재 이 세 가지 중 어떤 것을 가장 많이 활용하고 계신가요?

💬 예상 질문:
• "Exemplar가 정확히 뭔가요?" → 메트릭 데이터 포인트에 TraceID를 첨부하는 기능입니다. P99 레이턴시 스파이크가 발생했을 때, 해당 시점의 실제 요청 트레이스로 바로 점프할 수 있습니다.
• "세 가지 다 구축해야 하나요?" → 우선순위는 Metrics > Logs > Traces 순입니다. Metrics로 문제 감지, Logs로 원인 분석, Traces로 병목 구간 파악 순서로 도입하세요.
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
| **Logs** | Loki + Fluent Bit | 경량, 라벨 기반 쿼리, 비용 효율 |
| **Metrics** | Prometheus (AMP) + Grafana | PromQL, 무제한 커스텀 메트릭 |
| **Traces** | Tempo + OpenTelemetry | 벤더 중립, 전체 샘플링 가능 |
| **Dashboard** | Grafana (AMG) | 통합 시각화, 알림, 상관분석 |

:::notes
{timing: 2.5min}
현재 CloudWatch 중심 스택에서 LGTM(Loki, Grafana, Tempo, Mimir) 또는 Prometheus 기반 스택으로 전환을 권장합니다.

AWS 관리형 서비스:
- AMP (Amazon Managed Service for Prometheus): Prometheus 호환 메트릭 저장소
- AMG (Amazon Managed Grafana): 완전 관리형 Grafana

오픈소스 vs 관리형 선택은 운영 역량과 비용을 고려해서 결정하세요.

참고: 현재 사용 중인 OpenSearch(Elastic)는 Loki 전환 시 듀얼 출력 전략을 권장합니다. Fluent Bit에서 OpenSearch와 Loki 두 곳으로 동시 전송하다가, Loki 안정화 후 OpenSearch를 축소하는 방식입니다.

💬 예상 질문:
• "CloudWatch를 완전히 버려야 하나요?" → 아닙니다. Container Insights는 기본으로 유지하고, 상세 모니터링용으로 Prometheus를 추가하는 하이브리드 구성을 권장합니다.
• "Loki vs CloudWatch Logs 비용 차이는?" → 대용량 로그 환경에서 Loki + S3 백엔드가 CloudWatch Logs 대비 50-70% 저렴합니다. 단, 운영 인력 비용도 고려해야 합니다.
:::

---
@type: content

## Prometheus + Grafana 아키텍처

<div style="display:flex;align-items:center;justify-content:center;gap:0;flex-wrap:nowrap;padding:1rem 0;">
  <div style="display:flex;flex-direction:column;gap:0.5rem;align-items:center;">
    <div style="background:#4CAF50;color:#fff;padding:0.5rem 1rem;border-radius:6px;font-size:0.85rem;text-align:center">App Pod</div>
    <div style="background:#4CAF50;color:#fff;padding:0.5rem 1rem;border-radius:6px;font-size:0.85rem;text-align:center">App Pod</div>
    <div style="background:#4CAF50;color:#fff;padding:0.5rem 1rem;border-radius:6px;font-size:0.85rem;text-align:center">App Pod</div>
    <div style="color:var(--text-muted);font-size:0.75rem;margin-top:0.2rem">/metrics</div>
  </div>
  <div style="display:flex;flex-direction:column;align-items:center;padding:0 0.8rem">
    <span style="color:var(--accent);font-size:1.3rem">←</span>
    <span style="color:var(--text-muted);font-size:0.7rem">scrape</span>
  </div>
  <div style="background:#326CE5;color:#fff;padding:0.8rem 1.2rem;border-radius:8px;font-size:0.9rem;text-align:center;line-height:1.4">
    <strong>ServiceMonitor</strong><br><small style="opacity:0.8">Prometheus Operator CRD</small>
  </div>
  <div style="display:flex;flex-direction:column;align-items:center;padding:0 0.8rem">
    <span style="color:var(--accent);font-size:1.3rem">→</span>
    <span style="color:var(--text-muted);font-size:0.7rem">configure</span>
  </div>
  <div style="background:#E6522C;color:#fff;padding:0.8rem 1.2rem;border-radius:8px;font-size:0.9rem;text-align:center;line-height:1.4">
    <strong>Prometheus</strong><br><small style="opacity:0.8">Pull 방식 수집</small>
  </div>
  <div style="display:flex;flex-direction:column;align-items:center;padding:0 0.8rem">
    <span style="color:var(--accent);font-size:1.3rem">→</span>
    <span style="color:var(--text-muted);font-size:0.7rem">remote write</span>
  </div>
  <div style="background:#FF9900;color:#fff;padding:0.8rem 1.2rem;border-radius:8px;font-size:0.9rem;text-align:center;line-height:1.4">
    <strong>AMP</strong><br><small style="opacity:0.8">Amazon Managed<br>Prometheus</small>
  </div>
  <div style="display:flex;flex-direction:column;align-items:center;padding:0 0.8rem">
    <span style="color:var(--accent);font-size:1.3rem">→</span>
    <span style="color:var(--text-muted);font-size:0.7rem">PromQL</span>
  </div>
  <div style="background:#F8B52A;color:#000;padding:0.8rem 1.2rem;border-radius:8px;font-size:0.9rem;text-align:center;line-height:1.4">
    <strong>Grafana (AMG)</strong><br><small>대시보드 & 알림</small>
  </div>
</div>

:::col-3
<div class="card" style="border-left:3px solid #326CE5">
  <h4 style="color:#326CE5;margin:0 0 .3rem">ServiceMonitor</h4>
  <p style="font-size:0.85rem;margin:0">라벨 셀렉터로 스크래핑 대상 자동 발견. 새 서비스 배포 시 수동 설정 불필요</p>
</div>
:::

:::col-3
<div class="card" style="border-left:3px solid #E6522C">
  <h4 style="color:#E6522C;margin:0 0 .3rem">Pull 기반 수집</h4>
  <p style="font-size:0.85rem;margin:0">Prometheus가 /metrics 엔드포인트를 주기적으로 스크래핑 (기본 30s)</p>
</div>
:::

:::col-3
<div class="card" style="border-left:3px solid #FF9900">
  <h4 style="color:#FF9900;margin:0 0 .3rem">AWS 관리형</h4>
  <p style="font-size:0.85rem;margin:0">AMP + AMG로 운영 부담 최소화. HA/스토리지 자동 관리</p>
</div>
:::

:::notes
{timing: 2.5min}
Prometheus 기반 모니터링 아키텍처입니다.

전체 흐름: App Pod → ServiceMonitor(자동 발견) → Prometheus(Pull 수집) → AMP(관리형 저장) → Grafana(시각화)

1. **ServiceMonitor**: Prometheus Operator CRD. 라벨 셀렉터로 스크래핑 대상 자동 발견
2. **Pull 기반**: 애플리케이션의 /metrics 엔드포인트에서 주기적으로 수집 (기본 30s)
3. **AWS 관리형**: AMP + AMG 사용 시 HA/스토리지 자동 관리, 운영 부담 최소화

실제 ServiceMonitor 설정과 Grafana 대시보드 예시를 보여드리겠습니다.

💬 예상 질문:
• "Pull 방식이면 방화벽 설정은 어떻게?" → Prometheus가 Pod의 /metrics를 호출하므로, Pod 간 통신만 열려 있으면 됩니다. 클러스터 내부 통신이라 추가 방화벽 설정은 불필요합니다.
• "AMP 없이 자체 Prometheus 운영하면?" → 가능하지만 HA 구성, 스토리지 관리, 업그레이드 등 운영 부담이 큽니다. 월 $100-200 수준이면 AMP가 훨씬 효율적입니다.
:::

---
@type: code

## Prometheus + Grafana 셋업

```yaml {filename="servicemonitor.yaml" highlight="7-11"}
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: hwahae-api
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: hwahae-api      # 자동 발견
  endpoints:
    - port: metrics        # metrics 포트
      interval: 30s        # 30초 스크래핑
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
    grafana_dashboard: "1"
    # Grafana sidecar가 자동 로드
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

💬 예상 질문:
• "서비스마다 ServiceMonitor를 만들어야 하나요?" → 라벨 기반이라 하나의 ServiceMonitor로 여러 서비스를 커버할 수 있습니다. 예: app.kubernetes.io/part-of: hwahae 라벨을 공통으로 붙이면 됩니다.
• "대시보드 JSON은 어디서 구하나요?" → Grafana Labs에서 커뮤니티 대시보드를 제공합니다. EKS용, Karpenter용 등 검색해서 import 후 커스터마이징하세요.
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

### OSS Stack (Prometheus + Loki + Tempo)
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

수십 개 서비스 규모에서는 OSS Stack + AWS 관리형(AMP, AMG)을 권장합니다.
월 비용이 Datadog 대비 50-70% 절감 가능합니다.

💬 예상 질문:
• "Datadog 쓰다가 OSS로 전환한 사례가 있나요?" → 많습니다. 보통 월 $10K 이상 지출 시점에 전환을 검토합니다. 전환 시 Datadog Agent → OTel Collector로 교체하고, 대시보드를 Grafana로 재구축합니다.
• "New Relic, Dynatrace는요?" → 비슷한 SaaS 모델입니다. 기능은 우수하나 비용 구조가 복잡하고 예측하기 어렵습니다.
:::

---
@type: timeline

## 기존 OpenSearch와 공존 전략

1. **Phase 1: 메트릭 우선 (Month 1-2)** — 기존 OpenSearch 유지, Prometheus(AMP) + Grafana(AMG) 추가, CloudWatch Container Insights 병행
2. **Phase 2: 듀얼 로그 파이프라인 (Month 3-4)** — Fluent Bit 듀얼 아웃풋: OpenSearch + ClickHouse, 신규 서비스는 ClickHouse 전용
3. **Phase 3: 트레이싱 도입 (Month 5-6)** — OpenTelemetry Collector 설치, ClickHouse에 트레이스 저장, Grafana에서 상관분석
4. **Phase 4: 통합 완료 (Month 7+)** — OpenSearch 트래픽 모니터링, 단계적 축소 또는 공존 유지, 비용 비교 후 최종 판단

:::notes
{timing: 2.5min}
기존 OpenSearch와 공존하면서 점진적으로 전환하는 전략입니다.

**Phase 1**: 메트릭부터 시작합니다. OpenSearch는 그대로 두고 Prometheus + Grafana만 추가합니다.
**Phase 2**: Fluent Bit 듀얼 아웃풋으로 로그를 OpenSearch와 ClickHouse 양쪽에 전송합니다.
**Phase 3**: 트레이싱을 도입하고 Grafana에서 상관분석을 시작합니다.
**Phase 4**: OpenSearch 트래픽을 모니터링하고 실제 사용량 기반으로 축소 여부를 결정합니다.

💬 예상 질문:
• "왜 Loki 대신 ClickHouse인가요?" → ClickHouse는 SQL 기반 쿼리가 가능하고, 로그뿐 아니라 트레이스도 저장할 수 있어 통합 백엔드로 적합합니다. Loki는 로그 전용이라 별도 Tempo가 필요합니다.
• "듀얼 아웃풋 시 스토리지 비용이 2배 아닌가요?" → 맞습니다. 하지만 전환 기간(2-3개월)만 병행하고, 이후 OpenSearch를 축소하면 됩니다. 안전한 전환을 위한 비용입니다.
:::

---
@type: code

## Fluent Bit 듀얼 아웃풋 설정

```yaml {filename="fluent-bit-dual-output.yaml"}
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
{timing: 1.5min}
Fluent Bit 듀얼 아웃풋 설정 예시입니다.

기존 서비스는 OpenSearch + ClickHouse 양쪽에 전송하고, 신규 서비스는 ClickHouse 전용으로 설정합니다. Match 패턴으로 네임스페이스별 라우팅이 가능합니다.

💬 예상 질문:
• "Fluent Bit이 병목이 되지 않나요?" → DaemonSet으로 노드당 하나씩 배포하고, 버퍼 설정을 적절히 조정하면 문제없습니다. 메모리 512MB ~ 1GB 정도면 충분합니다.
• "기존 OpenSearch 대시보드는 어떻게 하나요?" → 듀얼 기간 동안 그대로 사용하고, Grafana 대시보드를 병행 구축합니다. 팀이 Grafana에 익숙해지면 OpenSearch 대시보드를 deprecate합니다.
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
핵심 메트릭 모니터링 팁입니다. 탭을 클릭해서 각 영역별 PromQL 쿼리를 확인하세요.

**EKS 필수**: 노드 CPU, Pod Restart, Pending Pod — 이 세 가지는 반드시 알림을 설정하세요.
**Karpenter**: Spot 중단 횟수와 Consolidation 이벤트를 모니터링해야 비용 최적화와 안정성의 균형을 잡을 수 있습니다.
**SQS/KEDA**: 큐 깊이 대비 Worker Pod 비율로 스케일링이 적절한지 판단합니다.

💬 예상 질문:
• "알림은 어디로 보내나요?" → Grafana Alerting → Slack/PagerDuty 연동이 일반적입니다. 심각도별로 채널을 분리하세요(Critical → PagerDuty, Warning → Slack).
• "PromQL 학습 자료 추천해주세요" → Prometheus 공식 문서와 PromLabs 블로그를 추천합니다. 실제 쿼리를 Grafana Explore에서 직접 실행해보는 게 가장 빠릅니다.
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

현재 EKS 버전은 몇 버전인가요? 업그레이드 주기는 어떻게 관리하시나요?

💬 예상 질문:
• "Blue/Green이면 비용이 2배 아닌가요?" → 전환 기간(1-2주)만 양쪽 클러스터를 유지합니다. Karpenter Consolidation으로 노드 수를 최소화하면 추가 비용은 10-20% 수준입니다.
• "인플레이스 업그레이드는 언제 괜찮나요?" → Dev/Staging 환경, 또는 EKS 마이너 버전 패치(1.29.1 → 1.29.2)는 인플레이스도 괜찮습니다. 메이저 버전 업그레이드는 Blue/Green 필수입니다.
:::

---
@type: compare

## DR 전략: GitOps 재구축 vs Velero 백업

### GitOps 기반 재구축
- **원본**: Git Repository = 클러스터 상태
- **복구**: ArgoCD Sync → 전체 복원
- **대상**: Stateless 워크로드에 최적
- **RTO**: 30분 ~ 1시간
- **추가 인프라**: 불필요
- **비용**: 없음 (Git 활용)

### Velero 백업/복구
- **원본**: etcd 스냅샷 + PV 백업
- **복구**: 네임스페이스/리소스 단위 선택적 복구
- **대상**: Stateful 워크로드 필수
- **RTO**: 15분 ~ 30분
- **추가 인프라**: S3 + Velero 서버
- **비용**: S3 저장 비용

:::callout-info
**권장**: Stateless 서비스 → GitOps 재구축 (추가 비용 0), DB → RDS 자체 백업/복구 활용, PV 있는 워크로드만 Velero 선택적 적용
:::

:::notes
{timing: 1.5min}
DR 전략 선택지입니다. GitOps 기반 재구축은 Git이 클러스터 상태의 원본이므로 별도 백업 인프라 없이도 ArgoCD Sync만으로 전체 복원이 가능합니다. Stateless 워크로드에 최적입니다.

Velero는 etcd 스냅샷과 PV 백업을 제공하여 Stateful 워크로드 복구에 필수적입니다. 하지만 대부분의 상태는 RDS, ElastiCache 등 관리형 서비스에 있으므로, 이러한 환경에서는 GitOps 재구축 + RDS 자체 백업 조합이 가장 효율적입니다.

💬 예상 질문:
• "Velero 백업 주기는 어떻게 설정하나요?" → 일반적으로 일 1회 전체 백업 + 시간당 증분 백업입니다. S3 Lifecycle 정책으로 30일 보관 후 자동 삭제하세요.
• "Cross-region DR은 어떻게?" → GitOps 기반이면 다른 리전에 클러스터만 만들고 ArgoCD Sync하면 됩니다. RDS는 Cross-region Read Replica를 미리 구성해두세요.
:::

---
@type: content

## 비용 모니터링 & 최적화

:::col-3
<div class="card" style="border-top:3px solid #4CAF50">
  <h3 style="color:#4CAF50;margin:0 0 .8rem">KubeCost</h3>
  <ul>
    <li>네임스페이스/워크로드별 비용 할당</li>
    <li>유휴 리소스 탐지 및 알림</li>
    <li>비용 예측 대시보드</li>
    <li><strong>무료 티어</strong>로 시작 가능</li>
  </ul>
</div>
:::

:::col-3
<div class="card" style="border-top:3px solid #FF9900">
  <h3 style="color:#FF9900;margin:0 0 .8rem">Right-sizing</h3>
  <ul>
    <li>VPA 권장값 기반 리소스 조정</li>
    <li>requests/limits 최적화</li>
    <li>Karpenter Consolidation 연계</li>
    <li>Over-provisioning 방지</li>
  </ul>
</div>
:::

:::col-3
<div class="card" style="border-top:3px solid #326CE5">
  <h3 style="color:#326CE5;margin:0 0 .8rem">Savings Plans + Spot</h3>
  <ul>
    <li>Compute Savings Plans (1yr/3yr)</li>
    <li>Spot Instance 활용 (Karpenter)</li>
    <li>On-Demand 대비 <strong>40-70% 절감</strong></li>
    <li>RI → SP 전환 검토</li>
  </ul>
</div>
:::

:::callout-info
**$5K-$20K/월 규모** → KubeCost 무료 티어로 시작, 네임스페이스별 비용 가시성 확보 후 Right-sizing 적용. Savings Plans로 장기 절감
:::

:::notes
{timing: 1.5min}
비용 최적화 3가지 축입니다.

KubeCost: 무료 티어로 네임스페이스별 비용 가시성을 확보하세요. 어떤 팀이, 어떤 서비스가 비용을 많이 사용하는지 파악이 우선입니다.

Right-sizing: VPA의 권장값을 참고하여 requests/limits를 최적화합니다. Karpenter Consolidation과 연계하면 노드 활용률도 자동으로 높아집니다.

Savings Plans: 안정적인 베이스라인 워크로드에 1년/3년 Compute Savings Plans를 적용하고, 변동 워크로드는 Spot으로 처리하면 전체 40-70% 절감이 가능합니다.

💬 예상 질문:
• "KubeCost 무료 버전 한계는?" → 단일 클러스터, 15일 데이터 보존입니다. 멀티 클러스터나 장기 분석이 필요하면 유료 버전 또는 OpenCost(오픈소스)를 검토하세요.
• "Savings Plans vs Reserved Instances?" → Savings Plans가 더 유연합니다. 인스턴스 패밀리에 종속되지 않고, Fargate에도 적용됩니다. 신규 구매는 SP를 권장합니다.
:::

---
@type: tabs

## 분산 추적 구현: ADOT → X-Ray / Tempo

<div style="display:flex;align-items:center;justify-content:center;gap:0.8rem;flex-wrap:wrap;margin-bottom:1.5rem">
  <div class="badge-green" style="padding:0.6rem 1.2rem;font-size:0.95rem">App (OTel SDK)</div>
  <span style="color:var(--text-muted);font-size:1.2rem">→</span>
  <div style="background:#FF9900;color:#fff;padding:0.6rem 1.2rem;border-radius:6px;font-size:0.95rem">ADOT Collector<br><small style="opacity:0.8">DaemonSet</small></div>
  <span style="color:var(--text-muted);font-size:1.2rem">→</span>
  <div style="display:flex;flex-direction:column;gap:0.5rem">
    <div style="background:#326CE5;color:#fff;padding:0.4rem 1rem;border-radius:6px;font-size:0.9rem;text-align:center">X-Ray <small>(AWS 네이티브)</small></div>
    <div style="background:#E6522C;color:#fff;padding:0.4rem 1rem;border-radius:6px;font-size:0.9rem;text-align:center">Tempo <small>(Grafana 연동)</small></div>
  </div>
</div>

### 1단계: ADOT + X-Ray
**빠른 시작 — AWS 관리형**
- ADOT Collector DaemonSet 설치 (EKS Add-on 지원)
- X-Ray 자동 연동 → AWS Console에서 트레이스 확인
- Java/Node.js Auto-instrumentation으로 코드 변경 최소화

```bash
# ADOT Add-on 설치
aws eks create-addon \
  --cluster-name hwahae-eks \
  --addon-name adot \
  --addon-version v0.92.1-eksbuild.1
```

### 2단계: + Tempo
**Grafana 통합 — Logs/Metrics/Traces 상관분석**
- Grafana Tempo 추가 설치 (S3 백엔드)
- ADOT Collector에 Tempo exporter 추가
- Grafana에서 Loki ↔ Prometheus ↔ Tempo 연결
- TraceID로 로그-메트릭-트레이스 원클릭 전환

### 3단계: 계측 확대
**서비스 계측 확대**
- Auto-instrumentation → Manual Spans 추가
- 비즈니스 로직 핵심 구간 커스텀 Span
- DB 쿼리, 외부 API 호출 추적
- Sampling 전략 수립 (Head-based → Tail-based)

:::callout-info
**현재 "분산 추적 미구축"** → 1단계 ADOT + X-Ray부터 시작 권장. EKS Add-on으로 설치하면 Terraform으로 관리 가능
:::

:::notes
{timing: 2min}
분산 추적 도입 로드맵입니다. 현재 분산 추적이 미구축된 상태이므로 단계별로 도입합니다.

1단계: ADOT(AWS Distro for OpenTelemetry) Collector를 EKS Add-on으로 설치하고 X-Ray와 연동합니다. Auto-instrumentation으로 코드 변경 없이 시작할 수 있습니다.

2단계: Grafana Tempo를 추가하여 Loki(로그), Prometheus(메트릭), Tempo(트레이스)를 Grafana에서 통합합니다. TraceID 하나로 로그-메트릭-트레이스를 오갈 수 있습니다.

3단계: 비즈니스 로직의 핵심 구간에 커스텀 Span을 추가하여 병목 구간을 정밀하게 파악합니다.

💬 예상 질문:
• "Auto-instrumentation이 성능에 영향을 주나요?" → 약간의 오버헤드(5% 미만)가 있습니다. 샘플링 비율을 조정하여 프로덕션 부하를 관리하세요. 초기엔 10% 샘플링으로 시작을 권장합니다.
• "X-Ray vs Jaeger vs Tempo?" → X-Ray는 AWS 네이티브로 빠른 도입에 적합, Tempo는 Grafana 생태계 통합에 최적, Jaeger는 자체 호스팅 선호 시 선택합니다.
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
  - Observability 스택 구축 (Prometheus, Loki)
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
{timing: 1.5min}
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

다음 슬라이드에서 더 깊이 학습할 수 있는 Deep Dive 자료를 안내드립니다.

💬 예상 질문:
• "90일이면 충분한가요?" → 규모에 따라 다릅니다. 서비스 10개 이하면 90일, 30개 이상이면 6개월 이상 잡으세요. 핵심은 속도보다 안정성입니다.
• "마이그레이션 중 양쪽 운영 비용은?" → 불가피합니다. 듀얼 운영 기간을 최소화하려면 서비스 단위로 완전히 전환 후 다음 서비스로 넘어가세요.
:::

---
@type: content

## Deep Dive 참조 링크

:::left
### Networking
- [Gateway API](https://atomoh.gitbook.io/kubernetes-docs/networking/gateway-api)
- [VPC CNI 심화](https://atomoh.gitbook.io/kubernetes-docs/networking/vpc-cni)
- [Network Policy](https://atomoh.gitbook.io/kubernetes-docs/security/network-policies)

### Service Mesh
- [Istio 가이드](https://atomoh.gitbook.io/kubernetes-docs/service-mesh/istio)
- [Argo Rollouts](https://atomoh.gitbook.io/kubernetes-docs/service-mesh/istio/advanced/argo-rollouts)
:::

:::right
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

💬 예상 질문:
• "GitBook 자료가 최신인가요?" → 주기적으로 업데이트하고 있습니다. EKS 버전별 변경사항도 반영됩니다.
• "오프라인 워크샵 가능한가요?" → 네, 별도로 요청해주시면 맞춤형 Deep Dive 세션을 진행할 수 있습니다.
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

퀴즈 풀이 후 질문 있으시면 말씀해주세요.

💬 예상 질문:
• "Push 기반 메트릭 수집은 언제 쓰나요?" → 단기 배치 잡이나 서버리스 환경에서는 Push(Pushgateway)를 사용합니다. 일반적인 장기 실행 서비스는 Pull이 더 적합합니다.
• "In-place 업그레이드로 성공한 사례도 있지 않나요?" → 있습니다. 하지만 문제 발생 시 롤백이 불가능해 리스크가 큽니다. 프로덕션에서는 Blue/Green이 안전합니다.
:::

---
@type: thankyou

# 수고하셨습니다!

전체 세션 질문 & 피드백을 환영합니다

[← 목차로 돌아가기](index.html)

**Speaker**: 오준석 (Junseok Oh) · **Email**: junseoko@amazon.com
**GitBook**: [atomoh.gitbook.io/kubernetes-docs](https://atomoh.gitbook.io/kubernetes-docs)

:::notes
{timing: 2min}
전체 세션을 마쳤습니다. 수고하셨습니다!

오늘 다룬 5개 블록:
1. Multi-Cluster Active-Active
2. GitOps & Progressive Delivery
3. Karpenter & KEDA 스케일링
4. Security & Platform Engineering
5. Observability & Upgrade Strategy

Q&A 시간입니다. 마이그레이션 관련 궁금한 점이 있으시면 질문해주세요.

Deep Dive가 필요하시면 GitBook 자료를 참고하시거나, 별도 워크샵을 요청해주세요.
감사합니다!

💬 예상 질문:
• "가장 먼저 시작해야 할 것은?" → GitOps(ArgoCD) 파이프라인 구축입니다. 이게 있어야 모든 변경이 추적 가능하고, 롤백도 쉬워집니다.
• "AWS SA 지원을 더 받을 수 있나요?" → 네, Enterprise Support 고객이시면 TAM을 통해 추가 워크샵이나 아키텍처 리뷰를 요청하실 수 있습니다.
:::
