"""
Security Tests for Authentication
================================
Tests specific authentication scenarios including secure token comparison.
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.api.main import app

class TestAuthSecurity(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("src.api.auth.settings")
    @patch("src.api.routes.vocab.get_vocab_store")
    def test_verify_token_secure_comparison(self, mock_vocab_store, mock_settings):
        """Test authentication with secure comparison"""
        # Mock vocab store to avoid errors inside the endpoint
        mock_store = MagicMock()
        mock_store.list_all.return_value = []
        mock_vocab_store.return_value = mock_store

        # Enable auth by setting a token
        mock_settings.API_TOKEN = "secret_token_123"

        # 1. Valid token
        response = self.client.get(
            "/vocab",
            headers={"Authorization": "Bearer secret_token_123"}
        )
        # Should be allowed (200 OK because we mocked the store)
        self.assertEqual(response.status_code, 200)

        # 2. Invalid token (wrong value)
        response = self.client.get(
            "/vocab",
            headers={"Authorization": "Bearer wrong_token"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"]["error"], "forbidden")

        # 3. Missing header
        response = self.client.get("/vocab")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"]["error"], "unauthorized")

        # 4. Malformed header (No Bearer)
        response = self.client.get(
            "/vocab",
            headers={"Authorization": "Basic user:pass"}
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"]["error"], "invalid_auth_format")

    @patch("src.api.auth.settings")
    @patch("src.api.routes.vocab.get_vocab_store")
    def test_auth_disabled(self, mock_vocab_store, mock_settings):
        """Test behavior when API_TOKEN is not set (Dev mode)"""
        # Mock vocab store
        mock_store = MagicMock()
        mock_store.list_all.return_value = []
        mock_vocab_store.return_value = mock_store

        # Disable auth
        mock_settings.API_TOKEN = ""

        response = self.client.get("/vocab")
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
