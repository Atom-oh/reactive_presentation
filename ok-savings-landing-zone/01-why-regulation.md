---
remarp: true
block: 01-why-regulation
---

---
<!-- Slide 1: 세션 커버 -->
@type: cover

# AWS Landing Zone

OK저축은행을 위한 금융 규제 준수형 멀티 어카운트 기반 설계

2026. 10. 27, 오준석, Senior Solutions Architect, AWS Korea

:::notes
{timing: 0.5min}
[요약]
- 세션 목적: Landing Zone이 무엇이고 금융 규제와 어떻게 연결되는지 공유
- OK저축은행 환경에서 설계 착수 전에 필요한 의사결정 항목을 함께 정리
- 총 60분, 본론 약 50분과 마지막 약 8분 Q&A

안녕하세요, AWS Korea 오준석입니다. 오늘은 Landing Zone이 무엇인지, 그리고 전자금융감독규정 같은 금융 규제와 어떻게 연결되는지를 OK저축은행 환경에 맞춰 설명드리겠습니다.
{cue: pause}
마지막에는 설계 단계에 들어가기 전에 함께 정해야 할 의사결정 항목을 한 장에 정리해 두었습니다. 그 부분은 중간중간 질문 주시면 바로 같이 보겠습니다.
{cue: transition}
먼저 오늘 순서입니다.
:::

---
<!-- Slide 2: 아젠다 -->
@type: agenda
@title: 오늘 세션 구성

## 오늘 세션 구성

1. 왜 Landing Zone인가 (6분)
2. 금융 규제와 클라우드 (10분)
3. 멀티 어카운트와 Control Tower (12분)
4. 네트워크 아키텍처 (8분)
5. 보안과 감사 (8분)
6. 구축 접근 방식과 의사결정 항목 (7분)
7. Q&A (약 8분)

:::notes
{timing: 0.5min}
[요약]
- 여섯 챕터, 시간 배분은 01 6분, 02 10분, 03 12분, 04 8분, 05 8분, 06 7분, 이후 Q&A 약 8분
- 02장의 규제 매핑표가 세션의 연결고리이고, 03장부터 05장은 그 표의 오른쪽 열을 상세히 푸는 구조
- 06장 마지막 의사결정 항목은 오늘 확정이 아니라 담당자 지정이 목표

여섯 챕터로 진행합니다. 1장에서 Landing Zone이 왜 필요한지 보고, 2장에서 전자금융감독규정이 요구하는 절차와 통제를 Landing Zone에 매핑합니다.
{cue: pause}
3장부터 5장은 그 매핑표의 오른쪽 열, 즉 기술 통제를 계정, 네트워크, 보안 순서로 풀어 가는 구조입니다. 마지막 6장에서 구축 방법과 로드맵, 그리고 함께 정해야 할 항목을 보겠습니다.
{cue: transition}
1장부터 시작하겠습니다.
:::

---
<!-- Slide 3: 섹션 01 -->
@type: section

# 01 왜 Landing Zone인가

클라우드 도입 첫 단계에서 거버넌스 기반을 먼저 설계하는 이유

:::notes
{timing: 0.5min}
[요약]
- 1장 질문: 첫 워크로드를 올리기 전에 무엇을 먼저 정해야 하는가
- 정의, 그리고 단일 계정과 멀티 어카운트 비교

1장은 하나의 질문에서 시작합니다. 첫 워크로드를 올리기 전에 무엇을 먼저 정해야 하느냐입니다.
{cue: transition}
Landing Zone의 정의부터 보겠습니다.
:::

---
<!-- Slide 4: Landing Zone 정의 -->
@type: content
@title: 나중에 바꾸기 가장 어려운 세 가지

## 나중에 바꾸기 가장 어려운 세 가지

