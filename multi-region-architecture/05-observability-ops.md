---
remarp: true
block: 05-observability-ops
---

---
<!-- Slide 1: Block 5 섹션 오프너 -->
@type: section

# Block 5: Observability & Operations

수집 → 샘플링 → 저장 → 리전 간 상관 → 비용 → 부하 테스트 → SLO → 출시 준비

:::notes
{timing: 0.5min}
[요약]
• 마지막 블록은 "두 리전을 어떻게 보고, 얼마에 운영하고, 언제 출시할 수 있는가"
• 관측 스택, tail sampling, trace backend, 리전 간 상관, CloudWatch 다계정, 비용, 성능, SLO, 출시 로드맵 순서
• 모든 가격과 설정 키는 2026-10-15 기준 AWS 문서, Pricing API, upstream README로 재확인

지금까지 Foundation, Data Sync, Traffic Routing, DR과 Failover를 봤습니다. 마지막 블록은 운영입니다. 두 리전에서 동시에 일어나는 일을 어떻게 한 화면에 모으고, 그 비용은 얼마이며, 출시 전에 무엇을 검증해야 하는지 30분 동안 정리하겠습니다.
{cue: pause}
시나리오는 그대로 이어갑니다. order, payment, catalog, cart 서비스가 us-east-1 primary, us-west-2 secondary에서 동작하는 e-commerce입니다.
{cue: transition}
먼저 관측 스택 전체 그림부터 보겠습니다.
:::

---
<!-- Slide 2: 관측 스택 전체 그림 (HTML architecture) -->
@type: content
@title: 텔레메트리는 리전 안에서 끝낸다

## 텔레메트리는 리전 안에서 끝낸다

:::html
<style>
.mr05-stack .flow-group-label { font-weight: var(--weight-bold); color: var(--on-surface); }
.mr05-stack .flow-box { word-break: keep-all; }
.mr05-sub { display: block; color: var(--text-secondary); font-size: var(--fs-caption); margin-top: var(--space-1); word-break: keep-all; }
.mr05-legend { margin-top: var(--space-4); }
.mr05-legend .callout { word-break: keep-all; }
.mr05-legend strong { color: var(--info); }
.mr05-legend .mr05-ok { color: var(--success); }
</style>
<div class="flow-h mr05-stack">
  <div class="flow-group bg-blue fragment fade-right" data-fragment-index="1">
    <div class="flow-group-label">사용자 경로</div>
    <div class="flow-box">CloudFront<span class="mr05-sub">유일한 public 진입점</span></div>
    <div class="flow-box">VPC origin → internal ALB<span class="mr05-sub">X-Amzn-Trace-Id 추가</span></div>
  </div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="2">→</div>
  <div class="flow-group bg-green fragment fade-right" data-fragment-index="2">
    <div class="flow-group-label">App Pod</div>
    <div class="flow-box">OTel SDK<span class="mr05-sub">W3C traceparent 전파</span></div>
    <div class="flow-box">order, payment<span class="mr05-sub">catalog, cart</span></div>
  </div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="3">→</div>
  <div class="flow-group bg-orange fragment fade-right" data-fragment-index="3">
    <div class="flow-group-label">Collector 2계층</div>
    <div class="flow-box">Agent (DaemonSet)<span class="mr05-sub">traceID로 분배</span></div>
    <div class="flow-box">Gateway (Deployment)<span class="mr05-sub">tail_sampling</span></div>
  </div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="4">→</div>
  <div class="flow-group bg-purple fragment fade-right" data-fragment-index="4">
    <div class="flow-group-label">리전 로컬 backend</div>
    <div class="flow-box">Amazon Managed Service for Prometheus</div>
    <div class="flow-box">Tempo on S3 또는 CloudWatch (X-Ray)</div>
  </div>
</div>
<div class="card-grid mr05-legend fragment" data-reveal="stagger" data-fragment-index="5">
  <div class="callout callout-info"><strong>같은 스택을 두 번</strong> us-east-1과 us-west-2에 동일하게 배포합니다. 한 리전 장애가 다른 리전의 관측을 끊지 않도록 합니다.</div>
  <div class="callout callout-success"><strong class="mr05-ok">조회만 전역으로</strong> Grafana가 두 리전 data source를 함께 조회합니다. 데이터 이동은 필요한 경우에만 합니다.</div>
</div>
:::

:::notes
{timing: 2min}
[요약]
• 사용자 트래픽은 CloudFront → VPC origin → internal ALB, 컴퓨트에 public IP 없음
• App Pod는 OTel SDK로 W3C traceparent를 전파
• Collector는 Agent(DaemonSet)와 Gateway 2계층, Gateway에서 tail sampling
• backend는 리전 로컬에 두고 조회만 전역으로 모음

왼쪽부터 보겠습니다. 사용자 요청은 CloudFront가 유일한 public 진입점이고, VPC origin을 통해 internal ALB로 들어옵니다. ALB는 요청에 X-Amzn-Trace-Id 헤더를 추가하므로 edge 다음 첫 hop부터 추적이 가능합니다.
App Pod에서는 OpenTelemetry SDK가 W3C traceparent 헤더로 trace context를 넘깁니다. 텔레메트리는 노드마다 있는 Agent Collector로 가고, Agent는 trace ID 기준으로 Gateway Collector에 분배합니다. tail sampling은 Gateway에서 합니다.
{cue: pause}
가장 중요한 원칙은 텔레메트리를 리전 안에서 끝낸다는 것입니다. us-east-1 장애 때 us-west-2의 관측까지 함께 끊기면 안 되기 때문입니다. 두 리전을 한 화면에 보는 것은 Grafana에서 두 data source를 조회하는 것으로 해결하고, 데이터 자체를 옮기는 것은 뒤에서 볼 비용 때문에 최소화합니다.
{cue: transition}
이 Collector 2계층을 실제 설정으로 보겠습니다.

[출처]
• ALB X-Amzn-Trace-Id: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-request-tracing.html
• CloudFront VPC origins: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-vpc-origins.html
:::

---
<!-- Slide 3: Collector 설정 (Tabs) -->
@type: tabs
@title: Collector는 2계층으로 나눈다

## Collector는 2계층으로 나눈다

### Agent (DaemonSet)
노드 로컬에서 받아 **trace ID 기준으로** Gateway에 분배합니다.

```yaml
receivers:
  otlp:
    protocols:
      grpc: { endpoint: "${env:MY_POD_IP}:4317" }
processors:
  memory_limiter: { check_interval: 1s, limit_percentage: 80, spike_limit_percentage: 25 }
exporters:
  loadbalancing:
    routing_key: traceID
    protocol:
      otlp: { timeout: 1s }
    resolver:
      k8s: { service: otel-gateway.observability, ports: [4317] }
```

### Gateway (tail sampling)
```yaml
processors:
  memory_limiter: { check_interval: 1s, limit_percentage: 80, spike_limit_percentage: 25 }
  batch: {}                     # 기본값 8192건, 200ms
  tail_sampling:
    decision_wait: 30s          # 기본값 30s
    num_traces: 50000           # 기본값 50000
    expected_new_traces_per_sec: 2000
    policies:
      - name: keep-errors
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: keep-slow
        type: latency
        latency: { threshold_ms: 500 }
      - name: baseline
        type: probabilistic
        probabilistic: { sampling_percentage: 10 }
```

### Export (X-Ray OTLP)
```yaml
extensions:
  sigv4auth/traces: { region: us-east-1, service: xray }
exporters:
  otlphttp/xray:
    compression: gzip
    traces_endpoint: https://xray.us-east-1.amazonaws.com/v1/traces
    auth: { authenticator: sigv4auth/traces }
service:
  extensions: [sigv4auth/traces]
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, tail_sampling, batch]
      exporters: [otlphttp/xray]
```

X-Ray OTLP endpoint는 **Transaction Search 활성화**가 전제입니다. us-west-2 Gateway는 region과 endpoint만 바꿉니다.

:::notes
{timing: 2.5min}
[요약]
• Agent는 loadbalancing exporter의 routing_key: traceID로 같은 trace를 같은 Gateway에 보냄
• Gateway의 tail_sampling: decision_wait 기본 30s, num_traces 기본 50000
• Gateway pipeline 순서: memory_limiter, tail_sampling, batch (batch는 기본값 8192건, 200ms)
• X-Ray는 이제 OTLP endpoint(xray.<region>.amazonaws.com/v1/traces)에 SigV4로 전송
• OTLP endpoint 사용 전 Transaction Search 활성화 필요

