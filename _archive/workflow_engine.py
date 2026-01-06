import time
import random
from typing import Dict, List, Any

class WorkflowEngine:
    """
    ワークフローエンジン
    複数のAIタスクを順番に実行し、前のステップの結果を次のステップに引き継ぐシステム
    """
    
    def __init__(self, builder_class, registry, goal_index, conflict_map, schema_registry):
        # プロンプトを作る工場（Builder）の設定を保存
        self.builder_config = {
            "registry": registry,
            "goal_index": goal_index,
            "conflict_map": conflict_map,
            "schema_registry": schema_registry
        }
        self.builder_class = builder_class
        self.steps = []  # 手順リスト
        self.memory = []  # 会話の履歴（記憶）

    def add_step(self, step_name: str, goal: str, schema_id: str = None):
        """ワークフローに新しい手順（ステップ）を追加する"""
        print(f"➕ ステップ追加: [{step_name}] (目的: {goal})")
        
        # このステップ専用のプロンプトビルダーを作成
        builder = self.builder_class(**self.builder_config)
        
        # 目的に応じて自動で部品を選ぶ（これまでの機能を再利用！）
        builder.recommend_by_goal(goal)
        
        # 出力形式があればセット
        if schema_id:
            builder.set_output_schema(schema_id)
            
        self.steps.append({
            "name": step_name,
            "builder": builder,
            "goal": goal,
            "schema_id": schema_id
        })

    def list_steps(self):
        """登録されているステップの一覧を表示"""
        if not self.steps:
            print("📋 登録されているステップはありません。")
            return
        
        print("【📝 ワークフローステップ一覧】")
        print("-" * 60)
        for i, step in enumerate(self.steps, 1):
            schema_info = f" → スキーマ: {step['schema_id']}" if step['schema_id'] else ""
            print(f"{i}. {step['name']} (目的: {step['goal']}){schema_info}")
        print("-" * 60)

    def remove_step(self, step_index: int):
        """ステップを削除する（0始まりのインデックス）"""
        if 0 <= step_index < len(self.steps):
            removed = self.steps.pop(step_index)
            print(f"🗑️ ステップを削除しました: {removed['name']}")
        else:
            print(f"❌ エラー: インデックス {step_index} は範囲外です。")

    def clear_steps(self):
        """すべてのステップをクリア"""
        count = len(self.steps)
        self.steps = []
        print(f"🧹 {count}個のステップをクリアしました。")

    def run(self, initial_input: str, simulate: bool = True):
        """
        ワークフローを実行する
        
        Args:
            initial_input: 最初の入力
            simulate: Trueの場合はAI応答をシミュレート、Falseの場合は実際のAPI呼び出し
        """
        print(f"\n🚀 ワークフローを開始します。入力: 「{initial_input}」\n")
        
        current_context = initial_input
        
        for i, step in enumerate(self.steps):
            step_name = step["name"]
            builder = step["builder"]
            
            print(f"\n--- Step {i+1}: {step_name} 実行中... ---")
            
            # 1. 履歴を含めた変数を準備
            # 前のステップの成果物を「背景」として渡すことで、文脈をつなぐ
            variables = {
                "max_tokens": "1000",
                "context": f"これまでの経緯:\n{self._format_memory()}",
                "objective": f"現在のタスク: {current_context} に基づいて処理を実行してください。",
                "style": "論理的かつ創造的に。",
                "tone": "丁寧な口調。",
                "audience": "次の工程の担当者。",
                "response_format": "指定された形式。"
            }
            
            # 2. プロンプト生成（スキーマ付き）
            if step["schema_id"]:
                prompt = builder.build_with_schema(variables)
            else:
                prompt = builder.build(variables)
            
            # 3. AIの実行
            if simulate:
                ai_response = self._simulate_ai_response(step_name)
            else:
                # 実際のAPI呼び出し（ユーザーが実装する）
                ai_response = self._call_ai_api(prompt, step_name)
            
            # 4. 結果を記憶に保存
            self.memory.append(f"【{step_name}の成果物】: {ai_response}")
            current_context = ai_response  # 次のステップへの入力になる
            
            print(f"✅ {step_name} 完了。")
            time.sleep(0.5)  # 処理してる感を出す演出

        print("\n🎉 全ステップ完了！")
        return self.memory

    def get_memory(self) -> List[str]:
        """メモリ（実行履歴）を取得"""
        return self.memory.copy()

    def clear_memory(self):
        """メモリをクリア"""
        count = len(self.memory)
        self.memory = []
        print(f"🧹 {count}個のメモリをクリアしました。")

    def show_memory(self):
        """メモリの内容を表示"""
        if not self.memory:
            print("📋 メモリは空です。")
            return
        
        print("【💭 ワークフローメモリ】")
        print("-" * 60)
        for i, mem in enumerate(self.memory, 1):
            print(f"{i}. {mem}")
        print("-" * 60)

    def _format_memory(self) -> str:
        """記憶をテキスト化する"""
        if not self.memory:
            return "（まだ履歴はありません）"
        return "\n".join(self.memory)

    def _simulate_ai_response(self, step_name: str) -> str:
        """AIの返答をシミュレーションする関数（実際はAPIを呼ぶ場所）"""
        return f"（ここでAIが「{step_name}」のタスクを実行し、素晴らしい結果を出力しました...）"

    def _call_ai_api(self, prompt: str, step_name: str) -> str:
        """
        実際のAI APIを呼び出す関数（ユーザーが実装する）
        
        例:
        import openai
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
        """
        raise NotImplementedError(
            "実際のAI API呼び出しを使用する場合は、この関数を実装してください。\n"
            "シミュレーションモードで実行する場合は、run(simulate=True)を使用してください。"
        )

    def export_workflow(self, filepath: str):
        """ワークフロー定義をJSONファイルに保存"""
        import json
        
        workflow_data = {
            "steps": [
                {
                    "name": step["name"],
                    "goal": step["goal"],
                    "schema_id": step["schema_id"]
                }
                for step in self.steps
            ]
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, ensure_ascii=False, indent=2)
            print(f"💾 ワークフローを保存しました: {filepath}")
        except Exception as e:
            print(f"❌ 保存エラー: {e}")

    def import_workflow(self, filepath: str):
        """ワークフロー定義をJSONファイルから読み込み"""
        import json
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            
            # 既存のステップをクリア
            self.steps = []
            
            # インポートしたステップを追加
            for step_data in workflow_data.get('steps', []):
                self.add_step(
                    step_data['name'],
                    step_data['goal'],
                    step_data.get('schema_id')
                )
            
            print(f"📂 {len(self.steps)}個のステップを読み込みました: {filepath}")
        except FileNotFoundError:
            print(f"❌ ファイルが見つかりません: {filepath}")
        except json.JSONDecodeError:
            print(f"❌ JSONファイルの形式が不正です: {filepath}")
        except Exception as e:
            print(f"❌ 読み込みエラー: {e}")

