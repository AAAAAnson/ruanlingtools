# Claude Code Quick Development Guide

> Quick reference document
> Read this document (2 minutes) before each development session, then check detailed README.md

---

## Current Status Overview

```
Project Name: Soft Collar Toolbox 2.0
Current Phase: P0 - Framework Setup
Current Progress: 0%
Next Task: Task 0.1 - Project Initialization
Estimated Completion: 2 weeks (14 days)
```

---

## 3 Checks Before Starting Development

### 1. Which phase am I in?
```bash
# Check "Development Progress Tracking" section in README.md
grep "### Current Phase" README.md
```

**Current: P0 - Framework Setup**
- Goal: Build complete skeleton, all pages accessible
- Time: 2 weeks
- Deliverables: 12 UI components + all page skeletons + Docker deployment

### 2. What should I do?
```bash
# View unfinished tasks
grep "\[ \]" README.md | head -5
```

**Current Task: 0.1 - Project Initialization**
- [ ] Create Next.js project (App Router)
- [ ] Configure Tailwind CSS
- [ ] Configure TypeScript
- [ ] Install base dependencies

### 3. Are prerequisites complete?
- Task 0.1 is the first task, no prerequisites
- Can start directly

---

## Start Development Immediately

### First Run (Initialize Project)

```bash
# 1. Create frontend project
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --app \
  --src-dir \
  --import-alias "@/*"

# 2. Enter frontend directory
cd frontend

# 3. Install additional dependencies
npm install framer-motion zustand lucide-react

# 4. Create backend project
cd ..
mkdir -p backend/{routers,services,models,utils}
cd backend

# 5. Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 6. Install backend dependencies
pip install fastapi uvicorn python-multipart pillow pillow-avif

# 7. Create requirements.txt
pip freeze > requirements.txt
```

### Subsequent Development (Start Services)

```bash
# Terminal 1: Start frontend
cd frontend
npm run dev
# Access: http://localhost:3000

# Terminal 2: Start backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Access: http://localhost:8000/docs
```

---

## Which Files Should I Create?

### P0 Phase Required Files (In Order)

#### Week 1: Frontend Basics

**Day 1-2: Project Initialization**
```
[x] frontend/package.json
[x] frontend/tsconfig.json
[x] frontend/tailwind.config.ts
[x] frontend/next.config.js
```

**Day 3-5: Styles and Theme**
```
[x] frontend/src/styles/globals.css
[x] frontend/src/styles/theme.ts
[x] frontend/src/styles/animations.css
[x] frontend/src/lib/animations.ts
```

**Day 6-10: UI Component Library (4 components per day)**
```
Day 6:
[x] frontend/src/components/ui/PixelButton.tsx
[x] frontend/src/components/ui/PixelCard.tsx
[x] frontend/src/components/ui/PixelInput.tsx
[x] frontend/src/components/ui/PixelTextarea.tsx

Day 7:
[x] frontend/src/components/ui/PixelSelect.tsx
[x] frontend/src/components/ui/PixelSlider.tsx
[x] frontend/src/components/ui/PixelProgress.tsx
[x] frontend/src/components/ui/PixelToast.tsx

Day 8:
[x] frontend/src/components/ui/PixelModal.tsx
[x] frontend/src/components/ui/PixelUpload.tsx
[x] frontend/src/components/ui/PixelLoading.tsx
[x] frontend/src/components/ui/PixelCheckbox.tsx
```

**Day 11-14: Layout and Homepage**
```
[x] frontend/src/components/layout/Header.tsx
[x] frontend/src/components/layout/Footer.tsx
[x] frontend/src/components/layout/Sidebar.tsx
[x] frontend/src/app/layout.tsx
[x] frontend/src/app/page.tsx
```

#### Week 2: Backend and Page Skeletons

**Day 15-16: Backend Basics**
```
[x] backend/main.py
[x] backend/config.py
[x] backend/models/response.py
[x] backend/requirements.txt
```

**Day 17-18: Routes and Pages**
```
[x] backend/routers/image.py
[x] backend/routers/text.py
[x] backend/routers/pdf.py
[x] backend/routers/ai.py
[x] backend/routers/youtube.py

[x] frontend/src/app/image/page.tsx
[x] frontend/src/app/text/page.tsx
[x] frontend/src/app/pdf/page.tsx
[x] frontend/src/app/ai/page.tsx
[x] frontend/src/app/youtube/page.tsx
```

