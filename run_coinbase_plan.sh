#!/bin/bash
set -euo pipefail

# Run the Coinbase manual trading plan (paper trade) on the scheduled intervals.
cd /home/cechinel/.openclaw/workspace/repos/coinbase-trading-support

DB_PATH="data/trades.db"
OPEN_TRADES=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM trades WHERE status='executed' AND exit_price IS NULL;" 2>/dev/null || echo 0)
if [ "$OPEN_TRADES" -ge 3 ]; then
  echo "🚫 Max open paper trades ($OPEN_TRADES) reached; skipping new plan."
  exit 0
fi

# Pipe a quick "y" to the confirmation prompt so cron can execute without interaction.
printf 'y
' | trading-support plan \
  --product-id BTC-USD \
  --direction buy \
  --size 0.00068 \
  --entry-price 73180 \
  --exit-logic "Target 74,500 with trailing protection once price clears 74,000; stay disciplined with the 30-minute cadence" \
  --reasoning "📈 Buying the ~73,180 area on short-term pullback; the 30-minute cadence keeps the bias bullish while reevaluating every half hour" \
  --order-type limit \
  --note "Auto plan via cron (🧠 max 3 paper trades)" \
  --paper
