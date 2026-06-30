from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from models import Document


@dataclass(frozen=True)
class AnswerSource:
    """A document reference used to answer a question."""

    document_id: int
    filename: str
    document_type: str

    def to_dict(self) -> dict[str, Any]:
        """Serialize the source for JSON responses."""
        return {
            "document_id": self.document_id,
            "filename": self.filename,
            "document_type": self.document_type,
        }


class OfflineAIService:
    """Local rule-based assistant for ClarityDoc questions."""

    STOPWORDS = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "ask",
        "at",
        "be",
        "by",
        "can",
        "do",
        "does",
        "for",
        "from",
        "give",
        "how",
        "i",
        "in",
        "is",
        "it",
        "me",
        "my",
        "of",
        "on",
        "or",
        "please",
        "show",
        "tell",
        "that",
        "the",
        "this",
        "to",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "with",
        "you",
    }

    @classmethod
    def answer_question(
        cls, question: str, documents: list[Document]
    ) -> dict[str, Any]:
        """Answer a user question using only local project data."""
        clean_question = cls._clean_text(question)
        if not clean_question:
            return cls._response(
                "Ask me about an uploaded document, deadline, payment, contact number, priority, or how ClarityDoc works.",
                "help",
            )

        intent_answer = cls._answer_project_intent(clean_question, documents)
        if intent_answer:
            return intent_answer

        if not documents:
            return cls._response(
                "I do not have any processed documents yet. Upload a document or paste text first, then ask me about it.",
                "no_documents",
            )

        if cls._contains_any(clean_question, {"latest", "recent", "newest", "last"}):
            best_document = documents[0]
        else:
            ranked_documents = cls._rank_documents(clean_question, documents)
            best_document = ranked_documents[0][1] if ranked_documents else documents[0]
        structured_answer = cls._answer_structured_question(
            clean_question, best_document
        )
        if structured_answer:
            return structured_answer

        answer_sentences = cls._find_relevant_sentences(clean_question, best_document)
        if answer_sentences:
            answer = " ".join(answer_sentences[:3])
            return cls._response(
                cls._plain_answer(answer),
                "document_search",
                [cls._source(best_document)],
            )

        summary = cls._document_summary(best_document)
        return cls._response(
            f"I could not find an exact match, but the closest document is {best_document.document_type}. {summary}",
            "closest_document",
            [cls._source(best_document)],
        )

    @classmethod
    def _answer_project_intent(
        cls,
        question: str,
        documents: list[Document],
    ) -> dict[str, Any] | None:
        """Answer general ClarityDoc questions that do not need document search."""
        if cls._contains_any(
            question,
            {"format", "file", "upload", "support", "pdf", "png", "jpg", "jpeg"},
        ):
            return cls._response(
                "ClarityDoc supports PDF, PNG, JPG, and JPEG files up to 20 MB. You can also paste document text directly.",
                "project_help",
            )

        if cls._contains_any(
            question, {"offline", "cloud", "privacy", "private", "internet"}
        ):
            return cls._response(
                "ClarityDoc is designed to work offline. Files are processed locally, saved in the uploads folder, and results are stored in SQLite.",
                "project_help",
            )

        if cls._contains_any(question, {"how", "work", "works", "process"}):
            return cls._response(
                "ClarityDoc works in three steps: upload or paste text, extract the text, then rewrite it in simple words and pull out important details.",
                "project_help",
            )

        if cls._contains_any(question, {"count", "many", "total", "documents"}):
            count = len(documents)
            noun = "document" if count == 1 else "documents"
            return cls._response(
                f"You have {count} processed {noun} saved locally.", "project_help"
            )

        return None

    @classmethod
    def _answer_structured_question(
        cls, question: str, document: Document
    ) -> dict[str, Any] | None:
        """Answer questions using extracted result fields when possible."""
        result = document.processed_result
        if result is None:
            return None

        combined_parts: list[str] = []
        if cls._contains_any(question, {"deadline", "date", "due"}) and result.deadline:
            combined_parts.append(f"Deadline: {result.deadline}")
        if (
            cls._contains_any(question, {"amount", "money", "pay", "payment"})
            and result.amount_due
        ):
            combined_parts.append(f"Amount due: {result.amount_due}")
        if (
            cls._contains_any(question, {"contact", "phone", "email"})
            and result.contact
        ):
            combined_parts.append(f"Contact: {result.contact}")
        if cls._contains_any(question, {"action", "do"}) and result.action_required:
            combined_parts.append(f"Action: {result.action_required}")

        if len(combined_parts) > 1:
            return cls._response(
                f"For {document.filename}, " + "; ".join(combined_parts) + ".",
                "structured_field",
                [cls._source(document)],
            )

        fields = {
            "deadline": result.deadline,
            "date": result.deadline,
            "due": result.deadline or result.amount_due,
            "amount": result.amount_due,
            "money": result.amount_due,
            "pay": result.amount_due or result.action_required,
            "payment": result.amount_due or result.action_required,
            "contact": result.contact,
            "phone": result.contact,
            "email": result.contact,
            "action": result.action_required,
            "do": result.action_required,
            "priority": result.priority,
            "urgent": result.priority,
            "type": document.document_type,
            "summary": result.summary,
            "explain": result.summary,
        }

        for keyword, value in fields.items():
            if keyword in question and value:
                return cls._response(
                    cls._format_field_answer(keyword, value, document),
                    "structured_field",
                    [cls._source(document)],
                )

        return None

    @classmethod
    def _format_field_answer(cls, keyword: str, value: str, document: Document) -> str:
        """Turn a structured value into a friendly offline assistant answer."""
        if keyword in {"deadline", "date"}:
            return f"The deadline in {document.filename} is {value}."
        if keyword in {"amount", "money"}:
            return f"The amount mentioned in {document.filename} is {value}."
        if keyword in {"contact", "phone", "email"}:
            return f"The contact detail in {document.filename} is {value}."
        if keyword in {"priority", "urgent"}:
            return f"The priority for {document.filename} is {value}."
        if keyword == "type":
            return f"This looks like a {document.document_type}."
        return f"For {document.filename}: {value}"

    @classmethod
    def _rank_documents(
        cls, question: str, documents: list[Document]
    ) -> list[tuple[int, Document]]:
        """Rank documents by keyword overlap with the question."""
        question_words = set(cls._keywords(question))
        ranked: list[tuple[int, Document]] = []
        for document in documents:
            text = " ".join(
                [
                    document.filename,
                    document.document_type,
                    document.raw_text,
                    (
                        document.processed_result.summary
                        if document.processed_result
                        else ""
                    ),
                    (
                        document.processed_result.action_required
                        if document.processed_result
                        and document.processed_result.action_required
                        else ""
                    ),
                ]
            )
            document_words = set(cls._keywords(text))
            score = len(question_words & document_words)
            ranked.append((score, document))
        return sorted(
            ranked, key=lambda item: (item[0], item[1].upload_time), reverse=True
        )

    @classmethod
    def _find_relevant_sentences(cls, question: str, document: Document) -> list[str]:
        """Find the most relevant sentences from a document."""
        question_words = set(cls._keywords(question))
        sentences = cls._sentences(
            " ".join(
                [
                    (
                        document.processed_result.summary
                        if document.processed_result
                        else ""
                    ),
                    (
                        document.processed_result.action_required
                        if document.processed_result
                        and document.processed_result.action_required
                        else ""
                    ),
                    document.raw_text,
                ]
            )
        )
        scored: list[tuple[int, str]] = []
        for sentence in sentences:
            sentence_words = set(cls._keywords(sentence))
            score = len(question_words & sentence_words)
            if score > 0:
                scored.append((score, sentence))
        return [
            sentence
            for _, sentence in sorted(scored, key=lambda item: item[0], reverse=True)
        ]

    @classmethod
    def _document_summary(cls, document: Document) -> str:
        """Create a short fallback answer for a document."""
        result = document.processed_result
        if result and result.summary:
            first_line = next(
                (
                    line.strip("-• ")
                    for line in result.summary.splitlines()
                    if line.strip()
                ),
                "",
            )
            if first_line:
                return first_line
        sentences = cls._sentences(document.raw_text)
        return (
            sentences[0]
            if sentences
            else "It has saved text, but I could not extract a short answer."
        )

    @classmethod
    def _plain_answer(cls, text: str) -> str:
        """Lightly clean a retrieved sentence for chat display."""
        replacements = {
            "shall": "must",
            "prior to": "before",
            "hereby": "",
            "subsequent": "next",
            "commence": "start",
            "terminate": "end",
            "notwithstanding": "even if",
        }
        answer = text
        for old, new in replacements.items():
            answer = re.sub(rf"\b{re.escape(old)}\b", new, answer, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", answer).strip()

    @classmethod
    def _contains_any(cls, text: str, words: set[str]) -> bool:
        """Return true when the text contains at least one keyword."""
        tokens = set(cls._keywords(text))
        return bool(tokens & words)

    @classmethod
    def _keywords(cls, text: str) -> list[str]:
        """Return searchable words from text."""
        words = re.findall(r"[a-zA-Z0-9@.₹$,-]+", text.lower())
        return [
            word.strip(".,-")
            for word in words
            if len(word.strip(".,-")) > 2 and word not in cls.STOPWORDS
        ]

    @staticmethod
    def _sentences(text: str) -> list[str]:
        """Split text into readable sentence-like chunks."""
        chunks = re.split(r"(?<=[.!?])\s+|\n+", text)
        return [
            re.sub(r"\s+", " ", chunk).strip(" -•") for chunk in chunks if chunk.strip()
        ]

    @staticmethod
    def _clean_text(text: str) -> str:
        """Normalize user question text."""
        return re.sub(r"\s+", " ", text).strip().lower()

    @classmethod
    def _source(cls, document: Document) -> AnswerSource:
        """Build an answer source from a document."""
        return AnswerSource(
            document_id=document.id,
            filename=document.filename,
            document_type=document.document_type,
        )

    @staticmethod
    def _response(
        answer: str,
        mode: str,
        sources: list[AnswerSource] | None = None,
    ) -> dict[str, Any]:
        """Build the standard assistant JSON response."""
        return {
            "success": True,
            "answer": answer,
            "mode": mode,
            "offline": True,
            "sources": [source.to_dict() for source in sources or []],
        }
