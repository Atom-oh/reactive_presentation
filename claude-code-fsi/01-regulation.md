---
remarp: true
block: 01-regulation
---

---
<!-- Slide 1: 세션 커버 -->
@type: cover
@theme: dark

# Claude Code for FSI

5호망 단말에서 AI 코딩 에이전트를 안전하게 도입하는 방법

하나증권, Claude Code on Amazon Bedrock

:::notes
{timing: 0.5min}
[요약]
- 90분 세션, 4부 구성. 규제 경로, 타사 사례와 랜딩존, Gateway와 Hub, 구축 방안과 하네스
- 3부와 4부에 실제 녹화 데모 영상 3편(관리 설정, LLM Gateway, 하네스)
- 주인공은 Claude Code, Codex는 같은 Gateway 뒤에 함께 붙는 보조 클라이언트로 다룸

안녕하세요. 오늘은 하나증권 5호망 단말에서 Claude Code 같은 AI 코딩 에이전트를 어떻게 안전하게 쓸 수 있는지, 규제 경로부터 랜딩존, 아키텍처, 그리고 실제로 돌려 본 데모까지 한 번에 정리해 드리겠습니다.
{cue: question}
지금 사내에서 코딩 어시스턴트를 개인적으로라도 써 보신 분이 얼마나 되시는지 먼저 여쭤봐도 될까요?
{cue: transition}
순서부터 보겠습니다.
:::

---
<!-- Slide 2: 아젠다 -->
@type: agenda
@theme: dark

## 오늘 세션 구성

1. 규제: 세 개의 문 (21분)
2. 타사 사례와 랜딩존, 네트워크 (22분)
3. MCP Hub와 LLM Gateway, 데모 영상 2편 (25분)
4. 구축 방안, 하네스 데모, 도입 경로 (22분)

:::notes
{timing: 1min}
[요약]
- 1부: 어떤 규제 경로로 들어갈 수 있는가 (Playground, 연구개발망, 5호망 혁신금융)
- 2부: KB증권이 지나간 길, 랜딩존 OU, SCP, 5호 단말에서 Bedrock까지의 네트워크
- 3부: MCP Hub와 LLM Gateway 구조, 관리 설정과 Gateway 데모
- 4부: 온프렘과 비교, 단일 통제면, 하네스 데모, 권장 도입 경로와 확인 필요 사항

네 파트로 진행합니다. 1부는 규제 경로, 2부는 타사 사례와 랜딩존, 네트워크입니다. 3부에서 MCP Hub와 LLM Gateway를 보고, 실제 녹화한 데모 두 편을 보여 드립니다. 4부에서는 구축 방안을 비교하고, 하네스 데모와 함께 권장 도입 경로로 마무리합니다.
{cue: transition}
본론 전에, 왜 이 이야기가 이미 현실적인지부터 보겠습니다.
:::

---
<!-- Slide 3: 선행 사례 -->
@type: content
@theme: dark
@title: 같은 증권업에서 이미 문을 통과했다

## 같은 증권업에서 이미 문을 통과했다

