@echo off
title AMTC Lab Management System - System Status

echo.
echo 🔬 AMTC Lab Management System - System Status
echo ============================================
echo.

REM Check current directory
echo 📂 Current Directory: %CD%
echo.

echo 📁 Available Scripts and Files:
echo --------------------------------

REM Check for key files
if exist "index.html" (
    echo ✅ index.html - Main web application
) else (
    echo ❌ index.html - MISSING
)

if exist "api_server.py" (
    echo ✅ api_server.py - Enhanced API server
) else (
    echo ❌ api_server.py - MISSING
)

if exist "automated_email_system.py" (
    echo ✅ automated_email_system.py - Automated email notifications
) else (
    echo ❌ automated_email_system.py - MISSING
)

if exist "email_config.json" (
    echo ✅ email_config.json - Email configuration
) else (
    echo ❌ email_config.json - MISSING
)

echo.
echo 🚀 Startup Scripts:
echo ------------------
if exist "start-server.bat" echo ✅ start-server.bat - Basic web server
if exist "start-api-server.bat" echo ✅ start-api-server.bat - Enhanced API server
if exist "setup-automated-emails.bat" echo ✅ setup-automated-emails.bat - Complete automation setup

echo.
echo 🧪 Test Scripts:
echo ---------------
if exist "test-api.bat" echo ✅ test-api.bat - Test API endpoints
if exist "test-notifications.bat" echo ✅ test-notifications.bat - Test email system
if exist "run-manual-notifications.bat" echo ✅ run-manual-notifications.bat - Manual email sending

echo.
echo 📊 Windows Task Scheduler Status:
echo --------------------------------

REM Check if scheduled tasks exist
schtasks /query /tn "AMTC Lab Email Notifications" >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ AMTC Lab Email Notifications - CONFIGURED
    schtasks /query /tn "AMTC Lab Email Notifications" /fo list | findstr "Next Run Time"
) else (
    echo ❌ AMTC Lab Email Notifications - NOT CONFIGURED
)

schtasks /query /tn "AMTC Lab API Server" >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ AMTC Lab API Server - CONFIGURED
) else (
    echo ❌ AMTC Lab API Server - NOT CONFIGURED
)

echo.
echo 🌐 API Server Status:
echo --------------------

REM Try to ping the API server
python -c "import urllib.request; urllib.request.urlopen('http://localhost:8084/api/health', timeout=3)" 2>nul
if %errorLevel% == 0 (
    echo ✅ API Server is RUNNING on http://localhost:8084
    echo   🔗 Web App: http://localhost:8084
    echo   📡 API Base: http://localhost:8084/api/
) else (
    echo ❌ API Server is NOT RUNNING
    echo   💡 Run: start-api-server.bat
)

echo.
echo 📧 Quick Actions:
echo ================
echo.
echo 1. 🌟 START EVERYTHING:
echo    run setup-automated-emails.bat (as Administrator)
echo.
echo 2. 🌐 START WEB APP:
echo    run start-api-server.bat
echo.
echo 3. 🧪 TEST SYSTEM:
echo    run test-api.bat
echo    run test-notifications.bat
echo.
echo 4. 📧 SEND EMAILS NOW:
echo    run run-manual-notifications.bat
echo.
echo 5. 📖 READ DOCUMENTATION:
echo    open AUTOMATION_GUIDE.md
echo.

echo ⭐ Your AMTC Lab Management System Features:
echo ==========================================
echo ✅ Web-based inventory management
echo ✅ Real-time API endpoints for data access
echo ✅ Fully automated email notifications
echo ✅ Smart scheduling (2 days before, on due date, daily after)
echo ✅ Windows Task Scheduler integration
echo ✅ Comprehensive logging and monitoring
echo ✅ Multiple data source fallbacks
echo ✅ Zero manual intervention required
echo.

pause