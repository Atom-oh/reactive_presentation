---
remarp: true
block: 03-operations
---

---
<!-- Slide 1: 4부 구분 (Section) -->
@type: section

# 4부: Auto Mode 심화와 운영

켜기, 노드 설정, 용량, 진단, 비용, 마이그레이션, 그리고 무엇을 고를까

:::notes
{timing: 0.5min}
[요약]
- 4부의 질문: Auto Mode를 켜고, 노드와 용량을 설정하고, 문제를 진단하고, 비용을 나누고, 기존 클러스터를 옮기려면 무엇을 알아야 하나
- 순서: 켜기와 built-in 풀, NodeClass와 보안 기본값, Spot과 예약 용량, GPU와 EFA, ARC zonal shift, 업그레이드, 진단과 관측, 비용, 마이그레이션, 선택 체크리스트
- 체크리스트가 끝나면 바로 데모 영상으로 넘어갑니다.

4부는 Auto Mode 심화와 운영입니다. 3부의 동작 원리를 실제로 운영할 때 필요한 내용을 순서대로 보겠습니다. Auto Mode를 켜는 방법과 built-in 풀, NodeClass와 바꿀 수 없는 보안 기본값, Spot과 예약 용량, GPU와 EFA, AZ 장애 대응, 업그레이드, SSH 없이 진단하는 방법, 비용, 마이그레이션, 그리고 마지막으로 무엇을 고를지입니다.
{cue: transition}
Auto Mode를 켜는 방법부터 보겠습니다.
:::


---
<!-- Slide 2: Auto Mode 켜기 -->
@type: content
@title: Auto Mode 켜기: IAM과 세 스위치

## Auto Mode 켜기: IAM과 세 스위치

:::html
<style>
.ak3-on { display: grid; grid-template-columns: 1fr 1.15fr; gap: var(--space-4); align-items: start; }
.ak3-iam { width: 100%; font-size: var(--fs-caption); word-break: keep-all; overflow-wrap: anywhere; }
.ak3-iam td:first-child { white-space: nowrap; }
.data-table th { text-transform: none; letter-spacing: normal; font-size: var(--fs-card); }
.ak3-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak3-on">
  <div class="ak3-stack">
    <table class="data-table ak3-iam">
      <thead><tr><th>역할</th><th>필요한 것</th></tr></thead>
      <tbody>
        <tr><td>클러스터 역할</td><td>신뢰: <code>sts:AssumeRole</code> + <code>sts:TagSession</code><br>정책 (<code>AmazonEKS</code> 접두사): <code>ClusterPolicy</code>, <code>ComputePolicy</code>, <code>BlockStoragePolicyV2</code>, <code>LoadBalancingPolicy</code>, <code>NetworkingPolicy</code></td></tr>
        <tr><td>노드 역할</td><td><code>AmazonEKSWorkerNodeMinimalPolicy</code>, <code>AmazonEC2ContainerRegistryPullOnly</code></td></tr>
        <tr><td>워크로드</td><td>Pod Identity로 따로 부여. OIDC provider 없이 활성화 가능</td></tr>
      </tbody>
    </table>
    <div class="callout callout-warning fragment fade-up" data-fragment-index="2"><strong class="text-warning">되돌릴 수 없는 것</strong><div class="on-surface-muted"><code>CONFIG_MAP</code>에서 <code>API_AND_CONFIG_MAP</code> 전환은 단방향. 기존 클러스터의 클러스터 역할 ARN은 교체 불가</div></div>
  </div>
  <div class="ak3-stack">
    <pre class="code-block fragment fade-left" data-fragment-index="1"><span class="comment"># 기존 클러스터: 세 기능을 한 요청에서 함께</span>
aws eks update-cluster-config --name $CLUSTER \
  --compute-config '{"enabled":true,
     "nodePools":["general-purpose","system"],
     "nodeRoleArn":"'$NODE_ROLE_ARN'"}' \
  --kubernetes-network-config \
     '{"elasticLoadBalancing":{"enabled":true}}' \
  --storage-config '{"blockStorage":{"enabled":true}}'
<span class="comment"># eksctl: 새 클러스터 create cluster --enable-auto-mode</span>
<span class="comment">#         기존 클러스터 update auto-mode-config -f cluster.yaml</span>
kubectl wait nodepool/general-purpose nodepool/system \
  --for=condition=Ready --timeout=300s</pre>
    <div class="callout callout-info fragment fade-left" data-fragment-index="3"><strong class="text-info">켠 직후 노드는 0대일 수 있음</strong><div class="on-surface-muted">Pending Pod가 생겨야 노드가 뜹니다. default NodeClass는 클러스터 subnet을 물려받으니 private subnet으로 클러스터를 만듭니다.</div></div>
  </div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- 클러스터 역할: sts:AssumeRole + sts:TagSession 신뢰, ClusterPolicy, ComputePolicy, BlockStoragePolicyV2, LoadBalancingPolicy, NetworkingPolicy
- 노드 역할: WorkerNodeMinimalPolicy, ContainerRegistryPullOnly 두 개만. 앱 권한은 Pod Identity, OIDC provider 불필요
- compute, elasticLoadBalancing, blockStorage 세 스위치는 한 요청에서 함께 켜고 함께 끔
- eksctl: 새 클러스터는 create cluster --enable-auto-mode, 기존 클러스터는 update auto-mode-config. 인증 모드 CONFIG_MAP에서 API_AND_CONFIG_MAP은 단방향, 클러스터 역할 ARN 교체 불가
- 켠 직후 노드 0대 가능. default NodeClass는 클러스터 subnet 상속

4부는 Auto Mode를 실제로 운영할 때 필요한 내용부터 시작합니다. 먼저 켜는 방법입니다. IAM 역할이 두 개 필요합니다. 클러스터 역할은 eks.amazonaws.com이 AssumeRole과 TagSession을 할 수 있어야 하고, 기존 ClusterPolicy에 Compute, BlockStorage V2, LoadBalancing, Networking 정책 네 개가 더 붙습니다. Auto Mode가 EC2, EBS, ELB를 대신 만들기 때문입니다.
노드 역할은 오히려 줄어듭니다. WorkerNodeMinimalPolicy와 ECR PullOnly 두 개뿐이고, 애플리케이션 권한은 Pod Identity로 따로 줍니다. Pod Identity agent가 내장되어 있어 Auto Mode를 켜기 위해 OIDC provider를 만들 필요는 없습니다. IRSA를 쓰는 앱이 있다면 그건 별도입니다.
{cue: demo}
오른쪽 명령을 보시면 compute, load balancing, block storage 세 설정이 한 요청에 들어 있습니다. 이 셋은 함께 켜고 함께 꺼야 합니다. eksctl이라면 새 클러스터는 create cluster --enable-auto-mode, 기존 클러스터는 ClusterConfig에 autoModeConfig.enabled: true를 넣고 update auto-mode-config를 씁니다.
{cue: pause}
노란 박스 두 가지는 되돌릴 수 없습니다. 인증 모드를 CONFIG_MAP에서 API_AND_CONFIG_MAP으로 바꾸는 것은 단방향이고, 기존 클러스터의 클러스터 역할 ARN은 바꿀 수 없으니 기존 역할에 정책을 더하는 방식으로 갑니다.
켠 뒤 kubectl wait로 두 NodePool이 Ready인지 봅니다. 노드가 0대여도 정상입니다. Pending Pod가 생겨야 노드가 뜹니다. 그리고 default NodeClass는 클러스터를 만들 때 쓴 subnet을 그대로 물려받으니, 클러스터 subnet은 private으로 두셔야 합니다.

[출처]
- https://docs.aws.amazon.com/eks/latest/userguide/automode-get-started-cli.html, auto-cluster-iam-role.html, auto-create-node-role.html
- https://docs.aws.amazon.com/eks/latest/userguide/auto-enable-existing.html, automode-get-started-eksctl.html, https://docs.aws.amazon.com/eks/latest/eksctl/auto-mode.html
- https://docs.atomai.click/kubernetes-docs/ko/eks-auto-mode/01-getting-started
{cue: transition}
켜면 NodePool 두 개가 생깁니다. 이 두 풀이 정확히 무엇인지 보겠습니다.
:::

---
<!-- Slide 3: Built-in NodePool -->
@type: content
@title: Built-in 풀과 default NodeClass

## Built-in 풀과 default NodeClass

