#!/bin/bash
if [ "$1" == "start" ]; then
    echo "🌅 Starting Session..."
    git pull origin main
elif [ "$1" == "end" ]; then
    echo "🌇 Ending Session..."
    python -m compileall . -q && git add . && git commit -m "wip: autosave $(date +%s)" && ./dev_tools/secure_push.sh
else
    echo "Usage: ./dev_tools/sync.sh [start|end]"
fi
