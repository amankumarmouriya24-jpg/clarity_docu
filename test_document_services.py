from __future__ import annotations

import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from services.extractor_service import ExtractorService
from services.simplifier_service import SimplifierService


class ExtractorServiceTests(unittest.TestCase):
    def test_extracts_bill_details(self) -> None:
        text = (
            "Electricity Bill. Total due: INR 1,250.00. "
            "Please pay before 30/06/2026. Contact billing@example.com."
        )

        result = ExtractorService.extract_information(text)

        self.assertEqual(result["document_type"], "Electricity Bill")
        self.assertEqual(result["amount_due"], "INR 1,250.00")
        self.assertEqual(result["deadline"], "30/06/2026")
        self.assertIn("billing@example.com", result["contact"])
        self.assertEqual(result["priority"], "High")

    def test_uses_general_document_when_no_keywords_match(self) -> None:
        result = ExtractorService.extract_information(
            "A short note with no specific category."
        )

        self.assertEqual(result["document_type"], "General Document")
        self.assertEqual(result["priority"], "Low")


class SimplifierServiceTests(unittest.TestCase):
    def test_replaces_formal_language(self) -> None:
        result = SimplifierService.simplify_document(
            "You are hereby notified that the outstanding balance must be paid.",
            {
                "document_type": "Bank Letter",
                "action_required": "remit payment",
                "deadline": None,
                "amount_due": None,
                "contact": None,
                "priority": "Medium",
            },
        )

        output = " ".join(result["easy_explanation"] + result["important_points"])
        self.assertIn("You need to pay", output)
        self.assertNotIn("hereby", output.lower())
        self.assertNotIn("remit", output.lower())

    def test_returns_fallback_for_blank_text(self) -> None:
        result = SimplifierService.simplify_text("   ")

        self.assertIn("important information", result.lower())
        self.assertTrue(result.startswith("- "))


if __name__ == "__main__":
    unittest.main()
