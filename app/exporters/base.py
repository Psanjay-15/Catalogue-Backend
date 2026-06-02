from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union


class Exporter(ABC):
    @abstractmethod
    async def export(self, html: str, out_path: Union[str, Path]) -> Path:
        """Write `html` (or its rendered form) to `out_path`. Returns the path."""
        ...
