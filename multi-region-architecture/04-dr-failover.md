---
remarp: true
block: dr-failover
title: "DR & Failover Automation"
---

---
<!-- Slide 1: Cover -->
@type: cover

# DR & Failover Automation
Disaster Recovery 현황 분석과 자동화 전략 (30min)

:::notes
{timing: 1min}
Block 4에 오신 것을 환영합니다. 이번 블록에서는 Multi-Region Shopping Mall의 DR과 Failover Automation을 심층적으로 다루겠습니다.

지금까지 아키텍처 개요, 데이터/마이크로서비스, 운영 최적화를 다뤘습니다. 이번 블록에서는 실제 장애 상황에서 시스템이 어떻게 대응하는지, 그리고 어떻게 개선해야 하는지를 구체적으로 살펴봅니다.

30분 동안 DR 현황 분석, 장애 시나리오별 대응, 그리고 자동화 파이프라인 구축까지 다룰 예정입니다.

{cue: transition}
먼저 현재 DR 상태의 리스크 평가부터 시작하겠습니다.
:::

---
<!-- Slide 2: DR Current State - Risk Assessment -->
@type: content

## DR Current State — Risk Assessment

:::html
<div style="overflow-x:auto;">
<table class="data-table" style="width:100%; border-collapse:collapse; font-size:0.82rem;">
  <thead>
    <tr style="background:var(--bg-card); border-bottom:2px solid var(--border);">
      <th style="padding:10px 12px; text-align:left; color:var(--text-muted);">Component</th>
      <th style="padding:10px 12px; text-align:center; color:var(--text-muted);">DR Capability</th>
      <th style="padding:10px 12px; text-align:center; color:var(--text-muted);">Failover Type</th>
      <th style="padding:10px 12px; text-align:center; color:var(--text-muted);">Risk Level</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom:1px solid var(--border);" data-fragment-index="1">
      <td style="padding:10px 12px;"><img src="common/aws-icons/services/Arch_Amazon-Route-53_48.svg" style="width:24px; vertical-align:middle; margin-right:8px;">Traffic Routing</td>
      <td style="padding:10px 12px; text-align:center;"><span style="color:var(--green);">Auto failover</span></td>
      <td style="padding:10px 12px; text-align:center;"><span style="background:var(--green); color:#fff; padding:2px 8px; border-radius:4px; font-size:0.75rem;">Auto</span></td>
      <td style="padding:10px 12px; text-align:center;"><span style="background:rgba(0,214,143,0.15); color:var(--green); padding:4px 10px; border-radius:4px;">LOW</span></td>
    </tr>
    <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);" data-fragment-index="2">
      <td style="padding:10px 12px;"><img src="common/aws-icons/services/Arch_Amazon-Aurora_48.svg" style="width:24px; vertical-align:middle; margin-right:8px;">Aurora DSQL</td>
      <td style="padding:10px 12px; text-align:center; color:var(--red); font-weight:600;">NO DR (single region)</td>
      <td style="padding:10px 12px; text-align:center;"><span style="background:var(--red); color:#fff; padding:2px 8px; border-radius:4px; font-size:0.75rem;">None</span></td>
      <td style="padding:10px 12px; text-align:center;"><span style="background:rgba(255,107,107,0.15); color:var(--red); padding:4px 10px; border-radius:4px; font-weight:600;">CRITICAL</span></td>
    </tr>
    <tr style="border-bottom:1px solid var(--border);" data-fragment-index="3">
      <td style="padding:10px 12px;"><img src="common/aws-icons/services/Arch_Amazon-DocumentDB_48.svg" style="width:24px; vertical-align:middle; margin-right:8px;">DocumentDB</td>
      <td style="padding:10px 12px; text-align:center;">Global Cluster</td>
      <td style="padding:10px 12px; text-align:center;"><span style="background:#fdcb6e; color:#1a1f35; padding:2px 8px; border-radius:4px; font-size:0.75rem;">Manual CLI</span></td>
      <td style="padding:10px 12px; text-align:center;"><span style="background:rgba(253,203,110,0.15); color:#fdcb6e; padding:4px 10px; border-radius:4px;">HIGH</span></td>
    </tr>
    <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);" data-fragment-index="3">
      <td style="padding:10px 12px;"><img src="common/aws-icons/services/Arch_Amazon-ElastiCache_48.svg" style="width:24px; vertical-align:middle; margin-right:8px;">ElastiCache</td>
      <td style="padding:10px 12px; text-align:center;">Global Datastore</td>
      <td style="padding:10px 12px; text-align:center;"><span style="background:#fdcb6e; color:#1a1f35; padding:2px 8px; border-radius:4px; font-size:0.75rem;">Manual CLI</span></td>
      <td style="padding:10px 12px; text-align:center;"><span style="background:rgba(253,203,110,0.15); color:#fdcb6e; padding:4px 10px; border-radius:4px;">MEDIUM</span></td>
    </tr>
    <tr style="border-bottom:1px solid var(--border);" data-fragment-index="4">
      <td style="padding:10px 12px;"><img src="common/aws-icons/services/Arch_Amazon-MSK_48.svg" style="width:24px; vertical-align:middle; margin-right:8px;">MSK</td>
      <td style="padding:10px 12px; text-align:center; color:var(--red); font-weight:600;">NO DR (per-region)</td>
      <td style="padding:10px 12px; text-align:center;"><span style="background:var(--red); color:#fff; padding:2px 8px; border-radius:4px; font-size:0.75rem;">None</span></td>
      <td style="padding:10px 12px; text-align:center;"><span style="background:rgba(255,107,107,0.15); color:var(--red); padding:4px 10px; border-radius:4px; font-weight:600;">CRITICAL</span></td>
    </tr>
    <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);" data-fragment-index="5">
      <td style="padding:10px 12px;"><img src="common/aws-icons/services/Arch_Amazon-OpenSearch-Service_48.svg" style="width:24px; vertical-align:middle; margin-right:8px;">OpenSearch</td>
      <td style="padding:10px 12px; text-align:center;">Per-region (rebuild)</td>
      <td style="padding:10px 12px; text-align:center;"><span style="background:var(--red); color:#fff; padding:2px 8px; border-radius:4px; font-size:0.75rem;">Hours</span></td>
      <td style="padding:10px 12px; text-align:center;"><span style="background:rgba(253,203,110,0.15); color:#fdcb6e; padding:4px 10px; border-radius:4px;">HIGH</span></td>
    </tr>
    <tr style="border-bottom:1px solid var(--border);" data-fragment-index="6">
      <td style="padding:10px 12px;"><img src="common/aws-icons/services/Arch_Amazon-Simple-Storage-Service_48.svg" style="width:24px; vertical-align:middle; margin-right:8px;">S3</td>
      <td style="padding:10px 12px; text-align:center;">Cross-Region Replication</td>
      <td style="padding:10px 12px; text-align:center;"><span style="background:var(--green); color:#fff; padding:2px 8px; border-radius:4px; font-size:0.75rem;">Auto CRR</span></td>
      <td style="padding:10px 12px; text-align:center;"><span style="background:rgba(0,214,143,0.15); color:var(--green); padding:4px 10px; border-radius:4px;">LOW</span></td>
    </tr>
    <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);" data-fragment-index="6">
      <td style="padding:10px 12px;"><img src="common/aws-icons/services/Arch_Amazon-Elastic-Kubernetes-Service_48.svg" style="width:24px; vertical-align:middle; margin-right:8px;">EKS</td>
      <td style="padding:10px 12px; text-align:center;">Karpenter auto-provision</td>
      <td style="padding:10px 12px; text-align:center;"><span style="background:var(--green); color:#fff; padding:2px 8px; border-radius:4px; font-size:0.75rem;">Auto</span></td>
      <td style="padding:10px 12px; text-align:center;"><span style="background:rgba(0,214,143,0.15); color:var(--green); padding:4px 10px; border-radius:4px;">LOW</span></td>
    </tr>
  </tbody>
