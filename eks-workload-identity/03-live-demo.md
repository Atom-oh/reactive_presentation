---
remarp: true
block: 03-live-demo
---

---
<!-- Slide 1: 3부 구분 -->
@type: section

# 3부: 라이브 데모

같은 앱 세 벌을 노드 역할에서 IRSA와 Pod Identity로

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
- 3부: 앞에서 본 동작을 실제 EKS 클러스터에서 확인
- 같은 orders 앱 세 벌 중 한 벌은 IRSA로, 한 벌은 Pod Identity로 옮기고, 마지막에 노드 역할의 S3 권한을 회수
- 단계마다 실측 화면 슬라이드가 있어 라이브가 막혀도 설명을 이어 갈 수 있음

이제 라이브 데모입니다. 같은 앱 세 벌을 띄워 두고, 한 벌씩 옮긴 다음 노드 역할의 권한을 지워서 누가 살아남는지 보겠습니다.
단계마다 명령과 기대 화면을 슬라이드에 그대로 넣어 두었습니다. 화면이 기대와 다르면 슬라이드의 실측 화면으로 설명을 이어 가겠습니다.
{cue: transition}
먼저 무대 구성입니다.
:::

---
<!-- Slide 2: 데모 구성 -->
@type: content
@title: 데모 무대: 노드 한 대, 앱 세 벌, 객체 하나

## 데모 무대: 노드 한 대, 앱 세 벌, 객체 하나

:::html
<div class="wid-grid-3">
  <div class="wid-card">
    <h4>환경</h4>
    <div class="wid-muted"><strong>기존 EKS 1.36 클러스터의 전용 노드 그룹 1대, orders 앱 3벌, S3 객체 1개</strong></div>
    <div class="wid-cap wid-gap-top">t3.medium, Private 서브넷, taint 적용. IMDSv2 필수, hop limit 2. 노드 역할에 앱의 s3:GetObject가 붙은 출발점</div>
  </div>
  <div class="wid-card">
    <h4>앱 (세 벌 모두 같은 코드)</h4>
    <div class="wid-muted">3초마다 STS(Security Token Service)에 <code>get-caller-identity</code>로 호출자를 묻고, <code>s3api get-object</code>를 호출해 JSON 한 줄을 남깁니다.</div>
    <div class="wid-cap wid-gap-top">hostNetwork 없는 일반 Pod, Pod 안의 AWS CLI 2.35.11, 자격 증명과 토큰은 출력하지 않음</div>
  </div>
  <div class="wid-card">
    <h4>안전장치</h4>
    <div class="wid-muted">만든 리소스에만 Lab, LabRun 태그를 붙이고 수정 전에 확인합니다.</div>
    <div class="wid-cap wid-gap-top">VPC, 서브넷, 보안 그룹, 애드온, OIDC provider는 만들지 않음. 계정 ID와 OIDC ID는 가려서 출력</div>
  </div>
</div>
<div class="wid-grid-2 wid-gap-top">
<pre class="wid-term"><span class="wid-dim"># 발표 전 (약 5분)</span>
export AWS_REGION=ap-northeast-2  RUN_ID=d1124
./demo.sh up    "$RUN_ID"</pre>
<pre class="wid-term"><span class="wid-dim"># 두 번째 터미널: 2초마다 갱신되는 표</span>
./demo.sh watch "$RUN_ID"</pre>
</div>
<div class="wid-card wid-gap-top"><strong>청중용 실시간 화면 (읽기 전용):</strong> <code>https://wid-demo.atomai.click/</code> <span class="wid-cap">CloudFront → VPC origin → internal ALB → 대시보드 Pod. <code>./demo.sh page-up "$RUN_ID"</code>로 발표 전에 띄움. 발표 중에만 열려 있음</span></div>
<div class="wid-src">데모 코드와 런북: github.com/Atom-oh/kubernetes-docs, examples/security/eks-workload-identity</div>
:::

:::notes
{timing: 1.5min}
[요약]
- 기존 EKS 1.36 클러스터에 전용 관리형 노드 그룹 한 대(t3.medium, Private 서브넷, taint)를 붙임
- 출발점: IMDSv2 필수, hop limit 2, 노드 역할에 앱의 s3:GetObject. 레거시 Pod도 hostNetwork 없는 일반 Pod
- orders 앱 세 벌(legacy, irsa, podid)이 3초마다 GetCallerIdentity와 GetObject, JSON 한 줄 출력
- up과 page-up은 발표 전에 실행(약 5분, 약 10분), watch는 두 번째 터미널, 청중은 공개 읽기 전용 페이지

데모 환경입니다. 이미 있는 EKS 1.36 클러스터에 이 데모만 쓰는 노드 그룹 한 대를 붙였고, 그 위에 같은 orders 앱을 세 벌 띄웠습니다. 출발점은 흔한 운영 상태 그대로, hop limit 2에 노드 역할이 앱의 S3 권한을 갖고 있습니다.
앱은 3초마다 "나는 누구인가"와 "객체를 읽을 수 있는가"를 물어서 한 줄로 남깁니다. 자격 증명 자체는 출력하지 않습니다.
up은 발표 전에 돌려 두었고, 왼쪽 터미널에서 watch가 2초마다 세 벌의 상태를 보여 줍니다.
여러분도 휴대폰이나 노트북으로 이 주소를 열어 보세요. 같은 상태를 카드로 보여 주는 읽기 전용 페이지입니다. CloudFront에서 VPC origin을 거쳐 internal ALB로만 들어오고, 대시보드 Pod에는 AWS 권한이 없습니다. 페이지가 안 열리면 터미널 watch로 진행합니다.
{cue: demo}
화면을 터미널로 전환합니다. watch가 떠 있지 않으면 ./demo.sh watch "$RUN_ID"를 먼저 실행합니다.
발표자 참고: 클리커의 오른쪽, Space, PageDown 키는 캔버스와 탭의 단계를 건너뛰고 다음 슬라이드로 넘어갑니다. 단계는 아래 방향키나 Play로 넘깁니다.
{cue: transition}
0단계, 지금 상태부터 보겠습니다.
:::