:::html
<div class="lz-grid-2">
  <div class="lz-stack">
    <div class="lz-card">
      <h4>Landing Zone: 안전한 멀티 어카운트 환경의 기본 골격</h4>
      <div class="lz-muted">계정, 권한, 네트워크, 로그를 처음부터 표준화해 이후 모든 워크로드가 같은 통제 위에서 동작합니다.</div>
    </div>
    <div class="lz-card">
      <div class="lz-cap">첫 워크로드 이후 변경 비용 (개념도)</div>
      <svg viewBox="0 0 520 210" width="100%" role="img" aria-label="시간이 지날수록 계정 구조, IP 대역, 권한 모델의 변경 비용이 급격히 커지는 곡선">
        <line class="lz-axis" x1="40" y1="180" x2="510" y2="180"/>
        <line class="lz-axis" x1="40" y1="20" x2="40" y2="180"/>
        <line class="lz-mark" x1="150" y1="20" x2="150" y2="180"/>
        <text class="lz-svg-cap" x="156" y="34">첫 워크로드</text>
        <path class="lz-curve" d="M40,172 C150,168 230,150 300,115 C370,80 430,45 505,24"/>
        <circle class="lz-dot-ok" cx="95" cy="171" r="8"/>
        <text class="lz-svg-cap" x="62" y="200">지금 결정</text>
        <circle class="lz-dot-bad" cx="440" cy="44" r="8"/>
        <text class="lz-svg-cap" x="240" y="64">운영 후 재설계</text>
        <text class="lz-svg-cap" x="440" y="200">시간</text>
        <text class="lz-svg-cap" x="46" y="16">변경 비용</text>
      </svg>
      <div class="lz-row">
        <span class="lz-pill no">계정 구조</span><span class="lz-pill no">IP 대역</span><span class="lz-pill no">권한 모델</span>
      </div>
    </div>
  </div>
  <div class="lz-stack">
    <div class="lz-cap lz-t-info">WHY: 세 가지 압력</div>
    <div class="lz-grid-3 fragment fade-up" data-fragment-index="1">
      <div class="lz-panel"><strong class="lz-t-danger">계정 확장 속도</strong><div class="lz-muted">업무와 환경이 늘수록 계정과 권한이 빠르게 분산</div></div>
      <div class="lz-panel"><strong class="lz-t-danger">규제 증적 요구</strong><div class="lz-muted">감독기관 점검 시 통제와 로그 증적을 즉시 제시</div></div>
      <div class="lz-panel"><strong class="lz-t-danger">재작업 비용</strong><div class="lz-muted">운영 후 구조 변경은 네트워크, 권한 전면 재설계</div></div>
    </div>
    <div class="lz-cap lz-t-success">WHAT: 세 가지 기반</div>
    <div class="lz-stack fragment fade-up" data-fragment-index="2">
      <div class="lz-card lz-row"><img class="lz-icon" src="common/aws-icons/services/Arch_AWS-Organizations_48.svg" alt=""><div><strong>계정 격리</strong><div class="lz-muted">업무, 환경 단위 계정 분리로 장애와 침해 영향 범위 축소. 계정이 곧 보안 경계</div></div></div>
      <div class="lz-card lz-row"><img class="lz-icon" src="common/aws-icons/services/Arch_AWS-Control-Tower_48.svg" alt=""><div><strong>중앙 거버넌스</strong><div class="lz-muted">OU별 예방, 탐지 통제와 조직 전체 로그 중앙 보관. 규제 통제를 일관되게 적용</div></div></div>
      <div class="lz-card lz-row"><img class="lz-icon" src="common/aws-icons/resources/Res_AWS-Organizations_Account_48.svg" alt=""><div><strong>표준 자동화</strong><div class="lz-muted">Account Factory로 표준 계정 즉시 발급. 신규 환경도 처음부터 준수</div></div></div>
    </div>
  </div>
</div>
:::


:::notes
{timing: 2.5min}
[요약]
- Landing Zone 정의: 계정, 권한, 네트워크, 로그를 처음부터 표준화한 멀티 어카운트 골격
- 핵심 메시지: 나중에 바꾸기 가장 어려운 것이 계정 구조, IP 대역, 권한 모델
- 그래서 첫 워크로드 전에 결정해야 함 (곡선은 개념도, 수치 아님)
- WHY 세 가지 압력, WHAT 세 가지 기반

