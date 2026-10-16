---
remarp: true
block: 01-foundation
---

---
<!-- Slide 1: 세션 커버 -->
@type: cover

# Multi-Region Architecture Deep Dive

두 리전에서 하나의 서비스처럼 동작하는 아키텍처 설계

Block 1: Multi-Region Foundation | 30분

:::notes
{timing: 0.5min}
[요약]
- 오늘 세션은 총 5개 블록, 각 30분으로 구성됩니다.
- 첫 블록은 "왜 멀티리전인가, 어떤 패턴을 고르는가, 네트워크 바닥을 어떻게 까는가"를 다룹니다.
- 기준일은 2026년 10월 15일이며, 예시 시나리오는 us-east-1 primary, us-west-2 secondary 이커머스입니다.

안녕하세요. 오늘은 멀티리전 아키텍처를 다섯 블록에 걸쳐 깊게 다룹니다. 예시는 주문, 결제, 카탈로그, 장바구니 서비스를 가진 이커머스이고, us-east-1을 primary, us-west-2를 secondary로 운영하는 구성입니다.
첫 블록에서는 멀티리전을 왜 하는지, Active-Active와 Active-Passive 중 무엇을 고르는지, 그리고 그 결정을 받쳐줄 VPC와 리전 간 연결을 설계합니다.
{cue: question}
시작 전에 여쭤보겠습니다. 지금 두 개 이상의 리전에서 프로덕션 트래픽을 받고 계신 분 계신가요?
{cue: transition}
전체 일정부터 보겠습니다.
:::

---
<!-- Slide 2: 아젠다 -->
@type: agenda
@timing: 150min

## 오늘 세션 구성

1. Multi-Region Foundation (30분)
2. Data Sync & Replication (30분)
3. Traffic Routing & Edge (30분)
4. DR & Failover Automation (30분)
5. Observability & Operations (30분)

> 질문은 각 Block 종료 시에 받겠습니다.

:::notes
{timing: 1min}
[요약]
- Block 1: 멀티리전 동기, 패턴, 일관성 모델, EKS와 VPC, 리전 간 연결
- Block 2: Aurora, DocumentDB, ElastiCache, MSK 데이터 복제
- Block 3: Route 53, CloudFront, WAF 기반 트래픽 라우팅
- Block 4: DR 전략과 페일오버 자동화
- Block 5: 멀티리전 관측성과 운영

오늘은 30분씩 다섯 블록입니다. 첫 블록에서 설계 원칙과 네트워크 바닥을 깔고, 두 번째 블록에서 데이터 계층 복제, 세 번째에서 사용자 트래픽을 어느 리전으로 보낼지, 네 번째에서 장애 시 넘어가는 방법, 마지막으로 이것을 어떻게 관측하고 운영하는지 봅니다.
{cue: pause}
질문은 각 블록이 끝날 때 받겠습니다.
{cue: transition}
먼저 멀티리전을 하는 이유부터 정리하겠습니다.
:::

---
<!-- Slide 3: 왜 멀티리전인가 -->
@type: content
@title: 멀티리전, 목적부터 정한다

## 멀티리전, 목적부터 정한다

