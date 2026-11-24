---
remarp: true
block: 01-why-migrate
---

---
<!-- Slide 1: 세션 커버 -->
@type: cover

# EKS 워크로드 IAM 이전

노드 인스턴스 프로파일에서 IRSA와 EKS Pod Identity로, 라이브 데모 포함

2026. 11. 24, 오준석, Senior Solutions Architect, AWS Korea

:::script
// 발표자 창 노트 순서: 대본 먼저, [요약]/[출처]/[약어]는 아래 (assets/presenter-notes.js)
if (!window.__widNotesLoader) {
  window.__widNotesLoader = true;
  var s = document.createElement('script');
  s.src = './assets/presenter-notes.js';
  document.head.appendChild(s);
}
:::

:::notes
{timing: 0.5min}
[요약]
- 주제: 앱의 AWS 권한을 노드 역할에서 워크로드 단위 역할로 옮기기
- 두 방식(IRSA, EKS Pod Identity)의 차이와 장단점, 보안과 운영 비용에서 얻는 것
- 방식별 이전 절차, 마지막에 실제 EKS 클러스터에서 라이브로 실행

안녕하세요, AWS Korea 오준석입니다. 오늘은 EKS에서 애플리케이션의 AWS 권한을 노드 역할에서 떼어 내 워크로드마다 주는 방법을 다룹니다.
노드 역할의 문제는 다들 알고 계시니 짧게 넘기고, IRSA와 EKS Pod Identity가 무엇이 다르고 각각 어떻게 옮기는지에 집중하겠습니다. 마지막에는 실제 클러스터에서 같은 앱 세 벌을 옮기는 과정을 라이브로 보여 드리겠습니다.
{cue: transition}
먼저 오늘 순서입니다.
:::

---
<!-- Slide 2: 아젠다 -->
@type: content
@timing: 50min
@title: 오늘 세션 구성

## 오늘 세션 구성

:::html
<div class="wid-grid-4">
  <div class="wid-card"><span class="wid-chip">1부, 14분</span><h4 class="wid-gap-top">차이와 선택</h4><div class="wid-muted">출발점, 두 방식의 차이와 장단점, 보안과 운영 비용, 선택 기준</div></div>
  <div class="wid-card"><span class="wid-chip">2부, 13분</span><h4 class="wid-gap-top">이전 절차</h4><div class="wid-muted">공통 다섯 단계, IRSA와 Pod Identity 명령, 교차 계정, 공존, hop limit과 IMDS 차단</div></div>
  <div class="wid-card"><span class="wid-chip">3부, 13분</span><h4 class="wid-gap-top">라이브 데모</h4><div class="wid-muted">같은 앱 세 벌을 옮기고 노드 역할 권한을 회수</div></div>
  <div class="wid-card"><span class="wid-chip">마무리, 4분</span><h4 class="wid-gap-top">문제 해결, 퀴즈</h4><div class="wid-muted">막혔을 때 보는 순서와 정리</div></div>
</div>
<div class="wid-grid-2 wid-gap-top">
  <div class="wid-panel"><strong>Q&amp;A, 6분</strong> <span class="wid-muted">남는 시간은 질문으로</span></div>
  <div class="wid-panel"><strong>부록: 동작 원리</strong> <span class="wid-muted">자격 증명 경로, SDK 체인, 주입, 두 방식의 단계별 흐름. 질문이 나오면 사용</span></div>
</div>
<div class="callout callout-info wid-gap-top">데모가 막히면 슬라이드에 같은 단계의 실측 화면이 있습니다.</div>
:::

:::notes
{timing: 1min}
[요약]
- 1부 14분: 출발점 한 장, 두 방식의 차이, 주입 변수와 SDK, 장단점, 보안과 운영 비용 이점, 선택 기준
- 2부 13분: 공통 다섯 단계, IRSA와 Pod Identity의 이전 명령, 교차 계정, 공존, hop limit 원리와 IMDS 차단
- 3부 데모 13분과 마무리 4분, 남는 시간은 Q&A. 동작 원리는 부록에 있어 질문이 나오면 사용

