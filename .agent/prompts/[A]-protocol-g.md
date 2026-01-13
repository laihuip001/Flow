# Protocol G: Git Operation Prohibition (Architect Only)

> **適用対象:** 設計担当IDE（C3-8 / laihuip001）のみ
> **理由:** 本環境ではGitコマンド実行時にIDEがハングする既知の問題がある

---

## ルール

Agent による Git コマンド (`git add`, `commit`, `push`, `status`, etc.) の**直接実行を禁止**する。

1. **基本ルール:** Git操作は環境固有の問題（ハング）があるため、**必ずユーザーに実行させる**。
2. **アクション:** `run_command` で Git コマンドを実行する代わりに、実行すべきコマンドを提示し、ユーザーに手動実行を依頼せよ。
3. **例外:** なし。

---

## 注意

- このルールは **設計担当IDE専用** のApp層設定です。
- 実装担当IDE（Constructor）には適用されません。
- OS層（`GEMINI.md`）には含めないこと。
