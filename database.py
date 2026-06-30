from __future__ import annotations

from flask import current_app

from extensions import db


def init_database() -> None:
    """Create all database tables required by the backend."""
    try:
        db.create_all()
        current_app.logger.info("Database initialized successfully")
    except Exception as exc:
        current_app.logger.exception("Database initialization failed: %s", exc)
        raise
