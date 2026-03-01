#!/bin/bash
# NBCOC - NVIDIA Build to OpenClaw Connector
# One-command startup script

echo "🚀 Starting NBCOC..."

# Kill old proxy if running
kill $(lsof -ti:8000) 2>/dev/null
sleep 1

# Start NBCOC proxy with nohup (fully detached, survives Ctrl+C)
cd ~/NBCOC
source venv/bin/activate
nohup python3 main.py > /tmp/nbcoc.log 2>&1 &
PROXY_PID=$!
disown $PROXY_PID
sleep 2

# Check if proxy started
if curl -s http://localhost:8000/v1/models -H "Authorization: Bearer sk-dummy" > /dev/null 2>&1; then
    echo "✅ NBCOC proxy is running on http://localhost:8000 (PID: $PROXY_PID)"
else
    echo "❌ NBCOC proxy failed to start. Check /tmp/nbcoc.log"
    cat /tmp/nbcoc.log
    exit 1
fi

# Restart OpenClaw gateway
echo "🔄 Restarting OpenClaw gateway..."
openclaw gateway restart
sleep 2

# Open TUI
echo "🦞 Opening OpenClaw TUI..."
openclaw tui
