"""
AI Clipboard API - FastAPI REST Server
スマホアプリや外部サービスから呼び出せるAPIサーバー
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import os

# --- アプリケーション設定 ---
app = FastAPI(
    title="AI Clipboard API",
    description="プロンプト最適化ライブラリのREST API",
    version="1.0.0"
)

# CORS設定（クロスオリジンリクエストを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Gemini API設定 ---
model = None

def get_model():
    """Gemini モデルを取得（遅延初期化）"""
    global model
    if model is not None:
        return model
    
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return None
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except Exception as e:
        print(f"Gemini API初期化エラー: {e}")
        return None


# --- ロジッククラス ---
class DataSynthesizer:
    """Few-Shotデータ合成"""
    def __init__(self, model):
        self.model = model
        
    def generate_examples(self, intent: str, count: int = 3) -> str:
        prompt = f"""ユーザーの意図「{intent}」を達成するための、理想的な「入力と出力の例」を{count}つ作成せよ。
Example 1:
Input: ...
Output: ..."""
        try:
            return self.model.generate_content(prompt).text.strip()
        except:
            return ""


# --- リクエスト/レスポンス型定義 ---
class RefineRequest(BaseModel):
    """テキスト最適化リクエスト"""
    text: str = Field(..., description="変換するテキスト")
    style: str = Field(default="ビジネス (丁寧)", description="変換スタイル")
    use_few_shot: bool = Field(default=True, description="Few-Shot合成を使用するか")

class RefineResponse(BaseModel):
    """テキスト最適化レスポンス"""
    result: str
    intent: str
    style: str

class StatusResponse(BaseModel):
    """ステータスレスポンス"""
    status: str
    message: str
    api_configured: bool

class StylesResponse(BaseModel):
    """利用可能なスタイル"""
    styles: List[str]


# --- APIエンドポイント ---

@app.get("/", response_model=StatusResponse)
def read_root():
    """ヘルスチェック"""
    return StatusResponse(
        status="ok",
        message="AI Clipboard API is running!",
        api_configured=get_model() is not None
    )

@app.get("/styles", response_model=StylesResponse)
def get_styles():
    """利用可能な変換スタイルを取得"""
    return StylesResponse(styles=[
        "ビジネスメール (謝罪・依頼)",
        "エンジニア向け (要件定義)",
        "SNS投稿 (親しみやすく)",
        "英語翻訳 (ビジネス)",
        "論理的要約 (箇条書き)",
        "丁寧なカスタマーサポート",
        "技術ドキュメント"
    ])

@app.post("/refine", response_model=RefineResponse)
async def refine_text(body: RefineRequest):
    """テキストを指定されたスタイルに最適化"""
    print(f"📩 受信: {body.text[:30]}...")
    
    current_model = get_model()
    if current_model is None:
        raise HTTPException(
            status_code=503,
            detail="Gemini APIが設定されていません。GEMINI_API_KEY環境変数を設定してください。"
        )
    
    try:
        # 1. 意図理解
        intent_resp = current_model.generate_content(
            f"以下のテキストの目的を簡潔に要約せよ: {body.text}"
        )
        intent = intent_resp.text.strip()
        
        # 2. 事例生成 (Data Synthesis)
        examples = ""
        if body.use_few_shot:
            synthesizer = DataSynthesizer(current_model)
            examples = synthesizer.generate_examples(intent)
        
        # 3. 最適化実行
        prompt = f"""
あなたはプロのライターです。
以下の「ラフな入力」を「{body.style}」に合わせて書き直してください。
{"以下の「成功事例」を参考に、クオリティを高めてください。" if examples else ""}

{"【成功事例】" + chr(10) + examples if examples else ""}

【入力】
{body.text}

【出力】
書き直したテキストのみを出力してください。（解説不要）
"""
        response = current_model.generate_content(prompt)
        result_text = response.text.strip()
        
        print(f"📤 返信: {result_text[:30]}...")
        
        return RefineResponse(
            result=result_text,
            intent=intent,
            style=body.style
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Filter (下処理) リクエスト/レスポンス ---
class FilterRequest(BaseModel):
    """プロンプト下処理リクエスト"""
    text: str = Field(..., description="下処理するテキスト")
    mode: str = Field(default="raw", description="raw/light (整形), heavy (構造化), deep (逆質問)")
    context: str = Field(default="", description="deepモードで逆質問への回答を含める")

class FilterResponse(BaseModel):
    """プロンプト下処理レスポンス"""
    type: str = Field(..., description="complete (完了) or question (追加質問)")
    text: str
    mode: str


def process_prompt(text: str, mode: str, context: str, current_model) -> dict:
    """
    モードに応じてプロンプトを処理する
    
    - raw/light: 高速整形（ノイズ除去のみ）
    - heavy: 完全構造化（6W3H補完）
    - deep: 逆質問で不足情報を補完
    """
    import google.generativeai as genai
    import json
    
    # -------------------------------------------------
    # 1. 【Raw / Light】: 高速整形
    # -------------------------------------------------
    if mode in ["raw", "light"]:
        system_prompt = """
