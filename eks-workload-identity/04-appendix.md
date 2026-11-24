---
remarp: true
block: 04-appendix
---

---
<!-- Slide 1: 부록 구분 -->
@type: section

# 부록: 동작 원리

질문이 나오면 여기서: 자격 증명 경로, SDK 체인, 두 방식의 단계별 흐름

:::html
<div class="wid-applinks"><a class="wid-applink" data-wid-goto="04-appendix:2" href="./04-appendix.html#2">2. IAM이 쓰이는 두 길</a><a class="wid-applink" data-wid-goto="04-appendix:3" href="./04-appendix.html#3">3. 세 갈래 경로</a><a class="wid-applink" data-wid-goto="04-appendix:4" href="./04-appendix.html#4">4. SDK 자격 증명 체인</a><a class="wid-applink" data-wid-goto="04-appendix:5" href="./04-appendix.html#5">5. IRSA 흐름</a><a class="wid-applink" data-wid-goto="04-appendix:6" href="./04-appendix.html#6">6. IRSA 다섯 단계</a><a class="wid-applink" data-wid-goto="04-appendix:7" href="./04-appendix.html#7">7. Pod Identity 흐름</a><a class="wid-applink" data-wid-goto="04-appendix:8" href="./04-appendix.html#8">8. Pod Identity 다섯 단계</a><a class="wid-applink" data-wid-goto="04-appendix:9" href="./04-appendix.html#9">9. Agent와 노드 역할</a><a class="wid-applink" data-wid-goto="04-appendix:10" href="./04-appendix.html#10">10. 노드 종류별 IMDS 설정</a></div>
:::

:::script
// 발표자 창 노트 순서: 대본 먼저, [요약]/[출처]/[약어]는 아래 (assets/presenter-notes.js)
if (!window.__widNotesLoader) {
  window.__widNotesLoader = true;
  ['./assets/presenter-notes.js', './assets/appendix-links.js'].forEach(function (src) {
    var s = document.createElement('script');
    s.src = src;
    document.head.appendChild(s);
  });
}
:::

:::notes
{timing: 0.5min}
[요약]
- 본편에서 뺀 동작 원리 장표. 질문이 나오거나 시간이 남을 때 사용
- 순서: IAM이 쓰이는 두 길, 세 갈래 경로, SDK 체인, IRSA 흐름과 단계, Pod Identity 흐름과 단계, Agent, 노드 종류별 IMDS 설정

여기부터는 부록입니다. 본편에서 결론만 말씀드린 동작 원리를 장표로 남겨 두었습니다.
질문에 맞는 장으로 바로 넘어가겠습니다.
{cue: transition}
먼저 EKS에서 IAM이 쓰이는 두 길입니다.
:::

---
<!-- Slide 2: IAM이 쓰이는 두 길 -->
@type: content
@title: IAM이 쓰이는 길은 둘, 오늘은 Pod 쪽

## IAM이 쓰이는 길은 둘, 오늘은 Pod 쪽

:::html
<div class="wid-grid-2">
  <div class="wid-card">
    <span class="wid-chip">클러스터 API</span>
    <h4 class="wid-gap-top">사람과 노드가 Kubernetes API로</h4>
    <div class="wid-muted">kubectl, kubelet이 클러스터에 들어갈 때</div>
    <div class="wid-stack wid-gap-top">
      <div class="wid-row"><strong>토큰</strong><span class="wid-mono"><span class="rp-detail" data-detail="gettoken" data-tip="STS GetCallerIdentity를 미리 서명한 URL을 base64로 담은 bearer 토큰입니다.">aws eks get-token</span></span></div>
      <div class="wid-row"><strong>검증</strong><span>control plane의 IAM Authenticator가 STS로 호출자 확인</span></div>
      <div class="wid-row"><strong>매핑</strong><span>access entry (기존 aws-auth ConfigMap은 이전 권고)</span></div>
      <div class="wid-row"><strong>권한</strong><span>access policy + Kubernetes RBAC</span></div>
    </div>
  </div>
  <div class="wid-card">
    <span class="wid-chip">오늘 주제</span>
    <h4 class="wid-gap-top">Pod가 AWS API로</h4>
    <div class="wid-muted">앱이 S3 같은 AWS 서비스를 부를 때</div>
    <div class="wid-stack wid-gap-top">
      <div class="wid-row"><span class="wid-chip wid-irsa">IRSA</span><span>OIDC 토큰 → STS AssumeRoleWithWebIdentity</span></div>
      <div class="wid-row"><span class="wid-chip wid-podid">Pod Identity</span><span>Agent → EKS Auth AssumeRoleForPodIdentity</span></div>
      <div class="wid-row"><strong>연결</strong><span>ServiceAccount 주석 또는 association</span></div>
      <div class="wid-row"><strong>access entry</strong><span>관여하지 않음</span></div>
    </div>
  </div>