Agent 탭부터 보겠습니다. receiver는 Pod IP에만 바인딩했고, memory_limiter는 퍼센트 기반으로 걸었습니다. 핵심은 loadbalancing exporter입니다. routing_key를 traceID로 두면 같은 trace의 span이 항상 같은 Gateway 인스턴스로 갑니다. resolver는 k8s 타입으로 Gateway Service를 "이름.네임스페이스" 형식으로 지정합니다.
{cue: pause}
Gateway 탭은 tail_sampling입니다. decision_wait와 num_traces는 upstream 기본값을 그대로 적었습니다. 에러는 모두, 500ms 넘는 요청은 모두, 나머지는 10%만 남기는 세 정책입니다. Gateway에도 memory_limiter를 두고, batch는 기본값 그대로 정의합니다. pipeline 순서는 upstream 권장대로 memory_limiter가 맨 앞, sampling 다음, batch는 exporter 바로 앞입니다. 버려질 span까지 묶어 보내지 않으려는 것입니다.
Export 탭은 2026년 기준 권장 경로입니다. 예전처럼 X-Ray daemon이나 awsxray exporter를 쓰지 않고, 표준 otlphttp exporter에 sigv4auth extension으로 X-Ray OTLP endpoint에 직접 보냅니다. 이 endpoint는 계정에 Transaction Search가 켜져 있어야 동작합니다.
{cue: transition}
tail sampling에는 반드시 알아야 할 전제가 있습니다.

[출처]
• tail_sampling README (기본값, 정책 문법, stability beta): https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/tailsamplingprocessor (확인일 2026-10-15)
• batch processor README (send_batch_size 8192, timeout 200ms 기본값): https://github.com/open-telemetry/opentelemetry-collector/tree/main/processor/batchprocessor
• processor 권장 순서 (memory_limiter, sampling, batch): https://github.com/open-telemetry/opentelemetry-collector/blob/main/processor/README.md
• loadbalancing exporter README (routing_key, k8s resolver): https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/exporter/loadbalancingexporter
• OTLP endpoint와 sigv4auth 예시: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-OTLPSimplesetup.html
• Transaction Search 전제: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-OTLP-UsingADOT.html
:::

---
<!-- Slide 4: Tail sampling 전제와 효과 -->
@type: content
@title: tail sampling은 같은 인스턴스가 전제

## tail sampling은 같은 인스턴스가 전제

:::html
<style>
.mr05-ts .metric-card { text-align: left; }
.mr05-ts .metric-value { font-size: var(--fs-subtitle); }
.mr05-t-danger { color: var(--danger); font-weight: var(--weight-bold); }
.mr05-t-warning { color: var(--warning); font-weight: var(--weight-bold); }
.mr05-t-accent { color: var(--accent); font-weight: var(--weight-bold); }
.mr05-t-info { color: var(--info); font-weight: var(--weight-bold); }
.mr05-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.mr05-ts-row { margin-top: var(--space-4); }
</style>
<div class="card-grid mr05-ts" data-reveal="stagger">
  <div class="metric-card"><strong class="mr05-t-danger">에러 trace</strong><div class="metric-value">100%</div><div class="mr05-muted">status_code = ERROR</div></div>
  <div class="metric-card"><strong class="mr05-t-warning">느린 trace</strong><div class="metric-value">100%</div><div class="mr05-muted">latency ≥ 500ms</div></div>
  <div class="metric-card"><strong class="mr05-t-accent">나머지</strong><div class="metric-value">10%</div><div class="mr05-muted">probabilistic baseline</div></div>
  <div class="metric-card"><strong class="mr05-t-info">예시 보존량</strong><div class="metric-value">약 12.7%</div><div class="mr05-muted">에러 1%, 느림 2% 가정: 3% + 97% × 10%</div></div>
</div>
<div class="card-grid mr05-ts-row">
  <div class="callout callout-danger fragment fade-up" data-fragment-index="1"><strong class="mr05-t-danger">같은 trace, 같은 인스턴스</strong><div class="mr05-muted">trace의 모든 span이 한 Collector에 모여야 판단할 수 있습니다. Gateway를 늘리면 앞단에 traceID 라우팅이 필수입니다.</div></div>
  <div class="callout callout-warning fragment fade-up" data-fragment-index="2"><strong class="mr05-t-warning">메모리 = 유입률 × 대기</strong><div class="mr05-muted">2,000 trace/s × 30s = 60,000개가 메모리에 머뭅니다. num_traces 50000보다 크면 판단 전에 밀려납니다.</div></div>
  <div class="callout callout-info fragment fade-up" data-fragment-index="3"><strong class="mr05-t-info">늦게 오는 span</strong><div class="mr05-muted">decision_wait 뒤에 도착한 span은 이미 내려진 결정을 따릅니다. 비동기 consumer가 긴 trace는 대기 시간을 따로 봅니다.</div></div>
</div>
:::

:::notes
{timing: 2min}
[요약]
• 정책 예시: 에러 100%, 500ms 이상 100%, 나머지 10%
• 에러 1%, 느림 2% 가정이면 보존량 약 12.7%, 즉 저장량 약 87% 감소 (시나리오 계산)
• tail sampling은 trace 전체가 한 인스턴스에 모여야 동작
• 필요 메모리는 trace 유입률 × decision_wait로 계산, num_traces와 비교

위 카드는 정책별 보존 비율입니다. 시나리오에서 에러가 1%, 느린 요청이 2%라고 가정하면 3%는 전부 남고 나머지 97%의 10%가 남아 약 12.7%가 저장됩니다. 예전 자료의 "90% 절감"은 이렇게 가정에 따라 달라지는 숫자라 계산식으로 바꿨습니다.
{cue: pause}
아래 세 가지가 운영 함정입니다. 첫째, README가 명시하듯 trace의 모든 span이 같은 Collector 인스턴스에 도착해야 합니다. 그래서 앞 슬라이드의 Agent 계층이 필요합니다.
둘째, 메모리입니다. 초당 2,000 trace에 30초를 기다리면 60,000개를 들고 있어야 하는데 num_traces 기본값은 50,000입니다. 이 값을 넘으면 판단 전에 오래된 trace가 밀려납니다.
셋째, decision_wait 이후에 도착한 span은 이미 내려진 결정을 따릅니다. MSK consumer처럼 비동기로 길게 이어지는 trace는 따로 확인하세요. 이 processor의 traces stability는 아직 beta입니다.
{cue: transition}
이렇게 남긴 trace를 어디에 저장할지 보겠습니다.

[출처]
• tail_sampling README: "All spans for a given trace MUST be received by the same collector instance", num_traces 기본 50000, decision_wait 기본 30s (확인일 2026-10-15)
:::

---
<!-- Slide 5: Trace backend 선택 (Tabs) -->
@type: tabs
@title: 백엔드는 Tempo와 X-Ray 중 고른다

## 백엔드는 Tempo와 X-Ray 중 고른다

### X-Ray + Transaction Search
| 항목 | 2026-10-15 기준 |
|---|---|
| 수집 경로 | OTLP endpoint, SigV4 (`service: xray`) |
| 저장 위치 | CloudWatch Logs `aws/spans` log group |
| 검색 | 모든 span을 attribute로 검색, trace 최대 10,000 span |
| 인덱싱 | 수집 span의 1%는 trace summary로 무료 인덱싱 |
| 수집 요금 | $0.35/GB (첫 10 TB, us-east-1 list price) |

### Tempo 3.x (self-managed)
| 항목 | 내용 |
|---|---|
| 저장 | S3에 Parquet 블록 (`storage.trace.backend: s3`) |
| 쓰기 경로 | 3.0에서 ingester 제거, block-builder와 live-store |
| 배포 모드 | monolithic은 Kafka 불필요, microservices는 Kafka 호환 큐 |
| 질의 | TraceQL, 구조 연산자 `>>`, `>`, `~` |
| service graph | metrics-generator `service_graphs`, 기본 비활성 |

### 선택 기준
| 질문 | Transaction Search | Tempo |
|---|---|---|
| 운영 부담 | 관리형 | 클러스터 직접 운영 |
| 샘플링 | 100% 수집 후 일부 인덱싱 | tail sampling 결과만 저장 |
| AWS 연계 | Application Signals, SLO | Grafana 생태계 |
| 비용 성격 | GB당 수집 요금 | S3 + 컴퓨트 |

### X-Ray SDK 상태
X-Ray SDK와 daemon은 **2026-02-25부터 maintenance mode**입니다. 보안 수정만 릴리스되며 X-Ray 서비스 자체는 계속 지원됩니다. 신규 계측은 OpenTelemetry(ADOT SDK 또는 upstream SDK)로 시작합니다.