순서는 이렇습니다. 노드 역할의 문제는 한 장으로 짚고, 바로 IRSA와 Pod Identity의 차이와 장단점, 그리고 옮기면 보안과 운영 비용에서 무엇이 좋아지는지 봅니다.
{cue: pause}
2부는 실제로 옮기는 절차입니다. 공통 순서와 방식별 명령을 보고, 3부에서 그 절차를 라이브로 실행합니다. 내부 동작 원리는 부록에 두었으니, 질문이 나오면 그 장을 열겠습니다.
{cue: transition}
출발점부터 보겠습니다.
:::

---
<!-- Slide 3: 출발점과 목표 -->
@type: content
@title: 출발점은 알고 있다, 오늘은 옮기는 법

## 출발점은 알고 있다, 오늘은 옮기는 법

:::html
<div class="wid-grid-2">
  <div class="wid-card wid-node wid-edge">
    <span class="wid-chip wid-node">지금: 앱 권한이 노드 역할에</span>
    <ul class="wid-gap-top">
      <li>같은 노드의 모든 Pod가 같은 권한을 씁니다.</li>
      <li>CloudTrail 호출자가 노드 세션이라 워크로드를 구분하기 어렵습니다.</li>
      <li>hop limit 2면 일반 Pod도 IMDS에서 노드 역할을 받습니다 (원리는 2부).</li>
    </ul>
  </div>
  <div class="wid-card">
    <span class="wid-chip">목표: 세 단계</span>
    <ol class="wid-gap-top">
      <li>앱 권한을 워크로드 역할로 옮긴다 (IRSA 또는 Pod Identity)</li>
      <li>노드 역할에서 앱 정책만 회수한다</li>
      <li>Pod의 IMDS 경로를 닫는다 (IMDSv2, hop limit 1)</li>
    </ol>
  </div>
</div>
<div class="callout callout-info wid-gap-top"><strong class="wid-t-info">오늘 답할 질문</strong>: 둘 중 무엇으로, 어떤 순서로 옮기고, 옮기면 무엇이 좋아지는가</div>
:::

:::notes
{timing: 1.5min}
[요약]
- 노드 역할 공유의 문제(권한 범위, 감사, hop limit 2)는 이미 아는 내용이라 한 장으로 정리
- 목표 세 단계: 워크로드 역할로 이전, 노드 역할에서 앱 정책 회수, Pod의 IMDS 경로 차단
- 오늘의 질문: 어느 방식으로, 어떤 순서로, 무엇이 좋아지는가

출발점은 다들 알고 계신 상태입니다. 앱이 쓰는 S3 같은 권한이 노드 역할에 붙어 있어서 같은 노드의 Pod가 모두 같은 권한을 씁니다. CloudTrail에도 노드 세션으로만 남고, hop limit이 2면 평범한 Pod도 IMDS에서 노드 역할을 받아 갑니다.
그래서 목표는 세 단계입니다. 앱 권한을 워크로드 역할로 옮기고, 노드 역할에서 앱 정책만 회수하고, 마지막에 Pod의 IMDS 경로를 닫습니다.
오늘은 이 가운데 "어떻게 옮기나"에 집중합니다. 두 방식이 어떻게 다르고, 무엇을 고르고, 어떤 순서로 옮기는지입니다.
{cue: transition}
먼저 두 방식이 설정을 어디에 거는지부터 보겠습니다.

[약어]
- IMDS: Instance Metadata Service, EC2 인스턴스 메타데이터 서비스
:::

---
<!-- Slide 4: 비교 1, 연결 방식 -->
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

[약어]
- OIDC: OpenID Connect
:::

