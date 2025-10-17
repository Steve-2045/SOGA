@echo off
REM ============================================================================
REM SOGA Dashboard Launcher Script for Windows
REM ============================================================================
REM
REM This script automatically sets up and launches the SOGA dashboard.
REM
REM First run:
REM   - Creates virtual environment (venv)
REM   - Installs all required dependencies
REM   - Launches Streamlit dashboard
REM
REM Subsequent runs:
REM   - Activates existing venv
REM   - Launches Streamlit dashboard
REM
REM Usage:
REM   run_dashboard.bat
REM
REM Requirements:
REM   - Python 3.9 or higher installed and in PATH
REM
REM ============================================================================

setlocal EnableDelayedExpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ========================================================================
echo SOGA Dashboard Launcher
echo ========================================================================
echo Project root: %SCRIPT_DIR%
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo ========================================================================
    echo.
    echo Please install Python 3.9 or higher from:
    echo   https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo ========================================================================
    pause
    exit /b 1
)

REM Display Python version
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Python found: %PYTHON_VERSION%
echo.

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo ========================================================================
    echo Virtual environment not found - Setting up for first time...
    echo ========================================================================
    echo.
    echo [1/3] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo    ^> Virtual environment created successfully
    echo.

    echo [2/3] Installing SOGA package...
    venv\Scripts\python.exe -m pip install --quiet --upgrade pip
    venv\Scripts\python.exe -m pip install --quiet -e .
    if errorlevel 1 (
        echo ERROR: Failed to install SOGA package!
        pause
        exit /b 1
    )
    echo    ^> SOGA package installed successfully
    echo.

    echo [3/3] Installing Streamlit and dashboard dependencies...
    venv\Scripts\python.exe -m pip install --quiet -r streamlit_app\requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies!
        pause
        exit /b 1
    )
    echo    ^> Dependencies installed successfully
    echo.
    echo ========================================================================
    echo Setup complete! Starting dashboard...
    echo ========================================================================
    echo.
) else (
    echo Using existing virtual environment: venv
    echo.
)

REM Set PYTHONPATH to include project root
set "PYTHONPATH=%SCRIPT_DIR%;%PYTHONPATH%"

echo Starting Streamlit dashboard...
echo Dashboard will be available at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ========================================================================
echo.

REM Run Streamlit
venv\Scripts\streamlit.exe run streamlit_app\SOGA_Dashboard.py --server.port=8501 --server.address=localhost

REM If streamlit failed
if errorlevel 1 (
    echo.
    echo ========================================================================
    echo ERROR: Failed to start Streamlit
    echo ========================================================================
    pause
    exit /b 1
)
