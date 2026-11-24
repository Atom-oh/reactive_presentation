---
remarp: true
block: 02-how-it-works
---

---
<!-- Slide 1: 2부 구분 -->
@type: section

# 2부: 실제로 옮기는 절차

공통 다섯 단계, 방식별 명령, 교차 계정, 공존, 그리고 IMDS 차단

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
- 2부: 운영 클러스터에서 옮기는 순서와 방식별 명령
- 공통 다섯 단계, IRSA 절차, Pod Identity 절차(IRSA에서 옮기는 경우 포함), 교차 계정, 공존, IMDS 차단 순서

2부는 실제로 옮기는 절차입니다. 어느 방식을 고르든 공통 순서가 있고, 방식마다 명령이 조금 다릅니다.
{cue: transition}
공통 다섯 단계부터 보겠습니다.
:::

---
<!-- Slide 2: 운영 이전 순서 -->
@type: content
@title: 운영 이전은 다섯 단계, 회수는 맨 뒤

## 운영 이전은 다섯 단계, 회수는 맨 뒤

:::html
<ol class="wid-flow">
  <li><strong>의존성 조사</strong><div class="wid-cap">노드 역할 정책과 CloudTrail의 실제 세션 비교. 워커 노드, ECR pull 권한은 유지</div></li>
  <li><strong>역할과 전용 SA 준비</strong><div class="wid-cap">리소스 단위로 제한한 워크로드 역할. SDK 최소 버전 확인</div></li>
  <li><strong>카나리 Pod 새로 생성</strong><div class="wid-cap">주입된 env 이름, 호출자 ARN, API 성공 확인. 토큰과 키는 로그에 출력하지 않기</div></li>
  <li><strong>순차 전환 후 회수</strong><div class="wid-cap">AccessDenied, 갱신, 크론까지 관찰. 노드 역할의 해당 정책 문장만 회수</div></li>
  <li><strong>노드 접근 제한</strong><div class="wid-cap">IMDSv2 강제, hop limit 1. hostNetwork Pod는 별도 통제</div></li>
</ol>
:::

:::notes
{timing: 2.5min}
[요약]
- 1 조사: 노드 역할 정책 대 CloudTrail 실제 세션, S3는 데이터 이벤트 필요. AmazonEKSWorkerNodePolicy, AmazonEC2ContainerRegistryPullOnly(또는 동등)는 유지. AmazonEKS_CNI_Policy는 aws-node 전용 역할로 옮길 수 있음
- 2 준비: 워크로드별 역할과 전용 ServiceAccount, IRSA는 aud와 정확한 sub, Pod Identity는 요청 태그 조건. SDK 최소 버전 확인
- 3 카나리: Pod를 새로 만들고 env 이름, 호출자 ARN, 실제 API 성공을 확인
- 4 전환과 회수: AccessDenied, 자격 증명 갱신, 크론까지 본 뒤 정책 문장만 회수. 롤백은 최소 정책 복구, 전파 확인, 이전 Pod 배포 순
- 5 제한: IMDSv2 강제와 hop limit 1, hostNetwork Pod는 따로

다섯 단계를 한 장에 놓았습니다. 첫 단계는 조사입니다. 노드 역할에 붙은 정책과 CloudTrail에 실제로 찍힌 세션을 비교해서, 어떤 워크로드가 무엇을 쓰는지 봅니다. 노드 등록과 ECR pull 권한은 남겨야 하고, CNI 정책은 aws-node 전용 역할로 옮길 수 있습니다.
둘째, 워크로드마다 역할과 전용 ServiceAccount를 만듭니다. 앱의 SDK가 IRSA나 Pod Identity를 지원하는 최소 버전인지도 여기서 봅니다.
셋째, 카나리입니다. 핵심은 Pod를 새로 만드는 것과, 호출 성공이 아니라 호출자 ARN을 확인하는 것입니다.
넷째, 나머지를 순서대로 옮기고 크론 실행까지 지켜본 뒤에야 노드 역할에서 그 정책 문장만 뺍니다. 되돌릴 때는 정책을 먼저 복구하고 전파를 확인한 다음 이전 Pod를 배포합니다.
다섯째가 Pod의 IMDS 경로 차단입니다. 2부 마지막 장에서 보겠습니다.
{cue: transition}
둘째부터 넷째 단계를 방식별 명령으로 보겠습니다. IRSA부터입니다.

