---
remarp: true
block: data-sync
---

<!-- Slide 1: Cover -->
@type: cover

# Multi-Region Architecture Deep Dive
Data Sync & Replication (30min)

@speaker: 오준석 (Junseok Oh), Sr. Solutions Architect, AWS

:::notes
{timing: 1min}
두 번째 블록인 Data Sync & Replication 세션에 오신 것을 환영합니다.

이 블록에서는 멀티리전 아키텍처의 핵심 과제인 데이터 동기화와 복제 전략을 심층적으로 다룹니다. Aurora Global Database, DocumentDB Global Cluster, ElastiCache Global Datastore, MSK Replicator 등 각 데이터 스토어의 크로스리전 복제 메커니즘과 트레이드오프를 분석합니다.

{cue: transition}
먼저 Polyglot Persistence 전략부터 살펴보겠습니다.
:::

---
<!-- Slide 2: Data Store Selection Matrix -->
@type: content

## Polyglot Persistence Strategy

| Workload Type | Data Store | Replication | Services |
|---|---|---|---|
| **ACID 트랜잭션** (강한 일관성) | Aurora PostgreSQL Global DB | ≤1s async | order, payment, inventory, user-account, shipping |
| **유연한 스키마** (문서 모델) | DocumentDB Global Cluster | ≤2s async | product-catalog, user-profile, wishlist, review |
| **실시간 캐시** (밀리초 응답) | ElastiCache Valkey Global | <1s async | cart, session, rate-limiting, leaderboard |
| **전문 검색** (한국어 nori) | OpenSearch 2.17 | Cross-cluster | search, analytics, notification-logs |
| **이벤트 스트리밍** (비동기) | MSK Kafka 3.6 | MSK Replicator | event-bus, saga orchestration |
| **정적 자산** (객체) | S3 + CRR | Async | CDN assets, Tempo traces |

> **원칙**: 각 데이터 스토어는 워크로드 특성에 최적화된 용도로 사용. 모든 것을 하나의 DB에 넣지 않는다.

:::notes
{timing: 2min}
멀티리전 환경에서 Polyglot Persistence, 즉 다양한 데이터 스토어를 목적에 맞게 사용하는 전략이 핵심입니다.

ACID 트랜잭션이 필요한 주문, 결제, 재고 등은 Aurora PostgreSQL Global Database를 사용합니다. 1초 이내의 비동기 복제로 Secondary 리전에서 읽기를 제공합니다.

유연한 스키마가 필요한 상품 카탈로그, 사용자 프로필 등은 DocumentDB Global Cluster를 사용합니다.

실시간 캐시는 ElastiCache Valkey Global Datastore로, 세션, 장바구니, 레이트 리미팅 등을 처리합니다.

이벤트 드리븐 아키텍처의 백본은 MSK Kafka이며, MSK Replicator로 크로스리전 토픽 복제를 합니다.

{cue: question}
혹시 현재 운영 중인 서비스에서 여러 데이터 스토어를 함께 사용하고 계신 분 계신가요?

{cue: transition}
이제 각 데이터 스토어의 복제 패턴을 하나씩 살펴보겠습니다.
:::

---
<!-- Slide 3: Replication Patterns Overview -->
@type: content
@canvas: replication-topology

## Cross-Region Replication Patterns

<canvas id="replication-topology" width="1100" height="420"></canvas>

<div class="canvas-controls">
  <button onclick="replicationAnim.play()" class="btn-play">▶ Play</button>
  <button onclick="replicationAnim.reset()" class="btn-reset">↺ Reset</button>
</div>

:::notes
{timing: 3min}
이 다이어그램은 우리 아키텍처에서 사용하는 5가지 크로스리전 복제 패턴을 보여줍니다.

Step 1: Aurora Global Database — Primary Writer가 us-east-1에 있고, Storage-level replication으로 us-west-2의 Secondary Cluster에 1초 이내로 복제됩니다. Write Forwarding을 통해 Secondary에서도 쓰기가 가능합니다.

Step 2: DocumentDB Global Cluster — 마찬가지로 Primary/Secondary 구조이며, oplog 기반 복제로 2초 이내 동기화됩니다.

Step 3: ElastiCache Global Datastore — Active-Active 읽기를 지원하되, 쓰기는 Primary에서만 가능합니다. Sub-second 복제 지연을 보장합니다.

Step 4: MSK Replicator — Kafka 토픽을 리전 간 비동기로 복제합니다. Consumer offset도 함께 동기화 가능합니다.

