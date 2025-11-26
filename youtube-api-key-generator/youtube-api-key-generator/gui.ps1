# YouTube API Key Generator - High Resolution GUI
# Modern Windows Forms interface with dark theme

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
[DPI]::SetProcessDPIAware() | Out-Null

# Color scheme
$colorPrimary = [System.Drawing.Color]::FromArgb(78, 205, 196)  # Teal
$colorSuccess = [System.Drawing.Color]::FromArgb(85, 239, 196)  # Green
$colorWarning = [System.Drawing.Color]::FromArgb(255, 234, 167) # Yellow
$colorError = [System.Drawing.Color]::FromArgb(255, 118, 117)   # Red
$colorBackground = [System.Drawing.Color]::FromArgb(30, 30, 40)
$colorSurface = [System.Drawing.Color]::FromArgb(40, 44, 52)
$colorText = [System.Drawing.Color]::FromArgb(255, 255, 255)
$colorTextDim = [System.Drawing.Color]::FromArgb(150, 150, 150)

# Global state
$script:isGenerating = $false
$script:generatedKeys = @()

# Create main form
$form = New-Object System.Windows.Forms.Form
$form.Text = "YouTube API Key Generator"
$form.Size = New-Object System.Drawing.Size(1200, 800)
$form.StartPosition = "CenterScreen"
$form.BackColor = $colorBackground
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false
$form.Font = New-Object System.Drawing.Font("Segoe UI", 10)

# Title Label
$labelTitle = New-Object System.Windows.Forms.Label
$labelTitle.Text = "YouTube API Key Batch Generator"
$labelTitle.Location = New-Object System.Drawing.Point(30, 20)
$labelTitle.Size = New-Object System.Drawing.Size(600, 40)
$labelTitle.Font = New-Object System.Drawing.Font("Segoe UI", 24, [System.Drawing.FontStyle]::Bold)
$labelTitle.ForeColor = $colorPrimary
$form.Controls.Add($labelTitle)

# Subtitle Label
$labelSubtitle = New-Object System.Windows.Forms.Label
$labelSubtitle.Text = "Generate multiple YouTube Data API v3 keys in batch"
$labelSubtitle.Location = New-Object System.Drawing.Point(30, 70)
$labelSubtitle.Size = New-Object System.Drawing.Size(600, 25)
$labelSubtitle.Font = New-Object System.Drawing.Font("Segoe UI", 11)
$labelSubtitle.ForeColor = $colorTextDim
$form.Controls.Add($labelSubtitle)

# Number Selection Panel
$panelNumber = New-Object System.Windows.Forms.Panel
$panelNumber.Location = New-Object System.Drawing.Point(30, 120)
$panelNumber.Size = New-Object System.Drawing.Size(550, 120)
$panelNumber.BackColor = $colorSurface
$panelNumber.BorderStyle = "FixedSingle"
$form.Controls.Add($panelNumber)

$labelCount = New-Object System.Windows.Forms.Label
$labelCount.Text = "Number of Keys to Generate:"
$labelCount.Location = New-Object System.Drawing.Point(20, 15)
$labelCount.Size = New-Object System.Drawing.Size(250, 25)
$labelCount.ForeColor = $colorText
$panelNumber.Controls.Add($labelCount)

$numericCount = New-Object System.Windows.Forms.NumericUpDown
$numericCount.Location = New-Object System.Drawing.Point(280, 12)
$numericCount.Size = New-Object System.Drawing.Size(100, 30)
$numericCount.Minimum = 1
$numericCount.Maximum = 20
$numericCount.Value = 5
$numericCount.BackColor = $colorBackground
$numericCount.ForeColor = $colorText
$panelNumber.Controls.Add($numericCount)

$sliderCount = New-Object System.Windows.Forms.TrackBar
$sliderCount.Location = New-Object System.Drawing.Point(20, 50)
$sliderCount.Size = New-Object System.Drawing.Size(510, 50)
$sliderCount.Minimum = 1
$sliderCount.Maximum = 20
$sliderCount.Value = 5
$sliderCount.TickFrequency = 1
$sliderCount.BackColor = $colorSurface
$sliderCount.Add_ValueChanged({
    $numericCount.Value = $sliderCount.Value
})
$panelNumber.Controls.Add($sliderCount)

$numericCount.Add_ValueChanged({
    $sliderCount.Value = $numericCount.Value
})

