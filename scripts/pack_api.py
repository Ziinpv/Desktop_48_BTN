"""Build the FastAPI backend into pyinstaller-dist/luxe-api/luxe-api.exe."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "pyinstaller-dist"
WORK = ROOT / "pyinstaller-build"
ENTRY = ROOT / "backend" / "run_server.py"


def main() -> int:
    shutil.rmtree(DIST, ignore_errors=True)
    shutil.rmtree(WORK, ignore_errors=True)
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--name",
        "luxe-api",
        "--console",
        "--paths",
        str(ROOT),
        "--distpath",
        str(DIST),
        "--workpath",
        str(WORK),
        "--specpath",
        str(WORK),
        "--collect-all",
        "uvicorn",
        "--collect-all",
        "starlette",
        "--collect-all",
        "fastapi",
        "--collect-all",
        "pydantic",
        "--collect-all",
        "jose",
        "--collect-submodules",
        "backend",
        "--hidden-import",
        "bcrypt",
        "--hidden-import",
        "sqlalchemy",
        "--hidden-import",
        "sqlalchemy.dialects.sqlite",
        "--hidden-import",
        "reportlab",
        "--hidden-import",
        "openpyxl",
        "--hidden-import",
        "qrcode",
        "--hidden-import",
        "PIL",
        "--hidden-import",
        "apscheduler",
        "--hidden-import",
        "apscheduler.schedulers.background",
        "--hidden-import",
        "email.mime.text",
        "--hidden-import",
        "email.mime.multipart",
        str(ENTRY),
    ]
    print(" ".join(cmd))
    result = subprocess.run(cmd, cwd=ROOT)
    exe = DIST / "luxe-api" / "luxe-api.exe"
    if result.returncode != 0 or not exe.exists():
        print("PyInstaller failed; expected", exe)
        return result.returncode or 1
    print("API binary:", exe)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
