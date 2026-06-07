from __future__ import annotations
from pathlib import Path
from typing import Union
from app.extractors.base import Extractor


class PdfExtractor(Extractor):
    def extract(self, source: Union[str, Path]) -> str:
        return self.extract_bytes(Path(source).read_bytes())

    def extract_bytes(self, data: bytes) -> str:
        import pymupdf

        doc = pymupdf.open(stream=data, filetype="pdf")
        try:
            parts = [p.get_text().strip() for p in doc if p.get_text().strip()]
            return "\n\n".join(parts).strip()
        finally:
            doc.close()
