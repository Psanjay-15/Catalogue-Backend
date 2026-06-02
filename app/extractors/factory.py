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
