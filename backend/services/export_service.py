from __future__ import annotations

import csv
import io
from datetime import date, datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


GOLD = colors.HexColor("#c59b27")
PURPLE = colors.HexColor("#5c3873")
LIGHT = colors.HexColor("#f5eff9")


def _font_name() -> str:
    candidates = [
        Path(r"C:\Windows\Fonts\arial.ttf"),
        Path(r"C:\Windows\Fonts\tahoma.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
        Path("/Library/Fonts/Arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            if "LuxeSans" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("LuxeSans", str(path)))
            return "LuxeSans"
    return "Helvetica"


def _styles():
    font = _font_name()
    base = getSampleStyleSheet()
    base.add(ParagraphStyle(name="LuxeTitle", fontName=font, fontSize=18, textColor=PURPLE, spaceAfter=8, leading=22))
    base.add(ParagraphStyle(name="LuxeSub", fontName=font, fontSize=10, textColor=colors.HexColor("#64748b"), spaceAfter=12))
    base.add(ParagraphStyle(name="LuxeBody", fontName=font, fontSize=10, leading=14))
    return base, font


def rows_to_csv(headers: list[str], rows: list[list]) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    writer.writerows(rows)
    return ("\ufeff" + buf.getvalue()).encode("utf-8")


def rows_to_xlsx(title: str, headers: list[str], rows: list[list]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = title[:31]
    header_fill = PatternFill("solid", fgColor="5C3873")
    header_font = Font(color="FFFFFF", bold=True)
    ws.append([title])
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    ws["A1"].font = Font(bold=True, size=14, color="5C3873")
    ws.append(headers)
    for cell in ws[2]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def build_pdf(title: str, subtitle: str, headers: list[str], rows: list[list], footer: str = "") -> bytes:
    styles, font = _styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story = [
        Paragraph("LUXE WEDDING STUDIO", styles["LuxeTitle"]),
        Paragraph(title, styles["LuxeTitle"]),
        Paragraph(subtitle, styles["LuxeSub"]),
    ]
    data = [headers] + [[str(c) if c is not None else "" for c in row] for row in rows]
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), font),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, -1), LIGHT),
                ("GRID", (0, 0), (-1, -1), 0.4, GOLD),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 16))
    story.append(Paragraph(footer or f"Xuất lúc {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["LuxeBody"]))
    doc.build(story)
    return buf.getvalue()


def invoice_pdf(customer: dict, rental: dict | None, services: list[dict], totals: dict) -> bytes:
    styles, font = _styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    story = [
        Paragraph("LUXE WEDDING STUDIO", styles["LuxeTitle"]),
        Paragraph("HÓA ĐƠN DỊCH VỤ / HÓA ĐƠN ĐỎ (MẪU NỘI BỘ)", styles["LuxeTitle"]),
        Paragraph(f"Khách hàng: {customer.get('tenKH')} — {customer.get('maKH')}", styles["LuxeBody"]),
        Paragraph(f"SĐT: {customer.get('sdt') or '-'} | Địa chỉ: {customer.get('diaChi') or '-'}", styles["LuxeBody"]),
        Paragraph(f"Ngày lập: {date.today().strftime('%d/%m/%Y')}", styles["LuxeSub"]),
    ]
    rows = [["Hạng mục", "Loại", "Ngày", "Thành tiền (VNĐ)"]]
    for s in services:
        rows.append([s.get("tenDV"), s.get("loaiDV"), s.get("ngaySD"), f"{s.get('giaLucSD', 0):,.0f}"])
    if rental:
        for item in rental.get("items") or []:
            rows.append([item.get("tenAo"), "Thuê áo cưới", rental.get("ngayThue"), f"{item.get('donGia', 0):,.0f}"])
        if rental.get("phiTreHan"):
            rows.append(["Phí trễ hạn", "Phạt", rental.get("ngayTraDuKien"), f"{rental.get('phiTreHan', 0):,.0f}"])
    rows.append(["TỔNG CỘNG", "", "", f"{totals.get('grandTotal', 0):,.0f}"])
    table = Table(rows, colWidths=[220, 110, 80, 110])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), font),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, GOLD),
                ("ALIGN", (3, 1), (3, -1), "RIGHT"),
                ("BACKGROUND", (0, -1), (-1, -1), GOLD),
                ("FONTSIZE", (0, -1), (-1, -1), 11),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 24))
    story.append(Paragraph("Cảm ơn quý khách đã tin tưởng LUXE WEDDING STUDIO.", styles["LuxeBody"]))
    story.append(Paragraph("Hóa đơn này dùng cho mục đích quản lý nội bộ studio.", styles["LuxeSub"]))
    pays = []
    for r in customer.get("rentals") or []:
        pays.extend(r.get("payments") or [])
    pays.extend(customer.get("payments") or [])
    if pays:
        story.append(Spacer(1, 16))
        story.append(Paragraph("Sổ thanh toán / biên lai", styles["LuxeTitle"]))
        prow = [["Biên lai", "Loại", "Hình thức", "Số tiền", "Còn lại"]]
        for p in pays:
            prow.append(
                [
                    p.get("maBienLai") or p.get("maGD"),
                    p.get("loai"),
                    p.get("phuongThuc"),
                    f"{p.get('soTien', 0):,.0f}",
                    f"{p.get('soConLai', 0):,.0f}",
                ]
            )
        ptable = Table(prow, colWidths=[110, 90, 90, 110, 110])
        ptable.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), font),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.4, GOLD),
                    ("ALIGN", (3, 1), (4, -1), "RIGHT"),
                ]
            )
        )
        story.append(ptable)
    doc.build(story)
    return buf.getvalue()


def receipt_pdf(payment: dict) -> bytes:
    styles, font = _styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=48, rightMargin=48, topMargin=48, bottomMargin=48)
    method = "Tiền mặt" if payment.get("phuongThuc") == "TIEN_MAT" else "Chuyển khoản"
    story = [
        Paragraph("LUXE WEDDING STUDIO", styles["LuxeTitle"]),
        Paragraph("BIÊN LAI THU TIỀN", styles["LuxeTitle"]),
        Paragraph(f"Số biên lai: {payment.get('maBienLai')}", styles["LuxeBody"]),
        Paragraph(f"Mã GD: {payment.get('maGD')} · HĐ: {payment.get('maHopDong') or '-'}", styles["LuxeBody"]),
        Paragraph(f"Khách: {payment.get('maKH')}", styles["LuxeBody"]),
        Paragraph(f"Loại: {payment.get('loaiTen') or payment.get('loai')}", styles["LuxeBody"]),
        Paragraph(f"Hình thức: {method}", styles["LuxeBody"]),
        Paragraph(f"Số tiền: {payment.get('soTien', 0):,.0f} VNĐ", styles["LuxeTitle"]),
        Paragraph(f"Còn lại sau giao dịch: {payment.get('soConLai', 0):,.0f} VNĐ", styles["LuxeBody"]),
        Paragraph(payment.get("ghiChu") or "", styles["LuxeSub"]),
        Paragraph(f"Thu ngân: {payment.get('createdBy') or '-'}", styles["LuxeBody"]),
    ]
    doc.build(story)
    return buf.getvalue()
