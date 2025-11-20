@echo off
echo ========================================================
echo    修复缺失的依赖包
echo ========================================================
echo.

echo 正在安装语言检测相关包...
pip install emoji langid langdetect

if errorlevel 1 (
    echo.
    echo 使用国内镜像重试...
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple emoji langid langdetect
)

echo.
echo 检查安装结果...
python -c "import emoji; print('✅ emoji 已安装')" 2>nul || echo ❌ emoji 未安装
python -c "import langid; print('✅ langid 已安装')" 2>nul || echo ❌ langid 未安装

echo.
echo 测试Shorts功能...
python -c "from src.language_detector import LanguageDetector; print('✅ 语言检测模块正常')" 2>nul || echo ❌ 语言检测模块导入失败

echo.
echo 如果还有问题，请运行完整安装：
echo   pip install -r requirements_complete.txt
echo.
pause
