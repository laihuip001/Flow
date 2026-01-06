# Prompt Engineering Component Library

このプロジェクトは、プロンプトエンジニアリングで使用される様々なフレームワークやテクニックを管理するためのライブラリです。

## プロジェクト構成

- `prompt_registry.py`: プロンプトのテンプレートやメタデータが定義されているメインデータファイルです。
- `prompt_builder.py`: コンポーネントを組み合わせてプロンプトを構築するビルダークラスです。
- `main.py`: このライブラリの使用例を示すデモスクリプトです。

## 使い方

以下のコマンドを実行して、登録されているプロンプトのコンポーネントを確認できます。

```bash
python main.py
```

## 登録されているテクニックの例

- **CO-STAR Framework**: 背景、目的、スタイルなどを定義する構造化テンプレート。
- **Chain-of-Thought (CoT)**: 論理的な思考プロセスを促すテクニック。
- **Persona Hub**: 特定の役割（ペルソナ）を割り当てるためのテンプレート。
- **Chain-of-Verification (CoVe)**: ハルシネーション（誤情報）を減らすための検証ループ。

## PromptBuilderの主な機能

### 基本機能

```python
from prompt_registry import COMPONENT_REGISTRY
from prompt_builder import PromptBuilder

builder = PromptBuilder(COMPONENT_REGISTRY)

# コンポーネントの追加
builder.add_component("structure_co_star")

# プロンプトの生成
variables = {
    "context": "あなたの背景情報",
    "objective": "達成したい目的",
    # ... その他の変数
}
final_prompt = builder.build(variables)
```

### 拡張機能

#### 1. コンポーネント管理
```python
# 選択済みコンポーネントの表示
builder.list_selected_components()

# コンポーネントの削除
builder.remove_component("component_id")

# すべてクリア
builder.clear_components()
```

#### 2. タグによるフィルタリング
```python
# 特定のタグのコンポーネントのみ表示
builder.list_components_by_tag("#Comp/Reasoning")
```

#### 3. バリデーション
```python
# ビルド前に必要なパラメータをチェック
validation = builder.validate_build(variables)
if validation["valid"]:
    print("すべてのパラメータが揃っています")
else:
    print(f"不足: {validation['errors']}")
```

#### 4. エクスポート/インポート
```python
# 選択内容をJSONファイルに保存
builder.export_selection("my_selection.json")

# 保存した選択内容を読み込み
builder.import_selection("my_selection.json")
```

## APIリファレンス

### PromptBuilderクラス

| メソッド | 説明 |
|---------|------|
| `add_component(component_id)` | コンポーネントを追加 |
| `remove_component(component_id)` | コンポーネントを削除 |
| `clear_components()` | すべての選択をクリア |
| `list_components()` | 利用可能なコンポーネント一覧を表示 |
| `list_selected_components()` | 選択済みコンポーネントを表示 |
| `list_components_by_tag(tag)` | タグでフィルタリングして表示 |
| `get_selected_components()` | 選択済みコンポーネントの詳細を取得 |
| `validate_build(variables)` | ビルド前のバリデーション |
| `build(variables)` | 最終的なプロンプトを生成 |
| `export_selection(filepath)` | 選択内容をJSONに保存 |
| `import_selection(filepath)` | JSONから選択内容を復元 |

## 🎯 GoalOrientedPromptBuilder（目的指向ビルダー）

### 概要

`GoalOrientedPromptBuilder`は、「やりたいこと」から逆引きでコンポーネントを選べる初心者向けの機能です。プロンプトエンジニアリングの知識がなくても、目的を選ぶだけで最適なコンポーネントが自動的に選択されます。

### 基本的な使い方

```python
from prompt_registry import COMPONENT_REGISTRY, GOAL_INDEX
from prompt_builder import GoalOrientedPromptBuilder

# 目的指向ビルダーの初期化
builder = GoalOrientedPromptBuilder(COMPONENT_REGISTRY, GOAL_INDEX)

# 利用可能な目的を確認
builder.list_goals()

# 目的に基づいてコンポーネントを自動追加
builder.recommend_by_goal("deep_reasoning")

# プロンプトを生成
variables = {...}
prompt = builder.build(variables)
```

