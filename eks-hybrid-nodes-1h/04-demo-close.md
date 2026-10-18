---
remarp: true
block: 04-demo-close
---

---
<!-- Slide 1: 5부 구분 (Section) -->
@type: section

# 5부: 데모 영상

실제로 돌려 본 결과: Gateway 전환, 버스팅, ALB, GPU

:::notes
{timing: 0.5min}
[요약]
- 5부의 질문: 1~4부에서 설명한 동작이 실제 클러스터에서도 그대로 일어나는가
- 영상 4개: V1 Gateway 리더 전환, V2 버스팅과 축소, V3 ALB ip 타깃과 역방향, V4 hybrid GPU 추론. 끝에 Istio 공존 결과 한 장
- 영상 V1~V4는 무음이고, 실제 터미널 녹화(2026-10-18)와 재구성한 설명 장면으로 구성됩니다. 측정 회차마다 날짜를 붙여 숫자를 구분합니다.

5부는 데모 영상입니다. 실제 터미널 녹화(2026-10-18)와 재구성한 설명 장면으로 영상을 만들었고, 네트워크 상황과 상관없이 같은 결과를 보여 드리려고 라이브 대신 영상을 씁니다.
영상은 네 개이고, 측정 회차가 여러 번이면 날짜를 붙여 숫자를 섞지 않았습니다.
{cue: transition}
먼저 어떤 환경에서 돌렸는지부터 말씀드리겠습니다.
:::

---
<!-- Slide 2: 시뮬레이션 환경 -->
@type: content
@title: 온프렘은 시뮬레이션: EC2 호스트와 TGW

## 온프렘은 시뮬레이션: EC2 호스트와 TGW

