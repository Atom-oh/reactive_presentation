---
remarp: true
block: foundation
---

<!-- Slide 1: Cover -->
@type: cover

# Multi-Region Architecture Deep Dive
Multi-Region Foundation (30min)

@speaker: 오준석 (Junseok Oh), Sr. Solutions Architect, AWS

:::notes
{timing: 1min}
안녕하세요, Multi-Region Architecture Deep Dive 세션에 오신 것을 환영합니다.

이 세션은 AWS 기반 멀티리전 아키텍처를 심층적으로 다루는 L300+ 레벨 세션입니다. Cloud Architect와 Senior Engineer를 대상으로 하며, 실제 프로덕션 환경에서 검증된 패턴과 구현 전략을 공유합니다.

첫 번째 블록인 Multi-Region Foundation에서는 왜 멀티리전이 필요한지, 어떤 아키텍처 패턴이 있는지, 그리고 네트워킹과 VPC 설계의 핵심을 다룹니다.

{cue: transition}
먼저 전체 세션 아젠다를 확인하겠습니다.
:::

---
<!-- Slide 2: Agenda -->
@type: agenda
@timing: 150min

## Agenda

1. Multi-Region Foundation (30분)
2. Data Sync & Replication (30분)
- Break (5분)
3. Traffic Routing & Edge (30분)
4. DR & Failover Automation (30분)
- Break (5분)
5. Observability & Operations (30분)

> 질문은 각 Block 종료 시에 받겠습니다.

:::notes
{timing: 2min}
오늘 세션은 5개 블록으로 구성되어 있습니다. 총 150분 분량이며, 중간에 두 번의 휴식이 있습니다.

첫 번째 블록 Multi-Region Foundation에서는 멀티리전의 비즈니스 드라이버, Active-Active vs Active-Passive 비교, CAP Theorem의 실전 적용, 그리고 VPC/네트워킹 설계를 다룹니다.

두 번째 블록에서는 Aurora Global Database, DocumentDB, ElastiCache 등 데이터 계층의 복제 전략을 살펴봅니다.

세 번째 블록은 CloudFront, Route53, Global Accelerator를 활용한 트래픽 라우팅입니다.

네 번째 블록에서 DR 전략과 자동화된 페일오버 메커니즘을 다루고, 마지막으로 멀티리전 환경의 Observability와 운영 전략을 설명합니다.

{cue: question}
혹시 특정 블록에 더 관심이 있으신 분 계신가요? 해당 부분에서 더 깊이 다루겠습니다.

{cue: transition}
그럼 왜 멀티리전이 필요한지부터 시작하겠습니다.
:::

---
<!-- Slide 3: Why Multi-Region? -->
@type: content
@layout: two-column

## Why Multi-Region?

::: left
### Business Drivers

:::click
**Latency Reduction**
- 글로벌 사용자에게 < 100ms 응답 제공
- Edge caching만으로는 해결 불가능한 동적 콘텐츠
- 실시간 트랜잭션 처리 요구사항
:::

:::click
**High Availability (99.99%+)**
- 단일 리전 SLA 한계: 99.9% (연간 8.76시간 다운타임)
- 멀티리전: 99.99%+ (연간 52분 미만)
- 리전 전체 장애에 대한 복원력
:::
:::

::: right
:::click
**Scalability (10x Traffic Spikes)**
- Black Friday, Prime Day 수준의 트래픽 급증
- 단일 리전 AZ 용량 한계 극복
- 지역별 피크 타임 분산 처리
:::

:::click
**Data Residency & Compliance**
- GDPR (EU), PDPA (Singapore), PIPL (China)
- 데이터 주권 요구사항
- 산업별 규제: 금융, 의료, 공공
:::

:::click
### ROI Consideration
- 복잡성 증가 vs 비즈니스 연속성
- 멀티리전 운영 비용: +40~60%
- 다운타임 비용 대비 투자 정당화 필요
:::
:::

:::notes
{timing: 3min}
왜 멀티리전이 필요한지, 비즈니스 드라이버 관점에서 살펴보겠습니다.

첫 번째는 Latency입니다. 글로벌 사용자에게 100ms 미만의 응답 시간을 제공하려면 물리적으로 가까운 곳에 컴퓨팅이 있어야 합니다. CDN으로 정적 콘텐츠는 해결되지만, 동적 API 응답이나 실시간 트랜잭션은 백엔드가 가까이 있어야 합니다.

서울에서 us-east-1까지 네트워크 왕복은 약 200ms입니다. 아무리 백엔드를 최적화해도 물리 법칙을 이길 수 없습니다. 그래서 ap-northeast-2에 백엔드를 두면 20ms 이내로 응답할 수 있습니다.

두 번째는 High Availability입니다. 단일 리전의 SLA는 보통 99.9%인데, 이건 연간 8.76시간의 다운타임을 의미합니다. 99.99%를 달성하려면 멀티리전이 필수입니다.

{cue: pause}
2017년 S3 us-east-1 장애를 기억하시는 분? 4시간 동안 절반 이상의 인터넷 서비스가 영향을 받았습니다. 단일 리전의 리스크를 보여주는 대표적 사례입니다.

세 번째는 Scalability입니다. Black Friday나 Prime Day 같은 이벤트에서 트래픽이 10배 이상 급증할 수 있습니다. 단일 리전의 AZ 용량에는 한계가 있고, 멀티리전으로 부하를 분산하면 더 큰 스케일을 처리할 수 있습니다.

네 번째는 Data Residency입니다. GDPR은 EU 시민 데이터가 EU 내에 저장되어야 한다고 요구합니다. 중국의 PIPL, 싱가포르의 PDPA도 유사한 요구사항이 있습니다. 글로벌 비즈니스라면 데이터 주권을 반드시 고려해야 합니다.

마지막으로 ROI를 따져봐야 합니다. 멀티리전은 운영 비용이 40~60% 증가합니다. 다운타임으로 인한 비즈니스 손실이 이 비용보다 크다면 투자가 정당화됩니다.

{cue: transition}
이제 구체적인 아키텍처 패턴을 비교해 보겠습니다.
:::

---
<!-- Slide 4: Active-Active vs Active-Passive -->
@type: compare

## Active-Active vs Active-Passive

### Active-Active
- **트래픽**: 양쪽 리전이 동시에 트래픽 처리
- **Latency**: 사용자에게 가장 가까운 리전으로 라우팅 (최적)
- **비용**: 항상 2x 리소스 운영 (높음)
- **데이터**: 양방향 복제, 충돌 해결 필요
- **Failover**: 즉시 (이미 트래픽 처리 중)
- **복잡성**: 높음 — 데이터 동기화, 충돌 해결 로직 필요
- **Use Case**: 글로벌 서비스, 실시간 협업, 게임

### Active-Passive
- **트래픽**: Primary만 처리, Secondary는 대기
- **Latency**: Primary 리전 기준 (지역별 차이)
- **비용**: Standby 리소스만 유지 (낮음)
- **데이터**: 단방향 복제, Primary → Secondary
- **Failover**: RTO 기반 (수 분 ~ 수십 분)
- **복잡성**: 낮음 — 단방향 복제만 관리
- **Use Case**: 지역 한정 서비스, 비용 민감, DR 중심

:::notes
{timing: 3min}
Active-Active와 Active-Passive, 두 가지 기본 패턴을 비교해 보겠습니다.

Active-Active는 양쪽 리전이 동시에 트래픽을 처리합니다. 사용자는 가장 가까운 리전으로 라우팅되므로 Latency가 최적화됩니다. 단점은 비용이 항상 2배라는 것과, 데이터 동기화가 복잡하다는 점입니다.

Active-Active에서 가장 어려운 문제가 데이터 충돌입니다. 같은 사용자가 두 리전에서 동시에 주문을 넣으면 어떻게 될까요? 양쪽에서 같은 재고를 차감하면 문제가 됩니다. 이런 충돌을 해결하는 로직이 필요합니다.

Active-Passive는 Primary 리전만 트래픽을 처리하고, Secondary는 대기합니다. 데이터는 Primary에서 Secondary로 단방향 복제됩니다. 복잡성이 낮고 비용도 적지만, Primary 리전에서 먼 사용자는 Latency가 높습니다.

