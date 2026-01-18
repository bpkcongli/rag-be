from __future__ import annotations

import os

from bs4 import BeautifulSoup

from domain.exceptions import UnsupportedFileTypeError
from domain.valueobjects.enums import FileType


def _normalize_text(text: str) -> str:
    # normalize whitespace
    return " ".join(text.split()).strip()


def extract_text_from_pdf(path: str) -> str:
    import fitz  # PyMuPDF

    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
        text += "\n"
    return _normalize_text(text)


def extract_text_from_docx(path: str) -> str:
    import docx

    d = docx.Document(path)
    parts: list[str] = []
    for p in d.paragraphs:
        if p.text:
            parts.append(p.text)
    return _normalize_text("\n".join(parts))


def extract_text_from_html(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    return _normalize_text(soup.get_text(separator=" "))


def extract_text(path: str, file_type: FileType) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    if file_type == FileType.PDF:
        return extract_text_from_pdf(path)
    if file_type == FileType.DOCX:
        return extract_text_from_docx(path)
    if file_type == FileType.HTML:
        return extract_text_from_html(path)

    raise UnsupportedFileTypeError(f"Unsupported file type: {file_type}")


