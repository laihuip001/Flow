"""
TEALS - ログ追加ロジック
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Optional
from .models import AuditLog

GENESIS_HASH = "0" * 64


def calculate_hash(
    timestamp: datetime,
    user_id: str,
    action_type: str,
    target_table: str,
    before_data: Optional[str],
    after_data: Optional[str],
    previous_hash: str,
    ai_model: Optional[str] = None
) -> str:
    """ハッシュ値を計算"""
    # Normalize timestamp to naive UTC for consistent hashing
    # (SQLite doesn't preserve timezone, so we must always use naive representation)
    if timestamp.tzinfo is not None:
        # Convert to UTC and strip timezone
        timestamp = timestamp.replace(tzinfo=None)
    timestamp_str = timestamp.isoformat()
    before_str = before_data if before_data else ""
    after_str = after_data if after_data else ""
    ai_model_str = ai_model if ai_model else ""
    
    data = (
        timestamp_str + user_id + action_type + target_table +
        ai_model_str + before_str + after_str + previous_hash
    )
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def add_log(
    session,
    user_id: str,
    action_type: str,
    target_table: str,
    before_data: Optional[dict] = None,
    after_data: Optional[dict] = None,
    timestamp: Optional[datetime] = None,
    ai_model: Optional[str] = None
) -> AuditLog:
    """監査ログを追加"""
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    
    last_log = session.query(AuditLog).order_by(AuditLog.id.desc()).first()
    previous_hash = last_log.current_hash if last_log else GENESIS_HASH
    
    before_json = json.dumps(before_data, ensure_ascii=False, sort_keys=True) if before_data else None
    after_json = json.dumps(after_data, ensure_ascii=False, sort_keys=True) if after_data else None
    
    current_hash = calculate_hash(
        timestamp=timestamp,
        user_id=user_id,
        action_type=action_type,
        target_table=target_table,
        before_data=before_json,
        after_data=after_json,
        previous_hash=previous_hash,
        ai_model=ai_model
    )
    
    log = AuditLog(
        timestamp=timestamp,
        user_id=user_id,
        action_type=action_type,
        target_table=target_table,
        ai_model=ai_model,
        before_data=before_json,
        after_data=after_json,
        previous_hash=previous_hash,
        current_hash=current_hash
    )
    
    session.add(log)
    session.commit()
    return log
