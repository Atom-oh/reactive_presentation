---
remarp: true
block: 04-demo-close
---

---
<!-- Slide 1: 5부 구분 (Section) -->
@type: section

# 5부: 데모 영상

같은 조건, 두 클러스터: 스케일 아웃, Consolidation, Drift, Spot 중단

:::notes
{timing: 0.5min}
[요약]
- 5부의 질문: 1~4부에서 설명한 동작이 EKS 1.37 클러스터에서 실제로 어떻게 보이는가
- 영상 4개: V1 스케일 아웃, V2 Consolidation, V3 Drift 교체, V4 Spot 중단
- 영상은 무음이고, 실제 터미널 녹화(2026-10-20)와 그 결과를 재구성한 설명 장면으로 구성됩니다

5부는 데모 영상입니다. 2026년 10월 20일에 EKS 1.37 클러스터 두 개를 만들어 직접 돌린 결과를 녹화했고, 네트워크 상황과 상관없이 같은 화면을 보여 드리려고 라이브 대신 영상을 씁니다.
모든 숫자는 한 번 실행한 결과입니다. 벤치마크가 아니라 동작을 눈으로 확인하는 용도라는 점을 먼저 말씀드립니다.
{cue: transition}
어떤 환경에서 돌렸는지부터 보겠습니다.
:::

---
<!-- Slide 2: 데모 환경 -->
@type: content
@title: 데모 환경: 같은 VPC, 같은 NodePool 조건

## 데모 환경: 같은 VPC, 같은 NodePool 조건

:::html
<style>
.ak4-env { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3); margin-bottom: var(--space-3); }
.ak4-env .card { word-break: keep-all; }
.ak4-auto { color: var(--accent); font-weight: var(--weight-bold); }
.ak4-karp { color: var(--warning); font-weight: var(--weight-bold); }
.ak4-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.ak4-list { margin: var(--space-2) 0 0; padding-left: var(--space-4); font-size: var(--fs-card); line-height: 1.6; }
.text-info { color: var(--info); font-weight: var(--weight-bold); }
</style>
<div class="ak4-env" data-reveal="stagger">
  <div class="card">
    <span class="ak4-auto">akd-auto: EKS Auto Mode</span>
    <ul class="ak4-list">
      <li>노드 OS: Bottlerocket (EKS Auto, Standard) 2026.10.9</li>
      <li>NodeClass <code>demo</code> (eks.amazonaws.com/v1)</li>
      <li>정책 미지정 시 라이브 값: <code>Balanced</code>, expireAfter 336h</li>
    </ul>
  </div>
  <div class="card">
    <span class="ak4-karp">akd-karp: 직접 설치 Karpenter 1.15.0</span>
    <ul class="ak4-list">
      <li>노드 OS: Amazon Linux 2023 (AMI v20261003으로 시작)</li>
      <li>EC2NodeClass <code>default</code> + interruption queue (SQS)</li>
      <li>정책 미지정 시 라이브 값: <code>WhenEmptyOrUnderutilized</code>, expireAfter 720h</li>
    </ul>
  </div>
</div>
<div class="callout callout-info fragment fade-up" data-fragment-index="1">
  <strong class="text-info">공통 조건</strong>: EKS 1.37, ap-northeast-2, 데모 VPC의 private 서브넷 2개(2a, 2b). NodePool <code>demo</code>: on-demand, c/m/r 계열, generation 5 초과, amd64, consolidateAfter 30s, budget <code>nodes: "1"</code>. 워크로드: pause 컨테이너, replica당 1 vCPU / 1.5Gi
  <div class="ak4-muted">노드에 공인 IP 없음. API endpoint는 작업 PC의 출구 IP 하나만 허용했습니다.</div>
</div>
:::

:::notes
{timing: 1.5min}
[요약]
- 클러스터 두 개: akd-auto(Auto Mode), akd-karp(직접 설치 Karpenter 1.15.0). 둘 다 EKS 1.37
- 두 NodePool의 조건을 똑같이 맞췄고, consolidationPolicy는 일부러 비워 두었습니다
- 다른 점: 노드 OS(Bottlerocket과 AL2023), 기본 정책(Balanced와 WhenEmptyOrUnderutilized), Spot 중단 처리 주체

