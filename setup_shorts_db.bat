@echo off
echo ========================================================
echo    YouTube Shorts - 数据库设置
echo ========================================================
echo.

REM 检查数据目录
if not exist data (
    echo 创建data目录...
    mkdir data
)

echo 运行数据库迁移...
echo.

python migrate_database.py

echo.
echo ========================================================
echo 如果迁移成功，您现在可以：
echo.
echo 1. 运行测试：
echo    python test_shorts_detection.py
echo.
echo 2. 更新现有数据：
echo    python update_shorts_field.py
echo.
echo 3. 分析Shorts数据：
echo    python shorts_analyzer.py
echo ========================================================
echo.
pause
