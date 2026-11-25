-- LUXE WEDDING STUDIO - Schema SQLite
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  full_name TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'staff',
  is_active INTEGER DEFAULT 1,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS service_types (
  ma_loai_dv TEXT PRIMARY KEY,
  ten_loai_dv TEXT NOT NULL,
  mo_ta TEXT NOT NULL,
  trang_thai INTEGER DEFAULT 1,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS services (
  ma_dv TEXT PRIMARY KEY,
  ten_dv TEXT NOT NULL,
  ma_loai_dv TEXT NOT NULL REFERENCES service_types(ma_loai_dv),
  don_gia REAL NOT NULL CHECK (don_gia >= 0),
  mo_ta TEXT,
  hinh_anh TEXT,
  trang_thai TEXT DEFAULT 'active',
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS customers (
  ma_kh TEXT PRIMARY KEY,
  ten_kh TEXT NOT NULL,
  sdt TEXT,
  dia_chi TEXT,
  email TEXT,
  ngay_tao TEXT
);

CREATE TABLE IF NOT EXISTS dresses (
  ma_dress TEXT PRIMARY KEY,
  ten_ao TEXT NOT NULL,
  loai_ao TEXT NOT NULL,
  don_gia REAL NOT NULL CHECK (don_gia >= 0),
  hinh_anh TEXT,
  trang_thai TEXT DEFAULT 'SAN_SANG',
  ghi_chu TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS dress_rentals (
  ma_hop_dong TEXT PRIMARY KEY,
  ma_kh TEXT NOT NULL REFERENCES customers(ma_kh),
  ngay_thue TEXT NOT NULL,
  ngay_tra_du_kien TEXT NOT NULL,
  ngay_tra_thuc_te TEXT,
  tien_coc REAL DEFAULT 0,
  trang_thai TEXT DEFAULT 'DANG_THUE',
  ghi_chu TEXT,
  created_at TEXT,
  created_by TEXT
);

CREATE TABLE IF NOT EXISTS dress_rental_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ma_hop_dong TEXT NOT NULL REFERENCES dress_rentals(ma_hop_dong) ON DELETE CASCADE,
  ma_dress TEXT NOT NULL REFERENCES dresses(ma_dress),
  don_gia REAL NOT NULL,
  tien_coc REAL NOT NULL,
  tinh_trang_ao TEXT DEFAULT 'TOT'
);

CREATE TABLE IF NOT EXISTS rental_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ma_hop_dong TEXT REFERENCES dress_rentals(ma_hop_dong),
  trang_thai TEXT,
  tien_phat REAL DEFAULT 0,
  ngay_cap_nhat TEXT,
  ghi_chu TEXT,
  username TEXT
);

CREATE TABLE IF NOT EXISTS service_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ma_kh TEXT REFERENCES customers(ma_kh),
  ma_dv TEXT REFERENCES services(ma_dv),
  ngay_sd TEXT,
  gia_luc_sd REAL,
  ghi_chu TEXT
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT,
  action TEXT NOT NULL,
  entity TEXT NOT NULL,
  entity_id TEXT,
  detail TEXT,
  created_at TEXT
);

CREATE INDEX IF NOT EXISTS ix_customers_sdt ON customers(sdt);
CREATE INDEX IF NOT EXISTS ix_services_loai ON services(ma_loai_dv);
CREATE INDEX IF NOT EXISTS ix_rentals_kh ON dress_rentals(ma_kh);
CREATE INDEX IF NOT EXISTS ix_rentals_status ON dress_rentals(trang_thai);
CREATE INDEX IF NOT EXISTS ix_items_dress ON dress_rental_items(ma_dress);
CREATE INDEX IF NOT EXISTS ix_usage_kh ON service_usage(ma_kh);
CREATE INDEX IF NOT EXISTS ix_audit_created ON audit_logs(created_at);
