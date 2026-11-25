from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload

from backend.config.database import get_db
from backend.models.entities import Customer, DressRental, DressRentalItem, User
from backend.services.auth_service import get_current_user
from backend.services.export_service import build_pdf, invoice_pdf, rows_to_csv, rows_to_xlsx
from backend.services.rental_service import refresh_overdue, serialize_rental
from backend.services.rules import ACTIVE_RENTAL_STATUSES
from backend.routes.lookup import lookup_customer
from backend.routes.reports import chart_payload

router = APIRouter(prefix="/api/export", tags=["export"])


def _file(content: bytes, filename: str, mime: str):
    return Response(
        content=content,
        media_type=mime,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _unreturned(db: Session):
    refresh_overdue(db)
    rows = (
        db.query(DressRental)
        .options(joinedload(DressRental.items).joinedload(DressRentalItem.dress), joinedload(DressRental.customer))
        .filter(DressRental.trang_thai.in_(ACTIVE_RENTAL_STATUSES))
        .all()
    )
    return [serialize_rental(r) for r in rows]


def _overdue(db: Session):
    refresh_overdue(db)
    rows = (
        db.query(DressRental)
        .options(joinedload(DressRental.items).joinedload(DressRentalItem.dress), joinedload(DressRental.customer))
        .filter(DressRental.trang_thai == "QUA_HAN")
        .all()
    )
    return [serialize_rental(r) for r in rows]


def _table(kind: str, db: Session):
    data = _unreturned(db) if kind == "unreturned" else _overdue(db)
    headers = ["Mã HĐ", "Khách hàng", "SĐT", "Bộ áo", "Ngày thuê", "Dự kiến trả", "Cọc", "Trạng thái", "Phí phạt"]
    rows = []
    for r in data:
        ao = ", ".join(i["maDress"] for i in r["items"])
        rows.append(
            [
                r["maHopDong"],
                r["tenKH"],
                r["sdt"],
                ao,
                r["ngayThue"],
                r["ngayTraDuKien"],
                r["tienCoc"],
                r["trangThai"],
                r.get("phiTreHan") or 0,
            ]
        )
    title = "Khách hàng thuê chưa trả" if kind == "unreturned" else "Khách hàng quá hạn"
    return title, headers, rows


@router.get("/charts.pdf")
def export_charts(
    fromDate: str = "",
    toDate: str = "",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    start = date.fromisoformat(fromDate) if fromDate else date(today.year, today.month, 1)
    end = date.fromisoformat(toDate) if toDate else today
    data = chart_payload(db, start, end)
    headers = ["Tháng", "Doanh thu dịch vụ", "Doanh thu thuê áo", "Đã thu (sổ TT)", "Lượt thuê"]
    rows = []
    for i, label in enumerate(data["revenue"]["labels"]):
        rows.append(
            [
                label,
                data["revenue"]["services"][i],
                data["revenue"]["rentals"][i],
                data["revenue"]["collected"][i],
                data["rentalVolume"][i],
            ]
        )
    totals = data["totals"]
    rows.append(["Tổng", totals["services"], totals["rentals"], totals["collected"], totals["contracts"]])
    for item in data["topServices"]:
        rows.append([f"Top DV: {item['name']}", item["revenue"], item["count"], "", ""])
    title = "Báo cáo đối soát doanh thu"
    subtitle = f"Từ {data['fromDate']} đến {data['toDate']} • LUXE WEDDING STUDIO"
    return _file(
        build_pdf(title, subtitle, headers, rows, footer="Dùng để đối soát cuối tháng theo sổ thanh toán."),
        "bao-cao-doanh-thu.pdf",
        "application/pdf",
    )


@router.get("/{kind}.{fmt}")
def export_report(kind: str, fmt: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if kind not in ("unreturned", "overdue"):
        raise HTTPException(400, "Loại báo cáo không hợp lệ")
    if fmt not in ("csv", "xlsx", "pdf"):
        raise HTTPException(400, "Định dạng không hỗ trợ")
    title, headers, rows = _table(kind, db)
    if fmt == "csv":
        return _file(rows_to_csv(headers, rows), f"{kind}.csv", "text/csv")
    if fmt == "xlsx":
        return _file(
            rows_to_xlsx(title, headers, rows),
            f"{kind}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    return _file(build_pdf(title, "LUXE WEDDING STUDIO • Nhóm 24", headers, rows), f"{kind}.pdf", "application/pdf")


@router.get("/invoice/{ma_kh}")
def export_invoice(ma_kh: str, red: bool = False, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    matches = lookup_customer(ma_kh, user, db)
    if not matches:
        raise HTTPException(404, "Không tìm thấy khách hàng")
    cust = matches[0]
    latest_rental = cust["rentals"][0] if cust["rentals"] else None
    totals = {"grandTotal": cust["grandTotal"]}
    content = invoice_pdf(cust, latest_rental, cust["services"], totals)
    name = f"{'hoa-don-do' if red else 'hoa-don'}-{ma_kh}.pdf"
    return _file(content, name, "application/pdf")
