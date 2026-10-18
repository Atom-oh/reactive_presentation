---
remarp: true
block: 03-operations
---

---
<!-- Slide 1: 4부 구분 (Section) -->
@type: section

# 4부: 운영

붙인 뒤의 일: 수명 주기, 단절, 버스팅

:::notes
{timing: 0.5min}
[요약]
- 4부의 질문: 붙인 노드를 어떻게 바꾸고, 끊기면 어떻게 되고, 모자라면 어디로 넘치는가
- 순서: 노드 라이프사이클과 업그레이드, 네트워크 단절 시 동작, 버스팅 전략
- 명령, 설정 예제, 버전별 점검 항목은 Deep Dive 3부와 4부에 있습니다.

4부는 운영입니다. 3부까지가 노드를 붙이는 이야기였다면, 여기부터는 붙인 뒤의 이야기입니다. 컨트롤 플레인은 AWS가 관리하지만 호스트, OS, 연결은 계속 고객이 운영하기 때문에, 의사결정 단계에서 운영 모델을 미리 그려 두셔야 합니다.
{cue: pause}
세 가지를 봅니다. 노드가 어떤 수명 주기를 거치고 업그레이드는 어떤 순서로 하는지, 네트워크가 끊기면 무슨 일이 일어나는지, 마지막으로 온프렘이 모자랄 때 클라우드로 넘치게 하는 버스팅입니다.
{cue: transition}
노드의 수명 주기부터 보겠습니다.
:::

---
<!-- Slide 2: 노드 라이프사이클과 업그레이드 -->
@type: content
@title: 노드 수명 주기: 업그레이드는 교체가 기본

## 노드 수명 주기: 업그레이드는 교체가 기본

:::html
<style>
.hn4-flow { margin: 0 0 var(--space-3); font-size: var(--fs-card); word-break: keep-all; overflow-wrap: break-word; }
.hn4-flow .flow-box { min-width: min-content; overflow-wrap: normal; }
.hn4-sub { display: block; color: var(--text-secondary); font-size: var(--fs-caption); margin-top: var(--space-1); word-break: keep-all; }
.hn4-label { font-size: var(--fs-card); font-weight: var(--weight-bold); color: var(--text-secondary); margin-bottom: var(--space-2); }
.hn4-skew { border: 1px dashed var(--border); border-radius: var(--radius-md); padding: var(--space-2) var(--space-3); font-size: var(--fs-card); margin-bottom: var(--space-3); word-break: keep-all; }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="hn4-label">조인</div>
<div class="flow-h hn4-flow fragment fade-right" data-fragment-index="1">
  <div class="flow-box">install<span class="hn4-sub">kubelet, containerd 설치</span></div>
  <div class="flow-arrow">→</div>
  <div class="flow-box">init<span class="hn4-sub">자격 증명 설정, EKS 조인</span></div>
  <div class="flow-arrow">→</div>
  <div class="flow-box">CNI 설치<span class="hn4-sub">그 전까지 NotReady는 정상</span></div>
  <div class="flow-arrow">→</div>
  <div class="flow-box">Ready 검증<span class="hn4-sub">워크로드까지 확인 후 투입</span></div>
</div>
<div class="hn4-label">업그레이드 순서</div>
<div class="flow-h hn4-flow fragment fade-right" data-fragment-index="2">
  <div class="flow-box">뒤처진 노드 정리<span class="hn4-sub">현재 컨트롤 플레인 마이너로</span></div>
  <div class="flow-arrow">→</div>
  <div class="flow-box">컨트롤 플레인<span class="hn4-sub">다음 마이너로 먼저</span></div>
  <div class="flow-arrow">→</div>
  <div class="flow-box">노드 교체<span class="hn4-sub">새 호스트 검증 후 이전 호스트를 비움</span></div>
  <div class="flow-arrow">→</div>
  <div class="flow-box">Cilium<span class="hn4-sub">별도 사전 검사, 한 마이너씩</span></div>
