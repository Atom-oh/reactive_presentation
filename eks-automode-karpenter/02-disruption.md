---
remarp: true
block: 02-disruption
---

---
<!-- Slide 1: 3부 구분 (Section) -->
@type: section

# 3부: 스케일링과 Disruption

노드를 고르고, 줄이고, 바꾸는 규칙

:::notes
{timing: 0.5min}
[요약]
- 3부의 질문: Karpenter는 어떤 노드를 고르고, 언제 줄이고, 언제 바꾸는가
- 순서: 프로비저닝, consolidation, 스케줄러 점수 전략, in-place resize, disruption budget, Drift와 만료, Spot 중단, 앱 보호
- 각 항목마다 self-managed Karpenter v1.15와 Auto Mode의 기본값 차이를 함께 봅니다.

3부는 스케일링과 disruption입니다. 노드를 만드는 것보다 줄이고 바꾸는 쪽에서 운영 이슈가 훨씬 많이 생깁니다. 그래서 이번 파트가 오늘 세션에서 가장 깁니다.
프로비저닝부터 시작해서 consolidation, 스케줄러 점수 전략, in-place resize, budget, Drift와 만료, Spot 중단, 그리고 앱을 지키는 장치 순서로 가겠습니다.
{cue: transition}
먼저 노드를 고르는 규칙입니다.
:::

---
<!-- Slide 2: 프로비저닝 결정 -->
@type: content
@title: requirements는 넓게, 제약은 명확하게

## requirements는 넓게, 제약은 명확하게

:::html
<style>
.ak2-body { display: grid; grid-template-columns: 1.15fr 1fr; gap: var(--space-4); align-items: start; margin-top: var(--space-3); }
.ak2-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">Self-managed NodePool</button>
  <button class="tab-btn">Auto Mode NodePool</button>
</div>
<div class="tc">
  <div class="ak2-body">
<pre class="code-block"><span class="key">requirements</span>:
- <span class="key">key</span>: karpenter.sh/capacity-type
  <span class="key">operator</span>: In
  <span class="key">values</span>: [<span class="string">"spot"</span>, <span class="string">"on-demand"</span>]
- <span class="key">key</span>: karpenter.k8s.aws/instance-category
  <span class="key">operator</span>: In
  <span class="key">values</span>: [<span class="string">"c"</span>, <span class="string">"m"</span>, <span class="string">"r"</span>]
- <span class="key">key</span>: kubernetes.io/arch
  <span class="key">operator</span>: In
  <span class="key">values</span>: [<span class="string">"amd64"</span>, <span class="string">"arm64"</span>]</pre>
    <div class="ak2-stack">
      <div class="callout callout-info fragment fade-left" data-fragment-index="1"><strong class="text-info">계열 단위로 넓게</strong><div class="on-surface-muted">특정 유형 몇 개보다 category, generation 같은 속성으로 후보를 넓힙니다.</div></div>
      <div class="callout callout-info fragment fade-left" data-fragment-index="2"><strong class="text-info">Spot은 유연성이 조건</strong><div class="on-surface-muted">single-node spot-to-spot 교체는 instance type 15개 이상 유연성이 필요합니다.</div></div>
    </div>
  </div>
</div>
<div class="tc" hidden>
  <div class="ak2-body">
<pre class="code-block"><span class="key">nodeClassRef</span>:
  <span class="key">group</span>: eks.amazonaws.com
  <span class="key">kind</span>: NodeClass
  <span class="key">name</span>: default
<span class="key">requirements</span>:
- <span class="key">key</span>: eks.amazonaws.com/instance-category
  <span class="key">operator</span>: In
  <span class="key">values</span>: [<span class="string">"c"</span>, <span class="string">"m"</span>, <span class="string">"r"</span>]
- <span class="key">key</span>: karpenter.sh/capacity-type
  <span class="key">operator</span>: In
  <span class="key">values</span>: [<span class="string">"on-demand"</span>]</pre>
    <div class="ak2-stack">
      <div class="callout callout-info"><strong class="text-info">Built-in pool의 범위</strong><div class="on-surface-muted"><code>system</code>, <code>general-purpose</code>: On-Demand만, C/M/R 계열, 5세대 이상. 수정 불가</div></div>
      <div class="callout callout-warning"><strong class="text-warning">지원 인스턴스 제약</strong><div class="on-surface-muted">1 vCPU 초과만, nano, micro, small 제외. Linux만 지원</div></div>
    </div>
  </div>
</div>
<div class="callout callout-info fragment fade-up" data-fragment-index="3"><strong class="text-info">capacity-type을 비워 두면</strong>: 두 방식 모두 reserved, spot, on-demand 순서로 고릅니다. Auto Mode 기본 풀은 On-Demand 고정이라 Spot은 커스텀 NodePool에서, self-managed는 비워 두면 Spot이 먼저 선택되니 의도를 명시하세요.</div>
:::

:::notes
{timing: 1.5min}
[요약]
- requirements는 특정 인스턴스 유형보다 category, generation, arch 같은 속성으로 넓게 잡습니다.
- Spot은 유연성이 핵심이며, single-node spot-to-spot 교체는 15개 이상 instance type이 필요합니다.
- Auto Mode built-in pool은 On-Demand, C/M/R, 5세대 이상 고정이고 수정할 수 없습니다.
- capacity-type 미지정 시 두 방식 모두 reserved, spot, on-demand 순. self-managed는 비워 두면 Spot이 먼저 선택됨

requirements는 특정 유형을 나열하기보다 category, arch 같은 속성으로 넓게 잡습니다. 후보가 많을수록 가격과 가용성에 맞춰 고를 여지가 생기고, Spot에서는 더 중요합니다. single-node spot-to-spot 교체는 15개 이상 유형이 필요하고 alpha gate 뒤에 있습니다.
{cue: demo}
두 번째 탭 Auto Mode는 라벨 키가 eks.amazonaws.com으로 시작하고, 1 vCPU 이하 유형은 쓸 수 없습니다.
{cue: pause}
아래 박스가 실무 팁입니다. capacity-type을 비워 두면 두 방식 모두 reserved, spot, on-demand 순서로 고릅니다. Auto Mode 기본 풀은 On-Demand 고정이라 Spot은 커스텀 NodePool이 필요하고, self-managed는 비워 두면 Spot이 먼저 뜹니다.