Step 5: S3 Cross-Region Replication — 객체 수준 비동기 복제, 15분 이내 SLA입니다.

각 패턴의 공통점은 비동기(async) 복제라는 것입니다. 강한 일관성이 필요한 쓰기는 Primary 리전으로 라우팅하고, 읽기는 양 리전에서 서비스합니다.

{cue: transition}
가장 중요한 Aurora부터 상세히 살펴보겠습니다.
:::

---
<!-- Slide 4: Aurora Global Database Deep Dive -->
@type: content
@layout: two-column

## Aurora PostgreSQL Global Database

::: left
### Cluster Topology

```
Global Cluster: aurora-global
┌─────────────────────────┐
│     us-east-1           │
│   (PRIMARY CLUSTER)     │
│                         │
│  Writer (r6g.2xlarge)   │
│  Reader 1 (r6g.xlarge)  │
│  Reader 2 (r6g.xlarge)  │
└───────────┬─────────────┘
            │ Storage-level
            │ Replication ≤1s
            ▼
┌─────────────────────────┐
│     us-west-2           │
│  (SECONDARY CLUSTER)    │
│                         │
│  Reader 1 (r6g.xlarge)  │
│  Reader 2 (r6g.xlarge)  │
└─────────────────────────┘
```
:::

::: right
### Key Specifications

| Parameter | Value |
|---|---|
| Engine | PostgreSQL 15.4 |
| Instance Class | r6g.2xlarge (Writer) |
| Replication Lag | ≤1 second (typical) |
| RPO | ~1 second |
| Failover RTO | <1 minute (planned) |
| Max Secondary Regions | 5 |
| Storage | Auto-scaling, encrypted |

### Services Using Aurora
- `order-service` — 주문 CRUD
- `payment-service` — 결제 트랜잭션
- `inventory-service` — 재고 관리
- `user-account-service` — 사용자 계정
- `shipping-service` — 배송 추적
- `returns-service` — 반품 처리
:::

:::notes
{timing: 2min}
Aurora Global Database는 Storage-level replication을 사용합니다. 이는 MySQL이나 PostgreSQL의 논리적 복제와 다릅니다.

스토리지 레이어에서 직접 복제하기 때문에 Primary의 성능에 영향을 미치지 않으면서 1초 이내의 복제 지연을 달성합니다.

Primary Cluster는 us-east-1에 Writer 1대, Reader 2대로 구성됩니다. Secondary Cluster는 us-west-2에 Reader 2대입니다. Secondary에는 Writer가 없지만, Failover 시 Reader 중 하나가 Writer로 승격됩니다.

주의할 점은 Aurora Global Database는 비동기 복제이므로 RPO가 0이 아닙니다. 최근 1초 이내의 데이터가 유실될 수 있습니다. 이 점이 Active-Active 쓰기를 직접 지원하지 않는 이유이기도 합니다.

{cue: transition}
그럼 Secondary 리전에서의 쓰기는 어떻게 처리할까요? Write Forwarding입니다.
:::

---
<!-- Slide 5: Aurora Write Forwarding -->
@type: content
@canvas: write-forwarding

## Aurora Global Write Forwarding

<canvas id="write-forwarding" width="1100" height="400"></canvas>

<div class="canvas-controls">
  <button onclick="writeForwardAnim.play()" class="btn-play">▶ Play</button>
  <button onclick="writeForwardAnim.reset()" class="btn-reset">↺ Reset</button>
</div>

:::notes
{timing: 3min}
Write Forwarding은 Secondary 리전의 애플리케이션이 로컬 Aurora Reader에게 쓰기 요청을 보내면, Aurora가 자동으로 이를 Primary Writer로 포워딩하는 메커니즘입니다.

Step 1: us-west-2의 order-service가 INSERT 쿼리를 로컬 Aurora Reader에 전송합니다.

Step 2: Aurora Reader가 이 쓰기를 감지하고 Primary Writer(us-east-1)로 자동 포워딩합니다.

Step 3: Primary Writer가 쓰기를 실행하고 커밋합니다.

Step 4: Storage-level replication으로 1초 이내에 Secondary Reader에 반영됩니다.

Step 5: 애플리케이션에게 성공 응답이 돌아옵니다.

총 추가 레이턴시는 리전 간 네트워크 RTT(약 60-80ms) + Primary 쓰기 시간입니다. 읽기 요청은 여전히 로컬에서 처리되므로, Read-heavy 워크로드에서 매우 효과적입니다.

