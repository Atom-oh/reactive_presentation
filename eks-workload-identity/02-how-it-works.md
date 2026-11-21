---
remarp: true
block: 02-how-it-works
---

---
<!-- Slide 1: 2부 구분 -->
@type: section

# 2부: 두 방식은 안에서 어떻게 다른가

IRSA와 EKS Pod Identity를 한 단계씩, 그리고 나란히

:::notes
{timing: 0.5min}
[요약]
- 2부 질문: 같은 결과(워크로드 전용 역할)를 두 방식은 어떤 경로로 만드는가
- IRSA, Pod Identity를 각각 애니메이션과 단계별 캔버스로 보고 비교표로 정리
- 마지막에 운영 클러스터 이전 순서와 Pod의 IMDS 경로 차단

2부에서는 두 방식의 내부를 봅니다. 결과는 둘 다 "이 Pod만의 역할"인데, 그 역할을 맡는 경로와 신뢰를 거는 위치가 다릅니다.
각 방식을 먼저 애니메이션으로 한 번 훑고, 캔버스에서 한 단계씩 멈춰 가며 보겠습니다.
{cue: transition}
IRSA부터 시작합니다.
:::

---
<!-- Slide 2: IRSA 흐름 -->
@type: content
@fit: off
@title: IRSA: Pod가 토큰을 들고 STS로 간다

## IRSA: Pod가 토큰을 들고 STS로 간다

:::html
<div class="wid-fig-row">
  <figure class="wid-fig">
    <img src="images/ko-security-17-eks-workload-identity-migration-anim-1.svg" alt="IRSA 흐름. ServiceAccount 주석을 본 웹훅이 환경 변수와 projected 토큰(aud sts.amazonaws.com)을 Pod에 넣고, SDK가 토큰을 STS AssumeRoleWithWebIdentity로 보내면 STS가 IAM OIDC provider로 서명을 검증하고 신뢰 정책의 aud와 sub를 확인한 뒤 임시 자격 증명을 돌려준다.">
    <figcaption>IRSA 전체 흐름 (16초 반복)</figcaption>
  </figure>
  <div class="wid-stack">
    <div class="wid-card wid-irsa wid-edge fragment fade-up" data-fragment-index="1"><strong class="wid-t-path">신뢰 준비</strong><div class="wid-muted">클러스터 issuer를 <span class="rp-detail" data-detail="oidc">IAM OIDC(OpenID Connect) provider</span>로 한 번 등록</div></div>
    <div class="wid-card wid-irsa wid-edge fragment fade-up" data-fragment-index="2"><strong class="wid-t-path">주입</strong><div class="wid-muted">SA 주석을 본 EKS mutating webhook(amazon-eks-pod-identity-webhook)이 env와 토큰 볼륨 추가</div></div>
    <div class="wid-card wid-irsa wid-edge fragment fade-up" data-fragment-index="3"><strong class="wid-t-path">교환</strong><div class="wid-muted">Pod가 리전 STS(Security Token Service)와 직접 통신</div></div>
  </div>
</div>
<div class="wid-src">출처: <a href="https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html">Amazon EKS User Guide, IAM roles for service accounts</a></div>
:::

:::detail oidc "IAM OIDC provider"
tip: 클러스터의 토큰 발급자(issuer)를 IAM이 믿도록 계정에 등록한 항목

EKS 클러스터마다 OIDC issuer URL이 있습니다. 이 issuer를 계정의 IAM OIDC provider로 등록하면, IAM 역할의 신뢰 정책이 그 provider를 `Federated` principal로 지정할 수 있습니다. STS는 provider에 등록된 issuer의 공개 키로 Pod 토큰의 서명을 검증합니다. 클러스터를 새로 만들 때마다 provider 등록과 신뢰 정책 수정이 필요합니다.
:::

:::notes
{timing: 1.5min}
[요약]
- 준비: 클러스터 OIDC issuer를 계정의 IAM OIDC provider로 한 번 등록
- 주입: ServiceAccount의 eks.amazonaws.com/role-arn 주석을 본 EKS mutating webhook(amazon-eks-pod-identity-webhook)이 env와 projected 토큰 볼륨 추가
- 교환: SDK가 토큰을 리전 STS AssumeRoleWithWebIdentity로 보내고, STS가 서명과 aud, sub를 확인
- Pod가 STS와 직접 통신하므로 Pod에서 STS로 가는 경로가 필요

애니메이션 한 바퀴가 16초입니다. ServiceAccount 주석에서 시작해서, 토큰이 STS까지 갔다가 열쇠가 돌아오는 흐름입니다.
{cue: pause}
그림의 웹훅 카드에 "EKS Pod Identity webhook"이라고 적혀 있는데, EKS Pod Identity 기능을 말하는 게 아닙니다. IRSA 변수를 넣는 EKS mutating webhook의 이름이 원래 amazon-eks-pod-identity-webhook이라 생긴 혼동입니다. 저는 오늘 이것을 "EKS mutating webhook"이라고 부르겠습니다.
{cue: click}
{cue: click}
{cue: click}
핵심은 세 줄입니다. IAM이 클러스터를 믿도록 OIDC provider를 등록하고, Pod 생성 때 EKS mutating webhook이 토큰을 넣고, Pod가 직접 STS에 가서 토큰을 자격 증명으로 바꿉니다.
{cue: transition}
캔버스에서 한 단계씩 멈춰 보겠습니다.

[약어]
- OIDC: OpenID Connect, 토큰 발급자와 서명 검증 규약
- STS: AWS Security Token Service
:::

---
<!-- Slide 3: IRSA 단계별 캔버스 -->
@type: content
@title: IRSA 다섯 단계, aud와 sub가 열쇠

## IRSA 다섯 단계, aud와 sub가 열쇠

:::html
<div class="wid-canvas-box"><canvas id="wid-irsa-canvas" role="img" aria-label="IRSA 단계. 1 ServiceAccount 주석을 본 EKS mutating webhook(amazon-eks-pod-identity-webhook)이 env와 토큰 볼륨을 주입, 2 kubelet이 audience sts.amazonaws.com 토큰 발급, 3 SDK가 리전 STS AssumeRoleWithWebIdentity 호출, 4 STS가 IAM OIDC provider로 서명 검증, 5 신뢰 정책의 aud와 sub 확인 후 임시 자격 증명 반환."></canvas></div>
<div class="wid-canvas-bar">
  <button class="btn btn-primary btn-sm" data-wid-play="wid-irsa-canvas">Play</button>
  <button class="btn btn-sm" data-wid-reset="wid-irsa-canvas">Reset</button>
  <span class="wid-step" data-wid-step="wid-irsa-canvas">0 / 5</span>
  <span class="wid-canvas-cap" data-wid-cap="wid-irsa-canvas" aria-live="polite">다섯 단계로 나눠 봅니다.</span>
</div>
:::

