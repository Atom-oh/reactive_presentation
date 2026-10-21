---
remarp: true
block: 02-ontology
---

---
<!-- Slide 1: 2부 구분 -->
@type: section

# 온톨로지, 쉽게 이해하기

개념, 관계, 어휘, 규칙. 그리고 직접 돌려 본 데모

:::script
(function () {
  // Hover (or focus) glossary: elements with data-tip show a one-line explanation near the term.
  if (window.__rpTips) return;
  window.__rpTips = true;
  var css = document.createElement('style');
  css.textContent =
    '.rp-tip { border-bottom: 2px dotted var(--accent); cursor: help; }' +
    '.rp-tipbox { position: fixed; z-index: 100001; max-width: min(38vw, 720px); padding: .6em .9em; border-radius: 8px;' +
    ' background: var(--text-primary); color: var(--bg-primary); font-size: clamp(14px, 1.75vh, 38px); line-height: 1.45;' +
    ' box-shadow: 0 6px 24px color-mix(in srgb, black 35%, transparent); pointer-events: none; opacity: 0; transition: opacity .12s; word-break: keep-all; }' +
    '.rp-tipbox.on { opacity: 1; }';
  document.head.appendChild(css);
  var box = document.createElement('div');
  box.className = 'rp-tipbox';
  box.setAttribute('role', 'tooltip');
  function show(t) {
    box.textContent = t.getAttribute('data-tip');
    box.classList.add('on');
    var r = t.getBoundingClientRect(), b = box.getBoundingClientRect();
    var x = Math.min(Math.max(8, r.left + r.width / 2 - b.width / 2), window.innerWidth - b.width - 8);
    var y = r.top - b.height - 10;
    if (y < 8) y = r.bottom + 10;
    box.style.left = x + 'px'; box.style.top = y + 'px';
  }
  function hide() { box.classList.remove('on'); }
  function mount() {
    document.body.appendChild(box);
    document.addEventListener('mouseover', function (e) { var t = e.target.closest && e.target.closest('.slide [data-tip]'); if (t) show(t); });
    document.addEventListener('mouseout', function (e) { if (e.target.closest && e.target.closest('.slide [data-tip]')) hide(); });
    document.addEventListener('focusin', function (e) { var t = e.target.closest && e.target.closest('.slide [data-tip]'); if (t) show(t); });
    document.addEventListener('focusout', hide);
    window.addEventListener('hashchange', hide);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
})();
:::

:::notes
{timing: 0.5min}
[요약]
- 2부의 질문: 사례마다 나오는 온톨로지는 무엇이고, 에이전트에서 어디에 쓰이는가
- 표준 문법이나 수식 대신 은행 예시와 데모로 설명
- 마지막에 같은 모델로 정답률이 어떻게 달라지는지 직접 측정한 결과

2부는 온톨로지입니다. 신한카드도 미래에셋증권도 온톨로지를 썼다고 하는데, 말이 어렵다 보니 "그래프 DB를 깔아야 하나", "표준을 공부해야 하나" 하고 멈추시는 경우가 많습니다.
오늘은 표준 문법보다 은행 예시와 데모로 풀겠습니다. 끝나면 "우리 과제에서 무엇부터 정리하면 되는지"가 보이도록 구성했습니다.
{cue: transition}
먼저 문제부터 보겠습니다.
:::

---
<!-- Slide 2: 왜 틀리는가 -->
@type: content
@title: LLM은 왜 우리 데이터 앞에서 틀릴까

## LLM은 왜 우리 데이터 앞에서 틀릴까

사람이 쓰는 말과 시스템에 저장된 값 사이의 세 가지 간극

:::html
<style>
.rp-gap-top { display: grid; grid-template-columns: 1fr auto 1fr; gap: var(--space-3); align-items: center; margin-bottom: var(--space-4); }
.rp-bubble { border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-3); background: var(--bg-card); font-size: var(--fs-body); word-break: keep-all; }
.rp-bubble small { display: block; font-size: var(--fs-caption); color: var(--on-surface-muted); margin-bottom: var(--space-1); }
.rp-db { font-family: var(--font-mono, monospace); font-size: var(--fs-card); }
.rp-qmark { font-size: 2.4rem; color: var(--danger); font-weight: var(--weight-bold); }
.rp-gaps { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); }
.rp-gaps .card { word-break: keep-all; }
.rp-gaps code { font-size: var(--fs-caption); }
</style>
<div class="rp-gap-top">
  <div class="rp-bubble"><small>고객 (또는 직원)의 질문</small>"<b>미국국채</b> ETF 중에 <b>보수</b>가 제일 싼 거 뭐예요?"</div>
  <div class="rp-qmark">?</div>
  <div class="rp-bubble rp-db"><small>상품 원장에 실제로 저장된 값</small>ast_cls = 'BD_OVS_GOV'<br>rgn_cd = 'US'<br>fee_bp = 5</div>
</div>
<div class="rp-gaps fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="card"><div class="card-title">말의 간극</div><div class="card-desc">"미국국채", "미국채", "US Treasury"는 같은 것. DB에는 <code>BD_OVS_GOV</code> 하나뿐입니다.</div></div>
  <div class="card"><div class="card-title">관계의 간극</div><div class="card-desc">미국국채는 해외국채이고, 해외국채는 채권입니다. 이 계층은 테이블 어디에도 적혀 있지 않습니다.</div></div>
  <div class="card"><div class="card-title">상식의 간극</div><div class="card-desc">"보수"는 <code>fee_bp</code>이고 단위는 bp(0.01%p). 담당자는 알지만 DB는 말해 주지 않습니다.</div></div>
</div>
:::

:::notes
{timing: 1.5min}
[요약]
- LLM이 SQL 문법을 몰라서 틀리는 경우는 드묾. 사람의 말과 저장된 값이 달라서 틀림
- 말의 간극: 동의어와 별칭 / 관계의 간극: 상위, 하위 분류 / 상식의 간극: 단위와 업무 규칙
- 온톨로지는 이 세 간극을 메우는 약속

이 질문을 받았다고 해 보겠습니다. "미국국채 ETF 중에 보수가 제일 싼 거 뭐예요?" 그런데 상품 원장에는 미국국채라는 글자가 없습니다. 자산분류 코드 BD_OVS_GOV와 지역 코드 US가 있을 뿐입니다.
LLM이 SQL 문법을 몰라서 틀리는 경우는 거의 없습니다. 틀리는 이유는 세 가지 간극입니다.
{cue: pause}
첫째, 말의 간극. 미국국채, 미국채, US Treasury가 같은 것인데 DB에는 코드 하나뿐입니다. 둘째, 관계의 간극. 미국국채는 해외국채의 한 종류이고 해외국채는 채권인데, 이 계층은 테이블 어디에도 없습니다. 셋째, 상식의 간극. 보수는 fee_bp 컬럼이고 단위가 bp라는 건 담당자 머릿속에만 있습니다.
온톨로지는 이 세 간극을 메우기 위해 "우리 조직에서 이 말은 이 뜻이고, 이렇게 연결된다"를 정리해 둔 약속입니다.
{cue: transition}
그 약속이 무엇으로 이루어지는지 보겠습니다.
:::

---
<!-- Slide 3: 온톨로지의 세 재료 -->
@type: content
@title: 온톨로지 = 개념, 관계, 규칙의 약속

## 온톨로지 = 개념, 관계, 규칙의 약속

탭을 눌러 은행 예시로 확인

:::html
<style>
.rp-onto3 .tab-bar { margin-bottom: var(--space-3); }
.rp-onto3 .tab-content { display: none; }
.rp-onto3 .tab-content.active { display: block; }
.rp-onto3-grid { display: grid; grid-template-columns: 1fr 1.2fr; gap: var(--space-4); align-items: start; }
.rp-onto3-grid .card { word-break: keep-all; }
.rp-ex { display: flex; flex-wrap: wrap; gap: var(--space-2); }
.rp-chip { border: 1px solid var(--border); border-radius: 999px; padding: var(--space-1) var(--space-3); font-size: var(--fs-card); background: var(--bg-card); }
.rp-chip.cls { border-color: var(--accent); color: var(--accent); font-weight: var(--weight-semibold); }
.rp-arrowline { font-size: var(--fs-card); line-height: 2; }
.rp-arrowline b { color: var(--accent); }
.rp-analogy { font-size: var(--fs-caption); color: var(--on-surface-muted); margin-top: var(--space-2); }
</style>
<div class="rp-onto3">
  <div class="tab-bar">
    <button class="tab-btn active" data-tab="o1">개념 (Class)</button>
    <button class="tab-btn" data-tab="o2">관계 (Property)</button>
    <button class="tab-btn" data-tab="o3">규칙 (Axiom, Rule)</button>
  </div>
  <div class="tab-content active" data-tab="o1">
    <div class="rp-onto3-grid">
      <div class="card"><div class="card-title">무엇이 있는가</div><div class="card-desc">업무에 등장하는 "종류"를 정합니다. 종류(클래스)와 그 종류에 속하는 실제 하나하나(인스턴스)를 구분합니다.</div><div class="rp-analogy">비유: 사전의 표제어</div></div>
      <div>
        <div class="rp-ex"><span class="rp-chip cls">고객</span><span class="rp-chip cls">계좌</span><span class="rp-chip cls">상품</span><span class="rp-chip cls">자산분류</span><span class="rp-chip cls">운용사</span></div>
        <div class="rp-arrowline">클래스 <b>고객</b>의 인스턴스: 홍길동, 김민지 ...<br>클래스 <b>상품</b>의 인스턴스: SKY 미국채10년, RIVER 코스피200 ...</div>
      </div>
    </div>
  </div>
  <div class="tab-content" data-tab="o2">
    <div class="rp-onto3-grid">
      <div class="card"><div class="card-title">어떻게 이어지는가</div><div class="card-desc">개념과 개념 사이에 이름 붙은 연결을 정합니다. 방향이 있고, 어떤 종류끼리 이어지는지도 정합니다.</div><div class="rp-analogy">비유: 지도의 길</div></div>
      <div class="rp-arrowline">고객 <b>보유</b> 계좌<br>계좌 <b>편입</b> 상품<br>상품 <b>자산분류</b> 자산분류<br>상품 <b>브랜드</b> 브랜드, 브랜드 <b>운용사</b> 운용사</div>
    </div>
  </div>
  <div class="tab-content" data-tab="o3">
    <div class="rp-onto3-grid">
      <div class="card"><div class="card-title">무엇은 반드시 지켜지는가</div><div class="card-desc">항상 참이어야 하는 제약과 업무 규칙입니다. 모델이 추측하지 않도록 시스템이 강제할 수 있습니다.</div><div class="rp-analogy">비유: 규정집</div></div>
      <div class="rp-arrowline"><b>상위, 하위</b>: 미국국채는 해외국채이고, 해외국채는 채권이다<br><b>단일값</b>: 상품의 자산분류는 하나뿐이다<br><b>상호배타</b>: 주식이면서 채권일 수는 없다<br><b>업무 규칙</b>: "배당"은 분배율로 비교한다</div>
    </div>
  </div>
