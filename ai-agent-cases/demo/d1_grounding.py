"""D1: 같은 모델, 같은 질문. 온톨로지를 '설명'할 때와 '값으로 확정'할 때의 정답률 비교.

A 스키마만      : DDL(컬럼 주석 포함)만 주고 SQL 생성
B 온톨로지 설명 : A + 온톨로지의 클래스, 관계, 분류 계층을 글로 설명
C 온톨로지 확정 : B + 질문 속 용어를 어휘(SKOS)로 DB 값까지 확정하고, 업무 규칙을 붙여서 전달

정답 판정: 생성된 SQL의 실행 결과가 정답 SQL 실행 결과와 같은지(값 집합과 행 수).
데이터와 상품은 모두 가상이며, 1회 실행 결과입니다.
"""
import argparse
import os
import re
import sys

from rdflib import Graph, Namespace, RDF, RDFS
from rdflib.namespace import SKOS, OWL

from bedrock import ask
from etf_data import DDL, build

HERE = os.path.dirname(os.path.abspath(__file__))
EX = Namespace("https://example.com/etf#")
MODEL = os.environ.get("D1_MODEL", "global.anthropic.claude-haiku-4-5-20251001-v1:0")

QUESTIONS = [
    ("미국국채 ETF 중 총보수가 가장 낮은 상품은?",
     "SELECT prd_nm FROM etf_mst WHERE ast_cls='BD_OVS_GOV' AND rgn_cd='US' ORDER BY fee_bp LIMIT 1"),
    ("2차전지 ETF는 모두 몇 개야?",
     "SELECT COUNT(*) FROM etf_mst WHERE thm_cd='T_BATT'"),
    ("배당 많이 주는 ETF 상위 3개 알려줘",
     "SELECT prd_nm FROM etf_mst ORDER BY dist_yld DESC LIMIT 3"),
    ("가람자산운용 ETF 중 순자산이 가장 큰 상품은?",
     "SELECT e.prd_nm FROM etf_mst e JOIN brnd b ON e.brnd_cd=b.brnd_cd JOIN mgr m ON b.mgr_cd=m.mgr_cd "
     "WHERE m.mgr_nm='가람자산운용' ORDER BY e.nav_ek DESC LIMIT 1"),
    ("총보수 0.1% 이하인 국내주식 ETF는 몇 개?",
     "SELECT COUNT(*) FROM etf_mst WHERE ast_cls='EQ_DOM' AND fee_bp<=10"),
    ("금 ETF 중 총보수가 가장 낮은 상품은?",
     "SELECT prd_nm FROM etf_mst WHERE ast_cls='CMD_GOLD' ORDER BY fee_bp LIMIT 1"),
    ("월배당 ETF의 평균 분배율은?",
     "SELECT ROUND(AVG(dist_yld),2) FROM etf_mst WHERE dist_freq='M'"),
    ("반도체 ETF 이름을 모두 알려줘",
     "SELECT prd_nm FROM etf_mst WHERE thm_cd='T_SEMI'"),
    ("국고채 ETF 순자산 합계는?",
     "SELECT SUM(nav_ek) FROM etf_mst WHERE ast_cls='BD_DOM_GOV'"),
    ("미국 주식 ETF 중 총보수가 가장 낮은 상품은?",
     "SELECT prd_nm FROM etf_mst WHERE ast_cls='EQ_OVS' AND rgn_cd='US' ORDER BY fee_bp LIMIT 1"),
    ("RIVER 브랜드 ETF는 몇 개야?",
     "SELECT COUNT(*) FROM etf_mst e JOIN brnd b ON e.brnd_cd=b.brnd_cd WHERE b.brnd_nm='RIVER'"),
    ("코스피200 ETF 중 순자산이 가장 큰 상품은?",
     "SELECT prd_nm FROM etf_mst WHERE prd_nm LIKE '%코스피200%' ORDER BY nav_ek DESC LIMIT 1"),
]
CLARIFY_Q = "친환경 ETF 중 보수가 낮은 걸 추천해줘"

