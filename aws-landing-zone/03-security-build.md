---
remarp: true
block: 03-security-build
---

---
<!-- Slide 1: 섹션 05 -->
@type: section

# 05 보안과 감사

위임 관리자 모델, 로그 아카이빙, 침해사고 대응

:::notes
{timing: 0.5min}
[요약]
- 5장: 보안 서비스 위임 관리자 구조, 로그 아카이빙과 보존, 침해사고 대응 흐름
- 매핑표의 로그 보존과 무결성, 침해사고 탐지와 보고 행을 구체화

5장은 매핑표 아래쪽, 로그와 탐지 계층입니다.
{cue: transition}
보안 서비스를 어느 계정에서 운영하는지부터 보겠습니다.
:::

---
<!-- Slide 2: 위임 관리자 -->
@type: content
@title: 탐지는 Audit에, 로그는 Log Archive에

## 탐지는 Audit에, 로그는 Log Archive에

:::html
<div class="lz-btns" id="lzSecBtns">
  <button class="lz-btn on" data-k="0">로그 흐름</button>
  <button class="lz-btn" data-k="1">Findings 흐름</button>
</div>
<div class="lz-arch lz-sec" id="lzSec">
  <div class="lz-zone">
    <div class="lz-zone-label">모든 멤버 계정</div>
    <div class="lz-node" data-n="ct"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-CloudTrail_48.svg" alt=""><div>CloudTrail<small>Organization Trail</small></div></div>
    <div class="lz-node" data-n="cfg"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-Config_48.svg" alt=""><div>AWS Config<small>구성 변경 기록</small></div></div>
    <div class="lz-node" data-n="flow"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_Amazon-Virtual-Private-Cloud_48.svg" alt=""><div>VPC Flow Logs</div></div>
    <div class="lz-node" data-n="gd"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_Amazon-GuardDuty_48.svg" alt=""><div>GuardDuty<small>위협 탐지</small></div></div>
    <div class="lz-node" data-n="insp"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_Amazon-Inspector_48.svg" alt=""><div>Inspector<small>취약점 스캔</small></div></div>
  </div>
  <div class="lz-stack lz-sec-mid">
    <div class="lz-zone net">
      <div class="lz-zone-label">Log Archive Account</div>
      <div class="lz-node" data-n="s3"><img class="lz-icon-sm" src="common/aws-icons/resources/Res_Amazon-Simple-Storage-Service_S3-Object-Lock_48.svg" alt=""><div>S3 로그 버킷<small>Object Lock, SSE-KMS</small></div></div>
      <div class="lz-node" data-n="lake"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_Amazon-Security-Lake_48.svg" alt=""><div>Security Lake<small>OCSF(공통 보안 스키마) 정규화</small></div></div>
    </div>
    <div class="lz-zone cloud">
      <div class="lz-zone-label">Audit Account (위임 관리자)</div>
      <div class="lz-node" data-n="hub"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-Security-Hub_48.svg" alt=""><div>Security Hub<small>통합 Findings, CSPM 표준 점검</small></div></div>
      <div class="lz-sec-row">
        <div class="lz-node" data-n="gdadm"><div>GuardDuty, Inspector<small>조직 단위 관리</small></div></div>
        <div class="lz-node" data-n="det"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_Amazon-Detective_48.svg" alt=""><div>Detective<small>조사, 상관 분석</small></div></div>
        <div class="lz-node" data-n="mac"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_Amazon-Macie_48.svg" alt=""><div>Macie<small>민감정보 탐지</small></div></div>
      </div>
    </div>
  </div>
  <div class="lz-zone">
    <div class="lz-zone-label">대응, 관제 연동</div>
    <div class="lz-node" data-n="eb"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_Amazon-EventBridge_48.svg" alt=""><div>EventBridge<small>자동 대응 트리거</small></div></div>
    <div class="lz-node" data-n="siem"><div>사내 SIEM, 보안관제</div></div>
  </div>
</div>
<div class="callout callout-info lz-flow-msg" id="lzSecMsg"></div>
:::