:::script
  var CANVAS_ID = 'wid-irsa-canvas', BASE_W = 960, BASE_H = 360, MAX_STEP = 5, STEP_DUR = 2.4;
  var CAPS = [
    '다섯 단계로 나눠 봅니다. 아래 방향키로 한 단계씩, Play로 전체를 재생합니다.',
    '① ServiceAccount에 role-arn 주석이 있으면 EKS mutating webhook(amazon-eks-pod-identity-webhook)이 새 Pod에 환경 변수 두 개와 projected 토큰 볼륨을 넣습니다.',
    '② kubelet이 audience sts.amazonaws.com인 ServiceAccount 토큰을 받아 파일로 두고, 만료 전에 갱신합니다.',
    '③ SDK가 그 토큰과 AWS_ROLE_ARN으로 리전 STS(Security Token Service)의 AssumeRoleWithWebIdentity를 호출합니다. Pod가 STS에 직접 갑니다.',
    '④ STS는 계정에 등록된 IAM OIDC(OpenID Connect) provider에서 클러스터 issuer를 찾아, issuer 공개 키로 토큰 서명을 검증합니다.',
    '⑤ 역할 신뢰 정책의 aud와 sub 조건이 맞으면 STS가 임시 자격 증명을 돌려줍니다.'
  ];
  function st(n) { return step === n ? 2 : (step > n ? 1 : 0); }
  function render() {
    var B = Colors.blue, G = Colors.green;
    group(20, 20, 470, 322, 'EKS 클러스터');
    group(510, 20, 430, 322, 'AWS 계정');
    // Kubernetes side
    card(40, 50, 200, 84, 'ServiceAccount', [{ t: 'eks.amazonaws.com/', mono: true }, { t: '  role-arn 주석', mono: true }], B, step === 0 ? 1 : st(1));
    card(270, 50, 200, 84, 'EKS mutating webhook', [{ t: 'amazon-eks-pod-', mono: true }, { t: '  identity-webhook', mono: true }], B, st(1));
    var pl = [];
    if (step >= 1) pl.push({ t: 'AWS_ROLE_ARN', mono: true }, { t: 'AWS_WEB_IDENTITY_', mono: true }, { t: '  TOKEN_FILE', mono: true });
    if (step >= 2) pl.push({ t: 'aud sts.amazonaws.com', color: B, weight: '700' });
    if (step >= 5 && prog >= 1) pl.push({ t: '임시 자격 증명 수신', color: G, weight: '700' });
    card(40, 180, 200, 146, 'Pod (SDK)', pl, B, step === 0 ? 1 : (step === 1 || step === 2 || step === 3 || step === 5 ? 2 : 1));
    card(270, 220, 200, 70, 'kubelet', [{ t: '토큰 발급, 만료 전 갱신' }], B, st(2));
    // AWS side
    var tl = [{ t: 'Principal Federated: OIDC provider', mono: true }];
    var ok = step >= 5 && prog > 0.45;
    tl.push({ t: (ok ? '✓ ' : '') + 'aud = sts.amazonaws.com', mono: true, color: ok ? G : undefined, weight: ok ? '700' : undefined });
    tl.push({ t: (ok ? '✓ ' : '') + 'sub = system:serviceaccount:<ns>:<sa>', mono: true, color: ok ? G : undefined, weight: ok ? '700' : undefined });
    card(530, 50, 390, 112, 'IRSA 역할의 신뢰 정책', tl, B, st(5));
    card(530, 214, 190, 82, 'AWS STS (리전)', [{ t: 'AssumeRoleWith', mono: true }, { t: 'WebIdentity', mono: true }], B, step === 3 || step === 4 || step === 5 ? 2 : (step > 3 ? 1 : 0));
    var sig = step >= 4 && (step > 4 || prog > 0.6);
    card(750, 214, 170, 82, 'IAM OIDC provider', [{ t: '클러스터 issuer 등록' }, { t: sig ? '서명 검증 ✓' : 'issuer 공개 키', color: sig ? G : undefined, weight: sig ? '700' : undefined }], B, st(4));
    // wires, completed steps stay drawn
    var inj = [{ x: 370, y: 134 }, { x: 370, y: 158 }, { x: 140, y: 158 }, { x: 140, y: 180 }];
    var sa = [{ x: 240, y: 92 }, { x: 270, y: 92 }];
    var tok = [{ x: 270, y: 255 }, { x: 242, y: 255 }];
    var call = [{ x: 140, y: 326 }, { x: 140, y: 336 }, { x: 625, y: 336 }, { x: 625, y: 296 }];
    var oidc = [{ x: 720, y: 255 }, { x: 750, y: 255 }];
    var trust = [{ x: 625, y: 214 }, { x: 625, y: 162 }];
    var back = [{ x: 560, y: 296 }, { x: 560, y: 331 }, { x: 205, y: 331 }, { x: 205, y: 326 }];
    if (step === 1) { wire(sa, B, seg(0, 0.25)); packet(inj, 0.25, 0.85, 'env + 토큰 볼륨', B); }
    else if (step > 1) { wire(sa, B, 1); wire(inj, B, 1); }
    if (step === 2) packet(tok, 0.1, 0.7, '토큰', B); else if (step > 2) wire(tok, B, 1);
    if (step === 3) packet(call, 0.05, 0.85, '토큰 + 역할 ARN', B); else if (step > 3) wire(call, B, 1);
    if (step === 4) packet(oidc, 0.1, 0.55, '서명 확인', B); else if (step > 4) wire(oidc, B, 1);
    if (step === 5) { wire(trust, B, seg(0, 0.4)); packet(back, 0.55, 1, '자격 증명', G); }
  }
  // Shared canvas helpers (copied into each canvas script so every block HTML stands alone).
  // Proportional scaling: draw in BASE_W x BASE_H, scale by the container (ResizeObserver).
  var canvas = document.getElementById(CANVAS_ID);
  if (!canvas) return;
  var slide = canvas.closest('.slide');
  var box = canvas.parentElement;
  var ctx = canvas.getContext('2d');
  var capEl = slide.querySelector('[data-wid-cap="' + CANVAS_ID + '"]');
  var stepEl = slide.querySelector('[data-wid-step="' + CANVAS_ID + '"]');
  var step = 0, prog = 1, auto = false, lastKey = '';
  var SANS = 'Pretendard, "Apple SD Gothic Neo", "Noto Sans KR", sans-serif';
  var MONO = '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace';
  if (!box.clientWidth) setupCanvas(CANVAS_ID, BASE_W, BASE_H);

  function fit() {
    var pw = box.clientWidth, ph = box.clientHeight;
    if (pw <= 0 || ph <= 0) return false;
    var dpr = window.devicePixelRatio || 1;
    var s = Math.min(pw / BASE_W, ph / BASE_H);
    var key = pw + 'x' + ph + '@' + dpr;
    if (key !== lastKey) {
      lastKey = key;
      canvas.width = Math.round(BASE_W * s * dpr);
      canvas.height = Math.round(BASE_H * s * dpr);
      canvas.style.width = Math.round(BASE_W * s) + 'px';
      canvas.style.height = Math.round(BASE_H * s) + 'px';
      canvas.style.maxWidth = 'none';
      canvas.style.aspectRatio = 'auto';
    }
    ctx.setTransform(s * dpr, 0, 0, s * dpr, 0, 0);
    return true;
  }
  function seg(a, b) { return clamp((prog - a) / (b - a), 0, 1); }
  function rr(x, y, w, h, fill, stroke, lw, dash) {
    ctx.save();
    ctx.beginPath();
    if (ctx.roundRect) ctx.roundRect(x, y, w, h, 8); else ctx.rect(x, y, w, h);
    if (fill) { ctx.fillStyle = fill; ctx.fill(); }
    if (stroke) { ctx.setLineDash(dash || []); ctx.strokeStyle = stroke; ctx.lineWidth = lw || 1.5; ctx.stroke(); }
    ctx.restore();
  }
  function txt(s, x, y, o) {
    o = o || {};
    ctx.fillStyle = o.color || Colors.textPri;
    ctx.font = (o.weight || '400') + ' ' + (o.size || 13) + 'px ' + (o.mono ? MONO : SANS);
    ctx.textAlign = o.align || 'left';
    ctx.textBaseline = 'middle';
    if ('letterSpacing' in ctx) ctx.letterSpacing = o.mono ? '0.3px' : '0px'; // non-zero spacing turns off mono ligatures such as -< and >-
    ctx.fillText(s, x, y);
  }
  // state: 0 = waiting (faded), 1 = shown, 2 = active step
  function card(x, y, w, h, title, lines, col, state) {
    var a = state === 0 ? 0.45 : 1;
    ctx.save();
    ctx.globalAlpha = a;
    rr(x, y, w, h, state === 2 ? withAlpha(col, 0.16) : withAlpha(col, 0.06), state === 2 ? col : withAlpha(col, 0.7), state === 2 ? 3 : 1.5);
    txt(title, x + 12, y + 20, { weight: '700', size: 15 });
    (lines || []).forEach(function (l, i) {
      var o = typeof l === 'string' ? { t: l } : l;
      txt(o.t, x + 12, y + 44 + i * 19, { size: o.mono ? 12 : 12.5, mono: !!o.mono, color: o.color || Colors.textSec, weight: o.weight });
    });
    ctx.restore();
  }
  function group(x, y, w, h, label) {
    rr(x, y, w, h, null, Colors.textMuted, 1.2, [6, 5]);
    txt(label, x + 12, y + 12, { size: 12, color: Colors.textMuted, weight: '600' });
  }
  function plen(p) { var L = 0; for (var i = 1; i < p.length; i++) L += Math.hypot(p[i].x - p[i - 1].x, p[i].y - p[i - 1].y); return L; }
  function at(p, t) {
    var L = plen(p) * clamp(t, 0, 1);
    for (var i = 1; i < p.length; i++) {
      var d = Math.hypot(p[i].x - p[i - 1].x, p[i].y - p[i - 1].y);
      if (L <= d || i === p.length - 1) { var k = d ? Math.min(1, L / d) : 0; return { x: lerp(p[i - 1].x, p[i].x, k), y: lerp(p[i - 1].y, p[i].y, k) }; }
      L -= d;
    }
    return p[p.length - 1];
  }
  // Draws a polyline up to fraction t; adds the arrow head once complete.
  function wire(p, col, t, dashed) {
    if (t <= 0) return;
    var end = at(p, t), L = plen(p) * t, acc = 0;
    ctx.save();
    ctx.strokeStyle = col; ctx.lineWidth = 2.2; ctx.setLineDash(dashed ? [7, 5] : []);
    ctx.beginPath(); ctx.moveTo(p[0].x, p[0].y);
    for (var i = 1; i < p.length; i++) {
      var d = Math.hypot(p[i].x - p[i - 1].x, p[i].y - p[i - 1].y);
      if (acc + d >= L) { ctx.lineTo(end.x, end.y); break; }
      ctx.lineTo(p[i].x, p[i].y); acc += d;
    }
    ctx.stroke();
    ctx.restore();
    if (t >= 1) {
      var a = p[p.length - 2], b = p[p.length - 1], ang = Math.atan2(b.y - a.y, b.x - a.x);
      ctx.beginPath(); ctx.fillStyle = col;
      ctx.moveTo(b.x, b.y);
      ctx.lineTo(b.x - 11 * Math.cos(ang - 0.45), b.y - 11 * Math.sin(ang - 0.45));
      ctx.lineTo(b.x - 11 * Math.cos(ang + 0.45), b.y - 11 * Math.sin(ang + 0.45));
      ctx.closePath(); ctx.fill();
    }
  }
  function pill(x, y, s, col, mono) {
    ctx.save();
    ctx.font = '700 12px ' + (mono ? MONO : SANS);
    var w = ctx.measureText(s).width + 18;
    rr(x - w / 2, y - 12, w, 24, Colors.surface, col, 2);
    ctx.restore();
    txt(s, x, y, { size: 12, weight: '700', color: col, align: 'center', mono: mono });
  }
  // Packet travelling along a wire during [a, b] of the step progress.
  function packet(p, a, b, label, col) {
    var t = seg(a, b);
    wire(p, col, t, false);
    if (t > 0 && t < 1) { var q = at(p, t); pill(q.x, q.y, label, col); }
    return t >= 1;
  }
  function draw() {
    if (!fit()) return;
    ctx.clearRect(0, 0, BASE_W, BASE_H);
    render();
    if (capEl) capEl.textContent = CAPS[step];
    if (stepEl) stepEl.textContent = step + ' / ' + MAX_STEP;
  }
  var loop = new AnimationLoop(function (t) {
    prog = Math.min(1, t / STEP_DUR);
    if (prog >= 1) {
      if (auto && step < MAX_STEP) { step += 1; prog = 0; loop.startTime = performance.now(); }
      else { auto = false; loop.stop(); }
    }
    draw();
  });
  function show(n, animate) {
    loop.stop();
    step = n; prog = animate ? 0 : 1;
    draw();
    if (animate) loop.start();
  }
  slide.querySelectorAll('[data-wid-play="' + CANVAS_ID + '"]').forEach(function (b) {
    b.addEventListener('click', function () { show(1, true); auto = true; });
  });
  slide.querySelectorAll('[data-wid-reset="' + CANVAS_ID + '"]').forEach(function (b) {
    b.addEventListener('click', function () { auto = false; show(0, false); });
  });
  // Up/Down arrow keys step through the animation (framework contract: return false to let the deck move on).
  slide.__canvasStep = function (dir) {
    var n = step + (dir === 'next' ? 1 : -1);
    if (n < 0 || n > MAX_STEP) return false;
    auto = false;
    show(n, dir === 'next');
    return true;
  };
  document.addEventListener('rp:slidechange', function (e) {
    var idx = Array.prototype.indexOf.call(document.querySelectorAll('.slide'), slide);
    if (e.detail && e.detail.index !== idx && (loop.running || step !== 0)) { auto = false; show(0, false); }
  });
  document.addEventListener('rp:themechange', function () { refreshThemeColors(); });
  document.addEventListener('remarp:theme-colors', function () { draw(); });
  new ResizeObserver(function () { draw(); }).observe(box);
  draw();
