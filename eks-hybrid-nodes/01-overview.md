---
remarp: true
block: 01-overview
---

---
<!-- Slide 1: 세션 커버 -->
@type: cover

# EKS Hybrid Nodes

온프레미스를 EKS로 확장하는 가이드

Block 1 — 개요 & 아키텍처 | 30분

:::notes
{timing: 0.5min}
[요약]
- 오늘 세션은 총 4개 블록, 각 30분으로 구성됩니다.
- 첫 블록은 "왜, 무엇, 어떻게 붙는가"를 다룹니다.
- 기준일은 2026년 10월이고, 예제 검토 기준은 EKS 1.36 / nodeadm 1.0.20입니다.

안녕하세요. 오늘은 EKS Hybrid Nodes를 주제로 두 시간 세션을 진행합니다. 첫 번째 블록에서는 온프레미스 쿠버네티스 운영이 왜 힘든지부터 시작해서, Hybrid Nodes가 무엇이고 어떤 구조로 동작하는지, 그리고 도입 전에 꼭 알아야 할 제약과 요금까지 훑어보겠습니다.
{cue: question}
시작 전에 하나만 여쭤볼게요. 지금 온프레미스에서 직접 컨트롤 플레인을 운영하고 계신 분 계신가요?
{cue: transition}
그럼 전체 일정부터 보겠습니다.
:::

---
<!-- Slide 2: 아젠다 -->
@type: agenda
@timing: 120min

## 오늘 세션 구성

1. 개요 & 아키텍처 (30분)
2. 네트워킹 & Hybrid Nodes Gateway (30분)
3. 노드 부트스트랩 & 라이프사이클 (30분)
4. 운영·워크로드·보안 & 전략 (30분)

> 질문은 각 Block 종료 시에 받겠습니다.

:::notes
{timing: 1min}
[요약]
- Block 1: 개요, 아키텍처, 제약, 지원 범위, 자격 증명, 요금
- Block 2: 네트워크 요구사항과 Hybrid Nodes Gateway
- Block 3: nodeadm 기반 부트스트랩과 라이프사이클
- Block 4: 운영, 워크로드 배치, 보안(망분리) 관점과 도입 전략

오늘은 30분씩 4개 블록입니다. 지금 보시는 첫 블록은 전체 그림을 잡는 단계이고, 두 번째 블록에서 네트워킹과 Gateway, 세 번째 블록에서 노드를 실제로 붙이고 업그레이드하는 과정, 마지막 블록에서 운영과 보안, 도입 전략을 다룹니다.
{cue: pause}
궁금한 점은 각 블록이 끝날 때 받겠습니다.
{cue: transition}
먼저 문제 정의부터 시작합니다.
:::

---
<!-- Slide 3: 온프렘 K8s 운영의 현실 -->
@type: content
@title: 온프렘 K8s, 왜 아직도 힘든가

## 온프렘 K8s, 왜 아직도 힘든가

:::html
<style>
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--on-surface-muted); font-size: var(--text-base); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="card-grid">
  <div class="card fragment fade-up" data-fragment-index="1">
    <strong class="text-accent">컨트롤 플레인 직접 운영</strong>
    <div class="on-surface-muted">etcd 백업·복구, API server 가용성, 인증서 갱신을 팀이 직접 책임</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="2">
    <strong class="text-accent">버전 업그레이드 부담</strong>
    <div class="on-surface-muted">마이너 버전마다 컨트롤 플레인과 노드를 순서대로 올려야 하고, 실패 시 영향 범위가 큼</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="3">
    <strong class="text-accent">클러스터 파편화</strong>
    <div class="on-surface-muted">클라우드와 온프렘이 서로 다른 도구·정책·버전으로 따로 운영되기 쉬움</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="4">
    <strong class="text-accent">인증·감사 이원화</strong>
    <div class="on-surface-muted">IAM 기반 클라우드 권한 체계와 온프렘 인증 체계를 각각 관리</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="5">
    <strong class="text-accent">GPU·데이터 근접성</strong>
    <div class="on-surface-muted">기존 하드웨어와 대규모 로컬 데이터 때문에 워크로드를 클라우드로 옮기기 어려움</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="6">
    <strong class="text-accent">가시성 도구 분산</strong>
    <div class="on-surface-muted">모니터링·로깅이 환경별로 나뉘어 한 화면에서 보기 어려움</div>
  </div>
</div>
:::


:::notes
{timing: 2min}
[요약]
- 온프렘 쿠버네티스는 컨트롤 플레인 운영 부담이 가장 큽니다.
- 업그레이드, 클러스터 파편화, 인증 이원화가 반복되는 고민입니다.
- GPU와 로컬 데이터 때문에 온프렘을 완전히 버리기도 어렵습니다.

현장에서 자주 듣는 고민을 여섯 가지로 정리했습니다. 제일 먼저 etcd 백업과 API server 가용성 같은 컨트롤 플레인 운영 부담이 있고, 마이너 버전 업그레이드는 항상 긴장되는 작업입니다.
{cue: pause}
클라우드와 온프렘이 따로 굴러가면서 도구와 정책이 갈라지는 파편화도 문제입니다. 그런데도 GPU 서버나 대용량 로컬 데이터 때문에 워크로드를 온프렘에 둬야 하는 경우가 많죠. 이 숫자들은 일반적인 현장 사례 정리이며 특정 통계가 아닙니다.
{cue: question}
여러분 환경에서는 어떤 항목이 가장 아픈가요?
{cue: transition}
그렇다면 AWS는 이 문제에 어떤 선택지를 제공하는지 보겠습니다.
:::

---
<!-- Slide 4: Hybrid/Edge 포트폴리오 비교 -->
@type: content
@title: Edge 옵션, 책임 경계가 다르다

## Edge 옵션, 책임 경계가 다르다

| 옵션 | 컨트롤 플레인 | 워커 노드 | 인프라 소유 |
|------|---------------|-----------|-------------|
| EKS (클라우드) | AWS 관리 | AWS Region의 컴퓨팅 | AWS |
| EKS on Local Zones | AWS 관리 (Region) | Local Zone의 AWS 인프라 | AWS |
| EKS on Outposts | 확장 클러스터는 Region, 로컬 클러스터는 Outposts에서 AWS 관리 | 고객 시설에 설치된 AWS 인프라 | AWS 제공 |
| EKS Anywhere | 고객이 직접 운영 | 고객 인프라 | 고객 |
| EKS Hybrid Nodes | AWS 관리 (EKS) | 고객 소유 온프레미스·엣지 호스트 | 고객 |

