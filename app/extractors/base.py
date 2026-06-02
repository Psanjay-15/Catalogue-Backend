from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union


class Extractor(ABC):

    @abstractmethod
    def extract(self, source: Union[str, Path]) -> str:
        """Return clean plain-text content extracted from `source`."""
        ...
