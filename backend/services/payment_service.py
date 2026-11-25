from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.entities import Customer, DressRental, Payment, Service
from backend.services.rental_service import _penalty_for
from backend.utils.ids import generate_code

LOAI_LABEL = {
    "COC": "Tiền cọc",
    "THUE": "Tiền thuê áo",
    "PHI_TRE": "Phí trễ hạn",
    "DICH_VU": "Dịch vụ",
    "HOAN_COC": "Hoàn cọc",
}


def payment_out(row: Payment) -> dict:
    return {
        "maGD": row.ma_gd,
        "maBienLai": row.ma_bien_lai,
        "maKH": row.ma_kh,
        "maHopDong": row.ma_hop_dong,
        "maDV": row.ma_dv,
        "loai": row.loai,
        "loaiTen": LOAI_LABEL.get(row.loai, row.loai),
        "soTien": row.so_tien,
        "phuongThuc": row.phuong_thuc,
        "soConLai": row.so_con_lai,
        "ghiChu": row.ghi_chu,
        "createdAt": row.created_at.isoformat() if row.created_at else None,
        "createdBy": row.created_by,
    }


def obligation_for(db: Session, rental: DressRental) -> float:
    tien_thue = sum(i.don_gia or 0 for i in (rental.items or []))
    return float(rental.tien_coc or 0) + float(tien_thue) + float(_penalty_for(rental))


def collected_for(db: Session, ma_hd: str) -> float:
    rows = db.query(Payment).filter(Payment.ma_hop_dong == ma_hd).all()
    total = 0.0
    for p in rows:
        if p.loai == "HOAN_COC":
            total -= p.so_tien or 0
        else:
            total += p.so_tien or 0
    return total


def remaining_for(db: Session, rental: DressRental) -> float:
    return max(0.0, obligation_for(db, rental) - collected_for(db, rental.ma_hop_dong))


def record_payment(db: Session, payload: dict, username: str) -> Payment:
    loai = payload.get("loai") or "COC"
    if loai not in LOAI_LABEL:
        raise HTTPException(400, "Loại giao dịch không hợp lệ")
    method = payload.get("phuongThuc") or "TIEN_MAT"
    if method not in ("TIEN_MAT", "CHUYEN_KHOAN"):
        raise HTTPException(400, "Phương thức phải là TIEN_MAT hoặc CHUYEN_KHOAN")
    amount = float(payload.get("soTien") or 0)
    if amount <= 0:
        raise HTTPException(400, "Số tiền phải > 0")
    ma_kh = payload.get("maKH")
    ma_hd = payload.get("maHopDong") or None
    rental = None
    if ma_hd:
        rental = db.query(DressRental).filter(DressRental.ma_hop_dong == ma_hd).first()
        if not rental:
            raise HTTPException(404, "Không tìm thấy hợp đồng")
        ma_kh = ma_kh or rental.ma_kh
    if not ma_kh or not db.query(Customer).filter(Customer.ma_kh == ma_kh).first():
        raise HTTPException(404, "Không tìm thấy khách hàng")
    if payload.get("maDV") and not db.query(Service).filter(Service.ma_dv == payload["maDV"]).first():
        raise HTTPException(404, "Không tìm thấy dịch vụ")

    remain = 0.0
    if rental:
        remain = max(0.0, remaining_for(db, rental) - (amount if loai != "HOAN_COC" else -amount))

    row = Payment(
        ma_gd=generate_code(db, Payment, "ma_gd", "GD"),
        ma_bien_lai=generate_code(db, Payment, "ma_bien_lai", "BL"),
        ma_kh=ma_kh,
        ma_hop_dong=ma_hd,
        ma_dv=payload.get("maDV"),
        loai=loai,
        so_tien=amount,
        phuong_thuc=method,
        so_con_lai=remain,
        ghi_chu=payload.get("ghiChu") or "",
        created_by=username,
        created_at=datetime.utcnow(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def backfill_deposits(db: Session) -> int:
    added = 0
    rentals = db.query(DressRental).all()
    for rental in rentals:
        if not rental.tien_coc:
            continue
        exists = db.query(Payment).filter(Payment.ma_hop_dong == rental.ma_hop_dong, Payment.loai == "COC").first()
        if exists:
            continue
        db.add(
            Payment(
                ma_gd=generate_code(db, Payment, "ma_gd", "GD"),
                ma_bien_lai=generate_code(db, Payment, "ma_bien_lai", "BL"),
                ma_kh=rental.ma_kh,
                ma_hop_dong=rental.ma_hop_dong,
                loai="COC",
                so_tien=rental.tien_coc,
                phuong_thuc="TIEN_MAT",
                so_con_lai=0,
                ghi_chu="Backfill tiền cọc khi lập hợp đồng",
                created_by=rental.created_by or "system",
            )
        )
        added += 1
        db.flush()
    if added:
        db.commit()
    return added