Landing Zone은 한 문장으로, 안전한 멀티 어카운트 환경의 기본 골격입니다. 계정, 권한, 네트워크, 로그를 처음부터 표준화해서 그 위에 올라가는 모든 워크로드가 같은 통제를 받게 만드는 것입니다.
{cue: pause}
왼쪽 곡선이 오늘 가장 드리고 싶은 메시지입니다. 계정 구조, IP 대역, 권한 모델 이 세 가지는 첫 워크로드가 올라간 뒤에 바꾸려면 네트워크와 권한을 전면 재설계해야 합니다. 이 곡선은 개념도이고 수치는 아닙니다.
{cue: click}
오른쪽 위는 왜 지금 필요한지, 세 가지 압력입니다. 계정은 빠르게 늘고, 감독기관은 증적을 즉시 요구하고, 나중에 고치면 비쌉니다.
{cue: click}
그래서 Landing Zone이 주는 세 가지 기반이 계정 격리, 중앙 거버넌스, 표준 자동화입니다.
{cue: transition}
그럼 계정을 나누면 실제로 무엇이 달라지는지 비교해 보겠습니다.
:::

---
<!-- Slide 5: 단일 vs 멀티 -->
@type: content
@title: 계정 분리가 통제와 감사의 출발점

## 계정 분리가 통제와 감사의 출발점

:::html
<div class="lz-vs">
  <div class="lz-card">
    <div class="lz-row"><span class="lz-pill no">단일 계정 또는 소수 계정</span></div>
    <div class="lz-single">
      <div class="lz-blast">
        <span class="lz-acct">업무계 운영</span><span class="lz-acct">채널계 운영</span><span class="lz-acct">개발, 테스트</span>
        <span class="lz-acct">보안 도구</span><span class="lz-acct">로그</span><span class="lz-acct">PoC</span>
      </div>
      <div class="lz-cap lz-t-danger">하나의 장애, 하나의 침해가 전체로 번지는 영향 범위</div>
    </div>
  </div>
  <div class="lz-card">
    <div class="lz-row"><span class="lz-pill ok">멀티 어카운트 Landing Zone</span></div>
    <div class="lz-multi">
      <div class="lz-ou"><b>Security</b><span class="lz-acct">Log Archive</span><span class="lz-acct">Audit</span></div>
      <div class="lz-ou"><b>Prod</b><span class="lz-acct">업무계</span><span class="lz-acct">채널계</span></div>
      <div class="lz-ou"><b>NonProd</b><span class="lz-acct">Dev</span><span class="lz-acct">Stg</span></div>
      <div class="lz-ou"><b>Sandbox</b><span class="lz-acct lz-hot">PoC</span></div>
    </div>
    <div class="lz-cap lz-t-success">계정 단위 격리: 사고의 영향을 그 계정 안으로 한정</div>
  </div>
</div>
<div class="lz-grid-3 lz-gap-top fragment fade-up" data-fragment-index="1">
  <div class="lz-panel"><strong>권한 관리</strong><div class="lz-muted"><span class="lz-t-danger">단일</span> IAM 예외 누적 <br><span class="lz-t-success">멀티</span> OU별 SCP(서비스 제어 정책) 상한, Identity Center SSO</div></div>
  <div class="lz-panel"><strong>감사 대응</strong><div class="lz-muted"><span class="lz-t-danger">단일</span> 분산 로그, 수작업 증적 <br><span class="lz-t-success">멀티</span> 조직 CloudTrail, Log Archive 중앙 보관</div></div>
  <div class="lz-panel"><strong>비용 배분</strong><div class="lz-muted"><span class="lz-t-danger">단일</span> 태그 누락 시 배분 불가 <br><span class="lz-t-success">멀티</span> 계정 단위 자동 분리</div></div>
  <div class="lz-panel"><strong>환경 분리</strong><div class="lz-muted"><span class="lz-t-danger">단일</span> 개발과 운영 리소스 혼재 <br><span class="lz-t-success">멀티</span> Prod, NonProd OU와 네트워크 격리</div></div>
  <div class="lz-panel"><strong>신규 환경</strong><div class="lz-muted"><span class="lz-t-danger">단일</span> 수작업, 환경 간 편차 <br><span class="lz-t-success">멀티</span> Account Factory 표준 발급</div></div>
  <div class="lz-panel"><strong>AWS 권장</strong><div class="lz-muted">워크로드와 환경 단위로 계정을 나누고, 보안과 로그는 전용 계정으로 분리</div></div>
