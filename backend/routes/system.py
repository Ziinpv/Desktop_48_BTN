import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from backend.config.database import get_db
from backend.config.settings import settings
from backend.models.entities import AuditLog, DressRental, DressRentalItem, User
from backend.services.auth_service import get_current_user, require_admin
from backend.services.backup import backup_database, list_backups, restore_backup
from backend.services.reminder_service import remind_contracts, sms_configured, smtp_configured
from backend.services.rental_service import refresh_overdue, serialize_rental

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/health")
def health():
    return {"ok": True, "app": settings.app_name}


@router.post("/backup")
def do_backup(_: User = Depends(get_current_user)):
    return backup_database(tag="manual")


@router.get("/backups")
def backups(_: User = Depends(get_current_user)):
    return list_backups()


@router.post("/restore")
def restore(payload: dict, _: User = Depends(require_admin)):
    name = payload.get("name")
    if not name:
        raise HTTPException(400, "Thiếu tên bản sao lưu")
    result = restore_backup(name)
    if not result.get("ok"):
        raise HTTPException(400, result.get("message") or "Restore thất bại")
    return result


@router.get("/audit")
def audit(limit: int = 200, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "username": r.username,
            "action": r.action,
            "entity": r.entity,
            "entityId": r.entity_id,
            "detail": r.detail,
            "createdAt": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.post("/refresh-overdue")
def do_refresh(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"updated": refresh_overdue(db)}


@router.get("/settings")
def get_settings(_: User = Depends(get_current_user)):
    return {
        "maxActiveDresses": settings.max_active_dresses,
        "depositRate": settings.deposit_rate,
        "lateFeeRate": settings.late_fee_rate,
        "dueSoonDays": settings.due_soon_days,
        "dbPath": str(settings.db_path),
        "backupDir": str(settings.backup_dir),
        "cloudSyncDir": str(settings.cloud_sync_dir) if settings.cloud_sync_dir else "",
        "smtpConfigured": smtp_configured(),
        "smsConfigured": sms_configured(),
    }


@router.post("/remind")
def remind(payload: dict, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    channels = [c for c in (payload.get("channels") or []) if c in ("email", "sms")]
    if not channels:
        raise HTTPException(400, "Chọn kênh email hoặc SMS")
    refresh_overdue(db)
    query = db.query(DressRental).options(
        joinedload(DressRental.items).joinedload(DressRentalItem.dress),
        joinedload(DressRental.customer),
        joinedload(DressRental.history),
        joinedload(DressRental.payments),
    )
    codes = payload.get("contracts") or []
    if codes:
        rows = query.filter(DressRental.ma_hop_dong.in_(codes)).all()
    else:
        rows = query.filter(DressRental.trang_thai.in_(("DANG_THUE", "QUA_HAN"))).all()
    data = [serialize_rental(r) for r in rows]
    if not codes:
        data = [r for r in data if r.get("sapHetHan") or r.get("trangThai") == "QUA_HAN"]
    return remind_contracts(data, channels)
