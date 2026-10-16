---
remarp: true
block: 02-data-sync
---

---
<!-- Slide 1: 블록 커버 (Section) -->
@type: section

# Block 2: Data Sync & Replication

쓰기는 어디서 받고, 복제는 얼마나 늦으며, 장애 때 무엇을 잃는가

:::notes
{timing: 0.5min}
[요약]
• 이 블록의 질문: 리전이 둘일 때 데이터는 누가 쓰고, 얼마나 늦게 따라오며, 장애 시 무엇을 잃는가
• 순서: 저장소 선택 → 복제 모델 → Aurora Global Database → DSQL → DocumentDB, Valkey, 캐시 → MSK → DynamoDB → RPO 매트릭스
• 시나리오는 Block 1과 같음: 이커머스 order, payment, catalog, cart, us-east-1 primary, us-west-2 secondary
Block 2에서는 데이터 이야기를 합니다. 멀티리전에서 가장 비싼 실수는 대부분 데이터 계층에서 나옵니다.
Block 1과 같은 이커머스 시나리오로 갑니다. 주문, 결제, 카탈로그, 장바구니 서비스가 있고, us-east-1이 primary, us-west-2가 secondary입니다.
각 저장소마다 세 가지를 묻겠습니다. 쓰기는 어디서 받는가, 복제는 얼마나 늦는가, 리전 장애가 나면 무엇을 잃는가.
{cue: transition}
먼저 서비스별로 어떤 저장소를 쓰는지부터 보겠습니다.
:::

---
<!-- Slide 2: Polyglot Persistence -->
@type: content
@title: 서비스마다 맞는 저장소가 다르다

## 서비스마다 맞는 저장소가 다르다

:::html
<style>
.mr02-acc  { color: var(--accent);  font-weight: var(--weight-bold); }
.mr02-info { color: var(--info);    font-weight: var(--weight-bold); }
.mr02-ok   { color: var(--success); font-weight: var(--weight-bold); }
.mr02-warn { color: var(--warning); font-weight: var(--weight-bold); }
.mr02-bad  { color: var(--danger);  font-weight: var(--weight-bold); }
.mr02-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.mr02-cap { font-size: var(--fs-caption); color: var(--text-secondary); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: break-word; }
.mr02-split { display: grid; grid-template-columns: 1.15fr 1fr; gap: var(--space-4); align-items: start; }
.mr02-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.mr02-code { font-family: var(--font-mono); font-size: var(--fs-caption); white-space: pre-wrap; overflow-wrap: anywhere; background: var(--surface-2); border: 1px solid var(--surface-3); border-radius: var(--radius-md); padding: var(--space-3); overflow: hidden; line-height: 1.6; margin: 0; }
.mr02-table { width: 100%; font-size: var(--fs-caption); word-break: keep-all; overflow-wrap: break-word; }
.mr02-table th { font-size: var(--fs-card); }
.mr02-table code, .mr02-muted code, .mr02-cap code { font-family: var(--font-mono); }
.mr02-take { margin-top: var(--space-3); }
.mr02-g2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-3); }
.mr02-edge { display: flex; align-items: center; gap: var(--space-2); flex-wrap: wrap; font-size: var(--fs-caption); color: var(--text-secondary); margin-bottom: var(--space-3); }
.mr02-chip { border: 1px solid var(--surface-3); background: var(--surface-2); border-radius: var(--radius-pill); padding: var(--space-1) var(--space-3); color: var(--on-surface); }
.mr02-ico { width: 1.5rem; height: 1.5rem; vertical-align: middle; margin-right: var(--space-1); }
</style>
<div class="mr02-edge">
  <span class="mr02-chip">CloudFront</span><span>→</span>
  <span class="mr02-chip">VPC origin</span><span>→</span>
  <span class="mr02-chip">internal ALB</span><span>→</span>
  <span class="mr02-chip">EKS 서비스 (private subnet)</span><span>→</span>
  <span>데이터 계층은 모두 private 연결로만 접근</span>
</div>
<div class="card-grid" data-reveal="stagger">
  <div class="metric-card"><strong class="mr02-acc"><img class="mr02-ico" src="./common/aws-icons/services/Arch_Amazon-Aurora_48.svg" alt="Amazon Aurora">Aurora PostgreSQL Global DB</strong><div class="mr02-muted">order, payment, inventory: ACID 트랜잭션, 단일 writer</div></div>
  <div class="metric-card"><strong class="mr02-acc"><img class="mr02-ico" src="./common/aws-icons/services/Arch_Amazon-DocumentDB_48.svg" alt="Amazon DocumentDB">DocumentDB Global Cluster</strong><div class="mr02-muted">catalog, user-profile, review: 유연한 문서 스키마, 읽기 위주</div></div>
  <div class="metric-card"><strong class="mr02-info"><img class="mr02-ico" src="./common/aws-icons/services/Arch_Amazon-ElastiCache_48.svg" alt="Amazon ElastiCache">ElastiCache for Valkey</strong><div class="mr02-muted">cart, session, rate-limit: 밀리초 응답, 원본이 아닌 사본</div></div>
  <div class="metric-card"><strong class="mr02-info"><img class="mr02-ico" src="./common/aws-icons/services/Arch_Amazon-Managed-Streaming-for-Apache-Kafka_48.svg" alt="Amazon MSK">Amazon MSK</strong><div class="mr02-muted">order.created 등 도메인 이벤트, saga 조율의 백본</div></div>
  <div class="metric-card"><strong class="mr02-ok"><img class="mr02-ico" src="./common/aws-icons/services/Arch_Amazon-DynamoDB_48.svg" alt="Amazon DynamoDB">DynamoDB Global Tables</strong><div class="mr02-muted">payment idempotency key, 주문 상태 조회처럼 key 단위 접근</div></div>
  <div class="metric-card"><strong class="mr02-ok"><img class="mr02-ico" src="./common/aws-icons/services/Arch_Amazon-Aurora_48.svg" alt="Amazon Aurora DSQL">Aurora DSQL (대안)</strong><div class="mr02-muted">양 리전 쓰기와 RPO 0이 꼭 필요한 SQL 워크로드의 선택지</div></div>
</div>
<div class="callout callout-info mr02-take fragment zoom-in" data-fragment-index="1"><strong class="mr02-info">원칙</strong><div class="mr02-muted">저장소마다 복제 모델, 지연, 장애 시 손실이 다릅니다. 서비스별로 "쓰기 위치"와 "허용 RPO"를 먼저 정하고 저장소를 고릅니다.</div></div>
:::

:::notes
{timing: 2min}
[요약]
• 이커머스 서비스별 저장소: Aurora PostgreSQL(주문, 결제, 재고), DocumentDB(카탈로그), Valkey(장바구니, 세션), MSK(이벤트), DynamoDB(idempotency key)
• Aurora DSQL은 양 리전 쓰기와 RPO 0이 필요할 때 검토하는 대안
• 진입 경로는 CloudFront → VPC origin → internal ALB, 데이터 계층은 private 연결만
• 저장소 선택보다 먼저 서비스별 쓰기 위치와 허용 RPO를 정의
Polyglot persistence, 즉 워크로드마다 맞는 저장소를 쓴다는 원칙입니다. 멀티리전에서는 이 선택이 곧 복제 방식의 선택이 됩니다.
주문과 결제, 재고는 트랜잭션이 필요하니 Aurora PostgreSQL Global Database, 카탈로그와 프로필은 DocumentDB, 장바구니와 세션은 Valkey 캐시, 서비스 간 이벤트는 MSK입니다. 결제 중복을 막는 idempotency key는 DynamoDB Global Tables에 둡니다.
{cue: pause}
위쪽 띠는 트래픽 경로입니다. 사용자는 CloudFront로만 들어오고, VPC origin을 통해 internal ALB로 갑니다. 저장소는 어느 것도 인터넷에 노출하지 않습니다.
{cue: question}
여러분 서비스는 저장소가 몇 종류인가요? 종류가 늘수록 리전 장애 시 각각의 RPO가 달라진다는 점이 이 블록의 핵심입니다.
{cue: transition}
저장소가 많아 보여도 복제 모델은 세 가지로 정리됩니다.
[근거]
• 보안 경로는 Block 1 기준 아키텍처(CloudFront VPC origin, internal ALB). 서비스 매핑은 발표자 설계 예시
:::

---
<!-- Slide 3: 복제 모델과 일관성-지연 트레이드오프 -->
@type: content
@title: 복제 모델은 세 가지, 대가는 지연

## 복제 모델은 세 가지, 대가는 지연