{cue: pause}
Failover 시간도 다릅니다. Active-Active는 이미 양쪽에서 트래픽을 처리하고 있으므로 한 쪽이 죽어도 즉시 다른 쪽이 전체 트래픽을 흡수합니다. Active-Passive는 Secondary를 활성화하는 시간이 필요합니다 — 보통 수 분에서 수십 분입니다.

어떤 패턴을 선택할지는 비즈니스 요구사항에 따라 다릅니다. 글로벌 서비스, 실시간 협업 도구, 게임처럼 Latency가 중요하면 Active-Active입니다. 지역 한정 서비스이거나 비용이 민감하면 Active-Passive가 적합합니다.

실제로는 하이브리드를 많이 씁니다. 읽기는 Active-Active로 양쪽에서 처리하고, 쓰기는 Active-Passive로 Primary에서만 처리하는 방식입니다. 이걸 Write-Primary/Read-Local 패턴이라고 부릅니다.

{cue: transition}
이런 패턴 선택의 이론적 배경이 되는 CAP Theorem을 살펴보겠습니다.
:::

---
<!-- Slide 5: CAP Theorem in Practice -->
@type: content

## CAP Theorem in Practice

:::html
<div class="flow-v" style="gap:1.5rem; padding:0.5rem;">
  <!-- CAP Triangle -->
  <div class="flow-h" style="justify-content:center; gap:3rem; align-items:center;">
    <!-- Triangle visualization -->
    <div style="position:relative; width:280px; height:250px;">
      <!-- C vertex -->
      <div style="position:absolute; top:0; left:50%; transform:translateX(-50%); text-align:center;">
        <div style="width:70px; height:70px; border-radius:50%; background:linear-gradient(135deg, #FF9900, #FF6600); display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:1.5rem;">C</div>
        <div style="font-size:0.85rem; margin-top:4px; color:rgba(255,255,255,0.8);">Consistency</div>
      </div>
      <!-- A vertex -->
      <div style="position:absolute; bottom:0; left:0; text-align:center;">
        <div style="width:70px; height:70px; border-radius:50%; background:linear-gradient(135deg, #3B82F6, #1D4ED8); display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:1.5rem;">A</div>
        <div style="font-size:0.85rem; margin-top:4px; color:rgba(255,255,255,0.8);">Availability</div>
      </div>
      <!-- P vertex -->
      <div style="position:absolute; bottom:0; right:0; text-align:center;">
        <div style="width:70px; height:70px; border-radius:50%; background:linear-gradient(135deg, #10B981, #059669); display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:1.5rem;">P</div>
        <div style="font-size:0.85rem; margin-top:4px; color:rgba(255,255,255,0.8);">Partition<br>Tolerance</div>
      </div>
      <!-- Lines -->
      <svg style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;">
        <line x1="140" y1="75" x2="35" y2="175" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
        <line x1="140" y1="75" x2="245" y2="175" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
        <line x1="35" y2="175" x2="245" y2="175" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
      </svg>
    </div>

    <!-- AWS Service mapping -->
    <div style="display:flex; flex-direction:column; gap:0.8rem;" data-fragment-index="1">
      <div class="card" style="padding:0.8rem; border-left:3px solid #FF9900;">
        <div style="display:flex; align-items:center; gap:0.6rem;">
          <span style="font-weight:bold; color:#FF9900;">CP</span>
          <img src="common/aws-icons/services/Arch_Amazon-Aurora_48.svg" style="width:32px;">
          <div>
            <div style="font-size:0.9rem; font-weight:600;">Aurora DSQL</div>
            <div style="font-size:0.75rem; color:rgba(255,255,255,0.6);">Strong consistency, may reject writes during partition</div>
          </div>
        </div>
      </div>
      <div class="card" style="padding:0.8rem; border-left:3px solid #3B82F6;">
        <div style="display:flex; align-items:center; gap:0.6rem;">
          <span style="font-weight:bold; color:#3B82F6;">AP</span>
          <img src="common/aws-icons/services/Arch_Amazon-DynamoDB_48.svg" style="width:32px;">
          <div>
            <div style="font-size:0.9rem; font-weight:600;">DynamoDB Global Tables</div>
            <div style="font-size:0.75rem; color:rgba(255,255,255,0.6);">Eventually consistent, always available, last-writer-wins</div>
          </div>
        </div>
      </div>
      <div class="card" style="padding:0.8rem; border-left:3px solid #10B981;">
        <div style="display:flex; align-items:center; gap:0.6rem;">
          <span style="font-weight:bold; color:#10B981;">AP</span>
          <img src="common/aws-icons/services/Arch_Amazon-ElastiCache_48.svg" style="width:32px;">
          <div>
            <div style="font-size:0.9rem; font-weight:600;">ElastiCache Global Datastore</div>
            <div style="font-size:0.75rem; color:rgba(255,255,255,0.6);">Async replication, < 1s lag, read replicas</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Key insight -->
  <div style="background:rgba(255,153,0,0.1); border:1px solid rgba(255,153,0,0.3); border-radius:8px; padding:0.8rem; text-align:center;" data-fragment-index="2">
    <strong style="color:#FF9900;">핵심</strong>: 네트워크 파티션은 불가피 → P는 필수 선택 → <strong>C vs A 트레이드오프</strong>
  </div>
</div>
:::

:::notes
{timing: 3min}
CAP Theorem을 실전에 적용해 보겠습니다.

CAP Theorem은 분산 시스템에서 Consistency(일관성), Availability(가용성), Partition Tolerance(파티션 허용) 세 가지를 동시에 만족할 수 없다고 말합니다. 네트워크 파티션이 발생했을 때, 일관성과 가용성 중 하나를 선택해야 합니다.

멀티리전 환경에서 네트워크 파티션은 피할 수 없습니다. 리전 간 연결이 끊어질 수 있고, 이건 우리가 통제할 수 없는 영역입니다. 따라서 Partition Tolerance는 필수 선택이고, 실제 선택은 Consistency vs Availability입니다.

{cue: pause}
AWS 서비스를 예로 보면, Aurora DSQL은 CP 시스템입니다. Strong consistency를 보장하지만, 파티션 상황에서 쓰기를 거부할 수 있습니다. 금융 트랜잭션처럼 데이터 정합성이 절대적으로 중요한 경우에 적합합니다.

DynamoDB Global Tables는 AP 시스템입니다. Eventually consistent지만 항상 가용합니다. 파티션 상황에서도 각 리전이 독립적으로 쓰기를 받고, 나중에 동기화합니다. 충돌은 last-writer-wins로 해결합니다. 쇼핑 카트나 사용자 프로필처럼 약간의 지연이 허용되는 경우에 적합합니다.

ElastiCache Global Datastore도 AP 시스템입니다. 비동기 복제로 1초 미만의 lag이 있지만, 캐시 용도로는 충분합니다.

핵심 메시지는, 어떤 서비스를 선택할지는 비즈니스 요구사항에 따라 다르다는 것입니다. 모든 데이터에 Strong consistency가 필요하지 않습니다. 데이터 유형별로 적절한 consistency 모델을 선택하는 것이 중요합니다.

{cue: transition}
Consistency 모델을 더 자세히 살펴보겠습니다.
:::

---
<!-- Slide 6: Consistency Models -->
@type: tabs

## Consistency Models

### Strong Consistency
**정의**: 모든 읽기가 최신 쓰기 결과를 반환
**AWS 서비스**: Aurora DSQL, DynamoDB (strongly consistent read)
**Latency**: 높음 (cross-region quorum 필요)
**Use Case**: 금융 트랜잭션, 재고 관리, 결제 처리

```
Write(x=5) → [Sync to all regions] → Read(x) = 5 ✓
```

### Bounded Staleness
**정의**: 읽기가 최대 N초 또는 N버전 이내의 데이터 반환
**AWS 서비스**: Cosmos DB (Azure), 커스텀 구현 필요
**Latency**: 중간 (설정된 bound 내에서 유연)
**Use Case**: 리더보드, 분석 대시보드, 실시간에 근접한 데이터

```
Write(x=5) → [Within 5 seconds] → Read(x) = 5 or recent value
```

### Session Consistency
**정의**: 같은 세션 내에서는 자신의 쓰기를 항상 읽음
**AWS 서비스**: DynamoDB (with session affinity)
**Latency**: 낮음 (local read 가능)
**Use Case**: 사용자 프로필, 쇼핑 카트, 개인 설정

