# 🚀 デプロイガイド

Google Colab以外の実行環境オプションです。
「スマホを取り出してすぐ使える」状態にするための選択肢を紹介します。

---

## 📊 選択肢の比較

| 方法 | 固定URL | コスト | 難易度 | おすすめ |
|------|---------|--------|--------|----------|
| Google Colab | ❌ | 無料 | ★☆☆ | 開発用 |
| **Render** | ✅ | 無料〜 | ★★☆ | 👑 推奨 |
| Railway | ✅ | $5/月〜 | ★★☆ | 高速 |
| **Termux** | localhost | 無料 | ★★★ | 完全オフライン |
| **自宅PC** | ✅ | 電気代 | ★★★ | 最高性能 |

---

## 案1: クラウドPaaS（Render）👑 推奨

Webサービスとしてインターネット上に公開。URLが固定され、どこからでもアクセス可能。

### メリット

- ✅ URL固定（`https://my-clipboard-ai.onrender.com`）
- ✅ スマホのバッテリーを消費しない
- ✅ 無料プランあり

### デメリット

- ⚠️ Cold Start問題（無料プランは放置後の初回反応が遅い）

### セットアップ手順（15分）

#### 1. GitHubにコードをアップロード

```bash
# 新しいリポジトリを作成後
git init
git add main.py logic.py models.py config.py database.py requirements.txt
git commit -m "AI Clipboard Pro v2.5"
git remote add origin https://github.com/YOUR_USERNAME/ai-clipboard-pro.git
git push -u origin main
```

#### 2. Render.com でデプロイ

1. [Render.com](https://render.com) に登録（GitHub連携）
2. 「New Web Service」をクリック
3. GitHubリポジトリを選択
4. 設定：
   - **Name:** `ai-clipboard-pro`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables** を設定：
   - `GEMINI_API_KEY` = あなたのAPIキー
6. 「Create Web Service」をクリック

#### 3. 完成

数分後、固定URLが発行されます：
> `https://ai-clipboard-pro.onrender.com`

---

## 案2: スマホ完結（Termux）📱

Androidの中にLinux環境を作り、そこでFastAPIを走らせます。

### メリット

- ✅ **通信ラグゼロ**
- ✅ インターネット不要（地下鉄でも動く！）
- ✅ 完全無料
- ✅ プライバシー最強

### デメリット

- ⚠️ バッテリー消費
- ⚠️ セットアップがコマンドライン

### セットアップ手順

#### 1. Termuxのインストール

> ⚠️ **重要:** Playストア版は更新が止まっているので非推奨

1. [F-Droid](https://f-droid.org/) からTermuxをインストール
2. または [GitHub Releases](https://github.com/termux/termux-app/releases) から直接APKをダウンロード

#### 2. 環境構築

Termuxを開いて以下を実行：

```bash
# パッケージの更新
pkg update && pkg upgrade -y

# PythonとGitのインストール
pkg install python git -y

# 作業フォルダの作成
mkdir ai-clipboard
cd ai-clipboard

# 仮想環境の作成（推奨）
python -m venv venv
source venv/bin/activate

# ライブラリのインストール
pip install fastapi uvicorn google-generativeai pydantic sqlalchemy python-dotenv
```

#### 3. コードの配置

PCで作ったファイルをスマホに転送：

- Google Drive経由
- USB接続
- Termux内で `git clone`

```bash
# GitHubからクローンする場合
git clone https://github.com/YOUR_USERNAME/ai-clipboard-pro.git
cd ai-clipboard-pro
```

#### 4. 環境変数の設定

```bash
# .envファイルを作成
echo 'GEMINI_API_KEY="your_api_key_here"' > .env
```

#### 5. サーバー起動

```bash
# 起動
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 6. HTTP Shortcutsの設定変更

URLを以下に変更：

```
http://localhost:8000/prefetch
http://localhost:8000/process/sync
```

### Termuxのバックグラウンド実行

スマホがスリープしてもサーバーを動かし続けるには：

```bash
# Termux:Boot をインストール（F-Droidから）
# ~/.termux/boot/ に起動スクリプトを置く

mkdir -p ~/.termux/boot
echo '#!/data/data/com.termux/files/usr/bin/sh
cd ~/ai-clipboard
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000' > ~/.termux/boot/start-api.sh
chmod +x ~/.termux/boot/start-api.sh
```

---

## 案3: 自宅PC（Cloudflare Tunnel）🏠

自宅PCでサーバーを動かし、Cloudflare Tunnelで外部公開。

### メリット

- ✅ PCのパワーが使える（ローカルLLMも可能）
- ✅ URL固定が**無料**
- ✅ Geminiだけでなく、様々なAIを利用可能

### デメリット

- ⚠️ PCをつけっぱなしにする必要がある（電気代）
- ⚠️ 初期設定がやや複雑

### セットアップ手順

#### 1. Cloudflareアカウント作成

1. [Cloudflare](https://dash.cloudflare.com/) に登録
2. 無料のドメインを追加（または既存ドメインを使用）

#### 2. cloudflared のインストール

```bash
# Windows (PowerShell)
winget install cloudflare.cloudflared

# Mac
brew install cloudflared

# Linux
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/
```

#### 3. トンネル作成

```bash
# ログイン
cloudflared tunnel login

# トンネル作成
cloudflared tunnel create ai-clipboard

# 設定ファイル作成
cloudflared tunnel route dns ai-clipboard ai-clipboard.yourdomain.com
```

#### 4. サーバー起動 + トンネル

```bash
# APIサーバー起動
python main.py &

# トンネル起動
cloudflared tunnel run ai-clipboard
```

これで `https://ai-clipboard.yourdomain.com` からアクセス可能に！

---

## 💡 ハイブリッド運用（推奨）

**自宅PC + スマホ（Termux）の組み合わせ**で最強の冗長性を実現！

### MacroDroidでの自動切り替えロジック

```
If: 自宅Wi-Fiに接続中
  → URL: http://192.168.x.x:8000 (自宅PCのローカルIP)
  
Else If: 自宅PCへのPingが通る
  → URL: https://ai-clipboard.yourdomain.com (Cloudflare Tunnel)
  
Else:
  → URL: http://localhost:8000 (Termux)
```

**メリット:**

- 自宅では高速なPC処理
- 外出時もCloudflare経由でPC利用
- PCが落ちてもスマホが頑張る！

---

## ⚠️ Google Cloud (GCP) について

GCP（特にCloud Run）でも無料運用は可能ですが：

- ❌ セットアップが複雑（Docker、IAM設定）
- ❌ クラウド破産のリスク
- ❌ 個人利用にはオーバースペック

**学習目的なら良い教材**ですが、まずはRenderかTermuxがおすすめです。
