# Titanium Constitution (Development Norms)

This document defines the **"Not To Do"** list (Anti-patterns) for the AI-Clipboard-Pro project.
Violating these rules implies a breach of trust as a professional engineer.

Based on internal audits and external standards (OWASP Top 10 for LLM, Python Anti-patterns).

## 🚫 1. Zero Trust Privacy & AI Security (OWASP LLM)

- **NEVER** commit personal information, specific mental health records, or sensitive personal context files (e.g., `ANTIGRAVITY_CONTEXT.md`).
- **NEVER** leave API Keys hardcoded. Always use `.env`.
- **NEVER** Implement security features (like `mask_pii`) without integrating them into the actual data flow. "Implemented but unused" is a security hole.
- **NEVER** Ignore Prompt Injection risks. Treat all user input as untrusted before sending to LLM.
- **NEVER** Allow "Sensitive Information Disclosure" by sending unmasked PII to external APIs (OWASP LLM06).

## 🚫 2. Code Hygiene & Python Best Practices

- **NEVER** leave unused imports (`F401`) or wildcard imports (`from module import *`). Explicit is better than implicit.
- **NEVER** silence exceptions with `except Exception: pass`. Always log the error or return a structured error response.
- **NEVER** use mutable default arguments (e.g., `def func(list=[])`).
- **NEVER** allow "God Objects" or Monolithic functions (> 500 lines). Break them down (Modular Monolith).
- **NEVER** leave legacy code in the root directory. Migrate to `_archive/` or delete immediately.
- **NEVER** duplicate entire libraries (DRY principle).

## 🚫 3. Professional Integrity & Architecture

- **NEVER** make performance claims (e.g., "90s -> 5s") without a reproducible benchmark script (`tests/benchmark_latency.py`).
- **NEVER** leave documentation that contradicts the code. Update `README.md` and `ARCHITECTURE.md` synchronously.
- **NEVER** engaging in "Cargo Culting" (e.g., microservices for a small app). Keep architecture simple and justified.
- **NEVER** bloat the root directory. Keep high-level structure clean (< 15 files).

## ⚡ 4. Titanium Operational Protocols (Execution Prime)

These settings are MANDATORY for maximizing productivity (3x) and minimizing risks (0%).

### 4.1. MCP (Model Context Protocol) Setup

- **GitHub MCP (Required):** Enable for Issue reading & PR creation.
- **Google Search / Documentation MCP (Required):** Enable for fetching latest SDK docs.

### 4.2. Environment Optimization (.antigravityignore)

- **Context Hygiene:** Exclude `venv/`, `__pycache__/`, and `.git/` to prevent token waste and hallucination from "garbage data".
- **Action:** Created `.antigravityignore` (mirrors `.gitignore` + `venv/`).

### 4.3. Remote-First UI Settings (Tablet Optimized)

- **Auto Save (ON):** Prevent data loss on disconnect.
- **Sidebar (RIGHT):** Reduce eye strain (Design on Right, Code on Left).
- **Font Size (+):** Ensure visibility on tablet screens.

### 4.4. Titanium Debug Automation

- **Terminal Output Analysis (ON):** AI automatically detects and suggests fixes for errors.
- **Pre-commit Rules:** "Check types/lint before save" (See `.gemini/rules.md`).

## ⚡ 5. Titanium Deep Customization (Optional but Recommended)

Pro-level tuning for zero-friction development.

### 5.1. Quality Automation (Extensions)

- **Ruff:** Automatic linting/formatting. "Red squiggles" = Immediate fix required.
- **GitLens:** Blame line-by-line. Prevent "Black Box" code generation.

### 5.2. Operational Aliases (PowerShell)

- `watcher` -> `./maintenance/titanium_watcher.sh`
- `push` -> `./dev_tools/secure_push.sh`
- `sync` -> `./dev_tools/sync.sh`
- **Action:** Run `dev_tools/setup_aliases.ps1`.

### 5.3. Cost & Auth Guardrails

- **Git Credential Manager:** Enable for password-less push.
- **GCP Shutdown:** Schedule daily stop (e.g., 04:00 AM JST) to prevent cost overrun.

---
*Enforced by Titanium Red Team Audit & Self-Correction protocols*

---

