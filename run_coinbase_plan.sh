#!/bin/bash
set -euo pipefail

# Run the Coinbase manual trading plan (paper trade) on the scheduled intervals.
cd /home/cechinel/.openclaw/workspace/repos/coinbase-trading-support

# Pipe a quick "y" to the confirmation prompt so cron can execute without interaction.
printf 'y
' | trading-support plan \
  --product-id BTC-USD \
  --direction buy \
  --size 0.00068 \
  --entry-price 73180 \
  --exit-logic "Target 74,500 with trailing protection once price clears 74,000; keep exposures limited to the hourly cadence" \
  --reasoning "Buying the ~73,180 area on hourly support; this hourly cadence keeps the bias bullish while reassessing every hour" \
  --order-type limit \
  --note "Auto plan via cron" \
  --paper
