from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
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
