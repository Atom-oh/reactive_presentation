"""D1 데모용 가상 ETF 원장. 상품, 운용사, 코드값은 모두 가상입니다.

실제 사내 원장처럼 컬럼과 값이 코드로 저장되어 있어, 사용자가 쓰는 말
("미국국채", "2차전지", "배당")과 DB 값이 바로 맞지 않습니다.
"""
import sqlite3

DDL = """
CREATE TABLE mgr (            -- 운용사
  mgr_cd TEXT PRIMARY KEY,    -- 운용사코드
  mgr_nm TEXT                 -- 운용사명
);
CREATE TABLE brnd (           -- ETF 브랜드
  brnd_cd TEXT PRIMARY KEY,   -- 브랜드코드
  brnd_nm TEXT,               -- 브랜드명
  mgr_cd  TEXT REFERENCES mgr(mgr_cd)
);
CREATE TABLE etf_mst (        -- ETF 상품 원장
  isin      TEXT PRIMARY KEY, -- 상품코드
  prd_nm    TEXT,             -- 상품명
  brnd_cd   TEXT REFERENCES brnd(brnd_cd),
  ast_cls   TEXT,             -- 자산분류코드
  rgn_cd    TEXT,             -- 투자지역코드
  thm_cd    TEXT,             -- 테마코드 (없으면 NULL)
  fee_bp    INTEGER,          -- 총보수
  dist_yld  REAL,             -- 분배율
  dist_freq TEXT,             -- 분배주기
  nav_ek    INTEGER           -- 순자산
);
"""

MGR = [("M01", "가람자산운용"), ("M02", "누리자산운용"), ("M03", "다온자산운용")]
BRND = [("B01", "SKY", "M01"), ("B02", "RIVER", "M02"), ("B03", "STONE", "M03"), ("B04", "PINE", "M01")]

# isin, 상품명, 브랜드, 자산분류, 지역, 테마, 총보수(bp), 분배율(%), 분배주기, 순자산(억원)
ETF = [
    ("KR7A00001", "SKY 미국채10년", "B01", "BD_OVS_GOV", "US", None, 9, 3.9, "M", 8200),
    ("KR7A00002", "RIVER 미국채30년액티브", "B02", "BD_OVS_GOV", "US", None, 15, 4.3, "M", 5400),
    ("KR7A00003", "STONE 미국단기채", "B03", "BD_OVS_GOV", "US", None, 5, 4.1, "M", 3100),
    ("KR7A00004", "PINE 미국회사채", "B04", "BD_OVS_CORP", "US", None, 20, 5.2, "M", 2600),
    ("KR7A00005", "SKY 국고채10년", "B01", "BD_DOM_GOV", "KR", None, 7, 3.1, "Q", 6100),
    ("KR7A00006", "RIVER 국고채3년", "B02", "BD_DOM_GOV", "KR", None, 4, 2.9, "Q", 4300),
    ("KR7A00007", "SKY 코스피200", "B01", "EQ_DOM", "KR", None, 5, 1.8, "Q", 52000),
    ("KR7A00008", "RIVER 코스피200", "B02", "EQ_DOM", "KR", None, 3, 1.9, "Q", 61000),
    ("KR7A00009", "STONE 코스닥150", "B03", "EQ_DOM", "KR", None, 12, 0.4, "Y", 9800),
    ("KR7A00010", "SKY 2차전지산업", "B01", "EQ_DOM", "KR", "T_BATT", 45, 0.2, "Y", 14500),
    ("KR7A00011", "RIVER K배터리소재", "B02", "EQ_DOM", "KR", "T_BATT", 39, 0.1, "Y", 7700),
    ("KR7A00012", "PINE 글로벌리튬", "B04", "EQ_OVS", "GL", "T_BATT", 49, 0.3, "Y", 3200),
    ("KR7A00013", "SKY 미국S&P500", "B01", "EQ_OVS", "US", None, 7, 1.2, "Q", 48000),
    ("KR7A00014", "STONE 미국나스닥100", "B03", "EQ_OVS", "US", None, 9, 0.6, "Q", 39000),
    ("KR7A00015", "PINE 미국배당다우존스", "B04", "EQ_OVS", "US", "T_DIV", 10, 3.6, "M", 21000),
    ("KR7A00016", "RIVER 고배당주", "B02", "EQ_DOM", "KR", "T_DIV", 25, 5.8, "Q", 6800),
    ("KR7A00017", "SKY 필라델피아반도체", "B01", "EQ_OVS", "US", "T_SEMI", 49, 0.2, "Y", 17500),
    ("KR7A00018", "STONE K반도체", "B03", "EQ_DOM", "KR", "T_SEMI", 30, 0.5, "Y", 8800),
    ("KR7A00019", "PINE 금현물", "B04", "CMD_GOLD", "GL", None, 39, 0.0, "N", 9100),
    ("KR7A00020", "RIVER 골드선물", "B02", "CMD_GOLD", "GL", None, 68, 0.0, "N", 2200),
    ("KR7A00021", "STONE WTI원유선물", "B03", "CMD_OIL", "GL", None, 70, 0.0, "N", 1500),
    ("KR7A00022", "SKY 커버드콜월배당", "B01", "EQ_OVS", "US", "T_DIV", 39, 9.8, "M", 11000),
]


def build(path=":memory:"):
    con = sqlite3.connect(path)
    con.executescript(DDL)
    con.executemany("INSERT INTO mgr VALUES (?,?)", MGR)
    con.executemany("INSERT INTO brnd VALUES (?,?,?)", BRND)
    con.executemany("INSERT INTO etf_mst VALUES (?,?,?,?,?,?,?,?,?,?)", ETF)
    con.commit()
    return con