:::html
<div class="callout callout-info fragment fade-up" data-fragment-index="1">
  Local Zone·Outposts·다른 클라우드의 머신을 <strong>hybrid node 인프라로 등록하는 것은 지원하지 않습니다.</strong> 이 비교는 개념 수준이며, 상세 지원 범위는 각 서비스의 공식 문서로 확인하세요.
</div>
:::

:::notes
{timing: 2min}
[요약]
- 선택지는 "컨트롤 플레인을 누가 운영하나"와 "워커 하드웨어를 누가 소유하나"로 갈립니다.
- Hybrid Nodes는 AWS 관리형 EKS 컨트롤 플레인에 고객 소유 하드웨어를 붙이는 방식입니다.
- Local Zone이나 Outposts는 AWS 인프라이므로 hybrid node로 등록할 수 없습니다.

표를 두 축으로 읽어주세요. 컨트롤 플레인을 누가 운영하는지, 그리고 워커 노드 하드웨어가 누구 소유인지입니다. EKS Anywhere는 컨트롤 플레인까지 고객이 운영하고, Hybrid Nodes는 컨트롤 플레인을 AWS가 맡습니다.
{cue: pause}
Outposts의 컨트롤 플레인 배치는 배포 방식에 따라 달라서 이 자리에서 단정하지 않고 공식 문서 확인이 필요하다고 표시했습니다. 중요한 점은 Local Zone과 Outposts는 AWS 인프라라서 hybrid node 인프라로 쓸 수 없다는 것입니다.
근거: kubernetes-docs/ko/eks-hybrid-nodes/README.md "Hybrid Nodes 개요" (Local Zone·Outposts 비지원 문장). 나머지 행은 개념 수준 설명이며 로컬 문서에 비교표가 없어 공식 문서 확인이 필요합니다.
{cue: transition}
그럼 Hybrid Nodes가 정확히 무엇인지 보겠습니다.
:::

---
<!-- Slide 5: EKS Hybrid Nodes란 -->
@type: content
@title: 컨트롤 플레인만 AWS에 맡긴다

## 컨트롤 플레인만 AWS에 맡긴다

:::html
<style>
.hn-split { display: grid; grid-template-columns: 1fr 1.1fr; gap: var(--space-4); align-items: center; }
.hn-stack { display: flex; flex-direction: column; gap: var(--space-3); }
.hn-split img { width: 100%; height: auto; }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--on-surface-muted); font-size: var(--text-base); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="hn-split">
  <div class="hn-stack">
    <div class="callout callout-info fragment fade-up" data-fragment-index="1">
      <strong class="text-info">What</strong>
      <div class="on-surface-muted">온프레미스·엣지 노드를 AWS 관리형 EKS 컨트롤 플레인에 연결하는 기능</div>
    </div>
    <div class="callout callout-success fragment fade-up" data-fragment-index="2">
      <strong class="text-success">Why</strong>
      <div class="on-surface-muted">클라우드와 온프렘을 같은 EKS API, 같은 도구로 운영하고 컨트롤 플레인 운영 부담을 줄임</div>
    </div>
    <div class="callout callout-warning fragment fade-up" data-fragment-index="3">
      <strong class="text-warning">단, 책임은 남는다</strong>
      <div class="on-surface-muted">Host·OS·연결·워크로드 운영은 계속 고객 몫</div>
    </div>
  </div>
  <div class="fragment fade-up" data-fragment-index="4">
    <img src="diagrams/hybrid-nodes-highlevel-network.png" alt="AWS 컨트롤 플레인 ENI와 온프레미스 하이브리드 노드를 연결하는 네트워크 개요">
  </div>
</div>
:::


:::notes
{timing: 2min}
[요약]
- Hybrid Nodes = 고객이 운영하는 온프레미스·엣지 노드를 AWS 관리형 EKS 컨트롤 플레인에 연결
- 같은 클러스터에 일반 AWS 노드와 hybrid node를 함께 둘 수 있음
- Host, OS, 연결, 워크로드 운영 책임은 계속 고객에게 있음
- 안정적인 private 양방향 연결이 전제

한 문장으로 말하면, 내 데이터센터의 서버를 AWS가 운영하는 EKS 컨트롤 플레인에 노드로 붙이는 기능입니다. 오른쪽 그림처럼 AWS 쪽에는 컨트롤 플레인과 VPC가 있고, 온프레미스의 hybrid node가 VPN이나 Direct Connect 같은 private 연결로 이어집니다.
{cue: pause}
그림에는 라우터와 게이트웨이가 보이는데, 이 연결과 라우팅은 고객이 준비해야 합니다. Hybrid Nodes가 네트워크를 자동으로 만들어주지는 않습니다. 이 부분은 Block 2에서 자세히 보겠습니다.
근거: kubernetes-docs/ko/eks-hybrid-nodes/README.md 개요 및 diagrams/hybrid-nodes-highlevel-network.png (내용이 fact sheet와 일치함을 확인).
{cue: transition}
다음은 노드가 어떻게 등록되는지 흐름으로 보겠습니다.
:::

---
<!-- Slide 6: 노드 등록 흐름 -->
@type: content
@title: Ready까지 여섯 단계

## Ready까지 여섯 단계

