from __future__ import annotations
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import NotFoundError
from app.db.models.catalog import utcnow
from app.db.models.template import Template
from app.db.repositories.template_repo import template_repo
from app.domain.schemas.responses import TemplateResponse


def default_sample_html(name: str, description: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{name} template</title>
  <style>
    @page {{ size: A4; margin: 0; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Inter, Arial, sans-serif; background: #e7e3da; }}
    .page {{
      width: 210mm;
      height: 297mm;
      overflow: hidden;
      padding: 20mm;
      background: #faf8f2;
      color: #17151f;
      display: flex;
      flex-direction: column;
      gap: 14mm;
    }}
    .hero {{ border-bottom: 1px solid #cfc7b8; padding-bottom: 12mm; }}
    .eyebrow {{ text-transform: uppercase; letter-spacing: .12em; color: #6d5efc; font-size: 9px; font-weight: 700; }}
    h1 {{ margin: 4mm 0 3mm; font-size: 34px; line-height: 1; }}
    p {{ margin: 0; font-size: 12px; line-height: 1.45; max-width: 120mm; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 6mm; }}
    .card {{ border: 1px solid #d8d1c4; padding: 6mm; min-height: 42mm; }}
    .card strong {{ display: block; margin-bottom: 3mm; }}
    .footer {{ margin-top: auto; font-size: 10px; color: #625d70; }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <div class="eyebrow" contenteditable="true">{name}</div>
      <h1 contenteditable="true">Template preview</h1>
      <p contenteditable="true">{description}</p>
    </section>
    <section class="grid">
      <div class="card"><strong contenteditable="true">Hero</strong><p contenteditable="true">A strong opening section for the catalog story.</p></div>
      <div class="card"><strong contenteditable="true">Products</strong><p contenteditable="true">Compact product cards sized for a single page.</p></div>
      <div class="card"><strong contenteditable="true">Contact</strong><p contenteditable="true">A clear call-to-action and business details.</p></div>
    </section>
    <footer class="footer" contenteditable="true">Generated preview placeholder</footer>
  </main>
</body>
</html>"""



TEMPLATE_CATALOG: dict[str, tuple[str, str, str]] = {
    # id              (name,                                  kind,           description)
    "ai":           ("AI Freestyle",                          "ai-freestyle", "Gemini designs a unique one-page brochure for your catalog. Varies each run."),
    "modern":       ("Modern",                                "fixed",        "Bold sans-serif, orange accent, image-first product cards."),
    "luxury":       ("Luxury",                                "fixed",        "Playfair serif, gold accents, refined editorial feel."),
    "minimal":      ("Minimal",                               "fixed",        "Monochrome, restrained typography, lots of whitespace."),
    "corporate":    ("Corporate",                             "fixed",        "Navy gradient hero, structured grid, blue accents."),
    "creative":     ("Creative",                              "fixed",        "Vivid gradients, hand-drawn accents, hard-offset shadows."),
    "showcase":     ("Showcase",                              "fixed",        "ONE featured product hero + supporting product cards."),
    "product-grid": ("Product Grid",                          "fixed",        "Tight 3-column product grid - for catalogs with many products."),
    "service":      ("Service",                               "fixed",        "Process steps + service offerings, designed for service businesses."),
    "magazine":     ("Magazine",                              "fixed",        "Editorial 3-column spread with masthead and pull-quotes."),
}


class TemplateService:
    async def ensure_default_templates(self, db: AsyncIOMotorDatabase) -> None:
        for template_id, (name, kind, description) in TEMPLATE_CATALOG.items():
            existing = await template_repo.get(db, template_id)
            if existing is not None:
                continue
            await template_repo.upsert_by_id(
                db,
                template_id,
                {
                    "name": name,
                    "description": description,
                    "kind": kind,
                    "sample_html": default_sample_html(name, description),
                    "created_at": utcnow(),
                },
            )

    async def list_templates(self, db: AsyncIOMotorDatabase) -> list[TemplateResponse]:
        await self.ensure_default_templates(db)
        rows = await template_repo.list_all(db)
        return [self._to_response(t) for t in rows]

    async def get_template(self, db: AsyncIOMotorDatabase, template_id: str) -> TemplateResponse:
        await self.ensure_default_templates(db)
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
