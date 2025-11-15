# Soft Collar Toolbox 2.0 - Complete Documentation Index

## Start Here

**Read this first: claude.md or QUICK_GUIDE_EN.md**

**claude.md** - Best for first-time setup and comprehensive overview  
**QUICK_GUIDE_EN.md** - Best for daily development sessions

These documents will tell you:
- What each document does
- How to use these documents
- What the development workflow is

---

## Core Documents (6 files)

### 0. claude.md (18KB) [5 STARS] **START HERE**
**Complete Project Summary for Claude**
- Quick project overview
- Technology stack summary
- Critical development rules (UTF-8, English, no emojis)
- Current task and next steps
- Code templates and examples
- Common issues and solutions

**When to read**:
- **First time working on this project**
- When you need a complete overview
- When starting a new development phase
- As a reference for all key information

### 1. README_EN.md (40KB) [5 STARS]
**Complete Project Documentation**
- Project overview and development strategy
- Complete task checklist (with progress tracking)
- Technical architecture and design specifications
- Development guide and deployment guide
- **UTF-8 encoding standards**

**When to read**:
- Read completely before project starts
- Look up relevant sections when encountering problems
- Review progress weekly

### 2. QUICK_GUIDE_EN.md (10KB) [5 STARS]
**Quick Development Guide**
- Understand current status in 2 minutes
- Clear next steps
- Common commands and tips

**When to read**:
- **Must read before each Claude Code development session!**
- When unsure what to do
- When need quick commands

### 3. UTF8_ENCODING_GUIDE.md (15KB) [5 STARS]
**UTF-8 Encoding Best Practices**
- Mandatory encoding standards for all Python code
- File operation templates with UTF-8
- FastAPI configuration for UTF-8
- Database UTF-8 setup
- Common encoding pitfalls to avoid
- Testing UTF-8 handling

**When to read**:
- **Before writing any Python code**
- When encountering encoding errors
- When working with files/databases/APIs

### 4. .clinerules_EN (11KB) [4 STARS]
**Claude Code Configuration File**
- Project specifications
- Code style
- Prohibited actions
- **UTF-8 requirements**

**How to use**:
Place in project root directory, Claude Code reads automatically

### 5. init-project_EN.sh (10KB) [4 STARS]
**Project Initialization Script**
- Auto-create all directories
- Auto-create required files with UTF-8 declarations
- Auto-generate configurations

**How to use**:
```bash
chmod +x init-project_EN.sh
./init-project_EN.sh
```

---

## Quick Start (3 Steps)

### Step 1: Read Documentation (30 minutes)
```
1. QUICK_GUIDE_EN.md     # Understand how to use docs (10 min)
2. README_EN.md          # Understand details (20 min)
```

### Step 2: Initialize Project (10 minutes)
```bash
# 1. Run initialization script
chmod +x init-project_EN.sh
./init-project_EN.sh

# 2. Install dependencies
cd frontend && npm install
cd ../backend && pip install -r requirements.txt
```

### Step 3: Start Development (Immediately)
```bash
# 1. Open Claude Code
# 2. Let it read QUICK_GUIDE_EN.md
# 3. Start task 0.1
```

---

## Document Importance Ranking

**Must read for each development**:
1. QUICK_GUIDE_EN.md [5 STARS]

**Read when project starts**:
1. README_EN.md [5 STARS]

**Run once**:
1. init-project_EN.sh [4 STARS]

**Place in project root**:
1. .clinerules_EN [4 STARS]

---

## Usage Suggestions

### For You (Project Owner)
1. First read QUICK_GUIDE_EN.md (understand document system)
2. Then read README_EN.md (understand all details)
3. Run init-project_EN.sh (initialize project)

### For Claude Code
Instructions before each development:
```
Please read QUICK_GUIDE_EN.md, understand current task, then start development.
```

---

## Key Changes from Original Requirements

### 1. Language: English
- All code comments in English
- All variable/function names in English
- All documentation in English
- User-facing text can be localized later

### 2. No Emojis
- Removed all emojis from documentation
- Use clear text markers instead
- Cleaner, more professional appearance

### 3. Open Source Icons
- Using **Lucide React** icon library
- 1000+ icons available
- Tree-shakable, lightweight
- MIT license

**Icon usage example**:
```tsx
import { 
  Image,      // Image tools
  FileText,   // Text tools
  File,       // PDF tools
  Wand2,      // AI tools
  Youtube,    // YouTube search
  Upload,     // Upload
  Download,   // Download
  Check,      // Success
  X,          // Error
  AlertCircle // Warning
} from 'lucide-react'

<Image className="w-6 h-6" />
<Upload className="w-4 h-4" />
```

---

## Document Quality Assurance

All documents include:
- Clear structure and table of contents
- Detailed usage instructions
- Practical code examples
- FAQ sections
- Quick command reference
- English language throughout
- No emojis
- Professional appearance

---

## File Downloads

You can download documents from these locations:

0. **claude.md** - [View](computer:///tmp/claude.md) **START HERE**
1. **README_EN.md** - [View](computer:///tmp/README_EN.md)
2. **QUICK_GUIDE_EN.md** - [View](computer:///tmp/QUICK_GUIDE_EN.md)
3. **UTF8_ENCODING_GUIDE.md** - [View](computer:///tmp/UTF8_ENCODING_GUIDE.md)
4. **UTF8_CHECKLIST.md** - [View](computer:///tmp/UTF8_CHECKLIST.md)
5. **.clinerules_EN** - [View](computer:///tmp/.clinerules_EN)
6. **init-project_EN.sh** - [View](computer:///tmp/init-project_EN.sh)

---

## Technical Stack Summary

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Animation**: Framer Motion
- **Icons**: Lucide React
- **State**: Zustand
- **Fonts**: Press Start 2P (pixel), Roboto (body)

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Async**: asyncio
- **Image**: Pillow, pillow-avif
- **PDF**: PyPDF2, pdf2image, python-docx
- **Validation**: Pydantic

### Deployment
- **Platform**: Synology NAS
- **Container**: Docker + Docker Compose
- **Port**: 8888

---

## Next Actions

**What you need to do now**:

1. Download all English documents
2. Read in order: QUICK_GUIDE_EN → README_EN
3. Run init-project_EN.sh to initialize project
4. Place .clinerules_EN in project root
5. Let Claude Code read QUICK_GUIDE_EN.md and start development

**Estimated time**: Can start development within 1 hour!

---

## If You Have Questions

If you have any questions:
1. Check QUICK_GUIDE_EN.md FAQ section
2. Check README_EN.md detailed explanation
3. Continue to ask me!

**Happy coding!**

---

**Total Documentation Size**: ~103KB
**Total Documents**: 7 core documents
**Language**: English
**Emojis**: None
**Icon Library**: Lucide React
**Encoding**: UTF-8 (strictly enforced)

---

**Last Updated**: 2025-11-15
**Document Version**: v2.2 (English + UTF-8 + claude.md)
**Current Phase**: P0 - Framework Setup
**Current Phase**: P0 - Framework Setup
