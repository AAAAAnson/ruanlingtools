# YouTube API Key Generator - Simplified GUI (Fixed Version)
# This version uses synchronous execution with UI updates

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Enable High DPI support
Add-Type @"
using System.Runtime.InteropServices;
public class DPI {
    [DllImport("user32.dll")]
    public static extern bool SetProcessDPIAware();
}
"@
[void][DPI]::SetProcessDPIAware()

# Color scheme
$colorPrimary = [System.Drawing.Color]::FromArgb(78, 205, 196)
$colorSuccess = [System.Drawing.Color]::FromArgb(85, 239, 196)
$colorWarning = [System.Drawing.Color]::FromArgb(255, 234, 167)
$colorError = [System.Drawing.Color]::FromArgb(255, 118, 117)
$colorBackground = [System.Drawing.Color]::FromArgb(30, 30, 40)
$colorSurface = [System.Drawing.Color]::FromArgb(40, 44, 52)
$colorText = [System.Drawing.Color]::FromArgb(255, 255, 255)
$colorTextDim = [System.Drawing.Color]::FromArgb(150, 150, 150)

# Global state
$script:isGenerating = $false
$script:generatedKeys = @()

# Create main form
$form = New-Object System.Windows.Forms.Form
$form.Text = "YouTube API Key Generator (Fixed)"
$form.Size = New-Object System.Drawing.Size(1000, 700)
$form.StartPosition = "CenterScreen"
$form.BackColor = $colorBackground
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false
$form.Font = New-Object System.Drawing.Font("Segoe UI", 10)

# Title Label
$labelTitle = New-Object System.Windows.Forms.Label
$labelTitle.Text = "YouTube API Key Generator"
$labelTitle.Location = New-Object System.Drawing.Point(30, 20)
$labelTitle.Size = New-Object System.Drawing.Size(500, 35)
$labelTitle.Font = New-Object System.Drawing.Font("Segoe UI", 20, [System.Drawing.FontStyle]::Bold)
$labelTitle.ForeColor = $colorPrimary
$form.Controls.Add($labelTitle)

# Number input
$labelCount = New-Object System.Windows.Forms.Label
$labelCount.Text = "Number of Keys (1-20):"
$labelCount.Location = New-Object System.Drawing.Point(30, 70)
$labelCount.Size = New-Object System.Drawing.Size(200, 25)
$labelCount.ForeColor = $colorText
$form.Controls.Add($labelCount)

$numericCount = New-Object System.Windows.Forms.NumericUpDown
$numericCount.Location = New-Object System.Drawing.Point(240, 68)
$numericCount.Size = New-Object System.Drawing.Size(100, 30)
$numericCount.Minimum = 1
$numericCount.Maximum = 20
$numericCount.Value = 5
$numericCount.BackColor = $colorSurface
$numericCount.ForeColor = $colorText
$form.Controls.Add($numericCount)

# Start Button
$btnStart = New-Object System.Windows.Forms.Button
$btnStart.Text = "Start Generation"
$btnStart.Location = New-Object System.Drawing.Point(360, 65)
$btnStart.Size = New-Object System.Drawing.Size(150, 35)
$btnStart.BackColor = $colorPrimary
$btnStart.ForeColor = $colorBackground
$btnStart.FlatStyle = "Flat"
$btnStart.Font = New-Object System.Drawing.Font("Segoe UI", 11, [System.Drawing.FontStyle]::Bold)
$form.Controls.Add($btnStart)

# Progress Bar
$progressBar = New-Object System.Windows.Forms.ProgressBar
$progressBar.Location = New-Object System.Drawing.Point(30, 120)
$progressBar.Size = New-Object System.Drawing.Size(930, 25)
$progressBar.Style = "Continuous"
$form.Controls.Add($progressBar)

# Status Label
$labelStatus = New-Object System.Windows.Forms.Label
$labelStatus.Text = "Ready. Click 'Start Generation' to begin."
$labelStatus.Location = New-Object System.Drawing.Point(30, 150)
$labelStatus.Size = New-Object System.Drawing.Size(930, 25)
$labelStatus.ForeColor = $colorTextDim
$form.Controls.Add($labelStatus)

