import os
import zipfile
from datetime import datetime

# Files to bundle in the installer
TARGET_FILES = [
    "config.py", "models.py", "database.py", "logic.py", "main.py", 
    "requirements.txt", ".env.example", "Procfile", "runtime.txt",
    "CHANGELOG.md", "COMPLETE_ARCHIVE.md", "README.md"
]

INSTALLER_NAME = "ai_clipboard_v2.6_installer.py"

def create_installer():
    print(f"🔨 Generating {INSTALLER_NAME}...")
    with open(INSTALLER_NAME, "w", encoding="utf-8") as out:
        out.write("#!/usr/bin/env python3\n")
        out.write("# AI Clipboard Pro v2.6 Self-Extracting Installer\n")
        out.write("import os\n\n")
        out.write("print('🚀 Installing AI Clipboard Pro v2.6...')\n\n")
        
        for filename in TARGET_FILES:
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Escape triple quotes
                    content = content.replace("'''", "\\'\\'\\'")
                    # Write writing logic
                    out.write(f"# --- {filename} ---\n")
                    out.write(f"print('📝 Creating {filename}...')\n")
                    out.write(f"with open('{filename}', 'w', encoding='utf-8') as f:\n")
                    out.write(f"    f.write(r'''{content}''')\n\n")
            else:
                print(f"⚠️ Warning: {filename} not found.")
        
        out.write("print('✅ Installation Complete!')\n")
    print(f"✅ Installer created: {INSTALLER_NAME}")

def create_zip():
    zip_name = f"ai_clipboard_v2.6_backup.zip"
    print(f"📦 Zipping to {zip_name}...")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add the installer
        if os.path.exists(INSTALLER_NAME):
            zipf.write(INSTALLER_NAME)
        
        # Add all other key files
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith((".py", ".md", ".txt", ".example")):
                    zipf.write(os.path.join(root, file), file)
    print(f"✅ Zip created: {zip_name}")

if __name__ == "__main__":
    create_installer()
    create_zip()
