from __future__ import annotations
import uuid
from app.core.database import get_database
from app.core.logging import get_logger
from app.db.models.catalog import (
    STATUS_DONE,
    STATUS_EXPORTING,
    STATUS_EXTRACTING,
    STATUS_FAILED,
    STATUS_REFINING,
    STATUS_RENDERING,
)
from app.core.sanitize import sanitize_html
from app.db.repositories.catalog_repo import catalog_repo
from app.db.repositories.template_repo import template_repo
from app.exporters.pdf_exporter import PdfExporter
from app.llm.factory import get_llm_provider
from app.renderers.freestyle_renderer import FreestyleRenderer


log = get_logger(__name__)


class CatalogService:

    async def run_pipeline(self, catalog_id: uuid.UUID) -> None:
        db = get_database()
        cat = await catalog_repo.get(db, catalog_id)
        if cat is None:
            log.error("catalog %s vanished before pipeline started", catalog_id)
            return

        try:
            # ---- 1. EXTRACT ------------------------------------------------
            await catalog_repo.update(db, catalog_id, status=STATUS_EXTRACTING)
            raw_text = cat.source_text

            # ---- 2. REFINE -------------------------------------------------
            await catalog_repo.update(db, catalog_id, status=STATUS_REFINING)
            llm = get_llm_provider(cat.llm_provider)
            refined = await llm.refine_catalog(raw_text, cat.style)

            # ---- 3. RENDER -------------------------------------------------
            await catalog_repo.update(
                db,
                catalog_id,
                status=STATUS_RENDERING,
                refined_json=refined.model_dump(),
            )
            style_hint = None
            if cat.template_id and cat.template_id != "ai":
                tpl = await template_repo.get(db, cat.template_id)
                if tpl:
                    style_hint = f"{tpl.name} - {tpl.description}"
            renderer = FreestyleRenderer(llm, style_hint=style_hint)
            html = await renderer.render(refined, cat.theme, cat.page_size)
            html = sanitize_html(html)

            # ---- 4. EXPORT -------------------------------------------------
            # HTML is already persisted in MongoDB; render the PDF to bytes
            # and store it there too. Nothing touches local disk.
            await catalog_repo.update(db, catalog_id, status=STATUS_EXPORTING, html=html)

            pdf_bytes = await PdfExporter().render(html)

            await catalog_repo.update(
                db,
                catalog_id,
                status=STATUS_DONE,
                pdf_bytes=pdf_bytes,
            )
            log.info("catalog %s done", catalog_id)

        except Exception as e:
            log.exception("catalog %s failed", catalog_id)
            await catalog_repo.update(
                db,
                catalog_id,
                status=STATUS_FAILED,
                error=str(e)[:1000],
            )


catalog_service = CatalogService()
