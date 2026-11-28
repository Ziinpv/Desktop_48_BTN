from sqlalchemy import inspect, text
from backend.config.database import Base, engine

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
