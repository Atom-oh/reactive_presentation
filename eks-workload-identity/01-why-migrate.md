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

:::notes
{timing: 0.5min}
[요약]
- 주제: 앱의 AWS 권한을 노드 역할에서 워크로드 단위 역할로 옮기기
- 두 방식(IRSA, EKS Pod Identity)이 어떻게 동작하고 어떻게 다른지
- 마지막에 실제 EKS 클러스터에서 이전 과정을 라이브로 실행

안녕하세요, AWS Korea 오준석입니다. 오늘은 EKS에서 애플리케이션의 AWS 권한을 노드 역할에서 떼어 내 워크로드마다 주는 방법을 다룹니다.
IRSA와 EKS Pod Identity가 각각 내부에서 어떻게 자격 증명을 만들어 내는지 보고, 그 차이를 정리한 다음, 실제 클러스터에서 같은 앱 세 벌을 옮기는 과정을 라이브로 보여 드리겠습니다.
{cue: transition}
먼저 오늘 순서입니다.
:::

---
<!-- Slide 2: 아젠다 -->
@type: agenda
@timing: 50min
@title: 오늘 세션 구성

## 오늘 세션 구성

1. 왜 옮기나, 자격 증명 체인 (13분)
2. IRSA와 Pod Identity의 동작 원리 (9분)
3. 비교, 선택 기준, 운영 이전 순서 (11분)
4. 라이브 데모 (12분)
5. 문제 해결, 퀴즈, Q&A (5분)

> 데모가 막히면 슬라이드에 같은 단계의 실측 화면이 있습니다.

:::notes
{timing: 1min}
[요약]
- 다섯 부분: 문제와 체인 13분, 동작 원리 9분, 비교와 이전 순서 11분, 데모 12분, 마무리 5분
- 앞 30분이 원리, 뒤 12분이 그 원리를 눈으로 확인하는 데모
- 데모 단계마다 실측 결과 슬라이드가 있어 네트워크 문제가 생겨도 이어 갈 수 있음

순서는 이렇습니다. 먼저 노드 역할에 앱 권한을 붙였을 때 생기는 문제와, SDK가 자격 증명을 찾는 순서를 봅니다. 그다음 IRSA와 Pod Identity를 한 단계씩 뜯어 보고 비교합니다.
{cue: pause}
뒤의 12분은 라이브 데모입니다. 앞에서 설명한 동작이 실제 Pod에서 그대로 보이는지 확인하는 시간이고, 단계마다 지난 리허설 실측 화면을 슬라이드로 준비해 두었습니다.
{cue: transition}
문제부터 보겠습니다.
:::

---
<!-- Slide 3: 노드 역할 공유 -->
@type: content
@title: 결제 Pod에 준 권한이 옆 Pod에도 열린다

## 결제 Pod에 준 권한이 옆 Pod에도 열린다

:::html
<div class="wid-grid-21">
  <div class="wid-card wid-node wid-edge fragment fade-up" data-fragment-index="1">
    <h4>워커 노드 한 대 (EC2)</h4>
    <div class="wid-stack">
      <div class="wid-row"><strong>결제 API Pod</strong><span class="wid-chip wid-node">node (IMDS)</span></div>
      <div class="wid-row"><strong>로그 수집기 Pod</strong><span class="wid-chip wid-node">node (IMDS)</span></div>
      <div class="wid-row"><strong>배치 Job Pod</strong><span class="wid-chip wid-node">node (IMDS)</span></div>
    </div>
    <div class="wid-muted wid-gap-top">세 Pod 모두 <span class="rp-detail" data-tip="EC2 인스턴스 메타데이터 서비스. 노드 안에서 169.254.169.254로 부르면 인스턴스 프로파일 역할의 임시 자격 증명을 줍니다." data-detail="imds">IMDS</span>(Instance Metadata Service)에서 같은 자격 증명을 받습니다.</div>
  </div>
  <div class="wid-stack">
    <div class="wid-card fragment fade-up" data-fragment-index="2">
      <h4>노드 IAM 역할 (인스턴스 프로파일)</h4>
      <div class="wid-mono">AmazonEKSWorkerNodePolicy</div>
      <div class="wid-mono">AmazonEC2ContainerRegistryPullOnly</div>
      <div class="wid-mono wid-t-danger">+ s3:GetObject (결제 앱 권한)</div>
    </div>
    <div class="wid-card fragment fade-up" data-fragment-index="3">
      <h4>CloudTrail에 남는 호출자</h4>
      <div class="wid-mono">assumed-role/&lt;node-role&gt;/i-&lt;instance-id&gt;</div>
      <div class="wid-muted">세 Pod의 호출이 같은 노드 세션으로 보입니다.</div>
    </div>
  </div>