# ============================================================
# 🔍 EVALUATOR (評価システム)
# ============================================================

class Evaluator:
    """
    AIの出力を評価するシステム
    合格/不合格を判定し、フィードバックを提供
    """
    
    def __init__(self):
        pass

    def evaluate(self, ai_output: str, criteria: List[str]) -> Dict:
        """
        AIの出力を評価する（シミュレーション）
        実際には、ここで別のLLMにプロンプトを投げて採点させます。
        
        Args:
            ai_output: AIの出力
            criteria: 評価基準のリスト
            
        Returns:
            評価結果の辞書 (is_passed, score, feedback)
        """
        print("\n🔍 --- 審査員(Evaluator)がチェック中... ---")
        
        # 今回はシミュレーションとして、ランダムに点数とコメントを返します
        # ※実際は、ai_outputの中身を解析します
        
        score = random.randint(40, 100)  # 40~100点でランダム採点
        
        if score >= 80:
            result = {
                "is_passed": True,
                "score": score,
                "feedback": "素晴らしい！要件を完全に満たしています。"
            }
        else:
            # 点数が低い場合のフィードバック例
            feedbacks = [
                "JSONの形式が崩れています。",
                "具体例が不足しており、抽象的すぎます。",
                "トーンが指示（丁寧語）と異なり、カジュアルすぎます。",
                "指定された文字数を超過しています。"
            ]
            result = {
                "is_passed": False,
                "score": score,
                "feedback": random.choice(feedbacks)  # ランダムにダメ出し
            }
            
        print(f"   📊 スコア: {result['score']}点")
        print(f"   💬 判定: {'合格 ✅' if result['is_passed'] else '不合格 ❌'}")
        print(f"   📝 コメント: {result['feedback']}")
        
        return result

    def evaluate_with_llm(self, ai_output: str, criteria: List[str]) -> Dict:
        """
        実際のLLMを使用して評価する（ユーザーが実装する）
        
        例:
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
        """
        raise NotImplementedError(
            "実際のLLM評価を使用する場合は、この関数を実装してください。\n"
            "シミュレーションモードで実行する場合は、evaluate()を使用してください。"
        )


