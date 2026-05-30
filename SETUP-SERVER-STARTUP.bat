@echo off
title Setup Startup - IDB Rental Server
echo ========================================
echo  Setup Startup Otomatis - Server
echo ========================================
echo.

set "PROJECT_DIR=%~dp0"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

echo Membuat shortcut startup...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTUP_DIR%\IDB-RentalServer.lnk'); $s.TargetPath = '%PROJECT_DIR%START-SERVER.bat'; $s.WorkingDirectory = '%PROJECT_DIR%'; $s.WindowStyle = 7; $s.Save()"

echo.
echo ========================================
echo  SELESAI
echo ========================================
echo.
echo Shortcut sudah dibuat di folder Startup.
echo Server akan otomatis jalan saat Windows boot.
echo.
echo Untuk test sekarang, double-click: START-SERVER.bat
echo.
pause
