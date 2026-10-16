---
remarp: true
block: 03-traffic-routing
---

---
<!-- Slide 1: 블록 커버 (Section) -->
@type: section

# Block 3: Traffic Routing & Edge

공개 입구는 CloudFront 하나, 리전 선택은 Edge에서, 절체 스위치는 데이터 플레인에

:::notes
{timing: 0.5min}
[요약]
• 이 블록의 질문: "사용자 요청이 어떤 경로로, 어느 리전의 어떤 서비스에 도달하는가"
• 순서: 전체 흐름 → 리전 선택(DNS vs Edge) → 헬스체크, ARC → CloudFront 구성 → Origin 잠금 → WAF, Bot Control → GA 비교 → 비용
• 쇼핑몰 시나리오 유지: order, payment, catalog, cart 서비스, us-east-1 primary + us-west-2 secondary
Block 3에서는 트래픽이 들어오는 길을 따라가 보겠습니다. 앞 블록에서 데이터를 두 리전에 어떻게 복제하는지 봤다면, 이번에는 사용자의 요청이 어느 리전으로 갈지 누가 결정하고, 장애 때 그 결정을 어떻게 바꾸는지가 주제입니다.
핵심 원칙 하나를 먼저 말씀드리면, 이 아키텍처의 공개 입구는 CloudFront 하나뿐입니다. 로드 밸런서는 모두 internal이고, CloudFront VPC origin으로만 들어옵니다.
{cue: transition}
먼저 요청 하나가 거치는 전체 경로부터 보겠습니다.
:::

---
<!-- Slide 2: End-to-End 흐름 -->
@type: content
@title: 공개 입구는 CloudFront 하나뿐

## 공개 입구는 CloudFront 하나뿐

