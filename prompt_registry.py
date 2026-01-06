from typing import List, Dict, Optional
import json

# Pydantic imports for structured output schemas
try:
    from pydantic import create_model, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    print("⚠️ 警告: Pydanticがインストールされていません。構造化出力機能を使用するには 'pip install pydantic' を実行してください。")

# プロンプトエンジニアリング・コンポーネントの定義
COMPONENT_REGISTRY = {
    # ----------------------------------------------------
    # 🏗 Frameworks (骨格)
    # ----------------------------------------------------
    "structure_co_star": {
        "name": "CO-STAR Framework",
        "tags": ["#Comp/Structure"],
        "description": "文脈(C)、目的(O)、スタイル(S)、トーン(T)、読者(A)、応答形式(R)を定義する強力なフレームワーク。",
        "template": """
# CONTEXT (背景)
{context}

# OBJECTIVE (目的)
{objective}

# STYLE (スタイル)
{style}

# TONE (トーン)
{tone}

# AUDIENCE (対象読者)
{audience}

# RESPONSE (応答フォーマット)
{response_format}
""",
        "required_params": ["context", "objective", "style", "tone", "audience", "response_format"],
        "synergy_ids": ["reasoning_cot", "safety_cove"]
    },
    
    "structure_persona_hub": {
        "name": "Persona Hub",
        "source": "10億人のペルソナ（人物像）で多様な合成データを作成するための技術 - AIDB",
        "tags": ["#Comp/Structure"],
        "template": """
# ROLE ASSIGNMENT
あなたは以下のペルソナとして振る舞ってください：
【名前/職業】{persona_name}
【詳細設定】{persona_details}
【視点】{persona_perspective}
""",
        "required_params": ["persona_name", "persona_details", "persona_perspective"],
        "synergy_ids": ["structure_few_shot", "reasoning_role_play"]
    },

    # ----------------------------------------------------
    # 🧠 Reasoning (推論)
    # ----------------------------------------------------
    "reasoning_cot": {
        "name": "Chain-of-Thought (CoT)",
        "source": "CoTの推論ステップ数がLLMの推論能力に及ぼす影響を詳細に検証した結果 - AIDB",
        "tags": ["#Comp/Reasoning"],
        "template": """
# REASONING PROCESS
回答を生成する前に、以下のステップに従って論理的に思考してください：
1. 問題を小さなサブタスクに分解する
2. 各サブタスクについて事実関係を確認する
3. ステップごとの中間結論を導き出す
4. 論理の飛躍がないか確認する

Let's think step by step.
""",
        "required_params": [],
        "synergy_ids": ["eval_self_consistency", "safety_cove"]
    },

    "reasoning_step_back": {
        "name": "Step-Back Prompting",
        "source": "LLMにまず前提から尋ることで出力精度を向上させる『ステップバック・プロンプティング』と実行プロンプト - AIDB",
        "tags": ["#Comp/Reasoning"],
        "template": """
# ABSTRACTION (抽象化)
具体的な回答をする前に、このタスクの背後にある「より高次の概念」や「前提知識」について考え、以下に出力してください：
- この問題が属する一般的なカテゴリ
- 適用されるべき基本的な原則や法則
""",
        "required_params": [],
        "synergy_ids": ["reasoning_cot"]
    },

    # ----------------------------------------------------
    # 🛡 Safety (安全性)
    # ----------------------------------------------------
    "safety_cove": {
        "name": "Chain-of-Verification (CoVe)",
        "source": "LLMの出力から誤り（ハルシネーション）を減らす新手法『CoVe（Chain-of-Verification）』と実行プロンプト - AIDB",
        "tags": ["#Comp/Safety"],
        "template": """
# VERIFICATION LOOP
ドラフト回答を作成した後、以下のプロセスを実行してください：
1. ドラフトに含まれる事実主張（Fact）をリストアップする
2. 各主張に対して検証質問（Verification Question）を作成する
3. 検証質問に回答し、事実と矛盾がないかチェックする
4. 矛盾がある場合は修正し、最終回答を生成する
""",
        "required_params": [],
        "synergy_ids": ["reasoning_cot", "optimize_rag"]
    },

    # ----------------------------------------------------
    # ⚡ Optimize (最適化)
    # ----------------------------------------------------
    "optimize_compression": {
        "name": "Prompt Compression",
        "source": "LLMコスト効率を高める「プロンプト圧縮」入門 比較で見える実践のポイント - AIDB",
        "tags": ["#Comp/Optimize"],
        "template": """
# OUTPUT CONSTRAINT
回答は冗長な表現を避け、情報の密度を高めてください。
以下の条件を守ること：
- 重要でない接続詞や挨拶は省略する
- 箇条書きや構造化データを活用する
- トークン効率を意識し、{max_tokens}トークン以内で完結させる
""",
        "required_params": ["max_tokens"],
        "synergy_ids": ["structure_xml_delimiters"]
    }
}

