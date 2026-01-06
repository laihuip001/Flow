# AI Clipboard Pro - Google Colab 実行ガイド

このファイルには、Google Colabでサーバーを起動するための手順が記載されています。

---

## 📋 事前準備

1. **Gemini API Key** を取得: <https://aistudio.google.com/app/apikey>
2. **ngrok のアカウント作成**: <https://ngrok.com/> で無料アカウントを作成し、Auth Tokenを取得

---

## 🚀 Colab での実行手順

### セル 1: ファイルをアップロード

以下のファイルをColabにアップロードするか、Google Driveにマウントしてください:

- `requirements.txt`
- `config.py`
- `models.py`
- `database.py`
- `logic.py`
- `main.py`

または、このリポジトリ全体をColabにクローン:

```python
!git clone https://github.com/YOUR_USERNAME/prompt-engineering-library.git
%cd prompt-engineering-library
```

---

### セル 2: ライブラリのインストール

```python
!pip install -r requirements.txt
```

---

### セル 3: 環境変数の設定

```python
# .envファイルの作成（APIキーの設定）
# ※ YOUR_GEMINI_API_KEY を実際のキーに置き換えてください

with open(".env", "w") as f:
    f.write('GEMINI_API_KEY="YOUR_GEMINI_API_KEY"\n')

print("✅ .env ファイルを作成しました")
```

---

### セル 4: サーバー起動 & ngrokで公開

```python
import subprocess
import time
from pyngrok import ngrok

# 既に走っているプロセスがあればキル
!pkill -f uvicorn

# uvicornをバックグラウンドで実行
proc = subprocess.Popen(["uvicorn", "main:app", "--port", "8000"])

# ngrokトークン設定（初回のみ必要）
# ※ YOUR_NGROK_TOKEN を実際のトークンに置き換えてください
!ngrok config add-authtoken "YOUR_NGROK_TOKEN"

# 起動待ち
time.sleep(5)

# ngrokで公開
public_url = ngrok.connect(8000).public_url
print(f"🚀 API Server is Online: {public_url}")
print(f"📄 Docs: {public_url}/docs")
```

---

## 📱 Android HTTP Shortcuts 設定

### 1. 「AI診断」ショートカット

- **URL**: `{public_url}/analyze`
- **Method**: POST
- **Body**: `{"text": "{clipboard_text}"}`
- **動作**: 推奨モードとコストを表示

### 2. 「Light処理」ショートカット

- **URL**: `{public_url}/process/sync`
- **Method**: POST
- **Body**: `{"text": "{clipboard_text}", "mode": "light"}`
- **動作**: 即座に整形結果を返す

### 3. 「Deep Research」ショートカット

- **URL**: `{public_url}/process/async`
- **Method**: POST
- **Body**: `{"text": "{clipboard_text}", "mode": "deep"}`
- **動作**: ジョブIDを返して終了（バックグラウンド処理）

### 4. 「結果確認」ショートカット

- **URL**: `{public_url}/jobs/{job_id}`
- **Method**: GET
- **動作**: 処理結果を取得

---

## 🔧 トラブルシューティング

### APIキーエラー

```
GEMINI_API_KEY が設定されていません
```

→ `.env` ファイルのAPIキーを確認

### ngrok接続エラー

```
ngrok ERR_NGROK_...
```

→ ngrokのAuth Tokenが正しいか確認

### ポートが使用中

```
Address already in use
```

→ `!pkill -f uvicorn` を実行してから再起動