:::notes
{timing: 2min}
[요약]
• Transaction Search: span을 aws/spans에 100% 저장, 1%는 무료 인덱싱, $0.35/GB(첫 10TB)
• Tempo 3.x: ingester 제거, block-builder와 live-store, S3 Parquet, TraceQL
• Transaction Search는 "모두 수집", Tempo는 "tail sampling 결과만 저장"이 기본 성격
• X-Ray SDK, daemon은 2026-02-25부터 maintenance mode

첫 탭은 AWS 관리형 경로입니다. Transaction Search를 켜면 X-Ray로 들어오는 span이 CloudWatch Logs의 aws/spans log group에 저장되고, 1%는 trace summary로 무료 인덱싱됩니다. 수집 요금은 us-east-1 기준 첫 10TB가 GB당 0.35달러입니다.
두 번째 탭은 Tempo입니다. 예전 자료는 Tempo 2.x 구조로 설명했는데, Tempo 3.0에서 ingester 기반 쓰기 경로가 제거됐습니다. microservices 모드는 distributor 뒤에 Kafka 호환 큐를 두고 block-builder와 live-store가 소비합니다. monolithic 모드는 Kafka 없이 동작합니다.
{cue: pause}
선택 기준 탭에서 중요한 차이는 샘플링 철학입니다. Transaction Search는 span을 전부 받아 저장하는 것을 전제로 하므로, 그 앞에서 tail sampling을 세게 걸면 Application Signals 지표가 왜곡될 수 있습니다. Tempo는 tail sampling 결과만 저장하는 구성이 자연스럽습니다.
{cue: question}
여러분 팀은 관측 플랫폼을 직접 운영할 인력이 있나요? 이 질문이 선택을 거의 결정합니다.
{cue: transition}
다음은 trace가 리전을 넘어갈 때입니다.

[출처]
• Transaction Search: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Transaction-Search.html
• 1% 무료 인덱싱: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Enable-TransactionSearch.html
• span 요금 $0.35/0.20/0.15 per GB: AWS Pricing API, AmazonCloudWatch USE1-Application-Signals-Bytes (publication 2026-10-07), https://aws.amazon.com/cloudwatch/pricing/
• Tempo 3.0 변경: https://github.com/grafana/tempo/releases (v3.1.0 최신, 확인일 2026-10-15), https://grafana.com/docs/tempo/latest/configuration/
• X-Ray SDK maintenance: https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-migration.html
:::

---
<!-- Slide 6: 리전 간 trace 상관 -->
@type: content
@title: trace ID는 리전을 넘어 이어진다

## trace ID는 리전을 넘어 이어진다

:::html
<style>
.mr05-xr .flow-box { word-break: keep-all; }
.mr05-xr .flow-group-label { font-weight: var(--weight-bold); color: var(--on-surface); }
.mr05-xr-sub { display: block; color: var(--text-secondary); font-size: var(--fs-caption); margin-top: var(--space-1); }
.mr05-xr-opts { margin-top: var(--space-4); }
.mr05-xr-opts strong { color: var(--accent); }
.mr05-xr-opts .mr05-rec { color: var(--success); }
.mr05-xr-code { margin-top: var(--space-3); }
</style>
<div class="flow-h mr05-xr">
  <div class="flow-group bg-blue" data-fragment-index="1">
    <div class="flow-group-label">us-west-2</div>
    <div class="flow-box">cart-service<span class="mr05-xr-sub">trace 시작, cloud.region = us-west-2</span></div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-group bg-orange">
    <div class="flow-group-label">traceparent 헤더</div>
    <div class="flow-box">같은 trace ID<span class="mr05-xr-sub">TGW peering 경유 사설 호출</span></div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-group bg-purple">
    <div class="flow-group-label">us-east-1 (write primary)</div>
    <div class="flow-box">order → payment<span class="mr05-xr-sub">span은 us-east-1 backend에 저장</span></div>
  </div>
</div>
<div class="card-grid mr05-xr-opts fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="callout callout-success"><strong class="mr05-rec">A. 리전별 저장 (기본)</strong> 각 리전 backend에 그대로 두고 trace ID로 양쪽을 조회합니다. 장애 격리가 우선입니다.</div>
  <div class="callout callout-info"><strong>B. sampled 사본만 이동</strong> Gateway에 원격 exporter를 하나 더 둡니다. tail sampling 뒤라 바이트가 작지만 리전 간 전송 요금이 붙습니다.</div>
</div>
<div class="code-block mr05-xr-code fragment fade-up" data-fragment-index="2"><span class="comment"># B 구성에서 한 Tempo에 두 리전 span이 있을 때</span>
<span class="key">{</span> resource.cloud.region = <span class="string">"us-west-2"</span> <span class="key">}</span> &gt;&gt; <span class="key">{</span> resource.cloud.region = <span class="string">"us-east-1"</span> &amp;&amp; status = <span class="value">error</span> <span class="key">}</span></div>
:::

:::notes
{timing: 2.5min}
[요약]
• W3C traceparent가 전파되면 리전이 달라도 trace ID는 하나
• span은 실행된 리전의 backend에 저장되므로 전체 trace는 자동으로 한 곳에 모이지 않음
• 기본은 리전별 저장 + trace ID 양쪽 조회, 필요 시 sampled span만 원격 복사
• cloud.region resource attribute는 resourcedetection processor로 부여

시나리오 흐름입니다. 서부 사용자의 cart 요청이 us-west-2에서 시작하고, 주문 쓰기는 write primary인 us-east-1의 order와 payment로 넘어갑니다. traceparent 헤더가 전파되면 두 리전의 span은 같은 trace ID를 가집니다.
{cue: pause}
여기서 오해하기 쉬운 점이 있습니다. trace ID가 같다고 해서 span이 한 곳에 모이지는 않습니다. 각 span은 실행된 리전의 Collector와 backend로 갑니다. 그래서 선택지가 두 가지입니다.
A는 리전별로 저장하고 trace ID로 양쪽 backend를 조회하는 방식입니다. 리전 장애 시에도 반대편 관측이 살아 있으므로 기본값으로 권장합니다.
B는 Gateway에 원격 리전 exporter를 하나 더 붙여 sampled span 사본을 보내는 방식입니다. tail sampling 뒤라 양은 작지만 GB당 리전 간 전송 요금이 붙습니다.
아래 TraceQL은 B처럼 한 Tempo에 두 리전 span이 있을 때 쓸 수 있는 구조 쿼리로, us-west-2 span의 하위에서 에러 난 us-east-1 span을 찾습니다. 구조 연산자는 항상 오른쪽 조건의 span을 반환합니다.
{cue: transition}
CloudWatch 쪽은 계정과 리전을 어떻게 묶는지 보겠습니다.

[약어]
• TGW: Transit Gateway

[출처]
• TraceQL 구조 연산자: https://grafana.com/docs/tempo/latest/traceql/construct-traceql-queries/ (확인일 2026-10-15)
• OTel propagators (tracecontext, baggage, xray): https://opentelemetry.io/docs/languages/sdk-configuration/general/
:::

---
<!-- Slide 7: CloudWatch 다계정, 다리전 -->
@type: content
@title: OAM은 리전을 넘지 않는다

## OAM은 리전을 넘지 않는다

:::html
<style>
.mr05-cw .metric-card { text-align: left; }
.mr05-cw-a { color: var(--accent); font-weight: var(--weight-bold); }
.mr05-cw-i { color: var(--info); font-weight: var(--weight-bold); }
.mr05-cw-w { color: var(--warning); font-weight: var(--weight-bold); }
.mr05-cw-s { color: var(--success); font-weight: var(--weight-bold); }
.mr05-cw ul { margin: var(--space-2) 0 0; padding-left: var(--space-4); color: var(--text-secondary); font-size: var(--fs-card); word-break: keep-all; }
.mr05-cw li { margin-bottom: var(--space-1); }
.mr05-cw-rec { margin-top: var(--space-4); word-break: keep-all; }
</style>
<div class="card-grid mr05-cw">
  <div class="metric-card fragment fade-up" data-fragment-index="1"><strong class="mr05-cw-a">Cross-account observability (OAM)</strong>
    <ul><li>sink와 link는 같은 Region에서만 연결</li><li>계정당 Region별 sink 1개</li><li>monitoring 계정당 source 최대 100,000</li><li>metrics, logs, traces를 복제 없이 조회</li></ul></div>
  <div class="metric-card fragment fade-up" data-fragment-index="2"><strong class="mr05-cw-i">Centralization rules</strong>
    <ul><li>Organizations 기반, source Region 여러 개 선택</li><li>destination Region + backup Region</li><li>@aws.account, @aws.region 필드 보존</li><li>첫 사본 무료, 추가 사본 $0.05/GB</li></ul></div>
  <div class="metric-card fragment fade-up" data-fragment-index="3"><strong class="mr05-cw-w">Cross-account cross-Region 대시보드</strong>
    <ul><li>metrics와 alarm 위젯용</li><li>logs와 traces는 지원하지 않음</li><li>alarm은 telemetry가 있는 Region에 생성</li></ul></div>
