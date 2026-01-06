import uvicorn
import os
import sys

# Ensure root directory is in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)

if __name__ == "__main__":
    print("🚀 Starting AI-Clipboard-Pro API Server...")
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