:::html
<style>
.hn-steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3); }
.hn-no { display: inline-block; min-width: 1.6em; margin-right: var(--space-2); text-align: center; border-radius: 50%; background: var(--accent); color: var(--surface-1); font-weight: var(--weight-bold); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--on-surface-muted); font-size: var(--text-sm); margin-top: var(--space-2); }
</style>
<div class="hn-steps">
  <div class="card fragment fade-up" data-fragment-index="1">
    <span class="hn-no">1</span><strong class="text-accent">nodeadm install · init</strong>
    <div class="on-surface-muted">의존성 설치와 구성. nodeadm은 상시 에이전트가 아닌 설치/bootstrap/upgrade CLI</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="2">
    <span class="hn-no">2</span><strong class="text-accent">자격 증명 획득</strong>
    <div class="on-surface-muted">SSM 또는 IAM Roles Anywhere로 임시 자격 증명 확보 (AWS 연결 필요)</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="3">
    <span class="hn-no">3</span><strong class="text-accent">kubelet 기동</strong>
    <div class="on-surface-muted">label eks.amazonaws.com/compute-type=hybrid 자동 부여, taint는 자동 아님</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="4">
    <span class="hn-no">4</span><strong class="text-accent">EKS API 인증</strong>
    <div class="on-surface-muted">Node IAM role의 HYBRID_LINUX access entry로 system:node 신원 매핑</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="5">
    <span class="hn-no">5</span><strong class="text-accent">CNI 설치</strong>
    <div class="on-surface-muted">Cilium 또는 Calico 필요. VPC CNI는 hybrid node를 관리하지 않음</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="6">
    <span class="hn-no">6</span><strong class="text-success">Ready</strong>
    <div class="on-surface-muted">Pod 스케줄 가능. Pod Identity 등 add-on은 별도 구성</div>
  </div>
</div>
:::


:::notes
{timing: 3min}
[요약]
- nodeadm install/init으로 의존성 설치와 구성을 마칩니다.
- 자격 증명(SSM 또는 IAM Roles Anywhere)이 있어야 EKS API 인증이 가능합니다.
- HYBRID_LINUX access entry가 node IAM role을 system:node 신원으로 매핑합니다.
- CNI를 설치해야 노드가 Ready가 됩니다.
- 자동 label은 compute-type=hybrid 하나뿐이고 taint는 자동 부여되지 않습니다.

여섯 단계로 순서대로 보겠습니다. 첫째, nodeadm이 의존성을 설치하고 구성합니다. nodeadm은 계속 떠 있는 에이전트가 아니라 설치, 부트스트랩, 업그레이드용 CLI라는 점을 기억해주세요.
{cue: pause}
둘째와 셋째, 자격 증명을 확보하고 kubelet을 기동합니다. 이때 붙는 label은 eks.amazonaws.com/compute-type=hybrid 하나뿐이고, taint는 자동으로 붙지 않습니다. 필요하면 직접 설계해야 합니다.
넷째, EKS 쪽에는 node IAM role에 대한 HYBRID_LINUX access entry가 있어야 하고 이 entry가 system:node 신원으로 매핑됩니다. 다섯째, CNI를 설치해야 Ready가 됩니다. Bottlerocket VMware 변형은 nodeadm 대신 자체 bootstrap 경로를 쓴다는 점도 참고하세요.
근거: D/01-prerequisites.md "Cluster Access와 생성 계획", D/README.md "아키텍처와 운영 책임", D/04-node-bootstrap.md (label/taint). CNI 설치 전 NotReady 동작은 공식 CNI 문서(hybrid-nodes-cni.html) 기준이며 로컬 문서에서 직접 재확인하지 못했습니다.
{cue: transition}
이 구조에서 누가 무엇을 책임지는지 정리해보겠습니다.
:::

---
<!-- Slide 7: 책임 공유 모델 -->
@type: content
@title: 책임은 나뉘고, 데이터는 AWS에

## 책임은 나뉘고, 데이터는 AWS에

:::html
<style>
.hn-two { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3); margin-bottom: var(--space-3); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--on-surface-muted); font-size: var(--text-base); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="hn-two">
  <div class="card fragment fade-up" data-fragment-index="1">
    <strong class="text-info">AWS 책임</strong>
    <ul class="on-surface-muted">
      <li>EKS API server, etcd, scheduler, controller</li>
      <li>SSM / IAM Roles Anywhere 서비스</li>
      <li>컨트롤 플레인 가용성 관리</li>
    </ul>
  </div>
  <div class="card fragment fade-up" data-fragment-index="2">
    <strong class="text-warning">고객 책임</strong>
    <ul class="on-surface-muted">
      <li>Host, OS, 보안 패치, kubelet·containerd 운영</li>
      <li>CNI 구성, VPN·Direct Connect·라우팅</li>
      <li>노드 인증서·자격 증명 준비, 워크로드 운영</li>
    </ul>
  </div>
</div>
<div class="callout callout-danger fragment fade-up" data-fragment-index="3">
  <strong class="text-danger">데이터 경계 주의</strong> — Secrets, Kubernetes 객체, 로그 등 컨트롤 플레인 데이터는 AWS에 저장됩니다. Private endpoint를 쓴다고 망분리 규정 준수가 입증되지는 않으며, Direct Connect 자체는 기본 암호화를 제공하지 않습니다.
</div>
:::


:::notes
{timing: 2min}
[요약]
- 컨트롤 플레인은 AWS, 노드 이하는 고객 책임입니다.
- 자격 증명 서비스는 AWS지만, 인증서·PKI·activation 준비는 고객 몫입니다.
- Secrets, K8s 객체, 로그는 AWS 컨트롤 플레인에 저장됩니다.
- Private endpoint가 망분리 규정 준수를 자동으로 뜻하지 않습니다.
- Direct Connect는 기본 암호화가 없어 MACsec 또는 IPsec 검토가 필요합니다.

왼쪽은 AWS가 책임지는 영역, 오른쪽은 고객이 책임지는 영역입니다. 컨트롤 플레인 구성요소와 자격 증명 서비스는 AWS가 운영하지만, 노드 OS 패치와 kubelet, containerd, CNI, 그리고 온프렘과 AWS 사이의 연결은 모두 고객이 운영합니다.
{cue: pause}
보안 담당자분들이 꼭 짚으셔야 할 부분이 아래 빨간 박스입니다. Kubernetes API 객체와 Secrets, 로그는 AWS가 관리하는 컨트롤 플레인에 저장됩니다. 그래서 node selector로 워크로드를 온프렘에 붙였다고 해서 데이터 주권이 입증되지는 않습니다.
Direct Connect만으로는 암호화가 보장되지 않기 때문에 MACsec 또는 IPsec 같은 추가 보호를 검토해야 합니다. 이 주제는 Block 4에서 망분리 관점으로 다시 다룹니다.
근거: D/README.md "사용 사례와 데이터 경계", "아키텍처와 운영 책임"; D/11-network-separation-security.md.
{cue: transition}
이제 도입 전에 확인해야 할 제약을 보겠습니다.
:::

