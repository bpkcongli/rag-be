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


class ChunkingStrategy(str, Enum):
    SEMANTIC_SLIDING_WINDOW = "SEMANTIC_SLIDING_WINDOW"


class VectorIndexStatus(str, Enum):
    BUILDING = "BUILDING"
    READY = "READY"
    FAILED = "FAILED"


