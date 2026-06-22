#!/bin/bash
# Shell script wrapper to run the Python E2E Trade Matching Test

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

if ! command -v python3 &>/dev/null; then
    if ! command -v python &>/dev/null; then
        echo "[-] Error: Python is not installed or not in PATH."
        exit 1
    else
        python "$SCRIPT_DIR/run_demo_test.py"
    fi
else
    python3 "$SCRIPT_DIR/run_demo_test.py"
fi