</div>
:::

:::notes
{timing: 1.5min}
[요약]
- 개념(클래스): 업무에 나오는 종류. 클래스와 인스턴스를 구분 (사전의 표제어)
- 관계(프로퍼티): 개념 사이의 이름 붙은 연결, 방향이 있음 (지도의 길)
- 규칙: 상위, 하위, 단일값, 상호배타, 업무 규칙 (규정집)
- 미래에셋증권은 자본시장법 §229의 집합투자기구 유형을 닫힌 목록으로 만들고, 단일값과 상호배타 제약을 넣음

온톨로지는 세 가지 재료로 만듭니다. 탭을 하나씩 눌러 보겠습니다.
첫째는 개념입니다. 고객, 계좌, 상품처럼 업무에 등장하는 종류를 정합니다. 여기서 중요한 구분이 클래스와 인스턴스입니다. 고객은 클래스이고, 홍길동 고객은 그 클래스의 인스턴스입니다.
{cue: click}
둘째는 관계입니다. 고객이 계좌를 보유하고, 계좌에 상품이 편입되고, 상품은 자산분류를 가집니다. 방향과 이름이 있는 연결이라는 점이 핵심입니다.
{cue: click}
셋째는 규칙입니다. 미국국채는 해외국채이고 해외국채는 채권이라는 계층, 상품의 자산분류는 하나뿐이라는 단일값, 주식이면서 채권일 수 없다는 상호배타 같은 것들입니다. 미래에셋증권은 자본시장법에 나오는 집합투자기구 유형을 닫힌 목록으로 만들고 이런 제약을 넣었습니다.
{cue: transition}
이 재료들을 실제로 담는 형식이 트리플입니다.
:::

---
<!-- Slide 4: 트리플 -->
@type: content
@title: 모든 지식을 세 단어 문장으로

## 모든 지식을 세 단어 문장으로

주어, 관계, 목적어(트리플)를 하나씩 쌓으면 지식 그래프

