from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.models.entities import Customer, DressRental, ServiceUsage, User
from backend.routes.schemas import CustomerIn, customer_out
from backend.services.audit import write_audit
from backend.services.auth_service import get_current_user
from backend.utils.ids import generate_code

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("")
def list_customers(q: str = "", _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Customer)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Customer.ten_kh.like(like)) | (Customer.ma_kh.like(like)) | (Customer.sdt.like(like))
        )
    return [customer_out(c) for c in query.order_by(Customer.ma_kh.asc()).all()]


@router.post("")
def create_customer(payload: CustomerIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    code = (payload.maKH or "").strip().upper() or generate_code(db, Customer, "ma_kh", "KH")
    if db.query(Customer).filter(Customer.ma_kh == code).first():
        raise HTTPException(400, "Mã khách hàng đã tồn tại")
    row = Customer(ma_kh=code, ten_kh=payload.tenKH.strip(), sdt=payload.sdt, dia_chi=payload.diaChi, email=payload.email)
    db.add(row)
    db.commit()
    write_audit(db, user.username, "CREATE", "Customer", code, payload.tenKH)
    return customer_out(row)


@router.put("/{code}")
def update_customer(code: str, payload: CustomerIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.query(Customer).filter(Customer.ma_kh == code).first()
    if not row:
        raise HTTPException(404, "Không tìm thấy khách hàng")
    row.ten_kh = payload.tenKH.strip()
    row.sdt = payload.sdt
    row.dia_chi = payload.diaChi
    row.email = payload.email
    db.commit()
    write_audit(db, user.username, "UPDATE", "Customer", code, payload.tenKH)
    return customer_out(row)


@router.delete("/{code}")
def delete_customer(code: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.query(Customer).filter(Customer.ma_kh == code).first()
    if not row:
        raise HTTPException(404, "Không tìm thấy khách hàng")
    if db.query(DressRental).filter(DressRental.ma_kh == code).count():
        raise HTTPException(400, "Khách hàng đã có hợp đồng thuê, không thể xóa")
    db.query(ServiceUsage).filter(ServiceUsage.ma_kh == code).delete()
    db.delete(row)
    db.commit()
    write_audit(db, user.username, "DELETE", "Customer", code, row.ten_kh)
    return {"ok": True}
