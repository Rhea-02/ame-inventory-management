@echo off
title AMTC Lab Management System - API Test Suite

echo.
echo 🧪 Running API Test Suite for AMTC Lab Management System...
echo.

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

REM Check if the API server is running
echo 🔍 Checking if API server is running...
timeout /t 2 /nobreak >nul

REM Run the API tests
python test_api.py

echo.
echo 📝 Test completed. Check the results above.
echo.
echo 💡 If tests failed, make sure to:
echo    1. Start the API server first (run start-api-server.bat)
echo    2. Wait a few seconds for the server to start
echo    3. Run this test again
echo.
pause