:::html
<style>
.cf-muted { color: var(--on-surface-muted); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.cf-src { color: var(--on-surface-muted); font-size: var(--fs-caption); margin-top: var(--space-2); word-break: keep-all; }
.cf-accent  { color: color-mix(in srgb, var(--accent) 72%, var(--on-surface));  font-weight: var(--weight-bold); }
.cf-info    { color: var(--info);    font-weight: var(--weight-bold); }
.cf-success { color: var(--success); font-weight: var(--weight-bold); }
.cf-warning { color: var(--warning); font-weight: var(--weight-bold); }
.cf-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.cf-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.cf-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); }
.cf-big { font-size: var(--text-4xl); font-weight: var(--weight-bold); line-height: 1.1; }
.cf-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.cf-pill { display: inline-block; padding: var(--space-1) var(--space-3); border-radius: var(--radius-pill); background: var(--surface-2); font-size: var(--fs-card); margin: var(--space-1); }
.cf-btns { display: flex; gap: var(--space-2); flex-wrap: wrap; margin-bottom: var(--space-3); }
.cf-btn { border: 1px solid color-mix(in srgb, var(--on-surface) 20%, transparent); background: var(--surface-1); color: var(--on-surface); padding: var(--space-2) var(--space-4); border-radius: var(--radius-pill); font-size: var(--fs-card); cursor: pointer; }
.cf-btn.on { background: var(--accent); color: var(--accent-on); border-color: var(--accent); }
.cf-panel { background: var(--surface-2); border-radius: var(--radius-md); padding: var(--space-4); }
.data-table th { text-transform: none; letter-spacing: normal; }
.data-table td, .data-table th { word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="cf-grid-2">
  <div class="metric-card fragment zoom-in" data-fragment-index="1">
    <div class="cf-big cf-success">적합</div>
    <div class="cf-muted">금융보안원 「생성형 AI 연계 이용 보안대책 평가」에서 국내 금융권 최초 적합 판정 (2026.06). 5호 단말에서 Claude Code를 쓰는 구성</div>
    <div class="cf-src">출처: AWS Financial Services Forum Seoul 2026, KB증권 발표</div>
  </div>
  <div class="metric-card fragment zoom-in" data-fragment-index="2">
    <div class="cf-big cf-accent">28%</div>
    <div class="cf-muted">베타테스터 1명이 1.2만 줄 레거시 코드를 한 달 만에 리팩토링. 코드량 28% 감소, 취약점 제거</div>
    <div class="cf-src">출처: 동일 발표, 디지털데일리 2026.08.27</div>
  </div>
</div>
<div class="callout callout-info fragment fade-up" data-fragment-index="3">
  <strong class="cf-info">오늘의 관점</strong>: 하나증권은 처음 가는 길이 아니라, 검증된 길을 재현하고 더 빨리 통과하는 문제입니다.
</div>
:::

:::notes
{timing: 1.5min}
[요약]
- KB증권이 5호 단말에서 Claude Code를 쓰는 구성으로 금보원 보안대책 평가 '적합'을 받음 (국내 금융권 최초, 2026.06)
- 공개된 성과: 베타테스터 1명, 한 달, 1.2만 줄 레거시, 코드량 28% 감소
- 하나증권에는 "재현과 단축"의 문제

출발점입니다. KB증권이 5호 단말에서 Claude Code를 쓰는 구성으로 금융보안원 적합 판정을 받았습니다. 국내 금융권에서는 처음입니다.
{cue: pause}
공개된 성과도 있습니다. 베타테스터 한 분이 한 달 동안 1만 2천 줄짜리 레거시를 리팩토링해서 코드량을 28% 줄이고 취약점을 걷어냈습니다. 그래서 오늘은 "할 수 있느냐"보다 "같은 길을 얼마나 빨리, 덜 헤매고 갈 수 있느냐"로 보시면 됩니다.
근거: AWS Financial Services Forum Seoul 2026 KB증권 발표, 디지털데일리 2026.08.27 보도
{cue: transition}
그 길이 어떻게 열렸는지, 규제 흐름부터 보겠습니다.
:::

---
<!-- Slide 4: 규제 흐름 -->
@type: content
@theme: dark
@title: 금융 클라우드 규제는 10년간 열려왔다

## 금융 클라우드 규제는 10년간 열려왔다

:::html
<style>
.cf-tl { display: grid; grid-template-columns: repeat(9, 1fr); gap: var(--space-2); margin-bottom: var(--space-4); }
.cf-tl-item { border: 0; background: var(--surface-2); color: var(--on-surface); border-radius: var(--radius-md); padding: var(--space-3) var(--space-2); cursor: pointer; text-align: center; font-size: var(--fs-card); border-top: 4px solid color-mix(in srgb, var(--on-surface) 25%, transparent); }
.cf-tl-item.new { border-top-color: var(--accent); }
.cf-tl-item.on { background: var(--accent-subtle); outline: 2px solid var(--accent); }
.cf-tl-item b { display: block; font-size: var(--fs-body); }
.cf-tl-detail { min-height: 7em; }
.cf-tl-detail h4 { margin: 0 0 var(--space-2); font-size: var(--fs-subtitle); }
</style>
<div class="cf-tl" id="cfTl">
  <button class="cf-tl-item" data-i="0"><b>2016.10</b>비중요</button>
  <button class="cf-tl-item" data-i="1"><b>2019.01</b>중요업무</button>
  <button class="cf-tl-item" data-i="2"><b>2022.11</b>연구개발망</button>
  <button class="cf-tl-item" data-i="3"><b>2023.09</b>SaaS</button>
  <button class="cf-tl-item" data-i="4"><b>2024.08</b>생성형 AI</button>
  <button class="cf-tl-item" data-i="5"><b>2025.02</b>원칙 중심</button>
  <button class="cf-tl-item" data-i="6"><b>2025.04</b>해설서</button>
  <button class="cf-tl-item new" data-i="7"><b>2026.04</b>모델 변경</button>
  <button class="cf-tl-item new" data-i="8"><b>2026.05~07</b>전면 해제 검토</button>
</div>
<div class="cf-panel cf-tl-detail" id="cfTlDetail"><h4>시점을 눌러 보세요</h4><div class="cf-muted">주황 표시는 올해 바뀐 두 가지입니다.</div></div>
<div class="callout callout-warning fragment fade-up" data-fragment-index="1">
  <strong class="cf-warning">기다리지 않는 이유</strong>: 방향은 전면 해제로 정해졌지만 일정은 불확실합니다. 지금 갖추는 통제가 향후 선별 대상이 되는 근거가 됩니다.
</div>
:::

:::script
(function () {
  var data = [
    ['2016.10', '비중요 정보처리시스템에 대한 퍼블릭 클라우드 활용 허용'],
    ['2019.01', '전자금융감독규정 개정으로 클라우드 이용 확대 (중요업무 포함)'],
    ['2022.11', '연구개발 목적 망분리 완화 조치 시행'],
    ['2023.09', '혁신금융서비스 제도를 통한 SaaS 제한적 허용'],
    ['2024.08', '망분리 개선 로드맵: 혁신금융서비스로 SaaS 확대, 생성형 AI 활용 허용'],
    ['2025.02', '원칙 중심 전자금융감독규정 개정, 자율보안체제 유도'],
    ['2025.04', '금융보안원 「연구개발 목적 망분리 예외 적용 보안 해설서」'],
    ['2026.04', '생성형 AI 모델 변경 절차 간소화: 경미, 보통, 상당 3단계. 지정 후 모델 버전 교체 부담이 줄어듦'],
    ['2026.05~07', '선별 금융사 대상 망분리 전면 해제 검토 공식화. 시점은 미정']
  ];
  var bar = document.getElementById('cfTl'), out = document.getElementById('cfTlDetail');
  if (!bar) return;
  bar.addEventListener('click', function (e) {
    var b = e.target.closest('.cf-tl-item'); if (!b) return;
    bar.querySelectorAll('.cf-tl-item').forEach(function (x) { x.classList.remove('on'); });
    b.classList.add('on');
    var d = data[+b.dataset.i];
    out.innerHTML = '<h4>' + d[0] + '</h4><div class="cf-muted">' + d[1] + '</div>';
  });
})();
:::

:::notes
{timing: 2min}
[요약]
- 2016년 비중요 시스템부터 2025년 원칙 중심 규정까지 단계적으로 완화
- 올해 바뀐 두 가지: 2026.04 모델 변경 절차 간소화(경미, 보통, 상당), 2026.05~7 전면 해제 검토 공식화
- 전면 해제 시점은 미정. 기다리는 전략은 권하지 않음

규제 흐름입니다. 시점을 하나씩 눌러 보면서 말씀드리겠습니다. 2016년에 비중요 시스템부터 시작해서, 2019년 중요업무, 2022년 연구개발망 완화, 2024년에는 생성형 AI 활용까지 열렸습니다.
{cue: demo}
주황색으로 표시한 2026년 두 칸을 눌러 주세요. 4월에 모델을 바꿀 때 절차가 세 단계로 간소화됐고, 5월부터 7월 사이에 전면 해제 검토가 공식화됐습니다.
{cue: pause}
다만 전면 해제가 언제 되는지는 정해지지 않았습니다. 그래서 기다리기보다, 지금 통제를 갖춰 두는 쪽이 나중에 선별 대상이 될 때도 근거가 됩니다.
{cue: transition}
그럼 지금 들어갈 수 있는 문이 몇 개인지 보겠습니다.
:::

---
<!-- Slide 5: 세 환경의 위치 -->
@type: content
@theme: dark
@title: 어느 단말에서 출발하느냐가 근거를 정한다

## 어느 단말에서 출발하느냐가 근거를 정한다

:::html
<style>
.cf-map { display: grid; grid-template-columns: 1.15fr 0.35fr 1fr; gap: var(--space-3); align-items: stretch; }
.cf-zone { border: 2px dashed color-mix(in srgb, var(--on-surface) 25%, transparent); border-radius: var(--radius-md); padding: var(--space-3); display: flex; flex-direction: column; gap: var(--space-2); transition: opacity var(--duration-normal), border-color var(--duration-normal); }
.cf-zone h5 { margin: 0; font-size: var(--fs-card); color: var(--on-surface-muted); }
.cf-node { background: var(--surface-2); border-radius: var(--radius-sm); padding: var(--space-2) var(--space-3); font-size: var(--fs-card); display: flex; align-items: center; gap: var(--space-2); }
.cf-node img { width: 32px; height: 32px; }
.cf-links { display: flex; flex-direction: column; justify-content: space-around; gap: var(--space-2); }
.cf-link { text-align: center; font-size: var(--fs-card); padding: var(--space-2); border-radius: var(--radius-sm); background: var(--surface-2); transition: opacity var(--duration-normal); }
.cf-map[data-path] .cf-p { opacity: 0.25; }
.cf-map[data-path="1"] .p1, .cf-map[data-path="2"] .p2, .cf-map[data-path="3"] .p3 { opacity: 1; border-color: var(--accent); }
.cf-map[data-path="1"] .cf-link.p1, .cf-map[data-path="2"] .cf-link.p2, .cf-map[data-path="3"] .cf-link.p3 { background: var(--accent); color: var(--accent-on); }
.cf-x { color: var(--danger); font-weight: var(--weight-bold); }
.cf-path-msg { margin-top: var(--space-3); min-height: 3.2em; }
</style>
<div class="cf-btns" onclick="(function(e){var b=e.target.closest('.cf-btn');if(!b)return;var m=document.getElementById('cfMap');b.parentNode.querySelectorAll('.cf-btn').forEach(function(x){x.classList.toggle('on',x===b)});m.setAttribute('data-path',b.dataset.p);var msg={1:'① Playground: 인터넷망 PC에서 출발. 사내망과는 선이 아예 없고, 승인 모델만 씁니다.',2:'② 연구개발망: 별도 망. 전산실로는 망연계 솔루션을 통해 한 방향으로만 보낼 수 있습니다.',3:'③ 5호망: 단말은 Bedrock을 직접 부르지 않습니다. 전산실 Gateway를 거쳐 전용회선(DX)으로만 나갑니다.'};document.getElementById('cfPathMsg').innerHTML='<strong class=&quot;cf-accent&quot;>'+msg[b.dataset.p]+'</strong>'})(event)">
  <button class="cf-btn" data-p="1">① AI Playground</button>
  <button class="cf-btn" data-p="2">② 연구개발망</button>
  <button class="cf-btn" data-p="3">③ 5호망 + 혁신금융</button>
</div>
<div class="cf-map" id="cfMap" data-reveal="static">
  <div class="cf-stack">
    <div class="cf-zone cf-p p3"><h5>온프렘 전산실 (5호망)</h5>
      <div class="cf-node">5호 단말: Claude Code</div>
      <div class="cf-node">LLM Gateway, MCP 중계, 망연계 솔루션 (수신)</div>
    </div>
    <div class="cf-zone cf-p p2"><h5>연구개발망</h5>
      <div class="cf-node">연구개발 단말(NAC, DLP, DRM), 망연계 솔루션 (송신), VPN</div>
    </div>
    <div class="cf-zone cf-p p1"><h5>인터넷망</h5>
      <div class="cf-node">인터넷 PC <span class="cf-x">✕ 사내망 미연결</span></div>
    </div>
  </div>
  <div class="cf-links">
    <div class="cf-link cf-p p3">③ DX</div>
    <div class="cf-link cf-p p2">② VPN<br>망연계 단방향</div>
    <div class="cf-link cf-p p1">① 인터넷</div>
  </div>
  <div class="cf-stack">
    <div class="cf-zone cf-p p3"><h5>AWS 서울 리전: Workloads OU, AI Platform</h5>
      <div class="cf-node"><img src="common/aws-icons/services/Arch_Amazon-Bedrock_48.svg" alt="">Bedrock, AgentCore (PrivateLink only)</div>
    </div>
    <div class="cf-zone cf-p p2"><h5>R&amp;D OU: 연구개발망</h5>
      <div class="cf-node">개발 VPC, SWG/CASB 경유 인터넷</div>
    </div>
    <div class="cf-zone cf-p p1"><h5>Sandbox OU: Playground</h5>
      <div class="cf-node">승인 모델만, 사내망 미연결</div>
    </div>
  </div>
</div>
<div class="cf-panel cf-path-msg" id="cfPathMsg"><span class="cf-muted">위 버튼으로 경로를 하나씩 켜 보세요. 공통 원칙: 단말에서 Bedrock 직접 호출은 불가, 인터넷망과 연구개발망은 차단</span></div>
:::

:::notes
{timing: 2.5min}
[요약]
- 같은 Bedrock을 써도 출발 단말이 법적 근거를 정함
- ① Playground: 인터넷망 PC, 사내망과 선 없음
- ② 연구개발망: 별도 망, 전산실로는 망연계 단방향만
- ③ 5호망: 단말은 Bedrock 직접 호출 불가, 전산실 Gateway 경유 후 DX로만

한 장으로 세 환경의 위치를 보여 드립니다. 위 버튼을 하나씩 눌러 보겠습니다.
{cue: demo}
1번 Playground는 인터넷망 PC에서 출발하고 사내망과는 아예 연결이 없습니다. 2번 연구개발망은 별도 망이고, 전산실로는 망연계 솔루션을 통해 한 방향으로만 보낼 수 있습니다.
{cue: pause}
3번이 오늘의 핵심인 5호망 경로입니다. 단말이 Bedrock을 직접 부르지 않고, 전산실의 Gateway를 거쳐 전용회선으로 나갑니다. 오른쪽 AWS 쪽도 환경마다 OU가 다릅니다. 이 OU 이야기는 2부에서 자세히 하겠습니다.
{cue: transition}
세 환경이 실제로 어떻게 다른지, 망 연결과 파일 흐름으로 비교해 보겠습니다.
:::

---
<!-- Slide 6: 망 연결과 파일 흐름 -->
@type: content
@theme: dark
@title: 파일이 오가는 지점을 하나로 좁힌다

## 파일이 오가는 지점을 하나로 좁힌다

:::html
<style>
.cf-env-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-3); }
.cf-env-grid .card { padding: var(--space-3); }
.cf-env-grid strong { display: block; margin-bottom: var(--space-1); }
</style>
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">① AI Playground</button>
  <button class="tab-btn">② 연구개발망</button>
  <button class="tab-btn">③ 5호망 + 혁신금융</button>
