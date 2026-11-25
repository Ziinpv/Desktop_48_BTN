from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from backend.config.database import get_db
from backend.models.entities import Appointment, Customer, Service, User
from backend.services.audit import write_audit
from backend.services.auth_service import get_current_user
from backend.utils.ids import generate_code

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


class AppointmentIn(BaseModel):
    maKH: str
    maDV: str | None = None
    nhiepAnh: str = ""
    phong: str = ""
    batDau: str
    ketThuc: str
    trangThai: str = "DA_DAT"
    ghiChu: str | None = ""


def out(row: Appointment) -> dict:
    return {
        "maLich": row.ma_lich,
        "maKH": row.ma_kh,
        "tenKH": row.customer.ten_kh if row.customer else row.ma_kh,
        "sdt": row.customer.sdt if row.customer else "",
        "maDV": row.ma_dv,
        "tenDV": row.service.ten_dv if row.service else "",
        "nhiepAnh": row.nhiep_anh,
        "phong": row.phong,
        "batDau": row.bat_dau.isoformat() if row.bat_dau else None,
        "ketThuc": row.ket_thuc.isoformat() if row.ket_thuc else None,
        "trangThai": row.trang_thai,
        "ghiChu": row.ghi_chu,
    }


@router.get("")
def list_appts(fromDate: str = "", toDate: str = "", _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Appointment).options(joinedload(Appointment.customer), joinedload(Appointment.service))
    if fromDate:
        q = q.filter(Appointment.bat_dau >= datetime.fromisoformat(fromDate))
    if toDate:
        q = q.filter(Appointment.bat_dau <= datetime.fromisoformat(toDate + "T23:59:59"))
    return [out(r) for r in q.order_by(Appointment.bat_dau.asc()).all()]


@router.post("")
def create_appt(payload: AppointmentIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.query(Customer).filter(Customer.ma_kh == payload.maKH).first():
        raise HTTPException(404, "Không tìm thấy khách hàng")
    if payload.maDV and not db.query(Service).filter(Service.ma_dv == payload.maDV).first():
        raise HTTPException(404, "Không tìm thấy dịch vụ")
    start = datetime.fromisoformat(payload.batDau)
    end = datetime.fromisoformat(payload.ketThuc)
    if end <= start:
        raise HTTPException(400, "Giờ kết thúc phải sau giờ bắt đầu")
    clash = (
        db.query(Appointment)
        .filter(Appointment.trang_thai != "HUY", Appointment.bat_dau < end, Appointment.ket_thuc > start)
        .filter((Appointment.nhiep_anh == payload.nhiepAnh) | (Appointment.phong == payload.phong))
        .first()
    )
    if clash and (payload.nhiepAnh or payload.phong):
        raise HTTPException(400, f"Trùng khung giờ với lịch {clash.ma_lich}")
    row = Appointment(
        ma_lich=generate_code(db, Appointment, "ma_lich", "LH"),
        ma_kh=payload.maKH,
        ma_dv=payload.maDV,
        nhiep_anh=payload.nhiepAnh,
        phong=payload.phong,
        bat_dau=start,
        ket_thuc=end,
        trang_thai=payload.trangThai,
        ghi_chu=payload.ghiChu,
        created_by=user.username,
    )
    db.add(row)
    db.commit()
    write_audit(db, user.username, "CREATE", "Appointment", row.ma_lich, payload.maKH)
    db.refresh(row)
    row = db.query(Appointment).options(joinedload(Appointment.customer), joinedload(Appointment.service)).filter(Appointment.ma_lich == row.ma_lich).first()
    return out(row)


@router.put("/{code}")
def update_appt(code: str, payload: AppointmentIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.query(Appointment).filter(Appointment.ma_lich == code).first()
    if not row:
        raise HTTPException(404, "Không tìm thấy lịch hẹn")
    row.ma_kh = payload.maKH
    row.ma_dv = payload.maDV
    row.nhiep_anh = payload.nhiepAnh
    row.phong = payload.phong
    row.bat_dau = datetime.fromisoformat(payload.batDau)
    row.ket_thuc = datetime.fromisoformat(payload.ketThuc)
    row.trang_thai = payload.trangThai
    row.ghi_chu = payload.ghiChu
    db.commit()
    write_audit(db, user.username, "UPDATE", "Appointment", code, payload.maKH)
    row = db.query(Appointment).options(joinedload(Appointment.customer), joinedload(Appointment.service)).filter(Appointment.ma_lich == code).first()
    return out(row)


@router.delete("/{code}")
def delete_appt(code: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.query(Appointment).filter(Appointment.ma_lich == code).first()
    if not row:
        raise HTTPException(404, "Không tìm thấy lịch hẹn")
    db.delete(row)
    db.commit()
    write_audit(db, user.username, "DELETE", "Appointment", code, "")
    return {"ok": True}