# Start Button
$btnStart = New-Object System.Windows.Forms.Button
$btnStart.Text = "Start Generation"
$btnStart.Location = New-Object System.Drawing.Point(600, 120)
$btnStart.Size = New-Object System.Drawing.Size(200, 50)
$btnStart.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
$btnStart.BackColor = $colorPrimary
$btnStart.ForeColor = $colorBackground
$btnStart.FlatStyle = "Flat"
$btnStart.FlatAppearance.BorderSize = 0
$btnStart.Cursor = "Hand"
$btnStart.Add_Click({
    if (-not $script:isGenerating) {
        Start-Generation
    }
})
$form.Controls.Add($btnStart)

# Stop Button
$btnStop = New-Object System.Windows.Forms.Button
$btnStop.Text = "Stop"
$btnStop.Location = New-Object System.Drawing.Point(820, 120)
$btnStop.Size = New-Object System.Drawing.Size(100, 50)
$btnStop.Font = New-Object System.Drawing.Font("Segoe UI", 11)
$btnStop.BackColor = $colorError
$btnStop.ForeColor = $colorText
$btnStop.FlatStyle = "Flat"
$btnStop.FlatAppearance.BorderSize = 0
$btnStop.Enabled = $false
$btnStop.Cursor = "Hand"
$form.Controls.Add($btnStop)

# Progress Bar
$progressBar = New-Object System.Windows.Forms.ProgressBar
$progressBar.Location = New-Object System.Drawing.Point(30, 260)
$progressBar.Size = New-Object System.Drawing.Size(1140, 30)
$progressBar.Style = "Continuous"
$progressBar.ForeColor = $colorPrimary
$form.Controls.Add($progressBar)

$labelProgress = New-Object System.Windows.Forms.Label
$labelProgress.Text = "Ready to generate API keys"
$labelProgress.Location = New-Object System.Drawing.Point(30, 300)
$labelProgress.Size = New-Object System.Drawing.Size(1140, 25)
$labelProgress.ForeColor = $colorTextDim
$labelProgress.Font = New-Object System.Drawing.Font("Segoe UI", 10)
$form.Controls.Add($labelProgress)

# Tab Control
$tabControl = New-Object System.Windows.Forms.TabControl
$tabControl.Location = New-Object System.Drawing.Point(30, 340)
$tabControl.Size = New-Object System.Drawing.Size(1140, 390)
$tabControl.Font = New-Object System.Drawing.Font("Segoe UI", 10)
$form.Controls.Add($tabControl)

# Log Tab
$tabLogs = New-Object System.Windows.Forms.TabPage
$tabLogs.Text = "Generation Log"
$tabLogs.BackColor = $colorBackground
$tabControl.Controls.Add($tabLogs)

$textBoxLog = New-Object System.Windows.Forms.RichTextBox
$textBoxLog.Location = New-Object System.Drawing.Point(10, 10)
$textBoxLog.Size = New-Object System.Drawing.Size(1100, 330)
$textBoxLog.Font = New-Object System.Drawing.Font("Consolas", 9)
$textBoxLog.BackColor = $colorSurface
$textBoxLog.ForeColor = $colorText
$textBoxLog.ReadOnly = $true
$textBoxLog.ScrollBars = "Vertical"
$tabLogs.Controls.Add($textBoxLog)

# Keys Tab
$tabKeys = New-Object System.Windows.Forms.TabPage
$tabKeys.Text = "Generated Keys"
$tabKeys.BackColor = $colorBackground
$tabControl.Controls.Add($tabKeys)

$listBoxKeys = New-Object System.Windows.Forms.ListBox
$listBoxKeys.Location = New-Object System.Drawing.Point(10, 10)
$listBoxKeys.Size = New-Object System.Drawing.Size(1100, 280)
$listBoxKeys.Font = New-Object System.Drawing.Font("Consolas", 10)
$listBoxKeys.BackColor = $colorSurface
$listBoxKeys.ForeColor = $colorText
$listBoxKeys.BorderStyle = "FixedSingle"
$tabKeys.Controls.Add($listBoxKeys)