---
<!-- Slide 8: 주요 제약 -->
@type: content
@title: 도입 전 꼭 확인할 6가지 제약

## 도입 전 꼭 확인할 6가지 제약

:::html
<style>
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--on-surface-muted); font-size: var(--text-base); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="card-grid">
  <div class="card fragment fade-up" data-fragment-index="1">
    <strong class="text-accent">IPv4 전용</strong>
    <div class="on-surface-muted">Remote node·Pod CIDR은 RFC1918 또는 CGNAT(100.64.0.0/10)이며 VPC·service CIDR과 겹치면 안 됨</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="2">
    <strong class="text-accent">CIDR 개수 상한</strong>
    <div class="on-surface-muted">클러스터당 remote node CIDR 15개, remote Pod CIDR 15개까지. 기존 클러스터에도 추가 가능</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="3">
    <strong class="text-accent">연결형 환경 전제</strong>
    <div class="on-surface-muted">AWS와 안정적인 private 양방향 연결 필요. 단절·간헐 연결(DDIL) 용도 아님</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="4">
    <strong class="text-accent">권장 연결 품질</strong>
    <div class="on-surface-muted">일반 권장: 100 Mbps 이상, RTT 200 ms 이하 (엄격한 최소값은 아님)</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="5">
    <strong class="text-warning">API endpoint는 하나만</strong>
    <div class="on-surface-muted">Public과 private를 동시에 켜면 VPC 밖 노드의 join이 실패할 수 있어 AWS는 하나만 권장</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="6">
    <strong class="text-warning">노드는 유휴여도 과금</strong>
    <div class="on-surface-muted">Join부터 제거까지 vCPU-hour로 과금. Workload가 idle이어도 자동 중단되지 않음</div>
  </div>
</div>
:::


:::notes
{timing: 2min}
[요약]
- 주소는 IPv4, RFC1918 또는 CGNAT, 서로 겹치면 안 됩니다.
- 클러스터당 node CIDR 15개, Pod CIDR 15개까지 지원합니다.
- 안정적인 private 양방향 연결이 필요하며 DDIL 용도는 아닙니다.
- 100 Mbps / RTT 200 ms는 일반 권장이지 엄격한 최소값이 아닙니다.
- API endpoint는 public-only 또는 private-only를 권장합니다.

여섯 가지 제약입니다. 위쪽 네 개는 네트워크 전제로, 주소는 IPv4에 RFC1918이나 CGNAT 범위여야 하고 node, Pod, VPC, service CIDR이 서로 겹치면 안 됩니다.
{cue: pause}
연결 품질은 "100 Mbps, RTT 200 ms 이하"가 일반 권장입니다. 예전 자료에 나오던 100ms나 Direct Connect 10ms 같은 수치는 근거를 확인하지 못해서 사용하지 않았습니다. 아래 두 개는 실수하기 쉬운 항목입니다. endpoint를 public과 private 모두 켜면 join이 실패할 수 있고, 노드는 workload가 놀아도 vCPU-hour 과금이 계속됩니다.
근거: D/README.md "계획에 반영할 제약", D/01-prerequisites.md "Network·CIDR·MTU".
{cue: transition}
다음은 지원 범위 매트릭스입니다.
:::

---
<!-- Slide 9: 지원 매트릭스 -->
@type: tabs

## 지원 매트릭스: OS·K8s·CNI

### OS · 아키텍처

| OS | 지원 범위 |
|----|-----------|
| Ubuntu | 20.04 · 22.04 · 24.04 |
| RHEL | 8 · 9 |
| Amazon Linux 2023 | 온프렘 **가상화** 환경만 (베어메탈 아님) |
| Bottlerocket | VMware 변형 v1.37.0+, **x86_64만**, nodeadm 미사용 |

아키텍처는 x86_64와 arm64. RHEL 10과 Ubuntu 26.04는 지원 목록에 없음.

### Kubernetes · nodeadm

| 항목 | 내용 |
|------|------|
| K8s 버전 | EKS와 동일한 버전 지원 (기준일 2026-10-07: 표준 1.34–1.37, 확장 1.31–1.33) |
| nodeadm | 현재 v1.0.20, SSM 사용 시 **1.0.19 이상** 필요 |
| 설치 권장 | `releases/latest` 대신 릴리스를 고정하고 checksum 검증 |
| 리전 | GovCloud (US)·중국 리전을 제외한 모든 AWS 리전 |

### CNI · Cilium

| 항목 | 내용 |
|------|------|
| AWS 지원 범위 | AWS 빌드 `oci://public.ecr.aws/eks/cilium/cilium` |
| 공식 CNI 페이지 | v1.17.x, v1.18.x 명시 (Gateway 문서는 1.19.2-1+ 언급) |
| 커널 | Cilium 1.18.3은 kernel 5.10+ 필요 → Ubuntu 20.04, RHEL 8 미지원 |
| 주의 | 업스트림 최신 Cilium이 자동으로 AWS 지원 대상은 아님 |
| 지원 범위 | IPv4, VXLAN, Cluster Scope IPAM 등 |

:::notes
{timing: 2min}
[요약]
- OS는 Ubuntu 20.04/22.04/24.04, RHEL 8/9, AL2023(가상화 한정), Bottlerocket VMware 변형(x86_64 한정)
- K8s 버전은 EKS 지원 버전과 동일
- Cilium은 AWS가 유지하는 빌드가 지원 범위이며, 업스트림 최신이 자동 지원은 아님
- 리전은 GovCloud(US)와 중국을 제외한 전체

