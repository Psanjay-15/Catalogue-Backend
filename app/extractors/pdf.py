from __future__ import annotations
from pathlib import Path
from typing import Union
from app.extractors.base import Extractor


class PdfExtractor(Extractor):
    def extract(self, source: Union[str, Path]) -> str:
        import pymupdf

        path = Path(source)
        doc = pymupdf.open(str(path))
        try:
            parts = [p.get_text().strip() for p in doc if p.get_text().strip()]
            return "\n\n".join(parts).strip()
        finally:
            doc.close()
