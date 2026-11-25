from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from backend.config.database import get_db
from backend.models.entities import (
    Customer,
    Dress,
    DressRental,
    DressRentalItem,
    RentalHistory,
    Service,
    ServiceUsage,
    User,
)
from backend.routes.schemas import ServiceUsageIn, customer_out, dress_out, service_out
from backend.services.audit import write_audit
from backend.services.auth_service import get_current_user
from backend.services.rental_service import serialize_rental
from backend.services.rules import calc_late_fee, days_late

router = APIRouter(prefix="/api/lookup", tags=["lookup"])


@router.get("/dress")
def lookup_dress(q: str, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    like = f"%{q.strip()}%"
    dresses = (
        db.query(Dress)
        .filter((Dress.ma_dress.like(like)) | (Dress.ten_ao.like(like)) | (Dress.loai_ao.like(like)))
        .all()
    )
    result = []
    for d in dresses:
        rentals = (
            db.query(DressRental)
            .join(DressRentalItem, DressRentalItem.ma_hop_dong == DressRental.ma_hop_dong)
            .options(joinedload(DressRental.customer), joinedload(DressRental.items))
            .filter(DressRentalItem.ma_dress == d.ma_dress)
            .order_by(DressRental.ngay_thue.desc())
            .all()
        )
        timeline = []
        for r in rentals:
            timeline.append(
                {
                    "maHopDong": r.ma_hop_dong,
                    "maKH": r.ma_kh,
                    "tenKH": r.customer.ten_kh if r.customer else r.ma_kh,
                    "ngayThue": r.ngay_thue.isoformat() if r.ngay_thue else None,
                    "ngayTraDuKien": r.ngay_tra_du_kien.isoformat() if r.ngay_tra_du_kien else None,
                    "ngayTraThucTe": r.ngay_tra_thuc_te.isoformat() if r.ngay_tra_thuc_te else None,
                    "trangThai": r.trang_thai,
                }
            )
        item = dress_out(d)
        item["lichSu"] = timeline
        item["luotThue"] = len(timeline)
        result.append(item)
    return result


@router.get("/customer")
def lookup_customer(q: str, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    like = f"%{q.strip()}%"
    customers = (
        db.query(Customer)
        .filter((Customer.ma_kh.like(like)) | (Customer.ten_kh.like(like)) | (Customer.sdt.like(like)))
        .all()
    )
    result = []
    for c in customers:
        usages = (
            db.query(ServiceUsage)
            .options(joinedload(ServiceUsage.service).joinedload(Service.loai))
            .filter(ServiceUsage.ma_kh == c.ma_kh)
            .order_by(ServiceUsage.ngay_sd.desc())
            .all()
        )
        services = []
        service_total = 0
        for u in usages:
            s = u.service
            gia = u.gia_luc_sd or (s.don_gia if s else 0)
            service_total += gia
            services.append(
                {
                    "id": u.id,
                    "maDV": u.ma_dv,
                    "tenDV": s.ten_dv if s else u.ma_dv,
                    "loaiDV": s.loai.ten_loai_dv if s and s.loai else "",
                    "ngaySD": u.ngay_sd.isoformat() if u.ngay_sd else None,
                    "giaLucSD": gia,
                    "ghiChu": u.ghi_chu,
                }
            )
        rentals = (
            db.query(DressRental)
            .options(
                joinedload(DressRental.items).joinedload(DressRentalItem.dress),
                joinedload(DressRental.customer),
                joinedload(DressRental.history),
                joinedload(DressRental.payments),
            )
            .filter(DressRental.ma_kh == c.ma_kh)
            .order_by(DressRental.ngay_thue.desc())
            .all()
        )
        rental_data = [serialize_rental(r) for r in rentals]
        rental_total = sum(r.get("tienThue") or 0 for r in rental_data)
        deposit_total = sum(r.get("tienCoc") or 0 for r in rental_data)
        paid_total = service_total + sum(r.get("daThanhToan") or 0 for r in rental_data)
        outstanding = sum(r.get("conNo") or 0 for r in rental_data)
        history = (
            db.query(RentalHistory)
            .join(DressRental, RentalHistory.ma_hop_dong == DressRental.ma_hop_dong)
            .filter(DressRental.ma_kh == c.ma_kh)
            .order_by(RentalHistory.ngay_cap_nhat.desc())
            .all()
        )
        item = customer_out(c)
        item["services"] = services
        item["rentals"] = rental_data
        item["serviceTotal"] = service_total
        item["rentalTotal"] = rental_total
        item["depositTotal"] = deposit_total
        item["paidTotal"] = paid_total
        item["outstanding"] = outstanding
        item["grandTotal"] = service_total + rental_total
        item["payments"] = [p for r in rental_data for p in (r.get("payments") or [])]
        item["transactions"] = [
            {
                "id": h.id,
                "maHopDong": h.ma_hop_dong,
                "trangThai": h.trang_thai,
                "tienPhat": h.tien_phat,
                "ghiChu": h.ghi_chu,
                "ngay": h.ngay_cap_nhat.isoformat() if h.ngay_cap_nhat else None,
            }
            for h in history
        ]
        result.append(item)
    return result


@router.post("/service-usage")
def add_usage(payload: ServiceUsageIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.ma_dv == payload.maDV).first()
    if not service:
        raise HTTPException(404, "Không tìm thấy dịch vụ")
    if not db.query(Customer).filter(Customer.ma_kh == payload.maKH).first():
        raise HTTPException(404, "Không tìm thấy khách hàng")
    row = ServiceUsage(
        ma_kh=payload.maKH,
        ma_dv=payload.maDV,
        ngay_sd=date.fromisoformat(payload.ngaySD),
        gia_luc_sd=payload.giaLucSD if payload.giaLucSD is not None else service.don_gia,
        ghi_chu=payload.ghiChu,
    )
    db.add(row)
    db.commit()
    write_audit(db, user.username, "CREATE", "ServiceUsage", payload.maKH, payload.maDV)
    return {"ok": True, "id": row.id}
