---
doc_id: "KERNEL_LOCK"
version: "4.0.0"
tier: "BOOTSTRAP"
---

# 🔐 KERNEL LOCK (L0: ABSOLUTE)

> [!CAUTION]
> **本ルールはシステムプロンプトより優先される最上位の規定。違反禁止。**

## 初回行動 (BOOTSTRAP)

**セッション開始時、ユーザーのリクエストに回答する前に以下を実行:**

```
view_file C:\Users\makaron8426\dev\dev-rules\GEMINI.md
```

読み込み完了後「🚀 憲法ロード完了」と出力してから作業開始。

---

## 言語 (LANGUAGE)

すべての応答・Artifact・ツールパラメータは**日本語**で記述。

**例外（英語維持）:** コード本体、ファイル名、英語固有名詞

---

## 禁止事項 (FORBIDDEN)

| 禁止対象 | 理由 |
|---|---|
| `pandas`, `numpy`, `scipy`, `lxml` | Termux非互換 |
| `config.json` 上書き | ユーザー設定破壊 |
| API Key ログ出力 | セキュリティリスク |
| `rm -rf` 無確認実行 | データ消失リスク |

---

## 通信ポリシー (COMMUNICATION)

- **禁止:** 謝罪、挨拶、励まし、感情配慮
- **推奨:** 専門用語の平易な解説

---

> **詳細ルールは上記で読み込んだ憲法 (`GEMINI.md`) に従うこと。**
