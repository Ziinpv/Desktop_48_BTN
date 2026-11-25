from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.config.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(120), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="staff")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ServiceType(Base):
    __tablename__ = "service_types"

    ma_loai_dv = Column(String(20), primary_key=True)
    ten_loai_dv = Column(String(120), nullable=False)
    mo_ta = Column(Text, nullable=False)
    trang_thai = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    services = relationship("Service", back_populates="loai")


class Service(Base):
    __tablename__ = "services"

    ma_dv = Column(String(20), primary_key=True)
    ten_dv = Column(String(200), nullable=False)
    ma_loai_dv = Column(String(20), ForeignKey("service_types.ma_loai_dv"), nullable=False, index=True)
    don_gia = Column(Float, nullable=False)
    mo_ta = Column(Text)
    hinh_anh = Column(String(500))
    trang_thai = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    loai = relationship("ServiceType", back_populates="services")


class Customer(Base):
    __tablename__ = "customers"

    ma_kh = Column(String(20), primary_key=True)
    ten_kh = Column(String(120), nullable=False)
    sdt = Column(String(20), index=True)
    dia_chi = Column(String(255))
    email = Column(String(120))
    ten_vo = Column(String(120))
    ten_chong = Column(String(120))
    ngay_cuoi = Column(Date)
    nguon_khach = Column(String(80))
    ngay_tao = Column(DateTime, default=datetime.utcnow)


class Dress(Base):
    __tablename__ = "dresses"

    ma_dress = Column(String(20), primary_key=True)
    ten_ao = Column(String(200), nullable=False)
    loai_ao = Column(String(80), nullable=False, index=True)
    don_gia = Column(Float, nullable=False)
    hinh_anh = Column(String(500))
    size = Column(String(20))
    mau = Column(String(50))
    phu_kien = Column(String(255))
    trang_thai = Column(String(20), default="SAN_SANG", index=True)
    ghi_chu = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def tien_coc(self) -> float:
        return round((self.don_gia or 0) * 0.5, 0)


class DressRental(Base):
    __tablename__ = "dress_rentals"

    ma_hop_dong = Column(String(20), primary_key=True)
    ma_kh = Column(String(20), ForeignKey("customers.ma_kh"), nullable=False, index=True)
    ngay_thue = Column(Date, nullable=False)
    ngay_tra_du_kien = Column(Date, nullable=False)
    ngay_tra_thuc_te = Column(Date)
    tien_coc = Column(Float, default=0)
    trang_thai = Column(String(20), default="DANG_THUE", index=True)
    ghi_chu = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(50))

    customer = relationship("Customer")
    items = relationship("DressRentalItem", back_populates="rental", cascade="all, delete-orphan")
    history = relationship("RentalHistory", back_populates="rental", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="rental", cascade="all, delete-orphan")


class DressRentalItem(Base):
    __tablename__ = "dress_rental_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ma_hop_dong = Column(String(20), ForeignKey("dress_rentals.ma_hop_dong"), nullable=False, index=True)
    ma_dress = Column(String(20), ForeignKey("dresses.ma_dress"), nullable=False, index=True)
    don_gia = Column(Float, nullable=False)
    tien_coc = Column(Float, nullable=False)
    tinh_trang_ao = Column(String(20), default="TOT")

    rental = relationship("DressRental", back_populates="items")
    dress = relationship("Dress")


class RentalHistory(Base):
    __tablename__ = "rental_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ma_hop_dong = Column(String(20), ForeignKey("dress_rentals.ma_hop_dong"), index=True)
    trang_thai = Column(String(20))
    tien_phat = Column(Float, default=0)
    ngay_cap_nhat = Column(DateTime, default=datetime.utcnow)
    ghi_chu = Column(Text)
    username = Column(String(50))

    rental = relationship("DressRental", back_populates="history")


class ServiceUsage(Base):
    __tablename__ = "service_usage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ma_kh = Column(String(20), ForeignKey("customers.ma_kh"), index=True)
    ma_dv = Column(String(20), ForeignKey("services.ma_dv"), index=True)
    ngay_sd = Column(Date)
    gia_luc_sd = Column(Float)
    ghi_chu = Column(Text)

    customer = relationship("Customer")
    service = relationship("Service")


class Payment(Base):
    __tablename__ = "payments"

    ma_gd = Column(String(20), primary_key=True)
    ma_bien_lai = Column(String(30), unique=True, index=True)
    ma_kh = Column(String(20), ForeignKey("customers.ma_kh"), index=True)
    ma_hop_dong = Column(String(20), ForeignKey("dress_rentals.ma_hop_dong"), index=True)
    ma_dv = Column(String(20), ForeignKey("services.ma_dv"))
    loai = Column(String(20), nullable=False, index=True)
    so_tien = Column(Float, nullable=False)
    phuong_thuc = Column(String(20), default="TIEN_MAT")
    so_con_lai = Column(Float, default=0)
    ghi_chu = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(50))

    rental = relationship("DressRental", back_populates="payments")
    customer = relationship("Customer")


class Appointment(Base):
    __tablename__ = "appointments"

    ma_lich = Column(String(20), primary_key=True)
    ma_kh = Column(String(20), ForeignKey("customers.ma_kh"), nullable=False, index=True)
    ma_dv = Column(String(20), ForeignKey("services.ma_dv"), index=True)
    nhiep_anh = Column(String(80))
    phong = Column(String(80))
    bat_dau = Column(DateTime, nullable=False, index=True)
    ket_thuc = Column(DateTime, nullable=False)
    trang_thai = Column(String(20), default="DA_DAT")
    ghi_chu = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(50))

    customer = relationship("Customer")
    service = relationship("Service")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), index=True)
    action = Column(String(50), nullable=False)
    entity = Column(String(50), nullable=False)
    entity_id = Column(String(50))
    detail = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


Index("ix_rentals_customer_status", DressRental.ma_kh, DressRental.trang_thai)
Index("ix_items_dress_contract", DressRentalItem.ma_dress, DressRentalItem.ma_hop_dong)
