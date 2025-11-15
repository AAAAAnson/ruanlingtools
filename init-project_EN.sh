#!/bin/bash

# Soft Collar Toolbox 2.0 - Project Structure Initialization Script
# Running this script will create the complete project directory structure

echo "Starting project structure initialization..."

# Create frontend directory structure
echo "Creating frontend directories..."
mkdir -p frontend/src/{app,components,lib,hooks,styles}
mkdir -p frontend/src/components/{ui,layout,features}
mkdir -p frontend/src/app/{image,text,pdf,ai,youtube}
mkdir -p frontend/src/app/image/{convert,watermark}
mkdir -p frontend/src/app/text/{case-converter,formatter,encoder,sort,stats}
mkdir -p frontend/src/app/pdf/{to-images,merge,split,compress,convert,extract-text}
mkdir -p frontend/public/{fonts,icons}

# Create backend directory structure
echo "Creating backend directories..."
mkdir -p backend/{routers,services,models,utils}
mkdir -p backend/{uploads,outputs}

# Create frontend required files (empty files, awaiting development)
echo "Creating frontend files..."

# Style files
touch frontend/src/styles/globals.css
touch frontend/src/styles/theme.ts
touch frontend/src/styles/animations.css

# Utility library
touch frontend/src/lib/animations.ts
touch frontend/src/lib/utils.ts
touch frontend/src/lib/api.ts

# Hooks
touch frontend/src/hooks/useLocalStorage.ts

# UI components
touch frontend/src/components/ui/PixelButton.tsx
touch frontend/src/components/ui/PixelCard.tsx
touch frontend/src/components/ui/PixelInput.tsx
touch frontend/src/components/ui/PixelTextarea.tsx
touch frontend/src/components/ui/PixelSelect.tsx
touch frontend/src/components/ui/PixelSlider.tsx
touch frontend/src/components/ui/PixelProgress.tsx
touch frontend/src/components/ui/PixelToast.tsx
touch frontend/src/components/ui/PixelModal.tsx
touch frontend/src/components/ui/PixelUpload.tsx
touch frontend/src/components/ui/PixelLoading.tsx
touch frontend/src/components/ui/PixelCheckbox.tsx

# Layout components
touch frontend/src/components/layout/Header.tsx
touch frontend/src/components/layout/Footer.tsx
touch frontend/src/components/layout/Sidebar.tsx
touch frontend/src/components/layout/MainLayout.tsx

# Feature components
touch frontend/src/components/features/ComingSoon.tsx
touch frontend/src/components/features/TextStats.tsx
touch frontend/src/components/features/ImageCompare.tsx

# Page files
touch frontend/src/app/layout.tsx
touch frontend/src/app/page.tsx
touch frontend/src/app/image/page.tsx
touch frontend/src/app/image/convert/page.tsx
touch frontend/src/app/image/watermark/page.tsx
touch frontend/src/app/text/page.tsx
touch frontend/src/app/pdf/page.tsx
touch frontend/src/app/ai/page.tsx
touch frontend/src/app/youtube/page.tsx

# Create backend required files
echo "Creating backend files with UTF-8 declarations..."

# Core files with UTF-8 headers
cat > backend/main.py << 'EOF'
# -*- coding: utf-8 -*-
"""
Main application entry point
"""
EOF

cat > backend/config.py << 'EOF'
# -*- coding: utf-8 -*-
"""
Configuration module
"""
EOF

touch backend/requirements.txt
touch backend/.env

# Models with UTF-8 headers
cat > backend/models/__init__.py << 'EOF'
# -*- coding: utf-8 -*-
EOF

cat > backend/models/response.py << 'EOF'
# -*- coding: utf-8 -*-
"""
Unified API response models
"""
EOF

# Routes with UTF-8 headers
cat > backend/routers/__init__.py << 'EOF'
# -*- coding: utf-8 -*-
EOF

cat > backend/routers/image.py << 'EOF'
# -*- coding: utf-8 -*-
"""
Image processing routes
"""
EOF

cat > backend/routers/text.py << 'EOF'
# -*- coding: utf-8 -*-
"""
Text processing routes
"""
EOF

cat > backend/routers/pdf.py << 'EOF'
# -*- coding: utf-8 -*-
"""
PDF processing routes
"""
EOF

cat > backend/routers/ai.py << 'EOF'
# -*- coding: utf-8 -*-
"""
AI tools routes (placeholder)
"""
EOF

