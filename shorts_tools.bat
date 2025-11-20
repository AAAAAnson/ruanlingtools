@echo off
echo ======================================
echo YouTube Shorts 检测功能
echo ======================================
echo.
echo 选择操作:
echo 1. 测试Shorts检测功能
echo 2. 更新数据库中的Shorts字段
echo 3. 导出包含Shorts信息的Excel报表
echo 4. 返回主菜单
echo.
set /p choice=请输入选项 (1-4): 

if "%choice%"=="1" (
    echo.
    echo 运行Shorts检测测试...
    python test_shorts_detection.py
    pause
    goto :eof
)

if "%choice%"=="2" (
    echo.
    echo 更新数据库中的Shorts字段...
    python update_shorts_field.py
    pause
    goto :eof
)

if "%choice%"=="3" (
    echo.
    set /p keyword=请输入关键词 (留空导出所有): 
    echo.
    echo 导出Excel报表...
    python -c "from src.exporter import DataExporter; e=DataExporter(); print('导出文件:', e.export_videos_report('%keyword%' or None, output_format='excel'))"
    pause
    goto :eof
)

if "%choice%"=="4" (
    echo 返回主菜单...
    call menu.bat
    goto :eof
)

echo 无效的选择！
pause
