from decimal import Decimal
import src.fee as fee


def total(qty, price, side):
    return Decimal(str(fee.calc(qty, price, side)))


def test_buy_minimum_fee():
    assert total(10, 1000, 1) == Decimal("100")


def test_sell_includes_tax():
    # 매도 1,234주 x 56,700원 = 69,967,800원
    # 수수료 0.015% = 10,495.17 -> 원 미만 절사 10,495
    # 거래세 0.18%  = 125,942.04 -> 원 미만 절사 125,942
    assert total(1234, 56700, 2) == Decimal("136437")


def test_large_buy_truncates_won():
    # 매수 3,333주 x 33,333원 = 111,098,889원, 수수료 16,664.83 -> 16,664
    assert total(3333, 33333, 1) == Decimal("16664")