```
Session A: Write(x=5) → Read(x) = 5 ✓
Session B: Read(x) = 3 (이전 값, 곧 업데이트됨)
```

### Eventual Consistency
**정의**: 충분한 시간이 지나면 모든 복제본이 동일해짐
**AWS 서비스**: S3, DynamoDB Global Tables, ElastiCache
**Latency**: 가장 낮음 (local read, async replication)
**Use Case**: 로그, 메트릭, 콘텐츠 캐시, 비핵심 데이터

```
Write(x=5) → Read(x) = 3 (stale) → [Eventually] → Read(x) = 5
```

:::notes
{timing: 3min}
네 가지 주요 Consistency 모델을 살펴보겠습니다.

Strong Consistency는 모든 읽기가 최신 쓰기를 반환하는 것을 보장합니다. 가장 직관적이지만 Latency가 높습니다. 쓰기가 모든 리전에 동기화된 후에야 성공을 반환하기 때문입니다. Aurora DSQL이 이 모델을 사용합니다. 금융 트랜잭션이나 결제 처리에 필수입니다.

Bounded Staleness는 읽기 데이터가 최대 N초 또는 N버전 이내임을 보장합니다. Strong과 Eventual의 중간입니다. 예를 들어 "5초 이내의 데이터"를 보장하면, 5초 전의 데이터는 받아들일 수 있는 경우에 적합합니다. 리더보드나 분석 대시보드에서 사용합니다.

{cue: pause}
Session Consistency는 "내가 쓴 것은 내가 읽을 수 있다"를 보장합니다. 같은 세션 내에서만 일관성이 유지됩니다. 다른 세션은 이전 값을 읽을 수 있습니다. 쇼핑 카트에 상품을 담으면 바로 보여야 하지만, 다른 사용자에게 내 카트가 즉시 보일 필요는 없죠.

Eventual Consistency는 "언젠가는" 모든 복제본이 동일해지는 것을 보장합니다. Latency가 가장 낮습니다. Local read가 가능하고 비동기 복제이기 때문입니다. S3, DynamoDB Global Tables, ElastiCache가 이 모델입니다. 로그, 메트릭, 콘텐츠 캐시에 적합합니다.

실무에서는 하나의 시스템 내에서도 데이터 유형에 따라 다른 consistency 모델을 적용합니다. 결제는 Strong, 상품 목록은 Eventual, 사용자 프로필은 Session — 이런 식으로 혼합합니다.

{cue: transition}
이제 실제 아키텍처를 살펴보겠습니다.
:::

---
<!-- Slide 7: Architecture at a Glance -->
@type: content

## Architecture at a Glance

:::html
<div class="flow-v" style="gap:0.8rem; padding:0.3rem;">
  <!-- Top: Edge Layer -->
  <div class="flow-h" style="justify-content:center; gap:1rem;">
    <div class="flow-group bg-orange" style="padding:0.6rem 1rem;" data-fragment-index="1">
      <div class="flow-group-label">Edge Layer</div>
      <div class="flow-h" style="gap:0.8rem;">
        <div class="icon-item sm">
          <img src="common/aws-icons/services/Arch_Amazon-CloudFront_48.svg">
          <span>CloudFront</span>
        </div>
        <div class="icon-item sm">
          <img src="common/aws-icons/services/Arch_AWS-WAF_48.svg">
          <span>WAF</span>
        </div>
        <div class="icon-item sm">
          <img src="common/aws-icons/services/Arch_Amazon-Route-53_48.svg">
          <span>Route53</span>
        </div>
      </div>
    </div>
  </div>

  <div class="flow-arrow" style="font-size:1.2rem;">↓</div>

  <!-- Middle: Dual Regions -->
  <div class="flow-h" style="justify-content:center; gap:1.5rem;">
    <!-- us-east-1 -->
    <div class="card" style="padding:0.8rem; min-width:280px; border-left:3px solid #FF9900;" data-fragment-index="2">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.6rem;">
        <span style="font-size:0.75rem; background:#FF9900; color:#000; padding:2px 8px; border-radius:4px; font-weight:600;">PRIMARY</span>
        <span style="font-weight:600;">us-east-1</span>
      </div>
      <div class="flow-h" style="gap:0.5rem; flex-wrap:wrap;">
        <div class="flow-box" style="padding:0.4rem 0.6rem; font-size:0.75rem;">
          <img src="common/aws-icons/services/Arch_Elastic-Load-Balancing_48.svg" style="width:24px;">
          <span>NLB</span>
        </div>
        <div class="flow-arrow" style="font-size:0.9rem;">→</div>
        <div class="flow-box" style="padding:0.4rem 0.6rem; font-size:0.75rem;">
          <img src="common/aws-icons/services/Arch_Amazon-Elastic-Kubernetes-Service_48.svg" style="width:24px;">
          <span>EKS</span>
        </div>
      </div>
      <div style="font-size:0.7rem; color:rgba(255,255,255,0.6); margin-top:0.5rem;">20 MSA | v1.35 | Karpenter v1.9</div>
    </div>

    <!-- us-west-2 -->
    <div class="card" style="padding:0.8rem; min-width:280px; border-left:3px solid #00cec9;" data-fragment-index="3">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.6rem;">
        <span style="font-size:0.75rem; background:#00cec9; color:#000; padding:2px 8px; border-radius:4px; font-weight:600;">SECONDARY</span>
        <span style="font-weight:600;">us-west-2</span>
      </div>
      <div class="flow-h" style="gap:0.5rem; flex-wrap:wrap;">
        <div class="flow-box" style="padding:0.4rem 0.6rem; font-size:0.75rem;">
          <img src="common/aws-icons/services/Arch_Elastic-Load-Balancing_48.svg" style="width:24px;">
          <span>NLB</span>
        </div>
        <div class="flow-arrow" style="font-size:0.9rem;">→</div>
        <div class="flow-box" style="padding:0.4rem 0.6rem; font-size:0.75rem;">
          <img src="common/aws-icons/services/Arch_Amazon-Elastic-Kubernetes-Service_48.svg" style="width:24px;">
          <span>EKS</span>
        </div>
      </div>
      <div style="font-size:0.7rem; color:rgba(255,255,255,0.6); margin-top:0.5rem;">20 MSA | v1.35 | Karpenter v1.9</div>
    </div>
  </div>

  <div class="flow-arrow" style="font-size:1.2rem;">↓</div>

  <!-- Bottom: Data Layer -->
  <div class="flow-group bg-purple" style="padding:0.8rem 1.2rem;" data-fragment-index="4">
    <div class="flow-group-label">Data Layer (6 Stores)</div>
    <div class="flow-h" style="gap:0.6rem; flex-wrap:wrap; justify-content:center;">
      <div class="icon-item sm" style="min-width:80px;">
        <img src="common/aws-icons/services/Arch_Amazon-Aurora_48.svg">
        <span style="font-size:0.7rem;">Aurora DSQL</span>
      </div>
      <div class="icon-item sm" style="min-width:80px;">
        <img src="common/aws-icons/services/Arch_Amazon-DocumentDB_48.svg">
        <span style="font-size:0.7rem;">DocumentDB</span>
      </div>
      <div class="icon-item sm" style="min-width:80px;">
        <img src="common/aws-icons/services/Arch_Amazon-ElastiCache_48.svg">
        <span style="font-size:0.7rem;">ElastiCache</span>
      </div>
      <div class="icon-item sm" style="min-width:80px;">
        <img src="common/aws-icons/services/Arch_Amazon-MSK_48.svg">
        <span style="font-size:0.7rem;">MSK</span>
      </div>
      <div class="icon-item sm" style="min-width:80px;">
        <img src="common/aws-icons/services/Arch_Amazon-OpenSearch-Service_48.svg">
        <span style="font-size:0.7rem;">OpenSearch</span>
      </div>
      <div class="icon-item sm" style="min-width:80px;">
        <img src="common/aws-icons/services/Arch_Amazon-Simple-Storage-Service_48.svg">
        <span style="font-size:0.7rem;">S3</span>
      </div>
    </div>
  </div>
</div>
:::

:::notes
{timing: 3min}
전체 아키텍처를 한눈에 보겠습니다. 세 계층으로 구성됩니다.

