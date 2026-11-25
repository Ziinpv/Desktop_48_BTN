from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler

from backend.config.settings import settings

_scheduler: BackgroundScheduler | None = None


def backup_database(tag: str = "auto") -> dict:
    src = settings.db_path
    if not src.exists():
        return {"ok": False, "message": "Chưa có file CSDL để sao lưu"}
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = settings.backup_dir / f"luxe_studio_{tag}_{stamp}.db"
    shutil.copy2(src, dest)
    cloud = settings.cloud_sync_dir
    cloud_path = None
    if cloud:
        cloud.mkdir(parents=True, exist_ok=True)
        cloud_path = cloud / dest.name
        shutil.copy2(dest, cloud_path)
    return {
        "ok": True,
        "file": str(dest),
        "cloud": str(cloud_path) if cloud_path else None,
        "createdAt": datetime.now().isoformat(),
    }


def list_backups() -> list[dict]:
    files = sorted(settings.backup_dir.glob("*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    return [
        {
            "name": f.name,
            "path": str(f),
            "size": f.stat().st_size,
            "createdAt": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
        }
        for f in files[:30]
    ]


def restore_backup(filename: str) -> dict:
    src = settings.backup_dir / Path(filename).name
    if not src.exists():
        return {"ok": False, "message": "Không tìm thấy bản sao lưu"}
    shutil.copy2(src, settings.db_path)
    return {"ok": True, "file": str(src)}


def start_backup_scheduler():
    global _scheduler
    if _scheduler:
        return
    _scheduler = BackgroundScheduler()
    _scheduler.add_job(backup_database, "cron", hour=2, minute=0, id="daily-backup", replace_existing=True)
    _scheduler.start()
