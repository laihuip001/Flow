from typing import List, Dict, Optional
import json

class PromptBuilder:
    def __init__(self, registry: Dict):
        self.registry = registry
        self.selected_components = []

    def add_component(self, component_id: str):
        """コンポーネントをIDで指定して追加する機能"""
        if component_id not in self.registry:
            raise ValueError(f"エラー: '{component_id}' というIDの部品は見つかりません。")
        
        # すでに追加されていなければリストに追加
        if component_id not in self.selected_components:
            self.selected_components.append(component_id)
            print(f"✅ 追加しました: {self.registry[component_id]['name']}")
            
            # 相性の良い部品があれば教えてくれる機能
            synergies = self.registry[component_id].get('synergy_ids', [])
            if synergies:
                print(f"   💡 ヒント: 一緒に {synergies} を使うともっと良くなるかもしれません。")

    def build(self, variables: Dict[str, str]) -> str:
        """選ばれた部品を合体させて、最終的な指示書を作る機能"""
        full_prompt = []
        
        for comp_id in self.selected_components:
            comp_data = self.registry[comp_id]
            template = comp_data['template']
            
            # 必要な情報（変数）が足りているかチェック
            required = comp_data.get('required_params', [])
            missing = [p for p in required if p not in variables]
            
            if missing:
                raise ValueError(f"エラー: {comp_id} を使うには、次の情報が足りません: {missing}")
            
            # テンプレートの空欄に情報を埋め込む
            try:
                formatted_part = template.format(**variables)
                full_prompt.append(formatted_part)
            except KeyError as e:
                raise ValueError(f"変数の埋め込みエラー: {comp_id} で {e} が発生しました")

        return "\n".join(full_prompt)

    def remove_component(self, component_id: str):
        """選択済みコンポーネントを削除する機能"""
        if component_id in self.selected_components:
            self.selected_components.remove(component_id)
            print(f"🗑️ 削除しました: {self.registry[component_id]['name']}")
        else:
            print(f"⚠️ '{component_id}' は選択されていません。")

    def clear_components(self):
        """すべての選択をクリアする機能"""
        count = len(self.selected_components)
        self.selected_components = []
        print(f"🧹 {count}個のコンポーネントをクリアしました。")

    def get_selected_components(self) -> List[Dict]:
        """選択済みコンポーネントの詳細情報を返す機能"""
        return [
            {
                "id": comp_id,
                "name": self.registry[comp_id]['name'],
                "tags": self.registry[comp_id].get('tags', []),
                "required_params": self.registry[comp_id].get('required_params', [])
            }
            for comp_id in self.selected_components
        ]

    def list_selected_components(self):
        """選択済みコンポーネントを表示する機能"""
        if not self.selected_components:
            print("📋 選択されているコンポーネントはありません。")
            return
        
        print("【選択済みコンポーネント】")
        for i, comp_id in enumerate(self.selected_components, 1):
            comp = self.registry[comp_id]
            print(f"{i}. ID: {comp_id} | 名前: {comp['name']}")

    def list_components(self):
        """使える部品の一覧を表示する機能"""
        print("【利用可能なコンポーネント一覧】")
        for k, v in self.registry.items():
            tags_str = ", ".join(v.get('tags', []))
            print(f"- ID: {k} | 名前: {v['name']} | タグ: {tags_str}")

    def list_components_by_tag(self, tag: str):
        """タグでフィルタリングしたコンポーネント一覧を表示する機能"""
        print(f"【タグ '{tag}' のコンポーネント一覧】")
        filtered = {k: v for k, v in self.registry.items() if tag in v.get('tags', [])}
        
        if not filtered:
            print(f"⚠️ タグ '{tag}' に該当するコンポーネントはありません。")
            return
        
        for k, v in filtered.items():
            print(f"- ID: {k} | 名前: {v['name']}")

    def validate_build(self, variables: Dict[str, str]) -> Dict[str, any]:
        """ビルド前に検証のみ実行する機能（実際のビルドなし）"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "required_params": set()
        }
        
        for comp_id in self.selected_components:
            comp_data = self.registry[comp_id]
            required = comp_data.get('required_params', [])
            missing = [p for p in required if p not in variables]
            
            if missing:
                validation_result["valid"] = False
                validation_result["errors"].append({
                    "component_id": comp_id,
                    "missing_params": missing
                })
            
            validation_result["required_params"].update(required)
        
        validation_result["required_params"] = list(validation_result["required_params"])
        return validation_result

    def export_selection(self, filepath: str):
        """選択したコンポーネントをJSONファイルに保存する機能"""
        export_data = {
            "selected_components": self.selected_components,
            "component_details": self.get_selected_components()
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            print(f"💾 選択内容を保存しました: {filepath}")
        except Exception as e:
            print(f"❌ 保存エラー: {e}")

    def import_selection(self, filepath: str):
        """JSONファイルから選択を復元する機能"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # 既存の選択をクリア
            self.selected_components = []
            
            # インポートしたコンポーネントを追加
            for comp_id in import_data.get('selected_components', []):
                if comp_id in self.registry:
                    self.selected_components.append(comp_id)
                else:
                    print(f"⚠️ 警告: '{comp_id}' は現在のレジストリに存在しません（スキップ）")
            
            print(f"📂 {len(self.selected_components)}個のコンポーネントを読み込みました: {filepath}")
        except FileNotFoundError:
            print(f"❌ ファイルが見つかりません: {filepath}")
        except json.JSONDecodeError:
            print(f"❌ JSONファイルの形式が不正です: {filepath}")
        except Exception as e:
            print(f"❌ 読み込みエラー: {e}")

