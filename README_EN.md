# Soft Collar Toolbox 2.0 - Development Documentation

> IMPORTANT: This document is for Claude Code development use
> Read this document completely before starting development to understand project requirements, current progress, and next tasks.

---

## Project Overview

### Project Positioning
Soft Collar Toolbox 2.0 is an online service platform integrating multiple utility tools, designed with **pixel art style**, providing image processing, PDF processing, text processing, and other multi-dimensional tool services.

### Core Features
- Pixel Art Design: 8-bit game style with rich dynamic interactions
- One-Stop Service: Integrate common tools, no need to switch between platforms
- Local Deployment: Deploy on Synology NAS for personal use
- Modular Design: Independent functions, easy to extend

### Deployment Environment
- Platform: Synology NAS
- Container: Container Manager (Docker)
- Port: 8888
- Access: http://NAS_IP:8888

---

## Development Strategy

### Core Concept
**"Framework First, Feature Iteration"**

1. **P0 Phase**: Build complete pixel art framework + all feature entries (placeholder pages)
2. **P1 Phase**: Implement image format conversion (as feature template)
3. **P2 Phase**: Implement text processing tools (15 features)
4. **P3 Phase**: Implement PDF toolset (6 basic features)
5. **Future Iteration**: AI features, YouTube KOL search, etc.

### Why This Approach?
- Quickly see overall effect, identify design issues early
- Establish unified component library and interaction patterns
- After completing one feature, others can reuse lots of code
- Can use while developing, gradually improve

---

## Development Progress Tracking

### Current Phase: P0 - Framework Setup
**Goal**: Build complete application skeleton, all pages accessible but features not implemented

#### P0 Task Checklist (Estimated 2 weeks)

**Week 1: Design System + Frontend Framework**
- [ ] Task 0.1: Project Initialization
  - [ ] Create Next.js project (App Router)
  - [ ] Configure Tailwind CSS
  - [ ] Configure TypeScript
  - [ ] Install base dependencies (framer-motion, zustand, etc.)
  
- [ ] Task 0.2: Pixel Art Design System
  - [ ] Define color scheme (/src/styles/theme.ts)
  - [ ] Configure pixel fonts (Press Start 2P, Roboto)
  - [ ] Create global styles (/src/styles/globals.css)
  - [ ] Create pixel animation library (/src/lib/animations.ts)
  
- [ ] Task 0.3: Core UI Component Library (/src/components/ui/)
  - [ ] PixelButton.tsx - Pixel button (hover glow, click scale)
  - [ ] PixelCard.tsx - Pixel card
  - [ ] PixelInput.tsx - Pixel input field
  - [ ] PixelTextarea.tsx - Pixel textarea
  - [ ] PixelSelect.tsx - Pixel dropdown
  - [ ] PixelSlider.tsx - Pixel slider
  - [ ] PixelProgress.tsx - Pixel progress bar (8-bit style)
  - [ ] PixelToast.tsx - Pixel toast (success/error/warning)
  - [ ] PixelModal.tsx - Pixel modal
  - [ ] PixelUpload.tsx - Pixel file upload (drag support)
  - [ ] PixelLoading.tsx - Pixel loading animation
  - [ ] PixelCheckbox.tsx - Pixel checkbox
  
- [ ] Task 0.4: Layout Components (/src/components/layout/)
  - [ ] Header.tsx - Top navigation bar
  - [ ] Footer.tsx - Footer info bar
  - [ ] Sidebar.tsx - Sidebar (mobile)
  - [ ] MainLayout.tsx - Main layout container
  
- [ ] Task 0.5: Homepage Implementation (/src/app/page.tsx)
  - [ ] Welcome section
  - [ ] Tool category cards (6 categories)
  - [ ] Recent usage records (empty state)
  - [ ] Statistics display

**Week 2: Backend Framework + Route Placeholders**
- [ ] Task 0.6: Backend Project Initialization
  - [ ] Create FastAPI project structure
  - [ ] Configure CORS middleware
  - [ ] Create unified response format (/backend/models/response.py)
  - [ ] Configure environment variables (.env)
  
