import os
import glob
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_document():
    doc = docx.Document()

    # Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(0.8)

    PRIMARY_COLOR = RGBColor(121, 82, 144)    # Purple
    DARK_COLOR = RGBColor(30, 41, 59)        # Slate Dark
    MUTED_COLOR = RGBColor(100, 116, 139)    # Gray
    
    # -------------------------------------------------------------
    # TRANG BÌA (COVER PAGE)
    # -------------------------------------------------------------
    p_univ = doc.add_paragraph()
    p_univ.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p_univ.add_run("TRƯỜNG ĐẠI HỌC ĐÀ LẠT\n")
    r1.font.name = 'Times New Roman'; r1.font.size = Pt(13); r1.font.bold = True
    r2 = p_univ.add_run("KHOA CÔNG NGHỆ THÔNG TIN\n")
    r2.font.name = 'Times New Roman'; r2.font.size = Pt(12); r2.font.bold = True; r2.font.color.rgb = PRIMARY_COLOR
    r_div = p_univ.add_run("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n\n")
    r_div.font.color.rgb = MUTED_COLOR

    p_title_sub = doc.add_paragraph()
    p_title_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_title_sub.add_run("BÁO CÁO BÀI TẬP LỚN / BÀI TẬP NHÓM\nPHÂN TÍCH THIẾT KẾ HỆ THỐNG & GIAO DIỆN\n\n")
    r_sub.font.name = 'Times New Roman'; r_sub.font.size = Pt(14); r_sub.font.bold = True; r_sub.font.color.rgb = DARK_COLOR

    p_main_title = doc.add_paragraph()
    p_main_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_main = p_main_title.add_run("ĐỀ TÀI SỐ 8:\nQUẢN LÝ STUDIO ẢNH CƯỚI\n")
    r_main.font.name = 'Times New Roman'; r_main.font.size = Pt(22); r_main.font.bold = True; r_main.font.color.rgb = PRIMARY_COLOR

    p_desc = doc.add_paragraph()
    p_desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_desc = p_desc.add_run("(Phân tích chức năng F1-F8, Ràng buộc tối đa N bộ, Tiền cọc & Thiết kế Mockup giao diện)\n\n\n\n")
    r_desc.font.name = 'Times New Roman'; r_desc.font.size = Pt(12); r_desc.font.italic = True; r_desc.font.color.rgb = MUTED_COLOR

    # Bảng thông tin sinh viên & giảng viên
    table_info = doc.add_table(rows=4, cols=2)
    table_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_info.autofit = False

    info_data = [
        ("Nhóm thực hiện:", "Nhóm 24"),
        ("Sinh viên thực hiện:", "Hoàng Long - MSSV: 2212407"),
        ("Học phần:", "Phân Tích Thiết Kế Hệ Thống & Cơ Sở Dữ Liệu"),
        ("Năm học:", "2025 - 2026")
    ]

    for row_idx, (label, val) in enumerate(info_data):
        cell_lbl = table_info.cell(row_idx, 0)
        cell_val = table_info.cell(row_idx, 1)
        cell_lbl.width = Inches(2.2)
        cell_val.width = Inches(3.8)

        p_l = cell_lbl.paragraphs[0]
        r_l = p_l.add_run(label)
        r_l.font.name = 'Times New Roman'; r_l.font.size = Pt(12); r_l.font.bold = True

        p_v = cell_val.paragraphs[0]
        r_v = p_v.add_run(val)
        r_v.font.name = 'Times New Roman'; r_v.font.size = Pt(12)
        if "Hoàng Long" in val:
            r_v.font.bold = True
            r_v.font.color.rgb = PRIMARY_COLOR

    p_footer = doc.add_paragraph()
    p_footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_ft = p_footer.add_run("\n\n\n\nĐÀ LẠT, NĂM 2026")
    r_ft.font.name = 'Times New Roman'; r_ft.font.size = Pt(11); r_ft.font.bold = True

    doc.add_page_break()

    # -------------------------------------------------------------
    # MỤC LỤC
    # -------------------------------------------------------------
    p_toc = doc.add_paragraph()
    r_toc = p_toc.add_run("MỤC LỤC NỘI DUNG BÁO CÁO")
    r_toc.font.name = 'Times New Roman'; r_toc.font.size = Pt(16); r_toc.font.bold = True; r_toc.font.color.rgb = PRIMARY_COLOR

    toc_items = [
        "CHƯƠNG 1: TỔNG QUAN BÀI TOÁN & PHÂN TÍCH YÊU CẦU NGHIỆP VỤ",
        "  1.1 Đặt vấn đề và Mục tiêu đề tài",
        "  1.2 Mô tả nghiệp vụ Studio Ảnh Cưới theo đề bài",
        "  1.3 Các quy định và ràng buộc nghiệp vụ then chốt",
        "CHƯƠNG 2: PHÂN TÍCH CHỨC NĂNG HỆ THỐNG (FUNCTIONAL REQUIREMENTS)",
        "  2.1 Ma trận đối chiếu các yêu cầu chức năng (F1 đến F8)",
        "  2.2 Mô hình Use Case và Danh sách Tác nhân (Actors)",
        "  2.3 Đặc tả chi tiết các Use Case chính",
        "CHƯƠNG 3: THIẾT KẾ CƠ SỞ DỮ LIỆU QUAN HỆ (DATABASE DESIGN)",
        "  3.1 Sơ đồ quan hệ thực thể (ERD Structure)",
        "  3.2 Thiết kế cấu trúc các bảng dữ liệu (Data Dictionary)",
        "  3.3 Định nghĩa các Ràng buộc toàn vẹn & Trigger nghiệp vụ",
        "CHƯƠNG 4: THIẾT KẾ GIAO DIỆN NGƯỜI DÙNG & HÌNH ẢNH MINH HỌA (UI/UX DESIGN)",
        "  4.1 Phong cách thiết kế, Bảng màu và Luồng điều hướng",
        "  4.2 Giao diện Dashboard Tổng quan & Cảnh báo",
        "  4.3 Giao diện Quản lý Loại Dịch Vụ & Dịch Vụ Cưới (F1, F2, F4)",
        "  4.4 Giao diện Quản lý Kho Áo Cưới & Trang Phục (F3)",
        "  4.5 Giao diện Lập Phiếu Thuê & Ràng buộc Tối đa N bộ, Đặt cọc (F3)",
        "  4.6 Giao diện Tra Cứu Áo Cưới & Lịch Sử Thuê Mượn (F7)",
        "  4.7 Giao diện Tra Cứu Dịch Vụ Theo Khách Hàng (F8)",
        "  4.8 Giao diện Báo Cáo Thuê Chưa Trả & Thuê Quá Hạn (F5, F6)",
        "CHƯƠNG 5: ĐÁNH GIÁ KẾT QUẢ & HƯỚNG DẪN TRẢI NGHIỆM PHẦN MỀM"
    ]

    for item in toc_items:
        p_item = doc.add_paragraph()
        p_item.paragraph_format.space_after = Pt(4)
        r = p_item.add_run(item)
        r.font.name = 'Times New Roman'; r.font.size = Pt(11)
        if item.startswith("CHƯƠNG"):
            r.font.bold = True; r.font.color.rgb = DARK_COLOR

    doc.add_page_break()

    def add_heading_1(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(title)
        r.font.name = 'Times New Roman'; r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = PRIMARY_COLOR

    def add_heading_2(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(title)
        r.font.name = 'Times New Roman'; r.font.size = Pt(12.5); r.font.bold = True; r.font.color.rgb = DARK_COLOR

    def add_body_p(text, bold_prefix=""):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.font.name = 'Times New Roman'; r_b.font.size = Pt(11); r_b.font.bold = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'; r.font.size = Pt(11)
        return p

    def add_image_safe(img_pattern, caption):
        # Find image matching pattern
        brain_dir = r"C:\Users\drago\.gemini\antigravity-ide\brain\2669b1a8-4851-4fda-8740-6aa2c8484d24"
        files = glob.glob(os.path.join(brain_dir, img_pattern))
        if files and os.path.exists(files[0]):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(2)
            doc.add_picture(files[0], width=Inches(6.0))
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(10)
            r_c = p_cap.add_run(caption)
            r_c.font.name = 'Times New Roman'; r_c.font.size = Pt(10); r_c.font.italic = True; r_c.font.color.rgb = MUTED_COLOR

    # CHƯƠNG 1
    add_heading_1("CHƯƠNG 1: TỔNG QUAN BÀI TOÁN & PHÂN TÍCH YÊU CẦU NGHIỆP VỤ")
    add_heading_2("1.1 Đặt vấn đề và Mục tiêu đề tài")
    add_body_p("Trong hoạt động của một Studio ảnh cưới hiện đại, sự đa dạng dịch vụ (chụp ngoại cảnh, phóng sự cưới, trang điểm cô dâu, trang trí tiệc cưới, cho thuê váy cưới/vest chú rể) đòi hỏi một hệ thống quản lý chuẩn mực.")
    add_body_p("Mục tiêu của đề tài Quản Lý Studio Ảnh Cưới (Đề tài 8 - Nhóm 24 - MSSV: 2212407 Hoàng Long) là chuẩn hóa danh mục dịch vụ, quy định bảng giá minh bạch, kiểm soát kho áo cưới chính xác, tự động hóa quy trình lập phiếu thuê mượn, kiểm tra ràng buộc số lượng tối đa N bộ và tiền cọc quy định, đồng thời hỗ trợ tra cứu nhanh và phát hiện khách hàng trễ hạn.")

    add_heading_2("1.2 Mô tả nghiệp vụ Studio Ảnh Cưới theo đề bài")
    add_body_p("Mỗi studio cung cấp nhiều loại dịch vụ (chụp ảnh, quay phim, make-up, thuê đồ...).", "• Loại dịch vụ: ")
    add_body_p("Mỗi dịch vụ cụ thể sẽ thuộc duy nhất về một loại dịch vụ nhất định.", "• Dịch vụ cưới: ")
    add_body_p("Giá dịch vụ được quy định chi tiết và minh bạch theo từng dịch vụ.", "• Giá dịch vụ: ")
    add_body_p("Khách hàng được thuê tối đa N bộ trang phục (trong hệ thống áp dụng N = 3) và bắt buộc phải đặt cọc số tiền theo quy định tương ứng của từng bộ trang phục.", "• Nghiệp vụ thuê áo cưới: ")

    add_heading_2("1.3 Các quy định và ràng buộc then chốt")
    add_body_p("1. Ràng buộc số lượng thuê mượn: Tổng số bộ trang phục trên 1 phiếu thuê không vượt quá N bộ. Hệ thống sẽ tự động chặn và nhắc nhở nếu người dùng chọn bộ thứ N+1.")
    add_body_p("2. Ràng buộc tiền cọc: Mỗi bộ áo cưới có mức cọc quy định (Deposit) riêng. Tiền đặt cọc thực tế studio nhận phải >= Tổng tiền cọc quy định của các bộ áo được thuê.")
    add_body_p("3. Ràng buộc ngày hẹn trả & quá hạn: Ngày hẹn trả >= Ngày thuê. Nếu Ngày hiện tại > Ngày hẹn trả và trạng thái chưa hoàn trả, phiếu thuê sẽ chuyển sang QUÁ HẠN và đưa vào danh sách cảnh báo thu hồi kèm tính phí phạt trễ hạn.")

    # CHƯƠNG 2
    add_heading_1("CHƯƠNG 2: PHÂN TÍCH CHỨC NĂNG HỆ THỐNG (FUNCTIONAL REQUIREMENTS)")
    add_heading_2("2.1 Ma trận đối chiếu 8 Yêu cầu Chức năng Chính (F1 - F8)")
    
    table_func = doc.add_table(rows=9, cols=3)
    table_func.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_func.autofit = False

    headers = ["Mã Yêu Cầu", "Mô Tả Chức Năng Đề Bài", "Giải Pháp & Đặc Tả Thiết Kế Hệ Thống"]
    widths = [Inches(1.2), Inches(2.6), Inches(2.8)]

    for col_idx, text in enumerate(headers):
        cell = table_func.cell(0, col_idx)
        cell.width = widths[col_idx]
        set_cell_background(cell, "795290")
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.font.name = 'Times New Roman'; r.font.size = Pt(10.5); r.font.bold = True; r.font.color.rgb = RGBColor(255, 255, 255)

    func_data = [
        ("F1", "Thêm, cập nhật, xóa thông tin loại dịch vụ", "Quản lý bảng LOAI_DICH_VU. Cho phép thêm mới, sửa tên/mô tả và kiểm tra khóa ngoại trước khi xóa."),
        ("F2", "Thêm, cập nhật, xóa thông tin dịch vụ", "Quản lý bảng DICH_VU. Gắn kết mỗi dịch vụ với 1 loại dịch vụ và quy định đơn giá niêm yết."),
        ("F3", "Thêm, cập nhật, xóa thông tin thuê mượn áo cưới", "Quản lý kho trang phục và lập phiếu thuê mượn. Kiểm tra ràng buộc tối đa N bộ và tiền đặt cọc quy định."),
        ("F4", "Liệt kê danh mục dịch vụ theo từng loại", "Bộ lọc phân loại danh mục dịch vụ cưới, hiển thị giá niêm yết và tỷ trọng cơ cấu các gói dịch vụ."),
        ("F5", "Xem danh sách khách hàng thuê chưa trả", "Thống kê tất cả các phiếu thuê có trạng thái 'ĐANG_THUE' hoặc 'QUA_HAN', hiển thị chi tiết khách hàng và tiền cọc đang giữ."),
        ("F6", "Xem danh sách khách hàng thuê quá hạn", "Lọc các phiếu thuê có Ngày hẹn trả < Ngày hiện tại. Tính số ngày trễ hạn, tính phí phạt và nút gửi cảnh báo SMS/Zalo."),
        ("F7", "Tìm thông tin bộ áo quần: tựa đề, giá, thông tin thuê - mượn", "Tra cứu theo mã/tên bộ áo cưới, xem ảnh mẫu, giá thuê, tiền cọc và toàn bộ lịch sử các khách hàng từng mượn."),
        ("F8", "Tìm thông tin về dịch vụ cung cấp theo khách hàng", "Tra cứu theo tên/SĐT khách hàng, hiển thị toàn bộ các gói dịch vụ cưới đã dùng và các phiếu thuê trang phục.")
    ]

    for row_idx, (f_id, f_desc, f_sol) in enumerate(func_data, start=1):
        for c_idx, val in enumerate([f_id, f_desc, f_sol]):
            cell = table_func.cell(row_idx, c_idx)
            cell.width = widths[c_idx]
            set_cell_margins(cell, 80, 80, 100, 100)
            if row_idx % 2 == 0:
                set_cell_background(cell, "F8FAFC")
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = 'Times New Roman'; r.font.size = Pt(10)
            if c_idx == 0:
                r.font.bold = True; r.font.color.rgb = PRIMARY_COLOR

    # CHƯƠNG 3
    add_heading_1("CHƯƠNG 3: THIẾT KẾ CƠ SỞ DỮ LIỆU QUAN HỆ (DATABASE DESIGN)")
    add_heading_2("3.1 Cấu trúc các bảng dữ liệu (Data Dictionary)")
    add_body_p("Hệ thống xây dựng trên mô hình quan hệ chuẩn hóa 3NF bao gồm các bảng:")
    add_body_p("1. LOAI_DICH_VU (MaLoaiDV, TenLoaiDV, MoTa)")
    add_body_p("2. DICH_VU (MaDV, MaLoaiDV [FK], TenDV, DonGia, GhiChu)")
    add_body_p("3. KHACH_HANG (MaKH, TenKH, SoDienThoai, DiaChi, Email)")
    add_body_p("4. TRANG_PHUC_AO_CUOI (MaTrangPhuc, TuaDe, LoaiTrangPhuc, GiaThue, TienCocQuyDinh, TinhTrangKho, HinhAnh)")
    add_body_p("5. PHIEU_THUE_AO_CUOI (MaPhieuThue, MaKH [FK], NgayThue, NgayHenTra, NgayTraThucTe, TienDatCoc, TrangThai)")
    add_body_p("6. CHI_TIET_THUE_AO_CUOI (MaPhieuThue [FK], MaTrangPhuc [FK], DonGiaThue, TienCoc)")

    # CHƯƠNG 4
    add_heading_1("CHƯƠNG 4: THIẾT KẾ GIAO DIỆN NGƯỜI DÙNG & HÌNH ẢNH MINH HỌA")
    add_heading_2("4.1 Phong cách thiết kế & Luồng điều hướng")
    add_body_p("Ứng dụng được thiết kế theo phong cách Studio Cưới Hoàng Gia (Luxe Wedding Theme) với tông màu Tím Hoàng Gia (#795290) phối Vàng Ánh Kim (#D4A373). Thanh Menu Sidebar cố định bên trái giúp chuyển đổi linh hoạt giữa các chức năng.")

    add_heading_2("4.2 Hình ảnh và Mô tả chi tiết từng Màn hình")
    
    add_body_p("Màn hình Dashboard cung cấp cái nhìn trực quan với 4 thẻ KPI, bảng cơ cấu phân bổ dịch vụ cưới theo loại (F4) và bảng danh sách cảnh báo khẩn cấp các phiếu thuê quá hạn (F6).", "• Màn hình 1: Dashboard Tổng Quan & Cảnh Báo:")
    add_image_safe("dashboard_overview_*.png", "Hình 1: Giao diện Dashboard tổng quan và bảng cảnh báo quá hạn F6")

    add_body_p("Màn hình quản lý phân loại dịch vụ cho phép thêm mới, chỉnh sửa thông tin mô tả và kiểm soát số lượng dịch vụ thuộc từng loại.", "• Màn hình 2: Quản Lý Loại Dịch Vụ (F1):")
    add_image_safe("service_types_tab_*.png", "Hình 2: Giao diện Quản lý Loại Dịch Vụ F1")

    add_body_p("Màn hình quản lý kho hiển thị trực quan các bộ váy cưới, áo dài, vest chú rể kèm ảnh mẫu, phân loại, đơn giá thuê và mức cọc quy định.", "• Màn hình 3: Quản Lý Kho Áo Cưới & Trang Phục (F3):")
    add_image_safe("costumes_tab_*.png", "Hình 3: Giao diện Kho Áo Cưới & Trang Phục F3")

    add_body_p("Màn hình quản lý phiếu thuê và Modal lập phiếu: Cho phép chọn khách hàng, ngày thuê, ngày hẹn trả và tích chọn tối đa N = 3 bộ trang phục sẵn sàng. Hệ thống tự động tính tổng tiền thuê và mức cọc quy định tối thiểu.", "• Màn hình 4: Quản Lý & Lập Phiếu Thuê Áo Cưới (F3 - Ràng buộc Max N & Đặt cọc):")
    add_image_safe("rentals_tab_*.png", "Hình 4: Giao diện Quản lý Phiếu Thuê Mượn Áo Cưới")

    add_body_p("Màn hình tra cứu nhanh theo mã hoặc tên bộ áo cưới. Hiển thị thông tin chi tiết, đơn giá thuê, tiền cọc và toàn bộ lịch sử các khách hàng đã từng thuê mượn bộ trang phục này.", "• Màn hình 5: Tra Cứu Thông Tin Áo Cưới & Lịch Sử Thuê Mượn (F7):")
    add_image_safe("search_costume_tab_*.png", "Hình 5: Giao diện Tra cứu Thông tin Áo Cưới F7")

    add_body_p("Màn hình tra cứu theo tên/SĐT khách hàng: Hiển thị thông tin khách hàng, danh sách các gói dịch vụ cưới khách đã đăng ký và toàn bộ các phiếu thuê áo cưới tương ứng.", "• Màn hình 6: Tra Cứu Dịch Vụ Theo Khách Hàng (F8):")
    add_image_safe("search_customer_tab_*.png", "Hình 6: Giao diện Tra cứu Dịch Vụ Theo Khách Hàng F8")

    add_body_p("Màn hình cảnh báo nổi bật với viền đỏ, hiển thị chính xác số ngày trễ hạn, tiền cọc đang giữ, tính toán phí phạt phát sinh và nút gửi tin nhắn SMS/Zalo cảnh báo thu hồi đồ.", "• Màn hình 7: Báo Cáo Khách Hàng Thuê Quá Hạn (F6):")
    add_image_safe("report_overdue_tab_*.png", "Hình 7: Giao diện Báo cáo & Cảnh báo Thuê Quá Hạn F6")

    # CHƯƠNG 5
    add_heading_1("CHƯƠNG 5: ĐÁNH GIÁ KẾT QUẢ & HƯỚNG DẪN TRẢI NGHIỆM")
    add_heading_2("5.1 Tổng kết mức độ đáp ứng đề tài")
    add_body_p("✔ Hoàn thành phân tích toàn diện 8 yêu cầu chức năng F1 đến F8 theo đúng nội dung Đề tài số 8.")
    add_body_p("✔ Hiện thực hóa chính xác các ràng buộc: Mỗi dịch vụ thuộc 1 loại dịch vụ, bảng giá rõ ràng, khách hàng thuê tối đa N bộ và bắt buộc đặt cọc theo quy định.")
    add_body_p("✔ Xây dựng ứng dụng web tương tác hoàn chỉnh (HTML/CSS/JS) với dữ liệu mẫu phong phú và giao diện hiện đại.")
    
    add_heading_2("5.2 Hướng dẫn mở và trải nghiệm ứng dụng")
    add_body_p("1. Mở thư mục bài làm: e:\\Long\\Desktop48\\BTN_N24")
    add_body_p("2. Nhấp đúp mở tệp index.html trên trình duyệt để trải nghiệm trực tiếp giao diện tương tác.")

    doc_path = "e:/Long/Desktop48/BTN_N24/BaoCao_BaiTapNhom_QuanLyStudioAnhCuoi_Nhom24.docx"
    doc.save(doc_path)
    print(f"Document with embedded screenshots saved at: {doc_path}")

if __name__ == "__main__":
    create_document()