[출처]
- EKS 노드 IAM 역할: https://docs.aws.amazon.com/eks/latest/userguide/create-node-role.html
- S3 CloudTrail 데이터 이벤트: https://docs.aws.amazon.com/AmazonS3/latest/userguide/cloudtrail-logging-s3-info.html
- SDK 최소 버전: https://docs.aws.amazon.com/eks/latest/userguide/pod-id-minimum-sdk.html
:::

---
<!-- Slide 3: IRSA 이전 절차 -->
@type: content
@title: IRSA로 옮기기: provider, 역할, 주석

## IRSA로 옮기기: provider, 역할, 주석

:::html
<div class="wid-grid-2">
  <div class="wid-card wid-irsa wid-edge">
    <span class="wid-chip wid-irsa">준비 (클러스터와 역할마다)</span>
    <div class="wid-row wid-gap-top"><span class="wid-stepbadge">1</span><h4>클러스터의 IAM OIDC provider 등록</h4></div>
<pre class="wid-term">eksctl utils associate-iam-oidc-provider \
  --cluster $CLUSTER --approve</pre>
    <div class="wid-row wid-gap-top"><span class="wid-stepbadge">2</span><h4>역할: Federated 신뢰 + aud, sub 조건</h4></div>
<pre class="wid-term">aws iam create-role --role-name orders-irsa \
  --assume-role-policy-document file://trust-irsa.json
aws iam put-role-policy --role-name orders-irsa \
  --policy-name orders-s3 --policy-document file://orders-s3.json</pre>
    <div class="wid-cap wid-gap-top">신뢰 정책 JSON은 1부 비교 1. 새 클러스터에서 쓰려면 1과 신뢰 정책 문장을 다시 추가합니다.</div>
  </div>
  <div class="wid-card">
    <span class="wid-chip">워크로드마다</span>
    <div class="wid-row wid-gap-top"><span class="wid-stepbadge">3</span><h4>ServiceAccount에 주석</h4></div>
<pre class="wid-term">kubectl -n orders annotate serviceaccount orders \
  eks.amazonaws.com/role-arn=arn:aws:iam::&lt;ACCOUNT_ID&gt;:role/orders-irsa</pre>
    <div class="wid-row wid-gap-top"><span class="wid-stepbadge">4</span><h4>Pod 재생성과 확인</h4></div>
<pre class="wid-term">kubectl -n orders rollout restart deployment/orders
<span class="wid-dim"># 카나리 Pod: AWS_ROLE_ARN 주입, 호출자 ARN이 assumed-role/orders-irsa</span></pre>
    <div class="wid-row wid-gap-top"><span class="wid-stepbadge">5</span><h4>노드 역할에서 그 앱의 정책 문장만 회수</h4></div>
  </div>
</div>
<div class="callout callout-info wid-gap-top"><strong class="wid-t-info">줄여 쓰기</strong>: <code>eksctl create iamserviceaccount</code>가 2와 3을 한 번에 합니다(이미 있는 SA는 <code>--override-existing-serviceaccounts</code>). 이미 떠 있는 Pod에는 주입되지 않으니 4의 재생성이 꼭 필요합니다.</div>
<div class="wid-src">출처: <a href="https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html">Amazon EKS User Guide, IAM roles for service accounts</a></div>
:::

:::notes
{timing: 2.5min}
[요약]
- 준비: 클러스터마다 IAM OIDC provider 등록, 역할은 Federated 신뢰와 aud, sub 조건
- 워크로드마다: SA 주석, rollout으로 Pod 재생성, 카나리에서 env와 호출자 ARN 확인, 노드 역할에서 정책 문장 회수
- eksctl create iamserviceaccount가 역할 생성과 주석을 한 번에. 새 클러스터는 provider와 신뢰 정책을 다시

