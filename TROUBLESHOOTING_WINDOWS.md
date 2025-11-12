# Troubleshooting: Windows libgobject-2.0-0 Error

## If you're still seeing the error after pulling the latest changes:

### Error Message
```
OSError: cannot load library 'libgobject-2.0-0': error 0x7e
```

## Solution Steps

### 1. Ensure You Have the Latest Code
```bash
git pull origin copilot/fix-file-upload-extraction
```

### 2. Clear Python Cache Files
Python caches compiled bytecode in `__pycache__` folders and `.pyc` files. These can cause old code to run even after you've updated:

```bash
# Windows PowerShell
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Force -Recurse
Get-ChildItem -Path . -Filter *.pyc -Recurse -Force | Remove-Item -Force

# Windows Command Prompt
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
del /s /q *.pyc

# Git Bash on Windows
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### 3. Restart Your Python Environment
If you're using a virtual environment or have Python shells open:

```bash
# Close all Python shells/terminals
# If using virtual environment, deactivate and reactivate:
deactivate
.\.venv\Scripts\activate  # Windows
```

### 4. Verify the Fix is Applied
Check that `modules/file_handler.py` has lazy imports:

```python
# The file should have imports INSIDE functions, not at the top:
@staticmethod
def extract_text_from_docx(file_content: bytes) -> str:
    try:
        from docx import Document  # ← This should be INSIDE the function
    except ImportError:
        raise ImportError("python-docx não está instalado...")
```

### 5. Alternative: Install GTK Dependencies (Not Recommended)
If you want WeasyPrint to work fully on Windows (not needed for file upload feature):

Download and install GTK for Windows from:
https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

However, **this is NOT necessary** for the file upload feature to work.

### 6. Test That It Works
```python
# This should work without errors:
from modules.file_handler import extract_text

text = "Hello World".encode('utf-8')
result, error = extract_text(text, "test.txt")
print(f"Result: {result}")  # Should print: Result: Hello World
```

## Why This Happened

The original code had:
```python
# OLD - Loaded immediately when module imported
from docx import Document
from PyPDF2 import PdfReader
```

This caused Python to load these libraries immediately, which then tried to load WeasyPrint dependencies (including libgobject-2.0-0) even though they weren't needed.

The fix uses lazy imports:
```python
# NEW - Only loads when function is called
def extract_text_from_docx(file_content: bytes):
    from docx import Document  # Loaded only when this function runs
    # ...
```

## Still Having Issues?

If you've tried all the above and still see the error:

1. **Check the error location**: Look at the full traceback - is the error really coming from `file_handler.py` or from somewhere else (like `exporter.py` which also uses WeasyPrint)?

2. **Try this test**:
   ```python
   # Run this in Python to see where the error comes from
   import sys
   import traceback
   
   try:
       sys.path.insert(0, '.')
       from modules.file_handler import extract_text
       print("✅ Import successful!")
   except Exception as e:
       print("❌ Import failed:")
       traceback.print_exc()
   ```

3. **Comment in the PR**: Share the full error traceback so we can see exactly which line is causing the problem.

## Expected Behavior After Fix

- ✅ Application starts without errors
- ✅ No libgobject-2.0-0 error on import
- ✅ File upload works for TXT, DOCX, and PDF
- ✅ Clear error message only if you try to upload a file type without its dependency installed

---
Updated: 2025-11-12
Commit: 56b06e2
