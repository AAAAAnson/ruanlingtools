# Soft Collar Toolbox 2.0 - PowerShell Deployment Script
# Compatible with Windows PowerShell 5.1+ and PowerShell Core 7+

param(
    [Parameter(Position=0)]
    [ValidateSet('deploy', 'start', 'stop', 'restart', 'status', 'logs', 'clean', 'update', 'health', 'help')]
    [string]$Command = 'help',

    [Parameter(Position=1)]
    [string]$Service = ''
)

# Set error action preference
$ErrorActionPreference = 'Stop'

# Color output functions
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = 'White'
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✓ $Message" 'Green'
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "✗ $Message" 'Red'
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠ $Message" 'Yellow'
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ $Message" 'Cyan'
}

function Write-Header {
    Write-ColorOutput "========================================" 'Cyan'
    Write-ColorOutput "  Soft Collar Toolbox 2.0" 'Cyan'
    Write-ColorOutput "========================================" 'Cyan'
}

# Check if Docker is installed and running
function Test-Docker {
    try {
        $null = docker --version
        $null = docker ps
        return $true
    }
    catch {
        Write-Error "Docker is not installed or not running"
        Write-Info "Please install Docker Desktop for Windows from:"
        Write-Info "https://www.docker.com/products/docker-desktop"
        exit 1
    }
}

# Check if docker-compose is available
function Test-DockerCompose {
    try {
        # Try docker compose (V2)
        $null = docker compose version 2>$null
        return 'docker compose'
    }
    catch {
        try {
            # Try docker-compose (V1)
            $null = docker-compose --version
            return 'docker-compose'
        }
        catch {
            Write-Error "Docker Compose is not available"
            Write-Info "Please install Docker Compose"
            exit 1
        }
    }
}

# Check if .env file exists
function Test-EnvFile {
    if (-not (Test-Path ".env")) {
        Write-Warning ".env file not found"
        Write-Info "Creating .env from .env.example..."

        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-Success ".env file created"
            Write-Warning "Please edit .env file with your configuration before deploying"
            exit 0
        }
        else {
            Write-Error ".env.example not found"
            exit 1
        }
    }
}

# Get docker-compose command
$script:DockerComposeCmd = Test-DockerCompose

# Deploy function
function Invoke-Deploy {
    Write-Header
    Write-Info "Starting deployment..."

    Test-Docker
    Test-EnvFile

    Write-Info "Building Docker images..."
    & $script:DockerComposeCmd.Split() build --no-cache

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Build failed"
        exit 1
    }

    Write-Info "Starting containers..."
    & $script:DockerComposeCmd.Split() up -d

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Deployment complete!"
        Write-Info "Application is running on http://localhost:8888"
        Write-Info "API documentation: http://localhost:8888/docs"
    }
    else {
        Write-Error "Deployment failed"
        exit 1
    }
}

# Start function
function Invoke-Start {
    Write-Header
    Write-Info "Starting containers..."

    Test-Docker
    Test-EnvFile

    & $script:DockerComposeCmd.Split() up -d

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Containers started!"
        Invoke-Status
    }
}

# Stop function
function Invoke-Stop {
    Write-Header
    Write-Info "Stopping containers..."

    Test-Docker
    & $script:DockerComposeCmd.Split() stop

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Containers stopped!"
    }
}

# Restart function
function Invoke-Restart {
    Write-Header
    Write-Info "Restarting containers..."

    Test-Docker
    & $script:DockerComposeCmd.Split() restart

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Containers restarted!"
        Invoke-Status
    }
}

# Status function
function Invoke-Status {
    Write-Header
    Write-Info "Container status:"
    & $script:DockerComposeCmd.Split() ps
}

# Logs function
function Invoke-Logs {
    param([string]$ServiceName)

    Write-Header
    Test-Docker

    if ($ServiceName) {
        Write-Info "Showing logs for $ServiceName (Ctrl+C to exit)..."
        & $script:DockerComposeCmd.Split() logs -f $ServiceName
    }
    else {
        Write-Info "Showing all logs (Ctrl+C to exit)..."
        & $script:DockerComposeCmd.Split() logs -f
    }
}