# WorkflowEngineクラスに評価機能を追加するための拡張メソッド
# 以下のメソッドをWorkflowEngineクラスに追加する必要があります

def _add_evaluation_to_workflow_engine():
    """
    WorkflowEngineクラスに run_with_evaluation メソッドを動的に追加
    """
    def run_with_evaluation(
        self, 
        initial_input: str, 
        criteria: List[str], 
        max_retries: int = 3,
        simulate: bool = True
    ):
        """
        評価付きでワークフローを実行する
        不合格の場合は自動的にリトライする
        
        Args:
            initial_input: 最初の入力
            criteria: 評価基準のリスト
            max_retries: 最大リトライ回数
            simulate: シミュレーションモード
            
        Returns:
            最終的なメモリと評価結果
        """
        print(f"\n🚀 評価付きワークフローを開始します。")
        print(f"   最大リトライ回数: {max_retries}回")
        print(f"   評価基準: {', '.join(criteria)}\n")
        
        evaluator = Evaluator()
        attempt = 0
        
        while attempt < max_retries:
            attempt += 1
            print(f"\n{'='*60}")
            print(f"【試行 {attempt}/{max_retries}】")
            print(f"{'='*60}")
            
            # メモリをクリア（前回の失敗をリセット）
            if attempt > 1:
                self.clear_memory()
            
            # ワークフローを実行
            results = self.run(initial_input, simulate=simulate)
            
            # 最後のステップの出力を評価
            final_output = results[-1] if results else ""
            
            # 評価を実行
            eval_result = evaluator.evaluate(final_output, criteria)
            
            if eval_result['is_passed']:
                print(f"\n🎊 成功！{attempt}回目の試行で合格しました。")
                return {
                    "memory": results,
                    "evaluation": eval_result,
                    "attempts": attempt
                }
            else:
                print(f"\n😞 不合格... フィードバック: {eval_result['feedback']}")
                if attempt < max_retries:
                    print(f"   🔄 リトライします...（残り{max_retries - attempt}回）")
                    # フィードバックを次の試行の入力に追加
                    initial_input = f"{initial_input}\n\n【前回のフィードバック】: {eval_result['feedback']}"
                else:
                    print(f"\n❌ 最大リトライ回数に達しました。")
        
        # 最大リトライ回数に達した場合
        return {
            "memory": results,
            "evaluation": eval_result,
            "attempts": attempt,
            "status": "failed"
        }
    
    # WorkflowEngineクラスにメソッドを追加
    WorkflowEngine.run_with_evaluation = run_with_evaluation

# 評価機能を追加
_add_evaluation_to_workflow_engine()

# ============================================================
# 🧠 INTENT ANALYZER (意図分析器)
# ============================================================

