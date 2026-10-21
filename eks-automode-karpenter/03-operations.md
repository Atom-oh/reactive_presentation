---
remarp: true
block: 03-operations
---

---
<!-- Slide 1: 4부 구분 (Section) -->
@type: section

# 4부: 운영과 선택 기준

업그레이드, 관측, 비용, 그리고 무엇을 고를까

:::notes
{timing: 0.5min}
[요약]
- 4부의 질문: 1.37로 어떻게 올리고, 무엇을 보고, 비용은 어떻게 달라지며, 어느 쪽을 고를까
- 순서: 업그레이드 순서, 관측 포인트, 비용, 선택 체크리스트
- 체크리스트가 끝나면 바로 데모 영상으로 넘어갑니다.

4부는 운영과 선택 기준입니다. 3부에서 본 동작을 실제로 운영할 때 필요한 네 가지를 짧게 보겠습니다. 업그레이드 순서, 무엇을 관측할지, 비용, 그리고 Auto Mode와 직접 운영 중 무엇을 고를지입니다.
{cue: transition}
업그레이드 순서부터 보겠습니다.
:::

---
<!-- Slide 2: 업그레이드 순서 -->
@type: content
@title: 1.37 업그레이드: Karpenter가 먼저

## 1.37 업그레이드: Karpenter가 먼저

