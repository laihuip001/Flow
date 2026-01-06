# 📚 AI Clipboard Pro v3.0.1 セットアップガイド

ゼロからの完全セットアップ手順です。

---

## 📋 目次

1. [必要なもの](#1-必要なもの)
2. [Gemini APIキーの取得](#2-gemini-apiキーの取得)
3. [サーバーセットアップ](#3-サーバーセットアップ)
4. [動作確認](#4-動作確認)
5. [クライアント設定（Android）](#5-クライアント設定android)
6. [本番環境での運用](#6-本番環境での運用)
7. [トラブルシューティング](#7-トラブルシューティング)

---

## 1. 必要なもの

### ソフトウェア
- **Python 3.9以上**
- **pip**（Pythonパッケージマネージャー）

### アカウント
- **Google AI Studio アカウント**（Gemini API用）

### オプション（Android連携時）
- **HTTP Shortcuts** アプリ
- **MacroDroid** アプリ（自動化用）

---

## 2. Gemini APIキーの取得

### Step 1: Google AI Studioにアクセス

https://aistudio.google.com/

### Step 2: APIキーを作成

1. 左メニュー「Get API key」をクリック
2. 「Create API key」をクリック
3. プロジェクトを選択（または新規作成）
4. 生成されたAPIキーをコピー

> ⚠️ **注意:** APIキーは他人に見せないでください

---

## 3. サーバーセットアップ

### Step 1: プロジェクトフォルダに移動

```bash
cd prompt-engineering-library
```

### Step 2: インストーラーを実行

```bash
python setup_v3.py
```

これで以下のファイルが生成されます：
- `config.py` - 設定ファイル
- `models.py` - データモデル
- `database.py` - データベース接続
- `logic.py` - ビジネスロジック
- `main.py` - APIサーバー
- `requirements.txt` - 依存関係
- `.env.example` - 環境変数サンプル

### Step 3: 依存関係をインストール

```bash
pip install -r requirements.txt
```

### Step 4: 環境変数を設定

```bash
# .envファイルを作成
cp .env.example .env

# .envを編集してAPIキーを設定
```

**.env ファイルの内容:**
```
GEMINI_API_KEY=あなたのAPIキー
API_TOKEN=（本番用：ランダムな文字列）
```

### Step 5: サーバーを起動

```bash
python main.py
```

成功すると以下が表示されます：
```
🚀 AI Clipboard Pro v3.0.1 - Production Ready
--------------------------------------------------
📖 API ドキュメント: http://localhost:8000/docs
🏥 ヘルスチェック: http://localhost:8000/healthz
--------------------------------------------------
```

---

## 4. 動作確認

### ブラウザで確認

http://localhost:8000/docs を開く

Swagger UIが表示されれば成功です。

### テストスクリプトで確認

```bash
python test_v3.py
```

全項目がPASSすればOKです。

### 手動テスト（curl）

```bash
# スタイル一覧
curl http://localhost:8000/styles

# テキスト処理
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"text": "明日の会議について", "style": "business"}'
```

---

## 5. クライアント設定（Android）

### HTTP Shortcuts アプリ

1. **新規ショートカット作成**
2. **URL:** `http://スマホのIP:8000/process`
3. **メソッド:** POST
4. **Body (JSON):**
   ```json
   {
     "text": "{clipboard}",
     "style": "business"
   }
   ```
5. **トリガー:** ホーム画面ウィジェット or 共有メニュー

### スタイル選択メニューを追加

1. 変数を追加（タイプ: 選択リスト）
2. 選択肢:
   - `business` (ビジネス)
   - `casual` (カジュアル)
   - `summary` (要約)
   - `english` (英語翻訳)
   - `proofread` (校正)
3. Bodyの`style`を変数に置き換え

詳細は `V3_CLIENT_SETUP.md` を参照してください。

---

## 6. 本番環境での運用

### 認証を有効にする

1. ランダムなトークンを生成:
   ```bash
   openssl rand -hex 32
   ```

2. `.env`に追加:
   ```
   API_TOKEN=生成したトークン
   ```

3. クライアント側でヘッダーを追加:
   ```
   Authorization: Bearer 生成したトークン
   ```

### 外部公開（ngrok）

```bash
ngrok http 8000
```

発行されたURLをクライアントに設定します。

### 永続化（Termux）

```bash
# バックグラウンド実行
nohup python main.py &

# または tmux使用
tmux new -s aiclip
python main.py
# Ctrl+B, D でデタッチ
```

---

## 7. トラブルシューティング

### サーバーが起動しない

```bash
# Pythonバージョン確認
python --version  # 3.9以上必要

# 依存関係の再インストール
pip install -r requirements.txt --force-reinstall
```

### APIキーエラー

- `.env`ファイルが存在するか確認
- APIキーが正しいか確認
- Google AI Studioでクォータを確認

### 接続できない（Android）

- スマホとPCが同じネットワークにあるか確認
- ファイアウォール設定を確認
- PCのIPアドレスを確認: `ipconfig` (Windows) / `ifconfig` (Mac/Linux)

### テストが失敗する

```bash
# サーバーが起動しているか確認
curl http://localhost:8000/

# ログを確認
python main.py  # ターミナルでログを見る
```

---

## 📎 クイックリファレンス

### API エンドポイント

| エンドポイント | メソッド | 説明 | 認証 |
|--------------|--------|------|-----|
| `/` | GET | ヘルスチェック | 不要 |
| `/healthz` | GET | 詳細ヘルスチェック | 不要 |
| `/styles` | GET | スタイル一覧 | 不要 |
| `/scan` | POST | PII検知 | 不要 |
| `/process` | POST | テキスト処理 | 必要* |
| `/prefetch` | POST | 先読み | 必要* |

*API_TOKEN設定時のみ

### スタイル一覧

| ID | 名前 | 用途 |
|----|------|------|
| `business` | ビジネス | メール、報告書 |
| `casual` | カジュアル | Slack、LINE |
| `summary` | 要約 | 箇条書きにまとめる |
| `english` | 英語翻訳 | ビジネス英語に翻訳 |
| `proofread` | 校正 | 誤字脱字修正 |

---

## 🆘 サポート

問題が解決しない場合は、以下を確認してください：

- `SECURITY.md` - セキュリティ設定
- `V3_CLIENT_SETUP.md` - クライアント詳細設定
- `CHANGELOG.md` - 変更履歴
