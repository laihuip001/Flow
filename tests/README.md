# tests/ ディレクトリ

## 構成

| パターン | 説明 |
|---|---|
| `test_*.py` | **pytest自動テスト** - `pytest tests/` で実行される |
| `run_*.py` | **手動実行スクリプト** - 開発者が手動で `python tests/run_*.py` |
| `blackbox_test.py` | ローカルサーバー起動状態でのE2Eテスト |

## 手動スクリプト一覧

- `run_stream.py` - ストリーミングAPIの動作確認
- `run_speed.py` - Geminiモデル別のレスポンス速度測定
- `run_quota.py` - API Quota状態の確認
- `run_user_text.py` - ユーザー入力テキストのテスト
- `run_benchmark_latency.py` - レイテンシベンチマーク
- `run_benchmark_privacy.py` - Privacyモジュールのベンチマーク

## 実行方法

```bash
# 全自動テスト
pytest tests/

# 特定ファイルのみ
pytest tests/test_privacy.py -v

# カバレッジ付き
pytest tests/ --cov=src --cov-report=html
```
