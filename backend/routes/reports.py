from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import extract, func
from sqlalchemy.orm import Session, joinedload

from backend.config.database import get_db
from backend.models.entities import (
    Customer,
    Dress,
    DressRental,
    DressRentalItem,
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


@router.get("/charts")
def charts(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    year = date.today().year
    months = list(range(1, 13))
    usage_rows = (
        db.query(extract("month", ServiceUsage.ngay_sd), func.sum(ServiceUsage.gia_luc_sd))
        .filter(extract("year", ServiceUsage.ngay_sd) == year)
        .group_by(extract("month", ServiceUsage.ngay_sd))
        .all()
    )
    usage_map = {int(m): float(v or 0) for m, v in usage_rows}
    rentals = db.query(DressRental).options(joinedload(DressRental.items)).all()
    rental_map = {m: 0.0 for m in months}
    rental_count = {m: 0 for m in months}
    for r in rentals:
        if not r.ngay_thue or r.ngay_thue.year != year:
            continue
        rental_map[r.ngay_thue.month] += sum(i.don_gia for i in r.items)
        rental_count[r.ngay_thue.month] += 1
    month_labels = [f"T{m}" for m in months]
    top_services = (
        db.query(Service.ten_dv, func.count(ServiceUsage.id), func.sum(ServiceUsage.gia_luc_sd))
        .join(ServiceUsage, ServiceUsage.ma_dv == Service.ma_dv)
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
    return {
        "year": year,
        "revenue": {
            "labels": month_labels,
            "services": [usage_map.get(m, 0) for m in months],
            "rentals": [rental_map[m] for m in months],
        },
        "rentalVolume": [rental_count[m] for m in months],
        "topServices": [{"name": n, "count": int(c or 0), "revenue": float(v or 0)} for n, c, v in top_services],
        "dressStatus": dress_stats,
    }
