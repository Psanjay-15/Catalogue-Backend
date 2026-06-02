from __future__ import annotations
from abc import ABC, abstractmethod
from app.domain.schemas.catalog import Catalog


class Renderer(ABC):
    @abstractmethod
    async def render(
        self,
        catalog: Catalog,
        theme: str,
        page_size: str,
    ) -> str:
        """Render `catalog` into a complete HTML document string."""
        ...