</table>
</div>
<p style="margin-top:12px; font-size:0.85rem; color:var(--text-muted); text-align:center;">
  <span style="color:var(--red); font-weight:600;">CRITICAL</span>: DSQL + MSK — 리전 장애 시 <strong>완전한 데이터 손실</strong>
</p>
:::

:::notes
{timing: 3min}
현재 DR 상태를 리스크 레벨별로 평가한 테이블입니다. 색상으로 위험도를 한눈에 파악할 수 있습니다.

녹색 영역은 안전합니다. Route53 Latency-based routing이 자동으로 트래픽을 전환하고, S3 Cross-Region Replication이 활성화되어 있고, EKS는 Karpenter가 노드를 자동 복구합니다.

노란색 영역은 수동 개입이 필요한 부분입니다. DocumentDB Global Cluster와 ElastiCache Global Datastore는 AWS CLI로 failover를 실행해야 합니다. 자동화되어 있지 않아서 RTO가 5-15분으로 늘어납니다.

{cue: pause}
빨간색이 가장 심각합니다. Aurora DSQL은 현재 us-east-1 단일 리전에만 존재합니다. MSK도 리전별로 독립적이어서 Replicator가 설정되어 있지 않습니다. OpenSearch는 리전 간 복제가 없어서 장애 시 전체 인덱스를 다시 빌드해야 합니다.

결론적으로 DSQL과 MSK가 Critical입니다. us-east-1 장애 시 6개 핵심 서비스의 트랜잭션 데이터와 이벤트 스트림이 완전히 손실됩니다.

{cue: transition}
각 컴포넌트의 구체적인 RTO와 RPO를 살펴보겠습니다.
:::

---
<!-- Slide 3: RTO/RPO Matrix -->
@type: content

## RTO/RPO Matrix

:::html
<table class="data-table" style="width:100%; border-collapse:collapse; font-size:0.85rem;">
  <thead>
    <tr style="background:var(--bg-card); border-bottom:2px solid var(--border);">
      <th style="padding:10px 14px; text-align:left; color:var(--text-muted);">Component</th>
      <th style="padding:10px 14px; text-align:center; color:var(--text-muted);">RTO</th>
      <th style="padding:10px 14px; text-align:center; color:var(--text-muted);">RPO</th>
      <th style="padding:10px 14px; text-align:left; color:var(--text-muted);">Recovery Notes</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom:1px solid var(--border);">
      <td style="padding:10px 14px;"><strong>Traffic Routing</strong></td>
      <td style="padding:10px 14px; text-align:center;"><span style="color:var(--green);">1-2 min</span></td>
      <td style="padding:10px 14px; text-align:center;"><span style="color:var(--green);">0</span></td>
      <td style="padding:10px 14px; color:var(--text-secondary);">Health check interval + DNS TTL</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);">
      <td style="padding:10px 14px;"><strong style="color:var(--red);">Aurora DSQL</strong></td>
      <td style="padding:10px 14px; text-align:center;"><span style="color:var(--red);">N/A</span></td>
      <td style="padding:10px 14px; text-align:center;"><span style="color:var(--red); font-weight:600;">Total Loss</span></td>
      <td style="padding:10px 14px; color:var(--text-secondary);">No cross-region replica exists</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border);">
      <td style="padding:10px 14px;"><strong>DocumentDB</strong></td>
      <td style="padding:10px 14px; text-align:center;"><span style="color:#fdcb6e;">5-15 min</span></td>
      <td style="padding:10px 14px; text-align:center;"><span style="color:var(--green);">&lt; 1 min</span></td>
      <td style="padding:10px 14px; color:var(--text-secondary);">Manual switchover-global-cluster</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);">
      <td style="padding:10px 14px;"><strong>ElastiCache</strong></td>
      <td style="padding:10px 14px; text-align:center;"><span style="color:var(--green);">1-5 min</span></td>
      <td style="padding:10px 14px; text-align:center;"><span style="color:var(--green);">&lt; 1 sec</span></td>
      <td style="padding:10px 14px; color:var(--text-secondary);">Manual promote secondary</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border);">
      <td style="padding:10px 14px;"><strong style="color:var(--red);">MSK</strong></td>
      <td style="padding:10px 14px; text-align:center;"><span style="color:var(--red);">N/A</span></td>
      <td style="padding:10px 14px; text-align:center;"><span style="color:var(--red); font-weight:600;">Total Loss</span></td>
      <td style="padding:10px 14px; color:var(--text-secondary);">Replicator disabled, no offset sync</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border); background:var(--bg-card);">
      <td style="padding:10px 14px;"><strong>S3</strong></td>
      <td style="padding:10px 14px; text-align:center;"><span style="color:var(--green);">Instant</span></td>
      <td style="padding:10px 14px; text-align:center;"><span style="color:var(--cyan);">&lt; 15 min</span></td>
      <td style="padding:10px 14px; color:var(--text-secondary);">CRR replication lag</td>
    </tr>
    <tr style="border-bottom:1px solid var(--border);">
      <td style="padding:10px 14px;"><strong>EKS</strong></td>
      <td style="padding:10px 14px; text-align:center;"><span style="color:var(--green);">2-5 min</span></td>
      <td style="padding:10px 14px; text-align:center;"><span style="color:var(--green);">0</span></td>
      <td style="padding:10px 14px; color:var(--text-secondary);">Karpenter node replacement</td>
    </tr>
  </tbody>
</table>
<div style="margin-top:16px; display:flex; gap:16px; justify-content:center;">
  <div style="display:flex; align-items:center; gap:6px; font-size:0.8rem;">
    <span style="width:12px; height:12px; background:var(--green); border-radius:2px;"></span>
    <span>RTO &lt; 5min, RPO &lt; 1min</span>
  </div>
  <div style="display:flex; align-items:center; gap:6px; font-size:0.8rem;">
    <span style="width:12px; height:12px; background:#fdcb6e; border-radius:2px;"></span>
    <span>RTO 5-15min</span>
  </div>
  <div style="display:flex; align-items:center; gap:6px; font-size:0.8rem;">
    <span style="width:12px; height:12px; background:var(--red); border-radius:2px;"></span>
    <span>Unrecoverable</span>
  </div>
</div>
:::

:::notes
{timing: 2min}
RTO와 RPO 매트릭스입니다. RTO는 Recovery Time Objective — 서비스 복구까지 걸리는 시간, RPO는 Recovery Point Objective — 허용 가능한 데이터 손실 시간입니다.

Route53은 RTO 1-2분, RPO 0입니다. Health check가 30초 간격이고 DNS TTL이 60초라서 최대 2분 내에 트래픽이 전환됩니다.

DocumentDB는 RTO 5-15분이지만 RPO는 1분 미만입니다. Global Cluster가 비동기로 복제하지만 지연이 매우 짧습니다. 문제는 수동 switchover 명령을 실행해야 한다는 점입니다.

ElastiCache는 RTO 1-5분, RPO 1초 미만으로 가장 빠릅니다. Global Datastore의 복제 지연이 매우 짧기 때문입니다. 하지만 역시 수동 promote가 필요합니다.

{cue: pause}
빨간색 행이 문제입니다. DSQL과 MSK는 RTO/RPO가 N/A입니다. 복구가 아니라 데이터 손실이죠. MSK의 경우 Replicator가 비활성화되어 있어서 consumer offset도 동기화되지 않습니다. 장애 후 어디서부터 다시 consume해야 하는지 알 수 없습니다.

{cue: transition}
이제 실제 장애 시나리오별로 어떤 일이 발생하는지 구체적으로 살펴보겠습니다.
:::

---
<!-- Slide 4: Scenario 1 - Full Region Failure -->
@type: content

## Scenario 1: Full Region Failure (us-east-1)

