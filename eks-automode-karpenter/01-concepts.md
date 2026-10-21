---
remarp: true
block: 01-concepts
---

---
<!-- Slide 1: 세션 커버 -->
@type: cover

# EKS Auto Mode와 Karpenter

노드 자동화 운영

EKS 1.37, Karpenter v1.15 기준 (2026-10-20 확인)

:::notes
{timing: 1min}
[요약]
- 90분 L300 세션: 플랫폼 엔지니어, SRE, 아키텍트 대상
- 노드를 누가 만들고, 언제 바꾸고, 어떻게 지키는지를 Auto Mode와 self-managed Karpenter 양쪽에서 봅니다.
- 모든 버전과 기본값은 2026-10-20 기준으로 확인한 값입니다.

안녕하세요. 오늘은 EKS Auto Mode와 Karpenter를 90분 동안 다룹니다. 두 가지는 따로 노는 기술이 아니라, 같은 Karpenter API를 누가 운영하느냐의 차이입니다. 그래서 오늘은 둘을 나란히 놓고 노드가 생기고, 바뀌고, 사라지는 과정을 따라가 보겠습니다.
{cue: pause}
버전 이야기가 많이 나옵니다. EKS 1.37과 Karpenter v1.15.0이 나온 지 얼마 되지 않았고, 기본값 몇 가지가 바뀌었습니다. 오늘 숫자는 모두 2026년 10월 20일에 공식 문서와 릴리스 노트로 다시 확인한 값입니다.
{cue: question}
지금 운영 중인 클러스터에서 Karpenter를 직접 설치해 쓰고 계신 분, 그리고 Auto Mode를 쓰고 계신 분이 각각 얼마나 되시는지 손을 한번 들어 주시겠어요?
{cue: transition}
전체 순서부터 보겠습니다.
:::

---
<!-- Slide 2: 아젠다 -->
@type: agenda

## 오늘 세션 구성

1. 개념: 왜 노드 자동화인가
2. 구조: NodePool, NodeClass, Auto Mode
3. 스케일링과 disruption
4. Auto Mode 심화와 운영: 설정, 용량, 진단, 비용, 마이그레이션
5. 데모 영상 4편
6. 마무리

:::notes
{timing: 1min}
[요약]
- 1, 2부(약 15분): Karpenter 제어 루프, API 구조, Auto Mode 책임 분담, 버전
- 3부(약 20분): 프로비저닝, consolidation과 Balanced 점수 애니메이션, 스케줄러 점수 전략, in-place resize, budget, drift와 만료, Spot, 앱 보호
- 4부(약 31분): Auto Mode 켜기와 built-in 풀, NodeClass와 보안 기본값, Spot과 예약 용량, GPU와 EFA, ARC zonal shift, 업그레이드, 로그와 진단, 비용 귀속, 마이그레이션, 선택 체크리스트
- 5, 6부(약 24분): 데모 영상 4편과 마무리

여섯 파트로 진행합니다. 앞의 두 파트에서 개념과 구조를 잡고, 3부에서 노드를 늘리고 줄이고 교체하는 disruption을 자세히 보고, 스케줄러 점수 전략과 in-place resize도 함께 다룹니다. 4부는 Auto Mode를 실제로 운영할 때 필요한 내용입니다. 켜는 방법과 built-in 풀, NodeClass 필드와 바꿀 수 없는 보안 기본값, Spot과 예약 용량, GPU와 EFA, AZ 장애, 업그레이드, SSH 없이 진단하는 방법, 비용, 마이그레이션, 그리고 무엇을 고를지까지 봅니다.
{cue: pause}
후반 24분은 데모 영상 네 편입니다. 앞에서 설명한 동작을 실제 클러스터에서 확인하는 순서로 구성했으니, 이론 파트에서 궁금한 점이 생기면 메모해 두셨다가 영상과 연결해 보셔도 좋습니다.
{cue: transition}
먼저 노드 자동화가 왜 필요한지부터 보겠습니다.
:::