class IntentAnalyzer:
    """
    プロンプトのテキストを分析し、適切な評価基準を自動選択する
    メタ認知アプローチによる適応的評価システム
    """
    
    def __init__(self, criteria_lib: Dict):
        self.criteria_lib = criteria_lib

    def analyze_intent(self, prompt_text: str) -> List[str]:
        """
        プロンプトの内容から「狙い」を読み取り、適切な評価基準IDのリストを返す
        
        Args:
            prompt_text: プロンプトのテキスト
            
        Returns:
            評価基準IDのリスト
        """
        print("🧠 --- メタ認知アナライザーがプロンプトの意図を解析中... ---")
        
        selected_criteria_ids = []
        
        # プロンプト内のキーワードをスキャンして、意図を汲み取る
        # （実際にはここでLLMに「このプロンプトの評価軸を3つ選んで」と聞くのがベストです）
        for c_id, c_data in self.criteria_lib.items():
            # プロンプトの中に、その基準に関連するキーワードが含まれているか？
            for keyword in c_data['keywords']:
                if keyword in prompt_text:
                    selected_criteria_ids.append(c_id)
                    break  # ヒットしたらその基準は採用
        
        # もし何もヒットしなければ、最低限「正確性」を入れる
        if not selected_criteria_ids:
            selected_criteria_ids = ["accuracy"]
        
        # 重複を削除
        selected_criteria_ids = list(set(selected_criteria_ids))
        
        print(f"   📋 選択された評価基準: {[self.criteria_lib[cid]['name'] for cid in selected_criteria_ids]}")
        
        return selected_criteria_ids

    def list_available_criteria(self):
        """利用可能な評価基準の一覧を表示"""
        print("【🎯 利用可能な評価基準】")
        print("-" * 60)
        for c_id, c_data in self.criteria_lib.items():
            print(f"👉 {c_id.ljust(20)} : {c_data['name']}")
            print(f"   {c_data['description']}")
            print(f"   キーワード: {', '.join(c_data['keywords'])}")
            print()
        print("-" * 60)


# ============================================================
# 🎯 ADAPTIVE EVALUATOR (適応的評価器)
# ============================================================

class AdaptiveEvaluator:
    """
    IntentAnalyzerを使用して、プロンプトの意図に基づいた適応的評価を行う
    メタ認知評価システムの中核
    """
    
    def __init__(self, analyzer: IntentAnalyzer):
        self.analyzer = analyzer

    def evaluate_prompt_effectiveness(self, prompt_text: str, ai_output_simulation: str) -> Dict:
        """
        プロンプトを見て評価基準を決め、その基準で出力を採点する
        
        Args:
            prompt_text: プロンプトのテキスト
            ai_output_simulation: AIの出力（シミュレーション）
            
        Returns:
            評価結果の辞書
        """
        # 1. まずプロンプトの意図を理解する（メタ認知）
        active_criteria_ids = self.analyzer.analyze_intent(prompt_text)
        
        print(f"\n🎯 抽出された評価観点: {[self.analyzer.criteria_lib[cid]['name'] for cid in active_criteria_ids]}")
        
        # 2. 選ばれた基準ごとに採点する（シミュレーション）
        print("\n📝 --- 採点開始 ---")
        total_score = 0
        report = {}
        
        for cid in active_criteria_ids:
            criteria_name = self.analyzer.criteria_lib[cid]['name']
            
            # ここで本来はLLMに「この基準で採点して」と投げます
            # 今回はランダムでシミュレーション
            score = random.randint(60, 100)
            
            print(f"   - {criteria_name}: {score}点")
            
            # もし基準が「形式遵守」なのに点数が低かったら、厳しいコメントを出すなど
            if score < 70:
                print(f"     ⚠️ 警告: {criteria_name} の基準を満たしていません。改善が必要です。")
            
            total_score += score
            report[cid] = score

        avg_score = total_score / len(active_criteria_ids)
        print(f"\n📊 総合評価: {avg_score:.1f}点")
        
        return {
            "average_score": avg_score,
            "detailed_scores": report,
            "criteria_used": active_criteria_ids,
            "is_passed": avg_score >= 75
        }

    def evaluate_with_llm(self, prompt_text: str, ai_output: str) -> Dict:
        """
        実際のLLMを使用して評価する（ユーザーが実装する）
        
        例:
        import openai
        
        # 1. プロンプトの意図を分析
        criteria_ids = self.analyzer.analyze_intent(prompt_text)
        
        # 2. 各基準で評価
        for cid in criteria_ids:
            criteria_desc = self.analyzer.criteria_lib[cid]['description']
            evaluation_prompt = f'''
            以下の出力を「{criteria_desc}」の観点で評価してください。
            
            出力:
            {ai_output}
            
            0-100点でスコアを付けてください。
            '''
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": evaluation_prompt}]
            )
            # レスポンスをパースして採点
        """
        raise NotImplementedError(
            "実際のLLM評価を使用する場合は、この関数を実装してください。\n"
            "シミュレーションモードで実行する場合は、evaluate_prompt_effectiveness()を使用してください。"
        )


# ============================================================
# 🌟 GEMINI API INTEGRATION (本物のLLM評価)
# ============================================================

# Gemini APIの初期化（オプション）
_gemini_model = None