:::html
<div class="col-2" style="gap:1.5rem;">
  <div>
    <h4 style="margin:0 0 0.8rem 0; color:var(--green);">Auto Recovery (30s - 2min)</h4>
    <div class="card" style="padding:0.8rem; margin-bottom:0.6rem; border-left:3px solid var(--green);">
      <div style="display:flex; align-items:center; gap:8px;">
        <img src="common/aws-icons/services/Arch_Amazon-Route-53_48.svg" style="width:28px;">
        <div>
          <strong>Route53 Health Check</strong>
          <div style="font-size:0.8rem; color:var(--text-muted);">30s detect → traffic switch to us-west-2</div>
        </div>
      </div>
    </div>
    <div class="card" style="padding:0.8rem; margin-bottom:0.6rem; border-left:3px solid var(--green);">
      <div style="display:flex; align-items:center; gap:8px;">
        <img src="common/aws-icons/services/Arch_Amazon-CloudFront_48.svg" style="width:28px;">
        <div>
          <strong>CloudFront Origin</strong>
          <div style="font-size:0.8rem; color:var(--text-muted);">Follows Route53, no config change</div>
        </div>
      </div>
    </div>
    <div class="card" style="padding:0.8rem; border-left:3px solid var(--green);">
      <div style="display:flex; align-items:center; gap:8px;">
        <img src="common/aws-icons/services/Arch_Amazon-Simple-Storage-Service_48.svg" style="width:28px;">
        <div>
          <strong>S3 CRR</strong>
          <div style="font-size:0.8rem; color:var(--text-muted);">Already replicated, RPO &lt;15min</div>
        </div>
      </div>
    </div>
  </div>

  <div>
    <h4 style="margin:0 0 0.8rem 0; color:#fdcb6e;">Manual Intervention (5-15min)</h4>
    <div class="card" style="padding:0.8rem; margin-bottom:0.6rem; border-left:3px solid #fdcb6e;">
      <div style="display:flex; align-items:center; gap:8px;">
        <img src="common/aws-icons/services/Arch_Amazon-DocumentDB_48.svg" style="width:28px;">
        <div>
          <strong>DocumentDB Failover</strong>
          <div style="font-size:0.8rem; color:var(--text-muted);">switchover-global-cluster CLI required</div>
        </div>
      </div>
    </div>
    <div class="card" style="padding:0.8rem; border-left:3px solid #fdcb6e;">
      <div style="display:flex; align-items:center; gap:8px;">
        <img src="common/aws-icons/services/Arch_Amazon-ElastiCache_48.svg" style="width:28px;">
        <div>
          <strong>ElastiCache Promotion</strong>
          <div style="font-size:0.8rem; color:var(--text-muted);">failover-global-replication-group CLI</div>
        </div>
      </div>
    </div>
  </div>
</div>

<div style="margin-top:1rem; padding:0.8rem; background:rgba(255,107,107,0.1); border:1px solid var(--red); border-radius:8px;">
  <h4 style="margin:0 0 0.5rem 0; color:var(--red);">DATA LOSS (Unrecoverable)</h4>
  <div class="col-2" style="gap:1rem;">
    <div style="font-size:0.85rem;">
      <strong style="color:var(--red);">DSQL:</strong> 6 services lose ALL transaction data
      <div style="font-size:0.75rem; color:var(--text-muted); margin-top:4px;">order, payment, inventory, user-account, shipping, warehouse</div>
    </div>
    <div style="font-size:0.85rem;">
      <strong style="color:var(--red);">MSK:</strong> Unbounded event loss + offset desync
      <div style="font-size:0.75rem; color:var(--text-muted); margin-top:4px;">notification, analytics, recommendation consumers affected</div>
    </div>
  </div>
</div>
:::

:::notes
{timing: 3min}
시나리오 1: us-east-1 전체 리전 장애입니다. 가장 심각한 케이스죠.

자동으로 복구되는 부분부터 보겠습니다. Route53 Health Check가 30초 내에 us-east-1 NLB 응답 실패를 감지하고, 트래픽을 자동으로 us-west-2로 전환합니다. CloudFront는 Route53을 따라가므로 별도 설정 없이 전환됩니다. S3는 이미 CRR이 설정되어 있어서 15분 이내 데이터는 us-west-2에 있습니다.

{cue: pause}
수동 개입이 필요한 부분입니다. DocumentDB는 switchover-global-cluster 명령을 실행해야 합니다. us-west-2 클러스터를 primary로 승격시키는 작업이죠. 5-15분 걸립니다. ElastiCache도 마찬가지로 failover-global-replication-group 명령이 필요합니다.

빨간색 박스가 가장 심각한 부분입니다. DSQL은 us-east-1에만 있어서 6개 서비스의 트랜잭션 데이터가 완전히 손실됩니다. 주문, 결제, 재고 — 쇼핑몰의 핵심 데이터죠. MSK도 이벤트 스트림이 끊기고 consumer offset이 동기화되지 않아서 정확히 어디서 재시작해야 하는지 알 수 없습니다.

결론적으로, 현재 us-east-1이 죽으면 시스템은 "반쪽짜리 복구"만 가능합니다.

{cue: transition}
개별 DB 장애 시나리오를 살펴보겠습니다.
:::

---
<!-- Slide 5: Scenario 2 - Individual DB Failure -->
@type: tabs

## Scenario 2: Individual DB Failure

### DSQL Failure

**Impact**: 6 services affected
- inventory, shipping, order, payment, user-account, warehouse

**Current Behavior**:
- Services fail with connection timeout
- No automatic fallback

**Graceful Degradation** (recommended):
```go
// Mock fallback mode
if err != nil && config.MockFallbackEnabled {
    return mockResponse(), nil
}
```

### DocumentDB Failure

**Impact**: 7 services affected
- product-catalog, recommendation, review, wishlist, notification, analytics, user-profile

**Manual Failover Steps**:
```bash
aws docdb failover-global-cluster \
  --global-cluster-identifier production-docdb-global \
  --target-db-cluster-identifier production-docdb-global-us-west-2
```

**RTO**: 5-15 minutes
**RPO**: < 1 minute

### ElastiCache Failure

**Impact**: cart service (session + cache)

**Manual Promotion**:
```bash
aws elasticache failover-global-replication-group \
  --global-replication-group-id production-elasticache \
  --primary-region us-west-2
```

**RTO**: 1-5 minutes
**Cart data**: Temporary loss (rebuild from DB)

:::notes
{timing: 3min}
시나리오 2: 개별 DB 장애입니다. 탭을 전환하면서 각 케이스를 설명하겠습니다.

첫 번째 탭, DSQL 장애입니다. 현재 DSQL이 죽으면 6개 서비스가 connection timeout으로 실패합니다. 자동 fallback이 없어서 500 에러가 사용자에게 노출됩니다.

권장하는 해결책은 Graceful Degradation입니다. MockFallbackEnabled 플래그를 두고, DB 연결 실패 시 mock 응답을 반환하는 방식입니다. 사용자는 일부 기능이 제한되지만 전체 서비스가 죽지는 않습니다.

{cue: pause}
두 번째 탭, DocumentDB 장애입니다. 7개 서비스가 영향받지만, Global Cluster 덕분에 수동 failover로 복구 가능합니다. 화면에 보이는 CLI 명령을 실행하면 us-west-2가 primary로 승격됩니다. RTO 5-15분, RPO 1분 미만입니다.

세 번째 탭, ElastiCache 장애입니다. cart 서비스만 직접 영향받습니다. 세션과 캐시 데이터가 들어있죠. 수동 promotion으로 1-5분 내에 복구 가능하고, 장바구니 데이터는 일시적으로 손실되지만 DB에서 재구축할 수 있습니다.

{cue: transition}
EKS 클러스터 장애 시나리오를 보겠습니다.
:::

---
<!-- Slide 6: Scenario 3 - EKS Cluster Failure -->
@type: content
@layout: two-column