## ✅ 6. Coding Style Standards (コーディング規約)

このセクションでは「やるべきこと」を定義する。全コードはこの規約に準拠すること。

### 6.1. File Structure (ファイル構造)

```
# 標準的なPythonファイル構造
"""
Module Name - One-line description

詳細説明（必要な場合のみ）
"""
# 1. Standard Library Imports
import os
import sys

# 2. Third-party Imports
from fastapi import FastAPI

# 3. Local Imports
from src.core.config import settings

# 4. Constants
MAX_RETRIES = 3

# 5. Classes & Functions
class MyClass:
    ...
```

### 6.2. Docstring Standards (ドキュメント規約)

**Module Level:**

```python
"""
Module Name - 一行で役割を説明

詳細な説明が必要な場合はここに記述。
責務: このモジュールが担う責任を明記。
"""
```

**Function Level:**

```python
def process_text(text: str, level: int = 30) -> dict:
    """
    テキストを変換する（一行で目的を説明）

    Args:
        text: 入力テキスト
        level: Seasoningレベル (0-100)

    Returns:
        dict: {"success": bool, "result": str, ...}

    Raises:
        ValueError: level が範囲外の場合
    """
```

**Class Level:**

```python
class CoreProcessor:
    """
    テキスト処理のコアロジック

    Attributes:
        privacy_scanner: PIIスキャナインスタンス

    Example:
        >>> processor = CoreProcessor()
        >>> result = await processor.process(req, db)
    """
```

### 6.3. Naming Conventions (命名規則)

| 種別 | 規則 | 例 |
|------|------|-----|
| クラス | PascalCase | `CoreProcessor`, `SeasoningManager` |
| 関数/メソッド | snake_case | `process_text`, `get_level_label` |
| 定数 | SCREAMING_SNAKE_CASE | `MAX_RETRIES`, `SALT_MAX` |
| 変数 | snake_case | `user_input`, `job_id` |
| プライベート | _prefix | `_internal_method` |

**禁止される命名:**

- `data`, `tmp`, `x`, `temp` など汎用的すぎる名前
- 1文字変数（ループカウンタ `i`, `j` を除く）

### 6.4. Type Hints (型ヒント)

**必須:**

- すべての関数パラメータと戻り値に型ヒントを付ける
- `Any` の使用は最小限に（使用時はコメントで理由を説明）

```python
# ✅ Good
def calculate_cost(tokens: int, model: str) -> float:
    ...

# ❌ Bad
def calculate_cost(tokens, model):
    ...
```

### 6.5. Error Handling (エラー処理)

```python
# ✅ Good: 具体的な例外をキャッチし、構造化されたエラーを返す
try:
    result = await api_call()
except APIError as e:
    logger.error(f"API call failed: {e}")
    return {"success": False, "error": "api_error", "message": str(e)}

# ❌ Bad: 例外を握りつぶす
try:
    result = await api_call()
except:
    pass
```

### 6.6. Comment Standards (コメント規約)

**コメントが必要な場合:**

- 「なぜ」そうしたかの説明（Why）
- 非自明なビジネスロジック
- TODO/FIXME（必ず Issue 番号を付ける）

**コメントが不要な場合:**

- コードを読めばわかること（What）
- 自明な処理

```python
# ✅ Good: Why を説明
# WALモードを有効化（並列アクセス時のロック競合を軽減）
conn.execute(text("PRAGMA journal_mode=WAL"))

# ❌ Bad: What を書いているだけ
# WALモードを有効化する
conn.execute(text("PRAGMA journal_mode=WAL"))
```

### 6.7. Magic Numbers (マジックナンバー禁止)

```python
# ✅ Good: 定数として定義
SALT_MAX = 30
SAUCE_MAX = 70

if level <= SALT_MAX:
    ...

# ❌ Bad: 直接数値を使用
if level <= 30:
    ...
```

---

## 🔧 7. IDE Integration (IDE連携)

この憲法をIDEに統合するため、以下のファイルを配置する:

| File | Purpose |
|------|---------|
| `.gemini/rules.md` | Gemini Code Assist 用ルール |
| `pyproject.toml` | Ruff/Black 設定 |
| `.editorconfig` | エディタ共通設定 |

---
*Last Updated: 2026-01-06*
