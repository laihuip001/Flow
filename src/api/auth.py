"""
Authentication Logic
"""
from fastapi import Header, HTTPException
from src.core.config import settings
import secrets

async def verify_token(authorization: str = Header(None)):
    """Bearer Token認証"""
    if not settings.API_TOKEN:
        return True

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "unauthorized",
                "message": "認証が必要です",
                "action": "Authorization: Bearer <token> ヘッダーを追加してください"
            }
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail={
                "error": "invalid_auth_format",
                "message": "認証形式が不正です"
            }
        )

    # Secure comparison using secrets.compare_digest to prevent timing attacks
    if not secrets.compare_digest(parts[1], settings.API_TOKEN):
        raise HTTPException(
            status_code=403,
            detail={"error": "forbidden", "message": "トークンが無効です"}
        )

    return True
