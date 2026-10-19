---
remarp: true
block: 05-live-demo
---

---
<!-- Slide 1: 5부 구분 -->
@type: section
@title: 5부: 라이브 데모, 직접 돌려 본 결과

# 5부: 라이브 데모, 직접 돌려 본 결과

gateway 전환, bursting, GPU 추론, Istio 공존, SNAT 없는 연결의 실측

:::notes
{timing: 0.5min}
[요약]
• 앞선 네 파트의 내용을 실제 클러스터에서 돌려 본 결과를 보여 줌
• 수치는 모두 2026-10-17 기준 실측이고 시나리오당 1회 측정
• 환경은 온프렘을 시뮬레이션한 구성이라는 점을 먼저 밝힘

지금까지는 문서와 개념을 봤습니다. 5부는 같은 내용을 실제 클러스터에서 돌려 본 기록입니다.
먼저 어떤 환경에서 돌렸는지부터 정확히 말씀드리겠습니다.
{cue: transition}
:::

---
<!-- Slide 2: 시뮬레이션 환경 -->
@type: content
@title: 온프렘을 시뮬레이션한 환경에서 돌렸다

## 온프렘을 시뮬레이션한 환경에서 돌렸다

:::html
<style>
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.ld-arch { display: grid; grid-template-columns: 1fr auto 1fr; gap: var(--space-3); align-items: stretch; margin-bottom: var(--space-4); }
.ld-vpc { border: 1px solid var(--border); border-radius: var(--space-2); padding: var(--space-3); background: var(--bg-card); }
.ld-vpc h4 { margin: 0 0 var(--space-2); font-size: var(--fs-card); color: var(--accent); }
.ld-vpc ul { margin: 0; padding-left: var(--space-4); font-size: var(--fs-card); color: var(--text-secondary); }
.ld-tgw { display: flex; align-items: center; justify-content: center; writing-mode: vertical-rl; letter-spacing: .12em; font-weight: var(--weight-bold); color: var(--accent); }
</style>
<div class="ld-arch fragment fade-up" data-fragment-index="1">
  <div class="ld-vpc"><h4>클라우드 VPC 10.0.0.0/16</h4><ul>
    <li>EKS 1.36, system 노드 2대</li>
    <li>gateway 노드 2대 (c6in.xlarge, 2개 AZ)</li>
    <li>Karpenter burst 노드 (m6i, m7i)</li>
    <li>클라우드 노드는 VPC CNI 사용</li></ul></div>
  <div class="ld-tgw">Transit Gateway</div>
  <div class="ld-vpc"><h4>시뮬레이션 온프렘 VPC 172.18.0.0/16</h4><ul>
    <li>hybrid 노드 호스트 2대 (m7i.xlarge)</li>
    <li>GPU 호스트 1대 (g6.xlarge, 데모 3 때만)</li>
    <li>Pod CIDR 172.17.0.0/16 (Cilium)</li>
    <li>SSH는 EC2 Instance Connect Endpoint만</li></ul></div>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="2">
  <div class="callout callout-danger"><strong class="text-danger">프로덕션 구성이 아님</strong><div class="on-surface-muted">EC2를 hybrid node로 쓰는 것은 지원되지 않고, join하면 hybrid node 요금이 부과됩니다.</div></div>
  <div class="callout callout-info"><strong class="text-info">실제 구성과의 차이</strong><div class="on-surface-muted">온프렘 서버 + VPN/Direct Connect로 바뀌고, 달라지는 값은 노드 CIDR과 호스트뿐입니다.</div></div>
</div>
:::


:::notes
{timing: 2min}
[요약]
• 두 번째 VPC를 TGW로 연결하고 그 안의 EC2를 온프렘 호스트로 사용
• 보안 기준 유지: 개방 ingress 없음, 공인 IP 없음, 로드 밸런서 없음
• 실제 구성에서는 호스트와 노드 CIDR만 바꾸면 같은 스크립트가 동작

온프렘 서버와 VPN이 없어서, 두 번째 VPC를 Transit Gateway로 연결하고 그 안의 EC2를 온프렘 호스트로 썼습니다.
이 구성은 지원되지 않고 hybrid node 요금이 부과된다는 점을 먼저 말씀드립니다. 데모의 목적은 동작 확인과 수치 확보입니다.
보안 기준은 지켰습니다. 보안 그룹에 인터넷 개방 ingress가 없고, 인스턴스에 공인 IP가 없고, 로드 밸런서를 만들지 않았습니다.
{cue: transition}
첫 번째 데모는 gateway의 리더 전환입니다.

[출처]
• https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-overview.html (EC2 실행은 미지원, hybrid fee 부과)
• 데모 저장소 RUNBOOK.md 환경 절 (private 저장소)
:::

---
<!-- Slide 3: 데모 1 녹화 영상: Gateway 리더 전환 -->
@type: content
@fit: off
@title: 데모 1 녹화 영상: Gateway 리더 전환

## 데모 1 녹화 영상: Gateway 리더 전환

:::html
<style>
.hn-video { width: 100%; max-height: 100%; aspect-ratio: 16 / 9; background: var(--bg-card); border-radius: var(--space-2); }
.hn-video-cap { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); }
.hn5-full { flex: 1; min-height: 0; display: flex; flex-direction: column; gap: var(--space-1); }
.hn5-vbox { flex: 1; min-height: 0; container-type: size; }
.hn5-full .hn-video { display: block; width: min(100cqw, calc(100cqh * 16 / 9)); height: auto; max-height: none; margin-inline: auto; }
.hn5-full .hn-video-cap { text-align: center; margin-top: 0; font-size: var(--fs-card); }
</style>
<div class="hn5-full">
<div class="hn5-vbox">
<video class="hn-video" src="../eks-hybrid-nodes-1h/media/v1-gateway-failover.mp4" poster="../eks-hybrid-nodes-1h/media/v1-gateway-failover.jpg" aria-label="데모 1 녹화 영상: Gateway 리더 전환, 실제 터미널 녹화 포함, 무음, 2분 58초" title="데모 1 녹화 영상: Gateway 리더 전환, 실제 터미널 녹화 포함, 무음, 2분 58초" controls preload="metadata" muted playsinline tabindex="-1"></video>
</div>
<div class="hn-video-cap">실측 결과 재구성 (2026-10 시뮬레이션 환경), 실제 터미널 녹화 포함, 무음</div>
</div>
:::

:::script
// While a video plays, Chromium's native controls keep focus and swallow arrow, PageDown and Space.
// Hand focus back to the page after any video interaction so the deck keys keep working.
document.querySelectorAll('video.hn-video').forEach(function (v) {
  var release = function () { setTimeout(function () { if (document.activeElement === v) v.blur(); }, 0); };
  ['focus', 'play', 'pause', 'seeked', 'volumechange', 'click', 'pointerup'].forEach(function (ev) { v.addEventListener(ev, release); });
});
// The deck updates location.hash on every slide change: pause any video left on a slide that is no longer active.
window.addEventListener('hashchange', function () {
  document.querySelectorAll('.slide:not(.active) video.hn-video').forEach(function (v) { if (!v.paused) v.pause(); });
});
:::

:::notes
{timing: 1min}
[요약]
• 영상 2분 58초. 라이브 시연을 했다면 건너뛰고, 시간이나 환경 문제로 라이브가 어려우면 이 영상을 재생합니다.
• 녹화 회차(2026-10-18): Lease 인계 5초, 1초 간격 요청 60개 중 2개 실패
• 일시정지 지점: 1:31 녹화의 결과 블록

리더 Gateway Pod를 지우고, standby가 Lease를 넘겨받아 VPC 라우트를 자기 ENI로 바꾸는 과정입니다. 터미널 장면은 0.5배속이고 출력 없는 대기는 줄였습니다.
{cue: pause}
1:31쯤 결과 블록에서 멈추고 인계 5초, 실패 2개, 라우트 ENI 교체를 읽어 주세요. 1:32 이후 격자에서 실패 칸의 위치는 실측 위치가 아니라 개수와 간격에 맞춘 배치입니다.
{cue: transition}
세 번 측정한 값을 정리하겠습니다.

[출처]
• 1시간 세션 V1 영상, eks-hybrid-nodes-1h/videos/rec/RECORDINGS.md R1
:::

---
<!-- Slide 4: 데모 1 리더 전환 -->
@type: content
@title: 데모 1: 리더가 바뀌어도 끊김은 3~5초

## 데모 1: 리더가 바뀌어도 끊김은 3~5초

:::html
<style>
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.flow-h { margin: 0 0 var(--space-4); }
.flow-h .flow-box { min-width: min-content; overflow-wrap: normal; }
.hn-flow-sub { display: block; color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: break-word; }
.ld-table { width: 100%; border-collapse: collapse; margin-bottom: var(--space-3); font-size: var(--fs-card); }
.ld-table th, .ld-table td { border: 1px solid var(--border); padding: var(--space-2) var(--space-3); text-align: left; }
.ld-table th { background: var(--bg-card); }
.ld-num { font-variant-numeric: tabular-nums; }
</style>
<div class="flow-h">
  <div class="flow-box fragment fade-right" data-fragment-index="1">리더 Pod 삭제<br><span class="hn-flow-sub">T0</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="2">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="2">standby가 Lease 획득<br><span class="hn-flow-sub">3~5초</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="3">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="3">VPC 라우트 교체<br><span class="hn-flow-sub">새 리더 ENI</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="4">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="4">VTEP 갱신, 트래픽 복구<br><span class="hn-flow-sub">1초 간격 요청 1~2개 실패</span></div>
</div>
<table class="ld-table fragment fade-up" data-fragment-index="5">
  <tr><th>실행</th><th>Lease 전환</th><th>실패한 요청 (1초 간격)</th><th>라우트</th></tr>
  <tr><td>1회차</td><td class="ld-num">3초</td><td class="ld-num">60개 중 1개</td><td>새 리더 ENI로 이동</td></tr>
  <tr><td>2회차</td><td class="ld-num">5초</td><td class="ld-num">60개 중 1개</td><td>새 리더 ENI로 이동</td></tr>
  <tr><td>3회차 (최소 권한 IAM)</td><td class="ld-num">5초</td><td class="ld-num">45개 중 2개</td><td>새 리더 ENI로 이동</td></tr>
