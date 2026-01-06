#!/usr/bin/env python3
"""
AI Clipboard Pro v2.6 - ワンクリックインストーラー (Safety Update Edition)

このスクリプトを実行すると、現在（v2.6）の最新コードが展開されます。
ネットカフェや別環境での復元用アップです。

使い方:
    python setup_project.py
"""

import os

print("🚀 AI Clipboard Pro v2.6 インストーラー")
print("-" * 50)

# --- 1. config.py ---
print("📝 config.py を生成中...")
with open("config.py", "w", encoding="utf-8") as f:
    f.write('''import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str = "YOUR_API_KEY_HERE"
    DATABASE_URL: str = "sqlite:///./tasks.db"
    MODEL_FAST: str = "gemini-1.5-flash"
    MODEL_SMART: str = "gemini-1.5-pro"
    COST_INPUT_FLASH: float = 0.075
    COST_OUTPUT_FLASH: float = 0.30
    COST_INPUT_PRO: float = 3.50
    COST_OUTPUT_PRO: float = 10.50
    USD_JPY_RATE: float = 150.0

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
''')

# --- 2. models.py ---
print("📝 models.py を生成中...")
with open("models.py", "w", encoding="utf-8") as f:
    f.write('''from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Optional, Any, List

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String)
    status = Column(String, default="pending")
    input_text = Column(Text)
    result_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    cost_yen = Column(Float, default=0.0)

class Preset(Base):
    __tablename__ = "presets"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class PrefetchCache(Base):
    __tablename__ = "prefetch_cache"
    hash_id = Column(String, primary_key=True, index=True)
    original_text = Column(Text)
    results = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

class TextRequest(BaseModel):
    text: str
    preset_id: Optional[str] = None
    current_app: Optional[str] = Field(None, description="呼び出し元アプリ名")
    mode: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    info_valve: Optional[float] = Field(None, ge=-1.0, le=1.0)
    use_privacy_wrap: Optional[bool] = None
    output_format: Optional[str] = None
    target_language: Optional[str] = None
    tone: Optional[str] = None

class PrefetchRequest(BaseModel):
    text: str
    target_presets: Optional[List[str]] = None
    current_app: Optional[str] = None

class PresetCreate(BaseModel):
    id: str
    name: str
    description: str = ""
    config: Dict[str, Any]

class PresetResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    config: Dict[str, Any]
    created_at: datetime

class JobResponse(BaseModel):
    job_id: int
    status: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: int
    status: str
    result: Optional[str]
    cost_yen: float
    completed_at: Optional[datetime]

class AnalysisResponse(BaseModel):
    recommended_mode: str
    reason: str
    estimates: Dict[str, Any]

# v2.6 New Models
class ScanRequest(BaseModel):
    text: str = Field(..., description="スキャン対象")

class ScanResponse(BaseModel):
    has_risks: bool
    risks: Dict[str, List[str]] = {}
    risk_count: int = 0
    message: str = ""

class MultiChoiceRequest(BaseModel):
    text: str
    current_app: Optional[str] = None
    acknowledge_risks: bool = False

class MultiChoiceResponse(BaseModel):
    choices: List[Dict[str, str]]
    config_used: Dict[str, Any]
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
print("📝 logic.py を生成中...")
with open("logic.py", "w", encoding="utf-8") as f:
    f.write('''import google.generativeai as genai
from config import settings
import json
import hashlib
from sqlalchemy.orm import Session
from models import Job, Preset, TextRequest, PrefetchCache
from datetime import datetime
import asyncio
import re
import os

# API Key Check
if "GEMINI_API_KEY" in os.environ:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
elif settings.GEMINI_API_KEY != "YOUR_API_KEY_HERE":
    genai.configure(api_key=settings.GEMINI_API_KEY)

class PrivacyScanner:
    """v2.6: 検知のみ行うスキャナー"""
    def __init__(self):
        self.patterns = {
            "EMAIL": r\'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}\',
            "PHONE": r\'\\d{2,4}-\\d{2,4}-\\d{4}\',
            "ZIP": r\'〒?\\d{3}-\\d{4}\',
            "CREDIT_CARD": r\'\\d{4}[-\\s]?\\d{4}[-\\s]?\\d{4}[-\\s]?\\d{4}\',
            "MY_NUMBER": r\'\\d{4}[-\\s]?\\d{4}[-\\s]?\\d{4}\'
        }
    def scan(self, text: str) -> dict:
        findings = {}
        for p_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                findings[p_type] = list(set(matches))
        return {
            "has_risks": len(findings) > 0,
            "risks": findings,
            "risk_count": sum(len(v) for v in findings.values())
        }

class PrivacyWrapper:
    """@deprecated"""
    def __init__(self):
        print("⚠️ PrivacyWrapper is deprecated.")
    def mask(self, text: str) -> str: return text
    def unmask(self, text: str) -> str: return text

class ContextBallast:
    """アプリに応じた自動設定"""
    def __init__(self):
        self.ballast_map = {
            "slack": {"tone": "casual", "output_format": "markdown", "mode": "light", "instruction": "Slack用。簡潔に。"},
            "discord": {"tone": "casual", "output_format": "markdown", "mode": "light", "instruction": "Discord用。フランクに。"},
            "line": {"tone": "casual", "output_format": "plain", "mode": "light", "instruction": "LINE用。短文で。"},
            "gm": {"tone": "polite", "output_format": "plain", "mode": "heavy", "instruction": "Gmailビジネスメール用。"},
            "outlook": {"tone": "polite", "output_format": "plain", "mode": "heavy", "instruction": "Outlookビジネスメール用。"},
            "keep": {"tone": "bullet", "output_format": "plain", "mode": "light", "instruction": "メモ用。要約して。"},
            "notion": {"tone": "academic", "output_format": "markdown", "mode": "heavy", "instruction": "Notion用。構造化重視。"},
            "chrome": {"info_valve": -0.5, "instruction": "Web検索クエリ、または要約。"},
            "twitter": {"tone": "emotional", "output_format": "plain", "info_valve": -0.2, "instruction": "SNS投稿。140字以内。"}
        }
    def get_ballast(self, app_name: str) -> dict:
        if not app_name: return {}
        app_lower = app_name.lower()
        for key, config in self.ballast_map.items():
            if key in app_lower:
                print(f"⚓ Ballast: {key}")
                return config.copy()
        return {}

def get_tone_instruction(tone: str) -> str:
    instructions = {
        "polite": "【口調】丁寧な敬語。",
        "casual": "【口調】カジュアル。",
        "academic": "【口調】論文調。",
        "bullet": "【口調】箇条書き。",
        "emotional": "【口調】感情豊かに。"
    }
    return instructions.get(tone, "")

def get_format_instruction(fmt: str) -> str:
    instructions = {
        "markdown": "【形式】Markdown。",
        "plain": "【形式】プレーンテキスト。",
        "json": "【形式】JSON。"
    }
    return instructions.get(fmt, "")

def get_valve_instruction(pressure: float) -> str:
    if pressure is None or pressure == 0: return ""
    if pressure < -0.6: return "【極限圧縮】可能な限り短く。"
    elif pressure < -0.2: return "【要約】簡潔に。"
    elif pressure > 0.6: return "【大幅拡張】詳細に補完。"
    elif pressure > 0.2: return "【補完】言葉足らずを補う。"
    return ""

def merge_config(req: TextRequest, db: Session) -> dict:
    final = {
        "mode": "light", "temperature": 0.5, "info_valve": 0.0,
        "use_privacy_wrap": False, "output_format": "plain",
        "target_language": None, "tone": None, "extra_instruction": ""
    }
    ballast = ContextBallast()
    app_cfg = ballast.get_ballast(req.current_app)
    if "instruction" in app_cfg:
        final["extra_instruction"] = app_cfg.pop("instruction")
    final.update(app_cfg)
    if req.preset_id:
        preset = db.query(Preset).filter(Preset.id == req.preset_id).first()
        if preset and preset.config:
            final.update(preset.config)
    for f in ["mode", "temperature", "info_valve", "use_privacy_wrap", "output_format", "target_language", "tone"]:
        v = getattr(req, f, None)
        if v is not None: final[f] = v
    return final

def process_sync_request(req: TextRequest, db: Session):
    cfg = merge_config(req, db)
    text = req.text
    privacy = PrivacyScanner() # v2.6 change
    # Note: Privacy checking is now done via /scan or manual confirmation
    
    model_name = settings.MODEL_FAST if cfg["mode"] == "light" else settings.MODEL_SMART
    model = genai.GenerativeModel(model_name)
    
    base = "テキスト整形ツール" if cfg["mode"] == "light" else "指示構造化エンジン"
    valve = get_valve_instruction(cfg["info_valve"])
    tone = get_tone_instruction(cfg["tone"])
    fmt = get_format_instruction(cfg["output_format"])
    lang = f"出力言語: {cfg[\'target_language\']}" if cfg["target_language"] else ""
    app = f"【文脈】{cfg[\'extra_instruction\']}" if cfg["extra_instruction"] else ""
    
    prompt = f"""あなたは{base}です。
{app} {valve} {tone} {fmt} {lang}
【禁止】余計な会話禁止。

入力:
{text}"""
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=cfg["temperature"])
        )
        return {"result": response.text.strip(), "config_used": cfg}
    except Exception as e:
        return {"error": str(e)}