</div>
:::

:::detail imds "IMDS와 인스턴스 프로파일"
tip: EC2 인스턴스 메타데이터 서비스: 노드 역할의 임시 자격 증명을 주는 링크 로컬 엔드포인트

EC2 인스턴스 프로파일은 노드 IAM 역할을 인스턴스에 전달합니다. 인스턴스 안에서 IMDS(`169.254.169.254`)를 호출하면 그 역할의 임시 자격 증명을 받습니다. IMDSv2는 먼저 PUT으로 세션 토큰을 받은 뒤 그 토큰으로 자격 증명을 조회합니다.

Pod가 이 경로에 닿을 수 있으면, SDK는 다른 공급자를 찾지 못했을 때 IMDS까지 내려가 노드 역할을 씁니다.
:::

:::notes
{timing: 1.5min}
[요약]
- 앱의 S3 권한을 노드 역할에 붙이면 IMDS에 닿는 그 노드의 모든 Pod가 같은 권한을 씀
- 결제 Pod 하나를 위해 추가한 권한이 로그 수집기와 배치 Job에도 열림
- CloudTrail에는 노드 인스턴스 ID 세션으로만 남아 워크로드를 구분하기 어려움

가장 흔한 시작점입니다. 결제 앱이 S3 버킷을 읽어야 해서 노드 IAM 역할에 s3:GetObject를 추가합니다. 당장은 잘 동작합니다.
{cue: click}
그런데 같은 노드에는 로그 수집기도, 배치 Job도 뜹니다. 이 Pod들도 IMDS에서 같은 노드 역할 자격 증명을 받으니 결제 버킷을 읽을 수 있습니다.
{cue: click}
{cue: click}
감사 쪽에서 보면 더 곤란합니다. CloudTrail의 호출자는 노드 역할에 인스턴스 ID가 붙은 세션이라, 어느 Pod가 호출했는지 로그만으로는 알기 어렵습니다.
{cue: transition}
이 구조의 위험을 세 가지로 정리하겠습니다.
:::

---
<!-- Slide 4: 세 가지 위험 -->
@type: content
@title: 노드 역할 공유의 세 가지 위험

## 노드 역할 공유의 세 가지 위험

:::html
<div class="wid-grid-3">
  <div class="wid-card fragment fade-up" data-fragment-index="1">
    <h4 class="wid-t-danger">권한 범위가 노드 단위</h4>
    <div class="wid-muted">한 앱에 필요한 권한이 그 노드에 스케줄되는 모든 Pod의 권한이 됩니다.</div>
    <div class="wid-cap wid-gap-top"><span class="rp-detail" data-detail="blast">어떤 Pod가 영향을 받나</span></div>
  </div>
  <div class="wid-card fragment fade-up" data-fragment-index="2">
    <h4 class="wid-t-danger">감사 로그로 구분 불가</h4>
    <div class="wid-muted">CloudTrail 호출자는 노드 역할 세션 하나입니다. 워크로드별 추적과 회수가 어렵습니다.</div>
    <div class="wid-cap wid-gap-top"><span class="rp-detail" data-detail="trail">CloudTrail에서 무엇이 보이나</span></div>
  </div>
  <div class="wid-card fragment fade-up" data-fragment-index="3">
    <h4 class="wid-t-danger">hop limit 2면 일반 Pod도 IMDS에 닿음</h4>
    <div class="wid-muted">hostNetwork가 아닌 Pod도 IMDSv2 토큰을 받아 노드 역할을 가져갑니다.</div>
    <div class="wid-cap wid-gap-top"><span class="rp-detail" data-detail="hop">hop limit이란</span></div>
  </div>
</div>
<div class="callout callout-info wid-gap-top fragment fade-up" data-fragment-index="4"><strong class="wid-t-info">목표</strong>: 앱 권한은 워크로드 전용 역할로 옮기고, 노드 역할에는 노드 운영에 필요한 권한만 남긴 뒤 Pod의 IMDS 경로를 닫습니다.</div>
:::