{cue: important}
Write Forwarding 사용 시 주의: read-after-write consistency가 즉시 보장되지 않습니다. 쓰기 후 바로 읽으면 이전 값이 나올 수 있습니다.

{cue: transition}
Write Forwarding의 레이턴시를 좀 더 상세히 분석해보겠습니다.
:::

---
<!-- Slide 6: Write Forwarding Latency Analysis -->
@type: content

## Write Forwarding Latency Analysis

| Operation | Local Region | With Write Forwarding | Overhead |
|---|---|---|---|
| Simple INSERT | 5-10ms | 65-90ms | +60-80ms (RTT) |
| Batch INSERT (100 rows) | 50-100ms | 110-180ms | +60-80ms |
| UPDATE with index | 3-8ms | 63-88ms | +60-80ms |
| Transaction (3 statements) | 15-30ms | 195-270ms | +180-240ms (3 RTT) |

:::click
### 중요 제약사항

| Constraint | Detail |
|---|---|
| **Read-after-write** | 복제 지연(≤1s)까지 기다려야 최신 데이터 확인 가능 |
| **Transaction isolation** | 각 statement마다 RTT 추가, 긴 트랜잭션은 비효율적 |
| **DDL 불가** | CREATE TABLE, ALTER TABLE 등은 Primary에서 직접 실행 |
| **Temp table 불가** | 임시 테이블 사용 불가 |
:::

> **Best Practice**: Write-heavy 서비스는 Primary 리전에, Read-heavy 서비스는 양 리전에 배치

:::notes
{timing: 2min}
Write Forwarding의 레이턴시를 분석해보면, 단일 쿼리는 리전 간 RTT인 60-80ms 정도의 오버헤드가 발생합니다.

그런데 트랜잭션의 경우 각 statement마다 RTT가 추가됩니다. 3개의 statement로 구성된 트랜잭션은 3번의 RTT, 즉 180-240ms의 추가 지연이 발생합니다.

따라서 Write Forwarding은 단발성 쓰기나 짧은 트랜잭션에 적합합니다. 복잡한 multi-statement 트랜잭션은 Primary 리전에서 직접 처리하는 것이 좋습니다.

실무적으로는 주문 생성처럼 write-after-write 패턴이 많은 서비스는 Primary 리전에 배치하고, 상품 조회나 사용자 프로필 읽기처럼 read-heavy한 서비스만 양 리전에서 서비스합니다.

{cue: transition}
다음은 DocumentDB Global Cluster를 살펴보겠습니다.
:::

---
<!-- Slide 7: DocumentDB Global Cluster -->
@type: content
@layout: tabs

## DocumentDB Global Cluster

::: tab Primary Cluster (us-east-1)
### Writer + 2 Readers

```json
{
  "cluster": "docdb-global-us-east-1",
  "role": "PRIMARY",
  "engine": "docdb 5.0 (MongoDB 5.0 compatible)",
  "instances": [
    { "id": "writer", "class": "db.r6g.2xlarge", "role": "writer" },
    { "id": "reader-1", "class": "db.r6g.xlarge", "role": "reader" },
    { "id": "reader-2", "class": "db.r6g.xlarge", "role": "reader" }
  ],
  "encryption": "at-rest (KMS) + in-transit (TLS)",
  "backup": "continuous, 35-day retention"
}
```

### Collections
- **products** (150 items, 10 categories) — 상품 카탈로그
- **user_profiles** — 프로필 + 선호도 + 배송지
- **wishlists** — 위시리스트
- **reviews** — 상품 리뷰 + 평점
- **notifications** — 알림 이력
:::

::: tab Secondary Cluster (us-west-2)
### 2 Readers (Read-Only)

```json
{
  "cluster": "docdb-global-us-west-2",
  "role": "SECONDARY",
  "engine": "docdb 5.0",
  "instances": [
    { "id": "reader-1", "class": "db.r6g.xlarge", "role": "reader" },
    { "id": "reader-2", "class": "db.r6g.xlarge", "role": "reader" }
  ],
  "replication_lag": "≤ 2 seconds (oplog-based)",
  "read_preference": "secondaryPreferred"
}
```

### Replication Mechanism
- **oplog** 기반 비동기 복제
- Secondary는 **read-only** (Write Forwarding 미지원)
- Failover 시 Secondary → Primary 승격 (manual)
- RPO: ~2 seconds
:::