Edge Layer는 CloudFront, WAF, Route53으로 구성됩니다. CloudFront가 글로벌 CDN과 정적 자산 서빙을 담당하고, WAF가 보안 필터링을 수행합니다. Route53은 Latency-based routing으로 사용자를 가장 가까운 리전으로 안내합니다.

Compute Layer는 두 리전에 동일하게 구성됩니다. us-east-1이 Primary, us-west-2가 Secondary입니다. 각 리전에 EKS v1.35 클러스터가 있고, Karpenter v1.9로 노드를 동적 프로비저닝합니다. 20개의 마이크로서비스가 5개 도메인에 걸쳐 배포됩니다.

{cue: pause}
Data Layer는 6종의 데이터 저장소로 구성됩니다. Aurora DSQL은 관계형 데이터를 위한 글로벌 분산 SQL 데이터베이스입니다. DocumentDB는 MongoDB 호환 문서 저장소, ElastiCache는 Valkey 기반 캐시, MSK는 Kafka 호환 이벤트 스트리밍, OpenSearch는 검색과 로그 분석, S3는 오브젝트 스토리지입니다.

이 아키텍처의 핵심 특징은 Write-Primary/Read-Local 패턴입니다. 모든 쓰기는 us-east-1에서 처리되고, 읽기는 각 리전에서 로컬로 처리됩니다. 데이터 복제는 각 서비스별로 적절한 방식을 사용합니다.

{cue: transition}
Write-Primary/Read-Local 패턴을 더 자세히 살펴보겠습니다.
:::

---
<!-- Slide 8: Write-Primary / Read-Local Pattern -->
@type: content

## Write-Primary / Read-Local Pattern

:::html
<div class="flow-v" style="gap:1rem; padding:0.5rem;">
  <!-- Main diagram -->
  <div class="flow-h" style="justify-content:center; gap:2rem; align-items:start;">
    <!-- us-east-1 Primary -->
    <div class="card" style="padding:1rem; min-width:280px; border:2px solid #FF9900;" data-fragment-index="1">
      <div style="text-align:center; margin-bottom:0.8rem;">
        <span style="background:#FF9900; color:#000; padding:4px 12px; border-radius:4px; font-weight:bold;">us-east-1 (Primary)</span>
      </div>
      <div class="flow-v" style="gap:0.6rem;">
        <div class="flow-box bg-orange" style="padding:0.6rem;">
          <span style="font-weight:600;">Write Path</span>
          <span style="font-size:0.75rem; display:block; color:rgba(255,255,255,0.7);">All writes processed here</span>
        </div>
        <div class="flow-box bg-blue" style="padding:0.6rem;">
          <span style="font-weight:600;">Read Path (Local)</span>
          <span style="font-size:0.75rem; display:block; color:rgba(255,255,255,0.7);">US East users read locally</span>
        </div>
        <div style="display:flex; align-items:center; gap:0.5rem; justify-content:center; margin-top:0.5rem;">
          <img src="common/aws-icons/services/Arch_Amazon-Aurora_48.svg" style="width:28px;">
          <span style="font-size:0.8rem;">Primary Writer</span>
        </div>
      </div>
    </div>

    <!-- Replication arrows -->
    <div class="flow-v" style="justify-content:center; gap:0.5rem;" data-fragment-index="2">
      <div style="text-align:center;">
        <div style="font-size:0.75rem; color:rgba(255,255,255,0.6);">Async Replication</div>
        <div style="font-size:1.5rem;">→</div>
        <div style="font-size:0.7rem; color:#00d68f;">< 1s lag</div>
      </div>
      <div style="text-align:center; margin-top:1rem;">
        <div style="font-size:0.75rem; color:rgba(255,255,255,0.6);">Write Forwarding</div>
        <div style="font-size:1.5rem;">←</div>
        <div style="font-size:0.7rem; color:#FF9900;">Transparent to app</div>
      </div>
    </div>

    <!-- us-west-2 Secondary -->
    <div class="card" style="padding:1rem; min-width:280px; border:2px solid #00cec9;" data-fragment-index="3">
      <div style="text-align:center; margin-bottom:0.8rem;">
        <span style="background:#00cec9; color:#000; padding:4px 12px; border-radius:4px; font-weight:bold;">us-west-2 (Secondary)</span>
      </div>
      <div class="flow-v" style="gap:0.6rem;">
        <div class="flow-box" style="padding:0.6rem; background:rgba(255,153,0,0.1); border:1px dashed rgba(255,153,0,0.5);">
          <span style="font-weight:600; color:#FF9900;">Write Forwarding</span>
          <span style="font-size:0.75rem; display:block; color:rgba(255,255,255,0.7);">Writes forwarded to Primary</span>
        </div>
        <div class="flow-box bg-blue" style="padding:0.6rem;">
          <span style="font-weight:600;">Read Path (Local)</span>
          <span style="font-size:0.75rem; display:block; color:rgba(255,255,255,0.7);">US West users read locally</span>
        </div>
        <div style="display:flex; align-items:center; gap:0.5rem; justify-content:center; margin-top:0.5rem;">
          <img src="common/aws-icons/services/Arch_Amazon-Aurora_48.svg" style="width:28px;">
          <span style="font-size:0.8rem;">Read Replica</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Benefits -->
  <div class="col-3" style="gap:0.8rem; margin-top:0.5rem;" data-fragment-index="4">
    <div class="card" style="padding:0.6rem; text-align:center;">
      <div style="font-weight:600; color:#00d68f;">No Conflict</div>
      <div style="font-size:0.75rem; color:rgba(255,255,255,0.7);">단일 쓰기 지점 → 충돌 없음</div>
    </div>
    <div class="card" style="padding:0.6rem; text-align:center;">
      <div style="font-weight:600; color:#3B82F6;">Low Read Latency</div>
      <div style="font-size:0.75rem; color:rgba(255,255,255,0.7);">로컬 읽기 → 최적 지연</div>
    </div>
    <div class="card" style="padding:0.6rem; text-align:center;">
      <div style="font-weight:600; color:#FF9900;">Simple Code</div>
      <div style="font-size:0.75rem; color:rgba(255,255,255,0.7);">Aurora가 포워딩 처리</div>
    </div>
  </div>
</div>
:::

:::notes
{timing: 3min}
Write-Primary/Read-Local 패턴을 상세히 보겠습니다.

이 패턴에서 모든 쓰기는 Primary 리전인 us-east-1에서 처리됩니다. Secondary 리전에서 쓰기 요청이 들어오면, Aurora의 Write Forwarding 기능이 자동으로 Primary로 전달합니다. 애플리케이션 코드는 이를 알 필요가 없습니다.

읽기는 각 리전에서 로컬로 처리됩니다. us-east-1 사용자는 us-east-1의 Primary에서, us-west-2 사용자는 us-west-2의 Read Replica에서 읽습니다. 이렇게 하면 읽기 Latency가 최소화됩니다.

{cue: pause}
비동기 복제 lag은 보통 1초 미만입니다. 대부분의 사용 사례에서 이 정도는 허용됩니다. 사용자가 상품을 주문하고 주문 내역을 바로 확인할 때, 1초 지연은 인지하기 어렵습니다.

이 패턴의 장점은 세 가지입니다.

첫째, No Conflict — 단일 쓰기 지점이므로 데이터 충돌이 없습니다. Active-Active에서 겪는 동시 쓰기 충돌 문제를 원천적으로 방지합니다.

둘째, Low Read Latency — 읽기는 항상 로컬에서 처리되므로 사용자에게 최적의 응답 시간을 제공합니다.

셋째, Simple Code — Aurora Write Forwarding이 복잡한 라우팅 로직을 대신 처리합니다. 개발자는 단순히 로컬 엔드포인트에 연결하면 됩니다.

단점도 있습니다. 쓰기가 많은 워크로드에서는 Primary 리전에 부하가 집중됩니다. 이 경우 샤딩이나 다른 분산 전략이 필요할 수 있습니다.

{cue: transition}
이제 리전별 배포 구성을 살펴보겠습니다.
:::

---
<!-- Slide 9: Regional Deployment -->
@type: content
@layout: two-column

## Regional Deployment

::: left
### us-east-1 (Primary)

:::click
**EKS Cluster**
- Version: v1.35 (v1.35.2-eks-f69f56f)
- Karpenter: v1.9
- Node Capacity: 500 vCPU max
:::

