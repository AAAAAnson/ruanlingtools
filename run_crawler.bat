# YouTube KOL Crawler PowerShell Runner
# 带ASCII进度条的执行脚本

param(
    [Parameter(Mandatory=$true)]
    [string[]]$Keywords,
    
    [string]$StartDate = "",
    [int]$StartYear = 0,
    [string]$EndDate = "",
    [int]$MaxResults = 0,
    
    [switch]$ProcessQueue,
    [switch]$EstimateOnly,
    [switch]$Status,
    [switch]$ResetQuota,
    
    [string]$LogLevel = "INFO",
    [int]$ShardId = -1,
    [int]$ShardCount = -1
)

# 设置控制台编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 颜色定义
$colors = @{
    'Header' = 'Cyan'
    'Success' = 'Green'
    'Warning' = 'Yellow'
    'Error' = 'Red'
    'Info' = 'White'
    'Progress' = 'Magenta'
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = 'White'
    )
    Write-Host $Message -ForegroundColor $colors[$Color]
}

function Show-ProgressBar {
    param(
        [int]$Current,
        [int]$Total,
        [string]$Activity = "Processing"
    )
    
    if ($Total -eq 0) {
        $percent = 0
    } else {
        $percent = [Math]::Round(($Current / $Total) * 100, 2)
    }
    
    $barLength = 50
    $filled = [Math]::Round($barLength * $percent / 100)
    $empty = $barLength - $filled
    
    $bar = "█" * $filled + "░" * $empty
    
    # 清除当前行并重写
    Write-Host "`r$Activity [$bar] $percent% ($Current/$Total)" -NoNewline -ForegroundColor $colors['Progress']
}

function Parse-StatsLine {
    param([string]$Line)
    
    if ($Line -match '\[stats\]\s+fetched=(\d+)\s+inserted=(\d+)\s+channels=(\d+)\s+errors=(\d+)\s+api_calls=(\d+)\s+api_cost=(\d+)') {
        return @{
            Fetched = [int]$Matches[1]
            Inserted = [int]$Matches[2]
            Channels = [int]$Matches[3]
            Errors = [int]$Matches[4]
            ApiCalls = [int]$Matches[5]
            ApiCost = [int]$Matches[6]
        }
    }
    return $null
}

# 显示标题
Write-ColorOutput "`n===============================================" "Header"
Write-ColorOutput "     YouTube KOL Crawler - PowerShell Runner" "Header"
Write-ColorOutput "===============================================`n" "Header"

# 检查Python环境
Write-ColorOutput "Checking Python environment..." "Info"
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-ColorOutput "Error: Python is not installed or not in PATH" "Error"
    exit 1
}
Write-ColorOutput "Found: $pythonVersion" "Success"

# 检查虚拟环境
$venvPath = Join-Path $PSScriptRoot "venv"
if (Test-Path $venvPath) {
    Write-ColorOutput "Activating virtual environment..." "Info"
    & "$venvPath\Scripts\Activate.ps1"
} else {
    Write-ColorOutput "No virtual environment found. Creating one..." "Warning"
    python -m venv $venvPath
    & "$venvPath\Scripts\Activate.ps1"
    
    Write-ColorOutput "Installing requirements..." "Info"
    pip install -r (Join-Path $PSScriptRoot "requirements.txt")
}

# 检查.env文件
$envFile = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $envFile)) {
    Write-ColorOutput "Warning: .env file not found!" "Warning"
    Write-ColorOutput "Please create .env file from .env.example and add your API keys" "Warning"
    
    # 提示创建.env文件
    $createEnv = Read-Host "Would you like to create .env from template? (Y/N)"
    if ($createEnv -eq 'Y' -or $createEnv -eq 'y') {
        Copy-Item (Join-Path $PSScriptRoot ".env.example") $envFile
        Write-ColorOutput ".env file created. Please edit it and add your API keys." "Success"
        notepad $envFile
        Read-Host "Press Enter after adding your API keys..."
    } else {
        exit 1
    }
}

# 构建Python命令
$pythonScript = Join-Path $PSScriptRoot "main.py"
$arguments = @($pythonScript)

# 添加关键词
foreach ($keyword in $Keywords) {
    $arguments += $keyword
}