[출처]
- https://karpenter.sh/docs/concepts/disruption/ (spot-to-spot 15개 유연성)
- https://docs.aws.amazon.com/eks/latest/userguide/set-builtin-node-pools.html, create-node-pool.html, automode-learn-instances.html
{cue: transition}
노드를 만들었으면, 다음은 언제 줄이느냐입니다.
:::

---
<!-- Slide 3: Consolidation 정책 -->
@type: content
@title: Consolidation: 절감이 중단보다 클 때

## Consolidation: 절감이 중단보다 클 때

:::html
<style>
.ak2-pol { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); margin-bottom: var(--space-3); }
.ak2-pol code { font-size: var(--fs-card); }
.ak2-time { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); margin-bottom: var(--space-3); }
.ak2-when { font-weight: var(--weight-bold); color: var(--accent); font-size: var(--fs-card); margin-bottom: var(--space-1); }
.ak2-ev { border: 1px dashed var(--border); border-radius: var(--radius-md); padding: var(--space-2) var(--space-3); font-size: var(--fs-card); word-break: keep-all; }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak2-pol" data-reveal="stagger">
  <div class="card"><strong class="text-accent"><code>WhenEmpty</code></strong><div class="on-surface-muted">Pod가 없는 노드만 회수합니다.</div></div>
  <div class="card"><strong class="text-accent"><code>WhenEmptyOrUnderutilized</code></strong><div class="on-surface-muted">작은 절감이라도 있으면 교체합니다. upstream 기본값</div></div>
  <div class="card"><strong class="text-accent"><code>Balanced</code></strong><div class="on-surface-muted">절감 비율이 유발하는 Pod disruption 비율보다 가치 있을 때만 실행</div></div>
</div>
<div class="ak2-time">
  <div class="ak2-ev fragment fade-right" data-fragment-index="1"><div class="ak2-when">2026-07-11 Karpenter v1.14.0</div>upstream에 <code>Balanced</code> 추가, opt-in</div>
  <div class="ak2-ev fragment fade-right" data-fragment-index="2"><div class="ak2-when">2026-07-27 Auto Mode</div>NodePool에 <code>Balanced</code> 추가, 기존 NodePool 동작은 그대로</div>
  <div class="ak2-ev fragment fade-right" data-fragment-index="3"><div class="ak2-when">2026-10-01 EKS 1.37</div>새로 만든 NodePool 중 정책 미지정은 <code>Balanced</code>, built-in pool도 <code>Balanced</code></div>
</div>
<div class="callout callout-warning fragment fade-up" data-fragment-index="4"><strong class="text-warning">GitOps라면 명시하세요</strong>: 기본값은 생성 시점에만 적용됩니다. 미지정 NodePool을 재생성하면 Git에는 값이 없고 live 객체는 <code>Balanced</code>인 drift가 생깁니다.</div>
:::

:::notes
{timing: 2.5min}
[요약]
- 정책 3가지: WhenEmpty(빈 노드만), WhenEmptyOrUnderutilized(작은 절감에도 교체, upstream 기본), Balanced(절감이 disruption만큼 가치 있을 때만)
- Balanced는 upstream v1.14.0에서 opt-in으로 추가, Auto Mode에는 2026-07-27 추가
- EKS 1.37부터 Auto Mode에서 새로 만드는 미지정 NodePool은 Balanced, built-in pool도 Balanced이며 매시간 reconcile되어 덮어쓸 수 없음
- 기본값은 생성 시점에만 적용되므로 GitOps에서는 값을 명시

consolidation은 남는 노드를 줄이는 기능이고, 정책이 세 가지입니다. WhenEmpty는 Pod가 하나도 없는 노드만 회수합니다. WhenEmptyOrUnderutilized는 덜 쓰이는 노드까지 교체 대상으로 보고, AWS 표현으로는 시간당 0.01달러 같은 작은 절감에도 교체를 진행합니다. upstream Karpenter의 기본값은 여전히 이것입니다.
{cue: pause}
세 번째 Balanced가 새 정책입니다. 각 consolidation 동작을 NodePool 비용 중 얼마를 줄이는지, 그리고 NodePool 전체 Pod disruption 중 얼마를 일으키는지로 점수를 매기고, 절감이 충분할 때만 실행합니다. 기본으로는 축출되는 Pod 수로 계산하고, priority가 높은 Pod는 더 큰 가중치를 받습니다. AWS는 "비슷한 비용에 더 적은 Pod eviction"이라고 설명합니다.
아래 타임라인을 보시면, upstream에는 7월 11일 v1.14.0에서 opt-in으로 들어왔고, Auto Mode에는 7월 27일에 추가되었습니다. 그리고 10월 1일 EKS 1.37부터 Auto Mode에서 새로 만드는 NodePool 중 정책을 지정하지 않은 것은 Balanced가 기본값이 됩니다. built-in NodePool 두 개도 1.37에서 Balanced로 바뀌고, EKS가 매시간 재조정하므로 덮어쓸 수 없습니다.
{cue: question}
여기서 GitOps를 쓰시는 분들은 주의하셔야 합니다. 기본값은 객체를 만들 때만 적용됩니다. 업그레이드한다고 기존 NodePool이 바뀌지는 않지만, Argo CD가 NodePool을 지웠다 다시 만들거나 새 1.37 클러스터를 부트스트랩하면 Balanced가 됩니다. Git에는 값이 없는데 live 객체에는 Balanced가 보이는 상태입니다. 그래서 정책은 반드시 명시하세요. 이전 동작이 필요하면 WhenEmptyOrUnderutilized를 명시한 커스텀 NodePool로 워크로드를 보내면 됩니다.

[출처]
- https://docs.aws.amazon.com/eks/latest/userguide/auto-change.html (2026-07-27, 2026-10-01 항목)
- https://karpenter.sh/docs/concepts/disruption/, https://github.com/aws/karpenter-provider-aws/releases/tag/v1.14.0
{cue: transition}
정책이 "무엇을 줄일지"였다면, 그 전에 Pod가 처음부터 어디에 놓이는지도 consolidation에 영향을 줍니다. 스케줄러 점수 전략입니다.
:::

---
<!-- Slide 3a: 스케줄러 점수 전략 -->
@type: content
@title: 스케줄러 점수: 흩을까, 모을까