:::script
// lzFlow: SVG connectors between DOM nodes ([data-n]) inside a root, with packets that travel along them.
// Coordinates are measured in the root's own CSS pixels, so deck scaling and fit zoom do not skew the lines.
window.lzFlow = window.lzFlow || (function () {
  var NS = 'http://www.w3.org/2000/svg';
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  function box(root, el) {
    var R = root.getBoundingClientRect(), r = el.getBoundingClientRect(), k = root.offsetWidth / (R.width || 1);
    return { x: (r.left - R.left) * k, y: (r.top - R.top) * k, w: r.width * k, h: r.height * k };
  }
  function route(a, b, via) {
    var ax = a.x + a.w / 2, ay = a.y + a.h / 2, bx = b.x + b.w / 2, by = b.y + b.h / 2;
    if (via === 'r') {
      var X = Math.max(a.x + a.w, b.x + b.w) + 28;
      return 'M' + (a.x + a.w) + ',' + ay + ' H' + X + ' V' + by + ' H' + (b.x + b.w);
    }
    if (via === 'v') {
      var sy = by > ay ? a.y + a.h : a.y, ey = by > ay ? b.y : b.y + b.h, my = (sy + ey) / 2;
      return 'M' + ax + ',' + sy + ' V' + my + ' H' + bx + ' V' + ey;
    }
    var sx = bx > ax ? a.x + a.w : a.x, ex = bx > ax ? b.x : b.x + b.w, mx = (sx + ex) / 2;
    return 'M' + sx + ',' + ay + ' H' + mx + ' V' + by + ' H' + ex;
  }
  return function (root, edges) {
    var svg = document.createElementNS(NS, 'svg'), P = {}, gen = 0, active = false, hooks = {};
    svg.setAttribute('class', 'lz-flow-svg'); svg.setAttribute('aria-hidden', 'true');
    root.appendChild(svg);
    edges.forEach(function (e) {
      var p = document.createElementNS(NS, 'path'); p.setAttribute('class', 'lz-edge'); svg.appendChild(p); P[e.id] = { el: p, e: e };
    });
    function node(id) { return root.querySelector('[data-n="' + id + '"]'); }
    function layout() {
      svg.setAttribute('viewBox', '0 0 ' + root.offsetWidth + ' ' + root.offsetHeight);
      Object.keys(P).forEach(function (k) {
        var a = node(P[k].e.from), b = node(P[k].e.to);
        P[k].el.setAttribute('d', a && b && a.offsetParent && b.offsetParent ? route(box(root, a), box(root, b), P[k].e.via) : '');
      });
    }
    function clear() {
      gen++;
      svg.querySelectorAll('.lz-pkt, .lz-x').forEach(function (n) { n.remove(); });
      Object.keys(P).forEach(function (k) { P[k].el.setAttribute('class', 'lz-edge'); });
      root.querySelectorAll('.lz-hit, .lz-blocked').forEach(function (n) { n.classList.remove('lz-hit', 'lz-blocked'); });
    }
    function packet(id, cls, my) {
      var E = P[id]; if (!E) return Promise.resolve();
      var path = E.el, len = path.getTotalLength ? path.getTotalLength() : 0, bad = cls === 'bad';
      path.setAttribute('class', 'lz-edge on' + (cls ? ' ' + cls : ''));
      var c = document.createElementNS(NS, 'circle'); c.setAttribute('r', '9'); c.setAttribute('class', 'lz-pkt' + (cls ? ' ' + cls : '')); svg.appendChild(c);
      var stop = bad ? 0.5 : 1, dur = reduce ? 1 : 900 * stop, t0 = null;
      return new Promise(function (done) {
        function frame(ts) {
          if (my !== gen) { c.remove(); return done(); }
          if (t0 === null) t0 = ts;
          var f = Math.min(1, (ts - t0) / dur), q = f < 0.5 ? 2 * f * f : 1 - Math.pow(-2 * f + 2, 2) / 2;
          var pt = len ? path.getPointAtLength(q * len * stop) : { x: 0, y: 0 };
          c.setAttribute('cx', pt.x); c.setAttribute('cy', pt.y);
          if (f < 1) return requestAnimationFrame(frame);
          var to = node(E.e.to);
          if (bad) {
            var x = document.createElementNS(NS, 'path'); x.setAttribute('class', 'lz-x');
            x.setAttribute('d', 'M' + (pt.x - 11) + ',' + (pt.y - 11) + ' l22,22 M' + (pt.x + 11) + ',' + (pt.y - 11) + ' l-22,22'); svg.appendChild(x);
            if (to) to.classList.add('lz-blocked');
          } else if (to) to.classList.add('lz-hit');
          setTimeout(function () { c.remove(); done(); }, 180);
        }
        requestAnimationFrame(frame);
      });
    }
    // seq: [[edgeId, cls], ...] played one after another.
    function play(seq) {
      clear(); var my = gen;
      return seq.reduce(function (pr, s) { return pr.then(function () { if (my === gen) return packet(s[0], s[1], my); }); }, Promise.resolve());
    }
    function sync() {
      var s = root.closest('.slide'), now = !!(s && s.classList.contains('active'));
      if (now && !active) { active = true; requestAnimationFrame(function () { layout(); if (hooks.enter) hooks.enter(); }); }
      else if (!now && active) { active = false; clear(); }
    }
    var sl = root.closest('.slide');
    if (sl && window.MutationObserver) new MutationObserver(sync).observe(sl, { attributes: true, attributeFilter: ['class'] });
    if (window.ResizeObserver) new ResizeObserver(function () { if (active) layout(); }).observe(root);
    setTimeout(sync, 300);
    return { layout: layout, play: play, clear: clear, on: function (k, f) { hooks[k] = f; } };
  };
})();
(function () {
  var root = document.getElementById('lzSec'), btns = document.getElementById('lzSecBtns'), msg = document.getElementById('lzSecMsg');
  if (!root || !btns || !window.lzFlow) return;
  var f = window.lzFlow(root, [
    { id: 'ct-s3', from: 'ct', to: 's3' }, { id: 'cfg-s3', from: 'cfg', to: 's3' }, { id: 'flow-s3', from: 'flow', to: 's3' },
    { id: 'lake-siem', from: 'lake', to: 'siem' },
    { id: 'gd-hub', from: 'gd', to: 'hub' }, { id: 'insp-hub', from: 'insp', to: 'hub' },
    { id: 'hub-eb', from: 'hub', to: 'eb' }, { id: 'eb-siem', from: 'eb', to: 'siem', via: 'v' }
  ]);
  var S = [
    { seq: [['ct-s3', 'info'], ['cfg-s3', 'info'], ['flow-s3', 'info'], ['lake-siem', 'info']], m: '<strong class="lz-t-info">로그</strong>: 모든 계정의 CloudTrail, Config, Flow Logs가 Log Archive 계정 S3로 모이고, Security Lake가 OCSF로 정규화해 사내 SIEM과 연동' },
    { seq: [['gd-hub', 'ok'], ['insp-hub', 'ok'], ['hub-eb', 'ok'], ['eb-siem', 'ok']], m: '<strong class="lz-t-success">Findings</strong>: GuardDuty, Inspector 탐지 결과가 Audit 계정 Security Hub로 모이고, EventBridge가 관제와 자동 대응으로 전달' }
  ];
  var cur = 0;
  function run(k) { cur = k; [].forEach.call(btns.children, function (b, j) { b.classList.toggle('on', j === k); }); msg.innerHTML = S[k].m; f.layout(); f.play(S[k].seq); }
  btns.addEventListener('click', function (e) { var b = e.target.closest('.lz-btn'); if (b) run(+b.dataset.k); });
  f.on('enter', function () { run(cur); });
  msg.innerHTML = S[0].m;
})();
:::

:::notes
{timing: 3min}
[요약]
- 원칙: 관리 계정에서는 보안 도구를 직접 운영하지 않음, Audit 계정을 위임 관리자로 지정
- 로그 흐름: 모든 계정의 CloudTrail, Config, Flow Logs가 Log Archive S3로, Security Lake가 OCSF로 정규화해 SIEM 연동
- Findings 흐름: GuardDuty, Inspector 결과가 Audit 계정 Security Hub로 통합, EventBridge로 대응 트리거
- AWS Foundational Security Best Practices, CIS 등 표준 점검은 Security Hub CSPM이 제공 (2025년 명칭 변경 이후 Security Hub는 통합 보안 제품)

보안 서비스는 두 계정에 나눠 모읍니다. 탐지는 Audit 계정, 로그는 Log Archive 계정입니다. 관리 계정에서 보안 도구를 직접 운영하지 않는 것이 원칙이고, Audit 계정을 각 서비스의 위임 관리자로 지정합니다.
{cue: demo}
로그 흐름을 보면, 모든 멤버 계정의 CloudTrail, Config, Flow Logs가 Log Archive 계정 S3 버킷으로 모입니다. Security Lake는 이것을 OCSF 형식으로 정규화해 사내 SIEM과 연동하기 좋게 만듭니다.
{cue: demo}
Findings 흐름 버튼을 누르면, GuardDuty와 Inspector의 탐지 결과가 Audit 계정 Security Hub로 모이고, EventBridge가 관제와 자동 대응으로 넘깁니다. AWS Foundational Security Best Practices와 CIS 같은 표준 점검은 Security Hub CSPM 기능으로 제공됩니다.
{cue: transition}
그럼 로그는 어떻게 보존하고 보호하는지 보겠습니다.
:::

---
<!-- Slide 3: 로그 아카이빙 -->
@type: content
@title: 로그는 만든 계정에 두지 않는다

## 로그는 만든 계정에 두지 않는다