---
<!-- Slide 3: 왜 노드 자동화인가 -->
@type: content
@title: 1부: Pending Pod가 노드를 부른다

## 1부: Pending Pod가 노드를 부른다

:::html
<style>
.ak1-cmp { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); margin-bottom: var(--space-3); }
.ak1-col { border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-3); }
.ak1-col h4 { margin: 0 0 var(--space-2); font-size: var(--fs-body); }
.ak1-col ul { margin: 0; padding-left: var(--space-4); font-size: var(--fs-card); color: var(--text-secondary); word-break: keep-all; }
.ak1-col li { margin-bottom: var(--space-1); }
.ak1-new { border-color: var(--accent); background: var(--accent-subtle); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak1-cmp">
  <div class="ak1-col fragment fade-right" data-fragment-index="1">
    <h4 class="text-warning">고정된 노드 그룹 중심</h4>
    <ul>
      <li>인스턴스 유형과 크기를 그룹마다 미리 정함</li>
      <li>워크로드 모양이 바뀌면 그룹을 새로 설계</li>
      <li>비어 가는 노드를 줄이는 판단은 사람이 함</li>
      <li>AMI 교체와 노드 수명 관리도 별도 작업</li>
    </ul>
  </div>
  <div class="ak1-col ak1-new fragment fade-left" data-fragment-index="2">
    <h4 class="text-accent">Pending Pod 기반 프로비저닝</h4>
    <ul>
      <li>스케줄되지 못한 Pod의 요구 사항이 수요 신호</li>
      <li>requirements를 만족하는 인스턴스 유형 중에서 선택</li>
      <li>남는 노드는 consolidation으로 회수</li>
      <li>설정이나 AMI가 바뀌면 Drift, 오래되면 만료로 교체</li>
    </ul>
  </div>
</div>
<div class="callout callout-info fragment fade-up" data-fragment-index="3">
  <strong class="text-info">핵심 질문이 바뀝니다</strong>: "몇 대를 띄울까"가 아니라 "어떤 조건의 노드를 허용하고, 언제 바꿔도 되는가"를 선언합니다.
</div>
:::

:::notes
{timing: 2min}
[요약]
- 노드 그룹 중심 운영은 인스턴스 유형, 수량, 교체를 사람이 미리 정합니다.
- Karpenter는 Pending Pod를 수요 신호로 보고 조건에 맞는 노드를 직접 만듭니다.
- 만드는 것뿐 아니라 회수(consolidation)와 교체(Drift, 만료)까지 하나의 루프로 다룹니다.

왼쪽은 우리가 익숙한 방식입니다. 노드 그룹마다 인스턴스 유형을 정해 두고, 워크로드가 바뀌면 그룹을 다시 설계합니다. 노드가 비어 가는지, AMI를 언제 바꿀지도 사람이 따로 챙깁니다.
{cue: pause}
오른쪽이 Karpenter의 방식입니다. 출발점은 Pending Pod입니다. 스케줄러가 자리를 찾지 못한 Pod의 CPU, 메모리, node selector, toleration 같은 요구 사항을 보고, NodePool에 허용된 조건 안에서 맞는 인스턴스를 고릅니다. 그리고 여기서 끝나지 않습니다. 남는 노드는 consolidation으로 줄이고, 설정이나 AMI가 바뀌면 Drift로, 정해진 수명이 지나면 만료로 교체합니다.
그래서 운영자가 선언하는 것이 달라집니다. 몇 대를 띄울지가 아니라, 어떤 노드를 허용하고 언제 바꿔도 되는지를 정합니다. 오늘 3부 전체가 이 "언제 바꿔도 되는가"에 대한 이야기입니다.
{cue: transition}
그럼 Pending Pod 하나가 노드가 되기까지 누가 무엇을 하는지 순서대로 보겠습니다.
:::

---
<!-- Slide 4: Karpenter 제어 루프 -->
@type: content
@title: 제어 루프: 누가 무엇을 하나

## 제어 루프: 누가 무엇을 하나

:::html
<style>
.ak1-loop { display: grid; grid-template-columns: repeat(5, 1fr); gap: var(--space-3); margin-bottom: var(--space-3); }
.ak1-step { border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-3); font-size: var(--fs-card); word-break: keep-all; overflow-wrap: break-word; }
.ak1-num { display: inline-flex; align-items: center; justify-content: center; width: 1.8em; height: 1.8em; border-radius: 50%; background: var(--accent-subtle); color: var(--accent); font-weight: var(--weight-bold); margin-bottom: var(--space-2); }
.ak1-who { display: block; font-size: var(--fs-caption); color: var(--text-secondary); margin-top: var(--space-2); }
.ak1-step strong { display: block; }
.ak1-k { border-color: var(--accent); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak1-loop">
  <div class="ak1-step fragment fade-up" data-fragment-index="1"><span class="ak1-num">1</span><strong>Pod가 Pending</strong>자리를 찾지 못한 Pod를 unschedulable로 표시<span class="ak1-who">kube-scheduler</span></div>
  <div class="ak1-step ak1-k fragment fade-up" data-fragment-index="2"><span class="ak1-num">2</span><strong>NodeClaim 생성</strong>NodePool 조건 안에서 인스턴스 후보를 계산하고 NodeClaim을 만듦<span class="ak1-who">Karpenter controller</span></div>
  <div class="ak1-step ak1-k fragment fade-up" data-fragment-index="3"><span class="ak1-num">3</span><strong>EC2 시작</strong>NodeClass의 subnet, SG, AMI로 인스턴스를 띄움<span class="ak1-who">Karpenter cloud provider, EC2</span></div>
  <div class="ak1-step fragment fade-up" data-fragment-index="4"><span class="ak1-num">4</span><strong>노드 Ready</strong>kubelet이 클러스터에 등록, NodeClaim이 Node와 연결<span class="ak1-who">kubelet</span></div>
  <div class="ak1-step fragment fade-up" data-fragment-index="5"><span class="ak1-num">5</span><strong>Pod 바인딩</strong>새 노드에 Pod를 배치<span class="ak1-who">kube-scheduler</span></div>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="6">
  <div class="callout callout-info"><strong class="text-info">Karpenter는 Pod를 배치하지 않음</strong><div class="on-surface-muted">노드를 만들 뿐이고, 바인딩은 여전히 kube-scheduler가 합니다.</div></div>
  <div class="callout callout-info"><strong class="text-info">NodeClaim이 노드 한 대의 기록</strong><div class="on-surface-muted">교체, 만료, 중단 판단도 NodeClaim 단위로 이루어집니다.</div></div>
  <div class="callout callout-info"><strong class="text-info">Auto Mode도 같은 루프</strong><div class="on-surface-muted">2번과 3번을 AWS가 운영하는 관리형 Karpenter가 맡습니다.</div></div>
</div>
:::

:::notes
{timing: 3min}
[요약]
- 다섯 단계: Pending 표시(scheduler), NodeClaim 생성(Karpenter), EC2 시작(Karpenter cloud provider), Ready(kubelet), 바인딩(scheduler)
- Karpenter는 노드를 만들 뿐 Pod를 배치하지 않습니다.
- NodeClaim은 노드 한 대에 대한 Karpenter의 기록이고, disruption 판단의 단위입니다.
- Auto Mode에서도 루프는 같고 2, 3번을 AWS가 운영합니다.

Pending Pod 하나가 노드가 되기까지를 다섯 단계로 나눠 보겠습니다. 첫 단계는 kube-scheduler입니다. 들어갈 노드가 없으면 Pod를 unschedulable로 표시합니다. Karpenter는 이 Pod들을 보고 있다가, NodePool이 허용하는 조건 안에서 어떤 인스턴스 유형이면 이 Pod들이 들어갈지 계산하고 NodeClaim이라는 객체를 만듭니다.
{cue: pause}
세 번째 단계에서 Karpenter의 AWS cloud provider가 NodeClass에 적힌 subnet, security group, AMI로 EC2 인스턴스를 띄웁니다. 네 번째로 kubelet이 클러스터에 등록하면 NodeClaim과 Node가 연결되고, 다섯 번째로 kube-scheduler가 그 노드에 Pod를 배치합니다.
여기서 자주 오해하는 부분이 있습니다. Karpenter는 Pod를 배치하지 않습니다. 노드를 만들 뿐이고, 배치는 여전히 스케줄러가 합니다. 그래서 affinity나 topology spread 같은 스케줄링 규칙은 그대로 유효하고, Karpenter는 그 규칙을 만족할 노드를 준비하는 역할입니다.
{cue: question}
그럼 NodeClaim은 왜 따로 있을까요. 노드 한 대에 대한 Karpenter의 기록이라서, 나중에 교체할지, 만료됐는지, Spot 중단을 받았는지를 모두 NodeClaim 단위로 판단합니다. 3부에서 계속 이 이름이 나옵니다.
Auto Mode도 루프는 같습니다. 2번과 3번을 AWS가 운영하는 관리형 Karpenter가 맡는다는 점만 다릅니다.
{cue: transition}
이 루프가 읽는 설정, NodePool과 NodeClass를 보겠습니다.
:::

---
<!-- Slide 5: NodePool vs NodeClass -->
@type: content
@title: 2부: NodePool과 NodeClass의 분업

## 2부: NodePool과 NodeClass의 분업

:::html
<style>
.ak1-tab-body { display: grid; grid-template-columns: 1.1fr 1fr; gap: var(--space-4); align-items: start; margin-top: var(--space-3); }
.ak1-api { font-family: var(--font-mono); font-size: var(--fs-card); color: var(--accent); margin-bottom: var(--space-2); }
.ak1-fields { margin: 0; padding-left: var(--space-4); font-size: var(--fs-card); color: var(--text-secondary); word-break: keep-all; }
.ak1-fields li { margin-bottom: var(--space-1); }
.ak1-fields code { color: var(--text-primary); }
.ak1-take { margin-top: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">NodePool (공통)</button>
  <button class="tab-btn">EC2NodeClass (직접 운영)</button>
  <button class="tab-btn">NodeClass (Auto Mode)</button>
</div>
<div class="tc">
  <div class="ak1-tab-body">
    <div>
      <div class="ak1-api">karpenter.sh/v1, kind: NodePool</div>
      <ul class="ak1-fields">
        <li><code>template.spec.requirements</code>: 허용할 인스턴스 조건</li>
        <li><code>disruption</code>: consolidation 정책, budget</li>
        <li><code>template.spec.expireAfter</code>, <code>terminationGracePeriod</code></li>
        <li><code>limits</code>, <code>weight</code>, <code>nodeClassRef</code></li>
      </ul>
    </div>
    <div class="callout callout-info"><strong class="text-info">무엇을, 언제 바꿀지</strong><div class="on-surface-muted">어떤 노드를 허용하고 언제 회수, 교체할지를 정합니다. Auto Mode와 직접 운영이 같은 API를 씁니다.</div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="ak1-tab-body">
    <div>
      <div class="ak1-api">karpenter.k8s.aws/v1, kind: EC2NodeClass</div>
      <ul class="ak1-fields">
        <li><code>amiSelectorTerms</code>: alias, id, name, tags, ssmParameter</li>
        <li><code>subnetSelectorTerms</code>, <code>securityGroupSelectorTerms</code></li>
        <li><code>role</code> 또는 <code>instanceProfile</code></li>
        <li><code>kubelet</code>, <code>userData</code></li>
      </ul>
    </div>
    <div class="callout callout-info"><strong class="text-info">어디에, 어떤 이미지로</strong><div class="on-surface-muted">AMI, 네트워크, IAM, 부팅 설정을 사용자가 정합니다. Karpenter가 launch template을 만듭니다.</div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="ak1-tab-body">
    <div>
      <div class="ak1-api">eks.amazonaws.com/v1, kind: NodeClass</div>
      <ul class="ak1-fields">
        <li><code>role</code> 또는 <code>instanceProfile</code></li>
        <li><code>subnetSelectorTerms</code>, <code>securityGroupSelectorTerms</code></li>
        <li><code>ephemeralStorage</code>, <code>advancedNetworking</code></li>
        <li><code>advancedCompute</code>: kubelet, sysctl, hugepages 일부</li>
      </ul>
    </div>
    <div class="callout callout-info"><strong class="text-info">AMI 필드가 없음</strong><div class="on-surface-muted">OS는 AWS가 고르는 Bottlerocket 변형입니다. launch template, userData, SSH, SSM도 쓰지 않습니다.</div></div>
  </div>
</div>
<div class="callout callout-warning ak1-take fragment fade-up" data-fragment-index="1"><strong class="text-warning">라벨 접두사도 다름</strong>: 직접 운영은 <code>karpenter.k8s.aws/instance-*</code>, Auto Mode는 <code>eks.amazonaws.com/instance-*</code>. NodePool을 옮길 때 requirements 키를 바꿔야 합니다.</div>
:::

:::notes
{timing: 3min}
[요약]
- NodePool(karpenter.sh/v1)은 "무엇을, 언제": requirements, disruption, 수명, limits. Auto Mode와 직접 운영이 공통으로 사용
- EC2NodeClass(karpenter.k8s.aws/v1)는 "어디에, 어떤 이미지로": AMI, subnet, SG, role, kubelet, userData
- Auto Mode NodeClass(eks.amazonaws.com/v1)는 AMI 필드가 없고, advancedCompute로 kubelet, sysctl, hugepages 일부만 조정
- 라벨 접두사가 karpenter.k8s.aws/instance-* 와 eks.amazonaws.com/instance-* 로 다릅니다.

여기서 2부 구조로 넘어갑니다. Karpenter 설정은 두 객체로 나뉩니다. 첫 번째 탭 NodePool은 karpenter.sh/v1 API이고, 어떤 노드를 허용할지, 언제 회수하고 교체할지를 정합니다. 이 API는 Auto Mode와 직접 운영하는 Karpenter가 똑같이 씁니다.
{cue: demo}
두 번째 탭을 눌러 주세요. 직접 운영할 때의 EC2NodeClass는 karpenter.k8s.aws/v1이고, AMI를 고르는 amiSelectorTerms, subnet과 security group, IAM role, kubelet과 userData까지 사용자가 정합니다. launch template은 Karpenter가 만들어 줍니다.
세 번째 탭이 Auto Mode의 NodeClass입니다. API 그룹이 eks.amazonaws.com/v1로 바뀌고, 가장 큰 차이는 AMI 필드가 없다는 점입니다. OS는 AWS가 고르는 Bottlerocket 변형이고 userData나 SSH, SSM 접속도 없습니다. 대신 advancedCompute로 kubelet의 maxPods, eviction, 허용 목록에 있는 sysctl과 hugepages는 조정할 수 있습니다. 필드 전체는 4부에서 다시 봅니다.
{cue: pause}
마지막으로 라벨입니다. NodePool requirements에서 인스턴스 계열을 고를 때 직접 운영은 karpenter.k8s.aws/instance-category, Auto Mode는 eks.amazonaws.com/instance-category를 씁니다. 마이그레이션할 때 이 키를 바꾸지 않으면 조건이 맞지 않습니다.

[출처]
- https://docs.aws.amazon.com/eks/latest/userguide/create-node-class.html (advancedCompute 필드)
- https://docs.aws.amazon.com/eks/latest/userguide/create-node-pool.html
- https://karpenter.sh/docs/concepts/nodeclasses/
{cue: transition}
그럼 Auto Mode에서 AWS가 정확히 어디까지 맡는지 보겠습니다.
:::

---
<!-- Slide 6: Auto Mode 책임 분담 -->
@type: content
@title: Auto Mode는 Karpenter를 AWS가 운영

## Auto Mode는 Karpenter를 AWS가 운영

:::html
<style>
.ak1-resp { width: 100%; font-size: var(--fs-card); word-break: keep-all; overflow-wrap: break-word; margin-bottom: var(--space-3); }
.data-table th { text-transform: none; letter-spacing: normal; font-size: var(--fs-card); }
.ak1-aws { color: var(--accent); font-weight: var(--weight-bold); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<table class="data-table ak1-resp">
  <thead><tr><th>항목</th><th>EKS Auto Mode</th><th>Self-managed Karpenter v1.15</th></tr></thead>
  <tbody>
    <tr class="fragment fade-up" data-fragment-index="1"><td>Karpenter controller</td><td><span class="ak1-aws">AWS 관리</span>, 클러스터 Pod 아님, 버전 비공개</td><td>사용자 노드의 Pod, Helm과 CRD chart로 업그레이드</td></tr>
    <tr class="fragment fade-up" data-fragment-index="2"><td>AMI, OS</td><td><span class="ak1-aws">AWS 결정</span>, Bottlerocket 변형, 새 AMI는 Drift로 교체</td><td><code>amiSelectorTerms</code>, custom AMI, userData</td></tr>
    <tr class="fragment fade-up" data-fragment-index="3"><td>VPC CNI, CoreDNS, kube-proxy, EBS CSI, Pod Identity Agent</td><td><span class="ak1-aws">내장</span>, CNI, CoreDNS, kube-proxy는 노드의 systemd service</td><td>add-on으로 설치, 관리</td></tr>
    <tr class="fragment fade-up" data-fragment-index="4"><td>Spot 중단, 노드 health</td><td><span class="ak1-aws">AWS 자동 처리</span>, 자동 repair 내장</td><td>SQS, EventBridge 구성, NodeRepair는 alpha gate</td></tr>
  </tbody>
</table>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="5">
  <div class="callout callout-info"><strong class="text-info">그래도 사용자 몫</strong><div class="on-surface-muted">NodePool과 NodeClass 정의, PDB, 워크로드 설계, 비용 관리는 여전히 사용자가 정합니다.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">둘 중 하나를 권장</strong><div class="on-surface-muted">AWS는 한쪽을 권장합니다. 마이그레이션 중 공존하면 NodePool로 워크로드를 분리합니다.</div></div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- Auto Mode = 업스트림 호환 관리형 Karpenter + 관리형 구성 요소(VPC CNI, CoreDNS, kube-proxy, EBS CSI, Pod Identity Agent 불필요, AWS LBC)
- controller는 클러스터 Pod가 아니고 버전을 사용자가 고르지 않습니다.
- AMI는 AWS가 결정하고 새 AMI는 Drift로 교체, Spot 중단과 노드 health도 AWS가 처리
- NodePool, NodeClass, PDB, 워크로드, 비용은 사용자 몫. 공존보다 한쪽 선택이 AWS 권장

Auto Mode를 한 줄로 정의하면, Karpenter와 노드 운영에 필요한 구성 요소를 AWS가 대신 운영하는 모드입니다. EKS FAQ의 관리형 구성 요소 목록에는 업스트림 호환 관리형 Karpenter controller, EBS CSI controller, 관리형 VPC CNI, CoreDNS, AWS Load Balancer Controller가 들어 있습니다.
{cue: pause}
표를 위에서부터 보겠습니다. 첫째 줄, controller는 클러스터 안의 Pod가 아니고 AWS가 업그레이드하며, 버전은 공개되지 않고 사용자가 고르지 않습니다. 둘째 줄, AMI도 AWS가 결정합니다. Bottlerocket 변형이고, 새 AMI가 나오면 Drift로 노드가 교체됩니다. 셋째 줄, VPC CNI, CoreDNS, kube-proxy는 Pod가 아니라 각 노드의 systemd service로 돌고, EBS CSI와 Pod Identity Agent도 add-on으로 설치하지 않습니다. 넷째 줄, Spot 중단 알림과 EC2 health 이벤트, 상태 검사 실패를 AWS가 자동 처리합니다. 직접 운영할 때는 이 모든 줄이 사용자 작업입니다.
{cue: question}
그럼 Auto Mode면 노드는 신경 쓰지 않아도 될까요. 아닙니다. 어떤 노드를 허용할지, 언제 바꿔도 되는지, 앱을 어떻게 보호할지, 비용은 여전히 사용자가 정합니다. 오늘 3부와 4부가 양쪽 모두에 해당하는 이유입니다.
그리고 한 클러스터에서 둘을 섞는 것은 권장되지 않습니다. 마이그레이션 중 잠시 공존할 때는 NodePool로 워크로드를 나눠 두라는 것이 AWS 안내입니다.

[출처]
- https://aws.amazon.com/eks/faqs/ (관리형 구성 요소 목록)
- https://docs.aws.amazon.com/eks/latest/userguide/automode.html (Automated Components)
- https://docs.aws.amazon.com/eks/latest/userguide/automode-learn-instances.html (공존 시 NodePool 분리)
{cue: transition}
마지막으로 오늘 기준의 버전 지도를 정리하고 3부로 넘어가겠습니다.
:::

---
<!-- Slide 7: 버전 지도 -->
@type: content
@title: 버전 지도: 2026-10-20 기준

## 버전 지도: 2026-10-20 기준

:::html
<style>
.ak1-ver { display: grid; grid-template-columns: 1.1fr 1fr; gap: var(--space-4); align-items: start; }
.ak1-pick { display: flex; gap: var(--space-2); margin-bottom: var(--space-3); }
.ak1-pick .btn { color: var(--on-surface); }
.ak1-pick .btn.active { background: var(--accent-subtle); border-color: var(--accent); color: var(--accent); }
.ak1-kv { display: grid; grid-template-columns: 9rem 1fr; gap: var(--space-2) var(--space-3); font-size: var(--fs-card); }
.ak1-kv dt { color: var(--text-secondary); }
.ak1-kv dd { margin: 0; font-weight: var(--weight-bold); }
.ak1-hint { font-size: var(--fs-caption); color: var(--text-secondary); margin-top: var(--space-3); word-break: keep-all; }
.ak1-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak1-ver">
  <div class="card">
    <div class="ak1-pick" id="ak1-pick">
      <button class="btn btn-sm" data-v="1.34">1.34</button>
      <button class="btn btn-sm" data-v="1.35">1.35</button>
      <button class="btn btn-sm" data-v="1.36">1.36</button>
      <button class="btn btn-sm active" data-v="1.37">1.37</button>
    </div>
    <dl class="ak1-kv">
      <dt>EKS 출시</dt><dd id="ak1-rel">-</dd>
      <dt>표준 지원 종료</dt><dd id="ak1-std">-</dd>
      <dt>확장 지원 종료</dt><dd id="ak1-ext">-</dd>
      <dt>Karpenter 최소</dt><dd id="ak1-kp">-</dd>
      <dt>비고</dt><dd id="ak1-note">-</dd>
    </dl>
    <div class="ak1-hint">버전을 누르면 ap-northeast-2 기준 지원 일정과 Karpenter 호환 버전이 바뀝니다.</div>
  </div>
  <div class="ak1-stack">
    <div class="callout callout-info fragment fade-left" data-fragment-index="1"><strong class="text-info">Karpenter v1.15.0 (2026-10-10)</strong><div class="on-surface-muted">1.37에 필요. regular release라 다음 minor 출시 전까지만 지원</div></div>
    <div class="callout callout-info fragment fade-left" data-fragment-index="2"><strong class="text-info">v1.14.x LTS (2027-07까지)</strong><div class="on-surface-muted">K8s 1.36까지. v1.14.2 패치 2026-10-19 출시</div></div>
    <div class="callout callout-warning fragment fade-left" data-fragment-index="3"><strong class="text-warning">Auto Mode는 버전 선택 없음</strong><div class="on-surface-muted">관리형 Karpenter 버전은 비공개이고 AWS가 업그레이드합니다.</div></div>
  </div>
</div>
:::

:::script
(function () {
  var DATA = {
    '1.34': ['2025-10-02', '2026-12-02', '2027-12-02', '>= 1.6', '표준 지원 중'],
    '1.35': ['2026-01-27', '2027-03-27', '2028-03-27', '>= 1.9', '표준 지원 중'],
    '1.36': ['2026-06-02', '2027-08-02', '2028-08-02', '>= 1.13', '리전 기본 버전 (v1.14 LTS 가능)'],
    '1.37': ['2026-10-01', '2027-12-01', '2028-12-01', '1.15.x', '버전 명시 필요, v1.14 LTS 불가']
  };
  var pick = document.getElementById('ak1-pick');
  if (!pick) return;
  function show(v) {
    var d = DATA[v];
    document.getElementById('ak1-rel').textContent = d[0];
    document.getElementById('ak1-std').textContent = d[1];
    document.getElementById('ak1-ext').textContent = d[2];
    document.getElementById('ak1-kp').textContent = d[3];
    document.getElementById('ak1-note').textContent = d[4];
    pick.querySelectorAll('.btn').forEach(function (b) { b.classList.toggle('active', b.getAttribute('data-v') === v); });
  }
  pick.addEventListener('click', function (e) {
    var b = e.target.closest('.btn');
    if (b) show(b.getAttribute('data-v'));
  });
  show('1.37');
})();
:::

:::notes
{timing: 2.5min}
[요약]
- EKS 1.37: 2026-10-01 출시, 표준 지원 2027-12-01, 확장 지원 2028-12-01. 서울 리전 기본 버전은 아직 1.36이라 1.37은 명시해야 함
- 1.37에는 Karpenter 1.15.x가 필요. v1.15.0(2026-10-10)은 LTS가 아니라 다음 minor 출시 전까지만 지원
- v1.14.x는 LTS(Jul 2027까지)지만 K8s 1.36까지. v1.14.2 패치가 2026-10-19 출시
- Auto Mode는 Karpenter 버전을 사용자가 고르지 않습니다.

왼쪽은 클릭해 보실 수 있는 버전 카드입니다. 지금 1.37이 선택되어 있습니다. EKS 1.37은 10월 1일에 나왔고 표준 지원은 2027년 12월 1일, 확장 지원은 2028년 12월 1일까지입니다. 서울 리전의 기본 버전은 아직 1.36이라서, 1.37 클러스터를 만들 때는 버전을 명시해야 합니다.
{cue: demo}
1.36을 눌러 보겠습니다. Karpenter 최소 버전이 1.13 이상으로 바뀝니다. 1.37로 돌아오면 1.15.x입니다. 이 차이가 오른쪽 카드의 이야기입니다.
{cue: pause}
Karpenter v1.15.0은 10월 10일에 나왔고 1.37을 쓰려면 필요합니다. 그런데 v1.15는 LTS가 아니라 regular release라서, 지원 정책상 다음 minor가 나올 때까지만 지원됩니다. LTS인 v1.14 계열은 2027년 7월까지 지원되고 2026-10-19에 v1.14.2 패치가 나왔지만, 호환성은 1.36까지입니다. 정리하면 1.37로 가는 순간 Karpenter도 regular release 주기를 따라가야 한다는 뜻입니다. 이 점이 4부 선택 기준의 "Karpenter minor마다 CRD와 breaking change를 따라갈 인력" 항목으로 이어집니다.
Auto Mode에는 이 고민이 없습니다. 관리형 Karpenter 버전은 공개되지 않고 AWS가 업그레이드합니다.

[출처]
- aws eks describe-cluster-versions --region ap-northeast-2 (2026-10-20 실행), https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions-standard.html
- https://karpenter.sh/docs/upgrading/compatibility/
- https://github.com/aws/karpenter-provider-aws/releases (v1.15.0, v1.14.2), SUPPORT.md @ v1.15.0
{cue: transition}
여기까지가 개념과 구조였습니다. 3부에서는 이 루프가 노드를 늘리고, 줄이고, 바꾸는 방식을 자세히 보겠습니다.
:::
