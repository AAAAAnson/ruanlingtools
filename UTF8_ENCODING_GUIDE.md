# UTF-8 Encoding Best Practices

> CRITICAL: This document contains mandatory encoding standards to prevent encoding issues across different platforms and systems.

---

## Why UTF-8 Encoding Matters

### Common Problems Without Proper UTF-8 Handling
- Chinese characters display as garbled text (乱码)
- Files cannot be read on different operating systems
- Database queries fail with encoding errors
- API responses show incorrect characters
- Logs become unreadable
- CSV/Excel exports corrupted

### Our Solution
**Strict UTF-8 everywhere** - from source code to database to API responses.

---

## Mandatory Standards

### 1. Python File Declaration

**EVERY Python file must start with:**
```python
# -*- coding: utf-8 -*-
```

**Complete file template:**
```python
# -*- coding: utf-8 -*-
"""
Module: image_service.py
Description: Image processing service
"""
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class ImageService:
    """Image processing service"""
    
    def __init__(self):
        pass
```

### 2. File Operations

**ALWAYS specify encoding='utf-8':**

```python
# -*- coding: utf-8 -*-

# Reading text files
def read_file(filepath: str) -> str:
    """Read file with UTF-8 encoding"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

# Writing text files
def write_file(filepath: str, content: str) -> None:
    """Write file with UTF-8 encoding"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# Reading CSV (remove BOM if present)
def read_csv(filepath: str) -> str:
    """Read CSV with UTF-8 encoding, removing BOM"""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        return f.read()

# Reading JSON
import json

def read_json(filepath: str) -> dict:
    """Read JSON with UTF-8 encoding"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(filepath: str, data: dict) -> None:
    """Write JSON with UTF-8 encoding"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

### 3. FastAPI Configuration

**main.py setup:**
```python
# -*- coding: utf-8 -*-
import sys
import os

# Set environment encoding
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

# Reconfigure stdout/stderr for UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Soft Collar Toolbox API",
    description="API with UTF-8 support",
    version="0.1.0"
)

# Add UTF-8 charset to all JSON responses
@app.middleware("http")
async def add_utf8_charset(request, call_next):
    response = await call_next(request)
    if "application/json" in response.headers.get("content-type", ""):
        response.headers["content-type"] = "application/json; charset=utf-8"
    return response

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Response format with UTF-8:**
```python
# -*- coding: utf-8 -*-
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Any

router = APIRouter()

@router.get("/test")
async def test_utf8():
    """Test UTF-8 response"""
    data = {
        "message": "成功",  # Chinese characters
        "english": "Success",
        "mixed": "混合文本 Mixed Text"
    }
    
    return JSONResponse(
        content=data,
        media_type="application/json; charset=utf-8"
    )

# File download with UTF-8 filename
@router.get("/download/{filename}")
async def download_file(filename: str):
    """Download file with UTF-8 filename"""
    from urllib.parse import quote
    
    # Encode filename for Content-Disposition header
    encoded_filename = quote(filename.encode('utf-8'))
    
    return FileResponse(
        path=f"outputs/{filename}",
        filename=filename,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )
```

### 4. Database Configuration

**SQLite:**
```python
# -*- coding: utf-8 -*-
import sqlite3

def get_sqlite_connection(db_path: str):
    """Get SQLite connection with UTF-8 support"""
    conn = sqlite3.connect(db_path)
    conn.text_factory = str  # Ensure UTF-8 strings
    conn.execute("PRAGMA encoding = 'UTF-8'")
    return conn

# Example usage
conn = get_sqlite_connection('toolbox.db')
cursor = conn.cursor()

# Create table with UTF-8 collation
cursor.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY,
        filename TEXT COLLATE NOCASE,
        content TEXT
    )
''')

# Insert UTF-8 data
cursor.execute(
    "INSERT INTO files (filename, content) VALUES (?, ?)",
    ("测试文件.txt", "这是测试内容")
)

conn.commit()
conn.close()
```

**PostgreSQL:**
```python
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine

# Include client_encoding in connection string
DATABASE_URL = "postgresql://user:pass@localhost:5432/dbname?client_encoding=utf8"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=True
)
```

### 5. Logging Configuration

**Setup UTF-8 logging:**
```python
# -*- coding: utf-8 -*-
import logging
import sys

def setup_logging():
    """Setup logging with UTF-8 encoding"""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with UTF-8
    file_handler = logging.FileHandler(
        'app.log',
        encoding='utf-8',
        mode='a'
    )
    file_handler.setFormatter(formatter)
    
    # Console handler with UTF-8
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Usage
logger = setup_logging()
logger.info("日志信息 Log message")
```

### 6. CSV and Excel Handling

**CSV with UTF-8:**
```python
# -*- coding: utf-8 -*-
import csv

def write_csv_utf8(filepath: str, data: list):
    """Write CSV with UTF-8 encoding"""
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerows(data)

def read_csv_utf8(filepath: str) -> list:
    """Read CSV with UTF-8 encoding"""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        return list(reader)

# Example
data = [
    ['姓名', 'Name', '年龄', 'Age'],
    ['张三', 'Zhang San', '25', '25'],
    ['李四', 'Li Si', '30', '30']
]

write_csv_utf8('output.csv', data)
```