---
<!-- Slide 5: 비교 2, 경로와 한도 -->
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
    <div class="wid-card wid-podid wid-edge"><span class="wid-chip wid-podid">Pod Identity</span><h4 class="wid-gap-top">세션 태그 6개</h4><div class="wid-row wid-mono"><code>eks-cluster-arn</code><code>eks-cluster-name</code><code>kubernetes-namespace</code><code>kubernetes-service-account</code><code>kubernetes-pod-name</code><code>kubernetes-pod-uid</code></div><div class="wid-cap">신뢰 조건에는 보통 <code>eks-cluster-arn</code>, <code>kubernetes-namespace</code>, <code>kubernetes-service-account</code> 3개를 씁니다.</div><div class="wid-muted">태그로 리소스 접근을 거는 <span class="rp-detail" data-detail="abac">ABAC(attribute-based access control)</span>이 가능합니다.</div></div>
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
    <div class="wid-card wid-podid wid-edge"><span class="wid-chip wid-podid">Pod Identity</span><h4 class="wid-gap-top">EKS Linux EC2 노드 + Hybrid Nodes</h4><div class="wid-muted">Hybrid Nodes는 IMDS가 없어 Agent의 하이브리드 DaemonSet과 노드 자격 증명 파일(<code>enableCredentialsFile</code>)이 필요합니다. Fargate, Windows, Outposts, EKS Anywhere는 지원하지 않습니다.</div></div>
  </div>
</div>
<div class="tab-content" data-tab="cmp-xacct">
  <div class="wid-grid-2">
    <div class="wid-card wid-irsa wid-edge"><span class="wid-chip wid-irsa">IRSA</span><h4 class="wid-gap-top">대상 계정 역할이 OIDC provider를 신뢰</h4><div class="wid-muted">대상 계정에 이 클러스터의 provider를 등록합니다.</div></div>
    <div class="wid-card wid-podid wid-edge"><span class="wid-chip wid-podid">Pod Identity</span><h4 class="wid-gap-top">association 역할은 같은 계정</h4><div class="wid-muted">대상 역할을 지정하거나 역할 체이닝으로 위임합니다.</div></div>
  </div>
</div>
<div class="wid-src">출처: <a href="https://docs.aws.amazon.com/eks/latest/userguide/service-accounts.html">Amazon EKS User Guide, IRSA와 Pod Identity 비교</a>, <a href="https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html">EKS Pod Identity considerations</a>, <a href="https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-add-ons.html">Configure add-ons for hybrid nodes</a></div>
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
- 실행 환경: IRSA는 Fargate, EKS Anywhere, ROSA, 자체 관리 Kubernetes까지, Pod Identity는 EKS Linux EC2와 Hybrid Nodes(추가 설정 필요)
- 교차 계정: IRSA는 대상 계정이 provider 신뢰, Pod Identity는 같은 계정 역할에서 대상 역할 지정 또는 체이닝

이 장은 다섯 탭입니다. 첫째 경로, IRSA는 Pod가 STS를 직접 부르고 Pod Identity는 Agent를 거칩니다. 프라이빗 클러스터라면 필요한 엔드포인트가 다릅니다.
(아래 방향키)
둘째 세션 태그입니다. Pod Identity는 클러스터 ARN과 이름, namespace, ServiceAccount, Pod 이름과 UID까지 태그 여섯 개가 붙어서, 정책 조건으로 태그를 비교하는 ABAC이 됩니다.
(아래 방향키)
셋째 한도입니다. OIDC provider는 계정당 기본 100개, 신뢰 정책은 기본 2,048자라 역할 하나에 클러스터 네 개 정도면 찹니다. 클러스터가 많은 조직이라면 이 숫자가 결정적입니다.
(아래 방향키)
넷째 실행 환경은 IRSA가 넓습니다. Fargate나 Windows 노드, EKS 밖의 Kubernetes라면 IRSA입니다. EKS Hybrid Nodes에서는 둘 다 됩니다. 다만 Pod Identity Agent는 원래 IMDS에서 노드 자격 증명을 받는데 온프레미스 노드에는 IMDS가 없어서, 노드 쪽에 자격 증명 파일을 만들고 Agent의 하이브리드 DaemonSet을 켜야 합니다.
(아래 방향키)
마지막 교차 계정은 둘 다 가능하지만 방식이 다릅니다.
{cue: transition}
그럼 실제 Pod에는 무엇이 들어가고, 누가 그걸 읽는지 보겠습니다.

[약어]
- ABAC: Attribute-based access control
- ROSA: Red Hat OpenShift Service on AWS
:::

---
<!-- Slide 6: 주입되는 것 -->
@type: content
@title: Pod에 주입되는 변수, 읽는 건 앱의 SDK

