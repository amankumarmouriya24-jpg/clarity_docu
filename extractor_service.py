from __future__ import annotations

import re
from typing import Any


class ExtractorService:
    """Extract structured information from OCR text using regex rules."""

    DOCUMENT_TYPE_KEYWORDS: dict[str, list[str]] = {
        "Medical Report": [
            "hospital",
            "patient",
            "doctor",
            "diagnosis",
            "medicine",
            "medical",
        ],
        "Insurance Policy": [
            "insurance",
            "policy",
            "premium",
            "claim",
            "insured",
            "beneficiary",
        ],
        "Government Notice": [
            "government",
            "department",
            "municipal",
            "notice",
            "application",
        ],
        "Bank Letter": ["bank", "account", "loan", "credit", "debit", "ifsc", "branch"],
        "Legal Notice": [
            "legal notice",
            "court",
            "advocate",
            "lawyer",
            "agreement",
            "liability",
        ],
        "Electricity Bill": ["electricity", "power", "meter", "kwh", "energy charges"],
        "Water Bill": ["water bill", "water supply", "water meter", "sewerage"],
    }

    DATE_PATTERNS: list[str] = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",
        r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{4}\b",
    ]

    @classmethod
    def extract_information(cls, text: str) -> dict[str, Any]:
        """Return structured document information extracted from text."""
        normalized = cls._normalize(text)
        document_type = cls._detect_document_type(normalized)
        deadline = cls._extract_deadline(normalized)
        contact = cls._extract_contact(normalized)
        amount_due = cls._extract_amount(normalized)
        action_required = cls._extract_action(
            normalized, document_type, amount_due, deadline
        )
        priority = cls._detect_priority(normalized, deadline, amount_due)
        summary = cls._build_summary(
            document_type, action_required, deadline, amount_due
        )

        return {
            "document_type": document_type,
            "summary": summary,
            "action_required": action_required,
            "deadline": deadline,
            "contact": contact,
            "amount_due": amount_due,
            "priority": priority,
        }

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize whitespace for reliable pattern matching."""
        return re.sub(r"\s+", " ", text).strip()

    @classmethod
    def _detect_document_type(cls, text: str) -> str:
        """Detect the closest supported document type from keywords."""
        lowered = text.lower()
        scores: dict[str, int] = {}
        for document_type, keywords in cls.DOCUMENT_TYPE_KEYWORDS.items():
            scores[document_type] = sum(1 for keyword in keywords if keyword in lowered)

        best_type = max(scores, key=scores.get)
        return best_type if scores[best_type] > 0 else "General Document"

    @classmethod
    def _extract_deadline(cls, text: str) -> str | None:
        """Extract a deadline date or duration from text."""
        deadline_patterns = [
            r"(?:deadline|due date|last date|pay by|submit by|before|on or before)\s*:?\s*([^.;,\n]+)",
            r"(?:within)\s+(\d+\s+(?:day|days|week|weeks|month|months))",
        ]
        for pattern in deadline_patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                date = cls._first_date(candidate)
                return date or candidate[:80]
        return cls._first_date(text)

    @classmethod
    def _first_date(cls, text: str) -> str | None:
        """Return the first date-like value found in text."""
        for pattern in cls.DATE_PATTERNS:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    @staticmethod
    def _extract_contact(text: str) -> str | None:
        """Extract phone numbers and email addresses."""
        emails = re.findall(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", text)
        phones = re.findall(r"(?:\+?\d[\d\s-]{7,}\d)", text)

        contacts: list[str] = []
        for item in phones + emails:
            cleaned = re.sub(r"\s+", " ", item).strip()
            if cleaned not in contacts:
                contacts.append(cleaned)

        return ", ".join(contacts) if contacts else None

    @staticmethod
    def _extract_amount(text: str) -> str | None:
        """Extract the most likely amount due from text."""
        patterns = [
            r"(?:amount due|total due|balance due|payable amount|payment of|total)\s*:?\s*((?:Rs\.?|INR|\$|USD)?\s?\d[\d,]*(?:\.\d{1,2})?)",
            r"\b((?:Rs\.?|INR|\$|USD)\s?\d[\d,]*(?:\.\d{1,2})?)\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    @staticmethod
    def _extract_action(
        text: str,
        document_type: str,
        amount_due: str | None,
        deadline: str | None,
    ) -> str | None:
        """Extract or infer the main action required from the user."""
        lowered = text.lower()
        payment_words = [
            "pay",
            "payment",
            "remit",
            "premium",
            "amount due",
            "balance due",
        ]
        if amount_due and any(word in lowered for word in payment_words):
            return f"Pay {amount_due}"

        patterns = [
            r"(?:shall remit payment|must pay|need to pay|payment should be completed)\s*(?:of)?\s*([^.!?]{0,120})",
            r"(?:you are required to|you must|please|kindly|requested to|need to)\s+([^.!?]{5,180})",
            r"\b(submit|send|upload|pay|visit|contact|call)\s+([^.!?]{3,160})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                action = " ".join(group for group in match.groups() if group)
                return action.strip(" .,:;")

        if amount_due:
            return f"Pay the amount due: {amount_due}"
        if deadline:
            return f"Complete the required action before {deadline}"
        if document_type == "Medical Report":
            return "Review the medical information and contact the hospital if anything is unclear"
        return None

    @staticmethod
    def _detect_priority(
        text: str, deadline: str | None, amount_due: str | None
    ) -> str:
        """Classify document priority as High, Medium, or Low."""
        lowered = text.lower()
        high_words = [
            "urgent",
            "final notice",
            "overdue",
            "penalty",
            "court",
            "termination",
        ]
        medium_words = ["due", "required", "submit", "payment", "claim", "notice"]

        if any(word in lowered for word in high_words):
            return "High"
        if deadline and amount_due:
            return "High"
        if deadline or amount_due or any(word in lowered for word in medium_words):
            return "Medium"
        return "Low"

    @staticmethod
    def _build_summary(
        document_type: str,
        action_required: str | None,
        deadline: str | None,
        amount_due: str | None,
    ) -> str:
        """Build a concise summary from extracted fields."""
        article = (
            "an" if document_type[:1].lower() in {"a", "e", "i", "o", "u"} else "a"
        )
        parts = [f"This looks like {article} {document_type}."]
        if action_required:
            parts.append(f"Main action: {action_required}.")
        if deadline:
            parts.append(f"Deadline: {deadline}.")
        if amount_due:
            parts.append(f"Amount mentioned: {amount_due}.")
        return " ".join(parts)