:::html
<style>
.mr02-spec { display: flex; justify-content: space-between; font-size: var(--fs-caption); color: var(--text-secondary); border-bottom: 2px solid var(--surface-3); padding-bottom: var(--space-2); margin-bottom: var(--space-3); }
.mr02-models { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-4); }
.mr02-models ul { margin: var(--space-2) 0 0 0; padding-left: var(--space-5); font-size: var(--fs-card); }
.mr02-models li { margin-bottom: var(--space-1); word-break: keep-all; }
</style>
<div class="mr02-spec"><span>← 강한 일관성, 쓰기 지연 큼</span><span>쓰기 지연 작음, 결과적 일관성 →</span></div>
<div class="mr02-models">
  <div class="callout callout-success fragment fade-right" data-fragment-index="1"><strong class="mr02-ok">① 동기 multi-Region</strong>
    <ul><li>커밋 전에 다른 리전에 기록</li><li>Aurora DSQL, DynamoDB MRSC</li><li>RPO 0, 대신 쓰기마다 리전 간 왕복</li></ul></div>
  <div class="callout callout-info fragment fade-right" data-fragment-index="2"><strong class="mr02-info">② 단일 writer + 비동기 복제</strong>
    <ul><li>쓰기는 primary 한 곳</li><li>Aurora Global DB, DocumentDB Global, Valkey Global Datastore</li><li>읽기는 로컬, 장애 시 lag만큼 손실 가능</li></ul></div>
  <div class="callout callout-warning fragment fade-right" data-fragment-index="3"><strong class="mr02-warn">③ multi-writer + 비동기</strong>
    <ul><li>모든 리전이 로컬 쓰기</li><li>DynamoDB MREC, MSK active-active</li><li>충돌 해소 규칙(last writer wins)을 앱이 수용</li></ul></div>
</div>
<div class="callout callout-info mr02-take fragment zoom-in" data-fragment-index="4"><strong class="mr02-info">설계 규칙</strong><div class="mr02-muted">쓰기 경로는 일관성을, 읽기 경로는 지연을 우선합니다. 같은 서비스 안에서도 쓰기와 읽기의 모델이 다를 수 있습니다.</div></div>
:::

:::notes
{timing: 2.5min}
[요약]
• 동기 multi-Region: 커밋 전에 다른 리전 기록, RPO 0, 쓰기 지연 증가 (DSQL, DynamoDB MRSC)
• 단일 writer + 비동기: 대부분의 Global 기능, 읽기 로컬, 장애 시 lag만큼 손실
• multi-writer + 비동기: DynamoDB MREC, 충돌은 last writer wins
• 규칙: 쓰기 경로는 일관성 우선, 읽기 경로는 지연 우선
복제 방식은 이름이 달라도 세 가지 모델로 분류됩니다. 하나씩 눌러 보겠습니다.
첫째, 동기 multi-Region입니다. 커밋이 끝나기 전에 다른 리전에도 기록되므로 리전 하나가 사라져도 데이터는 남습니다. 대신 모든 쓰기가 리전 간 왕복 시간을 냅니다. Aurora DSQL과 DynamoDB의 multi-Region strong consistency가 여기에 속합니다.
{cue: pause}
둘째, 가장 흔한 단일 writer와 비동기 복제입니다. 쓰기는 primary에서만, 읽기는 각 리전에서 로컬로 합니다. Aurora Global Database, DocumentDB Global Cluster, Valkey Global Datastore가 모두 이 모델입니다. 평시 복제 지연은 보통 1초 미만이지만, 비계획 장애에서는 그만큼을 잃을 수 있습니다.
셋째, 모든 리전이 쓰는 비동기 모델입니다. DynamoDB의 기본 global table 모드가 여기 속하고, 같은 item을 두 리전에서 거의 동시에 쓰면 마지막 쓰기가 이깁니다.
{cue: question}
주문 서비스의 쓰기와 상품 조회의 읽기를 같은 모델로 둘 필요가 있을까요? 대부분 아닙니다.
{cue: transition}
가장 많이 쓰는 두 번째 모델, Aurora Global Database부터 자세히 보겠습니다.
[근거]
• DynamoDB global tables MREC, MRSC: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/V2globaltables_HowItWorks.html
• Aurora DSQL GA 발표: https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-aurora-dsql-generally-available/
:::

---
<!-- Slide 4: Aurora Global Database 토폴로지 -->
@type: content
@title: Aurora Global DB: 스토리지가 복제한다

## Aurora Global DB: 스토리지가 복제한다

:::html
<div class="mr02-split">
  <div>
    <div class="flow-h">
      <div class="flow-group"><div class="flow-group-label">us-east-1 (primary)</div><div class="flow-box">Writer 1대</div><div class="flow-box">Reader 최대 15 - s대</div><div class="flow-box">order, payment, inventory</div></div>
      <div class="flow-arrow">→ 스토리지 복제<br>보통 1초 미만 →</div>
      <div class="flow-group"><div class="flow-group-label">us-west-2 (secondary)</div><div class="flow-box">Reader 최대 16대</div><div class="flow-box">로컬 읽기</div><div class="flow-box">write forwarding (선택)</div></div>
    </div>
    <div class="mr02-cap">s = secondary 리전 수. secondary가 늘면 primary의 reader 한도가 그만큼 줄어듭니다 (예: secondary 10개면 primary reader 5대).</div>
  </div>
  <div class="mr02-stack fragment" data-reveal="stagger" data-reveal-anim="left" data-fragment-index="1">
    <div class="metric-card"><strong class="mr02-acc">secondary 최대 10개 리전</strong><div class="mr02-muted">예전 자료의 "최대 5개"는 구버전 한도. 리전마다 클러스터는 1개</div></div>
    <div class="metric-card"><strong class="mr02-info">Aurora PostgreSQL 18.3 이상 지원</strong><div class="mr02-muted">Global DB는 PG 11부터 18까지 지원. 2026-09 기준 최신 minor는 18.6, 17.11</div></div>
    <div class="metric-card"><strong class="mr02-ok">global writer endpoint</strong><div class="mr02-muted">switchover, failover 후에도 같은 이름이 새 primary를 가리킴. 앱 연결 문자열 변경 불필요</div></div>
  </div>
</div>
<div class="callout callout-warning mr02-take fragment zoom-in" data-fragment-index="2"><strong class="mr02-warn">비동기라는 사실은 변하지 않음</strong><div class="mr02-muted">RPO는 보통 초 단위의 0이 아닌 값입니다. 그래서 다음 슬라이드들의 write forwarding, switchover, RPO 상한 설정이 필요합니다.</div></div>
:::

:::notes
{timing: 2min}
[요약]
• primary 리전에 writer 1대, secondary는 reader만, 스토리지 계층 비동기 복제(보통 1초 미만)
• secondary 최대 10개 리전, primary reader 한도는 15에서 secondary 수만큼 감소
• Global DB는 Aurora PostgreSQL 18.3 이상도 지원, 2026-09 최신 minor 18.6
• global writer endpoint를 쓰면 전환 후 연결 문자열 변경 불필요
Aurora Global Database는 논리 복제가 아니라 스토리지 계층에서 복제합니다. 그래서 primary 성능에 주는 영향이 작고, 복제 지연은 보통 1초 미만입니다.
한도가 바뀌었습니다. 예전 자료에는 secondary 리전이 최대 5개로 되어 있지만 현재는 10개입니다. 다만 primary의 reader 15대 한도에서 secondary 수만큼 빠지니, secondary를 많이 두면 primary reader가 줄어듭니다.
{cue: pause}
엔진 버전도 갱신하겠습니다. 예전 예시인 PostgreSQL 15.4는 이제 오래된 버전입니다. Global Database는 Aurora PostgreSQL 18.3 이상을 지원하고, 2026년 9월 릴리스 기준 최신 minor는 18.6입니다. 인스턴스는 memory-optimized 계열이 필요하고 AWS는 db.r5 이상을 권장합니다.
마지막 카드가 운영에서 가장 중요합니다. 앱은 리전별 cluster endpoint가 아니라 global writer endpoint로 연결하세요. 전환 후에도 같은 이름이 새 primary를 가리킵니다.
{cue: transition}
그럼 us-west-2에 있는 주문 서비스가 쓰기를 해야 하면 어떻게 할까요? write forwarding입니다.
[근거]
• 구성 한도: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.configuration.requirements.html
• 지원 엔진: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Concepts.Aurora_Fea_Regions_DB-eng.Feature.GlobalDatabase.html
• 최신 minor: https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-aurora-postgresql-18-6-17-11-16-15-15-19-14-24/
:::

---
<!-- Slide 5: Write Forwarding -->
@type: content
@title: Write Forwarding은 대신 전달한다

## Write Forwarding은 대신 전달한다

:::html
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">① 동작 흐름</button>
  <button class="tab-btn">② consistency_mode</button>
  <button class="tab-btn">③ 지원되지 않는 SQL</button>
  <button class="tab-btn">④ 켜는 방법</button>
</div>
<div class="tc">
  <div class="flow-h">
    <div class="flow-group"><div class="flow-group-label">us-west-2</div><div class="flow-box">order-service</div><div class="flow-box">secondary reader endpoint</div></div>
    <div class="flow-arrow">→ DML 전달 →</div>
    <div class="flow-group"><div class="flow-group-label">us-east-1</div><div class="flow-box">primary writer 실행, 커밋</div></div>
    <div class="flow-arrow">→ 스토리지 복제 →</div>
    <div class="flow-group"><div class="flow-group-label">us-west-2</div><div class="flow-box">변경 반영 후 읽기</div></div>
  </div>
  <div class="mr02-cap"><strong class="mr02-acc">DML만 전달</strong>되고, 전달된 쓰기마다 리전 간 왕복이 붙습니다. statement가 많은 긴 트랜잭션보다 가끔 발생하는 짧은 쓰기에 적합하며, 지연 수치는 반드시 실측하세요.</div>