IRSA는 준비가 두 가지입니다. 먼저 클러스터의 OIDC issuer를 IAM에 provider로 등록합니다. 클러스터마다 한 번입니다. 그다음 역할을 만드는데, 신뢰 정책에 이 provider를 Federated로 넣고 aud와 sub 조건으로 namespace와 ServiceAccount를 정확히 묶습니다. 1부 비교 1에서 본 그 JSON입니다.
워크로드 쪽은 ServiceAccount에 role-arn 주석 하나입니다. 중요한 건 다음 단계입니다. 주입은 Pod를 만들 때만 일어나니 rollout으로 Pod를 새로 만들고, 카나리 Pod에서 AWS_ROLE_ARN이 들어왔는지, 호출자 ARN이 새 역할인지 확인합니다. 확인이 끝난 다음에야 노드 역할에서 그 앱의 정책 문장을 뺍니다.
eksctl을 쓰면 create iamserviceaccount 한 번으로 역할과 주석을 같이 만들 수 있습니다. 다만 새 클러스터로 옮길 때는 provider 등록과 신뢰 정책 수정이 다시 필요합니다.
{cue: transition}
같은 일을 Pod Identity로 하면 이렇습니다.
:::

---
<!-- Slide 4: Pod Identity 이전 절차 -->
@type: content
@title: Pod Identity로 옮기기: Agent와 연결

## Pod Identity로 옮기기: Agent와 연결

:::html
<div class="wid-grid-2">
  <div class="wid-card wid-podid wid-edge">
    <span class="wid-chip wid-podid">준비 (클러스터마다 한 번, 역할은 재사용)</span>
    <div class="wid-row wid-gap-top"><span class="wid-stepbadge">1</span><h4>Agent 애드온 (Auto Mode는 생략)</h4></div>
<pre class="wid-term">aws eks create-addon --cluster-name $CLUSTER \
  --addon-name eks-pod-identity-agent</pre>
    <div class="wid-cap">노드 역할에 <code>eks-auth:AssumeRoleForPodIdentity</code> (AmazonEKSWorkerNodePolicy에 포함)</div>
    <div class="wid-row wid-gap-top"><span class="wid-stepbadge">2</span><h4>역할: 서비스 principal 신뢰</h4></div>
<pre class="wid-term">aws iam create-role --role-name orders-podid \
  --assume-role-policy-document file://trust-podid.json
aws iam put-role-policy --role-name orders-podid \
  --policy-name orders-s3 --policy-document file://orders-s3.json
<span class="wid-dim"># 신뢰: pods.eks.amazonaws.com, sts:AssumeRole + sts:TagSession</span></pre>
  </div>
  <div class="wid-card">
    <span class="wid-chip">워크로드마다</span>
    <div class="wid-row wid-gap-top"><span class="wid-stepbadge">3</span><h4>association 생성 (Kubernetes 객체 변경 없음)</h4></div>
<pre class="wid-term">aws eks create-pod-identity-association \
  --cluster-name $CLUSTER --namespace orders \
  --service-account orders \
  --role-arn arn:aws:iam::&lt;ACCOUNT_ID&gt;:role/orders-podid</pre>
    <div class="wid-row wid-gap-top"><span class="wid-stepbadge">4</span><h4>Pod 재생성과 확인</h4></div>
<pre class="wid-term">kubectl -n orders rollout restart deployment/orders
<span class="wid-dim"># AWS_CONTAINER_CREDENTIALS_FULL_URI 주입, 호출자 ARN 확인</span></pre>
    <div class="wid-row wid-gap-top"><span class="wid-stepbadge">5</span><h4>노드 역할에서 그 앱의 정책 문장만 회수</h4></div>
  </div>
</div>
<div class="callout callout-info wid-gap-top"><strong class="wid-t-info">IRSA에서 옮길 때</strong>: 신뢰 정책에 서비스 principal 추가, association, rollout, 확인 뒤 OIDC 신뢰와 SA 주석 정리. <code>eksctl utils migrate-to-pod-identity --cluster $CLUSTER</code>는 Agent, 신뢰 정책, association을 클러스터 전체에 일괄 처리합니다. <code>--approve</code> 없이 실행하면 계획만 출력합니다.</div>
<div class="wid-src">출처: <a href="https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html">EKS Pod Identity setup overview</a>, <a href="https://docs.aws.amazon.com/eks/latest/eksctl/pod-identity-associations.html">eksctl, EKS Pod Identity Associations</a></div>
:::

