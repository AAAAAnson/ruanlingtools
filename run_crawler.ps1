# YouTube KOL Crawler PowerShell Runner (ASCII-safe, dual-style args)

[CmdletBinding()]
param(
  [Parameter(Mandatory=$false, Position=0)]
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

# ----------- 环境与编码 -----------
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"
$root = Split-Path -Parent $PSCommandPath
Set-Location $root

# ----------- 兼容 GNU 风格与位置参数（GUI 旧调用） -----------
if ($args.Count -gt 0) {
  $pending = @()
  for ($i=0; $i -lt $args.Count; $i++) {
    $a = $args[$i]
    switch -regex ($a) {
      '^--start-date$'    { if ($i+1 -lt $args.Count) { $StartDate   = $args[++$i] }; continue }
      '^--end-date$'      { if ($i+1 -lt $args.Count) { $EndDate     = $args[++$i] }; continue }
      '^--start-year$'    { if ($i+1 -lt $args.Count) { $StartYear   = [int]$args[++$i] }; continue }
      '^--max-results$'   { if ($i+1 -lt $args.Count) { $MaxResults  = [int]$args[++$i] }; continue }
      '^--process-queue$' { $ProcessQueue = $true; continue }
      '^--estimate-only$' { $EstimateOnly = $true; continue }
      '^--status$'        { $Status       = $true; continue }
      '^--reset-quota$'   { $ResetQuota   = $true; continue }
      '^--log-level$'     { if ($i+1 -lt $args.Count) { $LogLevel    = $args[++$i] }; continue }
      '^--shard-id$'      { if ($i+1 -lt $args.Count) { $ShardId     = [int]$args[++$i] }; continue }
      '^--shard-count$'   { if ($i+1 -lt $args.Count) { $ShardCount  = [int]$args[++$i] }; continue }
      default             { $pending += $a }
    }
  }
  if (-not $Keywords -and $pending.Count -gt 0) { $Keywords = $pending }
}

if (-not $Keywords -or $Keywords.Count -eq 0) {
  Write-Error "No keywords provided. Use -Keywords 'kw' or pass a positional keyword."
  exit 1
}

# ----------- 解析 Python 解释器 -----------
$py = Join-Path $root 'venv\Scripts\python.exe'
if (-not (Test-Path $py)) { $py = 'python' }

# 安全引用参数（含空格时加引号）
function Quote-Arg {
  param([string]$s)
  if ($s -match '[\s"]') { return '"' + ($s -replace '"','`"') + '"' }
  return $s
}

# ----------- 输出工具 -----------
function Write-Info    { param([string]$m) Write-Host $m -ForegroundColor White }
function Write-OK      { param([string]$m) Write-Host $m -ForegroundColor Green }
function Write-Warn    { param([string]$m) Write-Host $m -ForegroundColor Yellow }
function Write-ErrLine { param([string]$m) Write-Host $m -ForegroundColor Red }

Write-Info  "==============================================="
Write-Info  "     YouTube KOL Crawler - PowerShell Runner"
Write-Info  "==============================================="

# ----------- ASCII 进度条 -----------
function Show-AsciiProgress {
  param([int]$Fetched = 0, [int]$Inserted = 0, [datetime]$StartTime)

  $elapsed = [datetime]::UtcNow - $StartTime
  $sec = [math]::Max(1, [int]$elapsed.TotalSeconds)
  $rps = [math]::Round($Fetched / $sec, 2)

  $width = 28
  $tick = ($Fetched % $width)
  $bar = '[' + ('#' * $tick) + ('.' * ($width - $tick)) + ']'
  $line = ("`r{0} fetched={1} inserted={2} rps={3}       " -f $bar, $Fetched, $Inserted, $rps)
  Write-Host $line -NoNewline
}

# ----------- 解析 [stats] 行 -----------
function Parse-StatsLine {
  param([string]$Line)
  if ($Line -match '^\[stats\]\s+fetched=(\d+)\s+inserted=(\d+)(?:\s+channels=(\d+))?(?:\s+errors=(\d+))?(?:\s+api_calls=(\d+))?(?:\s+api_cost=(\d+))?') {
    return @{
      Fetched  = [int]$Matches[1]
      Inserted = [int]$Matches[2]
      Channels = if ($Matches[3]) { [int]$Matches[3] } else { 0 }
      Errors   = if ($Matches[4]) { [int]$Matches[4] } else { 0 }
      ApiCalls = if ($Matches[5]) { [int]$Matches[5] } else { 0 }
      ApiCost  = if ($Matches[6]) { [int]$Matches[6] } else { 0 }
    }
  }
  return $null
}

# ----------- 构建 Python 参数 -----------
$pyArgs = @('main.py')
foreach ($kw in $Keywords) { $pyArgs += $kw }
if ($StartDate)            { $pyArgs += @('--start-date', $StartDate) }
if ($StartYear)            { $pyArgs += @('--start-year', "$StartYear") }
if ($EndDate)              { $pyArgs += @('--end-date',   $EndDate) }
if ($MaxResults)           { $pyArgs += @('--max-results', "$MaxResults") }
if ($ProcessQueue)         { $pyArgs += '--process-queue' }
if ($EstimateOnly)         { $pyArgs += '--estimate-only' }
if ($Status)               { $pyArgs += '--status' }
if ($ResetQuota)           { $pyArgs += '--reset-quota' }
if ($LogLevel)             { $pyArgs += @('--log-level', $LogLevel) }
if ($ShardId -ge 0)        { $pyArgs += @('--shard-id', "$ShardId") }
if ($ShardCount -gt 0)     { $pyArgs += @('--shard-count', "$ShardCount") }

$quotedPy   = Quote-Arg $py
$quotedArgs = ($pyArgs | ForEach-Object { Quote-Arg $_ }) -join ' '
$cmdLine    = "$quotedPy $quotedArgs 2>&1"  # 合并 stderr→stdout

Write-Info  ""
Write-Info  ">>> Running:"
Write-Info  "    $cmdLine"
Write-Info  ""

# ----------- Start-Process + 文件尾随读取 -----------
$startTime = Get-Date
$lastStats = $null

$logsDir   = Join-Path $root 'logs'
$stdoutLog = Join-Path $logsDir 'runner_stdout.log'
New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
"" | Out-File $stdoutLog -Encoding utf8

$proc = Start-Process -FilePath "cmd.exe" `
  -ArgumentList @("/c", $cmdLine) `
  -NoNewWindow -PassThru `
  -RedirectStandardOutput $stdoutLog

Get-Content -Path $stdoutLog -Wait -Tail 0 | ForEach-Object {
  $line = $_.ToString()
  $s = Parse-StatsLine -Line $line
  if ($s) {
    $lastStats = $s
    Show-AsciiProgress -Fetched $s.Fetched -Inserted $s.Inserted -StartTime $startTime
  } elseif ($line -ne '') {
    Write-Host "`r" -NoNewline
    Write-Host $line
  }
}

$proc.WaitForExit()
Write-Host ""

# ----------- 最终统计与退出码 -----------
if ($lastStats) {
  Write-Info  "-----------------------------------------------"
  Write-OK    ("Videos Fetched : {0}" -f $lastStats.Fetched)
  Write-OK    ("Videos Inserted: {0}" -f $lastStats.Inserted)
  if ($lastStats.Channels -gt 0) { Write-Info ("Channels Found  : {0}" -f $lastStats.Channels) }
  if ($lastStats.ApiCalls -gt 0) { Write-Info ("API Calls       : {0}" -f $lastStats.ApiCalls) }
  if ($lastStats.ApiCost  -gt 0) { Write-Info ("API Cost (units): {0}" -f $lastStats.ApiCost) }
  if ($lastStats.Errors   -gt 0) { Write-Warn ("Errors          : {0}" -f $lastStats.Errors) }
}

$elapsed = (Get-Date) - $startTime
Write-Info ("Elapsed: {0:hh\:mm\:ss}" -f $elapsed)

$exit = $proc.ExitCode
if ($exit -ne 0) {
  Write-ErrLine "Python exited with code $exit"
  exit $exit
}

Write-OK "Done."
exit 0
