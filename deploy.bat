@echo off
REM Soft Collar Toolbox 2.0 - Windows Batch Deployment Script
REM Simple version for quick operations

setlocal enabledelayedexpansion

REM Check if Docker is running
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running
    echo Please start Docker Desktop and try again
    exit /b 1
)

REM Determine docker-compose command
docker compose version >nul 2>&1
if %errorlevel% equ 0 (
    set DOCKER_COMPOSE=docker compose
) else (
    docker-compose --version >nul 2>&1
    if %errorlevel% equ 0 (
        set DOCKER_COMPOSE=docker-compose
    ) else (
        echo [ERROR] Docker Compose is not available
        exit /b 1
    )
)

REM Get command
set COMMAND=%1
if "%COMMAND%"=="" set COMMAND=help

REM Execute command
if /i "%COMMAND%"=="deploy" goto :deploy
if /i "%COMMAND%"=="start" goto :start
if /i "%COMMAND%"=="stop" goto :stop
if /i "%COMMAND%"=="restart" goto :restart
if /i "%COMMAND%"=="status" goto :status
if /i "%COMMAND%"=="logs" goto :logs
if /i "%COMMAND%"=="clean" goto :clean
if /i "%COMMAND%"=="health" goto :health
if /i "%COMMAND%"=="help" goto :help
goto :unknown

:deploy
echo ========================================
echo   Deploying Soft Collar Toolbox 2.0
echo ========================================
if not exist .env (
    if exist .env.example (
        echo [INFO] Creating .env from .env.example...
        copy .env.example .env
        echo [SUCCESS] .env file created
        echo [WARNING] Please edit .env file before deploying
        exit /b 0
    ) else (
        echo [ERROR] .env.example not found
        exit /b 1
    )
)
echo [INFO] Building Docker images...
%DOCKER_COMPOSE% build --no-cache
if %errorlevel% neq 0 (
    echo [ERROR] Build failed
    exit /b 1
)
echo [INFO] Starting containers...
%DOCKER_COMPOSE% up -d
if %errorlevel% equ 0 (
    echo [SUCCESS] Deployment complete!
    echo [INFO] Application: http://localhost:8888
    echo [INFO] API Docs: http://localhost:8888/docs
)
goto :end

:start
echo ========================================
echo   Starting Containers
echo ========================================
if not exist .env (
    echo [ERROR] .env file not found
    echo [INFO] Run: deploy.bat deploy
    exit /b 1
)
%DOCKER_COMPOSE% up -d
if %errorlevel% equ 0 (
    echo [SUCCESS] Containers started!
    goto :status
)
goto :end

:stop
echo ========================================
echo   Stopping Containers
echo ========================================
%DOCKER_COMPOSE% stop
if %errorlevel% equ 0 (
    echo [SUCCESS] Containers stopped!
)
goto :end

:restart
echo ========================================
echo   Restarting Containers
echo ========================================
%DOCKER_COMPOSE% restart
if %errorlevel% equ 0 (
    echo [SUCCESS] Containers restarted!
    goto :status
)
goto :end

:status
echo ========================================
echo   Container Status
echo ========================================
%DOCKER_COMPOSE% ps
goto :end

:logs
echo ========================================
echo   Container Logs
echo ========================================
set SERVICE=%2
if "%SERVICE%"=="" (
    echo [INFO] Showing all logs (Ctrl+C to exit)
    %DOCKER_COMPOSE% logs -f
) else (
    echo [INFO] Showing logs for %SERVICE% (Ctrl+C to exit)
    %DOCKER_COMPOSE% logs -f %SERVICE%
)
goto :end

:clean
echo ========================================
echo   Cleanup
echo ========================================
echo [WARNING] This will remove all containers, volumes, and images
set /p CONFIRM="Are you sure? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo [INFO] Cleanup cancelled
    goto :end
)
echo [INFO] Stopping containers...
%DOCKER_COMPOSE% down
echo [INFO] Removing volumes...
%DOCKER_COMPOSE% down -v
echo [INFO] Removing images...
%DOCKER_COMPOSE% down --rmi all
echo [SUCCESS] Cleanup complete!
goto :end

:health
echo ========================================
echo   Health Check
echo ========================================
echo Checking services...
echo.
curl -f http://localhost:8000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Backend: Healthy
) else (
    echo [ERROR] Backend: Unhealthy
)
curl -f http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Frontend: Healthy
) else (
    echo [ERROR] Frontend: Unhealthy
)
curl -f http://localhost:8888/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Nginx: Healthy
) else (
    echo [ERROR] Nginx: Unhealthy
)
goto :end

:help
echo ========================================
echo   Soft Collar Toolbox 2.0
echo   Windows Deployment Script
echo ========================================
echo.
echo Usage: deploy.bat [command] [service]
echo.
echo Commands:
echo   deploy    - Build and deploy all containers
echo   start     - Start all containers
echo   stop      - Stop all containers
echo   restart   - Restart all containers
echo   status    - Show container status
echo   logs      - Show logs (optionally: backend^|frontend^|nginx)
echo   clean     - Remove all containers, volumes, and images
echo   health    - Check health of all services
echo   help      - Show this help message
echo.
echo Examples:
echo   deploy.bat deploy          # Initial deployment
echo   deploy.bat logs backend    # Show backend logs
echo   deploy.bat restart         # Restart all services
echo.
echo Notes:
echo   - Docker Desktop must be running
echo   - For advanced features, use: deploy.ps1 (PowerShell)
goto :end

:unknown
echo [ERROR] Unknown command: %COMMAND%
echo.
goto :help

:end
endlocal