**Day 19-21: Docker and Documentation**
```
[x] docker-compose.yml
[x] frontend/Dockerfile
[x] backend/Dockerfile
[x] DEPLOYMENT.md
```

---

## Development Tips

### 1. Component Development Workflow
```typescript
// 1. Write type definitions first
interface PixelButtonProps {
  children: ReactNode;
  variant?: 'primary' | 'secondary';
  onClick?: () => void;
}

// 2. Write component logic
export function PixelButton({ children, variant, onClick }: PixelButtonProps) {
  // ...
}

// 3. Add animations last
<motion.button whileHover={{ scale: 1.05 }}>
```

### 2. API Development Workflow
```python
# 1. Define route first
@router.post("/convert")
async def convert_images():
    pass

# 2. Write business logic
async def process_image():
    pass

# 3. Return response last
return ApiResponse.success(data=result)
```

### 3. Testing Workflow
```bash
# 1. Frontend testing
npm run dev  # Open browser and test

# 2. Backend testing
# Access http://localhost:8000/docs
# Use Swagger UI to test API

# 3. Integration testing
# Run both frontend and backend, test complete flow
```

---

## Design Quick Reference

### Color Codes (Copy Directly)
```css
--color-primary: #FF6B6B;    /* Pixel Red */
--color-secondary: #4ECDC4;  /* Pixel Cyan */
--color-accent: #FFE66D;     /* Pixel Yellow */
--color-success: #51CF66;    /* Pixel Green */
--color-dark: #1A1A2E;       /* Dark background */
```

### Icon Usage (Lucide React)
```tsx
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
  AlertCircle,
  Loader2
} from 'lucide-react'

// Usage
<Image className="w-6 h-6" />
<Upload className="w-4 h-4" />
<Loader2 className="w-4 h-4 animate-spin" />
```

### Common Animations (Copy Directly)
```tsx
// Button hover
whileHover={{ scale: 1.05, boxShadow: '0 0 20px currentColor' }}

// Button tap
whileTap={{ scale: 0.95 }}

// Fade in
initial={{ opacity: 0 }}
animate={{ opacity: 1 }}

// Slide up
initial={{ y: 20, opacity: 0 }}
animate={{ y: 0, opacity: 1 }}
```

---

## Encountered Problems?

### Frontend Issues
```bash
# Dependency installation failed
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# TypeScript errors
npm run build  # Check specific errors
```

### Backend Issues
```bash
# Dependency installation failed
pip install --upgrade pip
pip install -r requirements.txt

# Port occupied
lsof -i :8000  # Check process
kill -9 <PID>  # Kill process
```

### Docker Issues
```bash
# View logs
docker logs toolbox-frontend
docker logs toolbox-backend

# Rebuild
docker-compose down
docker-compose up --build
```

---

## Actions After Task Completion

### 1. Update README
```bash
# Mark task as completed
- [x] Task 0.1: Project Initialization
```

### 2. Commit Code
```bash
git add .
git commit -m "feat(P0): Complete task 0.1 - project initialization"
git push
```

### 3. Check Next Task
```bash
# View next unfinished task
grep "\[ \]" README.md | head -1
```

---

## Quick Progress Tracking

```bash
# View P0 total progress
grep -c "\[x\]" README.md  # Completed tasks
grep -c "\[ \]" README.md  # Unfinished tasks

# View current phase
grep "### Current Phase" README.md -A 5
```

---

## Current Development Goal

**Today's Goal**: Task 0.1 - Project Initialization

**Specific Steps**:
1. [x] Create Next.js project
2. [x] Configure Tailwind CSS
3. [x] Configure TypeScript
4. [x] Install base dependencies
5. [x] Create project structure

**Acceptance Criteria**:
- [ ] Frontend project starts normally (npm run dev)
- [ ] Backend project structure created
- [ ] Can access http://localhost:3000
- [ ] No error messages

**After Completion**:
- Update README.md, mark task as [x]
- Commit code: `git commit -m "feat(P0): Initialize project"`
- Start next task: Task 0.2 - Pixel Art Design System

---

## Important Links

- Documentation: README.md
- Design Standards: README.md#design-specifications
- API Standards: README.md#api-interface-standards
- Common Issues: README.md#common-issues
- Deployment Guide: README.md#deployment-guide

---

## Remember These Principles

1. Read README first: Must read before each development
2. Develop in order: Don't skip tasks
3. Keep style consistent: Use pixel art components
4. Test before commit: Ensure functionality works
5. Update documentation: Check off tasks after completion

---

**Start Development!**

If unsure where to start, run:
```bash
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir
```