:::html
<div class="lz-logs">
  <div class="lz-loghead"><span>로그</span><span>수집</span><span>저장 위치</span><span>보존과 보호</span></div>
  <div class="lz-logrow fragment fade-up" data-fragment-index="1"><span><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-CloudTrail_48.svg" alt=""><b>CloudTrail 관리 이벤트</b></span><span>Organization Trail, 전 계정 자동</span><span class="lz-pill">Log Archive S3</span><span><span class="lz-pill ok">Object Lock</span><span class="lz-pill ok">KMS</span><span class="lz-pill ok">삭제 차단 SCP</span></span></div>
  <div class="lz-logrow fragment fade-up" data-fragment-index="1"><span><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-CloudTrail_48.svg" alt=""><b>CloudTrail 데이터 이벤트</b></span><span>중요 S3, Lambda 선별 수집</span><span class="lz-pill">Log Archive S3</span><span><span class="lz-pill">비용 고려해 대상 선정</span></span></div>
  <div class="lz-logrow fragment fade-up" data-fragment-index="2"><span><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-Config_48.svg" alt=""><b>AWS Config</b></span><span>Control Tower 기준선</span><span class="lz-pill">Log Archive S3, Aggregator</span><span><span class="lz-pill">구성 변경 이력 보존</span></span></div>
  <div class="lz-logrow fragment fade-up" data-fragment-index="2"><span><img class="lz-icon-sm" src="common/aws-icons/services/Arch_Amazon-Virtual-Private-Cloud_48.svg" alt=""><b>VPC Flow Logs</b></span><span>계정별 표준 배포</span><span class="lz-pill">Log Archive S3</span><span><span class="lz-pill">네트워크 접속 증적</span></span></div>
  <div class="lz-logrow fragment fade-up" data-fragment-index="2"><span><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-Security-Hub_48.svg" alt=""><b>보안 Findings</b></span><span>GuardDuty, Inspector, Macie, CSPM 점검</span><span class="lz-pill">Security Hub (Audit)</span><span><span class="lz-pill">SIEM 연동, 조치 이력 관리</span></span></div>
</div>
<div class="lz-card lz-gap-top fragment fade-up" data-fragment-index="3">
  <div class="lz-row"><img class="lz-icon" src="common/aws-icons/resources/Res_Amazon-Simple-Storage-Service_S3-Object-Lock_48.svg" alt=""><strong>보존 수명주기</strong><span class="lz-cap">기간은 로그와 기록 유형별 법정 보존기간을 준법감시 확인 후 확정</span></div>
  <div class="lz-life">
    <div class="hot">S3 Standard<small>최근 로그 조회, 분석</small></div>
    <div class="cold">S3 Glacier 계층<small>장기 보관 비용 절감</small></div>
    <div class="end">보존 만료<small>확정된 기간 이후</small></div>
  </div>
  <div class="lz-lock">Object Lock Compliance 모드: 보존 기간 동안 루트 사용자도 삭제 불가</div>
</div>
:::


:::notes
{timing: 2.5min}
[요약]
- 로그는 생성 계정이 아닌 Log Archive 계정에 저장해 변조와 삭제를 차단
- 다섯 종류: CloudTrail 관리 이벤트, 데이터 이벤트(선별), Config, VPC Flow Logs, 보안 Findings
- Object Lock Compliance 모드는 루트 사용자도 삭제 불가하므로 보존기간 확정 후 적용
- Glacier 계층 전환으로 장기 보관 비용 절감
- 법정 보존기간은 로그와 기록 유형별로 상이, 준법감시 확인 후 확정

로그의 원칙은 하나입니다. 로그를 만든 계정에 두지 않는다는 것입니다. 워크로드 계정 관리자가 자기 흔적을 지울 수 없게 Log Archive 계정에 저장합니다.
{cue: click}
CloudTrail 관리 이벤트는 Organization Trail로 모든 계정에서 자동 수집하고, Object Lock, KMS, 삭제 차단 SCP로 보호합니다. 데이터 이벤트는 비용이 크기 때문에 중요한 S3와 Lambda만 골라서 수집합니다.
{cue: click}
Config, Flow Logs, 보안 Findings도 같은 원칙으로 모읍니다.
{cue: click}
보존은 최근 로그는 Standard에 두고 오래된 것은 Glacier 계층으로 옮겨 비용을 줄입니다. 주의할 점은 Object Lock Compliance 모드입니다. 루트 사용자도 지울 수 없기 때문에, 보존기간을 준법감시와 먼저 확정한 뒤에 적용해야 합니다.
{cue: transition}
이렇게 모은 탐지 결과로 침해사고에 어떻게 대응하는지 보겠습니다.
:::

---
<!-- Slide 4: 침해사고 대응 -->
@type: content
@title: 자동화는 알림부터 격리까지 단계적으로

## 자동화는 알림부터 격리까지 단계적으로

:::html
<div class="lz-btns" id="lzIrBtns">
  <button class="lz-btn on" data-k="0">1단계: 알림 중심</button>
  <button class="lz-btn" data-k="1">2단계: 승인 후 조치</button>
  <button class="lz-btn" data-k="2">3단계: 검증된 시나리오 자동 격리</button>
</div>
<div class="lz-steps" id="lzIr">
  <div class="lz-step"><h4>탐지</h4><div class="lz-row"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_Amazon-GuardDuty_48.svg" alt=""><img class="lz-icon-sm" src="common/aws-icons/services/Arch_Amazon-Inspector_48.svg" alt=""></div><div class="lz-muted">GuardDuty, Inspector로 이상 행위와 취약점 지속 탐지</div><span class="lz-pill lz-mode"></span></div>
  <div class="lz-step"><h4>집계와 분류</h4><div class="lz-row"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-Security-Hub_48.svg" alt=""></div><div class="lz-muted">Security Hub 통합, 심각도 기준 자동 분류</div><span class="lz-pill lz-mode"></span></div>
  <div class="lz-step"><h4>대응</h4><div class="lz-row"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_Amazon-EventBridge_48.svg" alt=""><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-Lambda_48.svg" alt=""></div><div class="lz-muted">EventBridge, Lambda로 인스턴스 격리, 자격증명 비활성화</div><span class="lz-pill lz-mode"></span></div>
  <div class="lz-step"><h4>통보와 보고</h4><div class="lz-row"><span class="lz-pill">관제</span><span class="lz-pill">CISO</span></div><div class="lz-muted">즉시 통보, 감독기관 보고 절차와 연계</div><span class="lz-pill lz-mode"></span></div>
</div>
<div class="lz-grid-2 lz-gap-top">
  <div class="lz-panel"><div class="lz-cap">자동화 범위 (개념도, 상대 비교)</div><div class="lz-bar"><i id="lzIrBar"></i></div><div class="lz-muted" id="lzIrMsg"></div></div>
  <div class="callout callout-warning fragment fade-up" data-fragment-index="1"><strong class="lz-t-warning">Prod에 바로 자동 격리를 걸지 않습니다</strong><div class="lz-muted">알림 중심으로 시작하고, 검증된 시나리오부터 격리 자동화로 확대합니다.</div></div>
