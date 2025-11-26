# YouTube API Key Generator - Core Logic
# This script handles the batch generation of YouTube API keys

param(
    [Parameter(Mandatory = $true)]
    [int]$Count,
    
    [string]$Prefix = "yt-api",
    
    [string]$BillingAccount = "",
    
    [scriptblock]$ProgressCallback = $null,
    
    [switch]$NoGUI
)

$ErrorActionPreference = "Continue"

# Load configuration
$configPath = Join-Path $PSScriptRoot "config.json"
if (Test-Path $configPath) {
    $config = Get-Content $configPath -Encoding UTF8 | ConvertFrom-Json
    if (-not $Prefix) { $Prefix = $config.projectPrefix }
    if (-not $BillingAccount) { $BillingAccount = $config.billingAccount }
}

# Initialize results
$script:results = @{
    Success      = @()
    Failed       = @()
    TotalAttempted = 0
    StartTime    = Get-Date
}

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("Info", "Success", "Warning", "Error")]
        [string]$Level = "Info"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    # Write to console with colors
    $color = switch ($Level) {
        "Success" { "Green" }
        "Warning" { "Yellow" }
        "Error" { "Red" }
        default { "White" }
    }
    
    if ($NoGUI) {
        Write-Host $logMessage -ForegroundColor $color
    }
    
    # Write to log file if enabled
    if ($config.enableLogging) {
        $logDir = Join-Path $PSScriptRoot "logs"
        $logFile = Join-Path $logDir "generation-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
        Add-Content -Path $logFile -Value $logMessage -Encoding UTF8
    }
    
    # Send to progress callback
    if ($ProgressCallback) {
        & $ProgressCallback @{
            Type    = "Log"
            Level   = $Level
            Message = $Message
        }
    }
}

function New-GcpProject {
    param(
        [string]$ProjectId
    )
    
    Write-Log "Creating project: $ProjectId" -Level Info
    
    try {
        # Create project
        $createOutput = gcloud projects create $ProjectId --format=json 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            throw "Project creation failed: $createOutput"
        }
        
        Write-Log "Project created successfully" -Level Success
        
        # Link billing account if provided
        if ($BillingAccount) {
            Write-Log "Linking billing account..." -Level Info
            gcloud billing projects link $ProjectId --billing-account=$BillingAccount 2>&1 | Out-Null
            
            if ($LASTEXITCODE -ne 0) {
                Write-Log "Warning: Failed to link billing account" -Level Warning
            }
            else {
                Write-Log "Billing account linked" -Level Success
            }
        }
        
        return $true
    }
    catch {
        Write-Log "Failed to create project: $_" -Level Error
        return $false
    }
}

function Enable-YoutubeApi {
    param(
        [string]$ProjectId
    )
    
    Write-Log "Enabling YouTube Data API v3..." -Level Info
    
    try {
        # Enable API
        gcloud services enable youtube.googleapis.com --project=$ProjectId 2>&1 | Out-Null
        
        if ($LASTEXITCODE -ne 0) {
            throw "API enablement failed"
        }
        
        Write-Log "API enabled successfully" -Level Success
        
        # Wait for propagation
        Write-Log "Waiting for API propagation (30s)..." -Level Info
        Start-Sleep -Seconds 30
        
        return $true
    }
    catch {
        Write-Log "Failed to enable API: $_" -Level Error
        return $false
    }
}

function New-ApiKey {
    param(
        [string]$ProjectId
    )
    
    Write-Log "Creating API key..." -Level Info
    
    try {
        # Create API key
        $keyOutput = gcloud alpha services api-keys create --project=$ProjectId --display-name="YouTube-API-Key" --format=json 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            # Fallback: Try using projects API
            Write-Log "Trying alternative key creation method..." -Level Warning
            
            # Get project number
            $projectInfo = gcloud projects describe $ProjectId --format=json | ConvertFrom-Json
            $projectNumber = $projectInfo.projectNumber
            
            # This is a placeholder - actual implementation would use REST API
            throw "API key creation requires manual setup in GCP Console"
        }
        
        $keyData = $keyOutput | ConvertFrom-Json
        $apiKey = $keyData.response.keyString
        
        if (-not $apiKey) {
            throw "No API key returned"
        }
        
        Write-Log "API key created: $($apiKey.Substring(0, 20))..." -Level Success
        
        return $apiKey
    }
    catch {
        Write-Log "Failed to create API key: $_" -Level Error
        return $null
    }
}