### 利用可能な目的

| 目的キー | 説明 | 推奨コンポーネント |
|---------|------|-------------------|
| `deep_reasoning` | 複雑な問題を論理的に深く考えさせたい | CoT, Step-Back |
| `fact_checking` | ハルシネーションを防ぎ、正確性を高めたい | CoVe, CO-STAR |
| `cost_saving` | トークン数を節約して、API料金を安く済ませたい | Compression |
| `character_chat` | 特定のキャラクターになりきって会話させたい | Persona Hub |
| `business_doc` | ビジネス向けのしっかりした文書を作りたい | CO-STAR |
| `abstract_thinking` | 抽象的な概念から考えさせたい | Step-Back, CoT |
| `structured_output` | 整理された構造的な出力が欲しい | CO-STAR, Compression |

### 追加メソッド

| メソッド | 説明 |
|---------|------|
| `list_goals()` | 利用可能な目的の一覧を表示 |
| `recommend_by_goal(goal_key)` | 目的に基づいてコンポーネントを自動追加 |
| `show_goal_details(goal_key)` | 特定の目的の詳細情報を表示 |

### 使用例：複数の目的を組み合わせる

```python
builder = GoalOrientedPromptBuilder(COMPONENT_REGISTRY, GOAL_INDEX)

# 深い推論と事実確認を両方実現したい
builder.recommend_by_goal("deep_reasoning")
builder.recommend_by_goal("fact_checking")

# 選択されたコンポーネントを確認
builder.list_selected_components()
```

## 🚨 SafePromptBuilder（競合検出ビルダー）

### 概要

`SafePromptBuilder`は、矛盾するコンポーネントの組み合わせを自動検出し、警告を表示する品質管理機能です。例えば、「短くまとめる」指示と「長く深く考える」指示を同時に使うと、AIが混乱する可能性があります。このビルダーはそのような問題を事前に警告します。

### 基本的な使い方

```python
from prompt_registry import COMPONENT_REGISTRY, GOAL_INDEX, CONFLICT_MAP
from prompt_builder import SafePromptBuilder

# 安全なビルダーの初期化
builder = SafePromptBuilder(COMPONENT_REGISTRY, GOAL_INDEX, CONFLICT_MAP)

# コンポーネントを追加（競合があれば警告）
builder.add_component("reasoning_cot")
builder.add_component("optimize_compression")  # ⚠️ 競合警告が表示される

# 競合サマリーの確認
builder.show_conflict_summary()
```

### 検出される競合パターン

| コンポーネント1 | コンポーネント2 | 理由 |
|---------------|---------------|------|
| `optimize_compression` | `reasoning_cot` | 「短くまとめる」と「長く考える」は矛盾 |
| `optimize_compression` | `reasoning_step_back` | 「簡潔さ」と「抽象的思考」は両立困難 |

### 追加メソッド

| メソッド | 説明 |
|---------|------|
| `add_component(component_id)` | 競合チェック付きでコンポーネント追加（オーバーライド） |
| `get_conflict_report()` | 競合警告のレポートを取得 |
| `show_conflict_summary()` | 競合の要約を表示 |
| `clear_conflict_warnings()` | 競合警告履歴をクリア |

### 使用例：競合を検出して対処

```python
builder = SafePromptBuilder(COMPONENT_REGISTRY, GOAL_INDEX, CONFLICT_MAP)

# 目的ベースで追加
builder.recommend_by_goal("cost_saving")      # 圧縮が含まれる
builder.recommend_by_goal("deep_reasoning")   # CoTが含まれる → 競合警告

# 競合レポートを確認
report = builder.get_conflict_report()
if report['has_conflicts']:
    print(f"⚠️ {report['total_warnings']}件の競合が検出されました")
    builder.show_conflict_summary()
    
    # 対処方法を決定
    # 1. どちらかのコンポーネントを削除
    # 2. 競合を承知で使用
    # 3. 別のコンポーネントに変更
```