:::html
<style>
.mr01-why { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-3); }
.mr01-tag { display: inline-block; margin-left: var(--space-2); font-size: var(--fs-caption); color: var(--text-secondary); }
.mr01-cost { margin-top: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="mr01-why" data-reveal="stagger">
  <div class="card">
    <strong class="text-accent">리전 규모 장애 격리</strong><span class="mr01-tag">가용성</span>
    <div class="on-surface-muted">Multi-AZ는 AZ 장애를 막고, 멀티리전은 리전 전체에 영향을 주는 드문 이벤트를 막습니다</div>
  </div>
  <div class="card">
    <strong class="text-accent">사용자 근접 지연</strong><span class="mr01-tag">성능</span>
    <div class="on-surface-muted">CDN이 못 줄이는 동적 API 읽기를 사용자와 가까운 리전에서 처리</div>
  </div>
  <div class="card">
    <strong class="text-accent">데이터 레지던시</strong><span class="mr01-tag">규제</span>
    <div class="on-surface-muted">국가, 산업 규제로 특정 리전 안에 데이터를 보관해야 하는 경우</div>
  </div>
  <div class="card">
    <strong class="text-accent">배포 blast radius 축소</strong><span class="mr01-tag">운영</span>
    <div class="on-surface-muted">한 리전씩 순차 배포하면 잘못된 변경의 영향 범위가 리전 하나로 제한</div>
  </div>
</div>
<div class="callout callout-warning mr01-cost fragment fade-up" data-fragment-index="1">
  <strong class="text-warning">공짜가 아닙니다</strong>: 인프라 이중화, 리전 간 데이터 전송 요금, 일관성 설계, 페일오버 연습까지 비용이 늘어납니다. 목표 RTO, RPO가 이 비용을 정당화하는지 먼저 확인하세요.
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- 멀티리전의 목적은 가용성, 지연, 레지던시, 운영 격리 네 가지로 정리됩니다.
- Multi-AZ는 AZ 장애 대응, 멀티리전은 리전 규모 이벤트 대응입니다.
- EC2 Region-level SLA는 이미 99.99%이므로 "SLA 숫자를 올리려고" 멀티리전을 한다는 설명은 부정확합니다.
- 비용과 복잡성이 크게 늘기 때문에 목표 RTO, RPO로 정당화해야 합니다.

멀티리전을 왜 하는지 네 가지로 정리했습니다. 첫째는 리전 규모 장애 격리입니다. Multi-AZ는 AZ 하나의 장애를 막아주지만, 리전 전체에 영향을 주는 드문 이벤트는 다른 리전이 있어야 버팁니다.
둘째는 지연입니다. 정적 콘텐츠는 CloudFront가 해결하지만, 장바구니 조회 같은 동적 API는 백엔드가 가까이 있어야 합니다. 셋째는 데이터 레지던시, 넷째는 배포 영향 범위를 리전 하나로 묶는 운영상 이점입니다.
{cue: pause}
예전 자료에서 "단일 리전 SLA는 99.9%라서 멀티리전이 필요하다"는 설명이 있었는데 정확하지 않습니다. EC2의 Region-level SLA는 99.99%입니다. 멀티리전의 가치는 SLA 숫자가 아니라 리전 단위의 장애 격리와 우리가 직접 통제하는 복구 경로에 있습니다.
"운영비 40~60% 증가" 같은 일반화된 숫자도 근거를 확인할 수 없어 뺐습니다. 실제 비용은 워크로드마다 다르니 직접 산정하셔야 합니다.
{cue: question}
여러분 조직에서 멀티리전을 검토하는 가장 큰 이유는 네 가지 중 무엇인가요?
{cue: transition}
목적을 정했다면 다음은 패턴 선택입니다.
[출처]
- EC2 Region-level SLA 99.99%, Instance-level 99.5%: https://aws.amazon.com/compute/sla/ (확인일 2026-10-15)
:::

---
<!-- Slide 4: Active-Active vs Active-Passive -->
@type: content
@title: Active-Active냐, Passive냐

## Active-Active냐, Passive냐

:::html
<style>
.mr01-vs { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3); }
.mr01-vs ul { margin: var(--space-2) 0 0; padding-left: var(--space-4); }
.mr01-vs li { margin-bottom: var(--space-1); }
.mr01-pick { margin-top: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="mr01-vs">
  <div class="card fragment fade-right" data-fragment-index="1">
    <strong class="text-accent">Active-Active</strong>
    <ul class="on-surface-muted">
      <li>모든 리전이 동시에 트래픽 처리, 사용자는 가까운 리전으로</li>
      <li>리전 하나를 잃어도 다른 리전이 이미 서비스 중</li>
      <li>쓰기를 양쪽에서 받으면 충돌 해결 또는 동기 합의가 필요</li>
      <li>각 리전이 전체 부하를 흡수할 용량을 유지해야 함</li>
    </ul>
  </div>
  <div class="card fragment fade-left" data-fragment-index="2">
    <strong class="text-info">Active-Passive</strong>
    <ul class="on-surface-muted">
      <li>Primary만 트래픽 처리, secondary는 대기 또는 축소 운영</li>
      <li>DR 전략 스펙트럼: Backup &amp; Restore, Pilot Light, Warm Standby</li>
      <li>단방향 복제라 충돌이 없고 구현이 단순</li>
      <li>페일오버 절차와 승격 시간이 RTO를 결정</li>
    </ul>
  </div>
</div>
<div class="callout callout-success mr01-pick fragment zoom-in" data-fragment-index="3">
  <strong class="text-success">이 세션의 선택</strong>: 읽기는 Active-Active, 쓰기는 Active-Passive. 두 리전 모두 트래픽을 받되 쓰기는 us-east-1 한 곳으로 모읍니다 (Write-Primary / Read-Local).
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- Active-Active: 모든 리전이 트래픽 처리, 쓰기 충돌과 용량 이중화가 비용
- Active-Passive: 단방향 복제, 단순하지만 페일오버 시간이 RTO를 결정
- AWS DR 전략 스펙트럼은 Backup & Restore, Pilot Light, Warm Standby, Multi-site Active/Active
- 실무에서 많이 쓰는 절충안: 읽기는 양쪽, 쓰기는 한 리전

두 기본 패턴을 비교하겠습니다. 클릭하면 왼쪽부터 나옵니다. Active-Active는 모든 리전이 동시에 트래픽을 받습니다. 리전 하나가 빠져도 다른 리전이 이미 서비스 중이라 전환이 빠릅니다. 대신 양쪽에서 쓰기를 받으면 같은 재고를 두 리전에서 동시에 차감하는 식의 충돌을 해결해야 하고, 각 리전이 전체 부하를 받아낼 용량을 항상 갖고 있어야 합니다.
{cue: pause}
Active-Passive는 primary만 트래픽을 받고 secondary는 대기합니다. 대기 수준에 따라 Backup and Restore, Pilot Light, Warm Standby로 나뉘고, 마지막 단계가 Multi-site Active/Active입니다. 복제가 한 방향이라 충돌이 없지만, 승격과 전환 시간이 그대로 RTO가 됩니다.
이 세션에서는 둘을 섞습니다. 읽기는 두 리전 모두에서 받고, 쓰기는 us-east-1 한 곳으로 모읍니다. 주문과 결제의 정합성을 지키면서 서부 사용자의 읽기 지연을 줄이는 절충입니다. DR 전략의 세부 비교는 Block 4에서 다룹니다.
{cue: transition}
이 선택의 이론적 배경인 CAP과 PACELC를 보겠습니다.
[출처]
- AWS Disaster Recovery whitepaper, DR 전략 4단계: https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html
:::

---
<!-- Slide 5: CAP / PACELC -->
@type: content
@title: CAP은 장애 때, PACELC는 평소에

## CAP은 장애 때, PACELC는 평소에

:::html
<style>
.mr01-theory { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3); margin-bottom: var(--space-3); }
.mr01-svc { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-3); }
.mr01-pc { display: inline-block; margin-top: var(--space-2); padding: 0 var(--space-2); border-radius: var(--radius-sm); background: var(--accent-subtle); color: var(--on-surface); font-family: var(--font-mono); font-size: var(--fs-caption); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="mr01-theory" data-reveal="stagger">
  <div class="callout callout-info">
    <strong class="text-info">CAP: Partition이 나면</strong>
    <div class="on-surface-muted">리전 간 연결이 끊긴 순간, 쓰기를 거부해 일관성(C)을 지키거나 각자 받아 가용성(A)을 지킨다</div>
  </div>
  <div class="callout callout-info">
    <strong class="text-info">PACELC: Else, 평소에는</strong>
    <div class="on-surface-muted">장애가 없어도 동기 복제는 리전 간 RTT만큼 느리다. 지연(L)과 일관성(C) 중 하나를 고른다</div>
  </div>
</div>
<div class="mr01-svc fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="card">
    <strong class="text-accent">DynamoDB global tables (MREC)</strong>
    <div class="on-surface-muted">기본 모드. 리전마다 로컬 쓰기, 비동기 복제, 충돌은 last writer wins</div>
    <span class="mr01-pc">PA / EL</span>
  </div>
  <div class="card">
    <strong class="text-accent">DynamoDB global tables (MRSC)</strong>
    <div class="on-surface-muted">정확히 3개 리전(복제본 3 또는 2 + witness), 다른 리전 1곳 이상에 동기 복제 후 응답</div>
    <span class="mr01-pc">PC / EC</span>
  </div>
  <div class="card">
    <strong class="text-accent">Aurora DSQL multi-Region</strong>
    <div class="on-surface-muted">peered cluster 2개 + witness Region, 양쪽 읽기, 쓰기 모두 강한 일관성</div>
    <span class="mr01-pc">PC / EC</span>
  </div>
  <div class="card">
    <strong class="text-accent">Aurora Global Database</strong>
    <div class="on-surface-muted">writer는 primary 1곳, secondary는 비동기 읽기 전용(일반적으로 lag 1초 미만)</div>
    <span class="mr01-pc">쓰기 C / 읽기 L</span>
  </div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- CAP은 네트워크 파티션 상황에서 C와 A 중 무엇을 포기할지의 문제입니다.
- PACELC는 장애가 없을 때도 지연과 일관성 사이에 trade-off가 있음을 더합니다.
- DynamoDB MREC는 PA/EL, MRSC와 Aurora DSQL multi-Region은 PC/EC에 가깝습니다.
- Aurora Global Database는 쓰기를 한 리전에 모으고 읽기는 로컬에서 빠르게 처리하는 구조입니다.

CAP 정리는 잘 아실 겁니다. 리전 간 링크가 끊기는 파티션은 피할 수 없으니, 실제 선택은 그 순간 쓰기를 거부해서 일관성을 지킬지, 각자 받아서 가용성을 지킬지입니다.
그런데 멀티리전에서는 장애가 없는 평소가 더 중요합니다. 이걸 말해주는 게 PACELC입니다. Else, 즉 평소에도 동기 복제를 하면 쓰기마다 리전 간 왕복 시간이 붙습니다. 지연을 택할지 일관성을 택할지 고르라는 뜻입니다.
{cue: pause}
아래 네 카드는 AWS 서비스를 이 관점으로 해석한 것입니다. 이 분류는 문서에 공식 표기된 등급이 아니라 동작 방식에 따른 해석입니다. DynamoDB global tables의 기본 모드인 MREC는 각 리전이 로컬로 쓰기를 받고 비동기로 복제하며 충돌은 last writer wins로 정리합니다. MRSC는 반드시 세 개 리전에 배치하고, 쓰기는 다른 리전 한 곳 이상에 동기 복제된 뒤 응답합니다. Aurora DSQL의 multi-Region 구성도 peered cluster 두 개와 witness Region으로 강한 일관성을 줍니다.
예전 자료에서 Aurora DSQL을 단순히 "파티션 시 쓰기를 거부하는 CP"로만 설명했는데, 평소 지연 비용까지 함께 봐야 정확합니다. 우리 시나리오의 주력인 Aurora Global Database는 쓰기를 한 리전에 모으고 secondary 읽기는 일반적으로 1초 미만 lag으로 로컬에서 처리합니다.
{cue: transition}
그럼 데이터마다 어떤 일관성을 줄지 구체적으로 보겠습니다.
[약어]
- MREC: Multi-Region Eventual Consistency, MRSC: Multi-Region Strong Consistency
[출처]
- DynamoDB global tables 동작(MREC, MRSC, witness, 정확히 3개 리전): https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/V2globaltables_HowItWorks.html
- Aurora DSQL peered cluster, witness Region: https://docs.aws.amazon.com/aurora-dsql/latest/userguide/what-is-aurora-dsql.html
- Aurora Global Database secondary lag "typically under a second": https://docs.aws.amazon.com/rds/latest/auroraextendedcontent/aurora-faq-availability-and-durability.html
:::

---
<!-- Slide 6: 일관성 모델 -->
@type: content
@title: 일관성은 데이터마다 고른다

## 일관성은 데이터마다 고른다

:::html
<style>
.mr01-cm-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-3); margin-top: var(--space-3); }
.mr01-cm-grid code { font-size: var(--fs-caption); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">Strong</button>
  <button class="tab-btn">Session</button>
  <button class="tab-btn">Eventual</button>
  <button class="tab-btn">우리 서비스 매핑</button>
</div>
<div class="tc">
  <div class="mr01-cm-grid" data-reveal="static">
    <div class="card"><strong class="text-accent">보장</strong><div class="on-surface-muted">어느 리전에서 읽어도 마지막으로 커밋된 쓰기가 보임</div></div>
    <div class="card"><strong class="text-accent">대가</strong><div class="on-surface-muted">쓰기, 강한 읽기 지연이 참여 리전 간 RTT에 비례</div></div>
    <div class="card"><strong class="text-accent">AWS 예</strong><div class="on-surface-muted">DynamoDB MRSC, Aurora DSQL multi-Region, Aurora write forwarding <code>GLOBAL</code> 모드</div></div>
    <div class="card"><strong class="text-accent">적합</strong><div class="on-surface-muted">결제 승인, 재고 차감처럼 중복이나 역전이 치명적인 데이터</div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="mr01-cm-grid">
    <div class="card"><strong class="text-info">보장</strong><div class="on-surface-muted">내 세션이 쓴 것은 내 세션에서 바로 보임 (read-your-writes)</div></div>
    <div class="card"><strong class="text-info">대가</strong><div class="on-surface-muted">내 쓰기가 로컬로 복제될 때까지만 대기, 다른 세션의 변경은 늦게 보일 수 있음</div></div>
    <div class="card"><strong class="text-info">AWS 예</strong><div class="on-surface-muted"><code>apg_write_forward.consistency_mode</code> 기본값 <code>SESSION</code></div></div>
    <div class="card"><strong class="text-info">적합</strong><div class="on-surface-muted">주문 직후 "내 주문 내역" 확인처럼 본인 데이터 확인 흐름</div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="mr01-cm-grid">
    <div class="card"><strong class="text-success">보장</strong><div class="on-surface-muted">충분한 시간이 지나면 모든 복제본이 같아짐, 그 전엔 stale 가능</div></div>
    <div class="card"><strong class="text-success">대가</strong><div class="on-surface-muted">가장 빠르지만 앱이 stale 읽기와 충돌을 견뎌야 함</div></div>
    <div class="card"><strong class="text-success">AWS 예</strong><div class="on-surface-muted">DynamoDB MREC, Aurora secondary 일반 읽기, <code>EVENTUAL</code> 모드, S3 복제</div></div>
    <div class="card"><strong class="text-success">적합</strong><div class="on-surface-muted">상품 카탈로그, 리뷰, 추천, 검색 인덱스</div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="mr01-cm-grid">
    <div class="callout callout-danger"><strong class="text-warning">payment</strong><div class="on-surface-muted">Strong: 쓰기는 primary writer에서만, 승인 결과는 primary 기준으로 확인</div></div>
    <div class="callout callout-warning"><strong class="text-warning">order</strong><div class="on-surface-muted">Session: secondary에서 write forwarding, 본인 주문은 바로 보이게</div></div>
    <div class="callout callout-success"><strong class="text-success">catalog</strong><div class="on-surface-muted">Eventual: 로컬 읽기, 가격, 재고 표시는 수 초 지연 허용</div></div>
    <div class="callout callout-info"><strong class="text-info">cart</strong><div class="on-surface-muted">Eventual + 캐시: 로컬 읽기, 장바구니 담기는 결제 직전에 primary로 재검증</div></div>
  </div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- 일관성은 시스템 전체가 아니라 데이터 종류마다 고릅니다.
- Strong은 RTT만큼 느리고, Session은 read-your-writes, Eventual은 가장 빠르지만 stale을 허용합니다.
- Aurora PostgreSQL write forwarding은 consistency_mode로 SESSION(기본), EVENTUAL, GLOBAL, OFF를 고릅니다.
- 결제는 Strong, 주문은 Session, 카탈로그와 장바구니는 Eventual로 매핑합니다.

탭으로 세 가지 모델과 우리 서비스 매핑을 보겠습니다. Strong은 어디서 읽어도 최신 값이 보이지만, 쓰기마다 리전 간 왕복이 붙습니다. Session은 "내가 쓴 것은 내가 바로 본다"를 보장합니다. Eventual은 가장 빠르지만 잠시 오래된 값을 읽을 수 있습니다.
{cue: pause}
이건 이론만이 아니고 실제 설정 키로 존재합니다. Aurora PostgreSQL global database에서 secondary의 write forwarding을 켜면 apg_write_forward.consistency_mode 파라미터로 SESSION, EVENTUAL, GLOBAL, OFF를 고를 수 있고 기본값은 SESSION입니다. GLOBAL로 올리면 다른 리전에서 커밋된 변경까지 따라잡을 때까지 기다리므로 지연이 커집니다.
마지막 탭이 우리 서비스 매핑입니다. 결제는 primary에서만 쓰고 확인합니다. 주문은 서부에서 write forwarding을 쓰되 본인 주문은 바로 보이게 SESSION, 카탈로그와 장바구니는 로컬 읽기로 수 초 지연을 허용합니다. 장바구니는 결제 직전에 primary 기준으로 다시 검증하는 것이 안전합니다.
{cue: transition}
이 매핑을 전체 아키텍처에 올려보겠습니다.
[출처]
- apg_write_forward.consistency_mode 값과 기본값: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-write-forwarding-apg.html (확인일 2026-10-15)
:::

---
<!-- Slide 7: 아키텍처 한눈에 -->
@type: content
@title: 아키텍처 한눈에 보기

## 아키텍처 한눈에 보기

:::html
<style>
.mr01-arch { display: flex; flex-direction: column; gap: var(--space-2); font-size: var(--fs-card); word-break: keep-all; }
.mr01-edge { display: flex; justify-content: center; }
.mr01-regions { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3); }
.mr01-region { border-left: 4px solid var(--accent); }
.mr01-region.sec { border-left-color: var(--info); }
.mr01-ico { width: 40px; height: 40px; vertical-align: middle; margin-right: var(--space-1); }
.mr01-down { text-align: center; color: var(--accent); font-weight: var(--weight-bold); }
.mr01-data { display: grid; grid-template-columns: repeat(7, 1fr); gap: var(--space-2); }
.mr01-data .flow-box { word-break: keep-all; overflow-wrap: anywhere; }
.mr01-data .flow-box { text-align: center; }
.mr01-badge { display: inline-block; margin-left: var(--space-2); padding: 0 var(--space-2); border-radius: var(--radius-sm); font-size: var(--fs-card); background: var(--accent-subtle); color: var(--on-surface); }
.mr01-badge.sec { background: var(--info-subtle); }
</style>
<div class="mr01-arch">
  <div class="mr01-edge" data-reveal="stagger">
    <div class="flow-group">
      <div class="flow-group-label">Edge (global)</div>
      <div class="flow-h">
        <div class="flow-box"><img class="mr01-ico" src="./common/aws-icons/services/Arch_Amazon-Route-53_48.svg" alt="Amazon Route 53">Route 53</div>
        <div class="flow-box"><img class="mr01-ico" src="./common/aws-icons/services/Arch_Amazon-CloudFront_48.svg" alt="Amazon CloudFront">CloudFront</div>
        <div class="flow-box"><img class="mr01-ico" src="./common/aws-icons/services/Arch_AWS-WAF_48.svg" alt="AWS WAF">WAF</div>
      </div>
    </div>
  </div>
  <div class="mr01-down">↓ VPC origin (private) ↓</div>
  <div class="mr01-regions">
    <div class="flow-group mr01-region fragment fade-right" data-fragment-index="1">
      <div class="flow-group-label">us-east-1<span class="mr01-badge">PRIMARY, writer</span></div>
      <div class="flow-h">
        <div class="flow-box"><img class="mr01-ico" src="./common/aws-icons/services/Arch_Elastic-Load-Balancing_48.svg" alt="Elastic Load Balancing">internal ALB</div>
        <div class="flow-arrow">→</div>
        <div class="flow-box"><img class="mr01-ico" src="./common/aws-icons/services/Arch_Amazon-Elastic-Kubernetes-Service_48.svg" alt="Amazon EKS">EKS: order, payment, catalog, cart</div>
      </div>
    </div>
    <div class="flow-group mr01-region sec fragment fade-left" data-fragment-index="2">
      <div class="flow-group-label">us-west-2<span class="mr01-badge sec">SECONDARY, reader</span></div>
      <div class="flow-h">
        <div class="flow-box"><img class="mr01-ico" src="./common/aws-icons/services/Arch_Elastic-Load-Balancing_48.svg" alt="Elastic Load Balancing">internal ALB</div>
        <div class="flow-arrow">→</div>
        <div class="flow-box"><img class="mr01-ico" src="./common/aws-icons/services/Arch_Amazon-Elastic-Kubernetes-Service_48.svg" alt="Amazon EKS">EKS: 동일 서비스 세트</div>
      </div>
    </div>
  </div>
  <div class="mr01-down fragment" data-fragment-index="3">↓ 리전별 데이터 계층, primary → secondary 복제 ↓</div>
  <div class="mr01-data fragment" data-reveal="stagger" data-fragment-index="3">
    <div class="flow-box"><img class="mr01-ico" src="./common/aws-icons/services/Arch_Amazon-Aurora_48.svg" alt="Amazon Aurora"><br>Aurora PostgreSQL Global DB<br>order, payment</div>
    <div class="flow-box"><img class="mr01-ico" src="./common/aws-icons/services/Arch_Amazon-DocumentDB_48.svg" alt="Amazon DocumentDB"><br>DocumentDB Global Cluster<br>catalog</div>
    <div class="flow-box"><img class="mr01-ico" src="./common/aws-icons/services/Arch_Amazon-ElastiCache_48.svg" alt="Amazon ElastiCache"><br>ElastiCache Valkey<br>Global Datastore</div>
    <div class="flow-box"><img class="mr01-ico" src="./common/aws-icons/services/Arch_Amazon-Managed-Streaming-for-Apache-Kafka_48.svg" alt="Amazon MSK"><br>MSK<br>이벤트</div>
    <div class="flow-box"><img class="mr01-ico" src="./common/aws-icons/services/Arch_Amazon-DynamoDB_48.svg" alt="Amazon DynamoDB"><br>DynamoDB Global Tables<br>idempotency</div>
    <div class="flow-box"><img class="mr01-ico" src="./common/aws-icons/services/Arch_Amazon-OpenSearch-Service_48.svg" alt="Amazon OpenSearch Service"><br>OpenSearch<br>검색</div>
    <div class="flow-box"><img class="mr01-ico" src="./common/aws-icons/services/Arch_Amazon-Simple-Storage-Service_48.svg" alt="Amazon S3"><br>S3<br>이미지, 아카이브</div>
  </div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- Edge: Route 53, CloudFront, WAF가 유일한 공개 진입점입니다.
