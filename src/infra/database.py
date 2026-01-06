from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.core.config import settings
from src.core.models import Base

engine = create_engine(
    settings.DATABASE_URL.replace("sqlite:///./tasks.db", "sqlite:///./data/tasks.db"), 
    connect_args={
        "check_same_thread": False,
        "timeout": 30,  # 30秒待機
    },
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    # WALモード有効化（並列アクセス改善）
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL"))
        conn.commit()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

