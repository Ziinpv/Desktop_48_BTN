from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from backend.models.entities import (
    Customer,
    Dress,
    DressRental,
    DressRentalItem,
    Payment,
    RentalHistory,
)
from backend.services.rules import (
    ACTIVE_RENTAL_STATUSES,
    calc_deposit,
    calc_late_fee,
    can_rent_more,
    dates_overlap,
    days_late,
)
from backend.utils.ids import generate_code


def refresh_overdue(db: Session) -> int:
    today = date.today()
    changed = 0
    rows = db.query(DressRental).filter(DressRental.trang_thai == "DANG_THUE").all()
    for rental in rows:
        if rental.ngay_tra_du_kien and rental.ngay_tra_du_kien < today:
            rental.trang_thai = "QUA_HAN"
            db.add(
                RentalHistory(
                    ma_hop_dong=rental.ma_hop_dong,
                    trang_thai="QUA_HAN",
                    tien_phat=_penalty_for(rental, today),
                    ghi_chu="Tự động chuyển quá hạn",
                    username="system",
                )
            )
            changed += 1
    if changed:
        db.commit()
    return changed


def active_dress_count(db: Session, ma_kh: str, exclude_hd: str | None = None) -> int:
    q = (
        db.query(DressRentalItem)
        .join(DressRental, DressRentalItem.ma_hop_dong == DressRental.ma_hop_dong)
        .filter(DressRental.ma_kh == ma_kh, DressRental.trang_thai.in_(ACTIVE_RENTAL_STATUSES))
    )
    if exclude_hd:
        q = q.filter(DressRental.ma_hop_dong != exclude_hd)
    return q.count()


def _dress_conflicts(db: Session, ma_dress: str, start: date, end: date, exclude_hd: str | None = None) -> list[str]:
    q = (
        db.query(DressRental)
        .join(DressRentalItem, DressRentalItem.ma_hop_dong == DressRental.ma_hop_dong)
        .filter(
            DressRentalItem.ma_dress == ma_dress,
            DressRental.trang_thai.in_(ACTIVE_RENTAL_STATUSES + ("DA_TRA",)),
        )
    )
    if exclude_hd:
        q = q.filter(DressRental.ma_hop_dong != exclude_hd)
    conflicts = []
    for rental in q.all():
        actual_end = rental.ngay_tra_thuc_te or rental.ngay_tra_du_kien
        if dates_overlap(start, end, rental.ngay_thue, actual_end):
            conflicts.append(rental.ma_hop_dong)
    return conflicts


def _penalty_for(rental: DressRental, today: date | None = None) -> float:
    today = today or date.today()
    late = days_late(rental.ngay_tra_du_kien, today)
    total = 0.0
    for item in rental.items:
        total += calc_late_fee(item.don_gia, late)
    return total


