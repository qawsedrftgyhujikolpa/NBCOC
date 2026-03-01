#!/bin/bash
# NBCOC - NVIDIA Build to OpenClaw Connector
# One-command startup script

# Define model mappings
declare -A MODEL_MAPPING
MODEL_MAPPING["kimi"]="nbcoc/moonshotai/kimi-k2.5"
MODEL_MAPPING["llama"]="nbcoc/meta/llama-3.3-70b-instruct"
MODEL_MAPPING["qwen"]="nbcoc/qwen/qwen3-235b-a22b"
MODEL_MAPPING["qwen-coder"]="nbcoc/qwen/qwen3-coder-480b-a35b-instruct"
MODEL_MAPPING["mistral"]="nbcoc/mistralai/mistral-large-3-675b-instruct-2512"
MODEL_MAPPING["deepseek"]="nbcoc/deepseek-ai/deepseek-r1-distill-qwen-32b"
MODEL_MAPPING["codestral"]="nbcoc/mistralai/codestral-22b-instruct-v0.1"
MODEL_MAPPING["nemotron"]="nbcoc/nvidia/llama-3.1-nemotron-70b-instruct"
MODEL_MAPPING["swallow"]="nbcoc/tokyotech-llm/llama-3-swallow-70b-instruct-v0.1"

# --- Model Selection Logic ---
MODEL_TO_USE=""
# 1. Command-line argument (highest priority)
if [ -n "$1" ]; then
    if [[ -v "MODEL_MAPPING[$1]" ]]; then
        MODEL_TO_USE="${MODEL_MAPPING[$1]}"
        echo "Selected model from command-line shortcut: $1 -> $MODEL_TO_USE"
    else
        MODEL_TO_USE="$1"
        echo "Selected model from command-line argument: $MODEL_TO_USE"
    fi
# 2. model.json (second priority)
elif [ -f "$HOME/NBCOC/model.json" ]; then
    MODEL_FROM_FILE=$(python3 -c 'import json, os; print(json.load(open(os.path.expanduser("~/NBCOC/model.json")))["model"])' 2>/dev/null)
    if [ -n "$MODEL_FROM_FILE" ]; then
        MODEL_TO_USE="$MODEL_FROM_FILE"
        echo "Selected model from model.json: $MODEL_TO_USE"
    fi
fi

# 3. Default model (lowest priority)
if [ -z "$MODEL_TO_USE" ]; then
    MODEL_TO_USE="nbcoc/moonshotai/kimi-k2.5"
    echo "Using default model: $MODEL_TO_USE"
fi

# --- Update OpenClaw Config ---
OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"
if [ -f "$OPENCLAW_CONFIG" ]; then
    echo "Updating primary model in $OPENCLAW_CONFIG..."
    python3 -c "
import json, os
config_path = os.path.expanduser('$OPENCLAW_CONFIG')
model_id = '$MODEL_TO_USE'
try:
    with open(config_path, 'r+') as f:
        config = json.load(f)
        config['agents']['defaults']['model']['primary'] = model_id
        f.seek(0)
        json.dump(config, f, indent=2)
        f.truncate()
    print(f'Successfully updated primary model to: {model_id}')
except Exception as e:
    print(f'Error updating $OPENCLAW_CONFIG: {e}')
"
else
    echo "Warning: $OPENCLAW_CONFIG not found. Skipping update."
fi

# --- Start NBCOC Proxy ---
echo "🚀 Starting NBCOC..."

# Kill old proxy if running
kill $(lsof -ti:8000) 2>/dev/null
sleep 1

# Change to the script's directory to ensure correct paths
cd "$HOME/NBCOC"

# Start NBCOC proxy with nohup
source venv/bin/activate
nohup python3 main.py > /tmp/nbcoc.log 2>&1 &
PROXY_PID=$!
disown $PROXY_PID
sleep 2

# Check if proxy started
if curl -s http://localhost:8000/v1/models -H "Authorization: Bearer sk-dummy" > /dev/null; then
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
