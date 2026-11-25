from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from backend.config.database import get_db
from backend.models.entities import DressRental, DressRentalItem, User
from backend.routes.schemas import RentalIn, RentalUpdateIn, ReturnIn
from backend.services.audit import write_audit
from backend.services.auth_service import cashier_writer, get_current_user, studio_writer, warehouse_writer
from backend.services.rental_service import (
    create_rental,
    load_rental,
    pay_penalty,
    refresh_overdue,
    return_rental,
    serialize_rental,
    update_rental,
)

router = APIRouter(prefix="/api/rentals", tags=["rentals"])


@router.get("")
def list_rentals(status: str = "", maKH: str = "", _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    refresh_overdue(db)
    query = db.query(DressRental).options(
        joinedload(DressRental.items).joinedload(DressRentalItem.dress),
        joinedload(DressRental.customer),
        joinedload(DressRental.payments),
        joinedload(DressRental.history),
    )
    if status:
        query = query.filter(DressRental.trang_thai == status)
    if maKH:
        query = query.filter(DressRental.ma_kh == maKH)
    rows = query.order_by(DressRental.created_at.desc()).all()
    return [serialize_rental(r) for r in rows]


@router.get("/{code}")
def get_rental(code: str, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    refresh_overdue(db)
    return serialize_rental(load_rental(db, code))


@router.post("")
def add_rental(payload: RentalIn, user: User = Depends(studio_writer), db: Session = Depends(get_db)):
    rental = create_rental(db, payload.model_dump(), user.username)
    write_audit(db, user.username, "CREATE", "DressRental", rental.ma_hop_dong, f"Thuê {len(payload.dresses)} bộ")
    return serialize_rental(load_rental(db, rental.ma_hop_dong))


@router.put("/{code}")
def edit_rental(code: str, payload: RentalUpdateIn, user: User = Depends(studio_writer), db: Session = Depends(get_db)):
    rental = update_rental(db, code, payload.model_dump(), user.username)
    write_audit(db, user.username, "UPDATE", "DressRental", code, "Cập nhật hợp đồng")
    return serialize_rental(load_rental(db, rental.ma_hop_dong))


@router.post("/{code}/return")
def do_return(code: str, payload: ReturnIn, user: User = Depends(warehouse_writer), db: Session = Depends(get_db)):
    rental = return_rental(db, code, payload.model_dump(), user.username)
    write_audit(db, user.username, "RETURN", "DressRental", code, "Nhận trả áo cưới")
    return serialize_rental(load_rental(db, rental.ma_hop_dong))


@router.post("/{code}/pay-penalty")
def do_pay(code: str, user: User = Depends(cashier_writer), db: Session = Depends(get_db)):
    rental = pay_penalty(db, code, user.username)
    write_audit(db, user.username, "PAY", "DressRental", code, "Thanh toán phí trễ hạn")
    return serialize_rental(load_rental(db, rental.ma_hop_dong))


@router.delete("/{code}")
def delete_rental(code: str, user: User = Depends(studio_writer), db: Session = Depends(get_db)):
    rental = load_rental(db, code)
    if rental.trang_thai != "DA_TRA":
        raise HTTPException(400, "Chỉ xóa hợp đồng đã hoàn tất trả")
    db.delete(rental)
    db.commit()
    write_audit(db, user.username, "DELETE", "DressRental", code, "Xóa hợp đồng")
    return {"ok": True}
