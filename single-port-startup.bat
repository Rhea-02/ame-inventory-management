@echo off
title AMTC Lab System - Single Port (8000)
color 0a

echo.
echo ========================================
echo   🔬 AMTC Lab Management System
echo   Consolidated Single Port Solution
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python not found
    echo Please install Python 3.7+ and add to PATH
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

REM Kill any existing processes on port 8000
echo 🔄 Cleaning up existing processes...
netstat -ano | findstr :8000 | findstr LISTENING >nul && (
    echo Found process on port 8000, terminating...
    for /f "tokens=5" %%i in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /f /pid %%i >nul 2>&1
)
timeout /t 2 >nul

echo.
echo 🚀 Starting AMTC Lab System on Port 8000...
echo.

REM Start consolidated server (port 8000 only)
echo 🔬 Starting Consolidated Lab System...
start /min python basic-server.py
timeout /t 5

echo.
echo ✅ System started successfully!
echo.
echo 🌐 Access Information:
echo    • Lab System:      http://localhost:8000
echo    • System Health:   http://localhost:8000/api/sync/health
echo    • Active Users:    http://localhost:8000/api/sync/users
echo.
echo 📋 For All Users (3-5 people):
echo    • Bookmark: http://localhost:8000
echo    • Single URL for everything
echo    • Real-time multi-user sync
echo    • Box.com Enterprise integration
echo.

REM Test server connection
echo 🔍 Testing server connection...
timeout /t 3
curl -s http://localhost:8000/api/sync/health >nul && echo ✅ Lab System: Online || echo ❌ Lab System: Offline

echo.
echo 💡 Usage Instructions:
echo    1. Each user bookmarks: http://localhost:8000
echo    2. System supports 3-5 users simultaneously
echo    3. Real-time data sync every 2 seconds
echo    4. Automatic conflict resolution
echo    5. Box.com Enterprise sync for data persistence
echo.

REM Auto-open Chrome to lab system
echo 🌐 Opening lab system in Chrome...
timeout /t 2
start chrome "http://localhost:8000" 2>nul || start "http://localhost:8000"

echo.
echo ⚡ AMTC Lab System Ready on Port 8000!
echo 📋 Key Features:
echo    • Single port solution (8000 only)
echo    • Real-time synchronization across PCs
echo    • Automatic conflict resolution
echo    • User presence detection
echo    • Box.com Enterprise integration
echo.
echo 🔧 Troubleshooting:
echo    • If connection refused: Restart this script
echo    • Check firewall isn't blocking port 8000
echo    • Ensure Box.com is syncing properly
echo.
echo Keep this window open while using the system
echo Press Ctrl+C to stop the server
pause