</div>
<div class="callout callout-info wid-gap-top"><span class="wid-chip wid-node">노드 역할</span> 두 길에 모두 나옵니다. access entry(<span class="wid-mono">EC2_LINUX</span>, Hybrid Nodes는 <span class="wid-mono">HYBRID_LINUX</span>)로 노드가 클러스터에 가입하고, 같은 역할로 Pod Identity Agent가 EKS Auth를 부릅니다. 그래서 이전 마지막에 지우는 것은 앱 권한뿐이고, 노드 역할과 access entry는 그대로 둡니다.</div>
<div class="wid-src">출처: <a href="https://docs.aws.amazon.com/eks/latest/userguide/grant-k8s-access.html">Amazon EKS User Guide, Grant IAM users and roles access to Kubernetes APIs</a>, <a href="https://docs.aws.amazon.com/eks/latest/userguide/creating-access-entries.html">Create access entries</a>, <a href="https://docs.aws.amazon.com/eks/latest/userguide/migrating-access-entries.html">Migrating aws-auth entries to access entries</a>, <a href="https://docs.aws.amazon.com/eks/latest/best-practices/identity-and-access-management.html">EKS Best Practices, Identity and Access Management</a></div>
:::

:::detail gettoken "kubectl이 보내는 토큰"
tip: STS GetCallerIdentity를 미리 서명한 URL을 base64로 담은 bearer 토큰

kubeconfig의 exec 설정이 요청 때 `aws eks get-token`을 불러 토큰을 받습니다. 토큰은 `k8s-aws-v1.` 뒤에 STS `GetCallerIdentity` presigned URL을 base64로 붙인 값입니다. control plane의 AWS IAM Authenticator for Kubernetes가 이 URL로 STS에 호출자를 확인하고, 그 IAM ARN을 access entry(또는 aws-auth ConfigMap)로 Kubernetes 사용자와 그룹에 매핑합니다.

같은 IAM 역할이 양쪽에 매핑되어 있으면 access entry가 우선합니다. kubectl에서 `Unauthorized`가 나오면 Pod 자격 증명이 아니라 이 매핑을 먼저 봅니다.
:::

:::notes
{timing: 1min}
[요약]
- EKS에서 IAM이 쓰이는 길은 둘: 사람과 노드가 Kubernetes API로 들어가는 길, Pod가 AWS API를 부르는 길
- 클러스터 API: aws eks get-token 토큰(STS presigned URL) → IAM Authenticator가 STS로 확인 → access entry 또는 aws-auth로 매핑 → access policy와 RBAC
- Pod 쪽: IRSA와 Pod Identity. access entry와 무관
- 노드 역할은 양쪽에 다 나옴: access entry로 노드 가입, Agent가 같은 역할로 EKS Auth 호출. 그래서 지우는 건 앱 권한뿐

EKS에서 IAM이 쓰이는 길은 두 개입니다.
하나는 사람과 노드가 Kubernetes API로 들어가는 길입니다. kubectl이 aws eks get-token으로 STS 서명 토큰을 만들고, control plane이 STS로 누구인지 확인한 다음 access entry로 Kubernetes 사용자와 그룹에 매핑합니다. 권한은 access policy와 RBAC이 정합니다.
오늘 본편에서 다룬 건 다른 하나, Pod가 S3 같은 AWS API를 부를 때입니다. IRSA와 Pod Identity가 여기 속하고, access entry는 관여하지 않습니다. 그래서 Pod 권한 문제를 access entry에서 찾으면 안 되고, 반대로 kubectl Unauthorized는 Pod 자격 증명이 아니라 매핑을 봐야 합니다.
헷갈리는 지점이 노드 역할입니다. 노드는 이 역할로 access entry를 통해 클러스터에 가입하고, Pod Identity Agent도 같은 역할로 EKS Auth를 부릅니다. 그래서 이전 마지막에 노드 역할 자체를 지우는 게 아니라, 거기 붙어 있던 앱 권한만 지웁니다.
{cue: transition}
이제 Pod 쪽, 자격 증명이 오는 세 경로를 보겠습니다.

[약어]
- RBAC: Role-Based Access Control
- STS: AWS Security Token Service
:::

---
<!-- Slide 3: 세 갈래 경로 (단계별 장면) -->
@type: content
@fit: off
@title: Pod의 자격 증명은 세 곳에서 온다

## Pod의 자격 증명은 세 곳에서 온다

:::html

<div id="wid-paths">
<p>같은 노드의 orders 앱 세 벌이 서로 다른 곳에서 임시 자격 증명을 받고, 결국 같은 방식으로 S3 요청에 서명한다.</p>
<ol>
<li>노드 역할: 주입된 변수가 없는 Pod는 IMDSv2에서 노드 역할을 받는다</li>
<li>IRSA(IAM Roles for Service Accounts): Pod가 projected 토큰으로 리전 STS(Security Token Service) AssumeRoleWithWebIdentity를 호출한다</li>
<li>Pod Identity (1): Pod는 같은 노드의 Pod Identity Agent에만 묻는다</li>
<li>Pod Identity (2): Agent가 EKS Auth AssumeRoleForPodIdentity를 호출해 받아 온다</li>
<li>결과: 세 Pod 모두 받은 임시 자격 증명으로 S3 요청에 서명한다</li>
</ol>
</div>
:::