### クラス継承階層

```
PromptBuilder (基底クラス)
    ↓
GoalOrientedPromptBuilder (目的指向)
    ↓
SafePromptBuilder (競合検出)
```

**利点：**
- 必要に応じて適切なレベルのビルダーを選択可能
- すべての親クラスの機能を継承

## 📊 StructuredPromptBuilder（構造化出力ビルダー）

### 概要

`StructuredPromptBuilder`は、AIの出力を構造化されたJSONフォーマットに強制する機能です。Pydanticを使用してスキーマを定義し、AIが理解できるJSON Schemaに自動変換します。

> [!IMPORTANT]
> この機能を使用するには、Pydanticのインストールが必要です：
> ```bash
> pip install pydantic
> ```

### 基本的な使い方

```python
from prompt_registry import COMPONENT_REGISTRY, GOAL_INDEX, CONFLICT_MAP, SCHEMA_REGISTRY
from prompt_builder import StructuredPromptBuilder

# 構造化ビルダーの初期化
builder = StructuredPromptBuilder(
    COMPONENT_REGISTRY, 
    GOAL_INDEX, 
    CONFLICT_MAP, 
    SCHEMA_REGISTRY
)

# 利用可能なスキーマを確認
builder.list_schemas()

# スキーマを設定
builder.set_output_schema("news_analysis")

# スキーマ付きプロンプトを生成
variables = {...}
prompt = builder.build_with_schema(variables)
```

### 利用可能なスキーマ

| スキーマID | 説明 | 主なフィールド |
|-----------|------|---------------|
| `news_analysis` | ニュース記事の分析 | title, summary, keywords, sentiment_score, is_fake_news_risk |
| `product_review` | 商品レビューの分析 | product_name, user_rating, pain_points, feature_requests |
| `email_classification` | メールの自動分類 | category, priority, requires_response, action_items, deadline |
| `meeting_minutes` | 会議議事録の構造化 | meeting_title, attendees, key_decisions, action_items, next_meeting_date |

### 追加メソッド

| メソッド | 説明 |
|---------|------|
| `list_schemas()` | 利用可能なスキーマの一覧を表示 |
| `set_output_schema(schema_id)` | 出力スキーマを設定 |
| `get_json_schema()` | JSON Schemaを取得 |
| `show_schema_details(schema_id)` | スキーマの詳細情報を表示 |
| `build_with_schema(variables)` | スキーマ付きプロンプトを生成 |
| `clear_schema()` | 設定されているスキーマをクリア |

### 使用例：ニュース記事の分析

```python
builder = StructuredPromptBuilder(
    COMPONENT_REGISTRY, GOAL_INDEX, CONFLICT_MAP, SCHEMA_REGISTRY
)

# スキーマを設定
builder.set_output_schema("news_analysis")

# コンポーネントを追加
builder.add_component("structure_co_star")
builder.add_component("reasoning_cot")

# プロンプトを生成
variables = {
    "context": "最新のAI技術に関するニュース記事",
    "objective": "記事の内容を構造化されたデータとして抽出する",
    "style": "客観的で正確な分析",
    "tone": "専門的かつ中立的",
    "audience": "データアナリスト",
    "response_format": "JSON形式"
}

prompt = builder.build_with_schema(variables)
```

**生成されるプロンプトには以下が含まれます：**
- 選択したコンポーネントの指示
- JSON Schemaの定義
- 構造化出力の強制指示

### クラス継承階層（最終版）

```
PromptBuilder (基底クラス)
    ↓
GoalOrientedPromptBuilder (目的指向)
    ↓
SafePromptBuilder (競合検出)
    ↓
StructuredPromptBuilder (構造化出力)
```

**選択ガイド：**
- **PromptBuilder**: 基本機能のみ
- **GoalOrientedPromptBuilder**: 目的ベースで選びたい
- **SafePromptBuilder**: 競合検出が必要
- **StructuredPromptBuilder**: 構造化JSON出力が必要（推奨）

## 🔄 WorkflowEngine（ワークフローエンジン）

