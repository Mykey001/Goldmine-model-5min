@echo off
echo ============================================
echo   GOLDMINE ML TRADING - SYSTEM LAUNCHER
echo ============================================
echo.

echo [1/3] Checking Python environment...
set PYTHON_CMD=
where python >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    echo     Python found!
) else (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
        echo     Python found (using 'py' command^)!
    ) else (
        echo ERROR: Python not found! Please install Python 3.8+
        echo Note: You are using a virtual environment (venv)
        echo Please use PowerShell or activate venv manually
        pause
        exit /b 1
    )
)

echo.
echo [2/3] Checking Node.js environment...
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found! Please install Node.js 18+
    pause
    exit /b 1
)
echo     Node.js found!

echo.
echo [3/3] Checking virtual environment...
if exist "venv\Scripts\activate.bat" (
    echo     Virtual environment found!
    set ACTIVATE_VENV=call venv\Scripts\activate.bat
) else (
    echo     No virtual environment (will use system Python)
    set ACTIVATE_VENV=
)

echo.
echo [4/4] Starting services...
echo.

echo Starting Backend (Python with venv)...
echo This will open in a new window...
if defined ACTIVATE_VENV (
    start "Goldmine Backend" cmd /k "%ACTIVATE_VENV% && cd src\live_trading && %PYTHON_CMD% run.py"
) else (
    start "Goldmine Backend" cmd /k "cd src\live_trading && %PYTHON_CMD% run.py"
)
timeout /t 5 /nobreak >nul

echo.
echo Starting Frontend (React)...
echo This will open in a new window...
start "Goldmine Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ============================================
echo   SYSTEM STARTING...
echo ============================================
echo.
echo Backend API will be at: http://localhost:8000
echo Frontend Dashboard will be at: http://localhost:5173
echo.
echo Wait 10-15 seconds for services to start,
echo then open your browser to:
echo.
echo     http://localhost:5173
echo.
echo To stop the system:
echo 1. Close both terminal windows
echo 2. Or press Ctrl+C in each window
echo.
echo ============================================
pause