:::

:::notes
{timing: 2.5min}
[요약]
- 1 주입: role-arn 주석, AWS_ROLE_ARN과 AWS_WEB_IDENTITY_TOKEN_FILE, 토큰 볼륨 /var/run/secrets/eks.amazonaws.com/serviceaccount/token
- 2 토큰: kubelet이 audience sts.amazonaws.com으로 발급하고 만료 전 갱신 (데모 실측 수명 86,400초)
- 3 교환: Pod에서 리전 STS로 직접 AssumeRoleWithWebIdentity
- 4 서명: IAM OIDC provider의 issuer 공개 키로 검증
- 5 신뢰: aud = sts.amazonaws.com, sub = system:serviceaccount:<ns>:<sa>

(아래 방향키)
첫 단계, ServiceAccount에 role-arn 주석이 있으면 Pod를 만들 때 EKS mutating webhook이 환경 변수 두 개와 토큰 볼륨을 넣습니다.
(아래 방향키)
토큰 자체는 kubelet이 받아 옵니다. audience가 sts.amazonaws.com이고, 만료 전에 kubelet이 알아서 갱신합니다.
(아래 방향키)
SDK는 이 토큰과 역할 ARN을 들고 리전 STS에 직접 갑니다. 그래서 프라이빗 클러스터라면 Pod에서 STS로 가는 경로가 필요합니다.
(아래 방향키)
STS는 토큰의 issuer가 계정에 등록된 OIDC provider인지 보고, 그 issuer의 공개 키로 서명을 검증합니다.
(아래 방향키)
마지막으로 역할의 신뢰 정책에서 aud와 sub를 봅니다. sub에 namespace와 ServiceAccount 이름이 들어가니, 이 두 값이 정확히 맞는 Pod만 이 역할을 맡을 수 있습니다.
{cue: transition}
이번에는 Pod Identity입니다. 같은 결과를 전혀 다른 길로 만듭니다.
:::

---
<!-- Slide 4: Pod Identity 흐름 -->
@type: content
@fit: off
@title: Pod Identity: Agent가 대신 묻는다

## Pod Identity: Agent가 대신 묻는다

:::html
<div class="wid-fig-row">
  <figure class="wid-fig">
    <img src="images/ko-security-17-eks-workload-identity-migration-anim-2.svg" alt="Pod Identity 흐름. EKS API의 association이 ServiceAccount를 역할에 연결하고, EKS가 컨테이너 자격 증명 환경 변수와 projected 토큰(aud pods.eks.amazonaws.com)을 Pod에 넣는다. SDK는 같은 노드의 Pod Identity Agent를 호출하고, Agent가 노드 역할의 eks-auth 권한으로 EKS Auth AssumeRoleForPodIdentity를 호출하면 EKS가 세션 태그를 붙여 역할을 맡은 자격 증명을 돌려준다.">
    <figcaption>Pod Identity 전체 흐름 (18초 반복)</figcaption>
  </figure>
  <div class="wid-stack">
    <div class="wid-card wid-podid wid-edge fragment fade-up" data-fragment-index="1"><strong class="wid-t-path">연결</strong><div class="wid-muted">EKS API의 <span class="rp-detail" data-detail="assoc">association</span>, 주석 없음</div></div>
    <div class="wid-card wid-podid wid-edge fragment fade-up" data-fragment-index="2"><strong class="wid-t-path">조회</strong><div class="wid-muted">SDK는 같은 노드의 Agent만 호출</div></div>
    <div class="wid-card wid-podid wid-edge fragment fade-up" data-fragment-index="3"><strong class="wid-t-path">위임</strong><div class="wid-muted">EKS Auth가 역할을 맡고 세션 태그 부착</div></div>
  </div>
</div>
<div class="wid-src">출처: <a href="https://docs.aws.amazon.com/eks/latest/userguide/pod-id-how-it-works.html">Amazon EKS User Guide, How EKS Pod Identity works</a></div>
:::

:::detail assoc "Pod Identity association"
tip: EKS API에 저장하는 연결: 클러스터, namespace, ServiceAccount를 IAM 역할에 매핑

`aws eks create-pod-identity-association`으로 만드는 EKS 리소스입니다. 클러스터, namespace, ServiceAccount 조합을 IAM 역할 하나에 연결합니다. Kubernetes 객체에는 주석을 달지 않으며, 클러스터당 association은 5,000개까지 만들 수 있습니다. 생성 직후 몇 초 동안은 새 Pod에 반영되지 않을 수 있습니다(eventual consistency).
:::

:::notes
{timing: 1min}
[요약]
- 연결: EKS API의 association(클러스터, namespace, ServiceAccount에서 역할로). Kubernetes 객체 변경 없음
- 조회: SDK는 같은 노드의 Pod Identity Agent(169.254.170.23)에만 요청
- 위임: Agent가 EKS Auth AssumeRoleForPodIdentity 호출, EKS가 세션 태그를 붙여 역할을 맡음

Pod Identity 애니메이션입니다. IRSA와 가장 다른 점은 Pod가 AWS 쪽 엔드포인트를 직접 부르지 않는다는 겁니다.
{cue: click}
연결 정보는 ServiceAccount 주석이 아니라 EKS API의 association에 있습니다.
{cue: click}
Pod 안의 SDK는 같은 노드의 Agent에만 요청합니다.
{cue: click}
Agent가 EKS Auth를 부르고, EKS가 세션 태그를 붙여 역할을 맡은 자격 증명을 돌려줍니다.
{cue: transition}
역시 캔버스로 한 단계씩 보겠습니다.
:::

---
<!-- Slide 5: Pod Identity 단계별 캔버스 -->
@type: content
@title: Pod Identity 다섯 단계, 노드는 창구

## Pod Identity 다섯 단계, 노드는 창구

:::html
<div class="wid-canvas-box"><canvas id="wid-podid-canvas" role="img" aria-label="Pod Identity 단계. 1 EKS API의 association이 ServiceAccount를 역할에 연결, 2 새 Pod에 컨테이너 자격 증명 변수와 audience pods.eks.amazonaws.com 토큰 주입, 3 SDK가 같은 노드의 Agent 169.254.170.23에 토큰 전송, 4 Agent가 노드 역할의 eks-auth 권한으로 EKS Auth AssumeRoleForPodIdentity 호출, 5 EKS Auth가 association을 확인하고 세션 태그를 붙여 역할을 맡아 자격 증명 반환."></canvas></div>
<div class="wid-canvas-bar">
  <button class="btn btn-primary btn-sm" data-wid-play="wid-podid-canvas">Play</button>
  <button class="btn btn-sm" data-wid-reset="wid-podid-canvas">Reset</button>
  <span class="wid-step" data-wid-step="wid-podid-canvas">0 / 5</span>
  <span class="wid-canvas-cap" data-wid-cap="wid-podid-canvas" aria-live="polite">다섯 단계로 나눠 봅니다.</span>
</div>
:::