$btnCopyAll = New-Object System.Windows.Forms.Button
$btnCopyAll.Text = "Copy All Keys"
$btnCopyAll.Location = New-Object System.Drawing.Point(10, 300)
$btnCopyAll.Size = New-Object System.Drawing.Size(150, 35)
$btnCopyAll.BackColor = $colorPrimary
$btnCopyAll.ForeColor = $colorBackground
$btnCopyAll.FlatStyle = "Flat"
$btnCopyAll.Add_Click({
    if ($script:generatedKeys.Count -gt 0) {
        $keysText = $script:generatedKeys -join "`r`n"
        [System.Windows.Forms.Clipboard]::SetText($keysText)
        Add-Log "Copied $($script:generatedKeys.Count) keys to clipboard" "Success"
    }
})
$tabKeys.Controls.Add($btnCopyAll)

$btnExport = New-Object System.Windows.Forms.Button
$btnExport.Text = "Export to File"
$btnExport.Location = New-Object System.Drawing.Point(170, 300)
$btnExport.Size = New-Object System.Drawing.Size(150, 35)
$btnExport.BackColor = $colorPrimary
$btnExport.ForeColor = $colorBackground
$btnExport.FlatStyle = "Flat"
$btnExport.Add_Click({
    if ($script:generatedKeys.Count -gt 0) {
        $outputDir = Join-Path $PSScriptRoot "output"
        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $filePath = Join-Path $outputDir "api-keys-$timestamp.txt"
        $script:generatedKeys | Set-Content $filePath -Encoding UTF8
        Add-Log "Exported to: $filePath" "Success"
        [System.Windows.Forms.MessageBox]::Show("Keys exported to:`n$filePath", "Export Successful", "OK", "Information")
    }
})
$tabKeys.Controls.Add($btnExport)

# Functions
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
}

function Start-Generation {
    $script:isGenerating = $true
    $btnStart.Enabled = $false
    $btnStop.Enabled = $true
    $numericCount.Enabled = $false
    $sliderCount.Enabled = $false
    $script:generatedKeys = @()
    $listBoxKeys.Items.Clear()
    $textBoxLog.Clear()
    
    $count = [int]$numericCount.Value
    $progressBar.Maximum = $count
    $progressBar.Value = 0
    
    Add-Log "Starting generation of $count API keys..." "Info"
    Add-Log "This will take approximately $($count * 60) seconds" "Info"
    
    # Create progress callback
    $progressCallback = {
        param($data)
        
        switch ($data.Type) {
            "Log" {
                Add-Log $data.Message $data.Level
            }
            "Progress" {
                $progressBar.Value = $data.Current
                $labelProgress.Text = "$($data.Current)/$($data.Total) - $($data.Status)"
            }
            "KeyGenerated" {
                $script:generatedKeys += $data.ApiKey
                $listBoxKeys.Items.Add($data.ApiKey)
            }
        }
    }
    
    # Run generation in background
    $runspace = [runspacefactory]::CreateRunspace()
    $runspace.Open()
    $runspace.SessionStateProxy.SetVariable("PSScriptRoot", $PSScriptRoot)
    $runspace.SessionStateProxy.SetVariable("count", $count)
    $runspace.SessionStateProxy.SetVariable("progressCallback", $progressCallback)
    
    $powershell = [powershell]::Create()
    $powershell.Runspace = $runspace
    
    $powershell.AddScript({
        $generateScript = Join-Path $PSScriptRoot "generate-keys.ps1"
        . $generateScript -Count $count -ProgressCallback $progressCallback
    }) | Out-Null
    
    $handle = $powershell.BeginInvoke()
    
    # Monitor completion
    $timer = New-Object System.Windows.Forms.Timer
    $timer.Interval = 500
    $timer.Add_Tick({
        if ($handle.IsCompleted) {
            $timer.Stop()
            $results = $powershell.EndInvoke($handle)
            $powershell.Dispose()
            $runspace.Close()
            
            Add-Log "Generation complete!" "Success"
            Add-Log "Successfully generated: $($script:generatedKeys.Count) keys" "Success"
            
            $progressBar.Value = $progressBar.Maximum
            $labelProgress.Text = "Complete - Generated $($script:generatedKeys.Count) keys"
            
            $script:isGenerating = $false
            $btnStart.Enabled = $true
            $btnStop.Enabled = $false
            $numericCount.Enabled = $true
            $sliderCount.Enabled = $true
            
            $tabControl.SelectedTab = $tabKeys
        }
    })
    $timer.Start()
}

# Show form
Add-Log "Ready to generate API keys" "Info"
Add-Log "Select number of keys (1-20) and click Start Generation" "Info"
$form.Add_Shown({$form.Activate()})
[void]$form.ShowDialog()