def _initialize_gemini():
    """Gemini APIを初期化する"""
    global _gemini_model
    
    if _gemini_model is not None:
        return _gemini_model
    
    try:
        import os
        import google.generativeai as genai
        
        # 環境変数からAPIキーを取得
        api_key = os.environ.get('GEMINI_API_KEY')
        
        if not api_key:
            print("⚠️ GEMINI_API_KEY環境変数が設定されていません。")
            print("   シミュレーションモードで動作します。")
            return None
        
        genai.configure(api_key=api_key)
        _gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini APIが初期化されました。")
        return _gemini_model
        
    except ImportError:
        print("⚠️ google-generativeaiがインストールされていません。")
        print("   pip install google-generativeai を実行してください。")
        return None
    except Exception as e:
        print(f"❌ Gemini API初期化エラー: {e}")
        return None


class GeminiIntentAnalyzer:
    """
    Gemini APIを使用してプロンプトの意図を深く理解する
    キーワードマッチングではなく、文脈理解による評価基準選択
    """
    
    def __init__(self, criteria_lib: Dict):
        self.criteria_lib = criteria_lib
        self.model = _initialize_gemini()

    def analyze_intent(self, prompt_text: str) -> List[str]:
        """
        Gemini APIを使ってプロンプトの意図を分析し、
        適切な評価基準IDのリストを返す
        """
        import json
        import re
        
        print("🧠 --- Geminiがプロンプトの『意図』を読解中... ---")
        
        # APIが使えない場合はシミュレーションにフォールバック
        if self.model is None:
            print("   ⚠️ シミュレーションモードで動作中")
            return self._simulate_analyze(prompt_text)
        
        # 評価基準リストをAIに渡すためのテキストを作成
        criteria_list_text = "\n".join([
            f"- ID: {k} | 基準名: {v['name']} | 説明: {v['description']}"
            for k, v in self.criteria_lib.items()
        ])

        # Geminiへの指示（システムプロンプト）
        system_instruction = f"""
あなたはプロンプトエンジニアリングの専門家です。
以下の「ユーザーが書いたプロンプト」を分析し、その品質を評価するために適切な「評価基準ID」をリストから選んでください。

【評価基準リスト】
{criteria_list_text}

【ルール】
1. プロンプトの目的（創造的なのか、論理的なのか、など）を深く読み取ること。
2. 最も重要と思われる基準を1つ〜3つ選ぶこと。
3. 出力は、選んだIDのリスト（JSON形式）のみを返すこと。余計な解説は不要。
例: ["accuracy", "format_compliance"]
"""

        try:
            # Geminiに問い合わせ
            response = self.model.generate_content(
                f"{system_instruction}\n\n【ユーザーのプロンプト】\n{prompt_text}"
            )
            
            # レスポンスからJSON部分を抽出
            json_text = re.search(r'\[.*\]', response.text, re.DOTALL).group()
            selected_ids = json.loads(json_text)
            
            # IDがライブラリに存在するかチェック
            valid_ids = [pid for pid in selected_ids if pid in self.criteria_lib]
            
            if not valid_ids:
                return ["accuracy"]  # フォールバック
            
            print(f"   📋 選択された評価基準: {[self.criteria_lib[cid]['name'] for cid in valid_ids]}")
            return valid_ids

        except Exception as e:
            print(f"   ❌ APIエラー: {e}")
            return ["accuracy"]  # エラー時は最低限の基準を返す

    def _simulate_analyze(self, prompt_text: str) -> List[str]:
        """シミュレーション用のキーワードマッチング"""
        selected_ids = []
        
        for c_id, c_data in self.criteria_lib.items():
            for keyword in c_data['keywords']:
                if keyword in prompt_text:
                    selected_ids.append(c_id)
                    break
        
        if not selected_ids:
            selected_ids = ["accuracy"]
        
        selected_ids = list(set(selected_ids))
        print(f"   📋 選択された評価基準: {[self.criteria_lib[cid]['name'] for cid in selected_ids]}")
        return selected_ids


