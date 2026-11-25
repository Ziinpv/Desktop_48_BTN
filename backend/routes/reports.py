from datetime import date, datetime, time

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from backend.config.database import get_db
from backend.models.entities import (
    Customer,
    Dress,
    DressRental,
    DressRentalItem,
    Payment,
    Service,
    ServiceType,
    ServiceUsage,
    User,
)
from backend.services.auth_service import get_current_user
from backend.services.rental_service import refresh_overdue, serialize_rental
from backend.services.rules import ACTIVE_RENTAL_STATUSES

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _loaded(db: Session):
    refresh_overdue(db)
    return db.query(DressRental).options(
        joinedload(DressRental.items).joinedload(DressRentalItem.dress),
        joinedload(DressRental.customer),
    )


@router.get("/dashboard")
def dashboard(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    refresh_overdue(db)
    rentals = _loaded(db).all()
    unreturned = [r for r in rentals if r.trang_thai in ACTIVE_RENTAL_STATUSES]
    overdue = [r for r in rentals if r.trang_thai == "QUA_HAN"]
    dresses = db.query(Dress).all()
    services = db.query(Service).all()
    types = db.query(ServiceType).all()
    usage_total = db.query(func.coalesce(func.sum(ServiceUsage.gia_luc_sd), 0)).scalar() or 0
    rental_total = sum(sum(i.don_gia for i in r.items) for r in rentals if r.trang_thai != "HUY")
    cat = []
    for t in types:
        count = sum(1 for s in services if s.ma_loai_dv == t.ma_loai_dv)
        cat.append({"name": t.ten_loai_dv, "code": t.ma_loai_dv, "count": count})
    return {
        "totalServices": len(services),
        "totalDresses": len(dresses),
        "availableDresses": sum(1 for d in dresses if d.trang_thai == "SAN_SANG"),
        "rentingDresses": sum(1 for d in dresses if d.trang_thai == "DANG_THUE"),
        "damagedDresses": sum(1 for d in dresses if d.trang_thai == "HON_HOC"),
        "unreturned": len(unreturned),
        "overdue": len(overdue),
        "customers": db.query(Customer).count(),
        "revenueServices": usage_total,
        "revenueRentals": rental_total,
        "categories": cat,
        "overdueList": [serialize_rental(r) for r in overdue],
    }


@router.get("/unreturned")
def unreturned(sort: str = "date", _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = _loaded(db).filter(DressRental.trang_thai.in_(ACTIVE_RENTAL_STATUSES)).all()
    data = [serialize_rental(r) for r in rows]
    if sort == "customer":
        data.sort(key=lambda x: x["tenKH"])
    else:
        data.sort(key=lambda x: x["ngayTraDuKien"] or "")
    return data


@router.get("/overdue")
def overdue(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = _loaded(db).filter(DressRental.trang_thai == "QUA_HAN").all()
    return [serialize_rental(r) for r in rows]


@router.get("/due-soon")
def due_soon(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = _loaded(db).filter(DressRental.trang_thai.in_(ACTIVE_RENTAL_STATUSES)).all()
    data = [serialize_rental(r) for r in rows]
    return [r for r in data if r.get("sapHetHan") or r.get("trangThai") == "QUA_HAN"]


def month_keys(start: date, end: date) -> list[tuple[int, int]]:
    keys = []
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        keys.append((year, month))
        month += 1
        if month == 13:
            month = 1
            year += 1
    return keys


def chart_payload(db: Session, from_date: date, to_date: date) -> dict:
    keys = month_keys(from_date, to_date)
    labels = [f"{m:02d}/{y}" for y, m in keys]
    usage_map = {k: 0.0 for k in keys}
    rental_map = {k: 0.0 for k in keys}
    rental_count = {k: 0 for k in keys}
    paid_map = {k: 0.0 for k in keys}

    usages = db.query(ServiceUsage).filter(ServiceUsage.ngay_sd >= from_date, ServiceUsage.ngay_sd <= to_date).all()
    for row in usages:
        if row.ngay_sd:
            key = (row.ngay_sd.year, row.ngay_sd.month)
            if key in usage_map:
                usage_map[key] += float(row.gia_luc_sd or 0)

    rentals = (
        db.query(DressRental)
        .options(joinedload(DressRental.items))
        .filter(DressRental.ngay_thue >= from_date, DressRental.ngay_thue <= to_date, DressRental.trang_thai != "HUY")
        .all()
    )
    for rental in rentals:
        key = (rental.ngay_thue.year, rental.ngay_thue.month)
        if key in rental_map:
            rental_map[key] += sum(i.don_gia or 0 for i in rental.items)
            rental_count[key] += 1

    start_dt = datetime.combine(from_date, time.min)
    end_dt = datetime.combine(to_date, time.max)
    payments = db.query(Payment).filter(Payment.created_at >= start_dt, Payment.created_at <= end_dt).all()
    for pay in payments:
        if not pay.created_at:
            continue
        key = (pay.created_at.year, pay.created_at.month)
        if key not in paid_map:
            continue
        amount = float(pay.so_tien or 0)
        paid_map[key] += -amount if pay.loai == "HOAN_COC" else amount

    top_services = (
        db.query(Service.ten_dv, func.count(ServiceUsage.id), func.sum(ServiceUsage.gia_luc_sd))
        .join(ServiceUsage, ServiceUsage.ma_dv == Service.ma_dv)
        .filter(ServiceUsage.ngay_sd >= from_date, ServiceUsage.ngay_sd <= to_date)
        .group_by(Service.ma_dv)
        .order_by(func.sum(ServiceUsage.gia_luc_sd).desc())
        .limit(6)
        .all()
    )
    dress_stats = {
        "renting": db.query(Dress).filter(Dress.trang_thai == "DANG_THUE").count(),
        "ready": db.query(Dress).filter(Dress.trang_thai == "SAN_SANG").count(),
        "damaged": db.query(Dress).filter(Dress.trang_thai == "HON_HOC").count(),
        "out": db.query(Dress).filter(Dress.trang_thai == "HET_HANG").count(),
    }
    services_vals = [usage_map[k] for k in keys]
    rentals_vals = [rental_map[k] for k in keys]
    paid_vals = [paid_map[k] for k in keys]
    return {
        "fromDate": from_date.isoformat(),
        "toDate": to_date.isoformat(),
        "year": from_date.year if from_date.year == to_date.year else None,
        "revenue": {
            "labels": labels,
            "services": services_vals,
            "rentals": rentals_vals,
            "collected": paid_vals,
        },
        "rentalVolume": [rental_count[k] for k in keys],
        "topServices": [{"name": n, "count": int(c or 0), "revenue": float(v or 0)} for n, c, v in top_services],
        "dressStatus": dress_stats,
        "totals": {
            "services": sum(services_vals),
            "rentals": sum(rentals_vals),
            "collected": sum(paid_vals),
            "contracts": sum(rental_count.values()),
        },
    }


@router.get("/charts")
def charts(
    fromDate: str = "",
    toDate: str = "",
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    start = date.fromisoformat(fromDate) if fromDate else date(today.year, 1, 1)
    end = date.fromisoformat(toDate) if toDate else date(today.year, 12, 31)
    if end < start:
        start, end = end, start
    return chart_payload(db, start, end)
