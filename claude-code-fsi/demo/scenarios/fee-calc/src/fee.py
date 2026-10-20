# 위탁수수료 계산 (2014년 작성, 담당자 퇴사)
def calc(a, p, t):
    # a: 수량, p: 단가, t: 1=매수 2=매도
    amt = a * p
    f = amt * 0.00015
    if f < 100:
        f = 100
    if t == 2:
        tax = amt * 0.0018
    else:
        tax = 0
    return round(f + tax)
