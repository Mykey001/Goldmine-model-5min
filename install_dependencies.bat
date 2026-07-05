@echo off
echo Installing Live Trading Dependencies...
echo.

REM Install core packages
pip install sqlalchemy psycopg2-binary python-dotenv

REM Install FastAPI and server
pip install "fastapi[all]" uvicorn

REM Install WebSocket support
pip install python-socketio websockets

REM Install ML and data packages (if not already installed)
pip install pandas numpy xgboost joblib ta

echo.
echo ✅ Installation complete!
echo.
echo Run this to test: cd src\live_trading ^& python test_setup.py
pause
