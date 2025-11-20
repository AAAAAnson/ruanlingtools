@echo off
cls
echo ========================================================
echo    YouTube KOL Crawler - 主菜单
echo ========================================================
echo.
echo 1. 启动图形界面 (推荐)
echo 2. 运行爬虫 (命令行)
echo 3. Shorts分析工具 ⚡
echo 4. 数据导出工具
echo 5. 清理临时文件
echo 6. 查看工具菜单
echo 7. 退出
echo.
set /p choice="选择选项 (1-7): "

if "%choice%"=="1" (
    echo 启动图形界面...
    if exist venv\Scripts\python.exe (
        start venv\Scripts\python.exe gui_fixed.py
    ) else (
        start python gui_fixed.py
    )
    exit
)

if "%choice%"=="2" (
    echo.
    set /p keyword="请输入要爬取的关键词: "
    echo 开始爬取...
    if exist venv\Scripts\python.exe (
        venv\Scripts\python.exe main.py "%keyword%"
    ) else (
        python main.py "%keyword%"
    )
    pause
    goto :eof
)

if "%choice%"=="3" (
    cls
    echo ========================================================
    echo    YouTube Shorts 分析工具
    echo ========================================================
    echo.
    echo 1. 测试Shorts检测功能
    echo 2. 更新数据库Shorts字段
    echo 3. 分析Shorts数据
    echo 4. 导出Shorts报告
    echo 5. 返回主菜单
    echo.
    set /p shorts_choice="选择选项 (1-5): "
    
    if "!shorts_choice!"=="1" (
        echo 运行Shorts检测测试...
        python test_shorts_detection.py
        pause
    )
    
    if "!shorts_choice!"=="2" (
        echo 更新数据库中的Shorts字段...
        python update_shorts_field.py
        pause
    )
    
    if "!shorts_choice!"=="3" (
        echo 分析Shorts数据...
        python shorts_analyzer.py
        pause
    )
    
    if "!shorts_choice!"=="4" (
        set /p keyword="请输入关键词（留空导出所有）: "
        python -c "from shorts_analyzer import ShortsAnalyzer; a=ShortsAnalyzer(); print(a.export_shorts_report('!keyword!' if '!keyword!' else None))"
        pause
    )
    
    goto :eof
)

if "%choice%"=="4" (
    echo.
    echo 选择导出类型：
    echo 1. 导出频道报告
    echo 2. 导出视频报告（包含Shorts标识）
    echo.
    set /p export_choice="选择 (1-2): "
    set /p keyword="请输入关键词（留空导出所有）: "
    
    if "!export_choice!"=="1" (
        python -c "from src.exporter import DataExporter; e=DataExporter(); print('导出文件:', e.export_channels_report('!keyword!' if '!keyword!' else None, output_format='excel'))"
    )
    
    if "!export_choice!"=="2" (
        python -c "from src.exporter import DataExporter; e=DataExporter(); print('导出文件:', e.export_videos_report('!keyword!' if '!keyword!' else None, output_format='excel'))"
    )
    
    pause
    goto :eof
)

if "%choice%"=="5" (
    echo 运行清理...
    if exist venv\Scripts\python.exe (
        venv\Scripts\python.exe cleanup.py
    ) else (
        python cleanup.py
    )
    pause
    goto :eof
)

if "%choice%"=="6" (
    call tools.bat
    goto :eof
)

if "%choice%"=="7" (
    exit
)

echo 无效的选择！
pause
goto :eof