</div>
<div class="callout callout-success mr05-cw-rec fragment zoom-in" data-fragment-index="4"><strong class="mr05-cw-s">시나리오 적용</strong> monitoring 계정에 us-east-1, us-west-2 sink를 각각 만들고, 로그는 Centralization rule로 us-east-1에 모으며 backup Region을 us-west-2로 둡니다.</div>
:::

:::notes
{timing: 2min}
[요약]
• OAM(cross-account observability)은 sink와 link가 같은 Region, 리전마다 sink 필요
• 리전을 넘는 집계는 CloudWatch Centralization rule, backup Region 지정 가능
• Centralization 첫 사본 무료, 추가 사본 GB당 $0.05, 리전 간 전송 요금은 별도일 수 있음
• cross-Region 대시보드는 metrics와 alarm만, logs와 traces 미지원

CloudWatch에서 "여러 계정, 여러 리전을 한 곳에서"라는 요구는 세 가지 기능으로 나뉩니다. 첫째 OAM, 즉 cross-account observability는 이름과 달리 리전을 넘지 않습니다. sink와 link가 같은 Region에 있어야 하고, 계정당 Region별 sink는 하나입니다. 그래서 우리 시나리오는 monitoring 계정에 us-east-1과 us-west-2 sink를 따로 만듭니다.
{cue: pause}
둘째, 리전을 넘는 집계는 Centralization rule입니다. Organizations에서 source 계정과 source Region을 고르고, destination Region과 backup Region을 지정합니다. 복사된 로그에는 원래 계정과 리전 필드가 붙습니다. 첫 사본은 무료이고 추가 사본은 GB당 0.05달러이며, 리전 간 전송 요금이 별도로 생길 수 있다고 가격표에 명시돼 있습니다.
셋째, cross-account cross-Region 대시보드는 metrics와 alarm용이고 logs와 traces는 지원하지 않습니다.
{cue: transition}
이제 비용을 숫자로 보겠습니다.

[출처]
• CreateSink "one sink per Region", CreateLink "100,000 source accounts, five monitoring accounts": https://docs.aws.amazon.com/OAM/latest/APIReference/API_CreateSink.html
• same-Region 제약, cross-Region 대시보드 범위: https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/centralize-monitoring-by-using-amazon-cloudwatch-observability-access-manager.html
• Centralization: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CloudWatchLogs_Centralization.html
• 추가 사본 $0.05/GB, 전송 요금 별도: https://aws.amazon.com/cloudwatch/omni/pricing/ (확인일 2026-10-15)
:::

---
<!-- Slide 8: 비용 계산기 (interactive) -->
@type: content
@title: 변동비는 바이트 수가 정한다
@fit: shrink

## 변동비는 바이트 수가 정한다

:::html
<style>
.mr05-calc { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); align-items: start; }
.mr05-ctrl { display: flex; flex-direction: column; gap: var(--space-2); }
.mr05-row { display: grid; grid-template-columns: 11rem 1fr; align-items: center; gap: var(--space-3); }
.mr05-row label { color: var(--text-secondary); font-size: var(--fs-card); word-break: keep-all; }
.mr05-calc .slider-value { min-width: 6.5rem; }
.mr05-opt { display: flex; gap: var(--space-3); align-items: center; color: var(--text-secondary); font-size: var(--fs-card); }
.mr05-opt input { accent-color: var(--accent); }
.mr05-out { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-2); }
.mr05-out .metric-value { font-size: var(--fs-subtitle); white-space: nowrap; }
.mr05-out .mr05-total { grid-column: span 2; }
.mr05-out .mr05-total .metric-value { color: var(--accent); }
.mr05-note { color: var(--text-secondary); font-size: var(--fs-caption); margin-top: var(--space-2); word-break: keep-all; }
</style>
<div class="mr05-calc" data-reveal="static">
  <div class="mr05-ctrl">
    <div class="mr05-row"><label for="mr05-xr">리전 간 복제 GB/일</label><div class="slider-container"><input type="range" id="mr05-xr" min="0" max="2000" step="10" value="300"><span class="slider-value" id="mr05-xr-v">300</span></div></div>
    <div class="mr05-row"><label for="mr05-nat">NAT 처리 GB/일</label><div class="slider-container"><input type="range" id="mr05-nat" min="0" max="1000" step="10" value="100"><span class="slider-value" id="mr05-nat-v">100</span></div></div>
    <div class="mr05-row"><label for="mr05-log">로그 수집 GB/일</label><div class="slider-container"><input type="range" id="mr05-log" min="0" max="500" step="5" value="50"><span class="slider-value" id="mr05-log-v">50</span></div></div>
    <div class="mr05-row"><label for="mr05-span">span 생성 GB/일</label><div class="slider-container"><input type="range" id="mr05-span" min="0" max="200" step="1" value="20"><span class="slider-value" id="mr05-span-v">20</span></div></div>
    <div class="mr05-row"><label for="mr05-keep">tail sampling 보존율</label><div class="slider-container"><input type="range" id="mr05-keep" min="5" max="100" step="1" value="13"><span class="slider-value" id="mr05-keep-v">13%</span></div></div>
    <div class="mr05-opt"><label><input type="checkbox" id="mr05-ia"> 로그를 Infrequent Access class로</label></div>
    <div class="mr05-note">us-east-1 list price, 2026-10-15 Pricing API 기준, 30일/월, 730시간/월. 리전 간 $0.02/GB, NAT $0.045/GB와 $0.045/시간, Logs $0.50 또는 $0.25/GB, span $0.35/GB, EKS $0.10/시간.</div>
  </div>
  <div class="mr05-out">
    <div class="metric-card"><div class="metric-value" id="mr05-o-xr">-</div><div class="metric-label">리전 간 전송</div></div>
    <div class="metric-card"><div class="metric-value" id="mr05-o-nat">-</div><div class="metric-label">NAT 데이터 처리</div></div>
    <div class="metric-card"><div class="metric-value" id="mr05-o-log">-</div><div class="metric-label">로그 수집</div></div>
    <div class="metric-card"><div class="metric-value" id="mr05-o-span">-</div><div class="metric-label">span 수집</div></div>
    <div class="metric-card"><div class="metric-value" id="mr05-o-fix">-</div><div class="metric-label">고정: EKS 2개 + NAT GW 6개</div></div>
    <div class="metric-card"><div class="metric-value" id="mr05-o-share">-</div><div class="metric-label">변동비 중 리전 간 비중</div></div>
    <div class="metric-card mr05-total"><div class="metric-value" id="mr05-o-tot">-</div><div class="metric-label">월 합계 (컴퓨트, DB, 스토리지 제외)</div></div>
  </div>
</div>
:::

:::script
var MR05 = { XR: 0.02, NATGB: 0.045, NATH: 0.045, LOG: 0.50, LOGIA: 0.25, SPAN: 0.35, EKSH: 0.10, H: 730, D: 30 };
function mr05usd(n) { return '$' + n.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 }); }
function mr05v(id) { return parseFloat(document.getElementById(id).value); }
function mr05update() {
  var xr = mr05v('mr05-xr'), nat = mr05v('mr05-nat'), log = mr05v('mr05-log'), span = mr05v('mr05-span'), keep = mr05v('mr05-keep');
  var ia = document.getElementById('mr05-ia').checked;
  document.getElementById('mr05-xr-v').textContent = xr;
  document.getElementById('mr05-nat-v').textContent = nat;
  document.getElementById('mr05-log-v').textContent = log;
  document.getElementById('mr05-span-v').textContent = span;
  document.getElementById('mr05-keep-v').textContent = keep + '%';
  var cXr = xr * MR05.D * MR05.XR;
  var cNat = nat * MR05.D * MR05.NATGB;
  var cLog = log * MR05.D * (ia ? MR05.LOGIA : MR05.LOG);
  var cSpan = span * (keep / 100) * MR05.D * MR05.SPAN;
  var cFix = 2 * MR05.EKSH * MR05.H + 6 * MR05.NATH * MR05.H;
  var variable = cXr + cNat + cLog + cSpan;
  document.getElementById('mr05-o-xr').textContent = mr05usd(cXr);
  document.getElementById('mr05-o-nat').textContent = mr05usd(cNat);
  document.getElementById('mr05-o-log').textContent = mr05usd(cLog);
  document.getElementById('mr05-o-span').textContent = mr05usd(cSpan);
  document.getElementById('mr05-o-fix').textContent = mr05usd(cFix);
  document.getElementById('mr05-o-share').textContent = variable > 0 ? Math.round(cXr / variable * 100) + '%' : '0%';
  document.getElementById('mr05-o-tot').textContent = mr05usd(variable + cFix);
}
['mr05-xr', 'mr05-nat', 'mr05-log', 'mr05-span', 'mr05-keep'].forEach(function (id) { document.getElementById(id).addEventListener('input', mr05update); });
document.getElementById('mr05-ia').addEventListener('change', mr05update);
mr05update();
:::

