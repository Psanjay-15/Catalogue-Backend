from __future__ import annotations
from app.core.exceptions import UnsupportedFormatError
from app.domain.schemas.catalog import VALID_TEMPLATES
from app.llm.base import LLMProvider
from app.renderers.base import Renderer
from app.renderers.freestyle_renderer import FreestyleRenderer
from app.renderers.jinja_renderer import JinjaRenderer


def get_renderer(template_name: str, *, llm: LLMProvider | None = None) -> Renderer:
    if template_name not in VALID_TEMPLATES:
        raise UnsupportedFormatError(
            f"Unknown template '{template_name}'. Available: {sorted(VALID_TEMPLATES)}"
        )
    if template_name == "ai":
        if llm is None:
            raise ValueError("Freestyle 'ai' template requires an LLMProvider.")
        return FreestyleRenderer(llm)
    return JinjaRenderer(template_name)
