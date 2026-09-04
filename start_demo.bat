@echo off
title Industrial PPE Kit Detection Demo System
echo =====================================================================
echo  Starting Industrial PPE Kit Detection Demo System (v2.0)
echo =====================================================================
echo.

cd /d "%~dp0"

set PYTHON_CMD=..\.venv\Scripts\python.exe
if not exist "%PYTHON_CMD%" set PYTHON_CMD=C:\Users\Admin\AppData\Local\Python\bin\python.exe
if not exist "%PYTHON_CMD%" set PYTHON_CMD=python.exe

echo [1/2] Launching FastAPI Backend on http://localhost:8001 ...
start "PPE Demo Backend" cmd /k "%PYTHON_CMD% backend\run_backend.py"

echo [2/2] Launching React Vite Frontend on http://localhost:5173 ...
cd frontend
start "PPE Demo Frontend" cmd /k "npm run dev"

echo.
echo =====================================================================
echo  Both Backend & Frontend servers have been launched!
echo  Opening Dashboard in browser: http://localhost:5173
echo =====================================================================
timeout /t 3 >nul
start http://localhost:5173
