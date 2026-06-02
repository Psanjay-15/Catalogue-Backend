from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.domain.schemas.catalog import (
    VALID_PAGE_SIZES,
    VALID_STYLES,
    VALID_TEMPLATES,
    VALID_THEMES,
)

VALID_LLM_PROVIDERS = {"gemini", "openai", "anthropic", "ollama"}


class CreateCatalogRequest(BaseModel):

    source_text: Optional[str] = Field(None, description="Raw text input (paste a description, brand spec, etc.)")
    source_file_path: Optional[str] = Field(None, description="Path to a previously uploaded PDF/DOCX/TXT")
    template_name: str = Field("ai", description="Template id. 'ai' lets the LLM design from scratch.")
    style: str = Field("modern", description="Copywriting style — modern/luxury/minimal/corporate/creative")
    theme: str = Field("light", description="Color theme — light or dark")
    page_size: str = Field("A4", description="Page size — A4 / A3 / A2 / Letter")
    llm_provider: str = Field("gemini", description="Which LLM to use")

    @field_validator("template_name")
    @classmethod
    def _check_template(cls, v: str) -> str:
        if v not in VALID_TEMPLATES:
            raise ValueError(f"template_name must be one of {sorted(VALID_TEMPLATES)}")
        return v

    @field_validator("style")
    @classmethod
    def _check_style(cls, v: str) -> str:
        if v not in VALID_STYLES:
            raise ValueError(f"style must be one of {sorted(VALID_STYLES)}")
        return v

    @field_validator("theme")
    @classmethod
    def _check_theme(cls, v: str) -> str:
        if v not in VALID_THEMES:
            raise ValueError(f"theme must be one of {sorted(VALID_THEMES)}")
        return v

    @field_validator("page_size")
    @classmethod
    def _check_page_size(cls, v: str) -> str:
        if v not in VALID_PAGE_SIZES:
            raise ValueError(f"page_size must be one of {sorted(VALID_PAGE_SIZES)}")
        return v

    @field_validator("llm_provider")
    @classmethod
    def _check_provider(cls, v: str) -> str:
        if v not in VALID_LLM_PROVIDERS:
            raise ValueError(f"llm_provider must be one of {sorted(VALID_LLM_PROVIDERS)}")
        return v


class UpdateCatalogHtmlRequest(BaseModel):
    html: str = Field(..., min_length=1, description="The edited full HTML document.")


class SaveCatalogRequest(BaseModel):
  
    title: Optional[str] = Field(
        None, max_length=200, description="Display name for the saved catalog."
    )
    html: Optional[str] = Field(
        None, description="Latest edited HTML to persist + re-render before saving."
    )
