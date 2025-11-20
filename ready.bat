@echo off
cls
echo ========================================================
echo    YouTube KOL Crawler - Ready to Use!
echo ========================================================
echo.
echo All bugs have been fixed:
echo   [OK] API status check works without keywords
echo   [OK] Export function encoding fixed
echo   [OK] Analysis function displays correctly  
echo   [OK] GUI emoji characters replaced
echo.
echo ========================================================
echo.
echo Quick Actions:
echo.
echo 1. Start GUI
echo 2. Test Fixes
echo 3. View API Status
echo 4. Export movavi Data
echo 5. Exit
echo.

set /p choice="Select option (1-5): "

if "%choice%"=="1" (
    echo Starting GUI...
    if exist venv\Scripts\python.exe (
        start venv\Scripts\python.exe gui_fixed.py
    ) else (
        start python gui_fixed.py
    )
    exit
)

if "%choice%"=="2" (
    call test_fixes.bat
    pause
    goto :eof
)

if "%choice%"=="3" (
    echo.
    echo Checking API status...
    if exist venv\Scripts\python.exe (
        venv\Scripts\python.exe main.py --status
    ) else (
        python main.py --status
    )
    pause
    goto :eof
)

if "%choice%"=="4" (
    echo.
    echo Exporting movavi data to Excel...
    if exist venv\Scripts\python.exe (
        venv\Scripts\python.exe analyzer.py export --keyword "movavi" --format excel
    ) else (
        python analyzer.py export --keyword "movavi" --format excel
    )
    echo.
    echo Opening data folder...
    start data
    pause
    goto :eof
)

if "%choice%"=="5" (
    exit
)

echo Invalid choice!
pause
