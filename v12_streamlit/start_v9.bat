@echo off
echo ==============================
echo  UDX V9 Streamlit Dashboard
echo ==============================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.11+ and try again.
    pause
    exit /b 1
)

REM Check .env
if not exist ".env" (
    echo WARNING: .env file not found. Copying from .env.example...
    copy .env.example .env
    echo.
    echo >> IMPORTANT: Open .env and paste your McKinsey JWT token before using AI features.
    echo.
)

REM Install requirements if needed
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo Starting Streamlit...
echo Dashboard will open at http://localhost:8501
echo.
streamlit run app.py --server.port 8501
pause
