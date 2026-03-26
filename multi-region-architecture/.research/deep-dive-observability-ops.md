# Deep Research: Multi-Region Observability & Operations (L300+)

This report provides a technical deep-dive into the observability and operational strategies required for a resilient, cost-effective, and performant multi-region AWS architecture.

## 1. Cross-Region Observability Stack

A multi-region strategy requires a unified observability layer that provides global visibility while maintaining regional isolation for fault tolerance.

### OpenTelemetry (OTel) Collector Architecture

| Deployment Pattern | Usage | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **DaemonSet** | Node-level metrics/logs | Efficient resource usage per node. | Harder to scale for massive trace bursts. |
| **Sidecar** | App-level traces | Fine-grained control; low latency. | Higher overhead (RAM/CPU per Pod). |
| **Gateway** | Cross-region aggregation | Centralized sampling; TLS termination. | Single point of failure (needs HA). |

**Recommended Design:** 
- **Sidecar** for high-throughput trace ingestion at the app level.
- **Gateway (StatefulSet/HA)** for regional aggregation, tail-sampling, and dual exporting.

### Dual Export Pattern
We implement a "Best of Both Worlds" strategy:
1.  **Tempo (OTLP):** Vendor-neutral, high-scale tracing for deep debugging via TraceQL.
2.  **AWS X-Ray (AWS Exporter):** Native integration with AWS Service Map, CloudWatch, and Lambda.
3.  **Prometheus (Remote Write):** Multi-region metrics aggregation in Grafana.

### Cross-Region Trace Correlation
Linking traces across regions relies on the **W3C Trace Context** (`traceparent`, `tracestate`).
- **TraceID:** Must be propagated via HTTP headers (e.g., CloudFront `X-Amzn-Trace-Id` or OTel headers).
- **Correlation:** Service A in `us-east-1` calling Service B in `eu-west-1` will share the same `TraceID`, allowing Grafana Tempo to stitch them together.

### Service Map Generation
Tempo's `metrics_generator` processor automatically creates a service graph by analyzing span relationships (parent-child). This provides a real-time visualization of cross-region dependencies without manual instrumentation.

---

## 2. Tail-Based Sampling Strategy

Head-based sampling (sampling at the start) misses critical anomalies. Tail-based sampling (sampling at the end) ensures we capture what matters most.

### Why Tail-Based?
- **Head-based:** Randomly drops 90% of traces. We might miss the 1% of error traces.
- **Tail-based:** Buffer spans in the OTel Gateway, then decide whether to keep the *entire* trace based on its attributes (errors, latency).

### Policy Design
| Criterion | Sampling Rate | Logic |
| :--- | :---: | :--- |
| **Errors** | 100% | Keep any trace with `status.code == ERROR`. |
| **Slow Traces** | 100% | Keep traces where `duration > 500ms`. |
| **Health Checks** | 1% | Drop most noise from `/health` or `/metrics`. |
| **Default** | 10% | Probabilistic sampling for baseline performance. |

### OTel Collector Configuration (Gateway)
```yaml
processors:
  tail_sampling:
    decision_wait: 30s
    num_traces: 10000
    expected_new_traces_per_sec: 2000
    policies:
      [
        {
          name: errors-policy,
          type: status_code,
          status_code: {status_codes: [ERROR]}
        },
        {
          name: latency-policy,
          type: latency,
          latency: {threshold_ms: 500}
        },
        {
          name: probabilistic-policy,
          type: probabilistic,
          probabilistic: {sampling_percentage: 10}
        }
      ]
```

---

## 3. Grafana Tempo Integration

### Architecture: distributor → ingester → compactor → S3
1.  **Distributor:** Validates and routes spans.
2.  **Ingester:** Batches spans in memory and writes to S3.
3.  **Compactor:** Merges small files in S3 into larger blocks to optimize query performance.
4.  **S3 Backend:** Cost-effective, durable storage.

### S3 Lifecycle Policy
- **Standard:** 0–30 days (Hot storage for active debugging).
- **IA (Infrequent Access):** 31–90 days (Compliance/Post-mortems).
- **Glacier Deep Archive:** 91+ days (Historical records).

### TraceQL Examples
- Find slow spans in a specific region:
  `{ span.region = "us-east-1" && duration > 200ms }`
- Find all errors in a specific microservice:
  `{ resource.service.name = "auth-service" && status = error }`

### Grafana Dashboard: Multi-Region Overview (JSON Snippet)
This snippet defines a row with two panels: Global Request Rate and Regional Error Rate.

