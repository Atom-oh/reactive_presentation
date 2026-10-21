---
remarp: true
block: 05-demo-close
---

---
<!-- Slide 1: 5부 구분 -->
@type: section

# 온톨로지 위의 에이전트, 그리고 PoC 실행 팁

화면 데모 한 편, 체크리스트, 바로 쓸 자료

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
- 5부: 온톨로지 위에서 도는 에이전트 앱 화면 데모(D3)
- PoC 실행 체크리스트 다섯 가지와 바로 시작할 자료
- 마무리와 Q&A

마지막 5부입니다. 2부에서 개념, 관계, 그래프를 말씀드렸는데, 그게 실제 앱에서는 어떻게 보이는지 화면 데모 한 편을 보고, 남은 PoC 기간에 바로 쓸 체크리스트와 자료로 마무리하겠습니다.
{cue: transition}
데모 앱부터 소개하겠습니다.
:::

---
<!-- Slide 2: D3 데모 앱 소개 -->
@type: content
@title: D3 데모 앱: 국회 데이터 온톨로지

## D3 데모 앱: 국회 데이터 온톨로지

ontology-assembly (assembly.whchoi.net): 22대 국회 의원, 의안, 표결, 주제, 기사를 하나의 온톨로지로

:::html
<style>
.rp-d3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); }
.rp-d3 .card { word-break: keep-all; display: flex; flex-direction: column; gap: var(--space-2); }
.rp-d3 .rp-n { font-size: var(--fs-caption); color: var(--accent); font-weight: var(--weight-bold); letter-spacing: .06em; }
.rp-d3 .rp-v { font-size: 1.6rem; font-weight: var(--weight-bold); color: var(--accent); font-variant-numeric: tabular-nums; margin-top: auto; }
.rp-d3 .rp-c { font-size: var(--fs-caption); color: var(--on-surface-muted); }
.rp-d3-foot { margin-top: var(--space-3); word-break: keep-all; }
.text-accent { color: var(--accent); font-weight: var(--weight-bold); }
</style>
<div class="rp-d3 fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="card"><span class="rp-n">개념 (2부 3장)</span><div class="card-title">Object Explorer</div><div class="card-desc">인물, 입법, 주제, 미디어, 독자, 광고 영역의 클래스와 필드. 클래스를 누르면 인스턴스 목록</div><div class="rp-v">31 클래스</div><div class="rp-c">Person 인스턴스 306개</div></div>
  <div class="card"><span class="rp-n">관계 탐색 (2부 7장, 세 번째 자리)</span><div class="card-title">온톨로지 관계 그래프</div><div class="card-desc">의원, 의안, 표결, 주제, 기사에서 출발해 1~3 <span class="rp-tip" tabindex="0" data-tip="관계를 몇 번 건너가는지. 1 hop은 바로 이웃, 2 hop은 이웃의 이웃">hop</span> 관계를 펼침. 2 hop 이상은 Neptune Cypher multi-hop 조회</div><div class="rp-v">1~3 hop</div><div class="rp-c">노드 더블클릭으로 추가 확장</div></div>
  <div class="card"><span class="rp-n">에이전트 (1부)</span><div class="card-title">데스크 챗봇</div><div class="card-desc">같은 온톨로지를 도구로 조회하는 에이전트. planner, graph, analyst, editor 단계와 도구 호출 로그를 화면에 표시</div><div class="rp-v">10 도구</div><div class="rp-c">답변에 수치와 출처(실 데이터, 합성) 표시</div></div>
</div>
<div class="callout callout-info rp-d3-foot fragment fade-up" data-fragment-index="2"><strong class="text-accent">보는 포인트</strong>: 은행 과제로 바꾸면 의원은 고객, 의안은 상품, 표결은 거래입니다. 개념, 관계, 에이전트가 같은 데이터 위에 있다는 점을 보세요.</div>
:::

:::notes
{timing: 1.5min}
[요약]
- ontology-assembly: 22대 국회 데이터(의원, 의안, 표결, 주제, 기사)를 하나의 온톨로지로 묶은 데모 앱
- Object Explorer(31 클래스, Person 306개), 관계 그래프(1~3 hop, 2 hop 이상은 Neptune Cypher), 데스크 챗봇(10 도구)
- 2부의 개념, 관계 탐색, 1부의 에이전트가 같은 데이터 위에
- 은행으로 바꾸면 의원은 고객, 의안은 상품, 표결은 거래
- 수치는 2026-10-21 녹화 화면 기준