class GeminiEvaluator:
    """
    Gemini APIを使用してAIの出力を本格的に評価する
    JSON形式で詳細な採点結果を返す
    """
    
    def __init__(self, analyzer: GeminiIntentAnalyzer):
        self.analyzer = analyzer
        self.model = _initialize_gemini()

    def evaluate(self, prompt_text: str, ai_output: str) -> Dict:
        """
        プロンプトを見て評価基準を決め、その基準で出力を採点する
        """
        import json
        import re
        
        # 1. 意図を理解する（GeminiIntentAnalyzerを使用）
        active_criteria_ids = self.analyzer.analyze_intent(prompt_text)
        
        # 基準の名前リストを取得
        active_criteria_names = [
            self.analyzer.criteria_lib[cid]['name'] for cid in active_criteria_ids
        ]
        print(f"\n🎯 AIが決定した評価軸: {active_criteria_names}")
        
        # APIが使えない場合はシミュレーション
        if self.model is None:
            print("   ⚠️ シミュレーションモードで動作中")
            return self._simulate_evaluate(active_criteria_ids, active_criteria_names)

        # 2. 採点を行う
        print("📝 --- Gemini審査員が採点中... ---")
        
        # 採点用の指示
        scoring_instruction = f"""
以下の「プロンプト」と、それに対する「AIの出力」を評価してください。
評価は、以下の「重点評価項目」に基づいて厳密に行ってください。

【プロンプト（指示）】
{prompt_text}

【AIの出力（評価対象）】
{ai_output}

【重点評価項目】
{", ".join(active_criteria_names)}

【出力形式】
以下のJSONフォーマットで出力してください。
{{
    "total_score": 0〜100の整数,
    "feedback": "改善点や良かった点についての具体的なコメント（100文字程度）",
    "details": {{
        "基準名1": 点数,
        "基準名2": 点数
    }}
}}
"""
        try:
            response = self.model.generate_content(scoring_instruction)
            
            # JSON解析
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                print(f"\n📊 総合スコア: {result['total_score']}点")
                print(f"💬 フィードバック: {result['feedback']}")
                print("📋 詳細スコア:")
                for k, v in result.get("details", {}).items():
                    print(f"   - {k}: {v}点")
                
                result['criteria_used'] = active_criteria_ids
                result['is_passed'] = result['total_score'] >= 75
                return result
            else:
                print("❌ 解析エラー: JSONが見つかりませんでした")
                return {"total_score": 0, "is_passed": False}

        except Exception as e:
            print(f"❌ APIエラー: {e}")
            return {"total_score": 0, "is_passed": False}

    def _simulate_evaluate(self, criteria_ids: List[str], criteria_names: List[str]) -> Dict:
        """シミュレーション用のランダム評価"""
        print("📝 --- 採点開始（シミュレーション）---")
        
        total_score = 0
        details = {}
        
        for name in criteria_names:
            score = random.randint(60, 100)
            details[name] = score
            total_score += score
            print(f"   - {name}: {score}点")
        
        avg_score = total_score / len(criteria_names)
        
        print(f"\n📊 総合スコア: {avg_score:.0f}点")
        
        return {
            "total_score": round(avg_score),
            "feedback": "シミュレーションモードで評価しました。",
            "details": details,
            "criteria_used": criteria_ids,
            "is_passed": avg_score >= 75
        }


# ============================================================
# 🔄 OPTIMIZATION LOOP (自動最適化ループ)
# ============================================================

class GeminiRefiner:
    """
    フィードバックに基づいてプロンプトを自動的に書き直す
    """
    
    def __init__(self, model=None):
        self.model = model if model else _initialize_gemini()

    def refine_prompt(self, current_prompt: str, feedback: str, criteria_names: List[str]) -> str:
        """
        評価フィードバックに基づいてプロンプトを改善する
        """
        print("🔧 --- Refinerがプロンプトを修正中... ---")
        
        if self.model is None:
            print("   ⚠️ シミュレーションモードで動作中")
            return self._simulate_refine(current_prompt, feedback)

        # プロンプトを書き直させるためのメタプロンプト
        instruction = f"""
あなたは世界最高峰のプロンプトエンジニアです。
以下の「現在のプロンプト」を使ってAIに指示を出しましたが、品質チェックで「改善が必要」と判定されました。

【フィードバック（改善点）】
{feedback}

【重視すべき評価基準】
{", ".join(criteria_names)}

【現在のプロンプト】
{current_prompt}

【指示】
フィードバックの内容を反映し、評価基準を満たすように「現在のプロンプト」を書き直してください。
元の意図は崩さず、指示を具体化・明確化・強化してください。
出力は「修正後のプロンプト本文のみ」を返してください。挨拶や解説は不要です。
"""
        try:
            response = self.model.generate_content(instruction)
            new_prompt = response.text.strip()
            print("✨ プロンプトが書き直されました！")
            return new_prompt
        except Exception as e:
            print(f"❌ Refinerエラー: {e}")
            return current_prompt  # エラー時はそのまま返す

    def _simulate_refine(self, current_prompt: str, feedback: str) -> str:
        """シミュレーション用のプロンプト改善"""
        improved = f"{current_prompt}\n\n【改善適用】{feedback}に基づいて具体化しました。"
        print("✨ プロンプトが書き直されました！（シミュレーション）")
        return improved