</div>
<div class="tc" hidden>
  <table class="data-table mr02-table">
    <thead><tr><th>값</th><th>같은 세션의 쓰기</th><th>다른 세션, 리전의 커밋</th><th>대기 비용</th></tr></thead>
    <tbody>
      <tr><td><code>SESSION</code> (기본)</td><td>즉시 보임 (복제 대기)</td><td>기다리지 않음</td><td>중간</td></tr>
      <tr><td><code>EVENTUAL</code></td><td>복제된 뒤에야 보임</td><td>기다리지 않음</td><td>가장 낮음</td></tr>
      <tr><td><code>GLOBAL</code></td><td>즉시 보임</td><td>쿼리 시작 시점까지의 모든 커밋을 기다림</td><td>가장 높음</td></tr>
      <tr><td><code>OFF</code></td><td colspan="3">해당 세션에서 write forwarding 끔</td></tr>
    </tbody>
  </table>
  <div class="mr02-cap">파라미터 <code>apg_write_forward.consistency_mode</code>, 세션 단위로 바꿀 수 있고 재부팅 불필요. 격리 수준은 <code>READ COMMITTED</code>, <code>REPEATABLE READ</code>만 지원 (<code>SERIALIZABLE</code> 불가).</div>
</div>
<div class="tc" hidden>
  <div class="card-grid">
    <div class="callout callout-danger"><strong class="mr02-bad">DDL, 권한</strong><div class="mr02-muted">CREATE, ALTER, GRANT, REVOKE는 primary에서 직접 실행</div></div>
    <div class="callout callout-warning"><strong class="mr02-warn">세션 제어</strong><div class="mr02-muted">SAVEPOINT, LOCK, SET CONSTRAINTS, cursor 미지원</div></div>
    <div class="callout callout-warning"><strong class="mr02-warn">대량 작업</strong><div class="mr02-muted">COPY, TRUNCATE, SELECT INTO, VACUUM, ANALYZE 미지원</div></div>
    <div class="callout callout-info"><strong class="mr02-info">사용자 정의 함수, 프로시저</strong><div class="mr02-muted">지원되지 않으므로 ORM, 마이그레이션 도구의 동작 확인 필요</div></div>
  </div>
</div>
<div class="tc" hidden>
  <pre class="mr02-code"># secondary 클러스터에서 켜기 (중단, 재부팅 없음, 기본은 꺼짐)
aws rds modify-db-cluster --region us-west-2 \
  --db-cluster-identifier orders-usw2 \
  --enable-global-write-forwarding

# 세션에서 일관성 모드 확인
SHOW apg_write_forward.consistency_mode;</pre>
  <div class="mr02-cap">버전: PG 16 이상은 모든 minor, 15는 15.4 이상, 14는 14.9 이상. 상태는 <code>GlobalWriteForwardingStatus</code>로 확인합니다.</div>
</div>
<div class="callout callout-info mr02-take fragment zoom-in" data-fragment-index="1"><strong class="mr02-info">한 줄 정리</strong><div class="mr02-muted">write forwarding은 "secondary에서 쓰기 가능"이 아니라 "secondary가 대신 전달"입니다. write-heavy 서비스는 primary 리전에 둡니다.</div></div>
:::

:::notes
{timing: 2.5min}
[요약]
• secondary reader endpoint로 보낸 DML을 Aurora가 primary로 전달, 커밋 후 복제로 되돌아옴
• consistency_mode: SESSION(기본), EVENTUAL, GLOBAL, OFF
• DDL, SAVEPOINT, COPY, TRUNCATE, cursor, 사용자 정의 함수는 미지원, 기본값은 꺼짐
• PG 16 이상 모든 minor, 15.4 이상, 14.9 이상에서 지원
네 개 탭으로 보겠습니다. 첫 번째, 동작 흐름입니다. us-west-2의 주문 서비스가 secondary의 reader endpoint로 INSERT를 보내면 Aurora가 primary writer로 전달하고, 커밋된 결과가 스토리지 복제로 돌아옵니다. 즉 쓰기마다 리전 간 왕복이 붙습니다. 예전 자료에 있던 "트랜잭션 3개면 180에서 240 ms" 같은 수치는 환경마다 달라서 쓰지 않습니다. 직접 측정하세요.
{cue: pause}
두 번째 탭, 일관성 모드입니다. 기본값 SESSION은 내 세션이 방금 쓴 값을 바로 읽게 해 줍니다. EVENTUAL은 가장 빠르지만 내가 쓴 값도 복제될 때까지 안 보이고, GLOBAL은 다른 리전의 커밋까지 기다리므로 가장 느립니다.
세 번째 탭이 실무에서 자주 걸리는 부분입니다. DDL, SAVEPOINT, COPY, TRUNCATE, cursor, 사용자 정의 함수가 지원되지 않습니다. ORM이 SAVEPOINT를 쓰는 경우가 많으니 꼭 확인하세요. 그래서 기본값이 꺼져 있습니다.
네 번째 탭은 켜는 방법입니다. modify-db-cluster에 enable-global-write-forwarding 옵션 하나이고 재부팅이 없습니다.
{cue: question}
여러분의 ORM은 트랜잭션 안에서 SAVEPOINT를 쓰나요?
{cue: transition}
다음은 primary 리전 자체를 옮기는 두 가지 방법, switchover와 failover입니다.
[근거]
• https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-write-forwarding-apg.html (버전, SQL 호환성, consistency_mode, CLI)
:::

---
<!-- Slide 6: Switchover vs Failover + RPO guard -->
@type: content
@title: Switchover만 RPO 0이다

## Switchover만 RPO 0이다

:::html
<style>
.mr02-rpo { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); align-items: start; }
.mr02-rpo label { display: block; font-size: var(--fs-card); margin-bottom: var(--space-2); }
.mr02-rpo input[type=range] { width: 100%; accent-color: var(--accent); }
.mr02-rpo select { font-size: var(--fs-card); background: var(--surface-2); color: var(--on-surface); border: 1px solid var(--surface-3); border-radius: var(--radius-sm); padding: var(--space-1) var(--space-2); }
.mr02-val { font-family: var(--font-mono); color: var(--accent); font-weight: var(--weight-bold); }
</style>
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">Switchover (계획)</button>
  <button class="tab-btn">Failover (비계획)</button>
  <button class="tab-btn">RPO 상한 시뮬레이터</button>
</div>
<div class="tc">
  <div class="mr02-split" data-reveal="static">
    <div class="mr02-stack">
      <div class="metric-card"><strong class="mr02-ok">동기화 후 전환 → RPO 0</strong><div class="mr02-muted">대상 secondary가 완전히 따라잡을 때까지 기다린 뒤 primary를 read-only로 바꾸고 승격</div></div>
      <div class="metric-card"><strong class="mr02-info">보통 30초 미만</strong><div class="mr02-muted">Aurora PostgreSQL 16.8, 15.12, 14.17, 13.20 이상에서 read/write 복구 시간</div></div>
      <div class="metric-card"><strong class="mr02-warn">조건</strong><div class="mr02-muted">모든 클러스터가 정상이고 major, minor 버전이 같아야 함. DR 훈련, 리전 순환, failback 용도</div></div>
    </div>
    <pre class="mr02-code"># --region 은 현재 primary 리전
# USW2_ARN: us-west-2 secondary 클러스터 ARN
aws rds switchover-global-cluster \
  --region us-east-1 \
  --global-cluster-identifier shop-global \
  --target-db-cluster-identifier "$USW2_ARN"</pre>
  </div>
</div>
<div class="tc" hidden>
  <div class="mr02-split">
    <div class="mr02-stack">
      <div class="metric-card"><strong class="mr02-bad">동기화를 기다리지 않음</strong><div class="mr02-muted">미복제 트랜잭션은 새 primary에 없음. old primary 복구 시 <code>rds:unplanned-global-failover-...</code> 스냅샷 시도</div></div>
      <div class="metric-card"><strong class="mr02-warn">write fencing은 best effort</strong><div class="mr02-muted">old primary가 잠시 쓰기를 받을 수 있어 split-brain 가능. 앱 쓰기를 먼저 멈추고 DNS 캐시 TTL은 5초 수준으로</div></div>
      <div class="metric-card"><strong class="mr02-info">복구 후 자동 재편입</strong><div class="mr02-muted">old primary 리전이 정상화되면 secondary로 다시 붙음. failback은 switchover로</div></div>
    </div>
    <pre class="mr02-code"># --region 은 승격할 secondary 리전
aws rds failover-global-cluster \
  --region us-west-2 \
  --global-cluster-identifier shop-global \
  --target-db-cluster-identifier "$USW2_ARN" \
  --allow-data-loss</pre>
  </div>