## Pod에 주입되는 변수, 읽는 건 앱의 SDK

:::html
<table class="data-table wid-table">
  <thead><tr><th>경로</th><th>Pod에 주입되는 것</th><th>SDK가 호출하는 곳</th><th>결과 역할</th></tr></thead>
  <tbody>
    <tr><td><span class="wid-chip wid-node">node (IMDS)</span></td><td>없음</td><td>IMDSv2 <code>169.254.169.254</code></td><td>노드 IAM 역할 (노드의 모든 Pod가 공유)</td></tr>
    <tr><td><span class="wid-chip wid-irsa">IRSA (STS)</span></td><td><code>AWS_ROLE_ARN</code>, <code>AWS_WEB_IDENTITY_TOKEN_FILE</code>, 토큰 볼륨</td><td>리전 STS <code>AssumeRoleWithWebIdentity</code></td><td>ServiceAccount 주석의 역할</td></tr>
    <tr><td><span class="wid-chip wid-podid">Pod Identity</span></td><td><code>AWS_CONTAINER_CREDENTIALS_FULL_URI</code>, <code>AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE</code>, 토큰 볼륨</td><td>같은 노드의 Agent <code>169.254.170.23</code></td><td>association에 지정한 역할</td></tr>
  </tbody>
</table>
<div class="wid-grid-3 wid-gap-top">
  <div class="callout callout-info"><strong class="wid-t-info">받으러 가는 건 앱의 SDK</strong>: EKS는 변수와 토큰 파일만 넣습니다. 앱 안의 SDK가 이 변수를 읽고 STS나 Agent에 직접 요청합니다.</div>
  <div class="callout callout-warning"><strong class="wid-t-warning">변수를 모르는 SDK는 IMDS로</strong>: 오래된 SDK는 변수를 무시하고 체인 끝 IMDS에서 노드 역할을 씁니다. 오류 없이 지나가니 최소 버전을 확인합니다.</div>
  <div class="callout callout-warning"><strong class="wid-t-warning">주입은 Pod 생성 시점에만</strong>: 이미 떠 있는 Pod는 그대로라 rollout이 필요하고, 확인은 호출자 ARN으로 합니다.</div>
</div>
<div class="wid-src">출처: <a href="https://docs.aws.amazon.com/eks/latest/userguide/pod-id-minimum-sdk.html">EKS User Guide, Use pod identity with the AWS SDK</a>, <a href="https://docs.aws.amazon.com/sdkref/latest/guide/standardized-credentials.html">AWS SDKs and Tools, standardized credential providers</a></div>
:::

:::notes
{timing: 1.5min}
[요약]
- 노드 경로: 주입 없음, IMDS에서 노드 역할
- IRSA: AWS_ROLE_ARN, AWS_WEB_IDENTITY_TOKEN_FILE, 토큰 볼륨
- Pod Identity: AWS_CONTAINER_CREDENTIALS_FULL_URI, AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE, 토큰 볼륨
- EKS가 넣는 건 변수와 토큰 파일뿐. 자격 증명은 앱 프로세스 안의 SDK가 이 변수를 읽고 직접 받으러 감(IRSA는 STS, Pod Identity는 노드의 Agent)
- 변수를 모르는 오래된 SDK는 무시하고 체인 끝 IMDS로 내려가 노드 역할 사용. 오류가 없어 놓치기 쉬움. Pod Identity의 토큰 파일 변수와 169.254.170.23 주소는 비교적 최근에 SDK에 들어감
- 주입은 Pod 생성 때만 일어나므로 rollout 필요, 검증은 호출자 ARN으로

