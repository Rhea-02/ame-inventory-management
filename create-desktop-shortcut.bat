@echo off
echo ========================================
echo    Creating Desktop Shortcut for 
echo    AMTC Lab Management System
echo ========================================
echo.

:: Get the current directory
set "CURRENT_DIR=%~dp0"

:: Create the shortcut on desktop
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT_NAME=AMTC Lab System.url"

echo Creating desktop shortcut...
echo.

:: Create URL shortcut file
(
echo [InternetShortcut]
echo URL=file:///%CURRENT_DIR%launch-company-system.html
echo IconFile=%CURRENT_DIR%launch-company-system.html
echo IconIndex=0
) > "%DESKTOP%\%SHORTCUT_NAME%"

echo ✅ Desktop shortcut created successfully!
echo.
echo 📋 Instructions for employees:
echo    1. Double-click "AMTC Lab System" on desktop
echo    2. Click "Start Lab System" (first time only)
echo    3. Click "Open Lab System" to access the lab
echo.
echo 🎯 The shortcut is saved as: %SHORTCUT_NAME%
echo    on your desktop.
echo.
pause