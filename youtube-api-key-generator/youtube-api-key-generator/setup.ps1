# YouTube API Key Generator - Setup Script
# This script initializes the environment and checks prerequisites

param(
    [switch]$SkipChecks
)

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " YouTube API Key Generator - Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check PowerShell version
Write-Host "[1/5] Checking PowerShell version..." -ForegroundColor Yellow
$psVersion = $PSVersionTable.PSVersion
if ($psVersion.Major -lt 5) {
    Write-Host "✗ PowerShell 5.1 or later is required. Current: $psVersion" -ForegroundColor Red
    exit 1
}
Write-Host "✓ PowerShell $psVersion" -ForegroundColor Green

# Check Google Cloud SDK
Write-Host "[2/5] Checking Google Cloud SDK..." -ForegroundColor Yellow
if (-not $SkipChecks) {
    try {
        $gcloudVersion = gcloud --version 2>&1 | Select-Object -First 1
        Write-Host "✓ $gcloudVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Google Cloud SDK not found" -ForegroundColor Red
        Write-Host "  Download from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
        exit 1
    }

    # Check authentication
    Write-Host "[3/5] Checking Google Cloud authentication..." -ForegroundColor Yellow
    try {
        $authAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
        if ($authAccount) {
            Write-Host "✓ Authenticated as: $authAccount" -ForegroundColor Green
        }
        else {
            Write-Host "✗ Not authenticated" -ForegroundColor Red
            Write-Host "  Run: gcloud auth login" -ForegroundColor Yellow
            exit 1
        }
    }
    catch {
        Write-Host "✗ Authentication check failed" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "⊘ Skipping Google Cloud SDK check" -ForegroundColor Gray
    Write-Host "⊘ Skipping authentication check" -ForegroundColor Gray
}

# Create directory structure
Write-Host "[4/5] Creating directory structure..." -ForegroundColor Yellow
$directories = @("output", "logs", "temp")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✓ Created: $dir/" -ForegroundColor Green
    }
    else {
        Write-Host "✓ Exists: $dir/" -ForegroundColor Green
    }
}

# Create config file if not exists
Write-Host "[5/5] Creating configuration file..." -ForegroundColor Yellow
$configPath = "config.json"
if (-not (Test-Path $configPath)) {
    $config = @{
        projectPrefix     = "yt-api"
        billingAccount    = ""
        organization      = ""
        outputFormats     = @("txt", "json")
        enableLogging     = $true
        cleanupTempFiles  = $true
    }
    $config | ConvertTo-Json | Set-Content $configPath -Encoding UTF8
    Write-Host "✓ Created: $configPath" -ForegroundColor Green
    Write-Host "  Edit this file to customize settings" -ForegroundColor Gray
}
else {
    Write-Host "✓ Exists: $configPath" -ForegroundColor Green
}

# Create .gitignore
$gitignorePath = ".gitignore"
if (-not (Test-Path $gitignorePath)) {
    @"
output/
logs/
temp/
config.json
*.log
"@ | Set-Content $gitignorePath -Encoding UTF8
    Write-Host "✓ Created: $gitignorePath" -ForegroundColor Green
}

# Create batch file for easy launching
$batchContent = @"
@echo off
cd /d "%~dp0"
powershell.exe -ExecutionPolicy Bypass -File "%~dp0gui.ps1"
pause
"@
$batchPath = "YouTube-API-Key-Generator.bat"
$batchContent | Set-Content $batchPath -Encoding ASCII
Write-Host "✓ Created: $batchPath" -ForegroundColor Green

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit config.json to add your billing account (optional)" -ForegroundColor White
Write-Host "2. Run: .\gui.ps1" -ForegroundColor White
Write-Host "   Or double-click: YouTube-API-Key-Generator.bat" -ForegroundColor White
Write-Host ""
