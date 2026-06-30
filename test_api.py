from __future__ import annotations

import sys
import unittest
from io import BytesIO
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app import app


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_health_returns_service_information(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                "status": "running",
                "service": "ClarityDoc",
                "version": "1.0.0",
            },
        )

    def test_upload_requires_file_field(self) -> None:
        response = self.client.post("/upload")

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["success"])

    def test_upload_rejects_unsupported_extension(self) -> None:
        response = self.client.post(
            "/upload",
            data={"file": (BytesIO(b"plain text"), "notes.txt")},
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported file type", response.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