:::click
**20 Microservices**
| Domain | Services | Language |
|--------|----------|----------|
| Core | 6 | Go, Java |
| User | 4 | Python |
| Fulfillment | 3 | Java |
| Business | 4 | Python |
| Platform | 3 | Go |
:::
:::

::: right
### us-west-2 (Secondary)

:::click
**EKS Cluster**
- Version: v1.35 (identical)
- Karpenter: v1.9
- Node Capacity: 500 vCPU max
:::

:::click
**Service Distribution**
- 동일한 20개 서비스 배포
- ArgoCD로 GitOps 동기화
- Identical image tags
:::

:::click
**5 Domains**
- **Core**: product-catalog, inventory, cart, order, payment, search
- **User**: user-account, user-profile, wishlist, review
- **Fulfillment**: shipping, returns, warehouse
- **Business**: notification, recommendation, seller, pricing
- **Platform**: api-gateway, event-bus, auth
:::
:::

:::notes
{timing: 3min}
리전별 배포 구성을 보겠습니다.

양쪽 리전의 EKS 클러스터는 동일하게 구성됩니다. 버전 v1.35, Karpenter v1.9, 최대 500 vCPU 용량입니다. 동일한 버전을 유지하는 것이 중요합니다. 버전이 다르면 동작 차이가 발생할 수 있고, 디버깅이 어려워집니다.

20개 마이크로서비스가 5개 도메인에 분산되어 있습니다. Core 도메인은 쇼핑몰의 핵심 기능 — product-catalog, inventory, cart, order, payment, search입니다. Go와 Java로 구현되어 있고, 성능과 안정성이 가장 중요한 서비스들입니다.

User 도메인은 사용자 관련 기능입니다. user-account, user-profile, wishlist, review — 주로 Python/FastAPI로 구현했습니다. CRUD 위주의 로직이어서 Python의 생산성이 장점입니다.

{cue: pause}
Fulfillment 도메인은 주문 처리와 배송입니다. shipping, returns, warehouse — Java/Spring Boot로 구현했습니다. 외부 시스템 연동이 많고, 트랜잭션 관리가 필요해서 Java의 엔터프라이즈 기능을 활용합니다.

Business 도메인은 부가 기능입니다. notification, recommendation, seller, pricing — Python으로 빠르게 개발하고 실험합니다.

Platform 도메인은 공통 인프라입니다. api-gateway, event-bus, auth — Go로 높은 성능과 낮은 리소스 사용을 달성합니다.

ArgoCD를 통해 양쪽 리전에 동일한 코드가 배포됩니다. Git 리포지토리가 Single Source of Truth이고, 어느 한 쪽만 업데이트하는 실수를 방지합니다.

{cue: transition}
이제 VPC 설계를 살펴보겠습니다.
:::

---
<!-- Slide 10: VPC Design -->
@type: content

## VPC Design

:::html
<div class="col-2" style="gap:1.5rem; align-items:start;">
  <!-- us-east-1 -->
  <div class="card" style="padding:1rem;" data-fragment-index="1">
    <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.8rem;">
      <img src="common/aws-icons/services/Arch_Amazon-Virtual-Private-Cloud_48.svg" style="width:32px;">
      <h4 style="margin:0; color:#FF9900;">us-east-1 VPC</h4>
    </div>
    <div style="font-family:monospace; font-size:1rem; background:rgba(0,0,0,0.3); padding:0.6rem; border-radius:4px; margin-bottom:0.8rem; text-align:center;">
      <span style="color:#00d68f; font-weight:bold;">10.0.0.0/16</span>
    </div>
    <div style="font-size:0.8rem; color:rgba(255,255,255,0.7);">
      <div>• 65,536 IP addresses</div>
      <div>• 3 Availability Zones</div>
      <div>• Non-overlapping with us-west-2</div>
    </div>
  </div>

  <!-- us-west-2 -->
  <div class="card" style="padding:1rem;" data-fragment-index="2">
    <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.8rem;">
      <img src="common/aws-icons/services/Arch_Amazon-Virtual-Private-Cloud_48.svg" style="width:32px;">
      <h4 style="margin:0; color:#00cec9;">us-west-2 VPC</h4>
    </div>
    <div style="font-family:monospace; font-size:1rem; background:rgba(0,0,0,0.3); padding:0.6rem; border-radius:4px; margin-bottom:0.8rem; text-align:center;">
      <span style="color:#00d68f; font-weight:bold;">10.1.0.0/16</span>
    </div>
    <div style="font-size:0.8rem; color:rgba(255,255,255,0.7);">
      <div>• 65,536 IP addresses</div>
      <div>• 3 Availability Zones</div>
      <div>• Non-overlapping with us-east-1</div>
    </div>
  </div>
</div>

<!-- Key point -->
<div style="background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); border-radius:8px; padding:0.8rem; margin-top:1rem; text-align:center;" data-fragment-index="3">
  <strong style="color:#EF4444;">Critical</strong>: CIDR 겹침 방지 — Transit Gateway 피어링 필수 조건
</div>
:::

:::notes
{timing: 2min}
VPC CIDR 설계를 보겠습니다.

두 리전의 VPC는 겹치지 않는 CIDR 블록을 사용합니다. us-east-1은 10.0.0.0/16, us-west-2는 10.1.0.0/16입니다. 각각 65,536개의 IP 주소를 제공합니다.

왜 겹치지 않아야 하는가? Transit Gateway나 VPC Peering으로 두 VPC를 연결하면 라우팅 테이블이 합쳐집니다. CIDR이 겹치면 "10.0.5.10으로 가라"는 패킷이 어느 VPC로 가야 할지 모호해집니다. 라우팅이 불가능해지는 것이죠.

{cue: pause}
/16을 선택한 이유는 충분한 확장성 때문입니다. EKS에서 각 Pod는 VPC IP를 할당받습니다. 서비스 20개, 각 서비스당 평균 10 Pod, 3 AZ 분산이면 600개 IP가 필요합니다. 스케일링과 업데이트 중 추가 IP를 고려하면 수천 개가 필요합니다. /16이면 65,536개로 충분합니다.

미래 확장도 고려했습니다. 10.0.0.0/16, 10.1.0.0/16 다음에 10.2.0.0/16, 10.3.0.0/16으로 추가 리전을 쉽게 확장할 수 있습니다.

{cue: transition}
서브넷 구조를 더 자세히 보겠습니다.
:::

---
<!-- Slide 11: 3-Tier Subnet Architecture -->
@type: content

## 3-Tier Subnet Architecture

