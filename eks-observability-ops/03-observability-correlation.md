---
marp: true
title: "Block 3: Observability Correlation"
theme: default
paginate: true
---

<!-- block: observability-correlation -->

<!-- type: title -->

# 도구 간 데이터 연결이 안 됩니다

**Block 3: Observability Correlation (35분)**

> "Grafana에 Prometheus, Loki, Tempo 다 연결했는데, 에러 발생 시 각각 따로 검색해야 합니다"

> "메트릭 스파이크가 보이는데, 관련 로그와 트레이스를 찾는 데 20분 이상 걸립니다"

**핵심 문제:** 3가지 시그널(Metrics, Logs, Traces)이 있지만 연결되지 않으면 MTTR(평균 복구 시간)이 늘어남

| 20분+ | 3개 | 컨텍스트 손실 |
|-------|-----|---------------|
| 수동 상관관계 분석 | 별도 UI 전환 필요 | 시그널 간 연결고리 부재 |

<!-- notes: 운영자들이 겪는 가장 큰 고통점 중 하나입니다. 도구는 다 있는데 연결이 안 되어 있어서 장애 분석 시간이 길어집니다. -->

---

<!-- type: content -->

# 관측성 3대 축 + Grafana 스택

### Metrics (Prometheus / AMP)
- "무엇이 문제인가?"
- 수치 기반 이상 탐지

### Logs (Loki)
- "왜 발생했는가?"
- 상세 컨텍스트

### Traces (Tempo)
- "어디서 발생했는가?"
- 분산 요청 추적

**Grafana** - 통합 대시보드

<!-- notes: 관측성의 3대 축은 각각 다른 질문에 답합니다. Grafana가 이 세 가지를 통합하는 허브 역할을 합니다. -->

---

<!-- type: canvas -->

# 3-Signal Correlation 시뮬레이터

**Exemplar를 통한 메트릭 -> 트레이스 -> 로그 연결**

애니메이션 설명:
1. Metrics 컬럼에서 라인 차트가 표시되고, 에러 시 스파이크가 발생
2. 스파이크 포인트에 Exemplar(다이아몬드 마커)가 표시됨
3. Exemplar 클릭 시 화살표가 Traces 컬럼으로 이동
4. Traces에서 span waterfall이 나타나고 에러 span이 빨간색으로 강조됨
5. 화살표가 Logs 컬럼으로 이동
6. 관련 로그가 표시되고 에러 메시지가 강조됨

단계별 레이블:
- 1. 메트릭 스파이크 발생
- 2. Exemplar 표시
- 3. 트레이스로 이동
- 4. 에러 span 식별
- 5. 관련 로그 조회
- 6. 에러 메시지 확인

<!-- notes: 실제로 Grafana에서 메트릭 -> 트레이스 -> 로그로 이동하는 과정을 시뮬레이션합니다. -->

---

<!-- type: content -->

# Exemplars: 메트릭 -> 트레이스 연결

## Exemplar란?

히스토그램 메트릭의 특정 데이터 포인트에 **TraceID**를 첨부하여 해당 요청의 트레이스로 바로 이동할 수 있게 해주는 기능

- Prometheus 2.26+ 지원
- 히스토그램/Summary 메트릭에 적용
- OpenMetrics 형식 필요

> **동작 원리:** 메트릭 그래프에서 특정 데이터 포인트 클릭 -> TraceID 확인 -> Tempo에서 상세 트레이스 조회

## Prometheus Datasource 설정

```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    jsonData:
      exemplarTraceIdDestinations:
        - name: traceID
          datasourceUid: tempo
          urlDisplayLabel: "View Trace"
```

<!-- notes: Exemplar는 메트릭 그래프에서 다이아몬드 모양으로 표시됩니다. 클릭하면 해당 요청의 트레이스로 바로 이동할 수 있습니다. -->

---

<!-- type: tabs -->

# Grafana 데이터소스 설정

### Prometheus

**핵심 설정:**
- **endpoint:** Prometheus/AMP 엔드포인트
- **exemplarTraceIdDestinations:** 트레이스 연결 설정
- **httpMethod:** GET 또는 POST

```yaml
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    jsonData:
      httpMethod: POST
      exemplarTraceIdDestinations:
        - name: traceID
          datasourceUid: tempo
          urlDisplayLabel: "View Trace"
```

### Loki

**핵심 설정:**
- **endpoint:** Loki 게이트웨이 URL
- **derivedFields:** TraceID 추출 정규식
- **maxLines:** 최대 로그 라인 수

