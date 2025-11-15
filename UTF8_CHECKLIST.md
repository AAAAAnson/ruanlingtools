# UTF-8 Quick Checklist

> Print this and keep it next to your monitor

---

## Before Writing ANY Python File

```python
# -*- coding: utf-8 -*-
```

MUST be the first line of EVERY .py file!

---

## File Operations Quick Reference

### Reading Files
```python
# Text files
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# CSV files (removes BOM)
with open('file.csv', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# JSON files
import json
with open('file.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
```

### Writing Files
```python
# Text files
with open('file.txt', 'w', encoding='utf-8') as f:
    f.write(content)

# JSON files
with open('file.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

---

## FastAPI Quick Setup

### main.py Template
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

app = FastAPI()

# UTF-8 in all responses
@app.middleware("http")
async def add_utf8(request, call_next):
    response = await call_next(request)
    if "json" in response.headers.get("content-type", ""):
        response.headers["content-type"] = "application/json; charset=utf-8"
    return response
```

---

## Common Mistakes (AVOID THESE!)

### DON'T
```python
# Missing encoding declaration
import os  # WRONG!

# Missing encoding in file operations
with open('file.txt', 'r') as f:  # WRONG!

# Using ensure_ascii=True
json.dumps(data, ensure_ascii=True)  # WRONG!
```

### DO
```python
# -*- coding: utf-8 -*-  # CORRECT!
import os

# Always specify encoding
with open('file.txt', 'r', encoding='utf-8') as f:  # CORRECT!

# Don't escape non-ASCII
json.dumps(data, ensure_ascii=False)  # CORRECT!
```

---

## Testing Your Code

Quick test:
```python
# -*- coding: utf-8 -*-
test = "中文 English 日本語 한국어"
with open('test.txt', 'w', encoding='utf-8') as f:
    f.write(test)
with open('test.txt', 'r', encoding='utf-8') as f:
    assert f.read() == test
print("UTF-8 OK!")
```

---

## Emergency Fixes

### If you see garbled text:
1. Check file has `# -*- coding: utf-8 -*-`
2. Check all `open()` calls have `encoding='utf-8'`
3. Check FastAPI middleware is set
4. Restart your server

### If Windows shows errors:
```python
# -*- coding: utf-8 -*-
import sys
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')
```

---

## Pre-Commit Checklist

- [ ] All .py files start with `# -*- coding: utf-8 -*-`
- [ ] All `open()` calls have `encoding='utf-8'`
- [ ] JSON dumps use `ensure_ascii=False`
- [ ] FastAPI has UTF-8 middleware
- [ ] Tested with non-English characters
- [ ] No encoding errors in console

---

**Remember**: When in doubt, specify UTF-8!

**Quick command to check**:
```bash
# Check for missing UTF-8 declarations
grep -L "coding: utf-8" backend/**/*.py
```