def serialize_rental(rental: DressRental, today: date | None = None) -> dict:
    today = today or date.today()
    ref_date = rental.ngay_tra_thuc_te if rental.trang_thai == "DA_TRA" and rental.ngay_tra_thuc_te else today
    late = days_late(rental.ngay_tra_du_kien, ref_date) if rental.ngay_tra_du_kien else 0
    sap_het = (
        rental.trang_thai == "DANG_THUE"
        and rental.ngay_tra_du_kien is not None
        and 0 <= (rental.ngay_tra_du_kien - today).days <= 3
    )
    items = []
    tien_thue = 0.0
    for item in rental.items:
        dress = item.dress
        tien_thue += item.don_gia or 0
        items.append(
            {
                "id": item.id,
                "maDress": item.ma_dress,
                "tenAo": dress.ten_ao if dress else item.ma_dress,
                "loaiAo": dress.loai_ao if dress else "",
                "hinhAnh": dress.hinh_anh if dress else "",
                "donGia": item.don_gia,
                "tienCoc": item.tien_coc,
                "tinhTrangAo": item.tinh_trang_ao,
                "phiTre": calc_late_fee(item.don_gia, late),
            }
        )
    phi_tre = _penalty_for(rental, ref_date)
    paid_penalty = sum((h.tien_phat or 0) for h in (rental.history or []) if h.trang_thai == "THANH_TOAN_PHAT")
    tien_coc = rental.tien_coc or 0
    if rental.trang_thai == "DA_TRA":
        han_tra = "DUNG_HAN" if late == 0 else "TRE_HAN"
    elif rental.trang_thai == "QUA_HAN":
        han_tra = "TRE_HAN"
    else:
        han_tra = "SAP_HET_HAN" if sap_het else "TRONG_HAN"
    da_thu = 0.0
    payment_rows = []
    for p in rental.payments or []:
        if p.loai == "HOAN_COC":
            da_thu -= p.so_tien or 0
        else:
            da_thu += p.so_tien or 0
        payment_rows.append(
            {
                "maGD": p.ma_gd,
                "maBienLai": p.ma_bien_lai,
                "loai": p.loai,
                "soTien": p.so_tien,
                "phuongThuc": p.phuong_thuc,
                "soConLai": p.so_con_lai,
                "createdAt": p.created_at.isoformat() if p.created_at else None,
                "createdBy": p.created_by,
                "ghiChu": p.ghi_chu,
            }
        )
    if not payment_rows:
        da_thu = tien_coc + paid_penalty + (tien_thue if rental.trang_thai == "DA_TRA" else 0)
    phai_thu = tien_coc + tien_thue + phi_tre
    da_thanh_toan = da_thu
    con_no = max(0.0, phai_thu - da_thu)

    customer = rental.customer
    return {
        "maHopDong": rental.ma_hop_dong,
        "maKH": rental.ma_kh,
        "tenKH": customer.ten_kh if customer else rental.ma_kh,
        "sdt": customer.sdt if customer else "",
        "diaChi": customer.dia_chi if customer else "",
        "email": customer.email if customer else "",
        "ngayThue": rental.ngay_thue.isoformat() if rental.ngay_thue else None,
        "ngayNhan": rental.ngay_thue.isoformat() if rental.ngay_thue else None,
        "ngayTraDuKien": rental.ngay_tra_du_kien.isoformat() if rental.ngay_tra_du_kien else None,
        "ngayTraThucTe": rental.ngay_tra_thuc_te.isoformat() if rental.ngay_tra_thuc_te else None,
        "tienCoc": tien_coc,
        "tienThue": tien_thue,
        "phaiThu": phai_thu,
        "daThanhToan": da_thanh_toan,
        "tienPhatDaThu": paid_penalty,
        "conNo": con_no,
        "payments": payment_rows,
        "hanTra": han_tra,
        "trangThai": rental.trang_thai,
        "ghiChu": rental.ghi_chu,
        "createdAt": rental.created_at.isoformat() if rental.created_at else None,
        "createdBy": rental.created_by,
        "items": items,
        "soBo": len(items),
        "soNgayTre": late,
        "phiTreHan": phi_tre,
        "sapHetHan": sap_het,
        "boAo": ", ".join(f"{i['maDress']} · {i['tenAo']}" for i in items),
    }


