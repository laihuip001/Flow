# 🤖 AI Clipboard Pro: Context Restoration Protocol

**次のセッションで、以下のプロンプトを新しいAIチャットに貼り付けてください。**
これにより、現在の開発状況（v2.6）、決定事項、および次のアクションプランが復元されます。

---
(ここから下をコピー)

あなたは「AI Clipboard Pro」の専任開発パートナーです。
以下のコンテキストを引き継ぎ、開発を再開してください。

## 📍 プロジェクト状況: v2.6 (Safety Update)

- **現在のフェーズ:** 実装完了・検証フェーズ
- **直近の成果:** v2.6 安全化アップデートの実装完了
  - `PrivacyScanner` (個人情報検知・警告のみ、自動置換廃止)
  - `/scan` エンドポイント
  - `/process/multi` (3選択肢UI: フォーマル/カジュアル/要約)
- **次の目標:** v2.6の動作検証 & v2.7 (オフライン対応・安定化) の計画

## 🔑 キーファイルと設計思想

- `main.py`: FastAPIサーバー (Tags: v2.6 Safety)
- `logic.py`: コアロジック (PrivacyScannerは検知のみ。ContextBallastでアプリ判定)
- `setup_project.py`: **復元用インストーラー** (全ソースコードを含む)
- `COMPLETE_ARCHIVE.md`: ブレスト全記録 (課題・アイデア・ロードマップ)

## 🚧 重要な決定事項 (Design Decisions)

1. **Safety First:** `PrivacyWrapper`の自動mask/unmask機能は「データ消失リスク(Detokenization Fallacy)」があるため**廃止**しました。現在は「検知して警告」のみです。
2. **UX Shift:** AIを育てるのではなく、ユーザーに「3つの案から選ばせる」方式にシフトしました (`/process/multi`)。
3. **Architecture:** MacroDroid依存からの脱却を目指し、堅牢なAPIサーバー化を進めています。

## 📝 直近のネクストアクション

1. `setup_project.py` を実行して環境を復元する
2. `/process/multi` エンドポイントを実際のHTTP Shortcutsからテストする
3. `KNOWN_ISSUES_AND_ROADMAP.md` に基づき、v2.7のオフラインフォールバック検討を開始する

---
(ここまで)
