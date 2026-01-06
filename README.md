# Flow AI v4.0

> **テキストを貼り付けて、即座にAIで整える。**

クリップボードのテキストを Gemini AI で自動整形するツール。  
PC（Windows）とスマホ（Android）の両方から使えます。

<!-- TODO: デモGIFを追加 -->
<!-- ![Demo](docs/demo.gif) -->

---

## 🎯 What It Does (3秒で理解)

| Input | → | Output |
|-------|---|--------|
| `やあ、これやっといて` | 🤖 | `お疲れ様です。こちらの件、対応をお願いいたします。` |
| `明日mtgあるから資料よろ` | 🤖 | `明日のミーティングに向けて、資料のご準備をお願いいたします。` |

**Seasoning スペクトラム:**

- 🧂 **Salt (10%)** - 誤字脱字修正のみ（高速）
- 🍝 **Sauce (50%)** - 標準的な整形
- 🌶️ **Spice (90%)** - 積極的に補完・強化

---

## ⚡ Quick Start

```bash
# 1. Clone & Setup
git clone https://github.com/YOUR_USERNAME/AI-Clipboard-Pro.git
cd AI-Clipboard-Pro
python setup_titanium.py

# 2. 環境変数設定
# .env ファイルを編集して GEMINI_API_KEY を設定

# 3. 起動
python run_server.py     # API Server (Port 8000)
python run_app.py        # Desktop GUI (Windows)
```

---

## 🏗️ Architecture

```
src/
├── core/           # ビジネスロジック
│   ├── processor.py    # CoreProcessor (メイン処理)
│   ├── seasoning.py    # SeasoningManager (0-100スペクトラム)
│   ├── privacy.py      # PII検知・マスキング
│   └── gemini.py       # Gemini API クライアント
├── api/            # FastAPI エンドポイント
│   └── main.py         # /process, /seasoning, /scan
├── app/            # Flet Desktop GUI
└── infra/          # データベース
```

**技術スタック:**

- **Backend:** FastAPI + Uvicorn (async)
- **AI:** Google Gemini 3 (`google-genai` v1.0 SDK)
- **Database:** SQLite + WAL mode
- **Desktop:** Flet (Flutter-based)

---

## 🛡️ Security Features

| Feature | Description |
|---------|-------------|
| **PII Masking** | 送信前にメール・電話番号等をプレースホルダに置換 |
| **Token Auth** | Bearer Token による API 認証 |
| **Zero Trust** | Gemini API に PII を送信しない設計 |

---

## 📊 Technical Decisions

### Why Seasoning Spectrum (0-100)?

従来の離散的なスタイル（business, casual等）を廃止し、**連続スペクトラム**を採用。

```python
# 従来 (v3.x)
style = "business"  # 5種類の固定選択肢

# 現在 (v4.0)
seasoning = 50  # 0-100 の連続値
```

**理由:**

- ユーザーが「もう少しだけフォーマルに」を表現可能
- モデル選択の自動化（低Seasoning = Flash、高Seasoning = Pro）

### Why PII Masking Before API Call?

```python
masked, mapping = mask_pii("連絡先: test@example.com")
# masked: "連絡先: [PII_0]"

result = gemini_api(masked)
final = unmask_pii(result, mapping)
# "連絡先: test@example.com" に復元
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `run_server.py` | API サーバー起動 |
| `run_app.py` | Desktop GUI 起動 |
| `setup_titanium.py` | 環境復旧スクリプト |
| `CONSTITUTION.md` | 開発規約（コーディング標準） |

---

## 📚 Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - システム設計
- [CONSTITUTION.md](CONSTITUTION.md) - 開発規約
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - 使い方ガイド

---

## 🧪 Testing

```bash
pytest tests/test_logic.py tests/test_privacy.py -v
```

**テスト対象:**

- `SeasoningManager` - プロンプト生成
- `PrivacyScanner` - PII 検出
- `mask_pii / unmask_pii` - マスク往復

---

## 🎓 What I Learned

このプロジェクトを通じて学んだこと:

1. **非同期処理設計** - FastAPI + async/await パターン
2. **セキュリティ設計** - PII マスキング、トークン認証
3. **リファクタリング** - 大規模なスタイル → Seasoning 移行
4. **テスト駆動** - 変更前にテストを書く習慣

---

*Flow AI v4.0 - Built with Gemini AI*