## Scenario 3: EKS Cluster Failure

::: left
### Auto Recovery (Karpenter)

- **Node replacement**: 2-5 minutes {.click}
- **ArgoCD**: Auto-redeploy workloads {.click}
- **Karpenter**: Provisions new nodes on demand {.click}

### Workload Recovery

- Deployment rollout triggered automatically {.click}
- Pod scheduling to new nodes {.click}
- Service endpoints updated {.click}
:::

::: right
### Current Gap

:::click
**No PodDisruptionBudget defined**

```yaml
# Missing PDB
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-gateway-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: api-gateway
```
:::

:::click
**Impact without PDB:**
- All pods can be evicted simultaneously
- Zero availability during node churn
- Rolling updates unsafe
:::
:::

:::notes
{timing: 2min}
시나리오 3: EKS 클러스터 장애입니다. 노드나 Pod 레벨 장애를 다룹니다.

자동 복구 부분은 괜찮습니다. Karpenter가 2-5분 내에 새 노드를 프로비저닝하고, ArgoCD가 자동으로 워크로드를 재배포합니다. Deployment의 replicas 설정에 따라 Pod가 새 노드에 스케줄링되고, Service 엔드포인트가 업데이트됩니다.

{cue: pause}
하지만 현재 Gap이 있습니다. PodDisruptionBudget이 정의되어 있지 않습니다.

PDB가 없으면 무슨 일이 벌어지냐면, 노드 교체 중에 모든 Pod가 동시에 evict될 수 있습니다. api-gateway Pod 3개가 같은 노드에 있었다면, 그 노드가 drain될 때 3개가 동시에 사라집니다. 새 Pod가 뜨기 전까지 서비스가 완전히 중단됩니다.

minAvailable: 1만 설정해도 최소 1개 Pod는 항상 유지되어서 zero downtime을 보장할 수 있습니다. 이건 Low effort로 빠르게 적용 가능한 개선사항입니다.

{cue: transition}
DSQL의 단일 리전 리스크를 더 자세히 살펴보겠습니다.
:::

---
<!-- Slide 7: DSQL Single-Region Risk -->
@type: content

## DSQL Single-Region Risk — CRITICAL

:::html
<div style="display:flex; gap:1.5rem; align-items:stretch;">
  <div style="flex:1;">
    <div class="card" style="padding:1rem; border:2px solid var(--red); background:rgba(255,107,107,0.08);">
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.8rem;">
        <img src="common/aws-icons/services/Arch_Amazon-Aurora_48.svg" style="width:40px;">
        <div>
          <h4 style="margin:0; color:var(--red);">Aurora DSQL</h4>
          <div style="font-size:0.8rem; color:var(--text-muted);">us-east-1 ONLY</div>
        </div>
        <span style="margin-left:auto; background:var(--red); color:#fff; padding:4px 10px; border-radius:4px; font-size:0.75rem; font-weight:600;">SINGLE REGION</span>
      </div>
      <p style="font-size:0.9rem; color:var(--text-secondary); margin:0 0 0.8rem 0;">
        Region failure = <strong style="color:var(--red);">Total data loss</strong> for 6 core services
      </p>
      <div style="font-size:0.85rem;">
        <strong>Affected Services:</strong>
        <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:6px;">
          <span style="background:rgba(255,107,107,0.2); color:var(--red); padding:4px 10px; border-radius:4px; font-size:0.8rem;">order</span>
          <span style="background:rgba(255,107,107,0.2); color:var(--red); padding:4px 10px; border-radius:4px; font-size:0.8rem;">payment</span>
          <span style="background:rgba(255,107,107,0.2); color:var(--red); padding:4px 10px; border-radius:4px; font-size:0.8rem;">inventory</span>
          <span style="background:rgba(255,107,107,0.2); color:var(--red); padding:4px 10px; border-radius:4px; font-size:0.8rem;">user-account</span>
          <span style="background:rgba(255,107,107,0.2); color:var(--red); padding:4px 10px; border-radius:4px; font-size:0.8rem;">shipping</span>
          <span style="background:rgba(255,107,107,0.2); color:var(--red); padding:4px 10px; border-radius:4px; font-size:0.8rem;">warehouse</span>
        </div>
      </div>
    </div>
  </div>

  <div style="flex:1;">
    <h4 style="margin:0 0 0.8rem 0; color:var(--text-secondary);">Business Impact</h4>
    <div class="card" style="padding:0.8rem; margin-bottom:0.6rem; border-left:3px solid var(--red);">
      <strong>Order Processing</strong>
      <div style="font-size:0.85rem; color:var(--text-muted);">All active orders lost, no recovery</div>
    </div>
    <div class="card" style="padding:0.8rem; margin-bottom:0.6rem; border-left:3px solid var(--red);">
      <strong>Payment Records</strong>
      <div style="font-size:0.85rem; color:var(--text-muted);">Transaction history unavailable</div>
    </div>
    <div class="card" style="padding:0.8rem; margin-bottom:0.6rem; border-left:3px solid var(--red);">
      <strong>Inventory State</strong>
      <div style="font-size:0.85rem; color:var(--text-muted);">Stock levels unknown, oversell risk</div>
    </div>
    <div class="card" style="padding:0.8rem; border-left:3px solid var(--red);">
      <strong>User Accounts</strong>
      <div style="font-size:0.85rem; color:var(--text-muted);">Authentication data lost</div>
    </div>
  </div>
</div>
:::

:::notes
{timing: 2min}
DSQL 단일 리전 리스크를 강조하는 슬라이드입니다. 이게 현재 아키텍처의 가장 큰 약점입니다.

왼쪽을 보시면, Aurora DSQL이 us-east-1에만 존재합니다. 리전 장애가 발생하면 6개 핵심 서비스의 데이터가 완전히 손실됩니다. order, payment, inventory, user-account, shipping, warehouse — 모두 쇼핑몰의 핵심 비즈니스 로직을 담당하는 서비스입니다.

{cue: pause}
오른쪽에 비즈니스 영향을 정리했습니다. 주문 처리 — 진행 중인 모든 주문이 사라집니다. 결제 기록 — 트랜잭션 히스토리를 조회할 수 없습니다. 재고 상태 — 현재 재고 수량을 알 수 없어서 과잉 판매 위험이 있습니다. 사용자 계정 — 로그인 자체가 불가능해집니다.

이건 기술적 장애가 아니라 비즈니스 중단입니다. 복구가 아니라 처음부터 다시 시작해야 하는 상황이죠.

{cue: transition}
이 문제의 해결책인 DSQL Linked Clusters를 살펴보겠습니다.
:::

---
<!-- Slide 8: DSQL Linked Clusters Solution -->
@type: content
@layout: two-column

## DSQL Linked Clusters — Solution

::: left
### Future State: Multi-Region Active-Active

:::click
**Linked Clusters** (linked_cluster_arns)
- us-east-1 ↔ us-west-2 bi-directional sync
- **RPO = 0** (synchronous replication)
- Automatic failover on region failure
:::

:::click
**Configuration**:
```hcl
resource "aws_dsql_cluster" "primary" {
  deletion_protection_enabled = true

  linked_cluster_arns = [
    aws_dsql_cluster.secondary.arn
  ]
}
```
:::

:::click
**Benefits**:
- Zero data loss on region failure
- Read from nearest region
- Write to any region
:::
:::

::: right
### Interim Mitigation

:::click
**1. Periodic Snapshots**
- Daily automated snapshots
- Cross-region copy to us-west-2
- Max 24hr data loss (better than total)
:::

:::click
**2. Application Mock Fallback**
- ENABLE_MOCK_FALLBACK=true
- Return cached/mock data on DB failure
- Graceful degradation vs hard failure
:::

:::click
**3. Event Sourcing Pattern**
- MSK events as source of truth
- Rebuild state from event log
- Requires MSK Replicator first
:::
:::