표로 정리하면 이렇습니다. 노드 경로는 아무것도 주입되지 않고, IRSA와 Pod Identity는 서로 다른 환경 변수 두 개와 토큰 볼륨이 들어갑니다. 데모의 diff 단계에서 이 변수 이름을 실제 Pod에서 그대로 확인합니다.
여기서 꼭 짚을 점이 있습니다. EKS가 Pod에 넣어 주는 건 이 변수와 토큰 파일뿐이고, 자격 증명 자체는 아닙니다. 앱 프로세스 안의 SDK가 이 변수를 읽고, IRSA라면 STS에, Pod Identity라면 같은 노드의 Agent 주소로 직접 요청해서 자격 증명을 받아 옵니다. 노드의 Agent나 EKS Auth는 그 요청이 와야 움직입니다.
그래서 SDK가 이 변수를 모르면 아무 일도 일어나지 않습니다. 오래된 SDK는 변수를 무시하고 체인 끝의 IMDS로 내려가 노드 역할을 씁니다. 오류가 나지 않으니 노드 역할에 권한이 남아 있는 동안에는 이전이 된 것처럼 보입니다. 특히 Pod Identity의 토큰 파일 변수와 Agent 주소는 비교적 최근에 SDK에 들어갔기 때문에 최소 버전을 꼭 확인합니다.
또 하나, 주입은 Pod를 만들 때만 일어납니다. 주석을 달거나 association을 만들어도 이미 떠 있는 Pod는 그대로라 rollout이 필요합니다.
그리고 확인할 때는 API 호출이 성공했는지가 아니라 호출자 ARN이 무엇인지 봐야 합니다. 노드 역할에 권한이 남아 있으면 이전이 안 됐어도 성공하기 때문입니다.
{cue: transition}
이 차이를 장점과 단점으로 정리하겠습니다.
:::

---
<!-- Slide 7: 장단점 -->
@type: content
@title: 장단점: IRSA와 Pod Identity

## 장단점: IRSA와 Pod Identity

:::html
<div class="wid-grid-2">
  <div class="wid-card wid-irsa wid-edge">
    <span class="wid-chip wid-irsa">IRSA</span>
    <h4 class="wid-gap-top wid-t-success">장점</h4>
    <ul>
      <li>Fargate, Windows, EKS 밖(EKS Anywhere, ROSA, 자체 관리)에서도 같은 방식</li>
      <li>애드온 없이 IAM OIDC provider와 STS만으로 동작</li>
      <li>교차 계정: 대상 계정 역할이 이 클러스터의 provider를 직접 신뢰</li>
    </ul>
    <h4 class="wid-gap-top wid-t-danger">단점</h4>
    <ul>
      <li>클러스터마다 OIDC provider 등록 (계정당 기본 100개)</li>
      <li>새 클러스터마다 신뢰 정책 수정, 기본 2,048자라 역할당 보통 4개 안팎</li>
      <li>세션 태그 없음, Pod가 STS를 직접 호출해 STS 할당량 사용</li>
    </ul>
  </div>
  <div class="wid-card wid-podid wid-edge">
    <span class="wid-chip wid-podid">Pod Identity</span>
    <h4 class="wid-gap-top wid-t-success">장점</h4>
    <ul>
      <li>신뢰 정책은 서비스 principal 하나, 클러스터가 늘어도 그대로</li>
      <li>세션 태그로 ABAC: 한 역할을 여러 ServiceAccount에</li>
      <li>연결은 EKS API, 권한은 IAM: 팀 간 책임 분리</li>
    </ul>
    <h4 class="wid-gap-top wid-t-danger">단점</h4>
    <ul>
      <li>Agent 애드온과 노드 역할의 <code>eks-auth:AssumeRoleForPodIdentity</code> 필요 (Auto Mode는 내장)</li>
      <li>EKS Linux EC2와 Hybrid Nodes만: Fargate, Windows는 지원하지 않음</li>
      <li>지원 SDK 최소 버전 확인, 교차 계정은 대상 역할 지정이나 체이닝</li>
    </ul>
  </div>
</div>
<div class="wid-src">출처: <a href="https://docs.aws.amazon.com/eks/latest/userguide/service-accounts.html">Amazon EKS User Guide, Comparing EKS Pod Identity and IRSA</a>, <a href="https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html">Learn how EKS Pod Identity grants pods access</a></div>
:::