:::html
<style>
.ak3-bi { width: 100%; font-size: var(--fs-card); word-break: keep-all; overflow-wrap: anywhere; margin-bottom: var(--space-3); }
.data-table th { text-transform: none; letter-spacing: normal; font-size: var(--fs-card); }
.ak3-grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); }
.ak3-mt { margin-top: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<table class="data-table ak3-bi">
  <thead><tr><th>NodePool</th><th>아키텍처</th><th>용량, 인스턴스</th><th>누가 올라가나</th></tr></thead>
  <tbody>
    <tr><td><code>general-purpose</code></td><td><code>amd64</code></td><td>On-Demand, C/M/R, 5세대 이상</td><td>일반 워크로드</td></tr>
    <tr><td><code>system</code></td><td><code>amd64</code>, <code>arm64</code></td><td>On-Demand, C/M/R, 5세대 이상</td><td><code>CriticalAddonsOnly</code> taint를 tolerate하는 Pod</td></tr>
  </tbody>
</table>
<div class="ak3-grid3">
  <div class="card fragment fade-up" data-fragment-index="1"><strong class="text-accent">수정하지 말고 추가</strong><div class="on-surface-muted">built-in 풀은 AWS 관리 객체입니다. Spot, Graviton 범용, GPU는 커스텀 NodePool로 만듭니다. 1.37에서 built-in 풀은 <code>Balanced</code>입니다.</div></div>
  <div class="card fragment fade-up" data-fragment-index="2"><strong class="text-accent">default NodeClass 조건</strong><div class="on-surface-muted">built-in 풀이 하나 이상 켜져 있어야 생깁니다. 둘 다 끄면 NodeClass를 직접 만들고 참조를 바꿉니다.</div></div>
  <div class="card fragment fade-up" data-fragment-index="3"><strong class="text-danger">목록에서 빼면 노드 종료</strong><div class="on-surface-muted"><code>computeConfig.nodePools</code>에서 이름을 지우면 그 풀의 노드가 drain, 종료됩니다. 새 Pod만 막는 설정이 아닙니다.</div></div>
</div>
<div class="callout callout-info ak3-mt fragment fade-up" data-fragment-index="4"><strong class="text-info">추측 말고 조회</strong>: <code>kubectl get nodepool general-purpose system -o yaml</code>, <code>kubectl get nodeclass default -o yaml</code>로 실제 disruption과 taint 값을 확인합니다.</div>
:::

:::notes
{timing: 2min}
[요약]
- general-purpose: amd64, On-Demand, C/M/R 5세대 이상. system: amd64와 arm64, CriticalAddonsOnly toleration Pod 전용
- 둘 다 Spot 없음. Spot, 다른 아키텍처, GPU는 커스텀 NodePool. 1.37 built-in 풀은 Balanced
- default NodeClass는 built-in 풀이 하나 이상 켜져 있을 때만 존재
- computeConfig.nodePools에서 이름을 빼면 그 풀의 노드가 drain, 종료
- 실제 값은 kubectl get으로 조회

켜면 생기는 두 풀입니다. general-purpose는 amd64만, On-Demand, C, M, R 계열 5세대 이상입니다. system 풀은 같은 조건에 arm64가 추가되고, CriticalAddonsOnly taint가 있어 이것을 tolerate하는 Pod만 올라갑니다. 두 풀 모두 Spot이 없습니다. 3부에서 capacity-type을 비우면 Spot이 먼저라고 말씀드렸는데, built-in 풀은 On-Demand로 명시되어 있어서 해당되지 않습니다.
{cue: pause}
첫째 카드, built-in 풀은 AWS가 관리하는 객체라 고치지 말고 커스텀 풀을 추가합니다. 1.37부터 이 두 풀의 consolidation 정책은 Balanced입니다.
둘째 카드, default NodeClass는 built-in 풀이 하나라도 켜져 있어야 생깁니다. 마이그레이션처럼 built-in 풀 없이 켜면 NodeClass를 직접 만들어야 합니다.
셋째 카드가 가장 조심할 부분입니다. computeConfig.nodePools 목록에서 system을 빼면, 그 풀의 노드가 drain되고 종료됩니다. 새 Pod만 안 받는 스위치로 오해하시면 안 됩니다.
{cue: question}
그럼 실제 값은 어떻게 볼까요. 블로그나 예제 YAML을 믿지 말고 아래 두 명령으로 클러스터에 있는 객체를 직접 보시는 것이 가장 정확합니다.

[출처]
- https://docs.aws.amazon.com/eks/latest/userguide/set-builtin-node-pools.html
- https://docs.aws.amazon.com/eks/latest/userguide/create-node-class.html (default NodeClass)
- https://docs.atomai.click/kubernetes-docs/ko/eks-auto-mode/02-nodepool-configuration
{cue: transition}
커스텀 풀을 만들면 NodeClass도 직접 쓰게 됩니다. 어떤 필드가 있는지 보겠습니다.
:::

---
<!-- Slide 4: NodeClass 필드 지도 -->
@type: content
@title: 커스텀 NodeClass: 필드 지도

## 커스텀 NodeClass: 필드 지도

:::html
<style>
.ak3-nc { display: grid; grid-template-columns: 1fr 1.1fr; gap: var(--space-4); align-items: start; margin-top: var(--space-3); }
.ak3-nct { width: 100%; font-size: var(--fs-card); word-break: keep-all; overflow-wrap: anywhere; }
.data-table th { text-transform: none; letter-spacing: normal; font-size: var(--fs-card); }
.ak3-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.ak3-mt { margin-top: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">기본 골격</button>
  <button class="tab-btn">보안과 Pod 네트워크</button>
  <button class="tab-btn">쓸 수 없는 필드</button>
</div>
<div class="tc">
  <div class="ak3-nc">
<pre class="code-block"><span class="key">apiVersion</span>: eks.amazonaws.com/v1
<span class="key">kind</span>: NodeClass
<span class="key">spec</span>:
  <span class="key">role</span>: AmazonEKSAutoNodeRole  <span class="comment"># 또는 instanceProfile</span>
  <span class="key">subnetSelectorTerms</span>:
  - <span class="key">tags</span>: {<span class="key">kubernetes.io/role/internal-elb</span>: <span class="string">"1"</span>}
  <span class="key">securityGroupSelectorTerms</span>:
  - <span class="key">tags</span>: {<span class="key">Type</span>: worker-node}
  <span class="key">ephemeralStorage</span>:
    <span class="key">size</span>: 100Gi
    <span class="key">iops</span>: 3000
    <span class="key">throughput</span>: 125
  <span class="key">advancedNetworking</span>:
    <span class="key">associatePublicIPAddress</span>: <span class="value">false</span>
  <span class="key">advancedCompute</span>:
    <span class="key">kernel</span>:
      <span class="key">sysctl</span>: {<span class="key">vm.max_map_count</span>: <span class="value">262144</span>}
  <span class="key">tags</span>: {<span class="key">Environment</span>: production}</pre>
    <div class="ak3-stack">
      <div class="callout callout-info fragment fade-left" data-fragment-index="1"><strong class="text-info"><code>role</code>과 <code>instanceProfile</code>은 하나만</strong><div class="on-surface-muted"><code>AmazonEKSComputePolicy</code>가 <code>eks*</code> 이름의 instance profile에만 권한을 주므로 이름을 <code>eks</code>로 시작합니다. 새 역할에는 access entry가 필요합니다.</div></div>
      <div class="callout callout-warning fragment fade-left" data-fragment-index="2"><strong class="text-warning"><code>tags</code>는 클러스터 역할 권한 필요</strong><div class="on-surface-muted">커스텀 태그 키로 리소스를 만들 권한이 없으면 launch가 실패합니다. 데모에서 <code>CreateLaunchTemplate</code> 권한 오류로 확인했습니다.</div></div>
      <div class="callout callout-info fragment fade-left" data-fragment-index="3"><strong class="text-info">sysctl 변경은 Drift</strong><div class="on-surface-muted">부팅 시 적용되므로 기존 노드는 교체됩니다. 실행 중인 노드에 바로 적용되지 않습니다.</div></div>
    </div>
  </div>
</div>
<div class="tc" hidden>
  <table class="data-table ak3-nct ak3-mt">
    <thead><tr><th>필드</th><th>하는 일</th><th>주의</th></tr></thead>
    <tbody>
      <tr><td><code>ephemeralStorage.kmsKeyID</code></td><td>노드 root, data EBS를 고객 관리 키로 암호화</td><td>같은 리전 키. NVMe instance store와 앱 PVC에는 적용 안 됨</td></tr>
      <tr><td><code>certificateBundles[].data</code></td><td>사설 CA를 노드 신뢰 저장소에 추가 (base64)</td><td>앱 컨테이너의 trust store는 바뀌지 않음</td></tr>
      <tr><td><code>podSubnetSelectorTerms</code></td><td>Pod IP를 노드와 다른 subnet에서 할당</td><td rowspan="2"><code>podSecurityGroupSelectorTerms</code>와 반드시 함께. namespace 단위가 아니라 NodeClass 단위</td></tr>
      <tr><td><code>podSecurityGroupSelectorTerms</code></td><td>Pod 네트워크에 붙일 security group</td></tr>
      <tr><td><code>advancedNetworking.associatePublicIPAddress</code></td><td><code>false</code>면 노드에 공인 IP 없음</td><td>outbound 경로(NAT, endpoint)는 따로 필요</td></tr>
    </tbody>
  </table>
</div>
<div class="tc" hidden>
  <div class="card-grid ak3-mt">
    <div class="callout callout-danger"><strong class="text-danger">EC2NodeClass에서 옮기면 안 되는 필드</strong><div class="on-surface-muted"><code>amiFamily</code>, <code>amiSelectorTerms</code>, <code>blockDeviceMappings</code>, <code>userData</code>, <code>metadataOptions</code>. OS는 AWS가 고르는 Bottlerocket 변형입니다.</div></div>
    <div class="callout callout-info"><strong class="text-info">대체 경로</strong><div class="on-surface-muted">디스크는 <code>ephemeralStorage</code>, 부팅 sysctl은 <code>advancedCompute.kernel.sysctl</code>, IMDS는 고정값(다음 장)</div></div>
  </div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- 기본 골격: role 또는 instanceProfile(둘 중 하나만, ComputePolicy 권한 범위 때문에 eks로 시작하는 이름), subnet과 SG selector, ephemeralStorage(size, iops, throughput), advancedNetworking, advancedCompute.kernel.sysctl, tags
- tags는 클러스터 역할에 태깅 권한이 있어야 함. 데모에서 커스텀 태그로 launch 실패를 겪음
- 보안: kmsKeyID는 노드 EBS만, certificateBundles는 노드 신뢰만, Pod subnet과 Pod SG selector는 함께, NodeClass 단위
- 쓸 수 없는 필드: amiFamily, amiSelectorTerms, blockDeviceMappings, userData, metadataOptions

커스텀 NodeClass를 쓰게 되면 어떤 필드가 있는지 알아야 합니다. 첫 번째 탭이 기본 골격입니다. 노드 IAM은 role이나 instanceProfile 둘 중 하나만 씁니다. instanceProfile을 쓴다면 이름을 eks로 시작하세요. 클러스터 역할의 AmazonEKSComputePolicy가 eks로 시작하는 instance profile에만 권한을 주기 때문입니다. 새 역할이면 access entry도 만들어야 합니다.
subnet과 security group은 태그 selector로 고르고, 디스크는 blockDeviceMappings 대신 ephemeralStorage로 크기, IOPS, throughput을 정합니다. 커널 파라미터는 advancedCompute.kernel.sysctl로 넣는데, 부팅 시 적용되므로 바꾸면 Drift로 노드가 교체됩니다.
{cue: pause}
노란 박스는 저희가 데모를 준비하며 실제로 겪은 일입니다. NodeClass에 커스텀 tags를 넣었더니 클러스터 역할에 해당 태그로 리소스를 만들 권한이 없어 launch template 생성이 실패했습니다. 태그를 쓰려면 클러스터 역할 정책을 먼저 확인하세요.
{cue: demo}
두 번째 탭은 보안과 네트워크 필드입니다. kmsKeyID는 노드의 root와 data EBS만 암호화합니다. NVMe instance store나 애플리케이션 PVC는 StorageClass에서 따로 정합니다. certificateBundles는 사설 CA를 노드가 믿게 할 뿐, 컨테이너 안의 trust store는 그대로입니다. Pod를 다른 subnet에 두는 podSubnetSelectorTerms는 podSecurityGroupSelectorTerms와 꼭 같이 써야 하고, namespace가 아니라 NodeClass 단위로 나뉩니다.
세 번째 탭은 EC2NodeClass에서 그대로 복사하면 안 되는 필드입니다. AMI, 블록 디바이스, userData, metadataOptions는 Auto Mode NodeClass에 없습니다.

[출처]
- https://docs.aws.amazon.com/eks/latest/userguide/create-node-class.html
- https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonEKSComputePolicy.html (instance-profile/eks* 범위)
- https://aws.amazon.com/blogs/containers/new-amazon-eks-auto-mode-features-for-enhanced-security-network-control-and-performance/
- https://docs.atomai.click/kubernetes-docs/ko/eks-auto-mode/02-nodepool-configuration
- 데모 기록: 데모 저장소 RECORDINGS.md (CreateLaunchTemplateAuthCheckFailed)
{cue: transition}
반대로, NodeClass로도 바꿀 수 없는 보안 기본값이 있습니다.
:::

---
<!-- Slide 5: 바꿀 수 없는 보안 기본값 -->
@type: content
@title: 바꿀 수 없는 보안 기본값

## 바꿀 수 없는 보안 기본값

:::html
<style>
.ak3-sec { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-3); }
.ak3-sec .card { word-break: keep-all; }
.ak3-take { margin-top: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak3-sec">
  <div class="card fragment fade-up" data-fragment-index="1"><strong class="text-accent">IMDSv2, hop limit 1 고정</strong><div class="on-surface-muted">일반 Pod는 노드 메타데이터에 닿지 못합니다. <code>hostNetwork</code> Pod는 예외이니 앱 권한은 Pod Identity로 주고 리전 같은 값은 명시합니다.</div></div>
  <div class="card fragment fade-up" data-fragment-index="2"><strong class="text-accent">SSH, SSM 접속 없음</strong><div class="on-surface-muted">관리형 Bottlerocket 변형, 읽기 전용 root 파일 시스템, SELinux enforcing. 노드에 들어가 고치는 운영은 불가</div></div>
  <div class="card fragment fade-up" data-fragment-index="3"><strong class="text-accent">노드 역할은 최소 권한</strong><div class="on-surface-muted"><code>WorkerNodeMinimalPolicy</code>와 <code>ContainerRegistryPullOnly</code>. 앱 권한을 노드 역할에 넣지 않습니다.</div></div>
  <div class="card fragment fade-up" data-fragment-index="4"><strong class="text-accent">최대 21일, 주간 AMI</strong><div class="on-surface-muted">패치는 새 AMI와 Drift로 들어옵니다. 오래된 노드가 남지 않는 대신 교체를 견디는 앱이 전제입니다.</div></div>
</div>
<div class="callout callout-warning ak3-take fragment fade-up" data-fragment-index="5"><strong class="text-warning">taint와 label은 보안 경계가 아님</strong>: 배치를 나누는 도구입니다. 테넌트 격리가 필요하면 클러스터, 계정, 네트워크 정책 수준에서 나눕니다.</div>
:::

:::notes
{timing: 2min}
[요약]
- IMDSv2와 hop limit 1은 강제, NodeClass로 변경 불가. hostNetwork Pod는 도달성이 다름
- SSH, SSM 없음. 관리형 Bottlerocket, 읽기 전용 root, SELinux enforcing
- 노드 역할은 최소 정책 두 개, 앱 권한은 Pod Identity
- 21일 최대 수명과 주간 AMI로 패치가 Drift로 들어옴
- taint와 label은 테넌트 보안 경계가 아님

NodeClass로 바꿀 수 없는 보안 기본값 네 가지입니다. 첫째, IMDS는 v2만, hop limit 1로 고정입니다. 그래서 일반 Pod는 노드의 인스턴스 메타데이터에 닿지 못합니다. 예전처럼 노드 역할 권한을 Pod가 빌려 쓰는 패턴은 안 되고, 앱 권한은 Pod Identity로 줘야 합니다. hostNetwork Pod는 노드 네트워크를 쓰니 예외라는 점도 기억하세요.
{cue: pause}
둘째, SSH와 SSM 접속이 없습니다. 노드는 읽기 전용 root 파일 시스템의 Bottlerocket 변형이고 SELinux가 enforcing입니다. 노드에 들어가 로그를 보던 습관은 조금 뒤에 볼 로그 수집 기능으로 바꿔야 합니다.
셋째, 노드 역할은 최소 정책 두 개입니다. 넷째, 노드 최대 수명 21일과 주간 AMI입니다. 패치가 Drift로 들어오니 오래된 노드는 남지 않지만, 그만큼 앱이 교체를 견뎌야 합니다.
{cue: question}
마지막 노란 박스는 자주 받는 질문입니다. 팀별 NodePool에 taint를 걸면 격리가 되냐는 질문인데, taint와 label은 배치를 나누는 도구이지 보안 경계가 아닙니다. 테넌트 격리가 필요하면 클러스터나 계정 수준에서 나누셔야 합니다.

[출처]
- https://docs.aws.amazon.com/eks/latest/userguide/auto-security.html (SSH, SSM 미제공, 21일)
- https://docs.aws.amazon.com/eks/latest/userguide/automode.html (immutable AMI, SELinux, read-only root)
- https://docs.aws.amazon.com/eks/latest/userguide/automode-learn-instances.html (IMDSv2, hop limit 1, hostNetwork)
- https://docs.atomai.click/kubernetes-docs/ko/eks-auto-mode/02-nodepool-configuration, 07-node-lifecycle
{cue: transition}
보안 기본값을 봤으니, 이제 용량을 고르는 방법입니다. Spot과 예약 용량부터 보겠습니다.
:::

---
<!-- Slide 6: Spot과 예약 용량 -->
@type: content
@title: Spot, 예약 용량, 정적 풀

## Spot, 예약 용량, 정적 풀

:::html
<style>
.ak3-cap2 { display: grid; grid-template-columns: 1.05fr 1fr; gap: var(--space-4); align-items: start; margin-top: var(--space-3); }
.ak3-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">Spot 풀</button>
  <button class="tab-btn">Capacity Reservation</button>
  <button class="tab-btn">정적 풀</button>
</div>
<div class="tc">
  <div class="ak3-cap2">
    <div class="ak3-stack">
      <div class="callout callout-info"><strong class="text-info">커스텀 풀이 필요</strong><div class="on-surface-muted">built-in 풀은 On-Demand만. 한 풀 안의 우선순위는 reserved, spot, on-demand이고, 배열 순서와 <code>weight</code>는 Spot 비율을 정하지 않습니다.</div></div>
      <div class="callout callout-warning"><strong class="text-warning">selector가 reserved를 뺄 수 있음</strong><div class="on-surface-muted">Pod의 <code>capacity-type: on-demand</code> nodeSelector는 예약 용량을 제외합니다. preferred affinity는 비율을 보장하지 않습니다.</div></div>
    </div>
    <div class="ak3-stack">
      <div class="callout callout-danger"><strong class="text-danger">NTH는 필요 없음</strong><div class="on-surface-muted">중단 처리는 내장입니다. Node Termination Handler DaemonSet과 SQS를 Auto Mode 노드에 두면 처리가 중복됩니다.</div></div>
      <div class="callout callout-warning"><strong class="text-warning">2분은 best effort</strong><div class="on-surface-muted">감지, eviction, 종료 처리가 시간을 씁니다. <code>preStop: sleep 90</code>은 예산 대부분을 소비하는 안티패턴입니다.</div></div>
    </div>
  </div>
</div>
<div class="tc" hidden>
  <div class="ak3-cap2">
<pre class="code-block"><span class="comment"># NodeClass</span>
<span class="key">spec</span>:
  <span class="key">capacityReservationSelectorTerms</span>:
  - <span class="key">id</span>: cr-0123456789abcdef0
<span class="comment"># NodePool</span>
<span class="key">requirements</span>:
- <span class="key">key</span>: karpenter.sh/capacity-type
  <span class="key">operator</span>: In
  <span class="key">values</span>: [<span class="string">"reserved"</span>]</pre>
    <div class="ak3-stack">
      <div class="callout callout-info"><strong class="text-info">기존 예약을 고르는 것</strong><div class="on-surface-muted">manifest가 예약을 만들지 않습니다. 계정, AZ, 유형, 남은 수량을 먼저 확인합니다.</div></div>
      <div class="callout callout-warning"><strong class="text-warning">켜면 클러스터 전체가 바뀜</strong><div class="on-surface-muted">한 NodeClass라도 <code>capacityReservationSelectorTerms</code>를 쓰면 클러스터의 모든 NodeClass가 open ODCR 자동 사용을 멈춥니다. 예약은 쓰지 않아도 과금됩니다.</div></div>
    </div>
  </div>
</div>
<div class="tc" hidden>
  <div class="ak3-cap2">
<pre class="code-block"><span class="key">apiVersion</span>: karpenter.sh/v1
<span class="key">kind</span>: NodePool
<span class="key">spec</span>:
  <span class="key">replicas</span>: 4      <span class="comment"># Pod 수요와 무관하게 유지</span>
  <span class="key">limits</span>:
    <span class="key">nodes</span>: 6         <span class="comment"># 교체 여유</span>
  <span class="key">template</span>:
    <span class="key">spec</span>:
      <span class="key">nodeClassRef</span>: {<span class="key">group</span>: eks.amazonaws.com,
        <span class="key">kind</span>: NodeClass, <span class="key">name</span>: default}
      <span class="key">requirements</span>:
      - {<span class="key">key</span>: node.kubernetes.io/instance-type,
         <span class="key">operator</span>: In, <span class="key">values</span>: [<span class="string">"m5.xlarge"</span>]}</pre>
    <div class="ak3-stack">
      <div class="callout callout-info"><strong class="text-info">미리 띄워 두는 노드</strong><div class="on-surface-muted">GPU 초기화나 cache warm-up처럼 기다릴 수 없는 워크로드용입니다.</div></div>
      <div class="callout callout-warning"><strong class="text-warning">동적 풀과 다른 규칙</strong><div class="on-surface-muted"><code>limits</code>는 <code>nodes</code>만, <code>weight</code> 설정 불가, consolidation 없음. <code>replicas</code>는 지울 수 없어 동적 풀로 되돌릴 수 없습니다.</div></div>
    </div>
  </div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- Spot: 커스텀 풀 필요. 우선순위 reserved, spot, on-demand. 배열 순서와 weight는 비율을 정하지 않음
- capacity-type: on-demand nodeSelector는 reserved를 제외. preferred affinity는 비율 보장 아님
- NTH DaemonSet과 SQS 불필요, 배포 금지. 2분 경고는 best effort, preStop sleep 90은 안티패턴
- Capacity Reservation: NodeClass capacityReservationSelectorTerms + NodePool capacity-type reserved. 예약은 미사용에도 과금
- selector를 한 NodeClass라도 쓰면 클러스터 전체가 open ODCR 자동 사용 중지. selector 없이 open 예약에 맞은 노드는 on-demand label
- 정적 풀: spec.replicas. limits는 nodes만(replicas보다 크게 두어 교체 여유), weight 불가, consolidation 없음, replicas 제거 불가

용량 유형 세 가지를 탭으로 보겠습니다. 첫 탭 Spot입니다. built-in 풀에는 Spot이 없으니 커스텀 풀을 만듭니다. 한 풀 안에서 여러 용량을 허용하면 예약 용량, Spot, On-Demand 순으로 고르고, values 배열 순서나 weight로 Spot 비율을 정할 수는 없습니다. 비율이 필요하면 풀을 나누고 topology spread 같은 워크로드 제약으로 표현합니다.
{cue: pause}
주의할 점이 있습니다. Pod에 capacity-type: on-demand nodeSelector를 걸면 예약 용량은 빠집니다. 예약을 사 두고도 못 쓰는 경우가 여기서 나옵니다. 그리고 Auto Mode 노드에는 Node Termination Handler를 깔지 마세요. 중단 처리는 내장입니다. 2분 경고는 best effort라서, preStop에 sleep 90을 넣으면 정작 종료 처리할 시간이 없어집니다.
{cue: demo}
두 번째 탭은 Capacity Reservation입니다. NodeClass에 capacityReservationSelectorTerms로 예약 ID를 고르고, NodePool은 capacity-type을 reserved로 둡니다. 이 YAML이 예약을 만들어 주지는 않습니다. 이미 산 예약을 쓰는 것이고, 예약은 쓰지 않아도 요금이 나갑니다. 노란 박스가 중요합니다. 한 NodeClass라도 이 selector를 쓰면, 그 클러스터의 모든 NodeClass가 open 예약을 자동으로 쓰던 동작을 멈춥니다. selector 없이 open 예약에 맞춰 뜬 노드는 reserved가 아니라 on-demand로 표시된다는 점도 같이 기억하세요.
세 번째 탭은 정적 풀입니다. spec.replicas를 쓰면 Pod 수요와 무관하게 노드 수를 유지합니다. GPU처럼 초기화가 오래 걸리는 워크로드에 씁니다. 규칙이 다릅니다. limits는 nodes만 쓸 수 있고 replicas보다 크게 두어 교체 여유를 줍니다. weight는 설정할 수 없고 consolidation도 없습니다. 그리고 replicas는 한번 넣으면 지울 수 없어서 동적 풀로 되돌릴 수 없으니, 새 NodePool로 만드세요.

[출처]
- https://docs.aws.amazon.com/eks/latest/userguide/create-node-pool.html (capacity type 우선순위)
- https://docs.aws.amazon.com/eks/latest/userguide/auto-odcr.html (클러스터 전체 open ODCR 동작), create-node-class.html
- https://docs.aws.amazon.com/eks/latest/userguide/auto-static-capacity.html
- https://docs.atomai.click/kubernetes-docs/ko/eks-auto-mode/04-spot-strategies, 05-operations
{cue: transition}
다음은 가속기 워크로드입니다. GPU와 EFA를 Auto Mode에서 어떻게 쓰는지 보겠습니다.
:::

---
<!-- Slide 7: GPU와 EFA -->
@type: content
@title: GPU와 EFA: 드라이버는 AWS, 사양은 사용자

## GPU와 EFA: 드라이버는 AWS, 사양은 사용자

:::html
<style>
.ak3-gpu { display: grid; grid-template-columns: 1.05fr 1fr; gap: var(--space-4); align-items: start; margin-top: var(--space-3); }
.ak3-gt { width: 100%; font-size: var(--fs-caption); word-break: keep-all; }
.data-table th { text-transform: none; letter-spacing: normal; font-size: var(--fs-caption); }
.ak3-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">GPU 추론</button>
  <button class="tab-btn">EFA와 Placement Group</button>
</div>
<div class="tc">
  <div class="ak3-gpu">
<pre class="code-block"><span class="key">requirements</span>:
- <span class="key">key</span>: eks.amazonaws.com/instance-gpu-manufacturer
  <span class="key">operator</span>: In
  <span class="key">values</span>: [<span class="string">"nvidia"</span>]
- <span class="key">key</span>: node.kubernetes.io/instance-type
  <span class="key">operator</span>: In
  <span class="key">values</span>: [<span class="string">"g5.2xlarge"</span>, <span class="string">"g5.4xlarge"</span>]
<span class="key">taints</span>:
- <span class="key">key</span>: nvidia.com/gpu
  <span class="key">effect</span>: NoSchedule
<span class="key">limits</span>:
  <span class="key">nvidia.com/gpu</span>: <span class="string">"4"</span>
<span class="key">disruption</span>:
  <span class="key">consolidationPolicy</span>: WhenEmpty
  <span class="key">consolidateAfter</span>: 10m</pre>
    <div class="ak3-stack">
      <div class="callout callout-info"><strong class="text-info">드라이버와 device plugin은 관리형</strong><div class="on-surface-muted">NVIDIA, Neuron 드라이버와 NVIDIA device plugin이 내장입니다. plugin은 DaemonSet으로 보이지 않고, <code>amiFamily</code> 지정도 없습니다.</div></div>
      <table class="data-table ak3-gt">
        <thead><tr><th>유형</th><th>GPU</th><th>vCPU / RAM</th></tr></thead>
        <tbody>
          <tr><td>g5.xlarge</td><td>A10G 1개</td><td>4 / 16 GiB</td></tr>
          <tr><td>g5.2xlarge</td><td>A10G 1개</td><td>8 / 32 GiB</td></tr>
          <tr><td>g5.12xlarge</td><td>A10G 4개</td><td>48 / 192 GiB</td></tr>
        </tbody>
      </table>
      <div class="callout callout-warning"><strong class="text-warning">노드 전체 사양을 보세요</strong><div class="on-surface-muted">4 CPU, 16Gi를 요청하는 Pod는 시스템 예약 때문에 g5.xlarge에 들어가지 않습니다. GPU는 request와 limit을 같게 둡니다.</div></div>
    </div>
  </div>
</div>
<div class="tc" hidden>
  <div class="ak3-gpu">
<pre class="code-block"><span class="key">advancedNetworking</span>:
  <span class="key">networkInterfaces</span>:
  - {<span class="key">networkCardIndex</span>: 0, <span class="key">deviceIndex</span>: 0,
     <span class="key">interfaceType</span>: interface,
     <span class="key">secondaryIPv4PrefixCount</span>: 1}
  - {<span class="key">networkCardIndex</span>: 0, <span class="key">deviceIndex</span>: 1,
     <span class="key">interfaceType</span>: efa-only}
  - {<span class="key">networkCardIndex</span>: 1, <span class="key">deviceIndex</span>: 0,
     <span class="key">interfaceType</span>: efa-only}
<span class="key">placementGroupSelector</span>:
  <span class="key">name</span>: ml-training-pg</pre>
    <div class="ak3-stack">
      <div class="callout callout-info"><strong class="text-info">placement group 2026-05, EFA 2026-07</strong><div class="on-surface-muted">NodeClass에서 기존 placement group(cluster, spread, partition)과 EFA interface를 지정합니다.</div></div>
      <div class="callout callout-info"><strong class="text-info"><code>efa-only</code>는 Pod IP를 쓰지 않음</strong><div class="on-surface-muted">RDMA 전용입니다. Pod IP는 card 0, device 0의 <code>interface</code>와 prefix가 맡습니다. Pod는 <code>vpc.amazonaws.com/efa</code>를 요청합니다.</div></div>
      <div class="callout callout-warning"><strong class="text-warning">제약</strong><div class="on-surface-muted">IPv4만, 시작 후 ENI 추가 없음, 다중 interface와 <code>associatePublicIPAddress</code> 조합 불가, 같은 NodeClass에 static hugepages 불가, EFA DRA 경로 미지원</div></div>
    </div>
  </div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- GPU: NVIDIA, Neuron 드라이버와 NVIDIA device plugin 내장(DaemonSet으로 안 보임). requirements에 eks.amazonaws.com/instance-gpu-manufacturer, nvidia.com/gpu taint, limits nvidia.com/gpu
- g5.xlarge는 4 vCPU, 16 GiB라 4 CPU, 16Gi Pod는 들어가지 않음. GPU request와 limit은 같게
- 학습 후 churn을 줄이려면 WhenEmpty와 consolidateAfter 10m 같은 설정
- placement group(2026-05-05)과 EFA networkInterfaces(2026-07-21, auto-change 기준): advancedNetworking.networkInterfaces, efa-only, placementGroupSelector
- efa-only는 Pod IP 미사용, Pod는 vpc.amazonaws.com/efa 요청. IPv4 전용, 다중 interface와 공인 IP 조합 불가, DRA 경로 미지원

GPU 워크로드입니다. Auto Mode에는 NVIDIA와 Neuron 드라이버, NVIDIA device plugin이 들어 있어서 예전처럼 GPU AMI를 고르거나 device plugin DaemonSet을 설치할 일이 없습니다. plugin은 클러스터에서 DaemonSet으로 보이지도 않습니다. NodePool에는 GPU 제조사 label로 nvidia를 고르고, 일반 Pod가 비싼 노드에 올라가지 않도록 nvidia.com/gpu taint를 겁니다. limits에 GPU 개수를 넣으면 풀 전체의 GPU 상한이 됩니다.
{cue: pause}
가장 흔한 실수는 오른쪽 표입니다. g5.xlarge는 4 vCPU, 16 GiB인데, 4 CPU와 16Gi를 요청하는 Pod는 시스템 예약 때문에 들어가지 않습니다. 노드 전체 사양에서 예약분을 빼고 계산해야 합니다. GPU는 정수 리소스라 request와 limit을 같게 둡니다. 작업이 끝날 때마다 노드가 바로 사라졌다 다시 뜨는 것을 줄이려면 WhenEmpty와 consolidateAfter를 씁니다. 여기서는 10분으로 두었고, AWS 예제는 요청이 들쭉날쭉한 GPU 워크로드에 1시간을 씁니다. GPU 노드를 다시 띄우는 시간과 비용을 놓고 정하시면 됩니다.
{cue: demo}
두 번째 탭은 올해 추가된 placement group과 EFA입니다. placement group은 5월, EFA interface는 7월에 들어왔습니다. NodeClass의 advancedNetworking.networkInterfaces로 interface 구성을 직접 적습니다. card 0, device 0은 일반 interface로 Pod IP를 맡고, 나머지는 efa-only로 RDMA 전용입니다. placementGroupSelector로 이미 만든 placement group을 고릅니다.
제약도 있습니다. IPv4만 되고, 시작 후 ENI를 추가하지 않으며, 여러 interface와 공인 IP는 같이 쓸 수 없습니다. 다른 compute 모드의 EFA DRA 예제는 Auto Mode에서 동작하지 않으니 device plugin 경로를 씁니다.

[출처]
- https://docs.aws.amazon.com/eks/latest/userguide/auto-accelerated.html
- https://docs.aws.amazon.com/eks/latest/userguide/device-management-efa.html, create-node-class.html (networkInterfaces, placementGroupSelector)
- https://docs.aws.amazon.com/eks/latest/userguide/auto-change.html (2026-05-05 placement group, 2026-07-21 EFA)
- https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-eks-efa-placement-groups/
- https://aws.amazon.com/ec2/instance-types/g5/
- https://docs.atomai.click/kubernetes-docs/ko/eks-auto-mode/08-workload-optimization
{cue: transition}
가속기까지 봤으니, 이제 AZ 장애가 났을 때 Auto Mode가 어떻게 움직이는지 보겠습니다.
:::

---
<!-- Slide 8: ARC zonal shift -->
@type: content
@title: AZ 장애: ARC zonal shift

## AZ 장애: ARC zonal shift

:::html
<style>
.ak3-arc { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--space-3); margin-bottom: var(--space-3); }
.ak3-az { border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-3); font-size: var(--fs-card); word-break: keep-all; }
.ak3-az.bad { border-color: var(--danger); }
.ak3-az strong { display: block; margin-bottom: var(--space-1); }
.ak3-az .s { color: var(--text-secondary); }
.ak3-az code { white-space: normal; word-break: break-all; }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak3-arc">
  <div class="ak3-az bad fragment fade-up" data-fragment-index="1"><strong class="text-danger">장애 AZ (shift 대상)</strong><span class="s">새 노드 프로비저닝 중단. 그 AZ 노드의 consolidation, Drift 같은 voluntary disruption 중단</span></div>
  <div class="ak3-az fragment fade-up" data-fragment-index="2"><strong class="text-accent">정상 AZ</strong><span class="s">대체 용량은 여기서 뜹니다. 단, 대체 Pod가 장애 AZ에 의존하면 정상 AZ의 voluntary disruption도 멈춥니다.</span></div>
  <div class="ak3-az fragment fade-up" data-fragment-index="3"><strong class="text-accent">사용자 설정</strong><span class="s">클러스터의 <code>zonal-shift-config</code>를 켜면 끝. 플래그, IAM 변경 없음. autoshift는 ARC에서 따로</span></div>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="4">
  <div class="callout callout-info"><strong class="text-info">2026-07-10부터 Auto Mode 지원</strong><div class="on-surface-muted">ARC zonal shift 자체는 추가 요금이 없고, 대체 용량은 일반 요금입니다.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">옮겨 주지 않는 것</strong><div class="on-surface-muted">단일 AZ EBS 볼륨, <code>DoNotSchedule</code> 같은 엄격한 AZ 제약은 그대로입니다. replica와 topology spread가 먼저입니다.</div></div>
