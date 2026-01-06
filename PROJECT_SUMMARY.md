# 📚 AI Clipboard Pro - プロジェクト全史＆構成ファイル一覧

本ドキュメントは、本プロジェクトのv1.0からの進化の過程、アーキテクチャの変遷、および現在存在するすべてのファイルについて網羅的に解説したものです。

---

## 📅 プロジェクトの歴史 (History)

### v1.0: 黎明期 (Prototype)

**「コピーした内容をAIで変換したい」** というシンプルな欲求からスタート。

- **構成**: Termux + Tasker + 単純なPythonスクリプト
- **課題**: セットアップが複雑で、スマホ単体で完結させるために無理な構成になっていた（依存関係のスパゲッティ化）。

### v2.0: 基礎構築 (Foundation)

**「仕事で使えるレベルへ」** を目指し、DBや非同期処理を導入。

- **機能**: SQLiteによるジョブ管理、コスト見積もり機能、Auto Modeの実装。
- **v2.1 - v2.3**: `temperature`（感情）、`info_valve`（情報量）、`tone`（口調）などのパラメータ制御を追加。
- **v2.4 (Pre-Fetch)**: 「待ち時間ゼロ」を目指し、コピーした瞬間に裏で推論を走らせる先読み機能を実装。
- **v2.5 (Context Ballast)**: アプリ名（Slack/Gmail等）に応じてAIが空気を読む機能を実装。
- **v2.6 (Safety)**: `PrivacyScanner` を導入し、個人情報流出リスクを可視化。

### v3.0: アーキテクチャ刷新 (Re-Architecture)

**「どこでも動くハイブリッドな頭脳」** へ。

- **変革**: 複雑すぎたTermux/Tasker依存（Daisy Chain）を撤廃。PCをメインサーバーとする「ハイブリッド設計」へ移行。
- **特徴**: アプリ名に頼らず、テキストの中身から文脈を推論するロジックへ変更。

### v3.0.1: 本番運用対応 (Production Ready) - **現在 (Current)**

**「壊れない、安全な道具」** としての完成形。

- **セキュリティ**: Bearer Token認証、ログの匿名化（PIIハッシュ化）。
- **信頼性**: Gemini Safety Filterへの完全対応、詳細なヘルスチェック、堅牢なエラーハンドリング。
- **UX**: Web GUIの搭載、デスクトップ用ワンクリックツールの整備。

---

## 📂 完全ファイルカタログ (Files)

現在プロジェクトに含まれる全ファイルの解説です。

### 1. サーバーコア (Server Core)

| ファイル名 | 説明 |
|:---|:---|
| `main.py` | **本体**。FastAPIサーバーのエントリーポイント。APIエンドポイント定義。 |
| `logic.py` | **頭脳**。Gemini API呼び出し、PIIスキャン、コンテキスト推論ロジック。 |
| `config.py` | **設定**。環境変数(.env)の読み込み、モデル設定、定数管理。 |
| `models.py` | **データ構造**。Pydanticモデル（リクエスト/レスポンス定義）とDBテーブル定義。 |
| `database.py` | **DB接続**。SQLiteとの接続セッション管理。 |
| `tasks.db` | **データベース**。SQLiteの実体ファイル。ジョブ履歴などを保存。 |
| `.env` | **秘密情報**。APIキーやトークンを保存（※Git管理外）。 |

### 2. クライアントツール (Client Tools)

#### Web GUI

| ファイル名 | 説明 |
|:---|:---|
| `static/index.html` | ブラウザから利用できる管理画面（HTML/CSS/JS）。 |

#### PC (Windows) 用

| ファイル名 | 説明 |
|:---|:---|
| `ai_convert.ps1` | **変換コア**。APIを叩いてクリップボードを更新するPowerShellスクリプト。 |
| `pc_clipboard.ps1` | 右クリックメニュー用スクリプト（旧バージョン互換）。 |
| `pc_clipboard_debug.ps1` | トラブルシューティング用の詳細ログ付きスクリプト。 |
| `AI_Clipboard.bat` | `pc_clipboard_debug.ps1` を実行するためのラッパーバッチ。 |
| `AI_Business.bat` | 「ビジネス」スタイルで変換するワンクリックボタン。 |
| `AI_Casual.bat` | 「カジュアル」スタイル用ボタン。 |
| `AI_Summary.bat` | 「要約」スタイル用ボタン。 |
| `AI_English.bat` | 「英語翻訳」スタイル用ボタン。 |
| `AI_Proofread.bat` | 「校正」スタイル用ボタン。 |

### 3. ドキュメント (Documentation)

| ファイル名 | 説明 |
|:---|:---|
| `USAGE_GUIDE.md` | **利用ガイド**。PC/Androidでの具体的なセットアップと使い方の説明書。 |
| `PROJECT_SUMMARY.md` | **本書**。プロジェクトの経緯と構成ファイル一覧。 |
| `SETUP_GUIDE.md` | v3.0.1の新規セットアップ手順書（ゼロからのインストール用）。 |
| `SECURITY.md` | セキュリティ設定（認証、ログ、Safety Filter）に関するガイドライン。 |
| `CHANGELOG.md` | バージョンごとの詳細な変更履歴。 |
| `V3_CLIENT_SETUP.md` | v3.0向けクライアント（HTTP Shortcuts）設定ガイド。 |
| `README.md` | プロジェクトのトップページ（概要）。 |
| `DEPLOYMENT.md` | デプロイに関するメモ。 |
| `KNOWN_ISSUES...` | 既知の問題とロードマップ。 |

### 4. セットアップ・開発用 (Setup & Dev)

| ファイル名 | 説明 |
|:---|:---|
| `setup_v3.py` | **インストーラー**。v3.0.1環境を自動構築するスクリプト。 |
| `requirements.txt` | 必要なPythonライブラリの一覧（pip用）。 |
| `test_v3.py` | **自動テスト**。APIの動作検証を行うテストスイート。 |
| `test_gemini.py` | Gemini API連携の単体テスト用スクリプト。 |
| `workflow_engine.py` | 開発用。ワークフローエンジン（※現状は未使用の可能性あり）。 |

### 5. レガシー・アーカイブ (Legacy/Archive)

※過去のバージョンで使用していたファイル群（参考用）

- `api.py`, `app.py`: 旧バージョンのサーバーファイル。
- `setup_project.py`: 旧インストーラー。
- `prompt_builder.py`, `prompt_registry.py`: 旧プロンプト管理システム。
- `ANDROID_SETUP.md`, `TERMUX_SETUP.md`: 旧モバイル環境セットアップガイド。

---

## 🚀 現在の到達点 (Current Status)

**「AI Clipboard Pro v3.0.1」** は、PC上の常駐サーバーとして動作し、以下の経路でいつでもどこでもAIを利用可能です。

1. **Webブラウザ**: GUIで直感的に操作
2. **PCデスクトップ**: アイコンダブルクリックで瞬時に変換
3. **Androidスマホ**: 自宅Wi-Fi内でHTTP Shortcutsから遠隔操作

安全性、速度、使い勝手のすべてにおいて、v1.0当初の構想を大きく超えるシステムへと進化しました。
