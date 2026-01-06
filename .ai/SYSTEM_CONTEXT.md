# SYSTEM CONTEXT: AI Clipboard Pro v3.3 (Termux Edition)

## 1. 🌍 Runtime Environment Constraints (CRITICAL)
- **Target OS:** Android Termux (aarch64 / Linux)
- **Performance:** Low Memory, Battery constraint.
- **Library Restrictions:**
  - ❌ **BAN:** `pandas`, `numpy`, `scipy`, `tensorflow`, `playwright`, `selenium`
  - ✅ **USE:** `sqlite3`, `httpx`, `beautifulsoup4`, `uvicorn`, `fastapi`, `requests`
- **Strict Rule:** 新規ライブラリ追加時は、必ず「Termuxでビルド不要か（Pure Pythonか）」を確認せよ。

## 2. 🛡️ Security Protocols
- **Secrets:** APIキーやトークンは**絶対にコード内にハードコードしない**こと。
- **Env Vars:** すべての機密情報は `config.py` 経由で `os.environ` または `.env` から読み込むこと。
- **PII Policy:** 個人情報は「自動置換」ではなく「検知と警告」に留める。

## 3. 💾 Database Strategy
- **ORM:** SQLAlchemyを使用。
- **Migration:** モデル変更時は `alembic` を使用すること。
- **WAL Mode:** SQLiteはWALモードで運用。
