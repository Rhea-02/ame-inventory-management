@echo off
cd /d "C:\Users\223110730\Box\AME Lab Management System"
echo Starting server from: %CD%
echo Files in directory:
dir /b
echo.
echo Starting HTTP server on port 8084...
python -m http.server 8084