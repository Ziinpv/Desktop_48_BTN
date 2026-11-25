import base64
import io

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
import qrcode

from backend.config.database import get_db
from backend.models.entities import Dress, DressRental, DressRentalItem, User
from backend.routes.schemas import DressIn, dress_out
from backend.services.audit import write_audit
from backend.services.auth_service import get_current_user
from backend.services.rules import ACTIVE_RENTAL_STATUSES
from backend.utils.ids import generate_code

router = APIRouter(prefix="/api/dresses", tags=["dresses"])


@router.get("")
def list_dresses(
    q: str = "",
    status: str = "",
    loai: str = "",
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Dress)
    if q:
        like = f"%{q}%"
        query = query.filter((Dress.ten_ao.like(like)) | (Dress.ma_dress.like(like)) | (Dress.loai_ao.like(like)))
    if status:
        query = query.filter(Dress.trang_thai == status)
    if loai:
        query = query.filter(Dress.loai_ao == loai)
    return [dress_out(d) for d in query.order_by(Dress.ma_dress.asc()).all()]


@router.post("")
def create_dress(payload: DressIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    code = (payload.maDress or "").strip().upper() or generate_code(db, Dress, "ma_dress", "AC")
    if db.query(Dress).filter(Dress.ma_dress == code).first():
        raise HTTPException(400, "Mã áo đã tồn tại")
    row = Dress(
        ma_dress=code,
        ten_ao=payload.tenAo.strip(),
        loai_ao=payload.loaiAo,
        don_gia=payload.donGia,
        hinh_anh=payload.hinhAnh,
        trang_thai=payload.trangThai,
        ghi_chu=payload.ghiChu,
    )
    db.add(row)
    db.commit()
    write_audit(db, user.username, "CREATE", "Dress", code, payload.tenAo)
    return dress_out(row)


@router.put("/{code}")
def update_dress(code: str, payload: DressIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.query(Dress).filter(Dress.ma_dress == code).first()
    if not row:
        raise HTTPException(404, "Không tìm thấy bộ áo")
    row.ten_ao = payload.tenAo.strip()
    row.loai_ao = payload.loaiAo
    row.don_gia = payload.donGia
    row.hinh_anh = payload.hinhAnh
    row.trang_thai = payload.trangThai
    row.ghi_chu = payload.ghiChu
    db.commit()
    write_audit(db, user.username, "UPDATE", "Dress", code, payload.tenAo)
    return dress_out(row)


@router.delete("/{code}")
def delete_dress(code: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.query(Dress).filter(Dress.ma_dress == code).first()
    if not row:
        raise HTTPException(404, "Không tìm thấy bộ áo")
    used = (
        db.query(DressRentalItem)
        .join(DressRental, DressRentalItem.ma_hop_dong == DressRental.ma_hop_dong)
        .filter(DressRentalItem.ma_dress == code, DressRental.trang_thai.in_(ACTIVE_RENTAL_STATUSES))
        .count()
    )
    if used:
        raise HTTPException(400, "Bộ áo đang được thuê, không thể xóa")
    db.delete(row)
    db.commit()
    write_audit(db, user.username, "DELETE", "Dress", code, row.ten_ao)
    return {"ok": True}


@router.get("/{code}/qr")
def dress_qr(code: str, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.query(Dress).filter(Dress.ma_dress == code).first()
    if not row:
        raise HTTPException(404, "Không tìm thấy bộ áo")
    img = qrcode.make(f"LUXE|{row.ma_dress}|{row.ten_ao}")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return {
        "maDress": row.ma_dress,
        "tenAo": row.ten_ao,
        "qr": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(),
    }
