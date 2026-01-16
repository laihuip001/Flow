
import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.api.main import app
from src.core.config import settings

class TestAuthSecurity(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.original_token = settings.API_TOKEN
        settings.API_TOKEN = "test-secret-token"

    def tearDown(self):
        settings.API_TOKEN = self.original_token

    def test_auth_success(self):
        """Test valid token access"""
        # We target a protected route. Based on main.py, audit_router is protected.
        # Even if the specific path doesn't exist, if auth fails we get 403/401.
        # If auth succeeds but path is missing, we get 404.
        response = self.client.get(
            "/audit/logs",
            headers={"Authorization": "Bearer test-secret-token"}
        )
        self.assertNotEqual(response.status_code, 401)
        self.assertNotEqual(response.status_code, 403)

    def test_auth_failure_wrong_token(self):
        """Test invalid token access"""
        response = self.client.get(
            "/audit/logs",
            headers={"Authorization": "Bearer wrong-token"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"]["error"], "forbidden")

    def test_auth_failure_no_header(self):
        """Test missing auth header"""
        response = self.client.get("/audit/logs")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"]["error"], "unauthorized")

    def test_auth_failure_bad_format(self):
        """Test malformed auth header"""
        response = self.client.get(
            "/audit/logs",
            headers={"Authorization": "Basic user:pass"}
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"]["error"], "invalid_auth_format")

if __name__ == "__main__":
    unittest.main()