</div>
:::


:::script
(function () {
  var btns = document.getElementById('lzIrBtns'), g = document.getElementById('lzIr'), bar = document.getElementById('lzIrBar'), msg = document.getElementById('lzIrMsg');
  if (!btns || !g) return;
  var M = [
    { s: [['자동', 'ok'], ['자동', 'ok'], ['담당자 수동', 'no'], ['자동 알림', 'ok']], w: '35%', m: '탐지와 분류, 알림은 자동. 조치는 관제 담당자가 판단해 수동 실행' },
    { s: [['자동', 'ok'], ['자동', 'ok'], ['승인 후 실행', ''], ['자동 알림', 'ok']], w: '65%', m: '대응 Runbook을 준비해 두고, 담당자 승인 한 번으로 격리와 자격증명 비활성화 실행' },
    { s: [['자동', 'ok'], ['자동', 'ok'], ['자동 격리', 'ok'], ['자동 알림, 보고 초안', 'ok']], w: '90%', m: 'NonProd에서 검증한 시나리오만 Prod 자동 격리로 승격. 나머지는 2단계 유지' }
  ];
  function pick(k) {
    [].forEach.call(btns.children, function (b, j) { b.classList.toggle('on', j === k); });
    g.querySelectorAll('.lz-mode').forEach(function (p, j) { p.textContent = M[k].s[j][0]; p.className = 'lz-pill lz-mode' + (M[k].s[j][1] ? ' ' + M[k].s[j][1] : ''); });
    bar.style.width = M[k].w; msg.textContent = M[k].m;
  }
  btns.addEventListener('click', function (e) { var b = e.target.closest('.lz-btn'); if (b) pick(+b.dataset.k); });
  pick(0);
})();
:::

:::notes
{timing: 2min}
[요약]
- 탐지, 분류, 대응, 보고 네 단계의 리드타임을 자동화로 단축
- 자동화는 세 단계로 확대: 알림 중심, 승인 후 조치, 검증된 시나리오 자동 격리 (버튼으로 비교)
- Prod에 바로 자동 격리를 적용하지 말 것
- 2025년 감독규정 개정으로 침해사고 인지 시 신속 보고 의무가 강화된 것으로 안내되나, 세부 요건(보고 기한 등)은 정보보호 부서 확인 권장

침해사고 대응은 탐지, 집계와 분류, 대응, 통보와 보고 네 단계입니다. Landing Zone을 갖추면 이 단계 사이의 시간을 자동화로 줄일 수 있습니다.
{cue: demo}
다만 자동화는 단계적으로 늘립니다. 1단계는 탐지와 분류, 알림까지만 자동이고 조치는 사람이 합니다. 2단계는 Runbook을 준비해 두고 승인 한 번으로 격리를 실행합니다. 3단계에서 NonProd에서 검증한 시나리오만 Prod 자동 격리로 올립니다.
{cue: click}
처음부터 Prod에 자동 격리를 걸면 오탐 하나로 서비스가 멈출 수 있기 때문입니다.
{cue: pause}
보고와 관련해서는, 2025년 감독규정 개정으로 침해사고 인지 시 신속 보고 의무가 강화된 것으로 안내되고 있는데, 정확한 기한과 요건은 정보보호 부서와 확인을 부탁드립니다.
{cue: transition}
마지막 6장, 구축 접근 방식입니다.
:::

---
<!-- Slide 5: 섹션 06 -->
@type: section

# 06 구축 접근 방식

구축 옵션, Bedrock과 Claude Code 활용 사례, 로드맵

:::notes
{timing: 0.5min}
[요약]
- 6장: 구축 옵션 비교, Landing Zone 위의 Bedrock과 Claude Code, 로드맵, 의사결정 항목

6장은 무엇으로 만들지, 그 위에서 무엇을 할 수 있는지, 그리고 어떤 순서로 갈지를 봅니다.
{cue: transition}
구축 옵션부터 보겠습니다.
:::

---
<!-- Slide 6: 구축 옵션 -->
@type: content
@title: 무엇으로 만들지는 IaC 역량이 정한다

## 무엇으로 만들지는 IaC 역량이 정한다

:::html
<div class="lz-grid-2 lz-q">
  <div class="lz-panel"><strong>Q1. 인프라 표준 도구가 Terraform인가요?</strong><div class="lz-btns" id="lzQ1"><button class="lz-btn" data-v="1">예</button><button class="lz-btn on" data-v="0">아니오, 미정</button></div></div>
  <div class="lz-panel"><strong>Q2. 규제 기준선 전체를 코드로 관리해 감사 증적으로 쓰려 하나요?</strong><div class="lz-btns" id="lzQ2"><button class="lz-btn" data-v="1">예</button><button class="lz-btn on" data-v="0">아니오, 우선 빠른 시작</button></div></div>
</div>
<div class="lz-grid-3 lz-gap-top" id="lzOpts">
  <div class="lz-card"><div class="lz-row"><img class="lz-icon" src="common/aws-icons/services/Arch_AWS-Control-Tower_48.svg" alt=""><h4>Control Tower 기본</h4></div>
    <div class="lz-muted">콘솔 중심 설정, Blueprint 수준 커스터마이징</div>
    <div class="lz-meter"><span>운영 부담</span><div class="lz-bar success"><i class="w30"></i></div></div>
    <div class="lz-row"><span class="lz-pill">빠른 시작, 소규모</span><span class="lz-pill">PoC, 초기 도입</span></div></div>
  <div class="lz-card"><div class="lz-row"><img class="lz-icon" src="common/aws-icons/resources/Res_AWS-Organizations_Account_48.svg" alt=""><h4>Control Tower + AFT</h4></div>
    <div class="lz-muted">Terraform 기반 GitOps 계정 발급, 계정별 커스터마이징</div>
    <div class="lz-meter"><span>운영 부담</span><div class="lz-bar warning"><i class="w60"></i></div></div>
    <div class="lz-row"><span class="lz-pill">Terraform 표준 조직</span><span class="lz-pill">계정 발급 자동화 우선</span></div></div>
  <div class="lz-card"><div class="lz-row"><img class="lz-icon" src="common/aws-icons/services/Arch_AWS-CloudFormation_48.svg" alt=""><h4>Control Tower + LZA</h4></div>
    <div class="lz-muted">YAML 설정 파일로 네트워크, 보안 서비스까지 선언, CDK 파이프라인 배포</div>
    <div class="lz-meter"><span>운영 부담</span><div class="lz-bar warning"><i class="w60"></i></div></div>
    <div class="lz-row"><span class="lz-pill">규제 산업, 대규모 표준화</span><span class="lz-pill">기준선을 코드로</span></div></div>
