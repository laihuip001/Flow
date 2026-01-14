# 📋 ARCHITECT → CONSTRUCTOR 引き継ぎ指示書

> **発行日:** 2026-01-13
> **発行者:** Architect IDE (C3-8 / laihuip001)
> **対象:** Constructor IDE (N2-16 / makaron8426)

---

## 1. 本指示書の目的

設計担当IDE（Architect）と実装担当IDE（Constructor）間で、**IDE設定とワークフローをGitHubで一元管理**するための構造変更を行った。本書はその変更内容と、Constructor側で必要な対応を記載する。

---

## 2. 背景: なぜこの変更が必要か

| 課題 | 解決策 |
|---|---|
| IDE設定（GEMINI.md等）がリポジトリ外にあり、GitHub経由で共有できなかった | リポジトリ内 `Flow/.gemini/` に配置 |
| `.agent/rules/` の名称が曖昧だった | `.agent/prompts/` にリネームして役割を明確化 |
| 両IDEが独自の設定を持ち、「以心伝心」ができなかった | シンボリックリンクで単一ソースを参照 |

---

## 3. 新しいファイル構造

```
Flow/
├── .gemini/                    # IDE設定層（GitHub管理）
│   ├── GEMINI.md               # ★ グローバルAI動作規範（憲法）
│   └── rules.md                # プロジェクト固有コーディング規約
│
└── .agent/                     # エージェント動作層（GitHub管理）
    ├── prompts/                # ★ RENAMED (旧: rules/)
    │   ├── pronpt.md
    │   └── rule.md
    └── workflows/
        ├── [C]-rules.md
        ├── flow-dev-ecosystem.md
        ├── hihyou.md
        └── load.md
```

---

## 4. Constructor側で必要な作業

### 4-1. リポジトリ同期

```bash
cd C:\Users\makaron8426\dev\Flow
git pull origin main
```

### 4-2. シンボリックリンク作成（管理者PowerShell）

IDEは `~/.gemini/GEMINI.md` を読み込むため、リポジトリ版へのシンボリックリンクを作成：

```powershell
# 旧ファイルを削除
Remove-Item "$env:USERPROFILE\.gemini\GEMINI.md" -Force -ErrorAction SilentlyContinue

# シンボリックリンク作成
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.gemini\GEMINI.md" -Target "C:\Users\makaron8426\dev\Flow\.gemini\GEMINI.md"
```

### 4-3. 動作確認

1. IDE（Antigravity）を再起動
2. 新しいチャットで `GEMINI.md` の内容が反映されているか確認
3. `/load` コマンドが正常に動作するか確認

---

## 5. 設計思想: OS層 / App層

| Layer | Contents | Sync Policy |
|---|---|---|
| **OS層** | `GEMINI.md`, `global-rules.md` | 両IDE共通。変更にはCEO承認必須。|
| **App層** | `[C]-rules.md`, 各ワークフロー | 役割に特化。独立運用だが相互参照可。|

**原則:** OS層の変更は必ずGitHub経由でコミットし、両IDEで `git pull` して同期すること。

---

## 6. 注意事項

> [!CAUTION]
> **以下のファイルは共有禁止。各IDE独自に管理すること：**
>
> - `~/.gemini/oauth_creds.json` (認証トークン)
> - `~/.gemini/google_accounts.json` (アカウント情報)

---

## 7. 参照ドキュメント

| Document | Location |
|---|---|
| AI動作規範 | [GEMINI.md](file:///C:/Users/makaron8426/dev/Flow/.gemini/GEMINI.md) |
| プロジェクト規約 | [rules.md](file:///C:/Users/makaron8426/dev/Flow/.gemini/rules.md) |
| エコシステム定義 | [flow-dev-ecosystem.md](file:///C:/Users/makaron8426/dev/Flow/.agent/workflows/flow-dev-ecosystem.md) |
| Constructor行動規範 | [[C]-rules.md](file:///C:/Users/makaron8426/dev/Flow/.agent/workflows/[C]-rules.md) |

---

*本指示書に不明点があれば、Architect IDE（laihuip001）に確認すること。*