:::html
<style>
.rp-tri { display: grid; grid-template-columns: 1fr 300px; gap: var(--space-3); align-items: stretch; }
.rp-tri svg { width: 100%; height: auto; display: block; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md); }
.rp-tri .node rect { fill: var(--bg-primary); stroke: var(--border); stroke-width: 2; }
.rp-tri .node.inst rect { stroke: var(--accent); }
.rp-tri .node.cls rect { stroke: var(--on-surface-muted); stroke-dasharray: 6 4; }
.rp-tri .node text { fill: var(--text-primary); font-size: 19px; font-weight: 600; text-anchor: middle; dominant-baseline: central; }
.rp-tri .edge { opacity: 0; transition: opacity .35s; }
.rp-tri .edge.on { opacity: 1; }
.rp-tri .edge line { stroke: var(--on-surface-muted); stroke-width: 2.5; marker-end: url(#rpArrow); }
.rp-tri .edge text { fill: var(--on-surface-muted); font-size: 16px; text-anchor: middle; }
.rp-tri .edge.path line { stroke: var(--accent); stroke-width: 4; }
.rp-tri .edge.path text { fill: var(--accent); font-weight: 700; }
.rp-tri #rpArrow path { fill: var(--on-surface-muted); }
.rp-tri .edge text { paint-order: stroke; stroke: var(--bg-card); stroke-width: 6px; }
.rp-tri-side { display: flex; flex-direction: column; gap: var(--space-2); }
.rp-tri-side .btn { width: 100%; }
.rp-tri-now { border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-2) var(--space-3); font-size: var(--fs-card); min-height: 4.2em; word-break: keep-all; background: var(--bg-card); }
.rp-tri-now b { color: var(--accent); }
.rp-legend { font-size: var(--fs-caption); color: var(--on-surface-muted); line-height: 1.6; }
</style>
<div class="rp-tri">
  <svg id="rpTriSvg" viewBox="0 0 1100 440" role="img" aria-label="고객, 계좌, 상품, 자산분류가 트리플로 이어진 지식 그래프">
    <defs><marker id="rpArrow" viewBox="0 0 10 10" refX="10" refY="5" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="14" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z"/></marker></defs>
    <g class="edge" data-e="1"><line x1="140" y1="260" x2="222" y2="260"/><text x="181" y="244">보유</text></g>
    <g class="edge" data-e="2"><line x1="290" y1="235" x2="290" y2="137"/><text x="322" y="192">유형</text></g>
    <g class="edge" data-e="3"><line x1="360" y1="110" x2="480" y2="110"/><text x="420" y="94">하위분류</text></g>
    <g class="edge" data-e="4"><line x1="360" y1="260" x2="448" y2="260"/><text x="404" y="244">편입</text></g>
    <g class="edge" data-e="5"><line x1="650" y1="260" x2="738" y2="260"/><text x="694" y="244">자산분류</text></g>
    <g class="edge" data-e="6"><line x1="880" y1="260" x2="948" y2="260"/><text x="914" y="244">상위</text></g>
    <g class="edge" data-e="7"><line x1="1015" y1="285" x2="1015" y2="363"/><text x="1050" y="330">상위</text></g>
    <g class="node inst"><rect x="10" y="235" width="130" height="50" rx="10"/><text x="75" y="260">홍길동 고객</text></g>
    <g class="node inst"><rect x="222" y="235" width="138" height="50" rx="10"/><text x="291" y="260">ISA-001</text></g>
    <g class="node cls"><rect x="222" y="85" width="138" height="50" rx="10"/><text x="291" y="110">ISA 계좌</text></g>
    <g class="node cls"><rect x="480" y="85" width="140" height="50" rx="10"/><text x="550" y="110">절세계좌</text></g>
    <g class="node inst"><rect x="450" y="235" width="200" height="50" rx="10"/><text x="550" y="260">SKY 미국채10년</text></g>
    <g class="node cls"><rect x="740" y="235" width="140" height="50" rx="10"/><text x="810" y="260">미국국채</text></g>
    <g class="node cls"><rect x="950" y="235" width="130" height="50" rx="10"/><text x="1015" y="260">해외국채</text></g>
    <g class="node cls"><rect x="950" y="365" width="130" height="50" rx="10"/><text x="1015" y="390">채권</text></g>
  </svg>
  <div class="rp-tri-side">
    <button class="btn" id="rpTriNext" type="button">트리플 하나 추가</button>
    <button class="btn" id="rpTriAsk" type="button">질문 따라가기</button>
    <button class="btn btn-sm" id="rpTriReset" type="button">처음으로</button>
    <div class="rp-tri-now" id="rpTriNow">버튼을 눌러 트리플을 하나씩 쌓아 보세요.</div>
    <div class="rp-legend">실선 테두리: 인스턴스(실제 하나)<br>점선 테두리: 클래스(개념, 종류)<br>모든 이름과 계좌는 가상 예시</div>
  </div>
</div>
:::

:::script
(function () {
  var svg = document.getElementById('rpTriSvg');
  if (!svg) return;
  var T = [
    ['홍길동 고객', '보유', 'ISA-001'],
    ['ISA-001', '유형', 'ISA 계좌'],
    ['ISA 계좌', '하위분류', '절세계좌'],
    ['ISA-001', '편입', 'SKY 미국채10년'],
    ['SKY 미국채10년', '자산분류', '미국국채'],
    ['미국국채', '상위', '해외국채'],
    ['해외국채', '상위', '채권']
  ];
  var n = 0, now = document.getElementById('rpTriNow');
  function edge(i) { return svg.querySelector('.edge[data-e="' + i + '"]'); }
  document.getElementById('rpTriNext').addEventListener('click', function () {
    if (n >= T.length) { now.innerHTML = '트리플 7개로 작은 지식 그래프가 완성됐습니다. 이제 질문을 따라가 보세요.'; return; }
    n++; edge(n).classList.add('on');
    var t = T[n - 1];
    now.innerHTML = '(' + t[0] + ') <b>' + t[1] + '</b> (' + t[2] + ')<br><small>트리플 ' + n + ' / ' + T.length + '</small>';
  });
  document.getElementById('rpTriAsk').addEventListener('click', function () {
    for (var i = 1; i <= T.length; i++) edge(i).classList.add('on');
    n = T.length;
    [1, 4, 5, 6, 7].forEach(function (i) { edge(i).classList.add('path'); });
    now.innerHTML = '질문: "홍길동 고객 계좌에 <b>채권</b> 상품이 있나요?"<br>보유, 편입, 자산분류, 상위, 상위: 5개 관계를 따라가면 "예"';
  });
  document.getElementById('rpTriReset').addEventListener('click', function () {
    n = 0;
    svg.querySelectorAll('.edge').forEach(function (e) { e.classList.remove('on', 'path'); });
    now.innerHTML = '버튼을 눌러 트리플을 하나씩 쌓아 보세요.';
  });
})();
:::

:::notes
{timing: 1.5min}
[요약]
- 트리플: (주어) 관계 (목적어). 세 단어 문장 하나가 지식 한 조각
- 트리플을 쌓으면 점(개체)과 선(관계)으로 된 지식 그래프가 됨
- 질문 하나를 여러 관계를 따라가며(multi-hop) 답할 수 있음. 표에서는 조인 여러 번
- 저장 형식: RDF(표준 트리플), 속성 그래프(Property Graph). Amazon Neptune은 둘 다 지원

온톨로지와 지식 그래프의 기본 단위는 트리플입니다. "홍길동 고객이 ISA-001 계좌를 보유한다"처럼 주어, 관계, 목적어 세 단어로 된 문장입니다.
"트리플 하나 추가" 버튼을 눌러 보겠습니다. 고객이 계좌를 보유하고, 그 계좌는 ISA 계좌라는 유형이고, ISA 계좌는 절세계좌의 하위분류입니다.
{cue: click}
계속 누르면 계좌에 SKY 미국채10년이 편입되고, 그 상품의 자산분류는 미국국채이고, 미국국채의 상위는 해외국채, 그 상위는 채권입니다. 점선 테두리는 개념, 실선 테두리는 실제 하나하나입니다.
{cue: pause}
이제 "질문 따라가기"를 누르면, "홍길동 고객 계좌에 채권 상품이 있나요?"라는 질문을 관계 다섯 개를 따라가서 답합니다. 표로 하면 조인을 여러 번 해야 하는 질문이 그래프에서는 길을 따라가는 일이 됩니다. 이걸 multi-hop이라고 부릅니다.
저장 형식은 W3C 표준인 RDF와, 표준 대신 업계에서 널리 쓰는 속성 그래프 두 가지가 있고, Amazon Neptune은 둘 다 지원합니다.
{cue: transition}
마지막 두 칸, 상위 관계가 왜 중요한지 보겠습니다.
:::

---
<!-- Slide 5: 계층과 추론 -->
@type: content
@title: 계층이 있으면 "채권"이 저절로 풀린다

## 계층이 있으면 "채권"이 저절로 풀린다

개념을 누르면 하위 개념과 해당 상품까지 함께 포함

:::html
<style>
.rp-tg { display: flex; flex-direction: column; gap: var(--space-2); }
.rp-tg-head { display: flex; align-items: baseline; gap: var(--space-3); flex-wrap: wrap; word-break: keep-all; }
.rp-tg-head b { font-size: var(--fs-subtitle); color: var(--accent); }
.rp-tg-head span { font-size: var(--fs-card); color: var(--on-surface-muted); }
.rp-tg svg { width: 100%; height: 600px; display: block; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md); }
.rp-tg .ce { stroke: var(--border); stroke-width: 2; fill: none; transition: stroke .3s, stroke-width .3s; }
.rp-tg .ce.on { stroke: var(--accent); stroke-width: 3.5; }
.rp-tg .pe { stroke: var(--accent); stroke-width: 2; fill: none; opacity: 0; transition: opacity .35s; }
.rp-tg .pe.on { opacity: .85; }
.rp-tg .cn { cursor: pointer; }
.rp-tg .cn rect { fill: var(--bg-primary); stroke: var(--on-surface-muted); stroke-width: 2; stroke-dasharray: 6 4; transition: fill .3s, stroke .3s; }
.rp-tg .cn text { fill: var(--text-primary); font-size: 22px; font-weight: 700; text-anchor: middle; dominant-baseline: central; pointer-events: none; }
.rp-tg .cn:hover rect { stroke: var(--accent); }
.rp-tg .cn.inc rect { stroke: var(--accent); fill: var(--accent-subtle); }
.rp-tg .cn.sel rect { stroke: var(--accent); stroke-dasharray: none; stroke-width: 3; fill: var(--accent-subtle); }
.rp-tg .pn rect { fill: var(--bg-primary); stroke: var(--border); stroke-width: 1.5; transition: stroke .3s, fill .3s; }
.rp-tg .pn text { fill: var(--on-surface-muted); font-size: 20px; dominant-baseline: central; transition: fill .3s; }
.rp-tg .pn.on rect { stroke: var(--accent); fill: var(--accent-subtle); }
.rp-tg .pn.on text { fill: var(--text-primary); font-weight: 700; }
.rp-tg-note { font-size: var(--fs-caption); color: var(--on-surface-muted); word-break: keep-all; }
</style>
<div class="rp-tg" id="rpTg">
  <div class="rp-tg-head"><b id="rpTgTitle">개념 노드를 눌러 보세요</b><span id="rpTgDesc">예: "채권 ETF 보여줘". DB에 "채권"이라는 값은 없지만 계층을 따라가면 상품까지 이어집니다.</span></div>
  <svg id="rpTgSvg" viewBox="0 0 1560 600" role="img" aria-label="자산분류 개념 계층과 가상 ETF 상품을 잇는 그래프. 개념을 누르면 하위 개념과 상품이 강조됩니다"></svg>
  <div class="rp-tg-note">점선 테두리: 개념(클래스), 실선: 상품(인스턴스). 데모용 가상 ETF 22개 중 이 계층에 연결된 20개만 표시</div>
</div>
:::

:::script
(function () {
  var svg = document.getElementById('rpTgSvg');
  if (!svg) return;
  var NS = 'http://www.w3.org/2000/svg';
  var K = {
    '자산분류': { c: ['주식', '채권', '원자재'] }, '주식': { c: ['국내주식', '해외주식'] }, '채권': { c: ['국고채', '해외국채'] },
    '원자재': { c: ['금'] }, '해외주식': { c: ['미국주식'], e: ['PINE 글로벌리튬'] }, '해외국채': { c: ['미국국채'] },
    '국내주식': { e: ['SKY 코스피200', 'RIVER 코스피200', 'STONE 코스닥150', 'SKY 2차전지산업', 'RIVER K배터리소재', 'RIVER 고배당주', 'STONE K반도체'] },
    '미국주식': { e: ['SKY 미국S&P500', 'STONE 미국나스닥100', 'PINE 미국배당다우존스', 'SKY 필라델피아반도체', 'SKY 커버드콜월배당'] },
    '국고채': { e: ['SKY 국고채10년', 'RIVER 국고채3년'] },
    '미국국채': { e: ['SKY 미국채10년', 'RIVER 미국채30년액티브', 'STONE 미국단기채'] },
    '금': { e: ['PINE 금현물', 'RIVER 골드선물'] }
  };
  var DX = [95, 345, 600, 855], CW = 160, CH = 46, PX = 1110, PW = 430, PH = 26;
  var pos = {}, prodY = {}, order = [], row = 0, top = 18, step = 29.6;
  // Depth-first order: a concept's own products come right after it, then its children.
  (function place(n, d) {
    var ys = [];
    (K[n].e || []).forEach(function (p) { prodY[p] = top + row * step; order.push([p, n]); ys.push(prodY[p]); row++; });
    (K[n].c || []).forEach(function (c) { ys.push(place(c, d + 1)); });
    pos[n] = { x: DX[d], y: ys.reduce(function (a, b) { return a + b; }, 0) / ys.length };
    return pos[n].y;
  })('자산분류', 0);
  function el(tag, attrs, parent) { var e = document.createElementNS(NS, tag); for (var k in attrs) e.setAttribute(k, attrs[k]); (parent || svg).appendChild(e); return e; }
  function curve(x1, y1, x2, y2) { var m = (x1 + x2) / 2; return 'M' + x1 + ',' + y1 + ' C' + m + ',' + y1 + ' ' + m + ',' + y2 + ' ' + x2 + ',' + y2; }
  var gE = el('g', {}), gP = el('g', {}), gN = el('g', {});
  var cEdge = {}, pEdge = {}, cNode = {}, pNode = {};
  Object.keys(K).forEach(function (n) {
    (K[n].c || []).forEach(function (c) {
      cEdge[c] = el('path', { class: 'ce', d: curve(pos[n].x + CW / 2, pos[n].y, pos[c].x - CW / 2, pos[c].y) }, gE);
    });
  });
  order.forEach(function (o) {
    var p = o[0], n = o[1], y = prodY[p];
    pEdge[p] = el('path', { class: 'pe', d: curve(pos[n].x + CW / 2, pos[n].y, PX, y) }, gP);
    var g = el('g', { class: 'pn' }, gN);
    el('rect', { x: PX, y: y - PH / 2, width: PW, height: PH, rx: 6 }, g);
    el('text', { x: PX + 12, y: y }, g).textContent = p;
    pNode[p] = g;
  });
  Object.keys(pos).forEach(function (n) {
    var g = el('g', { class: 'cn', tabindex: '0', role: 'button', 'aria-label': n }, gN);
    el('rect', { x: pos[n].x - CW / 2, y: pos[n].y - CH / 2, width: CW, height: CH, rx: 10 }, g);
    el('text', { x: pos[n].x, y: pos[n].y }, g).textContent = n;
    cNode[n] = g;
    g.addEventListener('click', function () { select(n); });
    g.addEventListener('keydown', function (ev) { if (ev.key === 'Enter') { ev.stopPropagation(); select(n); } });
  });
  function walk(n, acc) { acc.nodes.push(n); (K[n].e || []).forEach(function (x) { acc.etf.push(x); }); (K[n].c || []).forEach(function (c) { walk(c, acc); }); return acc; }
  function select(n) {
    var r = walk(n, { nodes: [], etf: [] });
    Object.keys(cNode).forEach(function (k) { cNode[k].classList.toggle('sel', k === n); cNode[k].classList.toggle('inc', k !== n && r.nodes.indexOf(k) >= 0); });
    Object.keys(cEdge).forEach(function (k) { cEdge[k].classList.toggle('on', k !== n && r.nodes.indexOf(k) >= 0); });
    Object.keys(pEdge).forEach(function (k) { var on = r.etf.indexOf(k) >= 0; pEdge[k].classList.toggle('on', on); pNode[k].classList.toggle('on', on); });
    document.getElementById('rpTgTitle').textContent = '"' + n + '" = 개념 ' + r.nodes.length + '개, 상품 ' + r.etf.length + '개';
    document.getElementById('rpTgDesc').textContent = '포함되는 개념: ' + r.nodes.join(', ');
  }
})();
:::

