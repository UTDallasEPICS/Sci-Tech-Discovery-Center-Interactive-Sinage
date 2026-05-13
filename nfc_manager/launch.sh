#!/usr/bin/env bash
# launch.sh - Start the NFC Tag Manager.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"

if pgrep -f "UIDRead_Updated.py" >/dev/null 2>&1; then
    echo "ERROR: The kiosk NFC reader is already running."
    echo "Run ../stop.sh first, then launch the NFC Tag Manager."
    exit 1
fi

if [[ "$(uname -s)" == "Linux" && -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
    echo "ERROR: No desktop display is available."
    echo "Launch this from the Raspberry Pi desktop, not from a headless SSH session."
    exit 1
fi

NEEDS_SETUP=false
if [[ ! -x "$VENV_PYTHON" ]]; then
    NEEDS_SETUP=true
else
    SYS_VERSION="$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "")"
    VENV_VERSION="$("$VENV_PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "")"
    if [[ -z "$VENV_VERSION" || "$SYS_VERSION" != "$VENV_VERSION" ]]; then
        NEEDS_SETUP=true
    fi
fi

if [[ "$NEEDS_SETUP" == true ]]; then
    bash "$SCRIPT_DIR/setup.sh"
    echo ""
fi

if ! "$VENV_PYTHON" -c "import tkinter" 2>/dev/null; then
    echo "ERROR: Tkinter is not available in the NFC manager virtual environment."
    echo "Install it with: sudo apt install python3-tk"
    exit 1
fi

cd "$SCRIPT_DIR"
echo "Starting NFC Tag Manager for $PROJECT_DIR"
exec "$VENV_PYTHON" main.py "$@"
