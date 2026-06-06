from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundError
from app.db.models.template import Template
from app.db.repositories.template_repo import template_repo
from app.domain.schemas.responses import TemplateResponse



TEMPLATE_CATALOG: dict[str, tuple[str, str, str]] = {
    # id              (name,                                  kind,           description)
    "ai":           ("AI Freestyle",                          "ai-freestyle", "Gemini designs a unique one-page brochure for your catalog. Varies each run."),
    "modern":       ("Modern",                                "fixed",        "Bold sans-serif, orange accent, image-first product cards."),
    "luxury":       ("Luxury",                                "fixed",        "Playfair serif, gold accents, refined editorial feel."),
    "minimal":      ("Minimal",                               "fixed",        "Monochrome, restrained typography, lots of whitespace."),
    "corporate":    ("Corporate",                             "fixed",        "Navy gradient hero, structured grid, blue accents."),
    "creative":     ("Creative",                              "fixed",        "Vivid gradients, hand-drawn accents, hard-offset shadows."),
    "showcase":     ("Showcase",                              "fixed",        "ONE featured product hero + supporting product cards."),
    "product-grid": ("Product Grid",                          "fixed",        "Tight 3-column product grid — for catalogs with many products."),
    "service":      ("Service",                               "fixed",        "Process steps + service offerings, designed for service businesses."),
    "magazine":     ("Magazine",                              "fixed",        "Editorial 3-column spread with masthead and pull-quotes."),
}


class TemplateService:
    async def list_templates(self, db: AsyncSession) -> list[TemplateResponse]:
        rows = await template_repo.list_all(db)
        return [self._to_response(t) for t in rows]

    async def get_template(self, db: AsyncSession, template_id: str) -> TemplateResponse:
        row = await template_repo.get(db, template_id)
        if row is None:
            raise NotFoundError(f"Template '{template_id}' not found")
        return self._to_response(row)

    @staticmethod
    def _to_response(t: Template) -> TemplateResponse:
        return TemplateResponse(
            id=t.id,
            name=t.name,
            description=t.description,
            kind=t.kind,
            sample_html=t.sample_html,
        )


template_service = TemplateService()