- [ ] Task 0.7: Create Router Modules (placeholder interfaces)
  - [ ] /backend/routers/image.py - Image tool routes
  - [ ] /backend/routers/text.py - Text tool routes
  - [ ] /backend/routers/pdf.py - PDF tool routes
  - [ ] /backend/routers/ai.py - AI tool routes (placeholder)
  - [ ] /backend/routers/youtube.py - YouTube search routes (placeholder)
  
- [ ] Task 0.8: Frontend Page Skeletons
  - [ ] /src/app/image/page.tsx - Image tools list
  - [ ] /src/app/image/convert/page.tsx - Image conversion (P1 implementation)
  - [ ] /src/app/image/watermark/page.tsx - Image watermark (placeholder)
  - [ ] /src/app/text/page.tsx - Text tools list
  - [ ] /src/app/text/[tool]/page.tsx - Text tools dynamic route (P2 implementation)
  - [ ] /src/app/pdf/page.tsx - PDF tools list
  - [ ] /src/app/pdf/[tool]/page.tsx - PDF tools dynamic route (P3 implementation)
  - [ ] /src/app/ai/page.tsx - AI tools placeholder page
  - [ ] /src/app/youtube/page.tsx - YouTube search placeholder page
  
- [ ] Task 0.9: Special Components
  - [ ] ComingSoon.tsx - Generic placeholder component
  - [ ] TextStats.tsx - Text statistics component
  - [ ] ImageCompare.tsx - Image comparison slider (P1 use)
  
- [ ] Task 0.10: Docker Configuration
  - [ ] Write Dockerfile (frontend)
  - [ ] Write Dockerfile (backend)
  - [ ] Write docker-compose.yml
  - [ ] Test local deployment
  
- [ ] Task 0.11: Deployment Documentation
  - [ ] Write deployment steps document
  - [ ] Create deployment screenshots
  - [ ] Write FAQ

#### P0 Acceptance Criteria
- All pages accessible, no 404 errors
- Pixel style fully presented, smooth animations
- Placeholder pages show "Under Development" or "Coming Soon"
- Docker deployment successful, accessible on Synology
- Responsive design works well, mobile display normal

---

### Next Phase: P1 - Image Format Conversion (Estimated 3-4 days)

#### P1 Task Checklist
- [ ] Task 1.1: Frontend UI Implementation
  - [ ] File upload component (drag, batch support)
  - [ ] Parameter settings panel (format, quality, size)
  - [ ] Batch processing progress display
  - [ ] Result display grid
  - [ ] Comparison slider component (ImageCompare)
  
- [ ] Task 1.2: Backend API Implementation
  - [ ] POST /api/image/convert - Batch conversion interface
  - [ ] GET /api/image/download/{file_id} - Single file download
  - [ ] GET /api/image/download-zip/{task_id} - Batch ZIP download
  
- [ ] Task 1.3: Image Processing Service
  - [ ] ImageService class implementation
  - [ ] Format conversion logic (JPG/PNG/WebP/AVIF)
  - [ ] Quality adjustment
  - [ ] Size adjustment
  - [ ] Temporary file management
  
- [ ] Task 1.4: Testing and Optimization
  - [ ] Test various format conversions
  - [ ] Test large file processing
  - [ ] Test batch processing (100 images)
  - [ ] Performance optimization

#### P1 Acceptance Criteria
- Support JPG/PNG/WebP/AVIF format conversion
- Batch processing up to 100 images
- Comparison slider works smoothly
- Can download individually or batch as ZIP
- Processing progress displays in real-time

---

## Technology Stack

### Frontend
```json
{
  "framework": "Next.js 14 (App Router)",
  "language": "TypeScript",
  "styling": "Tailwind CSS",
  "animation": "Framer Motion",
  "state": "Zustand",
  "http": "fetch API",
  "icons": "Lucide React"
}
```

### Backend
```python
{
    "framework": "FastAPI",
    "language": "Python 3.11+",
    "async": "asyncio",
    "image": "Pillow, pillow-avif",
    "pdf": "PyPDF2, pdf2image, python-docx",
    "validation": "Pydantic"
}
```

### Project Structure

