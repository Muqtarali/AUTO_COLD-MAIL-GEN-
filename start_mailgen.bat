@echo off
REM MailGen Quick Start Script for Windows
REM This script helps you set up and run MailGen locally

echo.
echo ==========================================
echo   MailGen - HireSense HR Tech
echo   Quick Start Setup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Flutter is installed
flutter --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Flutter is not installed or not in PATH
    echo Please install Flutter from https://flutter.dev/docs/get-started/install/windows
    echo.
    echo Continuing with backend setup only...
    echo.
)

echo Step 1: Setting up Python Backend
echo ==================================
echo.

REM Create backend virtual environment
echo Creating Python virtual environment...
cd backend
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Backend setup complete!
echo.
echo Step 2: Flutter Frontend Setup (Optional)
echo ===========================================
echo.
echo To set up Flutter, run these commands in a new terminal:
echo   cd mailgen_frontend
echo   flutter pub get
echo   flutter run
echo.

echo Step 3: Starting the Backend
echo =============================
echo.
echo Choose an option:
echo   1. Start FastAPI (Port 8000)
echo   2. Start Flask (Port 5000)
echo   3. Exit
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Starting FastAPI server on http://localhost:8000
    echo Press Ctrl+C to stop
    echo.
    python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
) else if "%choice%"=="2" (
    echo.
    echo Starting Flask server on http://localhost:5000
    echo Press Ctrl+C to stop
    echo.
    python flask_app.py
) else (
    echo Exiting setup...
    pause
    exit /b 0
)

echo.
echo Backend is running! Open another terminal to start Flutter.
echo.
pause