:::notes
{timing: 1.5min}
[요약]
- 상위, 하위 관계(계층)가 있으면 "채권"이라는 넓은 말이 하위 개념 전체로 풀림
- 사람이 매번 설명하지 않아도 시스템이 기계적으로 펼칠 수 있음(추론)
- 계층이 없으면 모델이 "채권"을 값처럼 검색하거나 일부만 찾음

위쪽 질문을 보겠습니다. "채권 ETF 보여줘." DB에는 채권이라는 값이 없습니다. 국고채 코드와 해외국채 코드가 따로 있을 뿐입니다.
그래프에서 채권을 눌러 보겠습니다. 국고채, 해외국채, 미국국채까지 하위 개념 선이 굵어지고, 오른쪽 상품 다섯 개까지 선이 이어집니다.
{cue: click}
미국주식을 누르면 미국주식 다섯 개만, 주식을 누르면 국내와 해외를 합친 열세 개가 나옵니다.
{cue: pause}
이게 온톨로지에서 말하는 추론의 가장 쉬운 형태입니다. 사람이 매번 "채권은 국고채와 해외국채를 말해"라고 설명하지 않아도, 계층을 따라 기계적으로 펼칩니다. 계층이 없으면 모델은 채권이라는 글자를 그대로 값처럼 검색하거나, 아는 것 일부만 찾게 됩니다.
{cue: transition}
그럼 "미국채", "US Treasury" 같은 다른 말은 어떻게 처리할까요.
:::

---
<!-- Slide 6: 어휘 SKOS -->
@type: content
@title: 사람의 말을 DB 값으로 확정하는 사전

## 사람의 말을 DB 값으로 확정하는 사전

대표 이름(prefLabel), 별칭(altLabel), 실제 값을 한 개념에 묶는 어휘(SKOS)

:::html
<style>
.rp-voc { display: grid; grid-template-columns: 1.15fr 1fr; gap: var(--space-4); align-items: stretch; }
.rp-voc .code-block { margin: 0; }
.rp-flow3 { display: flex; flex-direction: column; gap: var(--space-2); }
.rp-flow3 .card { word-break: keep-all; padding: var(--space-2) var(--space-3); }
.rp-flow3 .card b { color: var(--accent); }
.rp-down { text-align: center; color: var(--on-surface-muted); font-size: var(--fs-card); line-height: 1; }
.rp-cap { font-size: var(--fs-caption); color: var(--on-surface-muted); }
</style>
<div class="rp-voc">
<pre class="code-block"><span class="comment"># etf_ontology.ttl (데모에 실제로 쓴 파일 일부)</span>
ex:BdUSGov  a skos:Concept ;
    skos:broader   ex:BdOvsGov ;        <span class="comment"># 상위: 해외국채</span>
    skos:prefLabel <span class="string">"미국국채"</span> ;
    skos:altLabel  <span class="string">"미국채"</span>, <span class="string">"미 국채"</span>, <span class="string">"US Treasury"</span> ;
    ex:sqlFilter   <span class="string">"ast_cls = 'BD_OVS_GOV' AND rgn_cd = 'US'"</span> .

<span class="comment"># 업무 상식 (Semantic Layer)</span>
ex:RuleFee  ex:trigger <span class="string">"보수"</span> ;
    rdfs:comment <span class="string">"fee_bp 단위는 bp(1bp = 0.01%p)다. 0.1% = 10bp."</span> .</pre>
  <div class="rp-flow3 fragment" data-reveal="stagger" data-fragment-index="1">
    <div class="card">질문 속 말: <b>"미 국채 ETF 중 보수가 낮은 것"</b></div>
    <div class="rp-down"><span class="rp-tip" tabindex="0" data-tip="질문 속 단어를 어휘 사전(prefLabel, altLabel)에서 찾아 개념으로 바꾸는 단계. 규칙 기반이라 항상 같은 결과">사전 조회 (LLM 호출 없음)</span></div>
    <div class="card">개념 확정: <b>미국국채</b> (상위: 해외국채, 채권)</div>
    <div class="rp-down">개념에 붙은 값</div>
    <div class="card">조건 확정: <b>ast_cls = 'BD_OVS_GOV' AND rgn_cd = 'US'</b>, 규칙: 보수는 fee_bp(bp)</div>
    <div class="rp-cap">사전에 없는 말이면 추측하지 않고 되묻습니다. 미래에셋증권은 vocabulary.ttl로 같은 일을 합니다.</div>
  </div>
</div>
:::

:::notes
{timing: 1.5min}
[요약]
- SKOS: 개념에 대표 이름(prefLabel)과 별칭(altLabel), 상위 개념(broader)을 붙이는 W3C 어휘 표준
- 개념에 실제 DB 조건(데모에서는 ex:sqlFilter)까지 붙여 두면 말에서 값까지 결정적으로 확정
- 확정은 사전 조회라 LLM 호출이 없음. 없는 말이면 되묻기
- 업무 상식(Semantic Layer)도 같은 파일에 규칙으로

간극 중 첫 번째, 말의 간극을 메우는 도구가 어휘입니다. 표준으로는 SKOS라는 W3C 어휘 표준을 많이 씁니다. 왼쪽은 오늘 데모에서 실제로 쓴 파일입니다.
미국국채라는 개념 하나에 대표 이름, 별칭 세 개, 상위 개념을 붙였고, 마지막 줄에 이 개념이 DB에서 실제로 어떤 조건인지까지 적었습니다. 아래는 "보수는 fee_bp이고 단위는 bp"라는 업무 상식입니다.
{cue: click}
오른쪽처럼 질문에 "미 국채"라는 말이 오면, 시스템이 사전을 조회해서 미국국채로 확정하고, 그 개념에 붙은 DB 조건까지 확정합니다. 이 단계에는 LLM이 끼지 않습니다. 그래서 같은 질문에는 항상 같은 조건이 나옵니다.
{cue: pause}
사전에 없는 말이 오면 추측하지 않고 되묻게 합니다. 미래에셋증권은 vocabulary.ttl이라는 파일로 똑같은 일을 합니다.
{cue: transition}
온톨로지가 에이전트 안에서 일하는 자리를 정리해 보겠습니다.
:::

---
<!-- Slide 7: 에이전트 안의 네 자리 -->
@type: content
@title: 온톨로지가 에이전트에서 일하는 네 자리

## 온톨로지가 에이전트에서 일하는 네 자리

질문이 들어와서 답이 나가기까지, 모델이 추측하던 일을 하나씩 결정적으로