</table>
<div class="callout callout-info fragment fade-up" data-fragment-index="6"><strong class="text-info">알아 둘 점</strong> Lease HOLDER는 Pod 이름이 아니라 노드이름_uuid 형식입니다. 라우트 쓰기 권한은 gateway의 route table로만 제한해도 동작했습니다.</div>
:::


:::notes
{timing: 2min}
[요약]
• 리더 Pod 삭제 후 Lease 전환 3초, 5초, 5초 (세 번 측정)
• 1초 간격 요청의 실패는 60개 중 1개, 45개 중 2개
• VPC 라우트가 새 리더 ENI로 이동, 최소 권한 IAM에서도 동일

리더 Pod를 지우고 1초 간격으로 요청을 보내 봤습니다. Lease는 3초에서 5초 사이에 넘어갔고, 실패한 요청은 많아야 두 개였습니다.
AWS가 안내하는 3~5초와 일치합니다. 다만 보장값은 아니고, 이 환경에서 세 번 측정한 값입니다.
{cue: pause}
Lease HOLDER 값이 Pod 이름이 아니라 노드 이름과 UUID라는 점은 시연할 때 헷갈리기 쉬워서 미리 말씀드립니다.
IAM은 문서 예시보다 좁혀서 라우트 쓰기 권한을 gateway의 route table로만 제한했고, 그래도 전환이 동작했습니다.
{cue: transition}
다음은 핵심 데모인 bursting입니다.

[출처]
• 데모 저장소 RUNBOOK.md 데모 1, demo1-gateway/failover.sh (세 번 실측)
• https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-gateway-overview.html (예상 전환 3~5초)
:::

---
<!-- Slide 5: 데모 2 설계 -->
@type: content
@title: 데모 2: 같은 워크로드를 세 가지로 줄여 본다

## 데모 2: 같은 워크로드를 세 가지로 줄여 본다

:::html
<style>
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.flow-h { margin: 0 0 var(--space-4); }
.flow-h .flow-box { min-width: min-content; overflow-wrap: normal; }
.hn-flow-sub { display: block; color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: break-word; }
</style>
<div class="flow-h">
  <div class="flow-box fragment fade-right" data-fragment-index="1">3개<br><span class="hn-flow-sub">모두 hybrid</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="2">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="2">15개<br><span class="hn-flow-sub">hybrid 8 + cloud 7</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="3">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="3">12개<br><span class="hn-flow-sub">warm-up</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="4">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="4">10개<br><span class="hn-flow-sub">배치 측정</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="5">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="5">3개<br><span class="hn-flow-sub">최종 배치와 정리 시간</span></div>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="6">
  <div class="callout callout-warning"><strong class="text-warning">A. 정책 없음</strong><div class="on-surface-muted">ReplicaSet 기본 규칙. Karpenter 기능도 끔.</div></div>
  <div class="callout callout-info"><strong class="text-info">B. Kyverno</strong><div class="on-surface-muted">hybrid 노드에 뜬 Pod에만 pod-deletion-cost 1을 부여.</div></div>
  <div class="callout callout-success"><strong class="text-success">C. Kyverno + Karpenter</strong><div class="on-surface-muted">B에 더해 Karpenter가 burst 노드 Pod의 cost를 순위로 기록.</div></div>
</div>
:::


:::notes
{timing: 1.5min}
[요약]
• hybrid 노드 2대에 Pod 8개가 들어가도록 Pod당 CPU 요청을 930m로 계산
• 3 → 15 → 12(warm-up) → 10 → 3 순서로 같은 흐름을 세 방식으로 반복
• 비교는 10개일 때 배치와 최종 3개, 빈 노드 정리 시간

같은 Deployment를 세 가지 방식으로 줄여서 어떤 Pod가 먼저 사라지는지 숫자로 비교합니다.
hybrid에는 선호 규칙만 걸고 selector나 toleration은 걸지 않았습니다. 그래서 hybrid가 꽉 차면 나머지는 Karpenter가 burst 노드를 만들어 받습니다.
Pod당 CPU 요청은 스크립트가 노드 allocatable을 읽어 계산해서 정확히 8개가 들어가게 했습니다. 12개로 줄이는 warm-up 단계가 왜 필요한지는 두 장 뒤에 설명합니다.
{cue: transition}
실행 장면부터 보겠습니다.

[출처]
• 데모 저장소 demo2-burst/run-compare.sh, calc-requests.sh
• https://karpenter.sh/preview/concepts/pod-deletion-cost/
:::

---
<!-- Slide 6: 데모 2 녹화 영상: 넘칠 때와 줄일 때 -->
@type: content
@fit: off
@title: 데모 2 녹화 영상: 넘칠 때와 줄일 때

## 데모 2 녹화 영상: 넘칠 때와 줄일 때

:::html
<style>
.hn-video { width: 100%; max-height: 100%; aspect-ratio: 16 / 9; background: var(--bg-card); border-radius: var(--space-2); }
.hn-video-cap { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); }
.hn5-full { flex: 1; min-height: 0; display: flex; flex-direction: column; gap: var(--space-1); }
.hn5-vbox { flex: 1; min-height: 0; container-type: size; }
.hn5-full .hn-video { display: block; width: min(100cqw, calc(100cqh * 16 / 9)); height: auto; max-height: none; margin-inline: auto; }
.hn5-full .hn-video-cap { text-align: center; margin-top: 0; font-size: var(--fs-card); }
</style>
<div class="hn5-full">
<div class="hn5-vbox">
<video class="hn-video" src="../eks-hybrid-nodes-1h/media/v2-bursting.mp4" poster="../eks-hybrid-nodes-1h/media/v2-bursting.jpg" aria-label="데모 2 녹화 영상: 버스팅과 축소, 실제 터미널 녹화 포함, 무음, 3분 36초" title="데모 2 녹화 영상: 버스팅과 축소, 실제 터미널 녹화 포함, 무음, 3분 36초" controls preload="metadata" muted playsinline tabindex="-1"></video>
</div>
<div class="hn-video-cap">실측 결과 재구성 (2026-10 시뮬레이션 환경), 실제 터미널 녹화 포함, 무음</div>
</div>
:::

:::notes
{timing: 1min}
[요약]
• 영상 3분 36초. 라이브 시연을 했다면 건너뜁니다.
• 앞부분은 2026-10-18 녹화 회차(시나리오 B, Pod 요청 910m), 뒷부분은 2026-10-15 A, B, C 비교 실행(930m)
• 일시정지 지점: 2:08 A, B, C 비교 장면

녹화 회차에서는 15개로 늘리자 35초에 모두 Ready(hybrid 8, burst 7)였고, 10개로 줄이면 hybrid 8, cloud 2, 3개로 줄이면 모두 hybrid였습니다. 두 실행이 섞여 나오니 장면마다 회차를 짚어 주세요.
{cue: pause}
2:08 비교 장면에서 멈추고, 정책이 없는 A만 hybrid Pod 2개가 먼저 빠졌다고 말씀하세요. 노드별 Pod 위치는 예시이고 Pod 수와 EC2 대수만 실측입니다.
{cue: transition}
비교 실행의 숫자를 표로 보겠습니다.

[출처]
• 1시간 세션 V2 영상, results/compare-20261015-1239.md, RECORDINGS.md R2
:::

---
<!-- Slide 7: 데모 2 결과 -->
@type: content
@title: 데모 2 결과: 온프렘 Pod를 지킨 것은 B와 C

## 데모 2 결과: 온프렘 Pod를 지킨 것은 B와 C

:::html
<style>
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.ld-chart { margin-bottom: var(--space-3); }
.ld-legend { display: flex; gap: var(--space-4); margin-bottom: var(--space-2); font-size: var(--fs-card); color: var(--text-secondary); }
.ld-sw { display: inline-block; width: var(--space-3); height: var(--space-3); border-radius: var(--space-1); margin-right: var(--space-2); vertical-align: middle; }
.ld-sw.hyb, .ld-seg.hyb { background: var(--success); }
.ld-sw.cld, .ld-seg.cld { background: var(--warning); }
.ld-row { display: grid; grid-template-columns: 1fr 2fr 2fr; gap: var(--space-3); align-items: center; margin-bottom: var(--space-2); }
.ld-label { font-size: var(--fs-card); }
.ld-bar { display: flex; height: var(--space-6); border-radius: var(--space-1); overflow: hidden; background: var(--bg-card); }
.ld-seg { display: flex; align-items: center; justify-content: center; color: var(--accent-on, var(--text-primary)); font-weight: var(--weight-bold); font-size: var(--fs-card); }
.ld-meta { font-size: var(--fs-card); color: var(--text-secondary); font-variant-numeric: tabular-nums; }
</style>
<div class="ld-chart fragment fade-up" data-fragment-index="1">
  <div class="ld-legend"><span><span class="ld-sw hyb"></span>hybrid Pod</span><span><span class="ld-sw cld"></span>cloud Pod</span><span>10개로 줄였을 때의 배치</span></div>
  <div class="ld-row"><div class="ld-label">A 정책 없음</div><div class="ld-bar"><div class="ld-seg hyb" style="width:60%">6</div><div class="ld-seg cld" style="width:40%">4</div></div><div class="ld-meta">최종 3개: hybrid 2 / cloud 1<br>EC2 3대, 정리 123초</div></div>
  <div class="ld-row"><div class="ld-label">B Kyverno</div><div class="ld-bar"><div class="ld-seg hyb" style="width:80%">8</div><div class="ld-seg cld" style="width:20%">2</div></div><div class="ld-meta">최종 3개: hybrid 3 / cloud 0<br>EC2 4대, 정리 118초</div></div>
  <div class="ld-row"><div class="ld-label">C Kyverno + Karpenter</div><div class="ld-bar"><div class="ld-seg hyb" style="width:80%">8</div><div class="ld-seg cld" style="width:20%">2</div></div><div class="ld-meta">최종 3개: hybrid 3 / cloud 0<br>EC2 3대, 정리 87초</div></div>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="2">
  <div class="callout callout-warning"><strong class="text-warning">A는 온프렘을 먼저 지움</strong><div class="on-surface-muted">기본 규칙은 위치를 보지 않아 hybrid Pod 2개가 먼저 사라졌습니다.</div></div>
  <div class="callout callout-success"><strong class="text-success">C의 이득은 작다</strong><div class="on-surface-muted">EC2 4대에서 3대, 정리 118초에서 87초. 시나리오당 1회 측정이라 반복 측정이 필요합니다.</div></div>