탭 세 개로 나눴습니다. OS 탭에서 주의할 점은 AL2023이 온프렘 가상화 환경 전용이라는 점과, Bottlerocket은 VMware 변형에 x86_64만 지원하고 nodeadm 대신 자체 bootstrap을 쓴다는 점입니다. RHEL 10이나 Ubuntu 26.04는 아직 목록에 없습니다.
{cue: pause}
두 번째 탭에서 버전은 EKS와 같은 버전을 지원한다고 말씀드리되, 1.37에서 hybrid 전용 검증을 했는지는 단정하지 않겠습니다. SSM을 쓸 때는 nodeadm 1.0.19 이상이 필요합니다.
세 번째 탭의 Cilium은 AWS 빌드가 지원 범위입니다. 공식 CNI 페이지는 1.17과 1.18을 명시하고 Gateway 문서에는 1.19.2-1 이상이 언급되어서 두 문서 사이에 차이가 있습니다. 업스트림 Cilium 최신 버전을 그대로 쓰면 AWS 지원 대상이 아닐 수 있습니다.
근거: D/01-prerequisites.md "OS와 Runtime", D/README.md "계획에 반영할 제약", fact sheet(EKS 지원 버전 2026-10-07 기준), D/04-node-bootstrap.md. 버전 숫자는 시점에 따라 바뀌므로 발표 전 공식 문서로 재확인 필요.
{cue: transition}
다음은 자격 증명 프로바이더 선택입니다.
:::

---
<!-- Slide 10: 크리덴셜 프로바이더 -->
@type: content
@title: 자격 증명: SSM vs IAM RA

## 자격 증명: SSM vs IAM RA

:::html
<style>
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--on-surface-muted); font-size: var(--text-base); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="tab-set" onclick="(function(e){var b=e.target.closest('.tab-btn');if(!b)return;var bar=b.parentNode,p=bar.parentNode,i=[].indexOf.call(bar.children,b);bar.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});b.classList.add('active');p.querySelectorAll('.tc').forEach(function(c,j){c.hidden=j!==i})})(event)">
  <button class="tab-btn active">SSM hybrid activation</button>
  <button class="tab-btn">IAM Roles Anywhere</button>
  <button class="tab-btn">공통 주의</button>
</div>
<div class="tc">
  <div class="card-grid">
    <div class="card fragment fade-up" data-fragment-index="1"><strong class="text-accent">세션 수명</strong><div class="on-surface-muted">고정 1시간, SSM이 자동 갱신</div></div>
    <div class="card fragment fade-up" data-fragment-index="2"><strong class="text-accent">Activation</strong><div class="on-surface-muted">기본 24시간, 최대 30일, RegistrationLimit 1–1000</div></div>
    <div class="card fragment fade-up" data-fragment-index="3"><strong class="text-accent">노드 이름</strong><div class="on-surface-muted">SSM이 생성하는 mi-... 이름</div></div>
    <div class="card fragment fade-up" data-fragment-index="4"><strong class="text-accent">언제 선택</strong><div class="on-surface-muted">기존 PKI가 없고 간단한 등록이 필요할 때</div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="card-grid">
    <div class="card"><strong class="text-accent">세션 수명</strong><div class="on-surface-muted">기본 1시간, 15분–12시간 설정 가능 (role 최대값 이하)</div></div>
    <div class="card"><strong class="text-accent">준비물</strong><div class="on-surface-muted">PKI, 노드별 인증서·키, trust anchor, profile, role</div></div>
    <div class="card"><strong class="text-accent">NodeConfig</strong><div class="on-surface-muted">nodeName, certificatePath, privateKeyPath 지정</div></div>
    <div class="card"><strong class="text-accent">언제 선택</strong><div class="on-surface-muted">기존 PKI와 인증서 수명 관리 체계가 있을 때</div></div>
  </div>
</div>
<div class="tc" hidden>
  <div class="card-grid">
    <div class="callout callout-warning"><strong class="text-warning">AWS 연결 필수</strong><div class="on-surface-muted">두 방식 모두 갱신에 AWS 서비스 endpoint 접근 필요. 로컬 CA로 offline 발급 불가</div></div>
    <div class="callout callout-danger"><strong class="text-danger">SSM Advanced tier 폐지</strong><div class="on-surface-muted">Advanced Instances tier는 2026-06-30 폐지</div></div>
    <div class="callout callout-info"><strong class="text-info">nodeadm 1.0.19+</strong><div class="on-surface-muted">SSM 신규 설치·upgrade에 필요 (현재 v1.0.20)</div></div>
    <div class="callout callout-success"><strong class="text-success">Provider 일관성</strong><div class="on-surface-muted">특별한 이유가 없다면 fleet에서 한 방식만 사용 권장</div></div>
  </div>
</div>
:::


:::notes
{timing: 2.5min}
[요약]
- SSM: 세션 1시간 고정, 별도 PKI 없이 시작하기 쉬움
- IAM Roles Anywhere: 세션 기본 1시간, 15분~12시간, 기존 PKI가 있을 때 적합
- 두 방식 모두 AWS 연결 없이는 자격 증명을 갱신할 수 없음
- SSM Advanced Instances tier는 2026년 6월 30일 폐지, SSM 사용 시 nodeadm 1.0.19 이상
- 한 fleet에서는 한 provider를 일관되게 쓰는 것을 권장

탭을 눌러가며 비교해보겠습니다. SSM은 activation으로 노드를 등록하고 세션은 1시간으로 고정이며 SSM이 갱신합니다. 인증서 인프라가 없어도 시작할 수 있어서 가장 단순합니다. 노드 이름은 SSM이 만드는 mi-로 시작하는 이름이 됩니다.
{cue: pause}
IAM Roles Anywhere는 PKI와 노드별 인증서, trust anchor, profile이 필요합니다. 세션은 기본 1시간이고 15분에서 12시간 사이로 설정하되 role의 최대값을 넘으면 안 됩니다. 기존에 인증서 수명 관리 체계를 갖고 계신 팀에 맞습니다.
공통으로 기억할 점은, 로컬 CA를 둔다고 해서 AWS 없이 자격 증명을 발급받을 수 있는 것은 아니라는 점입니다. 둘 다 갱신할 때 AWS 연결이 필요합니다. 또 SSM Advanced Instances tier는 2026년 6월 30일 폐지되었고, SSM을 쓰려면 nodeadm 1.0.19 이상이어야 합니다.
근거: D/README.md "자격 증명 프로바이더", D/01-prerequisites.md "Provider별 자격 증명", D/04-node-bootstrap.md(NodeConfig), 활성화 기본 24시간/최대 30일/RegistrationLimit은 fact sheet 기준.
{cue: transition}
이제 가장 궁금해하시는 가격을 보겠습니다.
:::

