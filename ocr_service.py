from __future__ import annotations

from pathlib import Path

import pytesseract
from flask import current_app
from pdf2image import convert_from_path
from PIL import Image, ImageOps
from PyPDF2 import PdfReader


class OCRService:
    """Extract text from PDFs and image files using local CPU OCR."""

    @staticmethod
    def extract_text(filepath: str | Path) -> str:
        """Extract text from a PDF, PNG, JPG, or JPEG file."""
        path = Path(filepath)
        extension = path.suffix.lower()

        if extension == ".pdf":
            return OCRService._extract_from_pdf(path)
        if extension in {".png", ".jpg", ".jpeg"}:
            return OCRService._extract_from_image(path)

        raise ValueError(f"Unsupported file extension: {extension}")

    @staticmethod
    def _extract_from_image(path: Path) -> str:
        """Run Tesseract OCR on an image file."""
        try:
            with Image.open(path) as image:
                normalized = ImageOps.exif_transpose(image).convert("RGB")
                text = pytesseract.image_to_string(normalized)
                return OCRService._clean_ocr_text(text)
        except Exception as exc:
            current_app.logger.exception("OCR failed for image %s: %s", path, exc)
            raise RuntimeError("Image OCR failed") from exc

    @staticmethod
    def _extract_from_pdf(path: Path) -> str:
        """Convert PDF pages to images and run Tesseract OCR on each page."""
        try:
            pages = convert_from_path(str(path), dpi=200)
            page_text = []
            for index, page in enumerate(pages, start=1):
                current_app.logger.info(
                    "Running OCR on PDF page %s of %s", index, path.name
                )
                page_text.append(pytesseract.image_to_string(page.convert("RGB")))
            combined = "\n\n".join(page_text)
            cleaned = OCRService._clean_ocr_text(combined)
            if cleaned:
                return cleaned
        except Exception as exc:
            current_app.logger.warning(
                "PDF image OCR failed for %s, trying embedded text fallback: %s",
                path,
                exc,
            )

        return OCRService._extract_pdf_text_fallback(path)

    @staticmethod
    def _extract_pdf_text_fallback(path: Path) -> str:
        """Extract embedded text from a PDF when OCR conversion is unavailable."""
        try:
            reader = PdfReader(str(path))
            text_parts = []
            for page in reader.pages:
                text_parts.append(page.extract_text() or "")
            return OCRService._clean_ocr_text("\n\n".join(text_parts))
        except Exception as exc:
            current_app.logger.exception(
                "PDF fallback extraction failed for %s: %s", path, exc
            )
            raise RuntimeError("PDF text extraction failed") from exc

    @staticmethod
    def _clean_ocr_text(text: str) -> str:
        """Normalize OCR output while preserving readable line breaks."""
        lines = [" ".join(line.split()) for line in text.splitlines()]
        cleaned_lines = [line for line in lines if line]
        return "\n".join(cleaned_lines).strip()
