from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.models.entities import Payment, User
from backend.services.audit import write_audit
from backend.services.auth_service import cashier_writer, get_current_user
from backend.services.export_service import receipt_pdf
from backend.services.payment_service import payment_out, record_payment
from backend.routes.export import _file

router = APIRouter(prefix="/api/payments", tags=["payments"])


class PaymentIn(BaseModel):
    maKH: str | None = None
    maHopDong: str | None = None
    maDV: str | None = None
    loai: str = "COC"
    soTien: float = Field(gt=0)
    phuongThuc: str = "TIEN_MAT"
    ghiChu: str | None = ""


@router.get("")
def list_payments(
    maHopDong: str = "",
    maKH: str = "",
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Payment)
    if maHopDong:
        q = q.filter(Payment.ma_hop_dong == maHopDong)
    if maKH:
        q = q.filter(Payment.ma_kh == maKH)
    rows = q.order_by(Payment.created_at.desc()).all()
    return [payment_out(r) for r in rows]


@router.post("")
def add_payment(payload: PaymentIn, user: User = Depends(cashier_writer), db: Session = Depends(get_db)):
    row = record_payment(db, payload.model_dump(), user.username)
    write_audit(db, user.username, "CREATE", "Payment", row.ma_gd, f"{row.loai} {row.so_tien}")
    return payment_out(row)


@router.get("/{code}/receipt")
def receipt(code: str, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.query(Payment).filter((Payment.ma_gd == code) | (Payment.ma_bien_lai == code)).first()
    if not row:
        raise HTTPException(404, "Không tìm thấy biên lai")
    return _file(receipt_pdf(payment_out(row)), f"bien-lai-{row.ma_bien_lai}.pdf", "application/pdf")