</div>
:::


:::notes
{timing: 3min}
[요약]
• A: 10개일 때 hybrid 6, cloud 4. 최종 3개는 hybrid 2, cloud 1
• B, C: 10개일 때 hybrid 8, cloud 2. 최종 3개는 모두 hybrid
• C는 B보다 EC2가 4대에서 3대, 빈 노드 정리가 118초에서 87초
• NodeClaim은 스케일 아웃 후 1~2초 안에 생성, 15개 Ready까지 약 37초

막대는 10개로 줄였을 때의 배치입니다. 초록이 온프렘, 주황이 클라우드 Pod입니다.
정책이 없으면 A처럼 온프렘 Pod가 먼저 지워집니다. ReplicaSet 기본 규칙이 Pod 위치를 보지 않기 때문입니다.
{cue: pause}
Kyverno만 써도 B처럼 온프렘 8개는 모두 지켜집니다. 대신 남은 클라우드 Pod 2개가 EC2 네 대에 흩어져 있었습니다.
Karpenter 기능을 켠 C는 burst 노드에 음수 값을 써서 EC2가 세 대로 줄고 정리도 87초로 빨랐습니다. 다만 한 번씩 잰 값이라 차이를 단정하지 마시고, 반복 측정 후에 수치를 인용하세요.
스케일 아웃은 빠릅니다. NodeClaim이 1~2초 안에 만들어지고 15개가 모두 Ready가 되기까지 약 37초가 걸렸습니다.
{cue: transition}
이 데모에서 만난 함정 세 가지를 정리하겠습니다.

[출처]
• 데모 저장소 results/compare-20261015-1239.md, RUNBOOK.md 데모 2 (2026-10-15 실측)
• https://karpenter.sh/preview/concepts/pod-deletion-cost/
:::

---
<!-- Slide 8: 데모 2 함정 -->
@type: content
@title: 데모가 알려 준 함정 세 가지

## 데모가 알려 준 함정 세 가지

:::html
<style>
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="callout callout-danger"><strong class="text-danger">1. 조용히 실패하는 Kyverno</strong><div class="on-surface-muted">background controller에 nodes get 권한이 없으면 에러 없이 annotation이 붙지 않아 B가 A와 똑같이 나왔습니다. Pod/binding은 기본 필터에서 빠져 있어 다시 켜야 합니다.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">2. Karpenter는 바로 순위를 매기지 않음</strong><div class="on-surface-muted">줄일 수 있는 노드에만 순위를 쓰고 갱신에 1~5분이 걸립니다. 꽉 찬 15개에서 바로 줄이면 C가 B와 같아져서 12개 warm-up이 필요했습니다.</div></div>
  <div class="callout callout-info"><strong class="text-info">3. Pod 요청은 init container까지</strong><div class="on-surface-muted">Pod의 유효 요청은 컨테이너 합과 가장 큰 init container 중 큰 값입니다. Cilium agent의 100m가 init에 있어 hybrid에 6개만 들어갔습니다.</div></div>
  <div class="callout callout-info"><strong class="text-info">그 밖에</strong><div class="on-surface-muted">ClusterPolicy는 deprecated, spec.failurePolicy는 거부되고, 기능을 끄면 Karpenter가 쓴 음수 값을 직접 지워야 합니다.</div></div>
</div>
:::


:::notes
{timing: 2min}
[요약]
• Kyverno: background controller의 nodes get 권한과 Pod/binding 필터 해제가 필요
• Karpenter: 순위는 줄일 수 있는 노드에만, 1~5분 지연. 그래서 warm-up
• 사이징: 유효 요청은 init container까지 계산

세 가지 모두 문서만 읽어서는 놓치기 쉬웠고, 실제로 돌려 보고서야 알았습니다.
첫째, Kyverno 정책이 에러 없이 적용되지 않았습니다. 정책은 Ready였고 Pod도 정상 생성됐는데 annotation만 없었습니다. 백그라운드 컨트롤러가 노드 라벨을 읽을 권한이 없었습니다.
{cue: pause}
둘째, Karpenter는 줄일 수 있는 노드에만 순위를 쓰고 갱신이 1~5분 걸립니다. 노드가 꽉 찬 상태에서 바로 줄이면 아직 순위가 없습니다.
셋째, Pod 크기 계산에서 init container의 요청을 빼먹으면 노드에 들어가는 개수가 달라집니다.
{cue: transition}
세 번째 데모는 GPU입니다.

[출처]
• 데모 저장소 KNOWN-ISSUES.md (Demo 2 findings)
• https://karpenter.sh/preview/concepts/pod-deletion-cost/
:::

---
<!-- Slide 9: 데모 3 녹화 영상: 온프렘 GPU 추론 -->
@type: content
@fit: off
@title: 데모 3 녹화 영상: 온프렘 GPU 추론

## 데모 3 녹화 영상: 온프렘 GPU 추론

:::html
<style>
.hn-video { width: 100%; max-height: 100%; aspect-ratio: 16 / 9; background: var(--bg-card); border-radius: var(--space-2); }
.hn-video-cap { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); }
.hn5-full { flex: 1; min-height: 0; display: flex; flex-direction: column; gap: var(--space-1); }
.hn5-vbox { flex: 1; min-height: 0; container-type: size; }
.hn5-full .hn-video { display: block; width: min(100cqw, calc(100cqh * 16 / 9)); height: auto; max-height: none; margin-inline: auto; }
.hn5-full .hn-video-cap { text-align: center; margin-top: 0; font-size: var(--fs-card); }
</style>
<div class="hn5-full">
<div class="hn5-vbox">
<video class="hn-video" src="../eks-hybrid-nodes-1h/media/v4-gpu.mp4" poster="../eks-hybrid-nodes-1h/media/v4-gpu.jpg" aria-label="데모 3 녹화 영상: hybrid GPU 추론, 실제 터미널 녹화 포함, 무음, 2분 14초" title="데모 3 녹화 영상: hybrid GPU 추론, 실제 터미널 녹화 포함, 무음, 2분 14초" controls preload="metadata" muted playsinline tabindex="-1"></video>
</div>
<div class="hn-video-cap">실측 결과 재구성 (2026-10 시뮬레이션 환경), 실제 터미널 녹화 포함, 무음</div>
</div>
:::

:::notes
{timing: 1min}
[요약]
• 영상 2분 14초. 2026-10-18에 GPU 호스트를 다시 조인해 녹화하고 바로 제거한 회차입니다. 라이브 시연을 했다면 건너뜁니다.
• g6.xlarge(NVIDIA L4)를 hybrid 노드로 붙이고, 클라우드 Job이 Service 이름으로 vLLM을 호출. 응답은 녹화 회차 1초 미만
• 일시정지 지점: 1:34 verify.sh 결과

영상 제목의 "데모 4"는 1시간 세션의 순서입니다. 녹화 첫 줄의 Demo 3은 데모 저장소 폴더 이름(demo3-gpu)이고, 이 덱에서도 데모 3입니다.
{cue: pause}
1:34쯤 verify.sh의 OK 네 줄에서 멈추고 읽어 주세요. elapsed_seconds=0은 1초 미만이라는 뜻입니다. 이미지 다운로드는 녹화 회차 4분 35초였습니다.
{cue: transition}
10월 15일 실행 결과와 함께 정리하겠습니다.

[출처]
• 1시간 세션 V4 영상, RECORDINGS.md R4, 데모 저장소 RUNBOOK.md 3절
:::

---
<!-- Slide 10: 데모 3 GPU -->
@type: content
@title: 데모 3: hybrid GPU에서 추론, 클라우드에서 호출

## 데모 3: hybrid GPU에서 추론, 클라우드에서 호출

:::html
<style>
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.flow-h { margin: 0 0 var(--space-4); }
.flow-h .flow-box { min-width: min-content; overflow-wrap: normal; }
.hn-flow-sub { display: block; color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: break-word; }
</style>
<div class="flow-h">
  <div class="flow-box fragment fade-right" data-fragment-index="1">클라우드 Job<br><span class="hn-flow-sub">system 노드</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="2">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="2">gateway 경로<br><span class="hn-flow-sub">VXLAN, VPC 라우트</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="3">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="3">vLLM Pod<br><span class="hn-flow-sub">hybrid GPU 노드, L4 23GB</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="4">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="4">응답 약 1초<br><span class="hn-flow-sub">모델 로드 후</span></div>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="5">
  <div class="callout callout-success"><strong class="text-success">확인한 것</strong><div class="on-surface-muted">allocatable nvidia.com/gpu = 1, istio-proxy 없음, hostNetwork 끔, GPU taint와 toleration 동작.</div></div>
  <div class="callout callout-info"><strong class="text-info">설정</strong><div class="on-surface-muted">taint nvidia.com/gpu=Exists:NoSchedule, label node-role/gpu, device plugin v0.17.1, vLLM v0.19.1, Qwen2.5-0.5B.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">첫 시작은 느림</strong><div class="on-surface-muted">vLLM 이미지(약 10GB) pull이 4분 28초. 발표 전에 미리 받아 두세요. GPU 1개라 Deployment는 Recreate.</div></div>
</div>
:::


:::notes
{timing: 2min}
[요약]
• g6.xlarge(NVIDIA L4)를 hybrid 노드로 붙여 한 번 검증하고 삭제
• GPU taint, device plugin, 사이드카 없는 추론 Pod, 클라우드 호출까지 확인
• 첫 시작은 이미지 pull과 모델 다운로드로 느려서 미리 준비

GPU 서버가 없어서 시뮬레이션 VPC에 GPU 인스턴스를 hybrid 노드로 붙였고, 검증한 뒤 바로 삭제했습니다.
GPU 노드에는 taint를 걸어서 CoreDNS 같은 일반 Pod가 올라오지 않게 했고, device plugin은 hybrid GPU 노드에만 배포했습니다.
추론 Pod에는 사이드카가 없고 hostNetwork도 쓰지 않았습니다. 클라우드 노드의 Job이 서비스를 호출해서 약 1초에 응답을 받았습니다.
실제 GPU 서버에서는 드라이버와 container toolkit이 이미지에 들어 있다고 가정하는 부분을, 이번에는 스크립트로 설치했습니다.
{cue: transition}
마지막으로 Istio와 gateway를 같이 쓸 수 있는지 확인한 결과입니다.

