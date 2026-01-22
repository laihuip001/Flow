import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
from src.api.main import verify_token
from src.core.config import settings
import secrets

# Mock settings
settings.API_TOKEN = "secret_token_123"

@pytest.mark.asyncio
async def test_verify_token_valid():
    """Test valid token verification"""
    result = await verify_token("Bearer secret_token_123")
    assert result is True

@pytest.mark.asyncio
async def test_verify_token_invalid_format():
    """Test invalid token format"""
    with pytest.raises(HTTPException) as excinfo:
        await verify_token("InvalidFormat")
    assert excinfo.value.status_code == 401

@pytest.mark.asyncio
async def test_verify_token_wrong_token():
    """Test wrong token"""
    with pytest.raises(HTTPException) as excinfo:
        await verify_token("Bearer wrong_token")
    assert excinfo.value.status_code == 403

@pytest.mark.asyncio
async def test_verify_token_timing_attack_protection():
    """Test that secrets.compare_digest is used (by mocking it)"""
    with patch("secrets.compare_digest", return_value=True) as mock_compare:
        await verify_token("Bearer secret_token_123")
        mock_compare.assert_called_once()
        # Verify arguments passed to compare_digest
        # Note: implementation might pass arguments in either order
        args = mock_compare.call_args[0]
        assert "secret_token_123" in args
