from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from backend.config.database import get_db
from backend.models.entities import Service, ServiceType, ServiceUsage, User
from backend.routes.schemas import ServiceIn, service_out
from backend.services.audit import write_audit
from backend.services.auth_service import catalog_writer, get_current_user
from backend.utils.ids import generate_code

router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("")
def list_services(
    q: str = "",
    typeId: str = "",
    status: str = "",
    sort: str = "ma_dv",
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Service).options(joinedload(Service.loai))
    if q:
        like = f"%{q}%"
        query = query.filter((Service.ten_dv.like(like)) | (Service.ma_dv.like(like)))
    if typeId:
        query = query.filter(Service.ma_loai_dv == typeId)
    if status:
        query = query.filter(Service.trang_thai == status)
    if sort == "price_asc":
        query = query.order_by(Service.don_gia.asc())
    elif sort == "price_desc":
        query = query.order_by(Service.don_gia.desc())
    else:
        query = query.order_by(Service.ma_dv.asc())
    return [service_out(row) for row in query.all()]


@router.get("/catalog")
def catalog(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    types = db.query(ServiceType).order_by(ServiceType.ma_loai_dv.asc()).all()
    result = []
    for t in types:
        services = (
            db.query(Service)
            .options(joinedload(Service.loai))
            .filter(Service.ma_loai_dv == t.ma_loai_dv)
            .order_by(Service.ten_dv.asc())
            .all()
        )
        result.append(
            {
                "maLoaiDV": t.ma_loai_dv,
                "tenLoaiDV": t.ten_loai_dv,
                "moTa": t.mo_ta,
                "trangThai": bool(t.trang_thai),
                "services": [service_out(s) for s in services],
            }
        )
    return result


@router.post("")
def create_service(payload: ServiceIn, user: User = Depends(catalog_writer), db: Session = Depends(get_db)):
    if not db.query(ServiceType).filter(ServiceType.ma_loai_dv == payload.maLoaiDV).first():
        raise HTTPException(400, "Loại dịch vụ không tồn tại")
    code = (payload.maDV or "").strip().upper() or generate_code(db, Service, "ma_dv", "DV")
    if db.query(Service).filter(Service.ma_dv == code).first():
        raise HTTPException(400, "Mã dịch vụ đã tồn tại")
    row = Service(
        ma_dv=code,
        ten_dv=payload.tenDV.strip(),
        ma_loai_dv=payload.maLoaiDV,
        don_gia=payload.donGia,
        mo_ta=payload.moTa,
        hinh_anh=payload.hinhAnh,
        trang_thai=payload.trangThai,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    write_audit(db, user.username, "CREATE", "Service", code, payload.tenDV)
    return service_out(row)


@router.put("/{code}")
def update_service(code: str, payload: ServiceIn, user: User = Depends(catalog_writer), db: Session = Depends(get_db)):
    row = db.query(Service).options(joinedload(Service.loai)).filter(Service.ma_dv == code).first()
    if not row:
        raise HTTPException(404, "Không tìm thấy dịch vụ")
    row.ten_dv = payload.tenDV.strip()
    row.ma_loai_dv = payload.maLoaiDV
    row.don_gia = payload.donGia
    row.mo_ta = payload.moTa
    row.hinh_anh = payload.hinhAnh
    row.trang_thai = payload.trangThai
    db.commit()
    write_audit(db, user.username, "UPDATE", "Service", code, payload.tenDV)
    return service_out(row)


@router.delete("/{code}")
def delete_service(code: str, user: User = Depends(catalog_writer), db: Session = Depends(get_db)):
    row = db.query(Service).filter(Service.ma_dv == code).first()
    if not row:
        raise HTTPException(404, "Không tìm thấy dịch vụ")
    db.query(ServiceUsage).filter(ServiceUsage.ma_dv == code).delete()
    db.delete(row)
    db.commit()
    write_audit(db, user.username, "DELETE", "Service", code, row.ten_dv)
    return {"ok": True}
