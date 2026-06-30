from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _database_url() -> str:
    """Return a database URL that is stable regardless of the launch directory."""
    configured_url = os.getenv("DATABASE_URL")
    if not configured_url:
        return f"sqlite:///{BASE_DIR / 'database' / 'claritydoc.db'}"

    sqlite_prefix = "sqlite:///"
    if not configured_url.startswith(sqlite_prefix):
        return configured_url

    sqlite_path = configured_url.removeprefix(sqlite_prefix)
    if sqlite_path.startswith("/"):
        return configured_url

    return f"{sqlite_prefix}{BASE_DIR / sqlite_path}"


class Config:
    """Central configuration for the ClarityDoc backend."""

    APP_NAME: str = "ClarityDoc"
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "claritydoc-local-dev-key")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "5000"))

    UPLOAD_FOLDER: str = str(BASE_DIR / "uploads")
    DATABASE_DIR: str = str(BASE_DIR / "database")
    INSTANCE_DIR: str = str(BASE_DIR / "instance")
    LOG_DIR: str = str(BASE_DIR / "instance" / "logs")

    SQLALCHEMY_DATABASE_URI: str = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    MAX_CONTENT_LENGTH: int = 20 * 1024 * 1024

    ALLOWED_EXTENSIONS: set[str] = {"pdf", "png", "jpg", "jpeg"}
    ALLOWED_MIME_TYPES: set[str] = {
        "application/pdf",
        "image/png",
        "image/jpeg",
        "application/octet-stream",
    }
