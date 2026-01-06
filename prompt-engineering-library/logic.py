import google.generativeai as genai
from config import settings
import hashlib
from sqlalchemy.orm import Session
from models import TextRequest, PrefetchCache
from datetime import datetime
import asyncio
import re
import os

# API Key Setup
if "GEMINI_API_KEY" in os.environ:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
elif settings.GEMINI_API_KEY != "YOUR_API_KEY_HERE":
    genai.configure(api_key=settings.GEMINI_API_KEY)

# --- 🛡️ Safety Module ---
class PrivacyScanner:
    """個人情報検知（警告のみ・置換なし）"""
    def __init__(self):
        self.patterns = {
            "EMAIL": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "PHONE": r'\d{2,4}-\d{2,4}-\d{4}',
            "ZIP": r'〒?\d{3}-\d{4}',
            "MY_NUMBER": r'\d{4}[-\s]?\d{4}[-\s]?\d{4}'
        }
    def scan(self, text: str) -> dict:
        findings = {}
        for p_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                findings[p_type] = list(set(matches))
        count = sum(len(v) for v in findings.values())
        return {
            "has_risks": count > 0,
            "risks": findings,
            "risk_count": count
        }

# --- 🎨 Style Module ---
class StyleManager:
    """スタイル定義とプロンプト生成"""
    STYLES = {
        "analyze_component": {
            "system": """
あなたはプロンプトエンジニアリングの専門家です。入力された記事やドキュメントを分析し、ユーザーのデータベース用に「機能コンポーネント」を抽出してください。
出力は以下のMarkdownテーブル形式のみを行ってください。余計な説明は不要です。

| Link | #Tag | 🔧 Component (Mechanism) | 🎯 Trigger (40文字以内) | 🔗 Synergy |

**ルール:**
- **Link**: 記事のタイトル（または空欄）
- **#Tag**: #Comp/Structure, #Comp/Reasoning, #Comp/Safety などから適切なものを選択
- **Component**: 技術名 + (メカニズムの簡潔な説明)
- **Trigger**: その技術を使うべき具体的な状況（40文字以内）
- **Synergy**: 相性の良い他の技術（CoT, Few-shot, Role-playなど）
""",
            "params": {"temperature": 0.1}
        },
        "reasoning_enhancer": {
            "system": """
あなたはAIプロンプト作成の達人です。入力された単純なプロンプトを、より高度な推論を引き出すための「強化版プロンプト」に書き換えてください。

**必須要件:**
1. `<thinking_process>` タグを追加し、モデルに思考の連鎖（CoT）を強制する。
2. 曖昧な指示を具体化し、前提条件やゴールを明確にする。
3. 出力形式を指定する（Markdownなど）。
""",
            "params": {"temperature": 0.7}
        },
        "structure_data": {
            "system": """
あなたは情報整理のスペシャリストです。入力された雑多なメモやテキストを、Obsidianでの利用に適した「構造化されたMarkdown」に整形してください。

**整形ルール:**
- 適切な見出し（##）をつける
- 箇条書き（-）や番号付きリスト（1.）を活用する
- 重要なキーワードは太字（**）にする
- 関連するタグ（#Idea, #Todoなど）を末尾に提案する
""",
            "params": {"temperature": 0.3}
        },
        "summary": {
            "system": "あなたは要約のプロです。入力されたテキストの要点を抽出し、箇条書きで簡潔にまとめてください。",
            "params": {"temperature": 0.1}
        },
        "proofread": {
            "system": "あなたは校正者です。文意を変えず、誤字脱字や不自然な表現のみを修正してください。",
            "params": {"temperature": 0.0}
        }
    }

    def get_config(self, style_key: str, app_name: str = None) -> dict:
        base = self.STYLES.get(style_key, self.STYLES["proofread"]).copy()
        if app_name:
            if "slack" in app_name.lower():
                base["system"] += " (Slack向けに短く)"
            elif "mail" in app_name.lower():
                base["system"] += " (メールの件名と本文を含めて)"
        return base

# --- ⚙️ Core Logic (v3.0.1: Safety Filter対応) ---
def get_text_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()

def sanitize_log(text: str, max_length: int = 20) -> str:
    """ログ用にテキストをサニタイズ（PII除去）"""
    if not text:
        return "[empty]"
    # ハッシュ化して識別可能だが復元不可能にする
    text_hash = get_text_hash(text)[:8]
    return f"[text:{text_hash}...len={len(text)}]"

