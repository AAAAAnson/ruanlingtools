@echo off
cls
echo ========================================================
echo      YouTube KOL Crawler - Homepage URL Update
echo ========================================================
echo.
echo This will add homepage URL support to the system:
echo   - Add homepage_url field to database
echo   - Add youtube_handle field for @usernames
echo   - Generate URLs for existing channels
echo   - Update export to include homepage links
echo.
echo ========================================================
echo.

set /p confirm="Do you want to proceed with the update? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo Update cancelled.
    pause
    exit /b
)

echo.
echo [1/3] Updating system files...

REM Use virtual environment Python if available
if exist venv\Scripts\python.exe (
    set PYTHON=venv\Scripts\python.exe
) else (
    set PYTHON=python
)

REM Run the update script
echo.
echo [2/3] Running update script...
%PYTHON% update_homepage_feature.py

if errorlevel 1 (
    echo.
    echo Error occurred during update!
    pause
    exit /b 1
)

echo.
echo [3/3] Verifying update...
%PYTHON% view_data_urls.py

echo.
echo ========================================================
echo               Update Completed Successfully!
echo ========================================================
echo.
echo What's new:
echo   + Every channel now has a homepage URL
echo   + @handle support for new YouTube format
echo   + Excel exports include clickable homepage links
echo.
echo Next steps:
echo   1. Export your data: tools.bat (Option 2)
echo   2. Check the new Homepage URL column in Excel
echo   3. Future crawls will automatically capture URLs
echo.
echo ========================================================
echo.
pause
