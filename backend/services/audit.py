from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.entities import AuditLog


def write_audit(db: Session, username: str, action: str, entity: str, entity_id: str = "", detail: str = ""):
    db.add(
        AuditLog(
            username=username or "system",
            action=action,
            entity=entity,
            entity_id=entity_id,
            detail=detail,
            created_at=datetime.utcnow(),
        )
    )
    db.commit()
