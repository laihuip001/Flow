"""
ingest_obsidian.py
P2: プロンプトライブラリからコンポーネントを抽出してDBに格納するETLスクリプト
"""
import os
import re
import logging
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, PromptComponent
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# テーブル行をパースする正規表現
# Format: | [[Link]] | #Tag | **Component** (Mechanism) | Trigger | Synergy |
TABLE_ROW_PATTERN = re.compile(
    r'\|\s*\[\[([^\]]+)\]\]\s*\|'  # Link
    r'\s*(#[^\|]+)\s*\|'           # Tag
    r'\s*\*\*([^*]+)\*\*\s*\(([^)]+)\)\s*\|'  # Component (Mechanism)
    r'\s*([^\|]+)\s*\|'            # Trigger
    r'\s*([^\|]+)\s*\|',           # Synergy
    re.MULTILINE
)


def parse_markdown_file(file_path: Path) -> list[dict]:
    """MarkdownファイルからPromptComponent表をパース"""
    components = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # カテゴリのヘッダーを検出
        current_category = "Unknown"
        category_pattern = re.compile(r'^## .+ \(([\w・]+)\)', re.MULTILINE)
        
        # ファイル内の各テーブル行をパース
        for match in TABLE_ROW_PATTERN.finditer(content):
            link, tag, comp_name, mechanism, trigger, synergy = match.groups()
            
            # Tagからカテゴリを推測
            if "Structure" in tag or "Framework" in tag:
                current_category = "Framework"
            elif "Reasoning" in tag:
                current_category = "Reasoning"
            elif "Safety" in tag:
                current_category = "Safety"
            
            components.append({
                "name": comp_name.strip(),
                "category": current_category,
                "mechanism": mechanism.strip(),
                "trigger_condition": trigger.strip(),
                "synergy": synergy.strip(),
                "source_file": str(file_path.name)
            })
    except Exception as e:
        logger.error(f"Failed to parse {file_path}: {e}")
    
    return components


def run_ingestion(db: Session = None) -> int:
    """メイン取り込み処理"""
    prompt_lib_dir = settings.PROMPT_LIB_DIR
    
    if not prompt_lib_dir or not os.path.isdir(prompt_lib_dir):
        logger.warning(f"PROMPT_LIB_DIR is not configured or invalid: {prompt_lib_dir}")
        return 0
    
    if db is None:
        db = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        Base.metadata.create_all(bind=engine)
        
        all_components = []
        lib_path = Path(prompt_lib_dir)
        
        for md_file in lib_path.rglob("*.md"):
            logger.info(f"Parsing: {md_file.name}")
            components = parse_markdown_file(md_file)
            all_components.extend(components)
        
        # Upsert logic
        ingested_count = 0
        for comp_data in all_components:
            existing = db.query(PromptComponent).filter_by(name=comp_data["name"]).first()
            if existing:
                for key, value in comp_data.items():
                    setattr(existing, key, value)
                existing.last_updated = datetime.utcnow()
            else:
                new_comp = PromptComponent(**comp_data)
                db.add(new_comp)
                ingested_count += 1
        
        db.commit()
        logger.info(f"Ingested {ingested_count} new components. Total parsed: {len(all_components)}")
        return ingested_count
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        db.rollback()
        return 0
    finally:
        if should_close:
            db.close()


if __name__ == "__main__":
    count = run_ingestion()
    print(f"Ingestion complete. New components: {count}")
