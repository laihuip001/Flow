import pytest
import os
import shutil
import tempfile
from pathlib import Path
from src.infra.audit import AuditManager

# Test fixture for isolated database
@pytest.fixture
def audit_manager():
    # Create a temporary directory for the test DB
    tmpdir = tempfile.mkdtemp()
    db_path = str(Path(tmpdir) / "test_audit.db")
    manager = AuditManager(db_path=db_path)
    
    yield manager
    
    # Explicitly dispose engine to release file lock for Windows
    manager.engine.dispose()
    
    # Cleanup
    try:
        shutil.rmtree(tmpdir)
    except Exception as e:
        print(f"Warning: Failed to cleanup temp dir: {e}")

def test_log_processing(audit_manager):
    """ログ記録の正常系テスト"""
    # ログ記録
    audit_manager.log_processing(
        user_id="test_user",
        input_text="テスト入力",
        output_text="テスト出力",
        seasoning=50,
        ai_model="gemini-3-pro",
        processing_time_ms=123
    )
    
    # 最新のログを取得 (DetachedInstanceError回避のため、戻り値のオブジェクトは使わずDBから引き直す)
    logs = audit_manager.get_logs(limit=1)
    assert len(logs) == 1
    saved_log = logs[0]
    
    assert saved_log is not None
    assert saved_log.user_id == "test_user"
    assert saved_log.current_hash is not None
    assert len(saved_log.current_hash) == 64

def test_hash_chain_integrity(audit_manager):
    """ハッシュチェーンの整合性テスト"""
    # 3件のログを追加
    for i in range(3):
        audit_manager.log_processing(
            user_id=f"user_{i}",
            input_text=f"input_{i}",
            output_text=f"output_{i}",
            seasoning=i * 30
        )
    
    # 検証
    result = audit_manager.verify_integrity()
    assert result.is_valid is True
    assert result.total_count == 3
    assert len(result.errors) == 0

def test_tamper_detection(audit_manager):
    """改ざん検知テスト"""
    # ログを追加
    audit_manager.log_processing(
        user_id="victim",
        input_text="original",
        output_text="original",
        seasoning=50
    )
    # 最新ログID取得
    logs = audit_manager.get_logs(limit=1)
    log_id = logs[0].id

    # 直接DBを改ざん (SQLAlchemy経由で無理やり更新)
    session = audit_manager.Session()
    try:
        from src.infra.teals.models import AuditLog
        session.query(AuditLog).filter(AuditLog.id == log_id).update({"user_id": "hacker"})
        session.commit()
    finally:
        session.close()
    
    # 検証 -> 失敗するはず
    result = audit_manager.verify_integrity()
    assert result.is_valid is False
    assert len(result.errors) > 0
    assert "current_hashの不整合" in result.errors[0] or "ハッシュ値が不正" in str(result.errors)