</div>
<div class="tc">
  <div class="cf-env-grid" data-reveal="stagger">
    <div class="card"><strong class="cf-accent">출발 단말, 사내망</strong><div class="cf-muted">인터넷망 PC. 업무망, 운영망 단말은 직접 접속 불가. 운영계, 고객계 미연계</div></div>
    <div class="card"><strong class="cf-accent">AWS 연결 경로</strong><div class="cf-muted">인터넷 → 중앙 Gateway → 승인 모델. 외부 SaaS는 승인 Endpoint만</div></div>
    <div class="card"><strong class="cf-warning">파일 업로드, 반입, 반출</strong><div class="cf-muted">MVP 단계는 업로드 비활성화 권장. 필요 시 PDF/TXT 등 확장자와 용량만. 사내 반입, 반출 모두 불가</div></div>
    <div class="card"><strong class="cf-success">핵심 통제</strong><div class="cf-muted">입력 패턴 탐지, 사용량 한도</div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="cf-env-grid">
    <div class="card"><strong class="cf-accent">출발 단말, 사내망</strong><div class="cf-muted">연구개발 전용 단말(NAC 인증만). 내부업무망과 논리적 분리, 전산실과는 단방향 망간전송만. 무선 차단(§15⑥)</div></div>
    <div class="card"><strong class="cf-accent">AWS 연결 경로</strong><div class="cf-muted">데이터센터 ↔ AWS 연구개발망 VPN. 재택은 IDP 인증 + Client VPN. 외부는 SWG/Proxy, CASB 화이트리스트</div></div>
    <div class="card"><strong class="cf-warning">파일 반입, 반출</strong><div class="cf-muted">전산실 → 연구개발망은 원칙적 불가(CISO 승인 + 정보보호위원회 의결 후 산출물만). 반대 방향은 망연계 단방향만</div></div>
    <div class="card"><strong class="cf-success">핵심 통제</strong><div class="cf-muted">방화벽, NGFW/IPS, SSE, DLP/DRM, NAC, EDR. 반출 주체는 인가된 형상관리 서버만, 한시적 연결</div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="cf-env-grid">
    <div class="card"><strong class="cf-accent">출발 단말, 사내망</strong><div class="cf-muted">기존 5호 단말. 전산실 내부, 운영계 연계는 지정 범위 안에서만. 기존 5호망 통제 유지</div></div>
    <div class="card"><strong class="cf-accent">AWS 연결 경로</strong><div class="cf-muted">DX → TGW → PrivateLink. 단말 직접 호출 불가, 전산실 Gateway 경유. 인터넷 경로 없음</div></div>
    <div class="card"><strong class="cf-warning">파일 반입, 반출</strong><div class="cf-muted">코드가 이미 전산실 안에 있어 반입, 반출 개념 없음. 밖으로 나가는 것은 Gateway DLP를 통과한 프롬프트뿐</div></div>
    <div class="card"><strong class="cf-success">핵심 통제</strong><div class="cf-muted">기존 5호망 통제 + LLM Gateway(DLP, 로깅). 3부 데모에서 실제로 보여 드립니다</div></div>
  </div>
