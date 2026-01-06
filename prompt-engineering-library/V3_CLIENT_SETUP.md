# 📱 AI Clipboard Pro v3.0 クライアント設定ガイド

**"The Unbreakable Hybrid"** 構成を実現するための設定手順です。

## 🎯 目標
1.  **Grid Menu:** コピー後にスタイル（ビジネス/カジュアル等）を選べるメニューを出す。
2.  **Failover:** PC/Cloudがダウンしていても、自動でTermuxに切り替わる。

---

## 🛠 ステップ 1: Termux用ショートカット (Local)

これが「最後の砦（バックアップ）」になります。

1.  **HTTP Shortcuts** で新規作成
2.  **名前:** `AI_Local`
3.  **URL:** `http://localhost:8000/process`
4.  **メソッド:** `POST`
5.  **Body (JSON):**
    ```json
    {
      "text": "{clipboard}",
      "style": "{style_variable}" 
    }
    ```
    ※ `{style_variable}` は後で作る変数です。一旦適当な文字でもOK。

---

## 🛠 ステップ 2: PC/Cloud用ショートカット (Main)

これが「メイン（高速・高性能）」になります。

1.  **HTTP Shortcuts** で新規作成
2.  **名前:** `AI_Main`
3.  **URL:** `https://your-cloud-url.com/process` (またはPCのIP)
4.  **メソッド:** `POST`
5.  **Body:** `AI_Local` と同じ
6.  **⚠️ 重要: フェイルオーバー設定**
    *   ショートカット編集画面の「実行後の操作 (Response)」タブへ
    *   **「失敗時 (On Error)」** → **「他のショートカットを実行」**
    *   **`AI_Local`** を選択
    *   **「タイムアウト」** (高度な設定) を `500` (ms) に設定

---

## 🛠 ステップ 3: メニューの作成 (Entry Point)

ユーザーが最初にタップするショートカットです。

1.  **HTTP Shortcuts** で新規作成
2.  **名前:** `AI Clipboard` (ホーム画面に置くやつ)
3.  **タイプ:** 「マルチショートカット (Multi-Shortcut)」または「スクリプト」
    *   ※一番簡単なのは、このショートカットの実行前変数でスタイルを聞くこと

**推奨設定 (変数を使う方法):**

1.  `AI_Main` のBodyにある `{style_variable}` をタップ
2.  「変数を追加」→「選択リスト (Enum)」
3.  **名前:** `Select Style`
4.  **選択肢:**
    *   `business` (ビジネス)
    *   `casual` (カジュアル)
    *   `summary` (要約)
    *   `english` (翻訳)
    *   `proofread` (校正)
5.  これで、`AI_Main` を実行するとメニューが出て、選ぶと送信されます。
6.  失敗したら自動で `AI_Local` が同じ変数を使って実行されます。

---

## 🚦 Pre-Fetch スイッチ (MacroDroid)

1.  **トリガー:** クリップボード更新
2.  **条件:** 変数 `AI_Prefetch` = True
3.  **アクション:** HTTPリクエスト (`POST /prefetch`)
    *   URL: `http://localhost:8000/prefetch` (ローカルだけで十分)
    *   Body: `{"text": "{clipboard}", "target_styles": ["business", "casual"]}`

これで、スイッチONの時だけ裏でTermuxが準備運動します。

---

## 📊 利用可能なスタイル

| スタイルID | 名前 | 説明 |
|-----------|------|------|
| `business` | ビジネス | 丁寧・フォーマル |
| `casual` | カジュアル | フランク・絵文字あり |
| `summary` | 要約 | 箇条書き・簡潔 |
| `english` | 英語翻訳 | ビジネス英語 |
| `proofread` | 校正 | 誤字脱字修正のみ |

---

## 🔧 トラブルシューティング

### サーバーが起動しない
```bash
pip install -r requirements.txt
python main.py
```

### APIキーエラー
`.env` ファイルを作成し、以下を記載:
```
GEMINI_API_KEY=your_actual_api_key
```

### フェイルオーバーが動作しない
HTTP Shortcutsの「タイムアウト」設定を確認してください（500ms推奨）。