## 스케줄러 점수: 흩을까, 모을까

:::html
<style>
.ak2s-wrap { display: grid; grid-template-columns: 1.15fr 1fr; gap: var(--space-4); align-items: start; }
.ak2s-nodes { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); margin-top: var(--space-3); }
.ak2s-node { border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-4) var(--space-3); font-size: var(--fs-card); text-align: center; }
.ak2s-bar { height: var(--space-7); border-radius: var(--radius-sm); background: var(--bg-card); margin-top: var(--space-3); overflow: hidden; display: flex; }
.ak2s-legend { display: flex; gap: var(--space-4); margin-top: var(--space-3); font-size: var(--fs-card); color: var(--text-secondary); }
.ak2s-legend i { display: inline-block; width: var(--space-4); height: var(--space-4); border-radius: var(--radius-sm); vertical-align: middle; margin-right: var(--space-1); }
.ak2s-effect { margin-top: var(--space-4); }
.ak2s-used { background: var(--text-secondary); }
.ak2s-new { background: var(--accent); }
.ak2s-bar [data-w="70"] { width: 70%; } .ak2s-bar [data-w="40"] { width: 40%; } .ak2s-bar [data-w="15"] { width: 15%; } .ak2s-bar [data-w="20"] { width: 20%; }
.ak2s-pick { color: var(--accent); font-weight: var(--weight-bold); }
.ak2s-cli { font-family: var(--font-mono); font-size: var(--fs-card); background: var(--bg-card); border-radius: var(--radius-md); padding: var(--space-3); white-space: pre; overflow-x: auto; margin: 0 0 var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.ak2s-wrap .callout + .callout { margin-top: var(--space-3); }
</style>
<div class="ak2s-wrap">
  <div>
    <div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
      <button class="tab-btn active">LeastAllocated (기본)</button>
      <button class="tab-btn">MostAllocated</button>
    </div>
    <div class="tc">
      <div class="on-surface-muted">여유가 많은 노드에 새 Pod를 보냅니다. 노드마다 여유를 남기는 분산 배치입니다.</div>
      <div class="ak2s-nodes">
        <div class="ak2s-node">노드 A<div class="ak2s-bar"><span class="ak2s-used" data-w="70"></span></div></div>
        <div class="ak2s-node">노드 B<div class="ak2s-bar"><span class="ak2s-used" data-w="40"></span></div></div>
        <div class="ak2s-node"><span class="ak2s-pick">노드 C, 선택</span><div class="ak2s-bar"><span class="ak2s-used" data-w="15"></span><span class="ak2s-new" data-w="20"></span></div></div>
      </div>
    </div>
    <div class="tc" hidden>
      <div class="on-surface-muted">이미 많이 쓰는 노드에 새 Pod를 보냅니다. 적게 쓰인 노드는 비워져 consolidation 대상이 되기 쉽습니다.</div>
      <div class="ak2s-nodes">
        <div class="ak2s-node"><span class="ak2s-pick">노드 A, 선택</span><div class="ak2s-bar"><span class="ak2s-used" data-w="70"></span><span class="ak2s-new" data-w="20"></span></div></div>
        <div class="ak2s-node">노드 B<div class="ak2s-bar"><span class="ak2s-used" data-w="40"></span></div></div>
        <div class="ak2s-node">노드 C<div class="ak2s-bar"><span class="ak2s-used" data-w="15"></span></div></div>
      </div>
    </div>
    <div class="ak2s-legend"><span><i class="ak2s-used"></i>기존 Pod requests</span><span><i class="ak2s-new"></i>새 Pod</span><span>개념 그림, 사용률은 예시</span></div>
    <div class="callout callout-info ak2s-effect fragment fade-up" data-fragment-index="4"><strong class="text-info">consolidation과의 관계</strong><div class="on-surface-muted">MostAllocated는 적게 쓰인 노드에 새 Pod를 보내지 않아, 그 노드가 비면 Auto Mode나 Karpenter가 정리할 수 있습니다.</div></div>
  </div>
  <div>
    <pre class="ak2s-cli fragment fade-up" data-fragment-index="1">aws eks update-cluster-config \
  --name $CLUSTER \
  --kube-scheduler-config \
  '{"nodeResourcesFit":{"scoringStrategy":
    {"type":"MostAllocated"}}}'</pre>
    <div class="callout callout-info fragment fade-up" data-fragment-index="2"><strong class="text-info">EKS control plane configuration</strong><div class="on-surface-muted">2026-08-12 출시, Kubernetes 1.31 이상. 가중치 1 to 100: cpu, memory, nvidia.com/gpu, Neuron</div></div>
    <div class="callout callout-warning fragment fade-up" data-fragment-index="3"><strong class="text-warning">노드 생성, 삭제 방식은 그대로</strong><div class="on-surface-muted">Pod 배치 점수만 바뀝니다. 클러스터 전체 적용, 실행 중 Pod는 옮기지 않고, 밀집할수록 노드 장애 영향이 커집니다.</div></div>
  </div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- EKS advanced control plane configuration(2026-08-12, 1.31 이상)으로 kube-scheduler nodeResourcesFit 점수 전략을 바꿀 수 있음
- LeastAllocated(기본)는 분산, MostAllocated는 이미 쓰는 노드로 모아서 적게 쓰인 노드를 consolidation이 지우기 쉬워짐
- Auto Mode와 Karpenter의 노드 생성, 삭제 방식은 바뀌지 않음. 클러스터 전체 적용, 실행 중 Pod 이동 없음, 밀집 시 장애 영향 범위 증가