:::detail blast "권한 범위가 노드 단위가 되는 이유"
tip: 같은 노드에 스케줄되는 모든 Pod가 노드 역할 자격 증명을 받을 수 있습니다.

노드 역할은 노드 하나에 하나입니다. 스케줄러는 권한을 보고 Pod를 배치하지 않으므로, 앱 권한을 노드 역할에 붙이면 그 노드 그룹에 뜨는 모든 Pod가 같은 권한을 갖게 됩니다. 결제 Pod를 위한 S3 읽기가 로그 수집기와 배치 Job에도 열립니다.
:::

:::detail trail "CloudTrail의 호출자"
tip: 호출자는 노드 역할 세션(인스턴스 ID)으로만 보입니다.

EC2 인스턴스 프로파일로 받은 자격 증명의 세션은 노드 역할과 인스턴스 ID로 기록됩니다. 같은 노드의 Pod가 모두 같은 세션을 쓰므로 어느 워크로드가 호출했는지 로그만으로 구분하기 어렵습니다. S3 객체 접근을 CloudTrail에서 보려면 버킷의 데이터 이벤트도 켜야 합니다.
:::

:::detail hop "IMDS hop limit (HttpPutResponseHopLimit)"
tip: IMDSv2 토큰 응답이 넘을 수 있는 네트워크 홉 수

IMDSv2는 PUT 요청으로 세션 토큰을 먼저 받습니다. hop limit은 이 토큰 응답이 지날 수 있는 홉 수입니다. 일반 Pod는 노드와 다른 네트워크 namespace에 있어 한 홉이 더 필요하므로, 값이 2 이상이면 Pod도 토큰을 받습니다.

관리형 노드 그룹의 launch template이 이 값을 2로 두는 경우가 많습니다. 이전을 마친 뒤 1로 내려 일반 Pod의 경로를 닫습니다. `hostNetwork` Pod는 노드 네트워크를 그대로 쓰므로 hop limit과 관계없이 IMDS에 닿습니다.
:::

:::notes
{timing: 2min}
[요약]
- 위험 1: 권한 범위가 Pod가 아니라 노드 단위
- 위험 2: CloudTrail에서 워크로드를 구분할 수 없어 추적과 회수가 어려움
- 위험 3: hop limit 2(관리형 노드 그룹에서 흔한 값)면 hostNetwork가 아닌 일반 Pod도 IMDS에서 노드 역할을 받음
- 목표: 앱 권한을 워크로드 역할로, 노드 역할에는 노드 운영 권한만, 마지막에 IMDS 경로 차단

{cue: click}
첫째, 권한 범위가 노드 단위입니다. 스케줄러는 권한을 보고 Pod를 배치하지 않으니, 노드 역할에 붙인 권한은 그 노드에 뜨는 모든 Pod의 권한입니다.
{cue: click}
둘째, 감사입니다. 호출자가 노드 역할 세션 하나로 보여서 어느 앱이 무엇을 호출했는지, 무엇을 회수해도 되는지 판단하기 어렵습니다.
{cue: click}
셋째가 hop limit입니다. IMDSv2 토큰 응답이 넘을 수 있는 홉 수인데, 관리형 노드 그룹 launch template에서 2로 두는 경우가 많습니다. 2면 hostNetwork를 쓰지 않는 평범한 Pod도 토큰을 받아 노드 역할을 가져갑니다. 오늘 데모의 레거시 Pod도 바로 이 평범한 Pod입니다.
{cue: click}
그래서 목표는 세 단계입니다. 앱 권한을 워크로드 역할로 옮기고, 노드 역할에는 노드 운영 권한만 남기고, 마지막에 Pod의 IMDS 경로를 닫습니다.
{cue: transition}
옮길 곳이 어디인지, 자격 증명이 오는 세 경로를 먼저 보겠습니다.

[약어]
- IMDS: Instance Metadata Service, EC2 인스턴스 메타데이터 서비스
:::

---
<!-- Slide 5: 세 갈래 경로 -->
@type: content
@fit: off
@title: Pod의 자격 증명은 세 곳에서 온다

## Pod의 자격 증명은 세 곳에서 온다

