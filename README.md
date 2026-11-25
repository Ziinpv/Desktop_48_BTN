# LUXE WEDDING STUDIO

Hệ thống quản lý studio ảnh cưới — ứng dụng desktop native (Electron + React 18 + FastAPI + SQLite).

- **Nhóm:** 24
- **Sinh viên:** Hoàng Long — MSSV 2212407
- **Khoa:** Khoa Khoa học và Kỹ thuật Máy tính — ĐH Bách Khoa TP.HCM
- **Đề tài số 8:** Quản lý Studio Ảnh Cưới (F1 → F8)

Web demo HTML cũ được giữ tại `web-demo/` (mở `web-demo/index.html` trên trình duyệt). Ứng dụng desktop thay thế hoàn toàn phần mô phỏng in-browser.

---

## Công nghệ

| Tầng | Stack |
| --- | --- |
| Desktop shell | Electron 28, IPC qua `preload.cjs` |
| Frontend | React 18, Vite, Redux Toolkit, Ant Design 5, i18next, Recharts |
| Backend | Python 3.11+ FastAPI, SQLAlchemy, JWT + bcrypt |
| CSDL | SQLite (dev) — có thể trỏ PostgreSQL bằng `DATABASE_URL` khi triển khai |
| Build | electron-builder, NSIS (Windows), DMG (macOS), AppImage (Linux) |

Kiến trúc: Main Process (Electron) + Renderer (React) + REST API (FastAPI). Lớp CSDL tách khỏi nghiệp vụ (`models` / `services` / `routes`).

---

## Chạy môi trường phát triển

Yêu cầu: Node.js 18+, Python 3.11+ (`py` trên Windows).

```bash
# 1. Python
py -3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. Node
npm install

# 3. Chạy đồng thời Vite + FastAPI + Electron
npm run dev
```

Tài khoản mặc định:

- `admin` / `admin123` (Quản trị)
- `staff` / `staff123` (Nhân viên)

CSDL SQLite được tạo và seed tự động tại `database/luxe_studio.db`.

Chỉ chạy backend (để mở UI trên trình duyệt `http://127.0.0.1:5173`):

```bash
npm run dev:backend
npm run dev:vite
```

Kiểm thử nghiệp vụ:

```bash
npm run test:backend
```

---

## Tám phân hệ

1. **F1** Loại dịch vụ — CRUD, không trùng mã, mô tả bắt buộc, lọc trạng thái.
2. **F2** Dịch vụ — CRUD, đơn giá ≥ 0, tự sinh mã DV, sort/filter loại-giá-trạng thái.
3. **F3** Thuê áo cưới — tối đa 3 bộ/khách cùng lúc, cọc = 50% đơn giá, không trùng ngày cùng bộ áo, cảnh báo hỏng hóc / quá hạn.
4. **F4** Danh mục dịch vụ theo loại — ảnh, giá, lọc còn/hết hàng.
5. **F5** Khách chưa trả — sort, highlight sắp hết hạn 3 ngày, xuất CSV/Excel/PDF.
6. **F6** Quá hạn — phí = đơn giá × 10% × số ngày trễ, thanh toán phí, xác nhận trả.
7. **F7** Tra cứu áo — chi tiết, timeline thuê, in QR tracking.
8. **F8** Tra cứu theo khách — dịch vụ + thuê + tổng chi phí, xuất hóa đơn / hóa đơn đỏ.

---

## Build installer

```bash
npm run dist:win      # NSIS .exe
npm run dist:mac      # DMG
npm run dist:linux    # AppImage
```

Artifact nằm trong `release/`. Máy đích cần Python 3 để chạy API nội bộ (cùng máy).

---

## Cấu trúc thư mục

Xem `docs/DEPLOY.md`. Hướng dẫn người dùng: `docs/HUONG_DAN_SU_DUNG.md`.

Sao lưu tự động lúc 02:00 mỗi ngày. Đặt `LUXE_CLOUD_SYNC_DIR` tới thư mục Google Drive / OneDrive để copy backup lên cloud.