# Clean function
function Invoke-Clean {
    Write-Header
    Write-Warning "This will remove all containers, volumes, and images"

    $confirmation = Read-Host "Are you sure? (y/N)"
    if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
        Test-Docker

        Write-Info "Stopping containers..."
        & $script:DockerComposeCmd.Split() down

        Write-Info "Removing volumes..."
        & $script:DockerComposeCmd.Split() down -v

        Write-Info "Removing images..."
        & $script:DockerComposeCmd.Split() down --rmi all

        Write-Success "Cleanup complete!"
    }
    else {
        Write-Info "Cleanup cancelled"
    }
}

# Update function
function Invoke-Update {
    Write-Header
    Write-Info "Updating application..."

    Test-Docker

    Write-Info "Pulling latest code..."
    git pull

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Git pull failed"
        exit 1
    }

    Write-Info "Rebuilding containers..."
    & $script:DockerComposeCmd.Split() build --no-cache

    Write-Info "Restarting containers..."
    & $script:DockerComposeCmd.Split() up -d --force-recreate

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Update complete!"
        Invoke-Status
    }
}

# Health check function
function Invoke-Health {
    Write-Header
    Write-Info "Performing health check..."

    # Check backend
    Write-Host "Backend: " -NoNewline
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Healthy"
        }
        else {
            Write-Error "Unhealthy"
        }
    }
    catch {
        Write-Error "Unhealthy - $($_.Exception.Message)"
    }

    # Check frontend
    Write-Host "Frontend: " -NoNewline
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Healthy"
        }
        else {
            Write-Error "Unhealthy"
        }
    }
    catch {
        Write-Error "Unhealthy - $($_.Exception.Message)"
    }

    # Check nginx
    Write-Host "Nginx: " -NoNewline
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8888/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Healthy"
        }
        else {
            Write-Error "Unhealthy"
        }
    }
    catch {
        Write-Error "Unhealthy - $($_.Exception.Message)"
    }
}

# Help function
function Show-Help {
    Write-Header
    Write-Host "Usage: .\deploy.ps1 [command] [service]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  deploy    - Build and deploy all containers"
    Write-Host "  start     - Start all containers"
    Write-Host "  stop      - Stop all containers"
    Write-Host "  restart   - Restart all containers"
    Write-Host "  status    - Show container status"
    Write-Host "  logs      - Show logs (optionally specify service: backend|frontend|nginx)"
    Write-Host "  clean     - Remove all containers, volumes, and images"
    Write-Host "  update    - Pull latest code and rebuild containers"
    Write-Host "  health    - Check health of all services"
    Write-Host "  help      - Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\deploy.ps1 deploy          # Initial deployment"
    Write-Host "  .\deploy.ps1 logs backend    # Show backend logs"
    Write-Host "  .\deploy.ps1 restart         # Restart all services"
    Write-Host ""
    Write-Host "Windows-specific notes:"
    Write-Host "  - Make sure Docker Desktop is running"
    Write-Host "  - Use PowerShell (not Command Prompt) for best experience"
    Write-Host "  - You may need to enable script execution:"
    Write-Host "    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
}

# Main script logic
switch ($Command) {
    'deploy'  { Invoke-Deploy }
    'start'   { Invoke-Start }
    'stop'    { Invoke-Stop }
    'restart' { Invoke-Restart }
    'status'  { Invoke-Status }
    'logs'    { Invoke-Logs -ServiceName $Service }
    'clean'   { Invoke-Clean }
    'update'  { Invoke-Update }
    'health'  { Invoke-Health }
    'help'    { Show-Help }
    default   {
        Write-Error "Unknown command: $Command"
        Write-Host ""
        Show-Help
        exit 1
    }
}