class GeminiGenerator:
    """
    プロンプトに基づいてコンテンツを生成する
    """
    
    def __init__(self, model=None):
        self.model = model if model else _initialize_gemini()

    def generate(self, prompt: str) -> str:
        """
        プロンプトに基づいてコンテンツを生成
        """
        print("🤖 --- Generatorがタスクを実行中... ---")
        
        if self.model is None:
            print("   ⚠️ シミュレーションモードで動作中")
            return self._simulate_generate(prompt)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"エラー発生: {e}"

    def _simulate_generate(self, prompt: str) -> str:
        """シミュレーション用のコンテンツ生成"""
        return f"（シミュレーション: 「{prompt[:30]}...」に対する生成結果）"


def run_optimization_loop(
    initial_prompt: str, 
    criteria_lib: Dict,
    max_retries: int = 3, 
    passing_score: int = 80
) -> Dict:
    """
    プロンプトを自動的に最適化するループ
    
    Args:
        initial_prompt: 初期プロンプト
        criteria_lib: 評価基準ライブラリ（CRITERIA_LIBRARY）
        max_retries: 最大リトライ回数
        passing_score: 合格点（これを超えたら終了）
        
    Returns:
        最終プロンプト、出力、スコアを含む辞書
    """
    # 各役割のインスタンス化
    analyzer = GeminiIntentAnalyzer(criteria_lib)
    evaluator = GeminiEvaluator(analyzer)
    refiner = GeminiRefiner()
    generator = GeminiGenerator()

    current_prompt = initial_prompt
    
    print(f"\n🏁 最適化ループを開始します（最大 {max_retries} 回）")
    print(f"   合格点: {passing_score}点\n")

    for i in range(1, max_retries + 1):
        print(f"\n{'='*60}")
        print(f"🔄 --- ラウンド {i}/{max_retries} ---")
        print(f"{'='*60}")
        
        # 1. 生成 (Generate)
        output = generator.generate(current_prompt)
        print(f"\n📄 [AIの生成結果 (抜粋)]:\n{output[:100]}...\n")
        
        # 2. 評価 (Evaluate)
        eval_result = evaluator.evaluate(current_prompt, output)
        score = eval_result.get("total_score", 0)
        feedback = eval_result.get("feedback", "フィードバックなし")
        
        # 3. 判定 (Check)
        if score >= passing_score:
            print(f"\n🎉 合格点({passing_score}点)を超えました！ループを終了します。")
            return {
                "final_prompt": current_prompt,
                "final_output": output,
                "score": score,
                "rounds": i,
                "status": "passed"
            }
        
        # 4. 修正 (Refine) - 最終ラウンドでなければ実行
        if i < max_retries:
            print(f"\n⚠️ スコア不足({score}点 < {passing_score}点)。")
            print("   フィードバックに基づいてプロンプトを修正します。")
            
            # 評価に使われた基準名を取得
            active_ids = eval_result.get("criteria_used", ["accuracy"])
            criteria_names = [criteria_lib[cid]['name'] for cid in active_ids if cid in criteria_lib]
            
            # プロンプトを書き換え
            current_prompt = refiner.refine_prompt(current_prompt, feedback, criteria_names)
            
            print(f"\n📝 [修正後のプロンプト]:\n{current_prompt[:200]}...")
        else:
            print(f"\n🛑 最大試行回数({max_retries}回)に達しました。")

    return {
        "final_prompt": current_prompt,
        "final_output": output,
        "score": score,
        "rounds": max_retries,
        "status": "max_retries_reached"
    }