```yaml
datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://loki-gateway:3100
    jsonData:
      maxLines: 1000
      derivedFields:
        - name: TraceID
          matcherRegex: '"traceId":"([a-f0-9]+)"'
          url: '$${__value.raw}'
          datasourceUid: tempo
```

### Tempo

**핵심 설정:**
- **tracesToLogs:** 트레이스 -> 로그 연결
- **tracesToMetrics:** 트레이스 -> 메트릭 연결
- **serviceMap:** 서비스 맵 활성화

```yaml
datasources:
  - name: Tempo
    type: tempo
    url: http://tempo:3200
    jsonData:
      tracesToLogs:
        datasourceUid: loki
        tags: ['namespace', 'pod']
        filterByTraceID: true
      tracesToMetrics:
        datasourceUid: prometheus
      serviceMap:
        datasourceUid: prometheus
```

<!-- notes: 각 데이터소스 설정에서 다른 데이터소스와의 연결을 정의합니다. 이것이 상관관계의 핵심입니다. -->

---

<!-- type: canvas -->

# Loki <-> Tempo 양방향 연동

애니메이션 설명:
- 왼쪽에 Loki 박스, 오른쪽에 Tempo 박스가 표시됨
- Loki에는 traceId가 포함된 로그 라인들이 표시됨
- Tempo에는 span waterfall이 표시됨
- "Loki -> Tempo" 버튼 클릭 시: Derived Fields를 통해 화살표가 Loki에서 Tempo로 이동
- "Tempo -> Loki" 버튼 클릭 시: tracesToLogs를 통해 화살표가 Tempo에서 Loki로 이동

## Loki -> Tempo (Derived Fields)

```yaml
derivedFields:
  - name: TraceID
    matcherRegex: '"traceId":"([a-f0-9]+)"'
    datasourceUid: tempo
```

## Tempo -> Loki (tracesToLogs)

```yaml
tracesToLogs:
  datasourceUid: loki
  tags: ['namespace', 'pod']
  filterByTraceID: true
```

<!-- notes: 양방향 연동이 중요합니다. 로그에서 트레이스로, 트레이스에서 로그로 자유롭게 이동할 수 있어야 합니다. -->

---

<!-- type: content -->

# Derived Fields & tracesToLogs 설정

## 정규식 테스터

샘플 로그:
```json
{"timestamp":"2024-01-15T10:30:00Z","level":"ERROR","traceId":"abc123def456789012345678","service":"payment-service","message":"Payment failed: Connection timeout to RDS"}
```

## 일반적인 TraceID 패턴

| 형식 | 정규식 |
|------|--------|
| JSON 필드 | `"traceId":"([a-f0-9]+"` |
| W3C Trace Context | `traceparent.*-([a-f0-9]{32})-` |
| Jaeger | `uber-trace-id:([a-f0-9]+):` |

## 주의사항

- 정규식은 **캡처 그룹 ()** 이 필수
- 첫 번째 캡처 그룹이 TraceID로 사용됨
- 대소문자 구분에 주의 (보통 소문자)
- 로그 형식 변경 시 정규식도 업데이트 필요

<!-- notes: Derived Fields 설정 시 정규식이 핵심입니다. 캡처 그룹을 잘못 지정하면 TraceID 추출이 안 됩니다. -->

---

<!-- type: tabs -->

# TraceQL 소개

**Tempo의 강력한 트레이스 쿼리 언어**

### 기본

```
{ resource.service.name = "payment-service" }
```
payment-service에서 발생한 모든 트레이스를 검색합니다.

```
{ span.http.method = "POST" }
```
HTTP POST 요청이 포함된 트레이스를 검색합니다.

### 에러

```
{ status = error }
```
에러 상태의 span이 포함된 트레이스를 검색합니다.

```
{ span.http.status_code >= 500 }
```
HTTP 5xx 에러가 발생한 트레이스를 검색합니다.

### 지연

```
{ duration > 1s }
```
1초 이상 걸린 span이 포함된 트레이스를 검색합니다.

```
{ duration > 500ms && duration < 2s }
```
500ms ~ 2s 사이의 span을 검색합니다.

### 복합

```
{ span.http.status_code >= 400 && duration > 500ms }
```
HTTP 4xx/5xx 에러이면서 500ms 이상 걸린 트레이스를 검색합니다.

```
{ resource.service.name = "api-gateway" && status = error } | count() > 5
```
api-gateway에서 에러 span이 5개 이상인 트레이스를 검색합니다.

### 체인

```
{ resource.service.name = "api-gateway" } >> { resource.service.name = "payment-service" }
```
api-gateway에서 payment-service로 이어지는 호출 경로를 가진 트레이스를 검색합니다.

