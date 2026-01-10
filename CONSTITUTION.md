# Titanium 開発規約（Development Norms）

このドキュメントは、Flow AIプロジェクトにおける **「やってはいけないこと」リスト（アンチパターン）** を定義する。
これらのルールに違反することは、プロフェッショナルエンジニアとしての信頼を損なう行為とみなす。

内部監査および外部基準（OWASP Top 10 for LLM、Pythonアンチパターン）に基づいて策定。

## 🚫 1. ゼロトラスト・プライバシー & AIセキュリティ（OWASP LLM）

- **絶対禁止**: 個人情報、具体的なメンタルヘルス記録、センシティブなパーソナルコンテキストファイル（例: `ANTIGRAVITY_CONTEXT.md`）をコミットすること。
- **絶対禁止**: APIキーをハードコードすること。常に `.env` を使用せよ。
- **絶対禁止**: セキュリティ機能（例: `mask_pii`）を実装しておきながら、実際のデータフローに統合しないこと。「実装済みだが未使用」はセキュリティホールである。
- **絶対禁止**: プロンプトインジェクション（Prompt Injection）のリスクを無視すること。すべてのユーザー入力はLLMに送信する前に「信頼できないもの」として扱え。
- **絶対禁止**: 外部APIにマスクされていないPII（個人識別情報）を送信する「機密情報漏洩（Sensitive Information Disclosure）」（OWASP LLM06）を許容すること。

## 🚫 2. コード衛生 & Pythonベストプラクティス

- **絶対禁止**: 未使用のインポート（`F401`）やワイルドカードインポート（`from module import *`）を放置すること。「明示的は暗黙的より優れている」。
- **絶対禁止**: `except Exception: pass` で例外を握りつぶすこと。常にエラーをログ出力するか、構造化されたエラーレスポンスを返せ。
- **絶対禁止**: ミュータブルなデフォルト引数（例: `def func(list=[])`）を使用すること。
- **絶対禁止**: 「神オブジェクト（God Objects）」や巨大関数（500行超）を許容すること。分割せよ（モジュラーモノリス）。
- **絶対禁止**: レガシーコードをルートディレクトリに放置すること。`_archive/` へ移動するか、即座に削除せよ。
- **絶対禁止**: ライブラリを丸ごと複製すること（DRY原則）。

## 🚫 3. プロフェッショナルとしての誠実さ & アーキテクチャ

- **絶対禁止**: 再現可能なベンチマークスクリプト（`tests/benchmark_latency.py`）なしに、パフォーマンスの主張（例: 「90秒→5秒」）を行うこと。
- **絶対禁止**: コードと矛盾するドキュメントを放置すること。`README.md` と `ARCHITECTURE.md` は同期的に更新せよ。
- **絶対禁止**: 「カーゴ・カルト（Cargo Culting）」に陥ること（例: 小規模アプリにマイクロサービス）。アーキテクチャはシンプルかつ正当化できるものであれ。
- **絶対禁止**: ルートディレクトリを肥大化させること。高レベル構造は15ファイル未満に保て。

## ⚡ 4. Titanium運用プロトコル（Execution Prime）

これらの設定は、生産性を最大化（3倍）しリスクを最小化（0%）するために**必須**である。

### 4.1. MCP（Model Context Protocol）設定

- **GitHub MCP（必須）:** Issueの読み取りとPR作成のために有効化。
- **Google検索/ドキュメントMCP（必須）:** 最新のSDKドキュメントを取得するために有効化。

### 4.2. 環境の最適化（.antigravityignore）

- **コンテキスト衛生:** `venv/`、`__pycache__/`、`.git/` を除外し、トークンの浪費と「ゴミデータ」によるハルシネーションを防止。
- **アクション:** `.antigravityignore` を作成済み（`.gitignore` + `venv/` をミラーリング）。

### 4.3. リモートファーストUI設定（タブレット最適化）

- **自動保存（ON）:** 切断時のデータ損失を防止。
- **サイドバー（右）:** 目の疲れを軽減（右にデザイン、左にコード）。
- **フォントサイズ（+）:** タブレット画面での視認性を確保。

### 4.4. Titaniumデバッグ自動化

- **ターミナル出力分析（ON）:** AIが自動的にエラーを検出し、修正を提案。
- **プリコミットルール:** 「保存前に型チェック/Lintを実行」（`.gemini/rules.md` を参照）。

## ⚡ 5. Titaniumディープカスタマイズ（推奨）

ゼロフリクション開発のためのプロレベルチューニング。

### 5.1. 品質自動化（拡張機能）

- **Ruff:** 自動リンティング/フォーマット。「赤い波線」= 即座に修正が必要。
- **GitLens:** 行ごとのBlame表示。「ブラックボックス」コード生成を防止。

### 5.2. 運用エイリアス（PowerShell）

- `watcher` -> `./maintenance/titanium_watcher.sh`
- `push` -> `./dev_tools/secure_push.sh`
- `sync` -> `./dev_tools/sync.sh`
- **アクション:** `dev_tools/setup_aliases.ps1` を実行。

### 5.3. コスト & 認証ガードレール

- **Git Credential Manager:** パスワードなしのプッシュを有効化。
- **GCPシャットダウン:** 毎日の停止をスケジュール（例: 午前4時 JST）してコストオーバーランを防止。

---
*Titanium Red Team Audit & Self-Correctionプロトコルによって執行*

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
*Last Updated: 2026-01-10*