</div>
<div class="tc" hidden>
  <div class="mr02-rpo" data-rpo="60">
    <div>
      <label>클러스터 파라미터 <code>rds.global_db_rpo</code>
        <select onchange="(function(s){var r=s.closest('.mr02-rpo');r.setAttribute('data-rpo',s.value);r.querySelector('input').dispatchEvent(new Event('input'));})(this)">
          <option value="20">20초 (최솟값)</option><option value="60" selected>60초</option><option value="300">300초</option>
        </select></label>
      <label>us-west-2 secondary의 RPO lag: <span class="mr02-val mr02-lagv">10</span>초</label>
      <input type="range" min="0" max="400" step="5" value="10" oninput="(function(el){var r=el.closest('.mr02-rpo'),v=+el.value,rpo=+r.getAttribute('data-rpo'),ok=v&lt;rpo,s=r.querySelector('.mr02-state');r.querySelector('.mr02-lagv').textContent=v;s.className='callout mr02-state '+(ok?'callout-success':'callout-danger');s.querySelector('strong').className=ok?'mr02-ok':'mr02-bad';s.querySelector('strong').textContent=ok?'커밋 진행':'primary 커밋 대기';s.querySelector('.mr02-muted').textContent=ok?'lag '+v+'초 &lt; RPO '+rpo+'초: 최소 1개 secondary가 RPO 안에 있음':'lag '+v+'초 ≥ RPO '+rpo+'초: 모든 secondary가 RPO 밖, 따라잡을 때까지 커밋이 멈춤';})(this)">
      <div class="mr02-cap">관측 메트릭: <code>AuroraGlobalDBRPOLag</code> (ms, secondary 기준)</div>
    </div>
    <div class="mr02-stack">
      <div class="callout callout-success mr02-state"><strong class="mr02-ok">커밋 진행</strong><div class="mr02-muted">lag 10초 &lt; RPO 60초: 최소 1개 secondary가 RPO 안에 있음</div></div>
      <div class="callout callout-warning"><strong class="mr02-warn">리전이 둘뿐이라면</strong><div class="mr02-muted">secondary 파라미터 그룹에는 기본값 유지 권장. 그렇지 않으면 failover 직후 새 primary의 커밋이 멈출 수 있음</div></div>
    </div>
  </div>
</div>
:::

:::notes
{timing: 3min}
[요약]
• Switchover: 동기화 후 전환, RPO 0, 지원 버전에서 보통 30초 미만, 계획된 작업 전용
• Failover: --allow-data-loss, 동기화 대기 없음, write fencing은 best effort, 스냅샷으로 미복제분 복구 시도
• rds.global_db_rpo: 모든 secondary가 RPO를 넘으면 primary 커밋을 멈춤 (최솟값 20초)
• 리전 2개 구성이면 secondary 파라미터 그룹에는 기본값 유지
primary 리전을 옮기는 방법은 두 가지이고 RPO가 다릅니다. 첫 탭, switchover는 예전 이름이 managed planned failover입니다. secondary가 완전히 따라잡을 때까지 기다린 다음 전환하므로 데이터 손실이 없습니다. 2025년 이후 버전, PostgreSQL 기준 16.8, 15.12, 14.17, 13.20 이상에서는 보통 30초 안에 read/write가 돌아옵니다.
{cue: pause}
두 번째 탭, failover는 리전 장애용입니다. allow-data-loss 옵션 이름 그대로, 동기화를 기다리지 않습니다. Aurora는 old primary의 쓰기를 막는 write fencing을 시도하지만 보장되지 않으므로, 앱 쓰기를 먼저 멈추고 global writer endpoint와 짧은 DNS TTL을 쓰라고 문서가 권장합니다. 주의할 점 하나, switchover의 region 옵션은 현재 primary, failover는 승격할 secondary 리전입니다.
{cue: question}
세 번째 탭은 시뮬레이터입니다. RPO를 60초로 두고 lag 슬라이더를 올려 보겠습니다. lag가 60초를 넘는 순간 primary의 커밋이 멈춥니다. 데이터 손실 상한을 보장하는 대신 가용성을 내주는 장치입니다.
리전이 둘뿐인 우리 구성에서는 secondary 쪽 파라미터 그룹에 이 값을 넣지 마세요. failover 후 새 primary에는 따라올 secondary가 없어서 커밋이 멈출 수 있습니다.
{cue: transition}
여기까지가 단일 writer 모델입니다. 양 리전 모두 쓰고 RPO 0이 필요하다면 Aurora DSQL을 볼 차례입니다.
[근거]
• https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-disaster-recovery.html (switchover, failover CLI, 30초 버전 조건, write fencing, rds.global_db_rpo 동작과 2리전 권고)
:::

---
<!-- Slide 7: Aurora DSQL multi-Region -->
@type: content
@title: DSQL: 두 리전 모두 쓰고 동기 커밋

## DSQL: 두 리전 모두 쓰고 동기 커밋

:::html
<div class="mr02-split">
  <div>
    <div class="flow-h">
      <div class="flow-group"><div class="flow-group-label">us-east-1</div><div class="flow-box">peered cluster<br>읽기, 쓰기</div></div>
      <div class="flow-arrow">⇄ 동기 복제 ⇄</div>
      <div class="flow-group"><div class="flow-group-label">us-west-2</div><div class="flow-box">peered cluster<br>읽기, 쓰기</div></div>
    </div>
    <div class="flow-h mr02-take">
      <div class="flow-group"><div class="flow-group-label">us-east-2 (witness)</div><div class="flow-box">전체 사본 없음, 쓰기 로그로 내구성과 quorum 제공</div></div>
    </div>
    <div class="mr02-cap">multi-Region 클러스터는 같은 Region set 안에서만 구성 (북미 set: us-east-1, us-east-2, us-west-2, 캐나다 2개 리전). 대륙 간 구성은 미지원.</div>
  </div>
  <div class="mr02-stack fragment" data-reveal="stagger" data-reveal-anim="left" data-fragment-index="1">
    <div class="metric-card"><strong class="mr02-ok">RPO 0, 수동 failover 없음</strong><div class="mr02-muted">한 리전이 사라져도 나머지 리전이 계속 처리. 가용성 설계 목표 99.999%</div></div>
    <div class="metric-card"><strong class="mr02-warn">OCC, Repeatable Read 고정</strong><div class="mr02-muted">잠금 대신 커밋 시 충돌 검사. 충돌한 트랜잭션은 앱이 재시도</div></div>
    <div class="metric-card"><strong class="mr02-bad">트랜잭션 한도</strong><div class="mr02-muted">3,000 rows, 10 MiB, DDL 1개, 연결 1시간, SAVEPOINT 미지원</div></div>
    <div class="metric-card"><strong class="mr02-info">private 연결</strong><div class="mr02-muted">AWS PrivateLink interface endpoint와 IAM 인증 토큰으로 접속</div></div>
  </div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
• Aurora DSQL multi-Region: 두 peered cluster 모두 읽기, 쓰기, 커밋 시 동기 복제, witness 리전 1개
• RPO 0, 수동 failover 없음, multi-Region 가용성 설계 목표 99.999% (2025-05 GA)
• 같은 Region set 안에서만 구성, 북미는 us-east-1, us-east-2, us-west-2 등
• OCC와 Repeatable Read 고정, 트랜잭션당 3,000 rows, 10 MiB 한도, PrivateLink 접속
Aurora DSQL은 2025년 5월 GA 된 서버리스 분산 SQL입니다. multi-Region 클러스터는 두 리전의 peered cluster가 모두 읽기와 쓰기를 받고, 커밋할 때 동기로 복제합니다. 우리 시나리오라면 us-east-1과 us-west-2를 peered cluster로, us-east-2를 witness로 둡니다. witness는 전체 사본은 없지만 쓰기 기록을 받아 내구성과 quorum을 제공합니다.
{cue: pause}
얻는 것은 RPO 0과 수동 failover가 없다는 점입니다. 잃는 것도 분명합니다. 잠금 대신 optimistic concurrency control이라 충돌하면 커밋이 실패하고 앱이 재시도해야 합니다. 트랜잭션당 3,000 rows, 10 MiB 한도가 있고, SAVEPOINT 같은 PostgreSQL 기능 일부가 없습니다. 그래서 기존 Aurora 앱을 그대로 옮기는 것이 아니라, 재시도 가능한 짧은 트랜잭션으로 설계한 서비스에 맞습니다.
접속은 PrivateLink interface endpoint와 IAM 인증 토큰으로 private하게 구성합니다.
{cue: question}
결제 원장처럼 리전 장애 때도 데이터 손실이 절대 안 되는 테이블이 있다면, Global Database의 RPO 상한과 DSQL의 RPO 0 중 무엇이 맞을까요?
{cue: transition}
다음은 단일 writer 모델의 문서 저장소, DocumentDB입니다.
[근거]
• GA, 99.999%: https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-aurora-dsql-generally-available/
• Region set: https://docs.aws.amazon.com/aurora-dsql/latest/userguide/what-is-aurora-dsql.html
• 트랜잭션 제약: https://docs.aws.amazon.com/aurora-dsql/latest/userguide/working-with-postgresql-compatibility-migration-guide.html , https://docs.aws.amazon.com/aurora-dsql/latest/userguide/CHAP_quotas.html
• PrivateLink: https://docs.aws.amazon.com/aurora-dsql/latest/userguide/privatelink-managing-clusters.html
:::