```
{ name = "HTTP GET" } >> { name = "SELECT" && duration > 100ms }
```
HTTP GET 이후 100ms 이상 걸리는 DB SELECT가 있는 트레이스를 검색합니다.

<!-- notes: TraceQL은 LogQL과 비슷한 문법을 가지고 있습니다. 복잡한 트레이스 검색이 가능합니다. -->

---

<!-- type: canvas -->

# Service Map 시각화

**마이크로서비스 의존성 그래프**

애니메이션 설명:
- 서비스 노드들이 그래프 형태로 표시됨
  - API Gateway (왼쪽)
  - Auth Service, Payment Service, Order Service (중간)
  - Notification, Database (오른쪽)
- 각 노드 사이에 화살표와 요청률(req/s)이 표시됨
- "장애 주입" 버튼 클릭 시:
  - Payment Service 노드가 빨간색으로 변경
  - Database 노드가 노란색으로 변경
  - 관련 경로가 노란색으로 하이라이트됨
  - "Payment Service 장애 -> 상위 경로 지연 전파" 메시지 표시

| 상태 | 색상 |
|------|------|
| Healthy | 초록색 |
| Slow (p99 > 500ms) | 노란색 |
| Error (> 1%) | 빨간색 |

<!-- notes: Service Map은 마이크로서비스 간의 의존성을 시각화합니다. 장애 전파 경로를 파악하는 데 유용합니다. -->

---

<!-- type: compare -->

# RED Method vs 4 Golden Signals

**두 방법론의 관계와 차이 — 메트릭 3개가 겹칩니다**

### RED Method

- **출처:** Tom Wilkie (Grafana Labs)
- **관점:** 마이크로서비스 — "내 서비스가 잘 응답하는가?"

| Rate | Errors | Duration |
|------|--------|----------|
| 1,247 req/s | 0.12% | 45ms (p99) |
| 초당 요청 수 | 에러율 | 응답 시간 |

### 4 Golden Signals

- **출처:** Google SRE Book (2016)
- **관점:** 인프라 + 서비스 — "시스템 전체가 건강한가?"

| Latency | Traffic | Errors | **Saturation** |
|---------|---------|--------|------------|
| 45ms | 1,247 req/s | 0.12% | **72%** |
| 요청 처리 시간 | 시스템 부하 | 실패율 | **리소스 포화도** |

### 메트릭 매핑

| RED Method | | 4 Golden Signals | PromQL 예시 |
|------------|---|-----------------|-------------|
| **Rate** | = | **Traffic** | `rate(http_requests_total[5m])` |
| **Errors** | = | **Errors** | `rate(http_requests_total{code=~"5.."}[5m])` |
| **Duration** | = | **Latency** | `histogram_quantile(0.99, ...)` |
| — | + | **Saturation** | `container_memory_usage / limits` |

> **핵심:** Saturation이 유일한 차이. RED는 "서비스가 요청을 잘 처리하는가"에 집중, Golden Signals는 "리소스가 포화되고 있는가"까지 포함합니다.

<!-- notes: 메트릭 프레임워크 비교: RED Method(Tom Wilkie)는 마이크로서비스에 적합, 4 Golden Signals(Google SRE Book)는 인프라에 적합. 3개 메트릭이 겹치고 Saturation이 유일한 차이입니다. 대시보드 구성 시 이 메트릭들을 기준으로 패널을 배치하면 표준화된 모니터링이 가능합니다. -->

---

<!-- type: timeline -->

# 장애 분석 워크플로우

1. **Alert 수신** (AlertManager -> Slack)
   ```
   [FIRING] PaymentService High Error Rate
   - alertname: PaymentServiceErrors
   - severity: critical
   - service: payment-service
   - error_rate: 5.2%
   - threshold: 1%
   ```

2. **Dashboard 확인** (Grafana -> RED metrics)
   - Rate: 정상 (1,200 req/s)
   - Errors: **5.2% (급증)**
   - Duration: p99 2.5s (증가)

3. **Trace 분석** (Tempo -> 느린 span 식별)
   ```
   TraceQL: { resource.service.name = "payment-service" && status = error }
   -> DB Query span: 2.3s (timeout)
   ```

4. **Log 확인** (Loki -> 에러 메시지 확인)
   ```
   {namespace="payment"} |= "error"

   ERROR: Connection timeout to RDS after 2000ms
   ERROR: Max connection pool exhausted (100/100)
   ERROR: Unable to acquire connection within 5s
   ```

