"""
AI Clipboard Pro v3.0 - Production Ready Installer
実行すると、v3.0の全ソースコード（本番対応版）が展開されます。

v3.0.1 変更点:
- Bearer Token認証の追加
- Gemini Safety Filterエラーハンドリング
- ログからPII除去
- ヘルスチェックエンドポイント追加
- エラーメッセージの改善
"""
import os

print("🚀 AI Clipboard Pro v3.0.1 インストーラー (Production Ready)")
print("-" * 50)

# --- 1. config.py ---
print("📝 config.py を生成中...")
with open("config.py", "w", encoding="utf-8") as f:
    f.write('''import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str = "YOUR_API_KEY_HERE"
    DATABASE_URL: str = "sqlite:///./tasks.db"
    
    # モデル設定
    MODEL_FAST: str = "gemini-1.5-flash"
    MODEL_SMART: str = "gemini-1.5-pro"
    
    # 🔐 認証設定 (v3.0.1)
    API_TOKEN: str = ""  # 空の場合は認証なし（開発モード）
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
''')

# --- 2. models.py ---
print("📝 models.py を生成中...")
with open("models.py", "w", encoding="utf-8") as f:
    f.write('''from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Optional, Any, List

Base = declarative_base()

# DB Models
class PrefetchCache(Base):
    __tablename__ = "prefetch_cache"
    hash_id = Column(String, primary_key=True, index=True)
    original_text = Column(Text)
    results = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

class Preset(Base):
    __tablename__ = "presets"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    config = Column(JSON)

# API Models
class TextRequest(BaseModel):
    text: str
    style: Optional[str] = Field(None, description="business, casual, summary, etc.")
    current_app: Optional[str] = Field(None, description="Optional: アプリ名による補正用")
    mode: Optional[str] = None
    temperature: Optional[float] = None

class PrefetchRequest(BaseModel):
    text: str
    target_styles: List[str] = ["business", "casual", "summary"]

class ScanResponse(BaseModel):
    has_risks: bool
    risks: Dict[str, List[str]]
    risk_count: int
    message: str

# v3.0.1: 改善されたエラーレスポンス
class ErrorResponse(BaseModel):
    error: str = Field(..., description="エラー種別")
    message: str = Field(..., description="ユーザー向けメッセージ")
    detail: Optional[str] = Field(None, description="技術的詳細（開発者向け）")
    action: Optional[str] = Field(None, description="推奨アクション")
''')

# --- 3. database.py ---
print("📝 database.py を生成中...")
with open("database.py", "w", encoding="utf-8") as f:
    f.write('''from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models import Base

engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''')

# --- 4. logic.py ---
print("📝 logic.py (v3.0.1 Production) を生成中...")
with open("logic.py", "w", encoding="utf-8") as f:
    f.write('''import google.generativeai as genai
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
            "EMAIL": r\'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}\',
            "PHONE": r\'\\d{2,4}-\\d{2,4}-\\d{4}\',
            "ZIP": r\'〒?\\d{3}-\\d{4}\',
            "MY_NUMBER": r\'\\d{4}[-\\s]?\\d{4}[-\\s]?\\d{4}\'
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
        "business": {
            "system": "あなたは優秀な秘書です。入力されたテキストを、丁寧で礼儀正しいビジネスメールや報告書の形式に整えてください。",
            "params": {"temperature": 0.3}
        },
        "casual": {
            "system": "あなたは親しい友人です。入力されたテキストを、SlackやLINE向けのフランクで親しみやすい口調に変換してください。絵文字も適度に使って。",
            "params": {"temperature": 0.7}
        },
        "summary": {
            "system": "あなたは要約のプロです。入力されたテキストの要点を抽出し、箇条書きで簡潔にまとめてください。",
            "params": {"temperature": 0.1}
        },
        "english": {
            "system": "あなたはプロの翻訳家です。入力されたテキストを自然なビジネス英語に翻訳してください。",
            "params": {"temperature": 0.2}
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
            f"{config[\'system\']}\\n\\n【入力】\\n{text}",
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
        
        # finish_reason チェック
        if hasattr(candidate, \'finish_reason\'):
            from google.generativeai.types import FinishReason
            if candidate.finish_reason == FinishReason.SAFETY:
                return {
                    "success": False,
                    "result": None,
                    "error": "safety_blocked",
                    "blocked_reason": "安全上の理由でブロックされました"
                }
            elif candidate.finish_reason == FinishReason.RECITATION:
                return {
                    "success": False,
                    "result": None,
                    "error": "recitation_blocked",
                    "blocked_reason": "引用制限によりブロックされました"
                }
        
        # 正常レスポンス
        if hasattr(candidate, \'content\') and candidate.content.parts:
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
    
    import asyncio
    try:
        result = asyncio.run(execute_gemini(req.text, config))
        
        if result["success"]:
            print(f"✅ 処理完了: {sanitize_log(result[\'result\'])}")
            return {"result": result["result"], "style": req.style}
        else:
            print(f"⚠️ 処理失敗: {result[\'error\']}")
            return {
                "error": result["error"],
                "message": result["blocked_reason"],
                "action": "テキストを修正して再試行してください"
            }
            
    except Exception as e:
        print(f"❌ 例外発生: {type(e).__name__}")
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
            current_results[name] = f"Error: {res.get(\'blocked_reason\', \'Unknown\')}"
        
    cache.results = current_results
    cache.created_at = datetime.utcnow()
    db.commit()
    print(f"✅ Pre-Fetch完了: {len(style_names)} styles")
''')