:::html
<style>
.rp-four { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-3); }
.rp-four .card { word-break: keep-all; display: flex; flex-direction: column; gap: var(--space-1); }
.rp-four .rp-n { font-size: 2rem; font-weight: var(--weight-bold); color: var(--accent); line-height: 1; }
.rp-four .rp-where { margin-top: auto; border-top: 1px solid var(--border); padding-top: var(--space-2); font-size: var(--fs-caption); color: var(--on-surface-muted); }
.rp-four .rp-where b { color: var(--text-primary); }
.rp-io { display: flex; justify-content: space-between; font-size: var(--fs-card); color: var(--on-surface-muted); margin-bottom: var(--space-2); }
</style>
<div class="rp-io"><span>질문 들어옴</span><span>근거와 함께 답 나감</span></div>
<div class="rp-four fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="card"><span class="rp-n">1</span><div class="card-title">의도 이해</div><div class="card-desc">"결제 취소"와 "결제 실패"처럼 비슷한 의도를 속성으로 쪼개 구분</div><div class="rp-where"><b>신한카드</b>: Domain, Action, Tag 3속성 인텐트 온톨로지</div></div>
  <div class="card"><span class="rp-n">2</span><div class="card-title">값 확정</div><div class="card-desc">사용자의 말을 DB에 있는 실제 값으로 바꾸고, 못 바꾸면 되묻기</div><div class="rp-where"><b>미래에셋증권</b>: <span class="rp-tip" tabindex="0" data-tip="사용자의 말을 실제 DB 값이나 개체로 확정하는 단계. 확정 못 하면 되묻기">Ontology Grounding</span>, vocabulary.ttl</div></div>
  <div class="card"><span class="rp-n">3</span><div class="card-title">관계 탐색</div><div class="card-desc">여러 관계를 따라가야 답이 나오는 질문을 그래프 조회로</div><div class="rp-where"><b>미래에셋증권</b>: Neptune 관계, 시점 조회 / <b>5부 데모 앱</b>: <span class="rp-tip" tabindex="0" data-tip="관계를 여러 번 건너가며 답을 찾는 조회. 1-hop은 바로 이웃, 2-hop은 이웃의 이웃">multi-hop</span></div></div>
  <div class="card"><span class="rp-n">4</span><div class="card-title">규칙 강제</div><div class="card-desc">단위, 금지 조건, 업무 상식을 모델 대신 시스템이 적용</div><div class="rp-where"><b>미래에셋증권</b>: <span class="rp-tip" tabindex="0" data-tip="담당자가 아는 업무 상식(단위, 금지 조건, 매핑)을 시스템 규칙으로 적어 둔 계층">Semantic Layer</span> / <b>Canva</b>: 결정론적 도구</div></div>
</div>
:::

:::notes
{timing: 1.5min}
[요약]
- 1 의도 이해: 신한카드, 51개 인텐트를 Domain, Action, Tag로 분해
- 2 값 확정: 미래에셋증권 Ontology Grounding, 확정 못 하면 되묻기
- 3 관계 탐색: multi-hop 그래프 조회(미래에셋 Neptune, 5부 데모 앱)
- 4 규칙 강제: Semantic Layer, Canva의 결정론적 도구와 같은 원리
- 공통점: 모델이 추측하던 일을 시스템이 결정적으로

지금까지 본 재료가 에이전트 안에서 일하는 자리는 네 곳입니다. 3부 사례를 보실 때 이 네 자리를 기억해 두시면 연결이 잘 됩니다.
첫째, 의도 이해입니다. 신한카드는 51개 상담 의도를 도메인, 액션, 태그 세 속성으로 쪼갠 온톨로지로 분류했습니다. 둘째, 값 확정입니다. 미래에셋증권은 사용자의 말을 DB의 실제 값으로 확정하고, 못 하면 되묻습니다.
{cue: pause}
셋째, 관계 탐색입니다. 여러 관계를 따라가야 하는 질문은 그래프 DB로 조회합니다. 5부에서 이런 앱을 화면으로 보여 드립니다. 넷째, 규칙 강제입니다. 단위나 금지 조건을 모델이 기억하길 바라지 않고 시스템이 적용합니다. Canva가 말한 결정론적 도구와 같은 생각입니다.
네 자리의 공통점은 하나입니다. 모델이 추측하던 일을 시스템이 결정적으로 하게 만드는 것입니다.
{cue: transition}
그럼 흔히 듣는 RAG, 지식 그래프와는 무엇이 다른지 짧게 정리하겠습니다.
:::

---
<!-- Slide 8: 벡터, 그래프, 온톨로지 -->
@type: content
@title: 벡터 검색, 지식 그래프, 온톨로지는 층이다

## 벡터 검색, 지식 그래프, 온톨로지는 층이다

경쟁이 아니라 역할 분담, 미래에셋증권은 세 가지를 동시에 조회

:::html
<style>
.rp-layer { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); }
.rp-layer .card { word-break: keep-all; display: flex; flex-direction: column; gap: var(--space-2); }
.rp-layer dl { margin: 0; display: grid; grid-template-columns: auto 1fr; gap: var(--space-1) var(--space-2); font-size: var(--fs-card); }
.rp-layer dt { color: var(--on-surface-muted); font-size: var(--fs-caption); padding-top: 3px; }
.rp-layer dd { margin: 0; }
.rp-layer .rp-q { font-size: var(--fs-caption); border-top: 1px solid var(--border); padding-top: var(--space-2); margin-top: auto; color: var(--on-surface-muted); }
.rp-layer .rp-q b { color: var(--accent); }
.rp-layer-foot { margin-top: var(--space-3); }
.text-accent { color: var(--accent); font-weight: var(--weight-bold); }
</style>
<div class="rp-layer fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="card"><div class="card-title"><span class="rp-tip" tabindex="0" data-tip="RAG(검색 증강 생성): 질문과 의미가 비슷한 문서 조각을 찾아 모델에게 함께 주고 답하게 하는 방식">벡터 검색 (RAG)</span></div>
    <dl><dt>저장</dt><dd>문서 조각과 그 <span class="rp-tip" tabindex="0" data-tip="문장의 의미를 숫자 목록으로 바꾼 것. 뜻이 비슷하면 숫자도 가까움">의미 벡터</span></dd><dt>잘함</dt><dd>비슷한 내용 찾기</dd><dt>약함</dt><dd>정확한 값, 개수, 연결</dd></dl>
    <div class="rp-q">예: <b>"요즘 주목받는 테마 설명해줘"</b><br>미래에셋: OpenSearch 의미 검색</div></div>
  <div class="card"><div class="card-title">지식 그래프</div>
    <dl><dt>저장</dt><dd>개체와 관계(트리플)</dd><dt>잘함</dt><dd>여러 단계로 이어진 사실</dd><dt>약함</dt><dd>말이 다르면 시작점을 못 찾음</dd></dl>
    <div class="rp-q">예: <b>"이차전지 테마에 속한 ETF"</b><br>미래에셋: Neptune 관계 조회</div></div>
  <div class="card"><div class="card-title">온톨로지</div>
    <dl><dt>저장</dt><dd>개념, 관계, 어휘, 규칙의 약속</dd><dt>잘함</dt><dd>말과 값을 잇고 규칙을 강제</dd><dt>역할</dt><dd>위 두 저장소를 어떻게 쓸지 정함</dd></dl>
    <div class="rp-q">예: <b>"미국국채"를 'BD_OVS_GOV'로 확정</b><br>미래에셋: Grounding, Semantic Layer</div></div>
</div>
<div class="callout callout-info rp-layer-foot fragment fade-up" data-fragment-index="2"><strong class="text-accent">정리</strong>: 온톨로지는 저장소라기보다 설계도입니다. 그래프 DB 없이 파일과 코드로 시작해도 됩니다(다음 데모가 그렇게 만들었습니다).</div>
:::

:::notes
{timing: 1.5min}
[요약]
- 벡터 검색: 비슷한 내용 찾기에 강하고 정확한 값, 개수, 연결에 약함
- 지식 그래프: 여러 단계로 이어진 사실에 강함. 말이 다르면 시작점을 못 찾음
- 온톨로지: 말과 값을 잇고 규칙을 강제하는 설계도. 두 저장소를 어떻게 쓸지 정함
- 미래에셋증권은 OpenSearch, Neptune, Aurora를 질문 유형에 따라 동시에 조회

자주 받는 질문이 "RAG 하면 되는 거 아니냐", "지식 그래프랑 온톨로지가 같은 거냐"입니다. 셋은 경쟁 관계가 아니라 층입니다.
벡터 검색은 비슷한 내용을 찾는 데 강합니다. 대신 총보수가 0.1% 이하인 상품이 몇 개냐 같은 정확한 값과 개수에는 약합니다. 지식 그래프는 여러 단계로 이어진 사실에 강하지만, 사용자가 다른 말을 쓰면 그래프의 어느 점에서 출발할지 모릅니다.
{cue: pause}
온톨로지는 그 위에서 말과 값을 잇고, 규칙을 강제하고, 어떤 질문을 어느 저장소로 보낼지 정하는 설계도입니다. 3부에서 볼 미래에셋증권은 이 세 가지를 질문 유형에 따라 동시에 조회합니다.
그래서 온톨로지를 시작하려고 그래프 DB부터 살 필요는 없습니다. 파일과 코드로 시작해도 되고, 다음 데모가 실제로 그렇게 만들었습니다.
{cue: transition}
AWS에서는 무엇으로 만드는지 한 장으로 보겠습니다.
:::

---
<!-- Slide 9: AWS에서 만드는 법 -->
@type: content
@title: AWS에서는 무엇으로 만드나

## AWS에서는 무엇으로 만드나

작게는 파일과 코드, 커지면 그래프 DB와 관리형 GraphRAG

