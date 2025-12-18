#!/bin/bash
# MailGen Quick Start Script for macOS/Linux
# This script helps you set up and run MailGen locally

echo ""
echo "=========================================="
echo "   MailGen - HireSense HR Tech"
echo "   Quick Start Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python from https://www.python.org/"
    exit 1
fi

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "WARNING: Flutter is not installed or not in PATH"
    echo "Please install Flutter from https://flutter.dev/docs/get-started/install"
    echo ""
    echo "Continuing with backend setup only..."
    echo ""
fi

echo "Step 1: Setting up Python Backend"
echo "=================================="
echo ""

# Navigate to backend directory
cd backend || exit 1

# Create backend virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Backend setup complete!"
echo ""
echo "Step 2: Flutter Frontend Setup (Optional)"
echo "=========================================="
echo ""
echo "To set up Flutter, run these commands in a new terminal:"
echo "   cd mailgen_frontend"
echo "   flutter pub get"
echo "   flutter run"
echo ""

echo "Step 3: Starting the Backend"
echo "============================"
echo ""
echo "Choose an option:"
echo "   1. Start FastAPI (Port 8000)"
echo "   2. Start Flask (Port 5000)"
echo "   3. Exit"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Starting FastAPI server on http://localhost:8000"
        echo "Press Ctrl+C to stop"
        echo ""
        python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
        ;;
    2)
        echo ""
        echo "Starting Flask server on http://localhost:5000"
        echo "Press Ctrl+C to stop"
        echo ""
        python flask_app.py
        ;;
    *)
        echo "Exiting setup..."
        exit 0
        ;;
esac

echo ""
echo "Backend is running! Open another terminal to start Flutter."
echo ""
