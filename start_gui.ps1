# YouTube KOL Crawler - GUI启动脚本 (PowerShell版本)

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "    YouTube KOL Crawler - GUI启动器" -ForegroundColor Cyan  
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python已安装: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 错误：未检测到Python！" -ForegroundColor Red
    Write-Host "请安装Python 3.8或更高版本" -ForegroundColor Yellow
    Read-Host "按Enter键退出"
    exit 1
}

Write-Host ""
Write-Host "[1] 检查环境..." -ForegroundColor Yellow

# 检查tkinter
$tkinterCheck = python -c "import tkinter; print('OK')" 2>&1
if ($tkinterCheck -ne "OK") {
    Write-Host "⚠️ tkinter可能未安装" -ForegroundColor Yellow
}

# 检查数据库
if (Test-Path "data\youtube_kol.db") {
    $fileInfo = Get-Item "data\youtube_kol.db"
    $sizeMB = [Math]::Round($fileInfo.Length / 1MB, 2)
    Write-Host "✅ 数据库已存在 (大小: ${sizeMB}MB)" -ForegroundColor Green
} else {
    Write-Host "⚠️ 数据库不存在（将在首次爬取时创建）" -ForegroundColor Yellow
}

# 检查.env文件
if (Test-Path ".env") {
    Write-Host "✅ 配置文件已存在" -ForegroundColor Green
} else {
    Write-Host "❌ 配置文件不存在" -ForegroundColor Red
    if (Test-Path ".env.example") {
        Write-Host "正在从模板创建配置文件..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "⚠️ 请编辑 .env 文件并添加您的YouTube API密钥！" -ForegroundColor Yellow
        notepad .env
        Read-Host "配置完成后，按Enter键继续"
    }
}

Write-Host ""
Write-Host "[2] 启动GUI界面..." -ForegroundColor Yellow
Write-Host ""

# 优先使用虚拟环境
if (Test-Path "venv\Scripts\python.exe") {
    Write-Host "使用虚拟环境Python..." -ForegroundColor Cyan
    & "venv\Scripts\python.exe" gui_fixed.py
} else {
    Write-Host "使用系统Python..." -ForegroundColor Cyan
    python gui_fixed.py
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ GUI启动失败！" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能的原因：" -ForegroundColor Yellow
    Write-Host "1. 缺少依赖包"
    Write-Host "2. 代码有错误"
    Write-Host ""
    Write-Host "尝试运行诊断：" -ForegroundColor Yellow
    Write-Host "  python test_gui_analysis.py"
    Write-Host ""
    Read-Host "按Enter键退出"
}