```json
{
  "panels": [
    {
      "title": "Global Request Rate (RPS)",
      "type": "timeseries",
      "targets": [
        {
          "expr": "sum(rate(http_requests_total[5m]))",
          "legendFormat": "Global"
        }
      ]
    },
    {
      "title": "Error Rate by Region",
      "type": "timeseries",
      "targets": [
        {
          "expr": "sum by (region) (rate(http_requests_total{status=~\"5..\"}[5m])) / sum by (region) (rate(http_requests_total[5m]))",
          "legendFormat": "{{region}}"
        }
      ]
    }
  ]
}
```

### Logs-to-Traces Correlation
Inject `traceID` into log patterns. In Grafana, click the TraceID in a log entry to jump directly to the Tempo trace view.

---

## 4. Cost Analysis & Optimization

### Multi-Region Infrastructure Cost Drivers
1.  **Compute:** EKS Control Plane + Worker Nodes.
2.  **Databases:** Aurora Global DB (Secondary instances + Replication).
3.  **Cross-Region Data Transfer (CRDT):** The "Silent Killer" ($0.02 per GB).
4.  **Observability Storage:** S3 (Traces/Logs) + EBS (Prometheus WAL).

### Multi-Region Infrastructure Cost Breakdown (Monthly Est. per Region)

| Component | Quantity | Unit Cost | Monthly Total |
| :--- | :--- | :--- | :--- |
| **EKS Control Plane** | 1 | $73/cluster | $73 |
| **m6g.large (2 vCPU, 8GB)** | 10 | $55.48/node (RI) | $554.80 |
| **Aurora Global (Secondary)** | 2 (db.r6g.large) | $175/instance | $350 |
| **MSK Cluster (Small)** | 3 nodes | $150/node | $450 |
| **NAT Gateway** | 2 | $32/mo + $0.045/GB | $100+ |
| **Cross-Region Transfer** | 1000 GB | $0.02/GB | $20 |

**Total Est. per Regional Cluster:** ~$1,547.80+ (Excluding Data Transfer volume).

### Optimization Strategies
- **Karpenter Consolidation:** Automatically terminates underutilized nodes and packs Pods onto fewer, more efficient instances (e.g., Graviton).
- **VPC Endpoints (PrivateLink):** Avoid NAT Gateway costs for AWS services (S3, ECR, CloudWatch).
- **S3 Gateway Endpoints:** Free (unlike Interface Endpoints) for S3 access within a region.
- **Spot Instances:** Use for non-critical workloads or CI/CD runners.

### Cost Calculation Example
*Scenario: 1TB data transfer per month from us-east-1 to eu-west-1.*
- **Standard Internet:** $0.09/GB = $90
- **Cross-Region Replication:** $0.02/GB = $20
- **Direct Connect / Transit Gateway:** Variable, but significantly lower for high volume.

---

## 5. Load Testing Strategy (k6)

### Multi-Region Test Profiles
1.  **Smoke:** Verify 1.0 RPS works (Baseline).
2.  **Load:** Test at expected peak (1000 RPS).
3.  **Stress:** Push until breaking point (e.g., 5000 RPS) to find bottlenecks.
4.  **Soak:** Long-duration test (24h) to find memory leaks or storage saturation.

### k6 Script Snippet
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '5m', target: 100 }, // ramp up
    { duration: '10m', target: 100 }, // stay at 100
    { duration: '5m', target: 0 },   // ramp down
  ],
  thresholds: {
    'http_req_duration': ['p(95)<300', 'p(99)<500'],
    'http_req_failed': ['rate<0.001'],
  },
};

export default function () {
  const regions = ['us-east-1', 'eu-west-1'];
  const region = regions[Math.floor(Math.random() * regions.length)];
  let res = http.get(`https://${region}.api.example.com/v1/health`);
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```

---

## 6. Gap Analysis & Production Readiness

### Priority Matrix (Effort vs. Impact)
| Task | Effort | Impact | Priority |
| :--- | :---: | :---: | :---: |
| Tail-Sampling Config | Med | High | **P0** |
| Cross-Region Tracing | High | High | **P0** |
| S3 Lifecycle Policies | Low | Med | **P1** |
| Karpenter Tuning | Med | Med | **P1** |

### Production Readiness Checklist
- [ ] OTel Collector HA (multiple replicas per region).
- [ ] SLO-based alerting (Error Budget).
- [ ] Multi-region Dashboard (Global vs Regional views).
- [ ] DR Failover runbooks tested via Chaos Engineering (AWS FIS).
- [ ] FinOps: Daily cost anomaly alerts via Cost Explorer.

### Roadmap
1.  **Phase 1 (Week 1-2):** Standardize OTel instrumentation + Head-based sampling.
2.  **Phase 2 (Week 3-4):** Deploy OTel Gateways + Tail-sampling + Tempo.
3.  **Phase 3 (Week 5-6):** Load testing + SLO refinement.
4.  **Phase 4 (Ongoing):** Cost optimization and FinOps integration.