function Start-KeyGeneration {
    Write-Log "Starting batch generation of $Count keys" -Level Info
    Write-Log "Project prefix: $Prefix" -Level Info
    
    for ($i = 1; $i -le $Count; $i++) {
        $script:results.TotalAttempted++
        
        # Generate unique project ID
        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $random = -join ((65..90) + (97..122) | Get-Random -Count 6 | ForEach-Object { [char]$_ })
        $projectId = "$Prefix-$timestamp-$random".ToLower()
        
        Write-Log "[$i/$Count] Processing: $projectId" -Level Info
        
        # Update progress
        if ($ProgressCallback) {
            & $ProgressCallback @{
                Type     = "Progress"
                Current  = $i
                Total    = $Count
                Status   = "Creating project $projectId"
            }
        }
        
        # Create project
        $projectCreated = New-GcpProject -ProjectId $projectId
        if (-not $projectCreated) {
            $script:results.Failed += @{
                ProjectId = $projectId
                Step      = "Project Creation"
                Error     = "Failed to create project"
            }
            continue
        }
        
        # Enable API
        $apiEnabled = Enable-YoutubeApi -ProjectId $projectId
        if (-not $apiEnabled) {
            $script:results.Failed += @{
                ProjectId = $projectId
                Step      = "API Enablement"
                Error     = "Failed to enable API"
            }
            continue
        }
        
        # Create API key
        $apiKey = New-ApiKey -ProjectId $projectId
        if (-not $apiKey) {
            $script:results.Failed += @{
                ProjectId = $projectId
                Step      = "Key Creation"
                Error     = "Failed to create API key"
            }
            continue
        }
        
        # Success!
        $script:results.Success += @{
            ApiKey    = $apiKey
            ProjectId = $projectId
            CreatedAt = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
        }
        
        Write-Log "[$i/$Count] Success! Key generated" -Level Success
        
        # Notify callback
        if ($ProgressCallback) {
            & $ProgressCallback @{
                Type   = "KeyGenerated"
                ApiKey = $apiKey
                ProjectId = $projectId
            }
        }
        
        # Small delay between iterations
        if ($i -lt $Count) {
            Start-Sleep -Seconds 2
        }
    }
    
    # Generate summary
    $script:results.EndTime = Get-Date
    $duration = ($script:results.EndTime - $script:results.StartTime).TotalSeconds
    
    Write-Log "Generation complete!" -Level Success
    Write-Log "Successful: $($script:results.Success.Count)" -Level Success
    Write-Log "Failed: $($script:results.Failed.Count)" -Level Warning
    Write-Log "Duration: $([math]::Round($duration, 2))s" -Level Info
    
    # Save results
    Export-Results
    
    return $script:results
}

function Export-Results {
    $outputDir = Join-Path $PSScriptRoot "output"
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    
    # Export to TXT
    if ($config.outputFormats -contains "txt") {
        $txtFile = Join-Path $outputDir "api-keys-$timestamp.txt"
        $script:results.Success | ForEach-Object { $_.ApiKey } | Set-Content $txtFile -Encoding UTF8
        Write-Log "Exported to: $txtFile" -Level Success
    }
    
    # Export to JSON
    if ($config.outputFormats -contains "json") {
        $jsonFile = Join-Path $outputDir "api-keys-$timestamp.json"
        $exportData = @{
            generated_at = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
            total_keys   = $script:results.Success.Count
            keys         = $script:results.Success
        }
        $exportData | ConvertTo-Json -Depth 10 | Set-Content $jsonFile -Encoding UTF8
        Write-Log "Exported to: $jsonFile" -Level Success
    }
}

# Main execution
if ($MyInvocation.InvocationName -ne '.') {
    Start-KeyGeneration
}
