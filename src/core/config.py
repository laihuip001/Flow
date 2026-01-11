from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""  # MUST be set via .env
    DATABASE_URL: str = "sqlite:///./tasks.db"
    
    # モデル設定 (gemini-3-flash-preview: 2.88s verified)
    MODEL_FAST: str = "models/gemini-3-flash-preview"
    MODEL_SMART: str = "models/gemini-3-flash-preview"
    
    # 🔐 認証設定 (v4.0)
    API_TOKEN: str = ""  # 空の場合は認証なし（開発モード）
    
    # 🚀 速度最優先設定 (v4.1)
    USER_SYSTEM_PROMPT: str = ""  # ユーザーカスタム指示（50トークン上限推奨）
    PRIVACY_MODE: bool = False  # False=PII検知OFF（軽量化）、True=PII検知ON
    
    # 🔒 並列処理制限 (SQLite lock回避)
    MAX_PREFETCH_WORKERS: int = 1  # プリフェッチジョブの最大並列数
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
