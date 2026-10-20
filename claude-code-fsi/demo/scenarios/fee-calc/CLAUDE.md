# fee-calc 사내 코딩 표준 (증권 IT)

- 금액 계산은 반드시 `decimal.Decimal`을 쓴다. `float` 금지.
- 원 미만은 항목별로 **절사**(ROUND_DOWN)한다. 수수료와 세금을 따로 절사한 뒤 더한다.
- 매수/매도 구분은 숫자 코드(1, 2)가 아니라 `Side` Enum으로 표현한다.
- 요율은 코드에 직접 쓰지 않고 모듈 상단 상수로 둔다 (FEE_RATE, MIN_FEE, SELL_TAX_RATE).
- 기존 호출부 호환: `calc(qty, price, side)` 시그니처와 반환값(총액, 원)은 유지한다. side는 `Side` 또는 기존 코드 1, 2를 받는다.
- 공개 함수는 타입 힌트와 한국어 docstring을 단다.
- `customer-data/` 아래 실고객 파일은 읽지 않는다. 테스트 데이터는 직접 만든다.
- 작업이 끝나면 `python3 -m pytest -q`가 전부 통과해야 완료로 보고한다.
- 답변과 작업 보고는 한국어로 짧게 쓴다.