:::script
import('./common/line-art-scene/flowscene.js').then(function (m) {
  m.mount('#wid-paths', {
    camera: false,
    aria: '같은 노드의 orders 앱 세 벌 중 노드 역할 Pod는 IMDSv2에서, IRSA Pod는 리전 STS에서, Pod Identity Pod는 같은 노드의 Agent와 EKS Auth를 거쳐 임시 자격 증명을 받고, 세 Pod 모두 그것으로 S3 요청에 서명하는 흐름',
    W: 900, H: 590,
    zones: [
      { box: [0, 0, 0, 17.2, 3.6, 0.4], label: '워커 노드 (EC2, 인스턴스 프로파일)', labelAt: [0.2, 0, -0.3],
        icon: './common/aws-icons/groups/EC2-instance-contents_32.svg' },
      { box: [18.4, 0, 0, 13.6, 3.6, 0.4], label: 'AWS 리전 (ap-northeast-2)', labelAt: [18.6, 0, -0.3],
        icon: './common/aws-icons/groups/Region_32.svg' }
    ],
    parts: {
      imds:    { boxes: [[0.5, 1.2, 0.4, 3.0, 1.8, 1.2]] },
      legacy:  { boxes: [[4.3, 1.2, 0.4, 2.4, 1.8, 1.4]] },
      irsa:    { boxes: [[7.3, 1.2, 0.4, 2.4, 1.8, 1.4]] },
      podid:   { boxes: [[10.3, 1.2, 0.4, 2.4, 1.8, 1.4]] },
      agent:   { boxes: [[13.5, 1.2, 0.4, 3.0, 1.8, 1.6]] },
      sts:     { boxes: [[19.6, 1.2, 0.4, 3.0, 1.8, 1.8]] },
      eksauth: { boxes: [[24.0, 1.2, 0.4, 3.0, 1.8, 1.8]] },
      s3:      { boxes: [[28.2, 1.2, 0.4, 3.0, 1.8, 2.2]] }
    },
    icons: [
      { part: 'imds',    at: [2.0, 2.1, 1.6],  src: './common/aws-icons/services/Arch_Amazon-EC2_48.svg', size: 26 },
      { part: 'agent',   at: [15.0, 2.1, 2.0], src: './common/aws-icons/services/Arch_Amazon-Elastic-Kubernetes-Service_48.svg', size: 26 },
      { part: 'sts',     at: [21.1, 2.1, 2.2], src: './common/aws-icons/services/Arch_AWS-Identity-and-Access-Management_48.svg' },
      { part: 'eksauth', at: [25.5, 2.1, 2.2], src: './common/aws-icons/services/Arch_Amazon-Elastic-Kubernetes-Service_48.svg' },
      { part: 's3',      at: [29.7, 2.1, 2.6], src: './common/aws-icons/services/Arch_Amazon-Simple-Storage-Service_48.svg', size: 34 }
    ],
    wires: {
      imds: { pts: [[5.5, 2.1, 1.8], [5.5, 2.1, 2.5], [2.0, 2.1, 2.5], [2.0, 2.1, 1.6]] },
      sts:  { pts: [[8.5, 2.1, 1.8], [8.5, 2.1, 3.3], [21.1, 2.1, 3.3], [21.1, 2.1, 2.2]] },
      pid:  { pts: [[11.5, 2.1, 1.8], [11.5, 2.1, 2.6], [15.0, 2.1, 2.6], [15.0, 2.1, 2.0], [15.0, 2.1, 4.3], [25.5, 2.1, 4.3], [25.5, 2.1, 2.2]] },
      pidA: { pts: [[11.5, 2.1, 1.8], [11.5, 2.1, 2.6], [15.0, 2.1, 2.6], [15.0, 2.1, 2.0]] },
      s3:   { pts: [[5.5, 1.2, 0.7], [5.5, 0.5, 0.45], [8.5, 0.5, 0.45], [8.5, 1.2, 0.7], [8.5, 0.5, 0.45], [11.5, 0.5, 0.45], [11.5, 1.2, 0.7], [11.5, 0.5, 0.45], [29.0, 0.5, 0.45], [29.7, 1.2, 1.0]] }
    },
    tags: [
      { id: 'n-legacy', at: [5.5, 1.2, 1.0],  text: 'orders-legacy', cls: 'fs-sub', show: ['node', 'irsa', 'agent', 'eksauth', 's3'] },
      { id: 'n-irsa',   at: [8.5, 1.2, 1.0],  text: 'orders-irsa',   cls: 'fs-sub', show: ['node', 'irsa', 'agent', 'eksauth', 's3'] },
      { id: 'n-podid',  at: [11.5, 1.2, 1.0], text: 'orders-podid',  cls: 'fs-sub', show: ['node', 'irsa', 'agent', 'eksauth', 's3'] },
      { id: 'ip-imds',  at: [2.0, 1.2, 0.9],  text: '169.254.169.254', cls: 'fs-sub', show: ['node', 'irsa', 'agent', 'eksauth', 's3'] },
      { id: 'ip-agent', at: [15.0, 1.2, 1.0], text: '169.254.170.23',  cls: 'fs-sub', show: ['node', 'irsa', 'agent', 'eksauth', 's3'] },
      { id: 'aud-sts',  at: [14.6, 2.1, 3.55], text: 'token aud: sts.amazonaws.com', show: ['irsa'], overview: false },
      { id: 'aud-pods', at: [20.3, 2.1, 4.55], text: 'token aud: pods.eks.amazonaws.com', show: ['eksauth'], overview: false }
    ],
    callouts: [
      { id: 'imds',    n: 1, anchor: [2.0, 2.1, 1.6],  at: [20, 150],  title: 'IMDSv2', sub: '노드 역할을 준다', charW: 9, subW: 11 },
      { id: 'sts',     n: 2, anchor: [21.1, 2.1, 2.2], at: [610, 165], title: 'AWS STS', sub: 'AssumeRoleWithWebIdentity', charW: 9 },
      { id: 'agent',   n: 3, anchor: [15.0, 2.1, 2.0], at: [380, 95],  title: 'Pod Identity Agent', sub: '노드마다 DaemonSet, hostNetwork', charW: 8.5 },
      { id: 'eksauth', n: 4, anchor: [25.5, 2.1, 2.2], at: [790, 95],  title: 'EKS Auth', sub: 'AssumeRoleForPodIdentity', charW: 9 },
      { id: 's3',      n: 5, anchor: [29.7, 1.2, 0.8], at: [850, 470], title: 'Amazon S3', sub: '받은 자격 증명으로 서명', charW: 9, subW: 11 }
    ],
    code: [
      'PUT 169.254.169.254/latest/api/token',
      'GET .../security-credentials/<역할 이름>',
      'sts:AssumeRoleWithWebIdentity',
      'GET 169.254.170.23/v1/credentials',
      'eks-auth:AssumeRoleForPodIdentity',
      's3:GetObject   (SigV4 서명)'
    ],
    hint: '장면을 누르거나 ↓ 키로 다음 단계, ↑ 키로 이전 단계',
    overview: { label: '전체 그림', title: '같은 코드, 세 갈래 경로',
      say: '한 노드에 같은 orders 앱이 세 벌 있습니다. 노드 안에는 <b>IMDS</b>와 <b>Agent</b>, 오른쪽에는 리전 서비스가 있습니다. 노란 선이 노드 역할, 파란 선이 IRSA, 분홍 선이 Pod Identity입니다.' },
    phases: [
      { key: 'node', d: 3.2, focus: ['imds', 'legacy'], badge: 'imds', lines: [1, 2],
        packet: { wire: 'imds', mode: 'pingpong', colour: 'var(--warning)' },
        label: '1  노드 역할 (IMDS)', title: '주입된 변수가 없으면 IMDS까지 간다',
        say: '<b>orders-legacy</b>에는 AWS 변수가 없어서, SDK 체인의 끝인 <b>IMDSv2</b>가 노드 인스턴스 프로파일의 역할을 줍니다. 이 노드의 Pod는 누구나 IMDS에서 같은 노드 역할을 받을 수 있습니다.' },
      { key: 'irsa', d: 4.2, focus: ['sts', 'irsa'], badge: 'sts', lines: [3],
        packet: { wire: 'sts', mode: 'pingpong', colour: 'var(--info)' },
        label: '2  IRSA (STS)', title: 'Pod가 토큰을 들고 STS로 간다',
        say: 'IRSA(IAM Roles for Service Accounts)에서 <b>orders-irsa</b>는 projected 토큰(aud <b>sts.amazonaws.com</b>)을 들고 리전 <b>STS</b>(Security Token Service)에 AssumeRoleWithWebIdentity를 직접 호출합니다. 노드 역할은 쓰지 않습니다.' },
      { key: 'agent', d: 3.0, focus: ['agent', 'podid'], badge: 'agent', lines: [4],
        packet: { wire: 'pidA', colour: 'var(--pink)' },
        label: '3  Pod Identity (Agent)', title: 'Pod는 같은 노드의 Agent에만 묻는다',
        say: '<b>orders-podid</b>는 링크 로컬 주소 <b>169.254.170.23</b>의 Pod Identity Agent에 자기 토큰을 건넵니다. 자격 증명을 얻으려고 Pod가 AWS API를 직접 부르지는 않습니다.' },
      { key: 'eksauth', d: 4.4, focus: ['eksauth', 'agent', 'podid'], badge: 'eksauth', lines: [5],
        packet: { wire: 'pid', span: [0, 6], mode: 'pingpong', colour: 'var(--pink)' },
        label: '4  Pod Identity (EKS Auth)', title: 'Agent가 EKS Auth에서 받아 온다',
        say: 'Agent가 토큰(aud <b>pods.eks.amazonaws.com</b>)으로 <b>EKS Auth</b>에 AssumeRoleForPodIdentity를 호출하고, 받은 자격 증명을 Pod에 돌려줍니다.' },
      { key: 's3', d: 3.6, focus: ['s3', 'legacy', 'irsa', 'podid'], badge: 's3', lines: [6],
        packet: { wire: 's3' },
        label: '5  결과', title: '세 경로 모두 임시 자격 증명으로 서명',
        say: '어디서 받든 결과는 <b>임시 자격 증명</b>이고, 세 Pod는 같은 코드로 S3 요청에 서명합니다. 다른 것은 <b>어느 역할</b>이냐 하나입니다.' }
    ],
    frame: function (c) {
      var path = { imds: 'var(--warning)', sts: 'var(--info)', pid: 'var(--pink)', pidA: 'var(--pink)' };
      for (var id in c.wires) {
        var lit = c.all || (c.ph.packet && c.ph.packet.wire === id);
        c.wires[id].node.style.stroke = lit && path[id] ? path[id] : '';
      }
    }
  });
});
:::