```
toolbox-2.0/
├── frontend/                          # Next.js Frontend
│   ├── src/
│   │   ├── app/                       # App Router pages
│   │   │   ├── layout.tsx            # Root layout
│   │   │   ├── page.tsx              # Homepage
│   │   │   ├── image/                # Image tools
│   │   │   │   ├── page.tsx          # Image tools list
│   │   │   │   ├── convert/          # P1: Format conversion
│   │   │   │   └── watermark/        # Placeholder: Watermark tool
│   │   │   ├── text/                 # P2: Text tools
│   │   │   ├── pdf/                  # P3: PDF tools
│   │   │   ├── ai/                   # Placeholder: AI tools
│   │   │   └── youtube/              # Placeholder: YouTube search
│   │   ├── components/
│   │   │   ├── ui/                   # Pixel art UI components
│   │   │   ├── layout/               # Layout components
│   │   │   └── features/             # Feature components
│   │   ├── lib/                      # Utilities
│   │   │   ├── animations.ts         # Animation configs
│   │   │   ├── utils.ts              # Utility functions
│   │   │   └── api.ts                # API calls
│   │   ├── hooks/                    # Custom Hooks
│   │   │   └── useLocalStorage.ts
│   │   └── styles/
│   │       ├── globals.css           # Global styles
│   │       ├── theme.ts              # Theme config
│   │       └── animations.css        # Animation styles
│   ├── public/
│   │   ├── fonts/                    # Pixel fonts
│   │   └── icons/                    # Pixel icons
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.js
│
├── backend/                           # FastAPI Backend
│   ├── main.py                       # Entry file
│   ├── config.py                     # Config file
│   ├── routers/                      # Router modules
│   │   ├── __init__.py
│   │   ├── image.py                 # Image processing routes
│   │   ├── text.py                  # Text processing routes (placeholder)
│   │   ├── pdf.py                   # PDF processing routes (placeholder)
│   │   ├── ai.py                    # AI tool routes (placeholder)
│   │   └── youtube.py               # YouTube search routes (placeholder)
│   ├── services/                     # Business logic
│   │   ├── __init__.py
│   │   └── image_service.py         # P1: Image processing service
│   ├── models/                       # Data models
│   │   ├── __init__.py
│   │   └── response.py              # Unified response format
│   ├── utils/                        # Utility functions
│   │   ├── __init__.py
│   │   ├── file_handler.py          # File handling
│   │   └── cleanup.py               # Scheduled cleanup
│   ├── uploads/                      # Upload directory
│   ├── outputs/                      # Output directory
│   ├── requirements.txt              # Python dependencies
│   └── .env                          # Environment variables
│
├── docker-compose.yml                # Docker orchestration config
├── .gitignore
└── README.md                         # This document
```

---

## Design Specifications

### Color Scheme
```typescript
// src/styles/theme.ts
export const pixelTheme = {
  colors: {
    primary: '#FF6B6B',      // Pixel Red (primary)
    secondary: '#4ECDC4',    // Pixel Cyan (secondary)
    accent: '#FFE66D',       // Pixel Yellow (accent)
    success: '#51CF66',      // Pixel Green (success)
    danger: '#FF6B6B',       // Pixel Red (error)
    warning: '#FFD93D',      // Pixel Yellow (warning)
    info: '#4ECDC4',         // Pixel Cyan (info)
    dark: '#1A1A2E',         // Dark background
    darker: '#0F0F1E',       // Darker background
    light: '#F0F0F0',        // Light background
    border: '#333344',       // Border color
  },
  fonts: {
    pixel: '"Press Start 2P", monospace',  // Pixel font (titles, buttons)
    body: '"Roboto", sans-serif',          // Body font
  },
  shadows: {
    pixel: '0 0 0 2px #000',              // Pixel shadow
    glow: '0 0 20px currentColor',        // Glow effect
  }
}
```

### Icon Library
```typescript
// Use Lucide React for all icons
import { 
  Image, 
  FileText, 
  File, 
  Wand2, 
  Youtube,
  Upload,
  Download,
  Check,
  X,
  AlertCircle
} from 'lucide-react'

// Example usage
<Image className="w-6 h-6" />
<FileText className="w-6 h-6" />
```

### Animation Effects
```typescript
// src/lib/animations.ts
export const pixelAnimations = {
  // Button tap
  buttonTap: {
    scale: 0.95,
    transition: { duration: 0.1 }
  },
  
  // Button hover
  buttonHover: {
    scale: 1.05,
    boxShadow: '0 0 20px currentColor',
    transition: { duration: 0.2 }
  },
  
  // Fade in
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 }
  },
  
  // Slide up
  slideUp: {
    initial: { y: 20, opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: -20, opacity: 0 }
  }
}
```