---
<!-- Slide 3: 0단계 -->
@type: content
@title: 0단계: 지금은 셋 다 노드 역할

## 0단계: 지금은 셋 다 노드 역할

:::html
<div class="wid-row"><span class="wid-stepbadge">0</span><pre class="wid-term">$ ./demo.sh watch "$RUN_ID"   <span class="wid-dim"># 이미 실행 중</span></pre></div>
<div class="wid-card wid-gap-top">
  <h4>watch 화면의 기대 값</h4>
<pre class="wid-term">COPY            CREDENTIALS    ROLE                           S3
orders-legacy   node (IMDS)    wid-d1124-node  ← node         <span class="wid-ok">allowed</span>
orders-irsa     node (IMDS)    wid-d1124-node  ← node         <span class="wid-ok">allowed</span>
orders-podid    node (IMDS)    wid-d1124-node  ← node         <span class="wid-ok">allowed</span></pre>
  <div class="wid-cap">리허설 화면, RUN_ID=d1124. 맨 오른쪽 AT 열(마지막 로그 시각)은 생략</div>
</div>
<div class="wid-grid-2 wid-gap-top">
  <div class="callout callout-info"><strong class="wid-t-info">볼 곳</strong>: CREDENTIALS 열은 주입된 변수로 판단한 출처, ROLE 열은 STS가 알려 준 실제 호출자입니다.</div>
  <div class="callout callout-info"><strong class="wid-t-info">의미</strong>: 이름이 달라도 세 벌 모두 노드 역할로 같은 객체를 읽고 있습니다.</div>
</div>
:::

:::notes
{timing: 1min}
{cue: demo}
[요약]
- 명령: 없음 (watch가 이미 실행 중, 없으면 ./demo.sh watch "$RUN_ID")
- 기대: 세 행 모두 node (IMDS), wid-<run>-node ← node, allowed
- CREDENTIALS는 Pod에 주입된 변수로 판단한 출처, ROLE은 GetCallerIdentity가 돌려준 실제 역할

watch 화면을 보시면 orders-legacy, orders-irsa, orders-podid 세 행이 있습니다. 이름은 다르지만 지금은 셋 다 node (IMDS), 노드 역할, allowed입니다.
CREDENTIALS 열은 Pod에 어떤 변수가 주입됐는지로 판단한 출처이고, ROLE 열은 STS에 직접 물어본 실제 호출자입니다. 이 두 열이 같이 바뀌는지를 계속 보겠습니다.
화면이 바뀌지 않으면: 행이 starting이나 - 로만 보이면 Pod가 아직 뜨는 중이니 몇 초 기다리고, 계속 비어 있으면 이 슬라이드의 기대 화면으로 설명합니다.
{cue: transition}
첫 번째 이전, IRSA입니다.
:::

---
<!-- Slide 4: 1단계 migrate-irsa -->
@type: content
@title: 1단계 migrate-irsa: 주석 하나

## 1단계 migrate-irsa: 주석 하나

:::html
<div class="wid-row"><span class="wid-stepbadge">1</span><pre class="wid-term">$ ./demo.sh migrate-irsa "$RUN_ID"</pre><span class="wid-chip wid-irsa">실측 6초</span></div>
<div class="wid-stack wid-gap-top">
  <div class="wid-card">
    <h4>스크립트가 실행하는 것</h4>
<pre class="wid-term">kubectl -n wid-&lt;run&gt; annotate serviceaccount orders-irsa --overwrite \
  eks.amazonaws.com/role-arn=arn:aws:iam::&lt;ACCOUNT_ID&gt;:role/wid-&lt;run&gt;-irsa
kubectl -n wid-&lt;run&gt; rollout restart deployment/orders-irsa
kubectl -n wid-&lt;run&gt; rollout status  deployment/orders-irsa</pre>
    <div class="wid-cap wid-gap-top">IRSA 역할과 IAM OIDC provider는 up에서 이미 준비되어 있습니다.</div>
  </div>
  <div class="wid-card wid-irsa wid-edge">
    <h4>watch에서 바뀌는 행</h4>
<pre class="wid-term"><span class="wid-hl">orders-irsa     IRSA (STS)     wid-d1124-irsa                 <span class="wid-ok">allowed</span></span></pre>
    <div class="wid-muted wid-gap-top">새 Pod에 주입된 변수: <code>AWS_ROLE_ARN</code>, <code>AWS_WEB_IDENTITY_TOKEN_FILE</code>, <code>AWS_STS_REGIONAL_ENDPOINTS</code></div>
    <div class="wid-cap wid-gap-top">나머지 두 행은 그대로 노드 역할입니다.</div>
  </div>
</div>
:::

:::notes
{timing: 1.5min}
{cue: demo}
[요약]
- 명령: ./demo.sh migrate-irsa "$RUN_ID"
- 하는 일: ServiceAccount orders-irsa에 role-arn 주석, 그다음 rollout restart와 rollout status
- 기대: orders-irsa 행이 IRSA (STS), wid-<run>-irsa, allowed. 리허설 2회차 실측 6초
- 새 Pod env: AWS_STS_REGIONAL_ENDPOINTS, AWS_ROLE_ARN, AWS_WEB_IDENTITY_TOKEN_FILE