:::notes
{timing: 2min}
[요약]
- 경로 1: IMDSv2에서 노드 역할 (오늘 옮길 대상)
- 경로 2: IRSA, Pod가 리전 STS AssumeRoleWithWebIdentity를 직접 호출
- 경로 3: Pod Identity, Pod는 같은 노드의 Agent에만 묻고 Agent가 EKS Auth를 호출
- 세 경로 모두 결과는 임시 자격 증명이고, Pod는 그것으로 S3 요청에 서명

한 노드에 같은 orders 앱이 세 벌 떠 있습니다. 데모에서 본 그 세 벌입니다. 색은 본편과 같이 노드 역할은 노란색, IRSA는 파란색, Pod Identity는 분홍색입니다. 한 경로씩 따라가 보겠습니다.
먼저 지금 상태입니다. orders-legacy에는 AWS 변수가 하나도 없어서, SDK가 체인 끝의 IMDS까지 내려가 노드 역할을 받습니다.↓
두 번째가 IRSA, IAM Roles for Service Accounts입니다. Pod가 자기 토큰을 들고 리전 STS에 직접 가서 역할을 맡습니다.↓
세 번째 Pod Identity는 두 단계로 봅니다. Pod는 같은 노드의 Agent에만 말을 겁니다.↓
그리고 Agent가 EKS Auth를 불러 자격 증명을 받아 와서 Pod에 돌려줍니다.↓
마지막으로, 어디서 받았든 결과는 같은 임시 자격 증명이고 세 Pod 모두 같은 코드로 S3에 서명합니다.↓
{cue: transition}
그러면 같은 코드가 어떻게 이 셋 중 하나를 고를까요. SDK의 자격 증명 체인입니다.
:::

