from __future__ import annotations
from app.core.exceptions import RenderError
from app.domain.schemas.catalog import PAGE_DIMENSIONS_MM, Catalog
from app.llm.base import LLMProvider
from app.renderers.base import Renderer


class FreestyleRenderer(Renderer):

    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    async def render(
        self,
        catalog: Catalog,
        theme: str,
        page_size: str,
    ) -> str:
        try:
            width_mm, height_mm = PAGE_DIMENSIONS_MM[page_size]
            return await self.llm.freestyle_html(
                catalog=catalog,
                theme=theme,
                page_size=page_size,
                width_mm=width_mm,
                height_mm=height_mm,
            )
        except Exception as e:
            raise RenderError(f"Freestyle render failed: {e}") from e
