"""
Audit API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, List
from src.infra.audit import get_audit_manager
from src.core.config import settings

router = APIRouter(prefix="/audit", tags=["Audit"])

class AuditLogResponse(BaseModel):
    id: int
    timestamp: str
    user_id: str
    action_type: str
    ai_model: Optional[str] = None
    current_hash: str
    
    class Config:
        from_attributes = True

class VerifyResponse(BaseModel):
    is_valid: bool
    total_count: int
    errors: List[str]
    message: str

def get_current_user_id(request: Request) -> str:
    """
    C-3: Get user_id from auth state or default to anonymous.
    Assuming middleware or auth dependency sets request.state.user
    For now, we derive it from token or default.
    """
    # In a real auth flow, this comes from the verify_token dependency decoding the token
    # For now, we return a simpler identifier
    auth = request.headers.get("Authorization")
    if auth and settings.API_TOKEN and auth.split()[-1] == settings.API_TOKEN:
        return "admin_user"
    return "anonymous"

@router.get("/logs", response_model=List[AuditLogResponse])
async def get_logs(limit: int = 100, offset: int = 0):
    """監査ログ一覧を取得"""
    audit = get_audit_manager()
    logs = audit.get_logs(limit=limit, offset=offset)
    return [
        {
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "user_id": log.user_id,
            "action_type": log.action_type,
            "ai_model": log.ai_model,
            "current_hash": log.current_hash
        }
        for log in logs
    ]

@router.post("/verify", response_model=VerifyResponse)
async def verify_integrity():
    """ハッシュチェーンの整合性を検証"""
    audit = get_audit_manager()
    result = audit.verify_integrity()
    return VerifyResponse(
        is_valid=result.is_valid,
        total_count=result.total_count,
        errors=result.errors,
        message=str(result)
    )