SYS_SQL = ("너는 SQLite 전문가다. 사용자의 질문에 답하는 SELECT 문 하나만 출력한다. "
           "설명, 주석, 코드펜스 없이 SQL만 출력한다.")

G = Graph().parse(os.path.join(HERE, "etf_ontology.ttl"), format="turtle")


def label(n):
    return str(G.value(n, SKOS.prefLabel) or G.value(n, RDFS.label))


def ontology_text():
    """B: 온톨로지 스키마와 분류 계층을 글로 설명 (DB 값은 포함하지 않음)."""
    lines = ["[온톨로지]"]
    for c in G.subjects(RDF.type, OWL.Class):
        lines.append(f"- 클래스 {label(c)}")
    for p in G.subjects(RDF.type, OWL.ObjectProperty):
        lines.append(f"- 관계 {label(G.value(p, RDFS.domain))} --{label(p)}--> {label(G.value(p, RDFS.range))}")
    for c in G.subjects(RDF.type, SKOS.Concept):
        b = G.value(c, SKOS.broader)
        alts = ", ".join(sorted(str(a) for a in G.objects(c, SKOS.altLabel)))
        lines.append(f"- 개념 {label(c)}" + (f" (상위: {label(b)})" if b else "") + (f" 별칭: {alts}" if alts else ""))
    return "\n".join(lines)


def ground(question):
    """C: 질문 속 용어를 어휘에서 찾아 DB 조건으로 확정 (결정적, LLM 없음)."""
    index = []
    for c in G.subjects(EX.sqlFilter, None):
        for lab in [G.value(c, SKOS.prefLabel), *G.objects(c, SKOS.altLabel)]:
            index.append((str(lab), c))
    index.sort(key=lambda x: -len(x[0]))  # 긴 말부터: "미국국채"가 "국채"보다 먼저
    found, taken = [], question
    for lab, c in index:
        if lab in taken:
            found.append((lab, label(c), str(G.value(c, EX.sqlFilter))))
            taken = taken.replace(lab, " " * len(lab))
    rules = [str(G.value(r, RDFS.comment)) for r in G.subjects(RDF.type, EX.SemanticRule)
             if str(G.value(r, EX.trigger)) in question]
    return found, rules


def grounded_text(question):
    found, rules = ground(question)
    lines = ["[확정된 조건] 아래 조건은 시스템이 어휘 사전으로 확정했다. 그대로 사용한다."]
    lines += [f"- '{lab}' -> {concept}: {flt}" for lab, concept, flt in found] or ["- 없음"]
    lines += ["[업무 규칙]"] + ([f"- {r}" for r in rules] or ["- 없음"])
    lines.append("상품 분류 용어 중 확정되지 않은 것이 있으면 SQL 대신 'CLARIFY: <되물을 질문>' 한 줄만 출력한다.")
    return "\n".join(lines), found, rules


def prompt(mode, q):
    parts = [f"[스키마]\n{DDL}"]
    if mode in "BC":
        parts.append(ontology_text())
    if mode == "C":
        parts.append(grounded_text(q)[0])
    parts.append(f"[질문]\n{q}")
    return "\n\n".join(parts)


def clean_sql(text):
    text = re.sub(r"^```(?:sql)?|```$", "", text.strip(), flags=re.M).strip()
    return text.split(";")[0].strip()


def flat(rows):
    out = []
    for r in rows:
        for v in r:
            out.append(round(v, 2) if isinstance(v, float) else v)
    return out


def judge(con, sql, gold):
    want = con.execute(gold).fetchall()
    try:
        got = con.execute(sql).fetchall()
    except Exception as e:  # noqa: BLE001
        return False, f"SQL 오류: {e}"
    ok = len(got) == len(want) and all(v in flat(got) for v in flat(want))
    return ok, str(flat(got)[:4])


C = {"ok": "\033[32m", "ng": "\033[31m", "dim": "\033[90m", "b": "\033[1m", "cy": "\033[36m", "y": "\033[33m", "0": "\033[0m"}


