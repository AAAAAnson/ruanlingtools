# Soft Collar Toolbox 2.0 - Claude Development Guide

> Quick reference for Claude to understand and work on this project

---

## Project Overview

**Name**: Soft Collar Toolbox 2.0  
**Type**: Full-stack web application  
**Style**: Pixel art (8-bit game aesthetic)  
**Deployment**: Synology NAS (Docker, Port 8888)  
**Purpose**: Multi-tool platform for image/PDF/text processing

---

## Current Status

**Phase**: P0 - Framework Setup  
**Progress**: 0% (Just starting)  
**Next Task**: Task 0.1 - Project Initialization  
**Timeline**: 2 weeks for P0 completion

---

## Technology Stack

### Frontend
- **Framework**: Next.js 14 (App Router, NOT Pages Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Animation**: Framer Motion
- **Icons**: Lucide React (open-source, MIT license)
- **State**: Zustand
- **Fonts**: Press Start 2P (pixel), Roboto (body)

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Async**: asyncio (all endpoints async)
- **Image**: Pillow, pillow-avif
- **PDF**: PyPDF2, pdf2image, python-docx
- **Validation**: Pydantic

### Deployment
- **Platform**: Synology NAS
- **Container**: Docker + Docker Compose
- **Port**: 8888
- **Database**: SQLite (for local use)

---

## Critical Development Rules

### 1. UTF-8 Encoding (MANDATORY)

**Every Python file must start with:**
```python
# -*- coding: utf-8 -*-
```

**Every file operation must specify encoding:**
```python
# CORRECT
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# WRONG - Never do this
with open('file.txt', 'r') as f:  # Missing encoding!
    content = f.read()
```

**FastAPI main.py must include:**
```python
# -*- coding: utf-8 -*-
import sys
import os

# Force UTF-8 encoding
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
```

### 2. Language Requirements

**All code must be in English:**
- Variable names: `buttonText` NOT `按钮文字`
- Function names: `processImage()` NOT `处理图片()`
- Comments: `// Process image` NOT `// 处理图片`
- Class names: `ImageService` NOT `图片服务`

**No emojis in code or documentation:**
- Use text markers: `[INFO]` NOT `ℹ️`
- Use Lucide icons: `<Info />` NOT `ℹ️`

### 3. Icon Usage (Lucide React)

```tsx
import { 
  Image,       // Image tools
  FileText,    // Text tools
  File,        // PDF tools
  Wand2,       // AI tools
  Youtube,     // YouTube
  Upload,      // Upload
  Download,    // Download
  Check,       // Success
  X,           // Error/Close
  AlertCircle, // Warning
  Loader2,     // Loading (with animate-spin)
  Settings,    // Settings
  HelpCircle   // Help
} from 'lucide-react'

// Usage
<Image className="w-6 h-6" />
<Loader2 className="w-4 h-4 animate-spin" />
```

### 4. Code Style

**TypeScript/React:**
- Function components + Hooks (no class components)
- TypeScript strict mode
- PascalCase for components: `PixelButton`
- camelCase for functions: `handleClick`
- All files must have .tsx extension for components

**Python:**
- Follow PEP 8
- Type annotations on all functions
- async/await for all I/O operations
- Black formatter for code formatting
- snake_case for functions: `process_image`

### 5. Component Standards

**All UI components must include:**
```tsx
// 1. Type definitions
interface PixelButtonProps {
  children: ReactNode;
  loading?: boolean;
  icon?: ReactNode;
}

// 2. Framer Motion animations
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
>

// 3. Lucide icons (if needed)
import { Loader2 } from 'lucide-react'
{loading && <Loader2 className="w-4 h-4 animate-spin" />}

// 4. Pixel art styling
className="pixel-btn pixel-btn-primary"

// 5. Accessibility
aria-label="Button description"
```

---

## Project Structure

```
toolbox-2.0/
├── frontend/                    # Next.js app
│   ├── src/
│   │   ├── app/                # App Router pages
│   │   │   ├── layout.tsx     # Root layout
│   │   │   ├── page.tsx       # Homepage
│   │   │   ├── image/         # Image tools
│   │   │   ├── text/          # Text tools
│   │   │   ├── pdf/           # PDF tools
│   │   │   ├── ai/            # AI tools (placeholder)
│   │   │   └── youtube/       # YouTube (placeholder)
│   │   ├── components/
│   │   │   ├── ui/            # Pixel art components
│   │   │   ├── layout/        # Layout components
│   │   │   └── features/      # Feature components
│   │   ├── lib/               # Utilities
│   │   ├── hooks/             # Custom hooks
│   │   └── styles/            # Global styles
│   └── public/                # Static assets
│
├── backend/                     # FastAPI app
│   ├── main.py                # Entry point
│   ├── config.py              # Configuration
│   ├── routers/               # API routes
│   ├── services/              # Business logic
│   ├── models/                # Data models
│   └── utils/                 # Utilities
│
├── docker-compose.yml          # Docker config
└── README_EN.md               # Full documentation
```

---

## Development Phases

### P0: Framework Setup (Current - 2 weeks)
**Goal**: Build complete skeleton with pixel art UI

**Deliverables**:
- 12 pixel art UI components (PixelButton, PixelCard, etc.)
- All page routes (functional but features not implemented)
- Docker deployment configuration
- Placeholder pages for AI and YouTube tools

**Key Files to Create**:
```
frontend/src/components/ui/
  - PixelButton.tsx
  - PixelCard.tsx
  - PixelInput.tsx
  - PixelTextarea.tsx
  - PixelSelect.tsx
  - PixelSlider.tsx
  - PixelProgress.tsx
  - PixelToast.tsx
  - PixelModal.tsx
  - PixelUpload.tsx
  - PixelLoading.tsx
  - PixelCheckbox.tsx

backend/routers/
  - image.py (with placeholder endpoints)
  - text.py (with placeholder endpoints)
  - pdf.py (with placeholder endpoints)
  - ai.py (501 status - not implemented)
  - youtube.py (501 status - not implemented)
```

### P1: Image Format Conversion (3-4 days)
- Batch image conversion (JPG/PNG/WebP/AVIF)
- Quality adjustment slider
- Image comparison slider
- Batch ZIP download

### P2: Text Processing Tools (3-4 days)
- 15 text processing functions (all frontend)
- Case conversion, formatting, encoding, sorting

### P3: PDF Toolset (5-7 days)
- PDF to images, merge, split
- PDF compression, Word conversion
- Text extraction

### Future: AI & YouTube
- AI text-to-image (API integration)
- AI background removal (API integration)
- YouTube KOL search (integrate existing tool)

---

## Design System

### Color Palette
```typescript
colors: {
  primary: '#FF6B6B',      // Pixel Red
  secondary: '#4ECDC4',    // Pixel Cyan
  accent: '#FFE66D',       // Pixel Yellow
  success: '#51CF66',      // Pixel Green
  danger: '#FF6B6B',       // Pixel Red
  dark: '#1A1A2E',         // Dark background
}
```

### Typography
```typescript
fonts: {
  pixel: '"Press Start 2P", monospace',  // Titles, buttons
  body: '"Roboto", sans-serif',          // Body text
}
```

### Animations (Framer Motion)
```typescript
// Button interactions
whileHover={{ scale: 1.05, boxShadow: '0 0 20px currentColor' }}
whileTap={{ scale: 0.95 }}

// Page transitions
initial={{ opacity: 0, y: 20 }}
animate={{ opacity: 1, y: 0 }}
exit={{ opacity: 0, y: -20 }}
```

---

## API Standards

### Unified Response Format
```python
# -*- coding: utf-8 -*-
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
        return ApiResponse(code=200, message=message, data=data)
    
    @staticmethod
    def error(message: str, code: int = 400):
        return ApiResponse(code=code, message=message, data=None)
```

### Route Structure
```
/api/image/*          # Image processing
/api/text/*           # Text processing (mostly frontend)
/api/pdf/*            # PDF processing
/api/ai/*             # AI tools (placeholder)
/api/youtube/*        # YouTube search (placeholder)
/api/health           # Health check
```

### Example Route
```python
# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from models.response import ApiResponse

router = APIRouter()

@router.post("/convert")
async def convert_images(
    files: List[UploadFile],
    output_format: str,
    quality: int = 85
):
    """
    Convert images to specified format
    
    Args:
        files: List of image files
        output_format: Target format (jpg/png/webp/avif)
        quality: Output quality (1-100)
    """
    try:
        # Process images
        results = await image_service.convert(files, output_format, quality)
        return ApiResponse.success(data=results)
    except Exception as e:
        return ApiResponse.error(message=str(e), code=500)
```

---

## Current Task: 0.1 - Project Initialization

### What to Do Now

**1. Initialize Next.js Frontend**
```bash
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --app \
  --src-dir \
  --import-alias "@/*"

cd frontend
npm install framer-motion zustand lucide-react
```

**2. Create Backend Structure**
```bash
mkdir -p backend/{routers,services,models,utils}
cd backend

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.0
uvicorn[standard]==0.24.0
python-multipart==0.0.6
Pillow==10.1.0
pillow-avif==1.4.0
pydantic==2.4.0
python-dotenv==1.0.0
EOF

pip install -r requirements.txt
```

**3. Create Initial Files**

**frontend/src/styles/theme.ts**
```typescript
export const pixelTheme = {
  colors: {
    primary: '#FF6B6B',
    secondary: '#4ECDC4',
    accent: '#FFE66D',
    success: '#51CF66',
    danger: '#FF6B6B',
    dark: '#1A1A2E',
  },
  fonts: {
    pixel: '"Press Start 2P", monospace',
    body: '"Roboto", sans-serif',
  },
}
```

**backend/main.py**
```python
# -*- coding: utf-8 -*-
import sys
import os

# Force UTF-8
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Soft Collar Toolbox API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# UTF-8 in responses
@app.middleware("http")
async def add_utf8(request, call_next):
    response = await call_next(request)
    if "json" in response.headers.get("content-type", ""):
        response.headers["content-type"] = "application/json; charset=utf-8"
    return response

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "API is running"}
```

**backend/models/response.py**
```python
# -*- coding: utf-8 -*-
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
        return ApiResponse(code=200, message=message, data=data)
    
    @staticmethod
    def error(message: str, code: int = 400):
        return ApiResponse(code=code, message=message, data=None)
```

---

## Testing Your Setup

**Test frontend:**
```bash
cd frontend
npm run dev
# Should open http://localhost:3000
```

**Test backend:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Should open http://localhost:8000/docs (Swagger UI)
```

**Test UTF-8:**
```python
# -*- coding: utf-8 -*-
# test_utf8.py
test = "中文 English 日本語"
with open('test.txt', 'w', encoding='utf-8') as f:
    f.write(test)
with open('test.txt', 'r', encoding='utf-8') as f:
    assert f.read() == test
print("UTF-8 encoding: OK")
```

---

## Common Issues and Solutions

### Issue: TypeScript errors
**Solution**: Check tsconfig.json has strict mode enabled

### Issue: Encoding errors in Python
**Solution**: Verify all files start with `# -*- coding: utf-8 -*-`

### Issue: Icons not showing
**Solution**: Verify lucide-react is installed: `npm install lucide-react`

### Issue: CORS errors
**Solution**: Check main.py has CORS middleware configured

### Issue: Docker build fails
**Solution**: Check Dockerfile has UTF-8 environment variables:
```dockerfile
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONIOENCODING=utf-8
```

---

## Important Files to Reference

1. **README_EN.md** - Complete project documentation
2. **QUICK_GUIDE_EN.md** - Quick development guide
3. **UTF8_ENCODING_GUIDE.md** - UTF-8 best practices (critical!)
4. **UTF8_CHECKLIST.md** - Quick UTF-8 reference
5. **.clinerules_EN** - Development rules and standards

---

## Key Reminders

1. **ALWAYS** start Python files with `# -*- coding: utf-8 -*-`
2. **ALWAYS** specify `encoding='utf-8'` in file operations
3. **NEVER** use emojis in code or documentation
4. **ALWAYS** use Lucide React for icons
5. **ALWAYS** write code and comments in English
6. **ALWAYS** use TypeScript strict mode
7. **ALWAYS** use async/await in Python
8. **ALWAYS** follow the task order (don't skip tasks)
9. **ALWAYS** test with non-English characters
10. **ALWAYS** check console for encoding errors

---

## Git Commit Format

```
feat(P0): Complete task 0.1 - project initialization
fix(image): Fix PNG transparency loss issue
docs: Update deployment documentation
style: Format code with Black
refactor: Reorganize component structure
test: Add UTF-8 encoding tests
chore: Update dependencies
```

---

## Success Criteria for P0

- [ ] All 12 UI components created and working
- [ ] All pages accessible (with placeholder content)
- [ ] No TypeScript errors
- [ ] No encoding errors
- [ ] Docker deployment working
- [ ] Can access at http://NAS_IP:8888
- [ ] All tests pass
- [ ] Mobile responsive design works

---

## Next Steps After P0

1. Complete P0 framework setup
2. Move to P1: Implement image format conversion
3. Build P2: Text processing tools
4. Develop P3: PDF toolset
5. Integrate AI features (future)
6. Add YouTube KOL search (future)

---

## Quick Commands

```bash
# Start development
cd frontend && npm run dev          # Frontend (port 3000)
cd backend && uvicorn main:app --reload  # Backend (port 8000)

# Check for UTF-8 issues
grep -L "coding: utf-8" backend/**/*.py  # Find files missing UTF-8

# Format code
cd frontend && npm run lint          # TypeScript
cd backend && black .                # Python

# Build for production
cd frontend && npm run build
docker-compose up --build           # Full stack
```

---

**Remember**: Read QUICK_GUIDE_EN.md before each development session!

**Last Updated**: 2025-11-15  
**Current Phase**: P0 - Framework Setup  
**Current Progress**: 0%  
**Next Task**: Task 0.1 - Project Initialization
