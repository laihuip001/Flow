# 📱 Flow AI v4.0 - Termux デプロイガイド

> Android スマートフォン上で Flow AI サーバーを運用するための完全手順書

---

## 前提条件

- Android 7.0以上
- 安定したWi-Fi接続
- PC不要（スマートフォンのみで完結）

---

## 0. Termuxのインストール

> ⚠️ **Google Play版は非推奨**（古くて動作しません）

1. **F-Droid**をインストール: https://f-droid.org/
2. F-Droidを開き、検索で「Termux」を探す
3. Termuxをインストール
4. Termuxを起動

---

## 1. 初期セットアップ

```bash
# Termuxパッケージ更新（初回は時間がかかります）
pkg update && pkg upgrade -y

# 必要なパッケージインストール
pkg install python git nano -y

# リポジトリをクローン
git clone https://github.com/laihuip001/Flow.git
cd Flow
```

---

## 2. 環境設定

### 2.1 設定ファイルの作成

```bash
cp .env.example .env
```

### 2.2 APIキーの設定

**Gemini API Keyの取得方法:**
1. https://aistudio.google.com/apikey にアクセス
2. Googleアカウントでログイン
3. 「Create API Key」をクリック
4. 表示されたキーをコピー

**設定ファイルの編集:**
```bash
# nanoエディタで開く
nano .env
```

以下のように編集:
```
GEMINI_API_KEY=ここにコピーしたキーを貼り付け
```

保存: `Ctrl + O` → `Enter` → `Ctrl + X`

---

## 3. 起動方法

### A) 初回・テスト用（手動起動）

```bash
# 依存インストール（初回のみ、数分かかります）
pip install -r requirements-termux.txt

# サーバー起動
python run_server.py
```

### B) 推奨: 自動セットアップ

```bash
chmod +x maintenance/start_termux.sh
./maintenance/start_termux.sh
```

### C) 本番運用: 自動復旧つき

```bash
chmod +x maintenance/titanium_watcher.sh
nohup ./maintenance/titanium_watcher.sh > watcher.log 2>&1 &
```

---

## 4. 動作確認

別のTermuxセッション、またはスマホのブラウザで:

```
http://localhost:8000/healthz
```

期待される応答:
```json
{"status": "healthy", ...}
```

---

## 5. 外部アクセス（オプション）

> これを設定すると、他の端末からもアクセス可能になります

### Cloudflare Tunnel

```bash
pkg install cloudflared -y
cloudflared tunnel login
cloudflared tunnel create flow-ai
cloudflared tunnel route dns flow-ai your-subdomain.yourdomain.com
cloudflared tunnel run flow-ai
```

> 💡 Cloudflareの無料アカウントが必要です

---

## 6. バックグラウンド動作の維持

Androidはバックグラウンドアプリを停止することがあります。

### 対策1: Termuxの通知を常時表示
Termuxアプリの設定で「Acquire Wakelock」を有効にする

### 対策2: PC接続時（開発者向け）
```bash
adb shell device_config put activity_manager max_phantom_processes 2147483647
```

---

## トラブルシューティング

| 症状 | 解決策 |
|---|---|
| `pip install` 失敗 | `pkg install build-essential` を先に実行 |
| ポート8000使用中 | `pkill -f uvicorn` でプロセス停止 |
| メモリ不足 | 他のアプリを終了してから再試行 |
| `nano`が見つからない | `pkg install nano` |

---

## 関連ファイル

- [requirements-termux.txt](./requirements-termux.txt) - Termux専用依存定義
- [maintenance/titanium_watcher.sh](./maintenance/titanium_watcher.sh) - 自動復旧スクリプト
- [maintenance/start_termux.sh](./maintenance/start_termux.sh) - 起動スクリプト
