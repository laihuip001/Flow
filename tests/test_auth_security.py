import pytest
from unittest.mock import patch
from fastapi import HTTPException
from src.api.main import verify_token

@pytest.mark.asyncio
async def test_verify_token_no_auth_required():
    with patch("src.api.main.settings") as mock_settings:
        mock_settings.API_TOKEN = ""
        result = await verify_token(authorization=None)
        assert result is True

@pytest.mark.asyncio
async def test_verify_token_missing_header():
    with patch("src.api.main.settings") as mock_settings:
        mock_settings.API_TOKEN = "secret"
        with pytest.raises(HTTPException) as excinfo:
            await verify_token(authorization=None)
        assert excinfo.value.status_code == 401
        assert excinfo.value.detail["error"] == "unauthorized"

@pytest.mark.asyncio
async def test_verify_token_invalid_format():
    with patch("src.api.main.settings") as mock_settings:
        mock_settings.API_TOKEN = "secret"
        with pytest.raises(HTTPException) as excinfo:
            await verify_token(authorization="Token secret")
        assert excinfo.value.status_code == 401
        assert excinfo.value.detail["error"] == "invalid_auth_format"

@pytest.mark.asyncio
async def test_verify_token_wrong_token():
    with patch("src.api.main.settings") as mock_settings:
        mock_settings.API_TOKEN = "secret"
        with pytest.raises(HTTPException) as excinfo:
            await verify_token(authorization="Bearer wrong")
        assert excinfo.value.status_code == 403
        assert excinfo.value.detail["error"] == "forbidden"

@pytest.mark.asyncio
async def test_verify_token_correct_token():
    with patch("src.api.main.settings") as mock_settings:
        mock_settings.API_TOKEN = "secret"
        result = await verify_token(authorization="Bearer secret")
        assert result is True