async def execute_gemini(text: str, config: dict) -> dict:
    """
    Gemini API呼び出し（v3.0.1: Safety Filter対応）
    
    Returns:
        dict: {"success": bool, "result": str, "error": str, "blocked_reason": str}
    """
    model = genai.GenerativeModel(settings.MODEL_FAST)
    try:
        response = await model.generate_content_async(
            f"{config['system']}\n\n【入力】\n{text}",
            generation_config=genai.types.GenerationConfig(
                temperature=config["params"]["temperature"]
            )
        )
        
        # Safety Filter チェック
        if not response.candidates:
            return {
                "success": False,
                "result": None,
                "error": "blocked",
                "blocked_reason": "コンテンツがブロックされました（安全フィルター）"
            }
        
        candidate = response.candidates[0]
        
        # finish_reason チェック（文字列比較）
        if hasattr(candidate, 'finish_reason'):
            finish_reason_str = str(candidate.finish_reason)
            if 'SAFETY' in finish_reason_str:
                return {
                    "success": False,
                    "result": None,
                    "error": "safety_blocked",
                    "blocked_reason": "安全上の理由でブロックされました"
                }
            elif 'RECITATION' in finish_reason_str:
                return {
                    "success": False,
                    "result": None,
                    "error": "recitation_blocked",
                    "blocked_reason": "引用制限によりブロックされました"
                }
        
        # 正常レスポンス
        if hasattr(candidate, 'content') and candidate.content.parts:
            return {
                "success": True,
                "result": candidate.content.parts[0].text.strip(),
                "error": None,
                "blocked_reason": None
            }
        
        return {
            "success": False,
            "result": None,
            "error": "empty_response",
            "blocked_reason": "空のレスポンスが返されました"
        }
        
    except Exception as e:
        return {
            "success": False,
            "result": None,
            "error": "api_error",
            "blocked_reason": str(e)
        }

def process_sync(req: TextRequest) -> dict:
    """同期処理（メイン）"""
    style_mgr = StyleManager()
    config = style_mgr.get_config(req.style, req.current_app)
    
    # ログはサニタイズ（PII除去）
    print(f"📩 処理開始: {sanitize_log(req.text)} style={req.style}")
    
    try:
        # 同期版のGemini呼び出し
        model = genai.GenerativeModel(settings.MODEL_FAST)
        # 温度設定（リクエスト指定があれば優先）
        temp = req.temperature if req.temperature is not None else config["params"]["temperature"]
        
        response = model.generate_content(
            f"{config['system']}\n\n【入力】\n{req.text}",
            generation_config=genai.types.GenerationConfig(
                temperature=temp
            )
        )
        
        # Safety Filter チェック
        if not response.candidates:
            print("⚠️ 処理失敗: blocked")
            return {
                "error": "blocked",
                "message": "コンテンツがブロックされました（安全フィルター）",
                "action": "テキストを修正して再試行してください"
            }
        
        candidate = response.candidates[0]
        
        # finish_reason チェック（文字列比較）
        if hasattr(candidate, 'finish_reason'):
            finish_reason_str = str(candidate.finish_reason)
            if 'SAFETY' in finish_reason_str:
                print("⚠️ 処理失敗: safety_blocked")
                return {
                    "error": "safety_blocked",
                    "message": "安全上の理由でブロックされました",
                    "action": "テキストを修正して再試行してください"
                }
        
        # 正常レスポンス
        if hasattr(candidate, 'content') and candidate.content.parts:
            result_text = candidate.content.parts[0].text.strip()
            print(f"✅ 処理完了: {sanitize_log(result_text)}")
            return {"result": result_text, "style": req.style}
        
        print("⚠️ 処理失敗: empty_response")
        return {
            "error": "empty_response",
            "message": "空のレスポンスが返されました",
            "action": "テキストを修正して再試行してください"
        }
            
    except Exception as e:
        print(f"❌ 例外発生: {type(e).__name__}: {e}")
        return {
            "error": "internal_error",
            "message": "内部エラーが発生しました",
            "action": "しばらく待ってから再試行してください"
        }

async def run_prefetch(text: str, styles: list, db: Session):
    """先読み処理（並列実行）"""
    text_hash = get_text_hash(text)
    
    # ログはサニタイズ
    print(f"🚀 Pre-Fetch開始: {sanitize_log(text)} styles={styles}")
    
    cache = db.query(PrefetchCache).filter(PrefetchCache.hash_id == text_hash).first()
    
    if not cache:
        cache = PrefetchCache(hash_id=text_hash, original_text=text, results={})
        db.add(cache)
        db.commit()
    
    style_mgr = StyleManager()
    tasks = []
    style_names = []
    
    for style in styles:
        config = style_mgr.get_config(style)
        tasks.append(execute_gemini(text, config))
        style_names.append(style)
        
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    current_results = dict(cache.results) if cache.results else {}
    for name, res in zip(style_names, results):
        if isinstance(res, Exception):
            current_results[name] = f"Error: {str(res)}"
        elif res.get("success"):
            current_results[name] = res["result"]
        else:
            current_results[name] = f"Error: {res.get('blocked_reason', 'Unknown')}"
        
    cache.results = current_results
    cache.created_at = datetime.utcnow()
    db.commit()
    print(f"✅ Pre-Fetch完了: {len(style_names)} styles")
