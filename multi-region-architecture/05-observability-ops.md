---
remarp: true
block: observability-ops
title: "Observability & Operations"
---

---
<!-- Slide 1: Cover -->
@type: cover

# Observability & Operations
Cross-Region Monitoring, Cost Optimization, Production Readiness

:::notes
{timing: 1min}
마지막 블록입니다. 지금까지 아키텍처 개요, 데이터 싱크, 트래픽 라우팅, DR/Failover를 다뤘고, 이제 운영의 핵심인 Observability와 Production Readiness를 살펴보겠습니다.

이 블록에서는 네 가지를 다룹니다. 첫째, Cross-Region Observability Stack — 20개 서비스에서 나오는 메트릭, 로그, 트레이스를 어떻게 수집하고 분석하는지. 둘째, Tail-Based Sampling — 트레이스 저장 비용을 90% 줄이면서 중요한 데이터는 100% 보존하는 전략. 셋째, Cost Analysis — 월 $9,600-12,400 비용의 상세 내역과 최적화 기회. 넷째, Production Readiness — Gap 분석, 성능 병목점, Load Test 전략까지.

{cue: transition}
먼저 Observability Stack 전체 구조부터 보겠습니다.
:::

---
<!-- Slide 2: Observability Stack Overview -->
@type: content

## Observability Stack Overview

:::html
<div class="flow-h" style="flex-wrap:wrap; gap:0.8rem; justify-content:center; align-items:flex-start;">
  <div class="flow-group bg-blue" style="min-width:140px;" data-fragment-index="1">
    <div class="flow-group-label">App Pods (20 svc)</div>
    <div class="flow-v" style="gap:0.3rem;">
      <div class="flow-box" style="font-size:0.8rem;">OTLP export</div>
    </div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-group bg-orange" style="min-width:180px;" data-fragment-index="2">
    <div class="flow-group-label">OTel Collector</div>
    <div class="flow-v" style="gap:0.3rem;">
      <div class="flow-box" style="font-size:0.8rem;">DaemonSet</div>
      <div class="flow-box" style="font-size:0.8rem;">ADOT 0.40.0</div>
      <div class="flow-box" style="font-size:0.8rem;">tail_sampling</div>
    </div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-col" style="gap:0.5rem;" data-fragment-index="3">
    <div class="flow-group bg-purple" style="min-width:150px;">
      <div class="flow-group-label">Traces</div>
      <div class="flow-h" style="gap:0.3rem;">
        <div class="icon-item sm"><img src="common/aws-icons/services/Arch_AWS-X-Ray_48.svg"><span>X-Ray</span></div>
        <div class="flow-box" style="font-size:0.75rem;">Tempo→S3</div>
      </div>
    </div>
    <div class="flow-group bg-green" style="min-width:150px;">
      <div class="flow-group-label">Metrics</div>
      <div class="icon-item sm"><img src="common/aws-icons/services/Arch_Amazon-Managed-Service-for-Prometheus_48.svg"><span>Prometheus</span></div>
      <div class="flow-box" style="font-size:0.75rem;">kube-prom 68.4.0</div>
    </div>
    <div class="flow-group bg-pink" style="min-width:150px;">
      <div class="flow-group-label">Logs</div>
      <div class="icon-item sm"><img src="common/aws-icons/services/Arch_Amazon-CloudWatch_48.svg"><span>CloudWatch</span></div>
    </div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-group bg-accent" style="min-width:120px;" data-fragment-index="4">
    <div class="flow-group-label">Visualization</div>
    <div class="flow-box" style="font-size:0.85rem;">Grafana</div>
  </div>
</div>
<p style="margin-top:16px; font-size:0.85rem; color:var(--text-muted); text-align:center;">
  <strong>Dual Export</strong>: Tempo (S3 장기 저장) + X-Ray (managed, 서비스 맵)
</p>
:::

:::notes
{timing: 3min}
전체 Observability 파이프라인입니다. 왼쪽부터 오른쪽으로 데이터가 흐릅니다.

먼저 20개 서비스의 Pod들이 OTLP 프로토콜로 텔레메트리를 내보냅니다. 각 서비스에는 OpenTelemetry SDK가 instrumentation되어 있고, 메트릭, 로그, 트레이스 세 가지 신호를 모두 내보냅니다.

그 다음 OTel Collector입니다. AWS Distro for OpenTelemetry 0.40.0 버전을 DaemonSet으로 배포했습니다. 여기서 핵심은 tail_sampling processor입니다. 모든 트레이스를 저장하면 비용이 폭발하니까, 에러와 느린 요청만 100% 저장하고 정상 요청은 10%만 샘플링합니다.

{cue: pause}
Collector에서 나온 데이터는 세 갈래로 갑니다. 트레이스는 Tempo와 X-Ray 둘 다로 보냅니다. Tempo는 S3에 장기 저장하고, X-Ray는 AWS 서비스 맵과 통합을 위해 씁니다. 메트릭은 kube-prometheus-stack 68.4.0으로 가고, 로그는 CloudWatch Logs로 갑니다.

마지막으로 Grafana에서 모든 데이터를 통합 조회합니다. Tempo, Prometheus, CloudWatch 세 가지 데이터소스를 연결해서 하나의 대시보드에서 메트릭-로그-트레이스 상관분석이 가능합니다.

{cue: transition}
OTel Collector 설정을 자세히 보겠습니다.
:::

---
<!-- Slide 3: OTel Collector Configuration -->
@type: tabs

## OTel Collector Configuration

### Receivers & Processors

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  memory_limiter:
    check_interval: 1s
    limit_mib: 512
    spike_limit_mib: 128

  tail_sampling:
    decision_wait: 10s
    policies:
      - name: errors-policy
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: slow-policy
        type: latency
        latency: { threshold_ms: 500 }
      - name: default-policy
        type: probabilistic
        probabilistic: { sampling_percentage: 10 }
```

### Exporters & Pipeline

```yaml
exporters:
  otlp/tempo:
    endpoint: tempo.observability:4317
    tls:
      insecure: true

  awsxray:
    region: ${AWS_REGION}
    index_all_attributes: true

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, tail_sampling, batch]
      exporters: [otlp/tempo, awsxray]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheusremotewrite]
