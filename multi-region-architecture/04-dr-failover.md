---
remarp: true
block: 04-dr-failover
---

---
<!-- Slide 1: 블록 커버 (Section) -->
@type: section

# Block 4: DR & Failover Automation

전략 선택 → 장애 시나리오 → 자동화 파이프라인 → 훈련과 검증

:::notes
{timing: 0.5min}
[요약]
• Block 4의 질문: "us-east-1이 멈추면 쇼핑몰은 몇 분 안에, 얼마의 데이터를 잃고 돌아오는가"
• 순서: DR 전략과 RTO/RPO → 장애 시나리오 3개 → Aurora failover와 RPO 관리 → 자동화 → DB별 절차 → 로드맵, 훈련
• 기준일 2026-10-15, 모든 API와 수치는 AWS 공식 문서로 재확인

Block 4에서는 DR과 Failover 자동화를 다룹니다. 지금까지 본 order, payment, catalog, cart 서비스를 그대로 두고, us-east-1 primary와 us-west-2 secondary 구성에서 리전 장애가 났을 때 무슨 일이 일어나는지 따라가 보겠습니다.
{cue: pause}
전략과 목표치를 먼저 정하고, 장애 시나리오를 본 다음, 그 간극을 자동화와 훈련으로 메우는 순서입니다.
{cue: transition}
먼저 DR 전략 네 가지부터 정리하겠습니다.
:::

---
<!-- Slide 2: DR 전략 4단계 -->
@type: content
@title: DR 전략은 비용과 RTO의 교환

## DR 전략은 비용과 RTO의 교환

:::html
<style>
.mr04-strat .metric-card { display: flex; flex-direction: column; gap: var(--space-2); }
.mr04-tag { color: var(--accent); font-weight: var(--weight-bold); font-size: var(--fs-card); }
.mr04-muted { color: var(--text-secondary); font-size: var(--fs-card); word-break: keep-all; overflow-wrap: anywhere; }
.mr04-ok { color: var(--success); font-weight: var(--weight-bold); }
.mr04-info { color: var(--info); font-weight: var(--weight-bold); }
.mr04-warn { color: var(--warning); font-weight: var(--weight-bold); }
.mr04-bad { color: var(--danger); font-weight: var(--weight-bold); }
.mr04-axis { display: flex; justify-content: space-between; color: var(--text-secondary); font-size: var(--fs-card); margin: var(--space-2) 0 var(--space-4); border-top: 2px solid var(--border); padding-top: var(--space-2); }
</style>
<div class="card-grid mr04-strat" data-reveal="stagger" data-reveal-anim="right">
  <div class="metric-card"><strong class="mr04-info">Backup &amp; Restore</strong><span class="mr04-tag">RPO 시간 단위, RTO 24시간 이내</span><div class="mr04-muted">복구 리전에 백업만 둡니다. 장애 시 IaC로 인프라를 만들고 데이터를 복원합니다.</div></div>
  <div class="metric-card"><strong class="mr04-info">Pilot Light</strong><span class="mr04-tag">RPO 분 단위, RTO 수십 분</span><div class="mr04-muted">데이터 복제와 DB는 상시 가동, 애플리케이션 서버는 필요할 때 배포합니다.</div></div>
  <div class="metric-card"><strong class="mr04-warn">Warm Standby</strong><span class="mr04-tag">RPO 초 단위, RTO 분 단위</span><div class="mr04-muted">축소된 전체 스택이 항상 실행됩니다. 장애 시 확장 후 트래픽을 받습니다.</div></div>
  <div class="metric-card"><strong class="mr04-ok">Multi-site Active/Active</strong><span class="mr04-tag">RPO 거의 0, RTO 0에 근접</span><div class="mr04-muted">두 리전이 동시에 트래픽을 처리합니다. 비용과 데이터 일관성 설계 부담이 가장 큽니다.</div></div>
</div>
<div class="mr04-axis"><span>비용, 복잡도 낮음</span><span>RTO, RPO 짧음 →</span></div>
<div class="callout callout-info fragment zoom-in" data-fragment-index="1"><strong class="mr04-info">이 쇼핑몰의 선택</strong> order, payment, inventory는 Aurora Global Database, catalog, cart는 global cluster, Global Datastore. 모두 쓰기는 us-east-1 한 곳인 Warm Standby이고, 양 리전 쓰기(Active/Active)는 DSQL multi-Region을 택할 때의 선택지입니다.</div>
:::

:::notes
{timing: 2min}
[요약]
• Well-Architected REL13-BP02의 네 가지 전략, 오른쪽으로 갈수록 비용은 늘고 RTO/RPO는 줄어듦
• Backup & Restore: RPO 시간, RTO 24시간 이내 / Pilot Light: RPO 분, RTO 수십 분
• Warm Standby: RPO 초, RTO 분 / Active/Active: RPO 거의 0, RTO 0에 근접
• 이 쇼핑몰: 데이터 계층 전체가 Warm Standby (Aurora Global DB, DocumentDB global cluster, Global Datastore)
• 양 리전 쓰기와 RPO 0이 필요한 테이블만 DSQL multi-Region (Active/Active) 검토

AWS Well-Architected 신뢰성 원칙은 다중 리전 DR 전략을 네 가지로 나눕니다. 왼쪽 Backup & Restore는 가장 싸지만 RTO가 하루 이내, Pilot Light는 데이터만 상시 복제하고 앱은 필요할 때 띄웁니다.
Warm Standby는 축소된 전체 스택을 항상 돌리고, Active/Active는 두 리전이 동시에 트래픽을 받습니다.
{cue: pause}
우리 쇼핑몰은 Block 2에서 정한 대로 데이터 계층 전체가 Warm Standby입니다. order, payment, inventory는 Aurora PostgreSQL Global Database로, us-west-2 secondary가 로컬 읽기를 받고 쓰기는 write forwarding으로 us-east-1 primary에 보냅니다. catalog와 cart도 같은 단일 writer 구조입니다. RPO는 초 단위, RTO는 분 단위가 현실적인 목표입니다.
결제 원장처럼 양 리전 쓰기와 RPO 0이 꼭 필요한 테이블이 생기면, 그때 DSQL multi-Region이 Active/Active로 가는 경로가 됩니다. 이 선택이 나머지 슬라이드의 전제입니다.
{cue: transition}
그럼 서비스별로 지금 RTO와 RPO가 어떤 상태인지 보겠습니다.

[출처]
• REL13-BP02: https://docs.aws.amazon.com/wellarchitected/2024-06-27/framework/rel_planning_for_recovery_disaster_recovery.html
:::

---
<!-- Slide 3: RTO/RPO 매트릭스 -->
@type: content
@title: 서비스마다 RTO, RPO가 다르다

## 서비스마다 RTO, RPO가 다르다

| 서비스 | 데이터 스토어 (현재) | us-east-1 장애 시 | RPO 성격 | 전환 방식 |
|---|---|---|---|---|
| order, payment, inventory | Aurora PostgreSQL Global DB | us-west-2 읽기 유지, 쓰기 중단 | 계획 0, 비계획은 복제 lag만큼 | failover (allow-data-loss), global writer endpoint (앱 적용 필요) |
| catalog | DocumentDB global cluster | us-west-2 읽기 유지 | 초 단위 (비동기) | managed failover, 보통 1분 내 승격 |
| cart, session | ElastiCache (Valkey) Global Datastore | us-west-2 읽기 유지 | 복제 지연 보통 1초 미만 | 수동 promote, 보통 1분 미만 |
| 이벤트 | MSK, Replicator 미구성 | us-west-2에 이벤트 없음 | 미처리 이벤트가 us-east-1에 남음 | Replicator 구성 전에는 전환 불가 |
| 정적 자산 | S3 CRR + RTC | 복제본에서 읽기 | 99.99% 객체 15분 이내 설계 | CloudFront origin group |
| 컴퓨트 | 리전별 EKS 클러스터 | us-west-2 확장 | stateless | GitOps + 용량 확장 |

:::html
<style>
.mr04-bad { color: var(--danger); font-weight: var(--weight-bold); }
</style>
<div class="callout callout-danger fragment zoom-in" data-fragment-index="1"><strong class="mr04-bad">가장 약한 고리</strong> 이벤트 경로입니다. MSK Replicator가 없어 DB가 넘어가도 order.created 같은 미처리 이벤트는 us-east-1에 남습니다.</div>
:::