- CloudFront는 VPC origin으로 각 리전의 internal ALB에 private하게 연결합니다.
- 두 리전에 동일한 EKS 서비스 세트를 배포하고, us-east-1이 writer입니다.
- 데이터 계층 7종은 모두 리전별로 존재하며 primary에서 secondary로 복제합니다.

전체 그림입니다. 맨 위 Edge 계층이 외부에서 들어오는 유일한 입구입니다. Route 53, CloudFront, WAF로 구성하고, CloudFront는 VPC origin 기능으로 각 리전의 internal ALB에 직접 붙습니다. ALB는 인터넷에 노출되지 않습니다.
{cue: pause}
클릭하면 두 리전이 나옵니다. 두 리전 모두 internal ALB 뒤에 EKS가 있고 주문, 결제, 카탈로그, 장바구니 서비스를 똑같이 배포합니다. 차이는 데이터 계층에서 누가 writer인가입니다. us-east-1이 writer, us-west-2는 reader입니다.
아래 데이터 계층은 Aurora PostgreSQL Global Database, DocumentDB Global Cluster, ElastiCache Valkey Global Datastore, MSK, DynamoDB Global Tables, OpenSearch, S3입니다. 각 저장소의 복제 방식과 버전 선택은 Block 2에서 자세히 다룹니다. 예전 자료에 있던 특정 엔진 버전이나 인스턴스 타입은 여기서 다루지 않습니다.
사용자를 어느 리전으로 보내는지, 즉 CloudFront와 Route 53 라우팅 정책은 Block 3 주제입니다.
{cue: transition}
이 구조의 핵심인 쓰기 경로와 읽기 경로를 나눠서 보겠습니다.
[출처]
- CloudFront VPC origins (ALB, NLB, EC2 in private subnets): https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-vpc-origins.html
:::