async def execute_single_task(text: str, config: dict) -> str:
    model = genai.GenerativeModel(settings.MODEL_FAST)
    base = "テキスト整形ツール" if config.get("mode") == "light" else "指示構造化エンジン"
    valve = get_valve_instruction(config.get("info_valve"))
    tone = get_tone_instruction(config.get("tone"))
    fmt = get_format_instruction(config.get("output_format"))
    lang = f"出力言語: {config[\'target_language\']}" if config.get("target_language") else ""
    app = f"【文脈】{config.get(\'extra_instruction\', \'\')}"
    
    prompt = f"あなたは{base}。{app} {valve} {tone} {fmt} {lang}\\n入力:\\n{text}"
    try:
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=config.get("temperature", 0.5))
        )
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"

def get_text_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()

async def run_prefetch_background(text: str, preset_ids: list, current_app: str, db: Session):
    text_hash = get_text_hash(text)
    cache = db.query(PrefetchCache).filter(PrefetchCache.hash_id == text_hash).first()
    if not cache:
        cache = PrefetchCache(hash_id=text_hash, original_text=text, results={})
        db.add(cache)
        db.commit()
    
    tasks, names = [], []
    for pid in preset_ids:
        req = TextRequest(text=text, preset_id=pid, current_app=current_app)
        cfg = merge_config(req, db)
        tasks.append(execute_single_task(text, cfg))
        names.append(pid)
    
    if not tasks: return
    print(f"🚀 Pre-Fetch: {len(tasks)} tasks...")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    current_results = dict(cache.results) if cache.results else {}
    for name, res in zip(names, results):
        current_results[name] = str(res) if isinstance(res, Exception) else res
    cache.results = current_results
    cache.created_at = datetime.utcnow()
    db.commit()
    print(f"✅ Pre-Fetch Done: {text_hash[:8]}...")
