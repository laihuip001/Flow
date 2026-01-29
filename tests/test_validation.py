import sys
import os
import unittest
from fastapi.testclient import TestClient

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.api.main import app

class TestInputValidation(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_scan_text_within_limit(self):
        """Test scanning text within the length limit"""
        text = "a" * 1000
        response = self.client.post("/scan", json={"text": text})
        self.assertEqual(response.status_code, 200)

    def test_scan_text_exceeding_limit(self):
        """Test scanning text exceeding the length limit"""
        text = "a" * 100001
        response = self.client.post("/scan", json={"text": text})
        self.assertEqual(response.status_code, 422)

        # Verify error message contains something about length
        data = response.json()
        self.assertIn("detail", data)
        # Pydantic v2 error structure is a list of dicts
        self.assertTrue(any(e['type'] == 'string_too_long' for e in data['detail']))

if __name__ == "__main__":
    unittest.main()