### 概要

`WorkflowEngine`は、複数のAIタスクを順番に実行し、前のステップの結果を次のステップに引き継ぐオーケストレーションシステムです。複雑なタスクを小さなステップに分解し、自動的に実行します。

### 基本的な使い方

```python
from prompt_registry import COMPONENT_REGISTRY, GOAL_INDEX, CONFLICT_MAP, SCHEMA_REGISTRY
from prompt_builder import StructuredPromptBuilder
from workflow_engine import WorkflowEngine

# ワークフローエンジンの初期化
workflow = WorkflowEngine(
    builder_class=StructuredPromptBuilder,
    registry=COMPONENT_REGISTRY,
    goal_index=GOAL_INDEX,
    conflict_map=CONFLICT_MAP,
    schema_registry=SCHEMA_REGISTRY
)

# ステップを追加
workflow.add_step("アイデア生成", "deep_reasoning")
workflow.add_step("アウトライン作成", "structured_output")
workflow.add_step("本文執筆", "character_chat")
workflow.add_step("校正", "fact_checking")

# ワークフローを実行
results = workflow.run("AIとプログラミング教育の未来について", simulate=True)

# 結果を確認
workflow.show_memory()
```

### 主要メソッド

| メソッド | 説明 |
|---------|------|
| `add_step(step_name, goal, schema_id)` | ワークフローにステップを追加 |
| `list_steps()` | 登録されているステップの一覧を表示 |
| `remove_step(step_index)` | ステップを削除 |
| `clear_steps()` | すべてのステップをクリア |
| `run(initial_input, simulate)` | ワークフローを実行 |
| `get_memory()` | 実行履歴を取得 |
| `show_memory()` | メモリの内容を表示 |
| `clear_memory()` | メモリをクリア |
| `export_workflow(filepath)` | ワークフロー定義をJSONに保存 |
| `import_workflow(filepath)` | JSONからワークフロー定義を読み込み |

### 使用例：ブログ記事作成パイプライン

```python
workflow = WorkflowEngine(
    builder_class=StructuredPromptBuilder,
    registry=COMPONENT_REGISTRY,
    goal_index=GOAL_INDEX,
    conflict_map=CONFLICT_MAP,
    schema_registry=SCHEMA_REGISTRY
)

# ステップ1: アイデア生成
workflow.add_step(
    step_name="アイデア生成",
    goal="deep_reasoning",
    schema_id=None
)

# ステップ2: アウトライン作成
workflow.add_step(
    step_name="アウトライン作成",
    goal="structured_output",
    schema_id=None
)

# ステップ3: 本文執筆
workflow.add_step(
    step_name="本文執筆",
    goal="character_chat",
    schema_id=None
)

# ステップ4: 校正
workflow.add_step(
    step_name="校正",
    goal="fact_checking",
    schema_id=None
)

# 実行
results = workflow.run("AIとプログラミング教育の未来について", simulate=True)
```

### コンテキストの連鎖

ワークフローエンジンの最大の特徴は、**コンテキストの連鎖**です：

1. **ステップ1**の出力 → **ステップ2**の入力
2. **ステップ2**の出力 → **ステップ3**の入力
3. **ステップ3**の出力 → **ステップ4**の入力

各ステップは前のステップの成果物を「これまでの経緯」として受け取り、それに基づいて処理を行います。

### ワークフローの保存と再利用

```python
# ワークフローを保存
workflow.export_workflow("my_workflow.json")

# 別のセッションで読み込み
workflow2 = WorkflowEngine(...)
workflow2.import_workflow("my_workflow.json")
workflow2.run("新しい入力", simulate=True)
```

### 実際のAI APIとの統合

シミュレーションモードではなく、実際のAI APIを使用する場合：

```python
# workflow_engine.py の _call_ai_api メソッドを実装
def _call_ai_api(self, prompt: str, step_name: str) -> str:
    import openai
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# 実行時に simulate=False を指定
workflow.run("入力", simulate=False)
```

### ワークフローパターン例

