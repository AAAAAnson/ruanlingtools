#!/bin/bash
# Pre-build validation for Docker deployment on NAS

set -e

echo "====================================="
echo "Docker Build Pre-Check"
echo "====================================="
echo ""

# Run encoding check
echo "Running encoding validation..."
./check-encoding.sh
echo ""

# Check Docker files
echo "Checking Docker configuration..."
if [ ! -f "docker-compose.yml" ]; then
    echo "ERROR: docker-compose.yml not found"
    exit 1
fi
echo "✓ docker-compose.yml exists"

if [ ! -f "frontend/Dockerfile" ]; then
    echo "ERROR: frontend/Dockerfile not found"
    exit 1
fi
echo "✓ frontend/Dockerfile exists"

if [ ! -f "backend/Dockerfile" ]; then
    echo "ERROR: backend/Dockerfile not found"
    exit 1
fi
echo "✓ backend/Dockerfile exists"
echo ""

# Check .env file
echo "Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found, using defaults"
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo "✓ .env created"
    fi
else
    echo "✓ .env exists"
fi
echo ""

# Check frontend dependencies
echo "Checking frontend package.json..."
if [ ! -f "frontend/package.json" ]; then
    echo "ERROR: frontend/package.json not found"
    exit 1
fi
echo "✓ frontend/package.json exists"
echo ""

# Check backend requirements
echo "Checking backend requirements.txt..."
if [ ! -f "backend/requirements.txt" ]; then
    echo "ERROR: backend/requirements.txt not found"
    exit 1
fi
echo "✓ backend/requirements.txt exists"
echo ""

# Check .dockerignore files
echo "Checking .dockerignore files..."
if [ ! -f "frontend/.dockerignore" ]; then
    echo "WARNING: frontend/.dockerignore not found"
else
    echo "✓ frontend/.dockerignore exists"
fi

if [ ! -f "backend/.dockerignore" ]; then
    echo "WARNING: backend/.dockerignore not found"
else
    echo "✓ backend/.dockerignore exists"
fi
echo ""

echo "====================================="
echo "✓ Pre-build checks PASSED"
echo "====================================="
echo ""
echo "You can now run:"
echo "  docker-compose up -d --build"
echo ""