---
<!-- Slide 4: 자격 증명 체인 캔버스 -->
@type: content
@title: SDK는 위에서부터 찾고, 처음 것을 쓴다

## SDK는 위에서부터 찾고, 처음 것을 쓴다

:::html
<div class="wid-canvas-box"><canvas id="wid-chain-canvas" role="img" aria-label="SDK 기본 자격 증명 체인. 1 환경 변수의 정적 키, 2 웹 ID 토큰(IRSA), 3 컨테이너 공급자(Pod Identity), 4 EC2 IMDS(노드 역할) 순서로 확인하고 처음 찾은 단계의 자격 증명을 쓴다. 아무것도 주입되지 않은 Pod는 IMDS까지 내려간다. IRSA 주석과 association이 모두 있는 ServiceAccount의 새 Pod에는 EKS 웹훅이 Pod Identity 변수만 넣으므로 3단계에서 멈춘다."></canvas></div>
<div class="wid-canvas-bar">
  <button class="btn btn-primary btn-sm" data-wid-play="wid-chain-canvas">Play</button>
  <button class="btn btn-sm" data-wid-reset="wid-chain-canvas">Reset</button>
  <span class="wid-step" data-wid-step="wid-chain-canvas">0 / 4</span>
  <span class="wid-canvas-cap" data-wid-cap="wid-chain-canvas" aria-live="polite">오른쪽 Pod를 바꿔 가며 SDK가 어느 단계에서 멈추는지 봅니다.</span>
</div>
<div class="wid-src">출처: <a href="https://docs.aws.amazon.com/sdkref/latest/guide/standardized-credentials.html">AWS SDKs and Tools, standardized credential providers</a>. 공유 config 파일 같은 나머지 단계는 생략했습니다.</div>
:::

