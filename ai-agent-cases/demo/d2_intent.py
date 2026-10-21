"""D2: 인텐트 20개를 소형 모델로 분류. 목록에서 바로 고르기 vs 3속성 분해 + 그래프 매칭.

A 직접 선택 : 소형 모델이 20개 인텐트 목록에서 하나를 고른다
B 온톨로지  : 소형 모델이 Domain, Action, Tag를 각각(병렬) 고르고,
              규칙 기반 매칭으로 후보를 좁힌다. 후보가 여럿이면 그때만 LLM이 비교한다

신한카드 사례(51개 인텐트, Qwen3 32B)의 구조를 작게 재현한 것입니다.
인텐트와 발화는 모두 가상이며, 1회 실행 결과입니다.
"""
import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor

from bedrock import ask

MODEL = os.environ.get("D2_MODEL", "apac.amazon.nova-micro-v1:0")

DOMAINS = {"결제": "카드로 물건값을 낸 건, 승인, 할부", "한도": "카드로 쓸 수 있는 최대 금액",
           "카드": "실물 카드 자체(분실, 해지, 비밀번호)", "명세서": "매달 청구되는 카드대금, 결제일, 통장 출금"}
ACTIONS = {"조회": "확인하거나 보여 달라", "취소": "없던 일로 하거나 끝내 달라, 정지를 풀어 달라",
           "변경": "설정이나 금액을 바꾸거나 올리거나 내리거나 막아 달라", "신청": "새로 해 달라, 신고",
           "오류": "안 된다, 실패했다, 거절됐다"}
TAGS = {"일반": "아래 어디에도 해당하지 않음", "해외": "해외, 직구, 외국", "할부": "할부, 개월 수",
        "분실": "잃어버림, 도난, 찾음", "자동이체": "통장 출금, 출금 계좌", "상향": "올림, 늘림",
        "하향": "내림, 줄임", "일시": "잠깐, 이번만, 기간 한정으로 올림"}

# 인텐트 = (Domain, Action, Tag). 세 속성 조합이 겹치지 않게 설계한 온톨로지 맵
INTENTS = {
    "결제내역조회": ("결제", "조회", "일반"), "결제취소": ("결제", "취소", "일반"),
    "결제실패": ("결제", "오류", "일반"), "해외결제내역조회": ("결제", "조회", "해외"),
    "해외결제차단설정": ("결제", "변경", "해외"), "해외결제실패": ("결제", "오류", "해외"),
    "할부전환": ("결제", "신청", "할부"), "할부개월변경": ("결제", "변경", "할부"),
    "한도조회": ("한도", "조회", "일반"), "한도상향": ("한도", "변경", "상향"),
    "일시한도상향": ("한도", "변경", "일시"), "한도하향": ("한도", "변경", "하향"),
    "분실신고": ("카드", "신청", "분실"), "분실해제": ("카드", "취소", "분실"),
    "카드해지": ("카드", "취소", "일반"), "비밀번호변경": ("카드", "변경", "일반"),
    "명세서조회": ("명세서", "조회", "일반"), "결제일변경": ("명세서", "변경", "일반"),
    "자동이체계좌변경": ("명세서", "변경", "자동이체"), "자동이체출금실패": ("명세서", "오류", "자동이체"),
}
DESC = {
    "결제내역조회": "국내에서 카드로 쓴 내역 확인", "결제취소": "이미 승인된 결제를 취소",
    "결제실패": "국내 결제 승인이 거절되거나 안 됨", "해외결제내역조회": "해외에서 쓴 내역 확인",
    "해외결제차단설정": "해외 결제를 막거나 다시 허용", "해외결제실패": "해외, 직구 결제가 거절되거나 안 됨",
    "할부전환": "일시불로 낸 결제를 할부로 바꿈", "할부개월변경": "이미 할부인 결제의 개월 수 변경",
    "한도조회": "현재 한도, 사용 가능 금액 확인", "한도상향": "한도를 계속 올림",
    "일시한도상향": "기간을 정해 잠깐만 한도를 올림", "한도하향": "한도를 낮춤",
    "분실신고": "잃어버리거나 도난당한 카드를 정지", "분실해제": "찾은 카드의 분실 정지를 풂",
    "카드해지": "카드를 없앰", "비밀번호변경": "카드 비밀번호를 바꿈",
    "명세서조회": "이번 달 청구 금액, 명세서 확인", "결제일변경": "카드대금 납부일을 바꿈",
    "자동이체계좌변경": "카드대금이 빠져나가는 통장을 바꿈", "자동이체출금실패": "카드대금이 통장에서 안 빠져나감",
}