</div>
<div class="hn4-skew fragment fade-up" data-fragment-index="3"><strong class="text-info">버전 skew</strong>: kubelet은 API 서버보다 새로울 수 없고, 최대 3개 마이너까지 뒤처질 수 있습니다. 허용 범위일 뿐 유지하라는 권장은 아닙니다.</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="4">
  <div class="callout callout-warning"><strong class="text-warning">롤백 명령은 없음</strong><div class="on-surface-muted">실패한 노드는 cordon을 유지하고, 승인된 버전의 호스트로 교체합니다.</div></div>
  <div class="callout callout-info"><strong class="text-info">릴리스 노트는 직접 점검</strong><div class="on-surface-muted">EKS 최적화 AMI가 아니라 고객 OS 이미지라서 "AMI는 영향 없음" 문구가 해당되지 않습니다.</div></div>
  <div class="callout callout-success"><strong class="text-success">Bottlerocket은 별도 경로</strong><div class="on-surface-muted">nodeadm 대신 자체 설정 경로로 조인, 업그레이드, 제거합니다.</div></div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- 조인은 install, init, CNI, Ready 검증 순서이고 CNI 전 NotReady는 정상. Ready는 필요 조건일 뿐
- 업그레이드는 새 호스트로 교체가 기본, 컨트롤 플레인이 먼저. kubelet은 API 서버보다 새로울 수 없고 n-3까지
- 롤백 명령은 없고 롤백은 호스트 교체. 릴리스 노트의 "AMI는 영향 없음"은 hybrid 노드에 해당하지 않음

위 줄은 노드 한 대가 클러스터에 들어오는 과정입니다. install은 kubelet, containerd 같은 소프트웨어만 깔고, init에서 SSM 등록 같은 자격 증명 설정과 EKS 조인이 일어납니다. 이 시점에 노드가 NotReady인 것은 이상한 일이 아닙니다. CNI가 아직 없기 때문이고, Cilium을 올리면 Ready가 됩니다. 그리고 Ready는 필요 조건일 뿐이라 DNS, 이미지 풀, 자격 증명 갱신, 실제 워크로드까지 확인한 뒤에 서비스에 투입합니다.
{cue: pause}
아래 줄은 업그레이드 순서입니다. kubelet은 API 서버보다 새 버전일 수 없고 최대 n-3까지 뒤처질 수 있습니다. 그래서 뒤처진 노드가 있으면 먼저 현재 컨트롤 플레인 마이너로 맞추고, 다음 마이너는 컨트롤 플레인부터 올립니다. 노드는 in-place 업그레이드도 가능하지만, AWS는 여유 용량이 있으면 새 호스트를 준비해 검증하고 이전 호스트를 비우는 교체 방식을 권장합니다. Cilium은 별도 사전 검사를 거쳐 한 마이너씩 올립니다.
{cue: question}
되돌리는 방법이 궁금하실 텐데, nodeadm에는 rollback 명령이 없습니다. 실패한 노드는 cordon을 유지하고 승인된 버전의 호스트로 바꾸는 것이 롤백입니다. 그래서 골든 이미지와 여유 용량을 미리 준비하는 것이 운영 설계의 핵심입니다.
또 하나, EKS 릴리스 노트에 "EKS 최적화 AMI는 영향 없음"이라고 적힌 항목이 있어도, hybrid 노드는 고객의 OS 이미지라 그 문구가 적용되지 않습니다. 버전마다 kubelet 설정과 이미지를 직접 점검하셔야 합니다. Bottlerocket은 nodeadm을 쓰지 않고 자체 설정 경로로 조인하고 업그레이드합니다.
Cilium 업그레이드 절차, 1.37 전 점검 항목, Bottlerocket 조인 절차는 Deep Dive 3부에 있습니다.
근거: Deep Dive 3부 "부트스트랩은 다섯 걸음", "업그레이드는 교체가 기본이다"(노드, Cilium, 롤백 탭), "1.37 업그레이드 전 필수 점검"(kubelet 탭의 AMI 문구), "Bottlerocket 조인과 운영의 차이"
{cue: transition}
노드를 바꾸는 것은 계획된 일입니다. 계획되지 않은 일, 네트워크가 끊기면 어떻게 될까요.
:::