</div>
<div class="callout callout-info lz-gap-top" id="lzOptMsg"></div>
<div class="lz-cap">AFT: Account Factory for Terraform, LZA: Landing Zone Accelerator on AWS. 운영 부담 막대는 상대 비교(낮음, 중간)입니다.</div>
:::


:::script
(function () {
  var q1 = document.getElementById('lzQ1'), q2 = document.getElementById('lzQ2'), opts = document.getElementById('lzOpts'), msg = document.getElementById('lzOptMsg');
  if (!q1 || !q2 || !opts) return;
  function val(g) { var b = g.querySelector('.on'); return b ? +b.dataset.v : 0; }
  function update() {
    var a = val(q1), b = val(q2), pick = b ? 2 : (a ? 1 : 0);
    var why = ['빠르게 시작하고, 운영하면서 AFT나 LZA로 확장하는 경로', '이미 쓰는 Terraform 파이프라인으로 계정 발급을 자동화', '네트워크와 보안 기준선까지 YAML로 선언해 감사 시 그대로 증적으로 제시'];
    [].forEach.call(opts.children, function (c, j) { c.classList.toggle('lz-sel', j === pick); c.classList.toggle('lz-dim', j !== pick); });
    msg.innerHTML = '<strong class="lz-t-info">추천: ' + opts.children[pick].querySelector('h4').textContent + '</strong>, ' + why[pick] + (a && b ? '. Terraform 조직이라도 기준선 코드 관리가 목적이면 LZA가 유리' : '');
  }
  [q1, q2].forEach(function (g) { g.addEventListener('click', function (e) { var t = e.target.closest('.lz-btn'); if (!t) return; [].forEach.call(g.children, function (x) { x.classList.toggle('on', x === t); }); update(); }); });
  update();
})();
:::

:::notes
{timing: 1.5min}
[요약]
- 세 가지 옵션: Control Tower 기본, Control Tower와 AFT, Control Tower와 LZA
- 선택 기준은 조직의 IaC 역량과 규제 기준선 관리 방식 (두 질문 토글로 시연)
- 질문: 인프라팀의 IaC 도구가 Terraform인지
- 규제 기준선을 코드로 관리해 감사 증적으로 쓰려면 LZA가 유리

구축 방법은 세 가지가 있고, 고르는 기준은 두 가지 질문입니다.
{cue: question}
먼저 여쭤보고 싶은 것이, 인프라팀에서 표준으로 쓰는 IaC 도구가 Terraform인지입니다.
{cue: demo}
Terraform이 표준이면 AFT로 계정 발급을 기존 파이프라인에 붙이는 것이 자연스럽습니다. 두 번째 질문, 규제 기준선 전체를 코드로 관리해서 감사 때 그대로 증적으로 쓰고 싶다면 LZA가 유리합니다. 네트워크와 보안 서비스까지 YAML 설정으로 선언하기 때문입니다.
{cue: pause}
둘 다 아니라면 Control Tower 기본으로 빠르게 시작하고, 운영하면서 확장해도 됩니다.
{cue: transition}
다음은 이 Landing Zone 위에서 생성형 AI를 어떻게 쓰는지입니다.
:::

---
<!-- Slide 7: Bedrock -->
@type: content
@title: AI 워크로드도 같은 통제를 상속

## AI 워크로드도 같은 통제를 상속

:::html
<div class="lz-ai">
  <div class="lz-zone cloud lz-ai-arch">
    <div class="lz-zone-label">AWS Cloud, 서울 리전</div>
    <div class="lz-ai-row">
      <div class="lz-zone">
        <div class="lz-zone-label">AI Workload Account (Prod OU)</div>
        <div class="lz-node"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_Amazon-Elastic-Container-Service_48.svg" alt=""><div>업무 애플리케이션<small>ECS, Lambda</small></div></div>
        <div class="lz-node"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-PrivateLink_48.svg" alt=""><div>VPC Endpoint (PrivateLink)<small>bedrock-runtime, KB용 bedrock-agent-runtime</small></div></div>
        <div class="lz-node"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-CloudTrail_48.svg" alt=""><div>호출 기록<small>CloudTrail API 기록, 호출 로그(S3, CloudWatch)를 Log Archive로 복제</small></div></div>
        <div class="lz-cap lz-t-danger">인터넷 경로 없음, SCP로 엔드포인트 외 호출 제한</div>
      </div>
      <div class="lz-pipe"></div>
      <div class="lz-zone">
        <div class="lz-zone-label">Amazon Bedrock</div>
        <div class="lz-node"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_Amazon-Bedrock_48.svg" alt=""><div>Guardrails<small>PII 마스킹, 주제 제한</small></div></div>
        <div class="lz-node"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_Amazon-Bedrock_48.svg" alt=""><div>Claude 모델<small>추론 API</small></div></div>
        <div class="lz-node"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_Amazon-Simple-Storage-Service_48.svg" alt=""><div>Knowledge Bases<small>S3 문서 RAG</small></div></div>
      </div>
    </div>
  </div>
  <div class="lz-stack">
    <div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
      <button class="tab-btn active">규정 Q&amp;A</button><button class="tab-btn">상담 요약</button><button class="tab-btn">보안 요약</button>
    </div>
    <div class="tc lz-card"><h4>사내 규정, 상품 문서 Q&amp;A</h4><div class="lz-muted">여신 업무 매뉴얼, 상품 설명서, 내규를 Knowledge Bases로 색인해 직원 질의응답 지원</div><div class="lz-row lz-gap-top"><span class="lz-pill">예시: 중도상환수수료 면제 조건 조회</span></div></div>
    <div class="tc lz-card" hidden><h4>상담 기록 요약과 민원 분류</h4><div class="lz-muted">상담 기록 요약, 민원 유형 자동 분류로 후처리 시간 단축과 VOC 분석</div><div class="lz-row lz-gap-top"><span class="lz-pill">예시: 통화 후 요약, 민원 유형 태깅</span></div></div>
    <div class="tc lz-card" hidden><h4>보안 Findings 요약</h4><div class="lz-muted">Security Hub Findings를 요약하고 조치 가이드를 생성해 관제 담당자 대응 지원</div><div class="lz-row lz-gap-top"><span class="lz-pill">예시: GuardDuty 탐지 건별 영향도 설명</span></div></div>
    <div class="callout callout-warning fragment fade-up" data-fragment-index="1"><strong class="lz-t-warning">확인 필요</strong><div class="lz-muted">개인신용정보 처리 여부, Cross-Region Inference 사용 시 데이터 처리 리전, 모델별 서울 리전 제공 여부<br>서울 외 리전 차단 SCP는 APAC, Global 추론 프로파일 호출도 막으므로 대상 리전 허용이나 bedrock:InferenceProfileArn 예외 필요</div></div>
  </div>
</div>
:::


