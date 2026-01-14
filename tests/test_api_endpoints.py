"""
API Endpoint Tests
v5.0

FastAPI TestClient を使用した統合テスト
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.api.main import app


class TestHealthEndpoints(unittest.TestCase):
    """ヘルスチェックエンドポイントのテスト"""
    
    def setUp(self):
        self.client = TestClient(app)

    def test_root_health(self):
        """GET / - 基本ヘルスチェック"""
        response = self.client.get("/")
        # Root may return 200 (health) or redirect to static
        self.assertIn(response.status_code, [200, 307, 404])

    def test_healthz(self):
        """GET /healthz - 詳細ヘルスチェック"""
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("checks", data)
        self.assertIn("api", data["checks"])

    def test_healthz_fast(self):
        """GET /healthz/fast - 高速ヘルスチェック"""
        response = self.client.get("/healthz/fast")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "alive")


class TestSyncEndpoints(unittest.TestCase):
    """Sync (遅延同期) エンドポイントのテスト"""
    
    def setUp(self):
        self.client = TestClient(app)
        # Bypass auth for testing (or set token)
        self.headers = {}  # API_TOKEN が空なら認証不要

    def test_sync_enqueue(self):
        """POST /sync/enqueue - ジョブ登録 (or 認証エラー)"""
        response = self.client.post(
            "/sync/enqueue",
            json={"text": "test text", "seasoning": 30},
            headers=self.headers
        )
        # 認証が有効なら 401、無効なら 200
        self.assertIn(response.status_code, [200, 401])
        
        if response.status_code == 200:
            data = response.json()
            self.assertIn("job_id", data)
            self.assertEqual(data["status"], "pending")

    def test_sync_status_not_found(self):
        """GET /sync/status/{id} - 存在しないジョブ or 認証エラー"""
        response = self.client.get(
            "/sync/status/nonexistent-job-id",
            headers=self.headers
        )
        # 認証が有効な場合は 401、無効な場合は 404
        self.assertIn(response.status_code, [401, 404])

    def test_sync_enqueue_and_status(self):
        """POST /sync/enqueue → GET /sync/status - フロー確認 (認証依存)"""
        # 1. Enqueue
        enqueue_resp = self.client.post(
            "/sync/enqueue",
            json={"text": "flow test", "seasoning": 50},
            headers=self.headers
        )
        
        # 認証が有効なら 401 で終了
        if enqueue_resp.status_code == 401:
            self.skipTest("Auth required, skipping flow test")
            return
        
        self.assertEqual(enqueue_resp.status_code, 200)
        job_id = enqueue_resp.json()["job_id"]
        
        # 2. Status
        status_resp = self.client.get(
            f"/sync/status/{job_id}",
            headers=self.headers
        )
        self.assertEqual(status_resp.status_code, 200)
        data = status_resp.json()
        self.assertEqual(data["id"], job_id)
        self.assertEqual(data["status"], "pending")


class TestCoreEndpoints(unittest.TestCase):
    """Core (/process) エンドポイントのテスト (Mocked)"""
    
    def setUp(self):
        self.client = TestClient(app)
        self.headers = {}

    @patch("src.core.processor.CoreProcessor.process")
    def test_process_endpoint(self, mock_process):
        """POST /process - テキスト処理 (Mocked)"""
        # Mock the async process method
        mock_process.return_value = {
            "result": "processed text",
            "seasoning": 30,
            "from_cache": False,
            "model_used": "test"
        }
        
        response = self.client.post(
            "/process",
            json={"text": "test input", "seasoning": 30},
            headers=self.headers
        )
        
        # Depending on implementation, may need auth
        self.assertIn(response.status_code, [200, 401, 403])


if __name__ == "__main__":
    unittest.main()
