@echo off
title AMTC Lab Management System - Basic Version

echo ================================================================
echo         AMTC Lab Management System - Basic Version
echo ================================================================
echo.
echo Starting basic localhost server on port 8000...
echo.
echo Features:
echo - Basic lab inventory management
echo - Email notifications (when configured)
echo - Browser localStorage for data
echo - Simple localhost access
echo.
echo ================================================================

REM Change to the script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo Starting server...
echo.
echo Access your lab system at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

REM Start the basic server
python basic-server.py

pause