### Component Standards

#### All UI components must include
1. **TypeScript type definitions**
2. **Framer Motion animations**
3. **Pixel art styles**
4. **Responsive design**
5. **Accessibility attributes** (aria-label, etc.)

#### Example: PixelButton
```tsx
// src/components/ui/PixelButton.tsx
import { motion } from 'framer-motion';
import { ButtonHTMLAttributes, ReactNode } from 'react';
import { Loader2 } from 'lucide-react';

interface PixelButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: ReactNode;
}

export function PixelButton({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  disabled,
  className = '',
  ...props
}: PixelButtonProps) {
  return (
    <motion.button
      className={`pixel-btn pixel-btn-${variant} pixel-btn-${size} ${className}`}
      whileHover={{ scale: 1.05, boxShadow: '0 0 20px currentColor' }}
      whileTap={{ scale: 0.95 }}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : (
        <>
          {icon && <span className="mr-2">{icon}</span>}
          {children}
        </>
      )}
    </motion.button>
  );
}
```

---

## API Interface Standards

### Unified Response Format
```typescript
interface ApiResponse<T = any> {
  code: number;        // HTTP status code
  message: string;     // Response message
  data?: T;           // Response data
  timestamp: number;   // Timestamp
}

// Success response
{
  "code": 200,
  "message": "success",
  "data": { ... },
  "timestamp": 1699999999
}

// Error response
{
  "code": 400,
  "message": "Invalid file format",
  "data": null,
  "timestamp": 1699999999
}
```

### Backend Implementation
```python
# backend/models/response.py
from pydantic import BaseModel
from typing import Any, Optional
import time

class ApiResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None
    timestamp: int = int(time.time())
    
    @staticmethod
    def success(data: Any = None, message: str = "success"):
        return ApiResponse(
            code=200,
            message=message,
            data=data
        )
    
    @staticmethod
    def error(message: str, code: int = 400, data: Any = None):
        return ApiResponse(
            code=code,
            message=message,
            data=data
        )
```

### API Route Standards
```
# Image tools
POST   /api/image/convert              # Batch conversion
GET    /api/image/download/{file_id}   # Download single file
GET    /api/image/download-zip/{task_id} # Download ZIP

# Text tools (frontend only, no backend needed)

# PDF tools
POST   /api/pdf/to-images              # PDF to images
POST   /api/pdf/merge                  # Merge PDFs
POST   /api/pdf/split                  # Split PDF
POST   /api/pdf/compress               # Compress PDF
POST   /api/pdf/to-word                # PDF to Word
POST   /api/pdf/extract-text           # Extract text

# AI tools (placeholder)
POST   /api/ai/text-to-image           # AI text-to-image
POST   /api/ai/remove-background       # Background removal

# YouTube search (placeholder)
GET    /api/youtube/search             # Search KOLs
GET    /api/youtube/channel/{id}       # Channel details

# System interfaces
GET    /api/health                     # Health check
```

---

## Development Guide

### Environment Requirements
- **Node.js**: 18.x or higher
- **Python**: 3.11 or higher
- **Docker**: 20.x or higher
- **Docker Compose**: 2.x or higher

### Local Development Startup

#### Frontend
```bash
cd frontend
npm install
npm run dev
# Access http://localhost:3000
```

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Access http://localhost:8000/docs (auto API docs)
```

### Code Standards

#### TypeScript/React
- Use function components + Hooks
- Use TypeScript strict mode
- Component names use PascalCase
- File names match component names
- Use ESLint + Prettier formatting
- **All files must be UTF-8 encoded**

#### Python
- Follow PEP 8 standards
- Use type annotations
- Use async/await async programming
- Use Black for code formatting
- **CRITICAL: All Python files must declare UTF-8 encoding**
  ```python
  # -*- coding: utf-8 -*-
  # Always add this as first line in ALL Python files
  ```

#### UTF-8 Encoding Standards (CRITICAL)

**1. Python File Headers**
```python
# -*- coding: utf-8 -*-
"""
Module description here
"""
```

**2. File Operations - Always Specify UTF-8**
```python
# CORRECT - Always specify encoding
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()