</div>
<div class="callout callout-info fragment fade-up" data-fragment-index="1"><strong class="cf-info">연구개발망의 트레이드오프</strong>: "개발은 클라우드에서, 반영은 망연계로". 통제와 감사는 쉬워지지만, 개발 속도는 망연계 절차가 결정합니다.</div>
:::

:::notes
{timing: 2.5min}
[요약]
- 원본 두 표(네트워크 연동, 파일과 소스코드)를 환경별 탭으로 재구성
- Playground: 들어가는 것도 나오는 것도 막음
- 연구개발망: 전산실로 가는 한 방향만 망연계로 열고, 반대는 CISO 승인 + 정보보호위원회 의결
- 5호망: 코드는 이미 안에 있고, 나가는 것은 파일이 아니라 Gateway가 검사한 프롬프트
- 출처: 메가존클라우드 「연구개발망 구축시 고려사항」

앞 장의 그림을 환경별로 풀었습니다. 탭을 하나씩 넘기겠습니다.
{cue: demo}
Playground는 인터넷망 PC에서만 쓰고, 파일은 들어가는 것도 나오는 것도 막습니다. 연구개발망은 전산실로 보내는 한 방향만 망연계 솔루션으로 열고, 반대 방향은 CISO 승인과 정보보호위원회 의결이 있어야 합니다.
{cue: pause}
5호망은 코드가 이미 전산실 안에 있습니다. 그래서 반입, 반출이라는 개념이 없고, 밖으로 나가는 건 파일이 아니라 프롬프트입니다. 그 프롬프트를 Gateway가 검사합니다. 이 장면은 3부 데모에서 실제로 보여 드리겠습니다.
근거: 메가존클라우드 「연구개발망 구축시 고려사항」(원본 제안서 7, 8장 표)
{cue: transition}
연구개발망을 고르면 망연계 절차가 속도를 좌우한다고 했는데, 그 절차를 보겠습니다.
:::

