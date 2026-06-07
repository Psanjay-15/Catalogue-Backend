from __future__ import annotations
from pathlib import Path
from typing import Union
from app.core.exceptions import ValidationError
from app.extractors.base import Extractor


class TxtExtractor(Extractor):
    def extract(self, source: Union[str, Path]) -> str:
        if isinstance(source, Path) or (isinstance(source, str) and Path(source).is_file()):
            text = Path(source).read_text(encoding="utf-8").strip()
        else:
            text = str(source).strip()
        if not text:
            raise ValidationError("Input is empty.")
        return text

    def extract_bytes(self, data: bytes) -> str:
        text = data.decode("utf-8", errors="replace").strip()
        if not text:
            raise ValidationError("Input is empty.")
        return text