---
<!-- Slide 11: 가격 모델 -->
@type: content
@title: 요금은 vCPU-hour 구간제

## 요금은 vCPU-hour 구간제

| 월 누적 vCPU-hours 구간 | vCPU-hour당 요금 |
|-------------------------|------------------|
| 처음 576,000 | $0.020 |
| 다음 576,000 | $0.014 |
| 다음 4,608,000 | $0.010 |
| 다음 5,760,000 | $0.008 |
| 11,520,000 초과 | $0.006 |

:::html
<style>
.hn-price-notes { display: flex; flex-direction: column; gap: var(--space-2); margin-top: var(--space-3); }
</style>
<div class="hn-price-notes">
  <div class="callout callout-info fragment fade-up" data-fragment-index="1">노드가 <strong>join된 시점부터 제거될 때까지</strong> 과금되며 workload가 idle이어도 요금은 유지됩니다.</div>
  <div class="callout callout-warning fragment fade-up" data-fragment-index="2">Hyperthreading된 bare-metal core는 vCPU 2개로 보고될 수 있습니다. <strong>머신당 32 vCPU 초과</strong> 시 account team과 상담하세요.</div>
  <div class="callout callout-danger fragment fade-up" data-fragment-index="3">모든 사용량에 적용되는 고정 요금이 아닙니다. 클러스터 요금, 네트워크, 로그, 스토리지, OS 요금은 별도입니다.</div>
</div>
:::


:::notes
{timing: 2min}
[요약]
- 월 단위 vCPU-hours 누적 구간별 요금: $0.020 → $0.014 → $0.010 → $0.008 → $0.006
- Join부터 제거까지 과금, idle이어도 계속
- Hyperthreading된 core는 vCPU 2개로 보고될 수 있음
- 클러스터, 네트워크, 로그, 스토리지, OS 요금은 별도

요금표입니다. 노드가 보고하는 vCPU-hours를 월 단위로 누적해서 구간별로 요금을 계산합니다. 처음 57만 6천 vCPU-hours까지는 0.020달러이고, 사용량이 늘수록 단가가 내려가서 1,152만 초과분은 0.006달러입니다.
{cue: pause}
예전 자료에 등장하던 "vCPU당 시간당 0.01달러 고정" 같은 단순화는 틀립니다. 구간제이고, 노드가 클러스터에 연결되어 있는 동안은 workload가 없어도 과금됩니다. 또 hyperthreading을 켠 베어메탈은 코어 하나가 vCPU 2개로 잡힐 수 있어서 사이징할 때 확인해야 합니다.
근거: https://aws.amazon.com/eks/pricing/ 및 D/09-bare-metal-os-setup.md 「비용 비교 분석」(요금 확인일 2026-09-16). 발표 직전에 최신 요금표 재확인 필요.
{cue: transition}
직접 숫자를 넣어서 계산해보겠습니다.
:::

---
<!-- Slide 12: 비용 계산기 -->
@type: content
@title: 내 환경 비용 직접 계산해보기

## 내 환경 비용 직접 계산해보기

:::html
<style>
.hn-calc { display: flex; flex-direction: column; gap: var(--space-3); }
.hn-controls { display: flex; flex-direction: column; gap: var(--space-2); }
.hn-row { display: grid; grid-template-columns: 8rem 1fr; align-items: center; gap: var(--space-3); }
.hn-row label { color: var(--on-surface-muted); }
.hn-presets { display: flex; gap: var(--space-2); }
.hn-break { color: var(--on-surface-muted); font-size: var(--text-sm); }
</style>
<div class="hn-calc">
  <div class="hn-controls">
    <div class="hn-row">
      <label for="hn-nodes">노드 수</label>
      <div class="slider-container">
        <input type="range" id="hn-nodes" min="1" max="200" step="1" value="10">
        <span class="slider-value" id="hn-nodes-v">10</span>
      </div>
    </div>
    <div class="hn-row">
      <label for="hn-vcpu">노드당 vCPU</label>
      <div class="slider-container">
        <input type="range" id="hn-vcpu" min="2" max="32" step="2" value="32">
        <span class="slider-value" id="hn-vcpu-v">32</span>
      </div>
    </div>
    <div class="hn-presets">
      <button class="btn btn-sm" id="hn-p10">10 노드 × 32</button>
      <button class="btn btn-sm" id="hn-p50">50 노드 × 32</button>
      <button class="btn btn-sm" id="hn-p100">100 노드 × 32</button>
    </div>
  </div>
  <div class="card-grid fragment fade-up" data-fragment-index="1">
    <div class="metric-card"><div class="metric-value" id="hn-hours">-</div><div class="metric-label">월 vCPU-hours</div></div>
    <div class="metric-card"><div class="metric-value" id="hn-month">-</div><div class="metric-label">월 노드 요금</div></div>
    <div class="metric-card"><div class="metric-value" id="hn-year">-</div><div class="metric-label">연환산 노드 요금</div></div>
    <div class="metric-card"><div class="metric-value" id="hn-year-cl">-</div><div class="metric-label">연환산 + 클러스터 1개</div></div>
  </div>
  <div class="hn-break" id="hn-break"></div>
  <div class="callout callout-warning fragment fade-up" data-fragment-index="2">
    <strong>추정치입니다.</strong> 가정: 월 730시간, 동일 리전·계정 합산, 같은 월을 12번 반복한 연환산. 마지막 카드는 기본 tier 표준 지원 클러스터 1개($0.10/시간 × 730 × 12 = $876)만 더했으며, 네트워크·로그·스토리지·EC2·OS·하드웨어·인력 비용은 제외입니다.
  </div>
</div>
:::