---
<!-- Slide 8: DocumentDB Global Cluster -->
@type: content
@title: DocumentDB: 카탈로그는 읽기 로컬로

## DocumentDB: 카탈로그는 읽기 로컬로

:::html
<div class="mr02-split">
  <div>
    <div class="flow-h">
      <div class="flow-group"><div class="flow-group-label">us-east-1 (primary)</div><div class="flow-box">writer + replica</div><div class="flow-box">catalog, review 쓰기</div></div>
      <div class="flow-arrow">→ 스토리지 기반<br>물리 복제 →</div>
      <div class="flow-group"><div class="flow-group-label">us-west-2 (secondary)</div><div class="flow-box">replica 최대 16대</div><div class="flow-box">상품 조회 로컬 처리</div></div>
    </div>
    <div class="callout callout-info mr02-take"><strong class="mr02-info">예전 자료 정정</strong><div class="mr02-muted">"oplog 기반, 2초 이내"가 아니라 전용 인프라의 스토리지 기반 물리 복제이며 일반적인 lag은 1초 미만입니다. 관측: <code>GlobalClusterReplicationLag</code> (secondary)</div></div>
  </div>
  <div class="mr02-g2 fragment" data-reveal="stagger" data-fragment-index="1">
    <div class="metric-card"><strong class="mr02-acc">secondary 최대 10개</strong><div class="mr02-muted">쓰기는 primary cluster endpoint로만</div></div>
    <div class="metric-card"><strong class="mr02-ok">switchover (RPO 0)</strong><div class="mr02-muted">모든 리전이 같은 engine version일 때만</div></div>
    <div class="metric-card"><strong class="mr02-warn">failover</strong><div class="mr02-muted"><code>AllowDataLoss</code>, 미복제분은 스냅샷으로 보존 시도</div></div>
    <div class="metric-card"><strong class="mr02-bad">제약</strong><div class="mr02-muted">v3.6과 db.t3, db.t4g, db.r4 인스턴스는 global cluster 미지원</div></div>
  </div>
</div>
:::

:::notes
{timing: 1.5min}
[요약]
• DocumentDB Global Cluster: 스토리지 기반 물리 복제, 일반적 lag 1초 미만 (oplog 아님)
• secondary 최대 10개 리전, 리전당 replica 최대 16대, 쓰기는 primary cluster endpoint만
• switchover(RPO 0)와 failover(AllowDataLoss) 모두 지원, engine version 일치 필요
• v3.6, t3, t4g, r4 미지원, GlobalClusterReplicationLag 관측
DocumentDB는 카탈로그, 프로필, 리뷰를 담습니다. 상품 조회는 읽기가 압도적이라 us-west-2에서 로컬로 처리하기 좋습니다.
예전 자료를 정정하겠습니다. DocumentDB Global Cluster는 oplog 복제가 아니라 Aurora처럼 스토리지 기반 물리 복제이고, 일반적인 lag은 1초 미만입니다. secondary는 최대 10개 리전입니다.
{cue: pause}
전환은 Aurora와 같은 구조입니다. 계획된 전환은 switchover로 데이터 손실 없이, 리전 장애는 AllowDataLoss를 준 failover로 합니다. 둘 다 모든 리전의 engine version이 같아야 하니 업그레이드 순서를 관리하세요.
write forwarding은 Aurora처럼 제공되는 기능으로 확인되지 않았으므로, us-west-2의 리뷰 작성은 앱이 primary endpoint로 보내도록 설계합니다.
{cue: transition}
다음은 캐시 계층, Valkey Global Datastore입니다.
[근거]
• 제약, 한도: https://docs.aws.amazon.com/documentdb/latest/devguide/global-clusters.html
• 복제 방식, replica 16대: https://aws.amazon.com/documentdb/features/
• switchover, failover: https://docs.aws.amazon.com/documentdb/latest/devguide/global-clusters-disaster-recovery.html , https://docs.aws.amazon.com/documentdb/latest/APIReference/API_FailoverGlobalCluster.html
:::

---
<!-- Slide 9: ElastiCache for Valkey Global Datastore -->
@type: content
@title: Valkey 캐시: 읽기만 로컬

## Valkey 캐시: 읽기만 로컬

:::html
<div class="flow-h">
  <div class="flow-group"><div class="flow-group-label">us-east-1: primary (active)</div><div class="flow-box">읽기, 쓰기</div><div class="flow-box">cart, session 쓰기 지점</div></div>
  <div class="flow-arrow">→ 비동기 복제, 보통 1초 미만<br>(전송 구간 암호화) →</div>
  <div class="flow-group"><div class="flow-group-label">us-west-2: secondary (passive)</div><div class="flow-box">읽기 전용</div><div class="flow-box">장애 시 수동 promote</div></div>
</div>
<div class="card-grid mr02-take" data-reveal="stagger">
  <div class="metric-card"><strong class="mr02-acc">secondary 최대 2개</strong><div class="mr02-muted">primary 1 + 다른 리전 secondary 2. Valkey 7.2 이상 (최신 9.0, 2026-05)</div></div>
  <div class="metric-card"><strong class="mr02-warn">자동 failover 없음</strong><div class="mr02-muted">secondary promote는 직접 실행, 보통 1분 미만. 미복제 쓰기는 손실 가능</div></div>
  <div class="metric-card"><strong class="mr02-info">동일 구성 강제</strong><div class="mr02-muted">node type, engine version, shard 수가 같아야 함. replica 수만 리전별로 다르게</div></div>
  <div class="metric-card"><strong class="mr02-ok">지원 노드</strong><div class="mr02-muted">large 이상 M5, M6g, M7g, M8g, R5, R6g, R6gd, R7g, R8g, C7gn, C8gn</div></div>
</div>
<div class="callout callout-warning mr02-take fragment zoom-in" data-fragment-index="1"><strong class="mr02-warn">장바구니 설계 포인트</strong><div class="mr02-muted">us-west-2 사용자의 장바구니 쓰기는 us-east-1 primary까지 갑니다. 캐시는 원본이 아니라 사본으로 두고, 잃어도 재구성 가능한 데이터만 둡니다.</div></div>
:::

:::notes
{timing: 1.5min}
[요약]
• primary(active) 1개와 다른 리전 secondary(passive) 최대 2개, 비동기 복제 보통 1초 미만
• Valkey 7.2 이상 지원, ElastiCache 최신은 Valkey 9.0 (2026-05)
• 자동 failover 없음, secondary promote는 수동이며 보통 1분 미만
• 모든 클러스터의 node type, engine version, shard 수가 같아야 함
Valkey Global Datastore는 단일 writer 모델의 캐시 버전입니다. us-east-1 primary가 쓰기를 받고, us-west-2 secondary는 읽기만 받습니다. secondary는 최대 두 개 리전까지 둘 수 있습니다.
예전 자료의 Valkey 7.2는 지원 하한이고, 지금 ElastiCache에는 2026년 5월에 Valkey 9.0이 나왔습니다. 노드도 r6g 고정이 아니라 R7g, R8g, M8g 같은 최신 Graviton 계열이 지원됩니다.
{cue: pause}
중요한 점은 자동 failover가 없다는 것입니다. 리전 장애 시 운영자가 secondary를 promote해야 하고, 보통 1분 안에 끝납니다. Block 4의 failover 자동화에서 이 단계를 runbook에 넣겠습니다.
장바구니 쓰기가 us-east-1까지 가야 한다는 점도 설계에 반영해야 합니다. 그래서 캐시에는 잃어도 재구성 가능한 데이터만 둡니다.
{cue: transition}
그럼 캐시에 무엇을, 얼마 동안 두는지 패턴과 TTL을 보겠습니다.
[근거]
• 구성 요건, 노드 계열: https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Redis-Global-Datastores-Getting-Started.html
• secondary 2개, Valkey 7.2 이상: https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Redis-Global-Datastores-Console.html
• 수동 promote 1분 미만: https://aws.amazon.com/elasticache/faqs/
• Valkey 9.0: https://aws.amazon.com/about-aws/whats-new/2026/05/valkey-amazon-elasticache/
:::

---
<!-- Slide 10: Cache patterns & TTL -->
@type: content
@title: 캐시 일관성은 TTL로 관리한다

## 캐시 일관성은 TTL로 관리한다

:::html
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">패턴 4가지</button>
  <button class="tab-btn">키와 TTL 예시</button>
  <button class="tab-btn">멀티리전 주의점</button>
</div>
<div class="tc">
  <div class="card-grid" data-reveal="static">
    <div class="metric-card"><strong class="mr02-acc">Cache-aside</strong><div class="mr02-muted">miss 때 DB 조회 후 SET. 읽기 많고 쓰기 적은 상품 정보</div></div>
    <div class="metric-card"><strong class="mr02-info">Write-through</strong><div class="mr02-muted">쓰기 시 DB와 캐시를 함께 갱신. 세션, 장바구니</div></div>
    <div class="metric-card"><strong class="mr02-ok">Event-driven invalidation</strong><div class="mr02-muted">MSK 이벤트(product.updated)로 키 삭제. 비동기 일관성 허용</div></div>
    <div class="metric-card"><strong class="mr02-warn">TTL 만료</strong><div class="mr02-muted">자연 만료 후 재적재. 모든 키의 최종 안전장치</div></div>
  </div>
