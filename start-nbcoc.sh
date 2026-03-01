#!/bin/bash
# NBCOC - NVIDIA Build to OpenClaw Connector
# One-command startup script

echo "🚀 Starting NBCOC..."

# Kill old proxy if running
kill $(lsof -ti:8000) 2>/dev/null
sleep 1

# Start NBCOC proxy in background
cd ~/NBCOC && source venv/bin/activate && python3 main.py &
sleep 2

# Check if proxy started
if curl -s http://localhost:8000/v1/models -H "Authorization: Bearer sk-dummy" > /dev/null 2>&1; then
    echo "✅ NBCOC proxy is running on http://localhost:8000"
else
    echo "❌ NBCOC proxy failed to start. Check config.yaml"
    exit 1
fi

# Restart OpenClaw gateway
echo "🔄 Restarting OpenClaw gateway..."
openclaw gateway restart

# Open TUI
echo "🦞 Opening OpenClaw TUI..."
openclaw tui