[출처]
• 데모 저장소 RUNBOOK.md 데모 3, demo3-gpu/verify.sh (2026-10-15 실측)
• https://aws.amazon.com/blogs/containers/run-genai-inference-across-environments-with-amazon-eks-hybrid-nodes/
:::

---
<!-- Slide 11: Istio 공존 -->
@type: content
@title: Istio와 gateway는 함께 쓸 수 있다

## Istio와 gateway는 함께 쓸 수 있다

:::html
<style>
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.ld-table { width: 100%; border-collapse: collapse; margin-bottom: var(--space-3); font-size: var(--fs-card); }
.ld-table th, .ld-table td { border: 1px solid var(--border); padding: var(--space-2) var(--space-3); text-align: left; vertical-align: top; }
.ld-table th { background: var(--bg-card); }
.ld-ok { color: var(--success); font-weight: var(--weight-bold); }
</style>
<table class="ld-table fragment fade-up" data-fragment-index="1">
  <tr><th>검증 항목 (Istio 1.30.6, sidecar 모드)</th><th>결과</th></tr>
  <tr><td>hybrid 노드 Pod에도 sidecar 주입</td><td><span class="ld-ok">통과</span> 4개 Pod 모두 2/2</td></tr>
  <tr><td>클라우드와 hybrid 사이 양방향 호출</td><td><span class="ld-ok">통과</span> 둘 다 200</td></tr>
  <tr><td>STRICT mTLS</td><td><span class="ld-ok">통과</span> 일반 Pod의 평문 호출은 거부, 메시 호출은 mutual_tls</td></tr>
  <tr><td>Istio L7 정책 (/admin 거부)</td><td><span class="ld-ok">통과</span> /echo 200, /admin/users 403</td></tr>
  <tr><td>이때 Cilium 설정</td><td>enable-l7-proxy=false, enable-vtep=true 그대로</td></tr>
</table>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="2">
  <div class="callout callout-success"><strong class="text-success">막히는 것은 Istio가 아니다</strong><div class="on-surface-muted">gateway의 l7Proxy=false로 막히는 것은 Cilium Ingress, Gateway API, L7 정책입니다. Istio의 L7은 sidecar Envoy가 처리해 영향이 없었습니다.</div></div>
  <div class="callout callout-info"><strong class="text-info">참고</strong><div class="on-surface-muted">최신 Istio는 sidecar를 native sidecar(init container, restartPolicy Always)로 주입합니다.</div></div>
</div>
:::


:::notes
{timing: 2.5min}
[요약]
• 같은 클러스터에서 Istio 1.30.6 sidecar와 Hybrid Nodes gateway를 함께 검증
• sidecar 주입, 양방향 호출, STRICT mTLS, Istio L7 정책이 모두 동작
• Cilium은 l7Proxy=false와 VTEP 켬을 유지한 채로 통과

이전에는 gateway가 l7Proxy를 꺼야 해서 Istio도 못 쓰는 것처럼 말씀드렸는데, 실제로 돌려 보니 그렇지 않았습니다.
막히는 것은 Cilium 자체의 L7 기능입니다. Cilium Ingress, Gateway API, L7 정책이 그렇습니다. Istio의 L7은 sidecar Envoy가 처리하기 때문에 Cilium의 l7Proxy와 무관하게 동작했습니다.
{cue: pause}
hybrid 노드의 Pod에도 sidecar가 주입됐고, STRICT mTLS가 켜진 상태에서 메시 안의 호출은 성공하고 메시 밖 Pod의 평문 호출은 거부됐습니다.
hybrid 쪽 서버에 걸어 둔 AuthorizationPolicy가 /admin 경로를 403으로 막았고, 그동안 Cilium 설정은 l7Proxy false, VTEP true 그대로였습니다.
한 가지 주의할 점은 이 결과가 sidecar 모드 기준이라는 점입니다. ambient 모드는 별도로 확인하지 않았습니다.
{cue: transition}
성능과 gateway 전환 중 동작도 재 봤습니다.

[출처]
• 데모 저장소 demo-istio/run-tests.sh, results/istio-20261017-2311.json (2026-10-17 실측)
• https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-gateway-cni.html (l7Proxy=false 필수)
:::

---
<!-- Slide 12: Istio 실측 -->
@type: content
@title: Istio 실측: 경로별 지연과 gateway 전환

## Istio 실측: 경로별 지연과 gateway 전환

:::html
<style>
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.ld-legend { display: flex; gap: var(--space-4); margin-bottom: var(--space-2); font-size: var(--fs-card); color: var(--text-secondary); }
.ld-sw { display: inline-block; width: var(--space-3); height: var(--space-3); border-radius: var(--space-1); margin-right: var(--space-2); vertical-align: middle; }
.ld-sw.p50, .ld-b.p50 { background: var(--accent); }
.ld-sw.p99, .ld-b.p99 { background: var(--warning); }
.ld-lrow { display: grid; grid-template-columns: 1fr 3fr 1fr; gap: var(--space-3); align-items: center; margin-bottom: var(--space-2); }
.ld-lab { font-size: var(--fs-card); }
.ld-stack { display: flex; flex-direction: column; gap: var(--space-1); }
.ld-b { height: var(--space-3); border-radius: var(--space-1); }
.ld-val { font-size: var(--fs-card); color: var(--text-secondary); font-variant-numeric: tabular-nums; }
</style>
<div class="fragment fade-up" data-fragment-index="1">
  <div class="ld-legend"><span><span class="ld-sw p50"></span>p50</span><span><span class="ld-sw p99"></span>p99</span><span>값은 p50 / p99, sidecar에서 sidecar까지, 순차 300회 요청</span></div>
  <div class="ld-lrow"><div class="ld-lab">cloud → cloud</div><div class="ld-stack"><div class="ld-b p50" style="width:37.7%"></div><div class="ld-b p99" style="width:56.9%"></div></div><div class="ld-val">1.32 / 1.99 ms</div></div>
  <div class="ld-lrow"><div class="ld-lab">cloud → hybrid</div><div class="ld-stack"><div class="ld-b p50" style="width:70.3%"></div><div class="ld-b p99" style="width:85.7%"></div></div><div class="ld-val">2.46 / 3.00 ms</div></div>
  <div class="ld-lrow"><div class="ld-lab">hybrid → hybrid</div><div class="ld-stack"><div class="ld-b p50" style="width:17.7%"></div><div class="ld-b p99" style="width:28.6%"></div></div><div class="ld-val">0.62 / 1.00 ms</div></div>
  <div class="ld-lrow"><div class="ld-lab">hybrid → cloud</div><div class="ld-stack"><div class="ld-b p50" style="width:60.3%"></div><div class="ld-b p99" style="width:83.4%"></div></div><div class="ld-val">2.11 / 2.92 ms</div></div>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="2">
  <div class="callout callout-success"><strong class="text-success">gateway 전환 중에도 실패 0건</strong><div class="on-surface-muted">초당 40건을 45초간 보내는 동안 리더 Pod를 삭제했고(전환 5초) 1,800건이 모두 200이었습니다.</div></div>
  <div class="callout callout-info"><strong class="text-info">읽는 법</strong><div class="on-surface-muted">gateway를 거치는 경로가 같은 쪽 경로보다 약 1ms 느립니다. 요청 재시도는 sidecar의 기본 동작입니다.</div></div>
</div>
:::


:::notes
{timing: 2min}
[요약]
• 같은 쪽 호출이 p50 0.62~1.32ms, gateway를 거치면 p50 2.11~2.46ms
• 리더 전환 중 초당 40건 45초 동안 1,800건 모두 성공
• 지연은 순차 300회 요청의 값이고 로드 테스트가 아님

네 경로의 지연입니다. 같은 쪽 호출은 p50이 1ms 안팎이고, gateway를 거쳐 건너가면 p50이 2ms대입니다. 약 1ms의 추가 hop이 보입니다.
gateway 리더를 지우는 동안 초당 40건을 계속 보냈는데 1,800건이 모두 성공했습니다. 전환이 5초 걸렸는데도 실패가 없었던 것은 sidecar의 기본 재시도 덕분일 가능성이 큽니다.
{cue: pause}
이 값은 순차 요청의 지연이고 처리량 테스트가 아닙니다. 활성 gateway 한 대가 처리량의 한계라는 점은 그대로입니다.
{cue: transition}
다음은 ALB로 hybrid Pod를 직접 타깃으로 붙였을 때입니다.

[출처]
• 데모 저장소 results/istio-20261017-2311.json, demo-istio/run-tests.sh (2026-10-17 실측)
:::

---
<!-- Slide 13: ALB 데모 녹화 영상: ip 타깃과 역방향 -->
@type: content
@fit: off
@title: ALB 데모 녹화 영상: ip 타깃과 역방향

## ALB 데모 녹화 영상: ip 타깃과 역방향

:::html
<style>
.hn-video { width: 100%; max-height: 100%; aspect-ratio: 16 / 9; background: var(--bg-card); border-radius: var(--space-2); }
.hn-video-cap { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); }
.hn5-full { flex: 1; min-height: 0; display: flex; flex-direction: column; gap: var(--space-1); }
.hn5-vbox { flex: 1; min-height: 0; container-type: size; }
.hn5-full .hn-video { display: block; width: min(100cqw, calc(100cqh * 16 / 9)); height: auto; max-height: none; margin-inline: auto; }
.hn5-full .hn-video-cap { text-align: center; margin-top: 0; font-size: var(--fs-card); }
</style>
<div class="hn5-full">
<div class="hn5-vbox">
<video class="hn-video" src="../eks-hybrid-nodes-1h/media/v3-alb-reverse.mp4" poster="../eks-hybrid-nodes-1h/media/v3-alb-reverse.jpg" aria-label="ALB 데모 녹화 영상: ALB ip 타깃과 온프렘에서 들어오는 역방향, 실제 터미널 녹화 포함, 무음, 3분 12초" title="ALB 데모 녹화 영상: ALB ip 타깃과 온프렘에서 들어오는 역방향, 실제 터미널 녹화 포함, 무음, 3분 12초" controls preload="metadata" muted playsinline tabindex="-1"></video>
</div>
<div class="hn-video-cap">실측 결과 재구성 (2026-10 시뮬레이션 환경), 실제 터미널 녹화 포함, 무음</div>
</div>
:::