:::notes
{timing: 2.5min}
[요약]
• Aurora Global DB: 계획 switchover는 RPO 0, 비계획 failover는 그 순간의 복제 lag만큼 손실 (보통 초 단위)
• DocumentDB global cluster: RPO 초 단위, managed failover 시 보통 1분 내 secondary 승격
• ElastiCache Global Datastore: 복제 지연 보통 1초 미만, 자동 failover 없음, promote 보통 1분 미만
• MSK Replicator는 아직 미구성: 리전 장애 시 미처리 이벤트가 us-east-1에 갇힘 (로드맵 P0)
• S3 RTC는 99.99% 객체를 15분 내 복제하도록 설계, SLA는 99.9%

표의 숫자는 모두 AWS 문서에 나온 "보통" 값입니다. 우리 환경의 실측이 아니니 훈련에서 직접 재야 합니다.
맨 위 행부터 보면, order, payment, inventory는 Aurora PostgreSQL Global Database입니다. us-west-2 secondary가 읽기를 계속 받으니 조회는 살아 있지만, 쓰기는 primary가 승격될 때까지 멈춥니다. 계획된 switchover는 데이터 손실이 없고, 리전 장애 때 쓰는 failover는 그 순간의 복제 lag만큼을 잃습니다.
catalog의 DocumentDB global cluster도 비동기 복제라 RPO가 초 단위이고, managed failover를 하면 보통 1분 안에 secondary가 writer가 됩니다. cart의 ElastiCache Global Datastore는 복제가 보통 1초 미만이지만 자동 failover가 없어서 누군가 promote를 실행해야 합니다.
{cue: pause}
문제는 이벤트 행입니다. MSK Replicator가 아직 구성되지 않았습니다. 그래서 DB를 us-west-2로 넘겨도 us-east-1 broker에 쌓인 order.created 같은 미처리 이벤트는 따라오지 않고, 결제와 재고 후속 처리가 끊깁니다. Block 2에서 본 Replicator와 offset 동기화를 붙이는 것이 로드맵 P0입니다. 붙인 뒤에도 offset은 근사값이라 consumer는 멱등이어야 합니다. S3 RTC는 99.99%를 15분 안에 복제하도록 설계됐고 SLA는 99.9%입니다.
{cue: transition}
이 상태로 세 가지 장애 시나리오를 돌려 보겠습니다.

[출처]
• Aurora Global DB switchover, failover: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-disaster-recovery.html
• DocumentDB DR: https://docs.aws.amazon.com/documentdb/latest/devguide/global-clusters-disaster-recovery.html
• ElastiCache FAQ (자동 failover 없음, 1분 미만): https://aws.amazon.com/elasticache/faqs/
• MSK Replicator offset sync: https://docs.aws.amazon.com/msk/latest/developerguide/msk-replicator-bidirectional-offset-sync.html
• S3 RTC: https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication-add-config.html , https://aws.amazon.com/s3/faqs/
:::

---
<!-- Slide 4: 장애 시나리오 3개 (Tabs) -->
@type: tabs
@title: 장애는 세 가지 크기로 온다

## 장애는 세 가지 크기로 온다

### 리전 전체 장애
us-east-1 전체가 응답하지 않는 경우입니다.

| 계층 | 자동 | 사람이 결정 |
|---|---|---|
| 엣지 (CloudFront) | GET/HEAD/OPTIONS는 origin group으로 자동 재시도 | 쓰기 요청의 활성 리전 전환 |
| catalog (DocumentDB) | 없음 | failover-global-cluster 실행 |
| cart (ElastiCache) | 없음 | failover-global-replication-group 실행 |
| order, payment (Aurora Global DB) | 없음 | failover-global-cluster 실행 |

**결론**: 읽기는 살아남지만 주문, 결제는 DB 승격과 쓰기 리전 전환이 끝날 때까지 멈춥니다. 순서를 정한 Runbook이 필요합니다.

### 단일 DB 장애
리전은 정상이고 한 데이터 스토어만 문제인 경우입니다.

| 상황 | 먼저 할 일 |
|---|---|
| catalog 장애 | 캐시된 상품 정보로 읽기 전용 모드 |
| cart 장애 | 세션 쿠키와 DB로 장바구니 재구성, 쓰기는 재시도 큐 |
| 데이터 손상 (잘못된 쓰기) | 복제본에도 전파되므로 PITR, 스냅샷으로 복구 |
| 리전 전환 판단 | "DB 하나 때문에 모든 서비스를 옮길 가치가 있는가" |

**원칙**: 리전 전체 전환보다 해당 서비스만 degrade하는 것이 먼저입니다.

### EKS 클러스터 장애
노드, AZ 수준인지 클러스터 전체인지 먼저 구분합니다.

