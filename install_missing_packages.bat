@echo off
echo ============================================
echo   Installing Missing Backend Packages
echo ============================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing python-socketio...
pip install python-socketio

echo.
echo Installing python-multipart...
pip install python-multipart

echo.
echo Installing websockets...
pip install websockets

echo.
echo Installing asyncpg...
pip install asyncpg

echo.
echo ============================================
echo   Installation Complete!
echo ============================================
echo.
echo You can now start the backend with:
echo   cd src\live_trading
echo   python run.py
echo.
pause
