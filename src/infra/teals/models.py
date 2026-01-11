"""
TEALS - データモデル定義
監査ログテーブルのSQLAlchemy ORM定義
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class AuditLog(Base):
    """監査ログテーブル（ハッシュチェーン形式）"""
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    user_id = Column(String(100), nullable=False)
    action_type = Column(String(10), nullable=False)
    target_table = Column(String(100), nullable=False)
    ai_model = Column(String(50), nullable=True)
    before_data = Column(Text, nullable=True)
    after_data = Column(Text, nullable=True)
    previous_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), nullable=False)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action_type})>"


def init_db(db_path: str = "audit_log.db"):
    """DB初期化"""
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session
