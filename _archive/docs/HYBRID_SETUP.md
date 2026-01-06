# 🏗️ ハイブリッド・アーキテクチャ構築

PC + スマホ（Termux）の自動切り替えで最強の冗長性を実現。

---

## 🎯 コンセプト

```
🏠 自宅Wi-Fi接続中 → PC (高性能)
📱 外出中 → Termux (オフライン対応)
☁️ PCダウン時 → Cloudflare Tunnel経由 or Termux
```

---

## 💻 フェーズ 1: 自宅PCを「母艦」にする

### 1. インストーラーの実行

```bash
# 作業フォルダ作成
mkdir ai-clipboard-pc
cd ai-clipboard-pc

# インストーラー実行
python setup_project.py

# ライブラリインストール
pip install -r requirements.txt

# .envファイル作成
cp .env.example .env
# GEMINI_API_KEY を設定
```

### 2. サーバー起動

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. PCのローカルIPアドレスを確認

```bash
# Windows
ipconfig
# → IPv4アドレス: 192.168.1.10

# Mac
ipconfig getifaddr en0
```

---

## 🌐 フェーズ 2: 外部からPCに接続 (Cloudflare Tunnel)

### 1. cloudflared インストール

```bash
# Windows
winget install cloudflare.cloudflared

# Mac
brew install cloudflared

# Linux
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/
```

### 2. トンネル起動

```bash
cloudflared tunnel --url http://localhost:8000
```

表示されたURL（例: `https://xxxx-xxxx.trycloudflare.com`）が外出用アドレス。

---

## 📱 フェーズ 3: Android側の自動切り替え

### 1. MacroDroid 変数の準備

変数タブで新規作成:

- 名前: `API_Base_URL`
- 型: 文字列 (String)

### 2. 切り替えマクロ作成

**マクロ名:** `AI接続先切替`

**トリガー:**

- Wifi接続時: 自宅SSID
- Wifi切断時: 自宅SSID

**アクション:**

```
If: Wifi接続中 = 自宅SSID
  → API_Base_URL = "http://192.168.1.10:8000"
  → トースト: "🏠 自宅モード: PCに接続"

Else:
  → API_Base_URL = "http://localhost:8000"
  → トースト: "📱 外出モード: Termuxに接続"

End If
```

### 3. HTTP Shortcuts の修正

グローバル変数を作成:

- 名前: `target_url`
- タイプ: MacroDroid Variable
- 変数名: `API_Base_URL`

ショートカットURLを変更:

```
変更前: http://localhost:8000/process/sync
変更後: {{target_url}}/process/sync
```

---

## 🎉 完成後の動作

### シチュエーション A: 自宅

1. スマホが家のWi-Fiを掴む
2. MacroDroidが検知 → PCに接続
3. コピーする
4. **PCのパワーで一瞬で処理**

### シチュエーション B: 外出中

1. Wi-Fiが切れる
2. MacroDroidが検知 → Termuxに接続
3. コピーする
4. **通信なし、スマホ内で完結**

---

## 🔄 フェイルオーバー（上級）

さらに堅牢にするなら:

```
1. PCにPing → 成功 → PCへ
2. PCにPing → 失敗 → Cloudflare経由でPC
3. Cloudflare失敗 → Termux
```

MacroDroidの「HTTPリクエスト」で `/` をGETして、
レスポンスコードで分岐させることで実現可能。

---

# 🛡️ 最強のバックアップ体制（フェイルオーバー）

HTTP Shortcutsの**エラーハンドリング機能**を使って、
**「実際に通信してダメなら次へ」** という自動切り替えを実現。

## ステップ 1: 予備（Termux）のショートカットを作る

「絶対に失敗しない最後の砦」を用意:

1. HTTP Shortcutsを開く
2. 既存ショートカットを「複製」
3. 設定:
   - **名前:** `AI処理_Termux`
   - **URL:** `http://localhost:8000/process/sync`
4. ホーム画面には配置しない（裏方用）

## ステップ 2: メインのタイムアウトを短く

PCが落ちている時に待たされるのを防ぐ:

1. メインのショートカット編集画面を開く
2. 「高度な設定 (Advanced)」→「タイムアウト (Timeout)」
3. **`1000`** (1秒) または **`500`** (0.5秒) に設定

> 💡 PCが生きていれば一瞬で返る。返らないなら死んでいる。

## ステップ 3: 失敗時のリレー設定

1. メインのショートカット編集画面
2. 「実行後の操作 (Response)」タブ
3. **「失敗時 (On Error)」** → **「他のショートカットを実行」**
4. **`AI処理_Termux`** を指定
5. 「エラー通知を表示しない」をON

---

## 🎉 完成した挙動

```
1. あなた: 「AI変換」を押す
2. HTTP Shortcuts: PCにアクセス試行

Case A (PC起動中):
  → 0.1秒で応答
  → PCパワーで処理完了 ✅

Case B (PC電源OFF):
  → 0.5秒で「応答なし」判断
  → 即座にTermuxへ切り替え
  → スマホ内で処理完了 ✅

結果: どちらでも同じ結果を返す
```

---

## 💡 Termux常駐化のTips

「いざという時にTermuxが起動していない」を防ぐ:

### 1. Termuxの常駐設定

```bash
termux-wake-lock
```

### 2. スマホ起動時の自動実行

**Termux:Boot** をインストール（F-Droid）:

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

---

## 🏆 完成

これで **「絶対に止まらないAIインフラ」** が完成:

- ☁️ クラウド不要
- 🏠 自宅PC → 高性能処理
- 📱 外出/PCダウン → Termuxで継続
- 🛡️ フェイルオーバー → 自動切り替え
