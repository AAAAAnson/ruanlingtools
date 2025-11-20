@echo off
cls
echo ========================================================
echo    YouTube KOL Crawler - GUI启动器
echo ========================================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未检测到Python！
    echo 请安装Python 3.8或更高版本
    pause
    exit /b 1
)

echo [1] 检查环境...

REM 检查关键依赖
python -c "import tkinter" 2>nul
if errorlevel 1 (
    echo ❌ tkinter未安装
    echo 正在安装GUI依赖...
    pip install tk
)

REM 检查数据库
if exist data\youtube_kol.db (
    echo ✅ 数据库已存在
) else (
    echo ⚠️ 数据库不存在（将在首次爬取时创建）
)

REM 检查.env文件
if exist .env (
    echo ✅ 配置文件已存在
) else (
    echo ❌ 配置文件不存在
    if exist .env.example (
        echo 正在从模板创建配置文件...
        copy .env.example .env
        echo.
        echo ⚠️ 请编辑 .env 文件并添加您的YouTube API密钥！
        notepad .env
        pause
    )
)

echo.
echo [2] 启动GUI界面...
echo.

REM 优先使用虚拟环境
if exist venv\Scripts\python.exe (
    echo 使用虚拟环境Python...
    venv\Scripts\python.exe gui_fixed.py
) else (
    echo 使用系统Python...
    python gui_fixed.py
)

if errorlevel 1 (
    echo.
    echo ❌ GUI启动失败！
    echo.
    echo 可能的原因：
    echo 1. 缺少依赖包
    echo 2. 代码有错误
    echo.
    echo 尝试运行诊断：
    echo   python test_gui_analysis.py
    echo.
    pause
)
