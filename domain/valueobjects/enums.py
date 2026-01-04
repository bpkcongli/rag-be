from enum import Enum


class FileType(str, Enum):
    PDF = "PDF"
    DOCX = "DOCX"
    HTML = "HTML"


class DocumentStatus(str, Enum):
    UPLOADED = "UPLOADED"
    INDEXING = "INDEXING"
    INDEXED = "INDEXED"
    FAILED = "FAILED"
