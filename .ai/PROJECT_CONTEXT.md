# 🤖 Antigravity Agent Context: SE就職プロジェクト

> **Last Updated:** 2026-01-06
> **Owner:** The Architect (24歳、横浜SE就職希望)
> **Goal:** 2026年4月までに横浜またはリモートでSE内定獲得

---

## 1. User Profile（必読）

### 1.1 認知特性: AuDHD (ASD + ADHD)

| 特性 | 影響 | 対応方法 |
|:--|:--|:--|
| **ASD** | 曖昧な指示でフリーズ、構造化必須 | 明確な定義、A or B形式の提案 |
| **ADHD** | 興味駆動、90%完了で満足 | タスクを「実験」「攻略」としてフレーミング |
| **強み** | 過集中、爆発的学習速度、論理的思考 | 興味を引く課題設定 |

### 1.2 コミュニケーション要件

```yaml
Required:
  - 結論から述べる（Act Mode）
  - 仮説提示型（A案/B案形式）
  - コピペで動くコード出力
  - 推論プロセスの開示

Prohibited:
  - 情緒的共感（「お辛いですね」等）
  - 曖昧な質問（「どう思いますか？」）
  - 冗長な前置き・繰り返し
  - 根拠なき断定
```

### 1.3 背景情報

- **保有資格:** 日商簿記1級（独学半年で合格）
- **学習中:** 応用情報技術者（2026年4月試験予定）
- **経歴リスク:** 元受刑者（刑務所を「学習キャンプ」として活用）
- **強み:** 簿記1級の内部統制知識、設計力、AI指揮能力

---

## 2. Project Overview

### 2.1 ポートフォリオ2件

| Project | 概要 | 技術 | GitHub |
|:--|:--|:--|:--|
| **TEALS** | 改ざん検知機能付き監査ログシステム | Python, SQLAlchemy, SHA-256 | https://github.com/laihuip001/test |
| **AI-Clipboard-Pro** | AIテキスト処理ミドルウェア | FastAPI, Pydantic v2, Gemini API, Flet | https://github.com/laihuip001/AI-Clipboard-Pro |

### 2.2 AI-Clipboard-Pro 現状

```yaml
Version: v4.0 Titanium Edition
Status: 開発中（/process 500エラー調査中）
Architecture: Titanium Architecture（Strategic/Execution/Runtime分離）
Final Goal: Google Play配布/販売
```

**現在の課題:**
```
POST /process → 500 Internal Server Error
原因候補:
1. config.py の MODEL_FAST 値（gemini-1.5-flash → gemini-2.0-flash?）
2. .env の GEMINI_API_KEY 無効/期限切れ
3. google.genai SDK の仕様変更
```

---

## 3. 就職戦略: 2軸ハイブリッド

### 3.1 ターゲット市場

| 軸 | ターゲット | アピール | 求人媒体 |
|:--|:--|:--|:--|
| **A. 横浜出社型** | SIer・社内SE（金融/会計系） | 簿記1級 × TEALS × コンプライアンス | doda, Green, ハローワーク |
| **B. リモート型** | AI活用スタートアップ | AI-Clipboard-Pro × 設計力 | Wantedly, LAPRAS, Findy |

### 3.2 面接ナラティブ

```
「私の強みは『設計力』と『AI指揮能力』です。

【TEALS】
簿記1級の『訂正仕訳原則』をハッシュチェーンで実装。
過去の経験から、透明性とルール遵守の重要性を深く理解しています。

【AI-Clipboard-Pro】
Google Antigravityを活用し、5日間でFastAPI + Flet GUIの
ハイブリッドアプリを構築。
Strategic Layer（設計）とExecution Layer（AI実装）を分離する
『Titanium Architecture』を採用しています。

2025年のエンジニアリングで重要なのは、
全てを自分で書くことではなく、
『何を作るべきか』を定義し、AIと協働して実現する能力です。」
```

### 3.3 経歴説明スクリプト（2分間）

```
1. 導入（15秒）：「過去に過ちを犯し、服役経験があります」

2. 転換（30秒）：「その環境で簿記1級を独学半年で取得。
   遮断環境でも自律学習できることの証明です」

3. 昇華（45秒）：「だからこそ『ルール遵守』『透明性担保』の
   重要性を深く理解しています。
   TEALSはその思想をコードで具現化したものです」

4. 着地（30秒）：「貴社の開発でも『信頼をエンジニアリングする』
   姿勢で貢献します」
```

