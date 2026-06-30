from __future__ import annotations

from pathlib import Path

from flask import Blueprint, current_app, jsonify, request
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from services.database_service import DatabaseService
from services.extractor_service import ExtractorService
from services.offline_ai_service import OfflineAIService
from services.ocr_service import OCRService
from services.simplifier_service import SimplifierService
from utils.helpers import delete_file_if_exists, make_unique_filename
from utils.validators import FileValidationError, FileValidator


api = Blueprint("api", __name__)


@api.get("/health")
def health():
    """Return backend health and release information."""
    return (
        jsonify(
            {
                "status": "running",
                "service": current_app.config["APP_NAME"],
                "version": current_app.config["APP_VERSION"],
            }
        ),
        200,
    )


@api.post("/upload")
def upload_document():
    """Upload, OCR, simplify, extract, store, and return document data."""
    uploaded_file = request.files.get("file")
    if uploaded_file is None:
        return (
            jsonify(
                {"success": False, "error": "No file part named 'file' was uploaded"}
            ),
            400,
        )

    try:
        FileValidator.validate_upload(uploaded_file)
    except FileValidationError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400

    saved_path: Path | None = None
    try:
        saved_path = _save_upload(uploaded_file)
        current_app.logger.info("Saved upload: %s", saved_path)

        raw_text = OCRService.extract_text(saved_path)
        if not raw_text.strip():
            delete_file_if_exists(saved_path)
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "No readable text found in uploaded file",
                    }
                ),
                400,
            )

        extracted = ExtractorService.extract_information(raw_text)
        simplified_result = SimplifierService.simplify_document(raw_text, extracted)
        document = DatabaseService.create_document_with_result(
            filename=saved_path.name,
            filepath=str(saved_path),
            raw_text=raw_text,
            document_type=extracted["document_type"],
            summary="\n".join(simplified_result["easy_explanation"]),
            action_required=simplified_result["action_required"],
            deadline=simplified_result["deadline"],
            contact=simplified_result["contact"],
            amount_due=simplified_result["amount_due"],
            priority=simplified_result["priority"],
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Document processed successfully",
                    "document": document.to_dict(),
                    "result": simplified_result,
                    "extracted_information": extracted,
                }
            ),
            201,
        )
    except Exception as exc:
        current_app.logger.exception("Upload processing failed: %s", exc)
        if saved_path is not None:
            delete_file_if_exists(saved_path)
        return (
            jsonify({"success": False, "error": "Failed to process uploaded document"}),
            500,
        )


@api.get("/documents")
def list_documents():
    """Return all processed documents."""
    try:
        documents = DatabaseService.list_documents()
        return (
            jsonify(
                {
                    "success": True,
                    "count": len(documents),
                    "documents": [
                        document.to_dict(include_result=True) for document in documents
                    ],
                }
            ),
            200,
        )
    except Exception as exc:
        current_app.logger.exception("Failed to list documents: %s", exc)
        return jsonify({"success": False, "error": "Failed to fetch documents"}), 500


@api.get("/document/<int:document_id>")
def get_document(document_id: int):
    """Return complete information for one document."""
    document = DatabaseService.get_document(document_id)
    if document is None:
        return jsonify({"success": False, "error": "Document not found"}), 404
    return (
        jsonify({"success": True, "document": document.to_dict(include_result=True)}),
        200,
    )


@api.delete("/document/<int:document_id>")
def delete_document(document_id: int):
    """Delete a document record, processed result, and uploaded file."""
    document = DatabaseService.get_document(document_id)
    if document is None:
        return jsonify({"success": False, "error": "Document not found"}), 404

    filepath = Path(document.filepath)
    try:
        DatabaseService.delete_document(document)
        delete_file_if_exists(filepath)
        return (
            jsonify({"success": True, "message": "Document deleted successfully"}),
            200,
        )
    except Exception as exc:
        current_app.logger.exception(
            "Failed to delete document %s: %s", document_id, exc
        )
        return jsonify({"success": False, "error": "Failed to delete document"}), 500


@api.post("/ask-ai")
def ask_offline_ai():
    """Answer user questions using the local offline assistant."""
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    if not question:
        return jsonify({"success": False, "error": "Question is required"}), 400

    try:
        documents = DatabaseService.list_documents()
        answer = OfflineAIService.answer_question(question, documents)
        current_app.logger.info(
            "Offline AI answered question mode=%s", answer.get("mode")
        )
        return jsonify(answer), 200
    except Exception as exc:
        current_app.logger.exception("Offline AI failed: %s", exc)
        return (
            jsonify({"success": False, "error": "Offline assistant failed to answer"}),
            500,
        )


def _save_upload(uploaded_file: FileStorage) -> Path:
    """Save an uploaded file using a safe unique filename."""
    original_name = secure_filename(uploaded_file.filename or "")
    unique_name = make_unique_filename(original_name)
    upload_folder = Path(current_app.config["UPLOAD_FOLDER"]).resolve()
    upload_folder.mkdir(parents=True, exist_ok=True)

    saved_path = (upload_folder / unique_name).resolve()
    if upload_folder not in saved_path.parents:
        raise ValueError("Invalid upload path")

    uploaded_file.save(saved_path)
    return saved_path