def show_one(con, idx):
    q, gold = QUESTIONS[idx]
    print(f"{C['b']}질문:{C['0']} {q}\n")
    text, found, rules = grounded_text(q)
    print(f"{C['cy']}[C 단계의 Grounding 결과: LLM 호출 전, 사전 조회만으로 확정]{C['0']}")
    for lab, concept, flt in found:
        print(f"  '{lab}'  ->  {concept}  ->  {C['y']}{flt}{C['0']}")
    for r in rules:
        print(f"  업무 규칙: {r}")
    print()
    for mode in "ABC":
        sql = clean_sql(ask(MODEL, SYS_SQL, prompt(mode, q))[0])
        ok, got = judge(con, sql, gold)
        mark = f"{C['ok']}정답{C['0']}" if ok else f"{C['ng']}오답{C['0']}"
        print(f"{C['b']}{mode}{C['0']} {C['dim']}{sql}{C['0']}\n   결과 {got}  {mark}\n")


def run_all(con, out=None):
    score = {m: 0 for m in "ABC"}
    log = []
    print(f"{'#':>2}  질문{' ' * 44} A  B  C")
    for i, (q, gold) in enumerate(QUESTIONS, 1):
        marks = []
        for mode in "ABC":
            text, sec, tin, tout = ask(MODEL, SYS_SQL, prompt(mode, q))
            sql = clean_sql(text)
            ok, got = judge(con, sql, gold)
            score[mode] += ok
            log.append({"q": i, "mode": mode, "ok": ok, "sql": sql, "result": got,
                        "sec": round(sec, 2), "in_tokens": tin, "out_tokens": tout})
            marks.append(f"{C['ok']}O{C['0']}" if ok else f"{C['ng']}X{C['0']}")
        pad = 48 - sum(2 if ord(ch) > 0x2000 else 1 for ch in q)
        print(f"{i:>2}  {q}{' ' * max(pad, 1)} {'  '.join(marks)}", flush=True)
    n = len(QUESTIONS)
    print()
    names = {"A": "스키마만", "B": "온톨로지 설명", "C": "온톨로지 확정"}
    for m in "ABC":
        bar = "#" * round(score[m] / n * 30)
        print(f"{C['b']}{m} {names[m]:<8}{C['0']} {score[m]:>2}/{n}  {score[m] / n * 100:5.1f}%  {C['cy']}{bar}{C['0']}")
    if out:
        import json, datetime
        json.dump({"model": MODEL, "run_utc": datetime.datetime.utcnow().isoformat(timespec="seconds"),
                   "score": score, "n": n, "calls": log}, open(out, "w"), ensure_ascii=False, indent=1)


def clarify():
    print(f"{C['b']}질문:{C['0']} {CLARIFY_Q}")
    found, _ = ground(CLARIFY_Q)
    print(f"  Grounding: {'확정된 용어 없음' if not found else found}")
    out = ask(MODEL, SYS_SQL, prompt("C", CLARIFY_Q))[0]
    print(f"  C 응답: {C['y']}{out}{C['0']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["one", "all", "clarify", "onto", "peek"])
    ap.add_argument("--idx", type=int, default=0)
    ap.add_argument("--out")
    a = ap.parse_args()
    con = build()
    if a.step == "one":
        show_one(con, a.idx)
    elif a.step == "all":
        print(f"{C['dim']}model={MODEL}  temperature=0  questions={len(QUESTIONS)}  (가상 데이터, 1회 실행){C['0']}\n")
        run_all(con, a.out)
    elif a.step == "clarify":
        clarify()
    elif a.step == "peek":
        cur = con.execute("SELECT isin, prd_nm, ast_cls, rgn_cd, thm_cd, fee_bp, dist_yld FROM etf_mst LIMIT 6")
        w = [10, 24, 12, 7, 7, 7, 8]
        cell = lambda v, n: str(v) + " " * max(n - sum(2 if ord(ch) > 0x2000 else 1 for ch in str(v)), 1)
        print("".join(cell(d[0], n) for d, n in zip(cur.description, w)))
        for r in cur.fetchall():
            print("".join(cell(v, n) for v, n in zip(r, w)))
    else:
        print(ontology_text())
    sys.stdout.flush()