:::notes
{timing: 1.5min}
[요약]
- Bedrock은 별도 AI 워크로드 계정(Prod OU)에 두어 기존 SCP, 로그, 네트워크 통제를 그대로 상속
- bedrock-runtime VPC 엔드포인트로 인터넷 없이 호출, Knowledge Bases(Retrieve, RetrieveAndGenerate)는 bedrock-agent-runtime 엔드포인트도 필요, SCP로 엔드포인트 외 호출 제한
- 호출 기록: CloudTrail은 API 호출만 기록(프롬프트, 응답 제외). 모델 호출 로깅은 같은 계정 S3나 CloudWatch Logs로 기록되므로 Log Archive로 복제
- 주의: Prod OU의 서울 외 리전 차단 SCP는 APAC, Global 추론 프로파일 호출을 막음. 대상 리전 허용이나 bedrock:InferenceProfileArn 조건 예외 필요
- 사례 세 가지(금융회사 업무 기준 예시): 사내 규정 Q&A, 상담 요약과 민원 분류, 보안 Findings 요약
- 최신 Claude 모델은 서울 리전 단독이 아닌 APAC 또는 Global 추론 프로파일로 제공되는 경우가 있어 데이터 처리 리전이 국외로 확장될 수 있음
- 중요업무, 개인신용정보 처리 시 준법감시 확인 필수

Landing Zone의 장점은 새 워크로드도 같은 통제를 자동으로 받는다는 것입니다. 생성형 AI도 마찬가지입니다. Bedrock을 쓰는 애플리케이션을 Prod OU 아래 별도 AI 워크로드 계정에 두면, SCP, 로그, 네트워크 통제를 그대로 상속합니다.
{cue: pause}
호출은 bedrock-runtime VPC 엔드포인트로 하기 때문에 인터넷을 거치지 않습니다. Knowledge Bases를 쓰려면 bedrock-agent-runtime 엔드포인트도 함께 둡니다. CloudTrail에는 API 호출이 남고, 프롬프트와 응답까지 남기는 모델 호출 로깅은 같은 계정의 S3나 CloudWatch Logs에 쌓이니 Log Archive로 복제합니다.
{cue: demo}
오른쪽 탭은 금융회사 업무 기준의 사례 예시입니다. 사내 규정 Q&A, 상담 요약과 민원 분류, 그리고 앞에서 본 보안 Findings를 요약해 주는 용도입니다.
{cue: click}
꼭 확인할 것이 있습니다. 최신 Claude 모델은 서울 리전 단독이 아니라 APAC이나 Global 추론 프로파일로 제공되는 경우가 있어, 데이터 처리 리전이 국외로 넓어질 수 있습니다. 개인신용정보나 중요업무에 쓸 때는 준법감시 확인이 꼭 필요합니다. 그리고 앞에서 본 서울 외 리전 차단 SCP가 이런 추론 프로파일 호출도 막기 때문에, 대상 리전을 허용하거나 추론 프로파일 조건으로 예외를 둬야 합니다.
{cue: transition}
AI는 Landing Zone 운영 자체에도 쓸 수 있습니다.
:::

---
<!-- Slide 8: Claude Code -->
@type: content
@title: Claude Code로 Landing Zone 운영

## Claude Code로 Landing Zone 운영

:::html
<div class="lz-cc">
  <div class="lz-cc-arch lz-arch" id="lzCc">
    <div class="lz-zone">
      <div class="lz-zone-label">사내망</div>
      <div class="lz-node" data-n="ms"><div>Managed Settings<small>허용 도구, 모델 정책</small></div></div>
      <div class="lz-node" data-n="pc"><div>개발자 단말<small>Claude Code CLI</small></div></div>
    </div>
    <div class="lz-cc-link"><span>DX</span></div>
    <div class="lz-zone cloud">
      <div class="lz-zone-label">Shared Services Account</div>
      <div class="lz-node" data-n="sso"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-IAM-Identity-Center_48.svg" alt=""><div>IAM Identity Center<small>SSO, 임시 자격증명</small></div></div>
      <div class="lz-node" data-n="vpce"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_AWS-PrivateLink_48.svg" alt=""><div>VPC Endpoint<small>bedrock-runtime</small></div></div>
      <div class="lz-node" data-n="br"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_Amazon-Bedrock_48.svg" alt=""><div>Amazon Bedrock<small>Claude 모델</small></div></div>
      <div class="lz-node" data-n="otel"><img class="lz-icon-sm" src="common/aws-icons/services/Arch_Amazon-CloudWatch_48.svg" alt=""><div>OTel 텔레메트리<small>사용량, 비용, 감사 추적</small></div></div>
    </div>
  </div>
  <div class="lz-stack">
    <div class="lz-card lz-row fragment fade-up" data-fragment-index="1"><span class="lz-num">1</span><div><strong>IaC 작성과 리뷰</strong><div class="lz-muted">LZA 설정 YAML, Terraform 변경안 작성과 PR 단위 기준선 위반 사전 점검</div><span class="lz-pill">예시: 신규 계정 추가 설정과 영향 범위 리뷰</span></div></div>
    <div class="lz-card lz-row fragment fade-up" data-fragment-index="2"><span class="lz-num">2</span><div><strong>통제 정책 초안 작성</strong><div class="lz-muted">규제 요건을 SCP, Config Rule 초안으로 변환 후 Policy Staging OU에서 검증</div><span class="lz-pill">예시: Prod OU 서울 외 리전 차단 SCP (Bedrock 추론 프로파일 예외 포함)</span></div></div>
    <div class="lz-card lz-row fragment fade-up" data-fragment-index="3"><span class="lz-num">3</span><div><strong>운영 이슈 분석</strong><div class="lz-muted">Config 위반, CloudTrail 이벤트를 분석해 원인과 수정 IaC 제안</div><span class="lz-pill">예시: 미암호화 EBS 탐지 건 수정 PR</span></div></div>
    <div class="callout callout-warning fragment fade-up" data-fragment-index="4"><strong class="lz-t-warning">확인 필요</strong><div class="lz-muted">개발 단말 망분리 환경의 Bedrock 연결 경로, 소스 코드의 모델 전송 범위와 내부 승인 절차</div></div>
  </div>
</div>
:::


:::script
(function () {
  var root = document.getElementById('lzCc');
  if (!root || !window.lzFlow) return;
  var f = window.lzFlow(root, [
    { id: 'ms-pc', from: 'ms', to: 'pc', via: 'v' }, { id: 'pc-sso', from: 'pc', to: 'sso' },
    { id: 'pc-vpce', from: 'pc', to: 'vpce' }, { id: 'vpce-br', from: 'vpce', to: 'br', via: 'v' }, { id: 'pc-otel', from: 'pc', to: 'otel' }
  ]);
  f.on('enter', function () { f.play([['ms-pc', 'info'], ['pc-sso', 'info'], ['pc-vpce', 'ok'], ['vpce-br', 'ok'], ['pc-otel', 'info']]); });
})();
:::