</div>
:::


:::notes
{timing: 3min}
[요약]
- 왼쪽: 모든 워크로드가 한 계정에 모이면 장애와 침해 영향 범위가 계정 전체
- 오른쪽: OU와 계정으로 나누면 PoC 계정 사고의 영향 범위(Blast radius)를 그 계정으로 한정
- 비교 다섯 축: 권한, 감사, 비용, 환경 분리, 신규 환경
- 질문: OK저축은행의 기존 AWS 계정 유무와 계정 수

금융권에서 계정 분리는 선택이라기보다 통제와 감사 대응의 출발점입니다. 왼쪽처럼 운영, 개발, 보안 도구, 로그가 한 계정에 있으면 한 번의 실수나 침해가 전체에 영향을 줍니다.
{cue: pause}
오른쪽은 같은 시스템을 OU와 계정으로 나눈 모습입니다. 예를 들어 Sandbox의 PoC 계정에서 문제가 생겨도 영향이 그 계정 안으로 한정됩니다. 계정 경계가 그대로 보안 경계가 되는 것입니다.
{cue: click}
아래는 다섯 가지 축으로 본 차이입니다. 특히 감사 대응에서, 로그가 Log Archive 계정 한 곳에 모이면 증적 수집이 수작업에서 조회로 바뀝니다.
{cue: question}
혹시 지금 OK저축은행에서 사용 중인 AWS 계정이 있으신지, 있다면 몇 개 정도인지 여쭤봐도 될까요? 뒤에서 기존 계정 처리 방식을 고를 때 필요합니다.
{cue: transition}
이제 2장, 금융 규제로 넘어가겠습니다.
:::

---
<!-- Slide 6: 섹션 02 -->
@type: section

# 02 금융 규제와 클라우드

전자금융감독규정이 요구하는 절차와 통제를 Landing Zone에 매핑

:::notes
{timing: 0.5min}
[요약]
- 2장: 제14조의2 이용 절차, 규제 요건과 Landing Zone 통제 매핑, 망분리 규제 변화
- 이 장의 매핑표가 세션 전체의 연결고리

2장은 규제 이야기입니다. 이용 절차, 요건과 통제의 매핑, 그리고 최근 망분리 규제 변화를 차례로 보겠습니다.
{cue: transition}
먼저 제14조의2 절차입니다.
:::

---
<!-- Slide 7: 제14조의2 절차 -->
@type: content
@title: 제14조의2, 네 단계 중 3단계가 핵심

## 제14조의2, 네 단계 중 3단계가 핵심

:::html
<div class="lz-steps" id="lzProc">
  <div class="lz-step" data-i="0"><h4>업무 중요도 평가</h4><div class="lz-muted">이용 대상 업무와 정보의 중요도 평가, 중요업무 여부 판단</div></div>
  <div class="lz-step" data-i="1"><h4>CSP(클라우드 제공자) 평가</h4><div class="lz-muted">건전성, 안전성 평가. 비중요업무는 필수항목만</div><span class="lz-pill ok">AWS 지원</span></div>
  <div class="lz-step lz-key lz-sel" data-i="2"><h4>BCP(업무연속성), 안전성 조치</h4><div class="lz-muted">재해복구, 출구전략 수립과 암호화, 접근통제, 백업</div><span class="lz-pill ok">Landing Zone 영역</span></div>
  <div class="lz-step" data-i="3"><h4>위원회 심의, 보고</h4><div class="lz-muted">심의 의결 후 이용 개시, 중요업무는 이용 후 3개월 이내 금융감독원 보고</div></div>
</div>
<div class="lz-panel lz-gap-top" id="lzProcDetail"></div>
<div class="callout callout-info fragment fade-up" data-fragment-index="1"><strong class="lz-t-info">Landing Zone의 역할</strong>: 3단계 안전성 확보조치의 기술 통제를 표준화해, 심의와 보고 증적을 반복 가능하게 만듭니다.</div>
<div class="lz-cap">세부 절차는 금융분야 클라우드 이용 가이드 참조. 각 단계를 클릭하면 설명이 바뀝니다.</div>
:::

