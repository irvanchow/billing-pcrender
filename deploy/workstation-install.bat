@echo off
setlocal EnableDelayedExpansion
title IDB PC Rental - Workstation Setup

echo ========================================
echo  IDB Bali - Setup Aplikasi Kiosk
echo ========================================
echo.

:: Check Admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Jalankan sebagai Administrator!
    pause
    exit /b 1
)

:: Prompt for PC ID
set /p PC_ID="Masukkan nomor PC (1 atau 2): "
if "%PC_ID%" neq "1" if "%PC_ID%" neq "2" (
    echo ERROR: Nomor PC harus 1 atau 2
    pause
    exit /b 1
)

set /p SERVER_IP="Masukkan IP server operator (contoh: 192.168.1.10): "
set /p API_KEY="Masukkan API_KEY (harus sama dengan server): "

set "INSTALL_DIR=C:\Program Files\IDB-Kiosk"
set "STARTUP_DIR=C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp"

echo [1/5] Membuat folder instalasi...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo [2/5] Menyalin file aplikasi...
copy /Y "%~dp0KioskTimer.exe" "%INSTALL_DIR%\KioskTimer.exe" >nul
if %errorlevel% neq 0 (
    echo ERROR: KioskTimer.exe tidak ditemukan di folder deploy.
    pause
    exit /b 1
)

echo [3/5] Membuat file konfigurasi...
(
    echo [workstation]
    echo SERVER_URL = http://%SERVER_IP%:8765
    echo API_KEY = %API_KEY%
    echo PC_ID = %PC_ID%
    echo POLL_INTERVAL = 5
) > "%INSTALL_DIR%\config.ini"

echo [4/5] Membuat shortcut autostart (semua pengguna)...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTUP_DIR%\IDB-KioskTimer.lnk'); $s.TargetPath = '%INSTALL_DIR%\KioskTimer.exe'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Save()"

echo [5/5] Mengatur kebijakan akun kiosk...
echo.
echo LANGKAH MANUAL yang perlu dilakukan IT:
echo.
echo A. Buat akun Windows terbatas bernama 'kiosk-user':
echo    net user kiosk-user KioskPass2026! /add
echo    net localgroup Users kiosk-user /add
echo.
echo B. Aktifkan auto-login untuk kiosk-user:
echo    Jalankan perintah berikut di PowerShell sebagai Admin:
echo    reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v AutoAdminLogon /d 1 /f
echo    reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultUserName /d "kiosk-user" /f
echo    reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultPassword /d "KioskPass2026!" /f
echo.
echo C. Disable Task Manager via Group Policy (gpedit.msc):
echo    User Configuration ^> Admin Templates ^> System ^> Ctrl+Alt+Del Options
echo    ^> Remove Task Manager: ENABLED
echo.

echo ========================================
echo  SETUP SELESAI - PC %PC_ID%
echo ========================================
echo.
echo Konfigurasi tersimpan di: %INSTALL_DIR%\config.ini
echo Reboot PC untuk memulai kiosk otomatis.
echo.
pause