D3는 제가 만든 데모가 아니라, 국회 데이터로 만든 온톨로지 데모 앱 ontology-assembly의 화면 녹화입니다. 22대 국회의 의원, 의안, 표결, 주제, 기사를 하나의 온톨로지로 묶었습니다.
세 화면을 봅니다. Object Explorer는 2부에서 말한 개념, 즉 클래스 목록입니다. 관계 그래프는 2부의 세 번째 자리, 관계 탐색입니다. 1 hop부터 3 hop까지 펼치고, 2 hop 이상은 Neptune에서 multi-hop으로 조회한다고 화면에 적혀 있습니다.
{cue: pause}
데스크 챗봇은 같은 온톨로지를 도구로 조회하는 에이전트이고, 어떤 단계와 도구를 거쳤는지 화면에 남깁니다.
은행 과제로 바꿔 생각하면 의원은 고객, 의안은 상품, 표결은 거래입니다. 개념, 관계, 에이전트가 같은 데이터 위에 있다는 점을 보시면 됩니다.
근거: demo/FACTS.md D3 (2026-10-21 녹화 화면 값)
{cue: transition}
영상을 보겠습니다.
:::

---
<!-- Slide 3: D3 영상 -->
@type: content
@fit: off
@title: D3 영상: 개념, 관계, 에이전트

## D3 영상: 개념, 관계, 에이전트

:::html
<style>
.rp-full { flex: 1; min-height: 0; display: flex; flex-direction: column; gap: var(--space-1); }
.rp-vbox3 { flex: 1; min-height: 0; container-type: size; }
.rp-video3 { display: block; width: min(100cqw, calc(100cqh * 16 / 9)); height: auto; margin-inline: auto; background: var(--bg-card); border-radius: var(--space-2); }
.rp-vcap3 { color: var(--on-surface-muted); text-align: center; font-size: var(--fs-card); }
</style>
<div class="rp-full">
  <div class="rp-vbox3"><video class="rp-video3" src="media/d3-assembly.mp4" poster="media/d3-assembly.jpg" aria-label="D3 영상: ontology-assembly 앱 화면 녹화, Object Explorer, 관계 그래프, 데스크 챗봇, 무음, 74초" title="D3 영상: ontology-assembly 앱 화면 녹화, 무음, 74초" controls preload="metadata" muted playsinline tabindex="-1"></video></div>
  <div class="rp-vcap3">assembly.whchoi.net 화면 녹화(2026-10-21), 노란 자막과 커서만 덧붙임, 무음, 74초</div>
</div>
:::

:::script
(function () {
  // Native video controls keep focus and swallow arrow and Space keys: hand focus back to the deck.
  document.querySelectorAll('video.rp-video3').forEach(function (v) {
    var release = function () { setTimeout(function () { if (document.activeElement === v) v.blur(); }, 0); };
    ['focus', 'play', 'pause', 'seeked', 'volumechange', 'click', 'pointerup'].forEach(function (ev) { v.addEventListener(ev, release); });
  });
  // Pause any video left playing on a slide that is no longer active.
  window.addEventListener('hashchange', function () {
    document.querySelectorAll('.slide:not(.active) video.rp-video3').forEach(function (v) { if (!v.paused) v.pause(); });
  });
})();
:::

:::notes
{timing: 2min}
[요약]
- 0:00 Object Explorer 31 클래스, 0:12 Person 인스턴스 306개
- 0:16 관계 그래프에서 의원 선택, 0:24 1-hop(정당, 위원회, 발의 의안, 표결, 주제), 0:32 2-hop(공동발의 의원, 그 의원의 위원회와 발의 의안)
- 0:44 데스크 챗봇, 0:48 planner, graph, analyst, editor 단계와 도구 호출 로그, 1:00 답변의 근거 수치와 출처
- 챗봇 응답 내용은 녹화 시점 그대로, 데모 앱의 데이터에는 합성 데이터가 섞여 있음
- 녹화 환경(headless Chromium) 폰트 문제로 표결 노드 라벨 "가결"의 자모가 분리되어 보임. 사이트 데이터 문제 아님

