#!/bin/bash
set -euo pipefail

# Launch Nova WebUI without spawning duplicate node instances.
cd /home/cechinel/.openclaw/workspace/webui-nova

# Kill any existing server bound to the same script so we can restart cleanly.
if pgrep -f "node server.mjs" >/dev/null; then
  pkill -f "node server.mjs"
  sleep 1
fi

# Start the UI and keep a log; store the PID for reference.
nohup npm start > webui.log 2>&1 &
echo "$!" > webui.pid
