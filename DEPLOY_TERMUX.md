# 📱 Flow AI v4.0 - Termux デプロイガイド

> Android スマートフォン上で Flow AI サーバーを運用するための完全手順書

---

## 前提条件

- Android 7.0以上
- [Termux](https://f-droid.org/packages/com.termux/) (F-Droid版を推奨)
- Python 3.10+
- Git
- 安定したWi-Fi接続

---

## 1. 初期セットアップ

```bash
# Termuxパッケージ更新
pkg update && pkg upgrade -y

# 必要なパッケージインストール
pkg install python git curl -y

# リポジトリをクローン
git clone https://github.com/laihuip001/Flow.git
cd Flow
```

---

## 2. 環境設定

```bash
# .env ファイルを作成
cp .env.example .env

# APIキーを設定 (必須)
vim .env
# GEMINI_API_KEY=your_api_key_here
```

---

## 3. 起動方法

### A) シンプル起動 (手動)

```bash
# 依存インストール
pip install -r requirements-termux.txt

# サーバー起動
python run_server.py
```

### B) 推奨: start_termux.sh (自動venv作成)

```bash
chmod +x maintenance/start_termux.sh
./maintenance/start_termux.sh
```

### C) 本番運用: Titanium Watcher (自動復旧)

```bash
chmod +x maintenance/titanium_watcher.sh
nohup ./maintenance/titanium_watcher.sh > watcher.log 2>&1 &
```

---

## 4. 動作確認

```bash
# ヘルスチェック
curl http://localhost:8000/healthz

# 期待される応答: {"status": "healthy"}
```

---

## 5. 外部アクセス (オプション)

### Cloudflare Tunnel (推奨)

```bash
# cloudflared インストール
pkg install cloudflared -y

# トンネル作成
cloudflared tunnel login
cloudflared tunnel create flow-ai
cloudflared tunnel route dns flow-ai your-subdomain.yourdomain.com

# 起動
cloudflared tunnel run flow-ai
```

---

## 6. Phantom Process Killer 対策

Androidはバックグラウンドプロセスを停止することがあります。  
PC接続時に以下のコマンドで無効化できます:

```bash
adb shell device_config put activity_manager max_phantom_processes 2147483647
```

---

## トラブルシューティング

| 症状 | 解決策 |
|---|---|
| `pip install` 失敗 | `pkg install build-essential` を先に実行 |
| ポート8000使用中 | `pkill -f uvicorn` でプロセス停止 |
| メモリ不足 | `--workers 1` オプションを追加 |

---

## 関連ファイル

- [requirements-termux.txt](./requirements-termux.txt) - Termux専用依存定義
- [maintenance/titanium_watcher.sh](./maintenance/titanium_watcher.sh) - 自動復旧スクリプト
- [maintenance/start_termux.sh](./maintenance/start_termux.sh) - 起動スクリプト