:::script
  var CANVAS_ID = 'wid-podid-canvas', BASE_W = 960, BASE_H = 360, MAX_STEP = 5, STEP_DUR = 2.4;
  var CAPS = [
    '다섯 단계로 나눠 봅니다. 아래 방향키로 한 단계씩, Play로 전체를 재생합니다.',
    '① association은 EKS API에 있습니다. 클러스터, namespace, ServiceAccount를 IAM 역할에 연결하고 Kubernetes 객체는 건드리지 않습니다.',
    '② 그 ServiceAccount로 새 Pod가 생길 때 EKS가 컨테이너 자격 증명 변수 두 개와 audience pods.eks.amazonaws.com 토큰을 넣습니다.',
    '③ SDK는 같은 노드의 Agent(169.254.170.23)에 토큰을 보냅니다. Agent는 hostNetwork로 뜨는 DaemonSet입니다.',
    '④ Agent는 hostNetwork에서 IMDS로 받은 노드 역할 자격 증명으로, 그 역할의 eks-auth:AssumeRoleForPodIdentity 권한을 써서 EKS Auth를 호출합니다.',
    '⑤ EKS Auth가 토큰과 association을 확인하고 세션 태그를 붙여 역할을 맡습니다. 자격 증명은 Agent를 거쳐 Pod로 돌아옵니다.'
  ];
  function st(n) { return step === n ? 2 : (step > n ? 1 : 0); }
  function render() {
    var P = Colors.pink, Y = Colors.yellow, G = Colors.green;
    group(20, 20, 500, 322, '워커 노드');
    group(540, 20, 400, 322, 'AWS (EKS API, EKS Auth, IAM)');
    card(560, 50, 360, 70, 'Pod Identity association', [{ t: '클러스터 + namespace + SA 에 IAM 역할 연결' }], P, step === 0 ? 1 : (step === 1 ? 2 : (step === 5 && prog > 0.2 && prog < 0.5 ? 2 : 1)));
    var pl = [];
    if (step >= 2) pl.push({ t: 'AWS_CONTAINER_', mono: true }, { t: '  CREDENTIALS_FULL_URI', mono: true }, { t: 'AWS_CONTAINER_', mono: true }, { t: '  AUTHORIZATION_TOKEN_FILE', mono: true });
    if (step >= 5 && prog >= 1) pl.push({ t: '임시 자격 증명 수신', color: G, weight: '700' });
    card(40, 50, 220, 160, 'Pod (SDK)', pl, P, step === 2 || step === 3 || step === 5 ? 2 : (step === 0 ? 1 : (step > 2 ? 1 : 0)));
    card(290, 160, 210, 82, 'Pod Identity Agent', [{ t: '169.254.170.23', mono: true }, { t: 'hostNetwork DaemonSet' }], P, step === 3 || step === 4 ? 2 : (step > 4 ? 1 : 0));
    card(290, 258, 210, 80, '노드 IAM 역할', [{ t: 'eks-auth:', mono: true }, { t: 'AssumeRoleForPodIdentity', mono: true }], Y, st(4));
    var tags = step >= 5 && prog > 0.4;
    card(560, 150, 360, 70, 'EKS Auth', [{ t: 'AssumeRoleForPodIdentity', mono: true }], P, step === 4 || step === 5 ? 2 : (step > 4 ? 1 : 0));
    card(560, 238, 360, 98, 'Pod Identity 역할', tags
      ? [{ t: '세션 태그 6개 중 신뢰 조건용 3개:', color: G, weight: '700' }, { t: 'eks-cluster-arn, kubernetes-namespace,', mono: true, color: G }, { t: 'kubernetes-service-account', mono: true, color: G }]
      : [{ t: '앱 업무 권한 (예: S3 읽기)' }], P, step === 5 ? 2 : 0);
    var inj = [{ x: 560, y: 85 }, { x: 260, y: 85 }];
    var tok = [{ x: 150, y: 210 }, { x: 150, y: 228 }, { x: 290, y: 228 }];
    var call = [{ x: 500, y: 185 }, { x: 560, y: 185 }];
    var chk = [{ x: 740, y: 150 }, { x: 740, y: 120 }];
    var role = [{ x: 740, y: 220 }, { x: 740, y: 238 }];
    var back1 = [{ x: 560, y: 210 }, { x: 530, y: 210 }, { x: 530, y: 236 }, { x: 500, y: 236 }];
    var back2 = [{ x: 290, y: 236 }, { x: 100, y: 236 }, { x: 100, y: 210 }];
    if (step === 2) packet(inj, 0.05, 0.75, '주입: env + 토큰', P); else if (step > 2) wire(inj, P, 1);
    if (step === 3) packet(tok, 0.1, 0.75, 'Pod 토큰', P); else if (step > 3) wire(tok, P, 1);
    if (step === 4) packet(call, 0.15, 0.75, '노드 역할로 서명', Y); else if (step > 4) wire(call, Y, 1);
    if (step === 5) {
      wire(chk, P, seg(0, 0.2));
      wire(role, P, seg(0.25, 0.4));
      packet(back1, 0.5, 0.72, '자격 증명', G);
      packet(back2, 0.74, 1, '자격 증명', G);
    }
  }
  // Shared canvas helpers (copied into each canvas script so every block HTML stands alone).
  // Proportional scaling: draw in BASE_W x BASE_H, scale by the container (ResizeObserver).
  var canvas = document.getElementById(CANVAS_ID);
  if (!canvas) return;
  var slide = canvas.closest('.slide');
  var box = canvas.parentElement;
  var ctx = canvas.getContext('2d');
  var capEl = slide.querySelector('[data-wid-cap="' + CANVAS_ID + '"]');
  var stepEl = slide.querySelector('[data-wid-step="' + CANVAS_ID + '"]');
  var step = 0, prog = 1, auto = false, lastKey = '';
  var SANS = 'Pretendard, "Apple SD Gothic Neo", "Noto Sans KR", sans-serif';
  var MONO = '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace';
  if (!box.clientWidth) setupCanvas(CANVAS_ID, BASE_W, BASE_H);

  function fit() {
    var pw = box.clientWidth, ph = box.clientHeight;
    if (pw <= 0 || ph <= 0) return false;
    var dpr = window.devicePixelRatio || 1;
    var s = Math.min(pw / BASE_W, ph / BASE_H);
    var key = pw + 'x' + ph + '@' + dpr;
    if (key !== lastKey) {
      lastKey = key;
      canvas.width = Math.round(BASE_W * s * dpr);
      canvas.height = Math.round(BASE_H * s * dpr);
      canvas.style.width = Math.round(BASE_W * s) + 'px';
      canvas.style.height = Math.round(BASE_H * s) + 'px';
      canvas.style.maxWidth = 'none';
      canvas.style.aspectRatio = 'auto';
    }
    ctx.setTransform(s * dpr, 0, 0, s * dpr, 0, 0);
    return true;
  }
  function seg(a, b) { return clamp((prog - a) / (b - a), 0, 1); }
  function rr(x, y, w, h, fill, stroke, lw, dash) {
    ctx.save();
    ctx.beginPath();
    if (ctx.roundRect) ctx.roundRect(x, y, w, h, 8); else ctx.rect(x, y, w, h);
    if (fill) { ctx.fillStyle = fill; ctx.fill(); }
    if (stroke) { ctx.setLineDash(dash || []); ctx.strokeStyle = stroke; ctx.lineWidth = lw || 1.5; ctx.stroke(); }
    ctx.restore();
  }
  function txt(s, x, y, o) {
    o = o || {};
    ctx.fillStyle = o.color || Colors.textPri;
    ctx.font = (o.weight || '400') + ' ' + (o.size || 13) + 'px ' + (o.mono ? MONO : SANS);
    ctx.textAlign = o.align || 'left';
    ctx.textBaseline = 'middle';
    if ('letterSpacing' in ctx) ctx.letterSpacing = o.mono ? '0.3px' : '0px'; // non-zero spacing turns off mono ligatures such as -< and >-
    ctx.fillText(s, x, y);
  }
  // state: 0 = waiting (faded), 1 = shown, 2 = active step
  function card(x, y, w, h, title, lines, col, state) {
    var a = state === 0 ? 0.45 : 1;
    ctx.save();
    ctx.globalAlpha = a;
    rr(x, y, w, h, state === 2 ? withAlpha(col, 0.16) : withAlpha(col, 0.06), state === 2 ? col : withAlpha(col, 0.7), state === 2 ? 3 : 1.5);
    txt(title, x + 12, y + 20, { weight: '700', size: 15 });
    (lines || []).forEach(function (l, i) {
      var o = typeof l === 'string' ? { t: l } : l;
      txt(o.t, x + 12, y + 44 + i * 19, { size: o.mono ? 12 : 12.5, mono: !!o.mono, color: o.color || Colors.textSec, weight: o.weight });
    });
    ctx.restore();
  }
  function group(x, y, w, h, label) {
    rr(x, y, w, h, null, Colors.textMuted, 1.2, [6, 5]);
    txt(label, x + 12, y + 12, { size: 12, color: Colors.textMuted, weight: '600' });
  }
  function plen(p) { var L = 0; for (var i = 1; i < p.length; i++) L += Math.hypot(p[i].x - p[i - 1].x, p[i].y - p[i - 1].y); return L; }
  function at(p, t) {
    var L = plen(p) * clamp(t, 0, 1);
    for (var i = 1; i < p.length; i++) {
      var d = Math.hypot(p[i].x - p[i - 1].x, p[i].y - p[i - 1].y);
      if (L <= d || i === p.length - 1) { var k = d ? Math.min(1, L / d) : 0; return { x: lerp(p[i - 1].x, p[i].x, k), y: lerp(p[i - 1].y, p[i].y, k) }; }
      L -= d;
    }
    return p[p.length - 1];
  }
  // Draws a polyline up to fraction t; adds the arrow head once complete.
  function wire(p, col, t, dashed) {
    if (t <= 0) return;
    var end = at(p, t), L = plen(p) * t, acc = 0;
    ctx.save();
    ctx.strokeStyle = col; ctx.lineWidth = 2.2; ctx.setLineDash(dashed ? [7, 5] : []);
    ctx.beginPath(); ctx.moveTo(p[0].x, p[0].y);
    for (var i = 1; i < p.length; i++) {
      var d = Math.hypot(p[i].x - p[i - 1].x, p[i].y - p[i - 1].y);
      if (acc + d >= L) { ctx.lineTo(end.x, end.y); break; }
      ctx.lineTo(p[i].x, p[i].y); acc += d;
    }
    ctx.stroke();
    ctx.restore();
    if (t >= 1) {
      var a = p[p.length - 2], b = p[p.length - 1], ang = Math.atan2(b.y - a.y, b.x - a.x);
      ctx.beginPath(); ctx.fillStyle = col;
      ctx.moveTo(b.x, b.y);
      ctx.lineTo(b.x - 11 * Math.cos(ang - 0.45), b.y - 11 * Math.sin(ang - 0.45));
      ctx.lineTo(b.x - 11 * Math.cos(ang + 0.45), b.y - 11 * Math.sin(ang + 0.45));
      ctx.closePath(); ctx.fill();
    }
  }
  function pill(x, y, s, col, mono) {
    ctx.save();
    ctx.font = '700 12px ' + (mono ? MONO : SANS);
    var w = ctx.measureText(s).width + 18;
    rr(x - w / 2, y - 12, w, 24, Colors.surface, col, 2);
    ctx.restore();
    txt(s, x, y, { size: 12, weight: '700', color: col, align: 'center', mono: mono });
  }
  // Packet travelling along a wire during [a, b] of the step progress.
  function packet(p, a, b, label, col) {
    var t = seg(a, b);
    wire(p, col, t, false);
    if (t > 0 && t < 1) { var q = at(p, t); pill(q.x, q.y, label, col); }
    return t >= 1;
  }
  function draw() {
    if (!fit()) return;
    ctx.clearRect(0, 0, BASE_W, BASE_H);
    render();
    if (capEl) capEl.textContent = CAPS[step];
    if (stepEl) stepEl.textContent = step + ' / ' + MAX_STEP;
  }
  var loop = new AnimationLoop(function (t) {
    prog = Math.min(1, t / STEP_DUR);
    if (prog >= 1) {
      if (auto && step < MAX_STEP) { step += 1; prog = 0; loop.startTime = performance.now(); }
      else { auto = false; loop.stop(); }
    }
    draw();
  });
  function show(n, animate) {
    loop.stop();
    step = n; prog = animate ? 0 : 1;
    draw();
    if (animate) loop.start();
  }
  slide.querySelectorAll('[data-wid-play="' + CANVAS_ID + '"]').forEach(function (b) {
    b.addEventListener('click', function () { show(1, true); auto = true; });
  });
  slide.querySelectorAll('[data-wid-reset="' + CANVAS_ID + '"]').forEach(function (b) {
    b.addEventListener('click', function () { auto = false; show(0, false); });
  });
  // Up/Down arrow keys step through the animation (framework contract: return false to let the deck move on).
  slide.__canvasStep = function (dir) {
    var n = step + (dir === 'next' ? 1 : -1);
    if (n < 0 || n > MAX_STEP) return false;
    auto = false;
    show(n, dir === 'next');
    return true;
  };
  document.addEventListener('rp:slidechange', function (e) {
    var idx = Array.prototype.indexOf.call(document.querySelectorAll('.slide'), slide);
    if (e.detail && e.detail.index !== idx && (loop.running || step !== 0)) { auto = false; show(0, false); }
  });
  document.addEventListener('rp:themechange', function () { refreshThemeColors(); });
  document.addEventListener('remarp:theme-colors', function () { draw(); });
  new ResizeObserver(function () { draw(); }).observe(box);
  draw();