# 添加可选参数
if ($StartDate) { $arguments += "--start-date", $StartDate }
if ($StartYear -gt 0) { $arguments += "--start-year", $StartYear }
if ($EndDate) { $arguments += "--end-date", $EndDate }
if ($MaxResults -gt 0) { $arguments += "--max-results", $MaxResults }
if ($ProcessQueue) { $arguments += "--process-queue" }
if ($EstimateOnly) { $arguments += "--estimate-only" }
if ($Status) { $arguments += "--status" }
if ($ResetQuota) { $arguments += "--reset-quota" }
if ($LogLevel) { $arguments += "--log-level", $LogLevel }
if ($ShardId -ge 0) { $arguments += "--shard-id", $ShardId }
if ($ShardCount -gt 0) { $arguments += "--shard-count", $ShardCount }

# 显示执行信息
Write-ColorOutput "`nStarting crawler with parameters:" "Info"
Write-ColorOutput "Keywords: $($Keywords -join ', ')" "Info"
if ($StartDate) { Write-ColorOutput "Start Date: $StartDate" "Info" }
if ($StartYear -gt 0) { Write-ColorOutput "Start Year: $StartYear" "Info" }
if ($EndDate) { Write-ColorOutput "End Date: $EndDate" "Info" }
if ($MaxResults -gt 0) { Write-ColorOutput "Max Results: $MaxResults" "Info" }
Write-ColorOutput "" "Info"

# 执行Python脚本并捕获输出
$process = Start-Process -FilePath "python" -ArgumentList $arguments -NoNewWindow -PassThru -RedirectStandardOutput "temp_output.txt" -RedirectStandardError "temp_error.txt"

# 监控输出并显示进度
$lastStats = $null
$startTime = Get-Date

while (-not $process.HasExited) {
    Start-Sleep -Milliseconds 500
    
    if (Test-Path "temp_output.txt") {
        $lines = Get-Content "temp_output.txt" -Tail 20
        foreach ($line in $lines) {
            if ($line -match '\[stats\]') {
                $stats = Parse-StatsLine $line
                if ($stats) {
                    $lastStats = $stats
                    
                    # 显示进度条
                    $activity = "Fetching videos"
                    if ($stats.Fetched -gt 0) {
                        Show-ProgressBar -Current $stats.Inserted -Total $stats.Fetched -Activity $activity
                    }
                }
            } elseif ($line -and -not ($line -match '\[stats\]')) {
                # 显示其他输出
                Write-Host "`r$(' ' * 80)`r" -NoNewline  # 清除进度条
                Write-Host $line
            }
        }
    }
}

# 等待进程结束
$process.WaitForExit()

# 清除进度条
Write-Host "`r$(' ' * 80)`r" -NoNewline

# 显示最终统计
if ($lastStats) {
    Write-ColorOutput "`n===============================================" "Header"
    Write-ColorOutput "                Final Statistics" "Header"
    Write-ColorOutput "===============================================" "Header"
    Write-ColorOutput "Videos Fetched:  $($lastStats.Fetched)" "Success"
    Write-ColorOutput "Videos Inserted: $($lastStats.Inserted)" "Success"
    Write-ColorOutput "Channels Found:  $($lastStats.Channels)" "Success"
    Write-ColorOutput "API Calls Made:  $($lastStats.ApiCalls)" "Info"
    Write-ColorOutput "API Cost:        $($lastStats.ApiCost) units" "Info"
    if ($lastStats.Errors -gt 0) {
        Write-ColorOutput "Errors:          $($lastStats.Errors)" "Warning"
    }
}

# 计算运行时间
$endTime = Get-Date
$duration = $endTime - $startTime
Write-ColorOutput "`nTotal execution time: $($duration.ToString('hh\:mm\:ss'))" "Info"

# 清理临时文件
if (Test-Path "temp_output.txt") { Remove-Item "temp_output.txt" }
if (Test-Path "temp_error.txt") { Remove-Item "temp_error.txt" }

# 检查退出码
if ($process.ExitCode -ne 0) {
    Write-ColorOutput "`nCrawler exited with error code: $($process.ExitCode)" "Error"
    exit $process.ExitCode
}

Write-ColorOutput "`nCrawler completed successfully!" "Success"
