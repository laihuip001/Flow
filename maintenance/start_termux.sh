#!/bin/bash
# Flow AI v4.0 - Termux Startup Script
# Usage: ./start_termux.sh

set -e

echo "🚀 Flow AI Termux Launcher"
echo "=========================="

# Navigate to project root
cd "$(dirname "$0")/.."

# Check .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "   Run: cp .env.example .env && vim .env"
    exit 1
fi

# Check GEMINI_API_KEY is set
if ! grep -q "GEMINI_API_KEY=." .env; then
    echo "⚠️ Warning: GEMINI_API_KEY may not be set in .env"
fi

# Install dependencies (first time only)
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements-termux.txt
else
    source venv/bin/activate
fi

echo ""
echo "✅ Environment Ready"
echo "🔗 Starting server on http://0.0.0.0:8000"
echo ""

# Start server
python run_server.py