:::

:::notes
{timing: 2.5min}
[요약]
- 1 association: EKS API에 저장, 클러스터별 OIDC provider 없음
- 2 주입: AWS_CONTAINER_CREDENTIALS_FULL_URI=http://169.254.170.23/v1/credentials, AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE, audience pods.eks.amazonaws.com 토큰
- 3 Agent: 같은 노드의 hostNetwork DaemonSet, 169.254.170.23
- 4 EKS Auth: Agent가 hostNetwork에서 IMDS로 받은 노드 역할로, eks-auth:AssumeRoleForPodIdentity 권한(AmazonEKSWorkerNodePolicy에 포함)을 써서 호출
- 5 위임: 토큰과 association 확인, 세션 태그 6개 부착. 신뢰 조건에 쓰는 3개는 eks-cluster-arn, kubernetes-namespace, kubernetes-service-account

(아래 방향키)
첫 단계, association은 EKS API에 있습니다. 클러스터마다 OIDC provider를 등록할 필요가 없습니다.
(아래 방향키)
이 ServiceAccount로 Pod가 생기면 EKS가 컨테이너 자격 증명 변수 두 개를 넣습니다. 토큰의 audience가 IRSA와 다르게 pods.eks.amazonaws.com입니다.
(아래 방향키)
SDK는 그 주소, 같은 노드의 Agent로 토큰을 보냅니다.
(아래 방향키)
여기가 오해가 많은 부분입니다. Agent는 hostNetwork에서 IMDS로 노드 역할 자격 증명을 받고, 그 노드 역할로 EKS Auth를 부릅니다. 그래서 노드 역할에 eks-auth 권한이 필요하지만, 노드 역할이 갖는 건 이 "창구 권한"뿐이고 앱의 S3 권한은 없습니다.
(아래 방향키)
EKS Auth가 토큰과 association을 확인하고, 세션 태그 6개를 붙여 역할을 맡습니다. 신뢰 정책 조건에 주로 쓰는 것은 클러스터 ARN, namespace, ServiceAccount 세 개입니다. 자격 증명은 Agent를 거쳐 Pod로 돌아옵니다.
{cue: transition}
이 창구 역할을 하는 Agent를 조금 더 보겠습니다.
:::

---
<!-- Slide 6: Agent와 노드 역할 -->
@type: content
@title: Agent는 노드마다, 권한은 노드 역할에

## Agent는 노드마다, 권한은 노드 역할에

:::html
<div class="wid-grid-2">
  <div class="wid-card fragment fade-up" data-fragment-index="1">
    <h4>eks-pod-identity-agent 애드온</h4>
    <div class="wid-muted">클러스터마다 한 번 설치하는 hostNetwork DaemonSet</div>
    <div class="wid-mono wid-gap-top">169.254.170.23, [fd00:ec2::23]</div>
    <div class="wid-mono">포트 80, 2703</div>
    <div class="wid-cap wid-gap-top">EKS Auto Mode에는 같은 기능이 내장되어 있습니다.</div>
  </div>
  <div class="wid-card wid-node wid-edge fragment fade-up" data-fragment-index="2">
    <h4>노드 역할에 남는 권한</h4>
    <div class="wid-mono">eks-auth:AssumeRoleForPodIdentity</div>
    <div class="wid-muted">AmazonEKSWorkerNodePolicy에 포함. Agent가 EKS Auth를 부르는 데만 씁니다.</div>
    <div class="wid-muted">Agent는 hostNetwork에서 IMDS로 이 역할의 자격 증명을 받습니다.</div>
    <div class="wid-cap wid-gap-top">앱의 업무 권한은 Pod Identity 역할에 둡니다.</div>
  </div>
</div>
<div class="callout callout-info wid-gap-top fragment fade-up" data-fragment-index="3"><strong class="wid-t-info">프록시 환경</strong>: <code>169.254.170.23</code>과 <code>[fd00:ec2::23]</code>을 <code>NO_PROXY</code>에 넣어야 SDK 요청이 Agent에 닿습니다.</div>
<div class="wid-src">출처: <a href="https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html">Amazon EKS User Guide, EKS Pod Identity considerations</a></div>
:::

:::notes
{timing: 1min}
[요약]
- Agent: eks-pod-identity-agent 애드온, hostNetwork DaemonSet, 169.254.170.23과 [fd00:ec2::23], 포트 80과 2703
- Auto Mode는 내장, 그 외에는 클러스터마다 애드온 한 번
- 노드 역할에는 eks-auth:AssumeRoleForPodIdentity(AmazonEKSWorkerNodePolicy 포함)만 필요, 업무 권한은 Pod Identity 역할
- Agent 자신은 hostNetwork에서 IMDS로 노드 역할을 받음. 그래서 hop limit 1에서도 동작하고, IMDS 자체를 끄면 Pod Identity가 멈춤
- 프록시를 쓰면 두 주소를 NO_PROXY에

{cue: click}
Agent는 애드온 하나입니다. 노드 네트워크에서 링크 로컬 주소로 듣는 DaemonSet이고, Auto Mode라면 따로 설치할 것이 없습니다.
{cue: click}
노드 역할에는 Agent가 EKS Auth를 부를 권한이 있어야 합니다. 이미 AmazonEKSWorkerNodePolicy에 들어 있으니 보통은 따로 붙일 게 없습니다. Agent는 이 자격 증명을 hostNetwork에서 IMDS로 받는다는 점도 기억해 두세요. 뒤에서 Pod의 IMDS 경로를 닫을 때 다시 나옵니다.
{cue: click}
실무에서 자주 막히는 곳은 프록시입니다. HTTP 프록시를 쓰는 앱이라면 두 Agent 주소를 NO_PROXY에 넣어야 합니다.
{cue: transition}
이제 두 방식을 나란히 놓겠습니다.
:::

---
<!-- Slide 7: 비교 1, 연결 방식 -->
@type: content
@title: 비교 1: 신뢰와 연결을 거는 위치

## 비교 1: 신뢰와 연결을 거는 위치

:::html
<div class="tab-bar">
  <button class="tab-btn active" data-tab="cmp-setup">준비와 연결 위치</button>
  <button class="tab-btn" data-tab="cmp-trust">신뢰 정책 JSON</button>
  <button class="tab-btn" data-tab="cmp-duty">권한 분리</button>
