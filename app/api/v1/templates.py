from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.api.v1.deps import SessionDep
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