:::html
<style>
.rp-build { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-3); }
.rp-build .card { word-break: keep-all; }
.rp-build .card-title { font-size: var(--fs-card); }
.rp-build .badge { margin-left: var(--space-2); vertical-align: middle; }
.rp-src { font-size: var(--fs-caption); color: var(--on-surface-muted); margin-top: var(--space-2); word-break: keep-all; }
</style>
<div class="rp-build fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="card"><div class="card-title">파일과 코드로 시작 <span class="badge badge-green">PoC 1~2주</span></div><div class="card-desc">개념, 별칭, 규칙을 <span class="rp-tip" tabindex="0" data-tip="Turtle: RDF 트리플을 사람이 읽기 쉽게 적는 텍스트 형식(.ttl)">TTL</span>이나 YAML 파일로 두고, 확정 로직은 도구 함수로. 오늘 D1 데모와 미래에셋증권 YAML 규칙표가 이 방식입니다.</div></div>
  <div class="card"><div class="card-title">Amazon Neptune</div><div class="card-desc">관리형 그래프 DB. 속성 그래프(<span class="rp-tip" tabindex="0" data-tip="속성 그래프용 질의 언어. Gremlin은 단계별 순회, openCypher는 (a)-[관계]->(b) 패턴으로 질의">Gremlin, openCypher</span>)와 <span class="rp-tip" tabindex="0" data-tip="RDF: W3C 표준 트리플 데이터 모델. SPARQL: RDF용 표준 질의 언어">RDF(SPARQL)</span>를 모두 지원. 관계와 multi-hop 조회가 많아질 때.</div></div>
  <div class="card"><div class="card-title">Bedrock Knowledge Bases GraphRAG</div><div class="card-desc">S3 문서에서 엔터티와 관계를 자동으로 뽑아 <span class="rp-tip" tabindex="0" data-tip="그래프를 메모리에 올려 빠르게 분석하고 벡터 검색도 하는 Neptune 분석 엔진">Neptune Analytics</span> 그래프로. 벡터 검색 결과를 그래프로 넓혀 답합니다.</div></div>
  <div class="card"><div class="card-title">GraphRAG Toolkit (오픈소스)</div><div class="card-desc">그래프 구축과 검색을 직접 설계하고 싶을 때. 미래에셋증권은 Phase 1에서 이 도구로 Ontology, <span class="rp-tip" tabindex="0" data-tip="Entity Resolution: 서로 다른 출처의 같은 대상(상품, 회사)을 하나의 개체로 합치는 작업">ER</span>, Search 방법론을 검증했습니다.</div></div>
</div>
<div class="rp-src">출처: Amazon Neptune 문서(What is Amazon Neptune), Bedrock 문서(Build a knowledge base with Amazon Neptune Analytics graphs). GraphRAG는 2026-10-21 문서 기준 서울 리전 목록에 없음: 도입 전 리전 확인 필요</div>
:::

:::notes
{timing: 1.5min}
[요약]
- 파일과 코드: 개념, 별칭, 규칙을 TTL이나 YAML로, 확정 로직은 도구 함수로. PoC는 여기서 시작
- Amazon Neptune: 속성 그래프(Gremlin, openCypher)와 RDF(SPARQL) 모두 지원
- Bedrock Knowledge Bases GraphRAG: S3 문서에서 엔터티와 관계 자동 추출, Neptune Analytics 사용. 데이터 소스는 S3만, 서울 리전은 문서 목록에 없음
- GraphRAG Toolkit: 오픈소스, 미래에셋증권 Phase 1에서 사용

만드는 방법은 크기에 따라 다릅니다. 8주 PoC라면 왼쪽 위에서 시작하시길 권합니다. 개념, 별칭, 규칙을 TTL이나 YAML 파일로 두고, 확정하는 로직은 에이전트의 도구 함수로 만드는 겁니다. 오늘 데모도, 미래에셋증권의 YAML 규칙표도 이 방식입니다.
관계와 여러 단계 조회가 많아지면 Amazon Neptune을 씁니다. 속성 그래프와 RDF를 모두 지원합니다.
{cue: pause}
문서에서 관계를 자동으로 뽑고 싶다면 Bedrock Knowledge Bases의 GraphRAG가 있습니다. S3에 있는 문서로 Neptune Analytics 그래프를 만들어 줍니다. 다만 오늘 확인한 문서 기준으로 서울 리전이 목록에 없으니, 내부망 환경이라면 리전부터 확인하셔야 합니다. 직접 설계하고 싶다면 오픈소스 GraphRAG Toolkit이 있고, 미래에셋증권이 Phase 1에서 이걸로 방법론을 검증했습니다.
{cue: transition}
이제 직접 돌려 본 데모입니다.
:::

---
<!-- Slide 10: D1 데모 설계 -->
@type: content
@title: D1 데모: 같은 모델, 세 가지 입력

## D1 데모: 같은 모델, 세 가지 입력

미래에셋증권 실험을 작게 재현: 가상 ETF 22개, 질문 12개, Claude Haiku 4.5

:::html
<style>
.rp-d1 { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); }
.rp-d1 .card { word-break: keep-all; display: flex; flex-direction: column; gap: var(--space-2); }
.rp-d1 .rp-m { font-size: 2rem; font-weight: var(--weight-bold); color: var(--accent); line-height: 1; }
.rp-d1 ul { margin: 0; padding-left: var(--space-4); font-size: var(--fs-card); color: var(--on-surface-muted); }
.rp-d1-env { margin-top: var(--space-3); font-size: var(--fs-card); word-break: keep-all; }
.rp-d1-env code { font-size: var(--fs-caption); }
.text-accent { color: var(--accent); font-weight: var(--weight-bold); }
</style>
<div class="rp-d1 fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="card"><span class="rp-m">A</span><div class="card-title">스키마만</div><ul><li>테이블 <span class="rp-tip" tabindex="0" data-tip="테이블과 컬럼 구조를 정의한 SQL(CREATE TABLE 문)">DDL</span>과 컬럼 주석</li><li>지금 많은 <span class="rp-tip" tabindex="0" data-tip="자연어 질문을 SQL로 바꿔 DB를 조회하는 방식">Text-to-SQL</span>이 이 상태</li></ul></div>
  <div class="card"><span class="rp-m">B</span><div class="card-title">온톨로지를 설명</div><ul><li>A + 클래스, 관계, 계층, 별칭을 글로 설명</li><li>"프롬프트에 온톨로지를 넣었다"</li></ul></div>
  <div class="card highlight"><span class="rp-m">C</span><div class="card-title">온톨로지로 확정</div><ul><li>B + 사전 조회로 확정한 DB 조건과 업무 규칙</li><li>사전에 없는 상품 분류는 되묻기</li></ul></div>
</div>
<div class="callout callout-info rp-d1-env fragment fade-up" data-fragment-index="2"><strong class="text-accent">측정 방법</strong>: 질문마다 모드별 1회 호출(<span class="rp-tip" tabindex="0" data-tip="모델 출력의 무작위성을 가장 낮춘 설정. 같은 입력에 가능한 한 같은 답">temperature 0</span>), 생성 SQL을 실행해 정답 SQL 결과와 같은지 비교. 원장 값은 코드(<code>BD_OVS_GOV</code>, <code>T_BATT</code>), 보수는 bp 단위. 모든 데이터는 가상, 1회 실행, 2026-10-21</div>
:::

:::notes
{timing: 1min}
[요약]
- 미래에셋증권 실험을 작게 재현: 같은 모델, 같은 질문, 입력만 다르게
- A 스키마만, B 온톨로지를 글로 설명, C 온톨로지로 DB 조건까지 확정
- Claude Haiku 4.5, 질문 12개, 모드별 1회 호출, 생성 SQL 실행 결과로 채점
- 데이터는 가상 ETF 22개, 원장 값은 실제 사내 원장처럼 코드로 저장

제가 미래에셋증권의 실험을 아주 작게 재현해 봤습니다. 모델은 Claude Haiku 4.5 하나로 고정하고, 질문 12개를 세 가지 방식으로 줬습니다.
A는 테이블 스키마만 줍니다. B는 거기에 온톨로지를 글로 설명해 줍니다. 클래스, 관계, 계층, 별칭까지 다 들어갑니다. C는 질문 속 용어를 사전으로 먼저 확정해서, DB 조건과 업무 규칙을 붙여 줍니다.
{cue: pause}
채점은 생성된 SQL을 실제로 실행해서 정답 SQL과 결과가 같은지로 했습니다. 데이터는 모두 가상이고, 한 번 돌린 결과라는 점을 먼저 말씀드립니다.
근거: demo/FACTS.md D1, demo/d1_grounding.py
{cue: transition}
녹화 영상을 보겠습니다.
:::

---
<!-- Slide 11: D1 영상 -->
@type: content
@fit: off
@title: D1 영상: 설명할 때와 확정할 때

## D1 영상: 설명할 때와 확정할 때

