@echo off
chcp 65001 >nul
echo ========================================
echo   YouTube KOL 分析工具
echo ========================================
echo.

if "%~1"=="" (
    echo 用法: run_kol_analyzer.bat "关键词" [选项]
    echo.
    echo 示例:
    echo   run_kol_analyzer.bat "AI technology" --db-only
    echo   run_kol_analyzer.bat "machine learning" --start-year 2023
    echo.
    pause
    exit /b 1
)

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

python analyze_keyword_kol.py %*

if errorlevel 1 (
    echo.
    echo [错误] 分析失败
) else (
    echo.
    echo [成功] 分析完成！
)

echo.
pause
