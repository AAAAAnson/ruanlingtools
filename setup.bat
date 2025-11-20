@echo off
cls
echo ========================================================
echo      YouTube KOL Crawler - One-Click Setup
echo ========================================================
echo.

:: 检查Python安装
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
python --version
echo OK - Python is installed
echo.

:: 创建虚拟环境
echo [2/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    echo Virtual environment created
)
echo.

:: 激活虚拟环境并安装依赖
echo [3/5] Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

:: 创建必要的目录
echo [4/5] Creating directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
echo Directories created
echo.

:: 设置.env文件
echo [5/5] Setting up configuration...
if exist ".env" (
    echo .env file already exists
    set /p OVERWRITE="Do you want to overwrite it? (y/n): "
    if /i "!OVERWRITE!"=="y" (
        copy .env.example .env >nul
        echo .env file created from template
    )
) else (
    copy .env.example .env >nul
    echo .env file created from template
)
echo.

echo ========================================================
echo              Setup Complete!
echo ========================================================
echo.
echo Next steps:
echo 1. Edit .env file and add your YouTube API keys
echo    Run: notepad .env
echo.
echo 2. Test the installation:
echo    Run: python main.py --status
echo.
echo 3. Start crawling:
echo    Run: run_crawler.bat "your keyword"
echo.
echo ========================================================
echo.

set /p EDIT_ENV="Would you like to edit .env file now? (y/n): "
if /i "%EDIT_ENV%"=="y" (
    notepad .env
)

echo.
echo Setup completed! Press any key to exit...
pause >nul