**Excel with openpyxl:**
```python
# -*- coding: utf-8 -*-
from openpyxl import Workbook, load_workbook

def create_excel_utf8(filepath: str, data: list):
    """Create Excel file with UTF-8 support"""
    wb = Workbook()
    ws = wb.active
    
    # openpyxl handles UTF-8 automatically
    for row in data:
        ws.append(row)
    
    wb.save(filepath)

def read_excel_utf8(filepath: str) -> list:
    """Read Excel file with UTF-8 support"""
    wb = load_workbook(filepath)
    ws = wb.active
    
    data = []
    for row in ws.iter_rows(values_only=True):
        data.append(row)
    
    return data
```

### 7. PDF Text Extraction

**Extract text with UTF-8:**
```python
# -*- coding: utf-8 -*-
from PyPDF2 import PdfReader

def extract_pdf_text(filepath: str) -> str:
    """Extract text from PDF with UTF-8 encoding"""
    reader = PdfReader(filepath)
    
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    # Ensure UTF-8
    return text.encode('utf-8', errors='ignore').decode('utf-8')

# Save extracted text
def save_pdf_text(pdf_path: str, output_path: str):
    """Extract and save PDF text"""
    text = extract_pdf_text(pdf_path)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
```

### 8. Image Processing with Pillow

**Handle text in images:**
```python
# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont

def add_text_to_image(
    image_path: str,
    text: str,
    output_path: str
):
    """Add UTF-8 text to image"""
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    # Use font that supports UTF-8
    try:
        font = ImageFont.truetype("NotoSansSC-Regular.ttf", 32)
    except:
        font = ImageFont.load_default()
    
    # Draw text
    draw.text((10, 10), text, font=font, fill=(255, 255, 255))
    
    # Save
    img.save(output_path)

# Example
add_text_to_image(
    "input.jpg",
    "测试文字 Test Text",
    "output.jpg"
)
```

---

## Platform-Specific Considerations

### Windows
```python
# -*- coding: utf-8 -*-
import sys
import locale

# Check system encoding
print(f"System encoding: {sys.getdefaultencoding()}")
print(f"Filesystem encoding: {sys.getfilesystemencoding()}")
print(f"Locale encoding: {locale.getpreferredencoding()}")

# Force UTF-8 on Windows
if sys.platform == 'win32':
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
```

### Linux/Mac
```python
# -*- coding: utf-8 -*-
import sys

# Usually UTF-8 by default, but verify
assert sys.getdefaultencoding() == 'utf-8', "System must use UTF-8"
```

### Docker
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set UTF-8 environment
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONIOENCODING=utf-8

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Testing UTF-8 Handling

**Test file:**
```python
# -*- coding: utf-8 -*-
"""
test_encoding.py - Test UTF-8 encoding
"""
import sys
import os

def test_basic_encoding():
    """Test basic UTF-8 encoding"""
    test_string = "测试 Test 테스트 テスト"
    
    # Test string encoding
    assert isinstance(test_string, str)
    encoded = test_string.encode('utf-8')
    decoded = encoded.decode('utf-8')
    assert test_string == decoded
    
    print("✓ Basic encoding test passed")

def test_file_operations():
    """Test file operations with UTF-8"""
    test_content = "混合内容 Mixed Content\n日本語\n한국어"
    test_file = "test_utf8.txt"
    
    # Write
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    # Read
    with open(test_file, 'r', encoding='utf-8') as f:
        read_content = f.read()
    
    assert test_content == read_content
    
    # Cleanup
    os.remove(test_file)
    
    print("✓ File operations test passed")

def test_json_encoding():
    """Test JSON encoding"""
    import json
    
    data = {
        "chinese": "中文",
        "english": "English",
        "japanese": "日本語",
        "korean": "한국어"
    }
    
    # Serialize with ensure_ascii=False
    json_str = json.dumps(data, ensure_ascii=False)
    
    # Deserialize
    loaded = json.loads(json_str)
    
    assert data == loaded
    
    print("✓ JSON encoding test passed")

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print(f"Default encoding: {sys.getdefaultencoding()}")
    print(f"Filesystem encoding: {sys.getfilesystemencoding()}")
    print()
    
    test_basic_encoding()
    test_file_operations()
    test_json_encoding()
    
    print("\n✓ All UTF-8 tests passed!")
```

---

## Checklist

Before deploying any code, verify:

- [ ] All Python files have `# -*- coding: utf-8 -*-` declaration
- [ ] All file operations specify `encoding='utf-8'`
- [ ] FastAPI responses include `charset=utf-8`
- [ ] Database connections specify UTF-8 encoding
- [ ] Logging configured with UTF-8
- [ ] CSV files use `encoding='utf-8-sig'` to remove BOM
- [ ] JSON serialization uses `ensure_ascii=False`
- [ ] Docker environment sets `LANG=C.UTF-8`
- [ ] All tests pass with multi-language content
- [ ] File downloads have properly encoded filenames

---

## Quick Reference

```python
# File template
# -*- coding: utf-8 -*-

# File operations
with open('file.txt', 'r', encoding='utf-8') as f:

# CSV with BOM removal
with open('file.csv', 'r', encoding='utf-8-sig') as f:

# JSON without ASCII escaping
json.dumps(data, ensure_ascii=False)

# FastAPI response
JSONResponse(content=data, media_type="application/json; charset=utf-8")

# Logging
logging.FileHandler('app.log', encoding='utf-8')

# Database
sqlite3.connect(db).text_factory = str
```

---

**Last Updated**: 2025-11-15
**Version**: 1.0
**Status**: Mandatory for all development