:::html
<div class="flow-v" style="gap:0.8rem; padding:0.5rem;">
  <!-- Subnet tiers -->
  <div class="flow-h" style="justify-content:center; gap:1rem;">
    <!-- Public -->
    <div class="card" style="padding:0.8rem; min-width:200px; border-left:3px solid #FF9900;" data-fragment-index="1">
      <h4 style="margin:0 0 0.5rem 0; color:#FF9900;">Public Tier</h4>
      <div style="font-size:0.8rem; color:rgba(255,255,255,0.8); margin-bottom:0.5rem;">
        <div><code>10.x.0.0/20</code> (AZ-a)</div>
        <div><code>10.x.16.0/20</code> (AZ-b)</div>
        <div><code>10.x.32.0/20</code> (AZ-c)</div>
      </div>
      <div style="font-size:0.75rem; color:rgba(255,255,255,0.6);">
        <strong>Resources:</strong>
        <div>• ALB / NLB</div>
        <div>• NAT Gateway</div>
        <div>• Bastion (if any)</div>
      </div>
    </div>

    <!-- Private -->
    <div class="card" style="padding:0.8rem; min-width:200px; border-left:3px solid #3B82F6;" data-fragment-index="2">
      <h4 style="margin:0 0 0.5rem 0; color:#3B82F6;">Private Tier</h4>
      <div style="font-size:0.8rem; color:rgba(255,255,255,0.8); margin-bottom:0.5rem;">
        <div><code>10.x.48.0/20</code> (AZ-a)</div>
        <div><code>10.x.64.0/20</code> (AZ-b)</div>
        <div><code>10.x.80.0/20</code> (AZ-c)</div>
      </div>
      <div style="font-size:0.75rem; color:rgba(255,255,255,0.6);">
        <strong>Resources:</strong>
        <div>• EKS Worker Nodes</div>
        <div>• Application Pods</div>
        <div>• Internal services</div>
      </div>
    </div>

    <!-- Data -->
    <div class="card" style="padding:0.8rem; min-width:200px; border-left:3px solid #A855F7;" data-fragment-index="3">
      <h4 style="margin:0 0 0.5rem 0; color:#A855F7;">Data Tier</h4>
      <div style="font-size:0.8rem; color:rgba(255,255,255,0.8); margin-bottom:0.5rem;">
        <div><code>10.x.96.0/20</code> (AZ-a)</div>
        <div><code>10.x.112.0/20</code> (AZ-b)</div>
        <div><code>10.x.128.0/20</code> (AZ-c)</div>
      </div>
      <div style="font-size:0.75rem; color:rgba(255,255,255,0.6);">
        <strong>Resources:</strong>
        <div>• Aurora, DocumentDB</div>
        <div>• ElastiCache, MSK</div>
        <div>• OpenSearch</div>
      </div>
    </div>
  </div>

  <!-- AZ distribution visualization -->
  <div style="background:rgba(255,255,255,0.05); border-radius:8px; padding:0.8rem; margin-top:0.5rem;" data-fragment-index="4">
    <div style="font-size:0.8rem; font-weight:600; margin-bottom:0.5rem;">3 AZ Distribution (per region)</div>
    <div class="flow-h" style="gap:0.5rem; justify-content:center;">
      <div style="background:rgba(255,153,0,0.2); padding:0.4rem 0.8rem; border-radius:4px; font-size:0.75rem; text-align:center;">
        <div style="font-weight:600;">AZ-a</div>
        <div style="color:rgba(255,255,255,0.6);">Public + Private + Data</div>
      </div>
      <div style="background:rgba(59,130,246,0.2); padding:0.4rem 0.8rem; border-radius:4px; font-size:0.75rem; text-align:center;">
        <div style="font-weight:600;">AZ-b</div>
        <div style="color:rgba(255,255,255,0.6);">Public + Private + Data</div>
      </div>
      <div style="background:rgba(168,85,247,0.2); padding:0.4rem 0.8rem; border-radius:4px; font-size:0.75rem; text-align:center;">
        <div style="font-weight:600;">AZ-c</div>
        <div style="color:rgba(255,255,255,0.6);">Public + Private + Data</div>
      </div>
    </div>
    <div style="font-size:0.7rem; color:rgba(255,255,255,0.5); text-align:center; margin-top:0.5rem;">
      Total: 9 subnets per region × 2 regions = 18 subnets
    </div>
  </div>
</div>
:::

:::notes
{timing: 3min}
3-Tier 서브넷 구조를 보겠습니다.

Public Tier는 인터넷과 직접 통신하는 리소스를 위한 서브넷입니다. ALB/NLB, NAT Gateway가 여기에 위치합니다. 각 AZ당 하나씩, 총 3개 서브넷입니다. /20이므로 각각 4,096개 IP를 제공합니다.

Private Tier는 EKS Worker Node와 애플리케이션 Pod가 위치합니다. 인터넷에서 직접 접근할 수 없고, NAT Gateway를 통해서만 아웃바운드 통신이 가능합니다. 대부분의 컴퓨팅 리소스가 여기 있으므로 가장 많은 IP가 필요합니다.

Data Tier는 데이터베이스와 캐시가 위치합니다. Aurora, DocumentDB, ElastiCache, MSK, OpenSearch — 모든 데이터 저장소가 이 티어에 격리됩니다. Private Tier에서만 접근 가능하고, 직접 인터넷 통신은 불가능합니다.

{cue: pause}
왜 3-Tier로 분리하는가? 보안과 네트워크 정책 관리를 위해서입니다.

Security Group과 Network ACL을 티어별로 다르게 적용할 수 있습니다. Data Tier는 3306(MySQL), 27017(MongoDB), 6379(Redis) 등 데이터베이스 포트만 Private Tier에서 허용합니다.

또한 Compliance 요구사항을 충족합니다. 많은 규정이 데이터베이스를 별도 네트워크 세그먼트에 격리하도록 요구합니다. 3-Tier 구조가 이를 자연스럽게 충족합니다.

각 리전에 9개 서브넷, 양쪽 합쳐서 18개 서브넷입니다. Terraform이나 CloudFormation으로 관리하면 복잡해 보이는 구조도 쉽게 프로비저닝할 수 있습니다.

{cue: transition}
리전 간 연결 방법을 살펴보겠습니다.
:::

---
<!-- Slide 12: Transit Gateway Peering -->
@type: content

## Transit Gateway Peering

:::html
<div class="flow-v" style="gap:1rem; padding:0.5rem;">
  <!-- Main diagram -->
  <div class="flow-h" style="justify-content:center; align-items:center; gap:2rem;">
    <!-- us-east-1 TGW -->
    <div class="card" style="padding:0.8rem; min-width:180px; text-align:center;" data-fragment-index="1">
      <img src="common/aws-icons/services/Arch_AWS-Transit-Gateway_48.svg" style="width:48px; margin-bottom:0.5rem;">
      <div style="font-weight:600;">TGW (us-east-1)</div>
      <div style="font-size:0.75rem; color:rgba(255,255,255,0.6); margin-top:0.3rem;">
        VPC Attachment<br>+ Peering Attachment
      </div>
    </div>

    <!-- Connection -->
    <div class="flow-v" style="align-items:center; gap:0.3rem;" data-fragment-index="2">
      <div style="font-size:0.7rem; color:#00d68f;">AWS Backbone</div>
      <div style="display:flex; align-items:center; gap:0.5rem;">
        <div style="width:80px; height:3px; background:linear-gradient(90deg, #FF9900, #00cec9);"></div>
        <span style="font-size:1.2rem;">⟷</span>
        <div style="width:80px; height:3px; background:linear-gradient(90deg, #00cec9, #FF9900);"></div>
      </div>
      <div style="font-size:0.65rem; color:rgba(255,255,255,0.5);">Encrypted, ECMP enabled</div>
    </div>

    <!-- us-west-2 TGW -->
    <div class="card" style="padding:0.8rem; min-width:180px; text-align:center;" data-fragment-index="3">
      <img src="common/aws-icons/services/Arch_AWS-Transit-Gateway_48.svg" style="width:48px; margin-bottom:0.5rem;">
      <div style="font-weight:600;">TGW (us-west-2)</div>
      <div style="font-size:0.75rem; color:rgba(255,255,255,0.6); margin-top:0.3rem;">
        VPC Attachment<br>+ Peering Attachment
      </div>
    </div>
  </div>

  <!-- Features grid -->
  <div class="col-2" style="gap:1rem; margin-top:0.5rem;" data-fragment-index="4">
    <div class="card" style="padding:0.8rem;">
      <h4 style="margin:0 0 0.5rem 0; color:#00d68f;">Benefits</h4>
      <div style="font-size:0.8rem; line-height:1.6;">
        <div>• <strong>ECMP</strong>: Equal-Cost Multi-Path routing for bandwidth</div>
        <div>• <strong>Centralized</strong>: Single routing table, easier management</div>
        <div>• <strong>Scalable</strong>: Add more VPCs without mesh complexity</div>
        <div>• <strong>Encrypted</strong>: All traffic encrypted on AWS backbone</div>
      </div>
    </div>
    <div class="card" style="padding:0.8rem;">
      <h4 style="margin:0 0 0.5rem 0; color:#FF9900;">Route Table Example</h4>
      <div class="code-block" style="font-size:0.7rem; padding:0.5rem;">
<span class="comment"># us-east-1 TGW Route Table</span>
<span class="key">10.0.0.0/16</span> → VPC Attachment (local)
<span class="key">10.1.0.0/16</span> → Peering Attachment (us-west-2)

<span class="comment"># us-west-2 TGW Route Table</span>
<span class="key">10.1.0.0/16</span> → VPC Attachment (local)
<span class="key">10.0.0.0/16</span> → Peering Attachment (us-east-1)</div>
    </div>
  </div>
</div>
:::

:::notes
{timing: 3min}
Transit Gateway Peering으로 두 리전을 연결합니다.