:::html
<style>
.rp-vid { flex: 1; min-height: 0; display: grid; grid-template-columns: auto 1fr; gap: var(--space-4); }
.rp-vbox { height: 100%; min-height: 0; aspect-ratio: 1920 / 1836; }
.rp-video { width: 100%; height: 100%; object-fit: contain; background: var(--bg-card); border-radius: var(--space-2); display: block; }
.rp-vside { display: flex; flex-direction: column; gap: var(--space-2); justify-content: center; word-break: keep-all; }
.rp-vside .card { padding: var(--space-2) var(--space-3); }
.rp-vside .card b { color: var(--accent); font-variant-numeric: tabular-nums; margin-right: var(--space-2); }
.rp-vside .card span { font-size: var(--fs-card); }
.rp-vcap { font-size: var(--fs-caption); color: var(--on-surface-muted); }
</style>
<div class="rp-vid">
  <div class="rp-vbox"><video class="rp-video" src="media/d1-grounding.mp4" poster="media/d1-grounding.jpg" aria-label="D1 영상: 온톨로지 Grounding 실측, 실제 터미널 녹화, 무음, 61초" title="D1 영상: 온톨로지 Grounding 실측, 실제 터미널 녹화, 무음, 61초" controls preload="metadata" muted playsinline tabindex="-1"></video></div>
  <div class="rp-vside fragment" data-reveal="stagger" data-fragment-index="1">
    <div class="card"><b>0:00</b><span>원장은 코드값으로 저장</span></div>
    <div class="card"><b>0:08</b><span>어휘: 미국국채의 별칭과 DB 조건</span></div>
    <div class="card"><b>0:14</b><span>질문 하나를 A, B, C로: A와 B는 빈 결과</span></div>
    <div class="card"><b>0:22</b><span>질문 12개 전체 실행과 점수</span></div>
    <div class="card"><b>0:53</b><span>사전에 없는 말: 되묻기</span></div>
    <div class="rp-vcap">실제 터미널 녹화(2026-10-21), Amazon Bedrock 호출, 무음. 2초 넘는 대기는 2초로 줄임</div>
  </div>
</div>
:::

:::script
(function () {
  // Native video controls keep focus and swallow arrow and Space keys: hand focus back to the deck.
  document.querySelectorAll('video.rp-video').forEach(function (v) {
    var release = function () { setTimeout(function () { if (document.activeElement === v) v.blur(); }, 0); };
    ['focus', 'play', 'pause', 'seeked', 'volumechange', 'click', 'pointerup'].forEach(function (ev) { v.addEventListener(ev, release); });
  });
  // Pause any video left playing on a slide that is no longer active.
  window.addEventListener('hashchange', function () {
    document.querySelectorAll('.slide:not(.active) video.rp-video').forEach(function (v) { if (!v.paused) v.pause(); });
  });
})();
:::

:::notes
{timing: 1.5min}
[요약]
- 0:00 원장 값이 코드로 저장된 모습(ast_cls, thm_cd, fee_bp)
- 0:14 "미국국채 ETF 중 총보수가 가장 낮은 상품": A는 ast_cls = '미국국채', B는 thm_cd IN ('미국국채', ...)로 빈 결과, C만 정답
- 0:22 12개 전체: A 6, B 4, C 11
- 0:53 "친환경 ETF": 사전에 없는 말이라 SQL 대신 되묻기

Play를 누르고 장면마다 짧게 설명합니다. 영상은 무음이고, 필요하면 멈추면서 보시면 됩니다.
처음은 원장입니다. 자산분류, 지역, 테마가 모두 코드로 들어가 있습니다. 이어서 미국국채 개념에 붙은 별칭과 DB 조건이 나옵니다.
{cue: pause}
0분 14초부터 질문 하나를 세 방식으로 돌립니다. A는 자산분류가 '미국국채'인 것을 찾다가 빈 결과가 나오고, B는 온톨로지 설명을 읽고는 대표 이름과 별칭 세 개를 테마 코드에서 찾다가 역시 빈 결과가 나옵니다. C만 확정된 조건으로 정답을 냅니다.
0분 22초부터 12개 전체를 돌리고 점수가 나옵니다. 마지막은 사전에 없는 "친환경 ETF"를 물었을 때 SQL을 만들지 않고 되묻는 장면입니다.
근거: demo/FACTS.md D1, results/d1-run.json
{cue: transition}
결과를 한 장으로 정리하겠습니다.
:::

---
<!-- Slide 12: D1 결과 -->
@type: content
@title: 설명은 값이 아니다: 50%, 33%, 92%

## 설명은 값이 아니다: 50%, 33%, 92%

D1 결과(12문항, 1회)와 미래에셋증권 결과(72문항)의 같은 방향

:::html
<style>
.rp-res { display: grid; grid-template-columns: 1.1fr 1fr; gap: var(--space-4); align-items: start; }
.rp-bars { display: flex; flex-direction: column; gap: var(--space-3); }
.rp-bar { display: grid; grid-template-columns: 150px 1fr 90px; gap: var(--space-2); align-items: center; font-size: var(--fs-card); }
.rp-bar .t { height: 28px; background: var(--surface-2, var(--bg-card)); border-radius: 6px; overflow: hidden; border: 1px solid var(--border); }
.rp-bar .f { height: 100%; background: var(--on-surface-muted); }
.rp-bar.c .f { background: var(--accent); }
.rp-bar .v { font-weight: var(--weight-bold); font-variant-numeric: tabular-nums; text-align: right; }
.rp-bar.c .v { color: var(--accent); }
.rp-mirae { font-size: var(--fs-caption); color: var(--on-surface-muted); margin-top: var(--space-2); word-break: keep-all; }
.rp-less { display: flex; flex-direction: column; gap: var(--space-2); }
.rp-less .card { word-break: keep-all; padding: var(--space-2) var(--space-3); }
.rp-less .card-title { font-size: var(--fs-card); }
.rp-less code { font-size: var(--fs-caption); }
.rp-w50 { width: 50%; } .rp-w33 { width: 33.3%; } .rp-w92 { width: 91.7%; }
</style>
<div class="rp-res">
  <div>
    <div class="rp-bars">
      <div class="rp-bar"><span>A 스키마만</span><div class="t"><div class="f rp-w50"></div></div><span class="v">6/12</span></div>
      <div class="rp-bar"><span>B 온톨로지 설명</span><div class="t"><div class="f rp-w33"></div></div><span class="v">4/12</span></div>
      <div class="rp-bar c"><span>C 온톨로지 확정</span><div class="t"><div class="f rp-w92"></div></div><span class="v">11/12</span></div>
    </div>
    <div class="rp-mirae">참고, 미래에셋증권(국내 ETF 72문항): 스키마만 45%, 온톨로지를 프롬프트에 설명 47.4%, 값 확정 65%, 연합 검색과 Semantic Layer까지 84.7%</div>
  </div>
  <div class="rp-less fragment" data-reveal="stagger" data-fragment-index="1">
    <div class="card"><div class="card-title">설명을 주면 오히려 헷갈린다</div><div class="card-desc">B는 개념 이름을 DB 값처럼 썼습니다: <code>thm_cd IN ('미국국채', 'US Treasury', ...)</code></div></div>
    <div class="card"><div class="card-title">확정은 같은 모델을 바꾼다</div><div class="card-desc">단위(0.1% = <span class="rp-tip" tabindex="0" data-tip="bp(basis point) = 0.01%p. 총보수 0.1%는 10bp">10bp</span>), 계층, 별칭이 조건으로 들어가자 11개를 맞혔습니다.</div></div>
    <div class="card"><div class="card-title">사전에 없는 말은 되묻는다</div><div class="card-desc">C의 오답 1건은 "코스피200"이 사전에 없어 되물은 경우. 사전 범위가 곧 성능입니다.</div></div>
  </div>
</div>
:::

:::notes
{timing: 1.5min}
[요약]
- A 스키마만 50.0%, B 온톨로지 설명 33.3%, C 온톨로지 확정 91.7% (12문항, 1회, 가상 데이터)
- B가 더 낮았던 이유: 개념 이름을 DB 값처럼 사용
- C 오답 1건: "코스피200"이 어휘에 없어 되물음. A는 상품명 LIKE 검색으로 맞힘
- 미래에셋증권도 같은 방향: 설명 +2.4%p, 값 확정 후 65%, 연합 검색과 Semantic Layer까지 84.7%

결과입니다. 스키마만 줬을 때 12개 중 6개, 온톨로지를 설명해 줬을 때 4개, 확정해 줬을 때 11개를 맞혔습니다.
가장 흥미로운 건 B입니다. 설명을 더 줬는데 오히려 떨어졌습니다. 쿼리를 열어 보니 모델이 개념 이름을 DB 값처럼 썼습니다. 테마 코드에서 '미국국채'라는 글자를 찾은 겁니다. 설명은 값이 아니라는 걸 보여 주는 장면입니다.
{cue: pause}
C는 단위, 계층, 별칭이 조건으로 들어가니 같은 모델이 11개를 맞혔습니다. 틀린 1개도 의미가 있습니다. 코스피200이라는 말이 사전에 없어서 모델이 되물었고, 오히려 A는 상품명 검색으로 맞혔습니다. 사전의 범위가 곧 성능이라는 뜻이고, 그래서 운영 중에 사전을 계속 보강하는 루프가 필요합니다.
왼쪽 아래 미래에셋증권 결과도 같은 방향입니다. 온톨로지를 프롬프트에 설명했을 때는 2.4%p만 올랐고, 값을 확정하면서 크게 올랐습니다. 제 데모는 12문항 한 번이라 숫자 자체보다 방향을 봐 주세요.
근거: demo/FACTS.md D1, results/d1-run.json, 미래에셋증권 AWS FSI Forum 발표
{cue: transition}
하나 더, 온톨로지가 잘 안 통했던 실험도 보여 드리겠습니다.
:::

