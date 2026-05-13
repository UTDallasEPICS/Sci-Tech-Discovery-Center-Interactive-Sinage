#!/usr/bin/env bash
# setup.sh - One-time (or repair) environment setup for NFC Tag Manager.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
REQUIREMENTS="$SCRIPT_DIR/requirements.txt"

echo "=== NFC Tag Manager - Setup ==="
echo "Manager: $SCRIPT_DIR"
echo ""

PYTHON="$(command -v python3 || true)"
if [[ -z "$PYTHON" ]]; then
    echo "ERROR: python3 not found. Install it with: sudo apt install python3"
    exit 1
fi

PYTHON_VERSION="$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")"
echo "Python:  $("$PYTHON" --version) ($PYTHON)"
echo "Version: $PYTHON_VERSION"
echo ""

if ! "$PYTHON" -c "import venv" 2>/dev/null; then
    echo "Installing python3-venv..."
    sudo apt-get update
    sudo apt-get install -y python3-venv
fi

if ! "$PYTHON" -c "import tkinter" 2>/dev/null; then
    echo "Installing python3-tk..."
    sudo apt-get update
    sudo apt-get install -y python3-tk
fi

if [[ -d "$VENV_DIR" ]]; then
    VENV_PYTHON="$VENV_DIR/bin/python"
    VENV_OK=false

    if [[ -x "$VENV_PYTHON" ]]; then
        VENV_VERSION="$("$VENV_PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "unknown")"
        if [[ "$VENV_VERSION" == "$PYTHON_VERSION" ]]; then
            VENV_OK=true
        else
            echo "Existing venv uses Python $VENV_VERSION, but system has $PYTHON_VERSION - rebuilding."
        fi
    else
        echo "Existing venv has no usable python binary - rebuilding."
    fi

    if [[ "$VENV_OK" == false ]]; then
        rm -rf "$VENV_DIR"
    fi
fi

if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

echo ""
echo "Installing Python dependencies..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip --quiet
IS_RASPBERRY_PI=false
if [[ -r "/proc/device-tree/model" ]] && grep -qi "raspberry pi" "/proc/device-tree/model"; then
    IS_RASPBERRY_PI=true
fi

if [[ "$IS_RASPBERRY_PI" == true ]]; then
    "$VENV_DIR/bin/python" -m pip install -r "$REQUIREMENTS"
else
    "$VENV_DIR/bin/python" -m pip install customtkinter Pillow darkdetect
    if ! "$VENV_DIR/bin/python" -m pip install spidev rpi-lgpio; then
        echo "Skipping Pi-only NFC packages on this platform; mock reader mode will still work."
    fi
fi

echo ""
echo "=== Setup complete ==="
echo "Launch with: ./launch.sh"
