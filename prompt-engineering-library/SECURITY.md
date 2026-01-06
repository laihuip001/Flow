# 🔐 AI Clipboard Pro v3.0.1 セキュリティガイド

## 概要

このドキュメントは、AI Clipboard Proを安全に運用するためのガイドラインです。

---

## 🚨 重要な警告

> **インターネットに公開する前に必ず認証を有効にしてください！**
>
> 認証なしで公開すると、第三者があなたのGemini APIクォータを使い放題になります。

---

## 🔐 認証の設定

### 1. トークンの生成

安全なランダムトークンを生成:

```bash
# Linux/Mac
openssl rand -hex 32

# Windows PowerShell
-join ((1..32) | ForEach-Object { '{0:x2}' -f (Get-Random -Maximum 256) })
```

### 2. 環境変数の設定

`.env` ファイルを作成:

```
GEMINI_API_KEY=your_gemini_api_key
API_TOKEN=your_generated_token_here
```

### 3. クライアント側の設定

HTTP Shortcutsでヘッダーを追加:

```
Authorization: Bearer your_generated_token_here
```

---

## 🛡️ エンドポイント別の認証要件

| エンドポイント | 認証 | 説明 |
|--------------|------|------|
| `GET /` | 不要 | ヘルスチェック |
| `GET /healthz` | 不要 | 詳細ヘルスチェック |
| `GET /styles` | 不要 | スタイル一覧 |
| `POST /scan` | 不要 | 個人情報検知 |
| `POST /process` | **必要** | メイン処理 |
| `POST /prefetch` | **必要** | 先読み |
| `GET /prefetch/{hash}` | 不要 | 結果取得 |

---

## 📝 ログのセキュリティ

v3.0.1では、ログに個人情報が含まれないよう設計されています:

**Before (危険):**
```
📩 受信: お世話になっております。山田太郎です。電話番号は090-1234-5678...
```

**After (安全):**
```
📩 処理開始: [text:a1b2c3d4...len=128] style=business
```

---

## 🏥 ヘルスチェック

監視ツール（UptimeRobot等）向けのエンドポイント:

```
GET /healthz
```

レスポンス例:
```json
{
  "status": "running",
  "version": "3.0.1",
  "timestamp": "2026-01-04T05:00:00.000000",
  "auth_enabled": true,
  "checks": {
    "api": "ok",
    "gemini": "configured",
    "database": "ok"
  }
}
```

---

## ⚠️ Safety Filter対応

Gemini APIの安全フィルターによりブロックされた場合:

```json
{
  "error": "safety_blocked",
  "message": "安全上の理由でブロックされました",
  "action": "テキストを修正して再試行してください"
}
```

クライアント側でこのエラーを適切に表示してください。

---

## 📋 チェックリスト

本番環境にデプロイする前に確認:

- [ ] `API_TOKEN` が設定されている
- [ ] `.env` ファイルが `.gitignore` に含まれている
- [ ] HTTPS経由でのみアクセス可能（ngrok/Cloudflare Tunnel使用時は自動）
- [ ] ログファイルへのアクセスが制限されている
- [ ] 定期的にトークンをローテーションする計画がある