:::notes
{timing: 2min}
DocumentDB Global Cluster는 Aurora와 유사한 Primary/Secondary 구조입니다.

핵심 차이점은 DocumentDB는 Write Forwarding을 지원하지 않는다는 것입니다. Secondary 리전에서 쓰기가 필요하면 애플리케이션이 직접 Primary 리전의 엔드포인트로 요청을 보내야 합니다.

복제는 oplog 기반으로 이루어지며, 지연은 일반적으로 2초 이내입니다. Aurora의 Storage-level replication보다는 약간 느립니다.

Collections을 보면, 상품 카탈로그는 주로 읽기 워크로드이므로 양 리전에서 서비스하기 적합합니다. 반면 위시리스트 추가, 리뷰 작성 등 쓰기는 Primary 리전으로 라우팅해야 합니다.

{cue: transition}
DocumentDB의 스키마 설계와 인덱스 전략을 보겠습니다.
:::

---
<!-- Slide 8: DocumentDB Schema Design -->
@type: content

## DocumentDB Schema Design

```json
// products collection — 상품 카탈로그
{
  "productId": "PROD-001",
  "name": "삼성 갤럭시 S25 울트라",
  "brand": "삼성전자",
  "category": { "id": "CAT-01", "name": "전자제품", "slug": "electronics" },
  "price": 1799000,
  "salePrice": 1439200,
  "discount": 20,
  "currency": "KRW",
  "rating": 4.5,
  "reviewCount": 342,
  "tags": ["electronics", "삼성전자", "인기상품"],
  "attributes": { "weight": "0.5kg", "origin": "한국" },
  "stock": { "available": 250, "warehouse": "WH-EAST-1" },
  "status": "active"
}
```

### Index Strategy
| Collection | Index | Purpose |
|---|---|---|
| products | `{ productId: 1 }` unique | PK lookup |
| products | `{ category.slug: 1 }` | 카테고리 필터 |
| products | `{ brand: 1 }`, `{ rating: -1 }` | 브랜드 필터, 평점 정렬 |
| user_profiles | `{ userId: 1 }` unique | 사용자 조회 |
| reviews | `{ productId: 1 }`, `{ rating: -1 }` | 상품별 리뷰, 평점순 |
| notifications | `{ userId: 1, sentAt: -1 }` | 최근 알림 조회 |

:::notes
{timing: 2min}
DocumentDB에서는 임베디드 문서 패턴을 적극 활용합니다. 상품의 카테고리, 속성 정보를 별도 테이블로 분리하지 않고 하나의 문서에 포함시킵니다.

이 방식의 장점은 한 번의 쿼리로 상품의 모든 정보를 가져올 수 있다는 것입니다. JOIN이 없으므로 읽기 성능이 우수하고, 크로스리전 복제 시에도 문서 단위로 원자적 복제가 보장됩니다.

인덱스는 읽기 패턴에 맞춰 설계합니다. 카테고리 필터, 평점 정렬, 브랜드 검색 등 주요 쿼리 패턴에 인덱스를 생성합니다.

주의할 점은 DocumentDB는 MongoDB 5.0 호환이지만, 100% 호환은 아닙니다. Change Streams, Transactions는 지원하지만, $graphLookup이나 일부 집계 연산자는 제한됩니다.

{cue: transition}
캐싱 계층인 ElastiCache를 살펴보겠습니다.
:::

---
<!-- Slide 9: ElastiCache Global Datastore -->
@type: content
@canvas: elasticache-global

## ElastiCache Valkey Global Datastore

<canvas id="elasticache-global" width="1100" height="400"></canvas>

<div class="canvas-controls">
  <button onclick="cacheAnim.play()" class="btn-play">▶ Play</button>
  <button onclick="cacheAnim.reset()" class="btn-reset">↺ Reset</button>
</div>

### Cluster Configuration

| Parameter | Value |
|---|---|
| Engine | Valkey 7.2 |
| Node Type | cache.r7g.xlarge |
| Shards | 3 (num_node_groups) |
| Replicas/Shard | 2 |
| Cross-region lag | < 1 second |
| Encryption | At-rest (KMS) + In-transit (TLS) |

:::notes
{timing: 3min}
ElastiCache Global Datastore는 Valkey(Redis 호환) 클러스터를 리전 간 복제합니다.

Step 1: Primary 클러스터(us-east-1)에 3개의 샤드, 각 샤드당 2개의 레플리카로 구성합니다.

Step 2: Global Datastore를 설정하면 us-west-2에 Secondary 클러스터가 자동 생성됩니다.