오른쪽 터미널에서 ./demo.sh migrate-irsa "$RUN_ID"를 실행합니다. 스크립트는 ServiceAccount에 주석 하나를 달고, Deployment를 재시작합니다. 리허설 2회차에서 6초 걸렸습니다.
watch에서 orders-irsa 행만 IRSA (STS), wid-<run>-irsa로 바뀝니다. 앱 코드는 그대로이고 Pod가 새로 만들어지면서 변수가 주입된 결과입니다.
화면이 바뀌지 않으면: watch는 각 Deployment의 가장 새 Pod를 읽으니 rollout status가 끝날 때까지 몇 초 기다립니다. 그래도 node (IMDS)라면 ./demo.sh status "$RUN_ID"로 irsa SA 주석을 확인하고, ./demo.sh migrate-irsa "$RUN_ID"를 한 번 더 실행합니다(같은 단계를 다시 돌려도 안전합니다). 그래도 안 되면 이 슬라이드의 기대 행으로 설명을 이어 갑니다.
{cue: transition}
다음은 Pod Identity입니다.
:::

---
<!-- Slide 5: 2단계 migrate-podid -->
@type: content
@title: 2단계 migrate-podid: API 호출 하나

## 2단계 migrate-podid: API 호출 하나

:::html
<div class="wid-row"><span class="wid-stepbadge">2</span><pre class="wid-term">$ ./demo.sh migrate-podid "$RUN_ID"</pre><span class="wid-chip wid-podid">실측 11초 (주입 확인 5초 포함)</span></div>
<div class="wid-stack wid-gap-top">
  <div class="wid-card">
    <h4>스크립트가 실행하는 것</h4>
<pre class="wid-term">aws eks create-pod-identity-association \
  --cluster-name &lt;cluster&gt; --namespace wid-&lt;run&gt; \
  --service-account orders-podid \
  --role-arn arn:aws:iam::&lt;ACCOUNT_ID&gt;:role/wid-&lt;run&gt;-podid
<span class="wid-dim"># 주입될 때까지 Pod 템플릿을 --dry-run=server로 확인</span>
kubectl -n wid-&lt;run&gt; rollout restart deployment/orders-podid</pre>
  </div>
  <div class="wid-card wid-podid wid-edge">
    <h4>watch에서 바뀌는 행</h4>
<pre class="wid-term"><span class="wid-hl">orders-podid    Pod Identity   wid-d1124-podid                <span class="wid-ok">allowed</span></span></pre>
    <div class="wid-muted wid-gap-top">새 Pod에 주입된 변수: <code>AWS_CONTAINER_CREDENTIALS_FULL_URI</code>, <code>AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE</code>, <code>AWS_STS_REGIONAL_ENDPOINTS</code></div>
  </div>
</div>
<div class="callout callout-warning wid-gap-top"><strong class="wid-t-warning">리허설에서 본 eventual consistency</strong>: 1회차에서 association 생성 직후 재시작한 Pod에는 변수가 주입되지 않아 노드 역할을 계속 썼습니다. 그래서 스크립트는 admission에서 주입이 보인 뒤에 재시작합니다(2회차와 3회차 모두 생성 5초 뒤 확인).</div>
:::

:::notes
{timing: 2min}
{cue: demo}
[요약]
- 명령: ./demo.sh migrate-podid "$RUN_ID"
- 하는 일: create-pod-identity-association, Pod 템플릿을 server-side dry run으로 보내 주입 확인, 그다음 rollout
- 기대: orders-podid 행이 Pod Identity, wid-<run>-podid, allowed. 리허설 2회차 실측 11초(주입 확인 5초 포함)
- 함정: association은 eventually consistent. 1회차는 생성 직후 rollout해서 주입 실패, 노드 역할 유지
- 2회차와 3회차는 생성 5초 뒤 주입 확인. 터미널의 "injected after Ns" 줄이 말할 거리

./demo.sh migrate-podid "$RUN_ID"를 실행합니다. Kubernetes 쪽에는 아무것도 바꾸지 않고 EKS API 호출 하나로 연결합니다.
orders-podid 행이 Pod Identity, wid-<run>-podid로 바뀝니다. 리허설 2회차에서 11초 걸렸고, 그중 5초가 주입 확인 대기였습니다.
리허설에서 한 번 배운 점이 있습니다. 1회차에서 association을 만든 직후 바로 재시작했더니 새 Pod에 변수가 안 들어가서 노드 역할을 그대로 썼습니다. 그래서 스크립트가 mutating 웹훅을 거치는 dry run으로 주입을 먼저 확인합니다. 터미널의 "injected after"가 그 대기 시간인데, 2회차와 3회차 모두 5초였습니다. 오늘은 몇 초가 나오는지 같이 보시죠. 운영에서도 association 직후 바로 rollout하면 같은 일이 생길 수 있습니다.
화면이 바뀌지 않으면: 터미널에 "injected after Ns"가 찍혔는지 보고, 행이 여전히 node (IMDS)면 ./demo.sh migrate-podid "$RUN_ID"를 한 번 더 실행합니다(association이 있으면 만들지 않고 주입 확인과 rollout만 다시 합니다). 그래도 안 되면 이 슬라이드의 기대 행으로 설명합니다.
{cue: transition}
두 Pod가 실제로 무엇을 받았는지 나란히 보겠습니다.
:::

---
<!-- Slide 6: 3단계 diff -->
@type: content
@title: 3단계 diff: 같은 issuer, 다른 aud

## 3단계 diff: 같은 issuer, 다른 aud