:::notes
{timing: 1min}
[요약]
• 영상 3분 12초. 라이브 시연을 했다면 건너뜁니다.
• 녹화 회차(2026-10-18 06:36 UTC 시작): 재시작 50초 뒤 새 IP만 healthy, 부하 174건 ERR 0, 온프렘 NodePort는 FAIL
• 02:11 UTC 측정 회차: Gateway 리더 인계 4초, 191건 중 1건 실패
• 일시정지 지점: 1:20 폴링 격자

정방향은 hybrid Pod를 다시 띄워 IP가 바뀌어도 LBC가 타깃을 따라가는 장면, 역방향은 온프렘 호스트에서 internal ALB로 들어오는 세 경로입니다. 화면의 "녹화 회차"와 "02:11 측정" 표시로 회차를 구분해 주세요. 영상 제목의 "데모 3"은 1시간 세션의 순서이고, 이 덱에서는 데모 3이 GPU입니다.
{cue: pause}
1:20 격자에서 멈추고, 타깃 등록과 해제가 사람 손 없이 일어났고 부하 오류가 0건이었다고 말씀하세요. 2:35 녹화에서 NodePort 세 번이 모두 FAIL인 이유는 뒤 슬라이드에서 설명합니다.
{cue: transition}
측정 회차의 결과를 정리하겠습니다.

[출처]
• 1시간 세션 V3 영상, results/lb-20261018-0211.json, RECORDINGS.md R3
:::

---
<!-- Slide 14: ALB ip 타깃 -->
@type: content
@title: ALB ip 타깃: hybrid Pod IP가 바뀌어도 LBC가 따라간다

## ALB ip 타깃: hybrid Pod IP가 바뀌어도 LBC가 따라간다

:::html
<style>
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.flow-h { margin: 0 0 var(--space-4); }
.flow-h .flow-box { min-width: min-content; overflow-wrap: normal; }
.hn-flow-sub { display: block; color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: break-word; }
.ld-table { width: 100%; border-collapse: collapse; margin-bottom: var(--space-3); font-size: var(--fs-card); }
.ld-table th, .ld-table td { border: 1px solid var(--border); padding: var(--space-2) var(--space-3); text-align: left; }
.ld-table th { background: var(--bg-card); }
.ld-num { font-variant-numeric: tabular-nums; }
</style>
<div class="flow-h">
  <div class="flow-box fragment fade-right" data-fragment-index="1">리전 클라이언트<br><span class="hn-flow-sub">10.0.x</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="2">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="2">internal ALB<br><span class="hn-flow-sub">ip 타깃 172.17.x, AZ all</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="3">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="3">VPC 라우트 172.17.0.0/16<br><span class="hn-flow-sub">gateway 리더 ENI</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="4">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="4">VXLAN → hybrid Pod<br><span class="hn-flow-sub">온프렘 노드</span></div>
</div>
<table class="ld-table fragment fade-up" data-fragment-index="5">
  <tr><th>테스트</th><th>무엇을 했나</th><th>결과</th></tr>
  <tr><td>등록</td><td>Ingress target-type ip, hybrid Pod 2개</td><td>172.17.0.202, .48이 healthy, AZ <code>all</code></td></tr>
  <tr><td>호출</td><td>리전 Pod에서 ALB로 20회</td><td class="ld-num">20/20</td></tr>
  <tr><td>Pod 교체</td><td>부하 중 rollout restart</td><td class="ld-num">새 IP .230, .76로 54초에 수렴, 276건 중 실패 0</td></tr>
  <tr><td>gateway 전환</td><td>부하 중 리더 Pod 삭제</td><td class="ld-num">인계 4초, 191건 중 실패 1 (재시도 없음)</td></tr>
</table>
<div class="callout callout-info fragment fade-up" data-fragment-index="6"><strong class="text-info">역할 분담</strong> 타깃 등록과 해제는 AWS Load Balancer Controller가 하고, gateway는 VPC 밖 Pod IP까지 가는 경로만 줍니다. 그래서 Pod IP가 라우팅 가능해야 합니다.</div>
:::


:::notes
{timing: 2.5min}
[요약]
• hybrid Pod IP를 ALB ip 타깃으로 등록, VPC 밖 IP라 AZ all
• rollout restart 중 LBC가 새 Pod IP로 교체, 54초에 수렴, 실패 0
• gateway 리더 전환 중 191건 중 1건 실패

자주 받는 질문이 "온프렘 Pod IP는 계속 바뀌는데 ALB 타깃은 누가 바꿔 주나"입니다. 답은 AWS Load Balancer Controller입니다. Endpoints를 보고 타깃을 등록하고 해제합니다. gateway가 하는 일은 VPC 밖에 있는 Pod IP까지 가는 경로를 주는 것뿐입니다.
실제로 internal ALB에 hybrid Pod 두 개를 붙였고, VPC 밖 IP라서 가용 영역이 all로 등록됐습니다. 헬스 체크도 gateway 경로로 통과했습니다.
{cue: pause}
부하를 거는 중에 rollout restart를 했더니, 새 Pod IP로 54초 만에 타깃이 바뀌었고 276건 중 실패는 없었습니다. preStop과 짧은 deregistration delay를 함께 준 결과입니다.
gateway 리더를 지웠을 때는 인계 4초 동안 191건 중 1건이 실패했습니다. 이 클라이언트는 재시도를 하지 않아서, Istio 측정보다 실제 공백에 가깝습니다.
{cue: transition}
그럼 반대 방향, 온프렘에서 LB로 들어오는 경우는 어떨까요.

[출처]
• 데모 저장소 results/lb-20261018-0211.json, demo-lb/run-tests.sh (2026-10-18 실측)
• https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-ingress.html
:::

---
<!-- Slide 15: 역방향 -->
@type: content
@title: 반대 방향: 온프렘에서 LB로 들어오면

## 반대 방향: 온프렘에서 LB로 들어오면

:::html
<style>
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.hn-path { font-size: var(--fs-card); color: var(--text-primary); margin-top: var(--space-2); word-break: keep-all; }
</style>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="callout callout-success"><strong class="text-success">① internal ALB → 리전 Pod: 20/20</strong><div class="hn-path">온프렘 → DX/VPN(데모는 TGW) → ALB private IP → VPC CNI Pod</div><div class="on-surface-muted">gateway를 거치지 않습니다. 온프렘 DNS가 ALB 이름을 private IP로 풀어야 하므로 Route 53 Resolver inbound endpoint가 필요합니다.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">② internal ALB → hybrid Pod: 20/20, 그러나 hairpin</strong><div class="hn-path">온프렘 → ALB → gateway → 다시 온프렘</div><div class="on-surface-muted">동작은 하지만 DX를 두 번 지나 지연과 전송 비용이 늘어납니다. 온프렘 Pod는 온프렘 LB로 받는 편이 낫습니다.</div></div>
  <div class="callout callout-danger"><strong class="text-danger">③ hybrid NodePort → 리전 Pod: 실패</strong><div class="hn-path">온프렘 → hybrid 노드 :30080 → 노드 IP로 SNAT → underlay → 리전 Pod</div><div class="on-surface-muted">Pod 출발 트래픽이 아니라 gateway를 타지 않습니다. 리전 노드 SG가 온프렘 노드 CIDR에서 오는 앱 포트를 허용해야 합니다(데모 SG는 443만 허용).</div></div>
</div>
<div class="callout callout-info fragment fade-up" data-fragment-index="2"><strong class="text-info">AWS 권장</strong> 리전에서 오는 트래픽은 ALB, 온프렘에서 오는 트래픽은 온프렘 쪽 Ingress나 LB로 받습니다. gateway를 쓰면 Cilium L7(Ingress, Gateway API)은 꺼지므로 온프렘은 L4 LoadBalancer나 기존 LB를 씁니다.</div>
:::


:::notes
{timing: 2.5min}
[요약]
• 온프렘 → internal ALB → 리전 Pod는 일반 VPC 경로, gateway 불필요 (20/20)
• 같은 ALB로 hybrid Pod를 부르면 hairpin, 동작은 하지만 비효율 (20/20)
• hybrid NodePort로 받아 리전 Pod로 보내면 underlay를 타서 SG가 필요 (실패)

온프렘 호스트에서 같은 internal ALB를 호출했습니다. ALB 이름은 private IP 두 개로 풀렸고, TGW를 지나 ALB에 닿은 뒤 리전 Pod로 갔습니다. 여기는 gateway가 전혀 관여하지 않는 일반 VPC 경로입니다. 실제 온프렘에서는 ALB 이름을 private IP로 풀 수 있게 Route 53 Resolver inbound endpoint를 두셔야 합니다.
같은 ALB로 hybrid Pod 경로를 부르면 온프렘에서 AWS로 갔다가 gateway를 지나 다시 온프렘으로 돌아옵니다. 동작은 했지만 DX를 두 번 지나니 온프렘 Pod는 온프렘 LB로 받는 게 낫습니다.
{cue: pause}
AWS 문서도 같은 기준을 줍니다. 리전에서 오는 트래픽은 ALB와 Load Balancer Controller, 온프렘에서 오는 트래픽은 온프렘 쪽 Ingress로 받으라고 권장합니다. 다만 gateway를 켜면 Cilium의 L7 proxy를 꺼야 해서 Cilium Ingress와 Gateway API는 같이 쓸 수 없고, 온프렘은 L4 LoadBalancer Service나 기존 하드웨어 LB를 쓰게 됩니다.
세 번째는 일부러 보여 드리는 실패입니다. hybrid 노드의 NodePort로 받아서 리전 Pod로 보내면, kube-proxy가 노드 IP로 SNAT하고 커널 라우팅으로 underlay를 탑니다. Pod에서 출발한 트래픽이 아니라서 gateway를 쓰지 않습니다. 데모 클러스터의 SG가 온프렘 노드 대역에 443만 열어 둬서 막혔습니다. 이 경로를 쓰려면 리전 노드 SG에 온프렘 노드 CIDR과 앱 포트를 열어야 합니다.
{cue: transition}
마지막으로 전체를 정리하겠습니다.

