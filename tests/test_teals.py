import sys
import os
import unittest
from datetime import datetime, timezone
from sqlalchemy.orm import sessionmaker

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from infra.teals.models import init_db, AuditLog
from infra.teals.log_manager import add_log, GENESIS_HASH
from infra.teals.verifier import verify_all

class TestTEALS(unittest.TestCase):
    def setUp(self):
        """インメモリDBでテスト環境を構築"""
        self.engine, self.Session = init_db(":memory:")
        self.session = self.Session()

    def tearDown(self):
        self.session.close()

    def test_log_chain_integrity_valid(self):
        """正常なハッシュチェーンの検証"""
        # 1. ログを追加
        log1 = add_log(self.session, "user1", "create", "docs", {"id": 1})
        log2 = add_log(self.session, "user1", "update", "docs", {"id": 1, "v": 1}, {"id": 1, "v": 2})

        # 2. 検証実行
        result = verify_all(self.session)

        # 3. アサーション
        self.assertTrue(result.is_valid)
        self.assertEqual(result.total_count, 2)
        self.assertEqual(len(result.errors), 0)
        
        # ハッシュリンクの確認
        self.assertEqual(log1.previous_hash, GENESIS_HASH)
        self.assertEqual(log2.previous_hash, log1.current_hash)

    def test_tamper_detection_previous_hash(self):
        """previous_hash改ざんの検知"""
        # 1. ログを追加
        log1 = add_log(self.session, "user1", "login", "auth")
        log2 = add_log(self.session, "user1", "logout", "auth")

        # 2. 改ざん: log2のリンクを切る
        log2.previous_hash = "0" * 64
        self.session.commit()

        # 3. 検証実行
        result = verify_all(self.session)

        # 4. アサーション
        self.assertFalse(result.is_valid)
        self.assertIn("previous_hashの不整合", str(result.errors[0]))
        # current_hashも再計算すると合わなくなるため両方出る可能性があるが
        # verify_allの実装順序によっては片方だけかも。実装を確認すると両方出るはず。

    def test_tamper_detection_data_modification(self):
        """データ改ざん（current_hash不整合）の検知"""
        # 1. ログを追加
        log1 = add_log(self.session, "user1", "payment", "sales", {"amount": 100})
        
        # 2. 改ざん: 金額を書き換え
        log1.before_data = '{"amount": 10000}' # JSON文字列として保存されている
        self.session.commit()

        # 3. 検証実行
        result = verify_all(self.session)

        # 4. アサーション
        self.assertFalse(result.is_valid)
        self.assertTrue(any("current_hashの不整合" in err for err in result.errors))

if __name__ == '__main__':
    unittest.main()
