@echo off
REM AMTC Lab Management System - Automated Email Setup
REM This script sets up Windows Task Scheduler for daily automated email notifications

echo.
echo ===============================================
echo AMTC Lab Management System
echo Automated Email Notification Setup
echo ===============================================
echo.

REM Check for administrative privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script requires administrator privileges
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo Setting up automated daily email notifications...
echo.

REM Get current directory
set "CURRENT_DIR=%~dp0"
set "SCRIPT_PATH=%CURRENT_DIR%automated_email_system.py"
set "CONFIG_PATH=%CURRENT_DIR%email_config.json"

REM Check if required files exist
if not exist "%SCRIPT_PATH%" (
    echo ERROR: automated_email_system.py not found
    echo Please ensure you're running this from the correct directory
    pause
    exit /b 1
)

if not exist "%CONFIG_PATH%" (
    echo ERROR: email_config.json not found
    echo Please create the configuration file first
    pause
    exit /b 1
)

echo Creating Windows Task Scheduler job...

REM Create the scheduled task
schtasks /create /tn "AMTC Lab Email Notifications" /tr "python \"%SCRIPT_PATH%\"" /sc daily /st 09:00 /ru SYSTEM /f

if %errorlevel% equ 0 (
    echo.
    echo ✅ SUCCESS: Automated email notifications have been set up!
    echo.
    echo 📅 Schedule: Daily at 9:00 AM
    echo 🔧 Task Name: "AMTC Lab Email Notifications"
    echo 📁 Script: %SCRIPT_PATH%
    echo.
    echo The system will now automatically:
    echo • Send warnings 2 days before items are due
    echo • Send due date notifications on the day items are due
    echo • Send daily overdue notifications for items past due date
    echo.
    echo To manage this task:
    echo • Open Task Scheduler (taskschd.msc)
    echo • Look for "AMTC Lab Email Notifications"
    echo.
) else (
    echo.
    echo ❌ ERROR: Failed to create scheduled task
    echo Please check permissions and try again
    echo.
)

echo Creating manual run script...

REM Create a manual run script
(
echo @echo off
echo echo Running AMTC Lab Email Notifications manually...
echo cd /d "%CURRENT_DIR%"
echo python automated_email_system.py
echo echo.
echo echo Process completed. Check the log file for details.
echo pause
) > "%CURRENT_DIR%run-manual-notifications.bat"

echo ✅ Created manual run script: run-manual-notifications.bat

echo.
echo Creating test run script...

REM Create a test script
(
echo @echo off
echo echo Testing AMTC Lab Email Notifications (DRY RUN)...
echo cd /d "%CURRENT_DIR%"
echo python automated_email_system.py --dry-run --verbose
echo echo.
echo echo Test completed. Check the output above for any issues.
echo pause
) > "%CURRENT_DIR%test-notifications.bat"

echo ✅ Created test script: test-notifications.bat

echo.
echo ===============================================
echo Setting up API Server for Better Data Access
echo ===============================================
echo.

echo Creating API server startup task for Windows...

REM Create API server startup task
schtasks /create /tn "AMTC Lab API Server" /tr "\"%CURRENT_DIR%start-api-server-background.bat\"" /sc onstart /ru SYSTEM /f

if %errorlevel% equ 0 (
    echo ✅ API server startup task created successfully
    echo    The API server will start automatically when Windows boots
) else (
    echo ❌ Failed to create API server startup task
)

echo.
echo ===============================================
echo Setup Complete!
echo ===============================================
echo.
echo Your AMTC Lab system now includes:
echo ✅ Daily automated email notifications (9:00 AM)
echo ✅ API server for real-time data access
echo ✅ Background services that start with Windows
echo.
echo Next steps:
echo 1. Configure your email settings in email_config.json
echo 2. Start the API server: run start-api-server.bat
echo 3. Test the system by running: test-notifications.bat
echo 4. Test API endpoints: run test-api.bat
echo.
echo Additional commands:
echo • Manual notifications: run-manual-notifications.bat
echo • Test without emails: test-notifications.bat
echo • API tests: test-api.bat
echo • Disable email task: schtasks /delete /tn "AMTC Lab Email Notifications"
echo • Disable API server: schtasks /delete /tn "AMTC Lab API Server"
echo.

pause