:::html
<div class="wid-fig-row">
  <figure class="wid-fig">
    <img src="images/ko-security-17-eks-workload-identity-migration-anim-0.svg" alt="세 Pod가 자격 증명을 받는 경로. 노드 역할 Pod는 IMDSv2에서, IRSA Pod는 STS AssumeRoleWithWebIdentity에서, Pod Identity Pod는 같은 노드의 Pod Identity Agent와 EKS Auth를 거쳐 임시 자격 증명을 받고, 각자 받은 자격 증명으로 S3 요청에 서명한다.">
    <figcaption>파란 봉투는 자격 증명 요청, 초록 열쇠는 돌려받은 임시 자격 증명 (18초 반복)</figcaption>
  </figure>
  <div class="wid-stack fragment fade-up" data-fragment-index="1">
    <div class="wid-card wid-node wid-edge"><span class="wid-chip wid-node">node (IMDS)</span><div class="wid-muted">IMDSv2에서 노드 역할</div></div>
    <div class="wid-card wid-irsa wid-edge"><span class="wid-chip wid-irsa">IRSA (STS)</span><div class="wid-muted">IAM Roles for Service Accounts. Pod가 리전 STS(Security Token Service)를 직접 호출</div></div>
    <div class="wid-card wid-podid wid-edge"><span class="wid-chip wid-podid">Pod Identity</span><div class="wid-muted">같은 노드의 Agent가 EKS Auth 호출</div></div>
  </div>
</div>
:::

:::notes
{timing: 2min}
[요약]
- 경로 1: IMDSv2에서 노드 역할 (오늘 옮길 대상)
- 경로 2: IRSA, Pod가 리전 STS AssumeRoleWithWebIdentity를 직접 호출
- 경로 3: Pod Identity, 같은 노드의 Agent가 EKS Auth를 호출
- 세 경로 모두 결과는 임시 자격 증명이고, Pod는 그것으로 S3 요청에 서명

애니메이션이 세 줄을 차례로 보여 줍니다. 위 줄이 지금 상태, IMDS에서 노드 역할을 받는 경로입니다.
가운데가 IRSA입니다. Pod가 자기 토큰을 들고 리전 STS에 직접 가서 역할을 맡습니다. 아래가 Pod Identity로, Pod는 같은 노드의 Agent에만 말을 걸고 Agent가 EKS Auth를 부릅니다.
{cue: click}
오른쪽 세 칩의 색과 이름은 데모의 watch 화면 표기와 같습니다. 오늘 내내 노드는 노란색, IRSA는 파란색, Pod Identity는 분홍색으로 보겠습니다.
{cue: transition}
그러면 같은 코드가 어떻게 이 셋 중 하나를 고를까요. SDK의 자격 증명 체인입니다.
:::

---
<!-- Slide 6: 자격 증명 체인 캔버스 -->
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
이 체인 덕분에 이전은 결국 "무엇을 주입하느냐"의 문제가 됩니다.
:::

---
<!-- Slide 7: 주입되는 것 -->
@type: content
@title: 바뀌는 것은 코드가 아니라 주입된 변수

## 바뀌는 것은 코드가 아니라 주입된 변수

:::html
<table class="data-table wid-table fragment fade-up" data-fragment-index="1">
  <thead><tr><th>경로</th><th>Pod에 주입되는 것</th><th>SDK가 호출하는 곳</th><th>결과 역할</th></tr></thead>
  <tbody>
    <tr><td><span class="wid-chip wid-node">node (IMDS)</span></td><td>없음</td><td>IMDSv2 <code>169.254.169.254</code></td><td>노드 IAM 역할 (노드의 모든 Pod가 공유)</td></tr>
    <tr><td><span class="wid-chip wid-irsa">IRSA (STS)</span></td><td><code>AWS_ROLE_ARN</code>, <code>AWS_WEB_IDENTITY_TOKEN_FILE</code>, 토큰 볼륨</td><td>리전 STS <code>AssumeRoleWithWebIdentity</code></td><td>ServiceAccount 주석의 역할</td></tr>
    <tr><td><span class="wid-chip wid-podid">Pod Identity</span></td><td><code>AWS_CONTAINER_CREDENTIALS_FULL_URI</code>, <code>AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE</code>, 토큰 볼륨</td><td>같은 노드의 Agent <code>169.254.170.23</code></td><td>association에 지정한 역할</td></tr>
  </tbody>
</table>
<div class="wid-grid-2 wid-gap-top">
  <div class="callout callout-warning fragment fade-up" data-fragment-index="2"><strong class="wid-t-warning">주입은 Pod 생성 시점에만</strong>: 이미 실행 중인 Pod는 바뀌지 않으므로 설정 후 rollout으로 Pod를 새로 만듭니다.</div>
  <div class="callout callout-info fragment fade-up" data-fragment-index="3"><strong class="wid-t-info">확인은 호출자 ARN으로</strong>: 호출 성공만으로는 부족합니다. 노드 역할로 성공했을 수도 있습니다.</div>