Step 3: Primary에서 쓰기(SET, HSET 등)가 발생하면, 1초 이내에 Secondary로 복제됩니다.

Step 4: 양 리전에서 읽기(GET 등)가 가능합니다. 쓰기는 Primary에서만 가능합니다.

Global Datastore는 Active-Active 모드를 지원하지 않습니다. 최근 Valkey는 Active-Active를 지원하기 시작했지만, AWS의 ElastiCache Global Datastore는 아직 Primary-Secondary 모델입니다.

이 점이 장바구니(cart) 데이터를 처리할 때 주요 고려사항입니다. 사용자가 us-west-2에서 장바구니에 상품을 추가하면, Primary(us-east-1)로 쓰기가 라우팅되어야 합니다.

{cue: transition}
캐시 패턴과 TTL 전략을 살펴보겠습니다.
:::

---
<!-- Slide 10: Cache Patterns & TTL Strategy -->
@type: content

## Cache Patterns & TTL Strategy

| Key Pattern | TTL | Data Type | Access Pattern |
|---|---|---|---|
| `product:{id}` | 1h | Hash | Cache-Aside: DB 조회 후 캐시 |
| `cache:categories` | 24h | String (JSON) | Refresh-Ahead |
| `cart:{userId}` | 7d | Hash | Write-Through: 즉시 반영 |
| `session:{sessionId}` | 2h | Hash | Write-Through |
| `ratelimit:api:{userId}` | 60s | String (counter) | Increment + EXPIRE |
| `stock:{productId}` | - (no TTL) | String (counter) | DECR on purchase |
| `leaderboard:popular` | - (no TTL) | Sorted Set | ZINCRBY on view |
| `search-history:{userId}` | 30d | List | LPUSH + LTRIM(50) |
| `promo:flash-sale` | 24h | Hash | Write-Through |

:::click
### Cache Invalidation Strategy

| Pattern | When to Use | Implementation |
|---|---|---|
| **Cache-Aside** | 읽기 빈번, 쓰기 적은 데이터 | App이 캐시 miss 시 DB 조회 → SET |
| **Write-Through** | 즉시 일관성 필요 | App이 DB + 캐시 동시 갱신 |
| **Event-Driven** | 비동기 일관성 OK | Kafka 이벤트로 캐시 무효화 |
| **TTL-Based** | 결과적 일관성 OK | 자연 만료 후 DB에서 재로드 |
:::

:::notes
{timing: 2min}
캐시 전략은 데이터 특성에 따라 4가지 패턴을 조합합니다.

상품 정보처럼 읽기가 많고 쓰기가 적은 데이터는 Cache-Aside 패턴을 사용합니다. 캐시 미스 시에만 DB에서 조회하고 캐시에 저장합니다.

장바구니나 세션처럼 즉시 일관성이 필요한 데이터는 Write-Through를 사용합니다. 쓰기 시 DB와 캐시를 동시에 갱신합니다.

재고 카운터(stock)는 TTL 없이 영구 보관하며, 구매 시 DECR 명령으로 원자적으로 감소시킵니다. 이는 동시 구매 시 재고 초과 판매를 방지합니다.

멀티리전에서 캐시 무효화의 핵심 과제는 Primary에서 데이터가 변경되었을 때 Secondary의 캐시도 갱신해야 한다는 것입니다. Global Datastore가 자동으로 처리하지만, 복제 지연(< 1s) 동안은 스테일 데이터를 읽을 수 있습니다.

{cue: transition}
이벤트 스트리밍의 핵심인 MSK를 살펴보겠습니다.
:::

---
<!-- Slide 11: MSK Kafka Architecture -->
@type: content
@canvas: msk-topology

## MSK (Kafka) Event Architecture

<canvas id="msk-topology" width="1100" height="420"></canvas>

<div class="canvas-controls">
  <button onclick="mskAnim.play()" class="btn-play">▶ Play</button>
  <button onclick="mskAnim.reset()" class="btn-reset">↺ Reset</button>
</div>

### Topic Summary
| Category | Topics | Partitions | Retention |
|---|---|---|---|
| Order | order.created/confirmed/shipped/delivered | 6 each | 7d |
| Payment | payment.completed/refunded/failed | 6 each | 7d |
| Inventory | inventory.reserved/released/restocked | 4 each | 7d |
| Notification | notification.email/push/sms | 3 each | 3d |
| Infrastructure | dlq.all, saga.orchestrator | 1, 6 | 30d, 7d |

