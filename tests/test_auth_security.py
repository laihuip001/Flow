import pytest
from fastapi import HTTPException
from src.api.auth import verify_token
from unittest.mock import patch

@pytest.mark.asyncio
async def test_verify_token_valid():
    with patch("src.core.config.settings.API_TOKEN", "test-token"):
        result = await verify_token(authorization="Bearer test-token")
        assert result is True

@pytest.mark.asyncio
async def test_verify_token_invalid():
    with patch("src.core.config.settings.API_TOKEN", "test-token"):
        with pytest.raises(HTTPException) as exc:
            await verify_token(authorization="Bearer wrong-token")
        assert exc.value.status_code == 403
        assert exc.value.detail["error"] == "forbidden"

@pytest.mark.asyncio
async def test_verify_token_missing_header():
    with patch("src.core.config.settings.API_TOKEN", "test-token"):
        with pytest.raises(HTTPException) as exc:
            await verify_token(authorization=None)
        assert exc.value.status_code == 401
        assert exc.value.detail["error"] == "unauthorized"

@pytest.mark.asyncio
async def test_verify_token_malformed_header():
    with patch("src.core.config.settings.API_TOKEN", "test-token"):
        with pytest.raises(HTTPException) as exc:
            await verify_token(authorization="Basic test-token")
        assert exc.value.status_code == 401
        assert exc.value.detail["error"] == "invalid_auth_format"

    with patch("src.core.config.settings.API_TOKEN", "test-token"):
        with pytest.raises(HTTPException) as exc:
            await verify_token(authorization="Bearer") # Missing token part
        assert exc.value.status_code == 401

@pytest.mark.asyncio
async def test_verify_token_dev_mode():
    with patch("src.core.config.settings.API_TOKEN", ""):
        result = await verify_token(authorization=None)
        assert result is True