---
<!-- Slide 7: 망연계 6단계 -->
@type: content
@theme: dark
@title: 망연계는 6단계, 병목은 승인 대기

## 망연계는 6단계, 병목은 승인 대기

:::html
<style>
.cf-steps { display: grid; grid-template-columns: repeat(6, 1fr); gap: var(--space-2); margin-bottom: var(--space-3); }
.cf-step { background: var(--surface-2); border-radius: var(--radius-md); padding: var(--space-3); font-size: var(--fs-card); position: relative; }
.cf-step b { display: block; color: color-mix(in srgb, var(--accent) 72%, var(--on-surface)); font-size: var(--fs-body); }
.cf-step .z { display: block; color: var(--on-surface-muted); font-size: var(--fs-caption); margin-bottom: var(--space-1); }
.cf-step.wait { outline: 2px solid var(--warning); }
</style>
<div class="cf-steps" data-reveal="stagger" data-reveal-anim="right">
  <div class="cf-step"><span class="z">AWS 연구개발망</span><b>1 전송 신청</b>Code Repository에서 Git 소스 전송 신청</div>
  <div class="cf-step wait"><span class="z">AWS 연구개발망</span><b>2 전송 승인</b>승인권자 승인</div>
  <div class="cf-step"><span class="z">데이터센터 연구개발망</span><b>3 망연계로 전송</b>Git → 망연계 솔루션</div>
  <div class="cf-step"><span class="z">데이터센터 연구개발망</span><b>4 목록 조회</b>전송 대상 확인, 선택</div>
  <div class="cf-step wait"><span class="z">전산실</span><b>5 망연계 승인</b>망연계 단계 승인, 신청</div>
  <div class="cf-step"><span class="z">전산실</span><b>6 반영, 기록</b>전산실 GitLab 수신, 전송 이력 기록</div>
</div>
<table class="data-table fragment fade-up" data-fragment-index="1">
  <thead><tr><th>통제</th><th>내용</th></tr></thead>
  <tbody>
    <tr><td>전송 방향</td><td>연구개발망 → 전산실 단방향, 한시적 연결</td></tr>
    <tr><td>사전 점검, 수신 검증</td><td>시큐어코딩 점검, 악성코드 검사. 수신 서버에서 무결성(해시), 바이너리 검증</td></tr>
    <tr><td>파일 통제</td><td>유형, 용량 제한, 암호 걸린 파일 금지, 중요정보, 개인신용정보 포함 여부 검토 후 반출</td></tr>
    <tr><td>통신, 기록</td><td>IPS, 보안 모니터링. 망간 파일 이동 내역 기록, 보관, 주기 점검</td></tr>
  </tbody>
</table>
<div class="callout callout-warning fragment fade-up" data-fragment-index="2"><strong class="cf-warning">리스크</strong>: 노란 테두리(2, 5단계) 승인 대기가 길어지면 연구개발망의 장점이 줄어듭니다. 승인 SLA와 자동 검증(SAST, 악성코드 검사)을 함께 설계해야 합니다.</div>
<div class="cf-src">출처: 메가존클라우드 「연구개발망 구축시 고려사항」 p26, p29</div>
:::

:::notes
{timing: 2min}
[요약]
- 신청, 승인, 전송, 선택, 다시 승인, 반영과 기록의 6단계
- 사람이 승인하는 단계가 두 번(2, 5단계): 병목 지점
- 각 구간에 악성코드 검사, 무결성 검증
- 권고: 승인 SLA + SAST, 악성코드 자동 검증을 함께 설계

연구개발망에서 만든 코드를 전산실로 반영하는 절차입니다. 신청, 승인, 전송, 선택, 다시 승인, 반영과 기록까지 여섯 단계입니다.
{cue: pause}
노란 테두리 두 곳이 사람이 승인하는 단계입니다. 코딩 에이전트로 하루에 여러 번 커밋하는데 반영이 승인 대기에 묶이면, 연구개발망을 쓰는 의미가 줄어듭니다. 그래서 승인 SLA와 자동 검증을 같이 설계하시길 권합니다.
근거: 메가존클라우드 「연구개발망 구축시 고려사항」 p26, p29
{cue: transition}
세 환경을 한 표로 놓고 비교해 보겠습니다.
:::

---
<!-- Slide 8: 3자 비교 -->
@type: content
@theme: dark
@title: 운영계와 실제 코드에 닿는 길은 하나

## 운영계와 실제 코드에 닿는 길은 하나

:::html
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">성격과 근거</button>
  <button class="tab-btn">단말과 인프라</button>
  <button class="tab-btn">결과: 기간과 활용</button>
</div>
<div class="tc">
  <table class="data-table">
    <thead><tr><th>비교축</th><th>AI Playground</th><th>연구개발망</th><th>5호망 + 혁신금융</th></tr></thead>
    <tbody>
      <tr><td>성격</td><td>프롬프트, 모델 체험용 테스트 콘솔</td><td>독립된 정식 R&amp;D 인프라</td><td>기존 IT 개발, 운영 단말에 AI 연계</td></tr>
      <tr><td>법적 근거</td><td>비조치의견서 / 사내 정책 (확인 필요)</td><td>전자금융감독규정 §15 연구개발망 예외 (조항 확인 필요)</td><td>혁신금융서비스 지정 (망분리 특례)</td></tr>
      <tr><td>승인 주체</td><td>CISO, 정보보호 조직</td><td>내부 정보보호위원회</td><td>금융위 지정 + 금보원 이행점검</td></tr>
      <tr><td>허용 데이터</td><td>공개, 샘플 (고객정보 입력 금지)</td><td>가명, 더미 (실데이터 금지)</td><td>지정 범위 업무 데이터, 개인정보 필터링 전제</td></tr>
    </tbody>
  </table>
