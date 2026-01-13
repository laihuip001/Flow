"""
Delayed Sync Manager (遅延同期マネージャー)
v5.0 Phase 4

オフライン時にリクエストをキューに登録し、後でまとめて処理する機能を提供します。

比喩: 郵便ポストに手紙を入れておき、集荷のタイミングでまとめて発送する仕組み。
"""
import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from .models import SyncJob
from .config import settings

logger = logging.getLogger("core_sync")

# 設定: 最大リトライ回数
MAX_RETRY_COUNT = 3


class SyncManager:
    """
    遅延同期のコアロジックを担当するクラス
    - enqueue: ジョブ登録
    - process_pending: 未処理ジョブの実行
    - get_result: 結果取得
    """

    def enqueue(self, db: Session, text: str, seasoning: int = 30) -> str:
        """
        新規ジョブをキューに登録する (CRUD: Create)
        
        Args:
            db: Database session
            text: 処理対象テキスト
            seasoning: 処理レベル (0-100)
        
        Returns:
            job_id: 登録されたジョブのID
        """
        job_id = str(uuid.uuid4())
        job = SyncJob(
            id=job_id,
            text=text,
            seasoning=seasoning,
            status="pending"
        )
        db.add(job)
        db.commit()
        logger.info(f"📥 Job Enqueued: {job_id[:8]}...")
        return job_id

    def get_pending_jobs(self, db: Session, limit: int = 10) -> List[SyncJob]:
        """
        未処理 (pending) のジョブを取得する
        
        Args:
            db: Database session
            limit: 取得上限
        
        Returns:
            List of SyncJob
        """
        return db.query(SyncJob).filter(
            SyncJob.status == "pending"
        ).order_by(SyncJob.created_at.asc()).limit(limit).all()

    def process_job(self, db: Session, job: SyncJob, processor) -> bool:
        """
        個別ジョブを処理する
        
        Args:
            db: Database session
            job: 処理対象ジョブ
            processor: CoreProcessor インスタンス (process メソッドを持つ)
        
        Returns:
            success: 成功なら True
        """
        # 1. 排他制御: status を processing に変更
        job.status = "processing"
        job.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"⚙️ Processing Job: {job.id[:8]}...")

        try:
            # 2. 処理実行
            result = processor.process_sync(job.text, job.seasoning)
            
            if result.get("success"):
                job.result = result.get("result")
                job.status = "completed"
                job.error_message = None
                logger.info(f"✅ Job Completed: {job.id[:8]}")
                db.commit()
                return True
            else:
                raise Exception(result.get("error", "Unknown error"))

        except Exception as e:
            job.retry_count += 1
            job.error_message = str(e)
            
            if job.retry_count >= MAX_RETRY_COUNT:
                job.status = "failed"
                logger.error(f"❌ Job Failed (Max Retry): {job.id[:8]} - {e}")
            else:
                job.status = "pending"  # 再試行可能
                logger.warning(f"⚠️ Job Retry ({job.retry_count}/{MAX_RETRY_COUNT}): {job.id[:8]} - {e}")
            
            db.commit()
            return False

    def process_pending(self, db: Session, processor, limit: int = 10) -> Dict[str, int]:
        """
        未処理ジョブをまとめて処理する (バッチ処理)
        
        Args:
            db: Database session
            processor: CoreProcessor インスタンス
            limit: 一度に処理する最大件数
        
        Returns:
            stats: { "processed": N, "failed": M }
        """
        stats = {"processed": 0, "failed": 0, "total": 0}
        
        jobs = self.get_pending_jobs(db, limit)
        stats["total"] = len(jobs)
        
        for job in jobs:
            success = self.process_job(db, job, processor)
            if success:
                stats["processed"] += 1
            else:
                stats["failed"] += 1
        
        logger.info(f"📊 Batch Complete: {stats}")
        return stats

    def get_result(self, db: Session, job_id: str) -> Optional[Dict[str, Any]]:
        """
        ジョブIDから結果を取得する (Polling用)
        
        Args:
            db: Database session
            job_id: ジョブID
        
        Returns:
            dict: { status, result, error_message, retry_count }
        """
        job = db.query(SyncJob).filter(SyncJob.id == job_id).first()
        
        if not job:
            return None
        
        return {
            "id": job.id,
            "status": job.status,
            "result": job.result,
            "error_message": job.error_message,
            "retry_count": job.retry_count,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None
        }