:::html
<div class="wid-row"><span class="wid-stepbadge">3</span><pre class="wid-term">$ ./demo.sh diff "$RUN_ID"</pre></div>
<table class="data-table wid-table wid-gap-top">
  <thead><tr><th>비교</th><th><span class="wid-chip wid-irsa">IRSA Pod</span></th><th><span class="wid-chip wid-podid">Pod Identity Pod</span></th></tr></thead>
  <tbody>
    <tr><td>주입된 env</td><td><code>AWS_ROLE_ARN</code>, <code>AWS_WEB_IDENTITY_TOKEN_FILE</code>, <code>AWS_STS_REGIONAL_ENDPOINTS</code></td><td><code>AWS_CONTAINER_CREDENTIALS_FULL_URI</code>, <code>AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE</code>, <code>AWS_STS_REGIONAL_ENDPOINTS</code></td></tr>
    <tr><td>토큰 aud</td><td><code>sts.amazonaws.com</code></td><td><code>pods.eks.amazonaws.com</code></td></tr>
    <tr><td>토큰 sub</td><td><code>system:serviceaccount:wid-&lt;run&gt;:orders-irsa</code></td><td><code>system:serviceaccount:wid-&lt;run&gt;:orders-podid</code></td></tr>
    <tr><td>토큰 iss, 수명</td><td colspan="2">같은 클러스터 issuer <code>https://oidc.eks.ap-northeast-2.amazonaws.com/id/&lt;OIDC_ID&gt;</code>. IRSA 86,400초(24시간), Pod Identity 약 22~24시간(웹훅이 무작위 편차를 줌)</td></tr>
    <tr><td>역할 신뢰 principal</td><td><code>Federated</code>: OIDC provider, 조건 aud와 sub</td><td><code>Service</code>: <code>pods.eks.amazonaws.com</code>, 요청 태그 조건 3개</td></tr>
  </tbody>
</table>
<div class="wid-cap wid-gap-top">diff는 토큰의 claim만 디코딩해 보여 주고, 토큰 원문과 자격 증명은 출력하지 않습니다.</div>
:::

:::notes
{timing: 1.5min}
{cue: demo}
[요약]
- 명령: ./demo.sh diff "$RUN_ID"
- env: IRSA는 AWS_ROLE_ARN, AWS_WEB_IDENTITY_TOKEN_FILE, Pod Identity는 AWS_CONTAINER_CREDENTIALS_FULL_URI, AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE (둘 다 AWS_STS_REGIONAL_ENDPOINTS)
- 토큰: 같은 클러스터 issuer가 서명, aud만 다름(sts.amazonaws.com 대 pods.eks.amazonaws.com), 수명 IRSA 24시간, Pod Identity 약 22~24시간
- 신뢰: Federated OIDC provider와 aud, sub 조건 대 Service pods.eks.amazonaws.com과 요청 태그 3개

./demo.sh diff "$RUN_ID"를 실행합니다. 두 Pod에 무엇이 들어갔는지 다섯 항목으로 나란히 찍습니다.
환경 변수는 1, 2단계에서 본 그대로입니다. 흥미로운 건 토큰입니다. 둘 다 같은 클러스터 issuer가 서명한 ServiceAccount 토큰인데 audience만 다릅니다. IRSA 토큰은 STS가, Pod Identity 토큰은 EKS가 받는 쪽입니다.
신뢰 정책도 한쪽은 클러스터의 OIDC provider, 다른 쪽은 EKS 서비스 principal을 믿습니다. 결과는 같고 배선이 다르다는 것이 이 화면의 요점입니다.
화면이 바뀌지 않으면: "app pods are not running"이 나오면 직전 rollout이 아직 진행 중이니 몇 초 뒤 다시 실행하고, 출력이 늦으면 이 표로 설명합니다.
{cue: transition}
이제 노드 역할에서 권한을 지웁니다.
:::

---
<!-- Slide 7: 4단계 revoke -->
@type: content
@title: 4단계 revoke: 레거시만 13초 뒤 거부

## 4단계 revoke: 레거시만 13초 뒤 거부

:::html
<div class="wid-row"><span class="wid-stepbadge">4</span><pre class="wid-term">$ ./demo.sh revoke "$RUN_ID"</pre><span class="wid-chip wid-node">실측 13초 후 거부 (2회 모두)</span></div>
<div class="wid-stack wid-gap-top">
  <div class="wid-card">
    <h4>스크립트가 실행하는 것</h4>
<pre class="wid-term">aws iam delete-role-policy --role-name wid-&lt;run&gt;-node \
  --policy-name OrdersReadInvoices
<span class="wid-dim"># legacy 행이 denied가 될 때까지 대기 (최대 180초)</span></pre>
  </div>
  <div class="wid-card">
    <h4>watch 화면의 기대 값</h4>
<pre class="wid-term">COPY            CREDENTIALS    ROLE                           S3        AT
<span class="wid-hl">orders-legacy   node (IMDS)    wid-d1124-node  ← node       <span class="wid-no">denied</span>    04:12:56</span>
orders-irsa     IRSA (STS)     wid-d1124-irsa                 <span class="wid-ok">allowed</span>   04:12:58
orders-podid    Pod Identity   wid-d1124-podid                <span class="wid-ok">allowed</span>   04:12:58</pre>
    <div class="wid-cap">revoke 직후 리허설 화면 그대로</div>
  </div>
</div>
<div class="callout callout-warning wid-gap-top"><strong class="wid-t-warning">IAM 회수도 eventual consistency</strong>: 첫 리허설에서 첫 denied 약 4분 30초 뒤에 allowed가 두 번 더 나왔고, 그 직후 다시 확인한 1분 동안(로그 11건)은 모두 denied였습니다. 운영에서는 회수 후 수 분 이상 관찰하고 판단합니다.</div>
:::

:::notes
{timing: 2min}
{cue: demo}
[요약]
- 명령: ./demo.sh revoke "$RUN_ID"
- 하는 일: 노드 역할 wid-<run>-node의 인라인 정책 OrdersReadInvoices 삭제, legacy가 denied가 될 때까지 대기
- 기대: orders-legacy만 denied, irsa와 podid는 allowed 유지(2회차). 레거시는 두 번 모두 13초 후 거부
- 1회차는 주입이 안 된 podid도 함께 거부됨(그래서 주입 확인 단계를 넣음)
- 주의: 첫 리허설에서 첫 denied 약 4분 30초 뒤 allowed가 두 번 더 나왔고, 직후 1분(로그 11건)은 모두 denied. 노드 역할 자체는 계속 발급됨