Play를 누르고 노란 자막에 맞춰 설명합니다. 영상은 무음입니다.
처음 12초는 Object Explorer입니다. 인물, 입법, 주제, 미디어 영역의 클래스가 보이고, Person을 누르면 인스턴스 목록이 나옵니다. 2부의 클래스와 인스턴스 구분이 그대로 화면입니다.
{cue: pause}
16초부터 관계 그래프입니다. 의원 한 명을 고르면 1-hop으로 정당, 위원회, 발의 의안, 표결, 주제가 이어지고, 32초에 2-hop을 누르면 의안을 거쳐 공동발의 의원, 그 의원의 위원회와 다른 의안까지 펼쳐집니다. 화면 자막에는 "다른 주제까지"라고 적혀 있지만 이 의원의 2-hop에는 새 주제가 없습니다. 트리플 슬라이드에서 질문을 따라갔던 것과 같은 일입니다.
44초부터는 데스크 챗봇입니다. AI 관련 의안 발의 상위 5명과 공동발의 네트워크를 물으면 planner, graph, analyst, editor 단계를 거치고, 오른쪽에 호출한 도구가 남습니다. 마지막에는 답변 속 수치와 출처를 보여 줍니다.
데모 앱 데이터에는 실 데이터와 합성 데이터가 섞여 있고, 화면에도 출처가 구분되어 있습니다. 은행에서도 이렇게 출처를 구분해 보여 주는 것이 설명 가능성의 출발점입니다.
근거: demo/FACTS.md D3 (자막 시각)
{cue: transition}
이제 PoC 실행 체크리스트입니다.
:::

---
<!-- Slide 4: PoC 실행 체크리스트 -->
@type: content
@title: PoC 실행 체크리스트

## PoC 실행 체크리스트

오늘 사례에서 뽑은 다섯 가지, 과제가 달라도 순서는 같음

:::html
<style>
.rp-ck { display: grid; grid-template-columns: repeat(5, 1fr); gap: var(--space-3); }
.rp-ck .card { word-break: keep-all; display: flex; flex-direction: column; gap: var(--space-2); }
.rp-ck .rp-n { font-size: 2rem; font-weight: var(--weight-bold); color: var(--accent); line-height: 1; }
.rp-ck .card-title { font-size: var(--fs-card); }
.rp-ck .rp-who { margin-top: auto; border-top: 1px solid var(--border); padding-top: var(--space-2); font-size: var(--fs-caption); color: var(--on-surface-muted); }
.rp-ck-foot { margin-top: var(--space-3); word-break: keep-all; }
.text-accent { color: var(--accent); font-weight: var(--weight-bold); }
</style>
<div class="rp-ck fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="card"><span class="rp-n">1</span><div class="card-title">평가셋부터</div><div class="card-desc">질문, 정답, 근거로 된 작은 골든셋과 실패 사례 목록을 첫 주에 만든다</div><div class="rp-who">NewDay, 미래에셋</div></div>
  <div class="card"><span class="rp-n">2</span><div class="card-title">지식을 구조화</div><div class="card-desc">용어 사전, 항목 정의서, 메타데이터. 사용자 말을 실제 값으로 확정</div><div class="rp-who">신한카드, 미래에셋, D1 데모</div></div>
  <div class="card"><span class="rp-n">3</span><div class="card-title">작게 시작, 검증은 따로</div><div class="card-desc">단일 에이전트로 시작해 필요할 때만 분리. 검증 에이전트는 별도로</div><div class="rp-who">LG전자, 링크알파, Canva</div></div>
  <div class="card"><span class="rp-n">4</span><div class="card-title">근거를 화면에</div><div class="card-desc">답마다 출처와 조항 표시. 확정 못 하면 되묻고, 없는 건 모른다고</div><div class="rp-who">미래에셋, 서울경제</div></div>
  <div class="card"><span class="rp-n">5</span><div class="card-title">첫날부터 <span class="rp-tip" tabindex="0" data-tip="요청 하나가 거친 모든 단계(모델 호출, 도구 호출)와 시간, 토큰의 기록">trace</span></div><div class="card-desc">관측을 켜고 평가 점수를 대시보드로. 조치성 도구엔 승인 단계</div><div class="rp-who">PropHero, 삼성계정</div></div>
</div>
<div class="callout callout-info rp-ck-foot fragment fade-up" data-fragment-index="2"><strong class="text-accent">데모 데이에 함께 보여주세요</strong>: 평가 점수, 근거가 보이는 응답, trace 화면</div>
:::

:::notes
{timing: 2min}
[요약]
- 1 평가셋부터: 작은 골든셋과 실패 사례 목록만 있어도 개선이 측정됨
- 2 지식을 구조화: 용어 사전, 항목 정의서, 메타데이터, 값 확정 단계(D1에서 확인)
- 3 작게 시작, 검증은 따로 / 4 근거를 화면에(금융에서 설명 가능성은 요건) / 5 첫날부터 trace, 조치성 도구엔 사람 승인
- 데모 데이: 잘 도는 화면 + 평가 점수, 근거, trace