# Log Text Box
$labelLog = New-Object System.Windows.Forms.Label
$labelLog.Text = "Generation Log:"
$labelLog.Location = New-Object System.Drawing.Point(30, 185)
$labelLog.Size = New-Object System.Drawing.Size(200, 25)
$labelLog.ForeColor = $colorText
$labelLog.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$form.Controls.Add($labelLog)

$textBoxLog = New-Object System.Windows.Forms.RichTextBox
$textBoxLog.Location = New-Object System.Drawing.Point(30, 215)
$textBoxLog.Size = New-Object System.Drawing.Size(930, 420)
$textBoxLog.BackColor = $colorSurface
$textBoxLog.ForeColor = $colorText
$textBoxLog.ReadOnly = $true
$textBoxLog.Font = New-Object System.Drawing.Font("Consolas", 9)
$textBoxLog.ScrollBars = "Vertical"
$form.Controls.Add($textBoxLog)

# Helper function to add log
function Add-Log {
    param(
        [string]$Message,
        [string]$Level = "Info"
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    $logLine = "[$timestamp] $Message"
    
    $textBoxLog.SelectionStart = $textBoxLog.TextLength
    $textBoxLog.SelectionLength = 0
    
    switch ($Level) {
        "Success" { $textBoxLog.SelectionColor = $colorSuccess }
        "Warning" { $textBoxLog.SelectionColor = $colorWarning }
        "Error" { $textBoxLog.SelectionColor = $colorError }
        default { $textBoxLog.SelectionColor = $colorText }
    }
    
    $textBoxLog.AppendText("$logLine`n")
    $textBoxLog.ScrollToCaret()
    $form.Refresh()
    [System.Windows.Forms.Application]::DoEvents()
}

# Test gcloud command
function Test-GcloudAvailable {
    try {
        $null = gcloud --version 2>&1
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

# Simplified key generation (inline, no external script dependency)
function Start-KeyGeneration {
    param([int]$Count)
    
    $btnStart.Enabled = $false
    $numericCount.Enabled = $false
    $script:isGenerating = $true
    
    $progressBar.Maximum = $Count
    $progressBar.Value = 0
    
    Add-Log "========================================" "Info"
    Add-Log "Starting generation of $Count API keys" "Info"
    Add-Log "========================================" "Info"
    
    # Check gcloud
    Add-Log "Checking Google Cloud SDK..." "Info"
    if (-not (Test-GcloudAvailable)) {
        Add-Log "ERROR: Google Cloud SDK not found!" "Error"
        Add-Log "Please install from: https://cloud.google.com/sdk/docs/install" "Error"
        $btnStart.Enabled = $true
        $numericCount.Enabled = $true
        $script:isGenerating = $false
        return
    }
    Add-Log "✓ Google Cloud SDK detected" "Success"
    
    $script:generatedKeys = @()
    $successCount = 0
    $failCount = 0
    
    for ($i = 1; $i -le $Count; $i++) {
        Add-Log "" "Info"
        Add-Log "Processing key $i of $Count..." "Info"
        $labelStatus.Text = "Processing key $i of $Count..."
        [System.Windows.Forms.Application]::DoEvents()
        
        # Generate unique project ID
        $timestamp = Get-Date -Format "yyyyMMddHHmmss"
        $random = -join ((65..90) + (97..122) | Get-Random -Count 6 | ForEach-Object { [char]$_ })
        $projectId = "yt-api-$timestamp-$random".ToLower()
        
        Add-Log "  Project ID: $projectId" "Info"
        
        # DEMO MODE: Simulate for testing
        # Remove this block and uncomment gcloud commands below for production
        Add-Log "  [DEMO MODE] Simulating project creation..." "Warning"
        Start-Sleep -Seconds 2
        Add-Log "  [DEMO MODE] Project created successfully" "Success"
        
        Add-Log "  [DEMO MODE] Simulating API enablement..." "Warning"
        Start-Sleep -Seconds 2
        Add-Log "  [DEMO MODE] YouTube Data API v3 enabled" "Success"
        
        $demoKey = "AIzaSy" + (-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 33 | ForEach-Object { [char]$_ }))
        Add-Log "  [DEMO MODE] Generated key: $demoKey" "Success"
        
        $script:generatedKeys += $demoKey
        $successCount++
        
        # Update progress
        $progressBar.Value = $i
        [System.Windows.Forms.Application]::DoEvents()
        
        <#
        # PRODUCTION CODE (uncomment for real generation):
        try {
            # Create project
            Add-Log "  Creating GCP project..." "Info"
            $createOutput = gcloud projects create $projectId --format=json 2>&1
            if ($LASTEXITCODE -ne 0) {
                throw "Project creation failed"
            }
            Add-Log "  ✓ Project created" "Success"
            
            # Enable YouTube API
            Add-Log "  Enabling YouTube Data API v3..." "Info"
            gcloud services enable youtube.googleapis.com --project=$projectId 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                throw "API enablement failed"
            }
            Add-Log "  ✓ API enabled" "Success"
            
            # Wait for propagation
            Add-Log "  Waiting for propagation (30s)..." "Info"
            Start-Sleep -Seconds 30
            
            # Create API key (this requires gcloud alpha)
            Add-Log "  Creating API key..." "Info"
            $keyOutput = gcloud alpha services api-keys create --project=$projectId --display-name="YouTube-API-Key" --format=json 2>&1
            if ($LASTEXITCODE -ne 0) {
                throw "API key creation failed"
            }
            
            $keyData = $keyOutput | ConvertFrom-Json
            $apiKey = $keyData.response.keyString
            
            if ($apiKey) {
                Add-Log "  ✓ Key generated: $apiKey" "Success"
                $script:generatedKeys += $apiKey
                $successCount++
            } else {
                throw "No API key returned"
            }
            
            $progressBar.Value = $i
            [System.Windows.Forms.Application]::DoEvents()
        }
        catch {
            Add-Log "  ✗ Failed: $_" "Error"
            $failCount++
        }
        #>
    }
    
    # Summary
    Add-Log "" "Info"
    Add-Log "========================================" "Info"
    Add-Log "Generation Complete!" "Success"
    Add-Log "Successful: $successCount" "Success"
    Add-Log "Failed: $failCount" "$(if($failCount -gt 0){'Error'}else{'Info'})"
    Add-Log "========================================" "Info"
    
    if ($script:generatedKeys.Count -gt 0) {
        Add-Log "" "Info"
        Add-Log "Generated Keys:" "Success"
        foreach ($key in $script:generatedKeys) {
            Add-Log "  $key" "Success"
        }
        
        # Save to file
        $outputDir = Join-Path $PSScriptRoot "output"
        if (-not (Test-Path $outputDir)) {
            New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
        }
        
        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $outputFile = Join-Path $outputDir "api-keys-$timestamp.txt"
        $script:generatedKeys | Set-Content $outputFile -Encoding UTF8
        
        Add-Log "" "Info"
        Add-Log "Keys saved to: $outputFile" "Success"
        
        # Open output folder
        Start-Process explorer.exe -ArgumentList $outputDir
    }
    
    $labelStatus.Text = "Complete! Generated $successCount keys."
    $btnStart.Enabled = $true
    $numericCount.Enabled = $true
    $script:isGenerating = $false
}

# Button click event
$btnStart.Add_Click({
    if (-not $script:isGenerating) {
        $count = [int]$numericCount.Value
        Start-KeyGeneration -Count $count
    }
})

# Initial log
Add-Log "YouTube API Key Generator Ready" "Info"
Add-Log "Select number of keys and click 'Start Generation'" "Info"
Add-Log "" "Info"
Add-Log "NOTE: Currently in DEMO MODE" "Warning"
Add-Log "Edit gui-fixed.ps1 to enable production mode" "Warning"

# Show form
[void]$form.ShowDialog()