</div>
<div class="tc" hidden>
  <table class="data-table mr02-table">
    <thead><tr><th>키 패턴</th><th>자료형</th><th>TTL (설계 예시)</th><th>패턴</th></tr></thead>
    <tbody>
      <tr><td><code>product:{id}</code></td><td>Hash</td><td>1h</td><td>cache-aside + 이벤트 무효화</td></tr>
      <tr><td><code>cart:{userId}</code></td><td>Hash</td><td>7d (item별 field TTL 가능)</td><td>write-through</td></tr>
      <tr><td><code>session:{id}</code></td><td>Hash</td><td>2h</td><td>write-through</td></tr>
      <tr><td><code>ratelimit:{userId}</code></td><td>String counter</td><td>60s</td><td>INCR + EXPIRE</td></tr>
      <tr><td><code>stock:{productId}</code></td><td>String</td><td>30s</td><td>표시용 사본, 원본은 Aurora</td></tr>
    </tbody>
  </table>
  <div class="mr02-cap">Valkey 9.0의 hash field expiration으로 장바구니 item마다 만료를 따로 둘 수 있습니다. TTL 값은 서비스 요구에 맞춘 예시입니다.</div>
</div>
<div class="tc" hidden>
  <div class="card-grid">
    <div class="callout callout-warning"><strong class="mr02-warn">stale 창 = 복제 lag</strong><div class="mr02-muted">primary에서 무효화해도 secondary는 lag만큼 옛 값을 보여 줄 수 있음. <code>ReplicationLag</code> 관측</div></div>
    <div class="callout callout-danger"><strong class="mr02-bad">재고 원본을 캐시에 두지 않기</strong><div class="mr02-muted">DECR 카운터를 원본으로 쓰면 promote 시 미복제 차감이 사라져 초과 판매 위험</div></div>
    <div class="callout callout-info"><strong class="mr02-info">무효화는 primary로</strong><div class="mr02-muted">secondary는 읽기 전용이므로 us-west-2의 무효화, 쓰기 요청도 primary endpoint로</div></div>
    <div class="callout callout-success"><strong class="mr02-ok">promote 후 warm-up</strong><div class="mr02-muted">손실된 키는 cache-aside가 다시 채움. DB 부하 급증에 대비해 요청 제한 준비</div></div>
  </div>
</div>
:::

:::notes
{timing: 1.5min}
[요약]
• 패턴 4가지: cache-aside, write-through, 이벤트 기반 무효화, TTL 만료
• TTL은 모든 키의 최종 안전장치, 값은 서비스 요구에 맞춘 설계 예시
• secondary의 stale 창은 복제 lag과 같음, 무효화와 쓰기는 primary로
• 재고 원본은 Aurora, 캐시는 표시용 사본, Valkey 9.0 hash field expiration 활용 가능
캐시 전략은 세 탭입니다. 첫 번째, 패턴 네 가지입니다. 상품 정보는 cache-aside, 세션과 장바구니는 write-through, 상품이 바뀌면 MSK 이벤트로 키를 지우고, 모든 키에 TTL을 둡니다.
두 번째 탭은 키 설계 예시입니다. 예전 자료와 달라진 부분은 재고입니다. 예전에는 stock 카운터를 TTL 없이 캐시에 두고 DECR로 차감했는데, 멀티리전에서는 위험합니다.
{cue: pause}
세 번째 탭에서 이유를 봅니다. Global Datastore는 비동기라 promote하는 순간 미복제 차감이 사라질 수 있고, 그러면 초과 판매가 납니다. 재고의 원본은 Aurora에 두고 캐시는 짧은 TTL의 표시용 사본으로 씁니다. 그리고 secondary는 읽기 전용이니 무효화 요청도 primary로 보내야 합니다.
{cue: transition}
캐시 무효화에 쓴 이벤트, 그 이벤트 자체는 어떻게 리전 간에 옮길까요? MSK Replicator입니다.
[근거]
• 캐시 키, TTL은 발표자 설계 예시. hash field expiration: https://aws.amazon.com/about-aws/whats-new/2026/05/valkey-amazon-elasticache/
• ReplicationLag 메트릭: https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/CacheMetrics.WhichShouldIMonitor.html
:::

---
<!-- Slide 11: MSK + MSK Replicator -->
@type: content
@title: MSK Replicator: offset도 복제

## MSK Replicator: offset도 복제

:::html
<div class="flow-h">
  <div class="flow-group"><div class="flow-group-label">us-east-1 MSK (source)</div><div class="flow-box">order.created, payment.completed</div><div class="flow-box">IAM 인증 9098, multi-VPC private connectivity</div></div>
  <div class="flow-arrow">→ 비동기 →</div>
  <div class="flow-group"><div class="flow-group-label">MSK Replicator (us-west-2에 생성)</div><div class="flow-box">topic, config, ACL, consumer offset 복제</div></div>
  <div class="flow-arrow">→</div>
  <div class="flow-group"><div class="flow-group-label">us-west-2 MSK (target)</div><div class="flow-box">standby consumer</div><div class="flow-box">장애 시 producer 전환</div></div>
</div>
<div class="card-grid mr02-take fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="metric-card"><strong class="mr02-acc">topic 이름</strong><div class="mr02-muted"><code>PREFIXED</code>(기본) 또는 identical. identical이면 전환 시 앱 설정 변경 불필요</div></div>
  <div class="metric-card"><strong class="mr02-info">offset 동기화</strong><div class="mr02-muted"><code>LEGACY</code>(기본, 단방향), <code>ENHANCED</code>(양방향 Replicator 필요)</div></div>
  <div class="metric-card"><strong class="mr02-warn">시작 위치, 한도</strong><div class="mr02-muted">기본 latest, 생성 후 변경 불가. Replicator당 750 topic</div></div>
  <div class="metric-card"><strong class="mr02-bad">중복은 필연</strong><div class="mr02-muted">비동기라 전환 시 재처리 발생. consumer를 idempotent하게</div></div>
  <div class="metric-card"><strong class="mr02-ok">관측</strong><div class="mr02-muted"><code>ReplicationLatency</code>(ms), <code>MessageLag</code>, target 리전 AWS/Kafka</div></div>
  <div class="metric-card"><strong class="mr02-acc">Kafka 4.x는 KRaft 전용</strong><div class="mr02-muted">3.9가 ZooKeeper 마지막. Standard 4.1, Express 4.2 지원</div></div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
• MSK Replicator는 target 리전에 만들고, topic 데이터와 config, ACL, consumer offset을 비동기 복제
• cross-Region은 source에 IAM 인증(9098)과 multi-VPC private connectivity 필요, 공용 경로 없음
• topic 이름 PREFIXED(기본) 또는 identical, offset 동기화 LEGACY 또는 ENHANCED
• 비동기라 중복 재처리는 필연, consumer idempotency 필수
• 예전 Kafka 3.6 예시 대신 Kafka 4.x(KRaft 전용) 기준
MSK는 이벤트 백본입니다. 주문이 생성되면 order.created가 발행되고, 결제와 재고 서비스가 이를 구독합니다. 이 이벤트를 us-west-2로 옮기는 것이 MSK Replicator입니다.
Replicator는 target 리전인 us-west-2에 만들고, source 클러스터에는 IAM 인증과 multi-VPC private connectivity를 켭니다. 모든 구간이 AWS 내부 private 경로입니다.
{cue: pause}
카드를 보겠습니다. topic 이름은 기본이 prefix를 붙이는 방식이고, identical을 고르면 failover 때 consumer 설정을 바꿀 필요가 없습니다. consumer offset도 복제되므로 standby consumer가 대략 이어서 읽을 수 있습니다. 시작 위치는 기본 latest이고 생성 후 바꿀 수 없으니 기존 데이터가 필요하면 earliest로 만드세요.
복제가 비동기라서 전환 시 일부 메시지는 다시 처리됩니다. 그래서 consumer는 반드시 idempotent해야 합니다. 이 부분이 다음 DynamoDB 슬라이드와 연결됩니다.
버전도 갱신합니다. 예전 자료의 Kafka 3.6 대신, 지금은 Kafka 4.x가 KRaft 전용이고 3.9가 ZooKeeper를 지원하는 마지막 버전입니다.
{cue: transition}
idempotency key를 어디에 저장할지, DynamoDB Global Tables로 넘어가겠습니다.
[근거]
• 설정 항목, 750 topic: https://docs.aws.amazon.com/msk/latest/developerguide/msk-replicator-create-console.html
• 네트워크, 인증: https://docs.aws.amazon.com/msk/latest/developerguide/msk-replicator-network-reqs.html , https://docs.aws.amazon.com/msk/latest/developerguide/msk-replicator-supported-configs.html
• 메트릭: https://docs.aws.amazon.com/msk/latest/developerguide/msk-replicator-metrics-ref.html
• Kafka 4.1, 4.2 Express, KRaft 이전: https://aws.amazon.com/about-aws/whats-new/2025/10/amazon-msk-apache-kafka-version-4-1/ , https://aws.amazon.com/about-aws/whats-new/2026/07/aws-msk-express-version-42/ , https://aws.amazon.com/about-aws/whats-new/2026/08/aws-msk-zk-kraft-migration/
• 중복 처리: https://aws.amazon.com/blogs/big-data/build-multi-region-resilient-apache-kafka-applications-with-identical-topic-names-using-amazon-msk-and-amazon-msk-replicator/
:::

