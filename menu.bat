@echo off
cls
echo ========================================================
echo    YouTube KOL Crawler - Main Menu
echo ========================================================
echo.
echo 1. Start GUI (Recommended)
echo 2. Clean Temporary Files  
echo 3. View Tools Menu
echo 4. Exit
echo.
set /p choice="Select option (1-4): "

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
    echo Running cleanup...
    if exist venv\Scripts\python.exe (
        venv\Scripts\python.exe cleanup.py
    ) else (
        python cleanup.py
    )
    goto :eof
)

if "%choice%"=="3" (
    call tools.bat
    goto :eof
)

if "%choice%"=="4" (
    exit
)

echo Invalid choice!
pause
goto :eof
