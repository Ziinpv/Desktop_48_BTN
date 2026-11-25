from datetime import date, timedelta

from backend.services.rules import calc_deposit, calc_late_fee, can_rent_more, dates_overlap, days_late, next_code


def test_deposit_is_half_price():
    assert calc_deposit(3_500_000) == 1_750_000
    assert calc_deposit(0) == 0


def test_late_fee_formula():
    assert calc_late_fee(1_000_000, 0) == 0
    assert calc_late_fee(1_000_000, 3) == 300_000


def test_max_three_dresses():
    assert can_rent_more(0, 3) is True
    assert can_rent_more(2, 1) is True
    assert can_rent_more(2, 2) is False
    assert can_rent_more(3, 1) is False


def test_dress_date_overlap():
    s1, e1 = date(2026, 9, 10), date(2026, 9, 12)
    assert dates_overlap(s1, e1, date(2026, 9, 12), date(2026, 9, 14)) is True
    assert dates_overlap(s1, e1, date(2026, 9, 13), date(2026, 9, 15)) is False


def test_days_late():
    assert days_late(date(2026, 9, 10), date(2026, 9, 15)) == 5
    assert days_late(date(2026, 9, 20), date(2026, 9, 15)) == 0


def test_auto_service_code():
    assert next_code("DV", ["DV001", "DV008"]) == "DV009"
    assert next_code("HD", []) == "HD001"
