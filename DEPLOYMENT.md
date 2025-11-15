# Soft Collar Toolbox 2.0 - Deployment Guide

## Quick Start

This guide will help you deploy the Soft Collar Toolbox 2.0 on your Synology NAS using Docker.

## Prerequisites

- Synology NAS with DSM 7.0 or higher
- Container Manager (Docker) installed
- At least 2GB of free RAM
- At least 1GB of free disk space

## Deployment Options

### Option 1: Docker Compose (Recommended)

This is the easiest and recommended method for Synology NAS deployment.

#### Step 1: Prepare Files

1. Download or clone the project to your local machine
2. Ensure all project files are present

#### Step 2: Upload to Synology

1. Open File Station on your Synology
2. Navigate to `/docker/` (create if it doesn't exist)
3. Create a new folder: `toolbox-2.0`
4. Upload all project files to `/docker/toolbox-2.0`

#### Step 3: Deploy with Container Manager

1. Open **Container Manager** (formerly Docker)
2. Go to **Project** tab
3. Click **Create**
4. Set the following:
   - **Project Name**: `toolbox-2.0`
   - **Path**: `/docker/toolbox-2.0`
   - **Source**: `docker-compose.yml`
5. Click **Next**
6. Review the configuration (port 8888 for frontend, 8000 for backend)
7. Click **Done**

#### Step 4: Wait for Build

The initial build will take 5-10 minutes. You can monitor progress in Container Manager.

#### Step 5: Access the Application

Once deployed, access the application at:
```
http://YOUR_NAS_IP:8888
```

Replace `YOUR_NAS_IP` with your Synology NAS IP address.

---

### Option 2: Manual Docker Commands

If you prefer command line or SSH access:

```bash
# Navigate to project directory
cd /docker/toolbox-2.0

# Build and start containers
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

---

## Configuration

### Environment Variables

#### Backend Configuration

Create or modify `backend/.env` file:

```env
DEBUG=False
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://YOUR_NAS_IP:8888
MAX_FILE_SIZE=52428800
```

#### Frontend Configuration

The frontend uses environment variables set in `docker-compose.yml`:
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://backend:8000)

### Port Configuration

Default ports:
- **Frontend**: 8888
- **Backend**: 8000

To change the frontend port, edit `docker-compose.yml`:
```yaml
ports:
  - "YOUR_PORT:3000"  # Change YOUR_PORT to desired port
```

---

## Updating the Application

### Method 1: Rebuild with Container Manager

1. Open Container Manager
2. Select the `toolbox-2.0` project
3. Click **Action** → **Build**
4. Wait for rebuild to complete

### Method 2: Command Line

```bash
cd /docker/toolbox-2.0

# Pull latest code (if using git)
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

---

## Troubleshooting

### Application won't start

**Check logs:**
```bash
docker-compose logs -f
```

**Common issues:**
- Port already in use
- Insufficient memory
- File permission issues

**Solutions:**
1. Change port in `docker-compose.yml`
2. Ensure at least 2GB RAM is available
3. Check file permissions: `chmod -R 755 /docker/toolbox-2.0`

### Cannot access application

**Check:**
1. Containers are running: `docker-compose ps`
2. Firewall settings on Synology
3. Correct IP address and port
4. Network connectivity

**Test backend API:**
```
http://YOUR_NAS_IP:8000/docs
```

Should show FastAPI documentation.

### High memory usage

The application is optimized for minimal resource usage, but if experiencing issues:

1. Limit container memory in `docker-compose.yml`:
```yaml
services:
  frontend:
    mem_limit: 512m
  backend:
    mem_limit: 512m
```

2. Restart containers:
```bash
docker-compose restart
```

---

## Maintenance

### View Logs

```bash
# All logs
docker-compose logs -f

# Frontend only
docker-compose logs -f frontend

# Backend only
docker-compose logs -f backend
```

### Clear Old Files

Backend automatically stores uploaded files temporarily. To clear:

```bash
# Clear uploads
rm -rf backend/uploads/*

# Clear outputs
rm -rf backend/outputs/*
```

Or set up automatic cleanup:
```bash
# Add to crontab
0 2 * * * docker exec toolbox-backend rm -rf /app/uploads/* /app/outputs/*
```

### Backup

Important files to backup:
- `docker-compose.yml`
- `backend/.env`
- `backend/app.log` (optional)

---

## Performance Optimization

### For Synology NAS

1. **Use SSD Cache** (if available)
2. **Allocate sufficient RAM** (minimum 2GB)
3. **Enable SSH** for easier maintenance
4. **Regular updates** for Docker and Container Manager

### Application Settings

1. **Disable DEBUG mode** in production (`DEBUG=False`)
2. **Limit file upload size** based on your needs
3. **Clear temporary files** regularly

---

## Security Recommendations

1. **Change default ports** if exposed to internet
2. **Use reverse proxy** (e.g., Nginx Proxy Manager)
3. **Enable HTTPS** with SSL certificates
4. **Restrict CORS origins** in production
5. **Regular updates** to keep dependencies secure

---

## Uninstalling

### Remove Application

```bash
# Stop and remove containers
docker-compose down

# Remove images
docker rmi toolbox-frontend toolbox-backend

# Remove project folder (optional)
rm -rf /docker/toolbox-2.0
```

### Clean Up

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune
```

---

## Getting Help

If you encounter issues:

1. Check the logs first
2. Review this troubleshooting guide
3. Ensure all prerequisites are met
4. Check Synology forums for Container Manager issues

---

## Version Information

- **Application Version**: 0.1.0
- **Docker Compose Version**: 3.8
- **Node.js Version**: 18
- **Python Version**: 3.11

---

## Next Steps

After successful deployment:

1. Access the application at `http://YOUR_NAS_IP:8888`
2. Explore available tools
3. Test image conversion features (P1 phase)
4. Wait for updates with new features (P2, P3 phases)

**Note**: P0 phase includes framework and placeholders. Features will be implemented in subsequent phases (P1, P2, P3).

---

**Last Updated**: 2025-11-15  
**Documentation Version**: 1.0