---
<!-- Slide 8: Write-Primary / Read-Local -->
@type: content
@title: 쓰기는 한 곳, 읽기는 가까운 곳

## 쓰기는 한 곳, 읽기는 가까운 곳

:::html
<style>
.mr01-wr { display: grid; grid-template-columns: 1fr auto 1fr; gap: var(--space-3); align-items: stretch; margin-bottom: var(--space-3); }
.mr01-wr .card { border-left: 4px solid var(--accent); }
.mr01-wr .card.sec { border-left-color: var(--info); }
.mr01-mid { display: flex; flex-direction: column; justify-content: center; gap: var(--space-3); text-align: center; font-size: var(--fs-caption); color: var(--text-secondary); }
.mr01-mid strong { display: block; color: var(--on-surface); font-size: var(--fs-card); }
.mr01-row { display: flex; justify-content: space-between; gap: var(--space-2); padding: var(--space-2) 0; border-bottom: 1px solid var(--surface-3); }
.mr01-trade { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="mr01-wr">
  <div class="card fragment fade-right" data-fragment-index="1">
    <strong class="text-accent">us-east-1 (primary)</strong>
    <div class="mr01-row on-surface-muted"><span>쓰기</span><span>writer instance</span></div>
    <div class="mr01-row on-surface-muted"><span>읽기</span><span>로컬 reader</span></div>
    <div class="mr01-row on-surface-muted"><span>접속</span><span>global writer endpoint</span></div>
  </div>
  <div class="mr01-mid fragment" data-fragment-index="2">
    <div><strong>→ 비동기 복제</strong>storage 기반, 일반적으로 1초 미만</div>
    <div><strong>← write forwarding</strong>secondary에서 받은 쓰기를 primary로 전달</div>
  </div>
  <div class="card sec fragment fade-left" data-fragment-index="2">
    <strong class="text-info">us-west-2 (secondary)</strong>
    <div class="mr01-row on-surface-muted"><span>쓰기</span><span>forwarding 또는 primary 직접</span></div>
    <div class="mr01-row on-surface-muted"><span>읽기</span><span>로컬 reader</span></div>
    <div class="mr01-row on-surface-muted"><span>접속</span><span>cluster reader endpoint</span></div>
  </div>
</div>
<div class="mr01-trade fragment" data-reveal="stagger" data-fragment-index="3">
  <div class="metric-card"><strong class="text-success">충돌 없음</strong><div class="on-surface-muted">writer가 하나라 충돌 해결 로직이 필요 없음</div></div>
  <div class="metric-card"><strong class="text-warning">서부 쓰기는 느리다</strong><div class="on-surface-muted">forwarding된 쓰기는 리전 간 RTT를 그대로 부담, <code>SERIALIZABLE</code> 격리 미지원</div></div>
  <div class="metric-card"><strong class="text-warning">연결 상한</strong><div class="on-surface-muted">forwarding 세션은 primary writer <code>max_connections</code>의 기본 25%까지만 허용</div></div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- 모든 쓰기는 us-east-1 writer 한 곳, 읽기는 각 리전의 로컬 reader에서 처리합니다.
- secondary의 쓰기는 write forwarding 또는 global writer endpoint로 primary에 보냅니다.
- Aurora Global Database 복제 lag은 일반적으로 1초 미만입니다.
- forwarding된 쓰기는 리전 간 RTT를 부담하고, SERIALIZABLE을 지원하지 않으며, 연결 수 상한(기본 25%)이 있습니다.

Write-Primary, Read-Local 패턴을 Aurora 기준으로 보겠습니다. us-east-1에는 writer가 있고 로컬 reader가 읽기를 처리합니다. us-west-2는 읽기 전용 secondary 클러스터라 읽기는 로컬에서 끝납니다.
{cue: pause}
서부에서 들어온 쓰기는 두 가지 방법으로 보냅니다. 하나는 secondary의 write forwarding을 켜서 Aurora가 primary로 전달하게 하는 방법, 다른 하나는 앱이 global writer endpoint로 직접 쓰는 방법입니다. global writer endpoint는 Route 53 기반 DNS라 switchover나 failover 후 자동으로 새 primary를 가리킵니다. 단 다른 리전 VPC의 IP로 접속하려면 리전 간 네트워크 연결이 있어야 합니다. 그래서 뒤에서 Transit Gateway를 설계합니다.
아래 세 카드가 trade-off입니다. writer가 하나라 충돌이 없지만, 서부의 쓰기는 리전 간 왕복 시간을 그대로 부담합니다. forwarding 세션에서는 SERIALIZABLE 격리 수준을 쓸 수 없고, forwarding 연결 수는 writer max_connections의 기본 25%로 제한됩니다.
예전 자료의 "앱 코드는 전혀 몰라도 된다"는 설명은 과장입니다. 격리 수준, 연결 상한, consistency_mode를 앱이 의식해야 합니다.
{cue: transition}
이제 이 패턴을 올릴 컴퓨트, 리전별 EKS를 보겠습니다.
[출처]
- Write forwarding 격리 수준, max_forwarding_connections_percent 기본 25: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-write-forwarding-apg.html
- Global writer endpoint, 리전 간 VPC 연결 고려 사항: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-connecting.html
:::

---
<!-- Slide 9: 리전별 EKS 배포 -->
@type: content
@title: 리전마다 독립된 EKS 클러스터

## 리전마다 독립된 EKS 클러스터

:::html
<style>
.mr01-eks { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="mr01-eks fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="card"><strong class="text-accent">클러스터는 리전 단위</strong><div class="on-surface-muted">EKS 컨트롤 플레인은 리전 서비스. 리전마다 독립 클러스터를 두고 서로 의존하지 않게 설계</div></div>
  <div class="card"><strong class="text-accent">버전을 맞춘다</strong><div class="on-surface-muted">두 리전 모두 같은 Kubernetes 버전. 2026-10 기준 최신은 1.37 (EKS 출시 2026-10-01)</div></div>
  <div class="card"><strong class="text-accent">GitOps로 같은 매니페스트</strong><div class="on-surface-muted">하나의 Git 저장소에서 두 클러스터로 배포, 리전 차이는 overlay 값(endpoint, ARN)으로만</div></div>
  <div class="card"><strong class="text-info">이미지도 리전마다</strong><div class="on-surface-muted">ECR 리전 간 복제로 각 리전에서 로컬 pull. 다른 리전 레지스트리에 의존하지 않음</div></div>
  <div class="card"><strong class="text-info">IAM은 Pod Identity</strong><div class="on-surface-muted">IAM role은 글로벌, association은 클러스터마다 생성. 리전별 리소스 ARN 범위 확인</div></div>
  <div class="card"><strong class="text-warning">흡수 용량 계획</strong><div class="on-surface-muted">한 리전이 빠지면 나머지가 전체 부하를 받는다. 페일오버 순간 스케일아웃에 기대지 않도록 여유 확보</div></div>
</div>
:::

:::notes
{timing: 2min}
[요약]
- EKS 클러스터는 리전마다 독립적으로 두고 리전 간 의존을 만들지 않습니다.
- 두 리전의 Kubernetes 버전을 맞추며, 2026년 10월 기준 최신 EKS 버전은 1.37입니다.
- GitOps로 같은 매니페스트를 배포하고 리전 차이는 overlay 값으로만 둡니다.
- ECR 복제, Pod Identity association, 흡수 용량을 리전별로 준비합니다.

컴퓨트 계층입니다. 핵심은 리전마다 완전히 독립된 클러스터라는 점입니다. 서부 클러스터가 동부의 무언가에 의존하면, 동부 장애 때 서부도 같이 넘어집니다.
버전은 두 리전에서 맞춥니다. 2026년 10월 1일 EKS에 1.37이 출시되었고 standard support는 2027년 12월 1일까지입니다. 예전 자료의 1.35와 Karpenter 1.9 같은 구체 버전은 시점이 지나 뺐습니다. 노드 프로비저닝 세부는 별도 세션 주제입니다.
{cue: pause}
배포는 GitOps로 하나의 저장소에서 두 클러스터로 내보내고, 리전마다 다른 값은 데이터베이스 endpoint나 ARN 같은 overlay 값으로만 둡니다. 이미지는 ECR 리전 간 복제를 써서 각 리전에서 로컬로 받습니다.
IAM은 EKS Pod Identity를 씁니다. IAM role은 글로벌이지만 Pod Identity association은 클러스터 단위라 두 클러스터에 모두 만들어야 합니다. 마지막으로 흡수 용량입니다. 한 리전이 빠지는 순간 나머지 리전이 전체 부하를 받아야 하므로, 그때 스케일아웃이 제때 될 거라고 기대하기보다 미리 여유를 확보해 두는 것이 안전합니다.
{cue: transition}
클러스터가 올라갈 VPC를 설계해 보겠습니다.
[출처]
- EKS Kubernetes release calendar (1.37: EKS 출시 2026-10-01, standard support 종료 2027-12-01): https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html (확인일 2026-10-15)
:::

---
<!-- Slide 10: VPC 설계 -->
@type: content
@title: CIDR은 겹치지 않게, 티어는 셋으로

## CIDR은 겹치지 않게, 티어는 셋으로

:::html
<style>
.mr01-vpc-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); margin-top: var(--space-3); }
.mr01-vpc-grid code { font-size: var(--fs-caption); }
.mr01-cidr { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); margin-top: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">CIDR 계획</button>
  <button class="tab-btn">3-tier 서브넷</button>
  <button class="tab-btn">티어별 라우팅</button>
