---
remarp: true
block: 03-node-lifecycle
---

---
<!-- Slide 1: 블록 커버 -->
@type: section

# Block 3 — 노드 부트스트랩 & 라이프사이클

사전 준비 → nodeadm → Cilium → 업그레이드 → 트러블슈팅 → 크리덴셜

:::notes
{timing: 0.5min}
[요약]
• Block 3은 "호스트 한 대를 EKS 노드로 만들고, 그 뒤 수명 주기를 관리하는 방법"입니다
• 흐름: 사전 준비 → nodeadm 설치/초기화 → Cilium → 튜닝 → 업그레이드 → 장애 대응 → 크리덴셜
• 모든 명령과 YAML은 검토한 로컬 문서(nodeadm v1.0.20 기준)에서 가져왔습니다

지금까지 Block 1, 2에서 아키텍처와 네트워크를 봤습니다. 이제 실제로 서버 한 대를 클러스터에 붙이는 과정을 순서대로 따라가 보겠습니다.
{cue: pause}
먼저 조인 전에 AWS 쪽에서 끝내야 할 준비부터 보겠습니다.
:::

---
<!-- Slide 2: 사전 준비 (Tabs) -->
@type: tabs
@title: 조인 전에 끝낼 AWS 사전 준비

## 조인 전에 끝낼 AWS 사전 준비

::::tab "Access Entry"
노드 IAM 역할에 **HYBRID_LINUX** 타입 access entry를 만듭니다. 일반 SSM 관리 역할만으로는 조인되지 않습니다.

```json
{
  "clusterName": "my-hybrid-cluster",
  "principalArn": "arn:aws:iam::123456789012:role/EKSHybridNodeRole",
  "type": "HYBRID_LINUX"
}
```

- 매핑은 `system:node:{{SessionName}}` + node-bootstrap 그룹 사용
- 기존 mapping을 지우는 한-role `aws-auth` ConfigMap은 적용하지 않기
::::

::::tab "eksctl remoteNetworkConfig"
클러스터 생성 시 원격 노드/Pod CIDR을 선언합니다. 기존 클러스터에도 remote network 구성을 추가할 수 있습니다.

```yaml
# ClusterConfig 중 hybrid 관련 부분
remoteNetworkConfig:
  iam:
    provider: SSM
    roleARN: arn:aws:iam::123456789012:role/EKSHybridNodeRole
  vpcGatewayID: tgw-0123456789abcdef0
  remoteNodeNetworks:
  - cidrs:
    - 10.80.0.0/16
  remotePodNetworks:
  - cidrs:
    - 10.85.0.0/16
```

- CIDR은 IPv4, 종류별 최대 15개, RFC1918 또는 CGNAT(100.64.0.0/10)
::::

::::tab "IAM 역할"
**AmazonEKSWorkerNodeMinimalPolicy만으로는 `eks:DescribeCluster` 권한이 없습니다.** 역할에 직접 추가합니다.

```json
{
  "Effect": "Allow",
  "Action": "eks:DescribeCluster",
  "Resource": "arn:aws:eks:ap-northeast-2:123456789012:cluster/my-hybrid-cluster"
}
```

- SSM: ECR pull + SSM core + 등록 해제 권한 (`ssm:DeregisterManagedInstance`)
- IAM Roles Anywhere: 프로필에 `acceptRoleSessionName: true`
- Pod Identity는 `eks-auth:AssumeRoleForPodIdentity`를 별도로 부여
::::

:::notes
{timing: 2min}
[요약]
• 조인 전 필수 3가지: HYBRID_LINUX access entry, remoteNetworkConfig, Hybrid Nodes IAM 역할
• MinimalPolicy에는 eks:DescribeCluster가 없어서 역할에 직접 붙여야 합니다
• remoteNetworkConfig는 기존 클러스터에도 추가 가능

탭을 순서대로 보겠습니다. 첫 번째는 access entry입니다. 노드 IAM 역할에 HYBRID_LINUX 타입으로 만들어야 하고, 일반 SSM 관리 역할만으로는 충분하지 않습니다.
{cue: pause}
두 번째는 eksctl의 remoteNetworkConfig입니다. 원격 노드 CIDR과 Pod CIDR을 선언하는데, 둘 다 IPv4이고 각각 최대 15개, RFC1918이나 CGNAT 대역이어야 합니다. 예전 문서에는 클러스터 생성 시에만 가능하다고 되어 있었지만, 지금은 기존 클러스터에도 remote network 구성을 추가할 수 있습니다.
{cue: question}
세 번째가 현장에서 가장 많이 놓치는 부분입니다. AmazonEKSWorkerNodeMinimalPolicy를 붙였는데 왜 조인이 안 되나요? 이 정책에는 DescribeCluster가 없기 때문입니다. nodeadm이 엔드포인트와 CA를 조회할 때 이 권한을 씁니다.
{cue: transition}
준비가 끝났다면 이제 노드 쪽 도구인 nodeadm을 보겠습니다.

[출처]
• D/01 prerequisites (access entry, DescribeCluster, eksctl remoteNetworkConfig 섹션)
:::

---
<!-- Slide 3: nodeadm 개요 -->
@type: content
@title: nodeadm: 명령은 여섯 개뿐

## nodeadm: 명령은 여섯 개뿐

:::html
<style>
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="card-grid" data-reveal="stagger" data-reveal-pace="fast">
  <div class="metric-card"><strong class="text-accent">install</strong><div class="on-surface-muted">kubelet, containerd, SSM agent 등 의존성 설치</div></div>
  <div class="metric-card"><strong class="text-accent">config check</strong><div class="on-surface-muted">로컬 NodeConfig 검사 (조인 시험 아님)</div></div>
  <div class="metric-card"><strong class="text-accent">init</strong><div class="on-surface-muted">호스트 구성 + EKS 조인</div></div>
  <div class="metric-card"><strong class="text-accent">upgrade</strong><div class="on-surface-muted">in-place 버전 변경 (중단 작업)</div></div>
  <div class="metric-card"><strong class="text-accent">uninstall</strong><div class="on-surface-muted">구성 요소 제거 + SSM 등록 해제</div></div>
  <div class="metric-card"><strong class="text-accent">debug</strong><div class="on-surface-muted">AWS/클러스터 연결·자격 증명 진단</div></div>
</div>
<div class="callout callout-info fragment fade-up" data-fragment-index="2"><strong class="text-info">v1.0.20</strong> — 저장소 <code>aws/eks-hybrid</code> (EC2용 amazon-eks-ami의 nodeadm과 다름). SSM 신규 설치·업그레이드는 <strong>1.0.19 이상</strong> 필요.</div>
<div class="callout callout-warning fragment zoom-in" data-fragment-index="1"><strong class="text-warning">없는 것</strong> — <code>upgrade --rollback</code>, <code>reset</code>, <code>init --dry-run</code>은 존재하지 않습니다.</div>
:::

```bash
# releases/latest 대신 승인한 릴리스를 받고 체크섬을 검증한 뒤 설치
printf '%s  %s\n' "$NODEADM_SHA256" "$STAGING_DIR/nodeadm" | sha256sum --check -
sudo install -m 0755 "$STAGING_DIR/nodeadm" /usr/local/bin/nodeadm
```


:::notes
{timing: 1.5min}
[요약]
• 현재 nodeadm은 v1.0.20, 저장소는 aws/eks-hybrid
• 명령: install, config check, init, upgrade, uninstall, debug
• rollback, reset, init --dry-run은 없다
• releases/latest 대신 버전을 고정하고 checksum을 검증

