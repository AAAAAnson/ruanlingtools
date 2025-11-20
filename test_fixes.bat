@echo off
cls
echo ========================================================
echo    YouTube KOL Crawler - Fix Verification
echo ========================================================
echo.
echo This will test all the fixes:
echo   1. API status check without keywords
echo   2. Analysis function encoding
echo   3. Export function encoding
echo.
echo ========================================================
echo.

if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe test_fixes.py
) else (
    python test_fixes.py
)
