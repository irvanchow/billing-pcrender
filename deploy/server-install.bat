@echo off
setlocal EnableDelayedExpansion
title IDB PC Rental - Server Setup

echo ========================================
echo  IDB Bali - Setup Aplikasi Server
echo ========================================
echo.

:: Check Admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Jalankan sebagai Administrator!
    pause
    exit /b 1
)

set "INSTALL_DIR=C:\Program Files\IDB-Rental-Server"
set "EXE_SRC=%~dp0RentalServer"

echo [1/5] Membuat folder instalasi...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%INSTALL_DIR%\data" mkdir "%INSTALL_DIR%\data"

echo [2/5] Menyalin file aplikasi...
xcopy /E /I /Y "%EXE_SRC%" "%INSTALL_DIR%" >nul
if %errorlevel% neq 0 (
    echo ERROR: Gagal menyalin file. Pastikan folder RentalServer ada.
    pause
    exit /b 1
)

echo [3/5] Membuat file konfigurasi...
set "CONFIG=%INSTALL_DIR%\config.ini"
if not exist "%CONFIG%" (
    (
        echo [server]
        echo HOST = 0.0.0.0
        echo PORT = 8765
        echo API_KEY = GANTI_KUNCI_INI_SEKARANG
        echo DB_NAME = rental.db
    ) > "%CONFIG%"
    echo PERHATIAN: Edit file config.ini dan ganti API_KEY!
)

echo [4/5] Mengizinkan port 8765 di Windows Firewall...
netsh advfirewall firewall add rule ^
    name="IDB PC Rental Server" ^
    dir=in ^
    action=allow ^
    protocol=TCP ^
    localport=8765 ^
    profile=private >nul

echo [5/5] Membuat shortcut startup...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\IDB-RentalServer.lnk'); $s.TargetPath = '%INSTALL_DIR%\RentalServer.exe'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Save()"

echo.
echo ========================================
echo  SETUP SELESAI
echo ========================================
echo.
echo Langkah selanjutnya:
echo 1. Edit file: %CONFIG%
echo    - Ganti API_KEY dengan kunci rahasia yang sama dengan workstation
echo    - Pastikan IP PC ini sudah STATIC di pengaturan jaringan
echo.
echo 2. Jalankan: %INSTALL_DIR%\RentalServer.exe
echo.
pause
