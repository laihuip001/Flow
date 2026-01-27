import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from src.api.auth import verify_token
from src.core.config import settings
import asyncio

class TestAuthSecurity(unittest.IsolatedAsyncioTestCase):
    async def test_auth_bypass_when_token_empty(self):
        """Test that auth is bypassed when API_TOKEN is not set"""
        with patch.object(settings, 'API_TOKEN', ""):
            result = await verify_token(authorization=None)
            self.assertTrue(result)

    async def test_missing_header_when_auth_enabled(self):
        """Test that missing header raises 401 when API_TOKEN is set"""
        with patch.object(settings, 'API_TOKEN', "secret-token"):
            with self.assertRaises(HTTPException) as cm:
                await verify_token(authorization=None)
            self.assertEqual(cm.exception.status_code, 401)
            self.assertEqual(cm.exception.detail["error"], "unauthorized")

    async def test_malformed_header_format(self):
        """Test that malformed header raises 401"""
        with patch.object(settings, 'API_TOKEN', "secret-token"):
            # Missing Bearer prefix
            with self.assertRaises(HTTPException) as cm:
                await verify_token(authorization="InvalidFormat")
            self.assertEqual(cm.exception.status_code, 401)
            self.assertEqual(cm.exception.detail["error"], "invalid_auth_format")

            # Wrong prefix
            with self.assertRaises(HTTPException) as cm:
                await verify_token(authorization="Basic secret-token")
            self.assertEqual(cm.exception.status_code, 401)
            self.assertEqual(cm.exception.detail["error"], "invalid_auth_format")

    async def test_invalid_token(self):
        """Test that invalid token raises 403"""
        with patch.object(settings, 'API_TOKEN', "secret-token"):
            with self.assertRaises(HTTPException) as cm:
                await verify_token(authorization="Bearer wrong-token")
            self.assertEqual(cm.exception.status_code, 403)
            self.assertEqual(cm.exception.detail["error"], "forbidden")

    async def test_valid_token(self):
        """Test that valid token returns True"""
        with patch.object(settings, 'API_TOKEN', "secret-token"):
            result = await verify_token(authorization="Bearer secret-token")
            self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()