[출처]
• 데모 저장소 results/lb-20261018-0211.json, KNOWN-ISSUES.md LB 데모 확인 사항 (2026-10-18 실측)
• https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-ingress.html (트래픽 출발지별 ALB와 Cilium Ingress 권장)
• https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-networking.html
:::

---
<!-- Slide 16: 데모 5 녹화 영상: 연결 검증 -->
@type: content
@fit: off
@title: 데모 5 녹화 영상: SNAT 없는 연결과 PrivateLink

## 데모 5 녹화 영상: SNAT 없는 연결과 PrivateLink

:::html
<style>
.hn-video { width: 100%; max-height: 100%; aspect-ratio: 16 / 9; background: var(--bg-card); border-radius: var(--space-2); }
.hn-video-cap { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); }
.hn5-full { flex: 1; min-height: 0; display: flex; flex-direction: column; gap: var(--space-1); }
.hn5-vbox { flex: 1; min-height: 0; container-type: size; }
.hn5-full .hn-video { display: block; width: min(100cqw, calc(100cqh * 16 / 9)); height: auto; max-height: none; margin-inline: auto; }
.hn5-full .hn-video-cap { text-align: center; margin-top: 0; font-size: var(--fs-card); }
</style>
<div class="hn5-full">
<div class="hn5-vbox">
<video class="hn-video" src="../eks-hybrid-nodes-1h/media/v5-connectivity.mp4" poster="../eks-hybrid-nodes-1h/media/v5-connectivity.jpg" aria-label="데모 5 녹화 영상: native routing에서 SNAT 없는 연결과 PrivateLink, 실제 터미널 녹화 포함, 무음, 2분 32초" title="데모 5 녹화 영상: native routing에서 SNAT 없는 연결과 PrivateLink, 실제 터미널 녹화 포함, 무음, 2분 32초" controls preload="metadata" muted playsinline tabindex="-1"></video>
</div>
<div class="hn-video-cap">실측 결과 재구성 (2026-10 시뮬레이션 환경), 실제 터미널 녹화 포함, 무음</div>
</div>
:::

:::notes
{timing: 1min}
[요약]
• 영상 2분 32초. 라이브 시연을 했다면 건너뜁니다.
• 녹화 회차(2026-10-19 13:18 UTC 시작): 서버 로그의 출발지가 상대 Pod IP, endpoint SG는 Pod IP만 통과
• 10:50 UTC 측정 회차: 연결 매트릭스 38개 모두 PASS
• 이 데모는 gateway를 걷어 낸 native routing 모드에서 돌렸습니다(AWS 지원 범위 밖)

앞의 데모들은 VXLAN과 gateway 위에서 돌렸고, 이 데모는 같은 클러스터를 native routing으로 바꾼 뒤 돌렸습니다. 요구사항은 하나였습니다. 방화벽이 온프렘 Pod를 Pod IP로 구분할 수 있어야 한다는 것입니다.
{cue: pause}
화면에서 "server saw" 줄을 짚어 주세요. 온프렘 Pod가 클라우드 Pod를 부르면 서버는 172.17 Pod IP를 보고, 반대 방향은 10.0 Pod IP를 봅니다. 마지막 장면에서 같은 노드인데 Pod IP는 302를 받고 노드 IP는 타임아웃이 나는 부분이 SNAT이 없다는 가장 확실한 증거입니다.
{cue: transition}
측정 회차의 전체 결과를 보겠습니다.

[출처]
• 1시간 세션 V5 영상, eks-hybrid-nodes-1h/videos/rec/RECORDINGS.md R5
:::

---
<!-- Slide 17: 연결 매트릭스 -->
@type: content
@title: native routing: 서버가 보는 출발지는 Pod IP

## native routing: 서버가 보는 출발지는 Pod IP

:::html
<style>
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.ld-table { width: 100%; border-collapse: collapse; margin-bottom: var(--space-3); font-size: var(--fs-card); }
.ld-table th, .ld-table td { border: 1px solid var(--border); padding: var(--space-1) var(--space-3); text-align: left; }
.ld-table th { background: var(--bg-card); }
.ld-num { font-variant-numeric: tabular-nums; white-space: nowrap; }
.ld-cols { display: grid; grid-template-columns: 3fr 2fr; gap: var(--space-4); align-items: start; }
</style>
<div class="ld-cols">
<table class="ld-table fragment fade-up" data-fragment-index="1">
  <tr><th>구간</th><th>확인한 것</th><th>결과</th></tr>
  <tr><td>Pod 간 직접</td><td>같은 hybrid 노드, hybrid 노드 사이, hybrid와 클라우드 양방향, 클라우드 기준선</td><td class="ld-num text-success">7/7</td></tr>
  <tr><td>ClusterIP</td><td>Service는 목적지만 바꾸고 출발지 Pod IP 유지</td><td class="ld-num text-success">3/3</td></tr>
  <tr><td>DNS, API</td><td>CoreDNS(클라우드), hostNetwork 포함, <code>/livez</code>, SA 토큰</td><td class="ld-num text-success">6/6</td></tr>
  <tr><td>control plane</td><td>webhook 경로, exec와 logs, metrics-server</td><td class="ld-num text-success">3/3</td></tr>
  <tr><td>온프렘 서버</td><td>쿠버네티스 밖 socat 서버가 본 주소: Pod IP</td><td class="ld-num text-success">2/2</td></tr>
  <tr><td>인터넷</td><td>모든 Pod가 클라우드 NAT 하나로 나감</td><td class="ld-num text-success">3/3</td></tr>
  <tr><td>정책, MTU, ALB</td><td><code>fromCIDR</code> 정책, 32 MiB 양방향, ip 타깃 healthy</td><td class="ld-num text-success">6/6</td></tr>
  <tr><td>PrivateLink</td><td>STS, S3 interface endpoint, IRSA, SG, 버킷 정책</td><td class="ld-num text-success">8/8</td></tr>
</table>
<div>
  <div class="callout callout-info fragment fade-up" data-fragment-index="2"><strong class="text-info">구성</strong><div class="on-surface-muted">Cilium <code>routingMode: native</code>, masquerade 끔. 온프렘 라우터(데모는 route table)가 노드별 Pod 블록을 노드로 보냅니다. VPC CNI도 172.17, 172.18 대역은 SNAT하지 않습니다.</div></div>
  <div class="callout callout-warning fragment fade-up" data-fragment-index="3"><strong class="text-warning">처음 돌렸을 때 실패한 것</strong><div class="on-surface-muted">hostNetwork Pod의 DNS(클러스터 SG에 노드 대역 53 없음), 클라우드 Pod가 온프렘 서버로 갈 때 SNAT(VPC CNI 제외 대역 누락), 익명 <code>/version</code> 401(1.36은 health endpoint만 허용).</div></div>
  <div class="callout callout-warning fragment fade-up" data-fragment-index="4"><strong class="text-warning">AWS 지원 범위 밖</strong><div class="on-surface-muted">지원 Networking Mode는 VXLAN뿐이고 gateway도 VXLAN이 필요합니다. 지원 범위 안의 대안은 VXLAN 유지, masquerade 끔, Cilium BGP로 Pod CIDR 광고입니다(개념, 이번에 측정하지 않음).</div></div>
</div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
• 10:50 UTC 측정: 38개 모두 PASS, Pod에서 출발한 요청은 서버 로그의 출발지가 상대 Pod IP
• 첫 실행의 실패 세 가지는 SG 53, VPC CNI SNAT 제외 대역, /livez로 해결
• native routing은 AWS 지원 범위 밖, 지원 경로는 VXLAN + masquerade 끔 + BGP

연결 매트릭스를 스크립트 하나로 돌렸습니다. Pod 간 통신, Service, DNS, API 서버, control plane에서 들어오는 경로, 쿠버네티스 밖의 온프렘 서버, 인터넷, 정책, 대용량 전송, ALB, PrivateLink까지 38개입니다. Pod에서 출발한 요청은 서버가 기록한 출발지를 확인했고, 모두 상대 Pod IP였습니다. control plane에서 오는 요청은 EKS 관리 ENI가, 인터넷은 NAT 주소가 출발지입니다.
{cue: pause}
처음 돌렸을 때는 세 개가 실패했습니다. hostNetwork Pod는 노드 IP로 CoreDNS를 부르는데 클러스터 SG에 노드 대역 53번이 없었습니다. 클라우드 Pod가 온프렘 서버로 갈 때는 VPC CNI가 노드 IP로 SNAT했는데, 제외 대역에 온프렘 노드 대역이 빠져 있었습니다. 그리고 1.36에서는 익명 요청이 health endpoint만 허용돼 /version이 401이었습니다.
꼭 말씀드릴 점이 있습니다. AWS 문서가 지원하는 Cilium 네트워킹 모드는 VXLAN뿐입니다. 지원 범위 안의 대안은 VXLAN을 유지한 채 masquerade를 끄고 BGP로 Pod CIDR을 광고하는 구성입니다. 이론상 클라우드와 온프렘 사이에서는 Pod IP가 보이고 hybrid 노드 사이 구간은 VXLAN 바깥 헤더의 노드 IP로 보이지만, 이 구성은 이번에 측정하지 않았습니다.
{cue: transition}
다음은 온프렘 Pod가 AWS API를 사설 경로로 쓰는 부분입니다.

[출처]
• 데모 저장소 results/connectivity-20261019-1050.md, demo-connectivity/run-tests.sh, RUNBOOK.md 0.1절 (2026-10-19 실측)
• https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-cni.html (Networking Mode: VXLAN encapsulation, masquerade를 끄면 Pod CIDR이 온프렘에서 라우팅 가능해야 함, BGP 권장)
:::

---
<!-- Slide 18: PrivateLink -->
@type: content
@title: 온프렘 Pod에서 PrivateLink로 AWS API 호출

## 온프렘 Pod에서 PrivateLink로 AWS API 호출