./demo.sh revoke "$RUN_ID"를 실행합니다. 노드 역할에서 앱의 S3 정책을 지웁니다.
레거시는 두 번 모두 13초 뒤 거부됐습니다. 2회차에는 옮긴 두 벌이 계속 allowed였고, 1회차에는 주입이 안 된 podid도 함께 거부됐습니다. 그래서 주입 확인 단계를 넣었습니다. ROLE 열은 여전히 노드 역할입니다. 자격 증명은 계속 나오고, 그 역할에 S3 권한이 없어졌을 뿐입니다.
한 가지 미리 말씀드립니다. 첫 리허설에서 첫 denied가 나오고 4분 30초쯤 뒤에 allowed가 두 번 더 보였습니다. 그 직후 1분 동안 다시 확인한 로그 11건은 모두 denied였습니다. IAM 변경도 바로 모든 곳에 반영되지 않으니, 운영에서 회수한 뒤에는 수 분 이상 지켜보고 판단해야 합니다.
화면이 바뀌지 않으면: 스크립트가 최대 180초 기다리며 "legacy still: allowed"를 찍으니 그동안 이 슬라이드의 기대 화면과 eventual consistency 설명을 하고, 180초를 넘기면 이 슬라이드로 결과를 설명합니다.
{cue: transition}
마지막 단계는 Pod의 IMDS 경로 차단입니다. 15분쯤 걸리니 지금 실행만 걸어 두겠습니다.
:::

---
<!-- Slide 8: 5단계 harden (옵션) -->
@type: content
@title: 5단계 harden (옵션): hop limit 1

## 5단계 harden (옵션): hop limit 1

:::html
<div class="wid-row"><span class="wid-stepbadge">5</span><pre class="wid-term">$ ./demo.sh harden "$RUN_ID"</pre><span class="wid-tag-opt">옵션</span><span class="wid-chip wid-node">실측 878초 (약 15분)</span></div>
<div class="callout callout-warning wid-gap-top"><strong class="wid-t-warning">revoke 직후 실행만 시작하고, 결과는 리허설 값으로 설명 (선택)</strong>: 노드 교체에 약 15분이 걸려 발표 시간 안에는 끝나지 않을 수 있습니다. 시간이 남으면 마지막에 watch를 확인합니다.</div>
<div class="wid-grid-2 wid-gap-top">
  <div class="wid-card">
    <h4>스크립트가 하는 일</h4>
    <div class="wid-muted">launch template 새 버전(hop limit 1)으로 관리형 노드 그룹을 롤링 교체합니다.</div>
    <div class="wid-cap wid-gap-top">새 노드 추가, 기존 노드 drain, 종료 순서. <code>restore</code>는 hop limit 2로 돌리느라 노드를 한 번 더 교체합니다(실측 578초).</div>
  </div>
  <div class="wid-card">
    <h4>watch 화면의 기대 값</h4>
<pre class="wid-term"><span class="wid-hl">orders-legacy   node (IMDS)    no-credentials                 <span class="wid-no">no-creds</span></span>
orders-irsa     IRSA (STS)     wid-d1124-irsa                 <span class="wid-ok">allowed</span>
orders-podid    Pod Identity   wid-d1124-podid                <span class="wid-ok">allowed</span></pre>
    <div class="wid-cap wid-gap-top">레거시 Pod는 IMDS 응답이 차단되어 자격 증명을 아예 받지 못합니다. 리허설 로그 한 줄:</div>
<pre class="wid-term">{"src":"imds","role":"no-credentials","s3":"no-creds"}</pre>
  </div>
</div>
:::

:::notes
{timing: 1min}
[요약]
- 명령: ./demo.sh harden "$RUN_ID" (옵션). revoke 직후 실행만 시작하고 기다리지 않음
- 무대에서 보여 줄 것: 명령과, ./demo.sh status "$RUN_ID"에서 노드 그룹이 UPDATING인 것
- 결과는 리허설 값으로 설명. 시간이 남을 때만 맨 마지막에 watch 확인
- 하는 일: hop limit 1 launch template 새 버전으로 노드 그룹 롤링 교체(새 노드, drain, 종료). 실측 878초, 약 15분
- 기대: orders-legacy는 no-credentials와 no-creds, irsa와 podid는 allowed
- 발표 후: ./demo.sh restore "$RUN_ID"(harden 뒤 약 10분, 실측 578초) 또는 ./demo.sh down "$RUN_ID"

마지막 단계는 옵션입니다. 오른쪽 터미널에서 ./demo.sh harden "$RUN_ID"를 실행합니다. hop limit을 1로 바꾼 노드로 교체하는데, 리허설에서 878초, 15분 가까이 걸렸습니다. 그래서 실행만 시작해 두겠습니다. ./demo.sh status "$RUN_ID"를 실행하면 노드 그룹이 UPDATING으로 바뀐 것이 보입니다. 결과는 발표 시간 안에 끝나지 않을 수 있어 리허설 결과로 설명드리겠습니다.
리허설에서 교체가 끝난 뒤에는 레거시 Pod가 권한 거부가 아니라 자격 증명 자체를 받지 못했습니다. 앱 로그가 {"src":"imds","role":"no-credentials","s3":"no-creds"}였습니다. 옮긴 두 벌은 IMDS를 쓰지 않으니 영향이 없습니다. 이게 2부 마지막 장에서 말씀드린 "마지막에 길을 닫는다"의 결과입니다.
발표 전에 같은 RUN_ID로 미리 harden하지는 않습니다. 0단계부터 레거시 행이 no-credentials가 되어 데모 흐름이 맞지 않습니다.
화면이 바뀌지 않으면: 명령이 "rolling the node group to hop limit 1"과 점을 찍고 있으면 정상 진행 중이니 그대로 다음 슬라이드로 갑니다. 교체 중에는 Pod가 옮겨지느라 watch의 irsa, podid 행이 잠시 starting이나 - 로 보일 수 있습니다. 결과는 이 슬라이드의 리허설 값(레거시는 no-credentials와 no-creds, 나머지 allowed, 878초)으로 설명합니다.
{cue: transition}
지금까지의 결과를 한 장으로 정리하겠습니다.
:::