TESTS = [
    ("지난달에 쓴 카드 내역 좀 보여줘", "결제내역조회"), ("어제 편의점에서 긁은 거 취소하고 싶어요", "결제취소"),
    ("결제하려는데 계속 승인 거절이 떠요", "결제실패"), ("일본 여행 가서 쓴 금액 확인하고 싶어", "해외결제내역조회"),
    ("해외에서 카드 못 쓰게 막아주세요", "해외결제차단설정"), ("아마존 직구 결제가 안 돼요", "해외결제실패"),
    ("이번에 산 노트북 할부로 바꿀 수 있나요", "할부전환"), ("3개월 할부를 6개월로 늘리고 싶어요", "할부개월변경"),
    ("내 카드 한도가 얼마예요?", "한도조회"), ("한도 좀 올려주세요", "한도상향"),
    ("이번 달만 잠깐 한도 늘릴 수 있을까요", "일시한도상향"), ("한도를 좀 낮춰 주세요, 너무 많이 써서요", "한도하향"),
    ("지갑을 잃어버렸어요 카드 정지해 주세요", "분실신고"), ("잃어버린 카드 찾았어요, 다시 쓰고 싶어요", "분실해제"),
    ("이 카드 이제 안 쓸래요, 없애 주세요", "카드해지"), ("카드 비밀번호 바꾸고 싶어요", "비밀번호변경"),
    ("이번 달 청구 금액 얼마 나왔어요?", "명세서조회"), ("결제일을 25일로 옮기고 싶어요", "결제일변경"),
    ("카드값 빠져나가는 통장을 바꾸려고요", "자동이체계좌변경"), ("카드값이 통장에서 안 빠져나갔대요", "자동이체출금실패"),
    ("해외 결제 막아놨던 거 풀어주세요", "해외결제차단설정"), ("백화점에서 산 옷 결제 취소 부탁해요", "결제취소"),
    ("승인이 안 나서 계산을 못 했어요", "결제실패"), ("할부 개월 수 변경 가능한가요", "할부개월변경"),
    ("일시불로 긁은 거 할부로 돌려 주세요", "할부전환"), ("급하게 다음 주까지만 한도 올려 주실 수 있나요", "일시한도상향"),
    ("신용카드 사용 가능 금액 확인", "한도조회"), ("카드를 도난당한 것 같아요", "분실신고"),
    ("카드 정지 풀어 주세요, 집에서 찾았어요", "분실해제"), ("연회비 나가기 전에 카드 해지하려고요", "카드해지"),
    ("비번을 새로 설정하고 싶어요", "비밀번호변경"), ("이번 달 명세서 다시 보내 주세요", "명세서조회"),
    ("출금 계좌를 다른 은행으로 바꾸고 싶어요", "자동이체계좌변경"),
    ("잔액 부족으로 카드대금 출금이 실패했다는 문자가 왔어요", "자동이체출금실패"),
    ("미국 출장 중인데 결제가 계속 거절돼요", "해외결제실패"), ("해외 사용 내역 중에 모르는 게 있어요", "해외결제내역조회"),
    ("결제일이 월급날이랑 안 맞아서 바꾸고 싶어요", "결제일변경"), ("한도 너무 높은데 줄여 주세요", "한도하향"),
    ("연봉 올랐는데 한도 상향 신청할게요", "한도상향"), ("카드 쓴 거 언제 얼마 썼는지 확인", "결제내역조회"),
]

SYS = "너는 카드사 상담 분류기다. 보기의 '|' 왼쪽 이름 하나만 그대로 출력한다. 설명이나 다른 말은 쓰지 않는다."


def pick(options, text, desc=None):
    """모델 출력에서 보기 이름을 찾는다(가장 긴 이름 우선). 설명을 그대로 출력했으면 설명으로 역매핑."""
    for name in sorted(options, key=len, reverse=True):
        if name in text:
            return name
    for name in options:
        if desc and desc.get(name) and desc[name] in text:
            return name
    return None


def classify_direct(utt):
    opts = "\n".join(f"- {k} | {v}" for k, v in DESC.items())
    out, sec, tin, tout = ask(MODEL, SYS, f"[보기]\n{opts}\n\n[고객 발화]\n{utt}", 30)
    return pick(INTENTS, out, DESC), sec, tin + tout, None


def choose(attr, table, utt):
    opts = "\n".join(f"- {k} | {v}" for k, v in table.items())
    out, sec, tin, tout = ask(MODEL, SYS, f"[{attr} 보기]\n{opts}\n\n[고객 발화]\n{utt}", 10)
    return pick(table, out, table), sec, tin + tout


