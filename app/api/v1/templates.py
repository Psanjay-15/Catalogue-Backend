from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from app.api.v1.deps import SessionDep
from app.config import settings
from app.core.exceptions import NotFoundError
from app.domain.schemas.responses import TemplateResponse
from app.domain.services.template_service import template_service


router = APIRouter(prefix="/templates", tags=["templates"])

@router.get("", response_model=list[TemplateResponse])
async def list_templates(db: SessionDep) -> list[TemplateResponse]:

    return await template_service.list_templates(db)


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str, db: SessionDep) -> TemplateResponse:
    try:
        return await template_service.get_template(db, template_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))


@router.get("/{template_id}/preview.png")
async def preview_png(template_id: str):
    path = settings.previews_dir / f"{template_id}.png"
    if not path.exists():
        raise HTTPException(404, f"Preview for '{template_id}' not generated yet. Run scripts/generate_previews.py.")
    return FileResponse(path, media_type="image/png")


@router.get("/{template_id}/sample.html", response_class=HTMLResponse)
async def sample_html(template_id: str, db: SessionDep) -> HTMLResponse:
    try:
        html = await template_service.get_sample_html(db, template_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    return HTMLResponse(content=html)
