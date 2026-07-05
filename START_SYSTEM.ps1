# Goldmine ML Trading - System Launcher (PowerShell)
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  GOLDMINE ML TRADING - SYSTEM LAUNCHER" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/4] Checking Python environment..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "    ✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    try {
        $pythonVersion = py --version 2>&1
        Write-Host "    ✓ Python found (py command): $pythonVersion" -ForegroundColor Green
        $pythonCmd = "py"
    } catch {
        Write-Host "    ✗ ERROR: Python not found! Please install Python 3.8+" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Check Node.js
Write-Host ""
Write-Host "[2/4] Checking Node.js environment..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "    ✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "    ✗ ERROR: Node.js not found! Please install Node.js 18+" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Virtual Environment
Write-Host ""
Write-Host "[3/4] Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "    ✓ Virtual environment found!" -ForegroundColor Green
    $useVenv = $true
} else {
    Write-Host "    ! No virtual environment (will use system Python)" -ForegroundColor Yellow
    $useVenv = $false
}

# Start Services
Write-Host ""
Write-Host "[4/4] Starting services..." -ForegroundColor Yellow
Write-Host ""

# Start Backend
Write-Host "Starting Backend (Python)..." -ForegroundColor Cyan
Write-Host "Opening new PowerShell window for backend..." -ForegroundColor Gray

if ($useVenv) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; cd src\live_trading; python run.py" -WindowStyle Normal
} else {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\src\live_trading'; python run.py" -WindowStyle Normal
}

Start-Sleep -Seconds 3

# Start Frontend
Write-Host ""
Write-Host "Starting Frontend (React)..." -ForegroundColor Cyan
Write-Host "Opening new PowerShell window for frontend..." -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SYSTEM STARTING..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API will be at: " -NoNewline
Write-Host "http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend Dashboard will be at: " -NoNewline
Write-Host "http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "Wait 10-15 seconds for services to start," -ForegroundColor Yellow
Write-Host "then open your browser to:" -ForegroundColor Yellow
Write-Host ""
Write-Host "    http://localhost:5173" -ForegroundColor Cyan -BackgroundColor Black
Write-Host ""
Write-Host "To stop the system:" -ForegroundColor Yellow
Write-Host "1. Close both PowerShell windows" -ForegroundColor White
Write-Host "2. Or press Ctrl+C in each window" -ForegroundColor White
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to close this launcher"
