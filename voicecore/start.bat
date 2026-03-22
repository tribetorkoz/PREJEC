@echo off
title VoiceCore - Quick Start
color 0A

echo.
echo  ================================================
echo       VOICECORE - QUICK START
echo  ================================================
echo.

:: Kill existing processes
echo [*] Stopping existing servers...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 1 /nobreak >nul

:: Initialize Database
echo [*] Initializing database...
cd /d "%~dp0backend"
start /B python scripts\seed.py >nul 2>&1
timeout /t 2 /nobreak >nul

:: Start Backend
echo [*] Starting Backend on port 8000...
start "VoiceCore Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000"

:: Wait for backend
timeout /t 5 /nobreak >nul

:: Start Python HTTP Server (for super-admin page)
echo [*] Starting Super Admin Panel on port 8080...
start "VoiceCore Admin" cmd /k "cd /d %~dp0 && python -m http.server 8080"

:: Wait
timeout /t 2 /nobreak >nul

:: Open browser with super admin
echo [*] Opening Super Admin Panel...
start http://localhost:8080/super-admin.html

:: Done
cls
echo.
echo  ================================================
echo   VOICECORE IS RUNNING!
echo  ================================================
echo.
echo   Super Admin Panel:  http://localhost:8080/super-admin.html
echo   Backend API:        http://localhost:8000
echo   API Docs:           http://localhost:8000/docs
echo.
echo   Email:    admin@voicecore.ai
echo   Password: VoiceCore2024!
echo.
echo  ================================================
echo.
pause