:::script
(function () {
  var root = document.getElementById('lzProc'), out = document.getElementById('lzProcDetail');
  if (!root || !out) return;
  var D = [
    '<div class="lz-grid-2"><div><strong class="lz-t-info">중요업무 여부가 이후 범위를 정합니다</strong><div class="lz-muted">이용 대상 업무와 처리 정보의 중요도를 먼저 평가합니다.</div></div><div class="lz-row"><span class="lz-pill">중요업무: 전체 평가 항목</span><span class="lz-pill">비중요업무: 필수항목 위주</span></div></div>',
    '<div class="lz-grid-2"><div><strong class="lz-t-info">CSP 평가 부담을 줄일 수 있습니다</strong><div class="lz-muted">AWS는 금융보안원 CSP 안전성 평가 결과를 제공하므로 이를 평가 자료로 활용합니다.</div></div><div class="lz-row"><span class="lz-pill">금융보안원 평가 결과 활용</span><span class="lz-muted">고객은 이용 업무에 대한 평가와 판단에 집중</span></div></div>',
    '<div class="lz-grid-2"><div><strong class="lz-t-accent">기술 통제를 코드와 표준으로</strong><div class="lz-muted">암호화, 접근통제, 백업, 재해복구 구성을 모든 계정에 같은 방식으로 적용합니다.</div></div><div class="lz-row"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-Key-Management-Service_48.svg" alt=""><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-IAM-Identity-Center_48.svg" alt=""><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-Backup_48.svg" alt=""><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-CloudFormation_48.svg" alt=""><span class="lz-muted">KMS, Identity Center, Backup, IaC</span></div></div>',
    '<div class="lz-grid-2"><div><strong class="lz-t-info">같은 자료를 매번 다시 쓸 수 있게</strong><div class="lz-muted">표준 계정과 통제 구성이 정해져 있으면 정보보호위원회 심의 자료와 보고 증적을 재사용합니다.</div></div><div class="lz-row"><span class="lz-pill">심의 의결</span><span class="lz-pill">이용 개시</span><span class="lz-pill">중요업무: 3개월 이내 보고</span></div></div>'
  ];
  function pick(i) {
    root.querySelectorAll('.lz-step').forEach(function (s, j) { s.classList.toggle('lz-sel', j === i); });
    out.innerHTML = D[i];
  }
  root.addEventListener('click', function (e) { var s = e.target.closest('.lz-step'); if (s) pick(+s.dataset.i); });
  pick(2);
})();
:::

:::notes
{timing: 3min}
[요약]
- 제14조의2 네 단계: 업무 중요도 평가, CSP 평가, BCP와 안전성 조치, 위원회 심의와 보고
- 1단계 결과(중요업무 여부)가 이후 절차 범위를 결정
- 2단계: AWS가 금융보안원 CSP 안전성 평가 결과를 제공해 부담 감소
- 3단계 기술 통제를 표준화하는 것이 Landing Zone의 역할
- 세부 절차는 금융분야 클라우드 이용 가이드 참조

전자금융감독규정 제14조의2는 클라우드 이용 절차를 네 단계로 정하고 있습니다. 업무 중요도 평가, CSP 평가, BCP와 안전성 확보조치, 그리고 정보보호위원회 심의와 보고입니다.
{cue: pause}
첫 단계에서 중요업무인지 아닌지가 정해지면 그 뒤 절차의 범위가 달라집니다. 2단계 CSP 평가는 AWS가 금융보안원 안전성 평가 결과를 제공하기 때문에 부담이 많이 줄어듭니다.
{cue: click}
오늘 이야기의 대부분은 3단계입니다. 암호화, 접근통제, 백업, 재해복구 같은 기술 통제를 계정마다 같은 방식으로 적용하는 것, 그게 Landing Zone이 하는 일입니다. 그러면 4단계 심의 자료와 보고 증적도 매번 새로 만들 필요 없이 재사용할 수 있습니다.
{cue: transition}
그럼 구체적으로 어떤 요건이 어떤 통제로 이어지는지 보겠습니다.
:::

