# 🚩 変更履歴 (CHANGELOG)

AI Clipboard Pro の進化の経緯

---

## 🏆 コンセプト

このシステムは、単なる「文章作成ツール」ではありません。
**「ユーザーの状況（アプリ）と意図（コピー）を察知し、先回りして思考を整理してくれる、影の参謀」** です。

- **プライバシー:** 個人情報を漏らさない安心感
- **スピード:** 使いたい時には既に答えがある（0秒待機）
- **コンテキスト:** Slackではフランクに、メールでは丁寧に、勝手に切り替わる

---

## 📅 バージョン履歴

### v4.0 - Seasoning Spectrum 🆕

**「0-100の連続スペクトラムで下処理を制御」**

#### ✨ Core Changes

- **Seasoning Spectrum:** 離散スタイル（business/casual等）を廃止し、0-100連続値に移行
  - Light (0-40): 誤字修正のみ、素材を最大限活かす
  - Medium (41-70): 標準的な構造整理
  - Rich (71-90): 積極的な補完・強化
  - Deep (91-100): 深い文脈理解、インキュベーション
- **SeasoningManager:** 新規クラス。レベルに応じたシステムプロンプト生成
- **PII Masking:** `mask_pii/unmask_pii` でAPI送信前にPIIをプレースホルダに置換

#### 🔧 Architecture

- **CoreProcessor:** 統合処理クラス（Gemini API呼び出し + マスク処理）
- **日本語プロンプト最適化:** 日本語入力には日本語指示で精度向上

---

### v3.0.1 - Production Ready

**「壊れない道具への進化」**

#### 🛡️ Security

- **Bearer Token認証:** `/process` と `/prefetch` に認証機構を追加
- **ログ浄化:** 入力テキストをハッシュ化し、PIIのログ出力を防止
- **Safety Filterハンドリング:** Geminiのブロック理由を適切にエラーレスポンスで返却

#### ✨ New Features

- **`GET /healthz`:** 詳細ヘルスチェック（監視ツール向け）
- **`GET /styles`:** 利用可能なスタイル一覧
- **`StyleManager`:** 5つのプリセットスタイル（business/casual/summary/english/proofread）

#### 🔧 Architecture

- **アプリ名依存排除:** `ContextBallast` → `StyleManager` へ簡素化
- **ハイブリッドモード設計:** ローカル/クラウドの切り替え基盤

#### 📚 Documentation

- `SECURITY.md` - セキュリティガイド
- `V3_CLIENT_SETUP.md` - クライアント設定ガイド
- `test_v3.py` - 自動検証テストスイート

---

### v2.6 - Safety Update

**「毎日使っても壊れない道具へ」**

- 🛡️ `PrivacyScanner` クラス追加（検知のみ、置換しない）
- `POST /scan` - 個人情報スキャン（警告ダイアログ用）
- `POST /process/multi` - 3選択肢UI（フォーマル/カジュアル/要約）
- ⚠️ `PrivacyWrapper` 非推奨化（データ消失リスク回避）

### v2.5 - Context Ballast Edition

**「アプリに応じてAIが空気を読む」**

- ⚓ `ContextBallast` クラス追加
- `current_app` パラメータでアプリ名を送信
- Slack/Gmail/Twitter等に応じて自動でトーン・形式を最適化

### v2.4 - Pre-Fetch Edition

**「待ち時間ゼロの先読み」**

- 🚀 `PrefetchCache` テーブル追加
- `POST /prefetch` - Fire-and-Forget で先読み実行
- `GET /prefetch/{hash}` - キャッシュから即座に結果取得
- 複数タスクの並列実行 (`asyncio.gather`)

### v2.3 - Tone & Format

**「出力形式と口調の制御」**

- 🎨 `output_format` パラメータ追加 (plain/markdown/json)
- 🎭 `tone` パラメータ追加 (polite/casual/academic/bullet)
- 🌐 `target_language` で出力言語指定

### v2.2 - Preset System

**「自分専用のコックピット」**

- 💾 `Preset` テーブル追加
- プリセット CRUD API (`POST/GET/DELETE /presets`)
- `preset_id` で設定を呼び出し
- 🗜️ `info_valve` スライダー化 (-1.0 ~ +1.0)

### v2.1 - Safety & Control

**「安心と制御」**

- 🛡️ `PrivacyWrapper` クラス追加（個人情報マスキング）
- 🌡️ `temperature` 感情スライダー追加
- 🗜️ `use_info_valve` 情報バルブ追加

### v2.0 - Foundation

**「土台構築」**

- 非同期エージェント (Deep Research)
- SQLiteでジョブ管理
- コスト見積もり機能
- Auto Mode (AIが最適なモードを推奨)

---

## 📂 ファイル別の変更サマリー

### `models.py`

| 追加内容 | バージョン |
|---------|-----------|
| `Job` テーブル | v2.0 |
| `Preset` テーブル | v2.2 |
| `PrefetchCache` テーブル | v2.4 |
| `temperature`, `info_valve` | v2.1 |
| `output_format`, `tone` | v2.3 |
| `current_app` | v2.5 |

### `logic.py`

| 追加内容 | バージョン |
|---------|-----------|
| `PrivacyWrapper` クラス | v2.1 |
| `get_valve_instruction()` | v2.1 |
| `merge_config()` | v2.2 |
| `get_tone_instruction()` | v2.3 |
| `execute_single_task()` | v2.4 |
| `run_prefetch_background()` | v2.4 |
| `ContextBallast` クラス | v2.5 |

### `main.py`

| 追加エンドポイント | バージョン |
|------------------|-----------|
| `/analyze` | v2.0 |
| `/process/sync`, `/process/async` | v2.0 |
| `/jobs/{id}` | v2.0 |
| `/presets` | v2.2 |
| `/prefetch`, `/prefetch/{hash}` | v2.4 |
| `/ballast` | v2.5 |