:::html
<style>
.hn5-arch { display: grid; grid-template-columns: 1fr auto 1fr; gap: var(--space-3); align-items: stretch; margin-bottom: var(--space-3); }
.hn5-vpc { border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-3); background: var(--bg-card); }
.hn5-vpc h4 { margin: 0 0 var(--space-2); font-size: var(--fs-card); color: var(--accent); }
.hn5-vpc ul { margin: 0; padding-left: var(--space-4); font-size: var(--fs-card); color: var(--text-secondary); word-break: keep-all; }
.hn5-tgw { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: var(--space-2); font-weight: var(--weight-bold); color: var(--accent); }
.hn5-tgw span { writing-mode: vertical-rl; letter-spacing: .12em; }
.hn5-ico { width: 40px; height: 40px; vertical-align: middle; margin-right: var(--space-2); }
.hn5-lico { width: 32px; height: 32px; vertical-align: middle; margin-right: var(--space-1); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="hn5-arch fragment fade-up" data-fragment-index="1">
  <div class="hn5-vpc"><h4><img class="hn5-ico" src="./common/aws-icons/services/Arch_Amazon-Virtual-Private-Cloud_48.svg" alt="Amazon VPC">클라우드 VPC 10.0.0.0/16</h4><ul>
    <li><img class="hn5-lico" src="./common/aws-icons/services/Arch_Amazon-Elastic-Kubernetes-Service_48.svg" alt="Amazon EKS">EKS 1.36, system 노드</li>
    <li><img class="hn5-lico" src="./common/aws-icons/services/Arch_Amazon-EC2_48.svg" alt="Amazon EC2">Gateway 노드 2대 (2개 AZ)</li>
    <li>Karpenter burst 노드 (m6i, m7i)</li>
    <li>클라우드 노드는 VPC CNI</li></ul></div>
  <div class="hn5-tgw"><img class="hn5-ico" src="./common/aws-icons/services/Arch_AWS-Transit-Gateway_48.svg" alt="AWS Transit Gateway" style="margin-right:0"><span>Transit Gateway</span></div>
  <div class="hn5-vpc"><h4><img class="hn5-ico" src="./common/aws-icons/services/Arch_Amazon-Virtual-Private-Cloud_48.svg" alt="Amazon VPC">시뮬레이션 온프렘 VPC 172.18.0.0/16</h4><ul>
    <li><img class="hn5-lico" src="./common/aws-icons/services/Arch_Amazon-EC2_48.svg" alt="Amazon EC2">hybrid 노드 호스트 2대 (EC2, 각 4 vCPU)</li>
    <li>GPU 호스트 1대 (g6.xlarge, V4 때만)</li>
    <li>Pod CIDR 172.17.0.0/16 (Cilium)</li>
    <li>실제 구성에서는 DX 또는 VPN 자리</li></ul></div>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="2">
  <div class="callout callout-danger"><strong class="text-danger">프로덕션 지원 구성이 아님</strong><div class="on-surface-muted">EC2를 hybrid 노드로 쓰는 것은 지원되지 않습니다. 동작 확인과 수치 확보가 목적입니다.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">수치는 이 환경의 값</strong><div class="on-surface-muted">회차가 적은 측정입니다. 실제 온프렘 서버와 회선에서는 다시 재야 합니다.</div></div>
  <div class="callout callout-info"><strong class="text-info">보안 기준은 유지</strong><div class="on-surface-muted">인터넷 개방 ingress 없음, 공인 IP 없음, LB는 internal만</div></div>
</div>
:::

:::notes
{timing: 1min}
[요약]
- 온프렘 서버와 회선 대신, 두 번째 VPC를 Transit Gateway로 연결하고 그 안의 EC2를 온프렘 호스트로 사용
- EC2를 hybrid 노드로 쓰는 것은 프로덕션 지원 구성이 아님. 데모 목적은 동작 확인과 수치 확보
- 모든 수치는 이 환경에서 적은 회차로 잰 값이라, 실제 온프렘에서는 다시 확인해야 함

영상을 보기 전에 환경부터 솔직하게 말씀드리겠습니다. 온프렘 서버와 VPN이 없어서, 두 번째 VPC를 Transit Gateway로 연결하고 그 안의 EC2를 온프렘 호스트처럼 썼습니다. 실제 구성이라면 이 자리에 Direct Connect나 Site-to-Site VPN이 들어갑니다.
{cue: pause}
EC2를 hybrid 노드로 쓰는 것은 AWS가 지원하는 프로덕션 구성이 아닙니다. 그리고 영상의 숫자는 모두 이 환경에서 한 번에서 몇 번 정도 잰 값입니다. 경향을 보시는 용도로 쓰시고, 실제 도입 전에는 고객 환경에서 다시 측정하셔야 합니다.
보안 기준은 지켰습니다. 인터넷에 열린 ingress가 없고, 인스턴스에 공인 IP가 없고, 로드 밸런서는 internal만 썼습니다.
근거: Deep Dive 5부 "온프렘을 시뮬레이션한 환경에서 돌렸다"(구성과 경고 카드), 데모 저장소 RUNBOOK.md 머리말, AWS docs hybrid-nodes-overview (EC2 실행 미지원)
{cue: transition}
첫 번째 영상은 Gateway 리더 전환입니다.
:::

---
<!-- Slide 3: V1 영상 -->
@type: content
@fit: off
@title: V1: Gateway 리더가 죽으면

## V1: Gateway 리더가 죽으면

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
<video class="hn-video" src="media/v1-gateway-failover.mp4" poster="media/v1-gateway-failover.jpg" aria-label="V1 영상: Gateway 리더 전환, 실제 터미널 녹화 포함, 무음, 2분 58초" title="V1 영상: Gateway 리더 전환, 실제 터미널 녹화 포함, 무음, 2분 58초" controls preload="metadata" muted playsinline tabindex="-1"></video>
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
{timing: 3.5min}
[요약]
- 영상 2분 58초. Gateway 리더 Pod를 지우고, standby가 Lease를 넘겨받아 VPC 라우트를 자기 ENI로 바꾸는 과정
- 녹화 회차(2026-10-18): Lease 인계 5초, 1초 간격 요청 60개 중 2개 실패
- 일시정지 지점은 한 곳: 1:31 녹화의 결과 블록

Play를 누르고 장면마다 짧게 설명합니다. 영상은 무음입니다.
0:00 제목과 환경 구성도입니다. 클라우드 VPC에 Gateway 2대가 있고, Transit Gateway 건너편이 시뮬레이션 온프렘, 그 안에 hybrid Pod CIDR이 있습니다.
0:24 실제 터미널 녹화입니다. Gateway Pod 2개, Lease를 가진 리더, 그리고 VPC route table에서 hybrid Pod CIDR이 리더 Gateway의 ENI를 가리키는 것을 보여 줍니다. 녹화는 0.5배속이고 출력 없는 대기는 줄였습니다.
0:44 평상시 경로입니다. 클라우드에서 보낸 요청이 리더 Gateway A를 지나 온프렘 Pod에 닿고, 1초 간격 요청이 모두 성공합니다.
1:06 다시 녹화입니다. 리더 Pod를 지우는 스크립트를 실행하고, 몇 초 뒤 새 리더가 Lease를 잡습니다. 1:31쯤 결과 블록이 나오면 잠시 멈추고 읽어 드리세요. 인계 5초, 실패 60개 중 2개, 라우트 ENI가 새 리더 ENI로 바뀌었다는 줄입니다.
{cue: pause}
1:32 구성도로 돌아와 리더가 사라진 순간을 봅니다. 그사이 요청 2개가 실패합니다. 격자에서 실패 칸의 위치는 실측 위치가 아니라, 개수와 간격(첫 실패부터 마지막 실패까지 5초)에 맞춘 배치입니다.
1:48 T0에서 5초 뒤 Gateway B가 Lease를 넘겨받고, VPC 라우트가 B의 ENI로 바뀌면서 요청이 다시 성공합니다. 이 라우트 교체를 사람이 하지 않는다는 점이 핵심입니다.
2:08 녹화로 확인합니다. Lease HOLDER가 새 노드로 바뀌었고, Deployment가 Pod 하나를 다시 띄워 2개가 Running입니다. HOLDER 값은 Pod 이름이 아니라 노드이름_uuid 형식입니다.
2:28 결과 카드입니다. 멈추지 말고 끝까지 둔 뒤 다음 슬라이드에서 숫자를 정리합니다.
근거: V1 영상 프로젝트 FACTS.md와 STORYBOARD.md(장면 시간), RECORDINGS.md R1(녹화 회차 값)
{cue: transition}
숫자를 회차별로 정리하겠습니다.
:::

---
<!-- Slide 4: V1 결과 -->
@type: content
@title: V1 결과: 전환은 3~5초, 실패는 1~2건

## V1 결과: 전환은 3~5초, 실패는 1~2건

:::html
<style>
.hn5-table { width: 100%; font-size: var(--fs-card); word-break: keep-all; }
.hn5-table td.hn5-num { font-variant-numeric: tabular-nums; font-weight: var(--weight-bold); }
.hn5-rec td { color: var(--accent); }
.data-table th { text-transform: none; letter-spacing: normal; font-size: var(--fs-card); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<table class="data-table hn5-table fragment fade-up" data-fragment-index="1">
  <thead><tr><th>측정 회차</th><th>Lease 인계</th><th>실패한 요청 (1초 간격)</th><th>VPC 라우트</th></tr></thead>
  <tbody>
    <tr><td>2026-10-15, 1회차</td><td class="hn5-num">3초</td><td class="hn5-num">60개 중 1개</td><td>새 리더 ENI로 이동</td></tr>
    <tr><td>2026-10-15, 2회차</td><td class="hn5-num">5초</td><td class="hn5-num">60개 중 1개</td><td>새 리더 ENI로 이동</td></tr>
    <tr><td>2026-10-15, 3회차 (최소 권한 IAM)</td><td class="hn5-num">5초</td><td class="hn5-num">45개 중 2개</td><td>새 리더 ENI로 이동</td></tr>
    <tr class="hn5-rec"><td>2026-10-18, 녹화 회차 (영상)</td><td class="hn5-num">5초</td><td class="hn5-num">60개 중 2개</td><td>새 리더 ENI로 이동</td></tr>
  </tbody>
</table>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="2">
  <div class="callout callout-info"><strong class="text-info">AWS 문서 예상 3~5초</strong><div class="on-surface-muted">측정값이 그 범위 안이었습니다. 보장값은 아닙니다.</div></div>
  <div class="callout callout-success"><strong class="text-success">라우트 교체는 자동</strong><div class="on-surface-muted">새 리더가 VPC route를 자기 ENI로 바꿉니다. 권한을 Gateway route table로 좁혀도 동작했습니다.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">짧은 공백은 생긴다</strong><div class="on-surface-muted">재시도 없는 1초 간격 요청에서 1~2건이 실패했습니다. 앱의 재시도 설정을 확인하세요.</div></div>
</div>
:::

:::notes
{timing: 1min}
[요약]
- 2026-10-15 세 번: Lease 인계 3초, 5초, 5초. 실패 60개 중 1개, 60개 중 1개, 45개 중 2개(3회차는 최소 권한 IAM)
- 2026-10-18 녹화 회차: 5초, 60개 중 2개. 네 번 모두 라우트가 새 리더 ENI로 이동
- AWS 문서의 예상 전환 3~5초와 맞지만 보장값은 아님

마지막 줄은 방금 영상의 녹화 회차이니, 영상에 없던 위 세 줄만 보겠습니다. 10월 15일에 세 번 잰 값으로 인계 3초에서 5초, 실패는 많아야 2개였습니다. AWS 문서의 예상 전환 3~5초와 맞지만 보장값은 아닙니다.
{cue: pause}
3회차는 Gateway의 IAM 권한을 Gateway route table로 좁혔는데도 전환이 동작했습니다. 재시도하지 않는 클라이언트는 짧은 공백을 보니, 이 경로를 쓰는 앱의 재시도 설정을 확인해 두세요.
근거: V1 영상 프로젝트 FACTS.md(이전 3회와 녹화 회차를 구분한 표), Deep Dive 5부 "데모 1: 리더가 바뀌어도 끊김은 3~5초", AWS docs hybrid-nodes-gateway-overview (예상 전환 3~5초)
{cue: transition}
두 번째 영상은 버스팅입니다. 4부에서 예고한 세 방식의 비교 결과가 여기 나옵니다.
:::

---
<!-- Slide 5: V2 영상 -->
@type: content
@fit: off
@title: V2: 넘칠 때와 줄일 때

## V2: 넘칠 때와 줄일 때

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
<video class="hn-video" src="media/v2-bursting.mp4" poster="media/v2-bursting.jpg" aria-label="V2 영상: 버스팅과 축소, 실제 터미널 녹화 포함, 무음, 3분 36초" title="V2 영상: 버스팅과 축소, 실제 터미널 녹화 포함, 무음, 3분 36초" controls preload="metadata" muted playsinline tabindex="-1"></video>
</div>
<div class="hn-video-cap">실측 결과 재구성 (2026-10 시뮬레이션 환경), 실제 터미널 녹화 포함, 무음</div>
</div>
:::

:::notes
{timing: 4min}
[요약]
- 영상 3분 36초. 앞부분은 2026-10-18 녹화 회차(시나리오 B, Pod 요청 910m), 뒷부분은 2026-10-15 A, B, C 비교 실행(930m)
- 녹화 회차: 15개로 늘리면 35초에 모두 Ready(hybrid 8, burst 7), 10개에서 hybrid 8, cloud 2, 3개에서 모두 hybrid
- 일시정지 지점은 한 곳: 2:08 A, B, C 비교 장면

두 실행이 섞여 나오니, 장면마다 어느 회차인지 짚어 주세요.
0:00 제목과 메시지입니다. C가 조금 빨랐다는 부분은 1회 측정 결과입니다.
0:06 먼저 ReplicaSet이 줄일 때 어떤 Pod를 먼저 지우는지 보여 줍니다. cost가 낮은 Pod, 복제본이 많은 노드의 Pod, 최근에 생긴 Pod 순서이고, Pod가 온프렘에 있는지 클라우드에 있는지는 보지 않습니다. 이어서 실험 환경(hybrid 호스트 2대, 각 4 vCPU, Pod 8개에서 포화, burst NodePool 한도 32 vCPU)과 시나리오 A, B, C를 소개합니다.
0:30 녹화 회차 기준 그림입니다. 3개에서 15개로 늘리면 hybrid에 8개가 들어가고 7개가 Pending, Karpenter가 NodeClaim 3개를 만들어 burst Pod 7개를 받습니다. 15개가 Ready가 되기까지 35초였습니다.
0:56 실제 터미널 녹화, 0.5배속입니다. 3개 모두 hybrid에서 시작해, 15개로 늘리자 Pending과 NodeClaim이 보이고 곧 15개가 Running이 됩니다.
1:32 이어지는 녹화입니다. 10개로 줄이면 hybrid 8개는 그대로이고 클라우드에 2개가 남습니다. 3개로 줄이면 남은 3개가 모두 hybrid 노드입니다. Kyverno가 붙인 cost 덕분입니다.
{cue: pause}
2:08 여기서 10월 15일 비교 실행으로 넘어갑니다. 잠시 멈추고 말씀하세요. 정책이 없는 A는 10개로 줄일 때 hybrid Pod 2개가 먼저 빠집니다. B와 C는 hybrid 8개를 지킵니다. 이 장면에서 노드별 Pod 위치는 예시이고, Pod 수와 EC2 대수만 실측입니다.
2:54 비교표입니다. 다음 슬라이드에서 같은 표를 다시 보니 멈추지 않습니다.
3:14 메시지 카드입니다. pod-deletion-cost는 best-effort이고, 시나리오마다 한 번씩 잰 값이라는 주의가 함께 나옵니다.
근거: V2 영상 프로젝트 FACTS.md(출처 1 비교 실행, 출처 2 녹화 회차를 분리한 표), STORYBOARD.md(장면 시간)
{cue: transition}
비교 실행의 숫자를 정리하겠습니다.
:::

---
<!-- Slide 6: V2 결과 -->
@type: content
@title: V2 결과: 온프렘 Pod를 지킨 것은 B와 C

## V2 결과: 온프렘 Pod를 지킨 것은 B와 C

:::html
<style>
.hn5-table { width: 100%; font-size: var(--fs-card); word-break: keep-all; }
.hn5-table td.hn5-num { font-variant-numeric: tabular-nums; font-weight: var(--weight-bold); }
.hn5-runlabel { font-size: var(--fs-card); color: var(--text-secondary); margin-bottom: var(--space-1); }
.data-table th { text-transform: none; letter-spacing: normal; font-size: var(--fs-card); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="fragment fade-up" data-fragment-index="1">
  <div class="hn5-runlabel">2026-10-15 비교 실행: 시나리오별 1회, Pod 요청 930m, 3 → 15 → 12 → 10 → 3</div>
  <table class="data-table hn5-table">
    <thead><tr><th>시나리오</th><th>10개일 때 hybrid / cloud</th><th>10개일 때 EC2</th><th>최종 3개 hybrid / cloud</th><th>burst 정리</th></tr></thead>
    <tbody>
      <tr><td>A 정책 없음</td><td class="hn5-num">6 / 4</td><td class="hn5-num">3대</td><td class="hn5-num">2 / 1</td><td class="hn5-num">123초</td></tr>
      <tr><td>B Kyverno</td><td class="hn5-num">8 / 2</td><td class="hn5-num">4대</td><td class="hn5-num">3 / 0</td><td class="hn5-num">118초</td></tr>
      <tr><td>C Kyverno + Karpenter</td><td class="hn5-num">8 / 2</td><td class="hn5-num">3대</td><td class="hn5-num">3 / 0</td><td class="hn5-num">87초</td></tr>
    </tbody>
  </table>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="2">
  <div class="callout callout-warning"><strong class="text-warning">A는 온프렘을 먼저 지움</strong><div class="on-surface-muted">기본 규칙은 위치를 보지 않습니다.</div></div>
  <div class="callout callout-success"><strong class="text-success">C의 이득은 작다</strong><div class="on-surface-muted">EC2 4대에서 3대, 정리 118초에서 87초. 1회 측정이라 반복 측정이 필요합니다.</div></div>
  <div class="callout callout-info"><strong class="text-info">녹화 회차 (2026-10-18, B, 910m)</strong><div class="on-surface-muted">15개 Ready 35초 (hybrid 8, burst 7), 10개에서 8 / 2, 3개는 모두 hybrid</div></div>
</div>
:::

:::notes
{timing: 1min}
[요약]
- 2026-10-15 비교(시나리오별 1회, 930m): A는 10개에서 6 / 4, 최종 2 / 1. B와 C는 10개에서 8 / 2, 최종 3 / 0
- C는 B보다 EC2 4대에서 3대, burst 정리 118초에서 87초. 차이가 작고 1회 측정이라 단정하지 않음
- 영상의 녹화 회차(2026-10-18, B, 910m)는 별도 실행. 같은 경향(온프렘 8개 유지, 최종 모두 hybrid)

표는 영상의 비교표와 같습니다. 영상에서 짧게 넘긴 차이만 짚겠습니다. C는 B보다 EC2가 한 대 적고 정리가 30초 정도 빨랐지만, 한 번씩 잰 값이라 이 차이로 결정하지는 마세요. 핵심은 Kyverno 정책 하나로도 온프렘 Pod를 지켰다는 것이고, 이것은 best-effort 선호입니다.
{cue: pause}
오른쪽 아래 카드는 영상 앞부분의 녹화 회차입니다. 날짜와 Pod 요청 값이 다른 별도 실행이라 표에 섞지 않았고, 녹화 회차의 burst 노드 소멸 시점(약 104초)은 기준이 달라 표와 비교하지 않습니다.
근거: V2 영상 프로젝트 FACTS.md(출처 1: results/compare-20261015-1239.md, 출처 2: RECORDINGS.md R2), Deep Dive 5부 "데모 2 결과: 온프렘 Pod를 지킨 것은 B와 C"
{cue: transition}
세 번째 영상은 ALB가 hybrid Pod를 직접 타깃으로 잡는 경우와, 반대로 온프렘에서 들어오는 경우입니다.
:::

---
<!-- Slide 7: V3 영상 -->
@type: content
@fit: off
@title: V3: ALB ip 타깃과 온프렘에서 들어오는 길

## V3: ALB ip 타깃과 온프렘에서 들어오는 길

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
<video class="hn-video" src="media/v3-alb-reverse.mp4" poster="media/v3-alb-reverse.jpg" aria-label="V3 영상: ALB ip 타깃과 온프렘에서 들어오는 역방향, 실제 터미널 녹화 포함, 무음, 3분 12초" title="V3 영상: ALB ip 타깃과 온프렘에서 들어오는 역방향, 실제 터미널 녹화 포함, 무음, 3분 12초" controls preload="metadata" muted playsinline tabindex="-1"></video>
</div>
<div class="hn-video-cap">실측 결과 재구성 (2026-10 시뮬레이션 환경), 실제 터미널 녹화 포함, 무음</div>
</div>
:::

:::notes
{timing: 3.5min}
[요약]
- 영상 3분 12초. 정방향: hybrid Pod를 다시 띄워 IP가 바뀌어도 Load Balancer Controller가 타깃을 따라감. 역방향: 온프렘에서 internal ALB로 들어오는 세 가지 경로
- 녹화 회차(2026-10-18 06:36 UTC 시작): 재시작 50초 뒤 새 IP만 healthy, 부하 174건 ERR 0, 온프렘 NodePort는 FAIL
- 일시정지 지점은 한 곳: 1:20 폴링 격자

이 영상에도 두 회차가 나옵니다. 화면의 "녹화 회차"와 "02:11 측정"(UTC) 표시를 읽어 주세요.
0:00 제목과 메시지입니다.
0:06 정방향 경로도입니다. ALB가 hybrid Pod IP를 타깃으로 잡고, 타깃 등록과 해제는 LBC가, 경로는 Gateway가 줍니다.
0:28 녹화입니다. ALB 이름, Pod 2개 Running, 두 타깃 healthy를 확인하고 클라우드 Pod에서 ALB로 0.5초 간격 부하를 시작합니다.
0:48 rollout restart로 Pod를 새로 띄웁니다. 약 6초 간격 폴링에서 새 IP가 initial, healthy가 되고 옛 IP가 draining, 해제되는 과정이 보입니다. 50초 시점에 새 IP 두 개만 healthy로 남습니다.
{cue: pause}
1:20 같은 폴링 결과를 격자로 정리한 장면입니다. 여기서 멈추고, 등록과 해제가 사람 손 없이 일어났고 그동안 부하 174건 중 오류가 0건이었다고 말씀하세요.
1:38 녹화로 rollout 완료를 봅니다. 옛 Pod 한 줄의 Failed는 종료 중인 상태이고 몇 초 뒤 사라집니다.
1:56 02:11 UTC 측정 회차입니다. Gateway 리더를 지웠을 때 인계 4초, 191건 중 1건 실패였고, 실패 칸의 위치는 예시입니다.
2:11 역방향 세 경로입니다. internal ALB로 클라우드 Pod, 같은 ALB로 hybrid Pod(hairpin), hybrid 노드의 NodePort로 클라우드 Pod이고, 마지막만 실패했습니다. 이유는 다음 슬라이드에서 설명합니다.
2:35 녹화로 온프렘 호스트에서 직접 호출합니다. /cloud 3번, /hybrid 3번 성공, NodePort는 3번 모두 FAIL입니다.
2:54 메시지와 회차별 결과 카드입니다.
근거: V3 영상 프로젝트 FACTS.md(실행 1: 02:11 UTC 측정, 실행 2: 녹화 회차), STORYBOARD.md(장면 시간)
{cue: transition}
두 회차의 결과를 방향별로 나눠 보겠습니다.
:::

---
<!-- Slide 8: V3 결과 -->
@type: content
@title: V3 결과: 타깃은 LBC가, 온프렘 진입은 internal LB로

## V3 결과: 타깃은 LBC가, 온프렘 진입은 internal LB로

:::html
<style>
.hn5-table { width: 100%; font-size: var(--fs-card); word-break: keep-all; }
.hn5-table td.hn5-num { font-variant-numeric: tabular-nums; font-weight: var(--weight-bold); }
.hn5-table td.hn5-dir { color: var(--accent); font-weight: var(--weight-bold); vertical-align: middle; border-right: 1px solid var(--border); }
.data-table th { text-transform: none; letter-spacing: normal; font-size: var(--fs-card); }
.hn5-fail { color: var(--danger); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<table class="data-table hn5-table fragment fade-up" data-fragment-index="1">
  <thead><tr><th>방향</th><th>항목</th><th>2026-10-18 02:11 UTC 측정</th><th>2026-10-18 녹화 회차 (영상)</th></tr></thead>
  <tbody>
    <tr><td class="hn5-dir" rowspan="2">정방향<br>VPC에서</td><td>rollout restart 후 새 IP만 healthy</td><td class="hn5-num">54초, 276건 중 실패 0</td><td class="hn5-num">50초, 174건 중 실패 0</td></tr>
    <tr><td>Gateway 리더 전환 중</td><td class="hn5-num">인계 4초, 191건 중 실패 1</td><td>측정 안 함</td></tr>
    <tr><td class="hn5-dir" rowspan="3">역방향<br>온프렘에서</td><td>internal ALB → 클라우드 Pod</td><td class="hn5-num">20 / 20</td><td class="hn5-num">3 / 3</td></tr>
    <tr><td>internal ALB → hybrid Pod (hairpin)</td><td class="hn5-num">20 / 20</td><td class="hn5-num">3 / 3</td></tr>
    <tr><td>hybrid NodePort → 클라우드 Pod</td><td class="hn5-num hn5-fail">실패</td><td class="hn5-num hn5-fail">3회 모두 실패</td></tr>
  </tbody>
</table>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="2">
  <div class="callout callout-info"><strong class="text-info">타깃은 LBC가 관리</strong><div class="on-surface-muted">IP가 바뀌어도 등록과 해제가 자동. Gateway는 경로만 줍니다.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">NodePort 실패의 이유</strong><div class="on-surface-muted">노드 IP로 SNAT된 뒤 underlay로 가는데, 클라우드 노드 SG가 온프렘 대역에 443만 허용했습니다.</div></div>
  <div class="callout callout-info"><strong class="text-info">온프렘 진입은 internal LB</strong><div class="on-surface-muted">Gateway를 거치지 않는 일반 VPC 경로. 실환경은 DNS 준비가 필요합니다.</div></div>
</div>
:::

:::notes
{timing: 1min}
[요약]
- 정방향: 새 IP만 healthy까지 02:11 UTC 측정 54초(276건 실패 0), 녹화 회차 50초(174건 실패 0). 리더 전환은 02:11 UTC 측정에서 인계 4초, 191건 중 1건 실패
- 역방향: internal ALB로 클라우드 Pod와 hybrid Pod 모두 성공(02:11 UTC 측정 20 / 20, 녹화 3 / 3). hybrid Pod 쪽은 DX를 두 번 지나는 hairpin
- NodePort 경로 실패는 이 환경의 SG 설정(온프렘 대역에 443만 허용) 때문. 온프렘 진입은 internal LB가 기본

오른쪽 두 열은 같은 날의 다른 회차이고, 정방향 54초와 실패 0은 02:11 UTC 측정, 50초는 녹화 회차입니다. 숫자는 대부분 영상에서 보셨으니 해석과 권장만 말씀드리겠습니다.
{cue: pause}
NodePort 실패는 영상에서 본 대로 노드 IP로 SNAT된 뒤 클라우드 노드 SG가 온프렘 대역에 443만 허용했기 때문입니다. 제품 한계라기보다 SG 설계 문제이고, 권장은 온프렘 진입을 internal LB로 받는 것입니다. hairpin은 동작하지만 DX를 두 번 지납니다. 실환경에서는 온프렘 DNS가 internal ALB 이름을 풀도록 Route 53 Resolver inbound endpoint가 필요합니다.
근거: V3 영상 프로젝트 FACTS.md(실행 1 results/lb-20261018-0211.json, 02:11 UTC, 실행 2 RECORDINGS.md R3), Deep Dive 5부 "ALB ip 타깃", "반대 방향: 온프렘에서 LB로 들어오면", 데모 저장소 RUNBOOK.md 5절
{cue: transition}
마지막 영상은 온프렘 GPU입니다.
:::

---
<!-- Slide 9: V4 영상과 결과 -->
@type: content
@title: V4: 온프렘 GPU 추론을 클라우드에서 호출

## V4: 온프렘 GPU 추론을 클라우드에서 호출

:::html
<style>
.hn-video { width: 100%; max-height: 100%; aspect-ratio: 16 / 9; background: var(--bg-card); border-radius: var(--space-2); }
.hn-video-cap { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); }
.hn5-v4 { display: grid; grid-template-columns: 43rem minmax(0, 1fr); gap: var(--space-4); align-items: start; }
.hn5-res { display: flex; flex-direction: column; gap: var(--space-2); }
.hn5-res .callout { padding: var(--space-2) var(--space-3); }
.hn5-runlabel { font-size: var(--fs-card); color: var(--text-secondary); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-1); word-break: keep-all; overflow-wrap: anywhere; }
.hn5-v4 .hn-video-cap { font-size: var(--fs-card); }
</style>
<div class="hn5-v4">
  <div>
    <video class="hn-video" src="media/v4-gpu.mp4" poster="media/v4-gpu.jpg" aria-label="V4 영상: hybrid GPU 추론, 실제 터미널 녹화 포함, 무음, 2분 14초" title="V4 영상: hybrid GPU 추론, 실제 터미널 녹화 포함, 무음, 2분 14초" controls preload="metadata" muted playsinline tabindex="-1"></video>
    <div class="hn-video-cap">실측 결과 재구성 (2026-10 시뮬레이션 환경), 실제 터미널 녹화 포함, 무음</div>
  </div>
  <div class="hn5-res fragment fade-up" data-fragment-index="1">
    <div class="hn5-runlabel">영상: 2026-10-18 녹화 회차, 이전 실행 2026-10-15</div>
    <div class="callout callout-info"><strong class="text-info">GPU 노드</strong><div class="on-surface-muted">g6.xlarge, NVIDIA L4 23 GB. GPU taint, device plugin, allocatable GPU 1</div></div>
    <div class="callout callout-info"><strong class="text-info">추론 Pod</strong><div class="on-surface-muted">vLLM, Qwen2.5-0.5B-Instruct. 컨테이너 1개, hostNetwork 끔</div></div>
    <div class="callout callout-success"><strong class="text-success">클라우드에서 호출</strong><div class="on-surface-muted">Service 이름으로 호출, 응답 1초 미만 (10-18 녹화), 약 1초 (10-15)</div></div>
    <div class="callout callout-warning"><strong class="text-warning">첫 시작은 느림</strong><div class="on-surface-muted">이미지 다운로드 4분 35초 (10-18), 4분 28초 (10-15). 드라이버와 toolkit은 호스트에 미리</div></div>
  </div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- 영상 2분 14초. 녹화 장면 두 개는 2026-10-18 녹화 회차(GPU 호스트를 다시 조인해 녹화하고 바로 제거), 나머지 장면은 재구성
- g6.xlarge(NVIDIA L4 23 GB)를 hybrid 노드로 붙이고, 클라우드 Job이 Service 이름으로 vLLM을 호출. 응답은 녹화 회차 1초 미만, 2026-10-15 실행 약 1초
- 준비할 것: 드라이버와 container toolkit은 호스트에, 이미지는 미리 받기(다운로드 녹화 회차 4분 35초, 2026-10-15 4분 28초)
- 일시정지 지점은 한 곳: 1:34 verify.sh 결과

GPU 실행은 두 번입니다. 10월 15일에 처음 검증했고, 10월 18일에 GPU 호스트를 다시 붙여 녹화한 뒤 바로 지웠습니다. 영상의 녹화 장면과 응답 시간은 18일 값입니다.
0:06 왜 온프렘 GPU인지입니다. 데이터가 온프렘에 있거나 이미 GPU 서버가 있는 경우이고, 이 데모는 g6.xlarge의 NVIDIA L4를 시뮬레이션 온프렘에 두었습니다.
0:22 구성입니다. GPU 노드에 taint와 label을 걸고 NVIDIA device plugin을 hybrid GPU 노드에만 배포해 allocatable GPU 1을 확인했습니다. 추론 Pod는 vLLM과 Qwen2.5-0.5B 컨테이너 1개입니다.
0:40 실제 터미널 녹화, 0.75배속입니다. 녹화 첫 줄의 Demo 3은 데모 저장소 폴더 이름(demo3-gpu)이고, 오늘 순서로는 네 번째 영상입니다.
1:03 호출 흐름입니다. 클라우드 Job이 Service 이름으로 호출하면 Gateway 경로를 지나 GPU 노드의 vLLM Pod에 닿습니다. 클라우드 쪽 앱은 상대가 온프렘인지 신경 쓰지 않습니다.
{cue: pause}
1:19 다시 녹화입니다. 1:34쯤 verify.sh의 OK 네 줄이 나오면 잠시 멈추고 읽어 주세요. elapsed_seconds=0은 1초 미만이라는 뜻입니다.
1:42 준비할 것입니다. 이미지 다운로드는 녹화 회차 4분 35초, 10월 15일 4분 28초였고, 운영에서는 이미지를 미리 받아 두세요.
1:58 메시지와 요약 카드입니다.
근거: V4 영상 프로젝트 FACTS.md, RECORDINGS.md R4(녹화 회차 값), Deep Dive 5부 "데모 3: hybrid GPU에서 추론, 클라우드에서 호출", 데모 저장소 RUNBOOK.md 3절(2026-10-15 값)
{cue: transition}
영상은 여기까지이고, 영상으로 만들지 않은 결과 하나를 더 보겠습니다. Istio입니다.
:::

---
<!-- Slide 10: Istio 공존 -->
@type: content
@title: Istio sidecar는 Gateway와 함께 동작했다

## Istio sidecar는 Gateway와 함께 동작했다

:::html
<style>
.hn5-table { width: 100%; font-size: var(--fs-card); word-break: keep-all; }
.hn5-ok { color: var(--success); font-weight: var(--weight-bold); }
.hn5-runlabel { font-size: var(--fs-card); color: var(--text-secondary); margin-bottom: var(--space-1); }
.data-table th { text-transform: none; letter-spacing: normal; font-size: var(--fs-card); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="fragment fade-up" data-fragment-index="1">
  <div class="hn5-runlabel">2026-10-17 측정, Istio 1.30.6 sidecar 모드, 영상 없음</div>
  <table class="data-table hn5-table">
    <thead><tr><th>검증 항목</th><th>결과</th></tr></thead>
    <tbody>
      <tr><td>hybrid 노드 Pod에도 sidecar 주입</td><td><span class="hn5-ok">통과</span> 4개 Pod 모두 2/2</td></tr>
      <tr><td>클라우드와 hybrid 사이 양방향 호출, STRICT mTLS</td><td><span class="hn5-ok">통과</span> 메시 안 호출 성공, 메시 밖 평문 호출 거부</td></tr>
      <tr><td>Istio L7 정책 (/admin 거부)</td><td><span class="hn5-ok">통과</span> /admin 경로 403</td></tr>
      <tr><td>Gateway 리더 전환 중 요청 (초당 40건, 45초)</td><td><span class="hn5-ok">1,800건 모두 성공</span> (전환 5초)</td></tr>
    </tbody>
  </table>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="2">
  <div class="callout callout-success"><strong class="text-success">꺼지는 것은 Cilium L7</strong><div class="on-surface-muted">Gateway 때문에 Cilium L7 proxy는 꺼진 채였습니다. Istio의 L7은 sidecar Envoy가 처리합니다.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">sidecar 모드만 확인</strong><div class="on-surface-muted">ambient 모드는 확인하지 않았습니다.</div></div>
</div>
:::

:::notes
{timing: 1min}
[요약]
- 2026-10-17, Istio 1.30.6 sidecar 모드: hybrid Pod에도 sidecar 주입, 양방향 호출과 STRICT mTLS, /admin 403 L7 정책 모두 통과
- Gateway 때문에 Cilium L7 proxy는 꺼져 있어야 하고, 실제로 끈 상태에서 통과. Istio L7은 sidecar Envoy가 처리
- Gateway 리더 전환 중 초당 40건 45초, 1,800건 모두 성공. ambient 모드는 미확인

Gateway를 쓰면 Cilium L7이 꺼지는데, 그럼 Istio도 못 쓰느냐는 질문을 자주 받습니다. sidecar 모드로 돌려 보니 함께 동작했습니다. Istio의 L7은 sidecar Envoy가 처리하기 때문입니다.
{cue: pause}
표의 네 항목이 모두 통과했고, 리더 전환 5초 동안 1,800건이 모두 성공한 것은 sidecar의 기본 재시도 덕분일 가능성이 큽니다. 지연은 p50 기준 같은 쪽 0.62~1.32 ms, Gateway를 건너면 2.11~2.46 ms였고 순차 300회 요청의 값입니다. ambient 모드는 확인하지 않았습니다.
근거: Deep Dive 5부 "Istio와 gateway는 함께 쓸 수 있다", "Istio 실측: 경로별 지연과 gateway 전환"(데모 저장소 results/istio-20261017-2311.json), AWS docs hybrid-nodes-gateway-cni (l7Proxy=false 필수)
{cue: transition}
여기까지가 5부였습니다. 이제 마지막 6부, 도입 판단 기준으로 정리하겠습니다.
:::

---
<!-- Slide 11: 도입 판단 체크리스트 -->
@type: content
@title: 6부: 도입 전에 정할 여섯 가지

## 6부: 도입 전에 정할 여섯 가지

:::html
<style>
.hn5-check { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); }
.hn5-item { border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-3); background: var(--bg-card); font-size: var(--fs-card); word-break: keep-all; overflow-wrap: break-word; }
.hn5-item h4 { margin: 0 0 var(--space-1); font-size: var(--fs-card); color: var(--accent); }
.hn5-q { font-weight: var(--weight-bold); }
.hn5-part { display: block; color: var(--text-muted); font-size: var(--fs-caption); margin-top: var(--space-1); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-1); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="hn5-check">
  <div class="hn5-item fragment fade-up" data-fragment-index="1"><h4>1. 연결</h4><div class="hn5-q">안정적인 사설 양방향 연결이 있는가</div><div class="on-surface-muted">DX 또는 VPN, 양방향 route. 간헐 연결, 단절 환경용이 아님</div><span class="hn5-part">3부, 4부</span></div>
  <div class="hn5-item fragment fade-up" data-fragment-index="2"><h4>2. CIDR</h4><div class="hn5-q">네 가지 CIDR이 서로 겹치지 않는가</div><div class="on-surface-muted">VPC, Service, remote node, remote Pod. 나중에 바꾸기 어려움</div><span class="hn5-part">3부</span></div>
  <div class="hn5-item fragment fade-up" data-fragment-index="3"><h4>3. 라우팅 방식</h4><div class="hn5-q">BGP, static, Gateway 중 무엇인가</div><div class="on-surface-muted">라우터 팀이 BGP를 운영할 수 있으면 BGP. 어려우면 Gateway, 대신 Cilium L7 끔, leader AZ 비용</div><span class="hn5-part">3부, V1, V3</span></div>
  <div class="hn5-item fragment fade-up" data-fragment-index="4"><h4>4. 자격 증명</h4><div class="hn5-q">SSM인가, IAM Roles Anywhere인가</div><div class="on-surface-muted">단절 후 복구 속도와 인증서 운영 역량으로 고름</div><span class="hn5-part">2부, 4부</span></div>
  <div class="hn5-item fragment fade-up" data-fragment-index="5"><h4>5. CNI</h4><div class="hn5-q">클라우드 노드가 있는가</div><div class="on-surface-muted">hybrid는 Cilium. 클라우드 노드가 있으면 VPC CNI와 혼합, webhook은 클라우드에</div><span class="hn5-part">3부</span></div>
  <div class="hn5-item fragment fade-up" data-fragment-index="6"><h4>6. 운영</h4><div class="hn5-q">교체, 단절, 버스팅을 준비했는가</div><div class="on-surface-muted">골든 이미지와 여유 용량, 300초 eviction 대비, Pending 기반 버스팅과 축소 정책</div><span class="hn5-part">4부, V2</span></div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- 여섯 가지 결정: 연결, CIDR, 라우팅 방식, 자격 증명, CNI, 운영. 앞의 셋은 네트워크 팀과, 뒤의 셋은 플랫폼 팀과 정함
- 라우팅은 BGP 우선, 라우터 변경이 어려우면 Gateway. Gateway를 고르면 Cilium L7 끔과 leader AZ 비용을 받아들임
- 운영은 업그레이드를 호스트 교체로, 단절은 300초와 자격 증명 만료로, 버스팅은 Pending과 축소 정책으로 준비

여기부터 6부, 마무리입니다. 오늘 내용을 도입 전에 정해야 할 여섯 가지로 묶었습니다. 카드 아래에 관련 파트를 적어 두었습니다.
첫째 연결입니다. Direct Connect나 VPN으로 안정적인 사설 연결이 있고, 양쪽 방향 route가 모두 있어야 합니다. 이 서비스는 간헐 연결이나 단절 환경용이 아닙니다. 둘째 CIDR입니다. VPC, Service, remote node, remote Pod 네 대역이 겹치지 않아야 하고, 나중에 바꾸기 어려우니 네트워크 팀과 먼저 확정합니다.
{cue: pause}
셋째 라우팅 방식입니다. 라우터 팀이 BGP를 운영할 수 있으면 BGP를 우선하고, 라우터 변경이 어려울 때 Gateway를 씁니다. Gateway를 고르면 Cilium L7 기능이 꺼지고, 트래픽이 leader AZ로 모이는 비용과 활성 1대의 처리량 한계를 받아들여야 합니다. V1에서 본 3~5초 전환도 이 선택에 따라오는 특성입니다.
넷째 자격 증명입니다. SSM은 자격 증명이 1시간 고정이고 단절 뒤 재연결이 늦을 수 있고, IAM Roles Anywhere는 빠르게 복구되지만 인증서를 운영해야 합니다. 다섯째 CNI입니다. hybrid 노드는 Cilium이고, 클라우드 노드가 있다면 VPC CNI와 섞는 것이 AWS 권장이며 webhook을 클라우드에 둡니다.
{cue: question}
여섯째 운영입니다. 업그레이드는 호스트 교체가 기본이고 롤백 명령이 없으니 골든 이미지와 여유 용량을 준비합니다. 단절되면 toleration이 없는 Pod는 300초 뒤 eviction되고, 버스팅은 Pending Pod에 반응하며 줄일 때는 V2처럼 정책이 있어야 온프렘 Pod가 남습니다. 이 중 우리 조직에서 아직 답이 없는 칸이 어디인지 보시면 다음 단계가 정해집니다.
근거: 이 덱 2부 자격 증명 선택, 3부 "연결이 먼저, CIDR은 겹치지 않게", "Pod 라우팅: static, BGP, Gateway", "CNI 구성", "Gateway 비용", 4부 "노드 수명 주기", "연결이 끊기면", "버스팅", 5부 V1, V2, V3 결과
{cue: transition}
마지막으로 더 깊이 보실 자료를 안내하겠습니다.
:::

---
<!-- Slide 12: 다음 단계와 참고 자료 -->
@type: content
@title: 다음 단계와 참고 자료

## 다음 단계와 참고 자료

:::html
<style>
.hn5-next { display: grid; grid-template-columns: 1fr 1.3fr; gap: var(--space-4); align-items: start; }
.hn5-col { display: flex; flex-direction: column; gap: var(--space-3); }
.hn5-label { font-size: var(--fs-card); font-weight: var(--weight-bold); color: var(--text-secondary); }
.hn5-ref { margin: 0; padding-left: var(--space-4); font-size: var(--fs-card); line-height: 1.7; }
.hn5-ref a, .hn5-col a { color: var(--accent); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="hn5-next">
  <div class="hn5-col">
    <div class="hn5-label">다음 단계</div>
    <div class="callout callout-info fragment fade-up" data-fragment-index="1"><strong class="text-info">설정과 명령까지 보려면</strong><div class="on-surface-muted"><a href="../eks-hybrid-nodes/index.html" target="_blank" rel="noopener">EKS Hybrid Nodes Deep Dive (2시간)</a>: 네트워킹, 노드 라이프사이클, 운영 전략, 라이브 데모</div></div>
    <div class="callout callout-info fragment fade-up" data-fragment-index="2"><strong class="text-info">직접 돌려 보려면</strong><div class="on-surface-muted"><a href="https://github.com/Atom-oh/eks-hybrid-demo" target="_blank" rel="noopener">Atom-oh/eks-hybrid-demo</a>: 오늘 영상의 데모 스크립트와 측정 결과. private 저장소, 요청 시 공유</div></div>
    <div class="callout callout-info fragment fade-up" data-fragment-index="3"><strong class="text-accent">Q&A</strong><div class="on-surface-muted">5부 수치는 시뮬레이션 환경의 실측입니다. 적용 전에 최신 AWS 문서로 지원 조합을 확인하세요.</div></div>
  </div>
  <div class="hn5-col">
    <div class="hn5-label">AWS 문서</div>
    <ul class="hn5-ref">
      <li><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-overview.html" target="_blank" rel="noopener">Hybrid Nodes 개요</a></li>
      <li><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-networking.html" target="_blank" rel="noopener">네트워킹 요구 사항</a></li>
      <li><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-creds.html" target="_blank" rel="noopener">자격 증명 준비 (SSM, IAM RA)</a></li>
      <li><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-cni.html" target="_blank" rel="noopener">CNI 구성</a></li>
      <li><a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-gateway-overview.html" target="_blank" rel="noopener">Hybrid Nodes Gateway 개요</a></li>
      <li><a href="https://docs.aws.amazon.com/eks/latest/best-practices/hybrid-nodes-network-disconnection-best-practices.html" target="_blank" rel="noopener">네트워크 단절 대비 모범 사례</a></li>
      <li><a href="https://aws.amazon.com/eks/pricing/" target="_blank" rel="noopener">EKS 요금</a></li>
    </ul>
  </div>
</div>
:::

:::notes
{timing: 4min}
[요약]
- 안내 1분, 이어서 Q&A 3분 (슬라이드 2에서 약속한 질문 시간)
- 설정 값, 명령, 방화벽 표, 버전별 점검은 Deep Dive(2시간) 덱에 있음
- 데모 스크립트와 측정 결과는 데모 저장소(private, 요청 시 공유)
- AWS 문서 7개: 개요, 네트워킹, 자격 증명, CNI, Gateway, 단절 대비 모범 사례, 요금. 이후 질문 받기

오늘은 판단에 필요한 내용만 다뤘습니다. 실제 설정 값과 명령, 방화벽 규칙 전체, 업그레이드 전 점검 항목은 2시간짜리 Deep Dive 덱에 있고, 오늘 슬라이드 곳곳에서 "Deep Dive N부"로 안내한 내용이 거기 있습니다.
직접 돌려 보시려면 데모 저장소를 쓰시면 됩니다. private 저장소라 필요하시면 요청해 주세요. 끝나면 정리 스크립트로 자원을 지워 비용을 멈추셔야 합니다.
오른쪽은 오늘 내용의 근거가 된 AWS 문서입니다. 링크는 바로 열 수 있습니다.
{cue: pause}
수치는 모두 EC2로 온프렘을 시뮬레이션한 환경에서 잰 값이고, 적용하시기 전에 최신 문서로 지원 조합을 확인하시기 바랍니다.
{cue: question}
이제 질문 받겠습니다. 질문 시간은 3분 정도이고, 남은 질문은 세션 뒤에 따로 받겠습니다.
근거: Deep Dive 5부 "참고 자료 & Q&A"(링크 주소는 그 슬라이드에서 그대로 가져옴), "정리: 무엇을 확인했고 무엇이 남았나"(teardown 안내)
:::

---
<!-- Slide 13: Thank You -->
@type: thankyou
@toc: toc.html
@message: EKS Hybrid Nodes, 감사합니다

# Thank You

:::notes
{timing: 0.5min}
[요약]
- 세션 마무리

오늘 세션 들어 주셔서 감사합니다. 더 깊은 내용은 Deep Dive 덱에서, 데모 코드와 측정 결과는 데모 저장소에서 보실 수 있습니다.
:::