:::notes
{timing: 3min}
MSK는 이벤트 드리븐 아키텍처의 백본입니다. 총 35개의 토픽으로 구성되어 있습니다.

Step 1: 서비스들이 이벤트를 발행합니다. order-service가 주문을 생성하면 order.created 토픽에 이벤트를 발행합니다.

Step 2: Consumer 서비스들이 관심 있는 토픽을 구독합니다. payment-service는 order.created를 구독하여 결제를 시작합니다.

Step 3: Saga Pattern으로 분산 트랜잭션을 관리합니다. saga.orchestrator 토픽이 전체 워크플로우를 조율합니다.

Step 4: 실패한 이벤트는 dlq.all(Dead Letter Queue)로 이동하며, 30일간 보관됩니다.

클러스터 구성은 kafka.m5.2xlarge 6대, 브로커당 1TB EBS, SASL/SCRAM 인증을 사용합니다.

{cue: transition}
크로스리전 토픽 복제를 담당하는 MSK Replicator를 보겠습니다.
:::

---
<!-- Slide 12: MSK Replicator -->
@type: content
@layout: compare

## MSK Replicator: Cross-Region Topic Replication

::: option-a MSK Replicator Enabled
### Active Configuration

```
[us-east-1 MSK] ─── MSK Replicator ──→ [us-west-2 MSK]
                    (IAM Auth, async)
```

**복제 대상**: 모든 토픽 (regex: `.*`)
**Consumer Offset**: 동기화 가능
**Compression**: GZIP
**Latency**: 수백 ms ~ 수 초

### 장점
- DR 시 Secondary에서 즉시 consume 가능
- Consumer offset 동기화로 이벤트 유실 최소화
- 토픽 구성(partitions, configs) 자동 동기화

### 비용
- 데이터 전송: $0.02/GB (리전 간)
- Replicator 시간당 요금 추가
:::

::: option-b MSK Replicator Disabled
### Passive Configuration

```
[us-east-1 MSK] ─── (no replication) ──→ [us-west-2 MSK]
```

**Secondary MSK**: 독립 클러스터 (빈 토픽)
**DR 시나리오**: Producer가 Secondary로 전환

### 장점
- 크로스리전 데이터 전송 비용 없음
- 구성 단순

### 단점
- DR 시 이벤트 유실 불가피 (in-flight events)
- Consumer offset 재설정 필요
- Failover 시간 증가 (토픽 재생성 불필요하나 데이터 없음)
:::

:::notes
{timing: 2min}
MSK Replicator는 리전 간 Kafka 토픽 복제를 담당합니다. 활성화 여부에 따른 트레이드오프를 비교합니다.

Replicator를 활성화하면 모든 토픽이 비동기로 Secondary 리전에 복제됩니다. DR 발생 시 Secondary의 Consumer가 즉시 복제된 토픽에서 메시지를 소비할 수 있습니다. Consumer offset도 동기화되므로 중복 처리가 최소화됩니다.

비활성화하면 비용은 절감되지만, DR 시 in-flight 이벤트가 유실됩니다. Producer가 Secondary MSK로 전환된 후 발행하는 새 이벤트부터만 처리 가능합니다.

우리 아키텍처에서는 Replicator를 활성화하되, 중요도가 낮은 토픽(analytics, notification-logs)은 제외하여 비용을 최적화합니다.

{cue: transition}
이제 전체 데이터 계층의 일관성과 레이턴시 트레이드오프를 분석하겠습니다.
:::

---
<!-- Slide 13: Consistency vs Latency Trade-offs -->
@type: content
@canvas: consistency-spectrum

## Consistency vs Latency Trade-offs

<canvas id="consistency-spectrum" width="1100" height="400"></canvas>

<div class="canvas-controls">
  <button onclick="consistencyAnim.play()" class="btn-play">▶ Play</button>
  <button onclick="consistencyAnim.reset()" class="btn-reset">↺ Reset</button>
</div>

:::notes
{timing: 3min}
이 다이어그램은 우리 아키텍처의 각 데이터 스토어를 일관성-레이턴시 스펙트럼에 매핑합니다.

왼쪽은 Strong Consistency(강한 일관성)이고, 오른쪽은 Eventual Consistency(결과적 일관성)입니다.

Step 1: Aurora Primary Writer — 가장 강한 일관성. 트랜잭션 격리 수준(READ COMMITTED)이 보장됩니다. 레이턴시는 5-10ms.