</div>
:::

:::notes
{timing: 2min}
[요약]
- 2026-07-10부터 Auto Mode 클러스터에서 ARC zonal shift와 autoshift 사용 가능. 클러스터에서 활성화만 하면 됨
- shift 중: 장애 AZ의 신규 프로비저닝 중단, 그 AZ의 voluntary disruption 중단. 대체 Pod가 장애 AZ에 의존하면 정상 AZ의 voluntary disruption도 중단
- autoshift는 별도 구성. zonal shift 자체 추가 요금 없음
- 단일 AZ 볼륨과 엄격한 AZ 제약은 이동시키지 않음

AZ 장애 대응입니다. 2026년 7월 10일부터 Auto Mode 클러스터에서도 ARC zonal shift를 쓸 수 있습니다. update-cluster-config의 zonal-shift-config로 켜면 되고, 별도 플래그나 IAM 변경, Karpenter 버전을 챙길 필요가 없습니다.
{cue: pause}
shift가 걸리면 세 상자처럼 움직입니다. 장애 AZ에는 새 노드를 만들지 않고, 그 AZ 노드의 consolidation이나 Drift 교체도 멈춥니다. 장애 중에 노드를 줄이거나 바꾸다가 용량을 잃는 일을 막는 것입니다. 정상 AZ에서는 대체 용량이 뜨는데, 대체 Pod 배치가 장애 AZ에 묶여 있으면 정상 AZ의 voluntary disruption도 멈춥니다.
autoshift, 즉 AWS가 장애를 감지해 자동으로 shift하는 기능은 따로 구성해야 합니다.
{cue: question}
그럼 zonal shift만 켜면 AZ 장애가 해결될까요. 노란 박스처럼, 단일 AZ에 묶인 EBS 볼륨이나 DoNotSchedule로 엄격하게 건 AZ 제약은 옮겨 주지 않습니다. replica를 여러 AZ에 나누고 topology spread를 설계하는 것이 먼저입니다.