#### パターン1: コンテンツ作成
```
アイデア生成 → アウトライン → 執筆 → 校正 → 公開準備
```

#### パターン2: データ分析
```
データ抽出 → クリーニング → 分析 → 可視化 → レポート生成
```

#### パターン3: カスタマーサポート
```
問い合わせ分類 → 情報収集 → 回答生成 → 品質チェック
```

## 🔍 Evaluator（評価システム）

### 概要

`Evaluator`は、AIの出力を自動評価し、品質基準を満たしているかチェックするシステムです。WorkflowEngineと統合することで、不合格の場合は自動的にリトライし、品質を向上させます。

### 基本的な使い方

```python
from workflow_engine import Evaluator

evaluator = Evaluator()

# AIの出力を評価
result = evaluator.evaluate(
    ai_output="（AIが生成した出力）",
    criteria=["JSON形式であること", "具体的であること"]
)

if result['is_passed']:
    print(f"合格！スコア: {result['score']}点")
else:
    print(f"不合格。フィードバック: {result['feedback']}")
```

### 評価結果の構造

```python
{
    "is_passed": True/False,  # 合格/不合格
    "score": 85,              # 0-100点のスコア
    "feedback": "素晴らしい！要件を完全に満たしています。"
}
```

### WorkflowEngineとの統合

```python
from workflow_engine import WorkflowEngine

workflow = WorkflowEngine(...)
workflow.add_step("コンテンツ生成", "character_chat")

# 評価付きで実行（自動リトライ）
result = workflow.run_with_evaluation(
    initial_input="プログラミング学習のコツについて",
    criteria=["内容が具体的であること", "文法が正しいこと"],
    max_retries=3,
    simulate=True
)

print(f"試行回数: {result['attempts']}回")
print(f"最終スコア: {result['evaluation']['score']}点")
```

### 自動リトライの仕組み

1. **ワークフロー実行** → AIが出力を生成
2. **評価** → Evaluatorが品質をチェック
3. **不合格の場合** → フィードバックを元に再実行
4. **合格 or 最大リトライ回数** → 終了

**フィードバックの活用：**
```
試行1: 「トーンがカジュアルすぎます」 → 不合格
試行2: （フィードバックを反映）→ 「丁寧な口調で」 → 合格
```

### 実際のLLM評価への拡張

```python
class Evaluator:
    def evaluate_with_llm(self, ai_output: str, criteria: List[str]) -> Dict:
        import openai
        evaluation_prompt = f'''
        以下の出力を評価してください。
        
        評価基準:
        {chr(10).join(f"- {c}" for c in criteria)}
        
        出力:
        {ai_output}
        
        0-100点でスコアを付け、合格/不合格を判定してください。
        '''
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": evaluation_prompt}]
        )
        # レスポンスをパースして返す
```

## 🧠 AdaptiveEvaluator（適応的評価）

### 概要

`AdaptiveEvaluator`は、プロンプトの意図を自動分析し、適切な評価基準を動的に選択するメタ認知評価システムです。ユーザーが評価基準を手動指定する必要がなく、システムが自動的に最適な評価軸を選びます。

### CRITERIA_LIBRARY（評価基準ライブラリ）

6つの汎用的な評価基準：

| 基準ID | 名前 | 説明 |
|--------|------|------|
| `accuracy` | 正確性 | 事実に即しているか、論理的矛盾がないか |
| `reasoning_depth` | 推論の深さ | ステップバイステップで深く考察されているか |
| `creativity` | 創造性 | 独創的で興味深い内容か |
| `persona_adherence` | ペルソナ一貫性 | 指定されたキャラクターを維持できているか |
| `format_compliance` | 形式遵守 | JSONスキーマや出力フォーマットを守っているか |
| `safety` | 安全性 | 有害な内容、差別的表現が含まれていないか |

### 基本的な使い方