</div>
<div class="tab-content active" data-tab="cmp-setup">
  <div class="wid-grid-2">
    <div class="wid-card wid-irsa wid-edge"><span class="wid-chip wid-irsa">IRSA</span>
      <div class="wid-muted wid-gap-top"><strong>클러스터 준비</strong>: 클러스터마다 IAM OIDC provider 등록</div>
      <div class="wid-muted"><strong>연결 위치</strong>: Kubernetes ServiceAccount 주석</div>
      <div class="wid-mono wid-gap-top">eks.amazonaws.com/role-arn: arn:aws:iam::&lt;ACCOUNT_ID&gt;:role/wid-&lt;run&gt;-irsa</div></div>
    <div class="wid-card wid-podid wid-edge"><span class="wid-chip wid-podid">Pod Identity</span>
      <div class="wid-muted wid-gap-top"><strong>클러스터 준비</strong>: 클러스터마다 Agent 애드온 (Auto Mode는 내장)</div>
      <div class="wid-muted"><strong>연결 위치</strong>: EKS API association, Kubernetes 객체 변경 없음</div>
      <div class="wid-mono wid-gap-top">aws eks create-pod-identity-association --namespace wid-&lt;run&gt; --service-account orders-podid --role-arn ...</div></div>
  </div>
</div>
<div class="tab-content" data-tab="cmp-trust">
  <div class="wid-grid-2">
    <div><span class="wid-chip wid-irsa">IRSA: Federated + aud, sub</span>
<pre class="wid-term">{
  "Effect": "Allow",
  "Principal": {"Federated":
    "arn:aws:iam::&lt;ACCOUNT_ID&gt;:oidc-provider/&lt;OIDC_ISSUER&gt;"},
  "Action": "sts:AssumeRoleWithWebIdentity",
  "Condition": {"StringEquals": {
    "&lt;OIDC_ISSUER&gt;:aud": "sts.amazonaws.com",
    "&lt;OIDC_ISSUER&gt;:sub":
      "system:serviceaccount:&lt;NAMESPACE&gt;:&lt;IRSA_SA&gt;"
  }}
}</pre>
      <div class="wid-cap">클러스터가 늘 때마다 이 문장을 추가합니다.</div></div>
    <div><span class="wid-chip wid-podid">Pod Identity: 서비스 principal 하나</span>
<pre class="wid-term">{
  "Effect": "Allow",
  "Principal": {"Service": "pods.eks.amazonaws.com"},
  "Action": ["sts:AssumeRole", "sts:TagSession"],
  "Condition": {"StringEquals": {
    "aws:RequestTag/eks-cluster-arn": "&lt;CLUSTER_ARN&gt;",
    "aws:RequestTag/kubernetes-namespace": "&lt;NAMESPACE&gt;",
    "aws:RequestTag/kubernetes-service-account":
      "&lt;POD_IDENTITY_SA&gt;"
  }}
}</pre>
      <div class="wid-cap">조건은 선택입니다. 쓰려면 association의 세션 태그를 켠 상태로 둡니다.</div></div>
  </div>
</div>
<div class="tab-content" data-tab="cmp-duty">
  <div class="wid-grid-2">
    <div class="wid-card wid-irsa wid-edge"><span class="wid-chip wid-irsa">IRSA</span>
      <div class="wid-muted wid-gap-top">OIDC provider 생성과 신뢰 정책은 IAM 관리자, 주석은 클러스터 운영자</div>
      <div class="wid-cap wid-gap-top">신뢰 정책에 클러스터 issuer가 들어가 두 팀이 함께 바꿔야 합니다.</div></div>
    <div class="wid-card wid-podid wid-edge"><span class="wid-chip wid-podid">Pod Identity</span>
      <div class="wid-muted wid-gap-top">IAM은 역할만, 연결은 EKS API에서</div>
      <div class="wid-cap wid-gap-top">팀 간 책임 경계가 명확합니다.</div></div>
  </div>
</div>
<div class="wid-src">출처: <a href="https://docs.aws.amazon.com/eks/latest/userguide/service-accounts.html">Amazon EKS User Guide, Grant Kubernetes workloads access to AWS (IRSA와 Pod Identity 비교)</a></div>
:::

:::notes
{timing: 2min}
[요약]
- 준비: IRSA는 클러스터마다 IAM OIDC provider, Pod Identity는 클러스터마다 Agent 애드온(Auto Mode 내장)
- 연결: IRSA는 ServiceAccount 주석, Pod Identity는 EKS API association
- 신뢰 정책: IRSA는 Federated provider와 aud, sub 조건으로 클러스터마다 문장 추가, Pod Identity는 pods.eks.amazonaws.com 하나
- 권한 분리: Pod Identity는 IAM(역할)과 EKS API(연결)로 책임이 나뉨

비교는 두 장으로 나눴습니다. 이 장은 "어디에 무엇을 거느냐"입니다. 위아래 방향키로 탭을 넘기겠습니다.
첫 탭, IRSA는 연결 정보가 ServiceAccount 주석, 즉 Kubernetes 안에 있고, Pod Identity는 EKS API에 있습니다.
(아래 방향키)
두 번째 탭이 신뢰 정책입니다. IRSA는 클러스터의 issuer가 정책 안에 박혀 있어서 클러스터가 늘 때마다 문장을 추가합니다. Pod Identity는 서비스 principal 하나라 새 클러스터에서도 고칠 게 없고, 요청 태그 조건으로 범위를 좁힙니다.
(아래 방향키)
세 번째, 그래서 조직 측면에서는 Pod Identity가 IAM 팀과 클러스터 팀의 경계를 더 깔끔하게 나눕니다.
{cue: transition}
두 번째 비교는 실행 경로와 한도입니다.
:::

---
<!-- Slide 8: 비교 2, 경로와 한도 -->
@type: content
@title: 비교 2: 경로, 태그, 한도, 실행 환경

## 비교 2: 경로, 태그, 한도, 실행 환경

:::html
<div class="tab-bar">
  <button class="tab-btn active" data-tab="cmp-path">자격 증명 경로</button>
  <button class="tab-btn" data-tab="cmp-tags">세션 태그</button>
  <button class="tab-btn" data-tab="cmp-scale">확장 한도</button>
  <button class="tab-btn" data-tab="cmp-env">실행 환경</button>
  <button class="tab-btn" data-tab="cmp-xacct">교차 계정</button>
</div>
<div class="tab-content active" data-tab="cmp-path">
  <div class="wid-grid-2">
    <div class="wid-card wid-irsa wid-edge"><span class="wid-chip wid-irsa">IRSA</span><h4 class="wid-gap-top">Pod에서 리전 STS로</h4><div class="wid-muted">Pod가 STS API 할당량을 씁니다. Pod에서 STS로 가는 경로가 필요합니다.</div></div>
    <div class="wid-card wid-podid wid-edge"><span class="wid-chip wid-podid">Pod Identity</span><h4 class="wid-gap-top">Pod, 노드 Agent, EKS Auth</h4><div class="wid-muted">Pod는 STS를 직접 호출하지 않습니다. Agent에서 EKS Auth로 가는 경로가 필요합니다.</div></div>
  </div>
</div>
<div class="tab-content" data-tab="cmp-tags">
  <div class="wid-grid-2">
    <div class="wid-card wid-irsa wid-edge"><span class="wid-chip wid-irsa">IRSA</span><h4 class="wid-gap-top">역할 세션 이름만</h4><div class="wid-muted">세션 태그가 없습니다.</div></div>
    <div class="wid-card wid-podid wid-edge"><span class="wid-chip wid-podid">Pod Identity</span><h4 class="wid-gap-top">세션 태그 6개</h4><div class="wid-row wid-mono"><code>eks-cluster-arn</code><code>eks-cluster-name</code><code>kubernetes-namespace</code><code>kubernetes-service-account</code><code>kubernetes-pod-name</code><code>kubernetes-pod-uid</code></div><div class="wid-cap">신뢰 조건에는 보통 앞의 3개(클러스터 ARN, namespace, SA)를 씁니다.</div><div class="wid-muted">태그로 리소스 접근을 거는 <span class="rp-detail" data-detail="abac">ABAC(attribute-based access control)</span>이 가능합니다.</div></div>
  </div>
</div>
<div class="tab-content" data-tab="cmp-scale">
  <div class="wid-grid-2">
    <div class="wid-card wid-irsa wid-edge"><span class="wid-chip wid-irsa">IRSA</span><div class="wid-big wid-gap-top">100</div><div class="wid-muted">계정당 OIDC provider 기본 한도</div><div class="wid-muted wid-gap-top">신뢰 정책 기본 2,048자, 보통 역할당 4개 안팎의 연결</div></div>
    <div class="wid-card wid-podid wid-edge"><span class="wid-chip wid-podid">Pod Identity</span><div class="wid-big wid-gap-top">5,000</div><div class="wid-muted">클러스터당 association</div><div class="wid-muted wid-gap-top">역할의 신뢰 정책은 클러스터가 늘어도 그대로</div></div>
  </div>
</div>
<div class="tab-content" data-tab="cmp-env">
  <div class="wid-grid-2">
    <div class="wid-card wid-irsa wid-edge"><span class="wid-chip wid-irsa">IRSA</span><h4 class="wid-gap-top">EKS 밖에서도 같은 방식</h4><div class="wid-muted">EKS의 EC2와 Fargate, EKS Anywhere, ROSA(Red Hat OpenShift Service on AWS), EC2의 자체 관리 Kubernetes</div></div>
    <div class="wid-card wid-podid wid-edge"><span class="wid-chip wid-podid">Pod Identity</span><h4 class="wid-gap-top">EKS의 Linux EC2 노드만</h4><div class="wid-muted">Fargate, Windows, Outposts, EKS Anywhere는 지원하지 않습니다.</div></div>
  </div>
</div>
<div class="tab-content" data-tab="cmp-xacct">
  <div class="wid-grid-2">
    <div class="wid-card wid-irsa wid-edge"><span class="wid-chip wid-irsa">IRSA</span><h4 class="wid-gap-top">대상 계정 역할이 OIDC provider를 신뢰</h4><div class="wid-muted">대상 계정에 이 클러스터의 provider를 등록합니다.</div></div>
    <div class="wid-card wid-podid wid-edge"><span class="wid-chip wid-podid">Pod Identity</span><h4 class="wid-gap-top">association 역할은 같은 계정</h4><div class="wid-muted">대상 역할을 지정하거나 역할 체이닝으로 위임합니다.</div></div>
  </div>