| 범위 | 대응 |
|---|---|
| 노드, AZ | Karpenter 노드 교체, ARC zonal shift로 해당 AZ 우회 |
| drain 중 | PodDisruptionBudget 없으면 replica가 동시에 빠질 수 있음 |
| 클러스터 전체 | GitOps로 같은 상태인 us-west-2 클러스터를 EKS resource scaling block으로 확장 |

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: order-api-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: order-api
```

:::notes
{timing: 3min}
[요약]
• 리전 장애: 읽기는 CloudFront origin group으로 넘어가지만 쓰기와 DB 승격은 사람이 결정
• 단일 DB 장애: 리전 전환보다 서비스별 degrade가 먼저, 데이터 손상은 복제로 못 막음
• EKS 장애: 노드, AZ는 Karpenter와 zonal shift, 클러스터 전체는 상대 리전 확장
• PDB가 없으면 drain 중 replica가 동시에 빠질 수 있음

첫 번째 탭, 리전 전체 장애입니다. CloudFront origin group은 GET, HEAD, OPTIONS만 secondary origin으로 재시도합니다. 그래서 상품 조회는 계속되지만 주문 POST는 넘어가지 않습니다. Aurora Global Database, DocumentDB, ElastiCache 모두 리전 간 승격은 자동이 아니라서 명령을 누군가 실행해야 합니다.
{cue: pause}
두 번째 탭은 DB 하나만 아플 때입니다. 이때 리전 전체를 옮기면 오히려 위험이 커집니다. 해당 서비스만 읽기 전용이나 캐시 응답으로 degrade하는 쪽이 먼저입니다. 그리고 잘못된 쓰기로 인한 데이터 손상은 복제가 막아주지 못합니다. 복제본에도 그대로 전파되니까요. 이건 PITR이나 스냅샷의 영역입니다.
세 번째 탭, EKS입니다. 노드나 AZ 장애는 Karpenter와 ARC zonal shift가 해결합니다. 클러스터 전체를 잃으면 us-west-2 클러스터를 키우는 쪽이고, 그러려면 GitOps로 두 클러스터 상태를 같게 유지해야 합니다.
{cue: question}
지금 운영 중인 Deployment에 PDB가 몇 개나 걸려 있는지 아시나요?
{cue: transition}
주문과 결제를 쥔 Aurora의 비계획 failover 절차부터 보겠습니다.

[출처]
• CloudFront origin failover 대상 메서드: https://aws.amazon.com/blogs/networking-and-content-delivery/building-multi-region-active-active-architectures-with-cloudfront-vpc-origins-and-advanced-routing/
• EKS resource scaling block: https://docs.aws.amazon.com/r53recovery/latest/dg/eks-resource-scaling-block.html
:::

---
<!-- Slide 5: Aurora 비계획 failover Runbook -->
@type: content
@title: Aurora failover는 쓰기부터 멈춘다

## Aurora failover는 쓰기부터 멈춘다

:::html
<style>
.mr04-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.mr04-sub { display: block; color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-1); word-break: keep-all; }
.mr04-ok { color: var(--success); font-weight: var(--weight-bold); }
.mr04-bad { color: var(--danger); font-weight: var(--weight-bold); }
.mr04-warn { color: var(--warning); font-weight: var(--weight-bold); }
.mr04-info { color: var(--info); font-weight: var(--weight-bold); }
.mr04-dg { display: grid; align-items: center; gap: var(--space-3); margin-bottom: var(--space-5); }
.mr04-node { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-3) var(--space-4); text-align: center; font-weight: var(--weight-semibold); word-break: keep-all; }
.mr04-node.mr04-key { border-color: var(--accent); }
.mr04-arrow { color: var(--text-secondary); font-size: var(--fs-subtitle); text-align: center; }
.mr04-dg5 { grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr; }
</style>
<div class="mr04-dg mr04-dg5" data-reveal="stagger" data-reveal-anim="right">
  <div class="mr04-node">1. 쓰기 중지<span class="mr04-sub">order, payment API 쓰기 차단</span></div>
  <div class="mr04-arrow">→</div>
  <div class="mr04-node">2. lag 기록<span class="mr04-sub">AuroraGlobalDBRPOLag로 손실 범위 추정</span></div>
  <div class="mr04-arrow">→</div>
  <div class="mr04-node mr04-key">3. failover<span class="mr04-sub">us-west-2에서 allow-data-loss</span></div>
  <div class="mr04-arrow">→</div>
  <div class="mr04-node">4. 쓰기 확인<span class="mr04-sub">global writer endpoint로 재개</span></div>
</div>
<div class="code-block fragment fade-up" data-fragment-index="1">aws rds failover-global-cluster --region us-west-2 \
  --global-cluster-identifier shop-global \
  --target-db-cluster-identifier "$USW2_ARN" --allow-data-loss</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="2">
  <div class="callout callout-danger"><strong class="mr04-bad">RPO는 0이 아니다</strong><div class="mr04-muted">동기화를 기다리지 않으므로 그 순간의 복제 lag만큼 잃습니다. 보통 초 단위입니다.</div></div>
  <div class="callout callout-warning"><strong class="mr04-warn">write fencing은 best effort</strong><div class="mr04-muted">old primary가 잠시 쓰기를 받을 수 있어 1단계가 필수입니다. DNS 캐시 TTL은 5초 수준으로 둡니다.</div></div>
  <div class="callout callout-success"><strong class="mr04-ok">연결 문자열은 그대로</strong><div class="mr04-muted">앱이 global writer endpoint를 쓰면 새 primary를 자동으로 가리킵니다. 단 parameter group, alarm은 상속되지 않습니다.</div></div>
</div>
:::

:::notes
{timing: 2min}
[요약]
• 비계획 failover 순서: 쓰기 중지 → RPO lag 기록 → us-west-2에서 failover-global-cluster --allow-data-loss → global writer endpoint로 쓰기 재개 확인
• 동기화를 기다리지 않으므로 RPO는 그 순간의 복제 lag, 보통 초 단위
• write fencing은 best effort: 앱 쓰기를 먼저 멈추고 DNS 캐시 TTL은 5초 수준
• global writer endpoint 덕분에 연결 문자열은 그대로, parameter group과 alarm은 새 primary에 다시 구성
• 원래 리전이 회복되면 secondary로 재합류, failback은 switchover로

Block 2에서 switchover와 failover의 차이를 봤으니, 여기서는 리전 장애가 난 날의 실제 순서를 정리합니다. 네 단계입니다.
첫째, order와 payment API의 쓰기를 먼저 막습니다. 둘째, 승격할 us-west-2 secondary의 AuroraGlobalDBRPOLag를 기록해 둡니다. 이 값이 이번 장애에서 잃을 수 있는 데이터의 범위이고, 나중에 대사할 때 기준이 됩니다.
{cue: pause}
셋째, failover-global-cluster를 allow-data-loss와 함께 실행합니다. region 옵션은 승격할 us-west-2입니다. 넷째, 앱이 global writer endpoint로 다시 쓸 수 있는지 확인합니다. 이 endpoint는 새 primary를 가리키니 연결 문자열은 바꾸지 않습니다.
왜 쓰기부터 멈추느냐. Aurora는 old primary의 쓰기를 막는 write fencing을 시도하지만 문서가 best effort라고 명시합니다. 막지 못하면 잠깐 두 리전이 쓰기를 받는 split-brain이 생길 수 있습니다. 그래서 문서도 앱 쓰기를 먼저 멈추고 DNS 캐시 TTL을 5초 정도로 낮추라고 권장합니다.
마지막 카드도 놓치기 쉽습니다. parameter group과 alarm은 새 primary로 따라오지 않으니 us-west-2 쪽에 미리 같은 구성을 만들어 두세요. us-east-1이 회복되면 Aurora가 secondary로 다시 붙이고, 원복은 switchover로 합니다.
{cue: transition}
그럼 그 "lag만큼의 손실"을 어떻게 제한하고, 잃은 것은 어떻게 찾을지 보겠습니다.

[출처]
• Aurora Global DB 비계획 failover 절차, write fencing, DNS TTL 5초, 파라미터 비상속: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-disaster-recovery.html
• Global writer endpoint: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-connecting.html
:::

---
<!-- Slide 6: RPO 관리와 유실분 대사 (Tabs) -->
@type: tabs
@title: RPO는 상한을 걸고 유실분은 대사한다

## RPO는 상한을 걸고 유실분은 대사한다

### RPO 상한
| 항목 | 내용 |
|---|---|
| 파라미터 | `rds.global_db_rpo` (Aurora PostgreSQL, 초 단위, 최솟값 20초) |
| 동작 | 모든 secondary의 RPO lag이 값을 넘으면 primary 커밋을 멈추고, 하나라도 따라잡으면 재개 |
| 관측 | `AuroraGlobalDBRPOLag` (ms) 알람으로 상한에 다가가는 것을 먼저 감지 |
| 2리전 주의 | secondary 쪽 parameter group은 기본값 유지: failover 직후 커밋 정지 방지 |
| 결정 | 커밋 가용성과 손실 상한 중 무엇을 택할지 결제 담당 팀과 합의 |

### 유실분 대사
| 단계 | 내용 |
|---|---|
| 스냅샷 | old primary 회복 시 `rds:unplanned-global-failover-...` 스냅샷 생성 시도 |
| 비교 | 스냅샷을 별도 클러스터로 복원해 새 primary에 없는 마지막 트랜잭션 확인 |
| 외부 원장 | PG 승인 내역과 대조해 주문 레코드 없는 승인 건 처리 |
| 재반영 | DynamoDB Global Tables의 idempotency key로 중복 없이 재처리 |

### 선택: DSQL multi-Region
| 항목 | 내용 |
|---|---|
| 구성 | peered cluster 2개 (us-east-1, us-west-2) + witness 리전 (us-east-2) |
| 얻는 것 | 두 리전 모두 쓰기, 동기 커밋으로 RPO 0, failover 명령 불필요 |
| 대가 | 쓰기마다 리전 간 왕복, OCC 충돌 재시도, 트랜잭션당 3,000 rows, 10 MiB 한도 |
| 적용 범위 | 기존 Aurora 앱 일괄 이관이 아니라 RPO 0이 필수인 원장 테이블부터 검토 |

:::notes
{timing: 2.5min}
[요약]
• rds.global_db_rpo: 모든 secondary가 상한을 넘으면 primary 커밋을 멈춰 손실 상한을 보장, 최솟값 20초, 동적 파라미터
• 리전 2개 구성이면 secondary 쪽 parameter group은 기본값 유지
• 유실분은 rds:unplanned-global-failover 스냅샷, PG 승인 내역, idempotency key로 찾아 재반영
• RPO 0이 필수라면 DSQL multi-Region (peered cluster 2개 + witness)이 선택지, 대가는 쓰기 지연과 트랜잭션 제약

failover의 RPO는 0이 아니라고 했습니다. 그렇다면 남은 일은 두 가지, 손실에 상한을 거는 것과 잃은 것을 찾는 것입니다.
첫 번째 탭, Aurora PostgreSQL은 rds.global_db_rpo 파라미터로 상한을 겁니다. 최솟값은 20초입니다. 모든 secondary의 lag이 이 값을 넘으면 primary가 커밋을 멈추고, 하나라도 따라잡으면 다시 커밋합니다. 손실 상한을 보장하는 대신 가용성을 내주는 장치라서, 결제 담당 팀과 어느 쪽을 택할지 합의해야 합니다. 그리고 우리처럼 리전이 둘뿐이면 secondary 쪽 parameter group에는 넣지 마세요. failover 직후 새 primary에는 따라올 secondary가 없어서 커밋이 멈출 수 있습니다.
{cue: pause}
두 번째 탭, 대사입니다. old primary가 회복되면 Aurora가 장애 시점의 스냅샷을 시도합니다. 이걸 별도 클러스터로 복원해 새 primary에 없는 마지막 트랜잭션을 찾고, PG 승인 내역과 맞춰 봅니다. 재반영은 idempotency key로 중복 없이 합니다. 이 절차가 없으면 "lag만큼 잃는다"는 말이 "얼마를 잃었는지 모른다"가 됩니다.
세 번째 탭은 선택지입니다. 결제 원장처럼 비계획 장애에서도 RPO 0이 꼭 필요하면 Aurora DSQL multi-Region을 검토합니다. 두 리전의 peered cluster가 모두 쓰기를 받고 witness 리전이 quorum에 참여하니 failover 명령이 없습니다. 대신 쓰기마다 리전 간 왕복이 붙고 OCC 재시도와 트랜잭션 한도를 받아들여야 하니, 전체 이관이 아니라 꼭 필요한 테이블부터 보세요.
{cue: transition}
DB 다음은 사용자가 들어오는 입구, 엣지입니다.

[출처]
• rds.global_db_rpo (20초부터), 2리전 권고, unplanned-global-failover 스냅샷: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-disaster-recovery.html
• Aurora DSQL multi-Region peered clusters, witness Region: https://docs.aws.amazon.com/aurora-dsql/latest/userguide/what-is-aurora-dsql.html
• DSQL 트랜잭션 한도: https://docs.aws.amazon.com/aurora-dsql/latest/userguide/CHAP_quotas.html
:::

---
<!-- Slide 7: 엣지 전환 -->
@type: content
@title: 입구는 CloudFront 하나로 고정

## 입구는 CloudFront 하나로 고정

:::html
<style>
.mr04-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.mr04-sub { display: block; color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-1); word-break: keep-all; }
.mr04-ok { color: var(--success); font-weight: var(--weight-bold); }
.mr04-warn { color: var(--warning); font-weight: var(--weight-bold); }
.mr04-info { color: var(--info); font-weight: var(--weight-bold); }
.mr04-dg { display: grid; align-items: center; gap: var(--space-3); margin-bottom: var(--space-5); }
.mr04-node { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-3) var(--space-4); text-align: center; font-weight: var(--weight-semibold); word-break: keep-all; }
.mr04-node.mr04-key { border-color: var(--accent); }
.mr04-arrow { color: var(--text-secondary); font-size: var(--fs-subtitle); text-align: center; }
.mr04-stack { display: flex; flex-direction: column; gap: var(--space-2); border: 1px dashed var(--border); border-radius: var(--radius-md); padding: var(--space-3); }
.mr04-stack-label { font-size: var(--fs-caption); color: var(--text-secondary); text-align: center; }
.mr04-dg7 { grid-template-columns: 1fr auto 1.3fr auto 1.6fr auto 1fr; }
</style>
<div class="mr04-dg mr04-dg7">
  <div class="mr04-node fragment fade-right" data-fragment-index="1">사용자<span class="mr04-sub">HTTPS</span></div>
  <div class="mr04-arrow fragment fade-right" data-fragment-index="2">→</div>
  <div class="mr04-node mr04-key fragment fade-right" data-fragment-index="2">CloudFront<span class="mr04-sub">Function + KeyValueStore</span></div>
  <div class="mr04-arrow fragment fade-right" data-fragment-index="3">→</div>
  <div class="mr04-stack fragment fade-right" data-fragment-index="3">
    <div class="mr04-stack-label">Origin group</div>
    <div class="mr04-node">VPC origin<span class="mr04-sub">us-east-1 internal ALB</span></div>
    <div class="mr04-node">VPC origin<span class="mr04-sub">us-west-2 internal ALB</span></div>
  </div>
  <div class="mr04-arrow fragment fade-right" data-fragment-index="4">→</div>
  <div class="mr04-node fragment fade-right" data-fragment-index="4">EKS<span class="mr04-sub">리전별 클러스터</span></div>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="5">
  <div class="callout callout-success"><strong class="mr04-ok">읽기: 자동 재시도</strong><div class="mr04-muted">primary origin이 오류를 내면 GET, HEAD, OPTIONS 요청은 secondary origin으로 재시도됩니다.</div></div>
  <div class="callout callout-warning"><strong class="mr04-warn">쓰기: 넘어가지 않음</strong><div class="mr04-muted">POST, PUT, DELETE는 origin failover 대상이 아닙니다. 활성 리전 값을 KeyValueStore에 두고 Function이 origin group을 고릅니다.</div></div>
  <div class="callout callout-info"><strong class="mr04-info">노출 범위</strong><div class="mr04-muted">ALB는 internal, 보안 그룹은 CloudFront VPC origin 쪽만 허용합니다. 컴퓨트에 public IP를 두지 않습니다.</div></div>
</div>
:::

:::notes
{timing: 2min}
[요약]
• 공개 진입점은 CloudFront 하나, origin은 VPC origin으로 연결한 리전별 internal ALB
• origin group failover는 GET, HEAD, OPTIONS만 대상
• 쓰기 요청의 활성 리전은 KeyValueStore 값으로 CloudFront Function이 선택
• 느린 origin은 failover되지 않으므로 origin timeout을 조정

트래픽 입구는 CloudFront 하나로 고정합니다. 각 리전의 ALB는 internal이고, CloudFront VPC origin으로 연결합니다. ALB 보안 그룹은 CloudFront VPC origin 쪽만 받도록 열어 둡니다.
{cue: pause}
origin group에 두 리전을 primary, secondary로 넣으면 읽기 요청은 오류 시 자동으로 넘어갑니다. 그런데 이 재시도는 GET, HEAD, OPTIONS에만 적용됩니다. 주문 POST는 넘어가지 않습니다.
그래서 AWS 블로그의 샘플처럼 활성 리전 값을 CloudFront KeyValueStore에 두고, viewer request Function이 어느 origin group을 쓸지 고르게 합니다. 리전 전환은 결국 이 값 하나를 바꾸는 일이 되고, 이게 다음 슬라이드의 자동화 대상입니다. 응답은 오지만 느린 origin은 오류로 보지 않으니 origin timeout도 함께 조정하세요.
{cue: transition}
그럼 이 전환을 누가, 어떤 순서로 실행하는지 보겠습니다.

[출처]
• CloudFront VPC origins + origin group + KVS: https://aws.amazon.com/blogs/networking-and-content-delivery/building-multi-region-active-active-architectures-with-cloudfront-vpc-origins-and-advanced-routing/
:::

---
<!-- Slide 8: 자동화 파이프라인 -->
@type: content
@title: 전환은 Region switch plan으로

## 전환은 Region switch plan으로

:::html
<style>
.mr04-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.mr04-sub { display: block; color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-1); word-break: keep-all; }
.mr04-ok { color: var(--success); font-weight: var(--weight-bold); }
.mr04-warn { color: var(--warning); font-weight: var(--weight-bold); }
.mr04-info { color: var(--info); font-weight: var(--weight-bold); }
.mr04-dg { display: grid; align-items: center; gap: var(--space-3); margin-bottom: var(--space-5); }
.mr04-node { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-3) var(--space-4); text-align: center; font-weight: var(--weight-semibold); word-break: keep-all; }
.mr04-node.mr04-key { border-color: var(--accent); }
.mr04-arrow { color: var(--text-secondary); font-size: var(--fs-subtitle); text-align: center; }
.mr04-stack { display: flex; flex-direction: column; gap: var(--space-2); border: 1px dashed var(--border); border-radius: var(--radius-md); padding: var(--space-3); }
.mr04-stack-label { font-size: var(--fs-caption); color: var(--text-secondary); text-align: center; }
.mr04-dg8 { grid-template-columns: 1fr auto 1fr auto 1.5fr auto 1fr; }
</style>
<div class="mr04-dg mr04-dg8">
  <div class="mr04-node fragment fade-right" data-fragment-index="1">CloudWatch alarm<span class="mr04-sub">또는 수동 실행</span></div>
  <div class="mr04-arrow fragment fade-right" data-fragment-index="2">→</div>
  <div class="mr04-node fragment fade-right" data-fragment-index="2">Manual approval<span class="mr04-sub">실행 승인</span></div>
  <div class="mr04-arrow fragment fade-right" data-fragment-index="3">→</div>
  <div class="mr04-stack fragment fade-right" data-fragment-index="3">
    <div class="mr04-stack-label">병렬 실행 (us-west-2)</div>
    <div class="mr04-node">EKS resource scaling</div>
    <div class="mr04-node">Aurora Global Database</div>
    <div class="mr04-node">DocumentDB global cluster</div>
    <div class="mr04-node">Lambda: ElastiCache promote</div>
  </div>
  <div class="mr04-arrow fragment fade-right" data-fragment-index="4">→</div>
  <div class="mr04-node mr04-key fragment fade-right" data-fragment-index="4">Custom Lambda<span class="mr04-sub">KVS 활성 리전 변경</span></div>
</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="5">
  <div class="callout callout-success"><strong class="mr04-ok">활성화 리전에서 실행</strong><div class="mr04-muted">Region switch는 리전별 data plane을 두고, 활성화하는 리전에서 plan을 실행합니다. 장애 리전에 의존하지 않습니다.</div></div>
  <div class="callout callout-info"><strong class="mr04-info">기본 제공 block</strong><div class="mr04-muted">EC2 ASG, ECS, EKS, Aurora Global Database, DocumentDB, Neptune, RDS replica, ARC routing control, Route 53 health check 등.</div></div>
  <div class="callout callout-warning"><strong class="mr04-warn">없는 것은 Lambda로</strong><div class="mr04-muted">ElastiCache Global Datastore와 CloudFront KVS 변경은 custom Lambda block으로 넣습니다.</div></div>
</div>
:::

:::notes
{timing: 2.5min}
[요약]
• ARC Region switch: plan, workflow, step, execution block 구조, CloudWatch alarm으로 자동 실행 가능
• plan은 활성화하는 리전의 data plane에서 실행되어 장애 리전에 의존하지 않음
• 기본 block: ASG, ECS, EKS scaling, Aurora Global, DocumentDB, Neptune, RDS, routing control, Route 53 health check, 승인
• Aurora Global Database block: graceful은 지정한 기본 동작, ungraceful에 Failover (data loss) 지정 시 AllowDataLoss로 failover
• ElastiCache와 CloudFront KVS는 custom Lambda block으로 처리

예전 자료는 CloudWatch, EventBridge, Lambda를 직접 엮는 구조였는데, 지금은 ARC Region switch가 이 오케스트레이션을 관리형으로 제공합니다. plan 안에 workflow가 있고, step마다 execution block을 순차나 병렬로 실행합니다. CloudWatch alarm을 트리거로 붙이면 자동 실행도 됩니다.
{cue: pause}
가장 중요한 설계 포인트는 실행 위치입니다. Region switch는 활성화하는 리전, 우리 경우 us-west-2에서 plan을 실행합니다. 장애가 난 us-east-1의 control plane에 기대지 않습니다.
우리 plan은 승인 단계 다음에 EKS 용량 확장, Aurora Global Database failover, DocumentDB failover, ElastiCache promote를 병렬로 돌리고, 마지막에 CloudFront KVS의 활성 리전 값을 바꿉니다. Aurora block은 graceful 실행이면 기본 동작으로 고른 switchover를, ungraceful 실행에 Failover (data loss)를 지정해 두면 AllowDataLoss를 켠 failover를 호출합니다. 앞 슬라이드 Runbook의 1단계인 쓰기 중지는 승인 직후 step으로 두거나, 리전 전체 장애라면 이미 쓰기가 실패하는 상태임을 확인하고 넘어갑니다. ElastiCache와 KVS는 기본 block이 없어서 custom Lambda block을 씁니다. Region switch로 다 표현되지 않는 복잡한 분기는 Step Functions를 Lambda에서 호출하는 방식으로 확장할 수 있습니다.
{cue: question}
자동 실행과 승인 단계 중 무엇을 기본으로 둘지, 여러분 조직은 누가 그 버튼을 누를 권한이 있나요?
{cue: transition}
custom Lambda 코드를 보겠습니다.

[출처]
• Region switch 개요: https://docs.aws.amazon.com/r53recovery/latest/dg/region-switch.html
• Aurora Global Database execution block: https://docs.aws.amazon.com/r53recovery/latest/dg/aurora-global-database-block.html
• Execution block 목록 (ExecutionBlockConfiguration): https://docs.aws.amazon.com/sdk-for-ruby/v3/api/Aws/ARCRegionswitch/Types/ExecutionBlockConfiguration.html
• 출시 블로그 (리전별 data plane): https://aws.amazon.com/blogs/aws/introducing-amazon-application-recovery-controller-region-switch-a-multi-region-application-recovery-service/
:::

---
<!-- Slide 9: Failover Lambda 코드 -->
@type: content
@title: Lambda는 재실행해도 안전하게

## Lambda는 재실행해도 안전하게

```python
import boto3
GDS, RG, REGION = "<global-datastore-id>", "cart-usw2", "us-west-2"
ec = boto3.client("elasticache", region_name=REGION)  # 승격할 리전

