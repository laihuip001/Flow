# Firebase Studio セットアップガイド (OPPO Pad 3)

## 1. Firebase Studio アクセス

1. OPPO Pad 3 でブラウザを開く
2. [Firebase Studio](https://firebase.studio) にアクセス
3. Googleアカウントでログイン

## 2. リポジトリのインポート

1. 「Import from GitHub」を選択
2. リポジトリ: `laihuip001/AI-Clipboard-Pro`
3. ブランチ: `main`

## 3. 環境変数の設定

Firebase Studio のターミナルで:

```bash
cp .env.example .env
# .env を編集して API キーを設定
```

## 4. 依存関係のインストール

```bash
pip install -r requirements.txt
```

## 5. 開発ワークフロー

### 作業開始

```bash
./dev_tools/sync.sh start
```

### 作業終了（自動Push）

```bash
./dev_tools/sync.sh end
```

## 6. AI エージェントへのコンテキスト設定

1. `.ai/SYSTEM_CONTEXT.md` を開く
2. チャットで指示: `@SYSTEM_CONTEXT.md を読んで制約を記憶せよ`

## 7. 現在の課題

- `/process` エンドポイントが 500 エラーを返す
- `config.py` の `MODEL_FAST` 設定を確認する必要あり
- `CONTEXT_HANDOVER.md` に詳細あり
