from __future__ import annotations
import uuid
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, Response
from app.api.v1.deps import SessionDep
from app.db.models.catalog import STATUS_DONE, STATUS_QUEUED, Catalog
from app.db.repositories.catalog_repo import catalog_repo
from app.domain.schemas.requests import (
    CreateCatalogRequest,
    SaveCatalogRequest,
    UpdateCatalogHtmlRequest,
)
from app.domain.schemas.responses import CatalogStatusResponse, SavedCatalogSummary
from app.domain.services.catalog_service import catalog_service
from app.exporters.pdf_exporter import PdfExporter


router = APIRouter(prefix="/catalogs", tags=["catalogs"])

def _to_response(c: Catalog) -> CatalogStatusResponse:
    return CatalogStatusResponse(
        id=c.id,
        status=c.status,
        template_id=c.template_id,
        llm_provider=c.llm_provider,
        theme=c.theme,
        page_size=c.page_size,
        error=c.error,
        created_at=c.created_at,
        updated_at=c.updated_at,
        html=c.html if c.status == STATUS_DONE else None,
        html_url=f"/api/v1/catalogs/{c.id}/html" if c.status == STATUS_DONE else None,
        pdf_url=f"/api/v1/catalogs/{c.id}/pdf" if c.status == STATUS_DONE else None,
        refined=c.refined_json,
        saved=c.saved,
        title=c.title,
    )


def _to_summary(c: Catalog) -> SavedCatalogSummary:
    return SavedCatalogSummary(
        id=c.id,
        title=c.title,
        status=c.status,
        template_id=c.template_id,
        style=c.style,
        theme=c.theme,
        page_size=c.page_size,
        created_at=c.created_at,
        updated_at=c.updated_at,
        html_url=f"/api/v1/catalogs/{c.id}/html" if c.status == STATUS_DONE else None,
        pdf_url=f"/api/v1/catalogs/{c.id}/pdf" if c.status == STATUS_DONE else None,
    )


async def _render_pdf(html: str) -> bytes:
    """Render HTML to PDF bytes (in memory) for storage in the database."""
    return await PdfExporter().render(html)


@router.post("", response_model=CatalogStatusResponse, status_code=202)
async def create_catalog(
    body: CreateCatalogRequest,
    background: BackgroundTasks,
    db: SessionDep,
) -> CatalogStatusResponse:

    if not body.source_text:
        raise HTTPException(422, "source_text is required (file uploads coming in a later iteration).")

    row = Catalog(
        id=uuid.uuid4(),
        status=STATUS_QUEUED,
        template_id=body.template_name,
        llm_provider=body.llm_provider,
        style=body.style,
        theme=body.theme,
        page_size="A4",  # fixed — catalogs are always a single A4 page
        source_text=body.source_text,
    )
    row = await catalog_repo.create(db, row)

    background.add_task(catalog_service.run_pipeline, row.id)
    return _to_response(row)


@router.get("/saved", response_model=list[SavedCatalogSummary])
async def list_saved_catalogs(db: SessionDep) -> list[SavedCatalogSummary]:
    """The "Saved Catalogs" library — catalogs the user explicitly kept."""
    rows = await catalog_repo.list_saved(db)
    return [_to_summary(r) for r in rows]


@router.get("/{catalog_id}", response_model=CatalogStatusResponse)
async def get_catalog_status(catalog_id: uuid.UUID, db: SessionDep) -> CatalogStatusResponse:
    row = await catalog_repo.get(db, catalog_id)
    if row is None:
        raise HTTPException(404, "Catalog not found")
    return _to_response(row)


@router.post("/{catalog_id}/save", response_model=CatalogStatusResponse)
async def save_catalog(
    catalog_id: uuid.UUID,
    body: SaveCatalogRequest,
    db: SessionDep,
) -> CatalogStatusResponse:
 
    row = await catalog_repo.get(db, catalog_id)
    if row is None:
        raise HTTPException(404, "Catalog not found")

    fields: dict = {"saved": True}
    if body.title is not None:
        title = body.title.strip()
        fields["title"] = title or None
    if body.html:
        pdf_bytes = await _render_pdf(body.html)
        fields.update(html=body.html, pdf_bytes=pdf_bytes, status=STATUS_DONE)

    updated = await catalog_repo.update(db, catalog_id, **fields)
    return _to_response(updated)


@router.delete("/{catalog_id}/save", response_model=CatalogStatusResponse)
async def unsave_catalog(catalog_id: uuid.UUID, db: SessionDep) -> CatalogStatusResponse:

    row = await catalog_repo.get(db, catalog_id)
    if row is None:
        raise HTTPException(404, "Catalog not found")
    updated = await catalog_repo.update(db, catalog_id, saved=False)
    return _to_response(updated)


@router.put("/{catalog_id}/html", response_model=CatalogStatusResponse)
async def update_catalog_html(
    catalog_id: uuid.UUID,
    body: UpdateCatalogHtmlRequest,
    db: SessionDep,
) -> CatalogStatusResponse:
 
    row = await catalog_repo.get(db, catalog_id)
    if row is None:
        raise HTTPException(404, "Catalog not found")

    pdf_bytes = await _render_pdf(body.html)

    updated = await catalog_repo.update(
        db,
        catalog_id,
        html=body.html,
        pdf_bytes=pdf_bytes,
        status=STATUS_DONE,
    )
    return _to_response(updated)


@router.get("/{catalog_id}/html", response_class=HTMLResponse)
async def get_catalog_html(catalog_id: uuid.UUID, db: SessionDep) -> HTMLResponse:
    row = await catalog_repo.get(db, catalog_id)
    if row is None:
        raise HTTPException(404, "Catalog not found")
    if row.html is None:
        raise HTTPException(404, f"HTML not ready (status={row.status})")
    return HTMLResponse(content=row.html)


@router.get("/{catalog_id}/pdf")
async def get_catalog_pdf(catalog_id: uuid.UUID, db: SessionDep) -> Response:
    row = await catalog_repo.get(db, catalog_id)
    if row is None:
        raise HTTPException(404, "Catalog not found")

    pdf_bytes = row.pdf_bytes
    if pdf_bytes is None:
        # Lazy backfill: a catalog edited/saved before its PDF was stored (or
        # generated under the old disk-based flow) has HTML but no PDF bytes.
        # Render once from the stored HTML and cache the result in the DB.
        if not row.html:
            raise HTTPException(404, f"PDF not ready (status={row.status})")
        pdf_bytes = await _render_pdf(row.html)
        await catalog_repo.update(db, catalog_id, pdf_bytes=pdf_bytes)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="catalog-{catalog_id}.pdf"'},
    )