---
<!-- Slide 9: 실측 결과 -->
@type: content
@title: 실측 결과: 옮긴 두 벌만 살아남았다

## 실측 결과: 옮긴 두 벌만 살아남았다

:::html
<table class="data-table wid-table">
  <thead><tr><th>단계</th><th>orders-legacy</th><th>orders-irsa</th><th>orders-podid</th><th>걸린 시간</th></tr></thead>
  <tbody>
    <tr><td>시작</td><td>IMDS, 노드 역할, 읽기 성공</td><td>IMDS, 노드 역할, 읽기 성공</td><td>IMDS, 노드 역할, 읽기 성공</td><td class="wid-num">없음</td></tr>
    <tr><td><code>migrate-irsa</code></td><td>변화 없음</td><td>STS, IRSA 역할, 읽기 성공</td><td>변화 없음</td><td class="wid-num">6초</td></tr>
    <tr><td><code>migrate-podid</code></td><td>변화 없음</td><td>변화 없음</td><td>Agent, Pod Identity 역할, 읽기 성공</td><td class="wid-num">11초 (주입 확인 5초 포함)</td></tr>
    <tr><td><code>revoke</code></td><td><strong class="wid-t-danger">노드 역할, 읽기 거부</strong></td><td>읽기 성공</td><td>읽기 성공</td><td class="wid-num">13초 후 거부</td></tr>
    <tr><td><code>harden</code> (옵션, 1회차)</td><td><strong class="wid-t-danger">자격 증명 없음</strong></td><td>읽기 성공</td><td>읽기 성공</td><td class="wid-num">878초</td></tr>
  </tbody>
</table>
<div class="wid-grid-2 wid-gap-top">
  <div class="callout callout-warning"><strong class="wid-t-warning">association 전파</strong>: 1회차는 생성 직후 rollout해 주입 실패. 2회차와 3회차는 생성 5초 뒤 주입 확인</div>
  <div class="callout callout-warning"><strong class="wid-t-warning">IAM 회수 전파</strong>: 첫 리허설에서 첫 거부 약 4분 30초 뒤 허용 두 번, 직후 1분(로그 11건)은 모두 거부. 회수 후 수 분 이상 관찰</div>
</div>
<div class="wid-cap wid-gap-top">고친 스크립트로 처음부터 이어서 실행한 2회차 리허설 값, harden만 1회차(2026년 11월 21일, ap-northeast-2, EKS 1.36, Pod 안의 AWS CLI 2.35.11). harden 뒤 restore는 578초</div>
:::

:::notes
{timing: 1min}
[요약]
- 시작: 세 벌 모두 IMDS, 노드 역할, 읽기 성공
- 2회차 값: migrate-irsa 6초, migrate-podid 11초(주입 확인 5초 포함), revoke 13초 후 레거시만 거부. harden은 1회차 878초, restore 578초
- 1회차: 주입 실패한 podid도 revoke 뒤 거부. 레거시 13초는 두 번 모두 같음
- eventual consistency 두 가지: association 전파, IAM 회수 전파
- 2026-11-21 서울 리전, EKS 1.36, AWS CLI 2.35.11

한 장으로 보면 이렇습니다. 2회차 기준으로 옮기는 작업은 IRSA 6초, Pod Identity 11초였고, 회수하자 레거시만 13초 만에 거부됐습니다. 1회차에서는 주입이 안 된 podid도 함께 거부됐는데, 그게 주입 확인 단계를 넣은 이유입니다. harden까지 하면 레거시는 자격 증명 자체를 받지 못합니다.
그리고 두 번의 eventual consistency가 있었습니다. association은 만든 직후 바로 주입되지 않을 수 있고, IAM 회수도 몇 분 동안 흔들릴 수 있습니다. 운영 절차에 "확인하고 기다리는" 단계를 넣어야 하는 이유입니다.
한 번 실행한 값이니 벤치마크가 아니라 동작 확인용으로 봐 주세요.
{cue: transition}
데모 흐름을 애니메이션으로 한 번 더 보겠습니다.
:::

---
<!-- Slide 10: 데모 다시 보기 -->
@type: content
@fit: off
@title: 다시 보기: 권한을 지우면 누가 남나

## 다시 보기: 권한을 지우면 누가 남나

:::html
<div class="wid-fig-row">
  <figure class="wid-fig">
    <img src="images/ko-security-17-eks-workload-identity-migration-anim-3.svg" alt="데모 흐름. 처음에는 orders 앱 세 벌이 모두 IMDS에서 노드 역할을 받아 S3를 읽는다. migrate-irsa 뒤 한 벌은 STS로 IRSA 역할을, migrate-podid 뒤 다른 한 벌은 Pod Identity Agent로 Pod Identity 역할을 받는다. revoke로 노드 역할의 S3 권한을 지우면 레거시 한 벌만 AccessDenied가 된다.">
    <figcaption>오른쪽 위 배지가 데모 단계 (22초 반복)</figcaption>
  </figure>
  <div class="wid-stack">
    <div class="wid-card wid-node wid-edge"><span class="wid-chip wid-node">orders-legacy</span><div class="wid-muted">revoke 뒤 AccessDenied</div></div>
    <div class="wid-card wid-irsa wid-edge"><span class="wid-chip wid-irsa">orders-irsa</span><div class="wid-muted">IRSA 역할로 계속 읽기</div></div>
    <div class="wid-card wid-podid wid-edge"><span class="wid-chip wid-podid">orders-podid</span><div class="wid-muted">Pod Identity 역할로 계속 읽기</div></div>
  </div>
</div>
:::

:::notes
{timing: 1min}
[요약]
- 1 up: 세 벌 모두 노드 역할로 S3 읽기 성공
- 2 migrate-irsa, 3 migrate-podid: 한 벌씩 카드가 바뀜
- 4 revoke: 노드 역할 정책에 취소선, 레거시만 AccessDenied

