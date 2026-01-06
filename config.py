import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str = "YOUR_API_KEY_HERE"
    DATABASE_URL: str = "sqlite:///./tasks.db"
    
    # モデル設定
    MODEL_FAST: str = "models/gemini-3-flash-preview"
    MODEL_SMART: str = "models/gemini-flash-latest"
    
    # 🔐 認証設定 (v3.0.1)
    API_TOKEN: str = ""  # 空の場合は認証なし（開発モード）
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
