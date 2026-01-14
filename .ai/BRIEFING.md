# 📋 BRIEFING.md - Flow v4.0 現状サマリー

> **最終更新:** 2026-01-12
> **用途:** AI Studio秘書へのコンテキスト共有

---

## プロジェクト概要

| 項目 | 内容 |
|------|------|
| **名称** | Flow v4.0 |
| **概要** | テキスト前処理ツール（クリップボード→LLM→出力） |
| **開発環境** | Antigravity IDE (GCP C3-8 / N2-16) |
| **本番環境** | Android Termux |

---

## 現在のフェーズ

**環境整備完了 → 開発フェーズ移行**

---

## 直近の意思決定

| 日付 | 決定事項 |
|------|----------|
| 01-07 | AI協働アーキテクチャ v2.0 確定 |
| 01-12 | Protocol D-Extended 実装（存在系断言禁止） |
| 01-12 | GEMINI.md 両環境同期完了 |

---

## 技術スタック

| 層 | 技術 |
|----|------|
| API | FastAPI + Uvicorn |
| LLM | Gemini 3 Flash/Pro |
| DB | SQLite (WAL mode) |
| GUI | Flet (PC only) |

---

## Termux制約

- `pandas`, `numpy`, `scipy`, `lxml` 禁止
- Pure Python優先
- メモリ・バッテリー効率重視

---

## 開発中機能

| 機能 | 状態 |
|------|------|
| PrivacyScanner v4.1 | 実装済み（API Key/Password/JP_Address検出） |
| カスタム語彙連携 | 実装済み（vocab_store） |
| Gemini Nano統合 | 設計書のみ（未実装） |
| TEALS連携 | 未着手 |

---

## 参照ドキュメント

- `CONSTITUTION.md` - 開発規約
- `ARCHITECTURE.md` - システム構成
- `.agent/workflows/global-rules.md` - グローバルルール
