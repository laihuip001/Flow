from sqlalchemy import Column, String, Text, DateTime, JSON, Integer, Boolean
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
    # v5.0 Phase 3.5: Lifecycle Management
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed_at = Column(DateTime, default=datetime.utcnow)

class Preset(Base):
    __tablename__ = "presets"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    config = Column(JSON)

class SyncJob(Base):
    """
    遅延同期ジョブ (v5.0 Phase 4: Delayed Sync)
    オフライン時のリクエストを保持し、後で処理するキュー
    """
    __tablename__ = "sync_jobs"
    id = Column(String, primary_key=True, index=True)
    text = Column(Text)
    seasoning = Column(Integer, default=30)
    result = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)  # エラー詳細
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    retry_count = Column(Integer, default=0)
    is_favorite = Column(Boolean, default=False) # v4.1 Favorite Persistence

# API Models
class TextRequest(BaseModel):
    text: str = Field(..., max_length=100000)
    seasoning: int = Field(30, description="Seasoning level 0-100 (0=Salt, 50=Sauce, 100=Spice)")
    current_app: Optional[str] = Field(None, description="Optional: アプリ名による補正用")
    mode: Optional[str] = None
    temperature: Optional[float] = None

class PrefetchRequest(BaseModel):
    text: str = Field(..., max_length=100000)
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
    seasoning: int = Field(30, description="Seasoning level 0-100")
    prompt: Optional[str] = Field(None, description="追加の指示")
