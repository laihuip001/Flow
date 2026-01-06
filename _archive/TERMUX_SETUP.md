# 📱 Termux 構築ガイド

スマホの中に「AI Clipboard Pro v2.5」のサーバーを立ち上げる完全手順書です。

---

## 🎯 これで何ができる？

- ✅ **通信ラグゼロ** - localhost で完結
- ✅ **オフライン対応** - 地下鉄でも動く
- ✅ **完全無料** - クラウド不要
- ✅ **プライバシー最強** - データがスマホ外に出ない

---

## ステップ 1: Termuxのインストール

> ⚠️ Google PlayストアのTermuxは古いため、必ず **F-Droid** からインストール

1. [F-Droid公式サイト](https://f-droid.org/en/packages/com.termux/) へアクセス
2. 「Download APK」をタップしてインストール
3. アプリを開く

---

## ステップ 2: 環境構築

Termuxを開くと黒い画面が出ます。
以下のコマンドを**一行ずつコピーして貼り付け、Enterキーを押してください**。

```bash
# 1. パッケージの更新
pkg update -y && pkg upgrade -y

# 2. Pythonと必須ツールのインストール
pkg install python git -y

# 3. 作業フォルダの作成と移動
mkdir -p ai-clipboard
cd ai-clipboard

# 4. 仮想環境の作成（推奨）
python -m venv venv
source venv/bin/activate

# 5. ライブラリのインストール
pip install fastapi uvicorn google-generativeai pydantic pydantic-settings sqlalchemy python-dotenv
```

---

## ステップ 3: コードの一括配置（インストーラー）

以下の「魔法のコマンド」をTermuxに貼り付けて実行してください。
全ファイル（`main.py`, `logic.py` 等）が自動生成されます。

```bash
# インストーラーをダウンロード（GitHubから）
# または以下のコマンドでローカルに作成
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/ai-clipboard-pro/main/setup_project.py

# 実行
python setup_project.py
```

### 手動でインストーラーを作る場合

`setup_project.py` がリポジトリにあります。
PCからスマホにコピーして実行してください。

---

## ステップ 4: APIキーの設定

```bash
# nanoエディタを開く
nano .env
```

以下を入力：

```text
GEMINI_API_KEY="AIzaSy..."
```

保存: `Ctrl + O` → `Enter`
終了: `Ctrl + X`

> 💡 AndroidキーボードにCtrlキーがない場合:
>
> - Termux画面上の拡張キーボードを使用
> - または「ボリュームダウン + X」 = Ctrl+X

---

## ステップ 5: サーバー起動

```bash
# スリープ防止（重要！）
termux-wake-lock

# サーバー起動
uvicorn main:app --host 0.0.0.0 --port 8000
```

`Application startup complete.` と出れば成功！ 🎉

---

## ステップ 6: HTTP Shortcuts の設定

URLを以下に変更：

```
http://localhost:8000/process/sync
http://localhost:8000/prefetch
```

これで、ネットワーク経由せずに爆速で処理できます！

---

## 🔧 バックグラウンド実行（常駐化）

スマホがスリープしてもサーバーを動かし続けるには：

### 1. Termux:Boot のインストール

F-Droidから「Termux:Boot」をインストール

### 2. 起動スクリプトの作成

```bash
mkdir -p ~/.termux/boot
cat << 'EOF' > ~/.termux/boot/start-api.sh
#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
cd ~/ai-clipboard
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
EOF
chmod +x ~/.termux/boot/start-api.sh
```

### 3. バッテリー最適化の除外

設定 → アプリ → Termux → バッテリー → 制限なし

---

## 🔄 2回目以降の起動

```bash
cd ai-clipboard
source venv/bin/activate
termux-wake-lock
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📚 関連ドキュメント

- [DEPLOYMENT.md](./DEPLOYMENT.md) - PC版セットアップ、ハイブリッド構成
- [ANDROID_SETUP.md](./ANDROID_SETUP.md) - MacroDroid/HTTP Shortcuts設定