:::script
var NODES = document.getElementById('hn-nodes');
var VCPU = document.getElementById('hn-vcpu');
var TIERS = [[576000, 0.020], [576000, 0.014], [4608000, 0.010], [5760000, 0.008], [Infinity, 0.006]];
var HOURS = 730;
var CLUSTER_YEAR = 0.10 * HOURS * 12;
function fmtInt(n) { return Math.round(n).toLocaleString('en-US'); }
function fmtUsd(n) { return '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
function calc(vcpuHours) {
  var left = vcpuHours, total = 0, parts = [];
  for (var i = 0; i < TIERS.length && left > 0; i++) {
    var used = Math.min(left, TIERS[i][0]);
    total += used * TIERS[i][1];
    parts.push(fmtInt(used) + ' × $' + TIERS[i][1].toFixed(3));
    left -= used;
  }
  return { total: total, parts: parts };
}
function update() {
  var n = parseInt(NODES.value, 10);
  var v = parseInt(VCPU.value, 10);
  var hours = n * v * HOURS;
  var r = calc(hours);
  document.getElementById('hn-nodes-v').textContent = n;
  document.getElementById('hn-vcpu-v').textContent = v;
  document.getElementById('hn-hours').textContent = fmtInt(hours);
  document.getElementById('hn-month').textContent = fmtUsd(r.total);
  document.getElementById('hn-year').textContent = fmtUsd(r.total * 12);
  document.getElementById('hn-year-cl').textContent = fmtUsd(r.total * 12 + CLUSTER_YEAR);
  document.getElementById('hn-break').textContent = '구간 계산: ' + r.parts.join(' + ');
}
function preset(n) { NODES.value = n; VCPU.value = 32; update(); }
NODES.addEventListener('input', update);
VCPU.addEventListener('input', update);
document.getElementById('hn-p10').addEventListener('click', function () { preset(10); });
document.getElementById('hn-p50').addEventListener('click', function () { preset(50); });
document.getElementById('hn-p100').addEventListener('click', function () { preset(100); });
update();
:::


:::notes
{timing: 3min}
[요약]
- 슬라이더로 노드 수와 노드당 vCPU를 바꾸면 구간 요금을 적용한 월·연 요금이 계산됩니다.
- 프리셋 검증값: 10노드 연 $56,064 / 50노드 $236,928 / 100노드 $377,088 (32 vCPU, 730시간)
- 클러스터 1개 요금($876/년)을 더하면 $56,940 / $237,804 / $377,964
- 이 값은 추정치이며 네트워크, 로그, 스토리지, EC2, OS, 하드웨어, 인력 비용은 제외

위의 프리셋 버튼을 눌러보겠습니다. 10노드에 노드당 32 vCPU, 월 730시간으로 계산하면 월 233,600 vCPU-hours이고 전부 첫 구간이라 월 4,672달러, 연 56,064달러입니다. 여기에 기본 tier 클러스터 1개 요금 876달러를 더하면 56,940달러가 됩니다. 50노드는 연 236,928달러, 100노드는 연 377,088달러이고 클러스터 요금을 더하면 각각 237,804달러, 377,964달러입니다.
{cue: demo}
슬라이더를 움직여서 구간이 넘어가는 지점을 보여주세요. 아래 "구간 계산" 줄에 어느 구간에서 얼마가 적용됐는지 표시됩니다.
{cue: pause}
이 값은 청구서나 실측이 아니라 계산 모델입니다. 실제 월 길이, 구간 초기화 시점, 할인과 세금이 달라질 수 있고, 하드웨어, 전력, OS 구독, 인력과 이전 비용은 비교하려면 별도로 더해야 합니다. 노드당 32 vCPU를 넘는 머신은 account team과 상담하라는 안내가 있어서 슬라이더 최대를 32로 두었습니다.
근거: D/09-bare-metal-os-setup.md 「규모별 연간 비용 비교」(L45-53), 직접 재계산으로 확인 (10노드 233,600h×$0.020=$4,672; 50노드 576,000×0.020+576,000×0.014+16,000×0.010=$19,744; 100노드 11,520+8,064+1,184,000×0.010=$31,424).
{cue: transition}
비용을 이해하셨으면 도입 전 준비 사항을 체크리스트로 점검해보겠습니다.
:::

---
<!-- Slide 13: 사전 준비 체크리스트 -->
@type: checklist

## Join 전 사전 준비 체크리스트

- [ ] Access entry: node IAM role에 HYBRID_LINUX 타입 생성
  ```json
  {
    "clusterName": "my-hybrid-cluster",
    "principalArn": "arn:aws:iam::123456789012:role/EKSHybridNodeRole",
    "type": "HYBRID_LINUX"
  }
  ```
- [ ] remoteNetworkConfig: remote node·Pod CIDR 선언 (기존 클러스터에도 추가 가능)
  ```yaml
  remoteNetworkConfig:
    remoteNodeNetworks:
    - cidrs: [10.80.0.0/16]
    remotePodNetworks:
    - cidrs: [10.85.0.0/16]
  ```
- [ ] IAM: eks:DescribeCluster 포함 (AmazonEKSWorkerNodeMinimalPolicy에는 없음)
- [ ] CIDR: IPv4, RFC1918/CGNAT, VPC·service CIDR과 중복 없음
- [ ] 연결: TGW/VGW 양방향 라우팅, 443 / 10250 / webhook 포트 방화벽
- [ ] OS: 지원 OS·nodeadm 버전·containerd source 확인

:::notes
{timing: 2min}
[요약]
- Access entry(HYBRID_LINUX)와 remoteNetworkConfig는 EKS 쪽 필수 준비입니다.
- 노드 IAM role에 eks:DescribeCluster 권한이 있어야 하며 AmazonEKSWorkerNodeMinimalPolicy만으로는 부족합니다.
- CIDR은 IPv4이고 서로 겹치면 안 됩니다.
- Remote CIDR을 선언했다고 해서 route와 firewall이 자동 생성되지는 않습니다.

체크박스를 눌러 가며 확인해보겠습니다. 첫 번째 항목은 access entry입니다. node IAM role에 HYBRID_LINUX 타입으로 만듭니다. 두 번째는 remoteNetworkConfig로, 온프렘 노드와 Pod CIDR을 클러스터에 알려주는 설정입니다.
{cue: pause}
IAM에서 자주 놓치는 부분은 AmazonEKSWorkerNodeMinimalPolicy에 eks:DescribeCluster가 없다는 점입니다. 따로 추가해야 합니다. 마지막으로 이 CIDR 선언이 라우트와 방화벽 규칙을 자동으로 만들어주지는 않습니다. VPC와 온프렘 양쪽 라우팅은 직접 구성해야 합니다. 코드 조각은 문서의 예시값이며 실제 클러스터에서 실행해본 결과가 아닙니다.
근거: D/01-prerequisites.md "Cluster Access와 생성 계획" 및 "Provider별 자격 증명", "Network·CIDR·MTU".
{cue: transition}
배운 내용을 퀴즈로 확인해보겠습니다.
:::

---
<!-- Slide 14: Block 1 퀴즈 1/2 -->
@type: quiz

## Block 1 퀴즈 (1/2)

**Q1: SSM hybrid activation을 쓸 때 자격 증명 세션 수명은?**
- [ ] 15분
- [x] 1시간
- [ ] 12시간

**Q2: 지원 OS에 대한 설명으로 옳은 것은?**
- [ ] AL2023은 베어메탈 서버에서 권장된다
- [ ] Bottlerocket은 arm64도 지원한다
- [x] AL2023은 온프렘 가상화 환경에서 지원된다

:::notes
{timing: 1.25min}
[요약]
- Q1 정답: SSM 세션은 1시간 고정입니다.
- Q2 정답: AL2023은 온프렘 가상화 환경에서 지원됩니다 (Bottlerocket은 x86_64만, RHEL 10은 목록에 없음).

문제를 풀어보겠습니다. 1번은 SSM 세션 수명으로 1시간 고정입니다. 2번은 AL2023이 온프렘 가상화 환경에서만 지원된다는 점을 묻고 있습니다. Bottlerocket은 VMware 변형에 x86_64만 지원하고 RHEL 10은 목록에 없습니다.
{cue: pause}
정답을 확인하고 다음 두 문제로 넘어가겠습니다.
근거: D/README.md, D/01-prerequisites.md.
{cue: transition}
이어서 3번, 4번입니다.
:::

---
<!-- Slide 15: Block 1 퀴즈 2/2 -->
@type: quiz

## Block 1 퀴즈 (2/2)

**Q3: Hybrid Nodes 요금 구조로 옳은 것은?**
- [ ] 모든 사용량에 vCPU-hour당 $0.01 고정
- [ ] Workload가 idle이면 과금이 중단된다
- [x] 월 누적 vCPU-hours 구간별 단가이며 처음 576,000까지 $0.020

**Q4: 클러스터 API endpoint 설정으로 옳은 것은?**
- [ ] Public과 private를 모두 켜는 것이 필수다
- [x] 둘 다 켜면 VPC 밖 노드의 join이 실패할 수 있어 하나만 권장된다
- [ ] Public endpoint를 쓰면 control plane에서 kubelet으로의 private 연결이 필요 없다

:::notes
{timing: 1.25min}
[요약]
- Q3 정답: 월 누적 구간제이며 처음 576,000 vCPU-hours는 $0.020입니다.
- Q4 정답: 둘 다 켜면 join이 실패할 수 있어 하나만 권장됩니다. 보편적인 API 금지는 아닙니다.

3번은 구간제 요금으로, 모든 사용량에 고정 단가가 적용되지 않고 idle이어도 과금됩니다. 4번은 endpoint 모드입니다. 둘 다 켜면 실패할 수 있어서 AWS가 하나만 쓰도록 권장하며, public endpoint를 써도 control plane에서 노드로의 private 연결 요구는 사라지지 않습니다.
{cue: pause}
근거: D/README.md, D/01-prerequisites.md, 요금표(aws.amazon.com/eks/pricing).
{cue: transition}
마지막으로 참고 자료와 질문 시간입니다.
:::

---
<!-- Slide 16: References + Q&A -->
@type: content
@title: References & Q&A

## References & Q&A

:::html
<style>
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--on-surface-muted); font-size: var(--text-sm); word-break: break-all; }
</style>
<div class="card-grid">
  <div class="card fragment fade-up" data-fragment-index="1">
    <strong class="text-accent">Overview</strong>
    <div class="on-surface-muted">docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-overview.html</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="2">
    <strong class="text-accent">nodeadm</strong>
    <div class="on-surface-muted">docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-nodeadm.html</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="3">
    <strong class="text-accent">Networking</strong>
    <div class="on-surface-muted">docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-networking.html</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="4">
    <strong class="text-accent">OS · Credentials</strong>
    <div class="on-surface-muted">hybrid-nodes-os.html · hybrid-nodes-creds.html</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="5">
    <strong class="text-accent">CNI · Troubleshooting</strong>
    <div class="on-surface-muted">hybrid-nodes-cni.html · hybrid-nodes-troubleshooting.html</div>
  </div>
  <div class="card fragment fade-up" data-fragment-index="6">
    <strong class="text-accent">Pricing</strong>
    <div class="on-surface-muted">aws.amazon.com/eks/pricing</div>
  </div>
