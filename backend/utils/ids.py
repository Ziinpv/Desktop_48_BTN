from sqlalchemy.orm import Session

from backend.services.rules import next_code


def generate_code(db: Session, model, pk_field: str, prefix: str, width: int = 3) -> str:
    rows = db.query(getattr(model, pk_field)).all()
    existing = [row[0] for row in rows]
    return next_code(prefix, existing, width)