:::html
<style>
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: break-word; }
.flow-h { margin: 0 0 var(--space-4); }
.flow-h .flow-box { min-width: min-content; overflow-wrap: normal; }
.hn-flow-sub { display: block; color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: break-word; }
</style>
<div class="flow-h">
  <div class="flow-box fragment fade-right" data-fragment-index="1">hybrid Pod<br><span class="hn-flow-sub">172.17.x, IRSA 토큰</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="2">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="2">CoreDNS, VPC resolver<br><span class="hn-flow-sub">sts, s3 이름을 endpoint ENI로</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="3">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="3">TGW (실환경 DX/VPN)<br><span class="hn-flow-sub">출발지 Pod IP 유지</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="4">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="4">interface endpoint<br><span class="hn-flow-sub">STS, S3 (10.0.x)</span></div>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="5">
  <div class="callout callout-success"><strong class="text-success">IRSA: 토큰 교환부터 사설 경로</strong><div class="on-surface-muted">hybrid Pod가 STS endpoint로 IRSA 토큰을 교환하고 S3 endpoint로 PutObject, 클라우드 Pod가 같은 객체를 읽었습니다.</div></div>
  <div class="callout callout-success"><strong class="text-success">SG가 Pod IP로 구분</strong><div class="on-surface-muted">endpoint SG의 443은 클라우드 VPC와 hybrid Pod 대역 172.17.0.0/16에만, 노드 대역은 제외. 같은 노드에서 Pod는 302, hostNetwork(노드 IP)는 타임아웃.</div></div>
  <div class="callout callout-info"><strong class="text-info">버킷 정책</strong><div class="on-surface-muted"><code>aws:SourceVpce</code> 조건으로 테스트 역할은 endpoint를 거칠 때만 허용. 같은 역할로 밖에서 부르면 거부됐습니다.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">S3는 interface endpoint</strong><div class="on-surface-muted">gateway endpoint는 온프렘에서 쓸 수 없습니다. 데모처럼 gateway endpoint 없이 만들 때는 <code>DnsOptions</code>를 <code>AllResolvers</code>로 줘야 생성됐습니다.</div></div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
• hybrid Pod의 sts, s3 이름이 클라우드 VPC의 interface endpoint ENI로 풀림
• IRSA 토큰 교환과 S3 쓰기가 모두 endpoint 경유, 버킷 정책으로 강제
• endpoint SG에서 온프렘 쪽은 Pod CIDR만 열고 노드 대역은 빼서 Pod 단위 통제 확인

온프렘 Pod가 AWS API를 쓸 때 인터넷으로 나가지 않게 하려면 PrivateLink가 답입니다. 클라우드 VPC에 STS와 S3 interface endpoint를 만들고 private DNS를 켰습니다. hybrid Pod는 CoreDNS를 거쳐 VPC resolver로 이름을 풀기 때문에, sts와 s3 이름이 endpoint ENI의 10.0 주소로 풀렸습니다. 실제 온프렘 서버가 직접 부를 때는 Route 53 Resolver inbound endpoint를 두셔야 합니다.
{cue: pause}
IRSA는 Pod가 직접 STS를 불러 토큰을 바꾸므로 그 호출부터 endpoint로 갑니다. 이어서 S3에 쓰고, 클라우드 Pod가 같은 객체를 읽었습니다. 버킷 정책에 SourceVpce 조건을 걸어서, 같은 역할로 endpoint 밖에서 부르면 거부되는 것도 확인했습니다.
endpoint SG를 온프렘 쪽은 Pod 대역에만 열고 노드 대역은 뺐더니, 같은 노드에서 Pod는 통과하고 hostNetwork는 막혔습니다. SNAT이 없으니 AWS 쪽 SG로도 온프렘 Pod를 구분할 수 있다는 뜻입니다.
S3는 주의할 점이 두 가지입니다. gateway endpoint는 온프렘 트래픽을 받지 않으니 interface endpoint가 필요하고, gateway endpoint 없이 만들 때는 DnsOptions를 AllResolvers로 줘야 생성됐습니다. 처음 시도는 이것 때문에 실패했습니다.
{cue: transition}
마지막으로 전체를 정리하겠습니다.

[출처]
• 데모 저장소 demo-connectivity/privatelink.yaml, results/connectivity-20261019-1050.md 11절 (2026-10-19 실측)
• https://docs.aws.amazon.com/vpc/latest/privatelink/privatelink-access-aws-services.html
• https://docs.aws.amazon.com/AmazonS3/latest/userguide/privatelink-interface-endpoints.html
:::

---
<!-- Slide 19: 링크 단절과 CoreDNS -->
@type: content
@title: 링크가 끊기면 hybrid Pod의 DNS는

## 링크가 끊기면 hybrid Pod의 DNS는

:::html
<style>
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.ld-table { width: 100%; border-collapse: collapse; margin-bottom: var(--space-3); font-size: var(--fs-card); }
.ld-table th, .ld-table td { border: 1px solid var(--border); padding: var(--space-2) var(--space-3); text-align: left; }
.ld-table th { background: var(--bg-card); }
.ld-num { font-variant-numeric: tabular-nums; white-space: nowrap; }
</style>
<table class="ld-table fragment fade-up" data-fragment-index="1">
  <tr><th>CoreDNS 구성</th><th>단절 약 95초 동안 hybrid Pod 이름 해석</th><th>원인</th></tr>
  <tr><td>기본: 2개 모두 클라우드 노드</td><td class="ld-num text-danger">경로 반영 뒤 모두 실패 (43~44개 중 26개)</td><td>ClusterIP 호출은 200, 이름만 못 풂</td></tr>
  <tr><td>zone label, 3개, <code>PreferSameZone</code> (문서와 다른 값)</td><td class="ld-num text-warning">절반가량 실패 (76~80개 중 38~44개)</td><td>Cilium이 이 값을 무시하고 끊긴 클라우드 CoreDNS로도 분산</td></tr>
  <tr><td>4개, <code>PreferClose</code>, zone 분산 강제, Cilium 재시작</td><td class="ld-num text-success">실패 0 (96~97개 중)</td><td>hybrid Pod는 온프렘 CoreDNS만 사용</td></tr>
</table>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="2">
  <div class="callout callout-warning"><strong class="text-warning">문서대로 PreferClose</strong><div class="on-surface-muted">hybrid 노드의 ClusterIP는 Cilium BPF가 분산합니다. Kubernetes 1.35의 새 이름 <code>PreferSameZone</code>은 Cilium 1.18이 무시했습니다.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">zone label은 조인할 때</strong><div class="on-surface-muted">나중에 붙여서 Cilium을 재시작했습니다. nodeadm의 kubelet <code>--node-labels</code>로 조인할 때 붙이세요.</div></div>
  <div class="callout callout-danger"><strong class="text-danger">PrivateLink 우회</strong><div class="on-surface-muted">온프렘 CoreDNS는 온프렘 DNS로 넘겨 STS, S3가 공인 IP로 풀렸습니다. Resolver inbound endpoint로 <code>amazonaws.com</code>을 넘겨 해결.</div></div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
• 기본 구성에서는 링크가 끊기면 hybrid Pod의 모든 이름 해석이 실패
• 권장 구성도 Cilium 1.18에서는 PreferClose, 조인 시 zone label, zone마다 CoreDNS가 있어야 실패 0
• 온프렘에 CoreDNS를 두면 PrivateLink 이름이 공인 IP로 풀리므로 amazonaws.com 전달이 필요

TGW에 blackhole 라우트를 넣어 DX 단절을 약 95초 동안 재현했습니다. 기본 구성은 CoreDNS 두 개가 모두 클라우드 노드에 있어서, 단절 중 hybrid Pod는 온프렘 Service 이름조차 풀지 못했습니다. 같은 Service를 ClusterIP로 부르면 계속 200이었으니, 온프렘 안의 통신은 살아 있는데 이름 때문에 서비스가 멈춘 셈입니다.
{cue: pause}
AWS 문서는 hybrid 노드에 zone label을 주고 kube-dns에 trafficDistribution PreferClose를 넣으라고 안내합니다. 저는 Kubernetes 1.35에서 deprecated된 이름이라 새 이름 PreferSameZone으로 바꿔 넣었는데, 그랬더니 절반가량 실패했습니다. hybrid 노드에서 ClusterIP를 분산하는 Cilium 1.18이 새 이름을 무시했기 때문입니다. 재시작 뒤에도 새 이름일 때는 백엔드가 그대로였고 PreferClose로 되돌리자 곧바로 온프렘 백엔드만 남았습니다. 그 회차에서 Cilium 재시작과 클라우드 AZ마다 하나씩 CoreDNS 강제 분산도 함께 적용했고, 실패가 0이 됐습니다.
그런데 온프렘 CoreDNS를 두자 새 문제가 생겼습니다. 온프렘 DNS로 넘기니 STS와 S3가 공인 IP로 풀려 PrivateLink를 우회했고, 버킷 정책에 막혔습니다. Route 53 Resolver inbound endpoint로 amazonaws.com만 넘겨 해결했습니다. 실제 환경에서는 온프렘 DNS의 조건부 전달이 같은 역할입니다.
{cue: transition}
마지막으로 전체를 정리하겠습니다.

[출처]
• 데모 저장소 results/dns-baseline-20261019-1335.md, dns-ha-20261019-1342.md, dns-final-20261019-1405.md, demo-connectivity/dns-failover.sh (2026-10-19 실측)
• https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-webhooks.html (mixed mode CoreDNS 권장 구성)
:::

---
<!-- Slide 20: 정리 -->
@type: content
@title: 정리: 무엇을 확인했고 무엇이 남았나

## 정리: 무엇을 확인했고 무엇이 남았나