```python
from prompt_registry import CRITERIA_LIBRARY
from workflow_engine import IntentAnalyzer, AdaptiveEvaluator

# IntentAnalyzerの初期化
analyzer = IntentAnalyzer(CRITERIA_LIBRARY)

# AdaptiveEvaluatorの初期化
adaptive_eval = AdaptiveEvaluator(analyzer)

# プロンプトと出力を評価
result = adaptive_eval.evaluate_prompt_effectiveness(
    prompt_text="創造的で面白いストーリーを書いてください",
    ai_output_simulation="（AIが生成した出力）"
)

print(f"総合評価: {result['average_score']:.1f}点")
print(f"使用された基準: {result['criteria_used']}")
```

### メタ認知の仕組み

1. **意図分析**: プロンプトのキーワードを分析
2. **基準選択**: 最適な評価軸を自動選択
3. **多次元評価**: 選択された基準ごとに採点
4. **総合判定**: 平均スコアと合格/不合格を判定

**例：**
```python
プロンプト: "創造的で面白いストーリーを物語形式で書いてください"
  ↓ IntentAnalyzer
選択された基準: ["creativity"]
  ↓ AdaptiveEvaluator
創造性: 85点 → 総合評価: 85点（合格）
```

```python
プロンプト: "正確にJSON形式で出力してください"
  ↓ IntentAnalyzer
選択された基準: ["accuracy", "format_compliance"]
  ↓ AdaptiveEvaluator
正確性: 90点, 形式遵守: 88点 → 総合評価: 89点（合格）
```

### IntentAnalyzerのメソッド

| メソッド | 説明 |
|---------|------|
| `analyze_intent(prompt_text)` | プロンプトから評価基準を自動選択 |
| `list_available_criteria()` | 利用可能な評価基準の一覧を表示 |

### AdaptiveEvaluatorのメソッド

| メソッド | 説明 |
|---------|------|
| `evaluate_prompt_effectiveness(prompt_text, ai_output)` | 適応的評価を実行 |
| `evaluate_with_llm(prompt_text, ai_output)` | LLMベースの評価（実装が必要） |

### 評価結果の構造

```python
{
    "average_score": 85.5,       # 総合評価スコア
    "detailed_scores": {          # 基準ごとの詳細スコア
        "creativity": 88,
        "persona_adherence": 83
    },
    "criteria_used": [            # 使用された評価基準
        "creativity", 
        "persona_adherence"
    ],
    "is_passed": True             # 合格/不合格（75点以上で合格）
}
```

### 複数の評価ケース

#### ケース1: 創造的コンテンツ
```python
プロンプト: "ユニークな物語を創造的に"
→ 評価基準: ["creativity"]
```

#### ケース2: データ正確性
```python
プロンプト: "事実に基づいて正確にJSON形式で"
→ 評価基準: ["accuracy", "format_compliance"]
```

#### ケース3: ペルソナ維持
```python
プロンプト: "キャラクターとして丁寧な口調で"
→ 評価基準: ["persona_adherence"]
```

#### ケース4: 深い分析
```python
プロンプト: "ステップバイステップで深く分析"
→ 評価基準: ["reasoning_depth"]
```

### メタ認知評価の利点

- ✅ **自動化**: ユーザーが評価基準を手動指定不要
- ✅ **適応性**: プロンプトに最適化された評価
- ✅ **多次元**: 複数の観点から包括的に評価
- ✅ **透明性**: どの基準が使用されたか明示

## 🌟 GeminiEvaluator（本物のLLM評価）

### 概要

`GeminiEvaluator`は、Google Gemini APIを使用して**本物のLLM評価**を行うシステムです。シミュレーションではなく、実際のAIがプロンプトの意図を深く理解し、プロフェッショナルな採点を行います。

> [!IMPORTANT]
> この機能を使用するには、Gemini APIキーが必要です：
> ```bash
> pip install google-generativeai
> set GEMINI_API_KEY=your_api_key  # Windows
> export GEMINI_API_KEY=your_api_key  # Linux/Mac
> ```

### 基本的な使い方

