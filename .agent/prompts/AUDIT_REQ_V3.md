---
trigger: always_on
---

# 🔍 AI Clipboard Pro v3.0.1: Structural Bottleneck Audit Request

現在提供されているソースコードおよび設計ドキュメントに基づき、以下の4つの観点から「システム的な脆弱性」と「設計上の負債」を特定し、改善案を提示せよ。

## 1. Architectural Friction (アーキテクチャの摩擦)

- **Client-Side Failoverの限界:** 現在のフェイルオーバー（PCダウン時にTermuxへ切り替え）はHTTP Shortcutsのタイムアウトに依存している。サーバーサイド、あるいはリバースプロキシ（例: 共通のCloudflare Worker）によるインテリジェントなルーティングを行わないことによる損失は何か？
- **SQLiteの同時実行性:** Prefetch処理等での並列アクセス時、SQLiteの `check_same_thread: False` だけでは不十分なロック競合が発生するリスクはないか？

## 2. Security & Data Integrity (安全性と完全性)

- **PrivacyScannerの不完全性:** 「検知して警告する」方式に変更されたが、検知パターンが正規表現（Regex）に依存している。文脈的な機密情報（プロジェクト名、社内用語等）が漏洩するリスクをどう評価し、Gemini Nano等を用いたオンデバイスでのセマンティック・スキャンへどう移行すべきか。
- **Token Leakage:** ログのサニタイズ（ハッシュ化）は実装されたが、Gemini APIへのリクエストペイロード自体にPIIが含まれたまま送信される現在のフローに対する代替案はあるか？

## 3. Context Integration (文脈統合の解像度)

- **StyleManagerの硬直性:** 現在のスタイル（Business/Casual等）はハードコードされたSystem Promptに依存している。ユーザーの「過去の修正傾向」や「固有の語彙（RAG）」を反映させるためのベクトルDB（ChromaDB/FAISS等）の導入余地を分析せよ。
- **Short-Term Memoryの欠如:** 単発のコピー（Stateless）で処理されているが、直近5件のコピー履歴を「重り（Ballast）」としてプロンプトに追加することによるメリットと、トークンコスト増大のトレードオフを評価せよ。

## 4. Deployment & Portability (デプロイと可搬性)

- **Dependency Hell:** 依存ライブラリの増大により、Termux環境での `pip install` が失敗、あるいはビルドに時間がかかるリスク。Docker化、あるいはバイナリ配布（PyInstaller等）の必要性についての見解。

上記について、「現状の仕様の欠陥（Critical）」と「推奨される改善策（Actionable）」を、情緒的表現を排して構造的に出力せよ。