---
<!-- Slide 13: D2 결과 -->
@type: content
@title: 온톨로지가 늘 이기지는 않는다

## 온톨로지가 늘 이기지는 않는다

D2: 신한카드식 3속성 인텐트 분류를 소형 모델로 재현해 본 결과

:::html
<style>
.rp-d2 { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); align-items: start; }
.rp-d2 .data-table { width: 100%; font-size: var(--fs-card); }
.rp-d2 .data-table th { text-transform: none; letter-spacing: normal; font-size: var(--fs-caption); }
.rp-d2 td.n { font-variant-numeric: tabular-nums; font-weight: var(--weight-bold); }
.rp-d2-cond { font-size: var(--fs-caption); color: var(--on-surface-muted); margin-top: var(--space-2); word-break: keep-all; }
.rp-d2-r { display: flex; flex-direction: column; gap: var(--space-2); }
.rp-d2-r .card { word-break: keep-all; padding: var(--space-2) var(--space-3); }
.rp-d2-r .card-title { font-size: var(--fs-card); }
</style>
<div class="rp-d2">
  <div>
    <table class="data-table">
      <thead><tr><th>회차</th><th>A 목록에서 직접 선택</th><th>B 3속성 + 그래프 매칭</th></tr></thead>
      <tbody>
        <tr><td>1차: 속성 정의 초안</td><td class="n">24/40 (60.0%)</td><td class="n">23/40 (57.5%)</td></tr>
        <tr><td>2차: 설명과 속성 정의 수정</td><td class="n">40/40 (100%)</td><td class="n">24/40 (60.0%)</td></tr>
      </tbody>
    </table>
    <div class="rp-d2-cond">Amazon Nova Micro, 가상 인텐트 20개(Domain 4, Action 5, Tag 8), 가상 발화 40개, 1회 실행, 2026-10-21. 발화를 설명과 같은 사람이 만들어 쉬운 편</div>
  </div>
  <div class="rp-d2-r fragment" data-reveal="stagger" data-fragment-index="1">
    <div class="card"><div class="card-title">정의가 모호하면 둘 다 무너진다</div><div class="card-desc">"한도 올려줘"가 신청인지 변경인지 정하지 않은 1차에서는 두 방식 모두 60% 안팎</div></div>
    <div class="card"><div class="card-title">작은 규모에서는 직접 선택이 낫다</div><div class="card-desc">20개, 설명이 분명하면 소형 모델도 목록에서 바로 고릅니다. 속성 3개를 따로 고르면 오류가 곱해집니다.</div></div>
    <div class="card"><div class="card-title">신한카드의 조건을 기억하기</div><div class="card-desc">51개로 잘게 나뉜 의도, 문맥이 비슷한 쌍, 규제와 비용 때문에 소형 모델만 쓸 수 있는 조건에서 보고된 효과입니다.</div></div>
  </div>
</div>
:::

:::notes
{timing: 1.5min}
[요약]
- D2: 인텐트 20개를 Nova Micro로, 목록에서 직접 선택(A)과 Domain, Action, Tag 3속성 + 매칭(B) 비교
- 1차(정의 초안): A 60.0%, B 57.5%. 2차(정의 수정): A 100%, B 60.0%
- 교훈: 정의가 모호하면 어떤 방식도 무너짐. 작은 규모에서는 직접 선택이 나음. 분해는 오류가 곱해짐
- 신한카드 효과는 51개 세분 의도, 유사 쌍, 소형 모델 제약이라는 조건에서 나온 값

공정하게 하나 더 보여 드리겠습니다. 신한카드처럼 인텐트를 세 속성으로 쪼개는 방식을 작은 모델로 재현해 봤습니다. 인텐트 20개, 발화 40개입니다.
1차에서는 두 방식 다 60% 안팎이었습니다. 열어 보니 제가 만든 정의가 모호했습니다. "한도 올려줘"가 신청인지 변경인지 정해 두지 않은 겁니다. 정의를 고치고 다시 돌렸더니 직접 고르는 방식이 40개를 다 맞혔고, 3속성 방식은 60%에 머물렀습니다.
{cue: pause}
이유는 단순합니다. 인텐트가 20개이고 설명이 분명하면 작은 모델도 목록에서 바로 잘 고릅니다. 속성 세 개를 따로 고르면 하나만 틀려도 결과가 틀리니 오류가 곱해집니다. 신한카드는 51개로 잘게 나뉜 의도, 문맥이 비슷한 쌍, 그리고 소형 모델만 쓸 수 있는 조건에서 효과를 봤습니다.
가져가실 메시지는 "온톨로지가 정답"이 아니라 "먼저 정의를 분명히 하고, 측정해서 고르라"입니다. 제 발화 세트가 쉬운 편이었다는 점도 함께 말씀드립니다.
근거: demo/FACTS.md D2, results/d2-run2-nova-micro.json
{cue: transition}
그럼 PoC에서는 어디서부터 시작하면 될까요.
:::

---
<!-- Slide 14: 작게 시작하는 4단계 -->
@type: content
@title: 온톨로지, 이렇게 작게 시작하세요

## 온톨로지, 이렇게 작게 시작하세요

미래에셋증권의 순서를 8주 PoC 크기로 줄이면

:::html
<style>
.rp-start { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-3); }
.rp-start .card { word-break: keep-all; display: flex; flex-direction: column; gap: var(--space-2); }
.rp-start .rp-n { font-size: var(--fs-caption); color: var(--accent); font-weight: var(--weight-bold); letter-spacing: .08em; }
.rp-start .rp-ex { margin-top: auto; border-top: 1px solid var(--border); padding-top: var(--space-2); font-size: var(--fs-caption); color: var(--on-surface-muted); }
.rp-start-foot { margin-top: var(--space-3); }
.text-accent { color: var(--accent); font-weight: var(--weight-bold); }
</style>
<div class="rp-start fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="card"><span class="rp-n">STEP 1</span><div class="card-title">답해야 할 질문부터</div><div class="card-desc">실제 질문 30~50개를 모으고, 정답과 근거를 붙입니다. 이것이 평가셋이 됩니다.</div><div class="rp-ex">미래에셋: 온톨로지가 답할 질문 목록을 먼저 뽑음</div></div>
  <div class="card"><span class="rp-n">STEP 2</span><div class="card-title">질문에 나온 개념만</div><div class="card-desc">질문에 등장한 개념과 관계만 정의합니다. 처음부터 전사 모델을 그리지 않습니다.</div><div class="rp-ex">예: 상품, 자산분류, 운용사, 계층 3단계</div></div>
  <div class="card"><span class="rp-n">STEP 3</span><div class="card-title">별칭 사전과 규칙</div><div class="card-desc">현업이 쓰는 말과 DB 값을 잇고, 담당자의 상식을 규칙으로 적습니다.</div><div class="rp-ex">예: 미국채는 미국국채, 0.1%는 10bp</div></div>
  <div class="card"><span class="rp-n">STEP 4</span><div class="card-title">측정하고 보강</div><div class="card-desc">평가셋으로 단계마다 점수를 재고, 되묻기와 실패 로그로 사전을 채웁니다.</div><div class="rp-ex">D1: "코스피200" 되묻기가 다음 보강 대상</div></div>
</div>
<div class="callout callout-info rp-start-foot fragment fade-up" data-fragment-index="2"><strong class="text-accent">과제 연결</strong>: TASK 01 마이데이터(상품, 자산 용어), TASK 05 운영지식 위키(시스템명, 장애 용어), TASK 04 서류 점검(서류 유형, 필수 항목)이 특히 효과가 큽니다.</div>
:::

:::notes
{timing: 1min}
[요약]
- STEP 1 질문 목록과 정답, 근거(평가셋 겸용) / STEP 2 질문에 나온 개념만 정의
- STEP 3 별칭 사전과 업무 규칙 / STEP 4 평가셋으로 측정하고 되묻기, 실패 로그로 보강
- 사내 용어가 많은 TASK 01, 05, 04에서 효과가 큼

PoC에서는 이렇게 작게 시작하시길 권합니다. 미래에셋증권이 실제로 밟은 순서를 8주 크기로 줄인 겁니다.
먼저 답해야 할 질문 30개에서 50개를 모으고 정답과 근거를 붙입니다. 이게 그대로 평가셋이 됩니다. 다음으로 그 질문에 나온 개념과 관계만 정의합니다. 처음부터 전사 데이터 모델을 그리면 8주가 금방 지나갑니다.
{cue: pause}
셋째, 현업이 쓰는 말과 DB 값을 잇는 별칭 사전, 담당자의 상식을 규칙으로 적습니다. 넷째, 평가셋으로 점수를 재고 되묻기와 실패 로그로 사전을 채웁니다. 오늘 D1에서 코스피200 되묻기가 바로 다음 보강 대상입니다.
마이데이터, 운영지식 위키, 서류 점검처럼 사내 용어가 많은 과제일수록 효과가 큽니다.
{cue: transition}
이제 이 원리가 실제 사례에서 어떻게 쓰였는지 3부에서 보겠습니다.
:::
