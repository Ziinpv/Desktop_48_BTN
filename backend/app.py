from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.config.database import Base, engine  # noqa: E402
from backend.config.settings import settings  # noqa: E402
from backend.routes import (  # noqa: E402
    auth,
    customers,
    dresses,
    export,
    lookup,
    payments,
    rentals,
    reports,
    service_types,
    services,
    system,
)
from backend.config.migrate import ensure_schema  # noqa: E402
from backend.seed import seed_if_empty  # noqa: E402
from backend.services.backup import start_backup_scheduler  # noqa: E402
from backend.services.payment_service import backfill_deposits  # noqa: E402
from backend.services.rental_service import refresh_overdue  # noqa: E402
from backend.config.database import SessionLocal  # noqa: E402


def _setup_logging():
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(settings.log_dir / "app.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[handler, logging.StreamHandler()],
    )


_setup_logging()
logger = logging.getLogger("luxe")

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(service_types.router)
app.include_router(services.router)
app.include_router(customers.router)
app.include_router(dresses.router)
app.include_router(rentals.router)
app.include_router(reports.router)
app.include_router(lookup.router)
app.include_router(export.router)
app.include_router(payments.router)
app.include_router(system.router)

ensure_schema()
seed_if_empty()


@app.api_route("/api/health", methods=["GET", "HEAD"])
def health():
    return {"ok": True, "app": settings.app_name}


@app.exception_handler(StarletteHTTPException)
async def http_exc(_request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def valid_exc(_request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": "Dữ liệu không hợp lệ", "errors": exc.errors()})


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    logger.exception("Unhandled error on %s: %s", request.url.path, exc)
    return JSONResponse(status_code=500, content={"detail": "Lỗi hệ thống. Chi tiết đã ghi vào nhật ký."})


@app.on_event("startup")
def on_startup():
    ensure_schema()
    seeded = seed_if_empty()
    db = SessionLocal()
    try:
        refresh_overdue(db)
        backfill_deposits(db)
    finally:
        db.close()
    start_backup_scheduler()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    logger.info("LUXE WEDDING STUDIO started. db=%s seeded=%s", settings.db_path, seeded)


if settings.upload_dir.exists():
    app.mount("/uploads", StaticFiles(directory=str(settings.upload_dir)), name="uploads")
