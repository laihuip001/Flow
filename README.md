# AI Clipboard Pro v4.0 Titanium Edition

> 🚀 **From Script to App** - AI-powered clipboard processing with beautiful GUI

PCのパワフルな計算能力でGemini 3を動かし、スマホやPC自身からあらゆるテキストを「AI視点」で変換・整理するためのツールキットです。

## ✨ NEW: Flet GUI App (v4.0)

**HTTP Shortcutsなしで使える、統合GUIアプリが誕生！**

```powershell
# 起動方法
python flet_app/main.py
```

| Feature | Description |
|:--|:--|
| 🎨 **タイルUI** | 5つのスタイルをワンタップで選択 |
| 📜 **履歴** | 処理結果を自動保存、後から参照可能 |
| ⚡ **ストリーミング** | AIの回答をリアルタイム表示 |
| 🌊 **オンボーディング** | 初回起動時の親切なセットアップガイド |

## 🏛️ Architecture Overview

```mermaid
graph TD
    User((👤 Architect))
    subgraph "🧠 STRATEGIC"
        Claude[🟣 Claude/Gemini]
        Task[📄 .ai/JULES_TASK.md]
    end
    subgraph "⚡ EXECUTION"
        Jules[👨‍💻 Jules Code Agent]
        Repo[🐙 GitHub]
    end
    subgraph "🛡️ RUNTIME"
        Watcher[🔄 titanium_watcher.sh]
        Termux[📟 Android Termux]
    end
    
    User --> Claude --> Task --> Jules --> Repo
    Repo -.-> Watcher --> Termux
```

**詳細:** [ARCHITECTURE.md](ARCHITECTURE.md)

## 📁 Project Structure

```text
AI-Clipboard-Pro/
├── .env                # 環境変数 (Gemini API Key, Token) [ユーザー作成]
├── main.py             # FastAPIサーバー本体 (エンドポイント定義)
├── logic.py            # AI処理ロジック (Gemini 3対応) / PII検知
├── config.py           # アプリケーション設定 (モデル指定など)
├── models.py           # データモデル (SQLAlchemy / Pydantic)
├── database.py         # データベース接続 (SQLite)
├── requirements.txt    # 依存ライブラリ一覧
├── tasks.db            # データベースファイル
├── check_models.py     # 利用可能モデル確認ツール
├── cloudflared.exe     # Cloudflare Tunnel (外部公開用)
├── tunnel.log          # トンネル接続ログ
└── ... (各種ドキュメント)
```

## 🚀 Setup Guide (Windows)

最新の **Gemini 3 (google-genai v1.0 SDK)** に対応済みです。

### 1. Python環境の準備

Python 3.10以降が必要です。

```powershell
# 依存ライブラリのインストール
pip install -r requirements.txt
pip install google-genai  # 最新モデル使用に必須
```

### 2. 環境変数の設定

`.env` ファイルを作成し、APIキーを設定します。

```ini
# .env
GEMINI_API_KEY=AIzaSy...
# 必要に応じて変更 (gemini-3-flash-preview など)
# Configは config.py でも変更可能
```

### 3. サーバー起動

FastAPIサーバーを起動します。

```powershell
python main.py
```

起動すると `http://localhost:8000` でアクセス可能になります。

### 4. 外部公開 (Cloudflare Tunnel)

Androidから接続するために、Cloudflare Tunnelで外部公開URLを発行します。

```powershell
.\cloudflared.exe tunnel --url http://localhost:8000
```

ログ (`tunnel.log` またはコンソール) に表示される `https://xxxx-xxxx.trycloudflare.com` というURLをメモしてください。

## 📱 Android Setup

1. **HTTP Shortcuts** アプリなどをインストールします。
2. **新しいショートカット** を作成:
    * **Method:** POST
    * **URL:** `https://<あなたのトンネルURL>/process`
    * **Body Type:** JSON
    * **Body:** `{"text": "<クリップボードの内容>", "style": "business"}`
3. **変数の利用:** マクロツールを使う場合、クリップボードの内容を動的に `text` に埋め込むように設定してください。
4. テスト実行して、AIによる整形結果が返ってくれば成功です。

## 📚 Documentation

| ドキュメント | 内容 |
|:---|:---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | システム設計・ワークフロー |
| [SETUP_GUIDE_TITANIUM.md](SETUP_GUIDE_TITANIUM.md) | Titanium Edition セットアップ |
| [USAGE_GUIDE.md](USAGE_GUIDE.md) | 使い方ガイド |

## 🛡️ Security Features

* **Rate Limiting**: 60 req/min per IP
* **PII Detection**: 日本/US/国際フォーマット対応（メール、電話、APIキー、機密キーワード）
* **PII Masking**: 送信前にPIIをプレースホルダに置換、結果で復元（v4.0+）
* **Secret Scanning**: `secure_push.sh` でAPIキー流出防止
* **Circuit Breaker**: クラッシュループ自動検知・停止

## 🧠 Technical Decisions

ポートフォリオとして本プロジェクトを評価される方向けに、主要な設計判断とその根拠を記載します。

### Why FastAPI + Flet Hybrid?

| 選択肢 | 採用理由 |
|:--|:--|
| **FastAPI** | 型安全（Pydantic）+ 非同期I/O + OpenAPI自動生成 |
| **Flet** | Flutterベースのクロスプラットフォームで、単一のPythonコードからDesktop/Android/Web対応 |

**Why not Django/Flask?**  
→ REST API + SSE（Server-Sent Events）のストリーミングを軽量に実装するため。

### Why Direct Gemini API (Not via FastAPI)?

v4.0では、Flet GUIから**FastAPIを経由せず**直接Gemini APIを呼び出すオプションを追加。

```
[Before] Flet → HTTP → FastAPI → Gemini → FastAPI → HTTP → Flet (90秒)
[After]  Flet → genai SDK → Gemini → Flet (5秒)
```

**結果:** レイテンシを 90秒 → 5秒 に短縮（18倍高速化）

### Why SQLite with WAL Mode?

```python
engine = create_engine(url, connect_args={"timeout": 30}, pool_pre_ping=True)
conn.execute(text("PRAGMA journal_mode=WAL"))
```

* **WAL (Write-Ahead Logging)**: 読み取り/書き込みの並列実行を許可
* **timeout=30**: ロック競合時に30秒待機（クラッシュ回避）
* **pool_pre_ping**: 接続プール内の無効な接続を自動検出

### Why PII Masking Before API Call?

```python
masked_text, mapping = mask_pii(text)  # [PII_0], [PII_1]...
result = gemini_api(masked_text)
final = unmask_pii(result, mapping)    # 元のPIIに復元
```

* **ゼロトラスト**: Gemini APIにPIIを送信しない
* **復元可能**: 結果に含まれるプレースホルダを自動復元

### Test Coverage

```bash
pytest tests/test_logic.py -v
```

* `PrivacyScanner`: メール/電話/APIキー/機密キーワード検出テスト
* `mask_pii/unmask_pii`: マスク→復元の往復テスト
* `StyleManager`: スタイル設定取得テスト

---
*AI Clipboard Pro v4.0 Titanium Edition - Built with 🧠 Gemini + 👨‍💻 Antigravity*
