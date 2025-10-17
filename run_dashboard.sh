#!/bin/bash
################################################################################
# SOGA Dashboard Launcher Script
################################################################################
#
# This script launches the SOGA Streamlit dashboard with proper configuration.
#
# Usage:
#   ./run_dashboard.sh
#
# Requirements:
#   - Virtual environment at ./venv with Streamlit installed
#   - Or system-wide Streamlit installation
#
################################################################################

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to project root
cd "$SCRIPT_DIR" || exit 1

echo "========================================================================"
echo "SOGA Dashboard Launcher"
echo "========================================================================"
echo "Project root: $SCRIPT_DIR"

# Check if venv exists and use it, otherwise use system Python
if [ -f "./venv/bin/python" ]; then
    echo "Using virtual environment: ./venv"
    PYTHON_BIN="./venv/bin/python"
    STREAMLIT_BIN="./venv/bin/streamlit"
else
    echo "No venv found, using system Python"
    PYTHON_BIN="python3"
    STREAMLIT_BIN="streamlit"
fi

echo "Python: $PYTHON_BIN"
echo "========================================================================"

# Check if Streamlit is installed
if ! "$PYTHON_BIN" -c "import streamlit" 2>/dev/null; then
    echo ""
    echo "ERROR: Streamlit is not installed!"
    echo "========================================================================"
    echo ""
    echo "Please install the required dependencies:"
    echo "  $PYTHON_BIN -m pip install -r streamlit_app/requirements.txt"
    echo ""
    echo "========================================================================"
    exit 1
fi

# Set PYTHONPATH to include the project root
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

echo ""
echo "Starting Streamlit dashboard..."
echo "Dashboard will be available at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================================================"
echo ""

# Run Streamlit
exec "$STREAMLIT_BIN" run streamlit_app/SOGA_Dashboard.py \
    --server.port=8501 \
    --server.address=localhost