def create_rental(db: Session, payload: dict, username: str) -> DressRental:
    ma_kh = payload["maKH"]
    dresses = payload.get("dresses") or []
    if not dresses:
        raise HTTPException(400, "Chọn ít nhất một bộ áo cưới")
    if len(set(dresses)) != len(dresses):
        raise HTTPException(400, "Không được chọn trùng bộ áo trong cùng hợp đồng")

    customer = db.query(Customer).filter(Customer.ma_kh == ma_kh).first()
    if not customer:
        raise HTTPException(404, "Không tìm thấy khách hàng")

    start = date.fromisoformat(payload["ngayThue"])
    due = date.fromisoformat(payload["ngayTraDuKien"])
    if due < start:
        raise HTTPException(400, "Ngày trả dự kiến phải sau ngày thuê")

    current = active_dress_count(db, ma_kh)
    if not can_rent_more(current, len(dresses)):
        raise HTTPException(
            400,
            f"Khách hàng đang thuê {current} bộ. Tối đa 3 bộ cùng lúc (còn nhận {max(0, 3 - current)} bộ).",
        )

    total_deposit = 0.0
    item_rows = []
    warnings = []
    for ma_dress in dresses:
        dress = db.query(Dress).filter(Dress.ma_dress == ma_dress).first()
        if not dress:
            raise HTTPException(404, f"Không tìm thấy bộ áo {ma_dress}")
        if dress.trang_thai == "HON_HOC":
            warnings.append(f"{ma_dress} đang ở trạng thái hỏng hóc")
            raise HTTPException(400, f"Bộ áo {ma_dress} đang hỏng hóc, không cho thuê")
        if dress.trang_thai == "HET_HANG":
            raise HTTPException(400, f"Bộ áo {ma_dress} đã hết hàng")
        conflicts = _dress_conflicts(db, ma_dress, start, due)
        if conflicts:
            raise HTTPException(400, f"Bộ áo {ma_dress} đã được thuê trùng ngày (HĐ {', '.join(conflicts)})")
        deposit = calc_deposit(dress.don_gia)
        total_deposit += deposit
        item_rows.append((dress, deposit))

    ma_hd = generate_code(db, DressRental, "ma_hop_dong", "HD")
    rental = DressRental(
        ma_hop_dong=ma_hd,
        ma_kh=ma_kh,
        ngay_thue=start,
        ngay_tra_du_kien=due,
        tien_coc=payload.get("tienCoc", total_deposit) if payload.get("tienCoc") is not None else total_deposit,
        trang_thai="DANG_THUE",
        ghi_chu=payload.get("ghiChu") or ("; ".join(warnings)),
        created_by=username,
    )
    if due < date.today():
        rental.trang_thai = "QUA_HAN"
    db.add(rental)
    db.flush()

    for dress, deposit in item_rows:
        db.add(
            DressRentalItem(
                ma_hop_dong=ma_hd,
                ma_dress=dress.ma_dress,
                don_gia=dress.don_gia,
                tien_coc=deposit,
                tinh_trang_ao="TOT",
            )
        )
        dress.trang_thai = "DANG_THUE"

    db.add(
        RentalHistory(
            ma_hop_dong=ma_hd,
            trang_thai=rental.trang_thai,
            tien_phat=0,
            ghi_chu="Lập hợp đồng thuê",
            username=username,
        )
    )
    collected = rental.tien_coc or 0
    if collected > 0:
        tien_thue = sum(d.don_gia for d, _ in item_rows)
        db.add(
            Payment(
                ma_gd=generate_code(db, Payment, "ma_gd", "GD"),
                ma_bien_lai=generate_code(db, Payment, "ma_bien_lai", "BL"),
                ma_kh=ma_kh,
                ma_hop_dong=ma_hd,
                loai="COC",
                so_tien=collected,
                phuong_thuc=payload.get("phuongThuc") or "TIEN_MAT",
                so_con_lai=max(0.0, collected + tien_thue - collected),
                ghi_chu="Thu cọc khi lập hợp đồng",
                created_by=username,
            )
        )
    db.commit()
    db.refresh(rental)
    return rental


def update_rental(db: Session, ma_hd: str, payload: dict, username: str) -> DressRental:
    rental = (
        db.query(DressRental)
        .options(joinedload(DressRental.items).joinedload(DressRentalItem.dress), joinedload(DressRental.customer))
        .filter(DressRental.ma_hop_dong == ma_hd)
        .first()
    )
    if not rental:
        raise HTTPException(404, "Không tìm thấy hợp đồng")
    if rental.trang_thai == "DA_TRA":
        raise HTTPException(400, "Hợp đồng đã trả, không sửa được")

    if "ngayTraDuKien" in payload and payload["ngayTraDuKien"]:
        rental.ngay_tra_du_kien = date.fromisoformat(payload["ngayTraDuKien"])
    if "ghiChu" in payload:
        rental.ghi_chu = payload["ghiChu"]
    if "tienCoc" in payload and payload["tienCoc"] is not None:
        rental.tien_coc = payload["tienCoc"]

    if rental.ngay_tra_du_kien < date.today() and rental.trang_thai == "DANG_THUE":
        rental.trang_thai = "QUA_HAN"

    db.add(RentalHistory(ma_hop_dong=ma_hd, trang_thai=rental.trang_thai, ghi_chu="Cập nhật hợp đồng", username=username))
    db.commit()
    db.refresh(rental)
    return rental