</div>
<div class="tc">
  <div class="mr01-cidr" data-reveal="static">
    <div class="metric-card"><div class="metric-value">10.0.0.0/16</div><div class="metric-label">us-east-1 VPC</div></div>
    <div class="metric-card"><div class="metric-value">10.1.0.0/16</div><div class="metric-label">us-west-2 VPC</div></div>
    <div class="metric-card"><div class="metric-value">10.2~10.15</div><div class="metric-label">향후 리전, 환경 예약</div></div>
    <div class="callout callout-danger"><strong class="text-danger">겹치면 못 붙인다</strong><div class="on-surface-muted">VPC peering은 CIDR이 하나라도 겹치면 생성 불가, TGW도 목적지가 모호해짐</div></div>
    <div class="callout callout-info"><strong class="text-info">IPAM으로 할당</strong><div class="on-surface-muted">Amazon VPC IPAM pool에서 리전별로 나눠주면 중복을 사전에 차단</div></div>
    <div class="callout callout-success"><strong class="text-success">Pod IP도 계산</strong><div class="on-surface-muted">VPC CNI는 Pod마다 VPC IP를 쓰므로 노드 수가 아니라 Pod 수로 산정</div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="mr01-vpc-grid">
    <div class="card"><strong class="text-warning">Public (AZ당 /24)</strong><div class="on-surface-muted"><code>10.x.0.0/24</code>, <code>.1.0/24</code>, <code>.2.0/24</code><br>NAT Gateway만. LB, 컴퓨트, public IP 없음</div></div>
    <div class="card"><strong class="text-accent">Private app (AZ당 /19)</strong><div class="on-surface-muted"><code>10.x.32.0/19</code>, <code>.64.0/19</code>, <code>.96.0/19</code><br>internal ALB, EKS 노드와 Pod, VPC origin ENI</div></div>
    <div class="card"><strong class="text-info">Data (AZ당 /21)</strong><div class="on-surface-muted"><code>10.x.128.0/21</code>, <code>.136.0/21</code>, <code>.144.0/21</code><br>Aurora, DocumentDB, ElastiCache, MSK, OpenSearch</div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="mr01-vpc-grid">
    <div class="card"><strong class="text-warning">Public RT</strong><div class="on-surface-muted">기본 경로 → IGW (NAT 아웃바운드 전용). IGW는 CloudFront VPC origin의 전제 조건이기도 함</div></div>
    <div class="card"><strong class="text-accent">Private app RT</strong><div class="on-surface-muted">기본 경로 → 같은 AZ NAT, 상대 리전 <code>/16</code> → TGW, S3, DynamoDB → gateway endpoint</div></div>
    <div class="card"><strong class="text-info">Data RT</strong><div class="on-surface-muted">인터넷 경로 없음. SG는 app 티어 SG만 DB 포트로 허용</div></div>
  </div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- us-east-1은 10.0.0.0/16, us-west-2는 10.1.0.0/16, 10.2~10.15는 향후 확장용으로 예약합니다.
- 서브넷은 public(/24), private app(/19), data(/21) 세 티어를 AZ 3개에 배치합니다.
- public 티어에는 NAT Gateway만 두고 로드밸런서나 컴퓨트, public IP는 두지 않습니다.
- data 티어에는 인터넷 경로를 두지 않고, SG는 app 티어 SG 참조로만 엽니다.

탭 세 개로 VPC를 보겠습니다. 첫 탭은 CIDR 계획입니다. 두 리전 VPC는 겹치지 않는 /16을 쓰고, 다음 리전이나 환경을 위해 10.2부터 10.15까지 미리 예약합니다. VPC peering은 CIDR이 하나라도 겹치면 만들 수 없고, Transit Gateway를 써도 목적지가 모호해집니다. 수동 엑셀 관리보다 VPC IPAM pool에서 나눠주는 것을 권합니다. EKS VPC CNI는 Pod마다 VPC IP를 쓰므로 Pod 수로 산정해야 합니다.
{cue: pause}
두 번째 탭은 서브넷입니다. 예전 자료와 달라진 점이 있습니다. 예전에는 public 티어에 ALB와 NLB를 뒀는데, 이번 설계에서는 public 티어에 NAT Gateway만 둡니다. ALB는 internal로 private app 티어에 두고 CloudFront가 VPC origin으로 붙습니다. 그래서 public 티어는 /24로 작게, Pod가 많은 app 티어는 /19로 크게 잡았습니다.
세 번째 탭은 라우팅입니다. public은 NAT 아웃바운드를 위해 IGW로 기본 경로를 둡니다. CloudFront VPC origin을 쓰려면 VPC에 IGW가 붙어 있어야 한다는 전제 조건도 있습니다. 단 IGW는 origin으로 가는 트래픽 경로에 쓰이지 않습니다. app 티어는 상대 리전 CIDR을 TGW로, S3와 DynamoDB는 gateway endpoint로 보냅니다. data 티어에는 인터넷 경로가 없습니다.
{cue: transition}
상대 리전 CIDR을 보내는 그 TGW, 리전 간 연결 선택지를 비교하겠습니다.
[출처]
- VPC peering CIDR 중복 제약: https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-basics.html
- VPC origin의 IGW 요구 사항: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-vpc-origins.html
:::