---

## 4. Timeline

| Phase | 期間 | タスク | Status |
|:--|:--|:--|:--|
| **1a** | 1/6〜1/10 | AI-Clipboard-Pro 500エラー修正 | 🔄 In Progress |
| **1b** | 1/6〜1/10 | 両リポジトリ整備（README、バッジ） | ⏳ Pending |
| **2** | 1/11〜1/20 | 履歴書・職務経歴書作成（2パターン） | ⏳ Pending |
| **3** | 1/21〜2/15 | 応募（A軸5社、B軸10社） | ⏳ Pending |
| **4** | 2/16〜3/31 | 面接、内定獲得 | ⏳ Pending |

---

## 5. Coding Guidelines（AI-Clipboard-Pro用）

### 5.1 Termux Compatibility

```yaml
Environment: Android Termux (aarch64)
Constraints:
  - メモリ制限あり（重厚ライブラリ禁止）
  - バッテリー制約（常時稼働の効率化必須）
  - Python 3.10+
```

### 5.2 Core Principles

1. **Robustness over Magic:** 「魔法のように動く」より「エラー時に何が起きたか明確」を優先
2. **Failover First:** 常に「オフライン時」「APIダウン時」の挙動を考慮
3. **Type Safety:** Pydanticモデル + Type Hint厳密使用
4. **90% is Done:** 完璧を求めない。動くものを優先

### 5.3 Security Requirements

```yaml
Authentication: Bearer Token (API_TOKEN)
PII Handling: ログ出力時はハッシュ化、自動マスク廃止（検知のみ）
Safety Filter: Gemini Safety Block時の適切なハンドリング
```

---

## 6. 現在のタスク指示

### 6.1 最優先: 500エラー修正

```
1. config.py を開き、MODEL_FAST の値を確認
2. 現在の値が "gemini-1.5-flash" なら "gemini-2.0-flash" に変更
3. .env の GEMINI_API_KEY が有効か確認
4. python main.py を実行し、エラーログを取得
5. /process エンドポイントをテスト
```

### 6.2 次: リポジトリ整備

```
1. TEALSリポジトリ名を "test" → "TEALS" に変更
2. Description追加: "改ざん検知機能付き監査ログシステム"
3. Topics追加: python, sqlalchemy, blockchain, audit-log, sha256
4. README.mdに英語セクション追加
```

---

## 7. Available Tools

| Tool | Purpose | When to Use |
|:--|:--|:--|
| **Google AI Pro (Gemini)** | Deep Research | 志望企業調査、業界トレンド |
| **Claude Pro** | 壁打ち・コードレビュー | 設計相談、面接スクリプト推敲 |
| **Antigravity** | バイブコーディング | 実装、デバッグ |
| **Firebase Studio** | 従来型コーディング | 細かい修正 |
| **Manus** | エージェント | 求人情報自動収集 |
| **Canva** | デザイン | 履歴書、ポートフォリオサマリー |

---

## 8. Quick Reference

### API Endpoints (AI-Clipboard-Pro)

| Endpoint | Method | Auth | Description |
|:--|:--|:--|:--|
| `/process` | POST | Bearer | テキスト変換（メイン機能） |
| `/prefetch` | POST | Bearer | 先読みキャッシュ |
| `/scan` | POST | None | PII検知（警告のみ） |
| `/healthz` | GET | None | ヘルスチェック |

### File Structure (AI-Clipboard-Pro)

```
AI-Clipboard-Pro/
├── main.py          # FastAPIサーバー
├── logic.py         # AI処理ロジック（Gemini呼び出し）
├── config.py        # 設定（MODEL_FAST等）
├── models.py        # Pydantic/SQLAlchemyモデル
├── database.py      # DB接続
├── flet_app/        # GUI（Flet）
│   └── main.py
├── .ai/             # エージェント用コンテキスト
│   ├── SYSTEM_CONTEXT.md
│   └── JULES_TASK.md
└── maintenance/
    └── titanium_watcher.sh
```

---

**End of Context Document**

*このドキュメントをAntigravityの新規セッション開始時に貼り付けてください*
