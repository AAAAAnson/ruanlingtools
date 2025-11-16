#!/bin/bash

# Soft Collar Toolbox 2.0 - Deployment Script
# This script helps you deploy, manage, and monitor the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Soft Collar Toolbox 2.0${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if .env exists
check_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found"
        print_info "Creating .env from .env.example..."
        cp .env.example .env
        print_success ".env file created"
        print_warning "Please edit .env file with your configuration before deploying"
        exit 0
    fi
}

# Build and start containers
deploy() {
    print_header
    print_info "Starting deployment..."

    check_env

    print_info "Building Docker images..."
    docker-compose build --no-cache

    print_info "Starting containers..."
    docker-compose up -d

    print_success "Deployment complete!"
    print_info "Application is running on http://localhost:8888"
    print_info "API documentation: http://localhost:8888/docs"
}

# Start containers
start() {
    print_header
    print_info "Starting containers..."

    check_env
    docker-compose up -d

    print_success "Containers started!"
    status
}

# Stop containers
stop() {
    print_header
    print_info "Stopping containers..."

    docker-compose stop

    print_success "Containers stopped!"
}

# Restart containers
restart() {
    print_header
    print_info "Restarting containers..."

    docker-compose restart

    print_success "Containers restarted!"
    status
}

# Show container status
status() {
    print_header
    print_info "Container status:"
    docker-compose ps
}

# Show logs
logs() {
    print_header
    if [ -z "$1" ]; then
        print_info "Showing all logs (Ctrl+C to exit)..."
        docker-compose logs -f
    else
        print_info "Showing logs for $1 (Ctrl+C to exit)..."
        docker-compose logs -f "$1"
    fi
}

# Clean up (remove containers, volumes, images)
clean() {
    print_header
    print_warning "This will remove all containers, volumes, and images"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Stopping containers..."
        docker-compose down

        print_info "Removing volumes..."
        docker-compose down -v

        print_info "Removing images..."
        docker-compose down --rmi all

        print_success "Cleanup complete!"
    else
        print_info "Cleanup cancelled"
    fi
}

# Update (rebuild and restart)
update() {
    print_header
    print_info "Updating application..."

    print_info "Pulling latest code..."
    git pull

    print_info "Rebuilding containers..."
    docker-compose build --no-cache

    print_info "Restarting containers..."
    docker-compose up -d --force-recreate

    print_success "Update complete!"
    status
}

# Health check
health() {
    print_header
    print_info "Performing health check..."

    # Check backend
    echo -n "Backend: "
    if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
        print_success "Healthy"
    else
        print_error "Unhealthy"
    fi

    # Check frontend
    echo -n "Frontend: "
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        print_success "Healthy"
    else
        print_error "Unhealthy"
    fi

    # Check nginx
    echo -n "Nginx: "
    if curl -f http://localhost:8888/health > /dev/null 2>&1; then
        print_success "Healthy"
    else
        print_error "Unhealthy"
    fi
}

# Show help
help() {
    print_header
    echo "Usage: ./deploy.sh [command]"
    echo ""
    echo "Commands:"
    echo "  deploy    - Build and deploy all containers"
    echo "  start     - Start all containers"
    echo "  stop      - Stop all containers"
    echo "  restart   - Restart all containers"
    echo "  status    - Show container status"
    echo "  logs      - Show logs (optionally specify service: backend|frontend|nginx)"
    echo "  clean     - Remove all containers, volumes, and images"
    echo "  update    - Pull latest code and rebuild containers"
    echo "  health    - Check health of all services"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh deploy          # Initial deployment"
    echo "  ./deploy.sh logs backend    # Show backend logs"
    echo "  ./deploy.sh restart         # Restart all services"
}

# Main script
case "$1" in
    deploy)
        deploy
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs "$2"
        ;;
    clean)
        clean
        ;;
    update)
        update
        ;;
    health)
        health
        ;;
    help|--help|-h)
        help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        help
        exit 1
        ;;
esac