:::notes
{timing: 1min}
[요약]
- 개발자 단말의 Claude Code가 사내망과 DX를 거쳐 Shared Services 계정의 Bedrock을 호출
- CLAUDE_CODE_USE_BEDROCK=1로 Bedrock 경유, 인증은 Identity Center SSO 임시 자격증명
- Managed settings로 허용 도구, 모델, 권한 모드를 중앙 배포, OTel 메트릭으로 팀별 사용량과 비용 추적
- 사례: IaC 작성과 리뷰, 통제 정책 초안, 운영 이슈 분석
- 단말 망분리 환경이면 Bedrock 엔드포인트 접근 경로와 소스 코드 반출 정책이 선결 과제

Landing Zone을 운영하는 일 자체에도 AI를 쓸 수 있습니다. 화면의 선이 순서대로 보여 주듯, 관리 설정이 단말에 배포되고, 단말은 Identity Center로 임시 자격증명을 받아 DX와 VPC 엔드포인트를 거쳐 Bedrock을 호출하며, 사용량은 OTel 텔레메트리로 보냅니다.
{cue: pause}
Claude Code는 CLAUDE_CODE_USE_BEDROCK 환경 변수로 Bedrock을 쓰게 하고, 인증은 Identity Center SSO의 임시 자격증명을 씁니다. 허용 도구와 모델, 권한 모드는 Managed settings로 중앙에서 배포하고, OTel 메트릭으로 팀별 사용량과 비용을 봅니다.
{cue: click}
사례는 세 가지입니다. LZA 설정이나 Terraform 변경안을 쓰고 리뷰하는 것,
{cue: click}
규제 요건을 SCP나 Config Rule 초안으로 바꾸고 Policy Staging OU에서 검증하는 것,
{cue: click}
그리고 Config 위반이나 CloudTrail 이벤트를 분석해서 수정 PR까지 제안하는 것입니다.
{cue: click}
단말이 망분리된 환경이라면, 내부망 단말에서 Bedrock 엔드포인트로 가는 경로와 소스 코드 반출 정책을 먼저 정해야 합니다.
{cue: transition}
그럼 전체를 어떤 순서로 구축할지 보겠습니다.
:::

---
<!-- Slide 9: 로드맵 -->
@type: content
@title: 1단계 산출물이 심의 자료가 된다

## 1단계 산출물이 심의 자료가 된다

:::html
<div class="lz-road">
  <div class="lz-road-s key fragment fade-up" data-fragment-index="1"><div class="lz-road-h"><span class="lz-num">1</span><strong>설계</strong></div>
    <div class="lz-muted">규제 요건 매핑, OU, 계정, IP 대역 설계, 통제 목록 확정</div>
    <div class="lz-out"><span class="lz-cap">산출물</span><span class="lz-pill">규제 매핑표</span><span class="lz-pill">OU 설계서</span><span class="lz-pill">IP 계획</span></div></div>
  <div class="lz-road-s fragment fade-up" data-fragment-index="2"><div class="lz-road-h"><span class="lz-num">2</span><strong>기반 구축</strong></div>
    <div class="lz-muted">Control Tower 활성화, 핵심 계정, Identity Center, 기준 통제 적용</div>
    <div class="lz-out"><span class="lz-cap">산출물</span><span class="lz-pill">관리, 로그, 감사 계정</span><span class="lz-pill">SSO 연동</span></div></div>
  <div class="lz-road-s fragment fade-up" data-fragment-index="3"><div class="lz-road-h"><span class="lz-num">3</span><strong>네트워크, 보안</strong></div>
    <div class="lz-muted">DX, TGW, Inspection VPC, 보안 서비스 위임 관리, 로그 보존 정책</div>
    <div class="lz-out"><span class="lz-cap">산출물</span><span class="lz-pill">Hub and Spoke</span><span class="lz-pill">탐지, 로그 체계</span></div></div>
  <div class="lz-road-s fragment fade-up" data-fragment-index="4"><div class="lz-road-h"><span class="lz-num">4</span><strong>워크로드 온보딩</strong></div>
    <div class="lz-muted">Account Factory 발급, 파일럿 워크로드 이전, 운영 이관과 교육</div>
    <div class="lz-out"><span class="lz-cap">산출물</span><span class="lz-pill">파일럿 운영</span><span class="lz-pill">운영 가이드</span></div></div>
</div>
<div class="lz-feed fragment fade-up" data-fragment-index="5">
  <span class="lz-pill ok">1단계 산출물</span><span class="lz-link"></span><span class="lz-pill">정보보호위원회 심의 자료의 기반</span><span class="lz-cap">단계별 기간은 범위와 기존 환경 확인 후 협의</span>
</div>
:::


:::notes
{timing: 0.5min}
[요약]
- 네 단계: 설계, 기반 구축, 네트워크와 보안, 워크로드 온보딩
- 1단계 산출물(규제 매핑표, OU 설계서, IP 계획)이 정보보호위원회 심의 자료의 기반
- 단계별 기간은 범위와 기존 환경 확인 후 협의

구축은 네 단계로 갑니다. 설계, 기반 구축, 네트워크와 보안, 그리고 워크로드 온보딩입니다.
{cue: click}
가장 중요한 것은 1단계입니다. 규제 매핑표, OU 설계서, IP 계획이 여기서 나오는데,
{cue: click}
2단계에서 Control Tower와 핵심 계정, Identity Center를 세우고,
{cue: click}
3단계에서 네트워크와 보안 체계를,
{cue: click}
4단계에서 Account Factory로 계정을 발급해 파일럿 워크로드를 옮깁니다.
{cue: click}
다시 1단계로 돌아가면, 그 산출물이 그대로 정보보호위원회 심의 자료의 기반이 됩니다. 단계별 기간은 범위와 기존 환경을 확인한 뒤 협의하겠습니다.
{cue: transition}
마지막으로, 설계 착수 전에 함께 정할 항목입니다.
:::

---
<!-- Slide 10: 의사결정 항목 -->
@type: content
@title: 착수 전에 함께 정할 일곱 가지

## 착수 전에 함께 정할 일곱 가지