---
<!-- Slide 3: 네트워크 단절 시 동작 -->
@type: content
@title: 연결이 끊기면: 300초와 1시간

## 연결이 끊기면: 300초와 1시간

:::html
<style>
.hn4-time { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-3); margin-bottom: var(--space-3); }
.hn4-step { border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-3); font-size: var(--fs-card); word-break: keep-all; overflow-wrap: break-word; }
.hn4-when { font-weight: var(--weight-bold); color: var(--accent); margin-bottom: var(--space-2); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.text-danger  { color: var(--danger);  font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="hn4-time">
  <div class="hn4-step fragment fade-right" data-fragment-index="1"><div class="hn4-when">단절 직후</div>kubelet이 Lease를 갱신하지 못해 노드는 Unknown, unreachable taint가 붙습니다.<div class="on-surface-muted">실행 중인 Pod는 바로 옮겨지지 않습니다.</div></div>
  <div class="hn4-step fragment fade-right" data-fragment-index="2"><div class="hn4-when">300초 뒤</div>toleration이 없는 Pod는 기본값으로 eviction됩니다.<div class="on-surface-muted">DaemonSet은 이 taint를 기본으로 견딥니다.</div></div>
  <div class="hn4-step fragment fade-right" data-fragment-index="3"><div class="hn4-when">1시간 넘게</div>SSM 자격 증명은 1시간 고정이라 만료됩니다.<div class="on-surface-muted">IAM Roles Anywhere는 기본 1시간, 최대 12시간</div></div>
  <div class="hn4-step fragment fade-right" data-fragment-index="4"><div class="hn4-when">연결 복구</div>SSM은 재시도 간격 때문에 재연결이 최대 30분 늦을 수 있습니다.<div class="on-surface-muted">IAM Roles Anywhere는 보통 몇 초</div></div>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="5">
  <div class="callout callout-danger"><strong class="text-danger">1. 연결을 전제로 설계</strong><div class="on-surface-muted">간헐 연결, 단절(DDIL) 환경용이 아닙니다. 안정적인 사설 양방향 연결을 유지합니다.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">2. 옮기기 어려운 앱은 tolerationSeconds</strong><div class="on-surface-muted">늘리면 짧은 단절은 견디지만, 실제 장애 노드의 Pod 이전도 늦어집니다.</div></div>
  <div class="callout callout-info"><strong class="text-info">3. 복구 속도로 자격 증명 선택</strong><div class="on-surface-muted">빠른 복구나 긴 세션이 필요하면 IAM Roles Anywhere. SSM이면 복구 후 agent 재시작 절차를 준비합니다.</div></div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
- 끊기면 노드는 Unknown과 unreachable taint, toleration 없는 Pod는 기본 300초 뒤 eviction. DaemonSet은 견딤
- SSM 자격 증명은 1시간 고정이라 오래 끊기면 만료되고 복구 후 재연결이 최대 30분 늦을 수 있음. IAM Roles Anywhere는 보통 몇 초
- 대비 세 가지: 연결 전제 설계, 옮기기 어려운 앱의 tolerationSeconds, 복구 속도에 맞춘 자격 증명 선택

Hybrid Nodes는 컨트롤 플레인이 AWS에 있으니, 온프렘과 AWS 사이 연결이 끊기면 시간 순서로 일이 벌어집니다.
먼저 kubelet이 Lease를 갱신하지 못해서 노드 상태가 Ready Unknown이 되고 unreachable taint가 붙습니다. 이때 노드에서 돌던 Pod를 바로 옮기지는 않습니다. toleration이 없는 Pod는 기본 300초를 기다린 뒤 eviction됩니다. DaemonSet은 이 taint를 기본으로 견딥니다.
{cue: pause}
단절이 1시간을 넘기면 자격 증명이 문제가 됩니다. SSM의 세션 자격 증명은 1시간 고정이라 그보다 오래 끊기면 만료됩니다. 그리고 SSM agent가 지수 백오프로 최대 30분 간격까지 재시도하기 때문에, 네트워크가 돌아와도 노드마다 재연결이 늦어질 수 있습니다. agent를 재시작하면 바로 갱신됩니다. IAM Roles Anywhere는 kubelet이 필요할 때 자격 증명을 받아서 보통 몇 초 안에 재연결되고, 세션도 최대 12시간까지 늘릴 수 있습니다. 대신 길게 잡을수록 유출 시 노출 시간도 길어집니다.
{cue: question}
그럼 무엇을 준비할까요. 첫째, 이 서비스는 간헐 연결이나 단절 환경용이 아니라는 전제를 받아들이고 안정적인 사설 양방향 연결을 설계합니다. 완전 단절이 필요한 요건이라면 맞지 않습니다. 둘째, 다른 호스트로 옮기기 어려운 앱은 tolerationSeconds를 늘리거나 컨트롤러로 taint를 관리할 수 있습니다. 다만 길게 잡을수록 진짜 장애 노드의 Pod 이전도 늦어지니 앱별로 정합니다. 셋째, 단절 후 복구 속도가 중요하면 IAM Roles Anywhere, SSM을 쓴다면 복구 후 agent 재시작 절차를 runbook에 넣어 두세요. 이 선택 기준은 2부 자격 증명 비교와 같은 이야기입니다.
근거: Deep Dive 4부 "도입 판단은 제약 확인부터"(단절 시 Unknown, unreachable taint, 300초 eviction, DaemonSet, tolerationSeconds 노트), Deep Dive 1부 자격 증명 선택 슬라이드(SSM 1시간 고정, 최대 30분 백오프, agent 재시작, IAM RA 보통 몇 초와 최대 12시간), Deep Dive 3부 "크리덴셜 만료를 먼저 감시하라". AWS docs hybrid-nodes-network-disconnection-best-practices, hybrid-nodes-host-creds
{cue: transition}
마지막은 용량 이야기입니다. 온프렘이 모자라면 어디로 넘치게 할까요.
:::

---
<!-- Slide 4: 버스팅 전략 -->
@type: content
@title: 버스팅: 온프렘 먼저, 넘치면 클라우드

## 버스팅: 온프렘 먼저, 넘치면 클라우드

:::html
<style>
.hn4-flow { margin: 0 0 var(--space-3); font-size: var(--fs-card); word-break: keep-all; overflow-wrap: break-word; }
.hn4-flow .flow-box { min-width: min-content; overflow-wrap: normal; }
.hn4-sub { display: block; color: var(--text-secondary); font-size: var(--fs-caption); margin-top: var(--space-1); word-break: keep-all; }
.hn4-handoff { margin-top: var(--space-3); }
.text-accent  { color: var(--accent);  font-weight: var(--weight-bold); }
.text-info    { color: var(--info);    font-weight: var(--weight-bold); }
.text-success { color: var(--success); font-weight: var(--weight-bold); }
.text-warning { color: var(--warning); font-weight: var(--weight-bold); }
.on-surface-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
</style>
<div class="flow-h hn4-flow">
  <div class="flow-box fragment fade-right" data-fragment-index="1">온프렘 우선<span class="hn4-sub">hybrid 노드를 선호하도록 배치</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="2">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="2">자리가 없으면 Pending<span class="hn4-sub">스케줄되지 못한 Pod</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="3">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="3">Karpenter가 EC2 생성<span class="hn4-sub">burst 노드에 스케줄</span></div>
  <div class="flow-arrow fragment fade-right" data-fragment-index="4">→</div>
  <div class="flow-box fragment fade-right" data-fragment-index="4">줄일 때 온프렘 보호<span class="hn4-sub">pod-deletion-cost로 클라우드 Pod를 먼저</span></div>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="5">
  <div class="callout callout-info"><strong class="text-info">Pending Pod에 반응</strong><div class="on-surface-muted">온프렘 포화를 감지하는 기능이 아닙니다. 조건과 toleration이 맞는 Pending Pod에 반응합니다.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">deletion cost는 선호</strong><div class="on-surface-muted">ReplicaSet 축소 때의 best-effort 순서입니다. NotReady인 온프렘 Pod는 먼저 지워질 수 있습니다.</div></div>
  <div class="callout callout-warning"><strong class="text-warning">자동 복귀 없음</strong><div class="on-surface-muted">온프렘 용량이 돌아와도 실행 중인 클라우드 Pod는 돌아오지 않습니다.</div></div>
</div>
<div class="callout callout-success hn4-handoff fragment fade-up" data-fragment-index="6"><strong class="text-success">정책 없음, Kyverno, Kyverno + Karpenter</strong>: 세 방식으로 줄였을 때 어느 Pod가 남는지는 오늘 5부 영상에서 직접 봅니다.</div>
:::

:::notes
{timing: 2.5min}
[요약]
- 온프렘을 선호하도록 배치하고, 자리가 없어 Pending이 된 Pod에 Karpenter가 EC2 burst 노드를 만듭니다.
- 줄일 때는 pod-deletion-cost로 온프렘 Pod를 지키지만 best-effort 선호이고, 비정상 온프렘 Pod는 먼저 지워질 수 있습니다.
- 온프렘 용량이 돌아와도 클라우드 Pod는 자동으로 돌아오지 않습니다. 세 방식 비교는 오늘 5부 영상 V2

버스팅의 흐름은 네 단계입니다. 먼저 hybrid 노드를 선호하도록 배치합니다. hybrid 노드에는 compute-type=hybrid label이 자동으로 붙으니 이것으로 온프렘을 선호하게 합니다. 이 선호는 스케줄링 점수이지 용량 비율이 아닙니다. 온프렘에 자리가 없으면 Pod는 Pending이 되고, Karpenter가 그 Pod에 맞는 EC2 노드를 만들어 받습니다.
{cue: pause}
흔한 오해가 "온프렘이 가득 차면 Karpenter가 감지해서 클라우드로 넘긴다"는 설명입니다. 실제로는 스케줄되지 못한 Pending Pod, 그것도 NodePool 조건과 toleration이 맞는 Pod에 반응합니다. 그리고 버스팅은 클라우드 노드가 있는 혼합 CNI 구성에서 가능하다는 점, 3부에서 본 그대로입니다.
줄일 때가 더 까다롭습니다. 아무 정책이 없으면 ReplicaSet 기본 규칙은 Pod 위치를 보지 않습니다. 그래서 pod-deletion-cost라는 annotation으로 클라우드 Pod가 먼저 지워지도록 선호를 줍니다. 다만 이 값은 best-effort 선호이고 비교 순서에서 뒤쪽이라, 온프렘 Pod라도 NotReady면 정상 클라우드 Pod보다 먼저 지워질 수 있습니다. 노드 장애나 eviction에서 지켜 주는 보호 장치가 아닙니다.
{cue: question}
마지막으로 온프렘 용량이 다시 생겨도 이미 뜬 클라우드 Pod는 자동으로 돌아오지 않습니다. 되돌리려면 별도의 통제된 재배치가 필요합니다.
그럼 실제로 어느 Pod가 남을까요. 정책 없음, Kyverno로 hybrid Pod에 cost 부여, 여기에 Karpenter 기능까지 켠 세 방식으로 같은 워크로드를 늘리고 줄여 봤습니다. 결과는 오늘 5부 영상에서 직접 봅니다. Karpenter 버전 호환성과 배치 설정 예제는 Deep Dive 4부에 있습니다.
근거: Deep Dive 4부 "배치는 label 하나에서 시작한다"(자동 label, weight는 점수), "버스팅은 Pending Pod가 트리거"(흐름, 자동 복귀 없음, 포화 감지기 아님), "스케일-인 순서는 선호일 뿐"(best-effort, 비교 순서, NotReady 온프렘 Pod). Deep Dive 5부 "데모 2: 같은 워크로드를 세 가지로 줄여 본다"(A, B, C 이름만, 수치는 오늘 5부). Deep Dive 2부 CNI 표(버스팅은 혼합 구성)
{cue: transition}
여기까지가 운영이었습니다. 이제 오늘 5부에서 실제로 돌려 본 결과를 영상으로 보겠습니다.
:::
