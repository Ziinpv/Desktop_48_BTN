from __future__ import annotations

import os
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


class Settings:
    app_name = "LUXE WEDDING STUDIO"
    jwt_secret = os.getenv("JWT_SECRET", "luxe-wedding-studio-nhom24-jwt-secret")
    jwt_algorithm = "HS256"
    jwt_expire_hours = int(os.getenv("JWT_EXPIRE_HOURS", "12"))
    max_active_dresses = 3
    deposit_rate = 0.50
    late_fee_rate = 0.10
    due_soon_days = 3
    host = "127.0.0.1"
    port = 8000

    @property
    def db_path(self) -> Path:
        env_path = os.getenv("LUXE_DB_PATH")
        if env_path:
            path = Path(env_path)
        else:
            data_dir = Path(os.getenv("LUXE_DATA_DIR", _project_root() / "database"))
            data_dir.mkdir(parents=True, exist_ok=True)
            path = data_dir / "luxe_studio.db"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def backup_dir(self) -> Path:
        path = Path(os.getenv("LUXE_BACKUP_DIR", _project_root() / "database" / "backups"))
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def upload_dir(self) -> Path:
        path = Path(os.getenv("LUXE_UPLOAD_DIR", _project_root() / "assets" / "uploads"))
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def log_dir(self) -> Path:
        path = Path(os.getenv("LUXE_LOG_DIR", _project_root() / "logs"))
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def cloud_sync_dir(self) -> Path | None:
        raw = os.getenv("LUXE_CLOUD_SYNC_DIR", "").strip()
        return Path(raw) if raw else None


settings = Settings()
