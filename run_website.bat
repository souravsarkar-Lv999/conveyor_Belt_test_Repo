@echo off
REM Launch the BeltGuard Streamlit website
REM Usage: double-click this file, OR run `run_website.bat` from cmd

cd /d "%~dp0"

echo.
echo ===========================================
echo   BeltGuard Streamlit Website Launcher
echo ===========================================
echo.

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo [setup] streamlit not found — installing dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [error] pip install failed. Please run manually:
        echo     python -m pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo [run] starting streamlit server on http://localhost:8501 ...
echo       press Ctrl+C to stop
echo.

python -m streamlit run streamlit_app.py --server.headless=false

if errorlevel 1 (
    echo.
    echo [error] streamlit failed to start.
    pause
)