방금 본 데모를 22초짜리 애니메이션으로 다시 정리했습니다. 오른쪽 위 배지가 단계 번호입니다.
처음에는 세 카드가 모두 노드 역할이고, 한 벌씩 파란색 IRSA, 분홍색 Pod Identity로 바뀝니다. 마지막에 노드 역할의 정책에 취소선이 그어지면 레거시만 거부됩니다.
결국 오늘 이전의 성공 기준은 "권한을 지워도 옮긴 워크로드는 멀쩡하다"는 것입니다.
{cue: transition}
운영에서 막혔을 때 보는 순서를 정리하겠습니다.
:::

---
<!-- Slide 11: 문제 해결 -->
@type: checklist
@title: 막히면 이 순서로 본다

## 막히면 이 순서로 본다

- [ ] **여전히 노드 역할이 보인다**: Pod를 새로 만들었는지, ServiceAccount 이름, IRSA 주석이나 정확한 association, 주입된 env 이름, SDK 버전
- [ ] **Pod Identity로 바꿨는데 IRSA 역할이 보인다**: association 전에 만든 Pod라 IRSA 변수를 그대로 가짐. rollout으로 재생성하고, 끝나면 주석 정리
- [ ] **IRSA 토큰 교환 실패**: 토큰 issuer에 맞는 IAM OIDC provider, 신뢰 정책의 aud와 sub, Pod에서 STS 도달
- [ ] **Pod Identity 조회 실패**: 그 노드의 Agent, EKS Auth 통신, 노드 역할의 eks-auth 권한, association 전파(수 초), 요청 태그 조건
- [ ] **역할은 맞는데 S3 거부**: 객체 ARN, 버킷 정책, SCP(Service Control Policy), 권한 경계, VPC 엔드포인트 정책, SSE-KMS(KMS 키로 서버 측 암호화)면 키 권한

:::notes
{timing: 1min}
[요약]
- 노드 역할이 보이면: 새 Pod, SA 이름, 주석이나 association, env 이름, SDK 버전
- IRSA가 보이면: association 전에 만든 Pod. 새 Pod에는 Pod Identity 변수만 주입되므로 rollout
- IRSA 실패: OIDC provider, aud와 sub, STS 경로
- Pod Identity 실패: Agent, EKS Auth 경로, eks-auth 권한, association 전파, 요청 태그
- S3 거부: 신원과 리소스 접근은 별개, 버킷 정책, SCP, 권한 경계, 엔드포인트 정책, KMS 키

항목을 클릭하면 체크됩니다. 위에서부터 증상별로 봅니다.
가장 흔한 건 첫 번째, 여전히 노드 역할이 보이는 경우입니다. 대부분 Pod를 새로 만들지 않았거나 ServiceAccount 이름이 다릅니다. 두 번째는 2부에서 본 공존 상황으로, 새 Pod는 Pod Identity를 쓰니 재생성하면 해결됩니다.
마지막 항목은 꼭 구분해 주세요. 역할이 맞게 나오는데 S3에서 거부된다면 신원 문제가 아니라 리소스 쪽 정책 문제입니다.
{cue: transition}
퀴즈로 정리해 보겠습니다.

[약어]
- SCP: Service Control Policy
- SSE-KMS: AWS KMS 키를 쓰는 S3 서버 측 암호화
:::

---
<!-- Slide 12: 퀴즈 1 -->
@type: quiz
@title: 퀴즈 1: 옮길 때 헷갈리는 것

## 퀴즈 1: 옮길 때 헷갈리는 것

**Q1: 이미 실행 중인 Deployment의 ServiceAccount에 IRSA role-arn 주석을 달았습니다. 다음으로 필요한 것은?**
[ ] 아무것도 필요 없다, 수 초 안에 반영된다
[x] rollout으로 Pod를 새로 만든다
[ ] 노드를 재부팅한다
[ ] 앱 코드에 역할 ARN을 넣는다

**Q2: IRSA Pod와 Pod Identity Pod의 토큰에서 서로 다른 claim은?**
[ ] iss (issuer)
[x] aud (audience)
[ ] 토큰 형식 (서명된 JWT)
[ ] 서명한 키

**Q3: IRSA 주석이 남아 있는 ServiceAccount에 Pod Identity association을 추가하고 rollout했습니다. 새 Pod가 쓰는 역할은?**
[ ] IRSA 역할 (체인에서 웹 ID 토큰이 앞이므로)
[x] Pod Identity 역할
[ ] 노드 역할
[ ] 두 변수가 함께 주입되어 오류

:::notes
{timing: 1min}
[요약]
- Q1 정답: rollout. 주입은 Pod 생성 시점에만 일어남
- Q2 정답: aud. 같은 클러스터 issuer, aud만 sts.amazonaws.com 대 pods.eks.amazonaws.com
- Q3 정답: Pod Identity 역할. EKS 웹훅이 새 Pod에 Pod Identity 변수만 넣음. 체인 순서와 혼동하기 쉬운 문제

세 문제입니다. 보기를 클릭하면 바로 채점됩니다. 잠깐 시간을 드리겠습니다.
{cue: pause}
첫 문제는 rollout입니다. 주입은 Pod를 만들 때만 일어납니다. 두 번째는 diff에서 본 audience입니다. 세 번째는 함정 문제입니다. 체인만 보면 IRSA 같지만, 새 Pod에는 EKS 웹훅이 Pod Identity 변수만 넣으니 Pod Identity 역할입니다.
{cue: transition}
운영 쪽 문제 세 개가 더 있습니다.
:::

---
<!-- Slide 13: 퀴즈 2 -->
@type: quiz
@title: 퀴즈 2: 운영과 차단

## 퀴즈 2: 운영과 차단

**Q4: Pod Identity를 쓸 때 노드 역할에 남아 있어야 하는 권한은?**
[ ] 앱의 s3:GetObject
[ ] sts:AssumeRoleWithWebIdentity
[x] eks-auth:AssumeRoleForPodIdentity
[ ] iam:PassRole

