from datetime import date, timedelta

MAX_ACTIVE_DRESSES = 3
DEPOSIT_RATE = 0.50
LATE_FEE_RATE = 0.10
DUE_SOON_DAYS = 3
ACTIVE_RENTAL_STATUSES = ("DANG_THUE", "QUA_HAN")


def calc_deposit(don_gia: float) -> float:
    return round(float(don_gia or 0) * DEPOSIT_RATE, 0)


def calc_late_fee(don_gia: float, days_late: int) -> float:
    if days_late <= 0:
        return 0.0
    return round(float(don_gia or 0) * LATE_FEE_RATE * days_late, 0)


def days_between(start: date, end: date) -> int:
    return (end - start).days


def days_late(due: date, today: date | None = None) -> int:
    today = today or date.today()
    return max(0, (today - due).days)


def is_due_soon(due: date, today: date | None = None, window: int = DUE_SOON_DAYS) -> bool:
    today = today or date.today()
    remaining = (due - today).days
    return 0 <= remaining <= window


def can_rent_more(current_active_count: int, new_count: int, limit: int = MAX_ACTIVE_DRESSES) -> bool:
    return current_active_count + new_count <= limit


def dates_overlap(start1: date, end1: date, start2: date, end2: date) -> bool:
    return start1 <= end2 and start2 <= end1


def next_code(prefix: str, existing: list[str], width: int = 3) -> str:
    max_n = 0
    for code in existing:
        if not code or not code.upper().startswith(prefix.upper()):
            continue
        suffix = code[len(prefix) :]
        if suffix.isdigit():
            max_n = max(max_n, int(suffix))
    return f"{prefix}{max_n + 1:0{width}d}"