consolidation 이야기를 하면 꼭 나오는 질문이 "애초에 Pod를 모아서 배치할 수는 없나요"입니다. 노드를 고르는 건 Karpenter지만, 이미 있는 노드 중 어디에 Pod를 놓을지는 kube-scheduler가 정합니다.
{cue: demo}
왼쪽 탭을 보시면 기본값 LeastAllocated는 여유가 많은 노드 C를 고릅니다. 두 번째 탭 MostAllocated로 바꾸면 이미 많이 쓰는 노드 A로 보냅니다. 새 Pod가 적게 쓰인 노드로 가지 않으니, 그 노드는 점점 비고 consolidation이 지우기 쉬워집니다.
{cue: pause}
EKS에서는 8월 12일부터 이 값을 바꿀 수 있습니다. 1.36 전용이 아니라 1.31 이상이면 됩니다. update-cluster-config에 kube-scheduler-config를 넘기면 control plane이 몇 분간 rolling update됩니다. GPU나 Neuron 가중치를 높이면 가속기 Pod를 이미 일부 쓰는 노드로 모을 수도 있습니다.
주의할 점은 세 가지입니다. 클러스터 전체에 적용되고, 이미 실행 중인 Pod는 옮기지 않으며, 모을수록 노드 하나가 죽을 때 영향받는 Pod가 많아집니다. 그리고 AWS 문서에 명시된 대로, 이 설정은 Auto Mode나 Karpenter가 노드를 만들고 지우는 방식은 바꾸지 않습니다. 오늘 데모에서는 이 값을 바꾸지 않았습니다.

[출처]
- https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-eks-control-plane-configuration-parameters/
- https://docs.aws.amazon.com/eks/latest/userguide/control-plane-configuration.html
- https://docs.aws.amazon.com/eks/latest/userguide/control-plane-configuration-getting-started.html
{cue: transition}
Pod 쪽에서도 노드를 덜 쓰게 만드는 방법이 있습니다. requests를 재시작 없이 바꾸는 것입니다.
:::

---
<!-- Slide 3b: In-place Pod resize -->
@type: content
@title: In-place resize: 재시작 없이 requests를 줄인다

## In-place resize: 재시작 없이 requests를 줄인다

:::html
<style>
.ak2r-time { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); margin-bottom: var(--space-3); }
.ak2r-when { font-weight: var(--weight-bold); color: var(--accent); font-size: var(--fs-card); margin-bottom: var(--space-1); }
.ak2r-ev { border: 1px dashed var(--border); border-radius: var(--radius-md); padding: var(--space-2) var(--space-3); font-size: var(--fs-card); word-break: keep-all; }
.ak2r-two .callout + .callout { margin-top: var(--space-3); }
.ak2r-two { display: grid; grid-template-columns: 1.2fr 1fr; gap: var(--space-4); align-items: start; }
.ak2r-table { width: 100%; font-size: var(--fs-card); word-break: keep-all; }
.ak2r-table td, .ak2r-table th { white-space: nowrap; }
.ak2r-table td.ak2r-num { font-variant-numeric: tabular-nums; font-weight: var(--weight-bold); }
.data-table th { text-transform: none; letter-spacing: normal; font-size: var(--fs-card); }
.ak2r-cap { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-1); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak2r-time" data-reveal="stagger">
  <div class="ak2r-ev"><div class="ak2r-when">1.35 GA</div>컨테이너 in-place resize, <code>resize</code> subresource</div>
  <div class="ak2r-ev"><div class="ak2r-when">1.36 Beta, 기본 켜짐</div>Pod 단위 <code>.spec.resources</code>도 Pod 재생성 없이 resize</div>
  <div class="ak2r-ev"><div class="ak2r-when">1.37 Alpha</div>노드가 꽉 차 Deferred된 resize를 위해 scheduler가 낮은 priority Pod를 preempt</div>
</div>
<div class="ak2r-two">
  <div class="fragment fade-up" data-fragment-index="1">
    <table class="data-table ak2r-table">
      <thead><tr><th>워크로드</th><th>CPU req=limit</th><th>Guaranteed</th><th>restartCount</th><th>containerID</th></tr></thead>
      <tbody>
        <tr><td>Deployment (Pod 2개)</td><td class="ak2r-num">200m → 50m</td><td>유지</td><td class="ak2r-num">0 → 0</td><td>동일</td></tr>
        <tr><td>StatefulSet</td><td class="ak2r-num">200m → 50m</td><td>유지</td><td class="ak2r-num">0 → 0</td><td>동일</td></tr>
        <tr><td>DaemonSet</td><td class="ak2r-num">200m → 50m</td><td>유지</td><td class="ak2r-num">0 → 0</td><td>동일</td></tr>
      </tbody>
    </table>
    <div class="ak2r-cap">실측 2026-06, EKS 1.36.1, AL2023 arm64 노드(Auto Mode 아님): startup probe 통과 후 <code>pods/resize</code>로 축소, memory 고정</div>
  </div>
  <div>
    <div class="callout callout-info fragment fade-up" data-fragment-index="2"><strong class="text-info">노드 자동화와 만나는 지점</strong><div class="on-surface-muted">Karpenter v1.14.0부터 Pod 크기를 requests와 allocatedResources 중 큰 값으로 계산합니다. requests가 줄면 consolidation 여지가 생깁니다.</div></div>
    <div class="callout callout-warning fragment fade-up" data-fragment-index="3"><strong class="text-warning">주의</strong><div class="on-surface-muted">QoS class는 바뀌지 않고, memory 축소는 재시작될 수 있습니다. Auto Mode의 resize 동작은 AWS 문서에 따로 없습니다.</div></div>
  </div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- 1.35 in-place resize GA, 1.36 Pod-level resources resize Beta(기본 켜짐), 1.37 resize를 위한 scheduler preemption Alpha
- 실측(EKS 1.36.1): CPU 200m에서 50m로 축소, Guaranteed 유지, restartCount 0, containerID 동일. Deployment, StatefulSet, DaemonSet 모두
- Karpenter v1.14.0+는 requests와 allocatedResources 중 큰 값으로 Pod 크기 계산. QoS 불변, memory 축소는 재시작 가능, Auto Mode 동작은 문서화되지 않음

