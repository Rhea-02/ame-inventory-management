@echo off
echo ========================================
echo    🌐 AMTC Lab Web Launcher
echo    Chrome Bookmark Edition
echo ========================================
echo.
echo 🚀 Starting web launcher server...
echo 📌 Employees can bookmark: http://localhost:8082/launcher
echo 🔬 Direct lab access: http://localhost:8082/lab
echo.
echo ✨ Your browser will open automatically
echo 💡 Share these URLs with your 5 employees for Chrome bookmarks
echo.
echo Press Ctrl+C to stop the server
echo ========================================

python web-launcher-server.py

pause