</div>
<div class="wid-src">출처: <a href="https://docs.aws.amazon.com/eks/latest/userguide/service-accounts.html">Amazon EKS User Guide, IRSA와 Pod Identity 비교</a>, <a href="https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html">EKS Pod Identity considerations</a></div>
:::

:::detail abac "ABAC (Attribute-based access control)"
tip: 역할 대신 태그 같은 속성으로 권한을 거는 방식

IAM 정책 조건에서 `aws:PrincipalTag/kubernetes-namespace` 같은 세션 태그를 비교해 접근을 허용하는 방식입니다. Pod Identity는 클러스터, namespace, ServiceAccount, Pod 이름과 UID를 담은 세션 태그 6개를 붙이므로, 역할 하나를 여러 워크로드가 쓰더라도 태그로 리소스 범위를 나눌 수 있습니다.
:::

:::notes
{timing: 2min}
[요약]
- 경로: IRSA는 Pod에서 리전 STS(Pod가 STS 할당량 사용), Pod Identity는 Agent에서 EKS Auth
- 세션 태그: IRSA 없음, Pod Identity는 6개(클러스터 ARN과 이름, namespace, SA, Pod 이름과 UID)로 ABAC 가능
- 한도: OIDC provider 계정당 기본 100개, 신뢰 정책 2,048자(역할당 4개 안팎) 대 association 클러스터당 5,000개
- 실행 환경: IRSA는 Fargate, EKS Anywhere, ROSA, 자체 관리 Kubernetes까지, Pod Identity는 EKS Linux EC2만
- 교차 계정: IRSA는 대상 계정이 provider 신뢰, Pod Identity는 같은 계정 역할에서 대상 역할 지정 또는 체이닝

이 장은 다섯 탭입니다. 첫째 경로, IRSA는 Pod가 STS를 직접 부르고 Pod Identity는 Agent를 거칩니다. 프라이빗 클러스터라면 필요한 엔드포인트가 다릅니다.
(아래 방향키)
둘째 세션 태그입니다. Pod Identity는 클러스터 ARN과 이름, namespace, ServiceAccount, Pod 이름과 UID까지 태그 여섯 개가 붙어서, 정책 조건으로 태그를 비교하는 ABAC이 됩니다.
(아래 방향키)
셋째 한도입니다. OIDC provider는 계정당 기본 100개, 신뢰 정책은 기본 2,048자라 역할 하나에 클러스터 네 개 정도면 찹니다. 클러스터가 많은 조직이라면 이 숫자가 결정적입니다.
(아래 방향키)
넷째 실행 환경은 IRSA가 넓습니다. Fargate나 Windows 노드, EKS 밖의 Kubernetes라면 IRSA입니다.
(아래 방향키)
마지막 교차 계정은 둘 다 가능하지만 방식이 다릅니다.
{cue: transition}
그럼 무엇을 고르면 될까요.

[약어]
- ABAC: Attribute-based access control
- ROSA: Red Hat OpenShift Service on AWS
:::

---
<!-- Slide 9: 선택 기준 -->
@type: content
@title: 기본은 Pod Identity, 예외는 IRSA

## 기본은 Pod Identity, 예외는 IRSA

:::html
<div class="wid-grid-3">
  <div class="wid-card wid-podid wid-edge fragment fade-up" data-fragment-index="1">
    <span class="wid-chip wid-podid">Pod Identity</span>
    <h4 class="wid-gap-top">신규 EKS Linux EC2 워크로드</h4>
    <div class="wid-muted">여러 클러스터에서 같은 역할, 세션 태그 ABAC, 팀 간 책임 분리</div>
  </div>
  <div class="wid-card wid-irsa wid-edge fragment fade-up" data-fragment-index="2">
    <span class="wid-chip wid-irsa">IRSA</span>
    <h4 class="wid-gap-top">Pod Identity가 닿지 않는 곳</h4>
    <div class="wid-muted">Fargate, Windows 노드, EKS 밖의 Kubernetes와 구성을 공유하는 워크로드</div>
  </div>
  <div class="wid-card fragment fade-up" data-fragment-index="3">
    <span class="wid-chip">함께 쓰기</span>
    <h4 class="wid-gap-top">한 클러스터에 공존 가능</h4>
    <div class="wid-muted">워크로드마다 고르고, 전환이 끝난 SA에는 한 방식만 남깁니다.</div>
  </div>
</div>
<div class="callout callout-info wid-gap-top fragment fade-up" data-fragment-index="4"><strong class="wid-t-info">AWS 권장</strong>: 가능한 경우 EKS Pod Identity를 씁니다. 실행 환경과 조직 구조에 따라 IRSA가 맞는 경우가 있습니다.</div>
<div class="wid-src">출처: <a href="https://docs.aws.amazon.com/eks/latest/userguide/service-accounts.html">Amazon EKS User Guide, Grant Kubernetes workloads access to AWS</a></div>
:::

:::notes
{timing: 1.5min}
[요약]
- 신규 EKS Linux EC2 워크로드: Pod Identity가 단순하고 확장에 유리
- Fargate, Windows, EKS 밖 Kubernetes와 구성 공유: IRSA
- 두 방식은 한 클러스터에서 공존 가능, 전환이 끝나면 한 ServiceAccount에는 한 방식만
- AWS는 가능한 경우 Pod Identity를 권장

{cue: click}
기본값은 Pod Identity입니다. 클러스터가 늘어도 신뢰 정책을 건드리지 않고, 세션 태그가 붙고, 팀 경계가 깔끔합니다.
{cue: click}
IRSA는 Pod Identity가 지원하지 않는 곳에서 씁니다. Fargate, Windows 노드, 그리고 EKS 밖의 Kubernetes와 같은 매니페스트를 공유해야 하는 경우입니다.
{cue: click}
둘은 한 클러스터에서 같이 써도 됩니다. 한 ServiceAccount에 둘을 함께 걸면 어떻게 되는지는 다음 장에서 보겠습니다.
{cue: click}
AWS 문서도 가능한 경우 Pod Identity를 권장하고, 환경에 따라 IRSA가 맞을 수 있다고 적고 있습니다.
{cue: transition}
IRSA에서 Pod Identity로 옮기는 도중, 한 ServiceAccount에 둘이 함께 걸린 상태를 보겠습니다.
:::

---
<!-- Slide 10: 공존과 프라이빗 경로 -->
@type: content
@title: 주석이 남아도 새 Pod는 Pod Identity

## 주석이 남아도 새 Pod는 Pod Identity

:::html
<div class="wid-grid-2">
  <div class="wid-card fragment fade-up" data-fragment-index="1">
    <h4>IRSA에서 Pod Identity로 옮기는 도중</h4>
<pre class="wid-term">ServiceAccount orders   <span class="wid-dim"># role-arn 주석이 남아 있음</span>
association    orders   ...:role/new-podid

<span class="wid-dim"># 새 Pod: EKS 웹훅이 Pod Identity 변수만 주입</span>
AWS_CONTAINER_CREDENTIALS_FULL_URI
AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE
<span class="wid-dim"># association 전에 만든 Pod: IRSA 변수 유지</span>
AWS_ROLE_ARN, AWS_WEB_IDENTITY_TOKEN_FILE</pre>
    <div class="wid-muted wid-gap-top">결정은 SDK 체인이 아니라 주입 단계에서 납니다. 기존 Pod는 재생성 전까지 IRSA입니다.</div>
  </div>
  <div class="wid-stack">
    <div class="callout callout-warning fragment fade-up" data-fragment-index="2"><strong class="wid-t-warning">체인 순서와 헷갈리지 않기</strong>: 체인에서는 웹 ID 토큰이 앞이지만, EKS는 한 Pod에 두 변수 세트를 함께 넣지 않습니다.</div>
    <div class="wid-card fragment fade-up" data-fragment-index="3">
      <h4>프라이빗 클러스터에서 열어 둘 경로</h4>
      <div class="wid-row wid-gap-top"><span class="wid-chip wid-irsa">IRSA</span><span class="wid-muted">Pod에서 리전 STS</span></div>
      <div class="wid-row wid-gap-top"><span class="wid-chip wid-podid">Pod Identity</span><span class="wid-muted">Agent에서 EKS Auth (<code>eks-auth</code>)</span></div>
      <div class="wid-cap wid-gap-top">인터넷 경로가 없으면 VPC 인터페이스 엔드포인트, DNS, 보안 그룹을 각각 확인합니다.</div>
    </div>
  </div>
</div>
<div class="wid-src">출처: 데모 클러스터 server-side dry run 검증, <a href="https://github.com/aws/amazon-eks-pod-identity-webhook">aws/amazon-eks-pod-identity-webhook</a> (container credentials가 우선), <a href="https://docs.aws.amazon.com/eks/latest/userguide/private-clusters.html">EKS private cluster requirements</a></div>
:::

:::notes
{timing: 1.5min}
[요약]
- 같은 ServiceAccount에 IRSA 주석과 association이 모두 있으면, 새 Pod에는 EKS 웹훅이 Pod Identity 변수만 넣음(association이 이김)
- association 전에 만든 Pod는 IRSA 변수를 그대로 갖고 재생성 전까지 IRSA. 롤아웃 중에는 두 역할이 섞여 보일 수 있음
- SDK 체인 순서(웹 ID 토큰이 앞)와 혼동 금지: 두 변수 세트가 한 Pod에 함께 주입되지 않음
- 전환이 끝나면 주석을 지워 설정을 하나로 정리
- 프라이빗 클러스터: IRSA는 STS, Pod Identity는 eks-auth 엔드포인트 경로를 각각 확보

