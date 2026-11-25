from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from backend.config.database import SessionLocal, engine
from backend.config.database import Base
from backend.models.entities import (
    AuditLog,
    Customer,
    Dress,
    DressRental,
    DressRentalItem,
    RentalHistory,
    Service,
    ServiceType,
    ServiceUsage,
    User,
)
from backend.services.rules import calc_deposit
from backend.utils.security import hash_password


DRESS_IMAGES = {
    "AC001": "https://images.unsplash.com/photo-1594552072238-b8a33785b261?w=600&auto=format&fit=crop&q=80",
    "AC002": "https://images.unsplash.com/photo-1532712938310-34cb3982ef74?w=600&auto=format&fit=crop&q=80",
    "AC003": "https://images.unsplash.com/photo-1546804784-896d0dca3805?w=600&auto=format&fit=crop&q=80",
    "AC004": "https://images.unsplash.com/photo-1519741497674-611481863552?w=600&auto=format&fit=crop&q=80",
    "AC005": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600&auto=format&fit=crop&q=80",
    "AC006": "https://images.unsplash.com/photo-1617137984095-74e4e5e3613f?w=600&auto=format&fit=crop&q=80",
    "AC007": "https://images.unsplash.com/photo-1596451190630-186aff535bf2?w=600&auto=format&fit=crop&q=80",
    "AC008": "https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=600&auto=format&fit=crop&q=80",
}


def seed_if_empty(db: Session | None = None) -> bool:
    own = False
    if db is None:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        own = True
    try:
        if db.query(User).count() > 0:
            return False
        _seed(db)
        return True
    finally:
        if own:
            db.close()


