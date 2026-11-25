from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.models.entities import Service, ServiceType, User
from backend.routes.schemas import ServiceTypeIn, type_out
from backend.services.audit import write_audit
from backend.services.auth_service import get_current_user
from backend.utils.ids import generate_code

router = APIRouter(prefix="/api/service-types", tags=["service-types"])


@router.get("")
def list_types(
    q: str = "",
    status: str = "all",
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(ServiceType)
    if q:
        like = f"%{q}%"
        query = query.filter((ServiceType.ten_loai_dv.like(like)) | (ServiceType.ma_loai_dv.like(like)))
    if status == "active":
        query = query.filter(ServiceType.trang_thai.is_(True))
    elif status == "inactive":
        query = query.filter(ServiceType.trang_thai.is_(False))
    rows = query.order_by(ServiceType.ma_loai_dv.asc()).all()
    result = []
    for row in rows:
        item = type_out(row)
        item["soDichVu"] = db.query(Service).filter(Service.ma_loai_dv == row.ma_loai_dv).count()
        result.append(item)
    return result


@router.post("")
def create_type(payload: ServiceTypeIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not payload.moTa.strip():
        raise HTTPException(400, "Mô tả không được để trống")
    code = (payload.maLoaiDV or "").strip().upper() or generate_code(db, ServiceType, "ma_loai_dv", "LDV", 2)
    if db.query(ServiceType).filter(ServiceType.ma_loai_dv == code).first():
        raise HTTPException(400, "Mã loại dịch vụ đã tồn tại")
    row = ServiceType(ma_loai_dv=code, ten_loai_dv=payload.tenLoaiDV.strip(), mo_ta=payload.moTa.strip(), trang_thai=payload.trangThai)
    db.add(row)
    db.commit()
    write_audit(db, user.username, "CREATE", "ServiceType", code, payload.tenLoaiDV)
    return type_out(row)


@router.put("/{code}")
def update_type(code: str, payload: ServiceTypeIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not payload.moTa.strip():
        raise HTTPException(400, "Mô tả không được để trống")
    row = db.query(ServiceType).filter(ServiceType.ma_loai_dv == code).first()
    if not row:
        raise HTTPException(404, "Không tìm thấy loại dịch vụ")
    row.ten_loai_dv = payload.tenLoaiDV.strip()
    row.mo_ta = payload.moTa.strip()
    row.trang_thai = payload.trangThai
    db.commit()
    write_audit(db, user.username, "UPDATE", "ServiceType", code, payload.tenLoaiDV)
    return type_out(row)


@router.delete("/{code}")
def delete_type(code: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.query(ServiceType).filter(ServiceType.ma_loai_dv == code).first()
    if not row:
        raise HTTPException(404, "Không tìm thấy loại dịch vụ")
    if db.query(Service).filter(Service.ma_loai_dv == code).count():
        raise HTTPException(400, "Không thể xóa loại đang có dịch vụ. Hãy chuyển dịch vụ sang loại khác trước.")
    db.delete(row)
    db.commit()
    write_audit(db, user.username, "DELETE", "ServiceType", code, row.ten_loai_dv)
    return {"ok": True}
