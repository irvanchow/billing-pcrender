@echo off
title Setup Startup - IDB Kiosk
echo ========================================
echo  Setup Startup Otomatis - Workstation
echo ========================================
echo.

set "PROJECT_DIR=%~dp0"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

echo Membuat shortcut startup...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTUP_DIR%\IDB-Kiosk.lnk'); $s.TargetPath = 'pythonw'; $s.Arguments = '-m workstation.main'; $s.WorkingDirectory = '%PROJECT_DIR%'; $s.WindowStyle = 7; $s.Save()"

echo.
echo ========================================
echo  SELESAI
echo ========================================
echo.
echo Shortcut sudah dibuat di folder Startup.
echo Kiosk akan otomatis jalan saat Windows boot.
echo.
echo Untuk test sekarang, double-click: START-WORKSTATION.bat
echo.
pause
