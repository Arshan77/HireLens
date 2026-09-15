import os
from pathlib import Path
from typing import Tuple

from app.core.config import (
    ALLOWED_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    MAX_FILE_SIZE_BYTES,
    MAGIC_BYTES,
)
from app.core.exceptions import FileValidationError


def sanitize_filename(filename: str) -> str:
    """
    Sanitize input filename to prevent Path Traversal attacks and normalize format.
    Strips directory separators and non-standard whitespace.
    """
    if not filename:
        raise FileValidationError("Filename cannot be empty.")
    
    # Strip path components to prevent path traversal
    safe_name = os.path.basename(filename).strip()
    # Replace dangerous characters
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in "._- ")
    if not safe_name:
        raise FileValidationError("Invalid filename after sanitization.")
    return safe_name


def validate_resume_file(filename: str, content_type: str, file_bytes: bytes) -> Tuple[str, str, int]:
    """
    Validate resume file against security rules:
    1. Extension whitelist check
    2. File size check (<= 5MB and > 0)
    3. MIME type check
    4. Magic-byte signature check
    
    Returns:
        Tuple[sanitized_filename, extension_without_dot, file_size_in_bytes]
    """
    safe_filename = sanitize_filename(filename)
    ext = Path(safe_filename).suffix.lower()
    
    # 1. Extension validation
    if ext not in ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"Unsupported file format '{ext}'. Only .pdf and .docx files are allowed."
        )
    
    # 2. File size validation
    file_size = len(file_bytes)
    if file_size == 0:
        raise FileValidationError("Uploaded file is empty (0 bytes).")
    
    if file_size > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES // (1024 * 1024)
        raise FileValidationError(
            f"File size ({file_size / (1024 * 1024):.2f} MB) exceeds maximum limit of {max_mb} MB."
        )
    
    # 3. MIME type validation (soft check with fallback to magic bytes)
    # Browsers sometimes send application/octet-stream for docx/pdf
    if content_type and content_type not in ALLOWED_MIME_TYPES and content_type != "application/octet-stream":
        raise FileValidationError(
            f"Invalid file MIME type '{content_type}'. Allowed types: PDF or Word DOCX."
        )
    
    # 4. Magic byte signature check
    expected_signatures = MAGIC_BYTES.get(ext, [])
    has_valid_signature = False
    
    for sig in expected_signatures:
        if file_bytes.startswith(sig):
            has_valid_signature = True
            break
            
    if not has_valid_signature:
        raise FileValidationError(
            f"File signature verification failed. File content does not match standard {ext.upper()} format."
        )
    
    file_type = ext.lstrip(".")
    return safe_filename, file_type, file_size
