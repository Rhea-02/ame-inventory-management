@echo off
echo ========================================
echo    AMTC Lab Management System 
echo    Basic Version - Localhost Only
echo ========================================
echo.
echo 🔬 Starting basic lab management server...
echo 💾 Local data storage (no cloud sync)
echo 📧 Email notifications (when configured)
echo.
echo 🚀 Starting Python server on port 8000...
echo.
echo 📋 Access Information:
echo    • Web Interface: http://localhost:8000
echo    • Basic localhost functionality
echo    • Data stored in browser localStorage
echo    • Email notifications available
echo.
echo 🛑 Press Ctrl+C to stop the server
echo.

REM Start the basic Python server
python basic-server.py

pause