:::html
<div class="lz-grid-2 lz-dec" id="lzDec">
  <div class="lz-check fragment fade-up" data-fragment-index="1"><span class="box"></span><div><strong>클라우드 이용 대상 업무</strong><div class="lz-muted">비중요업무 우선 vs 중요업무 포함</div><span class="lz-pill">정보보호위원회, 준법감시</span></div></div>
  <div class="lz-check fragment fade-up" data-fragment-index="1"><span class="box"></span><div><strong>기존 AWS 계정 처리</strong><div class="lz-muted">신규 구축 vs 통제 우선 적용 후 확장</div><span class="lz-pill">인프라팀</span></div></div>
  <div class="lz-check fragment fade-up" data-fragment-index="1"><span class="box"></span><div><strong>자동화 도구</strong><div class="lz-muted">Control Tower 기본, AFT, LZA</div><span class="lz-pill">인프라, DevOps</span></div></div>
  <div class="lz-check fragment fade-up" data-fragment-index="1"><span class="box"></span><div><strong>인증 연동</strong><div class="lz-muted">사내 IdP 연동 방식, MFA 정책</div><span class="lz-pill">정보보호팀</span></div></div>
  <div class="lz-check fragment fade-up" data-fragment-index="2"><span class="box"></span><div><strong>온프레미스 연결</strong><div class="lz-muted">DX 회선 수, 로케이션, 대역폭</div><span class="lz-pill">네트워크팀</span></div></div>
  <div class="lz-check fragment fade-up" data-fragment-index="2"><span class="box"></span><div><strong>로그 보존, SIEM</strong><div class="lz-muted">보존 기간, 기존 관제 연동 방식</div><span class="lz-pill">보안관제</span></div></div>
  <div class="lz-check fragment fade-up" data-fragment-index="2"><span class="box"></span><div><strong>DR 전략</strong><div class="lz-muted">서울 리전 멀티 AZ, 온프레미스 DR, 타 리전</div><span class="lz-pill">업무연속성 담당</span></div></div>
  <div class="lz-panel fragment fade-up" data-fragment-index="2"><strong class="lz-t-accent">오늘의 목표</strong><div class="lz-muted">확정이 아니라 항목별 담당자 지정과 후속 미팅 일정 합의. 항목을 클릭해 담당자 지정 여부를 표시합니다.</div><div class="lz-cap" id="lzDecCnt"></div></div>
</div>
:::


:::script
(function () {
  var g = document.getElementById('lzDec'), cnt = document.getElementById('lzDecCnt');
  if (!g) return;
  function count() { cnt.textContent = '담당자 지정 ' + g.querySelectorAll('.lz-check.done').length + ' / 7'; }
  g.addEventListener('click', function (e) { var c = e.target.closest('.lz-check'); if (!c) return; c.classList.toggle('done'); count(); });
  count();
})();
:::

:::notes
{timing: 1min}
[요약]
- 설계 착수 전에 함께 확정할 일곱 항목과 협의 대상
- 이용 대상 업무, 기존 계정 처리, 자동화 도구, 인증 연동, 온프레미스 연결, 로그 보존과 SIEM, DR 전략
- 오늘 목표는 확정이 아니라 담당자 지정과 후속 미팅 일정 합의 (항목 클릭으로 표시)
- 이후 Q&A 약 8분

마지막으로 설계 단계에 들어가기 전에 함께 정해야 할 일곱 가지입니다. 각 항목에 협의할 부서를 같이 적어 두었습니다.
{cue: click}
이용 대상 업무를 비중요업무부터 할지, 기존 계정을 어떻게 할지, 자동화 도구와 인증 연동 방식입니다.
{cue: click}
그리고 DX 회선 구성, 로그 보존과 관제 연동, DR 전략입니다.
{cue: question}
오늘 이걸 다 정하자는 것은 아니고, 항목별로 어느 분이 담당하실지와 다음 미팅 일정을 맞추는 것이 목표입니다. 지금 바로 정해지는 항목이 있으면 클릭해서 표시해 두겠습니다.
{cue: transition}
오늘 내용을 정리하겠습니다.
:::

---
<!-- Slide 11: Key Takeaways -->
@type: content
@title: 오늘의 결론, 네 줄

## 오늘의 결론, 네 줄

:::html
<div class="lz-grid-2">
  <div class="lz-card fragment fade-up" data-fragment-index="1"><div class="lz-row"><img class="lz-icon" src="common/aws-icons/services/Arch_AWS-Organizations_48.svg" alt=""><strong class="lz-t-accent">구조를 먼저 정한다</strong></div><div class="lz-muted">계정 구조, IP 대역, 권한 모델은 첫 워크로드 전에. 나중에 바꾸면 전면 재설계</div></div>
  <div class="lz-card fragment fade-up" data-fragment-index="2"><div class="lz-row"><span class="lz-reg">감독규정 제14조의2</span><strong class="lz-t-accent">규제는 통제 계층으로 번역한다</strong></div><div class="lz-muted">요건 하나가 계정, 권한, 네트워크, 로그, 탐지 계층의 기술 통제로 이어짐</div></div>
  <div class="lz-card fragment fade-up" data-fragment-index="3"><div class="lz-row"><img class="lz-icon" src="common/aws-icons/services/Arch_AWS-Control-Tower_48.svg" alt=""><strong class="lz-t-accent">통제는 겹으로, 시험 후 승격</strong></div><div class="lz-muted">사전, 예방, 탐지 세 겹과 Policy Staging OU. 4.0으로 예방 통제부터 도입하고, 탐지는 Config 통합으로</div></div>
  <div class="lz-card fragment fade-up" data-fragment-index="4"><div class="lz-row"><img class="lz-icon" src="common/aws-icons/services/Arch_AWS-CloudTrail_48.svg" alt=""><strong class="lz-t-accent">증적은 따로, 지울 수 없게</strong></div><div class="lz-muted">Log Archive와 Object Lock, Audit 위임 관리자. 통제 결과를 증명하는 구조</div></div>
</div>
<div class="callout callout-info lz-gap-top fragment fade-up" data-fragment-index="5"><strong class="lz-t-info">다음 단계 제안</strong>: 일곱 가지 의사결정 항목 담당자 지정, 1단계 설계 범위 협의, 기존 AWS 계정 현황 공유</div>
:::

:::notes
{timing: 1min}
[요약]
- 결론 네 줄: 구조를 먼저, 규제를 통제 계층으로, 통제는 겹으로 시험 후 승격, 증적은 따로 지울 수 없게
- 다음 단계: 의사결정 항목 담당자 지정, 1단계 설계 범위 협의, 기존 계정 현황 공유
- 이후 Q&A 약 8분

오늘 내용을 네 줄로 정리하겠습니다.
{cue: click}
첫째, 구조를 먼저 정합니다. 계정, IP 대역, 권한은 첫 워크로드 전에 결정합니다.
{cue: click}
둘째, 규제 요건은 통제 계층으로 번역합니다.
{cue: click}
셋째, 통제는 세 겹으로 걸고, 시험한 뒤 승격합니다.
{cue: click}
넷째, 증적은 별도 계정에, 지울 수 없게 보관합니다.
{cue: click}
다음 단계로는 의사결정 항목 담당자 지정과 1단계 설계 범위 협의를 제안드립니다.
{cue: question}
궁금하신 점 편하게 말씀해 주세요.
:::

---
<!-- Slide 12: Thank You -->
@type: thankyou
@toc: toc.html
@message: AWS Landing Zone, 감사합니다

# Thank you.

:::notes
{timing: 0.5min}
[요약]
- 세션 마무리, Q&A 계속

들어 주셔서 감사합니다. 남은 질문과 의사결정 항목은 후속 미팅에서 이어서 정리하겠습니다.
:::
