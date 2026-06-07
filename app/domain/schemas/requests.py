from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.domain.schemas.catalog import (
    VALID_STYLES,
    VALID_TEMPLATES,
    VALID_THEMES,
)

VALID_LLM_PROVIDERS = {"gemini", "openai", "anthropic", "ollama"}


class CreateCatalogRequest(BaseModel):

    source_text: Optional[str] = Field(
        None, max_length=100_000,
        description="Raw text input (paste a description, brand spec, etc.)",
    )
    template_name: str = Field("ai", description="Template id. 'ai' lets the LLM design from scratch.")
    style: str = Field("modern", description="Copywriting style — modern/luxury/minimal/corporate/creative")
    theme: str = Field("light", description="Color theme — light or dark")
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

    @field_validator("llm_provider")
    @classmethod
    def _check_provider(cls, v: str) -> str:
        if v not in VALID_LLM_PROVIDERS:
            raise ValueError(f"llm_provider must be one of {sorted(VALID_LLM_PROVIDERS)}")
        return v


_MAX_HTML = 10_000_000 


class UpdateCatalogHtmlRequest(BaseModel):
    html: str = Field(
        ..., min_length=1, max_length=_MAX_HTML, description="The edited full HTML document."
    )


class SaveCatalogRequest(BaseModel):

    title: Optional[str] = Field(
        None, max_length=200, description="Display name for the saved catalog."
    )
    html: Optional[str] = Field(
        None, max_length=_MAX_HTML,
        description="Latest edited HTML to persist + re-render before saving.",
    )