---
<!-- Slide 8: 규제 매핑 -->
@type: content
@title: 규제 요건을 통제 계층에 매핑

## 규제 요건을 통제 계층에 매핑

:::html
<div class="lz-map">
  <div class="lz-stack" id="lzReqs">
    <div class="lz-req lz-sel" data-l="0,1" data-ch="03장"><span>클라우드 이용 절차<small>표준 계정과 통제 구성을 심의 자료로 재사용</small></span><span class="lz-reg">감독규정 제14조의2</span></div>
    <div class="lz-req" data-l="2" data-ch="04장"><span>망분리와 대체 통제<small>Egress 중앙화, 업무계 VPC 인터넷 차단, Inspection VPC</small></span><span class="lz-reg">제15조, 시행세칙 별표7</span></div>
    <div class="lz-req" data-l="1" data-ch="03장"><span>접근통제, 권한 분리<small>사내 IdP 연동 Identity Center, MFA, OU별 SCP 상한</small></span><span class="lz-reg">감독규정</span></div>
    <div class="lz-req" data-l="1,3" data-ch="03장, 05장"><span>암호화<small>KMS 기본 암호화, Config 탐지와 SCP 차단</small></span><span class="lz-reg">감독규정</span></div>
    <div class="lz-req" data-l="3" data-ch="05장"><span>로그 보존과 무결성<small>Organization Trail, Log Archive, S3 Object Lock</small></span><span class="lz-reg">전자금융거래법, 감독규정</span></div>
    <div class="lz-req" data-l="4" data-ch="05장"><span>침해사고 탐지와 보고<small>GuardDuty, Security Hub, EventBridge 알림</small></span><span class="lz-reg">감독규정</span></div>
    <div class="lz-req" data-l="4,0" data-ch="04장 DX 이중화, 06장 DR 전략"><span>업무연속성, 출구전략<small>AWS Backup, 멀티 AZ 표준, IaC 재구축</small></span><span class="lz-reg">감독규정 별표 2의3</span></div>
  </div>
  <div class="lz-stack">
    <div class="lz-layers" id="lzLayers">
      <div class="lz-layer"><b>계정 구조</b><div class="lz-row"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-Organizations_48.svg" alt=""><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-Control-Tower_48.svg" alt=""><span class="lz-muted">Organizations, OU, Account Factory</span></div></div>
      <div class="lz-layer"><b>신원과 권한</b><div class="lz-row"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-IAM-Identity-Center_48.svg" alt=""><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-Key-Management-Service_48.svg" alt=""><span class="lz-muted">Identity Center, MFA, SCP, RCP(리소스 제어 정책), KMS</span></div></div>
      <div class="lz-layer"><b>네트워크</b><div class="lz-row"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-Transit-Gateway_48.svg" alt=""><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-Network-Firewall_48.svg" alt=""><span class="lz-muted">TGW(Transit Gateway), Inspection VPC, Egress 중앙화</span></div></div>
      <div class="lz-layer"><b>데이터와 로그</b><div class="lz-row"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-CloudTrail_48.svg" alt=""><img class="lz-icon-sm" src="common/aws-icons/resources/Res_Amazon-Simple-Storage-Service_S3-Object-Lock_48.svg" alt=""><span class="lz-muted">Organization Trail, Log Archive, Object Lock</span></div></div>
      <div class="lz-layer"><b>탐지와 복구</b><div class="lz-row"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_Amazon-GuardDuty_48.svg" alt=""><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-Security-Hub_48.svg" alt=""><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-Backup_48.svg" alt=""><span class="lz-muted">GuardDuty, Security Hub, Config, Backup</span></div></div>
    </div>
    <div class="callout callout-info" id="lzMapOut"></div>
  </div>
</div>
<div class="lz-cap">조항별 세부 해석과 적용 범위는 OK저축은행 준법감시, 정보보호 부서와 확인 필요. 왼쪽 요건을 클릭하면 해당 계층과 구현 방식이 표시됩니다.</div>
:::


