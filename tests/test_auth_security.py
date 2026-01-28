"""
Security Tests for Authentication
=================================

Tests for src.api.auth.verify_token
"""
import pytest
from fastapi import HTTPException
from src.api.auth import verify_token
from src.core.config import settings
from unittest.mock import patch

@pytest.mark.asyncio
async def test_verify_token_no_auth_configured():
    """API_TOKENが未設定の場合は常にTrueを返すこと"""
    with patch.object(settings, "API_TOKEN", ""):
        result = await verify_token(authorization=None)
        assert result is True

        result = await verify_token(authorization="Bearer whatever")
        assert result is True

@pytest.mark.asyncio
async def test_verify_token_valid():
    """正しいトークンで認証が成功すること"""
    with patch.object(settings, "API_TOKEN", "secret-token-123"):
        result = await verify_token(authorization="Bearer secret-token-123")
        assert result is True

@pytest.mark.asyncio
async def test_verify_token_missing_header():
    """ヘッダーがない場合は401エラーになること"""
    with patch.object(settings, "API_TOKEN", "secret-token-123"):
        with pytest.raises(HTTPException) as excinfo:
            await verify_token(authorization=None)
        assert excinfo.value.status_code == 401
        assert excinfo.value.detail["error"] == "unauthorized"

@pytest.mark.asyncio
async def test_verify_token_invalid_format_no_bearer():
    """Bearerスキームでない場合は401エラーになること"""
    with patch.object(settings, "API_TOKEN", "secret-token-123"):
        with pytest.raises(HTTPException) as excinfo:
            await verify_token(authorization="Basic dXNlcjpwYXNz")
        assert excinfo.value.status_code == 401
        assert excinfo.value.detail["error"] == "invalid_auth_format"

@pytest.mark.asyncio
async def test_verify_token_invalid_format_wrong_parts():
    """ヘッダーの形式が不正な場合は401エラーになること"""
    with patch.object(settings, "API_TOKEN", "secret-token-123"):
        with pytest.raises(HTTPException) as excinfo:
            await verify_token(authorization="Bearer")
        assert excinfo.value.status_code == 401

        with pytest.raises(HTTPException) as excinfo:
            await verify_token(authorization="Bearer token extra")
        assert excinfo.value.status_code == 401

@pytest.mark.asyncio
async def test_verify_token_wrong_token():
    """間違ったトークンの場合は403エラーになること"""
    with patch.object(settings, "API_TOKEN", "secret-token-123"):
        with pytest.raises(HTTPException) as excinfo:
            await verify_token(authorization="Bearer wrong-token")
        assert excinfo.value.status_code == 403
        assert excinfo.value.detail["error"] == "forbidden"
