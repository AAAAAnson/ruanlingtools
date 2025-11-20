@echo off
cls
echo ========================================================
echo    YouTube KOL Crawler - Project Cleanup
echo ========================================================
echo.
echo This will remove unnecessary temporary files.
echo.
set /p confirm="Continue? (Y/N): "
if /i not "%confirm%"=="Y" goto :end

echo.
echo Cleaning temporary files...

if exist "check_data.py" del "check_data.py" 2>nul && echo   Deleted: check_data.py
if exist "fix_aggregation.py" del "fix_aggregation.py" 2>nul && echo   Deleted: fix_aggregation.py
if exist "fix_and_check.bat" del "fix_and_check.bat" 2>nul && echo   Deleted: fix_and_check.bat
if exist "quickfix.py" del "quickfix.py" 2>nul && echo   Deleted: quickfix.py
if exist "view_imyfone_data.bat" del "view_imyfone_data.bat" 2>nul && echo   Deleted: view_imyfone_data.bat
if exist "view_data_safe.bat" del "view_data_safe.bat" 2>nul && echo   Deleted: view_data_safe.bat
if exist "solution.bat" del "solution.bat" 2>nul && echo   Deleted: solution.bat
if exist "view_simple.py" del "view_simple.py" 2>nul && echo   Deleted: view_simple.py
if exist "update_homepage_feature.py" del "update_homepage_feature.py" 2>nul && echo   Deleted: update_homepage_feature.py
if exist "clean_project.py" del "clean_project.py" 2>nul && echo   Deleted: clean_project.py
if exist "temp_clean.py.bak" del "temp_clean.py.bak" 2>nul && echo   Deleted: temp_clean.py.bak
if exist "run_crawler copy.ps1" del "run_crawler copy.ps1" 2>nul && echo   Deleted: run_crawler copy.ps1
if exist "CRAWL_SUCCESS_NOTE.md" del "CRAWL_SUCCESS_NOTE.md" 2>nul && echo   Deleted: CRAWL_SUCCESS_NOTE.md
if exist "README_FIX.md" del "README_FIX.md" 2>nul && echo   Deleted: README_FIX.md
if exist "SOLUTION_COMPLETE.md" del "SOLUTION_COMPLETE.md" 2>nul && echo   Deleted: SOLUTION_COMPLETE.md
if exist "HOMEPAGE_UPDATE_SUCCESS.md" del "HOMEPAGE_UPDATE_SUCCESS.md" 2>nul && echo   Deleted: HOMEPAGE_UPDATE_SUCCESS.md

echo.
echo Cleanup complete!
echo.
echo Project is now clean and organized.
echo.

:end
pause
