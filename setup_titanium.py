#!/usr/bin/env python3
"""
Flow AI v4.0 - Titanium Recovery Script
========================================

このスクリプトは、Android Termux または新しいPC環境で
Flow AI を5分以内に復旧するための自動化スクリプトです。

使用方法:
    python setup_titanium.py

機能:
    1. 必要なディレクトリの作成
    2. 依存関係のインストール
    3. .env ファイルのテンプレート作成
    4. データベースの初期化
    5. ヘルスチェック

冪等性: このスクリプトは何度実行しても安全です。
"""

import os
import sys
import subprocess
from pathlib import Path

# ========================================
# Configuration
# ========================================
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
ENV_FILE = PROJECT_ROOT / ".env"
ENV_EXAMPLE = PROJECT_ROOT / ".env.example"

DEPENDENCIES = [
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "google-generativeai>=0.3.0",
    "python-dotenv>=1.0.0",
    "sqlalchemy>=2.0.0",
    "requests>=2.28.0",
]

# PC専用 (Termuxではスキップ)
PC_ONLY_DEPS = [
    "flet>=0.21.0",
    "pyperclip>=1.8.0",
    "keyboard>=0.13.5",
]

# ========================================
# Helpers
# ========================================
def is_termux() -> bool:
    """Termux環境かどうかを判定"""
    return "com.termux" in os.environ.get("PREFIX", "")

def log(msg: str, level: str = "INFO"):
    icons = {"INFO": "📦", "OK": "✅", "WARN": "⚠️", "ERROR": "❌"}
    print(f"{icons.get(level, '📦')} [{level}] {msg}")

def run_cmd(cmd: list[str], check: bool = True) -> bool:
    """コマンド実行"""
    try:
        subprocess.run(cmd, check=check, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        log(f"Command failed: {' '.join(cmd)}", "ERROR")
        log(f"  stderr: {e.stderr[:200]}", "ERROR")
        return False

# ========================================
# Setup Steps
# ========================================
def step_1_directories():
    """Step 1: 必要なディレクトリを作成"""
    log("Creating directories...")
    DATA_DIR.mkdir(exist_ok=True)
    (PROJECT_ROOT / ".ai").mkdir(exist_ok=True)
    (PROJECT_ROOT / "docs").mkdir(exist_ok=True)
    log("Directories ready", "OK")

def step_2_dependencies():
    """Step 2: 依存関係のインストール"""
    log("Installing dependencies...")
    
    deps = DEPENDENCIES.copy()
    if not is_termux():
        deps.extend(PC_ONLY_DEPS)
        log("PC environment detected, including GUI dependencies")
    else:
        log("Termux detected, skipping GUI dependencies", "WARN")
    
    for dep in deps:
        log(f"  Installing {dep}...")
        if not run_cmd([sys.executable, "-m", "pip", "install", "-q", dep], check=False):
            log(f"  Failed to install {dep}", "WARN")
    
    log("Dependencies installed", "OK")

def step_3_env_file():
    """Step 3: .env ファイルの確認/作成"""
    log("Checking .env file...")
    
    if ENV_FILE.exists():
        log(".env already exists, skipping", "OK")
        return
    
    if ENV_EXAMPLE.exists():
        import shutil
        shutil.copy(ENV_EXAMPLE, ENV_FILE)
        log(".env created from .env.example", "OK")
        log("⚠️  Please edit .env and add your GEMINI_API_KEY!", "WARN")
    else:
        # 最小限の.envを作成
        ENV_FILE.write_text("""# Flow AI Configuration
GEMINI_API_KEY=YOUR_API_KEY_HERE
API_TOKEN=
""")
        log(".env created with template", "OK")
        log("⚠️  Please edit .env and add your GEMINI_API_KEY!", "WARN")

def step_4_database():
    """Step 4: データベースの初期化"""
    log("Initializing database...")
    try:
        from src.infra.database import init_db
        init_db()
        log("Database initialized", "OK")
    except Exception as e:
        log(f"Database init failed: {e}", "ERROR")

def step_5_healthcheck():
    """Step 5: ヘルスチェック"""
    log("Running health check...")
    
    checks = {"python": False, "imports": False, "api_key": False}
    
    # Python version
    checks["python"] = sys.version_info >= (3, 10)
    log(f"  Python {sys.version_info.major}.{sys.version_info.minor}", 
        "OK" if checks["python"] else "WARN")
    
    # Core imports
    try:
        from src.core.config import settings
        from src.core.processor import CoreProcessor
        checks["imports"] = True
        log("  Core imports", "OK")
    except ImportError as e:
        log(f"  Core imports failed: {e}", "ERROR")
    
    # API key
    try:
        from src.core.config import settings
        checks["api_key"] = bool(settings.GEMINI_API_KEY)
        log(f"  API Key configured", "OK" if checks["api_key"] else "WARN")
    except:
        pass
    
    return all(checks.values())

# ========================================
# Main
# ========================================
def main():
    print("=" * 50)
    print("🛡️  Flow AI v4.0 - Titanium Recovery")
    print("=" * 50)
    print()
    
    step_1_directories()
    step_2_dependencies()
    step_3_env_file()
    step_4_database()
    
    print()
    print("-" * 50)
    all_ok = step_5_healthcheck()
    print("-" * 50)
    print()
    
    if all_ok:
        print("🎉 Setup complete! Run:")
        print("   python run_server.py  # API Server")
        if not is_termux():
            print("   python run_app.py     # Desktop App (PC only)")
    else:
        print("⚠️  Setup completed with warnings.")
        print("   Please check the errors above and fix .env file.")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