</div>
<div class="tc" hidden>
  <table class="data-table">
    <thead><tr><th>비교축</th><th>AI Playground</th><th>연구개발망</th><th>5호망 + 혁신금융</th></tr></thead>
    <tbody>
      <tr><td>단말</td><td>인터넷망 PC</td><td>연구개발 전용 단말</td><td>기존 5호 단말 + AI 이용 통제</td></tr>
      <tr><td>네트워크</td><td>인터넷 → 중앙 Gateway</td><td>독립 VPC, SSE로 인터넷 통제</td><td>전산실 Gateway → DX → PrivateLink</td></tr>
      <tr><td>소스코드</td><td>반입 불가</td><td>망연계 단방향 + 반출 승인</td><td>사내 코드 직접 활용, 입력 필터링, 로깅</td></tr>
      <tr><td>운영계 연계</td><td>불가</td><td>불가</td><td><strong class="cf-success">지정 범위 내 가능</strong></td></tr>
    </tbody>
  </table>
</div>
<div class="tc" hidden>
  <table class="data-table">
    <thead><tr><th>비교축</th><th>AI Playground</th><th>연구개발망</th><th>5호망 + 혁신금융</th></tr></thead>
    <tbody>
      <tr><td>체감 기간</td><td>수주</td><td>수개월 (내부 의결 + 망 구축)</td><td>약 1년 (KB증권 사례)</td></tr>
      <tr><td>Coding Agent 활용</td><td>학습, 실험</td><td>실데이터 없는 코드베이스 전면 활용</td><td><strong class="cf-success">실제 업무 코드베이스 + 운영 도구 연계</strong></td></tr>
    </tbody>
  </table>
  <div class="callout callout-success" data-reveal="stagger"><strong class="cf-success">결정적인 두 줄</strong>: 운영계와 실제 업무 코드에 닿을 수 있는 건 5호망 경로뿐이고, 대신 약 1년이 걸립니다.</div>
</div>
<div class="callout callout-warning fragment fade-up" data-fragment-index="1"><strong class="cf-warning">리스크</strong>: 연구개발망 조항 번호는 자료마다 표기가 다릅니다(제15조 제5호 가목 vs §15①3 가목). 규정 원문으로 확정한 뒤 반영합니다.</div>
:::

:::notes
{timing: 2min}
[요약]
- 고객 요청 3자 비교를 성격과 근거, 단말과 인프라, 결과 3개 탭으로 나눔
- 결정적인 두 줄: 운영계 연계와 Coding Agent 활용 범위
- 5호망만 실업무 코드와 운영계에 닿음, 대신 약 1년
- 연구개발망 조항 번호는 원문 대조 후 확정

하나증권에서 요청하신 3자 비교입니다. 탭 세 개로 나눴습니다. 첫 탭은 성격, 근거, 승인 주체, 데이터입니다.
{cue: demo}
두 번째 탭에서 운영계 연계 줄을 봐 주세요. Playground와 연구개발망은 둘 다 불가입니다. 세 번째 탭이 결론입니다. 운영계와 실제 업무 코드베이스에 닿을 수 있는 건 5호망 경로뿐이고, 대신 1년 정도 걸립니다.
{cue: pause}
조항 번호는 자료마다 표기가 달라서, 원문으로 확인한 뒤 확정하겠습니다.
{cue: transition}
통제 항목으로 보면 어떤 차이가 있는지 보겠습니다.
:::

---
<!-- Slide 9: 통제 매트릭스 -->
@type: content
@theme: dark
@title: 연구개발망과 5호망, 통제는 거의 같다

## 연구개발망과 5호망, 통제는 거의 같다

:::html
<style>
.cf-mx td:nth-child(2), .cf-mx td:nth-child(3), .cf-mx td:nth-child(4), .cf-mx th:nth-child(2), .cf-mx th:nth-child(3), .cf-mx th:nth-child(4) { text-align: center; transition: background var(--duration-normal); }
.cf-mx[data-col="2"] td:nth-child(2), .cf-mx[data-col="3"] td:nth-child(3), .cf-mx[data-col="4"] td:nth-child(4) { background: var(--accent-subtle); font-weight: var(--weight-bold); }
.cf-mx[data-col="diff"] tr.diff td { background: var(--warning-subtle); }
.cf-mx td { padding-top: var(--space-1); padding-bottom: var(--space-1); }
</style>
<div class="cf-btns" onclick="(function(e){var b=e.target.closest('.cf-btn');if(!b)return;b.parentNode.querySelectorAll('.cf-btn').forEach(function(x){x.classList.toggle('on',x===b)});document.getElementById('cfMx').setAttribute('data-col',b.dataset.c)})(event)">
  <button class="cf-btn" data-c="2">Playground</button>
  <button class="cf-btn" data-c="3">연구개발망</button>
  <button class="cf-btn" data-c="4">5호망</button>
  <button class="cf-btn" data-c="diff">연구개발망과 5호망이 다른 행</button>
</div>
<table class="data-table cf-mx" id="cfMx">
  <thead><tr><th>통제 영역</th><th>Playground</th><th>연구개발망</th><th>5호망</th><th>AWS 구현 수단</th></tr></thead>
  <tbody>
    <tr><td>범위 (목적 한정)</td><td>●</td><td>●</td><td>●</td><td>이용 고지, 정보보호위원회 의결</td></tr>
    <tr><td>독립 네트워크, 접속 경로</td><td>◐</td><td>●</td><td>●</td><td>전용 VPC, TGW RT 분리, DX / Client VPN / PrivateLink</td></tr>
    <tr><td>접속 단말, 인증, 권한</td><td>◐</td><td>●</td><td>●</td><td>NAC, EDR, MDM + IAM Identity Center + IdP, MFA</td></tr>
    <tr><td>인터넷, SaaS</td><td>●</td><td>●</td><td>●</td><td>SSE(SWG/CASB), Network Firewall (5호망은 경로 없음)</td></tr>
    <tr class="diff"><td>망간 전송</td><td>○</td><td>●</td><td>○</td><td>망연계 솔루션 (연구개발망 → 전산실)</td></tr>
    <tr><td>계정 분리</td><td>◐</td><td>●</td><td>●</td><td>Control Tower, OU</td></tr>
    <tr><td>리전, 데이터 위치</td><td>●</td><td>●</td><td>●</td><td>SCP 리전 제한 (Bedrock은 승인 CRIS 프로파일만 예외)</td></tr>
    <tr><td>가명, 민감정보, 로그</td><td>●</td><td>●</td><td>●</td><td>Gateway DLP, Macie, CloudTrail → Log Archive, Invocation Logging</td></tr>
    <tr class="diff"><td>비용, 사용량</td><td>●</td><td>◐</td><td>●</td><td>Gateway Quota, AWS Budgets</td></tr>
  </tbody>
