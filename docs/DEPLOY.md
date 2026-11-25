# Hướng dẫn triển khai — LUXE WEDDING STUDIO

## 1. Máy phát triển

1. Cài Node.js 18+ và Python 3.11+ (Windows: cài từ python.org, dùng lệnh `py`).
2. Clone source, cài phụ thuộc:

```bash
py -3 -m venv .venv
.venv\Scripts\pip install -r requirements.txt
npm install
```

3. `npm run dev` — Electron mở cửa sổ, backend lắng nghe `127.0.0.1:8000`.

## 2. Biến môi trường

| Biến | Ý nghĩa |
| --- | --- |
| `LUXE_DB_PATH` | Đường dẫn file SQLite |
| `LUXE_BACKUP_DIR` | Thư mục sao lưu |
| `LUXE_UPLOAD_DIR` | Ảnh tải lên |
| `LUXE_LOG_DIR` | File log `app.log` |
| `LUXE_CLOUD_SYNC_DIR` | Folder Google Drive / OneDrive để copy backup |
| `JWT_SECRET` | Khóa ký JWT (đổi khi production) |

Khi chạy bằng Electron packaged, CSDL mặc định nằm trong `app.getPath('userData')/data`.

## 3. Installer

```bash
npm run dist:win
```

Phát hành file `release/LuxeWeddingStudio-Setup-1.0.0.exe`. Người dùng cài đặt, chạy shortcut Desktop. Python phải có trong PATH.

## 4. PostgreSQL (production)

Có thể đổi URL SQLAlchemy trong `backend/config/database.py` thành `postgresql+psycopg2://user:pass@host/luxe`. Schema tương đương `database/schema.sql`.

## 5. Sao lưu / phục hồi

- Tự động: APScheduler 02:00 hàng ngày.
- Thủ công: trang **Cài đặt & sao lưu**.
- Restore: chỉ Admin.