# ============================================================
# 🎯 GOAL-ORIENTED PROMPT BUILDER (目的指向ビルダー)
# ============================================================

class GoalOrientedPromptBuilder(PromptBuilder):
    """
    目的（ゴール）から逆引きでコンポーネントを選べるビルダー
    PromptBuilderの全機能を継承しつつ、初心者向けの目的ベース推奨機能を追加
    """
    
    def __init__(self, registry: Dict, goal_index: Dict):
        super().__init__(registry)  # 親クラスの初期化
        self.goal_index = goal_index

    def list_goals(self):
        """利用可能な「やりたいこと」リストを表示"""
        print("【🎯 目的から選ぶメニュー】")
        print("-" * 60)
        for key, info in self.goal_index.items():
            print(f"👉 {key.ljust(20)} : {info['description']}")
        print("-" * 60)
        print(f"合計 {len(self.goal_index)} 個の目的が利用可能です")

    def recommend_by_goal(self, goal_key: str):
        """ゴールを指定すると、おすすめの部品を自動で追加する"""
        if goal_key not in self.goal_index:
            print(f"❌ エラー: '{goal_key}' という目的は見つかりません。")
            print("💡 ヒント: list_goals() で利用可能な目的を確認してください。")
            return

        goal_info = self.goal_index[goal_key]
        print(f"\n🚀 目的「{goal_info['description']}」に合わせて部品を追加します...")
        print("-" * 60)
        
        target_ids = goal_info['ids']
        added_count = 0
        
        for comp_id in target_ids:
            # 既存の追加メソッドを使って追加（重複チェックやSynergy表示もそのまま動く）
            if comp_id not in self.selected_components:
                self.add_component(comp_id)
                added_count += 1
            else:
                print(f"⏭️ スキップ: {self.registry[comp_id]['name']} (既に追加済み)")
        
        print("-" * 60)
        print(f"✨ {added_count}個の新しいコンポーネントを追加しました！")

    def show_goal_details(self, goal_key: str):
        """特定の目的の詳細情報を表示"""
        if goal_key not in self.goal_index:
            print(f"❌ エラー: '{goal_key}' という目的は見つかりません。")
            return
        
        goal_info = self.goal_index[goal_key]
        print(f"\n【目的の詳細: {goal_key}】")
        print(f"説明: {goal_info['description']}")
        print(f"\n推奨コンポーネント:")
        for comp_id in goal_info['ids']:
            if comp_id in self.registry:
                comp = self.registry[comp_id]
                print(f"  - {comp_id}: {comp['name']}")
                print(f"    タグ: {', '.join(comp.get('tags', []))}")