nodeadm 명령은 여섯 개입니다. install, config check, init, upgrade, uninstall, debug입니다. 제한망 설치는 별도 명령이 아니라 install과 init의 manifest-override, private-mode 옵션으로 처리하며 뒤에서 다룹니다.
{cue: pause}
자주 받는 질문이 롤백 명령이 있느냐, reset이 있느냐, 드라이런이 있느냐인데요, 세 가지 모두 없습니다. 업그레이드가 잘못되면 어떻게 하는지는 뒤에서 따로 말씀드리겠습니다.
설치할 때는 최신 릴리스를 그냥 받지 마시고, 승인한 버전을 고정하고 체크섬을 대조한 뒤 설치하세요. SSM 공급자를 쓰신다면 1.0.19 이상이어야 합니다. 오래된 SSM 서명 키 문제 때문입니다.
{cue: transition}
그럼 이 명령들이 실제로 어떤 순서로 실행되는지 보겠습니다.

[출처]
• D/04 nodeadm 섹션, D/09 설치 단계, AWS hybrid-nodes-nodeadm 문서
:::

---
<!-- Slide 4: 부트스트랩 워크플로우 -->
@type: content
@title: 부트스트랩은 다섯 걸음

## 부트스트랩은 다섯 걸음

:::html
<style>
.hn-boot { display: grid; grid-template-columns: repeat(5, 1fr); gap: var(--space-3); }
.hn-boot-no { display: inline-block; min-width: 1.6em; margin-right: var(--space-2); text-align: center; border-radius: 50%; background: var(--accent); color: var(--surface-1); font-weight: var(--weight-bold); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="hn-boot">
  <div class="card fragment fade-right" data-fragment-index="1"><span class="hn-boot-no">1</span><strong class="text-accent">install</strong><div class="on-surface-muted">kubelet, containerd 등 의존성 설치. 등록은 하지 않음</div></div>
  <div class="card fragment fade-right" data-fragment-index="2"><span class="hn-boot-no">2</span><strong class="text-accent">config check</strong><div class="on-surface-muted">NodeConfig 로컬 검사. 통과해도 조인을 보증하지 않음 (dry-run 아님)</div></div>
  <div class="card fragment fade-right" data-fragment-index="3"><span class="hn-boot-no">3</span><strong class="text-accent">init</strong><div class="on-surface-muted">호스트 구성, SSM 등록 등 자격 증명 설정, EKS 조인</div></div>
  <div class="card fragment fade-right" data-fragment-index="4"><span class="hn-boot-no">4</span><strong class="text-warning">CNI</strong><div class="on-surface-muted">CNI 설치 전까지 Node가 NotReady인 것은 정상일 수 있음</div></div>
  <div class="card fragment fade-right" data-fragment-index="5"><span class="hn-boot-no">5</span><strong class="text-success">Ready 검증</strong><div class="on-surface-muted">노드 UID 대조, 라벨, DNS, 이미지 풀, 자격 증명 갱신</div></div>
</div>
<div class="callout callout-info fragment zoom-in" data-fragment-index="6"><strong class="text-accent">Ready는 필요 조건일 뿐</strong> — 실제 워크로드까지 확인한 뒤에 서비스에 투입합니다.</div>
:::

:::notes
{timing: 2min}
[요약]
• install은 소프트웨어만, SSM 등록과 조인은 init에서
• config check는 로컬 검사일 뿐 조인 보증이 아님
• CNI 없이는 NotReady가 정상일 수 있음
• Ready는 필요 조건일 뿐 충분 조건이 아님

방향키로 한 단계씩 넘겨 보겠습니다. install은 소프트웨어를 깔 뿐입니다. kubelet, containerd, ECR credential provider, SSM setup CLI를 설치하고, SSM 등록 자체는 init에서 일어납니다.
{cue: pause}
config check는 로컬 설정 검사입니다. 통과했다고 조인이 된다는 뜻은 아닙니다. 그래서 dry-run이 없다는 점을 기억해 두셔야 합니다.
init에서 호스트가 구성되고 EKS에 조인합니다. 그런데 이 시점에 Node가 NotReady인 것은 이상한 일이 아닙니다. CNI가 아직 없기 때문입니다.
{cue: question}
Node가 Ready가 되면 끝일까요? 아닙니다. 실제 노드 UID를 호스트와 대조하고, DNS, 이미지 풀, 자격 증명 갱신, 그리고 실제 워크로드까지 확인해야 서비스에 투입할 수 있습니다.
{cue: transition}
init의 입력이 되는 NodeConfig를 살펴보겠습니다.

[출처]
• D/04 "부트스트랩 흐름", "초기화와 확인" 섹션
:::

---
<!-- Slide 5: NodeConfig 탭 -->
@type: tabs
@title: NodeConfig는 공급자 하나로 충분

## NodeConfig는 공급자 하나로 충분

::::tab "SSM"
```yaml
apiVersion: node.eks.aws/v1alpha1
kind: NodeConfig
spec:
  cluster:
    name: my-hybrid-cluster
    region: ap-northeast-2
  hybrid:
    ssm:
      activationCode: REPLACE_WITH_ACTIVATION_CODE
      activationId: REPLACE_WITH_ACTIVATION_ID
  kubelet:
    config:
      maxPods: 110
    flags:
      - --node-labels=example.com/location=onprem
```
파일은 root 소유 `0600`으로 보호하고 활성화 코드를 로그에 남기지 않습니다. 등록 후 Node 이름은 `mi-*`입니다.
::::

::::tab "IAM Roles Anywhere"
```yaml
apiVersion: node.eks.aws/v1alpha1
kind: NodeConfig
spec:
  cluster:
    name: my-hybrid-cluster
    region: ap-northeast-2
  hybrid:
    iamRolesAnywhere:
      nodeName: hybrid-node-001
      trustAnchorArn: arn:aws:rolesanywhere:ap-northeast-2:123456789012:trust-anchor/REPLACE_ID
      profileArn: arn:aws:rolesanywhere:ap-northeast-2:123456789012:profile/REPLACE_ID
      roleArn: arn:aws:iam::123456789012:role/EKSHybridNodeRole
      certificatePath: /etc/iam/pki/server.pem
      privateKeyPath: /etc/iam/pki/server.key
```
::::

::::tab "최소 구성"
- 필수 입력은 **클러스터 이름 + 리전 + 공급자 블록**
- API 엔드포인트, CA, CIDR은 직접 쓰지 않습니다. 역할의 `eks:DescribeCluster`로 nodeadm이 조회합니다
- IAM Roles Anywhere는 `nodeName`, `certificatePath`, `privateKeyPath`가 추가로 필요
- `nodeName`은 인증서 CN과 역할 신뢰 정책 조건에 묶이며 최대 64자
- 인증서 하나를 여러 머신에 재사용하지 않습니다
::::

:::notes
{timing: 2min}
[요약]
• 공급자는 SSM 또는 IAM Roles Anywhere 중 정확히 하나
• 최소 구성은 cluster name + region + 공급자 정보
• endpoint/CA는 DescribeCluster로 자동 조회 — NodeConfig에 필수가 아님
• IRA는 nodeName, certificatePath, privateKeyPath 필요

SSM 탭부터 보겠습니다. 클러스터 이름, 리전, 그리고 활성화 코드와 ID가 핵심입니다. kubelet 섹션의 maxPods와 라벨은 선택입니다. 이 파일에는 비밀이 들어 있으니 0600으로 보호해야 합니다.
{cue: pause}
IAM Roles Anywhere 탭에는 nodeName과 인증서, 개인 키 경로가 추가됩니다. nodeName은 역할 신뢰 정책의 인증서 CN 조건과 연결됩니다.
{cue: question}
마지막 탭이 중요합니다. 예전 자료에는 apiServerEndpoint와 CA를 NodeConfig에 꼭 넣어야 하는 것처럼 나와 있습니다. 실제로는 클러스터 이름과 리전만 있으면 됩니다. 역할에 DescribeCluster 권한이 있으면 nodeadm이 알아서 가져옵니다. 앞에서 그 권한을 강조한 이유가 여기 있습니다.
{cue: transition}
다음은 nodeadm을 쓰지 않는 예외, Bottlerocket입니다.

[출처]
• D/04 "NodeConfig와 자격 증명" 섹션
:::

---
<!-- Slide 6: Bottlerocket -->
@type: content
@layout: two-column
@title: Bottlerocket은 nodeadm이 없다

## Bottlerocket은 nodeadm이 없다

::: left
:::html
<style>
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="on-surface-muted fragment fade-up" data-fragment-index="1"><strong class="text-accent">범위</strong> VMware variant · x86_64 · OS 1.37.0+ (vSphere 전용)<br><strong class="text-accent">방식</strong> settings.toml + <code>eks-hybrid-setup</code> bootstrap container, <code>guestinfo.userdata.encoding=base64</code></div>
<div class="on-surface-muted fragment fade-up" data-fragment-index="1">오른쪽은 공통 조각입니다. 공급자별 설정은 AWS 가이드에서 조합하고, <code>api-server</code>·CA는 자동 조회되지 않으므로 직접 기입합니다.</div>
<div class="callout callout-warning fragment fade-up" data-fragment-index="2"><strong class="text-warning">주의</strong> — base64는 암호화가 아닙니다. 활성화 비밀과 개인 키가 들어갈 수 있으니 VM 구성·guestinfo를 보호하고, 등록된 VM을 템플릿으로 복제하지 않습니다.</div>
:::
:::

::: right
```toml
[settings.kubernetes]
cluster-name = "my-hybrid-cluster"
api-server = "https://REPLACE_WITH_CLUSTER_ENDPOINT"
cluster-certificate = "REPLACE_WITH_BASE64_CLUSTER_CA"
hostname-override = "hybrid-node-001"
provider-id = "eks-hybrid:///ap-northeast-2/my-hybrid-cluster/hybrid-node-001"
authentication-mode = "aws"
cloud-provider = ""
server-tls-bootstrap = true
[settings.aws]
region = "ap-northeast-2"
[settings.kubernetes.node-labels]
"eks.amazonaws.com/compute-type" = "hybrid"
[settings.bootstrap-containers.eks-hybrid-setup]
mode = "always"
user-data = "REPLACE_WITH_BASE64_PROVIDER_BOOTSTRAP_INPUT"
```
:::


:::notes
{timing: 1.5min}
[요약]
• Bottlerocket은 nodeadm을 쓰지 않고 settings.toml과 bootstrap container로 부트스트랩
• VMware variant만 지원, OS 1.37.0 이상
• guestinfo로 base64 user-data 전달 — 암호화가 아님
• 이전에 돌던 [settings.hybrid.ssm] 예제는 유효한 계약이 아님

Bottlerocket은 완전히 다른 경로입니다. nodeadm이 없고, settings.toml과 eks-hybrid-setup이라는 bootstrap container가 그 역할을 합니다. 지원 대상은 VMware variant, x86_64, OS 1.37.0 이상으로 vSphere 환경에 한정됩니다.
{cue: pause}
VM을 처음 켜기 전에 settings.toml을 base64로 인코딩해서 guestinfo로 넣습니다. 여기서 base64는 인코딩일 뿐입니다. 활성화 비밀이나 개인 키가 들어가니까 VM 구성과 provisioning 로그를 보호하셔야 합니다.
공급자별 전체 설정은 AWS Bottlerocket 가이드를 그대로 따라 주세요. 슬라이드의 조각은 공통 부분만 보여 드린 것입니다. 이전 자료의 settings.hybrid.ssm 형태는 문서화된 계약이 아닙니다.
{cue: transition}
이제 nodeadm 경로로 돌아와서 containerd 규칙을 보겠습니다.

[출처]
• D/04 "Bottlerocket은 별도 부트스트랩 계약 사용" 섹션
• https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-bottlerocket.html
:::

---
<!-- Slide 7: containerd 소스 -->
@type: content
@title: containerd 소스는 OS가 정한다

## containerd 소스는 OS가 정한다

:::html
<style>
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="callout callout-success"><strong class="text-success">Ubuntu / AL2023</strong><div class="on-surface-muted"><code>distro</code> (기본)</div></div>
  <div class="callout callout-info"><strong class="text-info">RHEL</strong><div class="on-surface-muted"><code>docker</code> 또는 <code>none</code> — <code>distro</code>는 무효</div></div>
  <div class="callout callout-danger"><strong class="text-danger">AL2023</strong><div class="on-surface-muted"><code>docker</code> 사용 불가</div></div>
  <div class="callout callout-warning"><strong class="text-warning">none</strong><div class="on-surface-muted">containerd 설치를 건너뜀 — 미리 설치·관리해야 함</div></div>
</div>
:::

```bash
sudo nodeadm install "$KUBERNETES_VERSION" \
  --credential-provider "$CREDENTIAL_PROVIDER" \
  --containerd-source "$CONTAINERD_SOURCE" --region "$REGION" --timeout 20m
```


:::notes
{timing: 1.5min}
[요약]
• --containerd-source는 distro, docker, none 중 하나
• Ubuntu/AL2023은 distro, RHEL은 docker 또는 none
• AL2023은 docker 불가, RHEL은 distro 불가
• private mode도 OS 패키지를 건너뛰므로 런타임을 대신 설치해 주지 않음

OS별 규칙을 카드로 정리했습니다. Ubuntu와 AL2023은 기본값인 distro를 씁니다. RHEL은 distro가 지원되지 않아서 Docker 패키지 소스를 쓰거나, containerd를 미리 설치하고 none을 선택합니다. AL2023은 반대로 docker를 쓸 수 없습니다.
{cue: pause}
none은 containerd 설치를 건너뛴다는 뜻입니다. 그리고 뒤에서 볼 private mode도 OS 패키지 설치를 건너뜁니다. 그래서 제한망에서는 런타임과 systemd unit을 이미지에 미리 넣어 두어야 합니다.
Kubernetes 버전은 새 노드라면 컨트롤 플레인의 현재 마이너를 우선하세요.
{cue: transition}
이런 설치를 수십 대에 반복하려면 이미지로 만드는 편이 낫습니다. 베어메탈 이미지 빌드를 보겠습니다.

[출처]
• D/04 "nodeadm과 의존성 설치" 섹션, D/09 RHEL containerd 주의사항
:::

---
<!-- Slide 8: 베어메탈 이미지 -->
@type: content
@title: 베어메탈은 이미지로 찍어낸다

## 베어메탈은 이미지로 찍어낸다

:::html
<style>
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="card-grid" data-reveal="stagger">
  <div class="metric-card"><strong class="text-accent">Packer</strong><div class="on-surface-muted"><code>hybrid-nodes-template.pkr.hcl</code> — vSphere OVA, QEMU qcow2/raw</div></div>
  <div class="metric-card"><strong class="text-accent">Ubuntu Autoinstall</strong><div class="on-surface-muted">Subiquity YAML(cloud-init). 디스크는 승인한 serial로만 지정</div></div>
  <div class="metric-card"><strong class="text-accent">RHEL Kickstart</strong><div class="on-surface-muted"><code>ignoredisk</code>와 <code>clearpart</code>를 같은 디스크로 제한</div></div>
</div>
<div class="callout callout-warning fragment zoom-in" data-fragment-index="1"><strong class="text-warning">K8S_VERSION 검증</strong> — v1.0.20 템플릿은 1.26–1.31만 허용합니다. 템플릿 때문에 버전을 낮추지 말고 검토한 포크를 유지하세요.</div>
:::

```bash
export NODEADM_ARCH=amd        # amd/arm (뒤에 64가 붙음)
export CREDENTIAL_PROVIDER=ssm # ssm/iam (iam은 nodeadm의 iam-ra로 변환)
export PACKER_OUTPUT_FORMAT=raw
packer validate -syntax-only hybrid-nodes-template.pkr.hcl
```


:::notes
{timing: 1.5min}
[요약]
• 세 가지 방식: Packer 템플릿, Ubuntu Autoinstall, RHEL Kickstart
• Packer 변수: NODEADM_ARCH(amd/arm), CREDENTIAL_PROVIDER(ssm/iam), PACKER_OUTPUT_FORMAT(raw/qcow2)
• v1.0.20 템플릿의 K8S_VERSION 검증은 1.26–1.31만 허용
• 노드별 신원(활성화 코드, 개인 키, SSM 등록 상태)은 이미지에 넣지 않음

베어메탈 서버는 이미지로 찍어내는 방법이 가장 재현성이 좋습니다. AWS가 예제 Packer 템플릿을 제공하고, 파일 이름은 hybrid-nodes-template.pkr.hcl입니다. 예전에 쓰던 bare-metal-template 이름은 실제 파일이 아닙니다.
{cue: pause}
주의할 점 두 가지입니다. 첫째, NODEADM_ARCH는 amd 또는 arm이고 템플릿이 뒤에 64를 붙입니다. amd64라고 쓰면 amd6464가 됩니다. 둘째, v1.0.20 템플릿의 K8S_VERSION 검증은 아직 1.26부터 1.31만 허용합니다. 그래서 이 템플릿이 최신 EKS 버전을 바로 빌드해 주는 파이프라인은 아니라는 점을 알고 쓰셔야 합니다.
Autoinstall과 Kickstart는 디스크를 지우는 설정이라서 승인한 디스크 식별자만 지정하세요. 그리고 어떤 방식이든 이미지에 활성화 코드나 개인 키, 등록된 SSM 상태를 넣으면 안 됩니다. 노드별로 따로 전달합니다.
{cue: transition}
이제 노드가 붙었으니 네트워킹, Cilium을 설치하겠습니다.

[출처]
• D/09 "AWS Packer 템플릿", "Ubuntu LTS", "RHEL 9" 섹션; D/01 "Packer Image 준비"
:::

---
<!-- Slide 9: Cilium 설치 -->
@type: tabs
@title: Cilium: 하이브리드 노드에만 설치

## Cilium: 하이브리드 노드에만 설치

::::tab "values: agent·IPAM"
```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: eks.amazonaws.com/compute-type
              operator: In
              values: [hybrid]
ipam:
  mode: cluster-pool
  operator:
    clusterPoolIPv4MaskSize: 25
    clusterPoolIPv4PodCIDRList: [10.85.0.0/16]
```
::::

::::tab "values: operator·기타"
```yaml
operator:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: eks.amazonaws.com/compute-type
                operator: In
                values: [hybrid]
  unmanagedPodWatcher:
    restart: false
envoy:
  enabled: false
kubeProxyReplacement: "false"
```
::::

::::tab "설치·버전"
```bash
helm install cilium oci://public.ecr.aws/eks/cilium/cilium \
  --version "$CILIUM_VERSION" --namespace kube-system \
  --values cilium-values.yaml --wait --timeout 10m
```
- **AWS 지원 범위는 AWS 유지 관리 빌드**(`oci://public.ecr.aws/eks/cilium/cilium`)
- 공식 CNI 페이지: **1.17.x / 1.18.x** (예: 1.17.9-0, 1.18.3-0)
- Hybrid Nodes Gateway를 쓰면 branch별 VTEP 최소 **1.17.13-1 · 1.18.8-1 · 1.19.2-1** — 위 예시 버전으로는 Gateway 불가
- 1.18.3은 커널 요구로 **Ubuntu 20.04, RHEL 8 제외**
- 업스트림 최신 차트를 임의로 쓰지 않습니다
::::

:::notes
{timing: 2min}
[요약]
• AWS가 지원하는 Cilium은 AWS 유지 관리 OCI 차트 (public.ecr.aws/eks/cilium/cilium)
• agent와 operator 모두 compute-type=hybrid affinity로 하이브리드 노드에만 배치
• cluster-pool IPAM, envoy 비활성, kubeProxyReplacement는 "false"
• 공식 CNI 페이지는 1.17/1.18, Gateway 사용 시 branch별 최소 1.17.13-1·1.18.8-1·1.19.2-1

첫 탭은 agent affinity와 IPAM입니다. compute-type이 hybrid인 노드에만 agent를 올리고, 클라우드 노드는 기존 VPC CNI가 계속 관리합니다. Pod CIDR 리스트는 앞에서 remoteNetworkConfig에 넣은 값과 맞아야 하고, 노드/VPC/Service 대역과 겹치면 안 됩니다. 값은 최초 설치 전에 정하세요.
{cue: pause}
두 번째 탭은 operator 쪽입니다. operator에도 같은 affinity를 줍니다. envoy는 끄고 kubeProxyReplacement는 문자열 false입니다.
세 번째 탭은 버전 이야기입니다. 공식 CNI 페이지는 아직 1.17과 1.18만 명시하고 있습니다. 반면 Gateway CNI 문서는 VTEP 기능의 branch별 최소 버전을 1.17.13-1, 1.18.8-1, 1.19.2-1로 제시합니다. CNI 페이지 예시인 1.17.9-0과 1.18.3-0은 이 최소 버전보다 낮으므로, Gateway를 쓸 계획이라면 처음부터 최소 버전 이상의 AWS 빌드를 선택하세요. 업스트림 최신 Cilium이 자동으로 AWS 지원 대상이 되는 것은 아닙니다. 그리고 1.18.3은 커널 요구 때문에 Ubuntu 20.04와 RHEL 8을 명시적으로 제외합니다.
{cue: transition}
IPAM의 마스크 값이 노드당 Pod 수를 결정합니다. 다음 슬라이드에서 보겠습니다.

[출처]
• D/04 "Cilium CNI" 섹션; https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-cni.html
• Gateway 최소 버전: D/10 "Cilium VTEP 활성화"; https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-gateway-cni.html
:::

---
<!-- Slide 10: Pod CIDR / maxPods -->
@type: content
@title: 마스크가 노드당 Pod 수를 정한다

## 마스크가 노드당 Pod 수를 정한다

:::html
<style>
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<table>
  <thead><tr><th>MaskSize</th><th>전체 IPv4</th><th>사용 가능 (−2 예약)</th><th>maxPods 산정 예</th></tr></thead>
  <tbody>
    <tr><td>/26</td><td>64</td><td>62</td><td>50</td></tr>
    <tr><td>/25</td><td>128</td><td>126</td><td>110</td></tr>
    <tr><td>/24</td><td>256</td><td>254</td><td>240</td></tr>
  </tbody>
</table>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="1">
  <div class="callout callout-info"><strong class="text-info">AWS 공식 가이드</strong><div class="on-surface-muted">설치 후 <code>clusterPoolIPv4PodCIDRList</code>와 <code>MaskSize</code>를 변경하지 않는다</div></div>
  <div class="callout callout-success"><strong class="text-success">Cilium 문서 기준</strong><div class="on-surface-muted">기존 항목·MaskSize는 수정 금지. 확장은 <strong>새 CIDR 항목 추가</strong></div></div>
</div>
<div class="callout callout-warning fragment fade-up" data-fragment-index="2"><strong class="text-warning">산정 예일 뿐</strong> — maxPods 값은 검증된 권장값이 아닙니다. hostNetwork Pod, 데몬, CPU/메모리 여유를 함께 검토하세요.</div>
:::


:::notes
{timing: 2min}
[요약]
• 노드마다 MaskSize 크기의 블록을 할당 — /25면 노드당 128개 주소
• Cilium cluster-pool은 블록당 2개 주소를 예약 → 사용 가능 126개
• maxPods 산정 예: /25→110, /24→240, /26→50
• 확장은 새 항목 추가가 Cilium 문서 기준, AWS 가이드는 변경 자제를 강조

Pod CIDR 설계는 마스크에서 출발합니다. /25 마스크면 노드 하나가 128개 주소 블록을 받습니다. 그런데 cluster-pool은 블록당 주소 두 개를 예약하므로 사용 가능한 주소는 126개이고, 거기에 데몬과 운영 여유를 남겨서 maxPods를 110으로 잡는 식입니다. /24는 240, /26은 50으로 산정한 예입니다.
{cue: pause}
여기서 두 가지 서술이 있어서 정확히 말씀드립니다. AWS 공식 가이드는 설치 후에 clusterPoolIPv4PodCIDRList와 MaskSize를 바꾸지 말라고 안내합니다. 한편 로컬로 검토한 Cilium 문서는 기존 항목과 MaskSize는 건드리지 말고, 새로운 CIDR 항목을 추가하는 방식이 문서화된 확장이라고 설명합니다. 두 표현을 합치면, 기존 값은 고정하고 용량이 부족하면 새 항목을 추가하되 먼저 remote network와 라우팅을 검토하라는 뜻입니다.
이 maxPods 숫자는 어디까지나 산정 예입니다. 마스크를 나중에 바꿔서 블록을 키울 수는 없으니, 처음부터 노드 수와 노드당 Pod 수를 보고 정하세요.
{cue: transition}
설치가 끝나면 노드가 제대로 등록됐는지 확인해야 합니다.

[출처]
• D/07 "maxPods 계산" 표, D/04 "설치 값", cilium/04-ipam-policy.md 클러스터 풀 섹션
:::

---
<!-- Slide 11: 노드 등록 확인 + 라벨/테인트 -->
@type: content
@title: 라벨은 하나, 테인트는 없다

## 라벨은 하나, 테인트는 없다

```bash
kubectl get nodes -l eks.amazonaws.com/compute-type=hybrid -o wide
kubectl get node "$EXPECTED_NODE_NAME" --show-labels
kubectl wait --for=condition=Ready "node/$EXPECTED_NODE_NAME" --timeout=5m
kubectl -n kube-system get pods -o wide | grep cilium
```

:::html
<style>
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="card-grid">
  <div class="callout callout-success fragment fade-up" data-fragment-index="1"><strong class="text-success">자동 라벨</strong><div class="on-surface-muted"><code>eks.amazonaws.com/compute-type=hybrid</code> 하나뿐. <code>--node-labels</code>로 따로 넣을 필요 없음</div></div>
  <div class="callout callout-info fragment fade-up" data-fragment-index="2"><strong class="text-info">추가 라벨</strong><div class="on-surface-muted">NodeConfig <code>kubelet.flags</code>의 <code>--node-labels=...</code></div></div>
  <div class="callout callout-warning fragment zoom-in" data-fragment-index="3"><strong class="text-warning">테인트</strong><div class="on-surface-muted">자동 부여 없음. 선택 사항이며 쓰면 워크로드·CNI에 toleration 필요</div></div>
</div>
:::

```bash
kubectl taint nodes hybrid-gpu-001 gpu=true:NoSchedule   # 운영 중 수동 테인트
```


:::notes
{timing: 1.5min}
[요약]
• 등록 확인: compute-type 라벨로 조회 → Ready 대기 → Cilium agent 존재 확인
• 자동 라벨은 eks.amazonaws.com/compute-type=hybrid 하나뿐
• 테인트는 자동 부여되지 않음 — 선택 사항
• Ready는 필요 조건일 뿐, DNS·이미지 풀·워크로드 확인은 별도

확인 명령부터 보겠습니다. compute-type 라벨로 하이브리드 노드만 조회하고, 예상한 노드 이름에 대해 Ready를 기다립니다. 그리고 해당 노드에 Cilium agent가 올라왔는지 확인합니다. 스크립트로 만들 때는 Node UID를 기록해 두고 실제 호스트와 대조하는 것이 안전합니다.
{cue: pause}
{cue: question}
여기서 자주 나오는 오해가 있습니다. nodeadm이 라벨과 테인트를 알아서 잔뜩 붙여 준다는 생각입니다. 자동으로 붙는 라벨은 compute-type=hybrid 하나입니다. 테인트는 자동으로 붙지 않습니다.
테인트가 필요하면 NodeConfig에 register-with-taints 플래그를 선택적으로 넣거나, 운영 중에 kubectl taint로 직접 추가합니다. 이때 CNI 같은 필수 에이전트가 막히지 않도록 toleration을 반드시 확인하세요.
{cue: transition}
다음은 kubelet 튜닝입니다.

[출처]
• D/04 "초기화와 확인", D/07 "레이블 및 테인트 전략" (참고: D/07 표의 "자동 테인트" 항목은 NodeConfig로 설정하는 선택 사항을 뜻함)
:::

---
<!-- Slide 12: kubelet 튜닝 -->
@type: tabs
@title: kubelet 튜닝: 예약·축출·maxPods

## kubelet 튜닝: 예약·축출·maxPods

::::tab "리소스 예약"
```yaml
kubelet:
  config:
    systemReserved:
      cpu: "500m"
      memory: "1Gi"
      ephemeral-storage: "10Gi"
    kubeReserved:
      cpu: "500m"
      memory: "1Gi"
      ephemeral-storage: "5Gi"
```
Node Allocatable에서 차감하는 예약량입니다. OS·kubelet·런타임·CNI 사용량을 측정해 정합니다. 위 값은 초기 산정 예입니다.
::::

::::tab "축출 임계값"
```yaml
kubelet:
  config:
    evictionHard:
      memory.available: 200Mi
      nodefs.available: 10%
      imagefs.available: 15%
      nodefs.inodesFree: 5%
      imagefs.inodesFree: 5%
    evictionSoft:
      memory.available: 500Mi
    evictionSoftGracePeriod:
      memory.available: 1m30s
```
Hard 임계값은 유예 없이 처리됩니다. `evictionHard`를 바꾸면 inode 항목까지 **전체 의도한 임계값을 명시**하세요. 누락한 기본 임계값은 0이 됩니다.
::::

::::tab "maxPods·GC"
```yaml
kubelet:
  config:
    maxPods: 110
    imageGCHighThresholdPercent: 85
    imageGCLowThresholdPercent: 80
    shutdownGracePeriod: 60s
    shutdownGracePeriodCriticalPods: 20s
```
`maxPods`는 Cilium 노드별 pool 크기(/25 → 사용 가능 126)와 함께 정합니다. 종료 유예 60초에는 critical Pod용 20초가 포함됩니다.
::::

:::notes
{timing: 1.5min}
[요약]
• systemReserved/kubeReserved는 Node Allocatable 산정용 예약 — 측정 후 조정
• evictionHard를 바꿀 때는 전체 임계값을 명시 (누락한 기본값은 0)
• 노드 압박 축출은 PDB를 따르지 않음
• maxPods는 Cilium pool 크기와 함께 결정

kubelet 설정은 NodeConfig의 kubelet.config 아래에 넣습니다. 첫 번째 탭은 리소스 예약입니다. 값은 OS, kubelet, containerd, CNI가 실제로 쓰는 양을 측정해서 정하세요. 슬라이드 값은 초기 산정 예입니다.
{cue: pause}
두 번째는 축출 임계값입니다. hard 임계값은 유예 없이 처리되고, 노드 압박 축출은 API eviction과 달리 PodDisruptionBudget을 따르지 않습니다. evictionHard를 수정할 때는 inode 항목까지 모두 적어야 합니다. 빠뜨린 기본값은 0으로 처리됩니다.
세 번째 탭의 maxPods는 앞에서 본 Cilium 블록 크기와 맞춥니다. 종료 유예는 전체 60초 안에 critical Pod 20초가 포함되어 일반 Pod 창은 40초입니다.
{cue: transition}
튜닝까지 마친 노드를 어떻게 업그레이드할지 보겠습니다.

[출처]
• D/07 "kubelet 튜닝" 섹션 (리소스 예약, 축출 임계값, maxPods 계산, 이미지 GC, 셧다운)
:::

---
<!-- Slide 13: 업그레이드 전략 -->
@type: tabs
@title: 업그레이드는 교체가 기본이다

## 업그레이드는 교체가 기본이다

::::tab "노드"
- **권장: 새 호스트를 준비해 전환** — 새 노드를 초기화·검증한 뒤 이전 호스트를 비웁니다 (이전 호스트는 검증 완료까지 보존)
- **in-place**: 비운(cordon + drain) 호스트에서 `nodeadm upgrade` 실행. 중단 작업이며 트랜잭션식 다운그레이드가 아님
- kubelet은 API 서버보다 새 버전일 수 없고, **n-3까지** 뒤처질 수 있음 (계속 유지하라는 권장은 아님)
- 뒤처진 노드를 먼저 현재 컨트롤 플레인 마이너로 맞춘 뒤, 다음 마이너는 컨트롤 플레인부터

```bash
sudo /usr/local/bin/nodeadm upgrade "$TARGET_MINOR" \
  -c file:///etc/eks/nodeconfig.yaml --timeout 20m
```
::::

::::tab "Cilium"
1. 현재 values·Helm revision 저장, 버전별 업그레이드 문서 확인
2. Hybrid 노드로 한정한 **별도 preflight 릴리스** 실행 (`preflight.enabled=true`, `agent=false`, `operator.enabled=false`)
3. DaemonSet 커버리지와 검증 Deployment readiness를 **둘 다** 대기
4. 통과 후 preflight 릴리스만 제거
5. 기존 values + 적절한 `upgradeCompatibility`로 업그레이드, **한 마이너씩**

> 마이너 버전 사이에 `--reuse-values`를 쓰지 않습니다.
::::

::::tab "롤백"
- **`nodeadm upgrade --rollback`은 없습니다**
- 실패 시 해당 노드의 cordon 유지, 나머지 작업 중단
- 현재 컨트롤 플레인과 호환되는 **승인된 이미지/버전의 호스트로 교체**
- `/var/lib/kubelet`, `/etc/kubernetes` 재귀 삭제는 롤백 단계가 아님
- `uninstall`은 SSM 등록도 해제하므로 무조건 uninstall/reinstall 반복 금지
- Cilium만 명시한 Helm revision으로 `helm rollback` 가능하나 데이터 경로 복구를 보장하지 않음 (CRD 호환성 검토 필요)
::::

:::notes
{timing: 2min}
[요약]
• 기본 전략은 in-place보다 호스트 교체 — 새 호스트를 검증한 뒤 이전 호스트를 비움
• kubelet 스큐는 API 서버 대비 n-3까지 허용, 더 새로울 수는 없음
• Cilium은 preflight 릴리스 → upgradeCompatibility와 함께 한 마이너씩, --reuse-values 금지
• 롤백 명령은 없음 — 롤백은 호스트 교체, Cilium만 helm rollback 가능

첫 번째 탭, 노드 업그레이드입니다. AWS는 여유 용량이 있으면 새 호스트를 준비해서 제어된 방식으로 전환하는 것을 권장합니다. in-place nodeadm upgrade도 가능하지만, cordon과 drain을 한 호스트에서 먼저 하고 실행하는 중단 작업이고, 되돌리는 기능이 아닙니다.
{cue: pause}
kubelet 버전은 API 서버보다 새로울 수 없고, 최대 n-3까지 뒤처질 수 있습니다. 하지만 허용된다고 해서 오래된 버전을 유지하라는 뜻은 아닙니다.
두 번째 탭은 Cilium입니다. 먼저 preflight 릴리스를 따로 띄워서 검사하고, 통과하면 그 릴리스만 지운 뒤, 기존 values와 upgradeCompatibility로 업그레이드합니다. 마이너 버전 사이에 --reuse-values를 쓰면 오래된 설정이 그대로 넘어가므로 쓰지 않습니다.
{cue: question}
세 번째, 롤백은 어떻게 할까요? nodeadm에는 rollback이 없습니다. 실패한 노드는 cordon을 유지하고, 승인된 버전으로 호스트를 교체합니다. 롤백이 되는 것은 Cilium의 helm revision뿐인데, 그것도 데이터 경로 복구를 보장하지는 않습니다.
{cue: transition}
이제 제한망 환경에서 설치하는 방법을 보겠습니다.

[출처]
• D/07 "버전 스큐 정책", "롤링 업그레이드", "복구와 롤백의 한계"; D/04 "업그레이드와 제거 경계", "Cilium 업그레이드"
• cilium/07-advanced-topics.md "롤아웃과 복구" 섹션
:::

---
<!-- Slide 14: 제한망(air-gap) -->
@type: tabs
@title: 제한망 ≠ 단절: AWS 연결은 필수

## 제한망 ≠ 단절: AWS 연결은 필수

::::tab "정의"
- 제한망 = **퍼블릭 인터넷은 제한**, 하지만 EKS 컨트롤 플레인과 자격 증명용 AWS 서비스 연결은 계속 필요
- 물리적 단절(DDIL)은 Hybrid Nodes의 지원 운영 모델이 아님 — IAM Roles Anywhere도 CreateSession 호출이 필요
- 온프레미스에서 S3에는 **Interface 엔드포인트** 사용 (gateway 엔드포인트는 온프레미스에서 직접 접근 불가)
- 소프트웨어는 승인한 manifest를 자체 미러에서 사용 — artifact와 manifest는 검토한 절차로 직접 준비 (nodeadm은 SigV4 서명 없는 HTTP(S)로 다운로드)
::::

::::tab "명령"
```bash
sudo nodeadm install "$APPROVED_PATCH" --region "$REGION" \
  --credential-provider iam-ra --containerd-source none \
  --manifest-override "file://$LOCAL_MANIFEST" --private-mode

sudo nodeadm init --config-source file:///etc/eks/nodeconfig.yaml \
  --manifest-override file:///etc/eks/manifest.json --private-mode
```
`--private-mode`는 `--manifest-override`가 필수이며 OS 패키지 설치를 건너뜁니다. containerd, runc, iptables, CA 인증서는 **미리 설치**해 두세요.
::::

::::tab "PHZ CNAME은 안 됨"
`hybrid-assets.eks.amazonaws.com`을 Route 53 PHZ에서 S3로 CNAME 해도 **투명 미러가 되지 않습니다.**
- TLS 인증서·SNI 호스트명 불일치
- HTTP Host 헤더와 S3 버킷·키 매핑 불일치
- 요청 권한(서명) 미제공

TLS 검사를 끄는 방식으로 해결하지 않습니다. 대신 통제된 프록시, 사전 설치 이미지, 실제 미러 URL의 manifest override 중 선택하세요.
::::

:::notes
{timing: 1.5min}
[요약]
• 제한망은 "AWS 연결이 없는" 환경이 아님 — 컨트롤 플레인·자격 증명 연결은 필수
• 설치와 init 모두 --manifest-override + --private-mode
• private mode는 OS 패키지를 건너뛰므로 런타임을 미리 설치
• PHZ CNAME 방식은 TLS/SNI/Host 헤더 문제로 문서에서 기각

제한망을 먼저 정의하겠습니다. 퍼블릭 인터넷이 제한된다는 뜻이지, AWS 연결이 필요 없다는 뜻이 아닙니다. 완전히 단절된 환경은 Hybrid Nodes의 지원 운영 모델이 아닙니다.
{cue: pause}
두 번째 탭의 명령입니다. install과 init 양쪽에 manifest-override와 private-mode를 전달합니다. private mode는 OS 패키지 설치를 건너뛰기 때문에 containerd, runc, iptables, CA 인증서를 이미지에 미리 넣어 두어야 합니다. 그리고 init에는 dry-run이 없다는 점도 다시 한 번 기억해 주세요.
{cue: question}
"DNS만 바꿔서 hybrid-assets 도메인을 S3로 돌리면 되지 않나요?" 하는 질문을 자주 받습니다. 문서에서는 이 방식을 기각합니다. 원래 호스트 이름의 TLS 인증서, Host 헤더와 S3 키 매핑, 요청 서명이 모두 보존되지 않기 때문입니다. TLS 검사를 끄는 것도 해법이 아닙니다.
{cue: transition}
이제 장애가 났을 때 증상별로 어떻게 좁혀 가는지 보겠습니다.

[출처]
• D/03 "연결과 격리의 경계", "준비한 노드의 설치와 초기화", "DNS와 프라이빗 엔드포인트 요구 사항" 섹션
:::

---
<!-- Slide 15: 트러블슈팅 -->
@type: tabs
@title: 장애는 증상별로 좁혀 간다

## 장애는 증상별로 좁혀 간다

::::tab "join 실패"
```bash
sudo nodeadm debug --config-source file:///etc/eks/nodeconfig.yaml
sudo journalctl -u kubelet --since '-15 min' --lines 200 --no-pager
```
- 노드 IP가 EKS **remote node CIDR** 안에 있는가
- DNS·라우팅·TCP 443 반환 경로, 의도한 Hybrid 역할, `HYBRID_LINUX` access entry
- 엔드포인트가 "Public and Private"로 설정되지 않았는가 (public IP로 해석되어 join 실패 가능)
- `eks:DescribeCluster` 권한 여부
::::

::::tab "Not Ready"
```bash
sudo systemctl status kubelet containerd --no-pager
kubectl describe node "$NODE"
kubectl -n kube-system get pods -o wide | grep cilium
```
- CNI·agent 로그, 런타임, 디스크·리소스 조건 확인
- NotReady가 **항상 CNI 누락 때문은 아님**
- NotReady만으로 등록 해제·재초기화하지 않기 (`nodeadm reset`은 없음)
::::

::::tab "네트워크"
- API → kubelet **TCP 10250**이 온프레미스 방화벽으로 들어오는가
- Webhook은 실제 설정한 포트·Pod IP 경로가 열려 있는가
- 이미지 풀/x509 오류: ECR api·dkr, S3, 레지스트리 CA와 호스트명 (TLS 검증 유지, `curl -k` 금지)
- DNS: CoreDNS가 클라우드/온프레미스 양쪽에 있는지 확인
- EKS **cluster insights**의 hybrid nodes 점검 항목도 함께 확인
::::

::::tab "크리덴셜 만료"
```bash
openssl x509 -in "$CERT_PATH" -checkend 2592000 -noout
sudo nodeadm debug --config-source file:///etc/eks/nodeconfig.yaml
```
- SSM: 활성화 만료(신규 등록 제한)와 에이전트 갱신·시각 동기화를 구분
- IAM Roles Anywhere: 인증서 만료·역할 세션 시간·AWS 접근 확인
- `sudo aws sts get-caller-identity`는 kubelet이 쓰는 신원을 증명하지 않음
::::

:::notes
{timing: 2min}
[요약]
• 도구: nodeadm debug, journalctl -u kubelet, systemctl status, kubectl describe node
• join 실패 → access entry, DescribeCluster, remote node CIDR, 443 경로
• NotReady → 항상 CNI 문제는 아님
• 크리덴셜 → 활성화 만료와 에이전트 갱신을 구분, 인증서는 openssl checkend

증상별로 네 탭입니다. join 실패는 nodeadm debug부터 돌립니다. 이 명령이 AWS와 클러스터 연결, 자격 증명을 검사해 줍니다. 출력에는 민감한 정보가 있을 수 있으니 비공개로 보관하세요. 그다음 노드 IP가 remote node CIDR 안인지, 443 경로가 열렸는지, access entry와 DescribeCluster 권한이 있는지 봅니다. 퍼블릭과 프라이빗 엔드포인트를 동시에 켠 경우에도 join이 실패할 수 있습니다.
{cue: pause}
NotReady는 journalctl과 systemctl status, kubectl describe node로 봅니다. 항상 CNI 문제는 아닙니다. 디스크나 런타임 조건일 수도 있고요. 그리고 NotReady라는 이유로 무작정 등록 해제하고 재초기화하지 마세요.
네트워크 탭에서는 API에서 kubelet으로 들어오는 10250 포트가 방화벽에서 막히는지 확인합니다. 방향이 중요합니다. 노드에서 API로 나가는 443과, API에서 노드로 들어오는 10250은 다릅니다. EKS 콘솔의 cluster insights에도 hybrid nodes 관련 점검이 있으니 같이 보시기 바랍니다.
{cue: transition}
마지막 탭, 크리덴셜 만료는 다음 슬라이드에서 자세히 다루겠습니다.

[출처]
• D/04 "문제 해결" 표와 진단 명령, D/08 "노드 연결 문제", D/01 엔드포인트 주의
• cluster insights 항목은 로컬 D/ 문서에 명령 예가 없어 서술만 포함 — 공식 문서 확인 필요
:::

---
<!-- Slide 16: 크리덴셜 라이프사이클 -->
@type: tabs
@title: 크리덴셜 만료를 먼저 감시하라

## 크리덴셜 만료를 먼저 감시하라

::::tab "SSM"
- 활성화 기본 만료 **24시간**, 최대 **30일**, RegistrationLimit **1–1000**
- 활성화 만료는 **신규 등록만** 제한 — 이미 등록한 노드는 영향 없음
- 세션 자격 증명은 고정 1시간, 에이전트가 갱신
- 새 호스트 등록이나 승인된 복구에만 새 활성화 생성

```bash
aws ssm create-activation --iam-role "$HYBRID_NODE_ROLE_NAME" \
  --registration-limit "$NEW_NODE_COUNT" --region "$AWS_REGION" \
  --output json > activation.private.json   # 응답은 비공개 파일에 저장
```
::::

::::tab "IAM Roles Anywhere"
- 세션 기본 1시간, 범위 15분–12시간, 역할 `MaxSessionDuration` 이하
- 노드 호스트 인증서 만료를 모니터링 (30일은 경고 임계값 예시)

```bash
# 만료까지 30일 미만이면 실패(종료 코드 1)
openssl x509 -in "$CERT_PATH" -checkend 2592000 -noout
```
- 인증서 갱신은 기존 PKI/CA 정책으로, 후보 인증서는 활성 파일과 분리 검증 후 교체
- kubelet 재시작만으로 X.509가 갱신되지 않음
::::

::::tab "Trust Anchor"
동일 CA에서 leaf만 갱신하면 trust anchor 교체는 보통 불필요합니다. CA rollover는 **모든 호스트·profile·role에 영향**을 줍니다.

```bash
jq -n --rawfile bundle "$APPROVED_CA_PEM" \
  '{sourceType:"CERTIFICATE_BUNDLE", sourceData:{x509CertificateData:$bundle}}' \
  > trust-anchor-source.private.json
aws rolesanywhere update-trust-anchor --trust-anchor-id "$TRUST_ANCHOR_ID" \
  --region "$AWS_REGION" --source file://trust-anchor-source.private.json
```
카나리 노드에서 새 자격 증명 발급을 검증한 뒤 마칩니다.
::::

:::notes
{timing: 1.5min}
[요약]
• SSM 활성화 만료는 신규 등록만 막고 기존 노드는 그대로
• IAM Roles Anywhere는 인증서 만료가 핵심 — openssl x509 -checkend 2592000으로 30일 전 경고
• trust anchor 업데이트는 CA rollover 때만, 전체 노드에 영향
• 자격 증명 비밀은 비공개 파일에 저장

SSM 탭입니다. 활성화는 기본 24시간, 최대 30일까지 만료를 정할 수 있고, 등록 한도는 활성화당 1에서 1000입니다. 만료는 신규 등록을 제한할 뿐이어서, 이미 붙어 있는 노드는 영향을 받지 않습니다. 그러니 활성화가 만료됐다고 정상 노드를 uninstall하는 일은 없어야 합니다.
{cue: pause}
IAM Roles Anywhere에서 실제로 문제가 되는 것은 인증서 만료입니다. checkend 2592000은 30일을 초 단위로 쓴 값이고, 30일 안에 만료되면 0이 아닌 종료 코드를 반환하니 모니터링 스크립트에 넣기 좋습니다. 단, 이 검사는 만료만 보는 것이고 체인이나 CN, 신뢰 설정까지 검증하지는 않습니다.
{cue: question}
trust anchor는 언제 바꿀까요? 같은 CA에서 leaf 인증서만 갱신한다면 바꿀 필요가 없습니다. CA rollover일 때만 update-trust-anchor를 쓰고, 의존하는 모든 노드에 영향이 가므로 카나리로 먼저 검증하세요.
{cue: transition}
여기까지 Block 3의 내용입니다. 퀴즈로 확인해 보겠습니다.

[출처]
• D/07 "자격 증명 라이프사이클" 섹션, D/01 "SSM Role과 Activation", "Roles Anywhere Trust와 수명"
:::

---
<!-- Slide 17: Quiz (1/2) -->
@type: quiz
@title: Block 3 Quiz (1/2)

## Block 3 Quiz (1/2)

**Q1: nodeadm NodeConfig에서 반드시 직접 채워야 하는 최소 항목은?**
- [ ] API 서버 엔드포인트와 클러스터 CA
- [x] 클러스터 이름, 리전, 자격 증명 공급자 블록
- [ ] Node 라벨과 Taint

**Q2: nodeadm이 하이브리드 노드에 자동으로 붙여 주는 라벨은?**
- [ ] workload-type=hybrid
- [x] eks.amazonaws.com/compute-type=hybrid
- [ ] 자동 라벨은 없다

:::notes
{timing: 1min}
[요약]
• Q1 정답: 클러스터 이름+리전+공급자 블록 (endpoint/CA는 DescribeCluster로 조회)
• Q2 정답: eks.amazonaws.com/compute-type=hybrid, 테인트는 자동 부여되지 않음

퀴즈 첫 두 문제입니다. 1번은 NodeConfig 최소 구성인데, 엔드포인트와 CA를 직접 넣지 않아도 된다는 점을 기억하시면 됩니다.
{cue: poll}
2번은 자동 라벨입니다. 하나뿐이고, 테인트는 없습니다.
{cue: transition}
이어서 3, 4번입니다.
:::

---
<!-- Slide 18: Quiz (2/2) -->
@type: quiz
@title: Block 3 Quiz (2/2)

## Block 3 Quiz (2/2)

**Q3: nodeadm upgrade가 실패했을 때 올바른 대응은?**
- [ ] nodeadm upgrade --rollback 실행
- [x] cordon을 유지하고 승인된 버전의 호스트로 교체
- [ ] /var/lib/kubelet을 재귀 삭제하고 재시도

**Q4: 제한망(air-gap)에서 비공개 manifest로 설치할 때 쓰는 옵션 조합은?**
- [ ] Route 53 PHZ로 hybrid-assets를 S3에 CNAME
- [x] --manifest-override 와 --private-mode
- [ ] --dry-run 과 --config-source s3://

:::notes
{timing: 1min}
[요약]
• Q3 정답: cordon 유지 + 승인된 버전 호스트로 교체 (rollback/reset 명령 없음)
• Q4 정답: --manifest-override + --private-mode

3번은 롤백입니다. rollback과 reset은 존재하지 않습니다. 호스트 교체가 답입니다.
{cue: pause}
4번은 제한망 옵션입니다. PHZ 방식은 문서에서 기각했고, config-source로 S3를 지정하는 방식은 문서화되지 않았습니다. 정답은 manifest-override와 private-mode입니다.
{cue: transition}
마지막으로 참고 자료를 정리하겠습니다.
:::

---
<!-- Slide 19: References + Q&A -->
@type: content
@title: References & Q&A

## References & Q&A

:::html
<style>
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="card-grid" data-reveal="static">
  <div class="metric-card"><strong class="text-accent">nodeadm 레퍼런스</strong><div class="on-surface-muted">docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-nodeadm.html</div></div>
  <div class="metric-card"><strong class="text-accent">자격 증명</strong><div class="on-surface-muted">docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-creds.html</div></div>
  <div class="metric-card"><strong class="text-accent">Hybrid CNI</strong><div class="on-surface-muted">docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-cni.html</div></div>
  <div class="metric-card"><strong class="text-accent">Bottlerocket</strong><div class="on-surface-muted">docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-bottlerocket.html</div></div>
  <div class="metric-card"><strong class="text-accent">업그레이드</strong><div class="on-surface-muted">docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-upgrade.html</div></div>
  <div class="metric-card"><strong class="text-accent">nodeadm 소스</strong><div class="on-surface-muted">github.com/aws/eks-hybrid (v1.0.20)</div></div>
</div>
:::


:::notes
{timing: 1min}
[요약]
• Block 3의 근거는 AWS hybrid-nodes 문서와 aws/eks-hybrid v1.0.20 소스
• 문서의 예제는 실제 클러스터에서 모두 실행 검증된 것은 아님 — 적용 전 환경에서 확인
• 다음 Block 4에서는 운영·워크로드 배치·보안과 전략을 다룸

참고 자료를 정리했습니다. nodeadm 레퍼런스와 자격 증명, CNI, Bottlerocket, 업그레이드 문서가 오늘 내용의 근거입니다. 예제들은 문서 기준이고 모든 환경에서 검증된 레시피는 아니라는 점을 한 번 더 말씀드립니다.
{cue: pause}
{cue: question}
여기서 질문 받겠습니다. 부트스트랩이나 업그레이드, 크리덴셜 관리 중 궁금하신 부분 말씀해 주세요.
{cue: transition}
질문이 없으면 쉬는 시간을 가진 뒤 마지막 Block 4로 넘어가겠습니다.
:::

---
<!-- Slide 20: Thank You -->
@type: thankyou
@toc: toc.html
@next: 04-operations-strategy.html
@next-label: 다음: Block 4

# Thank You

Block 3 — 노드 부트스트랩 & 라이프사이클 완료

:::notes
{timing: 0.5min}
[요약]
• Block 3 완료: 사전 준비, nodeadm, Cilium, 업그레이드, 트러블슈팅, 크리덴셜
• 목차로 돌아가거나 Block 4로 이동

Block 3을 마치겠습니다. 5분 쉬고 Block 4에서 운영, 워크로드 배치, 보안과 전략을 다루겠습니다.
{cue: break}
:::
