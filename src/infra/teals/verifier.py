"""
TEALS - 検証ロジック
"""

from typing import List, Tuple
from .models import AuditLog
from .log_manager import calculate_hash, GENESIS_HASH


class VerificationResult:
    """検証結果"""
    def __init__(self, is_valid: bool, total_count: int, errors: List[str]):
        self.is_valid = is_valid
        self.total_count = total_count
        self.errors = errors
    
    def __str__(self):
        if self.is_valid:
            return f"[OK] 検証完了: {self.total_count}件のログが正常です"
        return f"[NG] 改ざん検出！ エラー: {len(self.errors)}件"


def verify_all(session) -> VerificationResult:
    """全レコードのハッシュ整合性チェック"""
    logs = session.query(AuditLog).order_by(AuditLog.id.asc()).all()
    
    if not logs:
        return VerificationResult(True, 0, [])
    
    errors = []
    expected_previous_hash = GENESIS_HASH
    
    for log in logs:
        if log.previous_hash != expected_previous_hash:
            errors.append(f"ID={log.id}: previous_hashの不整合")
        
        recalculated_hash = calculate_hash(
            timestamp=log.timestamp,
            user_id=log.user_id,
            action_type=log.action_type,
            target_table=log.target_table,
            before_data=log.before_data,
            after_data=log.after_data,
            previous_hash=log.previous_hash,
            ai_model=log.ai_model
        )
        
        if log.current_hash != recalculated_hash:
            errors.append(f"ID={log.id}: current_hashの不整合（データが改ざんされた可能性）")
        
        expected_previous_hash = log.current_hash
    
    return VerificationResult(len(errors) == 0, len(logs), errors)
