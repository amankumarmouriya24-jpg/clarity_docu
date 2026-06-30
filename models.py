from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from extensions import db


class Document(db.Model):
    """Uploaded document and raw OCR text."""

    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    upload_time = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    raw_text = db.Column(db.Text, nullable=False)
    document_type = db.Column(db.String(100), nullable=False)

    processed_result = db.relationship(
        "ProcessedResult",
        back_populates="document",
        cascade="all, delete-orphan",
        uselist=False,
    )

    def to_dict(self, include_result: bool = True) -> dict[str, Any]:
        """Serialize a document for JSON API responses."""
        data: dict[str, Any] = {
            "id": self.id,
            "filename": self.filename,
            "filepath": self.filepath,
            "upload_time": self.upload_time.isoformat(),
            "raw_text": self.raw_text,
            "document_type": self.document_type,
        }
        if include_result and self.processed_result:
            data["processed_result"] = self.processed_result.to_dict()
        return data


class ProcessedResult(db.Model):
    """Simplified and extracted information for a document."""

    __tablename__ = "processed_results"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(
        db.Integer,
        db.ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    summary = db.Column(db.Text, nullable=False)
    action_required = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.String(100), nullable=True)
    contact = db.Column(db.String(500), nullable=True)
    amount_due = db.Column(db.String(100), nullable=True)
    priority = db.Column(db.String(50), nullable=False)

    document = db.relationship("Document", back_populates="processed_result")

    def to_dict(self) -> dict[str, Any]:
        """Serialize a processed result for JSON API responses."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "summary": self.summary,
            "action_required": self.action_required,
            "deadline": self.deadline,
            "contact": self.contact,
            "amount_due": self.amount_due,
            "priority": self.priority,
        }
