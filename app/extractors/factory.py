from __future__ import annotations
from pathlib import Path
from typing import Union
from app.core.exceptions import UnsupportedFormatError
from app.extractors.base import Extractor
from app.extractors.docx import DocxExtractor
from app.extractors.pdf import PdfExtractor
from app.extractors.txt import TxtExtractor


_REGISTRY: dict[str, type[Extractor]] = {
    ".pdf":  PdfExtractor,
    ".docx": DocxExtractor,
    ".txt":  TxtExtractor,
}


def for_source(source: Union[str, Path]) -> Extractor:
    if isinstance(source, Path) or (isinstance(source, str) and Path(source).is_file()):
        ext = Path(source).suffix.lower()
        if ext not in _REGISTRY:
            raise UnsupportedFormatError(
                f"Unsupported file type: {ext}. Supported: {sorted(_REGISTRY)}"
            )
        return _REGISTRY[ext]()
    return TxtExtractor()


def extract_text(source: Union[str, Path]) -> str:
    return for_source(source).extract(source)


def extract_text_from_bytes(filename: str, data: bytes) -> str:
    """Extract plain text from an uploaded file's bytes, dispatching by its
    extension. In-memory only - no path is derived from user input."""
    ext = Path(filename or "").suffix.lower()
    extractor_cls = _REGISTRY.get(ext)
    if extractor_cls is None:
        raise UnsupportedFormatError(
            f"Unsupported file type: {ext or '?'}. Supported: {sorted(_REGISTRY)}"
        )
    return extractor_cls().extract_bytes(data)