:::notes
{timing: 2.5min}
[요약]
• 단가는 Pricing API로 확인한 us-east-1 list price (2026-10-15)
• 리전 간 전송 us-east-1 → us-west-2 $0.02/GB, NAT 처리 $0.045/GB, NAT 시간 $0.045
• CloudWatch Logs Standard $0.50/GB, IA $0.25/GB, span $0.35/GB(첫 10TB), EKS 클러스터 $0.10/시간
• 기본값(300/100/50/20GB, 13%)이면 월 합계 약 $1,435, 컴퓨트와 DB 인스턴스는 제외
• NAT Gateway는 리전당 3 AZ, AZ마다 1개로 두 리전 6개 (Block 1 설계)

예전 자료는 인스턴스 타입별로 월 9,600에서 12,400달러를 제시했지만, 인스턴스 세대와 가격이 바뀌어 그대로 쓸 수 없습니다. 대신 리전 운영에 고유한 비용, 즉 바이트에 비례하는 항목을 직접 계산해 보겠습니다.
{cue: demo}
기본값에서 리전 간 복제 300GB/일은 월 180달러, NAT 100GB/일은 135달러, 로그 50GB/일은 750달러, span 20GB/일에 13% 보존이면 약 27달러입니다. 고정비는 EKS 클러스터 2개 146달러와 NAT Gateway 6개 197달러입니다. Block 1에서 리전마다 3개 AZ에 NAT Gateway를 하나씩 뒀으니 두 리전이면 6개입니다. 합계는 약 1,435달러입니다.
복제 슬라이더를 2,000GB까지 올려보세요. 리전 간 전송이 월 1,200달러가 되며 변동비의 가장 큰 항목이 됩니다. 로그 IA 체크박스를 켜면 로그 비용이 절반이 됩니다.
{cue: pause}
주의할 점은 이 단가가 목록 가격이라는 것입니다. 할인 계약, Free Tier, 다른 방향 전송, DB 서비스별 복제 요금(예: Aurora Global Database의 복제 I/O, MSK Replicator 처리량)은 포함하지 않았습니다. Cost Explorer에서 usage type USE1-USW2-AWS-Out-Bytes로 실제 값을 확인하세요.
{cue: transition}
그럼 어디서 줄일 수 있는지 보겠습니다.

[출처]
• AWS Pricing API (확인일 2026-10-15): AWSDataTransfer USE1-USW2-AWS-Out-Bytes $0.02/GB (publication 2026-09-16); AmazonEC2 NatGateway-Hours $0.045, NatGateway-Bytes $0.045/GB (2026-10-15); AmazonCloudWatch USE1-DataProcessing-Bytes $0.50/GB, USE1-DataProcessingIA-Bytes $0.25/GB, USE1-Application-Signals-Bytes $0.35/GB 첫 10TB (2026-10-07); AmazonEKS USE1-AmazonEKS-Hours:perCluster $0.10 (2026-09-28)
• 기본값 재계산: 300×30×0.02=180, 100×30×0.045=135, 50×30×0.5=750, 20×0.13×30×0.35=27.3, 변동 1,092.3, 고정 146+197.1=343.1 (NAT 6×0.045×730=197.1), 합계 1,435.4
:::

---
<!-- Slide 9: 비용 최적화 -->
@type: content
@title: 최적화는 바이트를 줄이는 일

## 최적화는 바이트를 줄이는 일

