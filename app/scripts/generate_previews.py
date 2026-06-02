from __future__ import annotations
import asyncio
import json
from pathlib import Path
from app.config import settings
from app.core.database import AsyncSessionLocal
from app.core.logging import configure_logging, get_logger
from app.db.repositories.template_repo import template_repo
from app.domain.schemas.catalog import VALID_TEMPLATES, Catalog
from app.domain.services.template_service import TEMPLATE_CATALOG
from app.exporters.png_exporter import PngExporter
from app.extractors.factory import extract_text
from app.llm.factory import get_llm_provider
from app.renderers.factory import get_renderer


SAMPLE_INPUT_PATH    = settings.templates_dir.parent / "samples" / "sample_input.txt"
CANONICAL_JSON_PATH  = settings.templates_dir.parent / "samples" / "sample_catalog.json"


async def _load_or_build_sample_catalog() -> Catalog:

    log = get_logger("preview")

    if CANONICAL_JSON_PATH.exists():
        log.info("using cached canonical catalog at %s", CANONICAL_JSON_PATH)
        data = json.loads(CANONICAL_JSON_PATH.read_text(encoding="utf-8"))
        return Catalog.model_validate(data)

    log.info("calling Gemini once to build canonical catalog from %s", SAMPLE_INPUT_PATH)
    raw_text = extract_text(SAMPLE_INPUT_PATH)
    llm = get_llm_provider(settings.default_llm_provider)
    cat = await llm.refine_catalog(raw_text, style="modern")
    CANONICAL_JSON_PATH.write_text(cat.model_dump_json(indent=2), encoding="utf-8")
    log.info("cached canonical catalog to %s", CANONICAL_JSON_PATH)
    return cat


async def _render_preview(template_id: str, sample: Catalog) -> tuple[str, Path]:
   
    llm = get_llm_provider(settings.default_llm_provider) if template_id == "ai" else None
    renderer = get_renderer(template_id, llm=llm)
    html = await renderer.render(sample, theme="light", page_size="A4")

    html_path = settings.samples_dir / f"{template_id}.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")

    png_path = settings.previews_dir / f"{template_id}.png"
    await PngExporter().export(html, png_path)

    return html, png_path


async def main() -> None:
    configure_logging()
    log = get_logger("generate_previews")

    sample = await _load_or_build_sample_catalog()
    log.info("brand_name=%s, products=%d", sample.brand_name, len(sample.products))

    async with AsyncSessionLocal() as db:
        for template_id in sorted(VALID_TEMPLATES):
            try:
                log.info("rendering preview for %s ...", template_id)
                html, png_path = await _render_preview(template_id, sample)
            except Exception as e:
                log.error("FAILED %s: %s", template_id, e)
                continue

            name, kind, description = TEMPLATE_CATALOG.get(
                template_id,
                (template_id.title(), "fixed", ""),
            )
            await template_repo.upsert_by_id(
                db,
                template_id,
                defaults={
                    "name":         name,
                    "description":  description,
                    "kind":         kind,
                    "sample_html":  html,
                    "preview_path": f"previews/{template_id}.png",
                },
            )
            log.info("  -> seeded templates.%s (preview %s)", template_id, png_path.name)

    log.info("done. Visit http://localhost:8000/api/v1/templates to see the list.")


if __name__ == "__main__":
    asyncio.run(main())