:::script
(function () {
  var reqs = document.getElementById('lzReqs'), layers = document.getElementById('lzLayers'), out = document.getElementById('lzMapOut');
  if (!reqs || !layers || !out) return;
  var IMPL = [
    '표준 계정과 통제 구성을 정보보호위원회 심의 자료로 재사용',
    'Egress 중앙화, 업무계 VPC 인터넷 경로 차단, Inspection VPC',
    'Identity Center와 사내 IdP 연동, MFA 강제, OU별 SCP 권한 상한',
    'KMS 기본 암호화, 미암호화 리소스 Config 탐지와 SCP 차단',
    'Organization CloudTrail, Log Archive 계정, S3 Object Lock',
    'GuardDuty, Security Hub 통합 탐지, EventBridge 알림 자동화',
    'AWS Backup 정책, 멀티 AZ 표준, IaC 기반 재구축'
  ];
  function pick(el) {
    var items = [].slice.call(reqs.children), i = items.indexOf(el), on = el.dataset.l.split(',').map(Number);
    items.forEach(function (r) { r.classList.toggle('lz-sel', r === el); });
    [].forEach.call(layers.children, function (L, j) { var hit = on.indexOf(j) >= 0; L.classList.toggle('lz-sel', hit); L.classList.toggle('lz-dim', !hit); });
    out.innerHTML = '<strong class="lz-t-info">구현 방식</strong>: ' + IMPL[i] + ' <span class="lz-pill">상세: ' + el.dataset.ch + '</span>';
  }
  reqs.addEventListener('click', function (e) { var r = e.target.closest('.lz-req'); if (r) pick(r); });
  pick(reqs.children[0]);
})();
:::

:::notes
{timing: 3.5min}
[요약]
- 세션의 핵심 연결고리: 규정이 요구하는 결과를 계정, 권한, 네트워크, 로그, 탐지 계층의 기술 통제로 구현
- 일곱 요건 각각의 구현 방식은 행 아래에 표시, 클릭하면 해당 계층이 강조됨 (망분리, 로그 보존, 침해사고 순서로 시연 권장)
- 03장부터 05장은 이 표의 구현 방식 열을 상세히 설명
- 조항별 해석은 준법감시, 정보보호 부서와 확인 필요

이 슬라이드가 오늘 세션의 연결고리입니다. 왼쪽은 규제가 요구하는 결과와 그 구현 방식, 오른쪽은 구현이 속하는 Landing Zone의 다섯 계층입니다.
{cue: demo}
망분리와 대체 통제를 눌러 보면 네트워크 계층이 켜지고, Egress 중앙화와 업무계 VPC 인터넷 경로 차단이 구현 방식으로 나옵니다. 로그 보존과 무결성은 데이터와 로그 계층, Organization CloudTrail과 Object Lock입니다.
{cue: pause}
이렇게 요건 하나가 계층 한두 개로 이어지고, 뒤의 3장부터 5장이 각 계층을 하나씩 자세히 보는 구조입니다. 조항별 세부 해석과 적용 범위는 준법감시, 정보보호 부서와 함께 확인해야 합니다.
{cue: transition}
다음은 최근 가장 많이 받는 질문, 망분리 규제 변화입니다.
:::

---
<!-- Slide 9: 망분리 -->
@type: content
@title: 망분리, 형식적 분리에서 실질 통제로

## 망분리, 형식적 분리에서 실질 통제로

:::html
<div class="lz-tl">
  <div class="lz-tl-item"><div class="lz-tl-date">2024.8</div><strong>망분리 개선 로드맵</strong><div class="lz-muted">단계적 규제 개선 방향 제시. 혁신금융서비스를 통한 SaaS, 생성형 AI 활용</div></div>
  <div class="lz-tl-item"><div class="lz-tl-date">2026.1</div><strong>시행세칙 개정 예고</strong><div class="lz-muted">SaaS를 망분리 예외로 명시. 별표7 대체 정보보호통제 준수 의무화</div></div>
  <div class="lz-tl-item"><div class="lz-tl-date">2026.4.20</div><strong>개정 시행</strong><div class="lz-muted">혁신금융서비스 심사 없이 내부 업무망에서 SaaS 이용</div></div>
  <div class="lz-tl-item lz-key"><div class="lz-tl-date">Landing Zone</div><strong>시사점</strong><div class="lz-muted">통제 결과를 증명하는 구조. 계정, VPC 단위 경계와 로그 증적 확보가 핵심</div></div>
