from __future__ import annotations
from app.config import settings
from app.core.exceptions import LLMError, RateLimitError
from app.domain.schemas.catalog import Catalog
from app.llm.base import LLMProvider
from app.llm.prompts import (
    SYSTEM_PROMPT,
    build_freestyle_user_prompt,
    build_refine_user_prompt,
)


# Claude has no JSON-schema response mode, so we force structured output via a
# single tool whose input_schema IS the Catalog schema (derived from the Pydantic
# model). `tool_choice` forces Claude to call it, so its arguments are the catalog.
_CATALOG_TOOL_NAME = "build_catalog"
_CATALOG_TOOL = {
    "name": _CATALOG_TOOL_NAME,
    "description": "Return the structured single-page catalog built from the source.",
    "input_schema": Catalog.model_json_schema(),
}


class AnthropicProvider(LLMProvider):
    name = "anthropic"
    default_model = "claude-3-5-sonnet-latest"

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or self.default_model
        if not settings.anthropic_api_key:
            raise LLMError("ANTHROPIC_API_KEY not set.")

    def _client(self):
        from anthropic import AsyncAnthropic
        return AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def refine_catalog(self, raw_text: str, style: str) -> Catalog:
        client = self._client()
        user_prompt = build_refine_user_prompt(raw_text, style)

        try:
            response = await client.messages.create(
                model=self.model_name,
                max_tokens=4096,
                temperature=0.6,
                system=SYSTEM_PROMPT,
                tools=[_CATALOG_TOOL],
                tool_choice={"type": "tool", "name": _CATALOG_TOOL_NAME},
                messages=[{"role": "user", "content": user_prompt}],
            )
        except Exception as e:
            self._reraise(e)

        # Forced tool_choice means Claude responds with a tool_use block whose
        # `input` is the catalog object already shaped to the schema.
        data = None
        for block in response.content:
            if getattr(block, "type", None) == "tool_use" and block.name == _CATALOG_TOOL_NAME:
                data = block.input
                break
        if data is None:
            raise LLMError("Claude did not return the build_catalog tool output.")
        return Catalog.model_validate(data)

    async def freestyle_html(
        self,
        catalog: Catalog,
        theme: str,
        page_size: str,
        width_mm: int,
        height_mm: int,
    ) -> str:
        client = self._client()
        prompt = build_freestyle_user_prompt(
            catalog_json=catalog.model_dump_json(indent=2),
            theme=theme,
            page_size=page_size,
            width=width_mm,
            height=height_mm,
        )

        try:
            response = await client.messages.create(
                model=self.model_name,
                max_tokens=8192,
                temperature=0.85,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as e:
            self._reraise(e)

        text = ""
        for block in response.content:
            if getattr(block, "type", None) == "text":
                text = block.text
                break
        html = self._strip_code_fences(text)
        if not html.lower().lstrip().startswith("<!doctype"):
            raise LLMError(f"Freestyle returned non-HTML payload: {html[:200]}")
        return html

    @staticmethod
    def _reraise(e: Exception):
        msg = str(e)
        if "429" in msg or "rate" in msg.lower() or "overload" in msg.lower():
            raise RateLimitError("Claude rate limit / overload.") from e
        raise LLMError(f"Claude call failed: {msg}") from e