あなたは「テキスト整形ツール」です。
ユーザーの入力を、チャットボットへの指示として違和感がないように「体裁」だけを整えてください。

【ルール】
1. 文意、ニュアンスは可能な限り維持する（勝手に補完しない）。
2. 「えーと」などの明らかなノイズのみ削除する。
3. 語尾を「〜してください」「〜せよ」等の命令形、または体言止めに統一する。
4. ロール（人格）の付与はしない。

出力は整形後のテキストのみ。
"""
        user_prompt = f"【入力】\n{text}\n\n【整形後】"
        
        try:
            response = current_model.generate_content(
                system_prompt + user_prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.1)
            )
            return {"type": "complete", "text": response.text.strip()}
        except Exception as e:
            return {"type": "error", "text": str(e)}

    # -------------------------------------------------
    # 2. 【Heavy / Structure】: ガッツリ補完・構造化
    # -------------------------------------------------
    elif mode == "heavy":
        system_prompt = """
あなたは「指示構造化エンジン」です。
ユーザーの入力を、AIが誤解なく実行できる「完璧な仕様書」に変換してください。

【ルール】
1. 6W3H（誰が、いつ、どこで、何を、なぜ、どのように...）を推論し、不足があれば常識の範囲で補完する。
2. マークダウンで見出しを付け、視認性を高める。
3. ロール（人格）の付与はしない。
4. 抽象的な表現は具体的なパラメータに変換する。

出力は構造化された指示のみ。
"""
        user_prompt = f"【入力】\n{text}\n\n【構造化された指示】"
        
        try:
            response = current_model.generate_content(
                system_prompt + user_prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.2)
            )
            return {"type": "complete", "text": response.text.strip()}
        except Exception as e:
            return {"type": "error", "text": str(e)}

    # -------------------------------------------------
    # 3. 【Deep Research】: 不足情報の逆質問
    # -------------------------------------------------
    elif mode == "deep":
        # 既にヒアリング済みの情報（context）がある場合
        if context:
            system_prompt = """
あなたは「要件定義のプロ」です。
ユーザーの「最初の要望」と、質問に対する「追加回答」を統合し、
最終的な完成版プロンプトを出力してください。

出力は完成版プロンプトのみ。
"""
            user_prompt = f"【当初の要望】\n{text}\n\n【追加回答】\n{context}\n\n【完成版プロンプト】"
            
            try:
                response = current_model.generate_content(system_prompt + user_prompt)
                return {"type": "complete", "text": response.text.strip()}
            except Exception as e:
                return {"type": "error", "text": str(e)}
        
        # 初回：足りない情報を探る
        else:
            system_prompt = """
あなたは「慎重なコンサルタント」です。
ユーザーの要望を実現するために「致命的に足りない情報」や「確認すべき曖昧な点」があれば、
それをたずねる質問を1つ〜2つ作成してください。

もし情報が十分であれば、そのまま最適化されたプロンプトを出力してください。

出力形式は厳密にJSONで:
{
    "status": "question" または "complete",
    "content": "質問文" または "完成したプロンプト"
}
"""
            user_prompt = f"【要望】\n{text}"
            
            try:
                response = current_model.generate_content(
                    system_prompt + user_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.2,
                        response_mime_type="application/json"
                    )
                )
                
                result = json.loads(response.text)
                
                if result.get("status") == "question":
                    return {"type": "question", "text": result["content"]}
                else:
                    return {"type": "complete", "text": result["content"]}
                    
            except json.JSONDecodeError:
                # JSONパースに失敗した場合はそのまま返す
                return {"type": "complete", "text": response.text.strip()}
            except Exception as e:
                return {"type": "error", "text": str(e)}

    return {"type": "error", "text": f"Unknown mode: {mode}"}


@app.post("/filter", response_model=FilterResponse)
async def filter_prompt(body: FilterRequest):
    """
    プロンプトを下処理する（3モード対応）
    
    - **raw/light**: 湯がく - ノイズ除去のみ、高速
    - **heavy**: 炙る - 構造化、6W3H補完
    - **deep**: 深掘り - 逆質問で不足情報を取得
    """
    print(f"🥦 処理開始 ({body.mode}): {body.text[:20]}...")
    
    current_model = get_model()
    if current_model is None:
        raise HTTPException(
            status_code=503,
            detail="Gemini APIが設定されていません。GEMINI_API_KEY環境変数を設定してください。"
        )
    
    result = process_prompt(body.text, body.mode, body.context, current_model)
    
    print(f"✨ 結果 ({result['type']}): \n{result['text'][:50]}...")
    return FilterResponse(type=result["type"], text=result["text"], mode=body.mode)


# --- 起動スクリプト ---
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 AI Clipboard API Server")
    print("-" * 40)
    print("📖 API ドキュメント: http://localhost:8000/docs")
    print("🔧 環境変数 GEMINI_API_KEY を設定してください")
    print("-" * 40)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

