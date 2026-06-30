from __future__ import annotations

from pathlib import Path

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


class FileValidationError(ValueError):
    """Raised when an uploaded file fails validation."""


class FileValidator:
    """Validate uploaded documents before saving them."""

    @staticmethod
    def validate_upload(uploaded_file: FileStorage) -> None:
        """Validate presence, filename, extension, MIME type, and size."""
        if uploaded_file.filename is None or not uploaded_file.filename.strip():
            raise FileValidationError("Empty upload filename")

        safe_name = secure_filename(uploaded_file.filename)
        if not safe_name:
            raise FileValidationError("Invalid filename")

        extension = FileValidator._extension(safe_name)
        allowed_extensions = current_app.config["ALLOWED_EXTENSIONS"]
        if extension not in allowed_extensions:
            raise FileValidationError(
                "Unsupported file type. Allowed files: PDF, PNG, JPG, JPEG"
            )

        allowed_mimes = current_app.config["ALLOWED_MIME_TYPES"]
        if uploaded_file.mimetype and uploaded_file.mimetype not in allowed_mimes:
            raise FileValidationError(
                f"Unsupported MIME type: {uploaded_file.mimetype}"
            )

        FileValidator._validate_size(uploaded_file)

    @staticmethod
    def _extension(filename: str) -> str:
        """Return lowercase extension without dot."""
        return Path(filename).suffix.lower().lstrip(".")

    @staticmethod
    def _validate_size(uploaded_file: FileStorage) -> None:
        """Reject files larger than the configured maximum size."""
        max_size = int(current_app.config["MAX_CONTENT_LENGTH"])
        stream = uploaded_file.stream
        current_position = stream.tell()
        stream.seek(0, 2)
        size = stream.tell()
        stream.seek(current_position)

        if size == 0:
            raise FileValidationError("Uploaded file is empty")
        if size > max_size:
            raise FileValidationError("File is larger than 20 MB")