---
<!-- Slide 12: DynamoDB Global Tables MREC vs MRSC -->
@type: content
@title: DynamoDB: MREC와 MRSC 중 고른다

## DynamoDB: MREC와 MRSC 중 고른다

:::html
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">MREC (기본)</button>
  <button class="tab-btn">MRSC (강한 일관성)</button>
  <button class="tab-btn">결제 idempotency 예시</button>
</div>
<div class="tc">
  <div class="card-grid mr02-g2" data-reveal="static">
    <div class="metric-card"><strong class="mr02-acc">active-active 비동기</strong><div class="mr02-muted">모든 replica가 로컬 쓰기, 보통 1초 안에 전파 (SLA 없음)</div></div>
    <div class="metric-card"><strong class="mr02-warn">last writer wins</strong><div class="mr02-muted">같은 item을 거의 동시에 쓰면 item 단위로 마지막 쓰기가 이김. 충돌은 기록되지 않음</div></div>
    <div class="metric-card"><strong class="mr02-info">리전 수 제한 없음</strong><div class="mr02-muted">파티션 내 모든 리전에 replica 가능. 트랜잭션은 리전 간 묶여서 복제되지 않음</div></div>
    <div class="metric-card"><strong class="mr02-ok">관측</strong><div class="mr02-muted">리전 쌍별 <code>ReplicationLatency</code> 평균, 최대로 최악의 lag 확인</div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="card-grid mr02-g2">
    <div class="metric-card"><strong class="mr02-acc">정확히 3개 리전</strong><div class="mr02-muted">replica 3개, 또는 replica 2개 + witness 1개. 빈 테이블에서 생성</div></div>
    <div class="metric-card"><strong class="mr02-ok">동기 쓰기, RPO 0</strong><div class="mr02-muted">최소 1개 다른 리전에 기록 후 응답. strongly consistent read는 항상 최신</div></div>
    <div class="metric-card"><strong class="mr02-warn">충돌은 예외로</strong><div class="mr02-muted">다른 리전에서 수정 중이면 <code>ReplicatedWriteConflictException</code>, 재시도</div></div>
    <div class="metric-card"><strong class="mr02-bad">제약</strong><div class="mr02-muted">transaction API 미지원. 쓰기와 strong read 지연은 리전 간 RTT만큼 증가</div></div>
  </div>
  <div class="mr02-cap">지원 리전 예: us-east-1, us-east-2, us-west-2를 포함한 15개 리전, 대륙 간 조합도 가능 (문서 기준).</div>
</div>
<div class="tc" hidden>
  <div class="mr02-split">
    <pre class="mr02-code"># MRSC: us-east-1, us-west-2 replica
#       + us-east-2 witness
aws dynamodb put-item --region us-west-2 \
  --table-name payment-idempotency \
  --item '{"pk":{"S":"pay#ord-1001"}}' \
  --condition-expression \
    "attribute_not_exists(pk)"</pre>
    <div class="mr02-stack">
      <div class="callout callout-success"><strong class="mr02-ok">조건부 쓰기가 최신 버전 기준</strong><div class="mr02-muted">us-east-1에서 이미 기록했다면 us-west-2의 같은 key 쓰기는 조건 실패, 이중 결제 차단</div></div>
      <div class="callout callout-warning"><strong class="mr02-warn">MREC라면</strong><div class="mr02-muted">조건은 로컬 replica 기준으로만 평가되어 lag 사이에 양쪽 모두 성공 가능</div></div>
    </div>
  </div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
• MREC(기본): active-active 비동기, 보통 1초 안 전파(SLA 없음), item 단위 last writer wins
• MRSC: 정확히 3개 리전(replica 3 또는 replica 2 + witness), 동기 쓰기, RPO 0
• MRSC 충돌은 ReplicatedWriteConflictException으로 재시도, transaction API 미지원
• 결제 idempotency key는 MRSC의 조건부 쓰기로 리전 간 이중 결제 차단
DynamoDB Global Tables는 일관성 모드가 두 가지입니다. 첫 탭, 기본인 MREC는 모든 리전이 로컬로 쓰고 비동기로 전파합니다. 보통 1초 안에 전파되지만 SLA는 없습니다. 같은 item을 거의 동시에 두 리전에서 쓰면 마지막 쓰기가 이기고, 이 충돌은 어디에도 기록되지 않습니다.
{cue: pause}
두 번째 탭, MRSC는 2025년에 GA 된 multi-Region strong consistency입니다. 정확히 세 리전이 필요하고, 우리 구성이라면 us-east-1과 us-west-2에 replica, us-east-2에 witness를 둡니다. 쓰기는 다른 리전 한 곳 이상에 기록된 후 응답하므로 RPO가 0입니다. 대신 transaction API를 쓸 수 없고, 쓰기 지연이 리전 간 왕복만큼 늘어납니다.
세 번째 탭이 실제 활용입니다. 결제 서비스가 같은 주문을 두 리전에서 재시도하는 상황을 생각해 보세요. MRSC에서는 조건부 쓰기가 항상 최신 버전을 기준으로 평가되므로 두 번째 쓰기는 실패합니다. MREC라면 lag 사이에 양쪽 모두 성공할 수 있습니다.
{cue: question}
앞에서 본 MSK의 중복 재처리, 이 테이블로 막을 수 있겠죠?
{cue: transition}
이제 모든 저장소를 한 표에 모아 장애 시 무엇을 잃는지 정리합니다.
[근거]
• https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/V2globaltables_HowItWorks.html (MREC, MRSC, 지원 리전)
• https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-global-table-design.html (LWW, ReplicationLatency, ReplicatedWriteConflictException, transaction API)
:::

---
<!-- Slide 13: RPO / replication lag matrix -->
@type: content
@title: 장애 때 무엇을 잃는가: RPO 표

## 장애 때 무엇을 잃는가: RPO 표

:::html
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">데이터베이스</button>
  <button class="tab-btn">캐시, 이벤트, 객체</button>
</div>
<div class="tc">
  <table class="data-table mr02-table" data-reveal="static">
    <thead><tr><th>저장소</th><th>복제 모델</th><th>평시 lag</th><th>계획 전환</th><th>비계획 장애 시 손실</th><th>볼 메트릭</th></tr></thead>
    <tbody>
      <tr><td>Aurora PostgreSQL Global DB</td><td>단일 writer, 비동기</td><td>보통 1초 미만</td><td>switchover RPO 0</td><td>lag만큼 (<code>rds.global_db_rpo</code>로 상한)</td><td><code>AuroraGlobalDBRPOLag</code></td></tr>
      <tr><td>Aurora DSQL multi-Region</td><td>동기, active-active</td><td>커밋에 포함</td><td>불필요</td><td>0</td><td>OCC 재시도율</td></tr>
      <tr><td>DocumentDB Global</td><td>단일 writer, 비동기</td><td>보통 1초 미만</td><td>switchover RPO 0</td><td>lag만큼</td><td><code>GlobalClusterReplicationLag</code></td></tr>
      <tr><td>DynamoDB MREC</td><td>multi-writer, 비동기</td><td>보통 1초 이내, SLA 없음</td><td>불필요</td><td>미전파 쓰기는 해당 리전 복구 전까지 없음</td><td><code>ReplicationLatency</code></td></tr>
      <tr><td>DynamoDB MRSC</td><td>동기, 3개 리전</td><td>쓰기에 포함</td><td>불필요</td><td>0</td><td>충돌 예외 수</td></tr>
    </tbody>
  </table>
</div>
<div class="tc" hidden>
  <table class="data-table mr02-table">
    <thead><tr><th>저장소</th><th>복제 모델</th><th>평시 lag</th><th>계획 전환</th><th>비계획 장애 시 손실</th><th>볼 메트릭</th></tr></thead>
    <tbody>
      <tr><td>Valkey Global Datastore</td><td>단일 writer, 비동기</td><td>보통 1초 미만</td><td>수동 promote</td><td>lag만큼 (캐시는 재구성)</td><td><code>ReplicationLag</code></td></tr>
      <tr><td>OpenSearch CCR</td><td>leader → follower, 비동기 pull</td><td>측정 필요</td><td>follower 승격(replication 중지)</td><td>미복제 문서, 원천 DB에서 재색인</td><td>replication 상태 API</td></tr>
      <tr><td>MSK Replicator</td><td>비동기</td><td>측정 필요</td><td>producer 전환</td><td>in-flight 유실, 재처리 중복</td><td><code>ReplicationLatency</code>, <code>MessageLag</code></td></tr>
      <tr><td>S3 CRR + RTC</td><td>비동기</td><td>대부분 수초</td><td>해당 없음</td><td>99.99% 객체 15분 내 (SLA 99.9%)</td><td>RTC 복제 메트릭</td></tr>
    </tbody>
  </table>