</div>
:::

:::notes
{timing: 1.5min}
[요약]
- 노드 경로: 주입 없음, IMDS에서 노드 역할
- IRSA: AWS_ROLE_ARN, AWS_WEB_IDENTITY_TOKEN_FILE, 토큰 볼륨
- Pod Identity: AWS_CONTAINER_CREDENTIALS_FULL_URI, AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE, 토큰 볼륨
- 주입은 Pod 생성 때만 일어나므로 rollout 필요, 검증은 호출자 ARN으로

{cue: click}
표로 정리하면 이렇습니다. 노드 경로는 아무것도 주입되지 않고, IRSA와 Pod Identity는 서로 다른 환경 변수 두 개와 토큰 볼륨이 들어갑니다. 데모의 diff 단계에서 이 변수 이름을 실제 Pod에서 그대로 확인합니다.
{cue: click}
중요한 점은 주입이 Pod를 만들 때만 일어난다는 겁니다. 주석을 달거나 association을 만들어도 이미 떠 있는 Pod는 그대로라 rollout이 필요합니다.
{cue: click}
그리고 확인할 때는 API 호출이 성공했는지가 아니라 호출자 ARN이 무엇인지 봐야 합니다. 노드 역할에 권한이 남아 있으면 이전이 안 됐어도 성공하기 때문입니다.
{cue: transition}
그럼 이 변수를 누가, 언제 넣는지 보겠습니다.
:::

---
<!-- Slide 8: 누가 언제 주입하나 -->
@type: content
@title: 변수는 누가, 언제 넣나: API 서버의 mutating 웹훅

## 변수는 누가, 언제 넣나: API 서버의 mutating 웹훅

:::html
<div class="wid-grid-2">
<div>
<ol class="wid-flow">
  <li class="fragment fade-up" data-fragment-index="1"><strong>Pod 생성 요청</strong> <span class="wid-muted">rollout → ReplicaSet 컨트롤러가 API 서버에 Pod CREATE</span></li>
  <li class="fragment fade-up" data-fragment-index="1"><strong>인증·인가</strong> <span class="wid-muted">API 서버가 요청자를 확인</span></li>
  <li class="fragment fade-up wid-hl" data-fragment-index="2"><strong>Mutating admission: <code>iam-for-pods.amazonaws.com</code></strong><br><span class="wid-muted">EKS가 컨트롤 플레인에서 운영하는 웹훅(amazon-eks-pod-identity-webhook)이 Pod의 ServiceAccount를 봅니다.</span>
    <div class="wid-cap">association 있음 → <code>AWS_CONTAINER_*</code> 두 개 + 토큰 볼륨(aud <code>pods.eks.amazonaws.com</code>)<br>주석만 있음 → <code>AWS_ROLE_ARN</code>, <code>AWS_WEB_IDENTITY_TOKEN_FILE</code> + 토큰 볼륨(aud <code>sts.amazonaws.com</code>)<br>둘 다 있음 → Pod Identity만 · 아무것도 없음 → 그대로</div></li>
  <li class="fragment fade-up" data-fragment-index="3"><strong>Validating admission → etcd 저장</strong> <span class="wid-muted">Pod Security 등 검사 후 저장. 이때 Pod 스펙은 이미 바뀌어 있음</span></li>
  <li class="fragment fade-up" data-fragment-index="3"><strong>kubelet</strong> <span class="wid-muted">projected 토큰을 해당 audience로 발급받아 파일로 마운트하고 만료 전에 갱신</span></li>
  <li class="fragment fade-up" data-fragment-index="3"><strong>컨테이너 시작</strong> <span class="wid-muted">SDK가 환경 변수를 읽고 앞 슬라이드의 체인을 탑니다</span></li>
</ol>
</div>
<div>
<pre class="wid-term fragment fade-up" data-fragment-index="4"><span class="wid-dim"># 데모 클러스터에서 확인한 웹훅 설정</span>
$ kubectl get mutatingwebhookconfiguration \
    pod-identity-webhook -o yaml
