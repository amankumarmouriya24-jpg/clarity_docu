from __future__ import annotations

from flask import current_app

from extensions import db
from models import Document, ProcessedResult


class DatabaseService:
    """Database operations for documents and processed results."""

    @staticmethod
    def create_document_with_result(
        *,
        filename: str,
        filepath: str,
        raw_text: str,
        document_type: str,
        summary: str,
        action_required: str | None,
        deadline: str | None,
        contact: str | None,
        amount_due: str | None,
        priority: str,
    ) -> Document:
        """Store one uploaded document and its processed result."""
        try:
            document = Document(
                filename=filename,
                filepath=filepath,
                raw_text=raw_text,
                document_type=document_type,
            )
            db.session.add(document)
            db.session.flush()

            processed_result = ProcessedResult(
                document_id=document.id,
                summary=summary,
                action_required=action_required,
                deadline=deadline,
                contact=contact,
                amount_due=amount_due,
                priority=priority,
            )
            db.session.add(processed_result)
            db.session.commit()
            db.session.refresh(document)
            current_app.logger.info(
                "Stored document id=%s filename=%s", document.id, filename
            )
            return document
        except Exception as exc:
            db.session.rollback()
            current_app.logger.exception("Database save failed: %s", exc)
            raise

    @staticmethod
    def list_documents() -> list[Document]:
        """Return all documents newest first."""
        return Document.query.order_by(Document.upload_time.desc()).all()

    @staticmethod
    def get_document(document_id: int) -> Document | None:
        """Return one document by id, or None if it does not exist."""
        return Document.query.get(document_id)

    @staticmethod
    def delete_document(document: Document) -> None:
        """Delete one document and its processed result."""
        try:
            db.session.delete(document)
            db.session.commit()
            current_app.logger.info("Deleted document id=%s", document.id)
        except Exception as exc:
            db.session.rollback()
            current_app.logger.exception("Database delete failed: %s", exc)
            raise