</div>
<div class="callout callout-info mr02-take fragment zoom-in" data-fragment-index="1"><strong class="mr02-info">공통 방어선</strong><div class="mr02-muted">손실 0이 아닌 행이 대부분입니다. 모든 쓰기 API를 idempotent하게 만들고, 표의 메트릭에 RPO 기준 알람을 겁니다.</div></div>
:::

:::notes
{timing: 2min}
[요약]
• 단일 writer 비동기 저장소는 계획 전환 RPO 0, 비계획 장애는 lag만큼 손실
• 동기 모델(DSQL, DynamoDB MRSC)만 비계획 장애에서도 RPO 0
• MSK는 유실과 중복이 모두 가능, S3 RTC는 99.99% 객체 15분 내 복제
• 공통 방어선: idempotent API와 lag 메트릭 알람
이 표가 이 블록의 요약입니다. 데이터베이스 탭과 캐시, 이벤트, 객체 탭으로 나눴고, 행마다 계획 전환과 비계획 장애를 나눠서 보세요.
Aurora, DocumentDB, Valkey는 모두 단일 writer 비동기라서 계획된 switchover는 데이터 손실이 없지만, 리전 장애에서는 그 순간의 lag만큼 잃습니다. Aurora PostgreSQL은 rds.global_db_rpo로 그 상한을 걸 수 있습니다.
{cue: pause}
비계획 장애에서도 0인 것은 동기 모델인 DSQL과 DynamoDB MRSC뿐입니다. 두 번째 탭으로 넘기면, MSK는 in-flight 이벤트를 잃을 수도, 다시 처리할 수도 있습니다. OpenSearch는 cross-cluster replication으로 leader 인덱스를 다른 리전의 read-only follower 인덱스가 끌어오는 구조라, 장애 시 follower의 replication을 멈추고 쓰기 대상으로 바꿉니다. 검색 인덱스는 원천 DB에서 다시 만들 수 있으므로 미복제분은 재색인으로 메웁니다. S3는 Replication Time Control을 켜면 99.99%의 객체를 15분 안에 복제하도록 설계되어 있고, SLA는 99.9%입니다.
예전 자료의 RPO 열에 있던 "약 1초", "약 2초" 같은 고정 값은 쓰지 않았습니다. 실제 값은 장애 순간의 lag이고, 그래서 마지막 열의 메트릭을 봐야 합니다.
{cue: transition}
배운 내용을 세 문제로 확인해 보겠습니다.
[근거]
• Aurora: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-disaster-recovery.html
• DocumentDB: https://docs.aws.amazon.com/documentdb/latest/devguide/global-clusters-disaster-recovery.html
• DynamoDB: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-global-table-design.html
• OpenSearch CCR: https://docs.aws.amazon.com/wellarchitected/latest/amazon-opensearch-service-lens/aosrel04-bp04.html
• S3 RTC: https://aws.amazon.com/s3/faqs/
:::

---
<!-- Slide 14: Knowledge Check (1/2) -->
@type: quiz

## Knowledge Check (1/2)

**Q1: Aurora write forwarding에서 기본값이며, 내 세션이 방금 쓴 값을 바로 읽게 해 주는 consistency_mode는?**
- [ ] EVENTUAL
- [x] SESSION
- [ ] OFF

**Q2: 리전 장애로 failover-global-cluster --allow-data-loss를 실행했다. 맞는 설명은?**
- [ ] secondary가 따라잡을 때까지 기다리므로 RPO는 0이다
- [x] 미복제 트랜잭션은 유실될 수 있고, old primary 스냅샷으로 복구를 시도한다
- [ ] Aurora가 리전 장애를 감지하면 자동으로 실행된다

:::notes
{timing: 1min}
[요약]
• Q1: SESSION이 기본값, 내 세션의 쓰기를 복제 대기 후 바로 보여 줌
• Q2: failover는 동기화를 기다리지 않음, 미복제분은 스냅샷에서 복구 시도, 자동 실행 아님
세 문제를 두 장에 나눴습니다. 1번, 기본값 SESSION입니다. EVENTUAL은 내가 쓴 값도 복제될 때까지 안 보이고, OFF는 해당 세션의 write forwarding을 끕니다.
2번, failover는 동기화를 기다리지 않으므로 RPO가 0이 아닙니다. Aurora는 old primary의 스냅샷을 시도해 미복제 데이터를 건질 기회를 줍니다. 그리고 Global Database의 리전 간 failover는 운영자가 실행합니다.
{cue: question}
2번이 헷갈리셨다면 Block 4의 failover runbook에서 다시 다룹니다.
{cue: transition}
마지막 문제는 결제 중복입니다.
:::

---
<!-- Slide 15: Knowledge Check (2/2) -->
@type: quiz

## Knowledge Check (2/2)

**Q3: 두 리전에서 같은 결제 요청이 재시도될 때 이중 결제를 막는 저장 방식은?**
- [ ] DynamoDB MREC 테이블의 조건부 쓰기
- [x] DynamoDB MRSC 테이블의 조건부 쓰기
- [ ] Valkey Global Datastore secondary에 SETNX

:::notes
{timing: 0.5min}
[요약]
• Q3: MRSC는 조건부 쓰기가 항상 최신 버전 기준
• MREC는 로컬 replica 기준이라 lag 사이에 양쪽 모두 성공 가능
• Valkey secondary는 쓰기를 받지 않음
3번, 정답은 MRSC입니다. MREC의 조건은 로컬 replica만 보고 평가되므로 복제 lag 사이에 두 리전 모두 성공할 수 있고, Valkey secondary는 애초에 쓰기를 받지 않습니다.
{cue: transition}
마지막으로 핵심을 정리하겠습니다.
:::

---
<!-- Slide 16: Key Takeaways -->
@type: content
@title: Key Takeaways

## Key Takeaways

:::html
<div class="card-grid" data-reveal="stagger">
  <div class="metric-card"><strong class="mr02-acc">① 쓰기 위치부터 정한다</strong><div class="mr02-muted">서비스별 쓰기 리전과 허용 RPO를 정의한 뒤 저장소와 복제 모델을 고릅니다</div></div>
  <div class="metric-card"><strong class="mr02-info">② 계획 전환과 장애 전환은 다르다</strong><div class="mr02-muted">switchover는 RPO 0, failover는 lag만큼 손실. global writer endpoint로 연결을 고정</div></div>
  <div class="metric-card"><strong class="mr02-ok">③ RPO 0은 동기 모델에서만</strong><div class="mr02-muted">Aurora DSQL, DynamoDB MRSC. 대신 쓰기 지연, OCC 재시도, 트랜잭션 제약을 수용</div></div>
  <div class="metric-card"><strong class="mr02-warn">④ idempotency와 lag 알람</strong><div class="mr02-muted">MSK 재처리, 캐시 stale, 비동기 손실을 견디려면 idempotent API와 lag 메트릭 알람이 기본</div></div>
</div>
:::

:::notes
{timing: 1min}
[요약]
• 쓰기 위치와 허용 RPO가 먼저, 저장소 선택은 그다음
• switchover RPO 0, failover는 lag만큼 손실, global writer endpoint 사용
• RPO 0은 DSQL, DynamoDB MRSC 같은 동기 모델에서만, 대가는 지연과 제약
• idempotent API와 lag 메트릭 알람이 모든 저장소의 공통 방어선
네 가지만 기억해 주세요. 하나, 저장소를 고르기 전에 서비스별 쓰기 위치와 허용 RPO를 정합니다. 둘, switchover와 failover는 RPO가 다르고, 연결은 global writer endpoint로 고정합니다.
셋, 비계획 장애에서도 RPO 0이 필요하면 DSQL이나 DynamoDB MRSC 같은 동기 모델을 쓰되 쓰기 지연과 제약을 받아들여야 합니다. 넷, 어떤 저장소든 idempotent API와 lag 알람은 기본입니다.
{cue: transition}
Block 3에서는 이 데이터 계층 앞단, 트래픽을 어느 리전으로 보낼지 라우팅과 엣지를 다룹니다.
:::

---
<!-- Slide 17: Thank You -->
@type: thankyou
@toc: toc.html
@next: 03-traffic-routing.html
@next-label: 다음: Traffic Routing & Edge
@message: Block 2: Data Sync & Replication 완료

:::notes
{timing: 0.5min}
[요약]
• Block 2 핵심: 복제 모델 3가지, switchover와 failover의 RPO 차이, 동기 모델의 대가, idempotency
• Q&A 후 5분 휴식, 다음은 Block 3 Traffic Routing & Edge
Block 2를 마칩니다. 데이터 계층에서 정한 쓰기 위치와 RPO가 다음 블록의 라우팅 정책과 Block 4의 failover 자동화의 전제가 됩니다.
{cue: question}
질문 있으시면 지금 받겠습니다. 5분 쉬고 Block 3으로 이어가겠습니다.
:::