---
<!-- Slide 11: 리전 간 연결 -->
@type: content
@title: 리전 간 연결, 세 가지 선택지

## 리전 간 연결, 세 가지 선택지

:::html
<style>
.mr01-ic-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-3); margin-top: var(--space-3); }
.mr01-ic-code { margin-top: var(--space-3); font-size: var(--fs-caption); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn">VPC Peering</button>
  <button class="tab-btn active">TGW Peering (선택)</button>
  <button class="tab-btn">Cloud WAN</button>
</div>
<div class="tc" hidden>
  <div class="mr01-ic-grid">
    <div class="card"><strong class="text-accent">언제</strong><div class="on-surface-muted">VPC 두세 개를 1:1로 붙일 때 가장 단순, 별도 hourly 요금 없음 (리전 간 전송 요금은 부과)</div></div>
    <div class="card"><strong class="text-warning">transitive 불가</strong><div class="on-surface-muted">A-B, A-C를 붙여도 B-C는 통신 불가. VPC가 늘면 n(n-1)/2 mesh</div></div>
    <div class="card"><strong class="text-warning">리전 간 SG 참조 불가</strong><div class="on-surface-muted">inter-Region peering에서는 상대 SG를 참조할 수 없어 CIDR 규칙으로 작성</div></div>
    <div class="card"><strong class="text-info">상한</strong><div class="on-surface-muted">VPC당 active peering 기본 50개(최대 125개까지 상향), 두 VPC 사이에는 1개만</div></div>
  </div>
</div>
<div class="tc">
  <div class="mr01-ic-grid" data-reveal="static">
    <div class="card"><strong class="text-accent">static route만</strong><div class="on-surface-muted">peering attachment를 향한 static route를 TGW route table에 직접 추가 (BGP 전파 없음)</div></div>
    <div class="card"><strong class="text-success">암호화, 백본</strong><div class="on-surface-muted">리전 간 트래픽은 AWS 백본에서 AES-256으로 암호화, 인터넷을 거치지 않음</div></div>
    <div class="card"><strong class="text-warning">리전을 넘지 못하는 것</strong><div class="on-surface-muted">SG 참조, Route 53 Resolver 기반 상대 리전 private DNS 해석은 peering 너머로 동작하지 않음</div></div>
    <div class="card"><strong class="text-info">상한</strong><div class="on-surface-muted">TGW 쌍당 peering 1개, TGW당 peering 기본 50개, MTU 8500</div></div>
  </div>
  <pre class="code-block mr01-ic-code"><span class="comment"># us-east-1 TGW route table (us-west-2는 대칭)</span>
<span class="key">10.0.0.0/16</span> → vpc attachment (local VPC, propagation)
<span class="key">10.1.0.0/16</span> → peering attachment (<span class="string">static</span>, us-west-2)</pre>
</div>
<div class="tc" hidden>
  <div class="mr01-ic-grid">
    <div class="card"><strong class="text-accent">정책 기반</strong><div class="on-surface-muted">core network policy(JSON)에 리전, segment, attachment 규칙을 선언하면 Cloud WAN이 구성</div></div>
    <div class="card"><strong class="text-success">동적 라우팅</strong><div class="on-surface-muted">리전마다 core network edge(CNE)가 생성되고 CNE 간 경로를 자동 교환</div></div>
    <div class="card"><strong class="text-info">segment 격리</strong><div class="on-surface-muted">prod, dev, shared 같은 segment로 리전을 가로질러 격리, 태그로 자동 매핑</div></div>
    <div class="card"><strong class="text-warning">언제 고려</strong><div class="on-surface-muted">리전이 3개 이상으로 늘거나 segment 정책을 중앙에서 관리해야 할 때. 기존 TGW와 peering으로 공존 가능</div></div>
  </div>
</div>
:::

:::notes
{timing: 3min}
[요약]
- VPC Peering: 가장 단순하지만 transitive 불가, 리전 간 SG 참조 불가, VPC당 기본 50개, 최대 125개
- TGW Peering(이번 선택): static route만, AES-256 암호화, TGW 쌍당 1개, SG 참조와 상대 리전 DNS 해석 불가
- Cloud WAN: 정책 기반, CNE 간 동적 라우팅, segment 격리. 리전이 늘면 검토
- 예전 자료의 "TGW peering은 ECMP로 대역폭을 늘린다"는 틀렸습니다. ECMP는 VPN과 Connect attachment 기능입니다.

리전 간 연결 선택지를 세 탭으로 비교합니다. 기본으로 열린 탭이 이번 설계의 선택인 TGW peering입니다.
가장 먼저 기억할 점은 static route만 된다는 것입니다. peering attachment로는 BGP 전파가 없어서, 아래 코드처럼 상대 리전 CIDR을 peering attachment로 보내는 static route를 양쪽 TGW route table에 직접 넣어야 합니다. 리전 간 트래픽은 AWS 백본에서 AES-256으로 암호화됩니다.
{cue: pause}
peering 너머로 동작하지 않는 것도 있습니다. Security group 참조는 같은 TGW에 붙은 VPC끼리만 되고, Route 53 Resolver로 상대 리전 private DNS를 해석하는 것도 지원하지 않습니다. 그래서 상대 리전 규칙은 CIDR이나 prefix list로 쓰고, DNS는 별도로 설계해야 합니다.
예전 자료에서 TGW peering의 장점으로 ECMP를 들었는데 사실이 아닙니다. ECMP는 dynamic routing VPN과 Connect attachment에서 대역폭을 묶는 기능이고, peering attachment에는 해당하지 않습니다.
VPC peering 탭을 보면 두 VPC만 붙일 때는 가장 단순하지만 transitive가 안 되고 리전 간 SG 참조도 안 됩니다. Cloud WAN은 정책 JSON으로 리전과 segment를 선언하면 리전마다 CNE가 생기고 경로를 동적으로 교환합니다. 지금은 두 리전이라 TGW로 충분하고, 리전이 셋 이상으로 늘면 Cloud WAN을 검토합니다.
{cue: transition}
리전 안에서 AWS API로 나가는 트래픽, VPC endpoint 전략을 보겠습니다.
[출처]
- TGW peering static route, AES-256, Resolver 제약: https://docs.aws.amazon.com/vpc/latest/tgw/tgw-peering.html
- TGW quotas (peering 50, TGW 쌍당 1, MTU 8500, ECMP는 VPN/Connect): https://docs.aws.amazon.com/vpc/latest/tgw/transit-gateway-quotas.html
- TGW SG 참조는 peering 너머 미지원: https://docs.aws.amazon.com/vpc/latest/tgw/tgw-vpc-attachments.html
- VPC peering 기본 50개(최대 125), transitive 불가: https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-connection-quotas.html
- Inter-Region VPC peering SG 참조 불가: https://aws.amazon.com/vpc/faqs/
- Cloud WAN core network policy: https://aws.amazon.com/cloud-wan/faqs/
:::

---
<!-- Slide 12: VPC Endpoints -->
@type: content
@title: NAT 대신 endpoint, 손익분기 계산

## NAT 대신 endpoint, 손익분기 계산

:::html
<style>
.mr01-ep { display: grid; grid-template-columns: 1fr 1.25fr; gap: var(--space-4); align-items: start; }
.mr01-ep-list { display: flex; flex-direction: column; gap: var(--space-2); }
.mr01-ep-list code { font-size: var(--fs-caption); }
.mr01-calc { display: flex; flex-direction: column; gap: var(--space-2); }
.mr01-calc-row { display: grid; grid-template-columns: 11rem 1fr; align-items: center; gap: var(--space-3); }
.mr01-calc-row label { color: var(--text-secondary); }
.mr01-calc .slider-value { min-width: 6rem; }
.mr01-calc .metric-value { font-size: var(--fs-subtitle); white-space: nowrap; }
.mr01-calc .card-grid { margin-top: var(--space-2); }
.mr01-note { color: var(--text-secondary); font-size: var(--fs-caption); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-1); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="mr01-ep">
  <div class="mr01-ep-list" data-reveal="stagger">
    <div class="callout callout-success"><strong class="text-success">Gateway endpoint (무료)</strong><div class="on-surface-muted">S3, DynamoDB. ECR 이미지 레이어도 S3에서 받으므로 항상 생성</div></div>
    <div class="callout callout-info"><strong class="text-accent">Interface endpoint (EKS 필수군)</strong><div class="on-surface-muted"><code>ecr.api</code>, <code>ecr.dkr</code>, <code>sts</code>, <code>eks-auth</code>(Pod Identity), <code>logs</code></div></div>
    <div class="callout callout-warning"><strong class="text-accent">gateway endpoint의 한계</strong><div class="on-surface-muted">peered VPC의 다른 리전, TGW, 온프렘에서는 사용할 수 없음. 리전마다 따로 생성</div></div>
  </div>
  <div class="mr01-calc">
    <div class="mr01-calc-row">
      <label for="mr01-gb">AWS API 트래픽 (GB/월)</label>
      <div class="slider-container"><input type="range" id="mr01-gb" min="0" max="20000" step="250" value="3000"><span class="slider-value" id="mr01-gb-v">3,000 GB</span></div>
    </div>
    <div class="mr01-calc-row">
      <label for="mr01-n">Interface endpoint 수</label>
      <div class="slider-container"><input type="range" id="mr01-n" min="1" max="12" step="1" value="5"><span class="slider-value" id="mr01-n-v">5개</span></div>
    </div>
    <div class="mr01-calc-row">
      <label for="mr01-az">AZ 수</label>
      <div class="slider-container"><input type="range" id="mr01-az" min="2" max="3" step="1" value="3"><span class="slider-value" id="mr01-az-v">3 AZ</span></div>
    </div>
    <div class="card-grid">
      <div class="metric-card"><div class="metric-value" id="mr01-nat">-</div><div class="metric-label">NAT 경유 처리 요금</div></div>
      <div class="metric-card"><div class="metric-value" id="mr01-vpce">-</div><div class="metric-label">Interface endpoint 요금</div></div>
      <div class="metric-card"><div class="metric-value" id="mr01-be">-</div><div class="metric-label">손익분기 트래픽</div></div>
    </div>
    <div class="mr01-note">us-east-1, 월 730시간 기준: NAT 처리 $0.045/GB, endpoint $0.01/AZ-hour + $0.01/GB. NAT 시간 요금은 다른 egress가 있어 유지된다고 가정, 리전 1개 기준</div>
  </div>
</div>
:::

:::script
var MR01_GB = document.getElementById('mr01-gb');
var MR01_N = document.getElementById('mr01-n');
var MR01_AZ = document.getElementById('mr01-az');
var MR01_HOURS = 730;
function mr01Usd(v) { return '$' + Math.round(v).toLocaleString('en-US'); }
function mr01Update() {
  var gb = parseInt(MR01_GB.value, 10);
  var n = parseInt(MR01_N.value, 10);
  var az = parseInt(MR01_AZ.value, 10);
  var nat = gb * 0.045;
  var fixed = n * az * 0.01 * MR01_HOURS;
  var vpce = fixed + gb * 0.01;
  var be = fixed / (0.045 - 0.01);
  document.getElementById('mr01-gb-v').textContent = gb.toLocaleString('en-US') + ' GB';
  document.getElementById('mr01-n-v').textContent = n + '개';
  document.getElementById('mr01-az-v').textContent = az + ' AZ';
  document.getElementById('mr01-nat').textContent = mr01Usd(nat);
  document.getElementById('mr01-vpce').textContent = mr01Usd(vpce);
  document.getElementById('mr01-be').textContent = Math.round(be).toLocaleString('en-US') + ' GB';
}
MR01_GB.addEventListener('input', mr01Update);
MR01_N.addEventListener('input', mr01Update);
MR01_AZ.addEventListener('input', mr01Update);
mr01Update();
:::

:::notes
{timing: 2.5min}
[요약]
- S3, DynamoDB gateway endpoint는 무료이며 ECR 레이어 pull도 S3를 쓰므로 항상 만듭니다.
- Private 노드의 EKS에는 ecr.api, ecr.dkr, sts, eks-auth, logs interface endpoint가 기본입니다.
- us-east-1 기준 NAT 처리는 $0.045/GB, interface endpoint는 $0.01/AZ-hour + $0.01/GB입니다.
- 기본값(5개, 3 AZ)의 손익분기는 월 약 3,129 GB이고, 보안상 이유로 트래픽이 적어도 만들 가치가 있습니다.

VPC endpoint 전략입니다. 왼쪽 위 gateway endpoint는 S3와 DynamoDB용이고 추가 요금이 없습니다. ECR 이미지 레이어는 S3에서 받으므로 무조건 만듭니다. 다만 gateway endpoint는 peered VPC의 다른 리전이나 TGW 너머에서는 쓸 수 없으니 리전마다 각자 만들어야 합니다.
EKS 노드가 private subnet에 있으면 ecr.api, ecr.dkr, 그리고 IRSA를 쓴다면 sts, Pod Identity를 쓴다면 eks-auth endpoint가 필요합니다. 로그 전송용 logs도 기본으로 넣습니다.
{cue: demo}
오른쪽 계산기를 보겠습니다. 기본값은 endpoint 5개, AZ 3개, 월 3,000 GB입니다. NAT로 보내면 처리 요금이 135달러, endpoint로 보내면 고정비 약 110달러에 처리 요금 30달러로 약 140달러입니다. 손익분기는 약 3,129 GB입니다. 트래픽 슬라이더를 1만 GB로 올리면 NAT는 450달러, endpoint는 약 210달러가 됩니다.
{cue: pause}
예전 자료의 "82% 절감" 같은 숫자는 특정 가정에서만 나오는 값이라 쓰지 않고, 직접 넣어보는 계산기로 바꿨습니다. 그리고 비용이 손익분기보다 낮더라도, AWS API 트래픽을 NAT와 인터넷 경로 밖으로 빼는 보안 이점 때문에 EKS 필수 endpoint는 만드는 것을 권합니다. 리전이 두 개이니 실제 비용은 리전 수만큼 곱해야 합니다.
{cue: transition}
지금까지의 결정을 표 하나로 정리하겠습니다.
[출처]
- NAT Gateway us-east-1 $0.045/hour, $0.045/GB: AWS Price List API, AmazonEC2 NAT Gateway, 게시일 2026-10-15
- Interface endpoint $0.01/hour per ENI, $0.01/GB(첫 1 PB): https://aws.amazon.com/privatelink/pricing/
- Gateway endpoint 무료, peering/TGW 너머 미지원: https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints-s3.html
- eks-auth, sts endpoint 요구: https://docs.aws.amazon.com/eks/latest/userguide/private-clusters.html
:::

---
<!-- Slide 13: 아키텍처 결정 요약 -->
@type: content
@title: 이번 블록의 아키텍처 결정

## 이번 블록의 아키텍처 결정

:::html
<style>
.mr01-adr { width: 100%; border-collapse: collapse; font-size: var(--fs-card); }
.mr01-adr th, .mr01-adr td { text-align: left; padding: var(--space-2) var(--space-3); border-bottom: 1px solid var(--surface-3); word-break: keep-all; }
.mr01-adr th { color: var(--text-secondary); font-weight: var(--weight-semibold); }
.mr01-adr td:first-child { color: var(--accent); font-weight: var(--weight-bold); white-space: nowrap; }
.mr01-adr td:last-child { color: var(--text-secondary); }
</style>
<table class="mr01-adr" data-reveal="static">
  <thead><tr><th>영역</th><th>결정</th><th>대가, 주의점</th></tr></thead>
  <tbody>
    <tr><td>데이터 패턴</td><td>Write-Primary / Read-Local, 데이터별 일관성 선택</td><td>서부 쓰기는 리전 간 RTT 부담</td></tr>
    <tr><td>진입</td><td>CloudFront → VPC origin → internal ALB</td><td>VPC에 IGW 필요, ALB SG는 CloudFront prefix list 또는 VPC origin SG만 허용</td></tr>
    <tr><td>컴퓨트</td><td>리전별 독립 EKS, 같은 버전, GitOps 배포</td><td>흡수 용량을 평소에 확보</td></tr>
    <tr><td>네트워크</td><td>겹치지 않는 /16, 3-tier, public 티어엔 NAT만</td><td>Pod IP까지 포함해 CIDR 산정</td></tr>
    <tr><td>리전 간</td><td>TGW peering + static route</td><td>SG 참조, DNS 해석 불가. 리전 3개 이상이면 Cloud WAN 검토</td></tr>
    <tr><td>AWS API</td><td>Gateway endpoint 항상, EKS 필수 interface endpoint</td><td>리전마다 생성, 손익분기 확인</td></tr>
    <tr><td>IAM</td><td>EKS Pod Identity</td><td>association은 클러스터마다</td></tr>
  </tbody>
</table>
:::

:::notes
{timing: 1.5min}
[요약]
- 일곱 가지 결정을 "결정"과 "대가" 두 열로 정리했습니다.
- 진입은 CloudFront와 VPC origin, internal ALB이며 ALB SG는 CloudFront 출처만 허용합니다.
- 리전 간은 TGW peering이고, 리전이 늘면 Cloud WAN을 검토합니다.

이번 블록에서 내린 결정을 표로 정리했습니다. 각 행의 오른쪽 열은 그 결정의 대가입니다. 결정만 기억하면 나중에 왜 이렇게 했는지를 잊기 쉬워서, 대가를 같이 적어두는 습관을 권합니다.
{cue: pause}
진입 행을 다시 강조하겠습니다. 공개 진입점은 CloudFront 하나이고, VPC origin으로 internal ALB에 붙습니다. ALB의 SG는 CloudFront managed prefix list인 com.amazonaws.global.cloudfront.origin-facing이나, VPC origin을 만들면 생기는 CloudFront-VPCOrigins-Service-SG만 허용합니다. 후자가 내 distribution으로만 좁혀서 더 엄격합니다. 어떤 SG도 인터넷 전체에 열지 않습니다.
예전 자료에 있던 Karpenter 노드풀 구성, KEDA, 서비스별 KMS 같은 항목은 이 블록 주제와 거리가 있어 뺐습니다.
{cue: transition}
핵심을 세 줄로 정리하고 퀴즈로 넘어가겠습니다.
[출처]
- VPC origin SG 구성 옵션 두 가지: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-vpc-origins.html
:::

---
<!-- Slide 14: Key Takeaways -->
@type: content
@title: Key Takeaways

## Key Takeaways

:::html
<style>
.mr01-kt { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-3); }
.mr01-kt-no { display: inline-block; min-width: 1.6em; margin-right: var(--space-2); text-align: center; border-radius: 50%; background: var(--accent); color: var(--surface-1); font-weight: var(--weight-bold); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="mr01-kt fragment" data-reveal="stagger" data-reveal-anim="zoom" data-fragment-index="1">
  <div class="card"><span class="mr01-kt-no">1</span><strong class="text-accent">목적이 패턴을 정한다</strong><div class="on-surface-muted">가용성, 지연, 레지던시 중 무엇이 목표인지가 Active-Active와 Active-Passive를 가른다</div></div>
  <div class="card"><span class="mr01-kt-no">2</span><strong class="text-accent">평소의 지연이 진짜 비용</strong><div class="on-surface-muted">PACELC 관점에서 데이터마다 Strong, Session, Eventual을 고른다</div></div>
  <div class="card"><span class="mr01-kt-no">3</span><strong class="text-accent">쓰기는 한 곳에 모은다</strong><div class="on-surface-muted">Write-Primary / Read-Local은 충돌을 없애는 대신 서부 쓰기 지연을 받아들인다</div></div>
  <div class="card"><span class="mr01-kt-no">4</span><strong class="text-accent">네트워크는 처음에 정한다</strong><div class="on-surface-muted">겹치지 않는 CIDR, private 진입, TGW static route는 나중에 바꾸기 가장 어렵다</div></div>
</div>
:::

:::notes
{timing: 1min}
[요약]
- 목적이 패턴을 정합니다.
- 장애 때뿐 아니라 평소의 지연이 일관성 선택의 진짜 비용입니다.
- 쓰기를 한 곳에 모으면 충돌이 사라지는 대신 원격 쓰기 지연이 생깁니다.
- CIDR, 진입 경로, 리전 간 라우팅은 처음에 정해야 합니다.

네 가지로 정리하겠습니다. 첫째, 멀티리전의 목적이 패턴을 정합니다. 둘째, 일관성의 비용은 장애 때보다 평소의 지연으로 더 크게 다가오므로 데이터마다 다르게 고릅니다.
{cue: pause}
셋째, 쓰기를 한 리전에 모으면 충돌 해결이 필요 없어지지만 서부의 쓰기는 느려집니다. 넷째, CIDR과 진입 경로와 리전 간 라우팅은 서비스가 올라간 뒤에 바꾸기가 가장 어려우니 처음에 정합니다.
{cue: transition}
배운 내용을 퀴즈로 확인해 보겠습니다.
:::

---
<!-- Slide 15: Knowledge Check -->
@type: content
@title: Knowledge Check

## Knowledge Check

:::html
<style>
.mr01-quiz { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); align-items: start; }
.mr01-quiz .quiz { margin: 0; }
.mr01-quiz .quiz-question { word-break: keep-all; }
.mr01-quiz .quiz-option { word-break: keep-all; text-align: left; }
</style>
<div class="mr01-quiz" data-reveal="static">
  <div class="quiz" data-quiz="mr01-q1">
    <div class="quiz-question">Q1: Aurora PostgreSQL write forwarding의 기본 consistency_mode인 SESSION의 의미는?</div>
    <div class="quiz-options">
      <button class="quiz-option" data-correct="false">다른 리전의 모든 커밋을 따라잡은 뒤 읽는다</button>
      <button class="quiz-option" data-correct="true">내 세션이 쓴 변경은 같은 세션의 이후 읽기에서 보인다</button>
      <button class="quiz-option" data-correct="false">기다리지 않으므로 내 쓰기도 늦게 보일 수 있다</button>
    </div>
    <div class="quiz-feedback"></div>
  </div>
  <div class="quiz" data-quiz="mr01-q2">
    <div class="quiz-question">Q2: Transit Gateway inter-Region peering에 대해 옳은 것은?</div>
    <div class="quiz-options">
      <button class="quiz-option" data-correct="false">BGP로 상대 리전 경로가 자동 전파된다</button>
      <button class="quiz-option" data-correct="false">ECMP로 여러 peering을 묶어 대역폭을 늘린다</button>
      <button class="quiz-option" data-correct="true">상대 리전 CIDR을 peering attachment로 보내는 static route를 직접 추가한다</button>
    </div>
    <div class="quiz-feedback"></div>
  </div>
  <div class="quiz" data-quiz="mr01-q3">
    <div class="quiz-question">Q3: CloudFront VPC origin 뒤 internal ALB의 SG 설정으로 옳은 것은?</div>
    <div class="quiz-options">
      <button class="quiz-option" data-correct="false">인바운드 443을 모든 IPv4 주소에 연다</button>
      <button class="quiz-option" data-correct="true">CloudFront origin-facing prefix list 또는 CloudFront-VPCOrigins-Service-SG만 허용한다</button>
      <button class="quiz-option" data-correct="false">ALB를 internet-facing으로 바꾸고 WAF로 막는다</button>
    </div>
    <div class="quiz-feedback"></div>
  </div>