def handler(event, context):
    g = ec.describe_global_replication_groups(GlobalReplicationGroupId=GDS,
        ShowMemberInfo=True)["GlobalReplicationGroups"][0]
    if any(m["ReplicationGroupId"] == RG and m["Role"].lower() == "primary"
           for m in g["Members"]):
        return {"status": "already-primary"}    # 재실행해도 안전
    # Status로 막지 않음: 리전 장애 중에는 available이 아닐 수 있음
    ec.failover_global_replication_group(
        GlobalReplicationGroupId=GDS, PrimaryRegion=REGION,
        PrimaryReplicationGroupId=RG)
    return {"status": "failover-started"}
```

:::html
<style>
.mr04-info { color: var(--info); font-weight: var(--weight-bold); }
</style>
<div class="callout callout-info fragment zoom-in" data-fragment-index="1"><strong class="mr04-info">세 파라미터 필수, 상태로 막지 않는다</strong> 장애 중에는 Status가 available이 아닐 수 있어 "이미 primary인가"만 확인합니다.</div>
:::

:::notes
{timing: 2min}
[요약]
• failover_global_replication_group은 GlobalReplicationGroupId, PrimaryRegion, PrimaryReplicationGroupId 세 개가 필수
• 대상 리전에서 client를 만들어 장애 리전 API에 의존하지 않음
• 실행 전 현재 primary를 확인해 재실행 시에도 안전 (멱등성)
• Global Datastore Status를 전제 조건으로 두지 않음: primary 리전 장애 중에는 available이 아닐 수 있음
• 진행 중 작업과 충돌하면 API 오류가 그대로 올라가 plan이 재시도하거나 사람이 판단

이 Lambda는 Region switch의 custom Lambda block에서 호출되는 ElastiCache promote 함수입니다. 세 가지를 신경 썼습니다.
첫째, CLI 문서 기준으로 Global Datastore 이름, 새 primary 리전, 새 primary replication group ID 세 개가 모두 필수입니다. 예전 자료 예제에는 마지막 값이 빠져 있었습니다.
{cue: pause}
둘째, boto3 client를 승격할 us-west-2에서 만듭니다. 장애 리전의 API endpoint에 의존하지 않기 위해서입니다.
셋째, 멱등성입니다. 자동화는 재시도되기 마련이라, 대상이 이미 primary면 아무것도 하지 않고 성공을 반환합니다.
하나 더, 이전 버전은 Global Datastore의 Status가 available이 아니면 예외를 던졌습니다. 그런데 정작 primary 리전이 멈춘 상황에서는 Status가 available이 아닐 수 있고, 그러면 가장 필요한 순간에 failover가 막힙니다. 그래서 Status로 막지 않고 바로 failover를 요청합니다. 다른 작업과 충돌하면 API 오류가 그대로 올라가 plan이 재시도하거나 사람이 판단합니다. 환경 변수 읽기, 구조화 로그, SNS 알림은 화면에서 뺐지만 프로덕션 코드에는 넣으세요.
{cue: transition}
DocumentDB는 기본 block이 있지만, 그 안에서 무슨 일이 일어나는지는 알아야 합니다.

[출처]
• failover-global-replication-group: https://docs.aws.amazon.com/cli/latest/reference/elasticache/failover-global-replication-group.html
• Custom Lambda execution block: https://docs.aws.amazon.com/r53recovery/latest/dg/region-switch.html
:::

---
<!-- Slide 10: DocumentDB 전환 (Tabs) -->
@type: tabs
@title: DocumentDB 장애는 failover로

## DocumentDB 장애는 failover로

### Switchover (계획)
정상 상태의 global cluster에서 primary 리전을 옮깁니다. 훈련, 리전 순환, failover 후 원복에 씁니다.

```bash
aws docdb switchover-global-cluster \
  --region us-east-1 \
  --global-cluster-identifier mall-catalog-global \
  --target-db-cluster-identifier arn:aws:rds:us-west-2:<ACCOUNT>:cluster:catalog-usw2