5. **근본 원인 파악 & 수정**
   - **Root Cause:** RDS 연결 풀 고갈로 인한 타임아웃
   - **해결책:**
     - Connection pool 크기 증가 (100 -> 200)
     - Connection timeout 설정 조정
     - RDS 인스턴스 스케일업 검토

<!-- notes: 실제 장애 분석 시 이 워크플로우를 따르면 체계적으로 근본 원인을 파악할 수 있습니다. -->

---

<!-- type: content -->

# OpenTelemetry Collector 파이프라인

**Receivers -> Processors -> Exporters**

## Receivers
텔레메트리 데이터 수신
- **OTLP (gRPC)**: 4317 포트
- **OTLP (HTTP)**: 4318 포트
- **Jaeger**: 14250/14268 포트
- **Zipkin**: 9411 포트

## Processors
데이터 변환 및 필터링
- **batch**: 배치 처리로 효율성 향상
- **tail_sampling**: 에러/느린 요청 우선 샘플링
- **spanmetrics**: span에서 메트릭 생성
- **attributes**: 속성 추가/수정/삭제

## Exporters
백엔드로 데이터 전송
- **otlp/tempo**: Tempo로 트레이스 전송
- **loki**: Loki로 로그 전송
- **prometheusremotewrite**: Prometheus로 메트릭 전송

```yaml
receivers:
  otlp:
    protocols:
      grpc: { endpoint: "0.0.0.0:4317" }
      http: { endpoint: "0.0.0.0:4318" }

processors:
  batch:
    timeout: 5s
    send_batch_size: 1000
  tail_sampling:
    policies:
      - name: errors
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: slow
        type: latency
        latency: { threshold_ms: 1000 }
      - name: default
        type: probabilistic
        probabilistic: { sampling_percentage: 10 }

exporters:
  otlp/tempo:
    endpoint: tempo-distributor:4317
  prometheusremotewrite:
    endpoint: http://prometheus:9090/api/v1/write

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch, tail_sampling]
      exporters: [otlp/tempo]
```

<!-- notes: OTel Collector는 텔레메트리 데이터의 수집, 처리, 전송을 담당합니다. tail_sampling이 비용 최적화의 핵심입니다. -->

---

<!-- type: content -->

# 비용 효율적 샘플링 전략

## 샘플링률 조절

| 일일 트레이스 | 월 저장 비용 | Error 캡처율 |
|--------------|-------------|-------------|
| 1M | $450 | 100% |

> **Tip:** Tail Sampling을 사용하면 샘플링률을 낮춰도 모든 에러를 캡처할 수 있습니다.

## 샘플링 전략 비교

| 전략 | 샘플링률 | 비용 절감 | Error 캡처 |
|------|---------|----------|-----------|
| Head Sampling | 10% | 90% | 10% |
| **Tail Sampling** | 10% + errors | 80-90% | **100%** |
| Adaptive | 동적 | 85-95% | 100% |
| No Sampling | 100% | 0% | 100% |

## Tail Sampling 권장 정책

- **errors:** 모든 에러 100% 수집
- **slow:** 1초 이상 요청 100% 수집
- **default:** 나머지 10% 랜덤 샘플링

<!-- notes: Tail Sampling은 비용과 가시성 사이의 최적 균형점을 찾는 방법입니다. 에러는 100% 수집하면서 비용을 80-90% 절감할 수 있습니다. -->

---

<!-- type: quiz -->

# Block 3 요약 & 퀴즈

## 핵심 개념 정리

- **Exemplars:** 메트릭 -> 트레이스 연결
- **Derived Fields:** 로그 -> 트레이스 연결
- **tracesToLogs:** 트레이스 -> 로그 연결
- **TraceQL:** 강력한 트레이스 쿼리 언어
- **Tail Sampling:** 비용 효율적 샘플링

## Quiz 1: 메트릭에서 트레이스로 연결하는 Grafana 기능은?

- [x] Exemplars
- [ ] Derived Fields
- [ ] tracesToLogs
- [ ] Annotations

## Quiz 2: Loki에서 TraceID를 추출하는 설정은?

- [ ] Exemplars
- [x] Derived Fields
- [ ] Labels
- [ ] Annotations

## Quiz 3: 비용 효율적이면서 모든 에러를 캡처하는 샘플링 전략은?

- [ ] Head Sampling
- [x] Tail Sampling
- [ ] Random Sampling
- [ ] No Sampling

<!-- notes: Block 3의 핵심은 3가지 시그널을 연결하는 것입니다. Exemplars, Derived Fields, tracesToLogs가 핵심 설정입니다. -->
