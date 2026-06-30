from __future__ import annotations

import time
import uuid
from pathlib import Path


def make_unique_filename(filename: str) -> str:
    """Return a safe unique filename while preserving the extension."""
    path = Path(filename)
    stem = path.stem or "document"
    suffix = path.suffix.lower()
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:10]
    return f"{stem}_{timestamp}_{unique_id}{suffix}"


def delete_file_if_exists(filepath: str | Path) -> None:
    """Delete a file if it exists."""
    path = Path(filepath)
    if path.exists() and path.is_file():
        path.unlink()