마지막으로 실행 체크리스트입니다. 오늘 본 사례에서 뽑은 다섯 가지이고, 과제가 달라도 순서는 같다고 생각합니다.
첫째, 평가셋을 먼저 만드세요. 질문, 정답, 근거로 된 작은 골든셋과 실패 사례 목록만 있어도 개선이 측정됩니다. 둘째, 지식을 구조화하세요. 용어 사전, 항목 정의서, 메타데이터를 만들고, 사용자 말을 실제 값으로 확정하는 단계를 두세요. D1에서 같은 모델이 50%에서 92%로 달라지는 걸 보셨습니다.
{cue: pause}
셋째, 단일 에이전트로 작게 시작하고, 필요할 때만 나누되 검증 에이전트는 따로 두세요. 넷째, 근거를 화면에 보여주세요. 금융에서는 설명 가능성이 곧 요건입니다. 다섯째, 첫날부터 trace를 켜고, 실제 조치를 하는 도구에는 사람 승인 단계를 두세요.
데모 데이에는 잘 돌아가는 화면과 함께 평가 점수, 근거, trace를 같이 보여주시면 설득력이 확 올라갑니다.
{cue: transition}
바로 시작할 수 있는 자료입니다.
:::

---
<!-- Slide 5: 자료 -->
@type: content
@title: 바로 시작할 수 있는 자료

## 바로 시작할 수 있는 자료

링크는 공유 자료에서 클릭 가능

:::html
<style>
.rp-res3 { display: grid; grid-template-columns: 1.1fr 1fr; gap: var(--space-4); align-items: start; }
.rp-res3 .card { word-break: keep-all; }
.rp-res3 ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: var(--space-2); }
.rp-res3 li { font-size: var(--fs-card); border-top: 1px solid var(--border); padding-top: var(--space-1); }
.rp-res3 li:first-child { border-top: 0; padding-top: 0; }
.rp-res3 a { color: var(--accent); text-decoration: none; font-weight: var(--weight-semibold); overflow-wrap: anywhere; }
.rp-res3 li span { display: block; font-size: var(--fs-caption); color: var(--on-surface-muted); }
.rp-res3 .card-title { margin-bottom: var(--space-2); }
</style>
<div class="rp-res3">
  <div class="card">
    <div class="card-title">코드와 워크숍</div>
    <ul>
      <li><a href="https://github.com/awslabs/amazon-bedrock-agentcore-samples" target="_blank" rel="noopener">awslabs/amazon-bedrock-agentcore-samples</a><span>AgentCore 튜토리얼, 유즈케이스, 블루프린트</span></li>
      <li><a href="https://github.com/strands-agents/samples" target="_blank" rel="noopener">strands-agents/samples</a><span>Strands Agents 예제 (Python, TypeScript)</span></li>
      <li><a href="https://github.com/aws-samples/sample-deep-insight" target="_blank" rel="noopener">aws-samples/sample-deep-insight</a><span>Deep Insight 멀티 에이전트 분석과 보고서 (TASK 03)</span></li>
      <li><a href="https://github.com/aws-samples/sample-strands-agent-with-agentcore" target="_blank" rel="noopener">aws-samples/sample-strands-agent-with-agentcore</a><span>Strands + AgentCore 멀티 에이전트 챗봇 참조 구현</span></li>
      <li><a href="https://catalog.workshops.aws/agentcore-getting-started" target="_blank" rel="noopener">catalog.workshops.aws/agentcore-getting-started</a><span>AgentCore 입문 워크숍</span></li>
      <li><a href="demo/README.md" target="_blank" rel="noopener">오늘 데모 D1, D2 코드와 기록 (demo/)</a><span>가상 ETF 원장, etf_ontology.ttl, 실행 결과 JSON</span></li>
    </ul>
  </div>
  <div class="card fragment fade-up" data-fragment-index="1">
    <div class="card-title">사례 원문</div>
    <ul>
      <li><b>LG전자</b><span>Agentic 리포트 자동화, Deep Insight 설계 교훈</span></li>
      <li><b>신한카드</b><span>온톨로지 기반 분산형 챗봇</span></li>
      <li><b>미래에셋증권</b><span>AI-Ready Data (AWS FSI Forum 발표)</span></li>
      <li><b>Canva</b><span>ANT105 Agentic Engineering, Agentic Design Patterns</span></li>
      <li><b>과제별 사례</b><span>PropHero, NewDay, 미리디, 위메이드플레이, 링크알파, 서울경제신문, Rocket Close, Sun Finance, 춘시리, A1Mobilsoft, GS리테일, 삼성계정</span></li>
      <li><b>온톨로지 도구</b><span>Amazon Neptune, Bedrock Knowledge Bases GraphRAG, GraphRAG Toolkit</span></li>
    </ul>
  </div>
</div>
:::

