#!/bin/bash
# 役割: 自動Pull, 依存関係解消, ヘルスチェック連動型クラッシュループ防止

BRANCH="main"
INTERVAL=60
CRASH_COUNT=0
MAX_RETRIES=5

echo "🛡️ Titanium Watcher Started..."

while true; do
    git fetch origin $BRANCH
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/$BRANCH)

    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "⬇️ Update detected. Initiating strict deployment..."
        if [ -n "$(git status --porcelain)" ]; then
            git stash push -u -m "backup_$(date +%s)"
        fi
        git reset --hard origin/$BRANCH
        
        if git diff --name-only HEAD@{1} HEAD | grep -q "requirements.txt"; then
            pip install -r requirements.txt || echo "⚠️ Dependency install failed!"
        fi
        pkill -f "uvicorn main:app"
    fi

    if ! pgrep -f "uvicorn main:app" > /dev/null || ! curl -sSf http://localhost:8000/healthz > /dev/null; then
        if [ $CRASH_COUNT -ge $MAX_RETRIES ]; then
            echo "🚨 PANIC: Crash loop detected. Stopping."
            exit 1
        fi
        echo "♻️ Starting Application (Attempt: $((CRASH_COUNT+1)))..."
        if [ -f app.log ] && [ $(wc -c < app.log) -gt 10000000 ]; then 
            mv app.log app.log.old
        fi
        nohup uvicorn main:app --host 0.0.0.0 --port 8000 >> app.log 2>&1 &
        sleep 10
        if ! curl -sSf http://localhost:8000/healthz > /dev/null; then
            CRASH_COUNT=$((CRASH_COUNT+1))
        else
            CRASH_COUNT=0
        fi
    fi
    sleep $INTERVAL
done