{cue: click}
IRSA를 쓰던 앱을 Pod Identity로 옮기는 도중이라고 해 보겠습니다. ServiceAccount에는 role-arn 주석이 남아 있고, association을 새로 만들었습니다. 이때 새로 만든 Pod에는 EKS 웹훅이 Pod Identity 변수만 넣고 IRSA 변수는 넣지 않습니다. 데모 클러스터에서 server-side dry run으로 직접 확인했습니다.
association을 만들기 전에 떠 있던 Pod는 IRSA 변수를 그대로 갖고 있으니, rollout이 끝날 때까지는 두 역할이 섞여 보일 수 있습니다. 전환이 끝나면 주석을 지워 설정을 하나로 정리합니다.
{cue: click}
1부 체인 그림만 생각하면 IRSA가 이길 것 같지만, 결정은 그보다 앞의 주입 단계에서 납니다. 이 부분은 헷갈리기 쉬우니 꼭 구분해 주세요.
{cue: click}
프라이빗 클러스터라면 필요한 경로가 다릅니다. IRSA는 Pod에서 STS로, Pod Identity는 Agent에서 EKS Auth로 가는 길이 필요합니다.
{cue: transition}
이제 운영 클러스터에서 실제로 옮기는 순서입니다.
:::

---
<!-- Slide 11: 운영 이전 순서 -->
@type: timeline
@title: 운영 이전은 다섯 단계, 회수는 맨 뒤

## 운영 이전은 다섯 단계, 회수는 맨 뒤

### 의존성 조사
노드 역할 정책과 CloudTrail의 실제 세션 비교
워커 노드, ECR pull 권한은 유지

### 역할과 전용 SA 준비
리소스 단위로 제한한 워크로드 역할
SDK 최소 버전 확인

### 카나리 Pod 새로 생성
주입된 env 이름, 호출자 ARN, API 성공 확인
토큰과 키는 로그에 출력하지 않기

### 순차 전환 후 회수
AccessDenied, 갱신, 크론까지 관찰
노드 역할의 해당 정책 문장만 회수

### 노드 접근 제한
IMDSv2 강제, hop limit 1
hostNetwork Pod는 별도 통제

:::notes
{timing: 2.5min}
[요약]
- 1 조사: 노드 역할 정책 대 CloudTrail 실제 세션, S3는 데이터 이벤트 필요. AmazonEKSWorkerNodePolicy, AmazonEC2ContainerRegistryPullOnly(또는 동등)는 유지. AmazonEKS_CNI_Policy는 aws-node 전용 역할로 옮길 수 있음
- 2 준비: 워크로드별 역할과 전용 ServiceAccount, IRSA는 aud와 정확한 sub, Pod Identity는 요청 태그 조건. SDK 최소 버전 확인
- 3 카나리: Pod를 새로 만들고 env 이름, 호출자 ARN, 실제 API 성공을 확인
- 4 전환과 회수: AccessDenied, 자격 증명 갱신, 크론까지 본 뒤 정책 문장만 회수. 롤백은 최소 정책 복구, 전파 확인, 이전 Pod 배포 순
- 5 제한: IMDSv2 강제와 hop limit 1, hostNetwork Pod는 따로

위아래 방향키로 한 단계씩 넘깁니다. 첫 단계는 조사입니다. 노드 역할에 붙은 정책과 CloudTrail에 실제로 찍힌 세션을 비교해서, 어떤 워크로드가 무엇을 쓰는지 봅니다. 노드 등록과 ECR pull 권한은 남겨야 하고, CNI 정책은 aws-node 전용 역할로 옮길 수 있습니다.
(아래 방향키)
둘째, 워크로드마다 역할과 전용 ServiceAccount를 만듭니다. 앱의 SDK가 IRSA나 Pod Identity를 지원하는 최소 버전인지도 여기서 봅니다.
(아래 방향키)
셋째, 카나리입니다. 핵심은 Pod를 새로 만드는 것과, 호출 성공이 아니라 호출자 ARN을 확인하는 것입니다.
(아래 방향키)
넷째, 나머지를 순서대로 옮기고 크론 실행까지 지켜본 뒤에야 노드 역할에서 그 정책 문장만 뺍니다. 되돌릴 때는 정책을 먼저 복구하고 전파를 확인한 다음 이전 Pod를 배포합니다.
(아래 방향키)
다섯째가 Pod의 IMDS 경로 차단입니다. 다음 장에서 보겠습니다.
{cue: transition}
노드 종류별로 Pod의 IMDS 경로를 어떻게 닫는지입니다.

[출처]
- EKS 노드 IAM 역할: https://docs.aws.amazon.com/eks/latest/userguide/create-node-role.html
- S3 CloudTrail 데이터 이벤트: https://docs.aws.amazon.com/AmazonS3/latest/userguide/cloudtrail-logging-s3-info.html
- SDK 최소 버전: https://docs.aws.amazon.com/eks/latest/userguide/pod-id-minimum-sdk.html
:::

---
<!-- Slide 12: IMDS 차단 -->
@type: content
@title: 마지막에 Pod의 IMDS 길을 닫는다

## 마지막에 Pod의 IMDS 길을 닫는다

:::html
<div class="wid-grid-3">
  <div class="wid-card fragment fade-up" data-fragment-index="1">
    <h4>관리형 노드 그룹</h4>
    <div class="wid-muted">launch template 새 버전에 지정하고 롤링 교체</div>
<pre class="wid-term wid-gap-top">HttpTokens=required
HttpPutResponseHopLimit=1</pre>
  </div>
  <div class="wid-card fragment fade-up" data-fragment-index="2">
    <h4>Karpenter</h4>
    <div class="wid-muted">EC2NodeClass 기본값이 이미 required, hop limit 1. 2로 바꿔 둔 NodeClass만 되돌림</div>
<pre class="wid-term wid-gap-top">spec:
  metadataOptions:
    httpTokens: required
    httpPutResponseHopLimit: 1</pre>
  </div>
  <div class="wid-card fragment fade-up" data-fragment-index="3">
    <h4>EKS Auto Mode</h4>
    <div class="wid-muted">IMDSv2와 hop limit 1이 기본 적용</div>
    <div class="wid-cap wid-gap-top">별도 설정 없이 일반 Pod의 IMDS 경로가 닫혀 있습니다.</div>
  </div>
</div>
<div class="wid-grid-2 wid-gap-top">
  <div class="callout callout-warning fragment fade-up" data-fragment-index="4"><strong class="wid-t-warning">hostNetwork Pod는 예외</strong>: 노드 네트워크를 그대로 쓰므로 hop limit과 관계없이 IMDS에 닿습니다. 별도로 통제합니다.</div>
  <div class="callout callout-warning fragment fade-up" data-fragment-index="5"><strong class="wid-t-warning">IMDS 자체는 끄지 않기</strong>: Pod Identity Agent도 hostNetwork에서 IMDS로 노드 역할을 받습니다. <code>HttpEndpoint=disabled</code>면 Pod Identity가 멈춥니다.</div>
</div>
<div class="wid-src">출처: <a href="https://docs.aws.amazon.com/eks/latest/userguide/launch-templates.html">EKS managed node group launch templates</a>, <a href="https://docs.aws.amazon.com/eks/latest/best-practices/identity-and-access-management.html">EKS Best Practices, Identity and Access Management</a>, <a href="https://karpenter.sh/docs/concepts/nodeclasses/">Karpenter EC2NodeClass</a></div>
:::

:::notes
{timing: 1.5min}
[요약]
- 관리형 노드 그룹: launch template 새 버전에 HttpTokens=required, HttpPutResponseHopLimit=1, 롤링 교체
- Karpenter: EC2NodeClass.spec.metadataOptions, 기본값이 이미 required와 hop limit 1. 2로 바꾼 NodeClass만 되돌림
- Auto Mode: IMDSv2와 hop limit 1 기본
- hostNetwork Pod는 hop limit과 무관하게 IMDS 접근, 별도 통제
- hop limit 1로 일반 Pod의 경로만 닫고 IMDS 자체는 켜 둠. Agent가 hostNetwork에서 IMDS로 노드 역할을 받기 때문(HttpEndpoint=disabled면 Pod Identity 중단)
- 호환성을 검증한 노드 그룹부터 적용

{cue: click}
관리형 노드 그룹은 launch template 새 버전을 만들고 롤링 교체합니다. 노드가 바뀌어야 적용되니 시간이 걸립니다. 오늘 데모 환경에서는 노드 한 대 교체에 15분 가까이 걸렸습니다.
{cue: click}
Karpenter는 EC2NodeClass의 metadataOptions에서 정하는데, 기본값이 이미 httpTokens required, hop limit 1입니다. 2로 바꿔 둔 NodeClass가 있는지만 확인해서 되돌리면 됩니다.
{cue: click}
Auto Mode는 이미 IMDSv2와 hop limit 1이 기본입니다.
{cue: click}
예외가 하나 있습니다. hostNetwork Pod는 노드 네트워크를 그대로 쓰니 hop limit을 1로 내려도 IMDS에 닿습니다. 이런 Pod는 별도로 관리해야 합니다.
{cue: click}
그리고 "닫는다"는 말을 IMDS를 끈다는 뜻으로 받아들이시면 안 됩니다. Pod Identity Agent도 hostNetwork에서 IMDS로 노드 역할을 받아서 EKS Auth를 부릅니다. hop limit 1에서 Agent가 살아 있는 것도 hostNetwork이기 때문이고, HttpEndpoint를 disabled로 하면 Pod Identity 전체가 멈춥니다.
{cue: transition}
여기까지가 원리입니다. 이제 실제 클러스터에서 확인하겠습니다.
:::
