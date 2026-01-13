---
description: セッション開始時にリポジトリを自動同期する
triggers:
  - session_start  # 毎セッション開始時に自動実行
---

# Auto-Sync Workflow

## 目的

セッション開始時に `git pull` を自動実行し、両IDE間のワークフロー・設定を常に最新状態に保つ。

## 動作

**Constructor側（実装担当）:**

```bash
cd ~/dev/Flow && git pull origin main --quiet
```

**Architect側（設計担当）:**
Protocol G適用のため、以下を**ユーザーに提示**:

```
⚠️ リポジトリ同期が必要です: git pull origin main
```

## AIエージェントへの指示

> [!IMPORTANT]
> **セッション開始時、以下を実行せよ:**
>
> 1. `[A]-protocol-g.md` が存在するか確認
> 2. 存在する（Architect）: ユーザーに `git pull` を促すメッセージを表示
> 3. 存在しない（Constructor）: `git pull origin main` を自動実行

これにより、ワークフローの変更は**次回セッション開始時に自動反映**される。