</div>
:::

:::notes
{timing: 1.5min}
[요약]
- Q1 정답: SESSION은 read-your-writes입니다. 다른 리전 커밋까지 기다리는 것은 GLOBAL입니다.
- Q2 정답: TGW peering은 static route만 지원합니다. ECMP는 VPN, Connect attachment 기능입니다.
- Q3 정답: CloudFront prefix list 또는 VPC origin service SG만 허용합니다.

세 문제입니다. 1번은 write forwarding의 기본 consistency_mode입니다. SESSION은 내 세션이 쓴 것을 내 세션에서 바로 보는 read-your-writes이고, 다른 리전 커밋까지 따라잡는 것은 GLOBAL, 기다리지 않는 것은 EVENTUAL입니다.
{cue: pause}
2번은 TGW peering입니다. peering attachment에는 경로 전파가 없어서 static route를 직접 넣습니다. ECMP는 VPN과 Connect attachment 기능이라 오답입니다. 3번은 진입 경로입니다. ALB는 internal로 두고 SG는 CloudFront 출처만 허용합니다. 인터넷 전체에 열거나 internet-facing으로 바꾸는 것은 이 설계의 전제를 깨는 선택입니다.
{cue: transition}
Block 1을 마치겠습니다.
[출처]
- https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-write-forwarding-apg.html
- https://docs.aws.amazon.com/vpc/latest/tgw/tgw-peering.html
- https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-vpc-origins.html
:::

---
<!-- Slide 16: Thank You -->
@type: thankyou
@toc: toc.html
@next: 02-data-sync.html
@next-label: 다음: Data Sync & Replication
@message: Block 1: Multi-Region Foundation 완료

:::notes
{timing: 0.5min}
[요약]
- Block 1 마무리
- 다음 블록은 Data Sync & Replication

Block 1을 마무리합니다. 잠시 쉬었다가 Block 2에서 Aurora, DocumentDB, ElastiCache, MSK의 복제 방식을 자세히 보겠습니다.
{cue: transition}
감사합니다.
:::
