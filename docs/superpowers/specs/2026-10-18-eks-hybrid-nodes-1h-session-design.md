# EKS Hybrid Nodes 1시간 세션 (데모 영상 포함) 설계

날짜: 2026-10-18, 상태: 승인된 설계 (채팅에서 승인)

## 목적

기존 `eks-hybrid-nodes/` 덱은 2시간 Deep Dive로 남기고, 개념과 아키텍처 중심의 1시간 세션을 새로 만든다. 데모는 라이브 대신 무음 HyperFrames 영상으로 넣어 시간과 실패 위험을 없앤다.

## 결정 사항 (사용자)

| 항목 | 결정 |
|---|---|
| 길이와 레벨 | 60분, L200, 청중은 아키텍트와 의사결정자 |
| 범위 | 개념, 아키텍처, 선택 기준. YAML, 명령어, 설치 절차 같은 상세 설정은 제외하고 Deep Dive로 안내 |
| 데모 | 4편 모두 HyperFrames 영상, 무음 + 화면 텍스트, 설명은 발표자 노트 |
| 위치 | 새 폴더 `eks-hybrid-nodes-1h/`. 기존 `eks-hybrid-nodes/`는 URL 유지, 제목과 허브 카드만 "Deep Dive (2시간)"로 변경 |

## 구성 (약 28장)

| 부 | 시간 | 슬라이드 |
|---|---|---|
| 1. 왜 하이브리드인가 | 4분 | 표지, 고객 시나리오(데이터 위치 규정, 기존 투자, 엣지 저지연, GPU), 한 줄 정의, 아젠다 |
| 2. 개념과 아키텍처 | 12분 | 전체 아키텍처, 책임 분담(AWS와 고객), 요금 모델, 지원 OS와 노드 준비, 자격 증명 선택(SSM과 IAM RA, hover 카드) |
| 3. 네트워킹 | 13분 | 필수 연결과 CIDR, Pod 라우팅 3가지(static, BGP, Gateway)와 선택 기준, Gateway 동작(리더와 스탠바이), CNI 선택(Cilium 단독과 VPC CNI 혼합), 트래픽 방향(LB 진입, 역방향), cross-AZ 비용과 대용량 경로의 BGP |
| 4. 운영 | 8분 | 노드 라이프사이클(nodeadm, Bottlerocket은 개념만), 업그레이드, 네트워크 단절 시 동작, 버스팅 전략 개념 |
| 5. 데모 영상 | 16분 | 시뮬레이션 환경 소개, 영상 4편(각 영상 슬라이드 + 결과 요약 슬라이드), Istio 공존 결과 1장 |
| 6. 마무리 | 7분 | 도입 판단 체크리스트, Deep Dive와 데모 저장소 안내, 참고 자료와 Q&A, Thank you |

슬라이드 내용은 Deep Dive 덱의 검증된 그림, 표, 사실을 가져와 개념 수준으로 줄인다. 새 사실을 추가하지 않는다. 수치는 Deep Dive 5부와 `~/eks-hybrid-demo/results/`의 실측값만 쓴다.

## 데모 영상

| ID | 주제 | 길이 | 데이터 출처 |
|---|---|---|---|
| V1 | Gateway 리더 전환: Lease 이동, VPC 라우트 ENI 교체, 끊김 3~5초 | 약 2.5분 | RUNBOOK 1절, 데모 1 측정 3회 |
| V2 | bursting과 pod-deletion-cost: 스케일 아웃, 스케일 인 시 A/B/C에서 Pod가 남는 위치 | 약 3.5분 | `results/compare-20261015-1239.md` |
| V3 | ALB ip 타깃과 역방향: 타깃 교체 54초 실패 0, 리더 전환 191건 중 1건, 온프렘 경로 3가지 | 약 3분 | `results/lb-20261018-0211.json` |
| V4 | hybrid GPU 추론: device plugin GPU 1, sidecar 없는 vLLM, 클라우드에서 호출 약 1초 | 약 2분 | RUNBOOK 3절 |

- 형식: 1920×1080 mp4, 무음. 터미널 장면, 흐름도, 수치 카드로 구성한 재구성 영상. 화면에 "실측 결과 재구성 (2026-10 시뮬레이션 환경)"을 표기한다.
- 위치: 소스 `eks-hybrid-nodes-1h/videos/<id>/`(HyperFrames 프로젝트), 렌더 결과 `eks-hybrid-nodes-1h/media/<id>.mp4`. 슬라이드에는 `<video controls preload="metadata">`로 넣고, 포스터 이미지를 둔다.
- 영상당 파일 크기 목표 25MB 이하(GitHub Pages 배포).

## 파일

- `eks-hybrid-nodes-1h/`: `_presentation.md`, 블록 md(한 흐름, 블록 수는 생성기 편의로 정함), 생성된 html, `index.html`(통합본), `common/`(Deep Dive의 `common/` 복사), `media/`, `videos/`
- `eks-hybrid-nodes/`: `_presentation.md` 제목, 01 표지 부제에 "Deep Dive (2시간)" 반영 후 재빌드(`rebuild_all.py`)
- 루트 `index.html`: 기존 카드 이름 변경, 1시간 세션 카드 추가

## 검증

- 슬라이드: 헤드리스 Chrome 스크린샷으로 슬라이드마다 넘침과 깨짐 확인, em dash와 가운데 점 금지, 내용은 한국어(기술 용어는 영어)
- 영상: HyperFrames check, 렌더 후 프레임 샘플 확인, 수치가 출처와 일치하는지 대조
- content-review-agent 점수 85 이상
- PR로 올림(현재 PR #5 브랜치 위의 새 브랜치 `feat/eks-hybrid-nodes-1h-2026-10-18`)

## 범위 밖

- 라이브 데모, 내레이션과 자막, 퀴즈, 새 측정