''')

# --- 5. main.py ---
print("📝 main.py を生成中...")
with open("main.py", "w", encoding="utf-8") as f:
    f.write('''from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db, init_db
from models import (TextRequest, PresetCreate, PresetResponse, Preset, 
                   PrefetchRequest, PrefetchCache, ScanRequest, ScanResponse,
                   MultiChoiceRequest, MultiChoiceResponse, Job, JobStatusResponse, AnalysisResponse)
import logic
import hashlib
import asyncio

init_db()
app = FastAPI(title="AI Clipboard Pro v2.6", description="Safety Update")

@app.get("/")
def health_check():
    return {"status": "running", "version": "2.6"}

@app.post("/process/sync", tags=["Processing"])
def process_sync(req: TextRequest, db: Session = Depends(get_db)):
    return logic.process_sync_request(req, db)

@app.post("/prefetch", tags=["Pre-Fetch"])
async def trigger_prefetch(req: PrefetchRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    text_hash = logic.get_text_hash(req.text)
    targets = req.target_presets or ["mail_fix", "summarize", "english"]
    background_tasks.add_task(asyncio.create_task, logic.run_prefetch_background(req.text, targets, req.current_app, db))
    return {"status": "accepted", "hash_id": text_hash, "targets": targets}

@app.get("/prefetch/{text_hash}", tags=["Pre-Fetch"])
def get_prefetch(text_hash: str, db: Session = Depends(get_db)):
    cache = db.query(PrefetchCache).filter(PrefetchCache.hash_id == text_hash).first()
    if not cache: return {"status": "not_found", "results": {}}
    return {"status": "found", "results": cache.results}

@app.post("/scan", response_model=ScanResponse, tags=["v2.6 Safety"])
def scan_for_pii(req: ScanRequest):
    scanner = logic.PrivacyScanner()
    result = scanner.scan(req.text)
    if result["has_risks"]:
        result["message"] = f"⚠️ {result['risk_count']}件の個人情報が検出されました。送信しますか？"
    else:
        result["message"] = "✅ 個人情報は検出されませんでした。"
    return result

@app.post("/process/multi", response_model=MultiChoiceResponse, tags=["v2.6 Safety"])
async def process_multi_choice(req: MultiChoiceRequest, db: Session = Depends(get_db)):
    if not req.acknowledge_risks:
        scanner = logic.PrivacyScanner()
        scan_result = scanner.scan(req.text)
        if scan_result["has_risks"]:
            raise HTTPException(status_code=400, detail={"error": "pii_detected"})
    
    configs = [
        {"label": "フォーマル", "tone": "polite", "output_format": "plain", "mode": "heavy"},
        {"label": "カジュアル", "tone": "casual", "output_format": "plain", "mode": "light"},
        {"label": "要約", "tone": "bullet", "info_valve": -0.5, "mode": "light"}
    ]
    ballast = logic.ContextBallast()
    app_config = ballast.get_ballast(req.current_app)
    
    tasks = []
    for cfg in configs:
        merged = {**app_config, **cfg}
        merged["extra_instruction"] = app_config.get("instruction", "")
        tasks.append(logic.execute_single_task(req.text, merged))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    choices = []
    for cfg, result in zip(configs, results):
        choices.append({"label": cfg["label"], "result": str(result) if isinstance(result, Exception) else result})
    
    return MultiChoiceResponse(choices=choices, config_used={"app": req.current_app})

@app.post("/presets", tags=["Presets"])
def create_preset(preset: PresetCreate, db: Session = Depends(get_db)):
    db_preset = Preset(id=preset.id, name=preset.name, description=preset.description, config=preset.config)
    db.merge(db_preset)
    db.commit()
    return {"message": f"Preset \'{preset.id}\' saved."}

@app.get("/presets", response_model=List[PresetResponse], tags=["Presets"])
def list_presets(db: Session = Depends(get_db)):
    return [PresetResponse(id=p.id, name=p.name, description=p.description, config=p.config, created_at=p.created_at) for p in db.query(Preset).all()]

if __name__ == "__main__":
    import uvicorn
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

print("-" * 50)
print("✅ インストール完了！")
print("1. APIキー設定: export GEMINI_API_KEY='...'\n2. 実行: python main.py")
''')