:::script
  var CANVAS_ID = 'wid-chain-canvas', BASE_W = 960, BASE_H = 360, MAX_STEP = 4, STEP_DUR = 3.2;
  var CAPS = [
    '오른쪽 Pod를 바꿔 가며 SDK가 어느 단계에서 멈추는지 봅니다. 아래 방향키나 Play로 진행합니다.',
    '아무것도 주입되지 않은 Pod: 1~3단계에 해당 변수가 없어 마지막 IMDS까지 내려가 노드 역할을 받습니다.',
    'IRSA Pod: 웹 ID 토큰 변수가 있으니 2단계에서 멈춥니다. 코드는 그대로이고 주입된 변수만 다릅니다.',
    'Pod Identity Pod: 컨테이너 공급자 변수가 있으니 3단계에서 멈추고 IMDS까지 가지 않습니다.',
    '주석과 association이 모두 있는 SA의 새 Pod: EKS 웹훅이 Pod Identity 변수만 넣어 3단계에서 멈춥니다. 결정은 체인 순서가 아니라 주입 단계에서 납니다.'
  ];
  var ROWS = [
    { n: '1', t: '환경 변수의 정적 키', v: 'AWS_ACCESS_KEY_ID', c: 'textMuted' },
    { n: '2', t: '웹 ID 토큰 (IRSA)', v: 'AWS_WEB_IDENTITY_TOKEN_FILE', c: 'blue' },
    { n: '3', t: '컨테이너 공급자 (Pod Identity)', v: 'AWS_CONTAINER_CREDENTIALS_FULL_URI', c: 'pink' },
    { n: '4', t: 'EC2 IMDS (노드 역할)', v: '169.254.169.254', c: 'yellow' }
  ];
  var SC = [null,
    { pod: 'orders-legacy', env: [], hit: 3, res: '노드 역할', role: 'wid-<run>-node', note: '노드의 모든 Pod가 같은 역할', c: 'yellow' },
    { pod: 'orders-irsa', env: ['AWS_ROLE_ARN', 'AWS_WEB_IDENTITY_TOKEN_FILE'], hit: 1, res: 'IRSA 역할', role: 'wid-<run>-irsa', note: 'ServiceAccount 주석에 적힌 역할', c: 'blue' },
    { pod: 'orders-podid', env: ['AWS_CONTAINER_CREDENTIALS_FULL_URI', 'AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE'], hit: 2, res: 'Pod Identity 역할', role: 'wid-<run>-podid', note: 'association에 지정한 역할', c: 'pink' },
    { pod: '주석 + association (새 Pod)', env: ['AWS_CONTAINER_CREDENTIALS_FULL_URI', 'AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE', { t: 'IRSA 변수는 주입되지 않음', warn: true }], hit: 2, res: 'Pod Identity 역할', role: 'wid-<run>-podid', note: '기존 Pod는 재생성 전까지 IRSA', c: 'pink', warn: true }
  ];
  var RX = 40, RW = 440, RH = 56, RY = [56, 128, 200, 272];
  function cy(i) { return RY[i] + RH / 2; }

  function render() {
    var sc = SC[step];
    txt('SDK 기본 자격 증명 체인 (Pod에서 의미 있는 단계만)', RX, 30, { weight: '700', size: 14, color: Colors.textSec });
    var CHECK = 0.62, per = sc ? CHECK / (sc.hit + 1) : 0;
    ROWS.forEach(function (r, i) {
      var col = Colors[r.c], state = 1, tag = '';
      if (sc) {
        var done = prog >= (i + 1) * per, active = prog >= i * per && !done;
        if (i < sc.hit && done) { state = 0; tag = '변수 없음, 다음 단계'; }
        else if (i === sc.hit && done) { state = 2; tag = '여기서 결정'; }
        else if (i > sc.hit) { state = 0; tag = '확인하지 않음'; }
        else if (active) { state = 1; tag = '확인 중'; }
      }
      card(RX, RY[i], RW, RH, r.n + '.  ' + r.t, [{ t: r.v, mono: true }], col, state);
      if (tag) txt(tag, RX + RW - 12, RY[i] + 20, { size: 12, weight: '700', align: 'right', color: state === 2 ? col : Colors.textMuted });
    });
    // probe
    if (sc && prog < CHECK) {
      var k = Math.floor(prog / per), local = (prog - k * per) / per;
      var y = k === 0 ? cy(0) : lerp(cy(k - 1), cy(k), clamp(local / 0.35, 0, 1));
      drawCircle(ctx, RX + RW + 22, y, 8, Colors[sc.c], null);
    }
    // Pod card
    var px = 600, pw = 320;
    var podLines = !sc ? [{ t: 'Pod를 고르면 SDK가 위에서부터' }, { t: '차례로 확인합니다.' }]
      : (sc.env.length ? [{ t: '주입된 환경 변수', weight: '600' }].concat(sc.env.map(function (e) { return typeof e === 'string' ? { t: e, mono: true } : { t: e.t, color: Colors.red, weight: '700' }; })) : [{ t: '주입된 환경 변수', weight: '600' }, { t: '(없음)', mono: true }]);
    card(px, 56, pw, 140, sc ? 'Pod: ' + sc.pod : 'Pod', podLines, sc ? Colors[sc.c] : Colors.textMuted, 1);
    // result
    if (sc) {
      var rt = seg(CHECK, 0.85);
      var p = [{ x: RX + RW, y: cy(sc.hit) }, { x: 545, y: cy(sc.hit) }, { x: 545, y: 282 }, { x: px, y: 282 }];
      wire(p, Colors[sc.c], rt, false);
      if (prog >= 0.85) {
        card(px, 236, pw, 96, '결과: ' + sc.res, [{ t: sc.role, mono: true }, { t: sc.note, color: sc.warn ? Colors.red : Colors.textSec, weight: sc.warn ? '700' : '400' }], Colors[sc.c], 2);
      }
    } else {
      card(px, 236, pw, 96, '결과: 어떤 역할?', [{ t: '처음 성공한 단계의 자격 증명을 씁니다.' }], Colors.textMuted, 0);
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
- 기본 체인 순서(Pod 관점): 환경 변수 정적 키, 웹 ID 토큰(IRSA), 컨테이너 공급자(Pod Identity), IMDS
- 처음 찾은 단계에서 멈춤. 그래서 EKS가 변수만 주입하면 코드 변경 없이 출처가 바뀜
- 아무것도 없으면 IMDS까지 내려가 노드 역할
- 주석과 association이 모두 있으면 새 Pod에는 EKS 웹훅이 Pod Identity 변수만 넣음(association이 이김). 체인 순서와 혼동 금지
- association 전에 만든 Pod는 IRSA 변수를 그대로 갖고 재생성 전까지 IRSA

아래 방향키를 한 번씩 누르면서 Pod를 바꿔 보겠습니다. 왼쪽 네 칸이 SDK가 확인하는 순서입니다.
(아래 방향키)
첫 번째는 아무것도 주입되지 않은 레거시 Pod입니다. 1, 2, 3단계에 변수가 없으니 맨 아래 IMDS까지 내려가서 노드 역할을 받습니다.
(아래 방향키)
IRSA Pod에는 웹 ID 토큰 변수가 있어서 2단계에서 멈춥니다. 앱 코드는 똑같고, 바뀐 건 EKS가 넣어 준 환경 변수뿐입니다.
(아래 방향키)
Pod Identity Pod는 3단계, 컨테이너 공급자에서 멈춥니다.
(아래 방향키)
마지막은 헷갈리기 쉬운 경우입니다. 체인만 보면 IRSA가 앞이니 둘 다 걸면 IRSA가 이길 것 같지만, 실제로는 그 전 단계에서 갈립니다. 주석과 association이 모두 있는 ServiceAccount로 새 Pod를 만들면 EKS 웹훅이 Pod Identity 변수만 넣고 IRSA 변수는 넣지 않습니다. 그래서 새 Pod는 3단계에서 멈춥니다.
다만 association을 만들기 전에 떠 있던 Pod는 IRSA 변수를 그대로 갖고 있어서, 다시 만들기 전까지는 IRSA를 씁니다.
{cue: transition}
이 체인 덕분에 이전은 결국 "무엇을 주입하느냐"의 문제가 되고, 그 주입은 1부에서 본 웹훅이 합니다.
:::

---
<!-- Slide 5: IRSA 흐름 -->
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
    <div class="wid-card wid-irsa wid-edge"><strong class="wid-t-path">신뢰 준비</strong><div class="wid-muted">클러스터 issuer를 <span class="rp-detail" data-detail="oidc">IAM OIDC(OpenID Connect) provider</span>로 한 번 등록</div></div>
    <div class="wid-card wid-irsa wid-edge"><strong class="wid-t-path">주입</strong><div class="wid-muted">SA 주석을 본 EKS mutating webhook(amazon-eks-pod-identity-webhook)이 env와 토큰 볼륨 추가</div></div>
    <div class="wid-card wid-irsa wid-edge"><strong class="wid-t-path">교환</strong><div class="wid-muted">Pod가 리전 STS(Security Token Service)와 직접 통신</div></div>
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
핵심은 세 줄입니다. IAM이 클러스터를 믿도록 OIDC provider를 등록하고, Pod 생성 때 EKS mutating webhook이 토큰을 넣고, Pod가 직접 STS에 가서 토큰을 자격 증명으로 바꿉니다.
{cue: transition}
캔버스에서 한 단계씩 멈춰 보겠습니다.

[약어]
- OIDC: OpenID Connect, 토큰 발급자와 서명 검증 규약
- STS: AWS Security Token Service
:::

---
<!-- Slide 6: IRSA 단계별 캔버스 -->
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
<!-- Slide 7: Pod Identity 흐름 -->
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
    <div class="wid-card wid-podid wid-edge"><strong class="wid-t-path">연결</strong><div class="wid-muted">EKS API의 <span class="rp-detail" data-detail="assoc">association</span>, 주석 없음</div></div>
    <div class="wid-card wid-podid wid-edge"><strong class="wid-t-path">조회</strong><div class="wid-muted">SDK는 같은 노드의 Agent만 호출</div></div>
    <div class="wid-card wid-podid wid-edge"><strong class="wid-t-path">위임</strong><div class="wid-muted">EKS Auth가 역할을 맡고 세션 태그 부착</div></div>
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
연결 정보는 ServiceAccount 주석이 아니라 EKS API의 association에 있습니다.
Pod 안의 SDK는 같은 노드의 Agent에만 요청합니다.
Agent가 EKS Auth를 부르고, EKS가 세션 태그를 붙여 역할을 맡은 자격 증명을 돌려줍니다.
{cue: transition}
역시 캔버스로 한 단계씩 보겠습니다.
:::

---
<!-- Slide 8: Pod Identity 단계별 캔버스 -->
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
<!-- Slide 9: Agent와 노드 역할 -->
@type: content
@title: Agent는 노드마다, 권한은 노드 역할에

## Agent는 노드마다, 권한은 노드 역할에

:::html
<div class="wid-grid-2">
  <div class="wid-card">
    <h4>eks-pod-identity-agent 애드온</h4>
    <div class="wid-muted">클러스터마다 한 번 설치하는 hostNetwork DaemonSet</div>
    <div class="wid-mono wid-gap-top">169.254.170.23, [fd00:ec2::23]</div>
    <div class="wid-mono">포트 80, 2703</div>
    <div class="wid-cap wid-gap-top">EKS Auto Mode에는 같은 기능이 내장되어 있습니다.</div>
  </div>
  <div class="wid-card wid-node wid-edge">
    <h4>노드 역할에 남는 권한</h4>
    <div class="wid-mono">eks-auth:AssumeRoleForPodIdentity</div>
    <div class="wid-muted">AmazonEKSWorkerNodePolicy에 포함. Agent가 EKS Auth를 부르는 데만 씁니다.</div>
    <div class="wid-muted">Agent는 hostNetwork에서 IMDS로 이 역할의 자격 증명을 받습니다.</div>
    <div class="wid-cap wid-gap-top">앱의 업무 권한은 Pod Identity 역할에 둡니다.</div>
  </div>
</div>
<div class="callout callout-info wid-gap-top"><strong class="wid-t-info">프록시 환경</strong>: <code>169.254.170.23</code>과 <code>[fd00:ec2::23]</code>을 <code>NO_PROXY</code>에 넣어야 SDK 요청이 Agent에 닿습니다.</div>
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

Agent는 애드온 하나입니다. 노드 네트워크에서 링크 로컬 주소로 듣는 DaemonSet이고, Auto Mode라면 따로 설치할 것이 없습니다.
노드 역할에는 Agent가 EKS Auth를 부를 권한이 있어야 합니다. 이미 AmazonEKSWorkerNodePolicy에 들어 있으니 보통은 따로 붙일 게 없습니다. Agent는 이 자격 증명을 hostNetwork에서 IMDS로 받는다는 점도 기억해 두세요. IMDS 자체를 끄지 말라고 하는 이유이고, 다음 장에서 다시 나옵니다.
실무에서 자주 막히는 곳은 프록시입니다. HTTP 프록시를 쓰는 앱이라면 두 Agent 주소를 NO_PROXY에 넣어야 합니다.
{cue: transition}
마지막으로 노드 종류별 IMDS 설정입니다.
:::

---
<!-- Slide 10: IMDS 차단 -->
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

관리형 노드 그룹은 launch template 새 버전에 HttpTokens required와 hop limit 1을 넣고 롤링 교체합니다. 노드가 바뀌어야 적용되니 시간이 걸립니다. 리허설에서는 노드 한 대 교체에 878초, 15분 가까이 걸렸습니다.
Karpenter는 EC2NodeClass의 metadataOptions에서 정하는데, 기본값이 이미 httpTokens required, hop limit 1입니다. 2로 바꿔 둔 NodeClass가 있는지만 확인해서 되돌리면 됩니다.
Auto Mode는 이미 IMDSv2와 hop limit 1이 기본입니다.
예외가 하나 있습니다. hostNetwork Pod는 노드 네트워크를 그대로 쓰니 hop limit을 1로 내려도 IMDS에 닿습니다. 이런 Pod는 별도로 관리해야 합니다.
그리고 "닫는다"는 말을 IMDS를 끈다는 뜻으로 받아들이시면 안 됩니다. Pod Identity Agent도 hostNetwork에서 IMDS로 노드 역할을 받아서 EKS Auth를 부릅니다. hop limit 1에서 Agent가 살아 있는 것도 hostNetwork이기 때문이고, HttpEndpoint를 disabled로 하면 Pod Identity 전체가 멈춥니다.
{cue: transition}
부록은 여기까지입니다. 질문으로 돌아가겠습니다.
:::
