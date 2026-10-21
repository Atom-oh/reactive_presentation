# 세션 데모 코드 (D1, D2, D3)

`사례로 보는 AI 에이전트` 2부와 5부 데모의 코드와 실행 기록입니다. 데이터는 모두 가상이며, 결과는 1회 실행 값입니다. 자세한 수치와 조건은 [FACTS.md](FACTS.md)에 있습니다.

| 파일 | 내용 |
|---|---|
| `etf_data.py` | D1 가상 ETF 원장(SQLite, 코드값 저장) |
| `etf_ontology.ttl` | D1 온톨로지: OWL 클래스와 관계, SKOS 어휘(별칭, DB 조건), 업무 규칙 |
| `d1_grounding.py` | D1: 스키마만(A), 온톨로지 설명(B), 온톨로지 확정(C) 비교 |
| `d2_intent.py` | D2: 인텐트 직접 선택(A)과 Domain, Action, Tag 3속성 + 매칭(B) 비교 |
| `rec/` | 녹화 스크립트(asciinema driver, mp4 변환, D3 Playwright 화면 녹화) |
| `results/` | 녹화 회차 실행 결과 JSON |

## 실행

Amazon Bedrock 모델 접근 권한이 있는 AWS 자격 증명이 필요합니다. 별도 AWS 리소스는 만들지 않습니다.

```bash
pip install boto3 rdflib
export AWS_REGION=ap-northeast-2
python d1_grounding.py one --idx 0    # 질문 하나를 A, B, C로
python d1_grounding.py all --out results/d1-run.json
python d1_grounding.py clarify        # 사전에 없는 말: 되묻기
python d2_intent.py all --out results/d2-run.json   # 녹화 회차 기록: results/d2-run2-nova-micro.json
```

모델은 `D1_MODEL`, `D2_MODEL` 환경 변수로 바꿀 수 있습니다(기본값: Claude Haiku 4.5 global 추론 프로필, Amazon Nova Micro APAC 추론 프로필).