def _seed(db: Session):
    today = date.today()
    db.add_all(
        [
            User(
                username="admin",
                full_name="Hoàng Long",
                password_hash=hash_password("admin123"),
                role="admin",
            ),
            User(
                username="staff",
                full_name="Nhân viên Studio",
                password_hash=hash_password("staff123"),
                role="staff",
            ),
        ]
    )

    types = [
        ("LDV01", "Chụp Ảnh Cưới Album", "Chụp ngoại cảnh, phim trường, studio chuyên nghiệp"),
        ("LDV02", "Quay Phim Phóng Sự Cưới", "Ghi lại khoảnh khắc ngày cưới với chất lượng 4K Cinematic"),
        ("LDV03", "Trang Điểm & Làm Tóc Cô Dâu", "Make-up ngày cưới, lễ gia tiên, phong cách Hàn Quốc/Tây"),
        ("LDV04", "Thuê Trang Phục Cưới", "Váy cưới luxury, áo dài cô dâu, vest chú rể"),
        ("LDV05", "Trang Trí Gia Tiên & Tiệc Cưới", "Set up hoa tươi, background lễ cưới trọn gói"),
    ]
    for code, name, desc in types:
        db.add(ServiceType(ma_loai_dv=code, ten_loai_dv=name, mo_ta=desc, trang_thai=True))

    services = [
        ("DV001", "LDV01", "Gói Chụp Album Studio Classic", 6500000, "Bao gồm 1 album 30 trang, 2 ảnh cổng 60x90", "active"),
        ("DV002", "LDV01", "Gói Chụp Ngoại Cảnh Đà Lạt / Nha Trang", 14500000, "Trọn gói ekip 2 ngày, bao xe di chuyển", "active"),
        ("DV003", "LDV02", "Quay Phim Phóng Sự Cưới Highlight", 8000000, "Clip highlight 5-7 phút 4K + MV ca nhạc", "active"),
        ("DV004", "LDV03", "Trang Điểm Cô Dâu Ngày Cưới (2 Lần)", 3500000, "Tại nhà cô dâu, dặm phấn suốt tiệc", "active"),
        ("DV005", "LDV04", "Gói Thuê 1 Váy Luxury + 1 Vest Chú Rể", 5000000, "Thời hạn thuê 3 ngày 2 đêm", "active"),
        ("DV006", "LDV05", "Gói Trang Trí Gia Tiên Hoa Tươi Cao Cấp", 12000000, "Bàn thờ gia tiên, bàn hai họ 12 ghế, cổng hoa", "active"),
        ("DV007", "LDV01", "Gói Chụp Phim Trường Hàn Quốc", 9800000, "Makeup + 1 váy + 80 ảnh chỉnh sửa", "active"),
        ("DV008", "LDV02", "Flycam Phóng Sự Cưới", 4500000, "Dựng 1 clip flycam 2 phút", "out_of_stock"),
    ]
    for code, loai, name, price, desc, status in services:
        db.add(
            Service(
                ma_dv=code,
                ma_loai_dv=loai,
                ten_dv=name,
                don_gia=price,
                mo_ta=desc,
                hinh_anh="",
                trang_thai=status,
            )
        )

    customers = [
        ("KH001", "Nguyễn Thị Lan Anh", "0912345678", "Phường 2, TP. Đà Lạt", "lananh@example.com", "Nguyễn Thị Lan Anh", "Trần Quốc Bảo", date(2026, 12, 20), "Facebook"),
        ("KH002", "Trần Văn Hùng", "0987654321", "Phường 8, TP. Đà Lạt", "hung.tran@example.com", "Lê Thu Hà", "Trần Văn Hùng", date(2026, 1, 18), "Giới thiệu"),
        ("KH003", "Phạm Quỳnh Nga", "0905123987", "Phường 1, TP. Đà Lạt", "quynhnga@example.com", "Phạm Quỳnh Nga", "Đỗ Minh Khang", date(2026, 11, 8), "TikTok"),
        ("KH004", "Lê Hoàng Nam", "0934567890", "Phường 9, TP. Đà Lạt", "hoangnam@example.com", "Ngô Mỹ Linh", "Lê Hoàng Nam", date(2027, 2, 14), "Walk-in"),
        ("KH005", "Võ Minh Châu", "0978123456", "Phường 3, TP. Đà Lạt", "minhchau@example.com", "Võ Minh Châu", "Phan Gia Huy", date(2026, 12, 5), "Facebook"),
    ]
    for code, name, phone, addr, email, bride, groom, wedding, source in customers:
        db.add(
            Customer(
                ma_kh=code,
                ten_kh=name,
                sdt=phone,
                dia_chi=addr,
                email=email,
                ten_vo=bride,
                ten_chong=groom,
                ngay_cuoi=wedding,
                nguon_khach=source,
                ngay_tao=datetime.utcnow(),
            )
        )

    dresses = [
        ("AC001", "Váy Cưới Luxury Hoàng Gia Đính Pha Lê Swarovski", "Váy Cưới Luxury", 3500000, "DANG_THUE", "S", "Trắng ngà", "Voan, găng tay, vương miện"),
        ("AC002", "Váy Cưới Đuôi Cá Satin Phong Cách Pháp", "Váy Cưới Luxury", 2800000, "SAN_SANG", "M", "Ivory", "Găng tay dài, hoa cầm tay"),
        ("AC003", "Áo Dài Cưới Gấm Đỏ Thêu Phượng Hoàng", "Áo Dài Cưới Truyền Thống", 1200000, "DANG_THUE", "M", "Đỏ", "Khăn đóng, quạt lụa"),
        ("AC004", "Áo Dài Cặp Đôi Tơ Tằm Trắng Tinh Khôi", "Áo Dài Cưới Truyền Thống", 1800000, "SAN_SANG", "L", "Trắng", "Nón lá, hoa cài"),
        ("AC005", "Bộ Vest Chú Rể Tuxedo Đen Ý Sang Trọng", "Vest Chú Rể Cao Cấp", 1500000, "DANG_THUE", "L", "Đen", "Nơ, khăn túi, khuy cài"),
        ("AC006", "Bộ Vest Chú Rể Xanh Navy Form Slimfit", "Vest Chú Rể Cao Cấp", 1200000, "SAN_SANG", "M", "Navy", "Cà vạt, khăn túi"),
        ("AC007", "Váy Cưới Chữ A Voan Mềm Bồng Bềnh Hàn Quốc", "Váy Cưới Minimalist", 2000000, "SAN_SANG", "S", "Trắng", "Hoa voan, găng tay"),
        ("AC008", "Váy Cưới Xòe Cúp Ngực Đính Ngọc Trai", "Váy Cưới Luxury", 4000000, "DANG_THUE", "M", "Champagne", "Vương miện ngọc trai"),
        ("AC009", "Váy Cưới Minimalist Lụa Ý Cúp Ngực", "Váy Cưới Minimalist", 2200000, "HON_HOC", "S", "Ivory", "Dây lưng lụa"),
    ]
    for code, name, loai, price, status, size, color, accessory in dresses:
        db.add(
            Dress(
                ma_dress=code,
                ten_ao=name,
                loai_ao=loai,
                don_gia=price,
                hinh_anh=DRESS_IMAGES.get(code, DRESS_IMAGES["AC001"]),
                size=size,
                mau=color,
                phu_kien=accessory,
                trang_thai=status,
                ghi_chu="Hỏng khóa kéo, chờ sửa" if status == "HON_HOC" else "",
            )
        )

    usages = [
        ("KH001", "DV001", today - timedelta(days=40), 6500000, "Album studio"),
        ("KH001", "DV004", today - timedelta(days=20), 3500000, "Makeup ngày cưới"),
        ("KH002", "DV002", today - timedelta(days=25), 14500000, "Ngoại cảnh Đà Lạt"),
        ("KH002", "DV003", today - timedelta(days=25), 8000000, "Highlight 4K"),
        ("KH002", "DV005", today - timedelta(days=10), 5000000, "Gói thuê váy + vest"),
        ("KH003", "DV001", today - timedelta(days=12), 6500000, "Album classic"),
        ("KH004", "DV002", today - timedelta(days=50), 14500000, "Nha Trang"),
        ("KH004", "DV006", today - timedelta(days=8), 12000000, "Gia tiên hoa tươi"),
    ]
    for ma_kh, ma_dv, ngay, gia, note in usages:
        db.add(ServiceUsage(ma_kh=ma_kh, ma_dv=ma_dv, ngay_sd=ngay, gia_luc_sd=gia, ghi_chu=note))

    def add_rental(ma_hd, ma_kh, start, due, returned, status, dress_codes, created_by="admin"):
        items_meta = []
        total_coc = 0
        for code in dress_codes:
            dress = next(d for d in dresses if d[0] == code)
            coc = calc_deposit(dress[3])
            total_coc += coc
            items_meta.append((code, dress[3], coc))
        rental = DressRental(
            ma_hop_dong=ma_hd,
            ma_kh=ma_kh,
            ngay_thue=start,
            ngay_tra_du_kien=due,
            ngay_tra_thuc_te=returned,
            tien_coc=total_coc,
            trang_thai=status,
            created_by=created_by,
        )
        db.add(rental)
        db.flush()
        for code, gia, coc in items_meta:
            db.add(DressRentalItem(ma_hop_dong=ma_hd, ma_dress=code, don_gia=gia, tien_coc=coc, tinh_trang_ao="TOT"))
        db.add(RentalHistory(ma_hop_dong=ma_hd, trang_thai="DANG_THUE", tien_phat=0, ghi_chu="Lập hợp đồng", username=created_by))
        if status == "QUA_HAN":
            db.add(RentalHistory(ma_hop_dong=ma_hd, trang_thai="QUA_HAN", ghi_chu="Quá hạn trả", username="system"))
        if status == "DA_TRA":
            db.add(RentalHistory(ma_hop_dong=ma_hd, trang_thai="DA_TRA", ghi_chu="Đã trả", username=created_by))

    add_rental("HD001", "KH001", today - timedelta(days=5), today - timedelta(days=3), None, "QUA_HAN", ["AC001", "AC005"])
    add_rental("HD002", "KH002", today - timedelta(days=7), today - timedelta(days=4), None, "QUA_HAN", ["AC003"])
    add_rental("HD003", "KH003", today - timedelta(days=1), today + timedelta(days=2), None, "DANG_THUE", ["AC008"])
    add_rental("HD004", "KH004", today - timedelta(days=20), today - timedelta(days=17), today - timedelta(days=17), "DA_TRA", ["AC002", "AC006"])

    db.add(AuditLog(username="system", action="SEED", entity="Database", entity_id="init", detail="Khởi tạo dữ liệu mẫu Nhóm 24"))
    db.commit()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    created = seed_if_empty()
    print("Seeded" if created else "Database already has data")