앞 슬라이드가 Pod를 어디에 놓을지였다면, 이번에는 Pod 크기 자체를 줄이는 방법입니다. 1.35에서 in-place resize가 GA가 되어 Pod를 다시 만들지 않고 CPU와 memory를 바꿀 수 있습니다. 1.36에서는 Pod 단위 리소스까지 Beta로 들어와 기본으로 켜져 있고, 1.37에서는 노드가 꽉 차서 resize가 Deferred로 멈출 때 scheduler가 낮은 priority Pod를 밀어내는 기능이 Alpha로 추가됐습니다.
{cue: pause}
왼쪽 표는 EKS 1.36.1에서 직접 측정한 결과입니다. JVM 워밍업처럼 시작할 때만 CPU를 많이 쓰는 앱을 가정해, startup probe가 통과하면 작은 컨트롤러가 CPU를 200m에서 50m로 줄이게 했습니다. requests와 limits를 같게 유지해서 Guaranteed QoS가 그대로였고, restartCount는 0, containerID도 그대로였습니다. 컨테이너를 다시 만들지 않았다는 뜻입니다. resizePolicy는 1.36에서 GA된 MutatingAdmissionPolicy로 webhook 없이 넣었습니다.
{cue: question}
그럼 노드 자동화와는 어떻게 엮일까요. Karpenter는 v1.14.0부터 Pod 크기를 requests와 실제 할당값 중 큰 값으로 봐서 resize 중에도 scheduler와 같은 판단을 합니다. requests가 줄어 노드가 비면 consolidation이 정리할 수 있습니다. 다만 QoS class는 생성 시 정해져 바뀌지 않고, memory를 줄이면 재시작될 수 있습니다. Auto Mode에서의 resize 관련 동작은 AWS 문서에 따로 설명이 없으니 직접 검증하셔야 합니다.

[출처]
- https://kubernetes.io/blog/2026/04/30/kubernetes-v1-36-inplace-pod-level-resources-beta/
- https://kubernetes.io/blog/2026/09/10/kubernetes-v1-37-scheduler-preemption-for-in-place-pod-resize-alpha/
- 실측: https://atomoh.notion.site/Amazon-EKS-1-36-What-s-New-2026-06-3748907d4b018102983bd4a31f243512 하위 페이지 예시 ①, ②
- Karpenter in-place resize 설계: https://github.com/kubernetes-sigs/karpenter/blob/v1.15.0/designs/in-place-pod-vertical-scaling.md
{cue: transition}
이제 줄이는 속도를 정하는 장치, disruption budget입니다.
:::

---
<!-- Slide 4: Disruption budget -->
@type: content
@title: Disruption budget: 한 번에 몇 대까지

## Disruption budget: 한 번에 몇 대까지

