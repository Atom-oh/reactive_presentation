# Auto Mode·Karpenter 빠르게 이해하기

처음 볼 때는 **관리 책임 → 설정 역할 → 노드 변화 → 진단 순서**만 잡으면 됩니다. 버전·API·전체 YAML은 [공식 자료 검토](version-update.md)를 참고하세요.

## 5분만 있다면 이 순서로 보세요

| 순서 | 답할 질문 | 슬라이드 |
|---|---|---|
| 1 | Pod가 기다리면 누가 노드를 준비하나? | [노드가 준비되는 과정](01-architecture.html#5) |
| 2 | NodePool과 NodeClass는 무엇이 다른가? | [허용 조건](01-architecture.html#6) · [AWS 생성 설정](01-architecture.html#7) |
| 3 | 조금 싸져도 Pod를 다시 띄울까? | [Consolidation 정책 비교](01-architecture.html#12) |
| 4 | Spot 회수 전에 준비가 끝나지 않으면? | [병행 대응과 두 가지 결과](02-node-lifecycle.html#6) |
| 5 | 기다릴 자리를 미리 준비할 수 있나? | [여유 용량의 원리](02-node-lifecycle.html#7) |

먼저 화면의 설명과 단계 버튼을 보세요. YAML은 접힌 상세 또는 별도 탭에서 확인합니다.

## 1. 누가 무엇을 하나요?

- **Pod**: 앱이 실행되는 단위입니다.
- **Node**: Pod가 실행되는 서버입니다.
- **Karpenter**: 스케줄되지 못한 Pod에 맞는 노드를 준비하고, 조건이 맞으면 불필요한 노드를 정리합니다.
- **Auto Mode**: AWS가 이 노드 관리 기능과 OS·주요 인프라 구성 요소를 관리합니다.
- **우리 팀**: 앱의 CPU·메모리 요청량, 배치 조건, 중단 허용 범위를 설계합니다.

[관리 책임 비교하기 →](01-architecture.html#4)

## 2. 비슷한 이름 세 가지를 구분하세요

| 이름 | 답하는 질문 | 예시 |
|---|---|---|
| NodePool | 어떤 노드를 허용하나? | Spot 허용, CPU 아키텍처, 인스턴스 계열 |
| NodeClass | AWS에서 어떻게 만드나? | subnet, 보안 그룹, 노드 역할, 디스크 |
| NodeClaim | 요청한 노드 한 대가 어디까지 준비됐나? | 생성·등록·Ready 상태 |

Karpenter는 노드를 준비하고, Kubernetes Scheduler가 Pod를 배치합니다. **Pending이라는 사실만으로 노드 부족을 단정하지 않습니다.**

[Pod → 노드 흐름 따라가기 →](01-architecture.html#5)

## 3. 노드가 줄거나 바뀌는 이유는 다릅니다

| 이유 | 쉬운 설명 |
|---|---|
| Consolidation | Pod를 재배치하고 불필요한 노드 정리 |
| Drift | 새 설정을 반영하기 위해 교체 |
| Expiration | 설정한 수명에 도달해 교체 시작 |
| Spot interruption | EC2가 Spot 용량 회수 |

Consolidation 정책도 구분합니다. `WhenEmpty`는 빈 노드, `WhenEmptyOrUnderutilized`는 가능한 비용 절감, `Balanced`는 **비용 절감과 Pod 중단 비용을 함께** 봅니다.

[상황별로 세 정책 비교하기 →](01-architecture.html#12)

### Spot 회수는 두 일을 함께 시작합니다

회수 통지를 받으면 **기존 노드의 Pod 종료 처리**와 **대체 노드 준비**를 병행합니다. Pod를 모두 종료한 뒤에야 새 노드를 만드는 순서로 외우지 마세요.

준비가 늦으면 기존 인스턴스가 회수된 뒤에도 앱이 기다릴 수 있습니다. PDB는 EC2 회수 기한을 늘리지 못합니다. 버퍼는 이 노드 대기를 줄이기 위한 여유 용량이며 유지 비용이 듭니다. 실제 앱이 쓰려면 우선순위·배치 조건이 맞아야 하고, 이미지 다운로드와 앱 초기화 시간도 필요합니다.

[Spot 결과 비교 →](02-node-lifecycle.html#6) · [버퍼 복원 과정 →](02-node-lifecycle.html#7)

## 4. 숫자는 의미와 함께 읽으세요

- **14일**: Auto Mode 기본 `expireAfter: 336h`.
- **24시간**: `terminationGracePeriod` 미지정 시 노드 종료 시작 후 기본 유예.
- **21일**: Auto Mode 노드의 최대 수명. 앞의 두 값을 더한 숫자가 아닙니다.

Drift·Spot·노드 정리로 더 일찍 교체될 수 있습니다. PDB는 Pod 중단을 제어하지만 Spot 회수 기한을 늘리지 못합니다.

[세 숫자를 구분하고 YAML 확인하기 →](02-node-lifecycle.html#8)

## 5. 문제가 생기면 이 순서로 확인하세요

1. **앱 상태**: Pod Events에 `FailedScheduling`이 있나요? 이미 노드에 배치됐다면 이미지·볼륨·앱 시작도 확인합니다.
2. **노드 상태**: NodeClaim의 생성·등록·Ready 단계 중 어디에서 멈췄나요?
3. **교체 이유**: 같은 노드·같은 시간의 이벤트가 앱 장애 시각과 맞나요?

[조회 명령과 결과 읽는 법 →](02-node-lifecycle.html#4)

최신 검토 기준은 **2026-10-07**입니다. EKS **1.37**, 직접 설치한 Karpenter **v1.14.1**을 확인했습니다. Karpenter 공식 호환성 표는 Kubernetes **1.37에 Karpenter 1.15.x**를 요구합니다 (2026-10-12 재확인). v1.14.1은 1.36까지 해당하므로, 1.37 클러스터에 직접 설치한다면 v1.15 업그레이드 안내를 먼저 확인합니다.

## 최신 내용 중 먼저 기억할 세 가지

| 내용 | 쉬운 설명 | 적용 범위 |
|---|---|---|
| Balanced | 절감 효과와 Pod를 다시 띄우는 부담을 함께 봄 | EKS 1.37의 새 Auto Mode 풀 기본값. 직접 설치한 Karpenter v1.14는 명시적으로 선택 |
| Capacity Buffers API | 여유 용량을 선언하는 별도 방식 | 직접 설치한 Karpenter v1.14에서 v1beta1. 더미 Pod 예제와 구분하며 Auto Mode 지원을 추정하지 않음 |
| Controller + CRD | 동작하는 프로그램과 설정 형식을 함께 업데이트 | 직접 설치한 Karpenter 업그레이드. Auto Mode에 Helm 업그레이드를 적용하는 절차가 아님 |

[릴리스·호환성·공식 출처 확인 →](version-update.md)
