#!/bin/bash
################################################################################
# SOGA Dashboard Launcher Script for Linux/Mac
################################################################################
#
# This script automatically sets up and launches the SOGA dashboard.
#
# First run:
#   - Creates virtual environment (venv)
#   - Installs all required dependencies
#   - Launches Streamlit dashboard
#
# Subsequent runs:
#   - Activates existing venv
#   - Launches Streamlit dashboard
#
# Usage:
#   ./run_dashboard.sh
#
# Requirements:
#   - Python 3.9 or higher installed
#
################################################################################

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to project root
cd "$SCRIPT_DIR" || exit 1

echo "========================================================================"
echo "SOGA Dashboard Launcher"
echo "========================================================================"
echo "Project root: $SCRIPT_DIR"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "========================================================================"
    echo ""
    echo "Please install Python 3.9 or higher:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "  Fedora/RHEL:   sudo dnf install python3 python3-pip"
    echo "  macOS:         brew install python3"
    echo ""
    echo "========================================================================"
    exit 1
fi

# Display Python version
PYTHON_VERSION=$(python3 --version)
echo "Python found: $PYTHON_VERSION"
echo ""

# Function to setup/reinstall venv
setup_venv() {
    echo "========================================================================"
    echo "Setting up virtual environment..."
    echo "========================================================================"
    echo ""

    # Remove existing venv if it exists
    if [ -d "./venv" ]; then
        echo "Removing existing virtual environment..."
        rm -rf ./venv
        echo ""
    fi

    echo "[1/3] Creating virtual environment..."
    python3 -m venv venv
    echo "   > Virtual environment created successfully"
    echo ""

    echo "[2/3] Installing SOGA package..."
    ./venv/bin/python -m pip install --quiet --upgrade pip
    ./venv/bin/python -m pip install --quiet -e .
    echo "   > SOGA package installed successfully"
    echo ""

    echo "[3/3] Installing Streamlit and dashboard dependencies..."
    ./venv/bin/python -m pip install --quiet -r streamlit_app/requirements.txt
    echo "   > Dependencies installed successfully"
    echo ""
    echo "========================================================================"
    echo "Setup complete! Starting dashboard..."
    echo "========================================================================"
    echo ""
}

# Check if venv exists and is valid
if [ ! -f "./venv/bin/python" ]; then
    # No venv found
    setup_venv
else
    # Venv exists, check if it's valid
    if ! ./venv/bin/python -m pip --version &> /dev/null; then
        # Venv is corrupted (pip doesn't work)
        echo "Virtual environment is corrupted - recreating..."
        echo ""
        setup_venv
    elif [ ! -f "./venv/bin/streamlit" ]; then
        # Venv is valid but missing Streamlit
        echo "Using existing virtual environment: ./venv"
        echo ""
        echo "========================================================================"
        echo "Dependencies missing - Installing now..."
        echo "========================================================================"
        echo ""
        echo "[1/2] Installing SOGA package..."
        ./venv/bin/python -m pip install --quiet --upgrade pip
        ./venv/bin/python -m pip install --quiet -e .
        echo "   > SOGA package installed successfully"
        echo ""

        echo "[2/2] Installing Streamlit and dashboard dependencies..."
        ./venv/bin/python -m pip install --quiet -r streamlit_app/requirements.txt
        echo "   > Dependencies installed successfully"
        echo ""
        echo "========================================================================"
        echo "Setup complete! Starting dashboard..."
        echo "========================================================================"
        echo ""
    else
        # Everything looks good
        echo "Using existing virtual environment: ./venv"
        echo ""
    fi
fi

# Set PYTHONPATH to include the project root
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

echo "Starting Streamlit dashboard..."
echo "Dashboard will be available at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================================================"
echo ""

# Run Streamlit
exec ./venv/bin/streamlit run streamlit_app/SOGA_Dashboard.py \
    --server.port=8501 \
    --server.address=localhost