name: iam-for-pods.amazonaws.com
clientConfig.url: https://127.0.0.1:23443/mutate
rules: CREATE pods
failurePolicy: Ignore
objectSelector: eks.amazonaws.com/skip-pod-identity-webhook 없음</pre>
<div class="callout callout-warning fragment fade-up" data-fragment-index="5"><strong class="wid-t-warning">CREATE에서만 동작</strong>: 실행 중인 Pod는 바뀌지 않습니다. 설정 뒤에는 rollout.</div>
<div class="callout callout-danger fragment fade-up" data-fragment-index="5"><strong>failurePolicy: Ignore</strong>: 웹훅이 응답하지 못하면 변수 없이 Pod가 만들어져 조용히 노드 역할로 동작합니다. 그래서 호출자 ARN으로 확인합니다.</div>
<div class="callout callout-info fragment fade-up" data-fragment-index="6"><strong class="wid-t-info">미리 확인</strong>: <code>kubectl create --dry-run=server</code>로 Pod 템플릿을 보내면 웹훅을 거친 결과를 Pod를 만들지 않고 볼 수 있습니다.</div>
</div>
</div>
<div class="wid-src">출처: 데모 클러스터(EKS 1.36)의 MutatingWebhookConfiguration, <a href="https://github.com/aws/amazon-eks-pod-identity-webhook">amazon-eks-pod-identity-webhook</a>, <a href="https://docs.aws.amazon.com/eks/latest/userguide/pod-id-how-it-works.html">Understand how EKS Pod Identity works</a></div>
:::

:::notes
{timing: 2min}
[요약]
- 변수를 넣는 주체: API 서버의 mutating admission 단계에서 EKS가 컨트롤 플레인에 운영하는 웹훅(iam-for-pods.amazonaws.com, amazon-eks-pod-identity-webhook). 노드에는 웹훅 Pod가 없음
- 시점: Pod CREATE 때만. ServiceAccount의 주석(IRSA)과 association(Pod Identity)을 보고 env와 토큰 볼륨을 패치
- 둘 다 있으면 Pod Identity만. kubelet은 토큰을 audience별로 발급·갱신
- failurePolicy Ignore라 웹훅 실패 시 변수 없이 생성 → 노드 역할. 호출자 ARN과 dry-run으로 확인

그럼 이 변수는 누가 언제 넣을까요?
{cue: click}
Pod를 만들면 요청이 API 서버로 갑니다. rollout이면 ReplicaSet 컨트롤러가 Pod CREATE를 보냅니다. API 서버는 먼저 인증과 인가를 합니다.
{cue: click}
그다음이 핵심인 mutating admission 단계입니다. EKS가 컨트롤 플레인 안에서 운영하는 웹훅이 있고, 이름이 iam-for-pods.amazonaws.com입니다. 이 웹훅이 Pod의 ServiceAccount를 보고, association이 있으면 Pod Identity 변수 두 개와 토큰 볼륨을, 주석만 있으면 IRSA 변수와 토큰 볼륨을 Pod 스펙에 끼워 넣습니다. 둘 다 있으면 Pod Identity만 넣습니다.
{cue: click}
그 뒤 검증을 거쳐 저장되고, kubelet이 Pod를 띄우면서 토큰을 해당 audience로 발급받아 파일로 마운트합니다. 컨테이너가 시작되면 SDK가 그 변수를 읽고 앞에서 본 체인을 탑니다.
{cue: click}
실제 데모 클러스터에서 웹훅 설정을 꺼내 보면 주소가 127.0.0.1, 즉 컨트롤 플레인 안입니다. 그래서 노드에서 kubectl get pods로 찾아도 보이지 않습니다.
{cue: click}
여기서 두 가지를 기억하면 됩니다. 규칙이 Pod CREATE뿐이라 이미 떠 있는 Pod는 rollout 전까지 바뀌지 않습니다. 그리고 failurePolicy가 Ignore라서, 웹훅이 응답하지 못하면 Pod는 변수 없이 그냥 만들어지고 조용히 노드 역할을 씁니다. 그래서 확인은 항상 호출자 ARN으로 합니다.
{cue: click}
미리 확인하고 싶으면 kubectl create --dry-run=server로 Pod 템플릿을 보내 보세요. 웹훅을 거친 결과가 돌아오니 Pod를 만들지 않고도 무엇이 주입될지 볼 수 있습니다. 데모 스크립트도 이 방법으로 association 반영을 기다립니다.
{cue: transition}
이제 두 방식의 내부를 한 단계씩 보겠습니다. IRSA부터입니다.
:::
