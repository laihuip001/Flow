from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""  # MUST be set via .env
    DATABASE_URL: str = "sqlite:///./tasks.db"
    
    # モデル設定 (gemini-3-flash-preview: 2.88s verified)
    MODEL_FAST: str = "models/gemini-3-flash-preview"
    MODEL_SMART: str = "models/gemini-3-flash-preview"
    
    # 🔐 認証設定 (v4.0)
    API_TOKEN: str = ""  # 空の場合は認証なし（開発モード）
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