:::notes
{timing: 2min}
[요약]
- IRSA 장점: 실행 환경이 넓음(Fargate, Windows, EKS 밖), 애드온 불필요, 교차 계정이 단순
- IRSA 단점: 클러스터마다 OIDC provider(계정당 100), 새 클러스터마다 신뢰 정책 수정(역할당 4개 안팎), 세션 태그 없음, Pod가 STS 직접 호출
- Pod Identity 장점: 신뢰 정책 고정, 세션 태그 ABAC, EKS와 IAM의 책임 분리
- Pod Identity 단점: Agent 애드온과 노드 역할 권한, EKS Linux EC2와 Hybrid Nodes만, SDK 최소 버전

IRSA부터입니다. 가장 큰 장점은 범용성입니다. Fargate, Windows 노드, EKS Anywhere나 ROSA 같은 EKS 밖의 Kubernetes에서도 같은 방식으로 씁니다. 애드온 없이 IAM의 OIDC provider와 STS만으로 동작합니다.
단점은 클러스터 수에 비례해 커집니다. 클러스터마다 OIDC provider를 등록해야 하고, 계정당 기본 한도가 100개입니다. 역할을 새 클러스터에서 쓰려면 신뢰 정책에 문장을 추가해야 하는데, 기본 2,048자라 보통 네 개 안팎이면 찹니다. 세션 태그가 없고, Pod가 STS를 직접 부르니 STS 할당량도 씁니다.
Pod Identity는 정반대입니다. 신뢰 정책은 서비스 principal 하나라 클러스터가 늘어도 고칠 게 없고, 세션 태그가 붙어 한 역할을 태그 조건으로 여러 ServiceAccount에 나눠 쓸 수 있습니다. 연결은 EKS API, 권한은 IAM이라 플랫폼 팀과 보안 팀의 경계도 깔끔합니다.
대신 Agent 애드온이 필요하고, 노드 역할에 EKS Auth 호출 권한이 있어야 합니다. 관리형 정책 AmazonEKSWorkerNodePolicy를 쓰면 들어 있고, Auto Mode는 Agent가 내장입니다. 실행 환경은 EKS Linux EC2와 Hybrid Nodes만이라 Fargate와 Windows는 IRSA로 남습니다.
{cue: transition}
그럼 옮기고 나면 보안과 비용 측면에서 무엇이 좋아지는지 보겠습니다.

[약어]
- ABAC: Attribute-based access control
- ROSA: Red Hat OpenShift Service on AWS
- STS: AWS Security Token Service
:::

---
<!-- Slide 8: 보안과 운영 비용 -->
@type: content
@title: 옮기면 얻는 것: 보안과 운영 비용

## 옮기면 얻는 것: 보안과 운영 비용

:::html
<div class="wid-grid-2">
  <div class="wid-card">
    <span class="wid-chip">보안 (두 방식 공통)</span>
    <ul class="wid-gap-top">
      <li>권한 범위가 노드에서 ServiceAccount로: 그 SA를 쓰는 Pod만 권한을 받음</li>
      <li>노드 역할 회수와 IMDS 차단 뒤에는 다른 Pod의 역할에 닿지 않음</li>
      <li>CloudTrail에 워크로드 역할 세션으로 남아 추적과 회수 범위가 좁아짐</li>
      <li>임시 자격 증명과 자동 갱신은 그대로, 단위만 노드에서 워크로드로</li>
    </ul>
    <div class="wid-cap wid-gap-top"><span class="wid-chip wid-podid">Pod Identity</span> 세션 태그로 클러스터, namespace, ServiceAccount 조건을 정책에 걸 수 있음</div>
  </div>
  <div class="wid-card">
    <span class="wid-chip">운영 비용 (클러스터가 늘수록 차이가 큼)</span>
    <table class="data-table wid-table wid-gap-top">
      <thead><tr><th>작업</th><th>IRSA</th><th>Pod Identity</th></tr></thead>
      <tbody>
        <tr><td>클러스터 추가, blue/green 교체</td><td>provider 등록, 역할마다 신뢰 정책 수정</td><td>association만 다시 생성</td></tr>
        <tr><td>역할 수</td><td>권한 조합마다 역할</td><td>태그 조건으로 역할 재사용</td></tr>
        <tr><td>한도</td><td>provider 100개, 역할당 연결 4개 안팎(상향 시 8개)</td><td>클러스터당 association 5,000개</td></tr>
        <tr><td>STS 호출</td><td>Pod마다, STS 할당량 사용</td><td>노드마다 한 번, Pod는 STS를 부르지 않음</td></tr>
      </tbody>
    </table>
  </div>