각 리전에 Transit Gateway를 생성하고, Peering Attachment로 연결합니다. 트래픽은 AWS 백본 네트워크를 통해 전달됩니다. 인터넷을 거치지 않으므로 보안과 Latency 면에서 유리합니다.

왜 VPC Peering 대신 Transit Gateway를 선택했는가? 세 가지 이유가 있습니다.

첫째, ECMP(Equal-Cost Multi-Path) 지원입니다. Transit Gateway는 여러 경로로 트래픽을 분산해서 대역폭을 늘릴 수 있습니다. VPC Peering은 단일 경로만 지원합니다.

둘째, 중앙집중식 라우팅입니다. VPC가 많아지면 VPC Peering은 N×(N-1)/2 개의 연결이 필요합니다. 5개 VPC면 10개 Peering입니다. Transit Gateway는 허브-스포크 구조로 N개 연결만 필요합니다.

셋째, 확장성입니다. 새 VPC를 추가할 때 Transit Gateway에 Attachment만 추가하면 됩니다. 기존 모든 VPC와 자동으로 통신 가능해집니다.

{cue: pause}
Route Table을 보면, us-east-1의 TGW는 10.0.0.0/16(자기 VPC)은 VPC Attachment로, 10.1.0.0/16(상대 VPC)은 Peering Attachment로 라우팅합니다. us-west-2도 대칭적으로 구성합니다.

모든 트래픽은 AWS 백본에서 암호화됩니다. 별도 VPN이나 IPSec 설정 없이도 보안이 보장됩니다.

{cue: transition}
VPC Endpoints 전략을 살펴보겠습니다.
:::

---
<!-- Slide 13: VPC Endpoints Strategy -->
@type: content
@layout: two-column

## VPC Endpoints Strategy

::: left
### Gateway Endpoints (Free)

:::click
**S3 Gateway Endpoint**
- ECR 이미지 레이어 저장소
- Application 로그 아카이브
- 정적 자산 버킷

```
Cost Savings:
NAT GW: $0.045/GB + $0.045/hr
Gateway Endpoint: $0 ✓
```
:::
:::

::: right
### Interface Endpoints (PrivateLink)

:::click
**ECR Endpoints** (2개)
- `ecr.api` — API calls
- `ecr.dkr` — Image pulls
- 비용: ~$7.2/endpoint/month

**STS Endpoint**
- IRSA token exchange
- Pod identity validation
- 비용: ~$7.2/month

**CloudWatch Logs Endpoint**
- Container logs
- Application telemetry
- 비용: ~$7.2/month
:::

:::click
### Cost Analysis (Monthly)

| Item | Without EP | With EP |
|------|-----------|---------|
| NAT GW data | $450 | $50 |
| Endpoints | $0 | $29 |
| **Total** | $450 | $79 |

**Savings: ~82%**
:::
:::

:::notes
{timing: 3min}
VPC Endpoints 전략을 보겠습니다. 비용 절감과 보안 강화 두 가지 목적이 있습니다.

Gateway Endpoint는 S3와 DynamoDB에 사용할 수 있고, 무료입니다. S3 Gateway Endpoint가 가장 중요합니다. EKS에서 ECR 이미지를 Pull할 때 실제 이미지 레이어는 S3에 저장되어 있습니다. Gateway Endpoint 없이는 모든 이미지 Pull이 NAT Gateway를 거쳐서 GB당 $0.045의 데이터 전송 비용이 발생합니다.

대형 컨테이너 이미지가 많고 스케일링이 자주 일어나면 이 비용이 상당합니다. 월 10TB 전송이면 $450입니다. Gateway Endpoint를 설정하면 $0입니다.

{cue: pause}
Interface Endpoint는 PrivateLink 기반으로 비용이 발생하지만, 필수적인 것들이 있습니다.

ECR Endpoint는 두 개가 필요합니다. ecr.api는 이미지 매니페스트 조회용, ecr.dkr는 실제 이미지 Pull용입니다. 이것 없이 NAT Gateway로 ECR 통신하면 속도도 느리고 비용도 높습니다.

STS Endpoint는 IRSA에 필수입니다. Pod가 IAM Role을 assume할 때 STS AssumeRoleWithWebIdentity를 호출합니다. 이 트래픽이 NAT Gateway를 거치면 불필요한 비용이 발생합니다.

CloudWatch Logs Endpoint는 컨테이너 로그 전송에 사용됩니다. 로그 볼륨이 크면 NAT Gateway 비용이 상당해집니다.

비용 분석을 보면, Endpoint 없이 월 $450이던 비용이 Endpoint 도입 후 $79로 줄어듭니다. 82% 절감입니다. Interface Endpoint 비용 $29를 내더라도 충분히 이득입니다.

{cue: transition}
주요 아키텍처 결정들을 요약하겠습니다.
:::

---
<!-- Slide 14: Architecture Decisions Summary -->
@type: content

## Architecture Decisions Summary

:::html
<table class="data-table" style="width:100%; font-size:0.78rem;">
  <thead>
    <tr style="background:var(--bg-card);">
      <th style="padding:8px 10px; text-align:left; width:22%;">Decision</th>
      <th style="padding:8px 10px; text-align:left; width:28%;">Choice</th>
      <th style="padding:8px 10px; text-align:left;">Rationale</th>
    </tr>
  </thead>
  <tbody>
    <tr data-fragment-index="1">
      <td style="padding:6px 10px;">Data Pattern</td>
      <td style="padding:6px 10px;"><strong>Write-Primary / Read-Local</strong></td>
      <td style="padding:6px 10px; color:var(--text-secondary);">No conflict, Aurora handles forwarding</td>
    </tr>
    <tr style="background:var(--bg-card);" data-fragment-index="2">
      <td style="padding:6px 10px;">Cross-region</td>
      <td style="padding:6px 10px;"><strong>Transit Gateway</strong></td>
      <td style="padding:6px 10px; color:var(--text-secondary);">ECMP, centralized routing, scalability</td>
    </tr>
    <tr data-fragment-index="3">
      <td style="padding:6px 10px;">Ingress</td>
      <td style="padding:6px 10px;"><strong>CloudFront-only</strong></td>
      <td style="padding:6px 10px; color:var(--text-secondary);">No direct ALB, WAF integration, global edge</td>
    </tr>
    <tr style="background:var(--bg-card);" data-fragment-index="4">
      <td style="padding:6px 10px;">IAM</td>
      <td style="padding:6px 10px;"><strong>IRSA everywhere</strong></td>
      <td style="padding:6px 10px; color:var(--text-secondary);">Least privilege, no shared node role</td>
    </tr>
    <tr data-fragment-index="5">
      <td style="padding:6px 10px;">Node Provisioning</td>
      <td style="padding:6px 10px;"><strong>Karpenter 6-pool</strong></td>
      <td style="padding:6px 10px; color:var(--text-secondary);">Workload-specific, cost/availability balance</td>
    </tr>
    <tr style="background:var(--bg-card);" data-fragment-index="6">
      <td style="padding:6px 10px;">Service Discovery</td>
      <td style="padding:6px 10px;"><strong>DNS-based</strong></td>
      <td style="padding:6px 10px; color:var(--text-secondary);">Simpler ops, sufficient for current scale</td>
    </tr>
    <tr data-fragment-index="7">
      <td style="padding:6px 10px;">Autoscaling</td>
      <td style="padding:6px 10px;"><strong>KEDA + HPA dual</strong></td>
      <td style="padding:6px 10px; color:var(--text-secondary);">Event-driven + metric-driven scaling</td>
    </tr>
    <tr style="background:var(--bg-card);" data-fragment-index="8">
      <td style="padding:6px 10px;">GitOps</td>
      <td style="padding:6px 10px;"><strong>ArgoCD App-of-apps</strong></td>
      <td style="padding:6px 10px; color:var(--text-secondary);">Declarative, audit trail, multi-cluster</td>
    </tr>
    <tr data-fragment-index="9">
      <td style="padding:6px 10px;">Encryption</td>
      <td style="padding:6px 10px;"><strong>Per-service KMS</strong></td>
      <td style="padding:6px 10px; color:var(--text-secondary);">Isolation, granular rotation, blast radius</td>
    </tr>
    <tr style="background:var(--bg-card);" data-fragment-index="10">
      <td style="padding:6px 10px;">Network</td>
      <td style="padding:6px 10px;"><strong>3-tier subnets</strong></td>
      <td style="padding:6px 10px; color:var(--text-secondary);">Security segmentation, compliance</td>
    </tr>
  </tbody>
