@echo off
title AMTC Lab Management System

REM Change to the directory where this bat file is located
cd /d "%~dp0"

echo ================================================================
echo         AMTC Lab Management System
echo ================================================================
echo.
echo Starting server and opening browser...
echo.

REM Start the server in the background using full path
start /B python "%~dp0basic-server.py"

REM Wait 2 seconds for server to start
timeout /t 2 /nobreak >nul

REM Open the browser
start http://localhost:8000

echo.
echo ================================================================
echo Server is running at: http://localhost:8000
echo.
echo To STOP the server:
echo 1. Close this window, OR
echo 2. Press Ctrl+C
echo ================================================================
echo.

REM Keep the window open so server stays running
pause
