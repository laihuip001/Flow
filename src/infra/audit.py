"""
Flow-TEALS Integration: Audit Logging Module

AI処理結果を改ざん検知可能な監査ログに記録する。
"""

from datetime import datetime, timezone
from typing import Optional, List
from pathlib import Path

# TEALS package imports (local copy)
from src.infra.teals.models import init_db, AuditLog
from src.infra.teals.log_manager import add_log
from src.infra.teals.verifier import verify_all, VerificationResult

# ---

# Database path (Separate from Flow main DB)
AUDIT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "audit_log.db"


class AuditManager:
    """Flow監査ログマネージャー"""
    
    def __init__(self, db_path: str = str(AUDIT_DB_PATH)):
        self.db_path = db_path
        # C-2: Explicit init to ensure table creation
        self.engine, self.Session = init_db(db_path)
    
    def log_processing(
        self,
        user_id: str,
        input_text: str,
        output_text: str,
        seasoning: int,
        ai_model: str = "gemini-3-pro",
        processing_time_ms: Optional[int] = None
    ) -> AuditLog:
        """
        AI処理結果を監査ログに記録
        
        Args:
            user_id: 操作者ID (API Token等から特定)
            input_text: 入力テキスト (PII masked recommended)
            output_text: 出力テキスト
            seasoning: Seasoning値 (0-100)
            ai_model: 使用AIモデル
            processing_time_ms: 処理時間(ms)
        
        Returns:
            作成されたAuditLogオブジェクト
        """
        session = self.Session()
        try:
            log = add_log(
                session=session,
                user_id=user_id,
                action_type="AI_PROCESS",
                target_table="flow_requests",
                before_data={
                    "input": input_text,
                    "seasoning": seasoning,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                after_data={
                    "output": output_text,
                    "processing_time_ms": processing_time_ms
                },
                ai_model=ai_model
            )
            # Detach from session so object remains usable after close
            session.expunge(log)
            return log
        except Exception as e:
            # M-1: Log failure but raise (caller decides functionality fallback)
            # In production, this might write to a fallback file
            print(f"Audit log failure: {e}")
            raise
        finally:
            session.close()
    
    def verify_integrity(self) -> VerificationResult:
        """
        監査ログのハッシュチェーン整合性を検証
        
        Returns:
            VerificationResult: 検証結果
        """
        session = self.Session()
        try:
            return verify_all(session)
        finally:
            session.close()
    
    def get_logs(self, limit: int = 100, offset: int = 0) -> List[AuditLog]:
        """監査ログ一覧を取得"""
        session = self.Session()
        try:
            logs = session.query(AuditLog)\
                .order_by(AuditLog.id.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()
            # Start Detach: Make objects usable after session close
            session.expunge_all()
            return logs
        finally:
            session.close()
    
    def get_log_by_id(self, log_id: int) -> Optional[AuditLog]:
        """特定の監査ログを取得"""
        session = self.Session()
        try:
            log = session.query(AuditLog)\
                .filter(AuditLog.id == log_id)\
                .first()
            if log:
                session.expunge(log)
            return log
        finally:
            session.close()


# Singleton instance
_audit_manager: Optional[AuditManager] = None


def get_audit_manager() -> AuditManager:
    """AuditManager Singleton取得"""
    global _audit_manager
    if _audit_manager is None:
        _audit_manager = AuditManager()
    return _audit_manager
