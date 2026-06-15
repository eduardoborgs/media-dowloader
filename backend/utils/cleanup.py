import os
import time
from pathlib import Path

TEMP_DIR = Path("/tmp/media_downloader")
MAX_AGE_SECONDS = 3600


def ensure_temp_dir() -> Path:
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    return TEMP_DIR


def cleanup_old_files() -> None:
    if not TEMP_DIR.exists():
        return

    now = time.time()
    for f in TEMP_DIR.iterdir():
        if f.is_file() and (now - f.stat().st_mtime) > MAX_AGE_SECONDS:
            try:
                f.unlink()
            except OSError:
                pass