:::html
<style>
.ak3-steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-3); margin-top: var(--space-3); margin-bottom: var(--space-3); }
.ak3-step { border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-3); font-size: var(--fs-card); word-break: keep-all; overflow-wrap: break-word; }
.ak3-num { display: inline-flex; align-items: center; justify-content: center; width: 1.8em; height: 1.8em; border-radius: 50%; background: var(--accent-subtle); color: var(--accent); font-weight: var(--weight-bold); margin-bottom: var(--space-2); }
.ak3-step strong { display: block; margin-bottom: var(--space-1); }
.ak3-sub { color: var(--text-secondary); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">Self-managed</button>
  <button class="tab-btn">v1.15.0 breaking</button>
  <button class="tab-btn">Auto Mode</button>
</div>
<div class="tc">
  <div class="ak3-steps">
    <div class="ak3-step"><span class="ak3-num">1</span><strong>Karpenter 1.15.x</strong><span class="ak3-sub"><code>karpenter-crd</code>와 controller chart를 함께, 버전 문자열은 <code>1.15.0</code></span></div>
    <div class="ak3-step"><span class="ak3-num">2</span><strong>상태 확인</strong><span class="ak3-sub">EC2NodeClass <code>ValidationSucceeded</code>, 대시보드 label 변경</span></div>
    <div class="ak3-step"><span class="ak3-num">3</span><strong>컨트롤 플레인 1.37</strong><span class="ak3-sub">리전 기본은 1.36이라 버전 명시</span></div>
    <div class="ak3-step"><span class="ak3-num">4</span><strong>노드 AMI 갱신</strong><span class="ak3-sub">alias pin을 1.37 AMI로 바꾸면 Drift로 롤링, budget 적용</span></div>
  </div>
  <div class="callout callout-warning fragment fade-up" data-fragment-index="1"><strong class="text-warning">왜 Karpenter가 먼저인가</strong>: 1.37 호환 버전은 1.15.x뿐입니다. v1.14 LTS로는 1.36까지만 갈 수 있습니다.</div>
</div>
<div class="tc" hidden>
  <div class="card-grid">
    <div class="callout callout-warning"><strong class="text-warning">Node Repair가 voluntary로</strong><div class="on-surface-muted">대체 노드 선 생성, NDB reason <code>Unhealthy</code>. CRD enum이 바뀌므로 CRD를 함께 업그레이드</div></div>
    <div class="callout callout-warning"><strong class="text-warning">kubelet 검증이 controller로</strong><div class="on-surface-muted">apply는 성공, EC2NodeClass가 <code>Invalid<wbr>Kubelet<wbr>Configuration</code>으로 NotReady</div></div>
    <div class="callout callout-warning"><strong class="text-warning">무시되던 설정 거부</strong><div class="on-surface-muted">Bottlerocket <code>podsPerCore</code>, <code>clusterDNS</code> 2개 이상은 <code>Unsupported<wbr>Kubelet<wbr>Configuration</code></div></div>
    <div class="callout callout-warning"><strong class="text-warning">메트릭 label 변경</strong><div class="on-surface-muted"><code>reason</code> 소문자화, <code>consolidation_<wbr>type</code>은 empty, single, multi, 미분류 error는 <code>unknown</code></div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="ak3-steps">
    <div class="ak3-step"><span class="ak3-num">1</span><strong>관리형 구성 요소</strong><span class="ak3-sub">Karpenter, CNI, CoreDNS 등은 AWS가 업데이트</span></div>
    <div class="ak3-step"><span class="ak3-num">2</span><strong>1.37 변경 점검</strong><span class="ak3-sub">SELinuxMount 기본 활성, Auto Mode AMI는 SELinux enforcing</span></div>
    <div class="ak3-step"><span class="ak3-num">3</span><strong>NodePool 정책 명시</strong><span class="ak3-sub">새 NodePool의 기본 <code>Balanced</code> 반영 여부 결정</span></div>
    <div class="ak3-step"><span class="ak3-num">4</span><strong>노드는 Drift로 교체</strong><span class="ak3-sub">PDB와 NDB를 존중하며 롤링</span></div>
  </div>
  <div class="callout callout-info fragment fade-up" data-fragment-index="2"><strong class="text-info">사용자가 볼 것</strong>: PDB가 교체를 막고 있지 않은지, 같은 볼륨을 다른 SELinux 라벨로 공유하는 Pod가 <code>ContainerCreating</code>에 머물지 않는지</div>
</div>
:::

:::notes
{timing: 2min}
[요약]
- self-managed 순서: Karpenter 1.15.x(CRD chart 포함, 버전 문자열은 v 없이 1.15.0), 상태 확인, 컨트롤 플레인 1.37, 노드 AMI 갱신과 Drift 롤링
- v1.15.0 breaking: Node Repair voluntary화와 Unhealthy enum(CRD 동시 업그레이드), kubelet 검증의 controller 이동, Bottlerocket podsPerCore와 다중 clusterDNS 거부, 메트릭 label 변경
- Auto Mode: 구성 요소는 AWS가 업데이트, 사용자는 1.37 변경(SELinuxMount)과 NodePool 정책을 점검, 노드는 Drift로 교체

1.37로 올릴 때 self-managed의 순서는 Karpenter가 먼저입니다. 1.37을 지원하는 Karpenter는 1.15.x뿐이라서, 컨트롤 플레인을 먼저 올리면 지원 범위를 벗어난 상태가 됩니다. Helm으로 올릴 때는 CRD chart인 karpenter-crd와 controller chart를 같이 올리고, 버전 문자열은 v 없이 1.15.0입니다. v1.15.0이라고 쓰면 not found가 납니다.
{cue: demo}
두 번째 탭은 v1.15.0의 breaking change 네 가지입니다. Node Repair가 voluntary disruption이 되어 budget reason Unhealthy를 따르므로 CRD를 함께 올립니다. kubelet 검증이 controller로 옮겨져, 잘못된 값도 apply는 성공하고 EC2NodeClass가 NotReady가 됩니다. 무시되던 Bottlerocket 설정은 이제 거부되고, 메트릭 label이 바뀌어 대시보드 쿼리를 손봐야 합니다.
{cue: pause}
세 번째 탭 Auto Mode는 단계가 짧습니다. 관리형 구성 요소는 AWS가 업데이트하고, 사용자는 1.37의 SELinuxMount 기본 활성화를 확인합니다. 같은 볼륨을 다른 SELinux 라벨로 공유하는 Pod는 ContainerCreating에 머물 수 있습니다. 그리고 3부에서 본 Balanced 기본값을 반영할지 NodePool에 명시해 두고, 노드는 Drift로 교체되니 PDB가 막고 있지 않은지 봅니다.

[출처]
- https://karpenter.sh/docs/upgrading/upgrade-guide/#upgrading-to-1150, https://github.com/aws/karpenter-provider-aws/releases/tag/v1.15.0
- helm show chart oci://public.ecr.aws/karpenter/karpenter --version 1.15.0 (2026-10-20 실행)
- https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions-standard.html#kubernetes-1-37
{cue: transition}
업그레이드든 평소 운영이든, 무엇을 보고 있어야 이상을 알아챌 수 있을까요.
:::

---
<!-- Slide 3: 관측 포인트 -->
@type: content
@title: 무엇을 볼까: 이벤트와 메트릭

## 무엇을 볼까: 이벤트와 메트릭

:::html
<style>
.ak3-obs { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); margin-bottom: var(--space-3); }
.ak3-q { font-size: var(--fs-card); color: var(--text-secondary); margin-bottom: var(--space-2); word-break: keep-all; }
.ak3-sig { font-family: var(--font-mono); font-size: var(--fs-caption); color: var(--text-primary); word-break: break-all; margin-top: var(--space-1); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak3-obs">
  <div class="card fragment fade-up" data-fragment-index="1">
    <strong class="text-accent">얼마나 흔들렸나</strong>
    <div class="ak3-q">disruption이 Pod에 준 영향</div>
    <div class="ak3-sig">karpenter_pods_disrupted_total</div>
    <div class="ak3-sig">label: consolidation_policy, termination_mode</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="2">
    <strong class="text-accent">Balanced는 왜 승인했나</strong>
    <div class="ak3-q">점수와 실행된 이동</div>
    <div class="ak3-sig">karpenter_consolidation_score</div>
    <div class="ak3-sig">karpenter_consolidation_moves_total</div>
    <div class="ak3-sig">event: ConsolidationApproved</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="3">
    <strong class="text-accent">무엇이 막혔나</strong>
    <div class="ak3-q">budget 여유와 실패</div>
    <div class="ak3-sig">karpenter_nodepool_allowed_disruptions</div>
    <div class="ak3-sig">karpenter_voluntary_disruption_queue_failures_total</div>
    <div class="ak3-sig">karpenter_cloudprovider_errors_total</div>
  </div>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="4">
  <div class="callout callout-info"><strong class="text-info">Auto Mode는 kubectl부터</strong><div class="on-surface-muted">NodeClaim 상태와 event로 확인합니다. event source 이름은 <code>eks-auto-mode/compute</code></div></div>
  <div class="callout callout-warning"><strong class="text-warning">EC2 목록에서 기본 숨김</strong><div class="on-surface-muted">2026-04-22 이후 Auto Mode 인스턴스는 EC2 콘솔과 describe 목록에서 숨겨집니다. <code>include-managed-resources</code>로 조회</div></div>
</div>
:::

:::notes
{timing: 2min}
[요약]
- 영향: karpenter_pods_disrupted_total(v1.15 신규), consolidation_policy와 termination_mode label
- Balanced 판단: karpenter_consolidation_score, karpenter_consolidation_moves_total, ConsolidationApproved event
- 막힘: karpenter_nodepool_allowed_disruptions, voluntary_disruption_queue_failures_total, cloudprovider_errors_total (v1.15에서 label 변경)
- Auto Mode: kubectl의 NodeClaim과 event(eks-auto-mode/compute), 2026-04-22 이후 인스턴스는 EC2 목록에서 기본 숨김

관측은 세 가지 질문으로 나누면 쉽습니다. 첫째, disruption이 Pod를 얼마나 흔들었나. v1.15에서 karpenter_pods_disrupted_total이 추가되었고, consolidation_policy와 termination_mode label로 어떤 정책, 어떤 종료 방식에서 나온 것인지 나눠 볼 수 있습니다.
{cue: pause}
둘째, Balanced 정책이 왜 이 교체를 승인했나. karpenter_consolidation_score와 consolidation_moves_total 메트릭, 그리고 ConsolidationApproved event로 확인합니다. Balanced로 바꾼 뒤 "왜 노드가 안 줄어드냐"는 질문이 나오면 여기서 점수를 보시면 됩니다.
셋째, 무엇이 막혔나. NodePool별로 지금 허용되는 disruption 수, disruption queue 실패, cloud provider 오류를 봅니다. 앞에서 말씀드린 것처럼 v1.15에서 이 메트릭들의 label 값이 바뀌었으니 기존 쿼리를 확인하세요.
{cue: question}
Auto Mode에서는 어떨까요. 관리형 controller의 karpenter 메트릭을 사용자가 수집할 수 있는지는 오늘 확인한 공식 문서에서 찾지 못했습니다. 그래서 kubectl로 NodeClaim 상태와 event를 보는 것이 출발점이고, event source 이름은 eks-auto-mode/compute입니다. 한 가지 함정이 있습니다. 2026년 4월 22일 이후 만들어진 Auto Mode 인스턴스는 EC2 콘솔과 describe-instances 목록에서 기본으로 숨겨집니다. include-managed-resources 파라미터나 인스턴스 ID 직접 조회, EKS 콘솔로 보셔야 합니다.

[출처]
- https://karpenter.sh/docs/upgrading/upgrade-guide/#upgrading-to-1150, v1.15.0 릴리스 노트 (메트릭과 event)
- https://docs.aws.amazon.com/eks/latest/userguide/automode-learn-instances.html (2026-04-22 이후 관리형 리소스 기본 숨김)
- https://docs.aws.amazon.com/eks/latest/userguide/auto-change.html (2025-09-10, event source eks-auto-mode/compute)
{cue: transition}
운영의 마지막 축은 비용입니다.
:::

---
<!-- Slide 4: 비용 -->
@type: content
@title: 비용: 관리비는 할인되지 않는다

## 비용: 관리비는 할인되지 않는다

:::html
<style>
.ak3-cost { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); align-items: start; }
.ak3-calc { display: flex; flex-direction: column; gap: var(--space-2); }
.ak3-row { display: grid; grid-template-columns: 7rem 1fr; align-items: center; gap: var(--space-3); font-size: var(--fs-card); }
.ak3-row label { color: var(--text-secondary); }
.ak3-pick { display: flex; gap: var(--space-2); }
.ak3-pick .btn { color: var(--on-surface); }
.ak3-pick .btn.active { background: var(--accent-subtle); border-color: var(--accent); color: var(--accent); }
.ak3-calc .metric-value { font-size: var(--fs-subtitle); white-space: nowrap; }
.ak3-calc .slider-value { min-width: 4rem; }
.ak3-cap { font-size: var(--fs-caption); color: var(--text-secondary); word-break: keep-all; }
.ak3-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak3-cost">
  <div class="ak3-calc card">
    <div class="ak3-pick" id="ak3-pick">
      <button class="btn btn-sm active" data-t="m5">m5.large</button>
      <button class="btn btn-sm" data-t="m7g">m7g.large</button>
    </div>
    <div class="ak3-row"><label for="ak3-n">노드 수</label><div class="slider-container"><input type="range" id="ak3-n" min="1" max="150" value="20"><span class="slider-value" id="ak3-n-v">20</span></div></div>
    <div class="card-grid">
      <div class="metric-card"><div class="metric-value" id="ak3-fee">-</div><div class="metric-label">월 Auto Mode 관리비</div></div>
      <div class="metric-card"><div class="metric-value" id="ak3-od">-</div><div class="metric-label">월 On-Demand EC2</div></div>
    </div>
    <div class="ak3-cap" id="ak3-ratio"></div>
    <div class="ak3-cap">서울 리전 Price List API 단가, 월 730시간 가정의 계산 모델입니다.</div>
  </div>
  <div class="ak3-stack">
    <div class="callout callout-info fragment fade-left" data-fragment-index="1"><strong class="text-info">인스턴스 유형과 시간 기준</strong><div class="on-surface-muted">EC2 요금과 별도로 부과, 초 단위 과금, 최소 1분</div></div>
    <div class="callout callout-warning fragment fade-left" data-fragment-index="2"><strong class="text-warning">구매 옵션과 독립</strong><div class="on-surface-muted">Spot, RI, Savings Plans 할인이 관리비를 줄이지 않습니다. Spot일수록 비율이 커집니다.</div></div>
    <div class="callout callout-info fragment fade-left" data-fragment-index="3"><strong class="text-info">GPU 계열 인하 (2026-07-01)</strong><div class="on-surface-muted">G 계열 35%, P 계열과 Trainium 60% 인하. 조직 150노드 초과는 별도 문의</div></div>
  </div>