Step 2: Aurora Secondary + Write Forwarding — 쓰기는 Primary로 포워딩되지만, Read-after-write는 복제 지연(≤1s)까지 기다려야 합니다. 쓰기 레이턴시 65-90ms.

Step 3: ElastiCache Primary — 단일 리전 내에서는 강한 일관성. 레이턴시 <1ms. 하지만 Global Datastore를 통한 Secondary 읽기는 복제 지연 존재.

Step 4: DocumentDB Secondary — oplog 기반 복제로 2초 이내 결과적 일관성. readPreference: secondaryPreferred 사용 시.

Step 5: MSK Replicator — 가장 느슨한 결과적 일관성. 이벤트 전달은 수백 ms에서 수 초. 하지만 at-least-once delivery 보장.

핵심 원칙은: 쓰기 경로는 일관성을 우선시하고, 읽기 경로는 레이턴시를 우선시한다는 것입니다.

{cue: transition}
이를 RPO와 복제 지연 관점에서 정리해보겠습니다.
:::

---
<!-- Slide 14: RPO / Replication Lag Matrix -->
@type: content

## RPO & Replication Lag Matrix

| Data Store | Replication Method | Typical Lag | RPO | Risk Level |
|---|---|---|---|---|
| **Aurora Global DB** | Storage-level async | ≤ 1s | ~1s | 🟢 Low |
| **DocumentDB Global** | Oplog-based async | ≤ 2s | ~2s | 🟡 Medium |
| **ElastiCache Global** | Async replication | < 1s | ~1s | 🟢 Low |
| **MSK Replicator** | Topic-level async | 100ms ~ 5s | ~5s | 🟡 Medium |
| **OpenSearch** | Cross-cluster (manual) | Minutes | Minutes | 🔴 High |
| **S3 CRR** | Object-level async | ≤ 15min | ~15min | 🔴 High |

:::click
### Data Loss Scenarios During Regional Failover

| Scenario | Uncommitted Data | Impact | Mitigation |
|---|---|---|---|
| Aurora Failover | ≤1s of writes | 최근 주문/결제 유실 | Idempotent retry + DLQ |
| DocumentDB Failover | ≤2s of writes | 프로필/리뷰 업데이트 유실 | Event sourcing + replay |
| ElastiCache Failover | ≤1s of writes | 세션/장바구니 유실 | Session reconstruction |
| MSK Failover | In-flight events | 이벤트 순서 보장 불가 | Consumer idempotency |
:::

> **핵심**: 모든 서비스는 **idempotent**하게 설계하여 재시도 시 중복 처리를 방지해야 합니다.

:::notes
{timing: 2min}
RPO(Recovery Point Objective)를 데이터 스토어별로 정리하면, Aurora와 ElastiCache가 가장 낮은 RPO(~1s)를 보이고, S3 CRR이 가장 높은 RPO(~15min)를 보입니다.

OpenSearch는 현재 크로스리전 복제가 수동 구성이며, 실시간 동기화가 아닙니다. 이 점이 DR 상황에서의 주요 갭입니다.

Failover 시 데이터 유실 시나리오를 보면, 가장 크리티컬한 것은 Aurora의 미커밋 주문/결제 데이터입니다. 이를 위해 모든 서비스를 idempotent하게 설계하고, 실패한 이벤트는 DLQ로 보내 후처리합니다.

멀티리전에서 가장 중요한 설계 원칙 하나를 꼽자면, idempotency입니다. 네트워크 파티션, 복제 지연, 페일오버 등 모든 상황에서 동일한 요청을 여러 번 처리해도 결과가 같아야 합니다.

{cue: transition}
이 블록의 핵심을 정리하겠습니다.
:::

---
<!-- Slide 15: Key Takeaways -->
@type: content

## Key Takeaways

:::card-grid
:::card highlight
### 1. Polyglot Persistence
각 데이터 스토어는 워크로드 특성에 맞게 선택. Aurora(ACID), DocumentDB(문서), ElastiCache(캐시), MSK(이벤트)
:::

:::card
### 2. Write-Primary / Read-Local
모든 쓰기는 Primary 리전으로 라우팅. 읽기는 양 리전에서 서비스. Aurora Write Forwarding으로 Secondary에서도 쓰기 가능.
:::

:::card
### 3. Async Replication Trade-offs
모든 크로스리전 복제는 비동기. RPO는 1초(Aurora)부터 15분(S3)까지 다양. 강한 일관성이 필요하면 Primary에서 처리.
:::