```python
from prompt_registry import CRITERIA_LIBRARY
from workflow_engine import GeminiIntentAnalyzer, GeminiEvaluator

# GeminiIntentAnalyzerの初期化
analyzer = GeminiIntentAnalyzer(CRITERIA_LIBRARY)

# GeminiEvaluatorの初期化
gemini_eval = GeminiEvaluator(analyzer)

# プロンプトと出力を評価
result = gemini_eval.evaluate(
    prompt_text="創造的なファンタジー物語を書いてください",
    ai_output="むかしむかし、空を飛ぶクジラが住む..."
)

print(f"スコア: {result['total_score']}点")
print(f"フィードバック: {result['feedback']}")
```

### シミュレーション vs 本物のAPI

| 項目 | シミュレーション | Gemini API |
|------|-----------------|------------|
| 意図分析 | キーワードマッチング | 文脈理解 |
| 採点 | ランダム | 本物の評価 |
| フィードバック | 固定メッセージ | 具体的なコメント |
| API必要 | なし | あり |

### 評価結果の構造

```python
{
    "total_score": 85,
    "feedback": "独創的な世界観が素晴らしい。比喩表現も豊かです。",
    "details": {
        "創造性 (Creativity)": 90,
        "ペルソナ一貫性": 80
    },
    "criteria_used": ["creativity", "persona_adherence"],
    "is_passed": True
}
```

### APIキー未設定時の動作

APIキーが設定されていない場合、自動的にシミュレーションモードにフォールバックします：

```
⚠️ GEMINI_API_KEY環境変数が設定されていません。
   シミュレーションモードで動作します。
```

## 🔄 run_optimization_loop（自動最適化ループ）

### 概要

`run_optimization_loop`は、プロンプトを**自動的に改善し続ける**究極の機能です。生成→評価→修正のサイクルを、合格点に達するまで繰り返します。

```
初期プロンプト
    ↓ Generate
AI出力
    ↓ Evaluate
スコア: 65点（不合格）
    ↓ Refine
改善プロンプト
    ↓ Generate
AI出力
    ↓ Evaluate
スコア: 85点（合格！）✅
```

### 基本的な使い方

```python
from prompt_registry import CRITERIA_LIBRARY
from workflow_engine import run_optimization_loop

result = run_optimization_loop(
    initial_prompt="面白いストーリーを書いて",
    criteria_lib=CRITERIA_LIBRARY,
    max_retries=3,
    passing_score=80
)

print(f"最終スコア: {result['score']}点")
print(f"ステータス: {result['status']}")
print(f"改善後プロンプト: {result['final_prompt']}")
```

### 結果の構造

```python
{
    "final_prompt": "改善後のプロンプト",
    "final_output": "最終的なAI出力",
    "score": 85,
    "rounds": 2,
    "status": "passed"  # または "max_retries_reached"
}
```

### コンポーネント

| クラス | 役割 |
|--------|------|
| `GeminiGenerator` | プロンプトに基づいてコンテンツを生成 |
| `GeminiEvaluator` | 出力を評価してスコアとフィードバックを返す |
| `GeminiRefiner` | フィードバックに基づいてプロンプトを改善 |

### 最適化の利点

- ✅ **自律的改善**: 人間の介入なしでプロンプトを最適化
- ✅ **フィードバック反映**: 評価結果を次のイテレーションに活用
- ✅ **品質保証**: 合格点に達するまで継続
- ✅ **透明性**: 各ラウンドの進捗を可視化

## 🧬 DataSynthesizer（Few-Shotデータ合成）

### 概要

`DataSynthesizer`は、ユーザーの意図に合わせて**高品質なFew-Shot例**を自動生成します。

```python
from workflow_engine import DataSynthesizer

synthesizer = DataSynthesizer()
examples = synthesizer.generate_examples("謝罪メールを書く", count=3)
print(examples)
```

**出力例:**
```
Example 1:
Input: 会議に遅刻したことを謝りたい
Output: お世話になっております。本日の会議に遅刻し、誠に申し訳ございませんでした...

Example 2:
...
```

## 📋 CasualTextRefiner（テキスト最適化）

カジュアルなテキストを、指定されたスタイルに最適化します。

