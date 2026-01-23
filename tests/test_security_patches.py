import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.api.main import app
from src.core.config import settings

class TestSecurityPatches(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Mock API_TOKEN to be set for these tests
        self.original_token = settings.API_TOKEN
        settings.API_TOKEN = "test-secret-token"

    def tearDown(self):
        settings.API_TOKEN = self.original_token

    def test_prefetch_requires_auth(self):
        """Test that POST /prefetch requires authentication"""
        response = self.client.post(
            "/prefetch",
            json={
                "text": "test prefetch",
                "target_seasoning_levels": [30, 70]
            }
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"]["error"], "unauthorized")

    def test_prefetch_with_valid_token(self):
        """Test that POST /prefetch works with valid token"""
        # We need to mock core_processor to avoid actual background tasks logic failing if dependencies missing
        with patch("src.api.routes.safety.core_processor") as mock_processor:
            # Setup mock behavior if needed

            response = self.client.post(
                "/prefetch",
                json={
                    "text": "test prefetch",
                    "target_seasoning_levels": [30, 70]
                },
                headers={"Authorization": "Bearer test-secret-token"}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "accepted")

    def test_prefetch_with_invalid_token(self):
        """Test that POST /prefetch rejects invalid token"""
        response = self.client.post(
            "/prefetch",
            json={
                "text": "test prefetch",
                "target_seasoning_levels": [30, 70]
            },
            headers={"Authorization": "Bearer wrong-token"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"]["error"], "forbidden")

    def test_scan_no_auth_required(self):
        """Test that POST /scan still does NOT require auth"""
        response = self.client.post(
            "/scan",
            json={"text": "My phone is 090-1234-5678"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("has_risks", data)

if __name__ == "__main__":
    unittest.main()