:::card highlight
### 4. Idempotency is King
Failover, 복제 지연, 네트워크 파티션 — 모든 상황에서 안전하려면 서비스의 idempotent 설계가 필수.
:::
:::

:::notes
{timing: 1min}
이 블록의 핵심 네 가지를 정리합니다.

첫째, Polyglot Persistence — 모든 것을 하나의 DB에 넣지 마세요. 워크로드에 맞는 최적의 데이터 스토어를 선택하세요.

둘째, Write-Primary / Read-Local — 쓰기는 한 곳에서, 읽기는 가까운 곳에서. 이것이 멀티리전 데이터 아키텍처의 기본 원칙입니다.

셋째, 비동기 복제의 트레이드오프를 이해하세요. RPO가 0인 크로스리전 복제는 없습니다. 각 데이터 스토어의 RPO를 알고, 그에 맞는 전략을 세우세요.

넷째, Idempotency가 왕입니다. 분산 시스템의 모든 문제에 대한 첫 번째 방어선은 idempotent 설계입니다.

{cue: transition}
마지막으로 퀴즈를 풀어보겠습니다.
:::

---
<!-- Slide 16: Quiz -->
@type: quiz

## Block 2 Quiz

:::quiz
Aurora Global Write Forwarding에서 3개의 statement로 구성된 트랜잭션의 추가 레이턴시는 약 얼마입니까?
- 60-80ms (1 RTT)
- 120-160ms (2 RTT)
- [data-correct] 180-240ms (3 RTT)
- 240-320ms (4 RTT)

Write Forwarding은 각 statement마다 리전 간 RTT가 추가됩니다. 3개의 statement는 3번의 RTT, 약 180-240ms의 추가 지연이 발생합니다.
:::

:::quiz
DocumentDB Global Cluster에서 Secondary 리전의 쓰기 처리 방식은?
- Aurora처럼 Write Forwarding으로 자동 포워딩
- [data-correct] 애플리케이션이 직접 Primary 엔드포인트로 요청
- Secondary에서 직접 쓰기 후 Primary로 동기화
- Active-Active 양방향 쓰기 지원

DocumentDB는 Write Forwarding을 지원하지 않습니다. Secondary는 read-only이며, 쓰기가 필요하면 애플리케이션이 직접 Primary 리전의 엔드포인트로 요청을 보내야 합니다.
:::

:::quiz
ElastiCache Global Datastore에서 재고 카운터(stock)에 TTL을 설정하지 않는 이유는?
- 비용 절감을 위해
- [data-correct] 원자적 DECR 연산으로 실시간 재고를 관리하기 위해
- Global Datastore가 TTL을 지원하지 않기 때문에
- 복제 시 TTL이 동기화되지 않기 때문에

재고 카운터는 구매 시 DECR 명령으로 원자적으로 감소시켜야 합니다. TTL로 만료되면 재고 데이터가 사라져 동시 구매 시 초과 판매가 발생할 수 있습니다.
:::

:::quiz
멀티리전 데이터 아키텍처에서 가장 중요한 서비스 설계 원칙은?
- 강한 일관성 보장
- 최소 레이턴시
- [data-correct] Idempotent 설계
- 동기식 복제

Failover, 복제 지연, 네트워크 파티션 등 다양한 장애 상황에서 안전하려면 동일한 요청을 여러 번 처리해도 결과가 같은 idempotent 설계가 필수입니다.
:::

:::notes
{timing: 3min}
이 퀴즈는 이번 블록에서 다룬 핵심 개념을 확인합니다.

Q1은 Write Forwarding의 레이턴시 특성을 테스트합니다. 각 statement마다 RTT가 추가되므로, 긴 트랜잭션은 Write Forwarding에 적합하지 않습니다.

Q2는 Aurora와 DocumentDB의 Write Forwarding 지원 차이를 확인합니다. DocumentDB는 이 기능이 없으므로, 애플리케이션 수준에서 라우팅을 처리해야 합니다.

Q3는 캐시 설계의 실무적 고려사항을 테스트합니다. 재고처럼 원자적 연산이 필요한 데이터는 TTL 없이 영구 관리합니다.

Q4는 분산 시스템의 가장 중요한 원칙을 확인합니다. Idempotency는 모든 장애 시나리오의 안전망입니다.

{cue: transition}
5분 휴식 후 Block 3 Traffic Routing & Edge로 이어가겠습니다.
:::