:::html
<style>
.ak2-bud { display: grid; grid-template-columns: 1fr 1.1fr; gap: var(--space-4); align-items: start; }
.ak2-calc { display: flex; flex-direction: column; gap: var(--space-2); }
.ak2-row { display: grid; grid-template-columns: 7.5rem 1fr; align-items: center; gap: var(--space-3); font-size: var(--fs-card); }
.ak2-row label { color: var(--text-secondary); }
.ak2-calc .slider-value { min-width: 4rem; }
.ak2-calc .metric-value { font-size: var(--fs-subtitle); }
.ak2-formula { font-family: var(--font-mono); font-size: var(--fs-caption); color: var(--text-secondary); word-break: break-all; }
.ak2-notes { margin-top: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak2-bud">
<pre class="code-block"><span class="key">disruption</span>:
  <span class="key">consolidationPolicy</span>: Balanced
  <span class="key">budgets</span>:
  - <span class="key">nodes</span>: <span class="string">"10%"</span>
  - <span class="key">nodes</span>: <span class="string">"0"</span>
    <span class="key">schedule</span>: <span class="string">"0 0 * * 1-5"</span>  <span class="comment"># UTC</span>
    <span class="key">duration</span>: 9h
    <span class="key">reasons</span>: [<span class="string">"Underutilized"</span>, <span class="string">"Drifted"</span>]</pre>
  <div class="ak2-calc card">
    <div class="ak2-row"><label for="ak2-n">NodePool 노드</label><div class="slider-container"><input type="range" id="ak2-n" min="1" max="200" value="40"><span class="slider-value" id="ak2-n-v">40</span></div></div>
    <div class="ak2-row"><label for="ak2-p">nodes (%)</label><div class="slider-container"><input type="range" id="ak2-p" min="0" max="100" step="5" value="10"><span class="slider-value" id="ak2-p-v">10%</span></div></div>
    <div class="ak2-row"><label for="ak2-d">삭제 중</label><div class="slider-container"><input type="range" id="ak2-d" min="0" max="20" value="1"><span class="slider-value" id="ak2-d-v">1</span></div></div>
    <div class="ak2-row"><label for="ak2-r">NotReady</label><div class="slider-container"><input type="range" id="ak2-r" min="0" max="20" value="0"><span class="slider-value" id="ak2-r-v">0</span></div></div>
    <div class="metric-card"><div class="metric-value" id="ak2-out">-</div><div class="metric-label">지금 허용되는 voluntary disruption 수</div></div>
    <div class="ak2-formula" id="ak2-f"></div>
  </div>
</div>
<div class="card-grid ak2-notes fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="callout callout-info"><strong class="text-info">여러 budget은 최솟값</strong><div class="on-surface-muted">미지정 시 <code>nodes: 10%</code> 하나. Auto Mode 기본도 같습니다.</div></div>
  <div class="callout callout-info"><strong class="text-info">schedule은 UTC만</strong><div class="on-surface-muted">위 예시는 평일 KST 09시부터 9시간 동안 교체 금지입니다.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">만료는 막지 못함</strong><div class="on-surface-muted"><code>expireAfter</code>에 의한 교체는 budget과 무관하게 진행됩니다.</div></div>
</div>
:::

:::script
(function () {
  var ids = ['ak2-n', 'ak2-p', 'ak2-d', 'ak2-r'];
  var el = {};
  for (var i = 0; i < ids.length; i++) { el[ids[i]] = document.getElementById(ids[i]); if (!el[ids[i]]) return; }
  function update() {
    var n = parseInt(el['ak2-n'].value, 10);
    var p = parseInt(el['ak2-p'].value, 10);
    var d = parseInt(el['ak2-d'].value, 10);
    var r = parseInt(el['ak2-r'].value, 10);
    var base = Math.ceil(n * p / 100);
    var allowed = Math.max(0, base - d - r);
    document.getElementById('ak2-n-v').textContent = n;
    document.getElementById('ak2-p-v').textContent = p + '%';
    document.getElementById('ak2-d-v').textContent = d;
    document.getElementById('ak2-r-v').textContent = r;
    document.getElementById('ak2-out').textContent = allowed + '대';
    document.getElementById('ak2-f').textContent = 'roundup(' + n + ' x ' + p + '%) = ' + base + ', 빼기 삭제 중 ' + d + ', 빼기 NotReady ' + r;
  }
  ids.forEach(function (id) { el[id].addEventListener('input', update); });
  update();
})();
:::

:::notes
{timing: 2.5min}
[요약]
- budget 필드: nodes(정수 또는 %, 올림), schedule(cron, UTC만), duration(schedule과 함께), reasons(Drifted, Underutilized, Empty, Unhealthy)
- 허용 수 = roundup(전체 x %) - 삭제 중 - NotReady. 여러 budget이 겹치면 가장 작은 값
- 미지정 시 nodes 10% 하나, Auto Mode 기본도 10%
- expireAfter 만료는 budget으로 막을 수 없습니다.

budget은 voluntary disruption, 즉 consolidation이나 Drift 같은 자발적 교체를 한 번에 몇 대까지 허용할지 정합니다. 왼쪽 예시는 budget 두 개입니다. 평소에는 10%까지, 그리고 평일 특정 시간대에는 Underutilized와 Drifted 사유로는 0대, 즉 교체 금지입니다.
{cue: pause}
schedule은 UTC만 받습니다. 예시의 "0 0 * * 1-5"는 UTC 자정이니 한국 시간으로 평일 오전 9시이고, duration 9h면 오후 6시까지입니다. 업무 시간 보호를 KST로 쓰면 9시간 어긋나니 주의하세요. reasons에는 Drifted, Underutilized, Empty, 그리고 v1.15에서 추가된 Unhealthy를 넣을 수 있습니다.
{cue: demo}
오른쪽 계산기로 공식을 보겠습니다. 허용 수는 전체 노드에 퍼센트를 곱해 올림한 값에서, 이미 삭제 중인 노드와 NotReady 노드를 뺀 값입니다. 40대에 10%면 4대이고, 삭제 중 1대를 빼면 3대입니다. NotReady 슬라이더를 올려 보면 허용 수가 바로 줄어듭니다. 장애가 난 상황에서 교체가 더 보수적으로 바뀌는 구조입니다. 참고로 Unhealthy 사유는 NotReady를 빼지 않습니다.
여러 budget이 동시에 해당되면 가장 작은 값이 적용됩니다. 지정하지 않으면 nodes 10% 하나가 기본이고, Auto Mode의 기본도 10%입니다.
{cue: question}
그럼 업무 시간에 노드가 절대 안 바뀔까요. 아닙니다. 오른쪽 아래 박스처럼, expireAfter에 의한 만료는 budget이 막지 못합니다. 이것이 다음 슬라이드 주제입니다.

[출처]
- https://karpenter.sh/docs/concepts/disruption/ (budgets, 계산식, 만료 예외)
- https://docs.aws.amazon.com/eks/latest/userguide/create-node-pool.html (Auto Mode 기본 budget 10%)
{cue: transition}
Drift와 만료, 노드가 교체되는 두 가지 이유를 보겠습니다.
:::

---
<!-- Slide 5: Drift와 만료 -->
@type: content
@title: Drift와 만료: 노드는 결국 교체된다

## Drift와 만료: 노드는 결국 교체된다

:::html
<style>
.ak2-two { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3); margin-top: var(--space-3); }
.ak2-life { width: 100%; font-size: var(--fs-card); word-break: keep-all; margin-top: var(--space-3); }
.data-table th { text-transform: none; letter-spacing: normal; font-size: var(--fs-card); }
.ak2-take { margin-top: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">Drift</button>
  <button class="tab-btn">만료와 grace period</button>
</div>
<div class="tc">
  <div class="ak2-two">
    <div class="card"><strong class="text-accent">Drift를 일으킴</strong><div class="on-surface-muted">NodePool template과 NodeClass spec 변경. requirements, subnet, SG, AMI는 resolve 결과로 비교</div></div>
    <div class="card"><strong class="text-accent">Drift를 일으키지 않음</strong><div class="on-surface-muted"><code>spec.weight</code>, <code>spec.limits</code>, <code>spec.disruption.*</code></div></div>
    <div class="card"><strong class="text-accent">AMI는 alias로 고정</strong><div class="on-surface-muted"><code>al2023@v20261012</code>처럼 pin. <code>@latest</code>는 새 AMI마다 전체 Drift라 프로덕션 비권장</div></div>
    <div class="card"><strong class="text-accent">Auto Mode는 AMI가 Drift 신호</strong><div class="on-surface-muted">새 AMI가 대략 주 1회 나오고 Drift로 롤링. <code>advancedCompute</code> 변경도 in-place 없이 Drift</div></div>
  </div>
</div>
<div class="tc" hidden>
  <table class="data-table ak2-life">
    <thead><tr><th>항목</th><th>Self-managed v1.15</th><th>Auto Mode</th></tr></thead>
    <tbody>
      <tr><td><code>expireAfter</code> 기본</td><td>720h (30일)</td><td>336h (14일)</td></tr>
      <tr><td>최대 수명</td><td>상한 없음, <code>Never</code> 허용</td><td>21일 강제</td></tr>
      <tr><td><code>terminationGracePeriod</code></td><td>CRD 기본값 없음 (무제한 대기)</td><td>NodeClaim에 24h 적용</td></tr>
    </tbody>
  </table>
  <div class="callout callout-info ak2-take"><strong class="text-info">실제 최대 수명</strong>: <code>expireAfter</code> + <code>terminationGracePeriod</code>. grace period가 지나면 남은 Pod는 강제 삭제됩니다.</div>
</div>
<div class="callout callout-danger ak2-take fragment fade-up" data-fragment-index="1"><strong class="text-danger">만료는 강제입니다</strong>: NodePool budget을 무시합니다. <code>expireAfter</code> 값을 바꾸면 기존 NodeClaim은 Drift로 교체됩니다.</div>
:::

:::notes
{timing: 2min}
[요약]
- Drift: NodePool template, NodeClass spec 변경으로 발생. weight, limits, disruption 필드는 Drift를 일으키지 않음
- AMI는 al2023@v20261012처럼 alias를 pin. @latest는 새 AMI마다 모든 노드가 Drift되어 프로덕션 비권장
- Auto Mode는 새 AMI(대략 주 1회)와 advancedCompute 변경이 Drift로 교체됨
- 만료: expireAfter 기본 720h(upstream), 336h(Auto Mode), Auto Mode 최대 21일. terminationGracePeriod는 upstream 기본 없음, Auto Mode NodeClaim 24h
- 만료는 budget을 무시하는 강제 교체

노드가 교체되는 이유는 크게 두 가지, Drift와 만료입니다. 첫 번째 탭 Drift부터 보겠습니다. Drift는 "지금 노드가 선언된 설정과 다르다"는 뜻입니다. NodePool template이나 NodeClass spec을 바꾸면 해시를 비교해 Drift로 판단하고, requirements, subnet, security group, AMI는 실제 resolve된 결과로 비교합니다. 반대로 weight, limits, disruption 설정은 바꿔도 노드를 교체하지 않습니다.
{cue: pause}
AMI가 가장 흔한 Drift 원인입니다. 직접 운영할 때는 al2023@v20261012처럼 날짜 버전으로 고정하세요. @latest는 새 AMI마다 모든 노드가 Drift 대상이 되어 프로덕션에서 권장하지 않습니다. Auto Mode는 AWS가 대략 주 1회 새 AMI를 내고 그것이 Drift 신호가 되며, advancedCompute 변경도 Drift로 교체됩니다.
{cue: demo}
두 번째 탭이 만료입니다. expireAfter 기본값은 upstream 720시간, Auto Mode 336시간이고, Auto Mode는 최대 21일입니다. terminationGracePeriod는 upstream 기본값이 없고 Auto Mode는 24시간입니다. 실제 최대 수명은 둘을 더한 값입니다.
빨간 박스가 핵심입니다. 만료는 budget을 무시하는 강제 교체입니다. 업무 시간 보호 budget을 걸어도 만료는 진행되니, 만료 주기와 PDB를 함께 설계해야 합니다.

[출처]
- https://karpenter.sh/docs/concepts/disruption/, https://karpenter.sh/docs/tasks/managing-amis/
- https://docs.aws.amazon.com/eks/latest/userguide/create-node-pool.html, auto-security.html (21일), automode-learn-instances.html (주간 AMI)
- SSM /aws/service/eks/optimized-ami/1.37/amazon-linux-2023/x86_64/standard/recommended/image_id (2026-10-20 조회)
{cue: transition}
계획된 교체 말고, AWS가 2분 전에 알려 주는 교체도 있습니다. Spot 중단입니다.
:::

---
<!-- Slide 6: Spot 중단 처리 -->
@type: content
@title: Spot 중단: 2분 경고는 누가 받나

## Spot 중단: 2분 경고는 누가 받나

:::html
<style>
.ak2-spot { display: grid; grid-template-columns: 1.2fr 1fr; gap: var(--space-4); align-items: start; margin-bottom: var(--space-3); }
.ak2-col { border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-3); }
.ak2-col h4 { margin: 0 0 var(--space-2); font-size: var(--fs-body); }
.ak2-rules { margin: 0; padding-left: var(--space-4); font-size: var(--fs-card); color: var(--text-secondary); word-break: keep-all; }
.ak2-rules li { margin-bottom: var(--space-1); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak2-spot">
  <div class="ak2-col fragment fade-right" data-fragment-index="1">
    <h4 class="text-accent">Self-managed: SQS와 EventBridge를 직접</h4>
    <ul class="ak2-rules">
      <li>SQS interruption queue, Helm <code>settings.interruptionQueue</code>로 연결</li>
      <li>EventBridge rule 5개: Spot Interruption Warning, Rebalance, State-change, AWS Health, Capacity Reservation Interruption</li>
      <li>Spot 경고를 받으면 drain과 새 노드 생성을 병행</li>
      <li>Rebalance Recommendation은 이벤트 기록만 함</li>
    </ul>
  </div>
  <div class="ak2-col fragment fade-left" data-fragment-index="2">
    <h4 class="text-accent">Auto Mode: AWS가 처리</h4>
    <ul class="ak2-rules">
      <li>Spot 중단 알림, EC2 health 이벤트, 상태 검사 실패를 자동 처리</li>
      <li>사용자가 SQS나 EventBridge를 구성하지 않음</li>
      <li>ARC zonal shift 시 해당 AZ의 노드 생성과 자발적 disruption 중지</li>
    </ul>
  </div>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="3">
  <div class="callout callout-warning"><strong class="text-warning">queue를 안 붙이면 비활성</strong><div class="on-surface-muted">self-managed에서 <code>interruptionQueue</code>가 없으면 interruption 처리가 꺼집니다.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">FIS EC2 action은 Auto Mode 미지원</strong><div class="on-surface-muted"><code>SendSpotInstanceInterruptions</code> 포함. Spot 중단 리허설은 self-managed 노드에서 합니다.</div></div>
</div>
:::

:::notes
{timing: 2min}
[요약]
- self-managed: SQS queue와 EventBridge rule 5개를 만들고 Helm settings.interruptionQueue로 연결. 없으면 interruption 처리 비활성
- Spot 경고(2분)를 받으면 drain과 새 노드 생성을 병행, Rebalance Recommendation은 이벤트만 기록
- Auto Mode: Spot 중단, EC2 health, 상태 검사 실패를 AWS가 자동 처리. 사용자 구성 없음
- Auto Mode 인스턴스에는 FIS EC2 action(SendSpotInstanceInterruptions 등)을 쓸 수 없음

Spot 인스턴스는 회수 2분 전에 경고가 옵니다. 이 경고를 누가 받아서 처리하느냐가 두 방식의 차이입니다.
왼쪽 self-managed는 사용자가 수신 경로를 만듭니다. Karpenter가 제공하는 CloudFormation 템플릿으로 SQS queue와 EventBridge rule 다섯 개를 만들고, Helm 값 settings.interruptionQueue에 queue 이름을 넣습니다. Spot 경고를 받으면 Karpenter는 기존 노드 drain과 대체 노드 생성을 동시에 진행해서 2분을 최대한 활용합니다. Rebalance Recommendation은 이벤트로만 남기고 노드를 건드리지 않습니다.
{cue: pause}
주의할 점이 있습니다. interruptionQueue를 지정하지 않아도 Karpenter는 정상적으로 설치되고 돌아갑니다. 그런데 이 경우 interruption 처리 자체가 꺼진 상태입니다. 설치 후 Helm 값을 꼭 확인하세요.
오른쪽 Auto Mode는 이 모든 것을 AWS가 처리합니다. Spot 중단 알림, EC2 health 이벤트, 상태 검사 실패까지 자동이고 사용자가 queue를 만들 필요가 없습니다. ARC zonal shift와도 연동되어 영향받은 AZ에는 노드를 만들지 않습니다.
{cue: question}
그럼 Auto Mode에서 Spot 중단을 테스트해 볼 수 있을까요. AWS FIS의 EC2 action, Spot interruption을 포함해 reboot, stop, terminate 같은 action은 Auto Mode 인스턴스에서 지원되지 않습니다. 그래서 오늘 데모 영상의 Spot 중단 장면은 self-managed Karpenter 노드에서 FIS로 재현했습니다.

[출처]
- https://karpenter.sh/docs/concepts/disruption/#interruption, Karpenter v1.15 CloudFormation template (preview 경로)
- https://docs.aws.amazon.com/eks/latest/userguide/automode.html (Automated Components, FIS 미지원 action, zonal shift)
{cue: transition}
마지막으로, 이렇게 노드가 바뀌는 동안 애플리케이션을 지키는 장치를 보겠습니다.
:::

---
<!-- Slide 7: 앱 보호 -->
@type: content
@title: 교체 중 앱을 지키는 장치들

## 교체 중 앱을 지키는 장치들

:::html
<style>
.ak2-guard { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-3); margin-bottom: var(--space-3); }
.ak2-scope { display: inline-block; font-size: var(--fs-caption); color: var(--text-secondary); margin-left: var(--space-2); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak2-guard">
  <div class="card fragment fade-up" data-fragment-index="1"><strong class="text-accent">PodDisruptionBudget</strong><span class="ak2-scope">Pod 그룹</span><div class="on-surface-muted">drain 중 동시에 빠질 수 있는 Pod 수를 제한합니다. Karpenter와 Auto Mode 모두 존중</div></div>
  <div class="card fragment fade-up" data-fragment-index="2"><strong class="text-accent">karpenter.sh/do-not-disrupt</strong><span class="ak2-scope">Pod 또는 Node</span><div class="on-surface-muted">자발적 disruption 대상에서 뺍니다. 배치 작업처럼 끊으면 안 되는 Pod에 사용</div></div>
  <div class="card fragment fade-up" data-fragment-index="3"><strong class="text-accent">karpenter.sh/disruption-cost</strong><span class="ak2-scope">Pod, v1.15</span><div class="on-surface-muted">consolidation 비용 가중치. <code>pod-deletion-cost</code>로 조정하는 방식은 deprecated</div></div>
  <div class="card fragment fade-up" data-fragment-index="4"><strong class="text-accent">karpenter.sh/do-not-repair</strong><span class="ak2-scope">Node, v1.15 신규</span><div class="on-surface-muted">Node Auto Repair 대상에서 제외합니다.</div></div>
</div>
<div class="callout callout-warning fragment fade-up" data-fragment-index="5"><strong class="text-warning">보호에는 끝이 있습니다</strong>: <code>terminationGracePeriod</code>를 설정하면 blocking PDB나 do-not-disrupt가 있어도 Drift 교체가 진행됩니다. Auto Mode는 21일 최대 수명에서 blocking PDB가 있으면 개입이 필요할 수 있습니다.</div>
:::

:::notes
{timing: 2min}
[요약]
- PDB: drain 중 동시에 빠지는 Pod 수 제한, Karpenter와 Auto Mode 모두 존중
- karpenter.sh/do-not-disrupt(Pod/Node): 자발적 disruption 제외
- karpenter.sh/disruption-cost(v1.15): consolidation 가중치, pod-deletion-cost 방식은 deprecated. do-not-repair(Node, v1.15 신규)
- terminationGracePeriod가 있으면 blocking PDB나 do-not-disrupt가 있어도 Drift 교체 진행. Auto Mode 21일 상한에서는 개입 필요 가능

지금까지 노드를 바꾸는 규칙을 봤으니, 이제 애플리케이션 쪽 방어 장치입니다. 첫째는 PodDisruptionBudget입니다. 노드를 drain할 때 한 번에 빠질 수 있는 Pod 수를 제한하고, Karpenter와 Auto Mode 모두 이를 존중합니다. 가장 기본이니 replica가 둘 이상인 서비스에는 꼭 두세요.
{cue: pause}
둘째, karpenter.sh/do-not-disrupt annotation입니다. Pod나 Node에 붙이면 consolidation 같은 자발적 disruption 대상에서 빠집니다. 끊기면 처음부터 다시 해야 하는 배치 작업에 적합합니다.
셋째, v1.15에서 consolidation 대상을 조정하는 방법이 바뀌었습니다. karpenter.sh/disruption-cost annotation을 쓰고, 기존처럼 controller.kubernetes.io/pod-deletion-cost로 조정하는 방식은 deprecated입니다. Balanced 정책에서 이 값이 높으면 consolidation이 막힐 수도 있습니다. 넷째, v1.15에 새로 생긴 karpenter.sh/do-not-repair는 Node에 붙여 auto repair 대상에서 제외합니다.
{cue: question}
그럼 이 장치들로 노드를 영원히 붙잡아 둘 수 있을까요. 노란 박스처럼, terminationGracePeriod가 설정되어 있으면 blocking PDB나 do-not-disrupt가 있어도 Drift 교체는 결국 진행됩니다. Auto Mode는 21일 최대 수명이 있어서, 그때까지 PDB가 계속 막고 있으면 사람이 개입해야 할 수 있습니다. 보호 장치는 교체를 늦추는 것이지 없애는 것이 아니라고 기억해 주세요.

[출처]
- https://karpenter.sh/docs/concepts/disruption/ (do-not-disrupt, terminationGracePeriod)
- https://karpenter.sh/docs/upgrading/upgrade-guide/#upgrading-to-1150 (disruption-cost, do-not-repair)
- https://docs.aws.amazon.com/eks/latest/userguide/automode.html (PDB, NDB 존중과 21일)
{cue: transition}
여기까지가 3부 스케일링과 disruption이었습니다. 4부에서는 이 모든 것을 운영하는 관점, 업그레이드와 관측, 비용을 보겠습니다.
:::
