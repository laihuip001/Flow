import pytest
from fastapi import HTTPException
from unittest.mock import patch
from src.api.main import verify_token
from src.core.config import settings

@pytest.mark.asyncio
async def test_auth_valid_token():
    """Verify that a correct token is accepted."""
    with patch.object(settings, 'API_TOKEN', 'test_secret_token'):
        result = await verify_token(authorization="Bearer test_secret_token")
        assert result is True

@pytest.mark.asyncio
async def test_auth_invalid_token():
    """Verify that an incorrect token is rejected (403)."""
    with patch.object(settings, 'API_TOKEN', 'test_secret_token'):
        with pytest.raises(HTTPException) as excinfo:
            await verify_token(authorization="Bearer wrong_token")
        assert excinfo.value.status_code == 403

@pytest.mark.asyncio
async def test_auth_missing_header():
    """Verify that missing header is rejected (401)."""
    with patch.object(settings, 'API_TOKEN', 'test_secret_token'):
        with pytest.raises(HTTPException) as excinfo:
            await verify_token(authorization=None)
        assert excinfo.value.status_code == 401

@pytest.mark.asyncio
async def test_auth_invalid_format():
    """Verify that invalid header format is rejected (401)."""
    with patch.object(settings, 'API_TOKEN', 'test_secret_token'):
        with pytest.raises(HTTPException) as excinfo:
            await verify_token(authorization="Token test_secret_token")
        assert excinfo.value.status_code == 401

@pytest.mark.asyncio
async def test_auth_disabled():
    """Verify that auth is bypassed when API_TOKEN is empty."""
    with patch.object(settings, 'API_TOKEN', ''):
        result = await verify_token(authorization=None)
        assert result is True