```

:::notes
{timing: 3min}
OTel Collector 설정의 핵심 부분입니다.

첫 번째 탭은 Receivers와 Processors입니다. OTLP receiver가 gRPC 4317, HTTP 4318 포트에서 텔레메트리를 받습니다. memory_limiter는 OOM을 방지하기 위해 512MiB 제한을 걸었습니다.

핵심은 tail_sampling processor입니다. decision_wait 10초 동안 트레이스의 모든 span을 모은 다음 샘플링 결정을 내립니다. 세 가지 정책이 있는데요, errors-policy는 에러가 있는 트레이스를 100% 저장합니다. slow-policy는 500ms 이상 걸린 요청을 100% 저장합니다. default-policy는 나머지를 10%만 샘플링합니다.

{cue: pause}
두 번째 탭은 Exporters와 Pipeline입니다. Tempo로는 OTLP로 내보내고, X-Ray로는 awsxray exporter를 씁니다. index_all_attributes를 true로 해서 모든 span 속성을 검색 가능하게 했습니다.

Pipeline 정의를 보면, traces 파이프라인은 otlp → memory_limiter → tail_sampling → batch → tempo,xray 순서입니다. metrics는 tail_sampling이 없고 바로 prometheusremotewrite로 갑니다.

{cue: transition}
tail_sampling의 효과를 구체적인 숫자로 보겠습니다.
:::

---
<!-- Slide 4: Tail-Based Sampling Strategy -->
@type: content

## Tail-Based Sampling Strategy

:::html
<div class="col-2" style="gap:1.5rem;">
  <div>
    <h4 style="margin:0 0 0.75rem 0; color:var(--accent);">Why Tail > Head Sampling?</h4>
    <div class="card" style="padding:1rem; margin-bottom:0.75rem;">
      <p style="margin:0; font-size:0.9rem;"><strong>Head Sampling</strong>: 요청 시작 시 샘플링 결정</p>
      <p style="margin:0.5rem 0 0 0; font-size:0.85rem; color:var(--text-muted);">문제: 에러/지연 발생 전에 결정 → 중요 트레이스 누락</p>
    </div>
    <div class="card" style="padding:1rem; border-color:var(--green);">
      <p style="margin:0; font-size:0.9rem;"><strong>Tail Sampling</strong>: 전체 트레이스 완료 후 결정</p>
      <p style="margin:0.5rem 0 0 0; font-size:0.85rem; color:var(--green);">장점: 에러/지연 여부 확인 후 선택적 저장</p>
    </div>
  </div>
  <div>
    <h4 style="margin:0 0 0.75rem 0; color:var(--cyan);">Sampling Policies</h4>
    <table class="data-table" style="width:100%; font-size:0.85rem;">
      <thead>
        <tr style="background:var(--bg-card);">
          <th style="padding:8px; text-align:left;">Policy</th>
          <th style="padding:8px; text-align:center;">Rate</th>
          <th style="padding:8px; text-align:left;">Condition</th>
        </tr>
      </thead>
      <tbody>
        <tr style="border-bottom:1px solid var(--border);">
          <td style="padding:8px;"><span style="color:var(--red);">errors</span></td>
          <td style="padding:8px; text-align:center; font-weight:600;">100%</td>
          <td style="padding:8px;">status_code = ERROR</td>
        </tr>
        <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);">
          <td style="padding:8px;"><span style="color:#fdcb6e;">slow</span></td>
          <td style="padding:8px; text-align:center; font-weight:600;">100%</td>
          <td style="padding:8px;">latency > 500ms</td>
        </tr>
        <tr>
          <td style="padding:8px;"><span style="color:var(--text-muted);">default</span></td>
          <td style="padding:8px; text-align:center;">10%</td>
          <td style="padding:8px;">probabilistic</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
<div style="margin-top:1rem; padding:12px 16px; background:rgba(0,214,143,0.1); border:1px solid var(--green); border-radius:8px; text-align:center;">
  <strong style="color:var(--green);">Storage Savings: ~90%</strong>
  <span style="color:var(--text-muted); margin-left:12px;">while keeping 100% of errors & slow traces</span>
</div>
:::

:::notes
{timing: 2min}
Tail-Based Sampling이 왜 중요한지 설명드리겠습니다.

Head Sampling은 요청이 시작될 때 "이 요청을 추적할까 말까"를 결정합니다. 문제는 요청이 끝나기 전에 결정하니까, 나중에 에러가 나거나 느려져도 이미 샘플링에서 제외됐으면 트레이스가 없습니다. 디버깅할 때 정작 필요한 데이터가 없는 거죠.

Tail Sampling은 트레이스의 모든 span이 도착할 때까지 기다렸다가 결정합니다. 에러가 났는지, 얼마나 걸렸는지 다 확인한 후에 저장 여부를 정합니다.

{cue: pause}
오른쪽 테이블이 우리 정책입니다. 에러가 있으면 무조건 100% 저장합니다. 500ms 이상 걸린 요청도 100% 저장합니다. 나머지 정상 요청은 10%만 샘플링합니다.

결과적으로 저장 비용은 90% 절감되면서, 장애 분석에 필요한 모든 에러와 지연 트레이스는 100% 보존됩니다. 이게 핵심입니다.

{cue: transition}
이렇게 샘플링된 트레이스가 Tempo에 어떻게 저장되는지 보겠습니다.
:::

---
<!-- Slide 5: Grafana Tempo Integration -->
@type: content

## Grafana Tempo Integration

:::html
<div class="col-2" style="gap:1.5rem;">
  <div>
    <h4 style="margin:0 0 0.75rem 0; color:var(--accent);">Architecture</h4>
    <div class="flow-v" style="gap:0.5rem;">
      <div class="flow-box bg-orange" style="width:100%;">OTel Collector</div>
      <div class="flow-arrow">↓</div>
      <div class="flow-box bg-purple" style="width:100%;">Tempo (Monolithic)</div>
      <div class="flow-arrow">↓</div>
      <div class="flow-group bg-blue" style="width:100%;">
        <div class="flow-group-label">S3 Backend</div>
        <div class="flow-box" style="font-size:0.8rem;">Parquet blocks</div>
      </div>
    </div>
    <div class="card" style="margin-top:0.75rem; padding:0.75rem;">
      <p style="margin:0; font-size:0.85rem;"><strong>Retention</strong>: 30 days hot, 90 days warm</p>
      <p style="margin:0.25rem 0 0 0; font-size:0.85rem;"><strong>Compression</strong>: zstd (60% savings)</p>
    </div>
  </div>
  <div>
    <h4 style="margin:0 0 0.75rem 0; color:var(--cyan);">S3 Lifecycle Policy</h4>
    <table class="data-table" style="width:100%; font-size:0.85rem;">
      <thead>
        <tr style="background:var(--bg-card);">
          <th style="padding:8px; text-align:left;">Tier</th>
          <th style="padding:8px; text-align:center;">Days</th>
          <th style="padding:8px; text-align:right;">Cost/GB</th>
        </tr>
      </thead>
      <tbody>
        <tr style="border-bottom:1px solid var(--border);">
          <td style="padding:8px;">S3 Standard</td>
          <td style="padding:8px; text-align:center;">0-30</td>
          <td style="padding:8px; text-align:right;">$0.023</td>
        </tr>
        <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);">
          <td style="padding:8px;">S3 IA</td>
          <td style="padding:8px; text-align:center;">30-90</td>
          <td style="padding:8px; text-align:right;">$0.0125</td>
        </tr>
        <tr style="border-bottom:1px solid var(--border);">
          <td style="padding:8px;">Glacier IR</td>
          <td style="padding:8px; text-align:center;">90-365</td>
          <td style="padding:8px; text-align:right;">$0.004</td>
        </tr>
        <tr style="background:var(--bg-card);">
          <td style="padding:8px; color:var(--red);">Delete</td>
          <td style="padding:8px; text-align:center;">365+</td>
          <td style="padding:8px; text-align:right;">-</td>
        </tr>
      </tbody>
    </table>
    <div style="margin-top:0.75rem; padding:8px 12px; background:var(--bg-card); border-radius:6px; text-align:center;">
      <span style="font-size:0.85rem; color:var(--text-muted);">Est. Cost:</span>
      <strong style="color:var(--accent); margin-left:8px;">~$185/mo per region</strong>
    </div>
  </div>
</div>
:::

:::notes
{timing: 2min}
Tempo 아키텍처입니다. Monolithic 모드로 배포해서 단일 Pod에서 ingester, querier, compactor 역할을 다 합니다. 트래픽이 많지 않을 때는 이게 더 효율적입니다.

백엔드는 S3입니다. Parquet 포맷으로 블록을 저장하고, zstd 압축을 써서 저장 용량을 60% 줄였습니다.

{cue: pause}
오른쪽은 S3 Lifecycle Policy입니다. 최근 30일 데이터는 Standard에서 빠르게 조회합니다. 30-90일은 Infrequent Access로 내려서 비용을 절반으로 줄입니다. 90일 이후에는 Glacier Instant Retrieval로 가는데, 여전히 밀리초 단위로 조회 가능하면서 비용은 GB당 $0.004입니다. 1년이 지나면 삭제합니다.

이 구조로 리전당 월 $185 정도 비용이 예상됩니다. 두 리전이면 $370인데, 모든 트레이스를 저장하는 것보다 훨씬 저렴합니다.

{cue: transition}
Tempo와 다른 데이터소스 간 상관분석 방법을 보겠습니다.
:::

---
<!-- Slide 6: Cross-Region Trace Correlation -->
@type: content

## Cross-Region Trace Correlation

:::html
<div class="col-2" style="gap:1.5rem;">
  <div>
    <h4 style="margin:0 0 0.75rem 0; color:var(--accent);">TraceQL Examples</h4>
    <div class="code-block" style="font-size:0.8rem; margin-bottom:0.75rem;">
<span class="comment"># 특정 서비스의 에러 트레이스</span>
<span class="key">{</span> <span class="string">resource.service.name</span> = <span class="value">"order-service"</span> <span class="key">}</span>
  | <span class="key">status</span> = <span class="value">error</span>

<span class="comment"># 500ms 이상 걸린 결제 요청</span>
<span class="key">{</span> <span class="string">span.http.route</span> = <span class="value">"/api/payments"</span> <span class="key">}</span>
  | <span class="key">duration</span> > <span class="value">500ms</span>

<span class="comment"># Cross-region 트레이스 (us-east → us-west)</span>
<span class="key">{</span> <span class="string">resource.cloud.region</span> = <span class="value">"us-east-1"</span> <span class="key">}</span>
  >> <span class="key">{</span> <span class="string">resource.cloud.region</span> = <span class="value">"us-west-2"</span> <span class="key">}</span></div>
    <h4 style="margin:0.75rem 0 0.5rem 0; color:var(--cyan);">Service Map Generation</h4>
    <p style="font-size:0.85rem; color:var(--text-muted); margin:0;">
      Tempo <code>metrics_generator</code>가 span 데이터에서 자동으로 서비스 의존성 그래프 생성
    </p>
  </div>
  <div>
    <h4 style="margin:0 0 0.75rem 0; color:var(--green);">Logs-to-Traces Correlation</h4>
    <div class="card" style="padding:0.75rem; margin-bottom:0.5rem;">
      <p style="margin:0; font-size:0.85rem;"><strong>1. TraceID Injection</strong></p>
      <div class="code-block" style="font-size:0.75rem; margin-top:0.5rem;">
<span class="comment"># Application log format</span>
<span class="key">{"level"</span>:<span class="string">"error"</span>,
 <span class="key">"traceId"</span>:<span class="value">"abc123..."</span>,
 <span class="key">"spanId"</span>:<span class="value">"def456..."</span>,
 <span class="key">"msg"</span>:<span class="string">"payment failed"</span><span class="key">}</span></div>
    </div>
    <div class="card" style="padding:0.75rem;">
      <p style="margin:0; font-size:0.85rem;"><strong>2. Grafana Derived Fields</strong></p>
      <div class="code-block" style="font-size:0.75rem; margin-top:0.5rem;">
<span class="comment"># Loki datasource config</span>
<span class="key">derivedFields</span>:
  - <span class="key">name</span>: <span class="string">TraceID</span>
    <span class="key">matcherRegex</span>: <span class="string">"traceId\":\"([^\"]+)"</span>
    <span class="key">url</span>: <span class="string">"$${__value.raw}"</span>
    <span class="key">datasourceUid</span>: <span class="string">tempo</span></div>
    </div>
  </div>
</div>
:::

:::notes
{timing: 2min}
Tempo의 TraceQL로 트레이스를 검색하는 예시입니다.

첫 번째 쿼리는 order-service의 에러 트레이스를 찾습니다. 두 번째는 /api/payments 엔드포인트에서 500ms 이상 걸린 요청을 찾습니다. 세 번째가 재미있는데, Cross-region 트레이스를 찾습니다. us-east-1에서 시작해서 us-west-2로 넘어간 트레이스를 쿼리합니다. >> 연산자가 "자식 span"을 의미합니다.

{cue: pause}
오른쪽은 Logs-to-Traces correlation입니다. 로그에서 에러를 발견했을 때 해당 트레이스로 바로 점프하는 기능입니다.

먼저 애플리케이션 로그에 traceId와 spanId를 JSON 필드로 넣습니다. 대부분의 OpenTelemetry SDK가 자동으로 해줍니다. 그 다음 Grafana의 Loki 데이터소스에 derivedFields를 설정합니다. 정규식으로 traceId를 추출하고, 클릭하면 Tempo로 연결됩니다.

이렇게 하면 로그에서 에러를 보고 → 클릭 → 전체 트레이스 확인 → 어떤 서비스에서 지연이 발생했는지 바로 파악할 수 있습니다.

{cue: transition}
이제 전체 비용 분석으로 넘어가겠습니다.
:::

---
<!-- Slide 7: Cost Analysis Overview -->
@type: content

## Cost Analysis — $9,600 ~ $12,400/month

:::html
<div style="display:flex; gap:1rem; flex-wrap:wrap; justify-content:center;">
  <div class="card" style="flex:1; min-width:200px; max-width:250px; padding:1rem; text-align:center; border-top:3px solid var(--accent);">
    <img src="common/aws-icons/services/Arch_Amazon-EC2_48.svg" style="width:40px; margin-bottom:0.5rem;">
    <div style="font-size:1.5rem; font-weight:700; color:var(--accent);">$3,186-4,586</div>
    <div style="font-size:0.85rem; color:var(--text-muted);">Compute (33-37%)</div>
    <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:0.25rem;">EKS + EC2 (Karpenter)</div>
  </div>
  <div class="card" style="flex:1; min-width:200px; max-width:250px; padding:1rem; text-align:center; border-top:3px solid var(--cyan);">
    <img src="common/aws-icons/services/Arch_Amazon-RDS_48.svg" style="width:40px; margin-bottom:0.5rem;">
    <div style="font-size:1.5rem; font-weight:700; color:var(--cyan);">$2,560</div>
    <div style="font-size:0.85rem; color:var(--text-muted);">Database (21-27%)</div>
    <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:0.25rem;">Aurora + DocDB + ElastiCache</div>
  </div>
  <div class="card" style="flex:1; min-width:200px; max-width:250px; padding:1rem; text-align:center; border-top:3px solid #fdcb6e;">
    <img src="common/aws-icons/services/Arch_Amazon-MSK_48.svg" style="width:40px; margin-bottom:0.5rem;">
    <div style="font-size:1.5rem; font-weight:700; color:#fdcb6e;">$1,620</div>
    <div style="font-size:0.85rem; color:var(--text-muted);">Messaging (13-17%)</div>
    <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:0.25rem;">MSK kafka.m5.large x6</div>
  </div>
  <div class="card" style="flex:1; min-width:200px; max-width:250px; padding:1rem; text-align:center; border-top:3px solid var(--green);">
    <img src="common/aws-icons/services/Arch_Amazon-OpenSearch-Service_48.svg" style="width:40px; margin-bottom:0.5rem;">
    <div style="font-size:1.5rem; font-weight:700; color:var(--green);">$1,560</div>
    <div style="font-size:0.85rem; color:var(--text-muted);">Search (13-16%)</div>
    <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:0.25rem;">OpenSearch r6g.large x4</div>
  </div>
</div>
<div style="display:flex; gap:1rem; flex-wrap:wrap; justify-content:center; margin-top:1rem;">
  <div class="card" style="flex:1; min-width:150px; max-width:180px; padding:0.75rem; text-align:center;">
    <div style="font-size:1.1rem; font-weight:600; color:var(--text);">$452+</div>
    <div style="font-size:0.8rem; color:var(--text-muted);">Networking</div>
    <div style="font-size:0.7rem; color:var(--text-secondary);">NAT+TGW+NLB</div>
  </div>
  <div class="card" style="flex:1; min-width:150px; max-width:180px; padding:0.75rem; text-align:center;">
    <div style="font-size:1.1rem; font-weight:600; color:var(--text);">$50-500</div>
    <div style="font-size:0.8rem; color:var(--text-muted);">Edge</div>
    <div style="font-size:0.7rem; color:var(--text-secondary);">CloudFront+WAF</div>
  </div>
  <div class="card" style="flex:1; min-width:150px; max-width:180px; padding:0.75rem; text-align:center;">
    <div style="font-size:1.1rem; font-weight:600; color:var(--text);">$150-400</div>
    <div style="font-size:0.8rem; color:var(--text-muted);">Observability</div>
    <div style="font-size:0.7rem; color:var(--text-secondary);">CW+X-Ray+Prom</div>
  </div>
  <div class="card" style="flex:1; min-width:150px; max-width:180px; padding:0.75rem; text-align:center;">
    <div style="font-size:1.1rem; font-weight:600; color:var(--text);">$29</div>
    <div style="font-size:0.8rem; color:var(--text-muted);">Security</div>
    <div style="font-size:0.7rem; color:var(--text-secondary);">KMS+Secrets Mgr</div>
  </div>
</div>
:::

:::notes
{timing: 2min}
전체 비용 분석입니다. 월 $9,600에서 $12,400 사이로 추정됩니다.

가장 큰 비중은 Compute입니다. EKS Control Plane 두 개가 고정 $146이고, 나머지는 Karpenter가 프로비저닝하는 EC2 비용입니다. 트래픽에 따라 $3,000에서 $4,500까지 변동됩니다.

Database는 Aurora DSQL, DocumentDB, ElastiCache를 합쳐서 약 $2,560입니다. DSQL은 사용량 기반이라 변동이 있지만 DocumentDB와 ElastiCache는 인스턴스 비용이 고정입니다.

{cue: pause}
MSK가 $1,620으로 상당히 큽니다. kafka.m5.large 브로커 3개씩 두 리전이니까요. OpenSearch도 $1,560으로 비슷한 규모입니다.

아래 작은 카드들은 부가 비용입니다. Networking이 $452 이상인데, NAT Gateway가 가장 큽니다. Edge는 트래픽에 따라 $50에서 $500까지 변동되고, Observability는 CloudWatch, X-Ray, Prometheus 합쳐서 $150-400입니다.

{cue: transition}
이 비용을 어떻게 줄일 수 있는지 보겠습니다.
:::

---
<!-- Slide 8: Cost by Category Detail -->
@type: content

## Cost Breakdown by Service

:::html
<div style="overflow-x:auto;">
<table class="data-table" style="width:100%; font-size:0.82rem; border-collapse:collapse;">
  <thead>
    <tr style="background:var(--bg-card); border-bottom:2px solid var(--border);">
      <th style="padding:8px 10px; text-align:left; color:var(--text-muted);">Category</th>
      <th style="padding:8px 10px; text-align:left; color:var(--text-muted);">Service</th>
      <th style="padding:8px 10px; text-align:left; color:var(--text-muted);">Spec</th>
      <th style="padding:8px 10px; text-align:right; color:var(--text-muted);">Cost/mo</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom:1px solid var(--border);">
      <td rowspan="3" style="padding:8px 10px; vertical-align:top; font-weight:600; color:var(--accent);">Compute</td>
      <td style="padding:8px 10px;">EKS Control Plane</td>
      <td style="padding:8px 10px; color:var(--text-muted);">x2 regions</td>
      <td style="padding:8px 10px; text-align:right;">$146</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);">
      <td style="padding:8px 10px;">Karpenter EC2</td>
      <td style="padding:8px 10px; color:var(--text-muted);">m6i/c6i.xlarge variable</td>
      <td style="padding:8px 10px; text-align:right;">$2,800-4,200</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border);">
      <td style="padding:8px 10px;">Bootstrap Node Group</td>
      <td style="padding:8px 10px; color:var(--text-muted);">t3.medium x2 regions</td>
      <td style="padding:8px 10px; text-align:right;">$240</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);">
      <td rowspan="4" style="padding:8px 10px; vertical-align:top; font-weight:600; color:var(--cyan);">Database</td>
      <td style="padding:8px 10px;">Aurora DSQL</td>
      <td style="padding:8px 10px; color:var(--text-muted);">us-east-1 only (serverless)</td>
      <td style="padding:8px 10px; text-align:right;">$200-500</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border);">
      <td style="padding:8px 10px;">DocumentDB</td>
      <td style="padding:8px 10px; color:var(--text-muted);">r6g.large x4 (Global)</td>
      <td style="padding:8px 10px; text-align:right;">$1,480</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);">
      <td style="padding:8px 10px;">ElastiCache</td>
      <td style="padding:8px 10px; color:var(--text-muted);">r6g.large x4 (Valkey)</td>
      <td style="padding:8px 10px; text-align:right;">$880</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border);">
      <td style="padding:8px 10px;">OpenSearch</td>
      <td style="padding:8px 10px; color:var(--text-muted);">r6g.large x4 + master x3</td>
      <td style="padding:8px 10px; text-align:right;">$1,560</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);">
      <td style="padding:8px 10px; font-weight:600; color:#fdcb6e;">Messaging</td>
      <td style="padding:8px 10px;">MSK</td>
      <td style="padding:8px 10px; color:var(--text-muted);">kafka.m5.large x3 x2 regions</td>
      <td style="padding:8px 10px; text-align:right;">$1,620</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border);">
      <td rowspan="3" style="padding:8px 10px; vertical-align:top; font-weight:600; color:var(--green);">Network</td>
      <td style="padding:8px 10px;">NAT Gateway</td>
      <td style="padding:8px 10px; color:var(--text-muted);">x4 (2 per region)</td>
      <td style="padding:8px 10px; text-align:right;">$270</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);">
      <td style="padding:8px 10px;">Transit Gateway</td>
      <td style="padding:8px 10px; color:var(--text-muted);">x2 regions + attachments</td>
      <td style="padding:8px 10px; text-align:right;">$146</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border);">
      <td style="padding:8px 10px;">NLB</td>
      <td style="padding:8px 10px; color:var(--text-muted);">x2 regions</td>
      <td style="padding:8px 10px; text-align:right;">$36+</td>
    </tr>
  </tbody>
</table>
</div>
:::

:::notes
{timing: 2min}
서비스별 상세 비용입니다.

Compute 섹션을 보면, EKS Control Plane은 리전당 $73로 고정입니다. Karpenter EC2가 가장 변동폭이 큰데, 트래픽에 따라 $2,800에서 $4,200까지 갑니다. Bootstrap Node Group은 시스템 Pod용으로 t3.medium을 쓰는데 월 $240입니다.

Database 섹션에서 DocumentDB가 $1,480으로 가장 큽니다. r6g.large 4개인데, primary 2개와 replica 2개입니다. OpenSearch도 $1,560으로 비슷한데, dedicated master 3개가 포함되어 있습니다.

{cue: pause}
MSK가 $1,620입니다. kafka.m5.large 브로커 3개씩 두 리전이니까요. 이건 provisioned 모드라서 트래픽이 적어도 비용이 나갑니다.

Network에서 NAT Gateway가 $270입니다. 시간당 요금 + 데이터 처리 요금이 합쳐진 건데, 이게 의외로 큽니다.

{cue: transition}
이 비용을 어디서 줄일 수 있는지 보겠습니다.
:::

---
<!-- Slide 9: Cost Optimization Opportunities -->
@type: content

## Cost Optimization Opportunities

:::html
<table class="data-table" style="width:100%; font-size:0.85rem; border-collapse:collapse;">
  <thead>
    <tr style="background:var(--bg-card); border-bottom:2px solid var(--border);">
      <th style="padding:10px 12px; text-align:left; color:var(--text-muted);">Optimization</th>
      <th style="padding:10px 12px; text-align:center; color:var(--text-muted);">Savings</th>
      <th style="padding:10px 12px; text-align:center; color:var(--text-muted);">Effort</th>
      <th style="padding:10px 12px; text-align:left; color:var(--text-muted);">Notes</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom:1px solid var(--border);" data-fragment-index="1">
      <td style="padding:10px 12px;"><strong>Karpenter Spot Expansion</strong></td>
      <td style="padding:10px 12px; text-align:center; color:var(--green); font-weight:600;">30-40% EC2</td>
      <td style="padding:10px 12px; text-align:center;"><span style="color:var(--green);">L</span></td>
      <td style="padding:10px 12px; font-size:0.8rem;">worker-tier, batch-tier NodePool에 Spot 우선 설정</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);" data-fragment-index="1">
      <td style="padding:10px 12px;"><strong>DocumentDB Downsize</strong></td>
      <td style="padding:10px 12px; text-align:center; color:var(--green); font-weight:600;">$370/mo</td>
      <td style="padding:10px 12px; text-align:center;"><span style="color:var(--green);">L</span></td>
      <td style="padding:10px 12px; font-size:0.8rem;">r6g.large → r6g.medium (현재 CPU &lt;20%)</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border);" data-fragment-index="2">
      <td style="padding:10px 12px;"><strong>MSK Serverless</strong></td>
      <td style="padding:10px 12px; text-align:center; color:var(--green); font-weight:600;">50-70%</td>
      <td style="padding:10px 12px; text-align:center;"><span style="color:#fdcb6e;">M</span></td>
      <td style="padding:10px 12px; font-size:0.8rem;">저트래픽 시 유리 (현재 provisioned 유휴)</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);" data-fragment-index="2">
      <td style="padding:10px 12px;"><strong>OpenSearch Scale-down</strong></td>
      <td style="padding:10px 12px; text-align:center; color:var(--green); font-weight:600;">$520/mo</td>
      <td style="padding:10px 12px; text-align:center;"><span style="color:var(--green);">L</span></td>
      <td style="padding:10px 12px; font-size:0.8rem;">dedicated master 제거 (현재 search 미사용)</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border);" data-fragment-index="3">
      <td style="padding:10px 12px;"><strong>Reserved Instances 1yr</strong></td>
      <td style="padding:10px 12px; text-align:center; color:var(--green); font-weight:600;">30-40% DB</td>
      <td style="padding:10px 12px; text-align:center;"><span style="color:var(--green);">L</span></td>
      <td style="padding:10px 12px; font-size:0.8rem;">DocumentDB, ElastiCache, OpenSearch</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);" data-fragment-index="3">
      <td style="padding:10px 12px;"><strong>NAT → NAT Instance</strong></td>
      <td style="padding:10px 12px; text-align:center; color:var(--green); font-weight:600;">$200/mo</td>
      <td style="padding:10px 12px; text-align:center;"><span style="color:#fdcb6e;">M</span></td>
      <td style="padding:10px 12px; font-size:0.8rem;">t4g.micro + ASG (HA 구성)</td>
    </tr>
  </tbody>
</table>
<div style="margin-top:12px; padding:12px 16px; background:rgba(0,214,143,0.1); border:1px solid var(--green); border-radius:8px; text-align:center;">
  <strong style="color:var(--green);">Total Savings Potential: $2,500 - $3,500 / month</strong>
  <span style="color:var(--text-muted); margin-left:12px;">(25-35% reduction)</span>
</div>
:::

:::notes
{timing: 3min}
비용 최적화 기회입니다. 총 $2,500에서 $3,500 월 절감이 가능합니다.

가장 쉬운 건 Karpenter Spot 확장입니다. 현재 critical-tier만 On-Demand를 쓰고 있는데, worker-tier와 batch-tier NodePool에 Spot 인스턴스 우선 설정을 추가하면 EC2 비용이 30-40% 줄어듭니다. Effort가 Low라서 바로 할 수 있습니다.

DocumentDB는 현재 CPU 사용률이 20% 미만인데 r6g.large를 쓰고 있습니다. r6g.medium으로 내리면 월 $370 절약됩니다. 이것도 Low effort입니다.

{cue: pause}
MSK Serverless는 medium effort지만 효과가 큽니다. 현재 provisioned 클러스터가 유휴 상태일 때도 비용이 나가는데, Serverless로 바꾸면 실제 사용량만 과금됩니다. 트래픽이 적을 때 50-70% 절감이 가능합니다.

OpenSearch는 dedicated master 3개가 있는데, 현재 search 서비스가 실제로 OpenSearch를 안 쓰고 있어서 dedicated master를 제거하면 월 $520 절약됩니다.

Reserved Instances는 1년 약정으로 DocumentDB, ElastiCache, OpenSearch에 적용하면 30-40% 할인됩니다. NAT Gateway를 NAT Instance로 바꾸면 월 $200 정도 절약되는데, t4g.micro + ASG로 HA 구성이 가능합니다.

{cue: transition}
다음으로 성능 병목점을 보겠습니다.
:::

---
<!-- Slide 10: Performance Bottlenecks -->
@type: content

## Performance Bottlenecks

:::html
<div class="col-2" style="gap:1rem;">
  <div>
    <h4 style="margin:0 0 0.75rem 0; color:var(--red);">P0 — Critical Bugs</h4>
    <div class="card" style="padding:12px; margin-bottom:8px; border-left:3px solid var(--red);">
      <div style="font-weight:600; margin-bottom:4px;">1. Python Valkey MOVED error</div>
      <div style="font-size:0.82rem; color:var(--text-muted);">Redis() → RedisCluster() 필요</div>
      <div style="font-size:0.78rem; color:var(--text-secondary); margin-top:4px;">영향: 7개 Python 서비스</div>
    </div>
    <div class="card" style="padding:12px; margin-bottom:8px; border-left:3px solid var(--red);">
      <div style="font-weight:600; margin-bottom:4px;">2. DSQL connection pool default</div>
      <div style="font-size:0.82rem; color:var(--text-muted);">기본값 4/CPU → exhaustion 발생</div>
      <div style="font-size:0.78rem; color:var(--text-secondary); margin-top:4px;">영향: 6개 Go 서비스</div>
    </div>
    <div class="card" style="padding:12px; border-left:3px solid var(--red);">
      <div style="font-weight:600; margin-bottom:4px;">3. DocumentDB Motor maxPoolSize</div>
      <div style="font-size:0.82rem; color:var(--text-muted);">default 100 → Pod scale 시 초과</div>
      <div style="font-size:0.78rem; color:var(--text-secondary); margin-top:4px;">영향: 7개 Python 서비스</div>
    </div>
  </div>
  <div>
    <h4 style="margin:0 0 0.75rem 0; color:#fdcb6e;">P1 — Improvements</h4>
    <div class="card" style="padding:12px; margin-bottom:8px; border-left:3px solid #fdcb6e;">
      <div style="font-weight:600; margin-bottom:4px;">4. API GW MaxIdleConnsPerHost = 2</div>
      <div style="font-size:0.82rem; color:var(--text-muted);">Backend 연결 병목 → 100으로 상향</div>
    </div>
    <div class="card" style="padding:12px; margin-bottom:8px; border-left:3px solid #fdcb6e;">
      <div style="font-weight:600; margin-bottom:4px;">5. Java SimpleClientHttpRequestFactory</div>
      <div style="font-size:0.82rem; color:var(--text-muted);">Connection pooling 없음 → RestTemplate + pooling</div>
    </div>
    <h4 style="margin:0.75rem 0 0.5rem 0; color:var(--green);">Quick Wins</h4>
    <div class="card" style="padding:12px; border-left:3px solid var(--green);">
      <div style="font-size:0.85rem;">
        <strong>Product cache TTL 5min</strong> → DocDB 부하 감소<br>
        <strong>CloudFront API cache 1min</strong> → Origin 요청 50%↓
      </div>
    </div>
  </div>
</div>
:::

:::notes
{timing: 3min}
성능 병목점입니다. P0 Critical bug 3개와 P1 Improvement 2개가 있습니다.

P0 첫째, Python Valkey 연결입니다. 현재 Redis() 클라이언트를 쓰는데, Valkey는 클러스터 모드라서 MOVED 리다이렉션 에러가 납니다. RedisCluster()로 바꿔야 합니다. 7개 Python 서비스가 영향받습니다.

둘째, DSQL connection pool입니다. Go의 database/sql 기본값이 CPU당 4개인데, 고부하 시 connection exhaustion이 발생합니다. SetMaxOpenConns, SetMaxIdleConns를 명시적으로 설정해야 합니다. 6개 Go 서비스가 해당됩니다.

셋째, DocumentDB Motor입니다. Python Motor 드라이버의 maxPoolSize 기본값이 100인데, Pod이 10개로 scale되면 1000개 연결이 열리고 DocumentDB의 max_connections를 초과합니다.

{cue: pause}
P1으로 api-gateway의 MaxIdleConnsPerHost가 2입니다. 백엔드 20개 서비스에 각각 2개씩만 연결을 유지하니까 병목이 됩니다. 100으로 올려야 합니다.

Java 서비스들은 SimpleClientHttpRequestFactory를 쓰는데 connection pooling이 없습니다. Apache HttpClient로 바꾸고 pooling을 적용해야 합니다.

Quick Win으로 product-catalog에 5분 TTL 캐시를 넣으면 DocumentDB 부하가 크게 줄고, CloudFront에서 GET /products/* 경로에 1분 캐시를 설정하면 Origin 요청이 50% 이상 줄어듭니다.

{cue: transition}
이 성능 문제를 검증하기 위한 Load Test 전략을 보겠습니다.
:::

---
<!-- Slide 11: Load Test Strategy (k6) -->
@type: tabs

## Load Test Strategy (k6)

### Baseline

```javascript
// Profile 1: Baseline (100 VUs, 10min)
// 현재 상태의 기준선 측정
export const options = {
  vus: 100,
  duration: '10m',
  thresholds: {
    http_req_duration: ['p95<500'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function() {
  // 60% Browse, 15% Purchase, 20% Search, 5% Seller
  const scenario = weightedRandom([
    { weight: 60, fn: browseProducts },
    { weight: 15, fn: purchaseFlow },
    { weight: 20, fn: searchProducts },
    { weight: 5, fn: sellerDashboard },
  ]);
  scenario();
}
```

### Ramp-up

```javascript
// Profile 2: Ramp-up (100→1000 VUs, 30min)
// 점진적 부하 증가로 breaking point 탐색
export const options = {
  stages: [
    { duration: '5m', target: 100 },
    { duration: '10m', target: 500 },
    { duration: '10m', target: 1000 },
    { duration: '5m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p95<500', 'p99<1000'],
  },
};
```

### Spike

```javascript
// Profile 4: Spike (500→2000→500 VUs, 15min)
// 급격한 부하 증가 시 auto-scaling 반응 테스트
export const options = {
  stages: [
    { duration: '2m', target: 500 },
    { duration: '1m', target: 2000 },  // spike
    { duration: '5m', target: 2000 },  // sustain
    { duration: '2m', target: 500 },   // recovery
    { duration: '5m', target: 500 },
  ],
};

// Karpenter scaling 반응 시간 측정
// 목표: 2분 내 노드 프로비저닝
```

### Soak

```javascript
// Profile 5: Soak Test (300 VUs, 4hr)
// 메모리 누수, 연결 누수 탐지
export const options = {
  vus: 300,
  duration: '4h',
  thresholds: {
    http_req_duration: ['p95<300'],
    http_req_failed: ['rate<0.001'],
  },
};

// 모니터링 항목:
// - Pod memory usage trend
// - DB connection count
// - Goroutine/Thread count
// - File descriptor usage
```

:::notes
{timing: 3min}
k6 Load Test 프로필 4가지입니다. Kubernetes Operator로 클러스터 안에서 실행하고, 결과는 Prometheus로 보냅니다.

첫 번째 Baseline입니다. 100 VU로 10분간 현재 상태의 기준선을 측정합니다. 시나리오 비중은 Browse 60%, Purchase 15%, Search 20%, Seller 5%입니다. p95 500ms 미만, 에러율 1% 미만이 threshold입니다.

두 번째 Ramp-up입니다. 100에서 1000 VU까지 30분간 점진적으로 올립니다. 어느 지점에서 latency가 급격히 증가하는지, breaking point를 찾는 테스트입니다.

{cue: pause}
세 번째 Spike입니다. 500 VU에서 갑자기 2000으로 올렸다가 다시 내립니다. Karpenter가 얼마나 빨리 노드를 프로비저닝하는지, auto-scaling 반응 시간을 측정합니다. 목표는 2분 내 노드 프로비저닝입니다.

네 번째 Soak입니다. 300 VU로 4시간 동안 지속합니다. 메모리 누수, DB 연결 누수, Goroutine 증가 같은 장기 실행 시에만 나타나는 문제를 탐지합니다.

{cue: transition}
Target 메트릭과 SLO를 정리하겠습니다.
:::

---
<!-- Slide 12: Target Metrics (SLOs) -->
@type: content

## Target Metrics (SLOs)

:::html
<div class="col-2" style="gap:1.5rem;">
  <div>
    <h4 style="margin:0 0 0.75rem 0; color:var(--accent);">Latency SLOs</h4>
    <table class="data-table" style="width:100%; font-size:0.9rem;">
      <thead>
        <tr style="background:var(--bg-card);">
          <th style="padding:10px; text-align:left;">Percentile</th>
          <th style="padding:10px; text-align:right;">Target</th>
          <th style="padding:10px; text-align:center;">Status</th>
        </tr>
      </thead>
      <tbody>
        <tr style="border-bottom:1px solid var(--border);">
          <td style="padding:10px;">p50</td>
          <td style="padding:10px; text-align:right; font-weight:600;">< 100ms</td>
          <td style="padding:10px; text-align:center;"><span style="color:var(--green);">TBD</span></td>
        </tr>
        <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);">
          <td style="padding:10px;">p95</td>
          <td style="padding:10px; text-align:right; font-weight:600;">< 300ms</td>
          <td style="padding:10px; text-align:center;"><span style="color:var(--green);">TBD</span></td>
        </tr>
        <tr>
          <td style="padding:10px;">p99</td>
          <td style="padding:10px; text-align:right; font-weight:600;">< 500ms</td>
          <td style="padding:10px; text-align:center;"><span style="color:var(--green);">TBD</span></td>
        </tr>
      </tbody>
    </table>
    <h4 style="margin:1rem 0 0.75rem 0; color:var(--cyan);">Throughput & Availability</h4>
    <div class="card" style="padding:1rem;">
      <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
        <span>Sustained Throughput</span>
        <strong style="color:var(--cyan);">5,000 RPS</strong>
      </div>
      <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
        <span>Error Rate</span>
        <strong style="color:var(--green);">< 0.1%</strong>
      </div>
      <div style="display:flex; justify-content:space-between;">
        <span>Availability</span>
        <strong style="color:var(--accent);">99.9%</strong>
      </div>
    </div>
  </div>
  <div>
    <h4 style="margin:0 0 0.75rem 0; color:#fdcb6e;">Per-Endpoint Targets</h4>
    <table class="data-table" style="width:100%; font-size:0.85rem;">
      <thead>
        <tr style="background:var(--bg-card);">
          <th style="padding:8px; text-align:left;">Endpoint</th>
          <th style="padding:8px; text-align:right;">p95</th>
        </tr>
      </thead>
      <tbody>
        <tr style="border-bottom:1px solid var(--border);">
          <td style="padding:8px;">GET /products</td>
          <td style="padding:8px; text-align:right;">< 200ms</td>
        </tr>
        <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);">
          <td style="padding:8px;">GET /products/:id</td>
          <td style="padding:8px; text-align:right;">< 150ms</td>
        </tr>
        <tr style="border-bottom:1px solid var(--border);">
          <td style="padding:8px;">POST /orders</td>
          <td style="padding:8px; text-align:right;">< 500ms</td>
        </tr>
        <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);">
          <td style="padding:8px;">POST /payments</td>
          <td style="padding:8px; text-align:right;">< 500ms</td>
        </tr>
        <tr style="border-bottom:1px solid var(--border);">
          <td style="padding:8px;">GET /search</td>
          <td style="padding:8px; text-align:right;">< 300ms</td>
        </tr>
        <tr style="background:var(--bg-card);">
          <td style="padding:8px;">GET /seller/dashboard</td>
          <td style="padding:8px; text-align:right;">< 400ms</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
:::

:::notes
{timing: 2min}
SLO 타겟 메트릭입니다.

Latency SLO는 세 가지 퍼센타일로 정의했습니다. p50은 100ms 미만, p95는 300ms 미만, p99는 500ms 미만입니다. p50이 빠르면 대부분의 사용자 경험이 좋고, p99가 통제되면 최악의 경우도 관리 가능합니다.

Throughput은 5,000 RPS를 sustained로 버텨야 합니다. 피크 시간대 예상 트래픽의 2배 정도를 여유분으로 잡은 겁니다. Error Rate은 0.1% 미만, Availability는 99.9%입니다.

{cue: pause}
오른쪽은 엔드포인트별 세부 타겟입니다. 읽기 위주인 /products는 200ms 미만, 상품 상세는 150ms 미만으로 빨라야 합니다. 쓰기 작업인 /orders와 /payments는 트랜잭션이 포함되니까 500ms까지 허용합니다. Search는 300ms, Seller Dashboard는 400ms입니다.

이 타겟들을 Load Test에서 threshold로 설정하고, 통과 여부로 릴리즈 판단을 합니다.

{cue: transition}
Production Readiness를 위한 Gap Analysis를 보겠습니다.
:::

---
<!-- Slide 13: Gap Analysis Summary -->
@type: content

## Gap Analysis Summary

:::html
<div class="flow-h" style="flex-wrap:wrap; gap:0.75rem; justify-content:center;">
  <div class="flow-group" style="border:2px solid var(--red); background:rgba(255,107,107,0.08); min-width:260px; max-width:300px;" data-fragment-index="1">
    <div class="flow-group-label" style="color:var(--red);">P0 — Production Blockers</div>
    <div class="flow-v" style="gap:0.4rem; padding:0.4rem;">
      <div class="flow-box" style="display:flex; align-items:center; gap:6px; font-size:0.85rem;">
        <img src="common/aws-icons/services/Arch_Amazon-Cognito_48.svg" style="width:28px;">
        <div>
          <strong>Authentication</strong>
          <div style="font-size:0.75rem; color:var(--text-muted);">인증 미들웨어 없음</div>
        </div>
      </div>
      <div class="flow-box" style="display:flex; align-items:center; gap:6px; font-size:0.85rem;">
        <img src="common/aws-icons/services/Arch_Amazon-MSK_48.svg" style="width:28px;">
        <div>
          <strong>Event Bus → MSK</strong>
          <div style="font-size:0.75rem; color:var(--text-muted);">Mock publish only</div>
        </div>
      </div>
    </div>
  </div>
  <div class="flow-group" style="border:2px solid #fdcb6e; background:rgba(253,203,110,0.08); min-width:260px; max-width:300px;" data-fragment-index="2">
    <div class="flow-group-label" style="color:#fdcb6e;">P1 — High Risk</div>
    <div class="flow-v" style="gap:0.4rem; padding:0.4rem;">
      <div class="flow-box" style="display:flex; align-items:center; gap:6px; font-size:0.85rem;">
        <img src="common/aws-icons/services/Arch_AWS-WAF_48.svg" style="width:28px;">
        <div>
          <strong>WAF Reactivation</strong>
          <div style="font-size:0.75rem; color:var(--text-muted);">Bot Control 차단 중</div>
        </div>
      </div>
      <div class="flow-box" style="display:flex; align-items:center; gap:6px; font-size:0.85rem;">
        <img src="common/aws-icons/services/Arch_Amazon-OpenSearch-Service_48.svg" style="width:28px;">
        <div>
          <strong>Search → OpenSearch</strong>
          <div style="font-size:0.75rem; color:var(--text-muted);">strings.Contains mock</div>
        </div>
      </div>
      <div class="flow-box" style="display:flex; align-items:center; gap:6px; font-size:0.85rem;">
        <img src="common/aws-icons/services/Arch_Amazon-Aurora_48.svg" style="width:28px;">
        <div>
          <strong>DSQL Multi-Region</strong>
          <div style="font-size:0.75rem; color:var(--text-muted);">us-east-1 only</div>
        </div>
      </div>
    </div>
  </div>
  <div class="flow-group" style="border:2px solid var(--accent); background:rgba(108,92,231,0.08); min-width:260px; max-width:300px;" data-fragment-index="3">
    <div class="flow-group-label" style="color:var(--accent);">P2 — Improvements</div>
    <div class="flow-v" style="gap:0.4rem; padding:0.4rem;">
      <div class="flow-box" style="display:flex; align-items:center; gap:6px; font-size:0.85rem;">
        <img src="common/aws-icons/services/Arch_Amazon-MSK_48.svg" style="width:28px;">
        <div>
          <strong>MSK Replicator</strong>
          <div style="font-size:0.75rem; color:var(--text-muted);">Cross-region sync</div>
        </div>
      </div>
      <div class="flow-box" style="display:flex; align-items:center; gap:6px; font-size:0.85rem;">
        <img src="common/aws-icons/services/Arch_AWS-CodePipeline_48.svg" style="width:28px;">
        <div>
          <strong>CI/CD Automation</strong>
          <div style="font-size:0.75rem; color:var(--text-muted);">Manual deploys 상태</div>
        </div>
      </div>
    </div>
  </div>
</div>
<p style="margin-top:12px; font-size:0.85rem; color:var(--text-muted); text-align:center;">
  총 <strong>7개 Gap</strong> | P0 해결 없이는 Production 불가
</p>
:::

:::notes
{timing: 2min}
Gap Analysis 요약입니다. 총 7개 Gap이 있고, 우선순위별로 분류했습니다.

P0, Production Blocker가 두 개입니다. 첫째 Authentication이 아예 없습니다. api-gateway에 인증 미들웨어가 없고, 누구나 API를 호출할 수 있는 상태입니다. 둘째 event-bus 서비스가 MSK에 실제로 publish하지 않습니다. 7개 consumer 서비스가 이벤트를 못 받고 있습니다.

{cue: pause}
P1은 운영 리스크입니다. WAF Bot Control이 curl과 headless browser를 차단해서 모니터링 체크가 실패합니다. Search 서비스는 strings.Contains()로 mock 검색을 하고 있고요. DSQL이 us-east-1에만 있어서 진정한 Multi-Region이 아닙니다.

P2는 개선사항입니다. MSK Replicator로 Cross-region sync를 구성해야 하고, CI/CD가 수동 상태입니다.

P0 두 개가 해결되기 전까지는 Production 런칭이 불가능합니다.

{cue: transition}
이 Gap들을 해결하기 위한 로드맵을 보겠습니다.
:::

---
<!-- Slide 14: Production Readiness Roadmap -->
@type: timeline

## Production Readiness Roadmap

### Phase 1 (2주)
P0 Gaps 해결
Authentication + Event Bus MSK 연동

### Phase 2 (4주)
P1 Gaps + Performance
WAF 재설정, Search→OpenSearch, DSQL Multi-Region
성능 버그 수정 (Valkey, Pool)

### Phase 3 (2주)
P2 Gaps + DR
MSK Replicator, CI/CD Pipeline
DR 자동화 (EventBridge + Lambda)

### Phase 4 (ongoing)
Load Test + Optimization
k6 전체 프로필 실행
비용 최적화 적용

:::notes
{timing: 2min}
Production Readiness 로드맵을 4개 Phase로 정리했습니다.

Phase 1은 2주입니다. P0 Gap인 Authentication과 Event Bus MSK 연동을 해결합니다. Authentication이 가장 크고 복잡한데, Cognito User Pool 설정, JWT 미들웨어 구현, 각 서비스 integration 테스트까지 2주가 빠듯합니다. Event Bus는 병렬로 진행하면 됩니다.

Phase 2는 4주입니다. P1 Gap들과 성능 버그를 수정합니다. WAF scope-down rule 설정, Search 서비스의 OpenSearch 연동, DSQL Linked Clusters 구성이 여기에 들어갑니다. 동시에 Valkey ClusterClient, DSQL pool 설정, Motor maxPoolSize 같은 성능 버그도 수정합니다.

{cue: pause}
Phase 3는 2주입니다. P2 Gap인 MSK Replicator와 CI/CD Pipeline을 구축합니다. DR 자동화도 여기서 합니다. EventBridge가 CloudWatch Alarm을 받아서 Lambda로 DocumentDB/ElastiCache promote를 자동화하는 거죠.

Phase 4는 ongoing입니다. k6 Load Test 전체 프로필을 실행하고, 결과에 따라 튜닝합니다. 비용 최적화도 이 시점에 적용합니다. Spot 확장, DB downsize, RI 계약 같은 것들이요.

{cue: transition}
전체 내용을 정리하겠습니다.
:::

---
<!-- Slide 15: Key Takeaways -->
@type: content

## Key Takeaways

:::html
<div class="col-2" style="gap:1.5rem; margin-bottom:1rem;">
  <div class="card" style="padding:1rem; border-left:3px solid var(--accent);">
    <h4 style="margin:0 0 0.5rem 0; color:var(--accent);">Observability Stack</h4>
    <ul style="margin:0; padding-left:1.2rem; font-size:0.9rem;">
      <li>OTel Collector + Tail Sampling</li>
      <li>Storage 90% 절감, 에러 100% 보존</li>
      <li>Tempo + X-Ray dual export</li>
      <li>Logs-to-Traces correlation</li>
    </ul>
  </div>
  <div class="card" style="padding:1rem; border-left:3px solid var(--cyan);">
    <h4 style="margin:0 0 0.5rem 0; color:var(--cyan);">Cost Optimization</h4>
    <ul style="margin:0; padding-left:1.2rem; font-size:0.9rem;">
      <li>월 $9,600-12,400 총 비용</li>
      <li>$2,500-3,500 절감 가능 (25-35%)</li>
      <li>Quick wins: Spot, DB downsize</li>
      <li>Medium-term: MSK Serverless, RI</li>
    </ul>
  </div>
  <div class="card" style="padding:1rem; border-left:3px solid var(--red);">
    <h4 style="margin:0 0 0.5rem 0; color:var(--red);">Production Blockers</h4>
    <ul style="margin:0; padding-left:1.2rem; font-size:0.9rem;">
      <li>P0: Authentication, Event Bus</li>
      <li>P1: WAF, Search, DSQL Multi-Region</li>
      <li>P0 해결 없이 Production 불가</li>
      <li>8주 로드맵으로 해결</li>
    </ul>
  </div>
  <div class="card" style="padding:1rem; border-left:3px solid var(--green);">
    <h4 style="margin:0 0 0.5rem 0; color:var(--green);">Performance & Testing</h4>
    <ul style="margin:0; padding-left:1.2rem; font-size:0.9rem;">
      <li>P0 bugs: Valkey, DSQL pool, Motor</li>
      <li>SLO: p95 &lt;300ms, 5K RPS</li>
      <li>k6 4가지 프로필로 검증</li>
      <li>Soak test로 누수 탐지</li>
    </ul>
  </div>
</div>
<div style="text-align:center;">
  <div class="flow-h" style="justify-content:center; gap:0.5rem; flex-wrap:wrap;">
    <span style="background:var(--red); color:#fff; padding:6px 12px; border-radius:4px; font-size:0.85rem;">1. P0 Gaps</span>
    <span style="color:var(--text-muted);">→</span>
    <span style="background:#fdcb6e; color:#1a1f35; padding:6px 12px; border-radius:4px; font-size:0.85rem;">2. Performance Fix</span>
    <span style="color:var(--text-muted);">→</span>
    <span style="background:var(--accent); color:#fff; padding:6px 12px; border-radius:4px; font-size:0.85rem;">3. Load Test</span>
    <span style="color:var(--text-muted);">→</span>
    <span style="background:var(--green); color:#fff; padding:6px 12px; border-radius:4px; font-size:0.85rem;">4. Cost Optimize</span>
  </div>
</div>
:::

:::notes
{timing: 2min}
전체 내용을 네 가지로 정리하겠습니다.

첫째, Observability입니다. OTel Collector와 Tail-Based Sampling으로 저장 비용 90%를 절감하면서 에러와 지연 트레이스는 100% 보존합니다. Tempo와 X-Ray 둘 다로 export해서 장기 저장과 AWS 통합을 모두 확보합니다.

둘째, Cost입니다. 월 $9,600-12,400 비용 중 $2,500-3,500를 절감할 수 있습니다. Spot 확장과 DB downsize는 바로 할 수 있는 quick win이고, MSK Serverless와 RI는 중기적으로 적용합니다.

{cue: pause}
셋째, Production Blockers입니다. Authentication과 Event Bus가 P0입니다. 이것 없이는 Production 런칭 불가능합니다. 8주 로드맵으로 P0부터 P2까지 순차 해결합니다.

넷째, Performance입니다. Valkey, DSQL pool, Motor 세 가지 P0 bug를 수정하고, k6로 SLO를 검증합니다. Soak test로 장기 실행 시 누수도 탐지합니다.

권장 순서는 P0 Gap 먼저, Performance Fix, Load Test, 마지막에 Cost Optimize입니다.

{cue: transition}
이제 마지막 퀴즈로 이 블록을 마무리하겠습니다.
:::

---
<!-- Slide 16: Quiz -->
@type: quiz

## Knowledge Check

**Q1: Tail-Based Sampling의 핵심 장점은?**
- [ ] 트레이스 시작 시 빠른 결정
- [x] 에러/지연 확인 후 선택적 저장으로 중요 데이터 100% 보존
- [ ] 모든 트레이스 저장
- [ ] CPU 사용량 감소

**Q2: OTel Collector에서 tail_sampling의 decision_wait 역할은?**
- [ ] 샘플링 비율 결정
- [ ] 메모리 제한 설정
- [x] 트레이스의 모든 span을 모으기 위한 대기 시간
- [ ] 배치 크기 설정

**Q3: 비용 최적화에서 가장 빠르게 적용할 수 있는 항목은?**
- [x] Karpenter Spot 확장, DocumentDB downsize
- [ ] MSK Serverless 전환
- [ ] Reserved Instances 1년 계약
- [ ] NAT Instance 전환

**Q4: Production Blocker (P0) Gap에 해당하는 것은?**
- [ ] WAF Bot Control 설정
- [ ] MSK Replicator 구성
- [x] Authentication 미들웨어 없음
- [ ] CI/CD Pipeline 자동화

:::notes
{timing: 3min}
마지막 퀴즈입니다. 4문제를 풀어보시죠.

Q1은 Tail-Based Sampling의 핵심 장점입니다. 정답은 B, "에러/지연 확인 후 선택적 저장으로 중요 데이터 100% 보존"입니다. Head Sampling은 시작 시 결정하니까 에러 발생 전에 버려질 수 있지만, Tail은 다 보고 결정합니다.

Q2는 decision_wait의 역할입니다. 정답은 C, 트레이스의 모든 span을 모으기 위한 대기 시간입니다. 분산 시스템에서 span이 여러 서비스에서 비동기로 도착하니까, 전체를 모을 때까지 기다려야 에러 여부를 판단할 수 있습니다.

Q3은 가장 빠른 비용 최적화입니다. 정답은 A, Karpenter Spot 확장과 DocumentDB downsize입니다. 둘 다 Effort가 Low이고, 설정 변경만으로 바로 적용됩니다.

Q4는 P0 Gap입니다. 정답은 C, Authentication 미들웨어 없음입니다. 이것 없이는 누구나 API를 호출할 수 있어서 Production 런칭이 불가능합니다.
:::

---
<!-- Slide 17: Thank You -->
@type: thankyou

## Thank You

Block 5 — Observability & Operations 완료

Multi-Region Architecture Deep Dive 전체 완료!

수고하셨습니다!

[← 목차로 돌아가기](index.html)

:::notes
{timing: 1min}
수고하셨습니다. 이것으로 Multi-Region Architecture Deep Dive 전체 프레젠테이션을 마칩니다.

다섯 블록을 통해 Foundation, Data Sync, Traffic Routing, DR/Failover, 그리고 Observability & Operations까지 전체적으로 살펴봤습니다.

핵심 메시지를 다시 정리하면: Multi-Region 아키텍처는 단순히 리전을 두 개 쓰는 게 아니라, 데이터 일관성, 트래픽 라우팅, DR 자동화, Observability가 모두 갖춰져야 진정한 Active-Active가 됩니다.

질문이 있으시면 편하게 해주세요.
:::