cat > backend/routers/youtube.py << 'EOF'
# -*- coding: utf-8 -*-
"""
YouTube search routes (placeholder)
"""
EOF

# Services with UTF-8 headers
cat > backend/services/__init__.py << 'EOF'
# -*- coding: utf-8 -*-
EOF

cat > backend/services/image_service.py << 'EOF'
# -*- coding: utf-8 -*-
"""
Image processing service
"""
EOF

# Utilities with UTF-8 headers
cat > backend/utils/__init__.py << 'EOF'
# -*- coding: utf-8 -*-
EOF

cat > backend/utils/file_handler.py << 'EOF'
# -*- coding: utf-8 -*-
"""
File handling utilities
"""
EOF

cat > backend/utils/cleanup.py << 'EOF'
# -*- coding: utf-8 -*-
"""
Scheduled cleanup utilities
"""
EOF

# Create Docker related files
echo "Creating Docker files..."
touch docker-compose.yml
touch frontend/Dockerfile
touch backend/Dockerfile
touch .dockerignore
touch .gitignore

# Create documentation files
echo "Creating documentation files..."
touch DEPLOYMENT.md
touch CHANGELOG.md

# Create .gitkeep files (keep empty directories)
echo "Creating .gitkeep files..."
touch backend/uploads/.gitkeep
touch backend/outputs/.gitkeep

# Write basic .gitignore
echo "Writing .gitignore..."
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
__pycache__/
*.pyc
venv/
.venv/

# Environment variables
.env
.env.local

# Build output
.next/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# System files
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*

# Temporary files
backend/uploads/*
!backend/uploads/.gitkeep
backend/outputs/*
!backend/outputs/.gitkeep

# Docker
.docker/
EOF

# Write basic .dockerignore
cat > .dockerignore << 'EOF'
node_modules
.next
.git
.env.local
npm-debug.log
__pycache__
*.pyc
.venv
venv
EOF

# Create frontend package.json (basic version)
echo "Creating package.json..."
cat > frontend/package.json << 'EOF'
{
  "name": "toolbox-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "framer-motion": "^10.16.0",
    "zustand": "^4.4.0",
    "lucide-react": "^0.290.0"
  },
  "devDependencies": {
    "@types/node": "^20.8.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.2.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "eslint": "^8.51.0",
    "eslint-config-next": "14.0.0"
  }
}
EOF

# Create backend requirements.txt
echo "Creating requirements.txt..."
cat > backend/requirements.txt << 'EOF'
fastapi==0.104.0
uvicorn[standard]==0.24.0
python-multipart==0.0.6
Pillow==10.1.0
pillow-avif==1.4.0
PyPDF2==3.0.1
pdf2image==1.16.3
python-docx==1.1.0
pydantic==2.4.0
python-dotenv==1.0.0
EOF

# Create tsconfig.json
echo "Creating TypeScript configuration..."
cat > frontend/tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
EOF

# Create tailwind.config.ts
echo "Creating Tailwind configuration..."
cat > frontend/tailwind.config.ts << 'EOF'
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#FF6B6B',
        secondary: '#4ECDC4',
        accent: '#FFE66D',
        success: '#51CF66',
        danger: '#FF6B6B',
        dark: '#1A1A2E',
      },
      fontFamily: {
        pixel: ['"Press Start 2P"', 'monospace'],
        body: ['"Roboto"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
export default config
EOF

# Create next.config.js
echo "Creating Next.js configuration..."
cat > frontend/next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
}

module.exports = nextConfig
EOF

# Create backend config.py
echo "Creating backend configuration with UTF-8 support..."
cat > backend/config.py << 'EOF'
# -*- coding: utf-8 -*-
"""
Application configuration
"""
import os
import sys
from dotenv import load_dotenv

# Ensure UTF-8 encoding
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()

# Basic configuration
APP_NAME = "Soft Collar Toolbox 2.0"
APP_VERSION = "0.1.0"
DEBUG = os.getenv("DEBUG", "True") == "True"

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# File configuration
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# CORS configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
EOF

# Complete
echo ""
echo "Project structure initialization complete!"
echo ""
echo "Next steps:"
echo "1. cd frontend && npm install      # Install frontend dependencies"
echo "2. cd backend && pip install -r requirements.txt  # Install backend dependencies"
echo "3. Read QUICK_GUIDE_EN.md         # Understand development workflow"
echo "4. Start development task 0.1      # Refer to README_EN.md"
echo ""
echo "Happy coding!"
