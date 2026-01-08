from sqlalchemy import Column, String, Text, DateTime, JSON, Integer
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

class SyncJob(Base):
    """
    オフライン時のリクエストを保持するキュー (v4.0 Phase 3準備)
    """
    __tablename__ = "sync_jobs"
    id = Column(String, primary_key=True, index=True)
    text = Column(Text) 
    seasoning = Column(Integer, default=30)
    result = Column(Text, nullable=True) # Output result
    status = Column(String, default="pending") # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    retry_count = Column(Integer, default=0)

# API Models
class TextRequest(BaseModel):
    text: str = Field(..., max_length=20000, description="Text to process")
    seasoning: int = Field(30, ge=0, le=100, description="Seasoning level 0-100 (0=Salt, 50=Sauce, 100=Spice)")
    current_app: Optional[str] = Field(None, description="Optional: アプリ名による補正用")
    mode: Optional[str] = None
    temperature: Optional[float] = None

class PrefetchRequest(BaseModel):
    text: str
    target_seasoning_levels: List[int] = [10, 50, 90]  # Salt, Sauce, Spice

class ScanResponse(BaseModel):
    has_risks: bool
    risks: Dict[str, List[str]]
    risk_count: int
    message: str

# v4.0: 改善されたエラーレスポンス
class ErrorResponse(BaseModel):
    error: str = Field(..., description="エラー種別")
    message: str = Field(..., description="ユーザー向けメッセージ")
    detail: Optional[str] = Field(None, description="技術的詳細（開発者向け）")
    action: Optional[str] = Field(None, description="推奨アクション")

# v3.3: P2 新機能用モデル
class DiffResponse(BaseModel):
    """Diff表示UI用レスポンス"""
    original: str = Field(..., description="元のテキスト")
    result: str = Field(..., description="変換後のテキスト")
    diff_lines: List[Dict[str, Any]] = Field(default=[], description="行ごとの差分情報")
    seasoning: Optional[int] = None
    from_cache: bool = False

class ContextMode(BaseModel):
    """コンテキスト二極化（Light/Deep）"""
    mode: str = Field(..., description="light または deep")
    description: str
    estimated_tokens: int
    estimated_cost_yen: float

class ClipboardHistoryItem(BaseModel):
    """文脈の継続性用: クリップボード履歴"""
    text: str
    timestamp: datetime
    hash_id: str
    app_name: Optional[str] = None

class ImageProcessRequest(BaseModel):
    """画像認識用リクエスト"""
    image_base64: str = Field(..., description="Base64エンコードされた画像")
    seasoning: int = Field(30, ge=0, le=100, description="Seasoning level 0-100")
    prompt: Optional[str] = Field(None, description="追加の指示")