# --- 5. main.py ---
print("📝 main.py (v3.0.1 Production) を生成中...")
with open("main.py", "w", encoding="utf-8") as f:
    f.write('''from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db, init_db
from models import TextRequest, PrefetchRequest, ScanResponse, PrefetchCache, ErrorResponse
from config import settings
import logic
import asyncio
from datetime import datetime

init_db()
app = FastAPI(
    title="AI Clipboard Pro v3.0.1",
    description="The Unbreakable Hybrid - Production Ready",
    version="3.0.1"
)

# --- 🔐 認証ミドルウェア (v3.0.1) ---
async def verify_token(authorization: str = Header(None)):
    """
    Bearer Token認証
    API_TOKENが設定されている場合のみ認証を要求
    """
    # 認証が設定されていない場合はスキップ（開発モード）
    if not settings.API_TOKEN:
        return True
    
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "unauthorized",
                "message": "認証が必要です",
                "action": "Authorization: Bearer <token> ヘッダーを追加してください"
            }
        )
    
    # Bearer token形式をチェック
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail={
                "error": "invalid_auth_format",
                "message": "認証形式が不正です",
                "action": "Authorization: Bearer <token> 形式で指定してください"
            }
        )
    
    if parts[1] != settings.API_TOKEN:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "forbidden",
                "message": "トークンが無効です",
                "action": "正しいトークンを指定してください"
            }
        )
    
    return True

# --- 🏥 ヘルスチェック (v3.0.1) ---
@app.get("/", tags=["Health"])
def health_check():
    """基本的なヘルスチェック"""
    return {"status": "running", "version": "3.0.1"}

@app.get("/healthz", tags=["Health"])
def detailed_health_check():
    """
    詳細ヘルスチェック（監視ツール向け）
    
    - status: running/degraded/down
    - checks: 各コンポーネントの状態
    """
    checks = {
        "api": "ok",
        "gemini": "unknown",
        "database": "unknown"
    }
    
    # DB接続チェック
    try:
        from database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {type(e).__name__}"
    
    # Gemini API設定チェック
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "YOUR_API_KEY_HERE":
        checks["gemini"] = "configured"
    else:
        checks["gemini"] = "not_configured"
    
    # 総合ステータス
    all_ok = all(v in ["ok", "configured"] for v in checks.values())
    
    return {
        "status": "running" if all_ok else "degraded",
        "version": "3.0.1",
        "timestamp": datetime.utcnow().isoformat(),
        "auth_enabled": bool(settings.API_TOKEN),
        "checks": checks
    }

# --- 🎨 スタイル一覧 ---
@app.get("/styles", tags=["Core"])
def list_styles():
    """利用可能なスタイル一覧"""
    return {
        "styles": [
            {"id": "business", "name": "ビジネス", "description": "丁寧・フォーマル"},
            {"id": "casual", "name": "カジュアル", "description": "フランク・絵文字あり"},
            {"id": "summary", "name": "要約", "description": "箇条書き・簡潔"},
            {"id": "english", "name": "英語翻訳", "description": "ビジネス英語"},
            {"id": "proofread", "name": "校正", "description": "誤字脱字修正のみ"}
        ]
    }

# --- ⚙️ メイン処理 (認証付き) ---
@app.post("/process", tags=["Core"], dependencies=[Depends(verify_token)])
def process_text(req: TextRequest):
    """
    メイン処理: スタイル指定でテキスト変換
    
    認証が有効な場合、Authorization: Bearer <token> ヘッダーが必要
    """
    result = logic.process_sync(req)
    
    # エラーレスポンスの場合は適切なステータスコードを返す
    if "error" in result:
        if result["error"] == "blocked" or result["error"] == "safety_blocked":
            raise HTTPException(status_code=400, detail=result)
        else:
            raise HTTPException(status_code=500, detail=result)
    
    return result

# --- 🛡️ 安全スキャン ---
@app.post("/scan", response_model=ScanResponse, tags=["Safety"])
def scan_text(req: TextRequest):
    """個人情報検知（認証不要）"""
    scanner = logic.PrivacyScanner()
    result = scanner.scan(req.text)
    if result["has_risks"]:
        result["message"] = f"⚠️ {result[\'risk_count\']}件の個人情報が含まれています。送信前に確認してください。"
    else:
        result["message"] = "✅ 個人情報は検出されませんでした。"
    return result

# --- 🚀 先読み (認証付き) ---
@app.post("/prefetch", tags=["Background"], dependencies=[Depends(verify_token)])
async def trigger_prefetch(req: PrefetchRequest, bg_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """スイッチON時のみ呼ばれる先読み"""
    bg_tasks.add_task(asyncio.create_task, logic.run_prefetch(req.text, req.target_styles, db))
    return {"status": "accepted", "hash": logic.get_text_hash(req.text)}

@app.get("/prefetch/{text_hash}", tags=["Background"])
def get_prefetch_result(text_hash: str, db: Session = Depends(get_db)):
    """先読み結果取得（認証不要）"""
    cache = db.query(PrefetchCache).filter(PrefetchCache.hash_id == text_hash).first()
    if not cache:
        return {"status": "not_found", "results": {}}
    return {"status": "found", "results": cache.results}

# --- ❌ グローバルエラーハンドラ ---
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """未処理例外のキャッチ（詳細をログに、概要をクライアントに）"""
    import traceback
    print(f"❌ Unhandled Exception: {type(exc).__name__}")
    print(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "予期しないエラーが発生しました",
            "action": "問題が続く場合は管理者に連絡してください"
        }
    )

if __name__ == "__main__":
    import uvicorn
    print("🚀 AI Clipboard Pro v3.0.1 - Production Ready")
    print("-" * 50)
    print("📖 API ドキュメント: http://localhost:8000/docs")
    print("🏥 ヘルスチェック: http://localhost:8000/healthz")
    print("-" * 50)
    if settings.API_TOKEN:
        print("🔐 認証: 有効 (Bearer Token)")
    else:
        print("⚠️  認証: 無効 (開発モード)")
    print("-" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
''')

# --- 6. requirements.txt ---
print("📝 requirements.txt を生成中...")
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write('''fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
google-generativeai>=0.3.0
python-dotenv>=1.0.0
sqlalchemy>=2.0.0
''')

# --- 7. .env.example ---
print("📝 .env.example を生成中...")
with open(".env.example", "w", encoding="utf-8") as f:
    f.write('''# AI Clipboard Pro v3.0.1 設定

# Gemini API Key (必須)
GEMINI_API_KEY=your_gemini_api_key_here

# 認証トークン (本番環境では必須)
# 空の場合は認証なし（開発モード）
API_TOKEN=your_secret_token_here

# データベース (デフォルト: SQLite)
DATABASE_URL=sqlite:///./tasks.db
''')

print("-" * 50)
print("✅ v3.0.1 (Production Ready) インストール完了！")
print("")
print("📋 次のステップ:")
print("  1. .env.example を .env にコピー")
print("  2. GEMINI_API_KEY を設定")
print("  3. 本番環境では API_TOKEN を設定")
print("  4. python main.py でサーバー起動")
print("")
print("🔐 セキュリティ:")
print("  - API_TOKENが設定されている場合、/process と /prefetch は認証必須")
print("  - /scan と /healthz は認証不要（公開可）")
