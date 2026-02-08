#!/bin/sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.tmp_venv"
PYTHON="${PYTHON:-python3}"

cleanup() {
  echo "Removing temporary venv..."
  rm -rf "$VENV_DIR"
}

trap cleanup EXIT INT TERM

echo "Creating virtual environment..."
"$PYTHON" -m venv "$VENV_DIR"

echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip >/dev/null
"$VENV_DIR/bin/pip" install pyqrcode >/dev/null

echo "Running mac_tv_remote.py"
"$VENV_DIR/bin/python" "$SCRIPT_DIR/mac_tv_remote.py"