</div>
:::

:::script
(function () {
  var PRICE = { m5: [0.01416, 0.118], m7g: [0.01204, 0.1003] };
  var HOURS = 730;
  var pick = document.getElementById('ak3-pick');
  var n = document.getElementById('ak3-n');
  if (!pick || !n) return;
  var t = 'm5';
  function usd(x) { return '$' + x.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function update() {
    var k = parseInt(n.value, 10);
    var p = PRICE[t];
    var fee = k * HOURS * p[0];
    var od = k * HOURS * p[1];
    document.getElementById('ak3-n-v').textContent = k;
    document.getElementById('ak3-fee').textContent = usd(fee);
    document.getElementById('ak3-od').textContent = usd(od);
    document.getElementById('ak3-ratio').textContent = '관리비 $' + p[0] + '/h, On-Demand $' + p[1] + '/h, 비율 ' + (p[0] / p[1] * 100).toFixed(1) + '% (계산값, AWS 공식 표현 아님)';
    pick.querySelectorAll('.btn').forEach(function (b) { b.classList.toggle('active', b.getAttribute('data-t') === t); });
  }
  pick.addEventListener('click', function (e) { var b = e.target.closest('.btn'); if (b) { t = b.getAttribute('data-t'); update(); } });
  n.addEventListener('input', update);
  update();
})();
:::

:::notes
{timing: 1.5min}
[요약]
- Auto Mode 관리비는 EC2 요금과 별도, 관리하는 인스턴스의 유형과 시간 기준, 초 단위 과금(최소 1분)
- 구매 옵션과 독립: Spot, RI, Savings Plans 할인이 관리비를 줄이지 않음
- 서울 m5.large 관리비 $0.01416/h vs OD $0.118/h, m7g.large $0.01204/h vs $0.1003/h, 둘 다 OD의 약 12%(계산값)
- 2026-07-01 GPU 관리비 인하: G 35%, P와 Trainium 60%. 조직 150노드 초과는 별도 문의

Auto Mode의 비용 구조는 단순합니다. EC2 요금은 그대로 내고, Auto Mode가 관리하는 인스턴스마다 유형과 시간에 따라 관리비가 추가됩니다. 초 단위 과금이고 최소 1분입니다.
{cue: demo}
왼쪽 계산기로 보겠습니다. 서울 리전 m5.large 20대를 한 달 730시간 돌리면 관리비가 이 정도이고, On-Demand EC2 요금은 이 정도입니다. 아래 줄의 비율을 보시면 약 12%입니다. m7g.large로 바꿔도 비율은 비슷합니다. 다만 이 12%는 AWS가 공시한 퍼센트가 아니라, Price List API의 두 단가를 나눠 제가 계산한 값입니다. AWS는 인스턴스 유형별 단가로만 공시합니다.
{cue: pause}
중요한 것은 오른쪽 노란 박스입니다. 관리비는 EC2 구매 옵션과 독립입니다. Spot이나 Savings Plans로 EC2 비용을 줄여도 관리비는 그대로이니, Spot 비중이 높을수록 EC2 비용 대비 관리비 비율이 커집니다. self-managed는 이 관리비가 없는 대신 Karpenter controller를 돌릴 노드 비용과, 무엇보다 운영 인력의 시간이 듭니다.
GPU는 7월 1일부터 관리비가 G 계열 35%, P 계열과 Trainium 60% 인하되었습니다. 조직 전체로 150노드를 넘으면 별도 가격 문의 안내가 있습니다.

[출처]
- https://aws.amazon.com/eks/pricing/
- aws pricing get-products --service-code AmazonEKS, AmazonEC2 (regionCode ap-northeast-2, 2026-10-20 조회)
- https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-eks-auto-mode-gpu-price/
{cue: transition}
비용까지 봤으니, 이제 어느 쪽을 고를지 체크리스트로 정리하겠습니다.
:::

---
<!-- Slide 5: 선택 체크리스트 -->
@type: content
@title: Auto Mode인가, 직접 운영인가

## Auto Mode인가, 직접 운영인가

:::html
<style>
.ak3-dec { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); align-items: start; }
.ak3-dec h4 { margin: 0 0 var(--space-2); font-size: var(--fs-body); }
.ak3-dec .checklist { font-size: var(--fs-card); word-break: keep-all; }
.ak3-tally { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3); margin-top: var(--space-3); }
.ak3-tally .metric-value { font-size: var(--fs-subtitle); }
.ak3-verdict { margin-top: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak3-dec" id="ak3-dec">
  <div>
    <h4 class="text-accent">직접 운영 쪽 신호</h4>
    <ul class="checklist">
      <li data-side="self"><span class="check"></span><span class="checklist-text">custom AMI, userData, launch template, SSH나 SSM 접속이 필요</span></li>
      <li data-side="self"><span class="check"></span><span class="checklist-text">kubelet, sysctl 요구가 <code>advancedCompute</code> 지원 필드를 벗어남</span></li>
      <li data-side="self"><span class="check"></span><span class="checklist-text">Windows 노드, DRA, 대체 CNI 필요 (Security Groups per Pod는 podSecurityGroupSelectorTerms로 대체)</span></li>
      <li data-side="self"><span class="check"></span><span class="checklist-text">feature gate 기능이나 FIS EC2 장애 주입 테스트가 필요</span></li>
    </ul>
  </div>
  <div>
    <h4 class="text-accent">Auto Mode 쪽 신호</h4>
    <ul class="checklist">
      <li data-side="auto"><span class="check"></span><span class="checklist-text">Karpenter minor마다 CRD와 breaking change를 따라갈 인력이 부족</span></li>
      <li data-side="auto"><span class="check"></span><span class="checklist-text">CNI, CoreDNS, EBS CSI, LB controller 운영을 줄이고 싶음</span></li>
      <li data-side="auto"><span class="check"></span><span class="checklist-text">주간 AMI 교체와 21일 수명 상한을 보안 기준으로 받아들일 수 있음</span></li>
      <li data-side="auto"><span class="check"></span><span class="checklist-text">인스턴스당 관리비가 운영 시간 절감보다 작다고 판단</span></li>
    </ul>
  </div>
</div>
<div class="ak3-tally">
  <div class="metric-card"><div class="metric-value" id="ak3-self">0</div><div class="metric-label">직접 운영 신호</div></div>
  <div class="metric-card"><div class="metric-value" id="ak3-auto">0</div><div class="metric-label">Auto Mode 신호</div></div>
</div>
<div class="callout callout-info ak3-verdict fragment fade-up" data-fragment-index="1"><strong class="text-info">왼쪽이 하나라도 필수라면</strong>: 그 워크로드는 self-managed가 맞습니다. 클러스터를 나누거나, 마이그레이션 중에만 NodePool로 분리해 공존합니다.</div>
:::

:::script
(function () {
  var root = document.getElementById('ak3-dec');
  if (!root) return;
  function count() {
    document.getElementById('ak3-self').textContent = root.querySelectorAll('li.checked[data-side="self"]').length;
    document.getElementById('ak3-auto').textContent = root.querySelectorAll('li.checked[data-side="auto"]').length;
  }
  root.addEventListener('click', function (e) {
    if (e.target.closest('.checklist li')) setTimeout(count, 0);
  });
  count();
})();
:::

:::notes
{timing: 2min}
[요약]
- 직접 운영 신호: custom AMI, userData, SSH/SSM, advancedCompute 범위를 넘는 kubelet과 sysctl, Windows, DRA, 대체 CNI, SG per Pod, feature gate, FIS EC2 action
- Auto Mode 신호: Karpenter minor 추적 인력 부족(v1.15는 LTS 아님), 관리형 CNI, CoreDNS, EBS CSI, LBC 선호, 주간 AMI와 21일 상한 수용, 관리비 대비 운영 절감
- 왼쪽 항목이 하나라도 필수면 그 워크로드는 self-managed. AWS는 한 클러스터에서 한쪽을 권장
- 다음은 데모 영상 4편

마지막으로 선택 기준입니다. 항목을 클릭하면 체크되고 아래에 개수가 올라갑니다. 우리 조직 상황에 맞춰 같이 눌러 보겠습니다.
{cue: demo}
왼쪽은 직접 운영해야 하는 신호입니다. custom AMI, userData, launch template, SSH나 SSM 접속이 필요하거나, kubelet과 sysctl 요구가 advancedCompute 목록을 벗어나면 직접 운영입니다. Windows 노드, DRA, Cilium 같은 대체 CNI도 지원하지 않고, Security Groups per Pod 대신 NodeClass의 podSecurityGroupSelectorTerms를 씁니다. feature gate나 FIS EC2 장애 주입이 필요해도 직접 운영입니다.
{cue: pause}
오른쪽은 Auto Mode 쪽 신호입니다. 2부 버전 지도에서 본 것처럼 1.37은 LTS가 아닌 Karpenter 1.15.x가 필요하니, minor마다 따라갈 인력이 부족하면 이 부담을 AWS에 넘기는 것이 합리적입니다. 애드온 운영을 줄이고 싶을 때, 주간 AMI 교체와 21일 수명 상한을 보안 기준으로 받아들일 수 있을 때, 관리비가 운영 시간 절감보다 작을 때도 Auto Mode 쪽입니다.
{cue: question}
결론은 간단합니다. 왼쪽 항목 중 하나라도 반드시 필요하다면 그 워크로드는 self-managed가 맞습니다. 이때도 한 클러스터 안에 둘을 오래 섞기보다 클러스터를 나누고, 마이그레이션 중에만 NodePool로 분리해 공존하는 것이 AWS 권장입니다.

[출처]
- https://docs.aws.amazon.com/eks/latest/userguide/create-node-class.html (advancedCompute 필드)
- https://docs.aws.amazon.com/eks/latest/userguide/auto-networking.html (미지원 네트워킹 기능)
- https://docs.aws.amazon.com/eks/latest/userguide/automode-learn-instances.html (FIS 미지원, 공존 시 NodePool 분리)
{cue: transition}
지금까지 이론으로 본 프로비저닝, consolidation, Drift, Spot 중단을 이제 데모 영상으로 직접 확인해 보겠습니다. 영상은 네 편이고, 각 영상 앞에서 무엇을 보면 되는지 짚고 넘어가겠습니다.
:::
