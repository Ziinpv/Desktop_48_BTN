from sqlalchemy import inspect, text
from backend.config.database import Base, SessionLocal, engine

EXTRA_COLUMNS = {
    "customers": [
        ("ten_vo", "TEXT"),
        ("ten_chong", "TEXT"),
        ("ngay_cuoi", "DATE"),
        ("nguon_khach", "TEXT"),
    ],
    "dresses": [
        ("size", "TEXT"),
        ("mau", "TEXT"),
        ("phu_kien", "TEXT"),
    ],
}


def ensure_demo_roles():
    from backend.models.entities import User
    from backend.utils.security import hash_password

    extras = [
        ("cashier", "Thu ngân Studio", "cashier123", "cashier"),
        ("kho", "Nhân viên kho áo", "kho123", "warehouse"),
    ]
    db = SessionLocal()
    try:
        for username, full_name, password, role in extras:
            row = db.query(User).filter(User.username == username).first()
            if row:
                continue
            db.add(User(username=username, full_name=full_name, password_hash=hash_password(password), role=role))
        db.commit()
    finally:
        db.close()


def ensure_schema():
    Base.metadata.create_all(bind=engine)
    insp = inspect(engine)
    tables = set(insp.get_table_names())
    with engine.begin() as conn:
        for table, cols in EXTRA_COLUMNS.items():
            if table not in tables:
                continue
            existing = {c["name"] for c in inspect(engine).get_columns(table)}
            for name, typ in cols:
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {typ}"))
    if "users" in tables:
        ensure_demo_roles()
