from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

from config import Config
from database import init_database
from extensions import db
from routes import api


def create_app() -> Flask:
    """Create and configure the ClarityDoc Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    _ensure_directories(app)
    _configure_logging(app)

    CORS(app)
    db.init_app(app)
    app.register_blueprint(api)

    with app.app_context():
        init_database()

    @app.before_request
    def log_request() -> None:
        """Log every incoming API request."""
        app.logger.info("%s %s", request.method, request.path)

    @app.errorhandler(400)
    def bad_request(error: Exception):  # type: ignore[no-untyped-def]
        """Return JSON for bad request errors."""
        return jsonify({"success": False, "error": str(error)}), 400

    @app.errorhandler(404)
    def not_found(error: Exception):  # type: ignore[no-untyped-def]
        """Return JSON for not found errors."""
        return jsonify({"success": False, "error": "Resource not found"}), 404

    @app.errorhandler(413)
    def too_large(error: Exception):  # type: ignore[no-untyped-def]
        """Return JSON when an uploaded file is too large."""
        return jsonify({"success": False, "error": "File is larger than 20 MB"}), 413

    @app.errorhandler(500)
    def server_error(error: Exception):  # type: ignore[no-untyped-def]
        """Return JSON for unexpected server errors."""
        app.logger.exception("Unhandled server error: %s", error)
        return jsonify({"success": False, "error": "Internal server error"}), 500

    return app


def _ensure_directories(app: Flask) -> None:
    """Create required runtime folders if they do not already exist."""
    for key in ("UPLOAD_FOLDER", "DATABASE_DIR", "INSTANCE_DIR", "LOG_DIR"):
        Path(app.config[key]).mkdir(parents=True, exist_ok=True)


def _configure_logging(app: Flask) -> None:
    """Configure console and rotating file logs for the backend."""
    log_path = Path(app.config["LOG_DIR"]) / "claritydoc.log"
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    app.logger.handlers.clear()
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)


app = create_app()


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