두 클러스터는 같은 VPC, 같은 서브넷에 있습니다. 왼쪽이 Auto Mode, 오른쪽이 Karpenter를 직접 설치한 클러스터이고, 영상에서도 Auto Mode는 파란색, Karpenter는 노란색으로 구분합니다.
NodePool 조건은 똑같이 맞췄습니다. on-demand, c, m, r 계열, 5세대 초과, amd64이고, budget은 한 번에 노드 한 대입니다.
{cue: pause}
consolidationPolicy는 두 쪽 다 일부러 쓰지 않았습니다. 그랬더니 Auto Mode는 Balanced, Karpenter는 WhenEmptyOrUnderutilized가 들어갔습니다. 3부에서 말씀드린 1.37 기본값이 실제로 이렇게 보입니다.
노드 OS가 다르다는 점도 기억해 주세요. 뒤에서 나오는 시간 차이를 해석할 때 필요합니다.
근거: RECORDINGS.md 공통 사항(라이브 값), 데모 저장소 manifests/*nodepool.yaml.tmpl
{cue: transition}
첫 번째 영상, 스케일 아웃입니다.
:::

---
<!-- Slide 3: V1 영상 -->
@type: content
@fit: off
@title: V1: 같은 Pending Pod 10개

## V1: 같은 Pending Pod 10개

:::html
<style>
.ak4-video { width: 100%; max-height: 100%; aspect-ratio: 16 / 9; background: var(--bg-card); border-radius: var(--space-2); }
.ak4-full { flex: 1; min-height: 0; display: flex; flex-direction: column; gap: var(--space-1); }
.ak4-vbox { flex: 1; min-height: 0; container-type: size; }
.ak4-full .ak4-video { display: block; width: min(100cqw, calc(100cqh * 16 / 9)); height: auto; max-height: none; margin-inline: auto; }
.ak4-full .ak4-video-cap { color: var(--text-secondary); text-align: center; margin-top: 0; font-size: var(--fs-card); }
</style>
<div class="ak4-full">
<div class="ak4-vbox">
<video class="ak4-video" src="media/v1-scaleout.mp4" poster="media/v1-scaleout.jpg" aria-label="V1 영상: 스케일 아웃 비교, 실제 터미널 녹화 포함, 무음, 2분 30초" title="V1 영상: 스케일 아웃 비교, 실제 터미널 녹화 포함, 무음, 2분 30초" controls preload="metadata" muted playsinline tabindex="-1"></video>
</div>
<div class="ak4-video-cap">실제 터미널 녹화(2026-10-20)와 실측 결과 재구성, 무음</div>
</div>
:::

:::script
(function () {
  // While a video plays, Chromium's native controls keep focus and swallow arrow, PageDown and Space.
  // Hand focus back to the page after any video interaction so the deck keys keep working.
  document.querySelectorAll('video.ak4-video').forEach(function (v) {
    var release = function () { setTimeout(function () { if (document.activeElement === v) v.blur(); }, 0); };
    ['focus', 'play', 'pause', 'seeked', 'volumechange', 'click', 'pointerup'].forEach(function (ev) { v.addEventListener(ev, release); });
  });
  // The deck updates location.hash on every slide change: pause any video left on a slide that is no longer active.
  window.addEventListener('hashchange', function () {
    document.querySelectorAll('.slide:not(.active) video.ak4-video').forEach(function (v) { if (!v.paused) v.pause(); });
  });
})();
:::

:::notes
{timing: 2.5min}
[요약]
- 두 클러스터에 동시에 replica 10개(각 1 vCPU / 1.5Gi)를 배포
- 둘 다 NodeClaim 1개, c7i-flex.4xlarge on-demand를 골랐습니다
- 노드 Ready: Auto Mode 15초, Karpenter 40초. Pod 10개 Ready: +28초, +47초

Play를 누르고 장면마다 짧게 설명합니다. 영상은 무음입니다.
0:00 제목과 메시지입니다.
0:06 실험 조건입니다. 두 클러스터의 차이(노드 관리 주체, 노드 OS)와 공통 조건(EKS 1.37, 같은 NodePool 조건, pause 워크로드 10개)을 짚습니다.
0:34 실제 터미널 녹화입니다(0.5배속, 대기 구간 줄임). 두 NodePool의 requirements가 같다는 것을 먼저 보여 주고, 두 클러스터에 동시에 scale 명령을 보냅니다. Auto Mode 쪽이 먼저 10/10 Running이 되고 Karpenter 쪽은 아직 Pending인 화면에서 잠시 멈춰도 좋습니다.
{cue: pause}
1:28 타임라인 비교입니다. 노드 Ready는 NodeClaim 생성 시각 기준, Pod 10개 Ready는 scale 명령 기준이라는 점을 구분해 말해 주세요.
2:04 해석과 주의입니다. 같았던 것과 달랐던 것, 1회 측정이라는 점으로 마무리합니다.
근거: V1 영상 프로젝트 FACTS.md와 STORYBOARD.md(장면 시간), RECORDINGS.md D1
{cue: transition}
숫자를 한 장으로 정리하겠습니다.
:::

---
<!-- Slide 4: V1 결과 -->
@type: content
@title: V1 결과: 고른 인스턴스는 같고, 준비 시간은 달랐다

## V1 결과: 고른 인스턴스는 같고, 준비 시간은 달랐다

:::html
<style>
.ak4-table { width: 100%; font-size: var(--fs-card); word-break: keep-all; }
.ak4-table td.ak4-num { font-variant-numeric: tabular-nums; font-weight: var(--weight-bold); }
.ak4-table .ak4-auto { color: var(--accent); font-weight: var(--weight-bold); }
.ak4-table .ak4-karp { color: var(--warning); font-weight: var(--weight-bold); }
.data-table th { text-transform: none; letter-spacing: normal; font-size: var(--fs-card); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.ak4-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<table class="data-table ak4-table fragment fade-up" data-fragment-index="1">
  <thead><tr><th>클러스터</th><th>선택한 노드</th><th>NodeClaim 생성 (UTC)</th><th>노드 Ready</th><th>Pod 10개 Ready</th></tr></thead>
  <tbody>
    <tr><td class="ak4-auto">akd-auto (Auto Mode)</td><td>c7i-flex.4xlarge 1대</td><td class="ak4-num">13:54:15</td><td class="ak4-num">+15초</td><td class="ak4-num">+28초</td></tr>
    <tr><td class="ak4-karp">akd-karp (Karpenter 1.15.0)</td><td>c7i-flex.4xlarge 1대</td><td class="ak4-num">13:54:15</td><td class="ak4-num">+40초</td><td class="ak4-num">+47초</td></tr>
  </tbody>
</table>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="2">
  <div class="callout callout-info"><strong class="text-info">결정 로직은 같다</strong><div class="ak4-muted">같은 requirements와 같은 Pod 요청에 같은 인스턴스 유형, 같은 대수를 골랐습니다. Auto Mode 안에서도 Karpenter가 판단합니다.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">시간 차이는 1회 측정</strong><div class="ak4-muted">노드 OS(Bottlerocket과 AL2023)와 부팅 구성이 다릅니다. 직접 운영 시 AMI와 userData를 줄이는 만큼 달라질 수 있습니다.</div></div>
</div>
:::

:::notes
{timing: 1min}
[요약]
- 같은 조건에 같은 c7i-flex.4xlarge 1대, NodeClaim은 같은 초(13:54:15)에 생성
- 노드 Ready 15초 대 40초, Pod 10개 Ready 28초 대 47초
- 1회 측정이며 노드 OS가 다르므로 벤치마크로 쓰지 않습니다

두 클러스터 모두 같은 초에 NodeClaim을 만들었고, 같은 인스턴스를 한 대 골랐습니다. 노드를 고르는 판단은 같은 Karpenter 로직이라는 뜻입니다.
차이는 노드가 준비되는 시간이었습니다. Auto Mode 노드가 15초, Karpenter 노드가 40초 만에 Ready가 됐습니다.
{cue: pause}
이 숫자를 "Auto Mode가 항상 빠르다"로 가져가지는 마세요. 한 번 잰 값이고, 노드 OS와 부팅 구성이 다릅니다. 직접 운영하신다면 AMI와 부팅 스크립트를 가볍게 만드는 만큼 줄일 수 있는 영역입니다.
근거: RECORDINGS.md D1 (nodeclaims CREATED, READY lastTransitionTime, d1-timing.txt)
{cue: transition}
두 번째 영상은 줄일 때, consolidation입니다.
:::

---
<!-- Slide 5: V2 영상 -->
@type: content
@fit: off
@title: V2: 정책을 비워 두면 무엇이 들어갈까

## V2: 정책을 비워 두면 무엇이 들어갈까

:::html
<style>
.ak4-video { width: 100%; max-height: 100%; aspect-ratio: 16 / 9; background: var(--bg-card); border-radius: var(--space-2); }
.ak4-full { flex: 1; min-height: 0; display: flex; flex-direction: column; gap: var(--space-1); }
.ak4-vbox { flex: 1; min-height: 0; container-type: size; }
.ak4-full .ak4-video { display: block; width: min(100cqw, calc(100cqh * 16 / 9)); height: auto; max-height: none; margin-inline: auto; }
.ak4-full .ak4-video-cap { color: var(--text-secondary); text-align: center; margin-top: 0; font-size: var(--fs-card); }
</style>
<div class="ak4-full">
<div class="ak4-vbox">
<video class="ak4-video" src="media/v2-consolidation.mp4" poster="media/v2-consolidation.jpg" aria-label="V2 영상: 스케일 인과 consolidation, 실제 터미널 녹화 포함, 무음, 2분 50초" title="V2 영상: 스케일 인과 consolidation, 실제 터미널 녹화 포함, 무음, 2분 50초" controls preload="metadata" muted playsinline tabindex="-1"></video>
</div>
<div class="ak4-video-cap">실제 터미널 녹화(2026-10-20)와 실측 결과 재구성, 무음</div>
</div>
:::

:::notes
{timing: 3min}
[요약]
- 정책을 비워 둔 NodePool의 라이브 값: Auto Mode Balanced, Karpenter WhenEmptyOrUnderutilized
- 10개에서 4개로 줄이자 두 클러스터 모두 4xlarge를 2xlarge로 교체하고 Pod 4개를 옮겼습니다
- Balanced 승인 이벤트: savings 50.0%, disruption 100.0%, score 0.50 >= threshold 0.50

Play를 누르고 장면마다 짧게 설명합니다. 영상은 무음입니다.
0:00 제목과 메시지입니다.
0:06 정책을 지정하지 않은 NodePool의 라이브 값입니다. 왼쪽 Auto Mode는 Balanced와 336h, 오른쪽 Karpenter는 WhenEmptyOrUnderutilized와 720h입니다. 나머지 조건은 같습니다.
0:30 실제 터미널 녹화입니다(0.5배속, 대기 구간 줄임). 기본 정책을 확인한 뒤 두 클러스터를 10개에서 4개로 줄입니다. 상단 줄의 nodes와 moved pods 숫자가 바뀌는 순간을 짚어 주세요.
{cue: pause}
1:39 결과입니다. 두 클러스터 모두 4xlarge를 2xlarge로 교체했고 이벤트 순서도 같습니다.
2:03 Balanced 점수 장면입니다. savings 50%, disruption 100%, score 0.50이 임계값 0.50과 같아 승인되었습니다. 여기서 잠시 멈추고 읽어 드리세요.
2:27 정리입니다. 녹화 회차와 앞선 회차를 따로 보여 주고, 시점은 비교하지 않는다는 점을 강조합니다.
근거: V2 영상 프로젝트 FACTS.md와 STORYBOARD.md, RECORDINGS.md D2
{cue: transition}
결과와 Balanced 점수를 다시 보겠습니다.
:::

---
<!-- Slide 6: V2 결과 -->
@type: content
@title: V2 결과: 같은 교체, Balanced는 점수로 승인했다

## V2 결과: 같은 교체, Balanced는 점수로 승인했다

:::html
<style>
.ak4-two { display: grid; grid-template-columns: 1.1fr 1fr; gap: var(--space-4); align-items: start; }
.ak4-steps { margin: 0; padding-left: var(--space-4); font-size: var(--fs-card); line-height: 1.7; word-break: keep-all; }
.ak4-score { font-family: var(--font-mono); font-size: var(--fs-card); background: var(--bg-card); border-radius: var(--space-2); padding: var(--space-3); word-break: break-all; }
.ak4-auto { color: var(--accent); font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.ak4-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak4-two">
  <div>
    <div class="card fragment fade-up" data-fragment-index="1">
      <strong class="text-info">두 클러스터 모두 같은 순서</strong>
      <ol class="ak4-steps">
        <li>DisruptionLaunching: 대체 NodeClaim(c7i-flex.2xlarge) 먼저 생성</li>
        <li>새 노드 Ready 확인</li>
        <li>DisruptionTerminating: 기존 c7i-flex.4xlarge</li>
        <li>Evicted: Pod 4개가 새 노드로 이동</li>
      </ol>
    </div>
  </div>
  <div>
    <div class="fragment fade-up" data-fragment-index="2">
      <span class="ak4-auto">Auto Mode 이벤트 (ConsolidationApproved)</span>
      <div class="ak4-score">score 0.50 &gt;= threshold 0.50<br>(k: 2, savings 50.0%, disruption 100.0%)</div>
      <div class="ak4-muted">절감 비율을 disruption 비율로 나눈 점수가 임계값 이상일 때만 실행합니다. 노드 한 대뿐이라 disruption 100%였고, 절감 50%로 겨우 통과했습니다.</div>
    </div>
    <div class="callout callout-warning fragment fade-up" data-fragment-index="3"><strong class="text-warning">시점은 비교하지 않는다</strong><div class="ak4-muted">녹화 회차는 Auto Mode +67초, Karpenter +75초에 첫 이동. 앞선 회차는 Karpenter 약 1분, Auto Mode 약 5분 30초 뒤였습니다. 정책의 속도 차이로 해석하지 않습니다.</div></div>
  </div>
</div>
:::

:::notes
{timing: 1.5min}
[요약]
- 결과는 같았습니다: 4xlarge를 2xlarge로 교체, Pod 4개 이동, 새 노드를 먼저 띄운 뒤 기존 노드를 비움
- Balanced는 이벤트에 점수를 남깁니다: savings 50%, disruption 100%, score 0.50, 임계값 0.50
- 두 회차의 실행 시점이 달라서 속도 비교는 하지 않습니다. GitOps에서는 정책을 명시하세요

결과는 같았습니다. 두 클러스터 모두 2xlarge를 먼저 띄우고, Ready가 되자 4xlarge를 비우면서 Pod 네 개를 옮겼습니다.
오른쪽이 Balanced의 특징입니다. 승인할 때 점수를 남깁니다. 절감이 50%, 영향받는 Pod 비율이 100%라서 점수가 0.5, 임계값도 0.5라 딱 통과했습니다. 점수는 노드 수가 아니라, 옮기는 Pod 비율 대비 절감 비율로 정해집니다.
{cue: pause}
시간은 비교하지 않습니다. 이번 녹화에서는 거의 같은 시점이었는데, 앞선 회차에서는 Karpenter가 약 1분, Auto Mode가 약 5분 30초 뒤에 움직였습니다. 회차마다 달라서 이걸 정책 차이로 말하기는 어렵습니다.
실무 포인트는 하나입니다. 정책을 비워 두면 클러스터마다 다른 값이 들어가니, Git에 명시해 두세요.
근거: RECORDINGS.md D2(이벤트 메시지 원문, 두 회차 구분), FACTS.md 2.3(Balanced 정의, 1.37 기본값)
{cue: transition}
세 번째는 Drift입니다.
:::

---
<!-- Slide 7: V3 영상 -->
@type: content
@fit: off
@title: V3: NodeClass를 바꾸면 노드는 한 대씩

## V3: NodeClass를 바꾸면 노드는 한 대씩

:::html
<style>
.ak4-video { width: 100%; max-height: 100%; aspect-ratio: 16 / 9; background: var(--bg-card); border-radius: var(--space-2); }
.ak4-full { flex: 1; min-height: 0; display: flex; flex-direction: column; gap: var(--space-1); }
.ak4-vbox { flex: 1; min-height: 0; container-type: size; }
.ak4-full .ak4-video { display: block; width: min(100cqw, calc(100cqh * 16 / 9)); height: auto; max-height: none; margin-inline: auto; }
.ak4-full .ak4-video-cap { color: var(--text-secondary); text-align: center; margin-top: 0; font-size: var(--fs-card); }
</style>
<div class="ak4-full">
<div class="ak4-vbox">
<video class="ak4-video" src="media/v3-drift.mp4" poster="media/v3-drift.jpg" aria-label="V3 영상: Drift 교체, 실제 터미널 녹화 포함, 무음, 2분 40초" title="V3 영상: Drift 교체, 실제 터미널 녹화 포함, 무음, 2분 40초" controls preload="metadata" muted playsinline tabindex="-1"></video>
</div>
<div class="ak4-video-cap">실제 터미널 녹화(2026-10-20)와 실측 결과 재구성, 무음</div>
</div>
:::

:::notes
{timing: 3min}
[요약]
- Karpenter: AMI alias al2023@v20261003을 al2023@v20261012로. Auto Mode: NodeClass에 advancedCompute.kubelet.maxPods 64
- 두 클러스터 모두 기존 노드 2대가 즉시 Drifted, budget 1대에 따라 새 노드를 먼저 띄우고 한 대씩 교체
- 완료: Auto Mode +98초, Karpenter +127초

Play를 누르고 장면마다 짧게 설명합니다. 영상은 무음입니다.
0:00 제목과 메시지입니다.
0:06 무엇을 바꿨나입니다. Karpenter는 AMI alias를, Auto Mode는 AMI를 고를 수 없으니 advancedCompute.kubelet.maxPods를 바꿨습니다. 패치 직후 두 클러스터 모두 기존 노드 2대가 Drifted가 됩니다.
0:29 실제 터미널 녹화입니다(0.5배속, 대기 구간 줄임). DRIFTED 표시, 새 노드가 먼저 뜨는 장면, 한 대씩 교체되는 장면을 차례로 짚어 주세요.
{cue: pause}
1:39 교체 타임라인입니다. 초록 점이 Launch, 빨간 점이 Terminate이고, 두 클러스터 모두 번갈아 진행됩니다.
2:04 결과 확인입니다. 새 AMI, capacity.pods 56, 함께 교체된 spot 노드를 봅니다.
2:24 정리 장면으로 마칩니다.
근거: V3 영상 프로젝트 FACTS.md와 STORYBOARD.md, RECORDINGS.md D3
{cue: transition}
교체 결과를 확인해 보겠습니다.
:::

---
<!-- Slide 8: V3 결과 -->
@type: content
@title: V3 결과: 새 노드를 먼저, 한 번에 한 대

## V3 결과: 새 노드를 먼저, 한 번에 한 대

:::html
<style>
.ak4-table { width: 100%; font-size: var(--fs-card); word-break: keep-all; }
.ak4-table td.ak4-num { font-variant-numeric: tabular-nums; font-weight: var(--weight-bold); }
.ak4-table .ak4-auto { color: var(--accent); font-weight: var(--weight-bold); }
.ak4-table .ak4-karp { color: var(--warning); font-weight: var(--weight-bold); }
.data-table th { text-transform: none; letter-spacing: normal; font-size: var(--fs-card); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.ak4-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<table class="data-table ak4-table fragment fade-up" data-fragment-index="1">
  <thead><tr><th>클러스터</th><th>바꾼 값</th><th>Launch, Terminate, Launch, Terminate (UTC)</th><th>완료</th></tr></thead>
  <tbody>
    <tr><td class="ak4-auto">akd-auto</td><td>advancedCompute.kubelet.maxPods: 64</td><td class="ak4-num">14:20:12, 14:20:30, 14:20:45, 14:21:00</td><td class="ak4-num">+98초</td></tr>
    <tr><td class="ak4-karp">akd-karp</td><td>al2023@v20261003 → al2023@v20261012</td><td class="ak4-num">14:20:10, 14:20:46, 14:20:57, 14:21:27</td><td class="ak4-num">+127초</td></tr>
  </tbody>
</table>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="2">
  <div class="callout callout-info"><strong class="text-info">maxPods 64, 실제는 56</strong><div class="ak4-muted">새 Auto Mode 노드의 capacity.pods는 56이었습니다. 실제값은 설정값, 인스턴스 IP 수, 110 중 가장 작은 값입니다.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">같은 EC2NodeClass는 함께 교체</strong><div class="ak4-muted">AMI를 바꾸자 같은 EC2NodeClass를 쓰는 spot NodePool 노드도 Drift로 교체됐습니다. 영향 범위는 NodeClass 단위로 봅니다.</div></div>
</div>
:::

:::notes
{timing: 1min}
[요약]
- 두 클러스터 모두 Launch, Terminate를 번갈아 하며 한 대씩 교체 (budget nodes 1)
- Karpenter 새 노드 AMI v20261012 확인. Auto Mode 새 노드 capacity.pods 56 (설정 64보다 작음)
- EC2NodeClass를 공유한 spot NodePool도 함께 교체됨

표의 시각을 보시면 두 클러스터 모두 띄우고, 지우고, 띄우고, 지우는 순서입니다. budget을 한 대로 둔 효과입니다. Drift는 graceful 경로라 필요하면 새 노드를 먼저 띄우고, budget 1이라 한 번에 한 대씩입니다. 그래서 이 데모에서는 Pod가 갈 곳이 없어지는 순간이 없었습니다. 만료는 이 순서를 보장하지 않는다는 점은 3부에서 본 그대로입니다.
{cue: pause}
두 가지를 짚겠습니다. 첫째, maxPods를 64로 넣었는데 실제 노드에는 56이 잡혔습니다. 설정값은 상한이고, 인스턴스가 가질 수 있는 IP 수가 더 작으면 그 값이 적용됩니다.
둘째, Karpenter 쪽에서 AMI를 바꾸자 같은 EC2NodeClass를 쓰던 spot 풀 노드까지 같이 교체됐습니다. 운영에서는 NodeClass를 바꿀 때 어떤 NodePool이 그 NodeClass를 쓰는지 먼저 확인하세요.
근거: RECORDINGS.md D3(이벤트 시각, AMI 이름, capacity.pods), FACTS.md 2.7(maxPods 실제값 규칙)
{cue: transition}
마지막 영상은 Spot 중단입니다.
:::

---
<!-- Slide 9: V4 영상 -->
@type: content
@fit: off
@title: V4: Spot 중단 경고를 받으면

## V4: Spot 중단 경고를 받으면

:::html
<style>
.ak4-video { width: 100%; max-height: 100%; aspect-ratio: 16 / 9; background: var(--bg-card); border-radius: var(--space-2); }
.ak4-full { flex: 1; min-height: 0; display: flex; flex-direction: column; gap: var(--space-1); }
.ak4-vbox { flex: 1; min-height: 0; container-type: size; }
.ak4-full .ak4-video { display: block; width: min(100cqw, calc(100cqh * 16 / 9)); height: auto; max-height: none; margin-inline: auto; }
.ak4-full .ak4-video-cap { color: var(--text-secondary); text-align: center; margin-top: 0; font-size: var(--fs-card); }
</style>
<div class="ak4-full">
<div class="ak4-vbox">
<video class="ak4-video" src="media/v4-spot.mp4" poster="media/v4-spot.jpg" aria-label="V4 영상: Spot 중단 처리, 실제 터미널 녹화 포함, 무음, 2분 30초" title="V4 영상: Spot 중단 처리, 실제 터미널 녹화 포함, 무음, 2분 30초" controls preload="metadata" muted playsinline tabindex="-1"></video>
</div>
<div class="ak4-video-cap">실제 터미널 녹화(2026-10-20)와 실측 결과 재구성, akd-karp만, 무음</div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- Auto Mode는 FIS EC2 액션을 지원하지 않으므로 Karpenter 클러스터에서만 실행
- AWS FIS로 Spot 중단 알림(2분 전)을 보내고, Karpenter가 SQS로 받아 처리하는 과정
- 경고 직후 노드를 비우고 대체 노드를 띄웠고, Pod 3개가 한 노드에 있어 약 30초 동안 Running 0개

Play를 누르고 장면마다 짧게 설명합니다. 영상은 무음입니다.
0:00 제목입니다. 이 데모는 Karpenter 클러스터에서만 돌렸다는 점을 먼저 말합니다.
0:07 알림 경로입니다. FIS가 EC2에 2분 전 중단 알림을 보내면 EventBridge 규칙(이번에는 Spot 중단과 rebalance 규칙)이 SQS로 넘기고, Karpenter가 이 큐를 읽습니다. 규칙은 모두 다섯 개입니다. Auto Mode에서는 이 경로를 AWS가 처리합니다.
0:34 실제 터미널 녹화 첫 부분입니다(0.6배속, 대기 구간 줄임). interruptionQueue 설정과 EventBridge 규칙을 확인하고 FIS 실험을 시작합니다.
0:55 녹화 둘째 부분입니다. 노드에 taint가 붙고 Pod가 빠지고 대체 NodeClaim이 뜨는 순서를 자막과 함께 봅니다.
{cue: pause}
1:24 타임라인입니다. 경고에서 기존 인스턴스 종료까지 6초라는 점을 짚어 주세요.
1:52 공백 장면입니다. Running 수가 3, 0, 3으로 바뀌는 구간이 약 30초입니다. 여기서 잠시 멈추고 이유(Pod 3개가 한 노드)를 말합니다.
2:12 정리 카드로 마칩니다.
근거: V4 영상 프로젝트 FACTS.md와 STORYBOARD.md, RECORDINGS.md D4
{cue: transition}
이 결과에서 가져갈 교훈을 정리하겠습니다.
:::

---
<!-- Slide 10: V4 결과 -->
@type: content
@title: V4 결과: Karpenter는 2분을 기다리지 않는다

## V4 결과: Karpenter는 2분을 기다리지 않는다

:::html
<style>
.ak4-tl { display: grid; grid-template-columns: auto 1fr; gap: var(--space-1) var(--space-3); font-size: var(--fs-card); word-break: keep-all; margin-bottom: var(--space-3); }
.ak4-tl .t { font-family: var(--font-mono); font-variant-numeric: tabular-nums; color: var(--text-secondary); }
.ak4-tl .bad { color: var(--danger); font-weight: var(--weight-bold); }
.ak4-tl .good { color: var(--success); font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.ak4-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak4-tl fragment fade-up" data-fragment-index="1">
  <span class="t">14:23:15 UTC</span><span>FIS 실험 시작 (Spot 인스턴스 1대, 2분 전 알림)</span>
  <span class="t">14:23:29 UTC</span><span class="bad">SpotInterrupted: Pod 3개 Evicted, 대체 NodeClaim 지명</span>
  <span class="t">14:23:35 UTC</span><span>Karpenter가 기존 인스턴스 종료 시작</span>
  <span class="t">14:24:00 UTC</span><span class="good">대체 노드(c7i-flex.xlarge spot) Ready, Pod 다시 Running</span>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="2">
  <div class="callout callout-warning"><strong class="text-warning">약 30초 동안 Running 0개</strong><div class="ak4-muted">replica 3개가 모두 중단된 노드 한 대에 있었습니다. 대체 노드가 Ready가 될 때까지 서비스가 비었습니다.</div></div>
  <div class="callout callout-info"><strong class="text-info">대책: 분산과 여유</strong><div class="ak4-muted">topology spread로 replica를 여러 노드와 zone에 나누고, 여러 인스턴스 유형을 허용해 대체 용량을 넓힙니다. PDB는 중단 drain에도 적용되지만 2분 뒤 회수는 막지 못합니다(이번 시험에는 PDB 없음).</div></div>
</div>
:::

:::notes
{timing: 1min}
[요약]
- 경고 직후(14:23:29) Pod를 비우고 대체 NodeClaim을 지명, 6초 뒤 기존 인스턴스 종료 시작
- 대체 노드 Ready 14:24:00. 그 사이 약 30초 동안 Running Pod 0개
- 원인은 replica가 한 노드에 몰린 배치. 분산과 넓은 인스턴스 선택으로 대비. PDB는 interruption drain에도 적용되지만 회수 자체는 못 막음(이번 시험에는 PDB 없음)

많은 분들이 "2분 여유가 있으니 그 사이에 옮기겠지"라고 생각하시는데, Karpenter는 경고를 받자마자 노드를 비웁니다. 기다리지 않고 바로 대체 노드를 요청하고 기존 노드는 6초 뒤에 직접 종료했습니다.
{cue: pause}
문제는 배치였습니다. 이 데모에서는 Pod 세 개가 모두 그 노드 하나에 있었기 때문에, 새 노드가 준비되기까지 30초 정도 Running Pod가 하나도 없었습니다.
그래서 Spot을 쓰는 워크로드는 replica를 여러 노드와 zone에 나누고, NodePool에 여러 인스턴스 유형을 허용해 대체 용량을 찾기 쉽게 해 두셔야 합니다. 이번 시험에는 PDB를 두지 않았습니다. Karpenter 문서에 따르면 interruption 같은 강제 방식은 NodePool budget으로 늦출 수 없지만, drain은 Eviction API를 쓰므로 PDB로 애플리케이션 중단 속도는 제한할 수 있습니다. 다만 2분 뒤 EC2가 인스턴스를 회수하는 것은 막지 못하니, 기본 대책은 분산입니다. Auto Mode에서는 이 처리를 AWS가 하지만, 배치 설계는 똑같이 팀의 몫입니다.
근거: RECORDINGS.md D4(이벤트 시각 원문), FACTS.md(Auto Mode FIS 미지원, interruption queue), https://karpenter.sh/docs/concepts/disruption/ (Automated Forceful Methods, Interruption)
{cue: transition}
이제 오늘 내용을 정리하겠습니다.
:::

---
<!-- Slide 11: 정리 -->
@type: content
@title: 6부: 오늘 가져갈 다섯 가지

## 6부: 오늘 가져갈 다섯 가지

:::html
<style>
.ak4-take { display: grid; grid-template-columns: repeat(5, 1fr); gap: var(--space-3); }
.ak4-take .card { word-break: keep-all; }
.ak4-take .n { color: var(--accent); font-weight: var(--weight-bold); font-size: var(--fs-card); }
.ak4-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak4-take" data-reveal="stagger">
  <div class="card"><span class="n">1. 판단은 같은 Karpenter</span><div class="ak4-muted">Auto Mode도 같은 조건에 같은 노드를 골랐습니다. 차이는 누가 운영하느냐입니다.</div></div>
  <div class="card"><span class="n">2. 1.37 기본값을 명시</span><div class="ak4-muted">비워 두면 Auto Mode는 Balanced, Karpenter는 WhenEmptyOrUnderutilized입니다.</div></div>
  <div class="card"><span class="n">3. 버전 순서</span><div class="ak4-muted">직접 운영은 Karpenter 1.15.x와 CRD를 먼저, 그다음 Kubernetes 1.37입니다.</div></div>
  <div class="card"><span class="n">4. 교체는 budget으로</span><div class="ak4-muted">AMI는 버전을 고정하고, budget과 PDB로 교체 속도를 정합니다.</div></div>
  <div class="card"><span class="n">5. 배치가 가용성</span><div class="ak4-muted">Spot 중단에 견디는 힘은 replica 분산에서 나옵니다.</div></div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- 노드를 고르는 판단은 같은 Karpenter, Auto Mode와 직접 운영의 차이는 운영 책임
- 1.37에서 정책을 비우면 클러스터마다 다른 기본값이 들어가므로 Git에 명시
- 직접 운영: Karpenter 1.15.x와 CRD 먼저, 그다음 1.37. AMI 고정, budget과 PDB로 교체 속도 조절, Spot은 replica 분산

다섯 가지로 정리하겠습니다. 첫째, Auto Mode든 직접 설치든 노드를 고르는 판단은 같은 Karpenter입니다. 무엇을 직접 운영할지가 선택의 기준입니다.
둘째, 1.37부터는 정책을 비워 두면 Auto Mode와 Karpenter에 다른 기본값이 들어갑니다. 명시해 두세요.
셋째, 직접 운영하신다면 Karpenter 1.15.x와 CRD를 먼저 올리고 그다음 Kubernetes 1.37로 갑니다.
{cue: pause}
넷째, 노드 교체는 언젠가 반드시 일어납니다. AMI를 고정하고 budget과 PDB로 속도를 정하면 예측 가능하게 만들 수 있습니다.
다섯째, Spot 중단에 견디는 힘은 결국 replica를 어떻게 나눠 두었느냐에서 나옵니다.
근거: 1~4부 슬라이드와 V1~V4 결과(RECORDINGS.md)
{cue: transition}
참고 자료와 질문으로 마치겠습니다.
:::

---
<!-- Slide 12: 참고 자료와 Q&A -->
@type: content
@title: 참고 자료와 Q&A

## 참고 자료와 Q&A

:::html
<style>
.ak4-next { display: grid; grid-template-columns: 1fr 1.3fr; gap: var(--space-4); align-items: start; }
.ak4-col { display: flex; flex-direction: column; gap: var(--space-3); }
.ak4-label { font-size: var(--fs-card); font-weight: var(--weight-bold); color: var(--text-secondary); }
.ak4-ref { margin: 0; padding-left: var(--space-4); font-size: var(--fs-card); line-height: 1.7; }
.ak4-ref a, .ak4-col a { color: var(--accent); }
.text-accent { color: var(--accent); font-weight: var(--weight-bold); }
.text-info { color: var(--info); font-weight: var(--weight-bold); }
.ak4-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak4-next">
  <div class="ak4-col">
    <div class="ak4-label">다음 단계</div>
    <div class="callout callout-info fragment fade-up" data-fragment-index="1"><strong class="text-info">관측성과 리소스 최적화까지</strong><div class="ak4-muted"><a href="../eks-observability-ops/index.html" target="_blank" rel="noopener">EKS Auto Mode &amp; Karpenter 운영</a>: 노드 라이프사이클 모니터링, Grafana 상관분석, VPA와 KEDA</div></div>
    <div class="callout callout-info fragment fade-up" data-fragment-index="2"><strong class="text-info">Auto Mode 운영 가이드</strong><div class="ak4-muted"><a href="https://docs.atomai.click/kubernetes-docs/ko/eks-auto-mode/" target="_blank" rel="noopener">kubernetes-docs: EKS Auto Mode 운영 가이드</a>: 시작하기, NodePool, 스케일링, Spot, 운영, 비용, 수명, 워크로드, 마이그레이션 9개 장</div></div>
    <div class="callout callout-info fragment fade-up" data-fragment-index="3"><strong class="text-info">데모 스크립트</strong><div class="ak4-muted">오늘 영상의 클러스터 구성, NodePool, 녹화 driver, 정리 스크립트는 요청 시 공유합니다.</div></div>
    <div class="callout callout-info fragment fade-up" data-fragment-index="4"><strong class="text-accent">Q&amp;A</strong><div class="ak4-muted">버전과 기본값은 2026-10-20 기준입니다. 적용 전에 최신 문서를 확인하세요.</div></div>
  </div>
  <div class="ak4-col">
    <div class="ak4-label">공식 문서</div>
    <ul class="ak4-ref">
      <li><a href="https://docs.aws.amazon.com/eks/latest/userguide/automode.html" target="_blank" rel="noopener">EKS Auto Mode</a></li>
      <li><a href="https://docs.aws.amazon.com/eks/latest/userguide/create-node-class.html" target="_blank" rel="noopener">Auto Mode NodeClass</a></li>
      <li><a href="https://docs.aws.amazon.com/eks/latest/userguide/create-node-pool.html" target="_blank" rel="noopener">Auto Mode NodePool</a></li>
      <li><a href="https://docs.aws.amazon.com/eks/latest/userguide/auto-get-logs.html" target="_blank" rel="noopener">Auto Mode 노드 로그 수집</a></li>
      <li><a href="https://docs.aws.amazon.com/eks/latest/userguide/migrate-auto.html" target="_blank" rel="noopener">Auto Mode로 마이그레이션</a></li>
      <li><a href="https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html" target="_blank" rel="noopener">EKS Kubernetes 버전</a></li>
      <li><a href="https://karpenter.sh/docs/concepts/disruption/" target="_blank" rel="noopener">Karpenter Disruption</a></li>
      <li><a href="https://karpenter.sh/docs/upgrading/compatibility/" target="_blank" rel="noopener">Karpenter 호환성</a></li>
      <li><a href="https://github.com/aws/karpenter-provider-aws/releases/tag/v1.15.0" target="_blank" rel="noopener">Karpenter v1.15.0 릴리스</a></li>
    </ul>
  </div>
</div>
:::

:::notes
{timing: 3.5min}
[요약]
- 안내 1분, 이어서 Q&A 2.5분
- 관측성, VPA, KEDA는 "EKS Auto Mode & Karpenter 운영" 덱
- Auto Mode 운영 가이드(kubernetes-docs, 9개 장): 4부 내용의 원문과 예제
- 공식 문서 9개: Auto Mode, NodeClass, NodePool, 노드 로그 수집, 마이그레이션, EKS 버전, Karpenter Disruption, 호환성, v1.15.0 릴리스

오늘은 노드 자동화 자체에 집중했습니다. 노드 라이프사이클 모니터링, 로그와 메트릭 상관분석, VPA와 KEDA를 이용한 리소스 최적화는 운영 덱에서 이어서 보실 수 있습니다. 4부에서 다룬 Auto Mode 설정, Spot, 진단, 비용, 마이그레이션의 원문과 전체 예제는 kubernetes-docs의 Auto Mode 운영 가이드 9개 장에 있습니다.
데모 스크립트는 요청하시면 공유해 드립니다. 클러스터 두 개를 만들고 지우는 정리 스크립트까지 들어 있으니, 직접 돌려 보신 뒤에는 꼭 정리해 비용을 멈추세요.
{cue: pause}
버전과 기본값은 오늘 날짜 기준입니다. 특히 Auto Mode 기본값과 Karpenter 호환성 표는 자주 바뀌니 적용 전에 오른쪽 문서를 다시 확인해 주세요.
{cue: question}
이제 질문 받겠습니다. 2분 30초 정도 받고, 남은 질문은 세션 뒤에 따로 받겠습니다.
근거: FACTS.md(문서 URL), 데모 저장소 teardown.sh
:::

---
<!-- Slide 13: Thank You -->
@type: thankyou
@toc: toc.html
@message: EKS Auto Mode와 Karpenter, 감사합니다

# Thank You

:::notes
{timing: 0.5min}
[요약]
- 세션 마무리

오늘 세션 들어 주셔서 감사합니다. 오늘 보신 영상의 숫자는 모두 한 번 실행한 결과이니, 여러분 환경에서 같은 방식으로 직접 확인해 보시길 권합니다.
:::
