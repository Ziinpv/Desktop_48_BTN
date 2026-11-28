"""Entry point for the packaged FastAPI server (PyInstaller)."""
import sys
import traceback
from multiprocessing import freeze_support
from pathlib import Path

import uvicorn

from backend.app import app


def main():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


if __name__ == "__main__":
    freeze_support()
    try:
        main()
    except Exception:
        crash = Path.cwd() / "luxe-api-crash.txt"
        crash.write_text(traceback.format_exc(), encoding="utf-8")
        print(traceback.format_exc(), file=sys.stderr)
        raise

