#!/usr/bin/env python3
"""
AI Clipboard Pro v3.3 Titanium Edition - Genesis Installer (Integrated)
v3.1(Zero-Friction), v3.2(Fortified), v3.3(Titanium) の全機能を統合。
Refactored for robustness, type safety, and modern Python standards (3.10+).
"""

import logging
import os
import sys
from pathlib import Path
from typing import Final

# --- Configuration Registry ---
FILE_REGISTRY: Final[dict[str, str]] = {
    ".ai/SYSTEM_CONTEXT.md": """
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
    """.strip(),

    ".ai/JULES_TASK.md": """
# Implementation Plan: [Task Name]

## 1. Context
- Target Files: `src/...`
- Goal: ...

## 2. Spec / Pseudo Code
- [ ] Step 1: Implement logic
- [ ] Step 2: Add tests

## 3. Strict Rules
- No hardcoded secrets.
- Check Termux compatibility (No native build deps).
    """.strip(),

    ".ai/DEBUG_LOG.md": """
# Debug Log: [Error Summary]

## 1. Raw Error Log
```text
Paste traceback here
```

## 2. Attempted Fixes
1. ...

## 3. Current File Context
...
    """.strip(),

    "maintenance/titanium_watcher.sh": """
#!/bin/bash
# 役割: 自動Pull, 依存関係解消, ヘルスチェック連動型クラッシュループ防止

BRANCH="main"
INTERVAL=60
CRASH_COUNT=0
MAX_RETRIES=5

echo "🛡️ Titanium Watcher Started..."

while true; do
    git fetch origin $BRANCH
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/$BRANCH)

    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "⬇️ Update detected. Initiating strict deployment..."
        if [ -n "$(git status --porcelain)" ]; then
            git stash push -u -m "backup_$(date +%s)"
        fi
        git reset --hard origin/$BRANCH
        
        if git diff --name-only HEAD@{1} HEAD | grep -q "requirements.txt"; then
            pip install -r requirements.txt || echo "⚠️ Dependency install failed!"
        fi
        pkill -f "uvicorn main:app"
    fi

    if ! pgrep -f "uvicorn main:app" > /dev/null || ! curl -sSf http://localhost:8000/healthz > /dev/null; then
        if [ $CRASH_COUNT -ge $MAX_RETRIES ]; then
            echo "🚨 PANIC: Crash loop detected. Stopping."
            exit 1
        fi
        echo "♻️ Starting Application (Attempt: $((CRASH_COUNT+1)))..."
        if [ -f app.log ] && [ $(wc -c < app.log) -gt 10000000 ]; then 
            mv app.log app.log.old
        fi
        nohup uvicorn main:app --host 0.0.0.0 --port 8000 >> app.log 2>&1 &
        sleep 10
        if ! curl -sSf http://localhost:8000/healthz > /dev/null; then
            CRASH_COUNT=$((CRASH_COUNT+1))
        else
            CRASH_COUNT=0
        fi
    fi
    sleep $INTERVAL
done
    """.strip(),

    "dev_tools/secure_push.sh": """
#!/bin/bash
echo "🔒 Scanning for secrets..."
if grep -rE "sk-ant-[a-zA-Z0-9-*]+|AIza[0-9A-Za-z-*]{35}|sk-[a-zA-Z0-9]{40}" . --exclude-dir=venv --exclude-dir=.git --exclude=.env --exclude="*.pem"; then
    echo "❌ SECURITY ALERT: API Key found!"
    exit 1
fi
echo "✅ No secrets found."
git push origin main
    """.strip(),

    "dev_tools/sync.sh": """
#!/bin/bash
if [ "$1" == "start" ]; then
    echo "🌅 Starting Session..."
    git pull origin main
elif [ "$1" == "end" ]; then
    echo "🌇 Ending Session..."
    python -m compileall . -q && git add . && git commit -m "wip: autosave $(date +%s)" && ./dev_tools/secure_push.sh
else
    echo "Usage: ./dev_tools/sync.sh [start|end]"
fi
    """.strip(),

    ".env.example": "GEMINI_API_KEY=\nAPI_TOKEN=\nCUSTOM_PII_KEYWORDS=\nPROMPT_LIB_DIR=",
    
    "SETUP_GUIDE_TITANIUM.md": """
# 🛡️ v3.3 Titanium Setup Guide

## 1. Initialize
1. `cp .env.example .env` & Set API Keys.
2. `pip install -r requirements.txt`

## 2. Dev Routine (PC/Cloud)
* Start work: `./dev_tools/sync.sh start`
* End work: `./dev_tools/sync.sh end`

## 3. Termux Runtime
* **Phantom Process Killer Disable (PC connected):**
  `adb shell device_config put activity_manager max_phantom_processes 2147483647`
* **Start Watcher:**
  `chmod +x maintenance/titanium_watcher.sh`
  `./maintenance/titanium_watcher.sh &`

## 4. AI Agent Context
* Open `.ai/SYSTEM_CONTEXT.md` in Antigravity
* Instruct agent: "Read @SYSTEM_CONTEXT.md and remember the constraints"
    """.strip(),
}


class TitaniumBootstrapper:
    """Genesis installer for Titanium Edition"""
    
    def __init__(self, force: bool = False) -> None:
        self.force = force
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    def create_file(self, target_path: str, content: str) -> None:
        path = Path(target_path)
        try:
            if path.exists() and not self.force:
                logging.warning(f"Skipping existing file: {path}")
                return
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            logging.info(f"Created: {path}")
        except Exception as e:
            logging.error(f"Failed {path}: {e}")

    def make_executable(self, target_path: str) -> None:
        path = Path(target_path)
        if os.name == 'posix' and path.exists():
            path.chmod(path.stat().st_mode | 0o111)
            logging.info(f"Executable: {path}")

    def run(self) -> None:
        logging.info("🏗️  Initializing v3.3 Titanium Integrated Architecture...")
        for file_path, content in FILE_REGISTRY.items():
            self.create_file(file_path, content)
            if file_path.endswith(".sh"):
                self.make_executable(file_path)
        logging.info("\n🎉 Titanium Genesis Complete.")
        logging.info("Next: Read SETUP_GUIDE_TITANIUM.md")


if __name__ == "__main__":
    TitaniumBootstrapper(force="--force" in sys.argv).run()
