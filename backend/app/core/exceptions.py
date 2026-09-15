from fastapi import HTTPException, status

class HireLensException(Exception):
    """Base exception class for HireLens application."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class FileValidationError(HireLensException):
    """Raised when file validation (extension, size, MIME type, magic bytes) fails."""
    def __init__(self, message: str):
        super().__init__(message)

class FileExtractionError(HireLensException):
    """Raised when text extraction from PDF or DOCX fails or document is corrupted/encrypted."""
    def __init__(self, message: str):
        super().__init__(message)