</div>
<div class="lz-grid-2 lz-gap-top fragment fade-up" data-fragment-index="1">
  <div class="lz-card lz-scope ok">
    <div class="lz-row"><span class="lz-pill ok">이번 예외 대상</span></div>
    <h4>내부업무용 단말의 SaaS 이용</h4>
    <div class="lz-flowline"><span class="lz-acct">내부업무 단말</span><span class="lz-link"></span><span class="lz-acct">SaaS</span></div>
    <div class="lz-muted">금융보안원 등 평가를 거친 SaaS, 단말 보호대책, 반기 1회 평가와 정보보호위원회 보고. 고유식별정보, 개인신용정보 처리는 제외</div>
  </div>
  <div class="lz-card lz-scope keep">
    <div class="lz-row"><span class="lz-pill no">계속 필요</span></div>
    <h4>클라우드 정보처리시스템</h4>
    <div class="lz-flowline"><span class="lz-acct">업무계 VPC</span><span class="lz-link cut"></span><span class="lz-acct">인터넷</span></div>
    <div class="lz-muted">망분리 요건 검토와 대체 통제 설계가 계속 필요. Landing Zone 네트워크 설계가 담당</div>
  </div>
</div>
<div class="lz-cap">근거: 2026.1.19 금융위원회 보도자료(개정 예고, 예고기간 1.20 ~ 2.9), 2026.4 금융위원회 보도자료(4.20 시행)</div>
:::


:::notes
{timing: 3min}
[요약]
- 2024.8 금융위원회 망분리 개선 로드맵: 단계적 완화, 혁신금융서비스로 SaaS와 생성형 AI 활용
- 2026.1.19 보도자료: SaaS를 전자금융거래법 제21조, 감독규정 제15조 망분리 예외로 명시하는 시행세칙 개정 예고(예고기간 1.20~2.9), 별표7 대체 통제 의무화
- 2026.4.20 개정 시행: 혁신금융서비스 심사 없이 내부 업무망에서 SaaS 이용 가능
- 조건: 금융보안원 등 평가를 거친 SaaS, 접속 단말 보호대책, 반기 1회 평가와 정보보호위원회 보고. 고유식별정보, 개인신용정보 처리는 제외
- 이번 예외는 내부업무용 단말의 SaaS 이용 대상
- 클라우드 정보처리시스템 설계는 기존 망분리 요건 검토 지속 필요
- 시사점: 통제 결과를 증명하는 구조, 계정과 VPC 경계, 로그 증적

망분리 규제는 형식적인 물리 분리에서 실질적인 통제로 방향이 바뀌고 있습니다. 2024년 8월 금융위원회의 망분리 개선 로드맵 이후, 올해 1월에 SaaS를 망분리 예외로 명시하는 시행세칙 개정이 예고됐고, 4월 20일부터 시행되고 있습니다. 이제 금융보안원 등의 평가를 거친 SaaS라면 혁신금융서비스 심사 없이 내부 업무망에서 쓸 수 있습니다. 대신 단말 보호대책을 세우고, 반기마다 통제 이행을 평가해 정보보호위원회에 보고해야 합니다. 고유식별정보나 개인신용정보를 처리하는 경우는 여전히 예외가 아닙니다.
{cue: click}
여기서 주의할 점이 있습니다. 이번 예외는 왼쪽, 내부업무용 단말에서 SaaS를 쓰는 경우입니다. 오른쪽처럼 클라우드에 올리는 정보처리시스템 자체는 여전히 망분리 요건과 대체 통제 설계가 필요합니다.
{cue: pause}
그래서 Landing Zone 관점의 시사점은, 분리했다는 사실보다 통제 결과를 증명할 수 있는 구조가 중요하다는 것입니다. 계정과 VPC 단위의 경계, 그리고 로그 증적이 그 증명 수단입니다.
{cue: transition}
그 경계를 만드는 계정 구조부터, 3장에서 보겠습니다.
:::
