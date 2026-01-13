import sys
import os
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from dotenv import load_dotenv
    load_dotenv() # Load .env explicitly
    print("✅ Loaded .env file")
except ImportError:
    print("⚠️ dotenv not found")

from src.core.processor import CoreProcessor
from src.core.config import settings
from src.infra.database import get_db, engine
from src.core.models import Base

# Fix Windows Unicode Output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

async def main():
    parser = argparse.ArgumentParser(description="Prefetch Cache Warmup Tool")
    parser.add_argument("--force", action="store_true", help="既存キャッシュを再生成する")
    parser.add_argument("--file", default="docs/prefetch_templates.md", help="テンプレートファイルのパス")
    args = parser.parse_args()

    # Check File
    file_path = Path(args.file)
    if not file_path.exists():
        # Try relative to project root
        file_path = Path(os.getcwd()) / args.file
        if not file_path.exists():
            print(f"❌ Error: File not found: {args.file}")
            sys.exit(1)

    # Parse Templates
    print(f"📖 Reading templates from {file_path}...")
    templates = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if line.startswith("#"): continue
            if line.startswith(">"): continue # Ignore blockquotes
            # Support Markdown list format "- text"
            if line.startswith("- "):
                line = line[2:]
            templates.append(line)
    
    print(f"🔍 Found {len(templates)} templates.")

    # Convert to unique to save API calls
    unique_templates = sorted(list(set(templates)))
    if len(unique_templates) < len(templates):
        print(f"   (Unique: {len(unique_templates)})")

    # Initialize Components
    print("⚙️ Initializing Core components...")
    
    # Ensure Tables Exist
    Base.metadata.create_all(bind=engine)
    
    # CoreProcessor holds instances of Cache, Privacy, Gemini
    processor = CoreProcessor()
    
    # Check API Key
    if not processor.gemini_client.is_configured:
        print("❌ Error: Gemini API Key not configured.")
        print("Please set GEMINI_API_KEY in .env or environment variables.")
        sys.exit(1)

    # Progress Callback
    def progress_callback(current, total, text):
        bar_len = 20
        filled = int(bar_len * current / total)
        bar = "█" * filled + "-" * (bar_len - filled)
        # Clear line to avoid spamming
        print(f"\r[{bar}] {current}/{total} : {text[:30]:<30}", end="", flush=True)

    # Execute Warmup
    print("\n🚀 Starting Warmup... (This may take a while)")
    print("   Press Ctrl+C to abort.")
    
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        stats = await processor.cache_manager.warmup_from_list(
            db=db,
            templates=unique_templates,
            client=processor.gemini_client,
            privacy=processor.privacy_handler,
            callback=progress_callback,
            force=args.force
        )
        print("\n\n✅ Warmup Completed!")
        print(f"   Total:     {stats['total']}")
        print(f"   Processed: {stats['processed']}")
        print(f"   Skipped:   {stats['skipped']}")
        print(f"   Errors:    {stats['errors']}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Aborted by user.")
    except Exception as e:
        with open("warmup_error.txt", "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.utcnow()}] Unexpected Error: {e}\n")
            import traceback
            traceback.print_exc(file=f)
        print(f"\n\n❌ Unexpected Error: {e}")
    finally:
        db.close()
        try:
            db_gen.close()  # H-02 Fix: Properly close generator
        except:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except ImportError:
        # Fallback for some environments
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
