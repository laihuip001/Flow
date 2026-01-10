# 🧠 Flow AI v4.0 - システムコンテキスト
>
> 最終更新: 2026-01-10T10:06 JST
> 次セッションブートストラップ用にトークン最適化済み

---

## 1. セッションサマリー（2026-01-06）

### 完了タスク

- ✅ Titanium Guardianセキュリティ監査 - `YOUR_API_KEY_HERE` を削除
- ✅ 徹底的コード監査 - マジックナンバー → 定数化
- ✅ 構造的ボトルネック監査 - `/seasoning` エンドポイントを追加
- ✅ CONSTITUTION.md - コーディングスタイル規約（Section 6-7）を追加
- ✅ `.gemini/rules.md` - v4.0に更新
- ✅ テストファイル修正 - `style` → `seasoning` への移行
- ✅ 型ヒント - `processor.py` に追加
- ✅ README.md - ポートフォリオ向けに完全書き換え

### 保留中タスク

- ⏳ デモGIF録画（後日）
- ⏳ GitHub Actions CI設定
- ⏳ Flet GUIのクリーンアップまたは削除

---

## 2. アーキテクチャ概要

```
src/
├── core/      # processor.py, seasoning.py, privacy.py, gemini.py
├── api/       # main.py (FastAPI)
├── app/       # main.py, ui.py (Flet)
└── infra/     # database.py
```

エントリーポイント:

- `run_server.py` → FastAPI (ポート 8000)
- `run_app.py` → Flet Desktop

---

## 3. 今セッションの主な変更

| ファイル | 変更内容 |
|------|--------|
| `CONSTITUTION.md` | +Section 6（コーディング規約） |
| `.gemini/rules.md` | v4.0向けに完全書き換え |
| `README.md` | ポートフォリオ最適化版に書き換え |
| `processor.py` | 型ヒント追加、`styles` → `seasoning_levels` |
| `test_v3.py` | `/styles` → `/seasoning` |
| `blackbox_test.py` | 関数名変更 |
| `setup_titanium.py` | 災害復旧用に作成 |

---

## 4. 次セッションの優先事項

1. **デモ録画** - README用GIFを作成
2. **使用テスト** - Flow AIを1日使用し、フリクションポイントを記録
3. **Fletの判断** - GUIレイヤーを維持するか削除するか

---

## 5. 現在の構成

| キー | 値 |
|-----|-----|
| APIサーバー | 稼働中（ポート 8000） |
| バージョン | 4.0.0 |
| テスト状態 | すべてパス |
