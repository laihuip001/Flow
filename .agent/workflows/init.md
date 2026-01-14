---
description: セッション開始時に開発憲法（GEMINI.md）を読み込み、言語ルール等をコンテキストにロードする
---

# `/init` - セッション初期化

## 概要

新規セッション開始時に実行する初期化コマンド。
開発憲法（`GEMINI.md`）を読み込み、以下のルールを会話コンテキストの最新部分に配置することで、ルール遵守率を向上させる。

## 読み込まれる主要ルール

| ルール | 内容 |
|---|---|
| **LANGUAGE ENFORCEMENT** | すべての応答・成果物・ツールパラメータは日本語で行う |
| **COMMUNICATION POLICY** | 謝罪・挨拶・励まし等の非生産的出力を禁止 |
| **3原則** | Guard（守る）, Prove（証明する）, Undo（戻す） |
| **Mandatory Modules** | DMZ, Devil's Advocate, Rollback |
| **Forbidden** | Termux非互換ライブラリ、`config.json`上書き等 |

## 実行手順

// turbo-all

1. 開発憲法（`GEMINI.md`）を読み込む

```
view_file C:\Users\makaron8426\dev\dev-rules\GEMINI.md
```

1. 読み込み完了を確認し、以下を出力する

```
🚀 セッション初期化完了。開発憲法 v[バージョン] をロードしました。

**有効化されたルール:**
- 日本語強制
- 非生産的出力禁止
- 3原則 (Guard / Prove / Undo)
- Mandatory Modules (DMZ / Devil's Advocate / Rollback)

何から始めますか？
```

## 使用タイミング

- **新規会話開始時:** 必ず最初に `/init` を実行する運用を推奨
- **長時間セッション後:** コンテキストがリフレッシュされた場合に再実行

## 備考

このWorkflowは「言語ルール違反」等のAIミスを防ぐための**主防衛線**として設計されている。
`GEMINI.md` への追記（Last-Mile Checkpoint）は**バックアップ対策**として併用する。