</div>
<div class="callout callout-info wid-gap-top"><strong class="wid-t-info">따져 볼 비용</strong>: Pod Identity는 노드마다 Agent Pod가 하나씩 돕니다(DaemonSet). 클러스터가 하나뿐이고 교체가 드물면 운영 비용 차이는 작습니다.</div>
<div class="wid-src">출처: <a href="https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html">EKS Pod Identity benefits</a>, <a href="https://docs.aws.amazon.com/eks/latest/userguide/service-accounts.html">Comparing EKS Pod Identity and IRSA</a></div>
:::

:::notes
{timing: 2min}
[요약]
- 보안(공통): SA 단위 최소 권한, 회수와 IMDS 차단 뒤 자격 증명 격리, CloudTrail에서 워크로드 식별, 정적 키 없음
- Pod Identity는 세션 태그로 클러스터, namespace, SA 조건까지
- 운영 비용: 클러스터 추가와 교체 때 IRSA는 provider 등록과 신뢰 정책 수정, Pod Identity는 association만. 역할 재사용, 한도, STS 호출 횟수에서도 차이
- 따져 볼 것: 노드마다 Agent DaemonSet. 클러스터가 적으면 차이가 작음
- Agent 리소스(실측, 2026-11-24, 데모 클러스터 15노드): Pod당 CPU 1m, 메모리 10~14Mi. 기본 requests/limits 없음, 애드온 설정값 resources로 지정 가능(v1.4.0 스키마)

보안 쪽은 두 방식 모두 같은 걸 얻습니다. 권한이 노드가 아니라 ServiceAccount 단위가 되고, 노드 역할을 회수하고 IMDS를 닫으면 다른 Pod의 역할에 닿을 길이 없어집니다. CloudTrail에도 워크로드 역할 세션으로 남으니, 사고가 났을 때 무엇을 회수할지 바로 보입니다. Pod Identity는 여기에 세션 태그가 더해져서 namespace나 ServiceAccount를 정책 조건으로 쓸 수 있습니다.
경제적인 차이는 요금보다 운영 작업량에서 납니다. 클러스터를 추가하거나 blue/green으로 교체할 때 IRSA는 새 클러스터의 OIDC provider를 등록하고 그 클러스터를 쓰는 역할마다 신뢰 정책을 고칩니다. Pod Identity는 association만 다시 만들면 됩니다. 역할도 태그 조건으로 재사용할 수 있고, 한도와 STS 호출 횟수에서도 여유가 있습니다.
반대로 따져 볼 것도 있습니다. Pod Identity는 노드마다 Agent가 하나씩 돕니다. 클러스터가 하나뿐이고 교체도 드물다면 이 차이는 크지 않습니다.
(예상 질문, Agent 리소스) 데모 클러스터의 노드 15대에서 재 보면 Agent Pod 하나가 CPU 1m, 메모리 10~14Mi 정도입니다. 애드온 기본값에는 requests와 limits가 없고, 필요하면 애드온 설정값의 resources로 지정합니다. hostNetwork에 system-node-critical 우선순위로 돕니다.
{cue: transition}
그래서 고르는 기준은 이렇게 정리됩니다.
:::

---
<!-- Slide 9: 선택 기준 -->
@type: content
@title: 기본은 Pod Identity, 예외는 IRSA

## 기본은 Pod Identity, 예외는 IRSA

