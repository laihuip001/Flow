# HTTP Shortcuts 設定ガイド

このドキュメントでは、Android アプリ「HTTP Shortcuts」を使って Flow AI サーバーと連携する方法を説明します。

---

## 前提条件

1. **Flow AI サーバーが稼働していること**
    - ローカル: `http://localhost:8000`
    - Termux: `http://<端末IP>:8000`
    - クラウド: Cloudflare Tunnel 経由の URL

2. **HTTP Shortcuts アプリがインストール済みであること**
    - [Google Play Store](https://play.google.com/store/apps/details?id=ch.rmy.android.http_shortcuts)

---

## 基本設定

### 1. テキスト処理ショートカット（メイン機能）

| 項目 | 値 |
|---|---|
| **Name** | Flow AI - Process |
| **Method** | POST |
| **URL** | `http://<サーバーURL>:8000/process` |
| **Body Type** | JSON |
| **Body Content** | (下記参照) |

**Body Content:**

```json
{
  "text": "{{clipboard}}",
  "seasoning": 30
}
```

**Headers:**

| Key | Value |
|---|---|
| Content-Type | application/json |
| Authorization | Bearer `<API_TOKEN>` (設定している場合) |

**Response Parsing:**

- `{{json_body.result}}` を「クリップボードにコピー」で設定

---

### 2. 遅延同期ショートカット（オフライン用）

#### 2a. ジョブ登録 (Enqueue)

| 項目 | 値 |
|---|---|
| **Name** | Flow AI - Enqueue |
| **Method** | POST |
| **URL** | `http://<サーバーURL>:8000/sync/enqueue` |
| **Body Content** | `{"text": "{{clipboard}}", "seasoning": 30}` |

**Response:**

- `{{json_body.job_id}}` を変数に保存

#### 2b. 処理実行 (Process)

| 項目 | 値 |
|---|---|
| **Name** | Flow AI - Sync Process |
| **Method** | POST |
| **URL** | `http://<サーバーURL>:8000/sync/process?limit=10` |

**使い方:**

- ネットワーク復帰後に手動で実行、または Tasker 連携で自動実行

#### 2c. 結果取得 (Status)

| 項目 | 値 |
|---|---|
| **Name** | Flow AI - Sync Status |
| **Method** | GET |
| **URL** | `http://<サーバーURL>:8000/sync/status/{{job_id}}` |

---

## トリガー設定 (オプション)

### Tasker 連携

1. **ネットワーク復帰時に `/sync/process` を呼ぶ**
    - Tasker プロファイル: State → Net → Wifi Connected
    - タスク: HTTP Shortcuts アクション → "Flow AI - Sync Process"

2. **共有メニューからの起動**
    - HTTP Shortcuts の「Advanced Settings」→「Accept shared data」を有効化

---

## トラブルシューティング

| 症状 | 原因 | 対策 |
|---|---|---|
| 接続エラー | サーバー未起動 | `uvicorn` を起動 |
| 401 Unauthorized | トークン不一致 | `.env` の `API_TOKEN` を確認 |
| タイムアウト | ネットワーク問題 | Cloudflare Tunnel の状態を確認 |

---

## 参考リンク

- [HTTP Shortcuts 公式ドキュメント](https://http-shortcuts.rmy.ch/)
- [Tasker](https://tasker.joaoapps.com/)