[출처]
- https://aws.amazon.com/about-aws/whats-new/2026/07/eks-auto-mode-arc-zonal-shift
- https://docs.aws.amazon.com/eks/latest/userguide/zone-shift-enable.html
- https://aws.amazon.com/blogs/containers/arc-zonal-shift-support-for-eks-auto-mode-and-karpenter/
- https://docs.atomai.click/kubernetes-docs/ko/eks-auto-mode/README, 05-operations
{cue: transition}
여기까지가 Auto Mode 고유의 설정이었습니다. 이제 업그레이드 순서를 보겠습니다.
:::

---
<!-- Slide 9: 업그레이드 순서 -->
@type: content
@title: 1.37 업그레이드: Karpenter가 먼저

## 1.37 업그레이드: Karpenter가 먼저

:::html
<style>
.ak3-steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-3); margin-top: var(--space-3); margin-bottom: var(--space-3); }
.ak3-step { border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-3); font-size: var(--fs-card); word-break: keep-all; overflow-wrap: break-word; }
.ak3-num { display: inline-flex; align-items: center; justify-content: center; width: 1.8em; height: 1.8em; border-radius: 50%; background: var(--accent-subtle); color: var(--accent); font-weight: var(--weight-bold); margin-bottom: var(--space-2); }
.ak3-step strong { display: block; margin-bottom: var(--space-1); }
.ak3-sub { color: var(--text-secondary); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">Self-managed</button>
  <button class="tab-btn">v1.15.0 breaking</button>
  <button class="tab-btn">Auto Mode</button>
</div>
<div class="tc">
  <div class="ak3-steps">
    <div class="ak3-step"><span class="ak3-num">1</span><strong>Karpenter 1.15.x</strong><span class="ak3-sub"><code>karpenter-crd</code>와 controller chart를 함께, 버전 문자열은 <code>1.15.0</code></span></div>
    <div class="ak3-step"><span class="ak3-num">2</span><strong>상태 확인</strong><span class="ak3-sub">EC2NodeClass <code>ValidationSucceeded</code>, 대시보드 label 변경</span></div>
    <div class="ak3-step"><span class="ak3-num">3</span><strong>컨트롤 플레인 1.37</strong><span class="ak3-sub">리전 기본은 1.36이라 버전 명시</span></div>
    <div class="ak3-step"><span class="ak3-num">4</span><strong>노드 AMI 갱신</strong><span class="ak3-sub">alias pin을 1.37 AMI로 바꾸면 Drift로 롤링, budget 적용</span></div>
  </div>
  <div class="callout callout-warning fragment fade-up" data-fragment-index="1"><strong class="text-warning">왜 Karpenter가 먼저인가</strong>: 1.37 호환 버전은 1.15.x뿐입니다. v1.14 LTS로는 1.36까지만 갈 수 있습니다.</div>
</div>
<div class="tc" hidden>
  <div class="card-grid">
    <div class="callout callout-warning"><strong class="text-warning">Node Repair가 voluntary로</strong><div class="on-surface-muted">대체 노드 선 생성, NDB reason <code>Unhealthy</code>. CRD enum이 바뀌므로 CRD를 함께 업그레이드</div></div>
    <div class="callout callout-warning"><strong class="text-warning">kubelet 검증이 controller로</strong><div class="on-surface-muted">apply는 성공, EC2NodeClass가 <code>Invalid<wbr>Kubelet<wbr>Configuration</code>으로 NotReady</div></div>
    <div class="callout callout-warning"><strong class="text-warning">무시되던 설정 거부</strong><div class="on-surface-muted">Bottlerocket <code>podsPerCore</code>, <code>clusterDNS</code> 2개 이상은 <code>Unsupported<wbr>Kubelet<wbr>Configuration</code></div></div>
    <div class="callout callout-warning"><strong class="text-warning">메트릭 label 변경</strong><div class="on-surface-muted"><code>reason</code> 소문자화, <code>consolidation_<wbr>type</code>은 empty, single, multi, 미분류 error는 <code>unknown</code></div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="ak3-steps">
    <div class="ak3-step"><span class="ak3-num">1</span><strong>관리형 구성 요소</strong><span class="ak3-sub">Karpenter, CNI, CoreDNS 등은 AWS가 업데이트</span></div>
    <div class="ak3-step"><span class="ak3-num">2</span><strong>1.37 변경 점검</strong><span class="ak3-sub">SELinuxMount 기본 활성, Auto Mode AMI는 SELinux enforcing</span></div>
    <div class="ak3-step"><span class="ak3-num">3</span><strong>NodePool 정책 명시</strong><span class="ak3-sub">새 NodePool의 기본 <code>Balanced</code> 반영 여부 결정</span></div>
    <div class="ak3-step"><span class="ak3-num">4</span><strong>노드는 Drift로 교체</strong><span class="ak3-sub">PDB와 NDB를 존중하며 롤링</span></div>
  </div>
  <div class="callout callout-info fragment fade-up" data-fragment-index="2"><strong class="text-info">사용자가 볼 것</strong>: PDB가 교체를 막고 있지 않은지, 같은 볼륨을 다른 SELinux 라벨로 공유하는 Pod가 <code>ContainerCreating</code>에 머물지 않는지</div>
</div>
:::

:::notes
{timing: 2min}
[요약]
- self-managed 순서: Karpenter 1.15.x(CRD chart 포함, 버전 문자열은 v 없이 1.15.0), 상태 확인, 컨트롤 플레인 1.37, 노드 AMI 갱신과 Drift 롤링
- v1.15.0 breaking: Node Repair voluntary화와 Unhealthy enum(CRD 동시 업그레이드), kubelet 검증의 controller 이동, Bottlerocket podsPerCore와 다중 clusterDNS 거부, 메트릭 label 변경
- Auto Mode: 구성 요소는 AWS가 업데이트, 사용자는 1.37 변경(SELinuxMount)과 NodePool 정책을 점검, 노드는 Drift로 교체

1.37로 올릴 때 self-managed의 순서는 Karpenter가 먼저입니다. 1.37을 지원하는 Karpenter는 1.15.x뿐이라서, 컨트롤 플레인을 먼저 올리면 지원 범위를 벗어난 상태가 됩니다. Helm으로 올릴 때는 CRD chart인 karpenter-crd와 controller chart를 같이 올리고, 버전 문자열은 v 없이 1.15.0입니다. v1.15.0이라고 쓰면 not found가 납니다.
{cue: demo}
두 번째 탭은 v1.15.0의 breaking change 네 가지입니다. Node Repair가 voluntary disruption이 되어 budget reason Unhealthy를 따르므로 CRD를 함께 올립니다. kubelet 검증이 controller로 옮겨져, 잘못된 값도 apply는 성공하고 EC2NodeClass가 NotReady가 됩니다. 무시되던 Bottlerocket 설정은 이제 거부되고, 메트릭 label이 바뀌어 대시보드 쿼리를 손봐야 합니다.
{cue: pause}
세 번째 탭 Auto Mode는 단계가 짧습니다. 관리형 구성 요소는 AWS가 업데이트하고, 사용자는 1.37의 SELinuxMount 기본 활성화를 확인합니다. 같은 볼륨을 다른 SELinux 라벨로 공유하는 Pod는 ContainerCreating에 머물 수 있습니다. 그리고 3부에서 본 Balanced 기본값을 반영할지 NodePool에 명시해 두고, 노드는 Drift로 교체되니 PDB가 막고 있지 않은지 봅니다.

[출처]
- https://karpenter.sh/docs/upgrading/upgrade-guide/#upgrading-to-1150, https://github.com/aws/karpenter-provider-aws/releases/tag/v1.15.0
- helm show chart oci://public.ecr.aws/karpenter/karpenter --version 1.15.0 (2026-10-20 실행)
- https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions-standard.html#kubernetes-1-37
{cue: transition}
업그레이드든 평소 운영이든, 무엇을 보고 있어야 이상을 알아챌 수 있을까요.
:::


---
<!-- Slide 10: Auto Mode 로그와 진단 -->
@type: content
@title: SSH 없이 진단: 로그와 NodeDiagnostic

## SSH 없이 진단: 로그와 NodeDiagnostic

:::html
<style>
.ak3-dx { display: grid; grid-template-columns: 1fr 1.1fr; gap: var(--space-4); align-items: start; margin-top: var(--space-3); }
.ak3-lt { width: 100%; font-size: var(--fs-card); word-break: keep-all; overflow-wrap: anywhere; }
.data-table th { text-transform: none; letter-spacing: normal; font-size: var(--fs-card); }
.ak3-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.ak3-ev { display: flex; flex-wrap: wrap; gap: var(--space-2); margin-top: var(--space-2); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">관리형 구성 요소 로그</button>
  <button class="tab-btn">노드 로그: NodeDiagnostic</button>
  <button class="tab-btn">kubectl로 먼저 볼 것</button>
</div>
<div class="tc">
  <div class="ak3-dx">
    <table class="data-table ak3-lt">
      <thead><tr><th>log type</th><th>무엇의 판단인가</th></tr></thead>
      <tbody>
        <tr><td><code>AUTO_MODE_COMPUTE_LOGS</code></td><td>관리형 Karpenter: 프로비저닝, disruption</td></tr>
        <tr><td><code>AUTO_MODE_BLOCK_STORAGE_LOGS</code></td><td>EBS CSI</td></tr>
        <tr><td><code>AUTO_MODE_LOAD_BALANCING_LOGS</code></td><td>Load Balancer controller</td></tr>
        <tr><td><code>AUTO_MODE_IPAM_LOGS</code></td><td>IP 주소 관리</td></tr>
      </tbody>
    </table>
    <div class="ak3-stack">
      <div class="callout callout-info"><strong class="text-info">CloudWatch Vended Logs로 전달</strong><div class="on-surface-muted"><code>PutDeliverySource</code>, <code>PutDeliveryDestination</code>, <code>CreateDelivery</code> 순서. 목적지는 CloudWatch Logs, S3, Firehose</div></div>
      <div class="callout callout-warning"><strong class="text-warning">control plane logging과 별개</strong><div class="on-surface-muted">api, audit 로그를 켜도 이 로그는 오지 않습니다. 따로 연결하고 전송, 보관 요금을 확인합니다.</div></div>
    </div>
  </div>
</div>
<div class="tc" hidden>
  <div class="ak3-dx">
<pre class="code-block"><span class="key">apiVersion</span>: eks.amazonaws.com/v1alpha1
<span class="key">kind</span>: NodeDiagnostic
<span class="key">metadata</span>:
  <span class="key">name</span>: i-0abc1234def567890   <span class="comment"># 노드 이름</span>
<span class="key">spec</span>:
  <span class="key">logCapture</span>:
    <span class="key">destination</span>: <span class="string">"https://...presigned S3 PUT URL"</span></pre>
    <div class="ak3-stack">
      <div class="callout callout-info"><strong class="text-info">노드 monitoring agent가 수집</strong><div class="on-surface-muted">노드의 로그와 구성 번들을 S3로 올립니다. 결과는 <code>.status.captureStatuses</code>의 Success, SuccessWithErrors, Failure</div></div>
      <div class="callout callout-warning"><strong class="text-warning">spec에 URL이 그대로 남음</strong><div class="on-surface-muted">presigned 자격 증명까지 저장되고 자동 삭제되지 않습니다. 만료를 짧게, 끝나면 지웁니다. agent v1.6.1 이상은 <code>destination: node</code>도 받습니다.</div></div>
      <div class="callout callout-info"><strong class="text-info">그 밖의 도구</strong><div class="on-surface-muted"><code>kubectl debug</code> 디버그 컨테이너, 부팅 문제는 <code>aws ec2 get-console-output</code>. agent는 node condition과 event를 내고 자동 repair에 쓰입니다.</div></div>
    </div>
  </div>
</div>
<div class="tc" hidden>
  <div class="ak3-dx">
<pre class="code-block"><span class="comment"># Auto Mode 노드만</span>
kubectl get nodes -L eks.amazonaws.com/compute-type
<span class="comment"># NodeClaim condition (phase 필드는 없음)</span>
kubectl get nodeclaims -o wide
kubectl describe nodeclaim &lt;name&gt;
<span class="comment"># 못 뜬 Pod</span>
kubectl get events -A \
  --field-selector reason=FailedScheduling</pre>
    <div class="ak3-stack">
      <div class="card"><strong class="text-accent">NodeClaim condition</strong><div class="ak3-ev"><code>Launched</code><code>Registered</code><code>Initialized</code><code>Ready</code><code>Drifted</code></div></div>
      <div class="card"><strong class="text-accent">자주 보는 event</strong><div class="ak3-ev"><code>DisruptionBlocked</code><code>Unconsolidatable</code><code>FailedScheduling</code><code>NodeClassNotReady</code></div></div>
      <div class="callout callout-warning"><strong class="text-warning"><code>karpenter_*</code> 메트릭을 가정하지 않음</strong><div class="on-surface-muted">Auto Mode에 <code>Karpenter</code> CloudWatch namespace가 자동으로 생기지 않습니다.</div></div>
    </div>
  </div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- 관리형 구성 요소 로그 4종: AUTO_MODE_COMPUTE_LOGS, BLOCK_STORAGE, LOAD_BALANCING, IPAM. CloudWatch Vended Logs(delivery source, destination, delivery)로 CloudWatch Logs, S3, Firehose에 전달. control plane logging과 별개
- 노드 로그: NodeDiagnostic(eks.amazonaws.com/v1alpha1), metadata.name은 노드 이름, spec.logCapture.destination은 presigned S3 PUT URL. 로그와 구성 번들 업로드, captureStatuses로 결과 확인
- spec에 presigned URL이 자격 증명째 저장되고 자동 삭제 없음: 읽기 권한 제한, 짧은 만료, 사용 후 삭제
- kubectl debug 디버그 컨테이너, 부팅 문제는 ec2 get-console-output, agent는 node condition과 event 발행
- kubectl: compute-type label, NodeClaim condition, event 4종. karpenter_* 메트릭을 가정하지 않음

SSH가 없으면 노드 문제는 어떻게 볼까요. 세 가지 도구가 있습니다. 첫 번째 탭은 관리형 구성 요소 로그입니다. 관리형 Karpenter, EBS CSI, Load Balancer controller, IPAM의 로그를 네 가지 log type으로 받을 수 있습니다. 노드가 왜 안 뜨는지, 왜 consolidation을 안 하는지는 COMPUTE 로그에 나옵니다.
{cue: pause}
이 로그는 CloudWatch Vended Logs로 옵니다. delivery source, destination, delivery 세 개를 연결해야 하고, control plane logging의 api, audit을 켠다고 같이 오지 않습니다. 따로 연결하시고 전송과 보관 요금을 확인하세요.
{cue: demo}
두 번째 탭은 노드 자체의 로그입니다. NodeDiagnostic이라는 객체를 노드 이름으로 만들고 destination에 S3 presigned PUT URL을 넣으면, 노드의 monitoring agent가 로그와 구성 번들을 묶어 올립니다. 결과는 status의 captureStatuses로 봅니다. 주의할 점은 spec에 presigned URL이 자격 증명째 그대로 남는다는 것입니다. 이 객체를 읽을 수 있는 사람은 그 버킷 경로에 업로드할 수 있으니, 만료를 짧게 두고 끝나면 지웁니다. node monitoring agent v1.6.1 이상이면 destination에 node를 넣는 방법도 있고, kubectl ekslogs 플러그인이 이 과정을 감싸 줍니다. 그 밖에 kubectl debug로 디버그 컨테이너를 띄우거나, 부팅 단계 문제는 EC2 get-console-output으로 콘솔 출력을 봅니다.
세 번째 탭은 평소에 먼저 볼 것들입니다. compute-type label로 Auto Mode 노드를 고르고, NodeClaim의 condition을 봅니다. NodeClaim에는 phase 필드가 없습니다. event는 DisruptionBlocked, Unconsolidatable, FailedScheduling, NodeClassNotReady 네 가지를 자주 봅니다. 그리고 self-managed에서 쓰던 karpenter 메트릭이 Auto Mode에 자동으로 생긴다고 가정하지 마세요.

[출처]
- https://docs.aws.amazon.com/eks/latest/userguide/auto-managed-component-logs.html
- https://docs.aws.amazon.com/eks/latest/userguide/auto-get-logs.html
- https://docs.aws.amazon.com/eks/latest/userguide/auto-troubleshoot.html
- https://docs.atomai.click/kubernetes-docs/ko/eks-auto-mode/03-scaling-behavior, 05-operations
{cue: transition}
Auto Mode 진단 도구를 봤으니, self-managed에서 쓰는 메트릭과 함께 무엇을 볼지 정리하겠습니다.
:::

---
<!-- Slide 11: 관측 포인트 -->
@type: content
@title: 무엇을 볼까: 이벤트와 메트릭

## 무엇을 볼까: 이벤트와 메트릭

:::html
<style>
.ak3-obs { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); margin-bottom: var(--space-3); }
.ak3-q { font-size: var(--fs-card); color: var(--text-secondary); margin-bottom: var(--space-2); word-break: keep-all; }
.ak3-sig { font-family: var(--font-mono); font-size: var(--fs-caption); color: var(--text-primary); word-break: break-all; margin-top: var(--space-1); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak3-obs">
  <div class="card fragment fade-up" data-fragment-index="1">
    <strong class="text-accent">얼마나 흔들렸나</strong>
    <div class="ak3-q">disruption이 Pod에 준 영향</div>
    <div class="ak3-sig">karpenter_pods_disrupted_total</div>
    <div class="ak3-sig">label: consolidation_policy, termination_mode</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="2">
    <strong class="text-accent">Balanced는 왜 승인했나</strong>
    <div class="ak3-q">점수와 실행된 이동</div>
    <div class="ak3-sig">karpenter_consolidation_score</div>
    <div class="ak3-sig">karpenter_consolidation_moves_total</div>
    <div class="ak3-sig">event: ConsolidationApproved</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="3">
    <strong class="text-accent">무엇이 막혔나</strong>
    <div class="ak3-q">budget 여유와 실패</div>
    <div class="ak3-sig">karpenter_nodepool_allowed_disruptions</div>
    <div class="ak3-sig">karpenter_voluntary_disruption_queue_failures_total</div>
    <div class="ak3-sig">karpenter_cloudprovider_errors_total</div>
  </div>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="4">
  <div class="callout callout-info"><strong class="text-info">Auto Mode는 앞 장의 도구로</strong><div class="on-surface-muted">위 메트릭은 self-managed 기준입니다. Auto Mode는 COMPUTE 로그, NodeClaim, event로 봅니다. event source는 <code>eks-auto-mode/compute</code></div></div>
  <div class="callout callout-warning"><strong class="text-warning">EC2 목록에서 기본 숨김</strong><div class="on-surface-muted">2026-04-22 이후 Auto Mode 인스턴스는 EC2 콘솔과 describe 목록에서 숨겨집니다. <code>include-managed-resources</code>로 조회</div></div>
</div>
:::

:::notes
{timing: 2min}
[요약]
- 영향: karpenter_pods_disrupted_total(v1.15 신규), consolidation_policy와 termination_mode label
- Balanced 판단: karpenter_consolidation_score, karpenter_consolidation_moves_total, ConsolidationApproved event
- 막힘: karpenter_nodepool_allowed_disruptions, voluntary_disruption_queue_failures_total, cloudprovider_errors_total (v1.15에서 label 변경)
- Auto Mode: karpenter_* 메트릭 대신 COMPUTE 로그, NodeClaim, event(eks-auto-mode/compute). 2026-04-22 이후 인스턴스는 EC2 목록에서 기본 숨김

이번 장은 self-managed Karpenter의 메트릭입니다. 관측은 세 가지 질문으로 나누면 쉽습니다. 첫째, disruption이 Pod를 얼마나 흔들었나. v1.15에서 karpenter_pods_disrupted_total이 추가되었고, consolidation_policy와 termination_mode label로 어떤 정책, 어떤 종료 방식에서 나온 것인지 나눠 볼 수 있습니다.
{cue: pause}
둘째, Balanced 정책이 왜 이 교체를 승인했나. karpenter_consolidation_score와 consolidation_moves_total 메트릭, 그리고 ConsolidationApproved event로 확인합니다. Balanced로 바꾼 뒤 "왜 노드가 안 줄어드냐"는 질문이 나오면 여기서 점수를 보시면 됩니다.
셋째, 무엇이 막혔나. NodePool별로 지금 허용되는 disruption 수, disruption queue 실패, cloud provider 오류를 봅니다. 앞에서 말씀드린 것처럼 v1.15에서 이 메트릭들의 label 값이 바뀌었으니 기존 쿼리를 확인하세요.
{cue: question}
Auto Mode에서는 어떨까요. 관리형 controller의 karpenter 메트릭을 사용자가 수집하는 경로는 공식 문서에 없습니다. 그래서 앞 장에서 본 AUTO_MODE_COMPUTE_LOGS, NodeClaim condition, event가 출발점이고, event source 이름은 eks-auto-mode/compute입니다. 한 가지 함정이 있습니다. 2026년 4월 22일 이후 만들어진 Auto Mode 인스턴스는 EC2 콘솔과 describe-instances 목록에서 기본으로 숨겨집니다. include-managed-resources 파라미터나 인스턴스 ID 직접 조회, EKS 콘솔로 보셔야 합니다.

[출처]
- https://karpenter.sh/docs/upgrading/upgrade-guide/#upgrading-to-1150, v1.15.0 릴리스 노트 (메트릭과 event)
- https://docs.aws.amazon.com/eks/latest/userguide/automode-learn-instances.html (2026-04-22 이후 관리형 리소스 기본 숨김)
- https://docs.aws.amazon.com/eks/latest/userguide/auto-change.html (2025-09-10, event source eks-auto-mode/compute)
{cue: transition}
운영의 마지막 축은 비용입니다.
:::


---
<!-- Slide 12: 비용 -->
@type: content
@title: 비용: 관리비는 할인되지 않는다

## 비용: 관리비는 할인되지 않는다

:::html
<style>
.ak3-cost { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); align-items: start; }
.ak3-calc { display: flex; flex-direction: column; gap: var(--space-2); }
.ak3-row { display: grid; grid-template-columns: 7rem 1fr; align-items: center; gap: var(--space-3); font-size: var(--fs-card); }
.ak3-row label { color: var(--text-secondary); }
.ak3-pick { display: flex; gap: var(--space-2); }
.ak3-pick .btn { color: var(--on-surface); }
.ak3-pick .btn.active { background: var(--accent-subtle); border-color: var(--accent); color: var(--accent); }
.ak3-calc .metric-value { font-size: var(--fs-subtitle); white-space: nowrap; }
.ak3-calc .slider-value { min-width: 4rem; }
.ak3-cap { font-size: var(--fs-caption); color: var(--text-secondary); word-break: keep-all; }
.ak3-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak3-cost">
  <div class="ak3-calc card">
    <div class="ak3-pick" id="ak3-pick">
      <button class="btn btn-sm active" data-t="m5">m5.large</button>
      <button class="btn btn-sm" data-t="m7g">m7g.large</button>
    </div>
    <div class="ak3-row"><label for="ak3-n">노드 수</label><div class="slider-container"><input type="range" id="ak3-n" min="1" max="150" value="20"><span class="slider-value" id="ak3-n-v">20</span></div></div>
    <div class="card-grid">
      <div class="metric-card"><div class="metric-value" id="ak3-fee">-</div><div class="metric-label">월 Auto Mode 관리비</div></div>
      <div class="metric-card"><div class="metric-value" id="ak3-od">-</div><div class="metric-label">월 On-Demand EC2</div></div>
    </div>
    <div class="ak3-cap" id="ak3-ratio"></div>
    <div class="ak3-cap">서울 리전 Price List API 단가, 월 730시간 가정의 계산 모델입니다.</div>
  </div>
  <div class="ak3-stack">
    <div class="callout callout-info fragment fade-left" data-fragment-index="1"><strong class="text-info">인스턴스 유형과 시간 기준</strong><div class="on-surface-muted">EC2 요금과 별도로 부과, 초 단위 과금, 최소 1분</div></div>
    <div class="callout callout-warning fragment fade-left" data-fragment-index="2"><strong class="text-warning">구매 옵션과 독립</strong><div class="on-surface-muted">Spot, RI, Savings Plans 할인이 관리비를 줄이지 않습니다. Spot일수록 비율이 커집니다.</div></div>
    <div class="callout callout-info fragment fade-left" data-fragment-index="3"><strong class="text-info">GPU 계열 인하 (2026-07-01)</strong><div class="on-surface-muted">G 계열 35%, P 계열과 Trainium 60% 인하. 조직 150노드 초과는 별도 문의</div></div>
  </div>
</div>
:::

:::script
(function () {
  var PRICE = { m5: [0.01416, 0.118], m7g: [0.01204, 0.1003] };
  var HOURS = 730;
  var pick = document.getElementById('ak3-pick');
  var n = document.getElementById('ak3-n');
  if (!pick || !n) return;
  var t = 'm5';
  function usd(x) { return '$' + x.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function update() {
    var k = parseInt(n.value, 10);
    var p = PRICE[t];
    var fee = k * HOURS * p[0];
    var od = k * HOURS * p[1];
    document.getElementById('ak3-n-v').textContent = k;
    document.getElementById('ak3-fee').textContent = usd(fee);
    document.getElementById('ak3-od').textContent = usd(od);
    document.getElementById('ak3-ratio').textContent = '관리비 $' + p[0] + '/h, On-Demand $' + p[1] + '/h, 비율 ' + (p[0] / p[1] * 100).toFixed(1) + '% (계산값, AWS 공식 표현 아님)';
    pick.querySelectorAll('.btn').forEach(function (b) { b.classList.toggle('active', b.getAttribute('data-t') === t); });
  }
  pick.addEventListener('click', function (e) { var b = e.target.closest('.btn'); if (b) { t = b.getAttribute('data-t'); update(); } });
  n.addEventListener('input', update);
  update();
})();
:::

:::notes
{timing: 1.5min}
[요약]
- Auto Mode 관리비는 EC2 요금과 별도, 관리하는 인스턴스의 유형과 시간 기준, 초 단위 과금(최소 1분)
- 구매 옵션과 독립: Spot, RI, Savings Plans 할인이 관리비를 줄이지 않음
- 서울 m5.large 관리비 $0.01416/h vs OD $0.118/h, m7g.large $0.01204/h vs $0.1003/h, 둘 다 OD의 약 12%(계산값)
- 2026-07-01 GPU 관리비 인하: G 35%, P와 Trainium 60%. 조직 150노드 초과는 별도 문의

Auto Mode의 비용 구조는 단순합니다. EC2 요금은 그대로 내고, Auto Mode가 관리하는 인스턴스마다 유형과 시간에 따라 관리비가 추가됩니다. 초 단위 과금이고 최소 1분입니다.
{cue: demo}
왼쪽 계산기로 보겠습니다. 서울 리전 m5.large 20대를 한 달 730시간 돌리면 관리비가 이 정도이고, On-Demand EC2 요금은 이 정도입니다. 아래 줄의 비율을 보시면 약 12%입니다. m7g.large로 바꿔도 비율은 비슷합니다. 다만 이 12%는 AWS가 공시한 퍼센트가 아니라, Price List API의 두 단가를 나눠 제가 계산한 값입니다. AWS는 인스턴스 유형별 단가로만 공시합니다.
{cue: pause}
중요한 것은 오른쪽 노란 박스입니다. 관리비는 EC2 구매 옵션과 독립입니다. Spot이나 Savings Plans로 EC2 비용을 줄여도 관리비는 그대로이니, Spot 비중이 높을수록 EC2 비용 대비 관리비 비율이 커집니다. self-managed는 이 관리비가 없는 대신 Karpenter controller를 돌릴 노드 비용과, 무엇보다 운영 인력의 시간이 듭니다.
GPU는 7월 1일부터 관리비가 G 계열 35%, P 계열과 Trainium 60% 인하되었습니다. 조직 전체로 150노드를 넘으면 별도 가격 문의 안내가 있습니다.

[출처]
- https://aws.amazon.com/eks/pricing/
- aws pricing get-products --service-code AmazonEKS, AmazonEC2 (regionCode ap-northeast-2, 2026-10-20 조회)
- https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-eks-auto-mode-gpu-price/
{cue: transition}
그럼 Savings Plans와 Spot은 어디까지 할인되고, 비용은 어떻게 나눠 볼까요.
:::


---
<!-- Slide 13: 비용 귀속과 약정 -->
@type: content
@title: 비용 귀속: 태그, 약정, 무엇이 할인되나

## 비용 귀속: 태그, 약정, 무엇이 할인되나

:::html
<style>
.ak3-ca { display: grid; grid-template-columns: 1.1fr 1fr; gap: var(--space-4); align-items: start; }
.ak3-ct { width: 100%; font-size: var(--fs-card); word-break: keep-all; overflow-wrap: anywhere; }
.data-table th { text-transform: none; letter-spacing: normal; font-size: var(--fs-card); }
.ak3-no { color: var(--danger); font-weight: var(--weight-bold); }
.ak3-yes { color: var(--success); font-weight: var(--weight-bold); }
.ak3-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak3-ca">
  <table class="data-table ak3-ct">
    <thead><tr><th>할인 수단</th><th>EC2 요금</th><th>Auto Mode 관리비</th></tr></thead>
    <tbody>
      <tr class="fragment fade-up" data-fragment-index="1"><td>Compute Savings Plans</td><td><span class="ak3-yes">적용</span> (최대 66%)</td><td><span class="ak3-no">미적용</span></td></tr>
      <tr class="fragment fade-up" data-fragment-index="1"><td>EC2 Instance Savings Plans</td><td><span class="ak3-yes">적용</span> (최대 72%)</td><td><span class="ak3-no">미적용</span></td></tr>
      <tr class="fragment fade-up" data-fragment-index="1"><td>Reserved Instances</td><td><span class="ak3-yes">적용</span></td><td><span class="ak3-no">미적용</span></td></tr>
      <tr class="fragment fade-up" data-fragment-index="1"><td>Spot</td><td><span class="ak3-yes">Spot 가격</span> (SP 대상 아님)</td><td><span class="ak3-no">미적용</span></td></tr>
    </tbody>
  </table>
  <div class="ak3-stack">
    <div class="callout callout-info fragment fade-left" data-fragment-index="2"><strong class="text-info">클러스터별 귀속: <code>aws:eks:cluster-name</code></strong><div class="on-surface-muted">AWS가 EC2 인스턴스에 붙이는 태그입니다. Billing에서 cost allocation tag로 활성화해야 보이고, control plane 요금은 포함하지 않습니다.</div></div>
    <div class="callout callout-info fragment fade-left" data-fragment-index="3"><strong class="text-info">관리비만 보려면</strong><div class="on-surface-muted">Cost Explorer에서 usage type이 <code>*EKS-Auto:*-management-hours</code>인 항목으로 거릅니다.</div></div>
    <div class="callout callout-warning fragment fade-left" data-fragment-index="4"><strong class="text-warning">NodePool, 팀 단위는 직접</strong><div class="on-surface-muted">NodeClass <code>tags</code>로 팀 태그를 붙이거나 Kubecost 같은 도구로 Pod requests 기준 배분합니다.</div></div>
  </div>
</div>
:::

:::notes
{timing: 2min}
[요약]
- Savings Plans(Compute 최대 66%, EC2 Instance 최대 72%), RI, Spot은 EC2 요금만 할인. Auto Mode 관리비는 구매 옵션과 독립
- 클러스터 귀속 태그는 aws:eks:cluster-name(EC2에 AWS가 부착), Billing에서 활성화 필요, control plane 제외
- 관리비만 보려면 Cost Explorer usage type *EKS-Auto:*-management-hours(예: APN2-EKS-Auto:m5.large-management-hours)로 필터
- NodePool이나 팀 단위는 NodeClass tags나 Kubecost 같은 도구로

앞 장에서 관리비는 할인되지 않는다고 했는데, 표로 정리하면 이렇습니다. Compute Savings Plans는 최대 66%, EC2 Instance Savings Plans는 최대 72%까지 EC2 요금을 줄이고, RI도 EC2 요금에만 적용됩니다. Spot은 Spot 가격으로 나가고 Savings Plans 대상이 아닙니다. 네 경우 모두 Auto Mode 관리비는 그대로입니다.
{cue: pause}
그럼 클러스터별 비용은 어떻게 나눌까요. AWS가 EC2 인스턴스에 aws:eks:cluster-name 태그를 붙여 줍니다. eks:cluster-name이 아니라 aws: 접두사가 붙은 이름이고, Billing 콘솔에서 cost allocation tag로 활성화해야 Cost Explorer에 보입니다. control plane 요금은 이 태그에 포함되지 않습니다.
관리비만 따로 보고 싶으면 Cost Explorer에서 usage type에 EKS-Auto가 들어간 management-hours 항목으로 거르면 됩니다. 서울이면 APN2-EKS-Auto 뒤에 인스턴스 유형이 붙는 형태입니다.
{cue: question}
NodePool이나 팀 단위로 나누려면 어떻게 할까요. AWS가 자동으로 주는 태그는 클러스터까지입니다. NodeClass의 tags로 팀 태그를 붙이거나, Kubecost 같은 도구로 Pod requests 기준으로 배분합니다. tags를 쓸 때는 앞에서 본 것처럼 클러스터 역할의 태깅 권한을 먼저 확인하세요.

[출처]
- https://aws.amazon.com/eks/pricing/ (구매 옵션과 독립)
- https://aws.amazon.com/savingsplans/compute-pricing/
- https://docs.aws.amazon.com/eks/latest/userguide/eks-using-tags.html (aws:eks:cluster-name)
- https://docs.atomai.click/kubernetes-docs/ko/eks-auto-mode/06-cost-management
{cue: transition}
마지막 주제는 마이그레이션입니다. 기존 클러스터를 Auto Mode로 옮길 때 먼저 바뀌는 것은 이름입니다.
:::

---
<!-- Slide 14: 마이그레이션 1, 바뀌는 이름 -->
@type: content
@title: 마이그레이션 1: 바뀌는 driver 이름

## 마이그레이션 1: 바뀌는 driver 이름

:::html
<style>
.ak3-mg { width: 100%; font-size: var(--fs-card); word-break: keep-all; overflow-wrap: anywhere; margin-bottom: var(--space-3); }
.data-table th { text-transform: none; letter-spacing: normal; font-size: var(--fs-card); }
.ak3-grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); }
.ak3-mt { margin-top: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<table class="data-table ak3-mg">
  <thead><tr><th>리소스</th><th>직접 설치한 controller</th><th>Auto Mode</th></tr></thead>
  <tbody>
    <tr><td>StorageClass provisioner</td><td><code>ebs.csi.aws.com</code></td><td><code>ebs.csi.eks.amazonaws.com</code></td></tr>
    <tr><td>Service <code>loadBalancerClass</code> (NLB)</td><td><code>service.k8s.aws/nlb</code></td><td><code>eks.amazonaws.com/nlb</code></td></tr>
    <tr><td>IngressClass controller (ALB)</td><td><code>ingress.k8s.aws/alb</code></td><td><code>eks.amazonaws.com/alb</code></td></tr>
    <tr><td>TargetGroupBinding, IngressClassParams</td><td><code>elbv2.k8s.aws/v1beta1</code></td><td><code>eks.amazonaws.com/v1</code></td></tr>
    <tr><td>NodeClass</td><td><code>karpenter.k8s.aws/v1</code> EC2NodeClass</td><td><code>eks.amazonaws.com/v1</code> NodeClass</td></tr>
  </tbody>
</table>
<div class="ak3-grid3">
  <div class="card fragment fade-up" data-fragment-index="1"><strong class="text-danger">PVC는 넘어오지 않음</strong><div class="on-surface-muted">다른 provisioner의 볼륨은 마운트할 수 없습니다. snapshot 복원이나 Retain 후 static PV 재생성, AWS의 migration tool을 씁니다.</div></div>
  <div class="card fragment fade-up" data-fragment-index="2"><strong class="text-warning">LB도 인수하지 않음</strong><div class="on-surface-muted">새 LB를 만들고 DNS로 blue/green 전환합니다. 기존 LB controller는 자기 리소스가 남아 있는 동안 유지합니다.</div></div>
  <div class="card fragment fade-up" data-fragment-index="3"><strong class="text-warning">CoreDNS Deployment 유지</strong><div class="on-surface-muted">Auto Mode 노드는 node-local DNS를 씁니다. Auto가 아닌 노드가 남아 있는 동안 기존 CoreDNS를 지우지 않습니다.</div></div>
</div>
:::

:::notes
{timing: 2min}
[요약]
- EBS ebs.csi.aws.com에서 ebs.csi.eks.amazonaws.com, NLB service.k8s.aws/nlb에서 eks.amazonaws.com/nlb, ALB ingress.k8s.aws/alb에서 eks.amazonaws.com/alb, TGB와 IngressClassParams는 eks.amazonaws.com/v1
- Auto Mode는 StorageClass를 만들어 주지 않음. 기존 PVC는 이전되지 않음: snapshot, static PV 재생성, migration tool
- 기존 LB도 인수되지 않음: 새 LB와 DNS blue/green
- 혼합 클러스터에서는 CoreDNS Deployment 유지

마이그레이션의 첫 번째 함정은 이름입니다. Auto Mode의 EBS, NLB, ALB는 기존 add-on과 다른 driver, 다른 class 이름을 씁니다. 표 그대로 StorageClass provisioner, loadBalancerClass, IngressClass controller, TargetGroupBinding의 API 그룹이 모두 eks.amazonaws.com 계열로 바뀝니다. Auto Mode는 StorageClass를 자동으로 만들어 주지 않으니 새 provisioner로 하나 만들고 암호화 같은 옵션도 명시합니다.
{cue: pause}
이름만 바꾸면 끝일까요. 아닙니다. 빨간 카드처럼 기존 PVC는 넘어오지 않습니다. 다른 provisioner가 만든 볼륨은 마운트할 수 없어서, snapshot으로 복원하거나 Retain으로 두고 static PV를 다시 만드는 절차가 필요합니다. AWS가 EBS 마이그레이션 도구도 제공합니다.
Load Balancer도 마찬가지로 인수되지 않습니다. 새 LB를 만들어 검증하고 DNS로 blue/green 전환한 뒤 기존 것을 정리합니다. 그동안 기존 LB controller는 남겨 둡니다.
마지막으로 CoreDNS입니다. Auto Mode 노드는 node-local DNS를 쓰지만, Auto가 아닌 노드가 남아 있는 동안에는 기존 CoreDNS Deployment가 필요합니다.

[출처]
- https://docs.aws.amazon.com/eks/latest/userguide/migrate-auto.html
- https://docs.aws.amazon.com/eks/latest/userguide/create-storage-class.html
- https://docs.atomai.click/kubernetes-docs/ko/eks-auto-mode/09-migration-guide
{cue: transition}
이름을 정리했으면 노드를 옮길 차례입니다. 관리형 노드 그룹과 self-managed Karpenter에서 옮기는 순서를 보겠습니다.
:::

---
<!-- Slide 15: 마이그레이션 2, 옮기는 순서 -->
@type: content
@title: 마이그레이션 2: 노드를 옮기는 순서

## 마이그레이션 2: 노드를 옮기는 순서

:::html
<style>
.ak3-steps2 { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: var(--space-2); margin-top: var(--space-3); margin-bottom: var(--space-3); }
.ak3-step { border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-3); font-size: var(--fs-caption); word-break: keep-all; overflow-wrap: break-word; }
.ak3-num { display: inline-flex; align-items: center; justify-content: center; width: 1.8em; height: 1.8em; border-radius: 50%; background: var(--accent-subtle); color: var(--accent); font-weight: var(--weight-bold); margin-bottom: var(--space-2); }
.ak3-step strong { display: block; margin-bottom: var(--space-1); font-size: var(--fs-card); }
.ak3-sub { color: var(--text-secondary); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">관리형 노드 그룹에서</button>
  <button class="tab-btn">Self-managed Karpenter에서</button>
</div>
<div class="tc">
  <div class="ak3-steps2">
    <div class="ak3-step"><span class="ak3-num">1</span><strong>built-in 풀 없이 켜기</strong><span class="ak3-sub"><code>nodePools: []</code>. 무제한 general-purpose가 Pending Pod를 먼저 가져가지 않게</span></div>
    <div class="ak3-step"><span class="ak3-num">2</span><strong>NodeClass, 선택적 풀</strong><span class="ak3-sub">default NodeClass가 없으니 직접 만들고 EC2 access entry 추가. taint 건 풀</span></div>
    <div class="ak3-step"><span class="ak3-num">3</span><strong>wave별 이전</strong><span class="ak3-sub">Deployment, GitOps 원본에 toleration과 <code>compute-type: auto</code> selector. 저위험부터</span></div>
    <div class="ak3-step"><span class="ak3-num">4</span><strong>한 대씩 drain</strong><span class="ak3-sub">앱 검증 후 다음 노드. <code>--force</code>, <code>--delete-emptydir-data</code>로 오류를 덮지 않기</span></div>
    <div class="ak3-step"><span class="ak3-num">5</span><strong>비운 뒤 축소, 삭제</strong><span class="ak3-sub">기존 노드가 빈 것을 확인하고 desired 0, 삭제는 원래 IaC로</span></div>
  </div>
  <div class="callout callout-danger fragment fade-up" data-fragment-index="1"><strong class="text-danger">desired size 축소는 drain 단계가 아닙니다</strong>: 어떤 노드를 지울지 ASG가 고릅니다. 노드 그룹 전체를 지울 때는 AWS 기본 경로인 <code>eksctl delete nodegroup</code>이 노드를 drain한 뒤 삭제합니다.</div>
</div>
<div class="tc" hidden>
  <div class="ak3-steps2">
    <div class="ak3-step"><span class="ak3-num">1</span><strong>버전 확인</strong><span class="ak3-sub">Karpenter v1.1 이상, 그리고 현재 K8s 호환 버전 (1.37은 1.15.x)</span></div>
    <div class="ak3-step"><span class="ak3-num">2</span><strong>general-purpose 끄기</strong><span class="ak3-sub">선택적이지 않은 풀이라 공존 중에는 켜지 않습니다.</span></div>
    <div class="ak3-step"><span class="ak3-num">3</span><strong>taint 건 Auto 풀</strong><span class="ak3-sub">워크로드에 toleration과 <code>eks.amazonaws.com/compute-type: auto</code> selector</span></div>
    <div class="ak3-step"><span class="ak3-num">4</span><strong>공유 CRD는 그대로</strong><span class="ak3-sub"><code>nodepools.karpenter.sh</code>, <code>nodeclaims.karpenter.sh</code>를 바꾸거나 지우지 않기</span></div>
    <div class="ak3-step"><span class="ak3-num">5</span><strong>정리 후 uninstall</strong><span class="ak3-sub">기존 controller가 살아 있을 때 자기 NodePool, NodeClaim을 정리. uninstall을 먼저 하지 않기</span></div>
  </div>
  <div class="callout callout-warning fragment fade-up" data-fragment-index="2"><strong class="text-warning">라벨 접두사도 함께</strong>: requirements의 <code>karpenter.k8s.aws/instance-*</code>를 <code>eks.amazonaws.com/instance-*</code>로 바꿉니다. 공존 중에는 양쪽 compute와 LB가 함께 과금됩니다.</div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- MNG: nodePools: []로 켜기, NodeClass와 EC2 access entry 직접 생성, 선택적 taint 풀, wave별 이전, 한 대씩 drain(--force 금지), 비운 뒤 desired 0, 삭제는 원래 IaC
- desired size 축소는 ASG가 지울 노드를 고르는 방식이라 앱 검증 단위 drain을 대신하지 않음. AWS 문서의 기본 경로는 eksctl delete nodegroup(노드 drain 후 삭제)
- Karpenter: v1.1 이상과 현재 호환 버전, general-purpose 끄기, taint 풀과 compute-type: auto selector, 공유 CRD 수정 금지, 기존 controller로 정리 후 uninstall
- 라벨 접두사 변경, 공존 중 이중 과금

노드를 옮기는 순서입니다. 관리형 노드 그룹부터 보겠습니다. 1단계는 built-in 풀 없이, nodePools를 빈 배열로 켜는 것입니다. general-purpose 풀은 조건이 넓어서 켜자마자 Pending Pod를 가져갈 수 있기 때문입니다. 그러면 default NodeClass도 없으니 2단계에서 NodeClass와 노드용 access entry를 만들고, taint를 건 선택적 풀을 만듭니다.
{cue: pause}
3단계부터 워크로드를 옮깁니다. 실행 중인 Pod가 아니라 Deployment나 GitOps 원본에 toleration과 compute-type: auto selector를 넣고, 위험이 낮은 것부터 wave로 옮깁니다. 4단계 drain은 한 대씩, 앱을 확인하고 다음으로 갑니다. 오류가 난다고 force나 delete-emptydir-data를 붙이지 마세요.
빨간 박스가 가장 많이 하는 실수입니다. desired size를 줄이면 어떤 노드를 지울지 ASG가 고르기 때문에, 한 대씩 앱을 확인하며 비우는 drain을 대신하지 못합니다. 그래서 5단계에서는 기존 노드가 완전히 빈 것을 확인한 뒤에 desired를 0으로 두고, 삭제는 원래 만든 Terraform이나 eksctl로 합니다. AWS 문서의 기본 경로는 eksctl delete nodegroup이고, 이 명령이 노드를 drain한 뒤 노드 그룹을 지웁니다. 위 다섯 단계는 kubernetes-docs 마이그레이션 가이드의 순서입니다.
{cue: demo}
두 번째 탭은 self-managed Karpenter에서 옮길 때입니다. AWS는 두 controller를 나란히 두고 옮기는 방법을 안내합니다. Karpenter v1.1 이상이 조건이고, 1.37이라면 이미 1.15.x일 것입니다. general-purpose 풀은 켜지 말고, taint 건 Auto 풀로 워크로드를 골라 옮깁니다. 두 controller가 nodepools.karpenter.sh와 nodeclaims.karpenter.sh CRD를 공유하니 이 CRD는 건드리지 않습니다. 마지막으로 기존 controller가 살아 있을 때 자기 NodePool과 NodeClaim을 정리하게 한 뒤 uninstall합니다. 먼저 지우면 finalizer를 처리할 controller가 없어 정리가 끝나지 않을 수 있습니다.

[출처]
- https://docs.aws.amazon.com/eks/latest/userguide/auto-migrate-mng.html (eksctl delete nodegroup 경로)
- https://docs.aws.amazon.com/eks/latest/userguide/auto-migrate-karpenter.html
- https://docs.aws.amazon.com/eks/latest/userguide/create-node-pool.html (nodePools 빈 배열)
- https://docs.atomai.click/kubernetes-docs/ko/eks-auto-mode/09-migration-guide (다섯 단계, wave 이전, 단일 노드 drain)
{cue: transition}
여기까지 Auto Mode 운영에 필요한 내용을 모두 봤습니다. 이제 무엇을 고를지 체크리스트로 정리하겠습니다.
:::

---
<!-- Slide 16: 선택 체크리스트 -->
@type: content
@title: Auto Mode인가, 직접 운영인가

## Auto Mode인가, 직접 운영인가

:::html
<style>
.ak3-dec { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); align-items: start; }
.ak3-dec h4 { margin: 0 0 var(--space-2); font-size: var(--fs-body); }
.ak3-dec .checklist { font-size: var(--fs-card); word-break: keep-all; }
.ak3-tally { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3); margin-top: var(--space-3); }
.ak3-tally .metric-value { font-size: var(--fs-subtitle); }
.ak3-verdict { margin-top: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="ak3-dec" id="ak3-dec">
  <div>
    <h4 class="text-accent">직접 운영 쪽 신호</h4>
    <ul class="checklist">
      <li data-side="self"><span class="check"></span><span class="checklist-text">custom AMI, userData, launch template, SSH나 SSM 접속이 필요</span></li>
      <li data-side="self"><span class="check"></span><span class="checklist-text">kubelet, sysctl 요구가 <code>advancedCompute</code> 지원 필드를 벗어남</span></li>
      <li data-side="self"><span class="check"></span><span class="checklist-text">Windows 노드, DRA, 대체 CNI 필요 (Security Groups per Pod는 podSecurityGroupSelectorTerms로 대체)</span></li>
      <li data-side="self"><span class="check"></span><span class="checklist-text">feature gate 기능이나 FIS EC2 장애 주입 테스트가 필요</span></li>
    </ul>
  </div>
  <div>
    <h4 class="text-accent">Auto Mode 쪽 신호</h4>
    <ul class="checklist">
      <li data-side="auto"><span class="check"></span><span class="checklist-text">Karpenter minor마다 CRD와 breaking change를 따라갈 인력이 부족</span></li>
      <li data-side="auto"><span class="check"></span><span class="checklist-text">CNI, CoreDNS, EBS CSI, LB controller 운영을 줄이고 싶음</span></li>
      <li data-side="auto"><span class="check"></span><span class="checklist-text">주간 AMI 교체와 21일 수명 상한을 보안 기준으로 받아들일 수 있음</span></li>
      <li data-side="auto"><span class="check"></span><span class="checklist-text">인스턴스당 관리비가 운영 시간 절감보다 작다고 판단</span></li>
    </ul>
  </div>
</div>
<div class="ak3-tally">
  <div class="metric-card"><div class="metric-value" id="ak3-self">0</div><div class="metric-label">직접 운영 신호</div></div>
  <div class="metric-card"><div class="metric-value" id="ak3-auto">0</div><div class="metric-label">Auto Mode 신호</div></div>
</div>
<div class="callout callout-info ak3-verdict fragment fade-up" data-fragment-index="1"><strong class="text-info">왼쪽이 하나라도 필수라면</strong>: 그 워크로드는 self-managed가 맞습니다. 클러스터를 나누거나, 마이그레이션 중에만 NodePool로 분리해 공존합니다.</div>
:::

:::script
(function () {
  var root = document.getElementById('ak3-dec');
  if (!root) return;
  function count() {
    document.getElementById('ak3-self').textContent = root.querySelectorAll('li.checked[data-side="self"]').length;
    document.getElementById('ak3-auto').textContent = root.querySelectorAll('li.checked[data-side="auto"]').length;
  }
  root.addEventListener('click', function (e) {
    if (e.target.closest('.checklist li')) setTimeout(count, 0);
  });
  count();
})();
:::

:::notes
{timing: 2min}
[요약]
- 직접 운영 신호: custom AMI, userData, SSH/SSM, advancedCompute 범위를 넘는 kubelet과 sysctl, Windows, DRA, 대체 CNI, SG per Pod, feature gate, FIS EC2 action
- Auto Mode 신호: Karpenter minor 추적 인력 부족(v1.15는 LTS 아님), 관리형 CNI, CoreDNS, EBS CSI, LBC 선호, 주간 AMI와 21일 상한 수용, 관리비 대비 운영 절감
- 왼쪽 항목이 하나라도 필수면 그 워크로드는 self-managed. AWS는 한 클러스터에서 한쪽을 권장
- 다음은 데모 영상 4편

마지막으로 선택 기준입니다. 항목을 클릭하면 체크되고 아래에 개수가 올라갑니다. 우리 조직 상황에 맞춰 같이 눌러 보겠습니다.
{cue: demo}
왼쪽은 직접 운영해야 하는 신호입니다. custom AMI, userData, launch template, SSH나 SSM 접속이 필요하거나, kubelet과 sysctl 요구가 advancedCompute 목록을 벗어나면 직접 운영입니다. Windows 노드, DRA, Cilium 같은 대체 CNI도 지원하지 않고, Security Groups per Pod 대신 NodeClass의 podSecurityGroupSelectorTerms를 씁니다. feature gate나 FIS EC2 장애 주입이 필요해도 직접 운영입니다.
{cue: pause}
오른쪽은 Auto Mode 쪽 신호입니다. 2부 버전 지도에서 본 것처럼 1.37은 LTS가 아닌 Karpenter 1.15.x가 필요하니, minor마다 따라갈 인력이 부족하면 이 부담을 AWS에 넘기는 것이 합리적입니다. 애드온 운영을 줄이고 싶을 때, 주간 AMI 교체와 21일 수명 상한을 보안 기준으로 받아들일 수 있을 때, 관리비가 운영 시간 절감보다 작을 때도 Auto Mode 쪽입니다.
{cue: question}
결론은 간단합니다. 왼쪽 항목 중 하나라도 반드시 필요하다면 그 워크로드는 self-managed가 맞습니다. 이때도 한 클러스터 안에 둘을 오래 섞기보다 클러스터를 나누고, 마이그레이션 중에만 NodePool로 분리해 공존하는 것이 AWS 권장입니다.

[출처]
- https://docs.aws.amazon.com/eks/latest/userguide/create-node-class.html (advancedCompute 필드)
- https://docs.aws.amazon.com/eks/latest/userguide/auto-networking.html (미지원 네트워킹 기능)
- https://docs.aws.amazon.com/eks/latest/userguide/automode-learn-instances.html (FIS 미지원, 공존 시 NodePool 분리)
{cue: transition}
지금까지 이론으로 본 프로비저닝, consolidation, Drift, Spot 중단을 이제 데모 영상으로 직접 확인해 보겠습니다. 영상은 네 편이고, 각 영상 앞에서 무엇을 보면 되는지 짚고 넘어가겠습니다.
:::