</table>
:::

:::notes
{timing: 2min}
10가지 주요 아키텍처 결정을 요약합니다.

Write-Primary/Read-Local 패턴은 데이터 충돌을 방지하고 Aurora Write Forwarding으로 구현을 단순화합니다.

Transit Gateway는 VPC Peering 대신 선택했습니다. ECMP 지원, 중앙집중식 라우팅, 확장성이 장점입니다.

CloudFront-only 인그레스는 보안의 핵심입니다. 모든 트래픽이 WAF를 거치도록 강제합니다.

IRSA를 모든 서비스에 적용해서 최소 권한 원칙을 구현합니다. Node Role에 광범위한 권한을 주는 것을 피합니다.

{cue: pause}
Karpenter 6-pool 전략은 워크로드별로 최적화된 노드를 제공합니다. critical 풀은 On-Demand만, batch 풀은 Spot만 사용합니다.

DNS 기반 Service Discovery는 Service Mesh보다 단순합니다. 현재 규모에서는 충분합니다.

KEDA와 HPA를 함께 사용해서 이벤트 기반과 메트릭 기반 스케일링을 모두 지원합니다.

ArgoCD App-of-apps로 모든 배포를 Git에서 관리합니다. 양쪽 리전에 동일한 코드가 일관되게 배포됩니다.

Per-service KMS 키로 암호화를 분리하고, 3-tier 서브넷으로 네트워크를 세그먼트합니다.

{cue: transition}
이 블록의 핵심 내용을 정리하겠습니다.
:::

---
<!-- Slide 15: Key Takeaways -->
@type: content

## Key Takeaways

:::click
### Multi-Region Fundamentals
- **Business Drivers**: Latency reduction, 99.99%+ availability, 10x scalability, data residency
- **Pattern Choice**: Active-Active vs Active-Passive → Write-Primary/Read-Local as hybrid
- **CAP Trade-off**: Aurora DSQL (CP) for transactions, DynamoDB/ElastiCache (AP) for caching
:::

:::click
### Network Foundation
- **Non-overlapping CIDR**: us-east-1 = 10.0.0.0/16, us-west-2 = 10.1.0.0/16
- **3-Tier Subnets**: Public (ALB/NAT) / Private (EKS) / Data (Aurora/Cache) across 3 AZs
- **Transit Gateway Peering**: ECMP enabled, encrypted AWS backbone, centralized routing
:::

:::click
### Cost & Security Optimization
- **VPC Endpoints**: S3 Gateway (free) + ECR/STS/CW Logs Interface → 82% NAT cost savings
- **Security Layers**: CloudFront-only ingress, prefix-list SGs, IRSA, per-service KMS
:::

:::click
### Next: Data Sync & Replication
- Aurora DSQL distributed transactions
- DocumentDB Global Clusters
- ElastiCache Global Datastore
- MSK Cross-region Replication
:::

:::notes
{timing: 2min}
이 블록의 핵심 내용을 정리합니다.

Multi-Region Fundamentals에서 기억할 점은, 비즈니스 요구사항을 먼저 파악하고 적절한 패턴을 선택해야 한다는 것입니다. Write-Primary/Read-Local은 Active-Active와 Active-Passive의 장점을 조합한 실용적인 선택입니다. CAP Theorem에서 모든 것을 만족할 수 없으므로, 데이터 유형별로 적절한 consistency 모델을 선택합니다.

Network Foundation은 겹치지 않는 CIDR이 핵심입니다. 처음 설계할 때 충분한 IP 공간과 미래 확장을 고려하세요. 3-Tier 서브넷 구조는 보안과 컴플라이언스 요구사항을 자연스럽게 충족합니다. Transit Gateway Peering은 확장 가능하고 관리하기 쉬운 크로스 리전 연결을 제공합니다.

Cost와 Security 최적화에서 VPC Endpoints는 필수입니다. 특히 S3 Gateway Endpoint는 무료이면서 큰 비용 절감 효과가 있습니다. CloudFront-only 인그레스와 IRSA는 보안의 기본입니다.

{cue: pause}
다음 블록에서는 Data Sync & Replication을 다룹니다. Aurora DSQL의 분산 트랜잭션, DocumentDB Global Clusters, ElastiCache Global Datastore, MSK Cross-region Replication — 각 데이터 저장소가 어떻게 복제되는지 상세히 살펴봅니다.

{cue: transition}
질문 있으시면 지금 받겠습니다.
:::

---
<!-- Slide 16: Quiz -->
@type: quiz

## Knowledge Check

**Q1: Write-Primary / Read-Local 패턴에서 Secondary 리전의 Write 요청은 어떻게 처리되나요?**
- [ ] 거부됨 (Write는 Primary에서만 가능)
- [x] Aurora Write Forwarding으로 Primary에 자동 전달
- [ ] Secondary에서 로컬 처리 후 비동기 동기화
- [ ] 충돌 해결 후 양쪽에 모두 저장

**Q2: Transit Gateway Peering을 VPC Peering 대신 선택한 주요 이유는?**
- [ ] 더 저렴한 비용
- [ ] 더 낮은 Latency
- [x] ECMP 지원과 중앙집중식 라우팅 관리
- [ ] VPC Peering은 cross-region을 지원하지 않음

**Q3: 두 리전의 VPC CIDR이 겹치면 안 되는 이유는?**
- [ ] AWS 정책 위반
- [x] 라우팅 테이블에서 목적지가 모호해짐
- [ ] VPC Endpoint가 동작하지 않음
- [ ] IRSA가 올바르게 작동하지 않음

**Q4: VPC Endpoints로 NAT Gateway 비용을 ~82% 절감할 수 있었던 주요 서비스는?**
- [ ] EC2, Lambda, SQS
- [ ] Route53, CloudFront, WAF
- [x] S3, ECR, STS, CloudWatch Logs
- [ ] Aurora, DynamoDB, ElastiCache

:::notes
{timing: 3min}
이 블록에서 배운 내용을 확인하는 퀴즈입니다.

첫 번째 문제는 Write-Primary/Read-Local 패턴입니다. Secondary 리전에서 Write 요청이 들어오면 Aurora Write Forwarding이 자동으로 Primary로 전달합니다. 애플리케이션 코드 변경 없이 투명하게 처리됩니다.

두 번째 문제는 Transit Gateway 선택 이유입니다. 핵심은 ECMP 지원과 중앙집중식 라우팅입니다. VPC Peering도 cross-region을 지원하지만, 허브-스포크 구조가 아니어서 VPC가 많아지면 관리가 복잡해집니다.

세 번째 문제는 CIDR 설계의 기본입니다. CIDR이 겹치면 라우팅 테이블에서 목적지가 모호해집니다. 10.0.5.10이 어느 VPC인지 알 수 없게 됩니다.

네 번째 문제는 VPC Endpoints 비용 절감입니다. S3, ECR, STS, CloudWatch Logs — 이 네 가지가 EKS 운영에서 가장 트래픽이 많은 AWS 서비스입니다. Gateway Endpoint(S3)는 무료이고, Interface Endpoint(ECR, STS, CW Logs)는 NAT Gateway보다 훨씬 저렴합니다.

{cue: pause}
모든 문제를 맞추셨나요? 틀린 부분이 있으면 해당 슬라이드를 다시 복습해 보세요.

{cue: transition}
수고하셨습니다. 다음 블록에서는 Data Sync & Replication을 다룹니다.
:::

---
<!-- Slide 17: Thank You -->
@type: thankyou

## Thank You

Block 1 — Multi-Region Foundation 완료

[← 목차로 돌아가기](index.html) | [다음: Block 2 — Data Sync & Replication →](02-data-sync.html)

:::notes
{timing: 30sec}
첫 번째 블록을 마칩니다.

멀티리전 아키텍처의 기본 개념, Write-Primary/Read-Local 패턴, VPC 설계, Transit Gateway 연결, VPC Endpoints 전략을 살펴봤습니다.

다음 블록에서는 Aurora DSQL, DocumentDB, ElastiCache, MSK 등 데이터 계층의 복제 전략을 상세히 다룹니다.

5분 휴식 후 계속하겠습니다.
:::