</table>
<div class="cf-src">● 필수 ◐ 권장 ○ 해당 없음. 메가존 가이드의 통제 영역 기준 권장안이며, 최종 등급은 하나증권 정보보호 정책으로 확정합니다.</div>
:::

:::notes
{timing: 2min}
[요약]
- 통제 영역별 필수, 권장, 해당 없음 (원본 12행을 연관 행끼리 묶어 9행)
- 연구개발망과 5호망 열은 두 행(망간 전송, 비용)만 다름
- 의미: 연구개발망을 먼저 갖춰도 5호망으로 넘어갈 때 추가로 할 일이 적음. 반대로 5호망을 바로 가도 빠지는 통제가 거의 없음
- 등급은 권장안, 최종은 하나증권 정책

통제 항목을 환경별로 필수, 권장, 해당 없음으로 나눴습니다. 버튼으로 열을 하나씩 켜 보겠습니다.
{cue: demo}
마지막 버튼, "연구개발망과 5호망이 다른 행"을 누르면 두 줄만 노랗게 표시됩니다. 망간 전송과 비용입니다. 나머지는 같습니다.
{cue: pause}
즉 통제 관점에서는 연구개발망과 5호망이 거의 같은 수준을 요구합니다. 그렇다면 같은 노력으로 실업무 코드에 닿을 수 있는 쪽을 고르는 게 합리적이라는 이야기로 이어집니다. 최종 등급은 하나증권 정보보호 정책으로 확정합니다.
{cue: transition}
그 선택을 두 개의 문으로 정리해 보겠습니다.
:::

---
<!-- Slide 10: 두 개의 문 -->
@type: content
@theme: dark
@title: 문은 두 개, 권장은 PATH B

## 문은 두 개, 권장은 PATH B

:::html
<div class="cf-muted">세 환경 중 Playground는 체험용이라, 실업무 코드로 들어가는 문은 두 개입니다.</div>
<div class="compare-toggle">
  <button class="compare-btn active" data-compare="a">PATH A: 연구개발망</button>
  <button class="compare-btn" data-compare="b">PATH B: 5호망 + 혁신금융</button>
</div>
<div class="compare-content active" data-compare="a">
  <div class="cf-grid-2">
    <div class="card"><strong class="cf-accent">근거와 승인</strong><div class="cf-muted">제15조 연구개발망 예외(조항 확인 필요). 내부 정보보호위원회. 혁신금융 지정 불필요</div></div>
    <div class="card"><strong class="cf-accent">기간</strong><div class="cf-muted">내부 절차 중심이라 상대적으로 짧음</div></div>
    <div class="card"><strong class="cf-warning">데이터와 업무</strong><div class="cf-muted">개인정보 기본적으로 처리 불가. 연구개발 용도에 한정</div></div>
    <div class="card"><strong class="cf-danger">인프라</strong><div class="cf-muted">완전한 망분리 전제. Network, Security, Gateway, 로그를 5호망과 공유하지 못하고 독립적으로 신규 구축</div></div>
  </div>
</div>
<div class="compare-content" data-compare="b">
  <div class="cf-grid-2">
    <div class="card"><strong class="cf-accent">근거와 승인</strong><div class="cf-muted">혁신금융서비스 지정(망분리 특례). 금융위원회 + 금융보안원 이행점검. 연구개발망 구축 불필요</div></div>
    <div class="card"><strong class="cf-accent">기간</strong><div class="cf-muted">선행 사례 기준 약 1년</div></div>
    <div class="card"><strong class="cf-success">데이터와 업무</strong><div class="cf-muted">개인정보는 필터링 필수. 필터링 전제로 실업무까지 확장 가능</div></div>
    <div class="card"><strong class="cf-success">인프라</strong><div class="cf-muted">5호망 랜딩존, Gateway, Security를 그대로 활용. 상용 AI 프로젝트도 같은 통제면에 합류</div></div>
  </div>
</div>
<div class="callout callout-success fragment zoom-in" data-fragment-index="1"><strong class="cf-success">권장: PATH B</strong>. 연구개발망은 같은 구성을 한 벌 더 만들어야 하고, 그래도 실업무 코드와 운영계에는 닿지 못합니다.</div>
:::

:::notes
{timing: 2min}
[요약]
- PATH A 연구개발망: 내부 의결, 비교적 짧음, 실데이터 금지, 인프라 신규 구축
- PATH B 5호망 + 혁신금융: 금융위 지정 + 금보원 점검, 약 1년, 필터링 전제로 실업무 확장
- 결정적 차이는 인프라 공유 여부
- 권장은 PATH B

세 환경 중 Playground는 체험용이라, 실업무 코드로 들어가는 문은 결국 두 개입니다. 두 경로를 나란히 놓으면 이렇습니다. 토글로 왼쪽, 오른쪽을 바꿔 보겠습니다.
{cue: demo}
PATH A는 내부 절차라 빠르지만, 빨간색으로 표시한 인프라 칸이 중요합니다. 연구개발망은 완전한 망분리가 전제라서, 5호망에 만든 Gateway나 보안 장비를 같이 쓸 수 없습니다. 네트워크부터 보안, Gateway, 로그까지 한 벌을 새로 만들어야 합니다.
{cue: pause}
PATH B는 1년 정도 걸리지만, 5호망 랜딩존과 Gateway를 그대로 쓰고 실업무까지 확장할 수 있습니다. 그래서 저희 권고는 5호망에 구축하는 것입니다.
{cue: transition}
PATH B를 택하면 어떤 절차를 거치는지 보겠습니다.
:::

---
<!-- Slide 11: PATH B 절차와 일정 -->
@type: content
@theme: dark
@title: 지정이 끝이 아니다, 이행점검까지

## 지정이 끝이 아니다, 이행점검까지

