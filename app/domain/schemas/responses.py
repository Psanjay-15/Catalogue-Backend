from __future__ import annotations
from datetime import datetime
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel


class TemplateResponse(BaseModel):

    id: str
    name: str
    description: str
    kind: str
    sample_html: str


class CatalogStatusResponse(BaseModel):

    id: UUID
    status: str                             
    template_id: str
    llm_provider: str
    theme: str
    page_size: str
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


    html: Optional[str] = None                
    html_url: Optional[str] = None            
    pdf_url: Optional[str] = None             
    refined: Optional[dict[str, Any]] = None  

    saved: bool = False
    title: Optional[str] = None


class SavedCatalogSummary(BaseModel):

    id: UUID
    title: Optional[str] = None
    status: str
    template_id: str
    style: str
    theme: str
    page_size: str
    created_at: datetime
    updated_at: datetime
    html_url: Optional[str] = None
    pdf_url: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "ok"