def get_component(component_id: str) -> Optional[Dict]:
    """コンポーネントIDから詳細を取得する"""
    return COMPONENT_REGISTRY.get(component_id)

def list_components() -> List[str]:
    """登録されているコンポーネントIDの一覧を返す"""
    return list(COMPONENT_REGISTRY.keys())

# ============================================================
# 🎯 GOAL INDEX (目的インデックス)
# ============================================================
# 目的（ゴール）と、推奨されるコンポーネントIDの対応表
GOAL_INDEX = {
    # 🎯 精度・品質系
    "deep_reasoning": {
        "description": "複雑な問題を論理的に深く考えさせたい",
        "ids": ["reasoning_cot", "reasoning_step_back"]
    },
    "fact_checking": {
        "description": "嘘（ハルシネーション）を防ぎ、正確性を高めたい",
        "ids": ["safety_cove", "structure_co_star"]
    },
    
    # 💰 コスト・効率系
    "cost_saving": {
        "description": "トークン数を節約して、API料金を安く済ませたい",
        "ids": ["optimize_compression"]
    },
    
    # 🎭 キャラクター・スタイル系
    "character_chat": {
        "description": "特定のキャラクターになりきって会話させたい",
        "ids": ["structure_persona_hub"]
    },
    "business_doc": {
        "description": "ビジネス向けのしっかりした文書を作りたい",
        "ids": ["structure_co_star"]
    },
    
    # 🔬 高度な推論系
    "abstract_thinking": {
        "description": "抽象的な概念から考えさせたい",
        "ids": ["reasoning_step_back", "reasoning_cot"]
    },
    
    # 📝 構造化出力系
    "structured_output": {
        "description": "整理された構造的な出力が欲しい",
        "ids": ["structure_co_star", "optimize_compression"]
    }
}

# ============================================================
# 🚨 CONFLICT MAP (競合マップ)
# ============================================================
# 競合（コンフリクト）マップ
# キー：部品ID, 値：相性が悪い部品IDのリストと、その理由
CONFLICT_MAP = {
    # 「短くする」機能は、「長く考える」機能とぶつかります
    "optimize_compression": {
        "conflicts": ["reasoning_cot", "reasoning_step_back"],
        "reason": "⚠️ 警告: 「短くまとめる指示」と「長く深く考える指示」は矛盾するため、AIが混乱する可能性があります。"
    },
    
    # 「長く考える」機能は、「短くする」機能とぶつかります
    "reasoning_cot": {
        "conflicts": ["optimize_compression"],
        "reason": "⚠️ 警告: 「思考の連鎖」は長文になりがちですが、「圧縮」は短文を強制するため、効果が打ち消し合う恐れがあります。"
    },
    
    "reasoning_step_back": {
        "conflicts": ["optimize_compression"],
        "reason": "⚠️ 警告: 「ステップバック推論」は抽象的な思考を促すため詳細な説明が必要ですが、「圧縮」は簡潔さを要求するため矛盾します。"
    }
}

# ============================================================
# 📊 SCHEMA REGISTRY (スキーマレジストリ)
# ============================================================
# 出力データの設計図（スキーマ）カタログ
# Pydanticを使用して構造化されたJSON出力を定義

