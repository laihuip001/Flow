"""
Unit Tests for Sync Module (遅延同期)
v5.0 Phase 4
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.models import Base, SyncJob
from src.core.sync import SyncManager, MAX_RETRY_COUNT


class TestSyncManager(unittest.TestCase):
    def setUp(self):
        # In-memory DB
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()
        self.mgr = SyncManager()

    def tearDown(self):
        self.db.close()

    def test_enqueue(self):
        """enqueue: ジョブが pending で登録されること"""
        job_id = self.mgr.enqueue(self.db, "test text", 50)
        
        self.assertIsNotNone(job_id)
        
        job = self.db.query(SyncJob).filter_by(id=job_id).first()
        self.assertIsNotNone(job)
        self.assertEqual(job.status, "pending")
        self.assertEqual(job.text, "test text")
        self.assertEqual(job.seasoning, 50)

    def test_get_pending_jobs(self):
        """get_pending_jobs: pending ジョブのみ取得されること"""
        # 3件登録
        self.mgr.enqueue(self.db, "pending1", 30)
        self.mgr.enqueue(self.db, "pending2", 30)
        
        # 1件を completed に変更
        job = self.db.query(SyncJob).first()
        job.status = "completed"
        self.db.commit()
        
        pending = self.mgr.get_pending_jobs(self.db)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].status, "pending")

    def test_process_job_success(self):
        """process_job: 成功時に completed になること"""
        job_id = self.mgr.enqueue(self.db, "success text", 30)
        job = self.db.query(SyncJob).filter_by(id=job_id).first()
        
        # Mock processor
        mock_processor = Mock()
        mock_processor.process_sync.return_value = {"success": True, "result": "processed result"}
        
        success = self.mgr.process_job(self.db, job, mock_processor)
        
        self.assertTrue(success)
        self.assertEqual(job.status, "completed")
        self.assertEqual(job.result, "processed result")

    def test_process_job_failure_retry(self):
        """process_job: 失敗時にリトライカウント増加、pendingに戻ること"""
        job_id = self.mgr.enqueue(self.db, "fail text", 30)
        job = self.db.query(SyncJob).filter_by(id=job_id).first()
        
        # Mock processor
        mock_processor = Mock()
        mock_processor.process_sync.return_value = {"success": False, "error": "API error"}
        
        success = self.mgr.process_job(self.db, job, mock_processor)
        
        self.assertFalse(success)
        self.assertEqual(job.status, "pending")  # リトライ可能
        self.assertEqual(job.retry_count, 1)
        self.assertEqual(job.error_message, "API error")

    def test_process_job_max_retry(self):
        """process_job: 最大リトライ後に failed になること"""
        job_id = self.mgr.enqueue(self.db, "fail text", 30)
        job = self.db.query(SyncJob).filter_by(id=job_id).first()
        job.retry_count = MAX_RETRY_COUNT - 1  # あと1回で上限
        self.db.commit()
        
        # Mock processor
        mock_processor = Mock()
        mock_processor.process_sync.return_value = {"success": False, "error": "Final error"}
        
        success = self.mgr.process_job(self.db, job, mock_processor)
        
        self.assertFalse(success)
        self.assertEqual(job.status, "failed")
        self.assertEqual(job.retry_count, MAX_RETRY_COUNT)

    def test_get_result(self):
        """get_result: ジョブIDから結果を取得できること"""
        job_id = self.mgr.enqueue(self.db, "result text", 30)
        
        # 完了にする
        job = self.db.query(SyncJob).filter_by(id=job_id).first()
        job.status = "completed"
        job.result = "final result"
        self.db.commit()
        
        result = self.mgr.get_result(self.db, job_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["result"], "final result")

    def test_get_result_not_found(self):
        """get_result: 存在しないジョブIDでNoneが返ること"""
        result = self.mgr.get_result(self.db, "nonexistent-id")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
