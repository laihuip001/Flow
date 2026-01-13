---
description: セッション終了時に開発日記エントリを自動生成・追記する
triggers:
  - session_start_date_change  # 日付が変わった最初のセッションで自動実行
---

# /diary Workflow

## ⚡ Auto-Trigger (自動実行)

**このワークフローは以下の条件で自動実行される:**

1. **セッション開始時に日付が変わっていた場合:**
   - 前回セッションの日付と現在日付を比較
   - 異なる場合、前日のwalkthroughを参照して日記を自動生成

2. **実行条件:**
   - `brain/<conversation-id>/walkthrough.md` が存在する
   - 当該日付の日記エントリがまだ存在しない

> [!IMPORTANT]
> **AIエージェントへの指示:** セッション開始時、現在日付の日記ファイル `dev-rules/diary/YYYY-MM-DD.md` が存在しない場合、直近のwalkthroughから日記を自動生成せよ。

セッション終了時に、本セッションの成果・教訓を開発日記に自動追記する。

## Usage

```
/diary
```

## Steps

1. **セッション情報の収集（マルチIDE統合）**

   以下の情報源から両IDE（Architect/Constructor）の作業内容を統合:

   | Source | Location | Content |
   |---|---|---|
   | **Architect walkthrough** | `~/.gemini/antigravity/brain/*/walkthrough.md` | 設計・計画の成果 |
   | **Constructor walkthrough** | 同上（別アカウント） | 実装・テストの成果 |
   | **Git commits** | `git log --since="yesterday"` | 両IDE共通のコミット履歴 |
   | **Briefing** | `GoogleDrive/Flow_AI_Sync/BRIEFING.md` | 相互引き継ぎ情報 |

   > [!NOTE]
   > Constructor側のwalkthroughは `git pull` 後、またはGoogle Drive同期で取得

2. **日記エントリ生成**
   - 日付ファイル `diary/YYYY-MM-DD.md` の存在確認
   - 存在しない場合: TEMPLATE.md を参考に新規作成
   - 存在する場合: 既存内容に追記

3. **エントリ構造**

   ```markdown
   ## 📝 Summary
   [セッションの概要を1-2文で]

   ## 📁 File Changes
   [変更ファイル一覧]

   ## 🎯 Decisions
   [重要な設計判断]

   ## 💡 Learnings
   [教訓・学び]

   ## ➡️ Next Steps
   [次のアクション]
   ```

4. **保存先**
   - Path: `C:\Users\laihuip001\dev\dev-rules\diary\YYYY-MM-DD.md`
   - 同日に複数セッションがある場合は追記

## Notes

- このワークフローはセッション終了時に手動で `/diary` と入力して実行
- コミット履歴ベースの `run_diary.ps1` とは別の高レベル日記
- Artifactから教訓を抽出するため、walkthrough.md の作成を推奨
