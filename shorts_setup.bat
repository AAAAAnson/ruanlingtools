@echo off
cls
echo ========================================================
echo    YouTube Shorts 功能 - 快速设置向导
echo ========================================================
echo.
echo 欢迎使用YouTube Shorts检测功能！
echo.
echo 请选择操作：
echo.
echo 1. 首次设置（推荐新用户）
echo 2. 修复数据库字段
echo 3. 测试Shorts功能（不需要数据库）
echo 4. 更新现有视频数据
echo 5. 分析Shorts数据
echo 6. 退出
echo.
set /p choice="请选择 (1-6): "

if "%choice%"=="1" (
    cls
    echo ========================================================
    echo    首次设置
    echo ========================================================
    echo.
    echo 步骤 1: 检查依赖...
    python check_and_install_deps.py
    if errorlevel 1 (
        echo.
        echo ❌ 依赖安装失败，请手动安装：
        echo    pip install emoji langid langdetect
        pause
        goto :eof
    )
    
    echo.
    echo 步骤 2: 设置数据库...
    python migrate_database.py
    
    echo.
    echo 步骤 3: 运行测试...
    python test_shorts_simple.py
    
    echo.
    echo ========================================================
    echo ✅ 设置完成！
    echo.
    echo 现在您可以：
    echo 1. 运行爬虫（会自动检测Shorts）：
    echo    python main.py "关键词"
    echo.
    echo 2. 更新现有数据：
    echo    python update_shorts_field.py
    echo.
    echo 3. 分析Shorts数据：
    echo    python shorts_analyzer.py
    echo ========================================================
    pause
    goto :eof
)

if "%choice%"=="2" (
    echo.
    echo 修复数据库字段...
    python migrate_database.py
    pause
    goto :eof
)

if "%choice%"=="3" (
    echo.
    echo 运行Shorts功能测试（简化版）...
    python test_shorts_simple.py
    pause
    goto :eof
)

if "%choice%"=="4" (
    echo.
    echo 更新现有视频数据的Shorts标识...
    python update_shorts_field.py
    pause
    goto :eof
)

if "%choice%"=="5" (
    echo.
    echo 分析Shorts数据...
    python shorts_analyzer.py
    pause
    goto :eof
)

if "%choice%"=="6" (
    exit
)

echo.
echo 无效的选择！
pause
