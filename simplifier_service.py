from __future__ import annotations

import re
from typing import Any


class SimplifierService:
    """Offline document simplification pipeline.

    The service does not summarize by copying original sentences. It rewrites
    meaning into short plain-English bullets for elderly users and students.
    """

    SYSTEM_PROMPT = (
        "You are an expert document translator. Your job is NOT to summarize. "
        "Your job is to explain difficult documents in very simple everyday "
        "English. Never copy sentences. Rewrite everything. Use short sentences. "
        "Avoid legal, medical and insurance jargon. Explain like you are talking "
        "to a school student. Output only structured JSON."
    )

    JARGON_REPLACEMENTS: dict[str, str] = {
        "shall remit payment": "must pay",
        "remit payment": "pay",
        "coverage will lapse": "your insurance will stop",
        "coverage shall lapse": "your insurance will stop",
        "policy will lapse": "your insurance will stop",
        "policy shall lapse": "your insurance will stop",
        "hereby notified": "we are telling you",
        "you are hereby notified": "we are telling you",
        "subsequent": "next",
        "commence": "start",
        "terminate": "end",
        "terminated": "ended",
        "prior to": "before",
        "notwithstanding": "even if",
        "insured party": "you",
        "the insured": "you",
        "pursuant to": "under",
        "in accordance with": "under",
        "in the event that": "if",
        "failure to comply": "if you do not do this",
        "outstanding balance": "unpaid amount",
        "remittance": "payment",
        "beneficiary": "person who gets the benefit",
        "claimant": "person making the claim",
        "documentation": "documents",
        "verification": "checking",
        "liability": "responsibility",
        "indemnification": "payment for your loss",
        "aforementioned": "mentioned above",
        "hereinafter": "from now on",
        "at your earliest convenience": "as soon as possible",
        "enclosed herewith": "included",
        "we are writing to inform you": "",
        "please be advised that": "",
        "this is to inform you that": "",
    }

    FORBIDDEN_WORDS: set[str] = {
        "shall",
        "hereby",
        "pursuant",
        "notwithstanding",
        "aforementioned",
        "hereinafter",
        "thereof",
        "remit",
        "commence",
        "terminate",
        "subsequent",
        "prior",
        "indemnification",
    }

    @classmethod
    def simplify_document(cls, text: str, extracted: dict[str, Any]) -> dict[str, Any]:
        """Return a clean structured plain-English response."""
        cleaned = cls._prepare_text(text)
        plain_text = cls._replace_jargon(cleaned)
        easy_explanation = cls._build_easy_explanation(plain_text, extracted)
        important_points = cls._build_important_points(plain_text, extracted)

        return {
            "document_type": extracted.get("document_type") or "General Document",
            "easy_explanation": easy_explanation,
            "important_points": important_points,
            "action_required": cls._plain_action(extracted.get("action_required")),
            "deadline": extracted.get("deadline"),
            "amount_due": extracted.get("amount_due"),
            "contact": extracted.get("contact"),
            "priority": extracted.get("priority") or "Low",
        }

    @classmethod
    def simplify_text(cls, text: str) -> str:
        """Return plain bullets when only raw text is available."""
        extracted = {
            "document_type": "General Document",
            "action_required": None,
            "deadline": None,
            "amount_due": None,
            "contact": None,
            "priority": "Low",
        }
        structured = cls.simplify_document(text, extracted)
        return "\n".join(f"- {item}" for item in structured["easy_explanation"])

    @classmethod
    def _prepare_text(cls, text: str) -> str:
        """Normalize text and remove greeting/opening noise."""
        normalized = re.sub(r"\s+", " ", text).strip()
        normalized = re.sub(
            r"^(dear|to)\s+[^,.:\n]{1,80}[,.:]\s*",
            "",
            normalized,
            flags=re.IGNORECASE,
        )
        normalized = re.sub(
            r"^(sir|madam|respected sir|respected madam)[,.:]?\s*",
            "",
            normalized,
            flags=re.IGNORECASE,
        )
        return normalized.strip()

    @classmethod
    def _replace_jargon(cls, text: str) -> str:
        """Replace technical phrases with direct everyday words."""
        plain = text
        for hard, simple in cls.JARGON_REPLACEMENTS.items():
            plain = re.sub(re.escape(hard), simple, plain, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", plain).strip()

    @classmethod
    def _build_easy_explanation(cls, text: str, extracted: dict[str, Any]) -> list[str]:
        """Build short rewritten bullets that explain what the document means."""
        bullets: list[str] = []
        doc_type = extracted.get("document_type") or "General Document"
        action = cls._plain_action(extracted.get("action_required"))
        deadline = extracted.get("deadline")
        amount = extracted.get("amount_due")
        contact = extracted.get("contact")

        bullets.append(cls._document_intro(doc_type, text))

        if amount and deadline:
            bullets.append(f"You need to pay {amount} before {deadline}.")
        elif amount:
            bullets.append(f"The document mentions a payment of {amount}.")
        elif deadline:
            bullets.append(f"You need to do this before {deadline}.")

        if action and not (amount and "pay" in action.lower()):
            bullets.append(action)

        consequence = cls._detect_consequence(text, doc_type)
        if consequence:
            bullets.append(consequence)

        if contact:
            bullets.append(f"Contact {contact} if you need help.")

        if len(bullets) < 3:
            bullets.extend(cls._meaning_bullets_from_text(text, doc_type))

        return cls._clean_bullets(bullets, limit=5)

    @classmethod
    def _build_important_points(cls, text: str, extracted: dict[str, Any]) -> list[str]:
        """Build important facts without copying original sentences."""
        points: list[str] = []
        doc_type = extracted.get("document_type")
        action = cls._plain_action(extracted.get("action_required"))

        if doc_type:
            points.append(f"Document type: {doc_type}.")
        if extracted.get("priority"):
            points.append(f"Priority: {extracted['priority']}.")
        if action:
            points.append(f"Main action: {action}")
        if extracted.get("deadline"):
            points.append(f"Deadline: {extracted['deadline']}.")
        if extracted.get("amount_due"):
            points.append(f"Amount: {extracted['amount_due']}.")
        if extracted.get("contact"):
            points.append(f"Help contact: {extracted['contact']}.")

        if not points:
            points.append(cls._document_intro(doc_type or "General Document", text))

        return cls._clean_bullets(points, limit=6)

    @classmethod
    def _document_intro(cls, document_type: str, text: str) -> str:
        """Create a plain first bullet based on document type and meaning."""
        lowered = text.lower()
        if document_type == "Insurance Policy":
            if any(word in lowered for word in ["lapse", "expire", "renew", "premium"]):
                return "Your insurance needs attention so it does not stop."
            if "claim" in lowered:
                return "This is about your insurance claim."
            return "This document is about your insurance."
        if document_type == "Medical Report":
            return "This document is about your health or hospital visit."
        if document_type == "Government Notice":
            return "A government office is asking you to check or do something."
        if document_type == "Bank Letter":
            return "This document is about your bank account or money."
        if document_type == "Legal Notice":
            return "This is an important notice that needs careful action."
        if document_type == "Electricity Bill":
            return "This is about your electricity bill."
        if document_type == "Water Bill":
            return "This is about your water bill."
        return "This document has important information for you."

    @classmethod
    def _plain_action(cls, action: Any) -> str | None:
        """Rewrite an extracted action into direct plain English."""
        if not action:
            return None

        text = cls._replace_jargon(str(action)).strip(" .,:;")
        text = re.sub(
            r"^(you must|please|kindly|requested to|required to|need to)\s+",
            "",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r"\bpayment should be completed\b", "pay", text, flags=re.IGNORECASE
        )
        text = re.sub(
            r"\bshould be completed\b", "needs to be done", text, flags=re.IGNORECASE
        )
        text = re.sub(r"^pay\b", "pay", text, flags=re.IGNORECASE)

        lowered = text.lower()
        if lowered.startswith("pay"):
            rewritten = "You need to " + text
        elif lowered.startswith(
            ("submit", "send", "upload", "visit", "call", "contact")
        ):
            rewritten = "You need to " + text
        elif lowered.startswith("complete"):
            rewritten = "You need to " + text
        else:
            rewritten = "You need to " + text

        return cls._finish_sentence(rewritten)

    @classmethod
    def _detect_consequence(cls, text: str, document_type: str) -> str | None:
        """Explain likely consequence in plain English."""
        lowered = text.lower()
        if any(
            word in lowered
            for word in [
                "lapse",
                "expire",
                "termination",
                "terminated",
                "stop working",
                "will stop",
            ]
        ):
            if document_type == "Insurance Policy":
                return "If you do not act, your insurance may stop working."
            return "If you do not act, this service or benefit may stop."
        if any(word in lowered for word in ["penalty", "fine", "overdue", "late fee"]):
            return "If you are late, you may have to pay extra money."
        if "claim" in lowered and any(
            word in lowered for word in ["deny", "rejected", "pending"]
        ):
            return "If you do not send the needed documents, your claim may not be approved."
        return None

    @classmethod
    def _meaning_bullets_from_text(cls, text: str, document_type: str) -> list[str]:
        """Create fallback meaning bullets from concepts, not copied sentences."""
        lowered = text.lower()
        bullets: list[str] = []
        if any(
            word in lowered for word in ["document", "proof", "summary", "certificate"]
        ):
            bullets.append("You may need to give extra documents.")
        if any(
            word in lowered for word in ["hospital", "doctor", "patient", "diagnosis"]
        ):
            bullets.append("Keep this with your medical records.")
        if any(word in lowered for word in ["account", "bank", "loan"]):
            bullets.append("Check the money or account details carefully.")
        if not bullets:
            bullets.append(
                f"Read this {document_type.lower()} carefully before you ignore it."
            )
        return bullets

    @classmethod
    def _clean_bullets(cls, bullets: list[str], limit: int) -> list[str]:
        """Remove duplicates, legal wording, and overly long bullets."""
        cleaned: list[str] = []
        seen: set[str] = set()
        for bullet in bullets:
            simple = cls._remove_forbidden_words(cls._finish_sentence(bullet))
            words = simple.split()
            if len(words) > 18:
                simple = " ".join(words[:18]).rstrip(",;:") + "."
            key = simple.lower()
            if simple and key not in seen:
                cleaned.append(simple)
                seen.add(key)
            if len(cleaned) >= limit:
                break
        return cleaned

    @classmethod
    def _remove_forbidden_words(cls, text: str) -> str:
        """Remove legal wording that should never appear in final output."""
        result = text
        for word in cls.FORBIDDEN_WORDS:
            result = re.sub(rf"\b{re.escape(word)}\b", "", result, flags=re.IGNORECASE)
        result = re.sub(r"\s+", " ", result)
        return result.strip(" ,")

    @staticmethod
    def _finish_sentence(text: str) -> str:
        """Return a clean sentence with final punctuation."""
        cleaned = re.sub(r"\s+", " ", text).strip(" .,:;")
        if not cleaned:
            return ""
        return cleaned[0].upper() + cleaned[1:] + "."