```

모든 secondary가 동기화될 때까지 기다린 뒤 전환하므로 **데이터 손실이 없습니다.** 모든 리전의 engine version이 같아야 하고, 역할 전환은 수 분까지 걸릴 수 있습니다.

### Failover (비계획)
primary 리전 장애 시 secondary를 승격합니다. 명령은 **승격할 리전**에서 실행합니다.

```bash
aws docdb failover-global-cluster \
  --region us-west-2 \
  --global-cluster-identifier mall-catalog-global \
  --target-db-cluster-identifier arn:aws:rds:us-west-2:<ACCOUNT>:cluster:catalog-usw2 \
  --allow-data-loss
```

실행 전 `GlobalClusterReplicationLag`(ms)가 가장 작은 secondary를 고릅니다. 보통 1분 안에 승격되며 복제되지 않은 쓰기는 유실될 수 있습니다. 이전 primary는 회복 후 자동으로 secondary로 재합류합니다.

### 전환 후 점검
| 점검 항목 | 내용 |
|---|---|
| writer endpoint | 바뀜: 앱이 새 endpoint를 쓰는지 확인 |
| parameter group, alarm | **상속되지 않음**: 새 primary에 다시 구성 |
| 다른 secondary | 재구축에 수 분에서 수 시간 |
| 유실분 | `rds:docdb-unplanned-global-failover-...` snapshot을 수동 snapshot으로 복사 |
| 원복 | 원래 리전 회복 후 switchover로 수행 |

:::notes
{timing: 2min}
[요약]
• switchover는 계획된 전환, 동기화 후 실행되어 데이터 손실 없음
• failover는 --allow-data-loss, 승격할 secondary 리전에서 실행
• 승격 대상은 GlobalClusterReplicationLag가 가장 작은 secondary
• parameter group과 alarm은 상속되지 않고, 원복은 switchover로

예전 자료는 장애 상황에서도 switchover를 쓰라고 했는데, 문서 기준으로 switchover는 정상 클러스터용입니다. 모든 secondary가 따라잡을 때까지 기다리기 때문에 primary가 죽은 상황에서는 맞지 않습니다.
{cue: pause}
장애 때는 failover-global-cluster에 allow-data-loss를 붙입니다. 이 명령은 승격할 리전, 즉 us-west-2를 region으로 지정해 실행합니다. 복제 지연 지표가 가장 작은 secondary를 고르고, 보통 1분 안에 승격됩니다.
세 번째 탭은 사람들이 놓치는 부분입니다. writer endpoint가 바뀌고, parameter group과 alarm은 따라오지 않습니다. 이전 primary의 마지막 상태는 시스템 snapshot으로 남는데, 백업 보존 기간이 지나면 사라지니 수동 snapshot으로 복사해 두세요. 이 모든 과정은 Region switch의 DocumentDB block이 graceful이면 switchover, ungraceful이면 failover로 실행합니다.
{cue: transition}
cart의 ElastiCache는 어떻게 다를까요.

[출처]
• DocumentDB global cluster DR: https://docs.aws.amazon.com/documentdb/latest/devguide/global-clusters-disaster-recovery.html
• DocumentDB execution block: https://docs.aws.amazon.com/r53recovery/latest/dg/documentdb-global-cluster-block.html
:::

---
<!-- Slide 11: ElastiCache promotion -->
@type: content
@title: cart 캐시는 사람이 승격한다

## cart 캐시는 사람이 승격한다

:::html
<style>
.mr04-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.mr04-sub { display: block; color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-1); word-break: keep-all; }
.mr04-ok { color: var(--success); font-weight: var(--weight-bold); }
.mr04-warn { color: var(--warning); font-weight: var(--weight-bold); }
.mr04-dg { display: grid; align-items: center; gap: var(--space-3); margin-bottom: var(--space-5); }
.mr04-node { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md); padding: var(--space-3) var(--space-4); text-align: center; font-weight: var(--weight-semibold); word-break: keep-all; }
.mr04-node.mr04-key { border-color: var(--accent); }
.mr04-arrow { color: var(--text-secondary); font-size: var(--fs-subtitle); text-align: center; }
.mr04-stack { display: flex; flex-direction: column; gap: var(--space-2); border: 1px dashed var(--border); border-radius: var(--radius-md); padding: var(--space-3); }
.mr04-stack-label { font-size: var(--fs-caption); color: var(--text-secondary); text-align: center; }
.mr04-dg11 { grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr; }
</style>
<div class="mr04-dg mr04-dg11" data-reveal="stagger" data-reveal-anim="right">
  <div class="mr04-node">1. 쓰기 차단<span class="mr04-sub">cart API read-only</span></div>
  <div class="mr04-arrow">→</div>
  <div class="mr04-node mr04-key">2. promote 실행<span class="mr04-sub">us-west-2를 primary로</span></div>
  <div class="mr04-arrow">→</div>
  <div class="mr04-node">3. endpoint 전환<span class="mr04-sub">앱 설정 갱신</span></div>
  <div class="mr04-arrow">→</div>
  <div class="mr04-node">4. 재합류 확인<span class="mr04-sub">이전 primary는 secondary</span></div>
</div>
<div class="code-block fragment fade-up" data-fragment-index="1">aws elasticache failover-global-replication-group \
  --global-replication-group-id &lt;global-datastore-name&gt; \
  --primary-region us-west-2 \
  --primary-replication-group-id cart-usw2</div>
<div class="card-grid fragment" data-reveal="stagger" data-fragment-index="2">
  <div class="callout callout-warning"><strong class="mr04-warn">자동 failover 없음</strong><div class="mr04-muted">Global Datastore는 리전 장애 시 스스로 승격하지 않습니다. 승격은 보통 1분 미만입니다.</div></div>
  <div class="callout callout-warning"><strong class="mr04-warn">전환 중 cart</strong><div class="mr04-muted">secondary는 읽기 전용이라 담기, 수정이 실패합니다. 클라이언트에서 재시도 큐로 받습니다.</div></div>
  <div class="callout callout-success"><strong class="mr04-ok">유실 대비</strong><div class="mr04-muted">복제 지연은 보통 1초 미만. 마지막 변경분은 세션 쿠키나 주문 DB에서 재구성합니다.</div></div>
</div>
:::

:::notes
{timing: 2min}
[요약]
• Global Datastore는 자동 failover가 없고, promote는 보통 1분 미만
• 순서: 쓰기 차단 → promote → endpoint 전환 → 이전 primary의 secondary 재합류 확인
• 전환 중 secondary는 읽기 전용이라 cart 쓰기 실패, 재시도 큐로 흡수
• secondary 리전은 최대 2개

ElastiCache Global Datastore는 FAQ에 명시된 대로 자동으로 failover하지 않습니다. 사람이든 자동화든 누군가 promote를 실행해야 하고, 승격은 보통 1분 미만에 끝납니다.
순서는 네 단계입니다. cart API를 읽기 전용으로 돌려 쓰기를 막고, us-west-2를 primary로 승격하고, 앱이 새 primary endpoint를 쓰게 바꾼 뒤, 이전 primary가 secondary로 재합류했는지 확인합니다.
{cue: pause}
전환 중에는 secondary가 읽기 전용이라 장바구니 담기가 실패합니다. 클라이언트에서 재시도 큐로 받아 주면 사용자는 몇 초 지연만 느낍니다. 복제 지연이 보통 1초 미만이라 유실은 작지만 0은 아니니, 세션 쿠키나 주문 DB로 재구성하는 경로를 둡니다. 참고로 Global Datastore는 primary 외에 최대 두 개의 secondary 리전을 둘 수 있습니다.
{cue: transition}
이제 지금까지의 간극을 우선순위로 정리하겠습니다.

[출처]
• ElastiCache FAQ: https://aws.amazon.com/elasticache/faqs/
• Global Datastore 기능 (secondary 2개, 1초 미만 복제): https://aws.amazon.com/elasticache/features/
• CLI: https://docs.aws.amazon.com/cli/latest/reference/elasticache/failover-global-replication-group.html
:::

---
<!-- Slide 12: DR 개선 로드맵 -->
@type: content
@title: 로드맵: 데이터 먼저, 자동화 다음

## 로드맵: 데이터 먼저, 자동화 다음

:::html
<style>
.mr04-road { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-5); }
.mr04-road .metric-card { display: flex; flex-direction: column; gap: var(--space-3); }
.mr04-pri { font-size: var(--fs-subtitle); font-weight: var(--weight-bold); }
.mr04-road ul { margin: 0; padding-left: var(--space-5); color: var(--text-secondary); font-size: var(--fs-card); line-height: var(--leading-body); word-break: keep-all; }
.mr04-road li + li { margin-top: var(--space-2); }
.mr04-bad { color: var(--danger); }
.mr04-warn { color: var(--warning); }
.mr04-info { color: var(--info); }
.mr04-note { margin-top: var(--space-5); }
.mr04-muted { color: var(--text-secondary); font-size: var(--fs-card); }
</style>
<div class="mr04-road">
  <div class="metric-card fragment fade-right" data-fragment-index="1"><span class="mr04-pri mr04-bad">P0 데이터 보호</span><ul><li>MSK Replicator 구성 (us-west-2), consumer offset 동기화</li><li>Aurora RPO lag 알람, rds.global_db_rpo 정책, global writer endpoint 적용</li><li>failover 유실분 대사 절차 (스냅샷, PG 승인 대조)</li></ul></div>
  <div class="metric-card fragment fade-right" data-fragment-index="2"><span class="mr04-pri mr04-warn">P1 전환 자동화</span><ul><li>Region switch plan: 승인, EKS scaling, Aurora Global DB, DocumentDB block</li><li>custom Lambda: ElastiCache promote, CloudFront KVS 변경</li><li>전 서비스 PodDisruptionBudget</li></ul></div>
  <div class="metric-card fragment fade-right" data-fragment-index="3"><span class="mr04-pri mr04-info">P2 검증 루프</span><ul><li>분기별 FIS 훈련과 Region switch 리허설</li><li>Resilience Hub 평가를 CI/CD에 연결</li><li>실측 RTO/RPO로 목표표 갱신</li><li>RPO 0 필수 테이블은 DSQL multi-Region 검토</li></ul></div>
</div>
<div class="callout callout-info mr04-note fragment fade-up" data-fragment-index="4"><strong class="mr04-info">숫자는 비워 둔다</strong> <span class="mr04-muted">"자동화로 RTO 2분" 같은 목표는 P2 훈련에서 잰 값으로 채웁니다.</span></div>
:::

:::notes
{timing: 1.5min}
[요약]
• P0: 데이터를 잃지 않는 것이 먼저, MSK Replicator 구성, Aurora RPO 상한 정책, 유실분 대사 절차
• P1: 전환을 사람의 기억이 아니라 plan으로, Region switch (Aurora, DocumentDB block)와 custom Lambda
• P2: 검증 루프, FIS 훈련과 Resilience Hub 평가로 실측값 확보, RPO 0 필수 테이블은 DSQL multi-Region 검토

로드맵은 세 단계입니다. 우선순위의 원칙은 "자동화보다 데이터가 먼저"입니다. 아무리 빨리 전환해도 order와 payment 데이터가 없으면 의미가 없으니까요.
{cue: pause}
P0에서 데이터 경로를 닫습니다. 아직 없는 MSK Replicator를 붙여 이벤트가 us-east-1에 갇히지 않게 하고, Aurora의 RPO lag 알람과 rds.global_db_rpo 정책을 정하고 앱을 global writer endpoint로 옮기고, failover 후 유실분을 대사하는 절차를 만듭니다. P1에서 Region switch plan으로 전환을 문서가 아닌 실행 가능한 계획으로 만듭니다. P2는 그 계획이 실제로 작동하는지 계속 증명하는 루프이고, 그 결과 RPO 0이 꼭 필요한 테이블이 확인되면 DSQL multi-Region을 검토합니다.
예전 자료의 "자동화로 RTO 15분에서 2분" 같은 숫자는 근거가 없어 뺐습니다. 목표치는 P2 훈련에서 잰 실측값으로 채우세요.
{cue: transition}
마지막 단계, 훈련과 검증 도구를 보겠습니다.
:::

---
<!-- Slide 13: FIS 훈련과 Resilience Hub (Tabs) -->
@type: tabs
@title: 훈련 없는 DR은 가설일 뿐

## 훈련 없는 DR은 가설일 뿐

### AZ: Power Interruption
FIS scenario library의 시나리오로, 한 AZ의 전원 손실 증상을 주입합니다.

| 항목 | 내용 |
|---|---|
| 대상 | EC2 (EKS, ECS 노드 포함), EBS, ASG, 서브넷, ElastiCache, RDS |
| 용량 제약 재현 | 지정한 IAM role, ASG의 새 인스턴스 시작을 막아 "용량 확보 실패"까지 시험 |
| 관찰 지표 | Karpenter 노드 교체, zonal shift, DB writer 이동 시간 |
| 주기 (예시) | 월 1회 비운영, 분기 1회 운영: 조직 기준으로 조정 |

### Cross-Region: Connectivity
실험 리전에서 대상 리전으로 가는 트래픽을 막고 복제를 멈춥니다. 기본 지속 시간 3시간(`disruptionDuration`).

| Action | 효과 |
|---|---|
| `aws:network:route-table-disrupt-cross-region-connectivity` | 서브넷의 대상 리전 경로 차단 |
| `aws:network:transit-gateway-disrupt-cross-region-connectivity` | TGW 경유 트래픽 차단 |
| `aws:s3:bucket-pause-replication` | S3 복제 일시 정지 |
| `aws:dynamodb:global-table-pause-replication` | Global Table 복제 정지 |

AWS 관리형 서비스 트래픽은 막히지 않을 수 있습니다. DocumentDB, ElastiCache 복제는 이 시나리오로 끊기지 않으니 별도로 검증합니다.

### Region switch 리허설
| 단계 | 내용 |
|---|---|
| 실행 | 분기 1회 plan을 실제로 실행해 us-west-2로 전환, switchover로 원복 |
| 측정 | 감지까지, 승인까지, 전환 완료까지 시간과 유실 데이터 |
| 장애 중 전환 | FIS로 장애를 주입한 상태에서 plan 실행 |
| 회고 | PIR로 기록하고 Runbook과 plan을 함께 갱신 |

### Resilience Hub
| 기능 | 내용 |
|---|---|
| Resiliency policy | Application, Infrastructure, Availability Zone, Region별 RTO/RPO 목표 |
| Assessment | 구성 요소를 분석해 목표 충족, 위반과 추정 RTO/RPO 표시 |
| Recommendations | 개선안별 예상 RTO, RPO, 비용과 alarm, FIS 실험, SOP 제안 |
| CI/CD 연동 | 구성 변경이 목표를 깨는지 배포 전에 확인 |

:::notes
{timing: 2.5min}
[요약]
• AZ: Power Interruption은 한 AZ 전원 손실을 주입, 용량 확보 실패까지 재현 가능
• Cross-Region: Connectivity는 리전 간 경로 차단과 S3, DynamoDB 복제 정지, 기본 3시간
• Region switch 리허설로 실제 전환 시간을 측정하고 switchover로 원복
• Resilience Hub는 장애 유형별 RTO/RPO 정책으로 평가하고 개선안 제시

첫 번째 탭, AZ Power Interruption은 한 AZ의 전원을 뽑은 상황을 흉내 냅니다. 특정 IAM role이나 ASG가 새 인스턴스를 못 띄우게 막는 옵션이 있어서, "장애 AZ 밖에서 용량을 확보하지 못하는" 상황까지 시험할 수 있습니다. 주기는 예시이니 조직 기준으로 정하세요.
두 번째 탭은 리전 간 연결 차단입니다. 라우트 테이블과 TGW 경로를 막고 S3, DynamoDB 복제를 멈춥니다. 단, AWS 관리형 서비스 트래픽은 막히지 않을 수 있어서 DocumentDB나 ElastiCache의 복제는 이걸로 끊어지지 않습니다. 이 부분은 착각하기 쉽습니다.
{cue: pause}
세 번째 탭, Region switch 리허설은 실제로 plan을 돌려 us-west-2로 갔다가 switchover로 돌아오는 훈련입니다. 감지, 승인, 전환 완료 시간을 따로 재야 어디가 병목인지 보입니다.
네 번째 탭, Resilience Hub는 장애 유형별 RTO/RPO 정책을 정하고 앱이 그걸 지키는지 평가합니다. 개선안과 함께 alarm, FIS 실험, SOP까지 제안하니, CI/CD에 붙여 구성 변경이 목표를 깨는지 배포 전에 잡으세요.
{cue: transition}
이번 블록을 정리하겠습니다.

[출처]
• FIS 시나리오 출시: https://aws.amazon.com/blogs/aws/use-aws-fault-injection-service-to-demonstrate-multi-region-and-multi-az-application-resilience/
• Cross-Region: Connectivity: https://docs.aws.amazon.com/fis/latest/userguide/cross-region-scenario.html
• Action 목록: https://aws.amazon.com/blogs/mt/scaling-aws-fault-injection-service-across-your-organization-and-regions/
• Resilience Hub RTO/RPO: https://docs.aws.amazon.com/help-panel/resilience-hub/latest/console/assessment-report-rto.html
• Resilience Hub 추천: https://aws.amazon.com/blogs/publicsector/track-application-resiliency-in-public-sector-organizations-using-aws-resilience-hub/
:::

---
<!-- Slide 14: Key Takeaways -->
@type: content
@title: Key Takeaways

## Key Takeaways

:::html
<style>
.mr04-muted { color: var(--text-secondary); font-size: var(--fs-card); margin-top: var(--space-2); word-break: keep-all; overflow-wrap: anywhere; }
.mr04-tk { color: var(--accent); font-weight: var(--weight-bold); }
.mr04-ok { color: var(--success); font-weight: var(--weight-bold); }
.mr04-warn { color: var(--warning); font-weight: var(--weight-bold); }
</style>
<div class="card-grid fragment" data-reveal="stagger" data-reveal-anim="zoom" data-reveal-pace="slow" data-fragment-index="1">
  <div class="metric-card"><strong class="mr04-tk">1. 기본은 단일 writer</strong><div class="mr04-muted">지금은 전부 단일 writer Warm Standby. RPO 0이 필수인 테이블만 DSQL Active/Active를 검토합니다.</div></div>
  <div class="metric-card"><strong class="mr04-tk">2. 가장 약한 고리가 RTO, RPO</strong><div class="mr04-muted">MSK Replicator가 없으면 DB가 넘어가도 이벤트는 남습니다. Aurora failover는 lag만큼 잃고 rds.global_db_rpo로 상한을 둡니다.</div></div>
  <div class="metric-card"><strong class="mr04-tk">3. 엣지는 읽기만 자동</strong><div class="mr04-muted">CloudFront origin failover는 GET, HEAD, OPTIONS만. 쓰기는 KVS의 활성 리전 값으로 전환합니다.</div></div>
  <div class="metric-card"><strong class="mr04-ok">4. 전환은 plan으로</strong><div class="mr04-muted">Region switch는 활성화 리전에서 실행됩니다. 기본 block이 없는 단계는 멱등 Lambda로 채웁니다.</div></div>
  <div class="metric-card"><strong class="mr04-ok">5. 명령을 구분</strong><div class="mr04-muted">Aurora, DocumentDB 장애는 쓰기 중지 후 failover + allow-data-loss, 계획 전환과 원복은 switchover. ElastiCache는 수동 promote.</div></div>
  <div class="metric-card"><strong class="mr04-warn">6. 숫자는 훈련으로</strong><div class="mr04-muted">FIS 시나리오와 Region switch 리허설로 실측한 RTO/RPO만 목표표에 씁니다.</div></div>
</div>
:::

:::notes
{timing: 1.5min}
[요약]
• 단일 writer Warm Standby, 가장 약한 고리 (MSK Replicator 미구성, Aurora failover RPO), 엣지의 읽기 전용 자동 failover
• Region switch plan과 멱등 Lambda
• Aurora, DocumentDB는 failover와 switchover 구분, ElastiCache 수동 promote
• 목표 수치는 훈련 실측값으로

여섯 가지로 정리합니다. 지금 데이터 계층은 모두 단일 writer Warm Standby이고, RPO 0이 꼭 필요한 테이블만 DSQL을 검토합니다. 전체 RTO와 RPO는 가장 약한 고리가 결정합니다. 지금은 미구성인 MSK Replicator, 그리고 lag만큼 잃는 Aurora failover입니다. 엣지는 읽기만 자동으로 넘어갑니다.
{cue: pause}
전환은 사람의 기억이 아니라 Region switch plan으로 실행하고, 기본 block이 없는 단계는 재실행에 안전한 Lambda로 채웁니다. Aurora와 DocumentDB는 쓰기를 멈춘 뒤 장애 때 failover, 계획 전환과 원복은 switchover입니다. 마지막으로, 목표표의 숫자는 훈련에서 잰 값만 씁니다.
{cue: transition}
퀴즈로 확인해 보겠습니다.
:::

---
<!-- Slide 15: Knowledge Check -->
@type: quiz
@title: Knowledge Check

## Knowledge Check

**Q1: us-east-1 장애 시 DocumentDB global cluster를 us-west-2로 넘기는 올바른 방법은?**
- [ ] us-east-1에서 switchover-global-cluster 실행
- [x] us-west-2에서 failover-global-cluster를 --allow-data-loss와 함께 실행
- [ ] 자동으로 승격되므로 아무것도 하지 않음

**Q2: CloudFront origin group이 secondary origin으로 재시도하는 요청은?**
- [x] GET, HEAD, OPTIONS 요청만
- [ ] 주문 POST를 포함한 모든 요청

**Q3: us-east-1 장애로 Aurora Global Database를 failover했을 때 맞는 설명은?**
- [ ] switchover처럼 데이터 손실이 없다
- [x] 그 순간의 복제 lag만큼 잃을 수 있고, rds.global_db_rpo로 상한을 둘 수 있다

:::notes
{timing: 1.5min}
[요약]
• Q1: 장애 시는 승격할 리전에서 failover + allow-data-loss, switchover는 정상 클러스터용
• Q2: origin failover는 GET, HEAD, OPTIONS만 대상
• Q3: Aurora failover는 lag만큼 손실 가능, rds.global_db_rpo로 상한, global writer endpoint로 연결 문자열 유지

세 문제입니다. 1번은 DocumentDB 명령 구분, 2번은 엣지의 한계, 3번은 Aurora failover의 RPO입니다.
{cue: poll}
1번 정답은 us-west-2에서 failover와 allow-data-loss입니다. switchover는 모든 secondary 동기화를 기다리기 때문에 primary가 죽은 상황에는 맞지 않습니다. 2번은 GET, HEAD, OPTIONS만 재시도되니 주문 POST는 넘어가지 않습니다. 3번은 lag만큼 잃을 수 있다는 것입니다. 데이터 손실이 없는 것은 계획된 switchover뿐입니다. 덧붙여 global writer endpoint를 쓰면 failover 후에도 연결 문자열은 바꾸지 않습니다.
틀린 문항은 "DocumentDB 장애는 failover로", "입구는 CloudFront 하나로 고정", "Aurora failover는 쓰기부터 멈춘다" 슬라이드로 돌아가 확인하세요.
:::

---
<!-- Slide 16: Thank You -->
@type: thankyou
@toc: toc.html
@next: 05-observability-ops.html
@next-label: 다음: Observability & Operations
@message: Block 4: DR & Failover Automation 완료

# Thank You

Block 4: DR & Failover Automation 완료

:::notes
{timing: 0.5min}
[요약]
• Block 4 완료: 전략, 시나리오, Aurora failover와 RPO, 엣지, Region switch, DB별 절차, 훈련
• Q&A 후 5분 휴식, 다음은 Block 5 Observability & Operations

Block 4를 마칩니다. 데이터 경로를 먼저 닫고, 전환은 plan으로, 숫자는 훈련으로 증명한다는 세 가지를 기억해 주세요.
{cue: question}
질문 있으시면 지금 받겠습니다. 잠시 쉬고 Block 5에서 이 전환을 어떻게 관측하고 운영하는지 이어가겠습니다.
{cue: break}
:::