:::html
<div class="wid-grid-3">
  <div class="wid-card wid-podid wid-edge">
    <span class="wid-chip wid-podid">Pod Identity</span>
    <h4 class="wid-gap-top">신규 EKS Linux EC2, Hybrid Nodes 워크로드</h4>
    <div class="wid-muted">여러 클러스터에서 같은 역할, 세션 태그 ABAC, 팀 간 책임 분리</div>
  </div>
  <div class="wid-card wid-irsa wid-edge">
    <span class="wid-chip wid-irsa">IRSA</span>
    <h4 class="wid-gap-top">Pod Identity가 닿지 않는 곳</h4>
    <div class="wid-muted"><strong>실행 환경</strong>: Fargate, Windows 노드, Outposts, EKS Anywhere, EKS 밖과 매니페스트를 공유하는 워크로드, SDK를 올릴 수 없는 앱</div>
    <div class="wid-muted wid-gap-top"><strong>조직</strong>: 역할 연결 권한을 플랫폼 팀에 넘기지 않고 IAM 팀이 신뢰 정책으로 직접 쥐려는 경우</div>
  </div>
  <div class="wid-card">
    <span class="wid-chip">함께 쓰기</span>
    <h4 class="wid-gap-top">한 클러스터에 공존 가능</h4>
    <div class="wid-muted">워크로드마다 고르고, 전환이 끝난 SA에는 한 방식만 남깁니다.</div>
  </div>
</div>
<div class="callout callout-info wid-gap-top"><strong class="wid-t-info">AWS 권장</strong>: 가능한 경우 EKS Pod Identity를 씁니다. 실행 환경과 조직 구조에 따라 IRSA가 맞는 경우가 있습니다.</div>
<div class="wid-src">출처: <a href="https://docs.aws.amazon.com/eks/latest/userguide/service-accounts.html">Amazon EKS User Guide, Grant Kubernetes workloads access to AWS</a></div>
:::

:::notes
{timing: 1.5min}
[요약]
- 신규 EKS Linux EC2 워크로드: Pod Identity가 단순하고 확장에 유리
- IRSA(실행 환경): Fargate, Windows, Outposts, EKS Anywhere, EKS 밖과 구성 공유, SDK를 올릴 수 없는 앱(벤더 이미지, 오래된 런타임)
- IRSA(조직): 어느 클러스터의 어느 SA가 역할을 쓰는지 IAM 팀이 신뢰 정책으로 직접 승인하려는 경우. Pod Identity는 eks:CreatePodIdentityAssociation과 iam:PassRole을 가진 쪽이 연결을 만듦
- 클러스터가 한두 개로 고정되고 IRSA 자동화가 정착된 팀은 옮기는 이점이 작음
- 두 방식은 한 클러스터에서 공존 가능, 전환이 끝나면 한 ServiceAccount에는 한 방식만
- AWS는 가능한 경우 Pod Identity를 권장

기본값은 Pod Identity입니다. 클러스터가 늘어도 신뢰 정책을 건드리지 않고, 세션 태그가 붙고, 팀 경계가 깔끔합니다.
IRSA가 맞는 경우는 두 갈래입니다. 먼저 실행 환경입니다. Fargate로 돌리는 배치 Job, Windows 노드의 .NET 앱, Outposts나 EKS Anywhere처럼 Pod Identity가 지원하지 않는 곳입니다. EKS와 ROSA, 자체 관리 Kubernetes에 같은 매니페스트를 배포하는 경우나, 벤더 이미지처럼 SDK를 올릴 수 없는 앱도 IRSA가 편합니다. 앞에서 본 것처럼 변수를 읽는 건 앱의 SDK라서, 오래된 SDK도 아는 웹 ID 토큰 방식이 동작할 가능성이 높기 때문입니다.
다음은 조직입니다. IRSA는 어느 클러스터의 어느 ServiceAccount가 역할을 쓰는지가 신뢰 정책 안에 들어 있어서, IAM 팀이 정책만 보고 승인하고 감사할 수 있습니다. Pod Identity에서는 association을 만드는 플랫폼 팀이 그 연결을 정합니다. 이 권한을 넘기고 싶지 않은 조직이라면 IRSA가 맞습니다. 클러스터가 한두 개로 고정되어 있고 IRSA 자동화가 이미 정착된 팀도 굳이 옮길 이유가 크지 않습니다.
둘은 한 클러스터에서 같이 써도 됩니다. 한 ServiceAccount에 둘을 함께 걸면 어떻게 되는지는 2부 이전 절차에서 보겠습니다.
AWS 문서도 가능한 경우 Pod Identity를 권장하고, 환경에 따라 IRSA가 맞을 수 있다고 적고 있습니다.
{cue: transition}
이제 2부, 실제로 옮기는 절차입니다.
:::
