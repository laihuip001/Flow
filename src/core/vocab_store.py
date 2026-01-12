"""
Vocabulary Store - カスタム機密語彙管理

FORBIDDEN依存: ChromaDB (ビルド失敗リスク)
代替実装: SQLite + FTS5 (全文検索)

責務:
- ユーザー定義の機密語彙の管理
- 部分一致検索
- privacy.py との統合
"""
import sqlite3
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# デフォルトDBパス
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "vocab.db"


class VocabularyStore:
    """
    カスタム機密語彙のストア
    
    SQLite FTS5を使用した軽量実装（ChromaDB代替）
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """データベース初期化"""
        with sqlite3.connect(self.db_path) as conn:
            # FTS5仮想テーブル（全文検索）
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS vocab 
                USING fts5(term, category, tokenize='unicode61')
            """)
            # メタデータテーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vocab_meta (
                    term TEXT PRIMARY KEY,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def add_term(self, term: str, category: str = "custom") -> bool:
        """
        機密語彙を追加
        
        Args:
            term: 機密語彙（例: "プロジェクトX"）
            category: カテゴリ（例: "project", "person", "custom"）
        
        Returns:
            成功時True
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 重複チェック
                existing = conn.execute(
                    "SELECT term FROM vocab_meta WHERE term = ?", (term,)
                ).fetchone()
                if existing:
                    logger.info(f"語彙 '{term}' は既に登録済み")
                    return False
                
                # FTSテーブルに追加
                conn.execute(
                    "INSERT INTO vocab(term, category) VALUES (?, ?)",
                    (term, category)
                )
                # メタデータテーブルに追加
                conn.execute(
                    "INSERT INTO vocab_meta(term, category) VALUES (?, ?)",
                    (term, category)
                )
                conn.commit()
                logger.info(f"語彙 '{term}' ({category}) を追加")
                return True
        except Exception as e:
            logger.error(f"語彙追加エラー: {e}")
            return False
    
    def remove_term(self, term: str) -> bool:
        """語彙を削除"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM vocab WHERE term = ?", (term,))
                conn.execute("DELETE FROM vocab_meta WHERE term = ?", (term,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"語彙削除エラー: {e}")
            return False
    
    def search(self, query: str, limit: int = 10) -> list[dict]:
        """
        部分一致検索
        
        Args:
            query: 検索クエリ
            limit: 最大結果数
        
        Returns:
            マッチした語彙のリスト
        """
        with sqlite3.connect(self.db_path) as conn:
            # FTS5検索（部分一致）
            results = conn.execute(
                """
                SELECT term, category FROM vocab 
                WHERE vocab MATCH ? 
                LIMIT ?
                """,
                (f'"{query}"*', limit)
            ).fetchall()
            return [{"term": r[0], "category": r[1]} for r in results]
    
    def find_in_text(self, text: str) -> list[str]:
        """
        テキスト内に含まれる登録語彙を検出
        
        Args:
            text: 検査対象テキスト
        
        Returns:
            検出された語彙のリスト
        """
        with sqlite3.connect(self.db_path) as conn:
            all_terms = conn.execute(
                "SELECT term FROM vocab_meta"
            ).fetchall()
            found = []
            for (term,) in all_terms:
                if term in text:
                    found.append(term)
            return found
    
    def list_all(self) -> list[dict]:
        """全語彙を取得"""
        with sqlite3.connect(self.db_path) as conn:
            results = conn.execute(
                "SELECT term, category, created_at FROM vocab_meta ORDER BY created_at DESC"
            ).fetchall()
            return [
                {"term": r[0], "category": r[1], "created_at": r[2]} 
                for r in results
            ]
    
    def count(self) -> int:
        """登録語彙数を取得"""
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT COUNT(*) FROM vocab_meta").fetchone()[0]


# シングルトンインスタンス
_store: Optional[VocabularyStore] = None

def get_vocab_store() -> VocabularyStore:
    """語彙ストアのシングルトン取得"""
    global _store
    if _store is None:
        _store = VocabularyStore()
    return _store