:::notes
{timing: 2.5min}
[요약]
- 준비: 클러스터마다 Agent 애드온(Auto Mode는 내장), 노드 역할의 eks-auth 권한, 역할은 pods.eks.amazonaws.com 신뢰로 한 번 만들고 재사용
- 워크로드마다: association 생성(Kubernetes 객체 변경 없음), rollout, 확인, 정책 문장 회수
- IRSA에서 옮길 때: 신뢰 정책에 서비스 principal 추가, association, rollout, 확인 뒤 OIDC 신뢰와 주석 정리. eksctl utils migrate-to-pod-identity는 Agent 설치, 신뢰 정책, association까지 클러스터 전체에 일괄 처리. rollout, 확인, 주석 정리는 직접. --approve 없으면 계획만

Pod Identity는 클러스터마다 Agent 애드온 하나를 깝니다. Auto Mode라면 이미 들어 있습니다. Agent는 노드 역할로 EKS Auth를 부르니, 노드 역할에 그 권한이 있어야 합니다. AmazonEKSWorkerNodePolicy에 들어 있습니다. 역할의 신뢰 정책은 pods.eks.amazonaws.com 서비스 principal 하나라서, 한 번 만들면 다른 클러스터에서도 그대로 씁니다.
워크로드 쪽은 EKS API 호출 하나, association입니다. Kubernetes 객체는 건드리지 않습니다. 나머지는 IRSA와 같습니다. rollout으로 Pod를 새로 만들고, 컨테이너 자격 증명 변수와 호출자 ARN을 확인한 뒤 노드 역할에서 정책 문장을 뺍니다.
이미 IRSA를 쓰고 있다면 신뢰 정책에 서비스 principal을 추가한 다음 association을 만들고 rollout합니다. 확인이 끝나면 OIDC 쪽 신뢰와 주석을 정리합니다. eksctl utils migrate-to-pod-identity는 Agent 설치, 신뢰 정책 추가, association 생성을 클러스터 전체에 한 번에 해 줍니다. rollout, 확인, 주석 정리는 직접 해야 하고, OIDC 신뢰는 --remove-oidc-provider-trust-relationship을 줄 때만 지웁니다. 애드온 역할은 항상 지웁니다. --approve 없이 돌리면 계획만 보여 주니 계획부터 보시길 권합니다.
{cue: transition}
다른 계정의 리소스에 접근해야 할 때는 어떻게 다른지 보겠습니다.
:::

---
<!-- Slide 5: 교차 계정 -->
@type: content
@title: 교차 계정: IRSA와 Pod Identity

## 교차 계정: IRSA와 Pod Identity

:::html
<table class="data-table wid-table">
  <thead><tr><th>A 계정 클러스터의 Pod가 B 계정 리소스로</th><th><span class="wid-chip wid-irsa">IRSA</span></th><th><span class="wid-chip wid-podid">Pod Identity (대상 역할)</span></th></tr></thead>
  <tbody>
    <tr><td>B 계정에서 할 일</td><td>A 클러스터의 OIDC issuer를 B 계정 IAM provider로 등록, B 역할에 Federated 신뢰와 sub, aud 조건</td><td>B 역할이 A 역할을 신뢰, External ID 조건 권장</td></tr>
    <tr><td>클러스터가 늘면</td><td>B 계정마다 provider 등록과 신뢰 정책 수정. 클러스터 수 × 계정 수만큼 provider</td><td>B 쪽은 그대로, A 쪽에 association만 추가</td></tr>
    <tr><td>역할 홉</td><td>Pod가 B 역할을 바로 맡음 (1홉)</td><td>A 역할을 거쳐 B 역할로, EKS가 대신 체이닝</td></tr>
    <tr><td>앱 변경</td><td>없음, SA 주석에 B 역할 ARN</td><td>없음, association에 두 역할</td></tr>
  </tbody>
