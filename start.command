#!/bin/bash
# Double-click this file to start the ROPS Attrition & AOV Calculator.
# macOS ships with Python 3 already installed — nothing to download.
# This runs the single-file build in dist/rops-calculator.py.
cd "$(dirname "$0")"
( sleep 2 && open "http://localhost:8766" ) &
echo "Starting ROPS Attrition & AOV Calculator..."
echo "(Leave this window open while you use the tool. Close it when done.)"
echo
python3 dist/rops-calculator.py