:::notes
{timing: 3min}
DSQL 문제의 해결책입니다. 왼쪽이 최종 목표 상태, 오른쪽이 당장 적용할 수 있는 임시 완화책입니다.

최종 목표는 Linked Clusters입니다. linked_cluster_arns 설정으로 us-east-1과 us-west-2를 양방향으로 연결합니다. 동기 복제라서 RPO가 0입니다. 리전 장애 시 자동 failover되고, 읽기는 가장 가까운 리전에서, 쓰기는 어느 리전에서든 가능합니다.

Terraform 코드를 보시면, aws_dsql_cluster 리소스에 linked_cluster_arns만 추가하면 됩니다. 기존 클러스터에 적용할 수 있어서 마이그레이션 부담이 적습니다.

{cue: pause}
하지만 Linked Clusters 구축에는 시간이 걸리므로, 당장은 임시 완화책을 적용해야 합니다.

첫째, 일일 자동 스냅샷입니다. 매일 스냅샷을 찍고 us-west-2로 복사합니다. 최악의 경우 24시간 데이터 손실이지만, 전체 손실보다는 훨씬 낫습니다.

둘째, 애플리케이션 Mock Fallback입니다. ENABLE_MOCK_FALLBACK 플래그를 두고, DB 연결 실패 시 캐시된 데이터나 mock 응답을 반환합니다. 서비스가 완전히 죽는 것보다 제한된 기능이라도 제공하는 게 낫습니다.

셋째, Event Sourcing 패턴입니다. MSK 이벤트를 source of truth로 사용해서 상태를 재구축하는 방식입니다. 하지만 이건 MSK Replicator가 먼저 설정되어야 합니다.

{cue: transition}
이제 자동화된 Failover 파이프라인 설계를 보겠습니다.
:::

---
<!-- Slide 9: Automated Failover Pipeline -->
@type: content

## Automated Failover Pipeline

:::html
<div class="flow-v" style="gap:0.6rem; padding:0.5rem;">
  <!-- Trigger Layer -->
  <div class="flow-h" style="justify-content:center; gap:1rem;">
    <div class="flow-group bg-red" style="padding:0.6rem 1rem;" data-fragment-index="1">
      <div class="flow-group-label">Trigger</div>
      <div class="icon-item">
        <img src="common/aws-icons/services/Arch_Amazon-CloudWatch_48.svg" style="width:40px;">
        <span>CloudWatch Alarm</span>
      </div>
      <div style="font-size:0.7rem; color:var(--text-muted); margin-top:4px;">HealthCheckStatus = UNHEALTHY</div>
    </div>
  </div>

  <div class="flow-arrow" style="font-size:1.2rem;" data-fragment-index="2">↓</div>

  <!-- EventBridge Layer -->
  <div class="flow-h" style="justify-content:center; gap:1rem;">
    <div class="flow-group bg-orange" style="padding:0.6rem 1rem;" data-fragment-index="2">
      <div class="flow-group-label">Orchestration</div>
      <div class="icon-item">
        <img src="common/aws-icons/services/Arch_Amazon-EventBridge_48.svg" style="width:40px;">
        <span>EventBridge Rule</span>
      </div>
      <div style="font-size:0.7rem; color:var(--text-muted); margin-top:4px;">Pattern: cloudwatch.alarm.state_change</div>
    </div>
  </div>

  <div class="flow-arrow" style="font-size:1.2rem;" data-fragment-index="3">↓</div>

  <!-- Lambda Layer -->
  <div class="flow-h" style="justify-content:center; gap:1rem;">
    <div class="flow-group bg-purple" style="padding:0.6rem 1rem;" data-fragment-index="3">
      <div class="flow-group-label">Execution (Parallel)</div>
      <div class="flow-h" style="gap:0.8rem;">
        <div class="flow-box" style="min-width:140px;">
          <img src="common/aws-icons/services/Arch_AWS-Lambda_48.svg" style="width:32px;">
          <span style="font-size:0.8rem;">DocumentDB Failover</span>
        </div>
        <div class="flow-box" style="min-width:140px;">
          <img src="common/aws-icons/services/Arch_AWS-Lambda_48.svg" style="width:32px;">
          <span style="font-size:0.8rem;">ElastiCache Promotion</span>
        </div>
      </div>
    </div>
  </div>

  <div class="flow-arrow" style="font-size:1.2rem;" data-fragment-index="4">↓</div>

  <!-- Post-actions Layer -->
  <div class="flow-h" style="justify-content:center; gap:1rem;">
    <div class="flow-box bg-blue" style="padding:0.6rem 1rem;" data-fragment-index="4">
      <img src="common/aws-icons/services/Arch_Amazon-Route-53_48.svg" style="width:28px;">
      <span style="font-size:0.8rem;">Route53 Update</span>
      <div style="font-size:0.65rem; color:var(--text-muted);">(if manual override needed)</div>
    </div>
    <div class="flow-box bg-green" style="padding:0.6rem 1rem;" data-fragment-index="4">
      <img src="common/aws-icons/services/Arch_Amazon-Simple-Notification-Service_48.svg" style="width:28px;">
      <span style="font-size:0.8rem;">SNS Notification</span>
      <div style="font-size:0.65rem; color:var(--text-muted);">Ops team alert</div>
    </div>
  </div>
</div>
<div style="margin-top:0.8rem; padding:0.5rem 1rem; background:rgba(253,203,110,0.1); border-radius:6px; text-align:center; font-size:0.85rem;">
  <strong style="color:#fdcb6e;">RTO Reduction:</strong> Manual 15min → Automated <strong style="color:var(--green);">2min</strong>
</div>
:::

:::notes
{timing: 3min}
자동화된 Failover 파이프라인 아키텍처입니다. 단계별로 설명드리겠습니다.

첫 번째, 트리거입니다. CloudWatch Alarm이 Route53 Health Check 상태를 모니터링합니다. us-east-1 NLB가 UNHEALTHY로 바뀌면 알람이 발생합니다.

두 번째, EventBridge Rule이 알람 상태 변경 이벤트를 캐치합니다. cloudwatch.alarm.state_change 패턴을 매칭해서 Lambda를 트리거합니다.

{cue: pause}
세 번째, Lambda 함수들이 병렬로 실행됩니다. DocumentDB Failover Lambda는 switchover-global-cluster API를 호출하고, ElastiCache Promotion Lambda는 failover-global-replication-group API를 호출합니다. 병렬 실행이라서 시간이 단축됩니다.

네 번째, 후속 작업입니다. Route53은 이미 자동 전환되지만, 수동 override가 필요한 경우를 대비해 Lambda에서 업데이트할 수 있습니다. SNS로 Ops 팀에 알림을 보내서 상황을 인지하게 합니다.

하단에 보시면 RTO가 수동 15분에서 자동화로 2분으로 단축됩니다. 이게 자동화의 핵심 가치입니다.

{cue: transition}
Lambda 코드 구현을 살펴보겠습니다.
:::

---
<!-- Slide 10: Lambda Failover Code -->
@type: content

## Lambda Failover Code

:::html
<div class="col-2" style="gap:1.5rem;">
  <div>
    <h4 style="margin:0 0 0.5rem 0; color:var(--cyan);">DocumentDB Failover Lambda</h4>
    <div class="code-block" style="font-size:0.75rem; padding:0.8rem;">
<span class="keyword">import</span> boto3
<span class="keyword">import</span> os