# ============================================================
# 🧬 DATA SYNTHESIS (データ合成)
# ============================================================

class DataSynthesizer:
    """
    ユーザーの意図に合わせて、高品質な「例（Few-Shot）」を自動生成する
    """
    
    def __init__(self, model=None):
        self.model = model if model else _initialize_gemini()

    def generate_examples(self, intent: str, count: int = 3) -> str:
        """
        意図に基づいてFew-Shotの成功事例を自動生成
        
        Args:
            intent: ユーザーの意図
            count: 生成する例の数
            
        Returns:
            生成された例のテキスト
        """
        print(f"🧬 --- データ合成中: 「{intent}」の成功事例を作っています... ---")
        
        if self.model is None:
            print("   ⚠️ シミュレーションモードで動作中")
            return self._simulate_examples(intent, count)
        
        prompt = f"""
あなたは優秀なデータ作成者です。
ユーザーの意図「{intent}」を達成するための、理想的な「入力と出力の例」を{count}つ作成してください。

【要件】
1. 具体的で実用的な内容にすること。
2. 良い例（Good Example）であること。
3. 出力形式は以下のフォーマットのみ。

Example 1:
Input: ...
Output: ...

Example 2:
...
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"例の生成に失敗: {e}"

    def _simulate_examples(self, intent: str, count: int) -> str:
        """シミュレーション用の例生成"""
        examples = []
        for i in range(1, count + 1):
            examples.append(f"""Example {i}:
Input: {intent}に関する入力例{i}
Output: {intent}を達成する出力例{i}""")
        return "\n\n".join(examples)


class CasualTextRefiner:
    """
    話し言葉（カジュアル）を、目的に合わせて最適化する変換器
    """
    
    def __init__(self, model=None, synthesizer: DataSynthesizer = None):
        self.model = model if model else _initialize_gemini()
        self.synthesizer = synthesizer if synthesizer else DataSynthesizer(self.model)

    def refine(self, user_text: str, style: str, use_few_shot: bool = True) -> str:
        """
        カジュアルなテキストを指定されたスタイルに変換
        
        Args:
            user_text: ユーザーのカジュアルな入力
            style: 変換先のスタイル
            use_few_shot: Few-Shotデータ合成を使用するか
            
        Returns:
            変換されたテキスト
        """
        if self.model is None:
            print("   ⚠️ シミュレーションモードで動作中")
            return self._simulate_refine(user_text, style)
        
        # 1. まず、ユーザーのテキストから「意図」を読み取る
        print("🎯 --- ユーザーの意図を分析中... ---")
        intent_prompt = f"以下のテキストの『目的』を5文字〜20文字で要約してください。\nテキスト: {user_text}"
        
        try:
            intent_resp = self.model.generate_content(intent_prompt)
            intent = intent_resp.text.strip()
            print(f"   読み取った意図: {intent}")
        except Exception as e:
            print(f"   ❌ 意図分析エラー: {e}")
            intent = "テキスト最適化"
        
        # 2. その意図に合った「成功事例」を自動生成する (Few-Shot Data Synthesis)
        examples = ""
        if use_few_shot:
            examples = self.synthesizer.generate_examples(intent)
        
        # 3. 事例を使って、ユーザーのテキストを変換する (ICL)
        print("✍️ --- 本番書き込み中... ---")
        conversion_prompt = f"""
あなたはプロのライター/エンジニアです。
ユーザーの「ラフな入力」を、指定された「スタイル」に合わせて書き直してください。
{"以下の「成功事例」を参考に、品質を高めてください。" if examples else ""}

{"【成功事例 (Few-Shot Data)】" + chr(10) + examples if examples else ""}

【スタイル指定】
{style}

【ユーザーのラフな入力】
{user_text}

【出力】
書き直したテキストのみを出力してください。
"""
        try:
            response = self.model.generate_content(conversion_prompt)
            result = response.text.strip()
            print("✅ テキスト変換完了！")
            return result
        except Exception as e:
            return f"変換エラー: {e}"

    def _simulate_refine(self, user_text: str, style: str) -> str:
        """シミュレーション用のテキスト変換"""
        return f"【{style}スタイルに変換】\n{user_text}"
