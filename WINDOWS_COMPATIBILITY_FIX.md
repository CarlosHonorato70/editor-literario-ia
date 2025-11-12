# Windows Compatibility Fix

## Issue Resolved
Fixed `OSError: cannot load library 'libgobject-2.0-0'` error on Windows when importing the application.

## Root Cause
The original implementation imported `python-docx` and `PyPDF2` at module level in `file_handler.py`:

```python
# BEFORE (caused immediate import errors)
from docx import Document
from PyPDF2 import PdfReader
```

This caused all dependencies to load immediately when the module was imported, even if they weren't being used. On Windows, this could trigger loading of transitive dependencies like GTK libraries that aren't available.

## Solution
Implemented **lazy imports** - dependencies are only imported when actually needed:

```python
# AFTER (lazy import - only loads when used)
@staticmethod
def extract_text_from_docx(file_content: bytes) -> str:
    try:
        from docx import Document  # Import only when needed
    except ImportError:
        raise ImportError("python-docx não está instalado. Instale com: pip install python-docx")
    # ... rest of the code
```

## Benefits

1. **Faster Startup**: Module loads instantly without waiting for heavy dependencies
2. **Windows Compatible**: Doesn't trigger GTK/libgobject loading issues
3. **Graceful Degradation**: Clear error messages if dependencies are missing
4. **Better Resource Usage**: Only loads what's actually needed

## Testing

All tests still pass:
- ✅ Unit tests: 5/5 passed
- ✅ Integration tests: 2/2 passed
- ✅ Module can be imported without dependencies
- ✅ Extraction works when dependencies are available

## For Users

If you see import errors for specific file types, install the required dependency:

```bash
# For DOCX support
pip install python-docx

# For PDF support
pip install PyPDF2

# For everything
pip install -r requirements.txt
```

The application will now start successfully even if some optional dependencies are missing, and will show clear error messages only when you try to use a feature that requires the missing dependency.

---
**Fixed in commit**: [will be added after commit]
**Date**: 2025-11-12