<span class="keyword">def</span> <span class="value">handler</span>(event, context):
    <span class="comment"># Safety flag check</span>
    <span class="keyword">if not</span> os.environ.get(<span class="string">'ENABLE_AUTO_FAILOVER'</span>):
        <span class="keyword">return</span> {<span class="string">'status'</span>: <span class="string">'skipped'</span>}

    docdb = boto3.client(<span class="string">'docdb'</span>)

    response = docdb.switchover_global_cluster(
        GlobalClusterIdentifier=<span class="string">'production-docdb-global'</span>,
        TargetDbClusterIdentifier=
            <span class="string">'production-docdb-global-us-west-2'</span>
    )

    <span class="keyword">return</span> {<span class="string">'status'</span>: <span class="string">'success'</span>}
    </div>
  </div>

  <div>
    <h4 style="margin:0 0 0.5rem 0; color:var(--green);">ElastiCache Failover Lambda</h4>
    <div class="code-block" style="font-size:0.75rem; padding:0.8rem;">
<span class="keyword">import</span> boto3
<span class="keyword">import</span> os

<span class="keyword">def</span> <span class="value">handler</span>(event, context):
    <span class="comment"># Safety flag check</span>
    <span class="keyword">if not</span> os.environ.get(<span class="string">'ENABLE_AUTO_FAILOVER'</span>):
        <span class="keyword">return</span> {<span class="string">'status'</span>: <span class="string">'skipped'</span>}

    elasticache = boto3.client(<span class="string">'elasticache'</span>)

    response = elasticache.failover_global_replication_group(
        GlobalReplicationGroupId=
            <span class="string">'production-elasticache'</span>,
        PrimaryRegion=<span class="string">'us-west-2'</span>
    )

    <span class="keyword">return</span> {<span class="string">'status'</span>: <span class="string">'success'</span>}
    </div>
  </div>
</div>
<div style="margin-top:1rem; padding:0.8rem; background:rgba(253,203,110,0.1); border:1px solid #fdcb6e; border-radius:8px;">
  <div style="display:flex; align-items:center; gap:8px;">
    <span style="font-size:1.2rem;">⚠️</span>
    <div>
      <strong style="color:#fdcb6e;">ENABLE_AUTO_FAILOVER Safety Flag</strong>
      <div style="font-size:0.85rem; color:var(--text-secondary);">환경 변수로 자동 failover 활성화/비활성화 제어. 테스트 환경에서는 비활성화, 프로덕션에서만 활성화.</div>
    </div>
  </div>
</div>
:::

:::notes
{timing: 2min}
Lambda 함수 구현 코드입니다. Python으로 간단하게 작성됩니다.

왼쪽 DocumentDB Failover Lambda를 보시면, boto3 클라이언트를 생성하고 switchover_global_cluster API를 호출합니다. GlobalClusterIdentifier와 TargetDbClusterIdentifier를 지정하면 us-west-2가 새로운 primary가 됩니다.

오른쪽 ElastiCache Failover Lambda도 비슷합니다. failover_global_replication_group API를 호출하고 PrimaryRegion을 us-west-2로 지정합니다.

{cue: pause}
중요한 건 ENABLE_AUTO_FAILOVER 안전 플래그입니다. 이 환경 변수가 설정되어 있지 않으면 Lambda가 아무것도 하지 않고 종료됩니다.

왜 이게 필요하냐면, 테스트 환경에서 실수로 프로덕션 DB를 failover하는 걸 방지하기 위해서입니다. 프로덕션 Lambda에만 이 환경 변수를 설정하고, staging이나 dev에서는 비활성화합니다.

{cue: transition}
DocumentDB failover의 구체적인 단계와 타임라인을 보겠습니다.
:::

---
<!-- Slide 11: DocumentDB Failover Steps -->
@type: content

## DocumentDB Failover — Step by Step

:::html
<div class="card" style="padding:1rem; margin-bottom:1rem; background:rgba(0,0,0,0.2);">
  <h4 style="margin:0 0 0.5rem 0; color:var(--cyan);">CLI Command</h4>
  <div class="code-block" style="font-size:0.82rem; padding:0.8rem; margin:0;">
aws docdb switchover-global-cluster \
  --global-cluster-identifier <span class="string">production-docdb-global</span> \
  --target-db-cluster-identifier <span class="string">production-docdb-global-us-west-2</span>
  </div>
</div>

<div class="flow-h" style="justify-content:center; gap:0.5rem; flex-wrap:wrap;">
  <div class="card" style="padding:0.8rem; min-width:140px; text-align:center;" data-fragment-index="1">
    <div style="font-size:1.5rem; font-weight:700; color:var(--red);">30s</div>
    <div style="font-size:0.8rem; color:var(--text-muted);">Health Check Detect</div>
    <div style="font-size:0.7rem; color:var(--text-secondary); margin-top:4px;">Route53 detects failure</div>
  </div>
  <div class="flow-arrow" style="font-size:1.5rem;">→</div>
  <div class="card" style="padding:0.8rem; min-width:140px; text-align:center;" data-fragment-index="2">
    <div style="font-size:1.5rem; font-weight:700; color:#fdcb6e;">10s</div>
    <div style="font-size:0.8rem; color:var(--text-muted);">Lambda Trigger</div>
    <div style="font-size:0.7rem; color:var(--text-secondary); margin-top:4px;">EventBridge → Lambda</div>
  </div>
  <div class="flow-arrow" style="font-size:1.5rem;">→</div>
  <div class="card" style="padding:0.8rem; min-width:140px; text-align:center;" data-fragment-index="3">
    <div style="font-size:1.5rem; font-weight:700; color:var(--accent);">5-15m</div>
    <div style="font-size:0.8rem; color:var(--text-muted);">Failover Execution</div>
    <div style="font-size:0.7rem; color:var(--text-secondary); margin-top:4px;">switchover-global-cluster</div>
  </div>
  <div class="flow-arrow" style="font-size:1.5rem;">→</div>
  <div class="card" style="padding:0.8rem; min-width:140px; text-align:center;" data-fragment-index="4">
    <div style="font-size:1.5rem; font-weight:700; color:var(--green);">30s</div>
    <div style="font-size:0.8rem; color:var(--text-muted);">DNS Propagation</div>
    <div style="font-size:0.7rem; color:var(--text-secondary); margin-top:4px;">New endpoint active</div>
  </div>
</div>

<div style="margin-top:1rem; padding:0.8rem; background:var(--bg-card); border-radius:8px;">
  <h4 style="margin:0 0 0.5rem 0; font-size:0.9rem;">Endpoint Update</h4>
  <div style="display:flex; gap:1rem; font-size:0.85rem;">
    <div style="flex:1;">
      <div style="color:var(--text-muted);">Before (us-east-1):</div>
      <code style="font-size:0.75rem;">production-docdb-global.cluster-xxx.us-east-1.docdb.amazonaws.com</code>
    </div>
    <div style="flex:1;">
      <div style="color:var(--green);">After (us-west-2):</div>
      <code style="font-size:0.75rem;">production-docdb-global.cluster-yyy.us-west-2.docdb.amazonaws.com</code>
    </div>
  </div>
</div>
:::

:::notes
{timing: 2min}
DocumentDB failover의 단계별 타임라인입니다.

상단에 실제 CLI 명령이 있습니다. switchover-global-cluster를 호출하고 global-cluster-identifier와 target-db-cluster-identifier를 지정합니다.

타임라인을 보시면, 첫 번째 30초는 Route53 Health Check가 장애를 감지하는 시간입니다. 두 번째 10초는 EventBridge가 알람을 받아서 Lambda를 트리거하는 시간입니다.

{cue: pause}
세 번째가 실제 failover 시간입니다. 5-15분으로 가장 깁니다. DocumentDB가 내부적으로 us-west-2 클러스터를 primary로 승격하고, 복제 방향을 역전시키고, 연결을 재설정하는 과정입니다.

네 번째 30초는 DNS 전파 시간입니다. 새로운 엔드포인트가 활성화되면 애플리케이션이 자동으로 새 primary에 연결됩니다.

하단에 엔드포인트 변경을 보여드렸습니다. us-east-1에서 us-west-2로 바뀝니다. 애플리케이션에서 Global Cluster 엔드포인트를 사용하면 이 변경이 투명하게 처리됩니다.

