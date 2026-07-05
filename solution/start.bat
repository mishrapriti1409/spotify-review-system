@echo off
title Spotify Review Discovery Engine
echo =========================================
echo  Spotify AI Review Discovery Engine
echo =========================================
echo.

REM Start backend in a new window (no --reload to avoid port conflicts)
start "Backend - FastAPI" cmd /k "cd /d %~dp0 && python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8001"

REM Wait for backend to initialize
timeout /t 4 /nobreak >nul

REM Start frontend in a new window
start "Frontend - Next.js" cmd /k "cd /d %~dp0frontend && npx next dev"

echo.
echo Both servers are starting...
echo  Backend:  http://localhost:8001
echo  Frontend: http://localhost:3000
echo  API Docs: http://localhost:8001/docs
echo.
echo Close the individual server windows to stop.
pause