```python
from workflow_engine import CasualTextRefiner

refiner = CasualTextRefiner()
result = refiner.refine(
    user_text="部長にお詫び。寝坊して会議遅刻した。",
    style="ビジネスメール (謝罪)",
    use_few_shot=True
)
print(result)
```

## 🌐 Streamlit Web App

### 概要

`app.py`は、ブラウザで使えるGUIアプリケーションです。

### 起動方法

```bash
pip install -r requirements.txt
streamlit run app.py
```

### 機能

- 📝 カジュアルなテキストを入力
- 🎨 7種類の変換スタイルから選択
- 🧬 Few-Shotデータ合成（オプション）
- ✨ ワンクリックで最適化

### 変換スタイル

| スタイル | 用途 |
|---------|------|
| ビジネスメール | 謝罪・依頼 |
| エンジニア向け | 要件定義 |
| SNS投稿 | 親しみやすく |
| 英語翻訳 | ビジネス英語 |
| 論理的要約 | 箇条書き |

## 🔌 FastAPI REST API

### 概要

`api.py`は、スマホアプリや外部サービスから呼び出せる**REST API**サーバーです。

### 起動方法

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=your_api_key  # Linux/Mac
set GEMINI_API_KEY=your_api_key     # Windows
python api.py
```

または:
```bash
uvicorn api:app --reload --port 8000
```

### APIドキュメント

起動後、ブラウザで開く:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### エンドポイント

| エンドポイント | メソッド | 説明 |
|--------------|---------|------|
| `/` | GET | ヘルスチェック |
| `/styles` | GET | 利用可能なスタイル一覧 |
| `/refine` | POST | テキスト最適化 |

### リクエスト例

```bash
curl -X POST "http://localhost:8000/refine" \
  -H "Content-Type: application/json" \
  -d '{"text": "部長にお詫び。遅刻した。", "style": "ビジネスメール"}'
```

### レスポンス例

```json
{
  "result": "お世話になっております。本日は遅刻し...",
  "intent": "謝罪メール",
  "style": "ビジネスメール"
}
```

## 🥦 Prompt Filter（プロンプト下処理）

### 概要

`/filter`エンドポイントは、生のテキストを**3つのモード**で下処理します。

### 3つのモード

| モード | 名前 | 処理内容 |
|--------|------|---------|
| `raw`/`light` | 湯がく | ノイズ除去のみ、高速 |
| `heavy` | 炙る | 構造化、6W3H補完 |
| `deep` | 深掘り | **逆質問**で不足情報を取得 |

### リクエスト例

```bash
# Deep モード（逆質問）
curl -X POST "http://localhost:8000/filter" \
  -H "Content-Type: application/json" \
  -d '{"text": "アプリ作って", "mode": "deep"}'
```

### Deepモードの対話フロー

```
Step 1: 初回リクエスト
POST /filter {"text": "アプリ作って", "mode": "deep"}

レスポンス:
{
  "type": "question",  ← 追加質問
  "text": "どのプラットフォーム向けですか？Webですか？モバイルですか？",
  "mode": "deep"
}

Step 2: 回答を含めて再リクエスト
POST /filter {
  "text": "アプリ作って",
  "mode": "deep",
  "context": "iOSとAndroid両対応で、ToDoリストアプリです"
}

レスポンス:
{
  "type": "complete",  ← 完成
  "text": "iOS/Android対応のToDoリストアプリを作成...",
  "mode": "deep"
}
```

### レスポンスタイプ

| type | 説明 |
|------|------|
| `complete` | 処理完了、プロンプトを使用可能 |
| `question` | 追加情報が必要、質問に回答してください |
| `error` | エラー発生 |

## 拡張のヒント

`prompt_registry.py` の `COMPONENT_REGISTRY` 辞書に新しいコンポーネントを追加することで、自分専用のプロンプト集を簡単に作ることができます。

### コンポーネントの構造

```python
"your_component_id": {
    "name": "コンポーネント名",
    "tags": ["#Comp/Category"],
    "description": "説明文",
    "template": "テンプレート文字列 {variable}",
    "required_params": ["variable"],
    "synergy_ids": ["related_component_id"]
}
```