{cue: transition}
ElastiCache promotion 과정을 보겠습니다.
:::

---
<!-- Slide 12: ElastiCache Promotion -->
@type: content

## ElastiCache Promotion — Step by Step

:::html
<div class="card" style="padding:1rem; margin-bottom:1rem; background:rgba(0,0,0,0.2);">
  <h4 style="margin:0 0 0.5rem 0; color:var(--green);">CLI Command</h4>
  <div class="code-block" style="font-size:0.82rem; padding:0.8rem; margin:0;">
aws elasticache failover-global-replication-group \
  --global-replication-group-id <span class="string">production-elasticache</span> \
  --primary-region <span class="string">us-west-2</span>
  </div>
</div>

<div class="flow-h" style="justify-content:center; gap:0.5rem; flex-wrap:wrap;">
  <div class="card" style="padding:0.8rem; min-width:140px; text-align:center;" data-fragment-index="1">
    <div style="font-size:1.5rem; font-weight:700; color:var(--red);">30s</div>
    <div style="font-size:0.8rem; color:var(--text-muted);">Detect</div>
    <div style="font-size:0.7rem; color:var(--text-secondary); margin-top:4px;">Health check fail</div>
  </div>
  <div class="flow-arrow" style="font-size:1.5rem;">→</div>
  <div class="card" style="padding:0.8rem; min-width:140px; text-align:center;" data-fragment-index="2">
    <div style="font-size:1.5rem; font-weight:700; color:var(--accent);">1-5m</div>
    <div style="font-size:0.8rem; color:var(--text-muted);">Promote</div>
    <div style="font-size:0.7rem; color:var(--text-secondary); margin-top:4px;">Secondary → Primary</div>
  </div>
  <div class="flow-arrow" style="font-size:1.5rem;">→</div>
  <div class="card" style="padding:0.8rem; min-width:140px; text-align:center;" data-fragment-index="3">
    <div style="font-size:1.5rem; font-weight:700; color:var(--green);">Ready</div>
    <div style="font-size:0.8rem; color:var(--text-muted);">Writes Enabled</div>
    <div style="font-size:0.7rem; color:var(--text-secondary); margin-top:4px;">us-west-2 is primary</div>
  </div>
</div>

<div style="margin-top:1.5rem;">
  <h4 style="margin:0 0 0.8rem 0; font-size:0.9rem; color:var(--text-secondary);">Cart Service Impact</h4>
  <div class="col-2" style="gap:1rem;">
    <div class="card" style="padding:0.8rem; border-left:3px solid #fdcb6e;">
      <strong style="color:#fdcb6e;">During Failover (1-5min)</strong>
      <ul style="margin:0.5rem 0 0; padding-left:1.2rem; font-size:0.85rem; color:var(--text-secondary);">
        <li>Cart reads: degraded (stale data)</li>
        <li>Cart writes: fail (read-only)</li>
        <li>Session data: may be lost</li>
      </ul>
    </div>
    <div class="card" style="padding:0.8rem; border-left:3px solid var(--green);">
      <strong style="color:var(--green);">After Promotion</strong>
      <ul style="margin:0.5rem 0 0; padding-left:1.2rem; font-size:0.85rem; color:var(--text-secondary);">
        <li>Full read/write restored</li>
        <li>RPO: < 1 second (async lag)</li>
        <li>Cart rebuild from session cookie</li>
      </ul>
    </div>
  </div>
</div>
:::

:::notes
{timing: 2min}
ElastiCache promotion 과정입니다. DocumentDB보다 빠릅니다.

CLI 명령은 failover-global-replication-group입니다. global-replication-group-id와 primary-region을 지정하면 됩니다.

타임라인을 보시면, 감지 30초 후에 1-5분 내에 promotion이 완료됩니다. DocumentDB의 5-15분보다 훨씬 빠릅니다. ElastiCache는 인메모리 데이터베이스라서 상태 전환이 더 가볍기 때문입니다.

{cue: pause}
Cart 서비스에 미치는 영향을 정리했습니다. Failover 중에는 읽기가 stale 데이터를 반환할 수 있고, 쓰기는 실패합니다. 세션 데이터도 일부 손실될 수 있습니다.

Promotion 완료 후에는 full read/write가 복원됩니다. RPO가 1초 미만이라서 거의 모든 데이터가 보존됩니다. 손실된 장바구니 데이터는 세션 쿠키나 DB에서 재구축할 수 있습니다.

{cue: transition}
전체 DR 개선 로드맵을 정리해 보겠습니다.
:::

---
<!-- Slide 13: DR Improvement Roadmap -->
@type: timeline

## DR Improvement Roadmap

### P0 — Critical (Week 1-2)

DSQL Linked Clusters 설정
MSK Replicator 활성화
6개 서비스 multi-region 쓰기 가능

### P1 — High (Week 3-4)

Auto-failover Lambda + EventBridge 구축
PodDisruptionBudget 전체 서비스 적용
RTO 15min → 2min 달성

### P2 — Medium (Month 2)

CloudFront Origin Failover Group 설정
Route53 health check → /health/ready 변경
OpenSearch cross-cluster search 검토

:::notes
{timing: 2min}
DR 개선 로드맵을 타임라인으로 정리했습니다. ↑↓ 키로 단계별로 이동할 수 있습니다.

P0, Critical입니다. 첫 1-2주 안에 완료해야 합니다. DSQL Linked Clusters를 설정해서 us-west-2에 replica를 두고, MSK Replicator를 활성화해서 이벤트 복제를 시작합니다. 이게 완료되면 6개 핵심 서비스가 진정한 multi-region으로 동작합니다.

{cue: pause}
P1, High입니다. 3-4주차에 자동화를 구축합니다. Auto-failover Lambda와 EventBridge 파이프라인을 배포하고, PDB를 전체 20개 서비스에 적용합니다. 이걸로 RTO가 수동 15분에서 자동 2분으로 단축됩니다.

P2, Medium입니다. 2개월차에 세부 개선을 진행합니다. CloudFront Origin Failover Group을 설정해서 sub-second origin 전환을 가능하게 하고, Route53 health check를 /health/ready로 변경해서 더 정확한 상태를 감지합니다. OpenSearch cross-cluster search도 검토합니다.

{cue: transition}
DR Drill 전략을 살펴보겠습니다.
:::

---
<!-- Slide 14: DR Drill Strategy -->
@type: content
@layout: two-column

## DR Drill Strategy

::: left
### Drill Frequency

:::click
**Quarterly: Full Region Failure**
- Simulate us-east-1 complete outage
- Execute full failover pipeline
- Measure actual RTO/RPO
- Validate all services recover
:::

:::click
**Monthly: Individual DB Failover**
- Rotate: DocumentDB → ElastiCache → (future) DSQL
- Test Lambda automation
- Verify application reconnection
:::

:::click
**Weekly: Health Checks**
- Replication lag monitoring
- Traffic flow verification
- Endpoint connectivity test
:::
:::

::: right
### Tools & Automation

:::click
**AWS Fault Injection Simulator (FIS)**

```yaml
# FIS Experiment Template
actions:
  - name: stop-instances
    actionId: aws:ec2:stop-instances
    targets:
      Instances: us-east-1-targets
    duration: PT30M
```
:::

:::click
**Runbook Checklist**
- [ ] Notify stakeholders
- [ ] Enable ENABLE_AUTO_FAILOVER
- [ ] Monitor CloudWatch dashboards
- [ ] Validate service health
- [ ] Document findings
- [ ] Update RTO/RPO metrics
:::
:::

:::notes
{timing: 2min}
DR Drill 전략입니다. 정기적인 훈련 없이는 실제 장애 시 대응이 제대로 안 됩니다.

왼쪽 Drill 주기를 보시면, 분기별로 Full Region Failure 시뮬레이션을 합니다. us-east-1 전체 장애를 가정하고 완전한 failover를 실행합니다. 실제 RTO/RPO를 측정하고 모든 서비스가 복구되는지 검증합니다.