</div>
:::


:::notes
{timing: 1.5min}
[요약]
- 공식 문서는 hybrid-nodes-* 시리즈를 기준으로 확인합니다.
- 요금은 EKS 요금 페이지가 기준입니다.
- Block 2에서는 네트워킹과 Hybrid Nodes Gateway를 다룹니다.

오늘 다룬 내용의 공식 출처입니다. 버전과 요금은 시점에 따라 바뀌기 때문에, 실제 도입 전에는 반드시 공식 문서로 재확인하시기 바랍니다.
{cue: pause}
여기까지 질문 있으신가요? 특히 책임 경계나 요금 모델, 지원 OS에 대한 질문을 환영합니다.
{cue: transition}
이어서 다음 블록에서는 네트워킹과 Hybrid Nodes Gateway를 다루겠습니다.
:::

---
<!-- Slide 17: Thank You -->
@type: thankyou
@toc: toc.html
@next: 02-networking-gateway.html
@next-label: 다음: 네트워킹 & Gateway
@message: Block 1 — 개요 & 아키텍처 완료

:::notes
{timing: 0.5min}
[요약]
- Block 1 마무리
- 다음 블록은 네트워킹 & Hybrid Nodes Gateway

Block 1을 마무리하겠습니다. 잠시 쉬었다가 Block 2에서 네트워킹 요구사항과 Gateway를 살펴보겠습니다.
{cue: transition}
감사합니다.
:::