:::html
<style>
.cf-pb { display: grid; grid-template-columns: 1.25fr 1fr; gap: var(--space-4); }
.cf-proc { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-2); }
.cf-proc div { background: var(--surface-2); border-radius: var(--radius-sm); padding: var(--space-2) var(--space-3); font-size: var(--fs-card); border-left: 4px solid color-mix(in srgb, var(--on-surface) 20%, transparent); }
.cf-proc div.us { border-left-color: var(--accent); }
.cf-proc div.gov { border-left-color: var(--info); }
.cf-proc b { display: block; }
.cf-kb li { margin-bottom: var(--space-2); font-size: var(--fs-card); }
.cf-kb b { color: color-mix(in srgb, var(--accent) 72%, var(--on-surface)); margin-right: var(--space-2); }
.cf-legend { font-size: var(--fs-caption); color: var(--on-surface-muted); margin-top: var(--space-2); }
</style>
<div class="cf-pb">
  <div>
    <div class="cf-proc" data-reveal="stagger">
      <div class="us"><b>① 보안대책 수립</b>리스크 기반, 부가조건 대비</div>
      <div class="gov"><b>② 보안대책 컨설팅</b>금감원, 금보원: 적절성, 취약점</div>
      <div class="us"><b>③ 지정 신청</b>회차별 접수 기간에 제출</div>
      <div class="gov"><b>④ 심사 및 지정</b>혁신금융심사위원회 → 금융위 의결</div>
      <div class="us"><b>⑤ 보안대책 이행</b>수립한 대책 구현</div>
      <div class="gov"><b>⑥ 개시 전 이행점검</b>금보원: 보안조치 구비 여부</div>
      <div class="us"><b>⑦ 결과 제출</b>부가조건 이행 결과 (금융위, 금감원)</div>
      <div class="us"><b>⑧ 서비스 개시</b>생성형 AI 업무 이용 시작</div>
    </div>
    <div class="cf-legend">주황 막대: 자사 주관, 파란 막대: 당국 주관</div>
  </div>
  <div class="cf-panel fragment fade-left" data-fragment-index="1">
    <strong class="cf-accent">KB증권 공개 경과</strong>
    <ul class="cf-kb">
      <li><b>2025.07</b>사내 MCP 생태계 설계, 연동 PoC</li>
      <li><b>2025.09</b>3분기 혁신금융서비스 지정 신청</li>
      <li><b>2025.10</b>핀테크지원센터 접수 → 금감원 검토 (N차 보완)</li>
      <li><b>2026.01</b>혁신금융서비스 지정</li>
      <li><b>2026.06</b>금보원 이행평가 '적합'</li>
    </ul>
    <div class="cf-muted">신청 → 지정 약 4개월, 지정 → 적합 약 5개월</div>
  </div>
</div>
<div class="callout callout-info fragment fade-up" data-fragment-index="2"><strong class="cf-info">기간을 줄이는 곳</strong>: ③ 회차별 접수입니다. ①②를 먼저 끝내고 회차에 맞춰 넣어야 전체 기간이 줄어듭니다. 2026.04.15 간소화로 지정 후 모델 버전 교체 부담은 줄었습니다.</div>
:::

:::notes
{timing: 2min}
[요약]
- 8단계: 수립, 컨설팅, 신청, 지정, 이행, 이행점검, 결과 제출, 개시
- KB증권: PoC 2025.07 → 신청 2025.09 → 지정 2026.01 → 적합 2026.06
- 신청부터 적합까지 약 9개월, PoC부터 약 1년
- N차 보완: 신청 서류를 미리 완성해 두는 것이 가장 확실한 단축 방법
- 용어: 부가조건(지정과 함께 부과되는 이행 의무), 이행점검(대책이 실제 적용됐는지 확인)

왼쪽이 여덟 단계 절차, 오른쪽이 KB증권의 실제 일정입니다. 지정을 받는 게 끝이 아니라, 개시 전에 금보원 이행점검까지 통과해야 서비스를 시작할 수 있습니다.
{cue: pause}
KB증권은 신청부터 적합까지 대략 9개월, PoC부터 보면 1년이 걸렸습니다. 중간에 보완 요청이 여러 번 있었으니, 신청 서류를 미리 완성해 두고 회차에 맞춰 넣는 게 기간을 줄이는 가장 확실한 방법입니다.
{cue: transition}
1부를 정리하겠습니다.
:::

---
<!-- Slide 12: 1부 Key Takeaways -->
@type: content
@theme: dark
@title: 1부 정리: 문은 5호망으로 연다

## 1부 정리: 문은 5호망으로 연다

:::html
<div class="cf-grid-3" data-reveal="stagger">
  <div class="card"><strong class="cf-accent">출발 단말이 근거를 정한다</strong><div class="cf-muted">같은 Bedrock이어도 인터넷 PC, 연구개발 단말, 5호 단말에 따라 법적 근거와 승인 주체가 다릅니다.</div></div>
  <div class="card"><strong class="cf-accent">통제는 거의 같다</strong><div class="cf-muted">연구개발망과 5호망의 통제 요구는 망간 전송, 비용 두 줄만 다릅니다.</div></div>
  <div class="card"><strong class="cf-success">권장은 PATH B</strong><div class="cf-muted">실업무 코드와 운영계에 닿는 유일한 길. 약 1년, 회차와 서류 준비가 기간을 결정합니다.</div></div>
</div>
<div class="callout callout-info fragment fade-up" data-fragment-index="1"><strong class="cf-info">다음 2부</strong>: KB증권이 실제로 만든 구조, 그리고 랜딩존과 네트워크를 어떻게 깔아야 하는지 봅니다.</div>
:::

:::notes
{timing: 1min}
[요약]
- 출발 단말이 법적 근거를 정함
- 연구개발망과 5호망의 통제 차이는 두 줄뿐
- 권장 PATH B, 기간은 회차와 서류 준비가 좌우

1부를 세 줄로 정리하면, 출발 단말이 근거를 정하고, 통제 요구는 연구개발망이든 5호망이든 거의 같으며, 그래서 실업무에 닿는 5호망 경로를 권한다는 것입니다.
{cue: transition}
2부에서는 KB증권이 실제로 만든 구조부터 보겠습니다.
:::
