import os
import zipfile
from datetime import datetime

# 1. Zip Archiving
zip_filename = f"ai_clipboard_pro_v2.6_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
files_to_zip = [
    "main.py", "logic.py", "models.py", "database.py", "config.py", "setup_project.py",
    "requirements.txt", "Procfile", "runtime.txt", ".env.example",
    "CHANGELOG.md", "DEPLOYMENT.md", "DEVELOPMENT_MEMO.md", 
    "KNOWN_ISSUES_AND_ROADMAP.md", "V3_DESIGN.md", "COMPLETE_ARCHIVE.md",
    "ANDROID_SETUP.md", "COLAB_SETUP.md", "TERMUX_SETUP.md", "HYBRID_SETUP.md", 
    "README.md", "USAGE.md"
]

print(f"📦 Creating backup: {zip_filename}...")
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file in files_to_zip:
        if os.path.exists(file):
            zipf.write(file)
            print(f"  + {file}")
        else:
            print(f"  ⚠️ Missing: {file}")

# 2. Context Handover Prompt
handover_content = """# 🤖 AI Clipboard Pro: Context Handover Protocol

**For the Next AI Session:**
Please create a prompt based on the following context information to resume development seamlessly.

---

## 📍 Project Status: v2.6 (Safety Update)
- **Current Phase:** Implementation / Verification
- **Last Action:** Implemented v2.6 Safety features (PrivacyScanner, /scan, /process/multi)
- **Next Goal:** Verification of v2.6 & Planning v2.7 (Stability & Offlining)

## 🔑 Key Files & Architecture
- `main.py`: FastAPI server (Points: /scan, /process/multi, /ballast)
- `logic.py`: Core logic (Points: PrivacyScanner - NO auto-masking, ContextBallast)
- `models.py`: Data models (Points: ScanRequest, MultiChoiceRequest)
- `COMPLETE_ARCHIVE.md`: **Crucial** - Contains the full brainstorming history & roadmap.

## 🚧 Roadblocks & Decisions
- **Safety:** Auto-masking/unmasking was deprecating because of "Detokenization Fallacy". We now only DETECT and WARN.
- **UX:** Moved from "Teaching AI" to "Choosing from 3 options" (Formal/Casual/Summary).
- **Architecture:** Moving away from macro-droid dependency towards robust cloud/local split.

## 📝 Immediate Next Steps
1. Verify `/process/multi` with actual HTTP Shortcuts.
2. Plan v2.7 (Offline fallbacks).
3. Review `KNOWN_ISSUES_AND_ROADMAP.md` for Phasing.

---
**User Persona:**
The developer is working from a net cafe or unstable environment.
Prioritize: **Data Portability**, **Clear Documentation**, and **Robustness**.
"""

with open("CONTEXT_HANDOVER.md", "w", encoding="utf-8") as f:
    f.write(handover_content)

print("✅ Handover files created.")
