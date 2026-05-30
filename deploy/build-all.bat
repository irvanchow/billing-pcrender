@echo off
title Build IDB PC Rental Applications
echo ========================================
echo  Build Server + Workstation Apps
echo ========================================
echo.

cd /d "%~dp0.."

echo [1/2] Build Registration App (Server)...
cd server
pip install -r requirements.txt --quiet
pyinstaller build.spec --distpath ..\dist\server --workpath ..\build\server --noconfirm
if %errorlevel% neq 0 ( echo GAGAL build server & pause & exit /b 1 )
echo OK: dist\server\RentalServer\

echo.
echo [2/2] Build Workstation Kiosk App...
cd ..\workstation
pip install -r requirements.txt --quiet
pyinstaller build.spec --distpath ..\dist\workstation --workpath ..\build\workstation --noconfirm
if %errorlevel% neq 0 ( echo GAGAL build workstation & pause & exit /b 1 )
echo OK: dist\workstation\KioskTimer.exe

echo.
echo ========================================
echo  BUILD SELESAI
echo ========================================
echo Output ada di folder: dist\
echo Salin ke folder deploy\ lalu jalankan install script di masing-masing PC.
echo.
pause