with open('file.txt', 'w', encoding='utf-8') as f:
    f.write(content)

# WRONG - Never omit encoding
with open('file.txt', 'r') as f:  # DON'T DO THIS
    content = f.read()
```

**3. FastAPI Response Encoding**
```python
from fastapi.responses import JSONResponse

# Ensure UTF-8 in JSON responses
return JSONResponse(
    content=data,
    media_type="application/json; charset=utf-8"
)
```

**4. Database Connections**
```python
# SQLite
conn = sqlite3.connect('database.db')
conn.text_factory = str  # Ensure UTF-8

# PostgreSQL
DATABASE_URL = "postgresql://user:pass@localhost/db?client_encoding=utf8"
```

**5. Environment Variables**
```python
# .env file must be UTF-8
# config.py
import os
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
```

**6. CSV/Excel File Handling**
```python
# CSV with UTF-8
import csv
with open('file.csv', 'r', encoding='utf-8-sig') as f:  # utf-8-sig removes BOM
    reader = csv.reader(f)

# Excel with UTF-8
import openpyxl
wb = openpyxl.load_workbook('file.xlsx')
# Excel handles UTF-8 automatically
```

**7. Logging Configuration**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
```

### Git Commit Standards
```
feat: New feature
fix: Bug fix
docs: Documentation update
style: Code format adjustment
refactor: Code refactoring
test: Test related
chore: Build/toolchain update
```

Example:
```
feat(P0): Complete pixel button component
fix(image): Fix PNG transparency loss
docs: Update deployment documentation
```

---

## Deployment Guide

### Synology NAS Deployment (Container Manager)

#### Step 1: Prepare Files
1. Ensure `docker-compose.yml` exists in project root
2. Check `.env` file configuration
3. Ensure `uploads/` and `outputs/` directories exist

#### Step 2: Upload to Synology
1. Open File Station
2. Navigate to `/docker/`
3. Create folder `toolbox-2.0`
4. Upload all project files

#### Step 3: Container Manager Deployment
1. Open Container Manager
2. Click "Project" tab
3. Click "Add" button
4. Select path: `/docker/toolbox-2.0`
5. Select source: `docker-compose.yml`
6. Click "Next"
7. Check configuration, confirm port is 8888
8. Click "Done"
9. Wait for container build and start (about 5-10 minutes)

#### Step 4: Access Test
Open browser: `http://NAS_IP:8888`

### Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build: ./frontend
    container_name: toolbox-frontend
    ports:
      - "8888:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    restart: always

  backend:
    build: ./backend
    container_name: toolbox-backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads
      - ./outputs:/app/outputs
    restart: always

volumes:
  uploads:
  outputs:
```

---

## Current Task

### In Progress: P0 - Framework Setup

**Current Task**: Task 0.1 - Project Initialization

**Next Steps**:
1. Create Next.js project
2. Install base dependencies
3. Configure TypeScript and Tailwind
4. Create project structure

**Development Commands**:
```bash
# Create Next.js project
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir

# Enter project
cd frontend

# Install dependencies
npm install framer-motion zustand lucide-react

# Start dev server
npm run dev
```

---

## Developer Notes

### Project Owner
- **User**: A n son
- **Developer**: Claude Code
- **Deployment Environment**: Synology NAS (Container Manager)
- **Access Port**: 8888

### Project Characteristics
1. **Personal Use**: No user system needed, no complex permission control
2. **Local Deployment**: Data stays local, secure and reliable
3. **Pixel Art Style**: 8-bit game style, unique visual experience
4. **Modular Design**: Independent functions, easy future expansion

---

## Version History

### v0.1.0 (Current Version)
- [x] Create project documentation
- [ ] P0: Framework setup
- [ ] P1: Image format conversion
- [ ] P2: Text processing tools
- [ ] P3: PDF toolset
- [ ] Future: AI features and YouTube search

---

**Last Updated**: 2025-11-15
**Document Version**: v1.0
**Current Phase**: P0 - Framework Setup
**Completion Progress**: 0%

---

> TIP for Claude Code:
> Before each development session, check current status with:
> ```bash
> # Check current Git branch
> git branch
> 
> # View unfinished tasks
> grep "\[ \]" README.md
> 
> # View recent commits
> git log --oneline -5
> ```
