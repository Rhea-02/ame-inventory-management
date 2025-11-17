@echo off
echo.
echo 🔬 Starting AMTC Lab Management System with Enhanced API...
echo.

REM Set the window title
title AMTC Lab Management System - API Server

REM Change to the script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Start the enhanced API server
echo 📡 Starting enhanced server with API endpoints...
echo 🌐 Web App will be available at: http://localhost:8084
echo 📊 API endpoints will be available at: http://localhost:8084/api/
echo.
echo 🛑 Press Ctrl+C to stop the server
echo.

python api_server.py

echo.
echo 👋 Server stopped
pause