월별로 Individual DB Failover를 테스트합니다. DocumentDB, ElastiCache를 번갈아가며 테스트하고, 나중에 DSQL Linked Clusters가 설정되면 그것도 추가합니다. Lambda 자동화가 제대로 동작하는지, 애플리케이션이 자동 재연결하는지 확인합니다.

주별로 Health Check를 수행합니다. 복제 지연 모니터링, 트래픽 흐름 확인, 엔드포인트 연결 테스트를 합니다.

{cue: pause}
오른쪽에 도구와 자동화입니다. AWS FIS(Fault Injection Simulator)를 사용해서 장애를 주입합니다. EC2 인스턴스 중지, 네트워크 지연 주입 등을 자동화된 실험 템플릿으로 관리합니다.

Runbook 체크리스트도 중요합니다. 이해관계자 알림부터 시작해서 ENABLE_AUTO_FAILOVER 활성화, CloudWatch 대시보드 모니터링, 서비스 상태 검증, 결과 문서화, RTO/RPO 메트릭 업데이트까지 단계별로 체크합니다.

{cue: transition}
이번 블록의 핵심 내용을 정리하겠습니다.
:::

---
<!-- Slide 15: Key Takeaways -->
@type: content

## Key Takeaways

:::html
<div class="col-2" style="gap:1.5rem;">
  <div class="card" style="padding:1.2rem; border-left:3px solid var(--red);">
    <h4 style="margin:0 0 0.8rem 0; color:var(--red);">Critical Risks</h4>
    <ul style="margin:0; padding-left:1.2rem; font-size:0.9rem; line-height:1.8;">
      <li><strong>DSQL</strong>: Single region, total data loss risk</li>
      <li><strong>MSK</strong>: No replication, event loss</li>
      <li><strong>DocumentDB/ElastiCache</strong>: Manual CLI failover</li>
      <li>Current RTO: <span style="color:#fdcb6e;">15min manual</span></li>
    </ul>
  </div>
  <div class="card" style="padding:1.2rem; border-left:3px solid var(--green);">
    <h4 style="margin:0 0 0.8rem 0; color:var(--green);">Solutions</h4>
    <ul style="margin:0; padding-left:1.2rem; font-size:0.9rem; line-height:1.8;">
      <li><strong>P0</strong>: DSQL Linked Clusters + MSK Replicator</li>
      <li><strong>P1</strong>: Lambda + EventBridge automation</li>
      <li><strong>P1</strong>: PDB for all 20 services</li>
      <li>Target RTO: <span style="color:var(--green);">2min automated</span></li>
    </ul>
  </div>
  <div class="card" style="padding:1.2rem; border-left:3px solid var(--accent);">
    <h4 style="margin:0 0 0.8rem 0; color:var(--accent);">Automation Pipeline</h4>
    <ul style="margin:0; padding-left:1.2rem; font-size:0.9rem; line-height:1.8;">
      <li>CloudWatch Alarm → EventBridge → Lambda</li>
      <li>Parallel DB failover execution</li>
      <li>SNS notification to Ops team</li>
      <li>ENABLE_AUTO_FAILOVER safety flag</li>
    </ul>
  </div>
  <div class="card" style="padding:1.2rem; border-left:3px solid var(--cyan);">
    <h4 style="margin:0 0 0.8rem 0; color:var(--cyan);">DR Drill Strategy</h4>
    <ul style="margin:0; padding-left:1.2rem; font-size:0.9rem; line-height:1.8;">
      <li><strong>Quarterly</strong>: Full region failure simulation</li>
      <li><strong>Monthly</strong>: Individual DB failover test</li>
      <li><strong>Weekly</strong>: Replication lag + health checks</li>
      <li>Tool: AWS Fault Injection Simulator</li>
    </ul>
  </div>
</div>
:::

:::notes
{timing: 2min}
Block 4의 핵심 내용을 네 가지로 정리합니다.

첫째, Critical Risks입니다. DSQL 단일 리전과 MSK 무복제가 가장 심각합니다. DocumentDB와 ElastiCache는 수동 CLI가 필요하고, 현재 RTO는 수동으로 15분입니다.

둘째, Solutions입니다. P0으로 DSQL Linked Clusters와 MSK Replicator를 설정하고, P1으로 Lambda 자동화와 PDB를 전체 적용합니다. 목표 RTO는 자동화로 2분입니다.

셋째, Automation Pipeline입니다. CloudWatch Alarm이 EventBridge를 통해 Lambda를 트리거하고, DB failover를 병렬로 실행합니다. SNS로 Ops 팀에 알림을 보내고, ENABLE_AUTO_FAILOVER 안전 플래그로 실수를 방지합니다.

넷째, DR Drill 전략입니다. 분기별 Full region failure, 월별 Individual DB failover, 주별 Health check를 수행합니다. AWS FIS를 활용해서 장애를 자동으로 주입하고 테스트합니다.

{cue: transition}
마지막으로 퀴즈로 이번 블록 내용을 확인해 보겠습니다.
:::

---
<!-- Slide 16: Quiz -->
@type: quiz

## Knowledge Check

**Q1: 현재 Multi-Region Mall에서 가장 심각한 DR 리스크는?**
- [ ] Route53 Health Check 지연
- [x] Aurora DSQL 단일 리전 구성
- [ ] ElastiCache 수동 failover
- [ ] S3 CRR 15분 지연

**Q2: DocumentDB Global Cluster failover CLI 명령은?**
- [ ] aws docdb promote-read-replica
- [x] aws docdb switchover-global-cluster
- [ ] aws docdb failover-db-cluster
- [ ] aws rds failover-global-cluster

**Q3: 자동화 파이프라인에서 ENABLE_AUTO_FAILOVER 플래그의 목적은?**
- [ ] Failover 속도 향상
- [ ] 로그 레벨 설정
- [x] 테스트 환경에서 실수 방지
- [ ] 메트릭 수집 활성화

**Q4: DR Drill에서 Full Region Failure 시뮬레이션 권장 주기는?**
- [ ] 매주
- [ ] 매월
- [x] 분기별
- [ ] 매년

:::notes
{timing: 2min}
4개 문제로 이번 블록 내용을 확인해 보겠습니다.

Q1, 가장 심각한 DR 리스크입니다. 정답은 Aurora DSQL 단일 리전 구성입니다. Route53 지연이나 ElastiCache 수동 failover는 복구 가능하지만, DSQL은 데이터 손실이죠.

Q2, DocumentDB failover CLI입니다. switchover-global-cluster가 정답입니다. promote-read-replica는 RDS Read Replica용이고, failover-db-cluster는 단일 클러스터 AZ failover입니다.

Q3, ENABLE_AUTO_FAILOVER 목적입니다. 테스트 환경에서 실수로 프로덕션 DB를 failover하는 걸 방지합니다. 프로덕션에서만 이 플래그를 활성화합니다.

Q4, Full Region Failure 시뮬레이션 주기입니다. 분기별이 정답입니다. 너무 자주하면 리스크가 크고, 너무 드물면 실제 장애 시 대응이 미숙합니다.

{cue: transition}
이것으로 Block 4를 마무리합니다.
:::

---
<!-- Slide 17: Thank You -->
@type: thankyou

## Thank You

Block 4 — DR & Failover Automation 완료

[← 목차로 돌아가기](index.html) | [다음: Block 5 — Observability & Operations →](05-observability-ops.html)

:::notes
{timing: 30sec}
Block 4를 마무리합니다. DR 현황 분석, 장애 시나리오, 자동화 파이프라인, 그리고 개선 로드맵까지 다뤘습니다.

다음 Block 5에서는 Observability와 Operations를 다룹니다. 모니터링 스택, 알림 체계, 그리고 운영 자동화를 살펴보겠습니다.

질문이 있으시면 지금 받겠습니다.
:::
