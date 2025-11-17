@echo off
REM Start AMTC Lab Management API Server in background
REM This script is used by Windows Task Scheduler to start the API server automatically

REM Set the window title (won't be visible since it runs in background)
title AMTC Lab Management System - API Server (Background)

REM Change to the script directory
cd /d "%~dp0"

REM Wait a bit for system to fully boot
timeout /t 30 /nobreak >nul

REM Start the API server silently in background
REM The output will be redirected to a log file
python api_server.py > api_server_startup.log 2>&1

REM If the server stops, restart it after a delay
:restart_loop
echo API server stopped at %date% %time% >> api_server_restart.log
timeout /t 60 /nobreak >nul
python api_server.py >> api_server_startup.log 2>&1
goto restart_loop