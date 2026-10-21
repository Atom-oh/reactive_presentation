# 데모 기록 (2026-10-21)

모든 데이터(ETF 상품, 운용사, 카드 인텐트, 고객 발화)는 이 데모용 가상 데이터입니다. 모든 수치는 1회 실행 결과이며 벤치마크가 아닙니다.
실행 환경: 작업 PC, Amazon Bedrock Converse API, ap-northeast-2 엔드포인트, temperature 0. 별도 AWS 리소스는 만들지 않았습니다.

## D1: 온톨로지 Grounding (d1_grounding.py, 영상 media/d1-grounding.mp4)

- 모델: `global.anthropic.claude-haiku-4-5-20251001-v1:0`
- 데이터: 가상 ETF 22개(`etf_data.py`), 코드값 저장(`ast_cls='BD_OVS_GOV'`, `thm_cd='T_BATT'`, `fee_bp` 단위 bp)
- 온톨로지: `etf_ontology.ttl` (OWL 클래스 6, 관계 5, SKOS 개념 12, 업무 규칙 5)
- 질문 12개, 모드별 1회 호출. 정답 판정: 생성 SQL 실행 결과가 정답 SQL 결과와 같은지(값 집합, 행 수)
- 녹화 회차(2026-10-21T13:22:34Z, `results/d1-run.json`): **A 스키마만 6/12 (50.0%), B 온톨로지 설명 4/12 (33.3%), C 온톨로지 확정 11/12 (91.7%)**
- 이전 두 회차(같은 날, 12:30Z 녹화본 포함)도 같은 점수(A 6, B 4, C 11). 터미널 프롬프트 이름을 바꾸려고 13:22Z에 다시 녹화
- B가 틀린 방식: 개념 이름을 DB 값처럼 사용 (`thm_cd IN ('미국국채','US Treasury','미 국채','미국채')`, `ast_cls IN ('국고채', ...)`)
- C가 틀린 1건(Q12 코스피200): 어휘에 없는 말이라 SQL 대신 `CLARIFY`로 되물음. A는 `prd_nm LIKE '%코스피200%'`로 정답
- 되묻기 확인: "친환경 ETF 중 보수가 낮은 걸 추천해줘" → Grounding 확정 용어 없음 → C 응답 `CLARIFY: ...`
- 영상: asciinema 녹화 73.6초 → agg(idle 2초 제한) mp4 61초, 1920x1836, 무음

## D2: 3속성 인텐트 분류 (d2_intent.py, 영상 없음)

- 모델: `apac.amazon.nova-micro-v1:0`, 인텐트 20개, 발화 40개
- 1차(속성 정의 초안): A 직접 선택 24/40 (60.0%), B 3속성 + 매칭 23/40 (57.5%). 원인: 보기 설명과 속성 정의가 모호("한도 올려줘"가 신청인지 변경인지, A는 설명 문구를 이름 대신 출력)
- 2차(설명과 속성 정의 수정, `results/d2-run2-nova-micro.json`): **A 40/40 (100.0%), B 24/40 (60.0%)**, 평균 지연 A 0.31초, B 0.41초
- B 오답 대부분: Domain 단독 판단 오류(결제 내역을 명세서로) 또는 Tag 누락. 속성 3개를 따로 고르면 오류가 곱해짐
- 해석: 인텐트 20개, 설명이 분명한 경우 소형 모델도 목록에서 바로 잘 고름. 발화 세트를 설명과 같은 사람이 만들어 쉬운 편. 신한카드 효과는 51개 세분 인텐트, 문맥 유사 쌍, sLLM 제약 조건에서 보고된 값

## D3: assembly.whchoi.net 화면 녹화 (rec/d3-site.py, 영상 media/d3-assembly.mp4)

- 2026-10-21 12:38Z, Playwright Chromium recordVideo 1920x1080, 73.6초, 무음. 커서와 단계 자막(노란 띠)만 덧붙임
- 화면 확인 값: Object Explorer "31 클래스 · 31 구현", Person "306 인스턴스", 관계 그래프 1-hop "8 노드 · 7 엣지"(김태년 의원), 그래프 페이지 설명 "depth=1은 즉각 응답(in-memory), depth ≥ 2는 Neptune Cypher multi-hop traversal", 데스크 챗봇 "10 도구 · Sonnet 4.6", 에이전트 진행 5단계(agentic, planner, graph, analyst, editor)
- 녹화 영상에서 표결 노드 라벨 "가결"의 자모가 분리되어 보임. 사이트 API 응답에는 분해 자모 없음(`result":"passed"`), 그래프 라벨 렌더링이 헤드리스 Chromium 폰트 환경에서 깨진 것으로 판단
- 2-hop 화면(김태년 의원): 공동발의 의원, 그 의원의 위원회와 발의 의안이 추가됨. 새 주제 노드는 없음(자막 ⑤의 "다른 주제까지"는 부정확)
- 자막 시각: ① 0초 ② 12초 ③ 16초 ④ 24초 ⑤ 32초 ⑥ 44초 ⑦ 48초 ⑧ 60초

## 문서 확인 (2026-10-21)

- Neptune: property graph(Gremlin, openCypher)와 RDF(SPARQL) 지원. https://docs.aws.amazon.com/neptune/latest/userguide/intro.html
- Bedrock Knowledge Bases GraphRAG: Neptune Analytics 사용, 데이터 소스는 S3만, 그래프 빌드 설정 커스터마이즈 미지원. 리전: Frankfurt, London, Ireland, Oregon, N. Virginia, Tokyo, Singapore(서울 없음). https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-build-graphs.html