def return_rental(db: Session, ma_hd: str, payload: dict, username: str) -> DressRental:
    rental = (
        db.query(DressRental)
        .options(joinedload(DressRental.items).joinedload(DressRentalItem.dress), joinedload(DressRental.customer))
        .filter(DressRental.ma_hop_dong == ma_hd)
        .first()
    )
    if not rental:
        raise HTTPException(404, "Không tìm thấy hợp đồng")
    if rental.trang_thai == "DA_TRA":
        raise HTTPException(400, "Hợp đồng đã hoàn tất trả")

    today = date.fromisoformat(payload["ngayTraThucTe"]) if payload.get("ngayTraThucTe") else date.today()
    rental.ngay_tra_thuc_te = today
    rental.trang_thai = "DA_TRA"
    penalty = _penalty_for(rental, today)

    damaged = payload.get("damaged") or []
    for item in rental.items:
        if item.ma_dress in damaged:
            item.tinh_trang_ao = "HON_HOC"
            if item.dress:
                item.dress.trang_thai = "HON_HOC"
                item.dress.ghi_chu = payload.get("ghiChuHong") or "Hỏng hóc khi trả"
        elif item.dress and item.dress.trang_thai != "HON_HOC":
            item.dress.trang_thai = "SAN_SANG"

    db.add(
        RentalHistory(
            ma_hop_dong=ma_hd,
            trang_thai="DA_TRA",
            tien_phat=penalty,
            ghi_chu=payload.get("ghiChu") or f"Nhận trả. Phí trễ hạn: {penalty:,.0f}đ",
            username=username,
        )
    )
    db.commit()
    db.refresh(rental)
    return rental


def pay_penalty(db: Session, ma_hd: str, username: str) -> DressRental:
    rental = (
        db.query(DressRental)
        .options(joinedload(DressRental.items).joinedload(DressRentalItem.dress), joinedload(DressRental.customer))
        .filter(DressRental.ma_hop_dong == ma_hd)
        .first()
    )
    if not rental:
        raise HTTPException(404, "Không tìm thấy hợp đồng")
    penalty = _penalty_for(rental)
    db.add(
        RentalHistory(
            ma_hop_dong=ma_hd,
            trang_thai="THANH_TOAN_PHAT",
            tien_phat=penalty,
            ghi_chu=f"Thanh toán phí trễ hạn {penalty:,.0f}đ",
            username=username,
        )
    )
    if penalty > 0:
        db.add(
            Payment(
                ma_gd=generate_code(db, Payment, "ma_gd", "GD"),
                ma_bien_lai=generate_code(db, Payment, "ma_bien_lai", "BL"),
                ma_kh=rental.ma_kh,
                ma_hop_dong=ma_hd,
                loai="PHI_TRE",
                so_tien=penalty,
                phuong_thuc="TIEN_MAT",
                so_con_lai=0,
                ghi_chu="Thanh toán phí trễ hạn",
                created_by=username,
            )
        )
    db.commit()
    db.refresh(rental)
    return rental


def load_rental(db: Session, ma_hd: str) -> DressRental:
    rental = (
        db.query(DressRental)
        .options(
            joinedload(DressRental.items).joinedload(DressRentalItem.dress),
            joinedload(DressRental.customer),
            joinedload(DressRental.payments),
            joinedload(DressRental.history),
        )
        .filter(DressRental.ma_hop_dong == ma_hd)
        .first()
    )
    if not rental:
        raise HTTPException(404, "Không tìm thấy hợp đồng")
    return rental