:::html
<style>
.mr03-t-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.mr03-t-info    { color: var(--info);    font-weight: var(--weight-bold); }
.mr03-t-success { color: var(--success); font-weight: var(--weight-bold); }
.mr03-t-warning { color: var(--warning); font-weight: var(--weight-bold); }
.mr03-t-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.mr03-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-1); word-break: keep-all; overflow-wrap: break-word; }
.mr03-note { font-size: var(--fs-caption); color: var(--text-secondary); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: break-word; }
.mr03-take { margin-top: var(--space-3); }
.mr03-ico { width: 2.25rem; height: 2.25rem; vertical-align: middle; margin-right: var(--space-2); }
.mr03-flow { align-items: stretch; }
.mr03-flow .flow-group { flex: 1 1 0; min-width: 0; }
.mr03-flow .flow-box { font-size: var(--fs-caption); word-break: keep-all; overflow-wrap: anywhere; }
.mr03-flow .flow-box .mr03-ico { display: block; margin: 0 auto var(--space-1); }
.mr03-flow .flow-arrow { align-self: center; }
.mr03-code { font-variant-ligatures: none; font-family: var(--font-mono); font-size: var(--fs-caption); white-space: pre; background: var(--surface-2); border: 1px solid var(--surface-3); border-radius: var(--radius-md); padding: var(--space-3); overflow: hidden; line-height: 1.5; margin: 0; }
.mr03-split { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); align-items: start; }
.mr03-split.mr03-codesplit { grid-template-columns: 1.5fr 1fr; }
.mr03-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.mr03-grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3); }
.mr03-table { width: 100%; font-size: var(--fs-card); word-break: keep-all; overflow-wrap: break-word; }
.slide .mr03-table code, .slide .mr03-muted code, .slide .mr03-note code, .slide .mr03-t-accent code, .slide .mr03-t-info code, .slide .mr03-t-success code, .slide .mr03-t-warning code, .slide .mr03-t-danger code { font-family: var(--font-mono); white-space: normal; overflow-wrap: anywhere; word-break: break-all; }
.slide .mr03-table th { font-size: var(--fs-card); }
.mr03-calc { display: flex; flex-direction: column; gap: var(--space-3); }
.mr03-row { display: grid; grid-template-columns: 9rem 1fr; align-items: center; gap: var(--space-3); }
.mr03-row label { color: var(--text-secondary); font-size: var(--fs-card); }
.mr03-calc .slider-value { min-width: 6rem; }
.mr03-calc .metric-value { font-size: var(--fs-subtitle); white-space: nowrap; }
.mr03-btns { display: flex; gap: var(--space-2); flex-wrap: wrap; }
.mr03-btns .btn { color: var(--on-surface); font-size: var(--fs-card); }
.mr03-btns .btn.active { border-color: var(--accent); color: var(--accent); }
.mr03-out { font-family: var(--font-mono); font-size: var(--fs-card); background: var(--surface-2); border: 1px solid var(--surface-3); border-radius: var(--radius-md); padding: var(--space-3); line-height: 1.6; min-height: 7.5rem; white-space: pre-wrap; word-break: keep-all; }
.mr03-prio { display: flex; flex-direction: column; gap: var(--space-2); }
.mr03-prio-row { display: grid; grid-template-columns: 3rem 15rem 1fr; gap: var(--space-3); align-items: center; padding: var(--space-2) var(--space-3); background: var(--surface-1); border: 1px solid var(--surface-3); border-radius: var(--radius-md); }
.mr03-prio-num { font-family: var(--font-mono); color: var(--accent); font-weight: var(--weight-bold); font-size: var(--fs-card); }
.mr03-prio-name { font-weight: var(--weight-bold); font-size: var(--fs-card); }
.mr03-prio-row .mr03-muted { margin-top: 0; font-size: var(--fs-caption); }
</style>
<div class="flow-h mr03-flow">
  <div class="flow-group fragment fade-right" data-fragment-index="1">
    <div class="flow-group-label">사용자</div>
    <div class="flow-box">브라우저, 앱<br>mall.<wbr>example.com</div>
    <div class="flow-box"><img class="mr03-ico" src="./common/aws-icons/services/Arch_Amazon-Route-53_48.svg" alt="Amazon Route 53">Route 53<br>alias → CloudFront</div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-group fragment fade-right" data-fragment-index="2">
    <div class="flow-group-label">Edge: 유일한 공개 입구</div>
    <div class="flow-box"><img class="mr03-ico" src="./common/aws-icons/services/Arch_Amazon-CloudFront_48.svg" alt="Amazon CloudFront">CloudFront</div>
    <div class="flow-box"><img class="mr03-ico" src="./common/aws-icons/services/Arch_AWS-WAF_48.svg" alt="AWS WAF">WAF web ACL</div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-group fragment fade-right" data-fragment-index="3">
    <div class="flow-group-label">Behavior 분기</div>
    <div class="flow-box">/static/*<br>→ S3 (OAC)</div>
    <div class="flow-box">/api/*<br>→ CF Function<br>→ origin group</div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-group fragment fade-right" data-fragment-index="4">
    <div class="flow-group-label">VPC origin</div>
    <div class="flow-box"><img class="mr03-ico" src="./common/aws-icons/services/Arch_Elastic-Load-Balancing_48.svg" alt="Elastic Load Balancing">internal ALB<br>us-east-1 (primary)</div>
    <div class="flow-box">internal ALB<br>us-west-2 (secondary)</div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-group fragment fade-right" data-fragment-index="4">
    <div class="flow-group-label">EKS 서비스</div>
    <div class="flow-box"><img class="mr03-ico" src="./common/aws-icons/services/Arch_Amazon-Elastic-Kubernetes-Service_48.svg" alt="Amazon EKS">order, payment</div>
    <div class="flow-box">catalog, cart</div>
  </div>
</div>
<div class="callout callout-danger mr03-take fragment zoom-in" data-fragment-index="5"><strong class="mr03-t-danger">금지 목록</strong><div class="mr03-muted">internet-facing LB, compute의 public IP, 보안 그룹의 0.0.0.0/0 및 ::/0 ingress. 우회 경로가 하나라도 있으면 WAF와 Edge 정책이 무력화됩니다.</div></div>
:::

:::notes
{timing: 2.5min}
[요약]
• Route 53은 apex를 CloudFront로 alias, 리전 선택은 DNS가 아니라 CloudFront에서 함
• /static/*은 S3 + OAC, /api/*는 CloudFront Function이 고른 origin group으로
• origin은 두 리전의 internal ALB, CloudFront VPC origin으로만 연결
• internet-facing LB, public IP, 0.0.0.0/0 ingress는 설계에서 아예 존재하지 않음
왼쪽부터 클릭하며 보겠습니다. 사용자가 mall.example.com을 조회하면 Route 53이 alias 레코드로 CloudFront를 돌려줍니다. 서브도메인이라 CNAME도 동작하지만 alias A와 AAAA를 권장합니다. CloudFront를 가리키는 alias 질의는 요금이 없고, apex 도메인(example.com)은 애초에 CNAME을 쓸 수 없어서 alias만 가능합니다.
{cue: pause}
CloudFront에는 WAF web ACL이 붙습니다. CloudFront용 web ACL은 scope가 CLOUDFRONT이고 us-east-1에서 만듭니다. 그다음 behavior가 경로별로 나뉩니다. 정적 자산은 S3와 OAC, API는 viewer request 함수가 리전을 고른 뒤 origin group으로 보냅니다.
origin은 각 리전의 internal ALB이고 CloudFront VPC origin으로 연결됩니다. 예전 버전은 public NLB에 prefix list를 거는 구조였는데, 이번에는 로드 밸런서 자체를 인터넷에서 보이지 않게 바꿨습니다.
{cue: question}
여러분 환경에 CloudFront를 거치지 않고 들어올 수 있는 경로가 남아 있나요? 테스트용으로 잠깐 열어 둔 internet-facing ALB 하나가 WAF 전체를 우회하게 만듭니다.
{cue: transition}
그럼 "어느 리전으로 보낼지"는 누가 결정하는지 보겠습니다.
[출처]
• CloudFront VPC origins: docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-vpc-origins.html
:::

---
<!-- Slide 3: 리전 선택 DNS vs Edge -->
@type: content
@title: 리전 선택은 DNS가 아니라 Edge에서

## 리전 선택은 DNS가 아니라 Edge에서

:::html
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">Route 53 latency (DNS)</button>
  <button class="tab-btn">CloudFront Function + KVS (Edge)</button>
  <button class="tab-btn">Viewer request 코드</button>
</div>
<div class="tc">
  <div class="card-grid">
    <div class="metric-card"><strong class="mr03-t-accent">판단 근거</strong><div class="mr03-muted">recursive resolver IP, 또는 EDNS0 client subnet이 있으면 잘린 client IP. 회사 resolver가 다른 대륙이면 엉뚱한 리전이 나올 수 있음</div></div>
    <div class="metric-card"><strong class="mr03-t-accent">latency 데이터</strong><div class="mr03-muted">일정 기간 측정값 기반이라 바뀔 수 있음. 이번 주 Oregon이 다음 주 다른 리전이 될 수 있음 (실시간 측정 아님)</div></div>
    <div class="metric-card"><strong class="mr03-t-info">요금</strong><div class="mr03-muted">latency 질의 $0.60/M, 표준 질의 $0.40/M. CloudFront로 가는 alias 질의는 무료</div></div>
    <div class="metric-card"><strong class="mr03-t-warning">VPC origin과의 관계</strong><div class="mr03-muted">VPC origin은 ALB ARN에 묶임. DNS 응답을 바꿔도 다른 리전 ALB로 가지 않으므로 공개 경로의 리전 선택은 Edge에서 해야 함</div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="card-grid">
    <div class="metric-card"><strong class="mr03-t-success">viewer request 함수</strong><div class="mr03-muted">우선순위: session affinity cookie → weighted → geo (<code>CloudFront-Viewer-Country-Region</code>)</div></div>
    <div class="metric-card"><strong class="mr03-t-success"><code>cf.createRequestOriginGroup()</code></strong><div class="mr03-muted">선택한 리전의 VPC origin을 primary로, 다른 리전을 secondary로 하는 origin group을 요청마다 구성</div></div>
    <div class="metric-card"><strong class="mr03-t-info">KeyValueStore</strong><div class="mr03-muted">가중치, 활성 리전 값을 함수 재배포 없이 변경. 값은 invocation 사이에 반영</div></div>
    <div class="metric-card"><strong class="mr03-t-info">요금</strong><div class="mr03-muted">Functions $0.10/M invocation, KVS read $0.03/M (각각 월 2M 무료)</div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="mr03-split mr03-codesplit">
  <pre class="mr03-code">import cf from 'cloudfront';
const kvs = cf.kvs();
async function handler(event) {
  const req = event.request;
  const pin = req.cookies['mr-region'];  // affinity
  const region = pin ? pin.value
    : (await kvs.get('routing', { format: 'json' })).active;
  const ids = region === 'us-west-2'
    ? ['alb-usw2', 'alb-use1'] : ['alb-use1', 'alb-usw2'];
  cf.createRequestOriginGroup({
    originIds: ids.map(id =&gt; ({ originId: id })),
    failoverCriteria: { statusCodes: [500, 502, 503, 504] }
  });
  return req;
}</pre>
  <div class="mr03-stack">
    <div class="metric-card"><strong class="mr03-t-accent">runtime 2.0, viewer request</strong><div class="mr03-muted">origin 수정 helper는 viewer request 이벤트에서만 동작</div></div>
    <div class="metric-card"><strong class="mr03-t-info">behavior 기본값</strong><div class="mr03-muted">기본 origin을 origin group으로 둔 behavior에 연결</div></div>
    <div class="metric-card"><strong class="mr03-t-warning">입력 처리</strong><div class="mr03-muted">쿠키가 us-west-2가 아니면 us-east-1 순서로 처리 (설명용 예시)</div></div>
  </div>
  </div>
</div>
<div class="callout callout-info mr03-take fragment zoom-in" data-fragment-index="1"><strong class="mr03-t-info">한 줄 정리</strong><div class="mr03-muted">공개 경로는 Edge가 리전을 고르고, Route 53 latency는 private hosted zone의 내부 서비스 이름처럼 DNS가 직접 스위치인 곳에 씁니다.</div></div>
:::

:::notes
{timing: 2.5min}
[요약]
• Route 53 latency는 resolver 위치 기반이며 실시간 측정이 아님
• VPC origin은 ALB ARN에 고정되므로 공개 경로의 리전 선택은 CloudFront Function이 담당
• cf.createRequestOriginGroup()으로 선택 리전을 primary, 반대 리전을 secondary로 구성
• 활성 리전과 가중치는 KeyValueStore에 두고 재배포 없이 변경
첫 번째 탭은 Route 53 latency routing입니다. 판단 근거는 사용자의 실제 지연이 아니라 resolver IP이고, resolver가 EDNS0 client subnet을 보내면 잘린 client IP를 씁니다. 지연 데이터도 일정 기간 측정한 값이라 바뀔 수 있습니다. 예전 자료의 "24시간마다 갱신", "20개 이상 위치에서 측정" 같은 숫자는 공식 문서에서 확인되지 않아 뺐습니다.
{cue: pause}
중요한 건 VPC origin과의 관계입니다. VPC origin은 특정 ALB의 ARN으로 만들기 때문에 DNS 응답을 바꿔서 다른 리전 ALB로 보내는 방식이 통하지 않습니다. 그래서 두 번째 탭처럼 viewer request CloudFront Function이 리전을 고르고, createRequestOriginGroup으로 그 리전을 primary로 하는 origin group을 만듭니다. AWS 블로그의 multi-Region active-active 샘플이 이 구조입니다.
세 번째 탭이 최소 코드입니다. 쿠키로 고정된 리전이 있으면 그대로 쓰고, 없으면 KVS의 routing 키에서 활성 리전을 읽습니다. 장애 때는 KVS 값만 바꾸면 새 세션부터 다른 리전으로 갑니다.
{cue: question}
쿠키로 고정된 기존 세션은 어떻게 될까요? primary가 에러를 내면 GET은 secondary로 넘어가지만 POST는 넘어가지 않습니다. 이건 잠시 뒤 origin failover 슬라이드에서 다시 봅니다.
{cue: transition}
다음은 장애를 "감지"하는 쪽, 헬스체크입니다.
[출처]
• Route 53 latency routing: docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy-latency.html
• CloudFront Functions origin 수정 helper: docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/helper-functions-origin-modification.html
• KVS get(): .../functions-custom-methods.html, 요금: aws.amazon.com/cloudfront/pricing/pay-as-you-go/, aws.amazon.com/route53/pricing/
• AWS 블로그 "Building Multi-Region Active-Active Architectures with CloudFront VPC origins and Advanced Routing"
:::

---
<!-- Slide 4: 헬스체크 -->
@type: content
@title: 헬스체크는 internal ALB를 못 본다

## 헬스체크는 internal ALB를 못 본다

:::html
<div class="mr03-split">
  <div class="mr03-grid2" data-reveal="stagger">
    <div class="metric-card"><strong class="mr03-t-accent">판정 규칙</strong><div class="mr03-muted">전 세계 checker 중 18% 초과가 healthy라고 보고하면 healthy</div></div>
    <div class="metric-card"><strong class="mr03-t-accent">간격, 임계값</strong><div class="mr03-muted">간격 10초(fast, 유료 옵션) 또는 30초, 생성 후 변경 불가. 연속 실패 1~10 (기본 3)</div></div>
    <div class="metric-card"><strong class="mr03-t-info">HTTP(S) 기준</strong><div class="mr03-muted">TCP 연결 4초 이내, 연결 후 2초 이내 2xx/3xx. HTTPS 체크는 인증서를 검증하지 않음</div></div>
    <div class="metric-card"><strong class="mr03-t-warning">VPC 내부 대상</strong><div class="mr03-muted">checker는 VPC 밖에 있음. internal ALB는 CloudWatch alarm 기반 health check로 감시</div></div>
  </div>
  <div class="mr03-calc">
    <div class="mr03-row"><label>판정 주기</label><div class="mr03-btns" id="mr03-hc-int"><button class="btn btn-sm" data-v="10">10초 fast</button><button class="btn btn-sm active" data-v="30">30초</button><button class="btn btn-sm" data-v="60">alarm 1분</button></div></div>
    <div class="mr03-row"><label for="mr03-hc-th">연속 실패</label><div class="slider-container"><input type="range" id="mr03-hc-th" min="1" max="10" step="1" value="3"><span class="slider-value" id="mr03-hc-th-v">3회</span></div></div>
    <div class="mr03-row"><label for="mr03-hc-ttl">레코드 TTL</label><div class="slider-container"><input type="range" id="mr03-hc-ttl" min="10" max="300" step="10" value="60"><span class="slider-value" id="mr03-hc-ttl-v">60초</span></div></div>
    <div class="card-grid">
      <div class="metric-card"><div class="metric-value" id="mr03-hc-det">-</div><div class="metric-label">감지 (주기 × 횟수)</div></div>
      <div class="metric-card"><div class="metric-value" id="mr03-hc-tot">-</div><div class="metric-label">DNS 전환 근사 (+TTL)</div></div>
    </div>
    <div class="mr03-note">AWS 블로그의 근사식 Failover = TTL + Interval × Threshold. resolver가 TTL을 지키지 않거나 alarm 평가 지연이 있으면 더 길어집니다. 요금: AWS endpoint 체크 $0.50/월, 옵션 기능(HTTPS, fast 등)마다 $1.00/월.</div>
  </div>
</div>
:::

:::script
(function () {
  var INT = 30;
  var th = document.getElementById('mr03-hc-th');
  var ttl = document.getElementById('mr03-hc-ttl');
  var box = document.getElementById('mr03-hc-int');
  function fmt(s) { return s >= 60 ? (Math.floor(s / 60) + '분 ' + (s % 60) + '초') : (s + '초'); }
  function update() {
    var t = parseInt(th.value, 10), l = parseInt(ttl.value, 10);
    document.getElementById('mr03-hc-th-v').textContent = t + '회';
    document.getElementById('mr03-hc-ttl-v').textContent = l + '초';
    document.getElementById('mr03-hc-det').textContent = fmt(INT * t);
    document.getElementById('mr03-hc-tot').textContent = fmt(INT * t + l);
  }
  box.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    box.querySelectorAll('button').forEach(function (x) { x.classList.remove('active'); });
    b.classList.add('active'); INT = parseInt(b.getAttribute('data-v'), 10); update();
  });
  th.addEventListener('input', update);
  ttl.addEventListener('input', update);
  update();
})();
:::

:::notes
{timing: 2.5min}
[요약]
• 18% 초과 checker가 healthy면 healthy: 일부 지역 네트워크 문제로 오판하지 않기 위한 값
• 간격 10초 또는 30초(생성 후 변경 불가), 연속 실패 1~10, 기본 3
• Route 53 checker는 VPC 밖에 있으므로 internal ALB는 CloudWatch alarm 기반 health check
• 전환 시간 근사: TTL + 주기 × 횟수
왼쪽 카드부터 보겠습니다. 예전 자료에는 "모든 checker가 실패해야 unhealthy"라고 적혀 있었는데, 정확한 규칙은 18%입니다. checker의 18%를 넘게 healthy라고 보고하면 healthy, 18% 이하면 unhealthy입니다.
간격은 10초와 30초 중에서 고르고, 한 번 만들면 바꿀 수 없습니다. 10초 fast interval은 유료 옵션입니다. HTTP 체크는 TCP 연결 4초, 연결 후 2초 안에 2xx나 3xx를 받아야 하고, HTTPS 체크는 인증서를 검증하지 않습니다.
{cue: pause}
우리 구조에서 가장 중요한 카드는 네 번째입니다. Route 53 checker는 VPC 밖에 있어서 internal ALB에 직접 접속할 수 없습니다. public IP를 붙이는 건 금지이므로, ALB의 UnHealthyHostCount나 5xx 비율로 CloudWatch alarm을 만들고 그 alarm 상태를 보는 health check를 씁니다.
{cue: demo}
오른쪽 계산기에서 30초, 3회, TTL 60초면 감지 1분 30초, 전환은 약 2분 30초입니다. fast 10초로 바꾸면 감지 30초, 전환 1분 30초가 됩니다. alarm 1분 주기로 바꿔 보시면 alarm 기반 체크가 더 느리다는 것도 보입니다.
{cue: transition}
감지 다음은 "누가 스위치를 누르는가"입니다. Route 53 ARC를 보겠습니다.
[출처]
• docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-failover-determining-health-of-endpoints.html (18%, 4초/2초, HTTPS 인증서 미검증)
• .../health-checks-creating-values.html (10/30초, 변경 불가), AWS News Blog "Route 53 Health Check Improvements" (1~10, 기본 3, 근사식)
• CloudFormation AWS::Route53::HealthCheck "Private Hosted Zones" 절, aws.amazon.com/route53/pricing/
:::

---
<!-- Slide 5: Route 53 ARC -->
@type: content
@title: 절체 스위치는 데이터 플레인에 둔다

## 절체 스위치는 데이터 플레인에 둔다

:::html
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">Routing control</button>
  <button class="tab-btn">Region switch</button>
  <button class="tab-btn">Readiness check 종료</button>
</div>
<div class="tc">
  <div class="card-grid">
    <div class="metric-card"><strong class="mr03-t-accent">on/off 스위치</strong><div class="mr03-muted">routing control 상태가 Route 53 health check로 노출되어 failover 레코드를 움직임</div></div>
    <div class="metric-card"><strong class="mr03-t-accent">클러스터</strong><div class="mr03-muted">5개 리전 엔드포인트로 상태 조회, 변경. 한 리전이 장애여도 다른 엔드포인트 사용</div></div>
    <div class="metric-card"><strong class="mr03-t-info">safety rule</strong><div class="mr03-muted">"최소 1개 ON" 같은 assertion, gating 규칙으로 두 리전을 동시에 끄는 실수 방지</div></div>
    <div class="metric-card"><strong class="mr03-t-warning">요금</strong><div class="mr03-muted">클러스터 $2.50/시간 (계정당 최대 2개). 여러 routing control을 한 클러스터에</div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="card-grid">
    <div class="metric-card"><strong class="mr03-t-success">plan = workflow</strong><div class="mr03-muted">activate/deactivate workflow 안에 execution block을 순차, 병렬로 배치. active/passive, active/active 모두</div></div>
    <div class="metric-card"><strong class="mr03-t-success">execution block 예</strong><div class="mr03-muted">Route 53 health check, routing control, Aurora Global DB, EKS resource scaling, Lambda custom action, manual approval</div></div>
    <div class="metric-card"><strong class="mr03-t-info">활성화할 리전에서 실행</strong><div class="mr03-muted">Regional data plane 구조라 장애 리전에 의존하지 않음. CloudWatch alarm으로 자동 트리거 가능</div></div>
    <div class="metric-card"><strong class="mr03-t-warning">요금, 연결점</strong><div class="mr03-muted">plan당 $70/월. 우리 구조에서는 Lambda block이 KVS의 활성 리전 값을 바꾸는 설계가 가능 (설계 예시)</div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="card-grid">
    <div class="callout callout-warning"><strong class="mr03-t-warning">2026-04-30부터 신규 고객 불가</strong><div class="mr03-muted">ARC readiness check는 신규 가입이 닫혔고 기존 고객은 계속 사용 가능</div></div>
    <div class="callout callout-info"><strong class="mr03-t-info">새 설계에서는</strong><div class="mr03-muted">Region switch plan과 정기 연습, 리전별 capacity alarm으로 "절체 가능한 상태"를 확인</div></div>
    <div class="callout callout-success"><strong class="mr03-t-success">Route 53 accelerated recovery</strong><div class="mr03-muted">2025-11 출시. us-east-1 장애 시 대부분 1시간 안에 public hosted zone 레코드 변경을 복구, 추가 비용 없음</div></div>
  </div>
</div>
<div class="callout callout-info mr03-take fragment zoom-in" data-fragment-index="1"><strong class="mr03-t-info">한 줄 정리</strong><div class="mr03-muted">장애 시 control plane API(레코드 편집, 배포)에 기대지 말고, 미리 만든 스위치의 상태만 바꾸세요.</div></div>
:::

:::notes
{timing: 2.5min}
[요약]
• Routing control: on/off 스위치, 5개 리전 엔드포인트 클러스터, safety rule로 실수 방지, 클러스터 $2.50/시간
• Region switch: 리전 전환 workflow를 plan으로, 활성화할 리전에서 실행, plan당 $70/월
• Readiness check는 2026-04-30부터 신규 고객 불가
• Route 53 accelerated recovery: us-east-1 장애 시 대부분 1시간 안에 public DNS 레코드 변경 복구
첫 번째 탭, routing control은 미리 만들어 둔 on/off 스위치입니다. 상태가 Route 53 health check로 노출되므로 failover 레코드와 묶어 쓰고, 상태 변경은 5개 리전 엔드포인트를 가진 클러스터에 하므로 한 리전이 아파도 스위치를 누를 수 있습니다. safety rule로 두 리전을 동시에 끄는 실수를 막습니다. 클러스터 비용이 시간당 2.5달러라 월 약 1,800달러 수준이라는 점도 기억해 두세요.
{cue: pause}
두 번째 탭, Region switch는 2025년에 나온 orchestration 기능입니다. DB 승격, EKS 스케일, DNS 전환 같은 단계를 plan으로 만들고, 활성화할 리전에서 실행합니다. 우리 구조처럼 공개 경로를 CloudFront Function이 고르는 경우에는 Lambda custom action block이 KVS의 활성 리전 값을 바꾸는 방식으로 연결할 수 있습니다. 이 연결은 제가 제안하는 설계 예시이고 AWS가 제공하는 전용 block은 아닙니다.
세 번째 탭, 예전 자료에서 추천하던 readiness check는 2026년 4월 30일부터 신규 고객에게 열려 있지 않습니다. 새로 설계한다면 Region switch plan 연습과 capacity alarm으로 대신합니다.
{cue: question}
지난해 us-east-1 이슈 때 DNS 레코드를 못 바꿔서 곤란했던 경험이 있으신가요? 그 문제를 겨냥한 것이 Route 53 accelerated recovery입니다.
{cue: transition}
다음은 CloudFront 안쪽, behavior 구성입니다.
[출처]
• aws.amazon.com/application-recovery-controller/pricing/ (클러스터 $2.50/시간, 최대 2개, plan $70/월, readiness 신규 불가 2026-04-30)
• docs.aws.amazon.com/r53recovery/latest/dg/data-and-control-planes-rs.html, ARC Region switch API ExecutionBlockConfiguration
• What's New 2025-11 "Amazon Route 53 announces accelerated recovery for managing public DNS records"
:::

---
<!-- Slide 6: CloudFront Behaviors -->
@type: tabs
@title: Behavior: 캐시할 것과 안 할 것

## Behavior: 캐시할 것과 안 할 것

### /api/*
동적 API: 캐시 끄고, 함수가 리전을 고른 origin group으로
```yaml
PathPattern: /api/*
TargetOriginId: og-api            # origin group (alb-use1, alb-usw2)
CachePolicy: Managed-CachingDisabled
OriginRequestPolicy: Managed-AllViewerExceptHostHeader
AllowedMethods: [GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE]
ViewerProtocolPolicy: redirect-to-https
FunctionAssociations:
  - EventType: viewer-request
    Function: mr-region-router    # KVS 연결, 앞 슬라이드 코드
```

### /static/*
버전이 붙은 정적 자산: 길게 캐시, S3는 OAC로만
```yaml
PathPattern: /static/*
TargetOriginId: s3-assets         # OAC, 버킷 public access 차단
CachePolicy: Managed-CachingOptimized   # 기본 TTL 1일
AllowedMethods: [GET, HEAD]
Compress: true
ViewerProtocolPolicy: redirect-to-https
# 파일명에 해시를 넣어 배포마다 새 URL (invalidation 최소화)
```

### Default (*)
SPA 라우팅: custom error response 대신 함수로 rewrite
```yaml
PathPattern: "*"                  # default behavior
TargetOriginId: s3-assets
CachePolicy: Managed-CachingOptimized
FunctionAssociations:
  - EventType: viewer-request
    Function: spa-rewrite         # 확장자 없는 경로 → /index.html
# CustomErrorResponses(403/404 → 200 index.html)는 배포 전체에 적용되어
# /api/*의 404까지 HTML 200으로 바꿔 버림
```

:::notes
{timing: 2min}
[요약]
• /api/*: CachingDisabled + AllViewerExceptHostHeader, 모든 메서드, viewer request 함수로 origin group 선택
• /static/*: CachingOptimized, OAC, 파일명 해시로 invalidation 최소화
• Default: SPA rewrite는 함수로, custom error response는 배포 전체에 걸려 API 404를 가림
세 탭입니다. 첫 번째 /api/*는 캐시를 끄고, Host를 뺀 viewer 헤더를 origin으로 전달하는 managed 정책을 씁니다. Host를 그대로 넘기면 ALB 인증서, 라우팅과 어긋나는 문제가 생기기 때문입니다. target은 단일 origin이 아니라 origin group이고, 앞에서 본 함수가 요청마다 primary를 정합니다.
{cue: pause}
두 번째 /static/*은 CachingOptimized로 길게 캐시하고 S3는 OAC로만 접근하게 합니다. 파일명에 해시를 넣으면 배포 때 invalidation을 거의 안 해도 됩니다.
세 번째가 실무에서 자주 터지는 부분입니다. 예전 자료는 SPA를 위해 403, 404를 index.html 200으로 바꾸는 custom error response를 썼는데, 이 설정은 behavior가 아니라 distribution 전체에 적용됩니다. 그러면 /api/orders/123이 404를 내도 클라이언트는 HTML과 200을 받습니다. 그래서 default behavior에 viewer request 함수로 rewrite하는 방식으로 바꿨습니다.
{cue: transition}
이제 origin 쪽, VPC origin과 보안 그룹을 보겠습니다.
[출처]
• CloudFront managed cache/origin request policies, CustomErrorResponses는 DistributionConfig 수준 설정 (CloudFront API Reference)
:::

---
<!-- Slide 7: VPC origin + 잠금 -->
@type: content
@title: Origin 잠금: VPC origin과 SG

## Origin 잠금: VPC origin과 SG

:::html
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">준비 조건</button>
  <button class="tab-btn">SG 설계</button>
  <button class="tab-btn">제약 사항</button>
  <button class="tab-btn">가드레일</button>
</div>
<div class="tc">
  <div class="card-grid">
    <div class="metric-card"><strong class="mr03-t-accent">Internet gateway</strong><div class="mr03-muted">VPC에 붙어 있어야 함. "인터넷 트래픽을 받는 VPC" 표시용이며 origin 라우팅에는 쓰지 않음</div></div>
    <div class="metric-card"><strong class="mr03-t-accent">private subnet IP</strong><div class="mr03-muted">CloudFront가 service-managed ENI를 만들 IPv4 1개 이상 (dual-stack이면 IPv6도)</div></div>
    <div class="metric-card"><strong class="mr03-t-info">ALB Active 후 생성</strong><div class="mr03-muted">VPC origin은 Deployed까지 최대 15분. ALB, NLB, EC2 지원 (GWLB, TLS listener NLB 불가)</div></div>
    <div class="metric-card"><strong class="mr03-t-warning">AZ 예외</strong><div class="mr03-muted">us-east-1은 use1-az3 제외, us-west-2는 전체 지원. ALB subnet AZ ID를 확인</div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="card-grid">
    <div class="callout callout-success"><strong class="mr03-t-success">권장: Service SG 참조</strong><div class="mr03-muted"><code>CloudFront-VPCOrigins-Service-SG</code>를 소스로. 내 distribution 트래픽으로만 제한되어 가장 엄격 (VPC origin 생성 후 가능, 이 SG는 편집 금지)</div></div>
    <div class="callout callout-info"><strong class="mr03-t-info">대안: managed prefix list</strong><div class="mr03-muted"><code>com.amazonaws.global.<wbr>cloudfront.<wbr>origin-facing</code> (dual-stack은 ipv6 목록도). 모든 CloudFront 고객의 origin-facing IP라 더 넓음</div></div>
    <div class="callout callout-warning"><strong class="mr03-t-warning">prefix list weight 55</strong><div class="mr03-muted">SG 기본 60 rules 중 55 사용. HTTP, HTTPS 두 규칙이면 110이라 quota 초과, 443 하나만 열기</div></div>
  </div>
</div>
<div class="tc" hidden>
  <table class="data-table mr03-table">
    <thead><tr><th>항목</th><th>VPC origin에서</th><th>대응</th></tr></thead>
    <tbody>
      <tr><td>gRPC</td><td>미지원</td><td>gRPC는 별도 경로 설계 (예외 심사)</td></tr>
      <tr><td>Lambda@Edge origin request/response</td><td>미지원</td><td>origin 선택은 viewer request CloudFront Function으로</td></tr>
      <tr><td><code>updateRequestOrigin()</code></td><td>요청 실패</td><td><code>selectRequestOriginById()</code>, <code>createRequestOriginGroup()</code></td></tr>
      <tr><td>NACL</td><td>inbound 미평가, outbound는 평가</td><td>반환 경로용 ephemeral TCP 1024~65535 outbound 허용</td></tr>
    </tbody>
  </table>
</div>
<div class="tc" hidden>
  <div class="card-grid">
    <div class="metric-card"><strong class="mr03-t-danger">ALB scheme</strong><div class="mr03-muted">항상 <code>internal</code>. internet-facing LB는 생성 자체를 IaC 정책 검사에서 차단</div></div>
    <div class="metric-card"><strong class="mr03-t-danger">public IP</strong><div class="mr03-muted">EC2, EKS 노드, ECS task에 public IP, EIP 금지. subnet 자동 할당도 끔</div></div>
    <div class="metric-card"><strong class="mr03-t-danger">SG ingress</strong><div class="mr03-muted">0.0.0.0/0, ::/0 금지. 소스는 SG 참조 또는 사설 CIDR만, 배포 후 AWS Config로 상시 점검</div></div>
  </div>
</div>
<div class="callout callout-info mr03-take fragment zoom-in" data-fragment-index="1"><strong class="mr03-t-info">한 줄 정리</strong><div class="mr03-muted">ALB를 private subnet에 숨기고, SG는 VPC origin Service SG에서 443만 받으면 WAF를 우회할 경로가 사라집니다.</div></div>
:::

:::notes
{timing: 2min}
[요약]
• VPC origin 전제: IGW 부착(라우팅엔 미사용), private subnet 여유 IP, ALB Active, 생성 후 Deployed까지 최대 15분
• us-east-1은 use1-az3에서 VPC origin 미지원
• SG 소스는 CloudFront-VPCOrigins-Service-SG가 가장 엄격, prefix list는 weight 55
• 제약: gRPC, Lambda@Edge origin trigger, updateRequestOrigin() 미지원, outbound NACL은 평가됨
첫 탭은 준비 조건입니다. 의외인 점은 internet gateway가 VPC에 있어야 한다는 것인데, 문서 표현대로 "인터넷 트래픽을 받는 VPC"라는 표시일 뿐 라우팅에 쓰이지 않고 ALB는 private subnet에 그대로 둡니다. 그리고 us-east-1에서는 use1-az3가 VPC origin을 지원하지 않으니 ALB subnet의 AZ ID를 확인하세요. AZ 이름이 아니라 ID입니다.
{cue: pause}
두 번째 탭, 보안 그룹 소스는 두 가지입니다. CloudFront가 만드는 Service SG를 참조하면 내 distribution 트래픽만 받습니다. managed prefix list는 모든 CloudFront 고객의 origin-facing IP라서 더 넓고, weight가 55라 기본 quota 60 규칙에서 거의 다 씁니다. 그래서 443 하나만 엽니다.
세 번째 탭의 제약 중 updateRequestOrigin이 VPC origin에 안 된다는 점이 앞의 함수 설계와 직결됩니다. 네 번째 탭은 우리 팀 가드레일입니다. internal scheme, public IP 금지, 0.0.0.0/0 금지를 IaC 검사와 AWS Config로 이중 점검합니다.
{cue: transition}
다음은 origin 부하를 줄이는 Origin Shield입니다.
[출처]
• docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-vpc-origins.html (IGW, ENI, 15분, AZ 예외, SG 옵션, 미지원 기능, NACL)
• docs.aws.amazon.com/vpc/latest/userguide/working-with-aws-managed-prefix-lists.html (weight 55, SG 기본 60)
:::

---
<!-- Slide 8: Origin Shield -->
@type: content
@title: Origin Shield: 캐시될 때만 이득

## Origin Shield: 캐시될 때만 이득

:::html
<div class="mr03-split">
  <div class="mr03-stack">
    <div class="flow-h mr03-flow">
      <div class="flow-group"><div class="flow-group-label">Edge</div><div class="flow-box">서울, 도쿄, 시애틀 PoP</div></div>
      <div class="flow-arrow">→</div>
      <div class="flow-group"><div class="flow-group-label">Regional edge cache</div><div class="flow-box">여러 REC</div></div>
      <div class="flow-arrow">→</div>
      <div class="flow-group"><div class="flow-group-label">Origin Shield</div><div class="flow-box">us-east-1<br>(origin과 같은 리전)</div></div>
      <div class="flow-arrow">→</div>
      <div class="flow-group"><div class="flow-group-label">Origin</div><div class="flow-box">ALB, S3</div></div>
    </div>
    <div class="metric-card"><strong class="mr03-t-accent">origin마다 지정</strong><div class="mr03-muted">origin group이면 alb-use1은 us-east-1, alb-usw2는 us-west-2로 각자 Shield 리전을 둠</div></div>
  </div>
  <div class="mr03-stack">
    <div class="callout callout-warning fragment fade-left" data-fragment-index="1"><strong class="mr03-t-warning">동적 요청은 항상 과금</strong><div class="mr03-muted">PUT, POST, PATCH, DELETE와 TTL 3600초 미만 또는 캐시 비활성 GET, HEAD는 Shield가 언제나 추가 계층</div></div>
    <div class="callout callout-success fragment fade-left" data-fragment-index="2"><strong class="mr03-t-success">캐시 요청은 일부만 과금</strong><div class="mr03-muted">Shield와 같은 리전의 REC에서 오는 요청은 Shield를 건너뛰어 무과금, 다른 리전 REC에서 올 때만 과금</div></div>
    <div class="callout callout-info fragment zoom-in" data-fragment-index="3"><strong class="mr03-t-info">판단</strong><div class="mr03-muted">/static/*은 켬. /api/*는 모든 요청이 과금 대상이므로 지연 개선을 측정한 뒤 결정. 미국 요금 $0.0075/10K</div></div>
  </div>
</div>
:::

:::notes
{timing: 1.5min}
[요약]
• Origin Shield는 REC와 origin 사이의 추가 캐시 계층, origin과 가장 가까운 리전에 둠
• origin group에서는 origin마다 Shield 리전 지정
• 동적 요청(쓰기 메서드, TTL 3600초 미만 GET)은 항상 과금 대상
• /static/*은 켜고, /api/*는 측정 후 결정
Origin Shield는 regional edge cache 뒤에 하나 더 두는 캐시입니다. 여러 REC에서 같은 객체를 요청해도 Shield가 모아서 origin에는 한 번만 갑니다. Shield 리전은 origin과 가장 가까운 리전, 우리 경우 각 ALB와 같은 리전입니다.
{cue: pause}
오른쪽을 클릭하며 보겠습니다. 비용 규칙이 설계를 바꿉니다. POST 같은 쓰기 요청과 TTL 3600초 미만 GET은 Shield가 항상 추가 계층이라 모두 과금됩니다. 캐시를 끈 /api/*에 Shield를 켜면 요청 전부가 과금 대상이 됩니다. 반대로 캐시 요청은 Shield와 같은 리전의 REC에서 오면 건너뛰므로 과금되지 않습니다.
예전 자료의 "origin 요청 50~90% 감소", "순 절감 30~60%"는 근거가 없어 뺐습니다. 효과는 캐시 적중률과 트래픽 분포에 따라 다르니 CloudFront 리포트로 직접 측정하세요.
{cue: transition}
이제 origin group이 실제로 언제 넘어가는지, origin failover를 직접 눌러 보겠습니다.
[출처]
• docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/origin-shield.html "Estimate Origin Shield costs"
• aws.amazon.com/cloudfront/pricing/pay-as-you-go/ (Origin Shield 미국 $0.0075/10,000 요청)
:::

---
<!-- Slide 9: Origin failover 시뮬레이터 -->
@type: content
@title: Origin failover는 GET만 구한다

## Origin failover는 GET만 구한다

:::html
<div class="mr03-split">
  <div class="mr03-calc">
    <div class="mr03-row"><label>viewer 메서드</label><div class="mr03-btns" id="mr03-fo-m"><button class="btn btn-sm active" data-v="GET">GET /api/catalog</button><button class="btn btn-sm" data-v="POST">POST /api/orders</button></div></div>
    <div class="mr03-row"><label>primary 응답</label><div class="mr03-btns" id="mr03-fo-s"><button class="btn btn-sm" data-v="200">200</button><button class="btn btn-sm active" data-v="503">503</button><button class="btn btn-sm" data-v="timeout">연결 timeout</button></div></div>
    <div class="mr03-out" id="mr03-fo-out" aria-live="polite"></div>
  </div>
  <div class="mr03-stack" data-reveal="stagger">
    <div class="metric-card"><strong class="mr03-t-accent">조건</strong><div class="mr03-muted">설정한 상태 코드(예: 500, 502, 503, 504) 또는 연결 실패, timeout. viewer 메서드가 GET, HEAD, OPTIONS일 때만</div></div>
    <div class="metric-card"><strong class="mr03-t-warning">stateless</strong><div class="mr03-muted">health 상태를 기억하지 않아 모든 요청이 primary부터 시도. 장애 중에는 요청마다 지연이 붙음</div></div>
    <div class="metric-card"><strong class="mr03-t-info">timeout 튜닝</strong><div class="mr03-muted">connection attempts 1~3 (기본 3) × connection timeout 1~10초 (기본 10) → 기본값이면 넘어가기까지 최대 약 30초</div></div>
  </div>
</div>
<div class="callout callout-danger mr03-take fragment zoom-in" data-fragment-index="1"><strong class="mr03-t-danger">쓰기 요청은 앱이 책임</strong><div class="mr03-muted">POST /api/orders는 primary 오류가 그대로 사용자에게 갑니다. idempotency key + client retry, 그리고 KVS 활성 리전 전환으로 새 요청을 옮기세요.</div></div>
:::

:::script
(function () {
  var M = 'GET', S = '503';
  var out = document.getElementById('mr03-fo-out');
  function render() {
    var lines = ['1) ' + M + ' → primary alb-use1 (us-east-1)'];
    if (S === '200') {
      lines.push('2) 200 OK → viewer에 응답 (failover 없음)');
    } else {
      var why = S === 'timeout' ? '연결 실패 (attempts × timeout 소진, 기본값 최대 약 30초)' : '503 (failover 코드)';
      lines.push('2) primary: ' + why);
      if (M === 'GET') {
        lines.push('3) 같은 요청을 secondary alb-usw2 (us-west-2)로 재시도');
        lines.push('결과: 사용자는 성공 응답, 대신 지연이 추가됨');
      } else {
        lines.push('3) POST는 failover 대상이 아님 → secondary 시도 없음');
        lines.push('결과: 사용자에게 ' + (S === 'timeout' ? '504' : '503') + ' 반환, 앱이 재시도해야 함');
      }
    }
    out.textContent = lines.join('\n');
  }
  function bind(id, set) {
    var box = document.getElementById(id);
    box.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      box.querySelectorAll('button').forEach(function (x) { x.classList.remove('active'); });
      b.classList.add('active'); set(b.getAttribute('data-v')); render();
    });
  }
  bind('mr03-fo-m', function (v) { M = v; });
  bind('mr03-fo-s', function (v) { S = v; });
  render();
})();
:::

:::notes
{timing: 2.5min}
[요약]
• origin group failover는 viewer 메서드가 GET, HEAD, OPTIONS일 때만 동작
• 상태를 기억하지 않아 요청마다 primary부터 시도
• 기본 timeout(3회 × 10초)이면 넘어가기까지 최대 약 30초
• POST 주문, 결제는 idempotency key와 재시도, KVS 리전 전환으로 해결
{cue: demo}
왼쪽 버튼으로 직접 보겠습니다. GET에 503이면 CloudFront가 같은 요청을 us-west-2로 다시 보내고 사용자는 성공을 받습니다. 이제 POST /api/orders로 바꿔 보세요. 똑같이 503인데 secondary 시도가 없습니다. CloudFront는 GET, HEAD, OPTIONS가 아니면 failover하지 않습니다. 예전 자료의 "sub-second switching, 사용자는 실패를 인지하지 못한다"는 쓰기 요청에서는 사실이 아닙니다.
{cue: pause}
연결 timeout을 눌러 보면, 기본값인 연결 시도 3회와 연결 timeout 10초가 다 소진된 뒤에야 넘어갑니다. 최대 약 30초입니다. 그리고 origin group은 상태를 기억하지 않으므로 장애가 이어지는 동안 모든 요청이 이 대기를 반복합니다. 시도 횟수와 timeout을 줄이되, 정상 지연 분포를 보고 정하세요.
{cue: question}
주문, 결제 API에 idempotency key가 있나요? 없다면 클라이언트 재시도가 중복 주문을 만듭니다. 이건 Block 2의 데이터 일관성과도 연결됩니다.
{cue: transition}
경로와 절체를 봤으니 이제 Edge의 방어, WAF로 넘어가겠습니다.
[출처]
• docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/RequestAndResponseBehaviorOriginGroups.html (GET, HEAD, OPTIONS만)
• CloudFormation Origin ConnectionTimeout 1~10초 기본 10, CloudFront Functions helper (connectionAttempts 1~3)
:::

---
<!-- Slide 10: WAF 규칙 스택 -->
@type: content
@title: WAF 순서: 넓게 거르고 좁게 본다

## WAF 순서: 넓게 거르고 좁게 본다

:::html
<div class="mr03-split">
  <div class="mr03-prio fragment" data-reveal="stagger" data-reveal-anim="up" data-fragment-index="1">
    <div class="mr03-prio-row"><span class="mr03-prio-num">0</span><span class="mr03-prio-name">IP allow/block set</span><span class="mr03-muted">운영팀 명시 결정, 가장 먼저</span></div>
    <div class="mr03-prio-row"><span class="mr03-prio-num">1</span><span class="mr03-prio-name">Anti-DDoS AMR</span><span class="mr03-muted"><code>AWSManagedRulesAntiDDoSRuleSet</code>, 상단 배치, scope-down 금지</span></div>
    <div class="mr03-prio-row"><span class="mr03-prio-num">2</span><span class="mr03-prio-name">Rate-based</span><span class="mr03-muted">window 60, 120, 300, 600초, 약 10초마다 평가</span></div>
    <div class="mr03-prio-row"><span class="mr03-prio-num">3</span><span class="mr03-prio-name">IP reputation</span><span class="mr03-muted">AmazonIpReputationList, AnonymousIpList</span></div>
    <div class="mr03-prio-row"><span class="mr03-prio-num">4</span><span class="mr03-prio-name">Exploit</span><span class="mr03-muted">CommonRuleSet, KnownBadInputs, SQLiRuleSet</span></div>
    <div class="mr03-prio-row"><span class="mr03-prio-num">5</span><span class="mr03-prio-name">Bot Control + label 규칙</span><span class="mr03-muted">scope-down 적용, 뒤에서 label로 예외 처리</span></div>
  </div>
  <div class="mr03-stack">
    <div class="metric-card fragment fade-left" data-fragment-index="2"><strong class="mr03-t-accent">scope CLOUDFRONT</strong><div class="mr03-muted">CloudFront용 web ACL은 us-east-1에서 생성. ALB용 REGIONAL ACL과 별개</div></div>
    <div class="metric-card fragment fade-left" data-fragment-index="2"><strong class="mr03-t-info">WCU</strong><div class="mr03-muted">web ACL 기본 1,500 WCU. 초과 시 500 WCU마다 $0.20/M 요청 추가</div></div>
    <div class="metric-card fragment fade-left" data-fragment-index="2"><strong class="mr03-t-warning">요금</strong><div class="mr03-muted">web ACL $5/월, 규칙 또는 rule group $1/월, 요청 $0.60/M</div></div>
  </div>
</div>
:::

:::notes
{timing: 2min}
[요약]
• 순서: 명시 IP 목록 → Anti-DDoS AMR → rate-based → reputation → exploit → Bot Control
• Anti-DDoS AMR은 상단, scope-down 없이 (baseline 정확도)
• rate-based는 window 60/120/300/600초 중 선택, 약 10초마다 평가
• CloudFront용 web ACL은 us-east-1, 기본 1,500 WCU, $5 + $1/규칙 + $0.60/M
번호가 곧 priority입니다. 0번은 운영팀이 명시적으로 내린 허용, 차단 결정이라 가장 먼저 둡니다. 1번은 2025년에 추가된 Anti-DDoS managed rule group입니다. AWS 가이드는 IP 목록 바로 뒤에 두고 scope-down을 쓰지 말라고 합니다. 트래픽 baseline을 학습하는 방식이라 보는 요청이 줄면 판단이 부정확해지기 때문입니다.
{cue: pause}
2번 rate-based는 이제 window를 60초부터 600초까지 고를 수 있습니다. 예전 자료의 "5분 2,000건"은 고정값이 아니라 하나의 예시였을 뿐이니, 정상 사용자 분포를 보고 정하세요. 3, 4번은 managed rule group이고, 5번 Bot Control은 다음 슬라이드에서 자세히 봅니다.
오른쪽은 운영 사실입니다. CloudFront용 web ACL은 us-east-1에서 만들고, 기본 1,500 WCU를 넘기면 요청당 추가 요금이 붙습니다.
{cue: transition}
Bot Control은 켜는 순간 쇼핑몰 모바일 앱을 막을 수 있습니다. 왜 그런지 보겠습니다.
[출처]
• repost.aws/knowledge-center/waf-mitigate-ddos-attacks (Anti-DDoS 배치, scope-down 금지)
• WAF RateBasedStatement EvaluationWindowSec (60/120/300/600, 기본 300, 약 10초마다 평가)
• aws.amazon.com/waf/pricing/ (web ACL $5, 규칙 $1, $0.60/M, 1,500 WCU, 500 WCU당 $0.20/M)
:::

---
<!-- Slide 11: Bot Control -->
@type: content
@title: Bot Control은 Count로 시작한다

## Bot Control은 Count로 시작한다

:::html
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">레벨과 요금</button>
  <button class="tab-btn">쇼핑몰의 함정</button>
  <button class="tab-btn">Count 오버라이드</button>
</div>
<div class="tc">
  <div class="card-grid">
    <div class="metric-card"><strong class="mr03-t-accent">Common</strong><div class="mr03-muted">자기 신고형 봇, 검증된 봇 분류. 구독 $10/월, 월 10M 요청 무료, 이후 $1/M</div></div>
    <div class="metric-card"><strong class="mr03-t-warning">Targeted</strong><div class="mr03-muted">정교한 봇 탐지. 월 1M 요청 무료, 이후 $10/M. flat-rate 플랜에서는 미지원</div></div>
    <div class="metric-card"><strong class="mr03-t-success">verified bot</strong><div class="mr03-muted">검색 엔진 등은 차단하지 않고 <code>bot:verified</code> label만 붙임. web bot auth label은 v4.0 이상</div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="card-grid">
    <div class="callout callout-danger"><strong class="mr03-t-danger">모바일 앱</strong><div class="mr03-muted"><code>SignalNonBrowserUserAgent</code>는 기본 Block. 앱의 비브라우저 User-Agent가 막힘</div></div>
    <div class="callout callout-warning"><strong class="mr03-t-warning">서버 간 호출</strong><div class="mr03-muted">결제사 webhook, 파트너 SDK, synthetic 모니터링이 HTTP library 분류로 잡힐 수 있음</div></div>
    <div class="callout callout-info"><strong class="mr03-t-info">scope-down</strong><div class="mr03-muted">사람이 쓰는 경로만 검사 (예: /api/payments/webhook 제외). 탐지 범위와 Bot Control 요청 요금이 함께 줄어듦</div></div>
  </div>
</div>
<div class="tc" hidden>
  <pre class="mr03-code">"ManagedRuleGroupStatement": {
  "VendorName": "AWS",
  "Name": "AWSManagedRulesBotControlRuleSet",
  "ManagedRuleGroupConfigs": [
    { "AWSManagedRulesBotControlRuleSet": { "InspectionLevel": "COMMON" } }
  ],
  "RuleActionOverrides": [
    { "Name": "SignalNonBrowserUserAgent", "ActionToUse": { "Count": {} } }
  ]
}
// 다음 규칙: label awswaf:managed:aws:bot-control:signal:non_browser_user_agent
//            AND NOT (앱 User-Agent) → Block</pre>
  <div class="mr03-note">1) Count로 배포 → 2) WAF 로그에서 label 분포 확인 → 3) label + 조건으로 예외 규칙 → 4) Block 전환</div>
</div>
<div class="callout callout-info mr03-take fragment zoom-in" data-fragment-index="1"><strong class="mr03-t-info">한 줄 정리</strong><div class="mr03-muted">Bot Control의 결정은 label로 남기고, 차단은 우리가 쓴 다음 규칙이 하게 만드세요.</div></div>
:::

:::notes
{timing: 2.5min}
[요약]
• Common: $10/월 + 10M 무료 후 $1/M, Targeted: 1M 무료 후 $10/M (flat-rate 미지원)
• SignalNonBrowserUserAgent는 기본 Block: 모바일 앱, 서버 간 호출이 막힐 수 있음
• 규칙 오버라이드로 Count → label 분석 → 예외 규칙 → Block 순서
• scope-down은 오탐과 요청 요금을 같이 줄임
첫 탭은 레벨입니다. Common은 스스로 봇이라고 밝히는 클라이언트와 검증된 봇을 분류하고, Targeted는 더 정교한 탐지를 합니다. 요금 구조가 열 배 차이나니 Targeted는 로그인, 결제처럼 필요한 경로에만 scope-down으로 씁니다.
{cue: pause}
두 번째 탭이 이 블록에서 가장 실전적인 내용입니다. SignalNonBrowserUserAgent 규칙은 기본 동작이 Block이고, AWS 문서에도 모바일 앱은 보통 비브라우저 User-Agent라서 이 규칙에 막힌다고 적혀 있습니다. 쇼핑몰 트래픽의 상당 부분이 앱이라면 켜는 순간 장애입니다. 결제사 webhook이나 모니터링도 비슷하게 잡힐 수 있습니다.
세 번째 탭처럼 그 규칙만 Count로 오버라이드하면 label은 그대로 붙고 차단은 안 됩니다. 그다음 우리 규칙에서 label과 앱 User-Agent 조건을 조합해 차단합니다.
{cue: question}
현재 WAF 로그에서 non_browser_user_agent label이 붙은 요청 비율을 보신 적 있나요? 그 숫자가 Block 전환 전에 반드시 확인할 값입니다.
{cue: transition}
여기까지가 CloudFront 쪽입니다. Global Accelerator는 언제 쓰는지 비교해 보겠습니다.
[출처]
• docs.aws.amazon.com/waf/latest/developerguide/waf-bot-control-example-user-agent-exception.html (모바일 앱, Count 오버라이드 예시)
• aws.amazon.com/waf/pricing/ (Bot Control 구독, 무료 한도, 요청 요금), CloudFront flat-rate 미지원 기능 표 (Targeted Bots)
• aws.amazon.com/waf/faqs/ (web bot auth, v4.0 이상)
:::

---
<!-- Slide 12: GA vs CloudFront -->
@type: content
@title: CloudFront와 GA는 층이 다르다

## CloudFront와 GA는 층이 다르다

:::html
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">비교표</button>
  <button class="tab-btn">우리 선택</button>
</div>
<div class="tc">
  <table class="data-table mr03-table">
    <thead><tr><th>항목</th><th><img class="mr03-ico" src="./common/aws-icons/services/Arch_Amazon-CloudFront_48.svg" alt="Amazon CloudFront">CloudFront</th><th><img class="mr03-ico" src="./common/aws-icons/services/Arch_AWS-Global-Accelerator_48.svg" alt="AWS Global Accelerator">Global Accelerator</th></tr></thead>
    <tbody>
      <tr><td>계층, 프로토콜</td><td>L7 HTTP(S), WebSocket</td><td>L4 TCP, UDP</td></tr>
      <tr><td>입구 주소</td><td>DNS 이름 (Anycast static IP 옵션 있음)</td><td>고정 anycast IPv4 2개</td></tr>
      <tr><td>캐시, WAF</td><td>Edge 캐시, WAF를 Edge에서 적용</td><td>캐시 없음, WAF는 뒤쪽 ALB에 붙임</td></tr>
      <tr><td>리전 분배</td><td>origin group, CloudFront Function</td><td>traffic dial, endpoint weight, 자동 failover</td></tr>
      <tr><td>private origin</td><td>VPC origin (ALB, NLB, EC2)</td><td>internal ALB endpoint (client IP 보존)</td></tr>
      <tr><td>과금</td><td>요청 + 전송량, AWS origin fetch 무료</td><td>$0.025/시간 + DT-Premium (미국→미국 $0.015/GB) + public IPv4</td></tr>
    </tbody>
  </table>
</div>
<div class="tc" hidden>
  <div class="card-grid">
    <div class="callout callout-success"><strong class="mr03-t-success">쇼핑몰: CloudFront 단독</strong><div class="mr03-muted">HTTP(S) 트래픽, 정적 캐시, Edge WAF, VPC origin이 모두 필요</div></div>
    <div class="callout callout-warning"><strong class="mr03-t-warning">GA는 예외 심사</strong><div class="mr03-muted">비HTTP(TCP/UDP) 요구가 생기면 별도 공개 입구가 되므로 보안 검토 후 결정</div></div>
    <div class="callout callout-info"><strong class="mr03-t-info">고정 IP 요구</strong><div class="mr03-muted">파트너 방화벽 allowlist 때문이라면 CloudFront Anycast static IP를 먼저 검토</div></div>
  </div>
</div>
<div class="callout callout-info mr03-take fragment zoom-in" data-fragment-index="1"><strong class="mr03-t-info">한 줄 정리</strong><div class="mr03-muted">HTTP라면 CloudFront, 비HTTP라면 GA. 둘 다 쓰면 공개 입구가 두 개가 된다는 사실부터 인정하세요.</div></div>
:::

:::notes
{timing: 1.5min}
[요약]
• CloudFront: L7, 캐시, Edge WAF, VPC origin, AWS origin fetch 무료
• GA: L4 TCP/UDP, 고정 anycast IPv4 2개, traffic dial과 endpoint weight, internal ALB endpoint 가능
• GA 요금: $0.025/시간 + DT-Premium + public IPv4 요금
• 이 아키텍처의 가드레일상 공개 입구는 CloudFront 하나, GA는 예외 심사
두 서비스는 같은 "글로벌 가속"으로 묶이지만 동작하는 층이 다릅니다. CloudFront는 HTTP를 이해하므로 캐시하고 WAF를 Edge에서 적용합니다. GA는 TCP, UDP를 고정 IP로 받아 AWS 백본으로 가장 가까운 리전 endpoint에 넘기며, traffic dial로 리전 비율을 조정합니다.
{cue: pause}
예전 자료에 GA를 "per-flow 과금"으로 적었는데 정확하지 않습니다. 고정 시간당 요금 0.025달러와 지배적 방향 트래픽의 DT-Premium, 그리고 public IPv4 주소 요금입니다. CloudFront 요청 단가도 2026년 현재 미국 HTTPS 기준 1만 건당 0.0100달러입니다.
우리 쇼핑몰은 순수 HTTP(S)라 CloudFront 단독입니다. GA를 추가하면 공개 입구가 두 개가 되므로 보안 검토 대상입니다. 고정 IP가 필요한 이유가 파트너 allowlist라면 CloudFront의 Anycast static IP를 먼저 보세요.
{cue: transition}
마지막으로 이 Edge 구성이 한 달에 얼마인지 계산해 보겠습니다.
[출처]
• aws.amazon.com/global-accelerator/pricing/ ($0.025/시간, DT-Premium 지배 방향, 미국→미국 $0.015/GB, public IPv4 요금)
• docs.aws.amazon.com/global-accelerator (internal ALB endpoint, client IP preservation), repost "global-accelerator-failover-different-region" (traffic dial, weight)
:::

---
<!-- Slide 13: Edge 비용 계산기 -->
@type: content
@title: Edge 비용: 종량제 vs 정액제

## Edge 비용: 종량제 vs 정액제

:::html
<div class="mr03-calc">
  <div class="mr03-split">
    <div class="mr03-stack">
      <div class="mr03-row"><label for="mr03-c-req">월 요청 수</label><div class="slider-container"><input type="range" id="mr03-c-req" min="10" max="500" step="10" value="100"><span class="slider-value" id="mr03-c-req-v">100M</span></div></div>
      <div class="mr03-row"><label for="mr03-c-tb">월 전송량</label><div class="slider-container"><input type="range" id="mr03-c-tb" min="1" max="10" step="1" value="5"><span class="slider-value" id="mr03-c-tb-v">5TB</span></div></div>
      <div class="mr03-row"><label for="mr03-c-bot">Bot Control</label><label><input type="checkbox" id="mr03-c-bot" checked> Common, 전체 요청 검사</label></div>
      <div class="mr03-note" id="mr03-c-break"></div>
    </div>
    <div class="card-grid">
      <div class="metric-card"><div class="metric-value" id="mr03-c-payg">-</div><div class="metric-label">종량제 합계 (월)</div></div>
      <div class="metric-card"><div class="metric-value">$1,000</div><div class="metric-label">flat-rate Premium (월)</div></div>
    </div>
  </div>
  <div class="callout callout-warning fragment fade-up" data-fragment-index="1"><strong class="mr03-t-warning">이 구조는 Premium이 필요합니다.</strong><div class="mr03-muted">VPC origin은 Business 이상, 자동 origin failover와 Origin Shield는 Premium 전용. Premium 기본 한도 500M 요청, 50TB. 추정 가정: 미국 viewer, 전송량 첫 10TB 구간, 1TB=1,000GB 근사, WAF 규칙 8개, Anti-DDoS AMR, 로그, Route 53, ARC 제외.</div></div>
</div>
:::

:::script
(function () {
  var req = document.getElementById('mr03-c-req');
  var tb = document.getElementById('mr03-c-tb');
  var bot = document.getElementById('mr03-c-bot');
  function usd(n) { return '$' + n.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 }); }
  function update() {
    var m = parseInt(req.value, 10), t = parseInt(tb.value, 10);
    document.getElementById('mr03-c-req-v').textContent = m + 'M';
    document.getElementById('mr03-c-tb-v').textContent = t + 'TB';
    var dto = Math.max(0, t * 1000 - 1000) * 0.085;
    var rq = Math.max(0, m - 10) * 1.0;
    var waf = 5 + 8 + m * 0.60;
    var bc = bot.checked ? 10 + Math.max(0, m - 10) * 1.0 : 0;
    var fn = Math.max(0, m - 2) * 0.10 + Math.max(0, m - 2) * 0.03;
    var total = dto + rq + waf + bc + fn;
    document.getElementById('mr03-c-payg').textContent = usd(total);
    document.getElementById('mr03-c-break').textContent =
      '전송 ' + usd(dto) + ' + 요청 ' + usd(rq) + ' + WAF ' + usd(waf) + ' + Bot ' + usd(bc) + ' + Functions/KVS ' + usd(fn);
  }
  req.addEventListener('input', update);
  tb.addEventListener('input', update);
  bot.addEventListener('change', update);
  update();
})();
:::

:::notes
{timing: 2min}
[요약]
• 종량제: 전송 $0.085/GB(미국, 1TB 무료 후 첫 10TB 구간), HTTPS $0.0100/10K(10M 무료), WAF, Bot Control, Functions, KVS 합산
• flat-rate: 요청, 전송 초과 요금 없음, WAF 차단 요청은 한도에 미포함
• 이 아키텍처는 VPC origin(Business 이상) + origin failover, Origin Shield(Premium 전용) → Premium $1,000
• 기본값 100M 요청, 5TB면 종량제가 저렴, 500M, 10TB면 Premium이 저렴
{cue: demo}
기본값 100M 요청, 5TB에서 종량제는 약 616달러입니다. 전송량이 340달러로 가장 크고, Bot Control을 전체 요청에 걸면 100달러가 붙습니다. 슬라이더를 500M, 10TB까지 올려 보시면 2,100달러를 넘어 Premium 1,000달러보다 비싸집니다.
{cue: pause}
아래 경고가 핵심입니다. 2025년 11월에 나온 flat-rate 플랜은 기능이 티어별로 다릅니다. VPC origin은 Business부터, 자동 origin failover와 Origin Shield는 Premium에만 있습니다. 그래서 이 멀티리전 구조라면 비교 대상은 Business 200달러가 아니라 Premium 1,000달러입니다. 그리고 Targeted Bot Control이나 real-time log, staging distribution 같은 기능은 flat-rate에서 지원되지 않으니 필요하면 종량제여야 합니다.
예전 자료의 "CloudFront 월 50~500달러", "WAF 비활성화 상태 0달러" 같은 값은 근거가 없거나 지금 구조와 맞지 않아 뺐습니다. 실제 견적은 Pricing Calculator와 Cost Explorer 실측으로 확인하세요.
{cue: transition}
배운 내용을 세 문제로 점검해 보겠습니다.
[출처]
• aws.amazon.com/cloudfront/pricing/pay-as-you-go/ (전송, HTTPS 요청, 무료 한도, Functions, KVS, AWS origin fetch 무료)
• docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/flat-rate-pricing-plan.html (티어별 기능, 한도, 미지원 기능)
• aws.amazon.com/waf/pricing/
• 직접 계산(기본값): 전송 4,000GB × 0.085 = 340, 요청 90 × 1.00 = 90, WAF 13 + 60 = 73, Bot 10 + 90 = 100, Functions/KVS 98 × 0.13 ≈ 12.7, 합계 ≈ $616
:::

---
<!-- Slide 14: Knowledge Check -->
@type: content
@title: Knowledge Check

## Knowledge Check

:::html
<style>
.mr03-quiz { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-4); align-items: start; }
.mr03-quiz .quiz { margin: 0; }
.mr03-quiz .quiz-question { font-size: var(--fs-card); word-break: keep-all; }
.mr03-quiz .quiz-option { font-size: var(--fs-caption); word-break: keep-all; text-align: left; }
</style>
<div class="mr03-quiz" data-reveal="static">
  <div class="quiz" data-quiz="mr03-q1">
    <div class="quiz-question">Q1: POST /api/orders 처리 중 primary origin이 503을 반환하면?</div>
    <div class="quiz-options">
      <button class="quiz-option" data-correct="false">CloudFront가 secondary 리전으로 자동 재시도한다</button>
      <button class="quiz-option" data-correct="true">503이 그대로 viewer에게 간다 (GET, HEAD, OPTIONS만 failover)</button>
      <button class="quiz-option" data-correct="false">Route 53 health check가 즉시 DNS를 바꾼다</button>
    </div>
    <div class="quiz-feedback"></div>
  </div>
  <div class="quiz" data-quiz="mr03-q2">
    <div class="quiz-question">Q2: VPC origin 뒤 internal ALB의 SG 소스로 가장 엄격한 것은?</div>
    <div class="quiz-options">
      <button class="quiz-option" data-correct="false">443에 모든 IPv4 허용, 대신 WAF로 보호</button>
      <button class="quiz-option" data-correct="false">CloudFront managed prefix list를 모든 포트에</button>
      <button class="quiz-option" data-correct="true">CloudFront-VPCOrigins-Service-SG에서 443만</button>
    </div>
    <div class="quiz-feedback"></div>
  </div>
  <div class="quiz" data-quiz="mr03-q3">
    <div class="quiz-question">Q3: Bot Control(Common)을 켠 뒤 모바일 앱 요청이 막혔다. 원인과 대응은?</div>
    <div class="quiz-options">
      <button class="quiz-option" data-correct="true">SignalNonBrowserUserAgent 기본 Block, Count 오버라이드 후 label 기반 예외</button>
      <button class="quiz-option" data-correct="false">Rate-based window가 짧아서, 600초로 늘린다</button>
      <button class="quiz-option" data-correct="false">verified bot으로 분류되어서, Targeted로 올린다</button>
    </div>
    <div class="quiz-feedback"></div>
  </div>
</div>
:::

:::notes
{timing: 1.5min}
[요약]
• Q1: origin failover는 GET, HEAD, OPTIONS만, 쓰기는 앱 재시도와 KVS 전환
• Q2: VPC origin Service SG 참조 + 443이 가장 엄격, 0.0.0.0/0은 금지
• Q3: SignalNonBrowserUserAgent 기본 Block, Count 오버라이드 + label 예외
1번은 함정 문제입니다. origin group이 있어도 POST는 넘어가지 않으므로 503이 그대로 갑니다. Route 53 health check는 이 요청 경로와 무관합니다.
2번은 VPC origin이 만드는 Service SG를 참조하면 내 distribution 트래픽만 받습니다. prefix list는 모든 CloudFront 고객 IP라 더 넓고, 0.0.0.0/0은 WAF가 있어도 우회 경로가 되므로 금지입니다.
3번은 문서에 명시된 사례입니다. 모바일 앱은 비브라우저 User-Agent라 SignalNonBrowserUserAgent에 막힙니다.
{cue: question}
세 문제 중 어느 것이 가장 헷갈리셨나요? 대부분 1번에서 갈립니다.
{cue: transition}
핵심을 정리하겠습니다.
:::

---
<!-- Slide 15: Key Takeaways -->
@type: content
@title: Key Takeaways

## Key Takeaways

:::html
<div class="card-grid" data-reveal="stagger">
  <div class="metric-card"><strong class="mr03-t-accent">입구는 하나</strong><div class="mr03-muted">CloudFront → VPC origin → internal ALB. internet-facing LB, public IP, 0.0.0.0/0 없음</div></div>
  <div class="metric-card"><strong class="mr03-t-accent">리전은 Edge가 고름</strong><div class="mr03-muted">CloudFront Function + KVS + <code>createRequestOriginGroup()</code>, DNS latency는 내부 이름에</div></div>
  <div class="metric-card"><strong class="mr03-t-info">감지와 스위치 분리</strong><div class="mr03-muted">internal ALB는 alarm 기반 health check, 절체는 routing control, Region switch</div></div>
  <div class="metric-card"><strong class="mr03-t-warning">failover는 GET만</strong><div class="mr03-muted">쓰기 API는 idempotency key, 재시도, 활성 리전 전환으로 보완</div></div>
  <div class="metric-card"><strong class="mr03-t-warning">Bot Control은 Count부터</strong><div class="mr03-muted">모바일 앱, webhook을 label로 확인한 뒤 Block</div></div>
  <div class="metric-card"><strong class="mr03-t-success">비용은 구조로 결정</strong><div class="mr03-muted">VPC origin + failover + Shield면 flat-rate는 Premium. 종량제와 실측 비교</div></div>
</div>
:::

:::notes
{timing: 1min}
[요약]
• 공개 입구는 CloudFront 하나, origin은 VPC origin 뒤 internal ALB
• 리전 선택은 Edge 함수와 KVS, 절체는 데이터 플레인 스위치
• origin failover는 GET 계열만, 쓰기는 앱이 책임
• Bot Control은 Count로 시작, 비용은 구조가 정함
여섯 장의 카드로 정리합니다. 첫째, 입구는 하나입니다. 둘째, 공개 경로의 리전 선택은 DNS가 아니라 Edge 함수가 합니다. 셋째, 감지는 alarm 기반 health check, 스위치는 routing control과 Region switch로 분리합니다.
넷째, origin failover는 GET 계열만 구하므로 주문, 결제는 앱이 재시도와 멱등성을 책임집니다. 다섯째, Bot Control은 Count부터 시작합니다. 여섯째, VPC origin과 failover를 쓰는 순간 flat-rate 비교 대상은 Premium입니다.
{cue: transition}
다음 블록에서는 이 스위치를 실제로 누르는 DR과 failover 자동화를 다룹니다.
:::

---
<!-- Slide 16: Block 3 마무리 -->
@type: thankyou
@toc: toc.html
@next: 04-dr-failover.html
@next-label: 다음: DR & Failover Automation
@message: Block 3: Traffic Routing & Edge 완료

:::notes
{timing: 0.5min}
[요약]
• Block 3 핵심: 입구 하나(CloudFront VPC origin), Edge에서 리전 선택, 데이터 플레인 스위치
• Q&A 후 5분 휴식, 다음은 Block 4 DR & Failover Automation
Block 3을 마칩니다. 기억할 것은 세 가지입니다. 공개 입구는 CloudFront 하나, 리전 선택은 Edge 함수, 절체는 미리 만든 스위치입니다.
{cue: question}
질문 있으시면 지금 받겠습니다. 5분 쉬고 Block 4에서 이 스위치를 자동화하는 방법을 보겠습니다.
:::
