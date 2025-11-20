@echo off
chcp 65001 > nul
title YouTube KOL 互动率分析 - 演示

echo.
echo ============================================================
echo YouTube KOL 互动率分析 - 新功能演示
echo ============================================================
echo.

echo 选择操作:
echo.
echo [1] 查看功能说明（推荐先看这个）
echo [2] 运行互动率计算测试
echo [3] 查看使用示例说明
echo [4] 运行完整的 KOL 分析（需要输入关键词）
echo [5] 查看详细文档
echo [0] 退出
echo.

set /p choice=请选择 [0-5]: 

if "%choice%"=="1" goto show_guide
if "%choice%"=="2" goto run_test
if "%choice%"=="3" goto show_example
if "%choice%"=="4" goto run_analysis
if "%choice%"=="5" goto open_doc
if "%choice%"=="0" goto end

echo 无效选择，请重试
pause
goto start

:show_guide
cls
echo.
echo ============================================================
echo 📊 互动率功能说明
echo ============================================================
echo.
echo 什么是互动率？
echo   互动率 = (点赞数 + 评论数) / 播放量 × 100%%
echo.
echo 为什么重要？
echo   ✓ 反映观众真实参与度
echo   ✓ 筛选优质 KOL 的关键指标
echo   ✓ 比单纯看播放量更准确
echo.
echo 功能特点：
echo   ✓ 自动计算每个视频的互动率
echo   ✓ 计算频道平均互动率
echo   ✓ Excel 报表新增互动率列
echo   ✓ 支持实时 API 数据和数据库数据
echo.
echo 互动率标准：
echo   🔥 ^> 10%%  - 优秀
echo   ✅ 5-10%%  - 良好  
echo   ⚠️ 2-5%%   - 一般
echo   ❌ ^< 2%%   - 较低
echo.
echo ============================================================
echo.
pause
goto start

:run_test
cls
echo.
echo ============================================================
echo 🧪 运行互动率计算测试
echo ============================================================
echo.
venv\Scripts\python.exe test_engagement_rate.py
echo.
echo ============================================================
echo.
pause
goto start

:show_example
cls
echo.
echo ============================================================
echo 💡 查看使用示例说明
echo ============================================================
echo.
venv\Scripts\python.exe example_engagement_analysis.py
echo.
echo ============================================================
echo.
pause
goto start

:run_analysis
cls
echo.
echo ============================================================
echo 🚀 运行 KOL 分析（包含互动率）
echo ============================================================
echo.
echo 提示: 输入关键词后，系统将:
echo   1. 爬取相关视频
echo   2. 分析频道数据
echo   3. 计算互动率
echo   4. 生成 Excel 报表
echo.
set /p keyword=请输入分析关键词: 

if "%keyword%"=="" (
    echo 错误: 关键词不能为空
    pause
    goto start
)

echo.
echo 开始分析关键词: %keyword%
echo 使用最新数据（会消耗 API 配额）
echo.

venv\Scripts\python.exe analyze_keyword_kol.py "%keyword%" --start-year 2024 --get-latest-videos

echo.
echo ============================================================
echo 分析完成！请查看 data 目录下的 Excel 文件
echo ============================================================
echo.
pause
goto start

:open_doc
cls
echo.
echo ============================================================
echo 📖 打开详细文档
echo ============================================================
echo.
start ENGAGEMENT_RATE_GUIDE.md
echo.
echo 已在默认编辑器中打开文档
echo.
pause
goto start

:start
cls
goto :eof

:end
echo.
echo 感谢使用！
timeout /t 2 > nul