# ============================================================
# 🚨 SAFE PROMPT BUILDER (安全なビルダー)
# ============================================================

class SafePromptBuilder(GoalOrientedPromptBuilder):
    """
    競合検出機能付きのビルダー
    GoalOrientedPromptBuilderの全機能を継承しつつ、
    矛盾するコンポーネントの組み合わせを警告する
    """
    
    def __init__(self, registry: Dict, goal_index: Dict, conflict_map: Dict):
        super().__init__(registry, goal_index)  # 親クラスの初期化
        self.conflict_map = conflict_map
        self.conflict_warnings = []  # 警告履歴を保存

    def add_component(self, component_id: str):
        """部品を追加する際、既存の部品とケンカしないかチェックする"""
        
        # すでに選ばれている部品たちと、これから入れる部品を比較
        for existing_id in self.selected_components:
            
            # パターンA: 新しい部品が、既存の部品と相性が悪い場合
            if component_id in self.conflict_map:
                if existing_id in self.conflict_map[component_id]["conflicts"]:
                    reason = self.conflict_map[component_id]["reason"]
                    warning_msg = (
                        f"\n🚨 矛盾を検知: '{self.registry[component_id]['name']}' を追加しようとしていますが、\n"
                        f"   すでに '{self.registry[existing_id]['name']}' が入っています。\n"
                        f"   {reason}\n"
                    )
                    print(warning_msg)
                    self.conflict_warnings.append({
                        "new_component": component_id,
                        "existing_component": existing_id,
                        "reason": reason
                    })
            
            # パターンB: 既存の部品が、新しい部品と相性が悪い場合
            if existing_id in self.conflict_map:
                if component_id in self.conflict_map[existing_id]["conflicts"]:
                    reason = self.conflict_map[existing_id]["reason"]
                    warning_msg = (
                        f"\n🚨 矛盾を検知: '{self.registry[component_id]['name']}' を追加しようとしていますが、\n"
                        f"   すでに '{self.registry[existing_id]['name']}' が入っています。\n"
                        f"   {reason}\n"
                    )
                    print(warning_msg)
                    self.conflict_warnings.append({
                        "new_component": component_id,
                        "existing_component": existing_id,
                        "reason": reason
                    })

        # チェックが終わったら、通常通り追加する（親クラスの機能を使う）
        super().add_component(component_id)

    def get_conflict_report(self) -> Dict:
        """競合警告のレポートを取得"""
        return {
            "total_warnings": len(self.conflict_warnings),
            "warnings": self.conflict_warnings,
            "has_conflicts": len(self.conflict_warnings) > 0
        }

    def clear_conflict_warnings(self):
        """競合警告履歴をクリア"""
        self.conflict_warnings = []
        print("🧹 競合警告履歴をクリアしました。")

    def show_conflict_summary(self):
        """競合の要約を表示"""
        if not self.conflict_warnings:
            print("✅ 競合は検出されていません。")
            return
        
        print(f"\n【⚠️ 競合サマリー】")
        print(f"検出された競合: {len(self.conflict_warnings)}件")
        print("-" * 60)
        for i, warning in enumerate(self.conflict_warnings, 1):
            new_comp = self.registry[warning['new_component']]['name']
            existing_comp = self.registry[warning['existing_component']]['name']
            print(f"{i}. {new_comp} ⚔️ {existing_comp}")
        print("-" * 60)

# ============================================================
# 📊 STRUCTURED PROMPT BUILDER (構造化ビルダー)
# ============================================================

