#!/usr/bin/env python3
"""
SOGA Dashboard Launcher
=======================

Convenience script to launch the Streamlit dashboard with proper path configuration.

Usage:
    python run_dashboard.py

    Or make it executable and run directly:
    chmod +x run_dashboard.py
    ./run_dashboard.py

    Or use the venv directly:
    ./venv/bin/python run_dashboard.py
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

# Print startup information
print("=" * 70)
print("SOGA Dashboard Launcher")
print("=" * 70)
print(f"Project root: {project_root}")
print(f"Python version: {sys.version}")
print(f"Python path configured: {project_root}")
print("=" * 70)
print("\nStarting Streamlit dashboard...")
print("Dashboard will be available at: http://localhost:8501")
print("=" * 70)

# Run Streamlit
try:
    import streamlit.web.cli as stcli

    if __name__ == "__main__":
        sys.argv = [
            "streamlit",
            "run",
            str(project_root / "streamlit_app" / "SOGA_Dashboard.py"),
            "--server.port=8501",
            "--server.address=localhost",
        ]
        sys.exit(stcli.main())

except ImportError:
    print("\n" + "=" * 70)
    print("ERROR: Streamlit is not installed!")
    print("=" * 70)
    print("\nPlease install the required dependencies:")
    print(f"  {sys.executable} -m pip install -r streamlit_app/requirements.txt")
    print("\nOr if using the venv:")
    print("  ./venv/bin/pip install -r streamlit_app/requirements.txt")
    print("=" * 70)
    sys.exit(1)