:::html
<style>
.mr05-opt-grid .metric-card { text-align: left; }
.mr05-o-a { color: var(--accent); font-weight: var(--weight-bold); }
.mr05-o-s { color: var(--success); font-weight: var(--weight-bold); }
.mr05-o-i { color: var(--info); font-weight: var(--weight-bold); }
.mr05-o-w { color: var(--warning); font-weight: var(--weight-bold); }
.mr05-o-d { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.mr05-o-tag { display: inline-block; margin-left: var(--space-2); }
</style>
<div class="card-grid mr05-opt-grid fragment" data-reveal="stagger" data-reveal-anim="right" data-fragment-index="1">
  <div class="metric-card"><strong class="mr05-o-s">S3 gateway endpoint</strong><span class="badge badge-green mr05-o-tag">즉시</span><div class="mr05-o-d">S3 트래픽을 NAT에서 빼면 GB당 $0.045 처리 요금이 사라집니다. gateway endpoint는 추가 요금이 없습니다.</div></div>
  <div class="metric-card"><strong class="mr05-o-s">sampled span만 이동</strong><span class="badge badge-green mr05-o-tag">즉시</span><div class="mr05-o-d">원격 리전 exporter는 tail sampling 뒤에 둡니다. 원본 span을 리전 간으로 보내지 않습니다.</div></div>
  <div class="metric-card"><strong class="mr05-o-i">복제 범위 축소</strong><span class="badge badge-blue mr05-o-tag">설계</span><div class="mr05-o-d">MSK Replicator topic 필터, 리전 로컬로 재생성 가능한 cache와 search index는 복제 대신 재구축을 검토합니다.</div></div>
  <div class="metric-card"><strong class="mr05-o-i">로그 class 분리</strong><span class="badge badge-blue mr05-o-tag">설계</span><div class="mr05-o-d">감사, 디버그 로그는 IA class($0.25/GB)로 보냅니다. IA에서 쓸 수 없는 기능은 사전에 확인합니다.</div></div>
  <div class="metric-card"><strong class="mr05-o-w">컴퓨트 통합</strong><span class="badge badge-yellow mr05-o-tag">튜닝</span><div class="mr05-o-d">stateless tier NodePool은 Spot과 Graviton을 허용하고 Karpenter consolidation을 켭니다. 할인 폭은 시점마다 다릅니다.</div></div>
  <div class="metric-card"><strong class="mr05-o-a">측정이 먼저</strong><span class="badge badge-yellow mr05-o-tag">상시</span><div class="mr05-o-d">Cost Explorer를 usage type으로 묶어 USE1-USW2 전송, NAT, DataProcessing을 주 단위로 봅니다.</div></div>
</div>
:::

:::notes
{timing: 2min}
[요약]
• S3 gateway endpoint는 무료, NAT 처리 요금($0.045/GB)을 바로 제거
• 리전 간으로는 sampled span만, 원본은 보내지 않음
• 재생성 가능한 데이터(cache, search index)는 복제 대신 재구축 검토
• 로그 IA class, Spot과 Graviton, consolidation은 기능 제약과 시점별 가격을 확인

카드는 효과가 빨리 나는 순서로 배치했습니다. 가장 쉬운 것은 S3 gateway endpoint입니다. ECR 이미지 레이어나 Tempo 블록처럼 S3로 가는 트래픽이 NAT를 지나면 GB당 0.045달러가 붙는데, gateway endpoint는 추가 요금이 없습니다.
두 번째는 trace 사본을 리전 간으로 보낼 때 sampled 결과만 보내는 것입니다.
{cue: pause}
세 번째는 설계 판단입니다. 모든 데이터를 복제할 필요는 없습니다. 원본 DB에서 다시 만들 수 있는 cache나 search index는 장애 시 재구축하는 편이 싸고 단순할 수 있습니다. 다만 RTO와 맞는지는 Block 4의 기준으로 판단합니다.
로그 IA class는 GB당 0.25달러로 절반이지만 Standard와 기능 차이가 있으니 쓰는 기능을 먼저 확인하세요. 예전 자료에 있던 "Spot 30에서 40% 절감", "MSK Serverless 50에서 70%" 같은 수치는 검증할 수 없어 뺐습니다.
{cue: transition}
비용 다음은 성능입니다.

[출처]
• S3 gateway endpoint 무료: https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html
• NAT 처리 $0.045/GB, Logs IA $0.25/GB: AWS Pricing API (확인일 2026-10-15)
• Log classes: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CloudWatch_Logs_Log_Classes.html
:::

---
<!-- Slide 10: 성능 병목 -->
@type: content
@title: 병목은 클라이언트 기본값에 숨는다

## 병목은 클라이언트 기본값에 숨는다

:::html
<style>
.mr05-perf .metric-card { text-align: left; }
.mr05-p-d { color: var(--danger); font-weight: var(--weight-bold); }
.mr05-p-w { color: var(--warning); font-weight: var(--weight-bold); }
.mr05-p-s { color: var(--success); font-weight: var(--weight-bold); }
.mr05-p-t { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.mr05-p-t code { font-size: var(--fs-caption); }
.mr05-perf-qw { margin-top: var(--space-4); word-break: keep-all; }
.mr05-perf .card-grid, .mr05-perf.card-grid { grid-template-columns: 1fr 1fr; }
.mr05-p-fix { color: var(--on-surface); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; }
.mr05-p-fix b { color: var(--success); }
</style>
<div class="card-grid mr05-perf">
  <div class="metric-card fragment fade-up" data-fragment-index="1"><strong class="mr05-p-d">Valkey cluster mode</strong><div class="mr05-p-t">cluster-aware client가 아니면 다른 shard 키에서 MOVED 응답을 처리하지 못합니다. </div><div class="mr05-p-fix"><b>조치</b> Python은 <code>RedisCluster</code> 계열 client로 교체</div></div>
  <div class="metric-card fragment fade-up" data-fragment-index="2"><strong class="mr05-p-d">Go pgxpool</strong><div class="mr05-p-t"><code>MaxConns</code> 기본값은 max(4, NumCPU)입니다. 작은 Pod에서는 4개라 고부하에서 대기열이 생깁니다.</div><div class="mr05-p-fix"><b>조치</b> <code>pool_max_conns</code>를 부하 테스트로 정하고 명시</div></div>
  <div class="metric-card fragment fade-up" data-fragment-index="3"><strong class="mr05-p-w">PyMongo / Motor</strong><div class="mr05-p-t"><code>maxPoolSize</code> 기본 100입니다. Pod 수 × 100이 DocumentDB 연결 한도를 넘지 않는지 계산합니다.</div><div class="mr05-p-fix"><b>조치</b> HPA 최대 Pod 수 기준으로 pool 크기 역산</div></div>
  <div class="metric-card fragment fade-up" data-fragment-index="4"><strong class="mr05-p-w">Go http.Transport</strong><div class="mr05-p-t"><code>DefaultMaxIdleConnsPerHost</code>는 2입니다. 내부 API 호출이 많으면 연결을 계속 새로 맺습니다.</div><div class="mr05-p-fix"><b>조치</b> 공유 Transport에 <code>MaxIdleConnsPerHost</code> 상향</div></div>
</div>
<div class="callout callout-success mr05-perf-qw fragment zoom-in" data-fragment-index="5"><strong class="mr05-p-s">Quick win</strong> catalog의 GET 응답에 짧은 TTL cache를 두고, CloudFront cache behavior로 상품 조회 경로를 캐싱해 origin 요청을 줄입니다.</div>
:::

:::notes
{timing: 2min}
[요약]
• 시나리오 코드 리뷰에서 나온 병목 4개, 모두 라이브러리 기본값 문제
• Valkey cluster mode는 cluster-aware client 필요(MOVED 처리)
• pgxpool MaxConns 기본 max(4, NumCPU), Motor maxPoolSize 기본 100, Go MaxIdleConnsPerHost 기본 2
• quick win은 catalog cache와 CloudFront 캐싱

이 시나리오 서비스들의 코드 리뷰에서 나온 병목입니다. 공통점은 모두 라이브러리 기본값이라는 것입니다.
첫째, ElastiCache for Valkey를 cluster mode로 쓰면서 단일 노드용 client를 쓰면 다른 shard의 키에 대해 MOVED 응답을 받습니다. cluster-aware client로 바꿔야 합니다.
둘째, Go의 pgxpool은 MaxConns 기본값이 4와 CPU 수 중 큰 값입니다. 예전 자료에 "database/sql 기본 CPU당 4개"라고 적혀 있었는데 정확히는 pgxpool의 기본값입니다.
{cue: pause}
셋째, PyMongo와 Motor의 maxPoolSize 기본값은 100입니다. Pod가 20개로 늘면 이론상 2,000개 연결이 열릴 수 있으니 인스턴스 연결 한도와 비교해야 합니다.
넷째, Go 표준 http.Transport는 호스트당 유휴 연결을 2개만 유지합니다. 서비스 간 호출이 많은 gateway에서는 값을 올립니다.
이 수치들은 다음 슬라이드의 부하 테스트로 검증합니다.
{cue: transition}

[출처]
• pgxpool MaxConns 기본값: https://pkg.go.dev/github.com/jackc/pgx/v5/pgxpool (확인일 2026-10-15)
• Go DefaultMaxIdleConnsPerHost = 2: https://pkg.go.dev/net/http#DefaultMaxIdleConnsPerHost
• PyMongo maxPoolSize 기본 100: https://pymongo.readthedocs.io/en/stable/api/pymongo/mongo_client.html
• ElastiCache cluster mode client: https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Replication.Redis-RedisCluster.html
:::

---
<!-- Slide 11: k6 부하 테스트 (Tabs) -->
@type: tabs
@title: 부하 테스트는 네 가지 모양으로

## 부하 테스트는 네 가지 모양으로

### Baseline
```javascript
export const options = {
  vus: 100,
  duration: '10m',
  thresholds: {
    http_req_duration: ['p(95)<300', 'p(99)<500'],
    http_req_failed: ['rate<0.001'],
    'http_req_duration{endpoint:orders}': ['p(95)<500'],
  },
};
// 트래픽 비율: browse 60, search 20, purchase 15, seller 5
```

### Ramp-up
```javascript
export const options = {
  stages: [
    { duration: '5m', target: 100 },
    { duration: '10m', target: 500 },
    { duration: '10m', target: 1000 },
    { duration: '5m', target: 0 },
  ],
  thresholds: {
    http_req_duration: [{ threshold: 'p(99)<1000', abortOnFail: true, delayAbortEval: '1m' }],
  },
};
```

### Spike
```javascript
export const options = {
  scenarios: {
    spike: {
      executor: 'ramping-arrival-rate',
      startRate: 500, timeUnit: '1s',
      preAllocatedVUs: 500, maxVUs: 3000,
      stages: [
        { duration: '2m', target: 500 },
        { duration: '1m', target: 2000 },
        { duration: '5m', target: 2000 },
        { duration: '2m', target: 500 },
      ],
    },
  },
};
// 관찰: Karpenter 노드 준비 시간, HPA 반응, 5xx
```

### Soak
`vus: 300`, `duration: '4h'`로 4시간 유지합니다. 지표 대신 **추세**를 봅니다.

| 관찰 대상 | 누수 신호 |
|---|---|
| Pod 메모리 | 시간에 비례해 증가 |
| DB 연결 수 | pool 한도에 수렴 후 대기 |
| goroutine, thread | 반환되지 않고 누적 |
| tail sampling 메모리 | num_traces 도달 후 drop |

:::notes
{timing: 2.5min}
[요약]
• Baseline, Ramp-up, Spike, Soak 네 가지 프로필
• threshold 문법은 'p(95)<300' 형식, 태그별 threshold와 abortOnFail 사용
• Spike는 ramping-arrival-rate(open model)로 초당 요청 수를 직접 제어
• Soak는 절대값보다 메모리, 연결, goroutine 추세를 봄

Baseline 탭부터 보겠습니다. 예전 자료에는 threshold가 'p95<500'으로 적혀 있었는데, k6 문법은 'p(95)<500'입니다. 잘못 쓰면 테스트가 시작되지 않습니다. 태그로 orders 엔드포인트만 따로 기준을 줄 수 있습니다.
Ramp-up은 VU를 단계적으로 늘리며, abortOnFail로 p99가 1초를 넘으면 테스트를 중단합니다. delayAbortEval로 초기 워밍업 구간은 평가에서 뺍니다.
{cue: pause}
Spike는 ramping-arrival-rate executor를 씁니다. VU 수가 아니라 초당 요청 수를 고정하는 open model이라, 서버가 느려져도 부하가 줄지 않아 실제 트래픽 폭주와 비슷합니다. 이때 Karpenter 노드가 준비되는 시간과 HPA 반응을 같이 기록합니다.
Soak는 4시간 동안 추세를 봅니다. 앞에서 본 연결 pool과 tail sampling 메모리가 여기서 드러납니다.
{cue: question}
부하 테스트를 CloudFront 앞에서 할지, internal ALB에 직접 할지도 정해야 합니다. edge까지 포함하려면 AWS 시뮬레이션 이벤트 정책을 먼저 확인하세요.
{cue: transition}
이 테스트의 합격선이 SLO입니다.

[출처]
• k6 thresholds 문법, abortOnFail, delayAbortEval: https://grafana.com/docs/k6/latest/using-k6/thresholds/ (확인일 2026-10-15)
• ramping-arrival-rate: https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/ramping-arrival-rate/
• AWS Simulated Events: https://aws.amazon.com/security/ddos-simulation-testing/
:::

---
<!-- Slide 12: SLO와 burn rate -->
@type: content
@title: SLO는 burn rate로 경보한다

## SLO는 burn rate로 경보한다

:::html
<style>
.mr05-slo .metric-value { font-size: var(--fs-subtitle); }
.mr05-slo-row { margin-top: var(--space-4); }
.mr05-s-a { color: var(--accent); font-weight: var(--weight-bold); }
.mr05-s-i { color: var(--info); font-weight: var(--weight-bold); }
.mr05-s-w { color: var(--warning); font-weight: var(--weight-bold); }
.mr05-s-t { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="card-grid mr05-slo" data-reveal="stagger">
  <div class="metric-card"><div class="metric-value">99.9%</div><div class="metric-label">가용성, 30일</div></div>
  <div class="metric-card"><div class="metric-value">p95 &lt; 300ms</div><div class="metric-label">전체 latency</div></div>
  <div class="metric-card"><div class="metric-value">p99 &lt; 500ms</div><div class="metric-label">orders, payments</div></div>
  <div class="metric-card"><div class="metric-value">43.2분</div><div class="metric-label">30일 error budget</div></div>
</div>
<div class="card-grid mr05-slo-row">
  <div class="callout callout-info fragment fade-up" data-fragment-index="1"><strong class="mr05-s-i">Application Signals SLO</strong><div class="mr05-s-t">period-based와 request-based 두 방식입니다. SLO당 burn rate 설정은 최대 10개입니다.</div></div>
  <div class="callout callout-warning fragment fade-up" data-fragment-index="2"><strong class="mr05-s-w">burn rate</strong><div class="mr05-s-t">baseline error rate = 100% - 목표입니다. 99.9%면 0.1%가 기준이고, 1보다 크면 budget을 빨리 씁니다.</div></div>
  <div class="callout callout-success fragment zoom-in" data-fragment-index="3"><strong class="mr05-s-a">리전별 SLO</strong><div class="mr05-s-t">SLO는 리전마다 따로 둡니다. 전역 평균은 한 리전 장애를 희석해 경보를 늦춥니다.</div></div>
</div>
:::

:::notes
{timing: 2min}
[요약]
• 시나리오 목표: 가용성 99.9%, p95 300ms, 쓰기 경로 p99 500ms
• 99.9% 30일 error budget = 30 × 24 × 60 × 0.001 = 43.2분
• Application Signals는 period-based, request-based SLO와 burn rate 알람 지원
• SLO와 알람은 리전별로, 전역 평균은 장애를 희석

위 숫자는 이 시나리오의 목표입니다. 99.9% 가용성은 30일 기준으로 43.2분의 error budget입니다.
CloudWatch Application Signals는 SLO를 두 방식으로 만듭니다. period-based는 정상 기간의 비율, request-based는 성공 요청의 비율입니다. burn rate는 baseline error rate 대비 실제 에러 비율이며, SLO 하나에 burn rate 설정을 최대 10개까지 둘 수 있고 각각 알람을 걸 수 있습니다.
{cue: pause}
실무 팁은 짧은 창과 긴 창을 같이 쓰는 multi-window 방식입니다. 그리고 SLO를 리전별로 둡니다. 두 리전 평균을 보면 us-west-2가 절반 장애여도 전체 수치는 목표 근처에 머물 수 있습니다. Block 3의 Route 53 health check와도 이 리전별 지표를 연결합니다.
{cue: transition}
마지막으로 출시까지 남은 간극을 보겠습니다.

[출처]
• Application Signals SLO, burn rate 정의: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-ServiceLevelObjectives.html
• BurnRateConfigurations 최대 10: https://docs.aws.amazon.com/applicationsignals/latest/APIReference/API_UpdateServiceLevelObjective.html (확인일 2026-10-15)
:::

---
<!-- Slide 13: Gap 분석과 로드맵 -->
@type: content
@title: P0 네 개가 출시를 막는다

## P0 네 개가 출시를 막는다

:::html
<style>
.mr05-gap { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-4); }
.mr05-gap .card { display: flex; flex-direction: column; gap: var(--space-2); }
.mr05-g-h { display: flex; justify-content: space-between; align-items: center; font-weight: var(--weight-bold); }
.mr05-g-d { color: var(--danger); }
.mr05-g-w { color: var(--warning); }
.mr05-g-i { color: var(--info); }
.mr05-g-item { color: var(--on-surface); font-size: var(--fs-card); word-break: keep-all; }
.mr05-g-item span { display: block; color: var(--text-secondary); font-size: var(--fs-caption); }
.mr05-g-phase { margin-top: auto; color: var(--text-secondary); font-size: var(--fs-caption); border-top: 1px solid var(--border); padding-top: var(--space-2); }
</style>
<div class="mr05-gap">
  <div class="card fragment fade-up" data-fragment-index="1">
    <div class="mr05-g-h"><span class="mr05-g-d">P0 출시 차단, 데이터 보호</span><span class="badge badge-red">Phase 1, 2주</span></div>
    <div class="mr05-g-item">인증 미들웨어 없음<span>gateway가 누구의 호출이든 통과</span></div>
    <div class="mr05-g-item">event bus가 mock publish<span>MSK consumer 7개가 이벤트를 못 받음</span></div>
    <div class="mr05-g-item">MSK Replicator 미구성<span>리전 간 topic, consumer offset 동기화 없음</span></div>
    <div class="mr05-g-item">Aurora Global DB 전환 준비 미흡<span>rds.global_db_rpo 미설정, global writer endpoint 미적용</span></div>
    <div class="mr05-g-phase">완료 기준: 인증 통합 테스트, 이벤트 end-to-end trace, us-west-2 topic 복제 lag 확인</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="2">
    <div class="mr05-g-h"><span class="mr05-g-w">P1 운영 위험</span><span class="badge badge-yellow">Phase 2, 4주</span></div>
    <div class="mr05-g-item">WAF Bot Control이 synthetic 차단<span>모니터링 체크 실패, scope-down 필요</span></div>
    <div class="mr05-g-item">search가 문자열 비교 mock<span>OpenSearch 연동 전</span></div>
    <div class="mr05-g-phase">함께 처리: 클라이언트 기본값 4건 수정</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="3">
    <div class="mr05-g-h"><span class="mr05-g-i">P2 개선</span><span class="badge badge-blue">Phase 3, 2주</span></div>
    <div class="mr05-g-item">CI/CD 수동 배포<span>두 리전 동시 배포 파이프라인</span></div>
    <div class="mr05-g-phase">Phase 4 상시: k6 4개 프로필, SLO 튜닝, 비용 최적화</div>
  </div>
</div>
:::

:::notes
{timing: 2min}
[요약]
• 시나리오 gap 7개: P0 4개, P1 2개, P2 1개
• P0(인증, event bus mock, MSK Replicator)이 해결되기 전에는 출시 불가, Block 4 로드맵의 P0 데이터 보호와 같은 항목
• P1의 Aurora Global Database gap: rds.global_db_rpo 미설정, 앱이 global writer endpoint 대신 클러스터 endpoint 사용
• Phase 1 2주, Phase 2 4주, Phase 3 2주, Phase 4는 상시
• 각 Phase 완료 기준을 관측 데이터로 확인

이 시나리오 코드베이스를 점검한 결과입니다. 왼쪽 P0 네 개가 출시를 막습니다. gateway에 인증이 없고, event bus가 MSK에 실제로 publish하지 않아 consumer들이 이벤트를 받지 못합니다. 그리고 MSK Replicator가 아직 없어서 us-east-1이 멈추면 그 시점까지의 이벤트가 us-west-2에 없습니다. 넷째, order와 payment가 쓰는 Aurora PostgreSQL Global Database는 복제는 돌고 있지만 전환 준비가 덜 됐습니다. rds.global_db_rpo가 없어 RPO 상한이 없고, 앱이 global writer endpoint 대신 us-east-1 클러스터 endpoint를 직접 써서 failover 후 앱 설정을 바꿔야 합니다. Block 4 로드맵에서 데이터 보호를 P0로 둔 것과 같은 이유입니다. Phase 1의 2주 안에 해결하고, 완료 기준은 이벤트가 producer에서 consumer까지 하나의 trace로 보이고, us-west-2에서 복제 lag가 관측되는 것입니다. 앞에서 만든 관측 스택이 바로 검증 도구가 됩니다.
{cue: pause}
P1은 운영 위험입니다. WAF Bot Control이 synthetic 모니터링 요청을 막고 있고, search는 아직 mock입니다. 전환 절차 자체는 Block 4에서 다뤘습니다. 앞에서 본 클라이언트 기본값 4건도 이 Phase에서 함께 고칩니다.
P2는 CI/CD 자동화입니다. 그 뒤 Phase 4는 부하 테스트, SLO 튜닝, 비용 최적화를 상시로 돌립니다. 순서가 중요합니다. 기능 gap을 닫기 전에 비용 최적화를 하면 측정 기준이 계속 바뀝니다.
{cue: transition}
전체 내용을 정리하겠습니다.

[출처]
• Aurora PostgreSQL managed RPO, rds.global_db_rpo: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-disaster-recovery.html
• Aurora Global Database global writer endpoint: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-connecting.html
• MSK Replicator: https://docs.aws.amazon.com/msk/latest/developerguide/msk-replicator.html
:::

---
<!-- Slide 14: Key Takeaways -->
@type: content
@title: Key Takeaways

## Key Takeaways

:::html
<style>
.mr05-kt .metric-card { text-align: left; }
.mr05-k-a { color: var(--accent); font-weight: var(--weight-bold); }
.mr05-k-s { color: var(--success); font-weight: var(--weight-bold); }
.mr05-k-w { color: var(--warning); font-weight: var(--weight-bold); }
.mr05-k-t { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="card-grid mr05-kt fragment" data-reveal="stagger" data-reveal-anim="zoom" data-reveal-pace="slow" data-fragment-index="1">
  <div class="metric-card"><strong class="mr05-k-a">1. 리전 로컬 관측</strong><div class="mr05-k-t">텔레메트리는 리전 안에서 끝내고 조회만 전역으로 모읍니다.</div></div>
  <div class="metric-card"><strong class="mr05-k-a">2. Collector 2계층</strong><div class="mr05-k-t">traceID 라우팅 없이는 tail sampling을 확장할 수 없습니다.</div></div>
  <div class="metric-card"><strong class="mr05-k-a">3. OTel이 표준</strong><div class="mr05-k-t">X-Ray SDK는 maintenance mode, OTLP endpoint와 Transaction Search로 갑니다.</div></div>
  <div class="metric-card"><strong class="mr05-k-s">4. OAM은 리전 안</strong><div class="mr05-k-t">리전마다 sink, 리전 간 집계는 Centralization rule입니다.</div></div>
  <div class="metric-card"><strong class="mr05-k-s">5. 바이트가 비용</strong><div class="mr05-k-t">리전 간 $0.02/GB, NAT $0.045/GB. 측정하고 줄입니다.</div></div>
  <div class="metric-card"><strong class="mr05-k-w">6. 출시는 P0부터</strong><div class="mr05-k-t">gap, 성능, 부하 테스트, 비용 순서로 리전별 SLO에 맞춥니다.</div></div>
</div>
:::

:::notes
{timing: 1.5min}
[요약]
• 관측은 리전 로컬, 조회만 전역
• tail sampling 확장에는 traceID 라우팅 필수, X-Ray는 OTel 경로로
• OAM은 같은 Region, 리전 간은 Centralization
• 비용은 리전 간과 NAT 바이트, 출시는 P0부터

여섯 가지로 정리합니다. 텔레메트리는 리전 안에서 끝내고, Collector는 2계층으로 나눠 traceID로 라우팅합니다. X-Ray는 SDK가 maintenance mode에 들어갔으니 OpenTelemetry와 OTLP endpoint로 갑니다.
{cue: pause}
CloudWatch OAM은 리전을 넘지 않으므로 리전마다 sink를 만들고, 리전 간 집계는 Centralization rule로 합니다. 비용은 리전을 넘는 바이트와 NAT를 지나는 바이트가 정합니다. 마지막으로 출시는 P0 gap부터, 리전별 SLO를 합격선으로 삼습니다.
{cue: transition}
퀴즈로 확인해 보겠습니다.
:::

---
<!-- Slide 15: Knowledge Check 1/2 -->
@type: quiz
@title: Knowledge Check 1

## Knowledge Check (1/2)

**Q1: tail sampling Gateway를 여러 개로 늘릴 때 반드시 필요한 것은?**
- [ ] decision_wait를 0으로 설정
- [x] trace ID 기준으로 span을 같은 인스턴스에 보내는 loadbalancing exporter
- [ ] probabilistic 정책을 100%로 설정

**Q2: CloudWatch cross-account observability(OAM)에 대한 설명으로 맞는 것은?**
- [ ] 하나의 sink로 모든 리전의 source 계정을 연결한다
- [x] sink와 link가 같은 Region이어야 하므로 리전마다 sink가 필요하다
- [ ] logs와 traces는 공유할 수 없다

:::notes
{timing: 1min}
[요약]
• Q1: loadbalancing exporter, routing_key: traceID
• Q2: OAM은 같은 Region, 리전마다 sink
• 오답이면 "Collector 2계층", "OAM은 리전을 넘지 않는다" 슬라이드로 돌아가 확인

두 문제를 먼저 풀어보겠습니다.
{cue: poll}
1번은 loadbalancing exporter입니다. 같은 trace의 span이 다른 Gateway로 흩어지면 에러 여부를 판단할 수 없습니다. decision_wait를 0으로 두면 span이 다 오기 전에 판단하게 됩니다.
2번은 리전마다 sink가 필요하다는 것입니다. OAM은 logs와 traces도 공유하므로 세 번째 보기도 틀립니다.
{cue: transition}
마지막 한 문제는 비용입니다.
:::

---
<!-- Slide 16: Knowledge Check 2/2 -->
@type: quiz
@title: Knowledge Check 2

## Knowledge Check (2/2)

**Q3: us-east-1 → us-west-2 리전 간 데이터 전송 list price는? (2026-10-15 기준)**
- [ ] $0.00/GB, 같은 국가 안 리전 간은 무료
- [ ] $0.01/GB
- [x] $0.02/GB
- [ ] $0.09/GB

:::notes
{timing: 0.5min}
[요약]
• Q3: $0.02/GB (Pricing API, USE1-USW2-AWS-Out-Bytes)
• $0.09/GB는 인터넷 전송 요금대와 혼동하기 쉬운 숫자

3번은 GB당 0.02달러입니다. 같은 국가 안이라도 리전 간 전송은 무료가 아니며, 0.09달러는 인터넷으로 나가는 전송 요금대와 혼동하기 쉬운 숫자입니다. 하루 1TB를 복제하면 월 약 600달러라는 감각을 기억해 두세요.
{cue: transition}
이것으로 마무리하겠습니다.
:::

---
<!-- Slide 17: Thank You -->
@type: thankyou
@toc: toc.html
@message: Multi-Region Architecture Deep Dive, 감사합니다

# Thank You

Block 5: Observability & Operations 완료

:::notes
{timing: 0.5min}
[요약]
• 다섯 블록 완료: Foundation, Data Sync, Traffic Routing, DR과 Failover, Observability와 Operations
• 가격과 설정 키는 2026-10-15 기준, 적용 전 최신 문서로 재확인
• 목차로 돌아가 다른 블록을 복습 가능

이것으로 Multi-Region Architecture Deep Dive를 마칩니다. 다섯 블록에 걸쳐 리전 기반 설계, 데이터 복제, 트래픽 라우팅, DR 자동화, 그리고 관측과 운영까지 살펴봤습니다. 오늘 보여드린 가격과 설정 키는 2026년 10월 15일 기준이니 적용 전에 다시 확인해 주세요.
{cue: question}
질문 받겠습니다.
:::
