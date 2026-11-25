from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    username: str
    password: str


class ServiceTypeIn(BaseModel):
    maLoaiDV: Optional[str] = None
    tenLoaiDV: str
    moTa: str
    trangThai: bool = True


class ServiceIn(BaseModel):
    maDV: Optional[str] = None
    tenDV: str
    maLoaiDV: str
    donGia: float = Field(ge=0)
    moTa: Optional[str] = ""
    hinhAnh: Optional[str] = ""
    trangThai: str = "active"


class CustomerIn(BaseModel):
    maKH: Optional[str] = None
    tenKH: str
    sdt: Optional[str] = ""
    diaChi: Optional[str] = ""
    email: Optional[str] = ""
    tenVo: Optional[str] = ""
    tenChong: Optional[str] = ""
    ngayCuoi: Optional[str] = None
    nguonKhach: Optional[str] = ""


class DressIn(BaseModel):
    maDress: Optional[str] = None
    tenAo: str
    loaiAo: str
    donGia: float = Field(ge=0)
    hinhAnh: Optional[str] = ""
    size: Optional[str] = ""
    mau: Optional[str] = ""
    phuKien: Optional[str] = ""
    trangThai: str = "SAN_SANG"
    ghiChu: Optional[str] = ""


class RentalIn(BaseModel):
    maKH: str
    dresses: list[str]
    ngayThue: str
    ngayTraDuKien: str
    tienCoc: Optional[float] = None
    phuongThuc: Optional[str] = "TIEN_MAT"
    ghiChu: Optional[str] = ""


class RentalUpdateIn(BaseModel):
    ngayTraDuKien: Optional[str] = None
    tienCoc: Optional[float] = None
    ghiChu: Optional[str] = None


class ReturnIn(BaseModel):
    ngayTraThucTe: Optional[str] = None
    damaged: list[str] = []
    ghiChu: Optional[str] = ""
    ghiChuHong: Optional[str] = ""


class ServiceUsageIn(BaseModel):
    maKH: str
    maDV: str
    ngaySD: str
    giaLucSD: Optional[float] = None
    ghiChu: Optional[str] = ""


class UserIn(BaseModel):
    username: str
    fullName: str
    password: str
    role: str = "staff"
    isActive: bool = True


class PasswordIn(BaseModel):
    password: str


def type_out(row) -> dict:
    return {
        "maLoaiDV": row.ma_loai_dv,
        "tenLoaiDV": row.ten_loai_dv,
        "moTa": row.mo_ta,
        "trangThai": bool(row.trang_thai),
        "createdAt": row.created_at.isoformat() if row.created_at else None,
    }


def service_out(row) -> dict:
    loai = row.loai
    return {
        "maDV": row.ma_dv,
        "tenDV": row.ten_dv,
        "maLoaiDV": row.ma_loai_dv,
        "tenLoaiDV": loai.ten_loai_dv if loai else row.ma_loai_dv,
        "donGia": row.don_gia,
        "moTa": row.mo_ta,
        "hinhAnh": row.hinh_anh,
        "trangThai": row.trang_thai,
        "createdAt": row.created_at.isoformat() if row.created_at else None,
    }


def parse_optional_date(value: Optional[str]):
    if not value:
        return None
    return date.fromisoformat(str(value)[:10])


def customer_out(row) -> dict:
    return {
        "maKH": row.ma_kh,
        "tenKH": row.ten_kh,
        "sdt": row.sdt,
        "diaChi": row.dia_chi,
        "email": row.email,
        "tenVo": row.ten_vo or "",
        "tenChong": row.ten_chong or "",
        "ngayCuoi": row.ngay_cuoi.isoformat() if row.ngay_cuoi else None,
        "nguonKhach": row.nguon_khach or "",
        "ngayTao": row.ngay_tao.isoformat() if row.ngay_tao else None,
    }


def dress_out(row) -> dict:
    return {
        "maDress": row.ma_dress,
        "tenAo": row.ten_ao,
        "loaiAo": row.loai_ao,
        "donGia": row.don_gia,
        "tienCoc": round((row.don_gia or 0) * 0.5, 0),
        "hinhAnh": row.hinh_anh,
        "size": row.size or "",
        "mau": row.mau or "",
        "phuKien": row.phu_kien or "",
        "trangThai": row.trang_thai,
        "ghiChu": row.ghi_chu,
        "createdAt": row.created_at.isoformat() if row.created_at else None,
    }


def user_out(row) -> dict:
    return {
        "id": row.id,
        "username": row.username,
        "fullName": row.full_name,
        "role": row.role,
        "isActive": bool(row.is_active),
        "createdAt": row.created_at.isoformat() if row.created_at else None,
    }