**Q5: EKS Pod Identity를 쓸 수 없어 IRSA를 써야 하는 곳은?**
[ ] 관리형 노드 그룹의 Linux EC2 노드
[ ] Karpenter가 띄운 Linux 노드
[ ] EKS Auto Mode 노드
[x] EKS의 Fargate Pod

**Q6: hop limit을 1로 내린 뒤에도 IMDS에 닿는 Pod는?**
[ ] IRSA를 쓰는 Pod
[x] hostNetwork를 쓰는 Pod
[ ] Pod Identity를 쓰는 Pod
[ ] 모든 일반 Pod

:::notes
{timing: 1min}
[요약]
- Q4 정답: eks-auth:AssumeRoleForPodIdentity (AmazonEKSWorkerNodePolicy에 포함), 업무 권한은 Pod Identity 역할
- Q5 정답: Fargate. Pod Identity는 EKS Linux EC2 노드와 Hybrid Nodes(추가 설정)에서만
- Q6 정답: hostNetwork Pod. 노드 네트워크를 그대로 써서 hop limit과 무관

운영 문제입니다.
{cue: pause}
네 번째는 eks-auth 권한입니다. Agent가 EKS Auth를 부르는 창구 권한이고, 앱 권한은 노드 역할에 남기지 않습니다. 다섯 번째는 Fargate로, Pod Identity는 EKS의 Linux EC2 노드와 추가 설정을 한 Hybrid Nodes에서만 됩니다. 여섯 번째는 hostNetwork Pod라서 따로 통제해야 합니다.
{cue: transition}
오늘 내용을 정리하겠습니다.
:::

---
<!-- Slide 14: 정리 -->
@type: content
@title: 정리: 옮기고, 확인하고, 닫는다

## 정리: 옮기고, 확인하고, 닫는다

:::html
<div class="wid-grid-2">
  <div class="wid-card"><h4>코드는 그대로, 연결 하나와 rollout</h4><div class="wid-muted">IRSA는 SA 주석, Pod Identity는 association. 이미 떠 있는 Pod는 재생성해야 바뀝니다.</div></div>
  <div class="wid-card"><h4>기본은 Pod Identity</h4><div class="wid-muted">신뢰 정책 하나, 세션 태그, 5,000개 association. Fargate, Windows, EKS 밖은 IRSA</div></div>
  <div class="wid-card"><h4>확인은 호출자 ARN으로</h4><div class="wid-muted">카나리에서 env 이름과 호출자 ARN을 보고, 전파를 기다린 뒤 정책 문장만 회수</div></div>
  <div class="wid-card"><h4>마지막에 Pod의 IMDS 경로를 닫는다</h4><div class="wid-muted">IMDSv2 필수, hop limit 1. IMDS 자체는 켜 두고 hostNetwork Pod는 따로 통제</div></div>
</div>
<div class="callout callout-info wid-gap-top"><strong class="wid-t-info">더 읽을 거리</strong>: kubernetes-docs의 security/17 문서(비교표, 신뢰 정책, 카나리 명령)와 데모 코드 examples/security/eks-workload-identity</div>
:::

:::notes
{timing: 0.5min}
[요약]
- 코드는 그대로: IRSA는 주석, Pod Identity는 association, 그리고 rollout
- 기본은 Pod Identity, 예외는 IRSA
- 확인은 호출자 ARN, 회수는 전파를 기다린 뒤 정책 문장만
- 마지막에 Pod의 IMDS 경로 차단(hop limit 1). IMDS 자체는 켜 둠(Agent가 사용), hostNetwork는 별도
- harden은 이 시점에 보통 교체 중(약 40%). 리허설 결과로 설명

네 줄로 정리합니다. 앱 코드는 그대로 두고, IRSA는 주석, Pod Identity는 association 하나로 연결한 뒤 Pod를 새로 만듭니다.
새 워크로드는 Pod Identity가 기본이고, Pod Identity가 닿지 않는 곳에 IRSA를 씁니다.
옮긴 뒤에는 호출자 ARN으로 확인하고, 전파를 기다렸다가 정책 문장만 회수합니다.
마지막으로 Pod의 IMDS 경로를 닫습니다. IMDS 자체는 Agent가 쓰니 켜 둡니다. 문서와 데모 코드는 공개 저장소에 있으니 그대로 돌려 보셔도 됩니다.
{cue: demo}
harden 결과 확인: 이 시점에는 노드 교체가 보통 40% 정도라 결과가 아직 없습니다. 5단계 슬라이드의 리허설 결과로 이미 설명했으니 watch로 전환하지 않고 넘어갑니다.
{cue: transition}
질문 받겠습니다.
:::

---
<!-- Slide 15: Thank You -->
@type: thankyou
@toc: toc.html
@message: EKS 워크로드 IAM 이전, 감사합니다

# Thank you.

:::notes
{timing: 0.5min}
[요약]
- 세션 마무리, Q&A
- 시간이 남을 때만 맨 마지막에 watch로 harden 결과 확인(revoke 후 약 15분 필요)
- 발표 뒤: ./demo.sh restore "$RUN_ID"(약 10분) 또는 ./demo.sh down "$RUN_ID"

들어 주셔서 감사합니다. 궁금하신 점 편하게 질문해 주세요. 데모 화면이 필요한 질문이면 watch를 다시 띄워서 보여 드리겠습니다.
{cue: demo}
harden 결과 확인: Q&A가 길어져 revoke 후 15분이 지났다면 맨 마지막에 watch로 전환해 레거시만 no-credentials인지 확인합니다. 시간이 없으면 생략합니다.
발표가 끝나면 다시 리허설할 경우 ./demo.sh restore "$RUN_ID"(harden 뒤 약 10분), 정리할 경우 ./demo.sh down "$RUN_ID"를 실행합니다.
:::