</table>
<div class="wid-grid-21 wid-gap-top">
<pre class="wid-term">aws eks create-pod-identity-association \
  --cluster-name $CLUSTER --namespace orders --service-account orders \
  --role-arn        arn:aws:iam::&lt;ACCOUNT_A&gt;:role/account-a-role \
  --target-role-arn arn:aws:iam::&lt;ACCOUNT_B&gt;:role/account-b-role</pre>
  <div class="wid-panel"><strong>External ID</strong> <span class="wid-muted">EKS가 <code>리전/A계정/클러스터/namespace/SA</code>로 자동으로 넣습니다. B 역할 신뢰 정책의 <code>sts:ExternalId</code> 조건에 이 값을 겁니다.</span></div>
</div>
<div class="wid-src">출처: <a href="https://aws.amazon.com/blogs/containers/amazon-eks-pod-identity-streamlines-cross-account-access/">AWS Containers Blog, EKS Pod Identity streamlines cross account access</a>, <a href="https://docs.aws.amazon.com/eks/latest/best-practices/multi-account-strategy.html">EKS Best Practices, Multi Account Strategy</a></div>
:::

:::notes
{timing: 1min}
[요약]
- IRSA: B 계정마다 A 클러스터의 OIDC provider를 등록하고 B 역할에 Federated 신뢰. 클러스터 수 × 계정 수만큼 provider가 늘어 한도(계정당 기본 100)에 닿기 쉬움
- Pod Identity: association에 A 역할(--role-arn)과 B 역할(--target-role-arn)을 함께 지정, EKS가 역할 체이닝. B 쪽 설정은 클러스터가 늘어도 그대로
- A 역할 권한: B 역할에 sts:AssumeRole, sts:TagSession. B 역할 신뢰: A 역할 + sts:ExternalId 조건(TagSession은 별도 문장)
- 주의: 세션 태그로 PackedPolicyTooLarge가 나면 --disable-session-tags (그러면 태그 조건은 못 씀)

교차 계정은 질문이 많이 나오는 부분이라 따로 정리했습니다. IRSA는 B 계정 역할을 Pod가 바로 맡으니 단순해 보이지만, 그러려면 B 계정 IAM에 A 클러스터의 OIDC provider를 등록해야 합니다. 클러스터가 늘 때마다 B 계정마다 등록과 신뢰 정책 수정이 반복됩니다.
Pod Identity는 association에 역할을 두 개 넣습니다. 클러스터 계정의 A 역할과 리소스 계정의 B 역할입니다. EKS가 A 역할로 B 역할을 대신 맡아서 Pod에는 B 역할 자격 증명이 들어갑니다. B 계정은 A 역할만 신뢰하면 되니 클러스터가 늘어도 손댈 게 없습니다.
B 역할 신뢰 정책에는 External ID 조건을 거는 걸 권장합니다. EKS가 리전, A 계정, 클러스터, namespace, ServiceAccount를 이어 붙인 값을 자동으로 넣어 줍니다.
{cue: transition}
옮기는 도중에 주석과 association이 함께 걸려 있으면 어떻게 되는지 보겠습니다.

[약어]
- External ID: AssumeRole 요청에 붙는 식별 값, confused deputy 방지용
:::

---
<!-- Slide 6: 공존과 프라이빗 경로 -->
@type: content
@title: 주석이 남아도 새 Pod는 Pod Identity

## 주석이 남아도 새 Pod는 Pod Identity

:::html
<div class="wid-grid-2">
  <div class="wid-card">
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
    <div class="callout callout-warning"><strong class="wid-t-warning">체인 순서와 헷갈리지 않기</strong>: 체인에서는 웹 ID 토큰이 앞이지만, EKS는 한 Pod에 두 변수 세트를 함께 넣지 않습니다.</div>
    <div class="wid-card">
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

