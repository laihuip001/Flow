#!/bin/bash
echo "🔒 Scanning for secrets..."
if grep -rE "sk-ant-[a-zA-Z0-9-*]+|AIza[0-9A-Za-z-*]{35}|sk-[a-zA-Z0-9]{40}" . --exclude-dir=venv --exclude-dir=.git --exclude=.env --exclude="*.pem"; then
    echo "❌ SECURITY ALERT: API Key found!"
    exit 1
fi
echo "✅ No secrets found."
git push origin main