:::notes
{timing: 1min}
[요약]
- 코드: AgentCore 샘플(튜토리얼, 유즈케이스, 블루프린트), Strands 예제, Deep Insight(TASK 03 출발점), Strands + AgentCore 참조 구현, AgentCore 입문 워크숍
- 오늘 데모 D1, D2 코드와 실행 기록: 이 덱의 demo 폴더
- 사례 원문: LG전자, 신한카드, 미래에셋증권, Canva, 과제별 사례
- Canva 발표 영상: https://youtu.be/4EJJwXseuzw

바로 쓰실 수 있는 자료입니다. 왼쪽은 코드입니다. AgentCore 샘플 저장소에 튜토리얼부터 유즈케이스, 블루프린트까지 있고, Strands 예제 저장소에는 파이썬과 타입스크립트 예제가 있습니다. 리서치 보고서 과제 팀은 Deep Insight 저장소를 출발점으로 쓰시면 시간을 많이 아끼실 수 있습니다.
{cue: pause}
오늘 2부에서 보여 드린 D1, D2 데모 코드와 실행 기록도 이 덱의 demo 폴더에 넣어 두었습니다. 온톨로지 파일 하나와 파이썬 파일 몇 개라서, 과제 데이터로 바꿔서 바로 돌려 보실 수 있습니다. 오른쪽은 오늘 소개한 사례의 원문입니다.
Canva 발표 영상 참고 링크: https://youtu.be/4EJJwXseuzw
{cue: transition}
정리하겠습니다.
:::

---
<!-- Slide 6: 마무리 -->
@type: content
@title: 작게 만들고, 채점하고, 운영처럼

## 작게 만들고, 채점하고, 운영처럼

8주 PoC를 마무리하며

:::html
<style>
.rp-close { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-4); }
.rp-close .card { word-break: keep-all; text-align: left; }
.rp-close .rp-n { font-size: var(--fs-caption); color: var(--accent); font-weight: var(--weight-bold); letter-spacing: .08em; }
.rp-close-foot { margin-top: var(--space-4); text-align: center; font-size: var(--fs-body); word-break: keep-all; }
.rp-close-foot b { color: var(--accent); }
</style>
<div class="rp-close fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="card"><span class="rp-n">작게 만들고</span><div class="card-title">질문에 나온 개념부터</div><div class="card-desc">어휘 사전과 규칙 파일 하나, 단일 에이전트 하나로 시작합니다.</div></div>
  <div class="card"><span class="rp-n">채점하고</span><div class="card-title">첫 주부터 골든셋</div><div class="card-desc">모델을 바꾸기 전에 지식, 역할, 평가를 바꾸고 그때마다 점수를 잽니다.</div></div>
  <div class="card"><span class="rp-n">운영처럼 데모</span><div class="card-title">점수, 근거, trace를 함께</div><div class="card-desc">데모 데이에 잘 도는 화면과 함께 근거와 실행 경로를 보여 줍니다.</div></div>
</div>
<div class="rp-close-foot fragment fade-up" data-fragment-index="2">오준석, Senior Solutions Architect, AWS Korea: <b>Q&A</b></div>
:::

:::notes
{timing: 1.5min}
[요약]
- 작게 만들고, 첫 주부터 채점하고, 데모는 운영처럼(점수, 근거, trace)
- 네 사례 모두 모델보다 지식, 역할, 평가를 먼저 설계해서 결과를 냄
- 남은 기간 질문은 언제든, 이어서 Q&A

정리하겠습니다. 작게 만들고, 첫 주부터 채점하고, 데모는 운영처럼, 점수와 근거와 trace를 같이 보여주세요.
오늘 보신 LG전자, 신한카드, 미래에셋증권, Canva 모두 모델보다 지식과 역할과 평가를 먼저 설계해서 결과를 냈습니다. 그리고 제가 직접 돌려 본 데모에서도 같은 모델이 지식을 어떻게 주느냐에 따라 50%에서 92%까지 달라졌습니다.
{cue: pause}
남은 기간 동안 언제든 질문 주시면 함께 고민하겠습니다.
{cue: question}
질문 받겠습니다. 온톨로지를 우리 과제의 어디부터 적용하면 좋을지 같은 질문도 환영합니다.
:::

---
<!-- Slide 7: Thank You -->
@type: thankyou
@toc: toc.html
@message: 사례로 보는 AI 에이전트, 감사합니다

# Thank You

:::notes
{timing: 0.5min}
[요약]
- 세션 마무리

들어 주셔서 감사합니다. 오늘 데모 코드와 기록은 공유 자료의 demo 폴더에 있으니, 과제 데이터로 바꿔 직접 돌려 보시길 권합니다.
:::