:::html
<style>
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.ld-list { margin: var(--space-2) 0 0; padding-left: var(--space-4); color: var(--text-secondary); font-size: var(--fs-card); }
</style>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="callout callout-success"><strong class="text-success">확인한 것</strong><ul class="ld-list"><li>gateway 전환 3~5초, 그동안 요청 실패 있음</li><li>온프렘 Pod 보호(B, C), GPU 추론, Istio sidecar 공존</li><li>ALB ip 타깃 자동 갱신, 온프렘에서 internal ALB</li><li>SNAT 없는 연결 38개, PrivateLink, 단절 중 DNS 실패 0</li></ul></div>
  <div class="callout callout-warning"><strong class="text-warning">아직 남은 것</strong><div class="on-surface-muted">B와 C의 반복 측정, Istio ambient 모드, gateway 처리량, hostNetwork와 NodePort 경로(노드 SG), 실제 온프렘 서버에서의 재검증.</div></div>
  <div class="callout callout-info"><strong class="text-info">직접 해 보려면</strong><div class="on-surface-muted">데모 저장소의 RUNBOOK.md 순서를 따르고, 끝나면 teardown.sh로 정리해 비용을 멈추세요.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">반드시 기억할 것</strong><div class="on-surface-muted">모든 수치는 EC2로 시뮬레이션한 환경의 값입니다. native routing은 AWS 지원 범위 밖입니다.</div></div>
</div>
:::


:::notes
{timing: 1.5min}
[요약]
• 확인: gateway 전환, 온프렘 Pod 보호, GPU 추론, Istio 공존, ALB ip 타깃, SNAT 없는 연결과 PrivateLink, 링크 단절 중 DNS
• 남은 것: 반복 측정, ambient, 처리량, 실제 온프렘 재검증
• 수치는 시뮬레이션 환경의 값

정리하겠습니다. gateway 전환은 3~5초, 온프렘 Pod는 Kyverno만으로도 지켜졌고, Karpenter 기능은 EC2 수와 정리 시간에서 작은 이득을 줬습니다.
GPU 추론은 hybrid 노드에서 돌고 클라우드에서 호출됐고, Istio는 gateway와 함께 동작했고, ALB는 바뀌는 hybrid Pod IP를 따라갔습니다. native routing으로 바꾼 뒤에는 38개 연결 항목이 모두 통과했고 Pod에서 출발한 요청은 서버에 Pod IP로 보였으며, 온프렘 Pod도 PrivateLink로 STS와 S3를 썼습니다. 링크를 끊었을 때 hybrid Pod의 이름 해석은 CoreDNS 구성을 고친 뒤 실패가 0이었습니다. native routing은 AWS 지원 범위 밖이라는 점도 다시 말씀드립니다.
남은 것도 솔직히 말씀드립니다. B와 C의 차이는 반복 측정이 필요하고, Istio ambient 모드와 gateway 처리량은 보지 못했고, 모든 수치는 시뮬레이션 환경의 값이라 실제 온프렘에서 다시 확인해야 합니다.
{cue: transition}
마지막으로 참고 자료를 정리하고 질문을 받겠습니다.

[출처]
• 데모 저장소 RUNBOOK.md, KNOWN-ISSUES.md (private 저장소)
:::

---
<!-- Slide 21: 통합 참고 자료 -->
@type: content
@title: 참고 자료 & Q&A

## 참고 자료 & Q&A

:::html
<style>
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.hn-ref a { color: var(--accent); }
</style>
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">개요와 요금</button>
  <button class="tab-btn">네트워킹과 Gateway</button>
  <button class="tab-btn">노드와 라이프사이클</button>
  <button class="tab-btn">운영, GPU, 비용</button>
  <button class="tab-btn">데모</button>
</div>
<div class="tc">
  <div class="card-grid" data-reveal="static">
    <div class="card"><strong class="text-accent">개요</strong><div class="on-surface-muted hn-ref"><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-overview.html" target="_blank" rel="noopener">Hybrid Nodes 개요</a><br><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-os.html" target="_blank" rel="noopener">지원 OS</a></div></div>
    <div class="card"><strong class="text-accent">자격 증명</strong><div class="on-surface-muted hn-ref"><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-creds.html" target="_blank" rel="noopener">자격 증명 준비 (SSM, IAM RA)</a></div></div>
    <div class="card"><strong class="text-accent">요금</strong><div class="on-surface-muted hn-ref"><a href="https://aws.amazon.com/eks/pricing/" target="_blank" rel="noopener">EKS 요금</a></div></div>
    <div class="card"><strong class="text-accent">문제 해결</strong><div class="on-surface-muted hn-ref"><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-troubleshooting.html" target="_blank" rel="noopener">Troubleshooting</a></div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="card-grid" data-reveal="static">
    <div class="card"><strong class="text-accent">네트워킹</strong><div class="on-surface-muted hn-ref"><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-networking.html" target="_blank" rel="noopener">네트워킹 요구 사항</a><br><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-cni.html" target="_blank" rel="noopener">CNI 구성</a><br><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-cilium-bgp.html" target="_blank" rel="noopener">Cilium BGP</a></div></div>
    <div class="card"><strong class="text-accent">webhook과 혼합 모드</strong><div class="on-surface-muted hn-ref"><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-webhooks.html" target="_blank" rel="noopener">webhook과 혼합 모드 고려 사항</a></div></div>
    <div class="card"><strong class="text-accent">Hybrid Nodes Gateway</strong><div class="on-surface-muted hn-ref"><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-gateway-overview.html" target="_blank" rel="noopener">개요</a><br><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-gateway-getting-started.html" target="_blank" rel="noopener">시작하기</a><br><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-gateway-operations.html" target="_blank" rel="noopener">운영</a><br><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-gateway-cni.html" target="_blank" rel="noopener">CNI 설정</a></div></div>
    <div class="card"><strong class="text-accent">Gateway 소스와 블로그</strong><div class="on-surface-muted hn-ref"><a href="https://github.com/aws/eks-hybrid-nodes-gateway" target="_blank" rel="noopener">aws/eks-hybrid-nodes-gateway</a><br><a href="https://aws.amazon.com/blogs/containers/simplify-hybrid-kubernetes-networking-with-amazon-eks-hybrid-nodes-gateway/" target="_blank" rel="noopener">AWS Containers 블로그</a></div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="card-grid" data-reveal="static">
    <div class="card"><strong class="text-accent">nodeadm</strong><div class="on-surface-muted hn-ref"><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-nodeadm.html" target="_blank" rel="noopener">nodeadm 레퍼런스</a><br><a href="https://github.com/aws/eks-hybrid" target="_blank" rel="noopener">aws/eks-hybrid 소스</a></div></div>
    <div class="card"><strong class="text-accent">Bottlerocket</strong><div class="on-surface-muted hn-ref"><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-bottlerocket.html" target="_blank" rel="noopener">Bottlerocket 연결</a></div></div>
    <div class="card"><strong class="text-accent">업그레이드</strong><div class="on-surface-muted hn-ref"><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-upgrade.html" target="_blank" rel="noopener">Hybrid 노드 업그레이드</a><br><a href="https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions-standard.html" target="_blank" rel="noopener">Kubernetes 버전</a></div></div>
    <div class="card"><strong class="text-accent">애드온</strong><div class="on-surface-muted hn-ref"><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-add-ons.html" target="_blank" rel="noopener">애드온 구성 (Pod Identity 등)</a></div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="card-grid" data-reveal="static">
    <div class="card"><strong class="text-accent">네트워크 단절</strong><div class="on-surface-muted hn-ref"><a href="https://docs.aws.amazon.com/eks/latest/best-practices/hybrid-nodes-network-disconnection-best-practices.html" target="_blank" rel="noopener">단절 대비 모범 사례</a><br><a href="https://docs.aws.amazon.com/eks/latest/best-practices/hybrid-nodes-host-creds.html" target="_blank" rel="noopener">단절 시 자격 증명</a></div></div>
    <div class="card"><strong class="text-accent">GPU</strong><div class="on-surface-muted hn-ref"><a href="https://docs.aws.amazon.com/eks/latest/userguide/device-management-nvidia.html" target="_blank" rel="noopener">NVIDIA GPU 장치 관리</a></div></div>
    <div class="card"><strong class="text-accent">스케줄링</strong><div class="on-surface-muted hn-ref"><a href="https://karpenter.sh/docs/upgrading/compatibility/" target="_blank" rel="noopener">Karpenter 호환성</a><br><a href="https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/" target="_blank" rel="noopener">ReplicaSet pod-deletion-cost</a></div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="card-grid" data-reveal="static">
    <div class="card"><strong class="text-accent">데모 가이드</strong><div class="on-surface-muted hn-ref"><a href="demo-guide.html" target="_blank" rel="noopener">구현과 실측 결과 정리</a></div></div>
    <div class="card"><strong class="text-accent">데모 저장소</strong><div class="on-surface-muted hn-ref"><a href="https://github.com/Atom-oh/eks-hybrid-demo" target="_blank" rel="noopener">Atom-oh/eks-hybrid-demo (private)</a></div></div>
  </div>
</div>
<div class="callout callout-info fragment fade-up" data-fragment-index="1"><strong class="text-info">Q&A</strong> 예제는 검토 기준(EKS 1.36, nodeadm 1.0.20)이고, 5부 수치는 시뮬레이션 환경의 실측입니다. 적용 전에 최신 AWS 문서로 지원 조합을 확인하세요.</div>
:::


:::notes
{timing: 1min}
[요약]
• 주제별 탭으로 공식 문서를 모았음: 개요와 요금, 네트워킹과 Gateway, 노드와 라이프사이클, 운영과 GPU와 비용, 데모
• 링크는 모두 클릭해서 열 수 있음
• 예제는 검토 기준이고, 5부 수치는 시뮬레이션 환경의 실측

오늘 다룬 내용의 근거 문서를 주제별 탭으로 모았습니다. 링크는 바로 열 수 있습니다. 데모 탭에는 구현과 실측 결과를 정리한 가이드 페이지가 있습니다.
{cue: pause}
예제와 명령은 EKS 1.36, nodeadm 1.0.20을 기준으로 검토했고, 5부의 수치는 EC2로 온프렘을 시뮬레이션한 환경에서 잰 값입니다. 적용하시기 전에 최신 문서로 지원 조합을 확인하시기 바랍니다.
{cue: question}
이제 질문 받겠습니다.
:::

---
<!-- Slide 22: Thank You -->
@type: thankyou
@toc: toc.html
@message: EKS Hybrid Nodes, 감사합니다

# Thank You

:::notes
{timing: 0.5min}
[요약]
• 세션 마무리

오늘 세션 들어 주셔서 감사합니다. 데모 코드와 측정 결과는 데모 가이드 페이지에 정리해 두었습니다.
:::
