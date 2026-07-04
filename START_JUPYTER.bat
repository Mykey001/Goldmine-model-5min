@echo off
echo ========================================
echo   Goldmine ML Strategy
echo   Starting Jupyter Notebook
echo ========================================
echo.

cd notebooks
echo Starting Jupyter in notebooks directory...
echo.
echo Once Jupyter opens in your browser:
echo   1. Click "New" -^> "Python 3"
echo   2. Rename to: 02_feature_engineering.ipynb
echo   3. Follow FEATURE_ENGINEERING_GUIDE.md
echo.
echo Press Ctrl+C here to stop Jupyter when done
echo.

jupyter notebook

pause
