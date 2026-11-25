"""Sinh PDF hướng dẫn sử dụng tiếng Việt."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.services.export_service import build_pdf

ROWS = [
    ["Đăng nhập", "admin / admin123 hoặc staff / staff123"],
    ["F1 Loại DV", "Thêm/sửa/xóa, không trùng mã, mô tả bắt buộc"],
    ["F2 Dịch vụ", "Đơn giá ≥ 0, hệ thống tự sinh mã DV"],
    ["F3 Thuê áo", "Tối đa 3 bộ/khách, cọc 50%, không trùng ngày"],
    ["F4 Danh mục", "Xem DV theo loại, lọc còn/hết hàng"],
    ["F5 Chưa trả", "Highlight sắp hết hạn 3 ngày, xuất CSV/Excel/PDF"],
    ["F6 Quá hạn", "Phí = đơn giá × 10% × số ngày trễ"],
    ["F7 Tra cứu áo", "Chi tiết, lịch sử, in QR"],
    ["F8 Theo khách", "Tổng DV + thuê, xuất hóa đơn / hóa đơn đỏ"],
    ["Sao lưu", "Cài đặt → Sao lưu ngay (tự động 02:00 mỗi ngày)"],
]


def main():
    out = ROOT / "docs" / "HUONG_DAN_SU_DUNG.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    pdf = build_pdf(
        "Hướng dẫn sử dụng",
        "LUXE WEDDING STUDIO • Nhóm 24 • Hoàng Long 2212407",
        ["Hạng mục", "Cách dùng"],
        ROWS,
        "In tài liệu này kèm installer khi nộp bài.",
    )
    out.write_bytes(pdf)
    print("Wrote", out)


if __name__ == "__main__":
    main()