IRSA를 쓰던 앱을 Pod Identity로 옮기는 도중이라고 해 보겠습니다. ServiceAccount에는 role-arn 주석이 남아 있고, association을 새로 만들었습니다. 이때 새로 만든 Pod에는 EKS 웹훅이 Pod Identity 변수만 넣고 IRSA 변수는 넣지 않습니다. 데모 클러스터에서 server-side dry run으로 직접 확인했습니다.
association을 만들기 전에 떠 있던 Pod는 IRSA 변수를 그대로 갖고 있으니, rollout이 끝날 때까지는 두 역할이 섞여 보일 수 있습니다. 전환이 끝나면 주석을 지워 설정을 하나로 정리합니다.
SDK 자격 증명 체인은 웹 ID 토큰을 먼저 보니 IRSA가 이길 것 같지만(체인 그림은 부록에 있습니다), 결정은 그보다 앞의 주입 단계에서 납니다. 이 부분은 헷갈리기 쉬우니 꼭 구분해 주세요.
프라이빗 클러스터라면 필요한 경로가 다릅니다. IRSA는 Pod에서 STS로, Pod Identity는 Agent에서 EKS Auth로 가는 길이 필요합니다.
{cue: transition}
마지막으로 Pod의 IMDS 경로를 닫습니다.
:::

---
<!-- Slide 7: IMDS 차단 -->
@type: content
@title: 마지막에 Pod의 IMDS 길을 닫는다

## 마지막에 Pod의 IMDS 길을 닫는다

:::html
<div class="wid-grid-3">
  <div class="wid-card">
    <h4>관리형 노드 그룹</h4>
    <div class="wid-muted">launch template 새 버전에 지정하고 롤링 교체</div>
<pre class="wid-term wid-gap-top">HttpTokens=required
HttpPutResponseHopLimit=1</pre>
  </div>
  <div class="wid-card">
    <h4>Karpenter</h4>
    <div class="wid-muted">EC2NodeClass 기본값이 이미 required, hop limit 1. 2로 바꿔 둔 NodeClass만 되돌림</div>
<pre class="wid-term wid-gap-top">spec:
  metadataOptions:
    httpTokens: required
    httpPutResponseHopLimit: 1</pre>
  </div>
  <div class="wid-card">
    <h4>EKS Auto Mode</h4>
    <div class="wid-muted">IMDSv2와 hop limit 1이 기본 적용</div>
    <div class="wid-cap wid-gap-top">별도 설정 없이 일반 Pod의 IMDS 경로가 닫혀 있습니다.</div>
  </div>
</div>
<div class="wid-grid-2 wid-gap-top">
  <div class="callout callout-warning"><strong class="wid-t-warning">hostNetwork Pod는 예외</strong>: 노드 네트워크를 그대로 쓰므로 hop limit과 관계없이 IMDS에 닿습니다. 별도로 통제합니다.</div>
  <div class="callout callout-warning"><strong class="wid-t-warning">IMDS 자체는 끄지 않기</strong>: Pod Identity Agent도 hostNetwork에서 IMDS로 노드 역할을 받습니다. <code>HttpEndpoint=disabled</code>면 Pod Identity가 멈춥니다.</div>
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

관리형 노드 그룹은 launch template 새 버전을 만들고 롤링 교체합니다. 노드가 바뀌어야 적용되니 시간이 걸립니다. 리허설에서는 노드 한 대 교체에 878초, 15분 가까이 걸렸습니다.
Karpenter는 EC2NodeClass의 metadataOptions에서 정하는데, 기본값이 이미 httpTokens required, hop limit 1입니다. 2로 바꿔 둔 NodeClass가 있는지만 확인해서 되돌리면 됩니다.
Auto Mode는 이미 IMDSv2와 hop limit 1이 기본입니다.
예외가 하나 있습니다. hostNetwork Pod는 노드 네트워크를 그대로 쓰니 hop limit을 1로 내려도 IMDS에 닿습니다. 이런 Pod는 별도로 관리해야 합니다.
그리고 "닫는다"는 말을 IMDS를 끈다는 뜻으로 받아들이시면 안 됩니다. Pod Identity Agent도 hostNetwork에서 IMDS로 노드 역할을 받아서 EKS Auth를 부릅니다. hop limit 1에서 Agent가 살아 있는 것도 hostNetwork이기 때문이고, HttpEndpoint를 disabled로 하면 Pod Identity 전체가 멈춥니다.
{cue: transition}
여기까지가 절차입니다. 이제 실제 클러스터에서 확인하겠습니다.
:::