def classify_onto(utt):
    t0 = time.time()
    with ThreadPoolExecutor(3) as ex:
        fs = [ex.submit(choose, n, t, utt) for n, t in (("Domain", DOMAINS), ("Action", ACTIONS), ("Tag", TAGS))]
        (d, _, k1), (a, _, k2), (t, _, k3) = [f.result() for f in fs]
    tokens = k1 + k2 + k3
    # 그래프 매칭: Tag로 거르고, Domain과 Action이 맞는 인텐트만 남긴다. 없으면 Tag 조건을 푼다
    cands = [k for k, v in INTENTS.items() if v == (d, a, t)]
    if not cands:
        cands = [k for k, v in INTENTS.items() if v[0] == d and v[1] == a]
    if not cands:
        cands = [k for k, v in INTENTS.items() if v[0] == d]
    if len(cands) == 1:
        return cands[0], time.time() - t0, tokens, (d, a, t, cands)
    opts = "\n".join(f"- {k} | {DESC[k]}" for k in cands)
    out, _, tin, tout = ask(MODEL, SYS, f"[보기]\n{opts}\n\n[고객 발화]\n{utt}", 30)
    return pick(cands, out, DESC), time.time() - t0, tokens + tin + tout, (d, a, t, cands)


C = {"ok": "\033[32m", "ng": "\033[31m", "dim": "\033[90m", "b": "\033[1m", "cy": "\033[36m", "y": "\033[33m", "0": "\033[0m"}


def show(utt):
    print(f"{C['b']}고객 발화:{C['0']} {utt}\n")
    got, sec, _, (d, a, t, cands) = classify_onto(utt)
    print(f"  {C['cy']}병렬 추출{C['0']}  Domain={C['y']}{d}{C['0']}  Action={C['y']}{a}{C['0']}  Tag={C['y']}{t}{C['0']}")
    print(f"  {C['cy']}그래프 매칭{C['0']} 20개 -> 후보 {len(cands)}개 {cands}")
    print(f"  {C['cy']}확정{C['0']}       {C['b']}{got}{C['0']}  ({sec:.2f}s)\n")


def run_all(out=None):
    score = {"A": 0, "B": 0}
    secs = {"A": [], "B": []}
    log = []
    print(f"{'#':>2}  고객 발화{' ' * 47} A  B")
    for i, (utt, gold) in enumerate(TESTS, 1):
        ga, sa, ka, _ = classify_direct(utt)
        gb, sb, kb, trace = classify_onto(utt)
        for m, g, s in (("A", ga, sa), ("B", gb, sb)):
            score[m] += g == gold
            secs[m].append(s)
        log.append({"i": i, "utt": utt, "gold": gold, "A": ga, "B": gb, "B_attrs": trace[:3],
                    "B_cands": trace[3], "A_sec": round(sa, 2), "B_sec": round(sb, 2), "A_tokens": ka, "B_tokens": kb})
        mk = lambda g: f"{C['ok']}O{C['0']}" if g == gold else f"{C['ng']}X{C['0']}"
        pad = 56 - sum(2 if ord(ch) > 0x2000 else 1 for ch in utt)
        wrong = "" if ga == gold and gb == gold else f"  {C['dim']}정답 {gold} / A {ga} / B {gb}{C['0']}"
        print(f"{i:>2}  {utt}{' ' * max(pad, 1)} {mk(ga)}  {mk(gb)}{wrong}", flush=True)
    n = len(TESTS)
    print()
    for m, name in (("A", "직접 선택  "), ("B", "3속성+매칭")):
        avg = sum(secs[m]) / n
        print(f"{C['b']}{m} {name}{C['0']} {score[m]:>2}/{n}  {score[m] / n * 100:5.1f}%   평균 {avg:.2f}s/건")
    if out:
        import datetime
        json.dump({"model": MODEL, "run_utc": datetime.datetime.utcnow().isoformat(timespec="seconds"),
                   "score": score, "n": n, "calls": log}, open(out, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["one", "all", "map"])
    ap.add_argument("--utt", default="해외 결제 막아놨던 거 풀어주세요")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.step == "one":
        show(a.utt)
    elif a.step == "map":
        for k, (d, ac, t) in INTENTS.items():
            print(f"  {k:<10}  Domain={d:<4} Action={ac:<3} Tag={t}")
    else:
        print(f"{C['dim']}model={MODEL}  temperature=0  intents={len(INTENTS)}  utterances={len(TESTS)}  (가상 데이터, 1회 실행){C['0']}\n")
        run_all(a.out)