class StructuredPromptBuilder(SafePromptBuilder):
    """
    構造化出力機能付きのビルダー
    SafePromptBuilderの全機能を継承しつつ、
    Pydanticベースのスキーマ定義で構造化されたJSON出力を強制
    """
    
    def __init__(self, registry: Dict, goal_index: Dict, conflict_map: Dict, schema_registry: Dict):
        super().__init__(registry, goal_index, conflict_map)  # 親クラスの初期化
        self.schema_registry = schema_registry
        self.current_schema_model = None  # ここに作成された型定義が入ります
        self.current_schema_id = None

    def list_schemas(self):
        """利用可能なスキーマの一覧を表示"""
        if not self.schema_registry:
            print("⚠️ スキーマレジストリが空です。Pydanticがインストールされているか確認してください。")
            return
        
        print("【📊 利用可能なスキーマ一覧】")
        print("-" * 60)
        for schema_id, schema_info in self.schema_registry.items():
            print(f"👉 {schema_id.ljust(20)} : {schema_info['description']}")
        print("-" * 60)
        print(f"合計 {len(self.schema_registry)} 個のスキーマが利用可能です")

    def set_output_schema(self, schema_id: str):
        """欲しい出力データの形式（ID）をセットする"""
        if schema_id not in self.schema_registry:
            print(f"❌ エラー: スキーマ '{schema_id}' は見つかりません。")
            print("💡 ヒント: list_schemas() で利用可能なスキーマを確認してください。")
            return

        schema_config = self.schema_registry[schema_id]
        print(f"🏗 出力スキーマを「{schema_id}」に設定しました。")
        print(f"   説明: {schema_config['description']}")
        
        # Pydanticを使って、動的に「型」を作成する（ここが魔法のポイント！）
        # これにより、Pythonプログラムとして扱えるクラスが自動生成されます。
        try:
            from pydantic import create_model
            self.current_schema_model = create_model(
                schema_id,
                **schema_config["fields"]
            )
            self.current_schema_id = schema_id
        except ImportError:
            print("❌ エラー: Pydanticがインストールされていません。")
            print("   'pip install pydantic' を実行してください。")
            self.current_schema_model = None
            self.current_schema_id = None

    def get_json_schema(self):
        """AI（API）に渡すためのJSON Schemaを取得する"""
        if self.current_schema_model:
            # Pydanticの機能で、自動的にAIが理解できるJSON形式に変換
            return self.current_schema_model.model_json_schema()
        return None

    def show_schema_details(self, schema_id: str = None):
        """スキーマの詳細情報を表示"""
        target_id = schema_id or self.current_schema_id
        
        if not target_id:
            print("❌ エラー: スキーマが指定されていません。")
            return
        
        if target_id not in self.schema_registry:
            print(f"❌ エラー: スキーマ '{target_id}' は見つかりません。")
            return
        
        schema_config = self.schema_registry[target_id]
        print(f"\n【スキーマ詳細: {target_id}】")
        print(f"説明: {schema_config['description']}")
        print(f"\nフィールド定義:")
        for field_name, (field_type, field_info) in schema_config['fields'].items():
            type_name = field_type.__name__ if hasattr(field_type, '__name__') else str(field_type)
            print(f"  - {field_name} ({type_name}): {field_info.description}")

    def build_with_schema(self, variables: Dict[str, str]) -> str:
        """プロンプト本文にスキーマ情報を追加して出力する"""
        base_prompt = self.build(variables)
        
        if self.current_schema_model:
            # プロンプトの末尾に、強制力を高めるための指示を追加
            import json
            schema_instruction = f"""

# STRUCTURED OUTPUT REQUIREMENT
回答は必ず以下のJSONスキーマに従って出力してください。
余計な解説やMarkdownの装飾（```jsonなど）は不要です。
純粋なJSONのみを出力すること。

{json.dumps(self.get_json_schema(), indent=2, ensure_ascii=False)}
"""
            return base_prompt + schema_instruction
        
        return base_prompt

    def clear_schema(self):
        """設定されているスキーマをクリア"""
        if self.current_schema_id:
            print(f"🧹 スキーマ '{self.current_schema_id}' をクリアしました。")
            self.current_schema_model = None
            self.current_schema_id = None
        else:
            print("📋 設定されているスキーマはありません。")