if PYDANTIC_AVAILABLE:
    SCHEMA_REGISTRY = {
        # 📝 パターンA: ニュースや記事の要約・分析用
        "news_analysis": {
            "description": "ニュース記事から重要な要素を抽出するスキーマ",
            "fields": {
                "title": (str, Field(..., description="記事の適切なタイトル（30文字以内）")),
                "summary": (str, Field(..., description="要約文（300文字程度）")),
                "keywords": (List[str], Field(..., description="重要なキーワードのリスト（5つまで）")),
                "sentiment_score": (float, Field(..., description="記事のポジティブ/ネガティブ度合い（-1.0〜1.0）")),
                "is_fake_news_risk": (bool, Field(..., description="フェイクニュースの可能性があるかどうかの真偽値"))
            }
        },
        
        # 🛒 パターンB: 商品レビューの分析用
        "product_review": {
            "description": "顧客の声から改善点を洗い出すスキーマ",
            "fields": {
                "product_name": (str, Field(..., description="対象の商品名")),
                "user_rating": (int, Field(..., description="ユーザーの満足度（1〜5段階）")),
                "pain_points": (List[str], Field(..., description="ユーザーが不満に感じている具体的な点")),
                "feature_requests": (List[str], Field(..., description="要望されている新機能"))
            }
        },
        
        # 📧 パターンC: メール分類用
        "email_classification": {
            "description": "メールを自動分類するスキーマ",
            "fields": {
                "category": (str, Field(..., description="メールのカテゴリ（urgent/normal/spam/promotional）")),
                "priority": (int, Field(..., description="優先度（1-5、5が最高）")),
                "requires_response": (bool, Field(..., description="返信が必要かどうか")),
                "action_items": (List[str], Field(..., description="実行すべきアクションアイテム")),
                "deadline": (Optional[str], Field(None, description="締切日（YYYY-MM-DD形式、なければNull）"))
            }
        },
        
        # 💬 パターンD: 会議議事録の構造化
        "meeting_minutes": {
            "description": "会議の内容を構造化して記録するスキーマ",
            "fields": {
                "meeting_title": (str, Field(..., description="会議のタイトル")),
                "attendees": (List[str], Field(..., description="参加者のリスト")),
                "key_decisions": (List[str], Field(..., description="重要な決定事項")),
                "action_items": (List[Dict[str, str]], Field(..., description="アクションアイテム（担当者と内容）")),
                "next_meeting_date": (Optional[str], Field(None, description="次回会議の予定日"))
            }
        }
    }
else:
    # Pydanticが利用できない場合は空の辞書
    SCHEMA_REGISTRY = {}

# ============================================================
# 🎯 CRITERIA LIBRARY (評価基準ライブラリ)
# ============================================================
# 評価基準の定義（一般妥当な指標のカタログ）
CRITERIA_LIBRARY = {
    # --- 論理・正確性重視 ---
    "accuracy": {
        "name": "正確性 (Accuracy)",
        "description": "事実に即しているか、論理的な矛盾がないか、計算ミスがないか。",
        "keywords": ["正確", "事実", "論理", "計算", "真実"]
    },
    "reasoning_depth": {
        "name": "推論の深さ (Reasoning Depth)",
        "description": "表面的な回答ではなく、ステップバイステップで深く考察されているか。",
        "keywords": ["思考", "ステップ", "理由", "分析", "深掘り"]
    },
    
    # --- 創造・表現重視 ---
    "creativity": {
        "name": "創造性 (Creativity)",
        "description": "ありきたりでない、独創的で興味深い内容か。比喩や物語性が豊かか。",
        "keywords": ["創造", "ユニーク", "物語", "面白い", "アイデア"]
    },
    "persona_adherence": {
        "name": "ペルソナ一貫性 (Role Adherence)",
        "description": "指定されたキャラクター（口調、性格、視点）を維持できているか。",
        "keywords": ["ペルソナ", "口調", "キャラクター", "なりきって", "としての"]
    },

    # --- 形式・制約重視 ---
    "format_compliance": {
        "name": "形式遵守 (Format Compliance)",
        "description": "指定されたJSONスキーマや出力フォーマットを厳密に守っているか。",
        "keywords": ["JSON", "形式", "フォーマット", "スキーマ", "出力して"]
    },
    "safety": {
        "name": "安全性 (Safety)",
        "description": "有害な内容、差別的表現、ハルシネーション（嘘）が含まれていないか。",
        "keywords": ["安全", "検証", "確認", "嘘", "ハルシネーション"]
    }
}




