from __future__ import annotations
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.config import settings
from app.core.exceptions import RenderError
from app.domain.schemas.catalog import PAGE_DIMENSIONS_MM, Catalog
from app.renderers.base import Renderer
from app.renderers.image_url import image_url


class JinjaRenderer(Renderer):
    def __init__(self, template_name: str) -> None:
        self.template_name = template_name
        self.env = Environment(
            loader=FileSystemLoader(str(settings.templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.env.filters["image_url"] = image_url

    async def render(
        self,
        catalog: Catalog,
        theme: str,
        page_size: str,
    ) -> str:
        try:
            width_mm, height_mm = PAGE_DIMENSIONS_MM[page_size]
            template = self.env.get_template(f"{self.template_name}.html")
            return template.render(
                catalog=catalog,
                theme=theme,
                page_size=page_size,
                page_width_mm=width_mm,
                page_height_mm=height_mm,
            )
        except Exception as e:
            raise RenderError(f"Jinja render of '{self.template_name}' failed: {e}") from e
