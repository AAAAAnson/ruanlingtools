@echo off
echo ========================================================
echo      YouTube KOL Crawler - Quick Tools
echo ========================================================
echo.
echo Select an option:
echo.
echo 1. Start GUI (Recommended)
echo 2. View Data Summary
echo 3. Export to Excel
echo 4. Export to CSV
echo 5. Analyze Keyword
echo 6. View API Status
echo 7. Exit
echo.

set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" (
    echo.
    echo Starting GUI...
    if exist venv\Scripts\python.exe (
        start venv\Scripts\python.exe gui_fixed.py
    ) else (
        start python gui_fixed.py
    )
    goto :eof
)

if "%choice%"=="2" (
    echo.
    echo Viewing data summary...
    if exist venv\Scripts\python.exe (
        venv\Scripts\python.exe view_data.py
    ) else (
        python view_data.py
    )
    pause
    goto :eof
)

if "%choice%"=="3" (
    set /p keyword="Enter keyword to export (press Enter for all): "
    echo.
    echo Exporting to Excel...
    if exist venv\Scripts\python.exe (
        if "%keyword%"=="" (
            venv\Scripts\python.exe analyzer.py export --format excel
        ) else (
            venv\Scripts\python.exe analyzer.py export --keyword "%keyword%" --format excel
        )
    ) else (
        if "%keyword%"=="" (
            python analyzer.py export --format excel
        ) else (
            python analyzer.py export --keyword "%keyword%" --format excel
        )
    )
    echo.
    echo Export complete! Opening data folder...
    start data
    pause
    goto :eof
)

if "%choice%"=="4" (
    set /p keyword="Enter keyword to export (press Enter for all): "
    echo.
    echo Exporting to CSV...
    if exist venv\Scripts\python.exe (
        if "%keyword%"=="" (
            venv\Scripts\python.exe analyzer.py export --format csv
        ) else (
            venv\Scripts\python.exe analyzer.py export --keyword "%keyword%" --format csv
        )
    ) else (
        if "%keyword%"=="" (
            python analyzer.py export --format csv
        ) else (
            python analyzer.py export --keyword "%keyword%" --format csv
        )
    )
    echo.
    echo Export complete! Opening data folder...
    start data
    pause
    goto :eof
)

if "%choice%"=="5" (
    set /p keyword="Enter keyword to analyze: "
    echo.
    echo Analyzing keyword: %keyword%
    if exist venv\Scripts\python.exe (
        venv\Scripts\python.exe analyzer.py keyword "%keyword%"
    ) else (
        python analyzer.py keyword "%keyword%"
    )
    pause
    goto :eof
)

if "%choice%"=="6" (
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

if "%choice%"=="7" (
    exit
)

echo Invalid choice!
pause
