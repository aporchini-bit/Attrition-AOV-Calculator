#!/bin/bash
# Double-click this file to start the ROPS Attrition & AOV Calculator.
# macOS ships with Python 3 already installed — nothing to download.
# This runs the single-file build in dist/rops-calculator.py on port 8766.
cd "$(dirname "$0")"

# Stop any old instance still holding port 8766 so you always get the latest version.
OLD_PIDS=$(lsof -ti tcp:8766 2>/dev/null)
if [ -n "$OLD_PIDS" ]; then
  echo "Stopping an earlier calculator still running on port 8766…"
  echo "$OLD_PIDS" | xargs kill 2>/dev/null
  sleep 1
fi

( sleep 2 && open "http://localhost:8766" ) &
echo "Starting ROPS Attrition & AOV Calculator…"
echo "(Leave this window open while you use the tool. Close it when done.)"
echo
python3 dist/rops-calculator.py
