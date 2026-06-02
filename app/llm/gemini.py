from __future__ import annotations
import asyncio
import json
from app.config import settings
from app.core.exceptions import LLMError, RateLimitError
from app.domain.schemas.catalog import Catalog
from app.llm.base import LLMProvider
from app.llm.prompts import (
    SYSTEM_PROMPT,
    build_freestyle_user_prompt,
    build_refine_user_prompt,
)


class GeminiProvider(LLMProvider):
    name = "gemini"
    default_model = "gemini-2.5-flash"

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or self.default_model
        if not settings.gemini_api_key:
            raise LLMError(
                "GEMINI_API_KEY not set. Add it to .env to use the Gemini provider."
            )

    def _client(self):  
        from google import genai
        return genai.Client(api_key=settings.gemini_api_key)

    async def refine_catalog(self, raw_text: str, style: str) -> Catalog:
        from google.genai import types as genai_types

        client = self._client()
        config = genai_types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            temperature=0.6,
        )
        user_prompt = build_refine_user_prompt(raw_text, style)

        def _call():
            return client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=config,
            )

        response = await self._run(_call)
        payload = response.text or ""
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as e:
            raise LLMError(f"Gemini returned invalid JSON: {e}\nPayload: {payload[:500]}") from e
        return Catalog.model_validate(data)

    async def freestyle_html(
        self,
        catalog: Catalog,
        theme: str,
        page_size: str,
        width_mm: int,
        height_mm: int,
    ) -> str:
        from google.genai import types as genai_types

        client = self._client()
        prompt = build_freestyle_user_prompt(
            catalog_json=catalog.model_dump_json(indent=2),
            theme=theme,
            page_size=page_size,
            width=width_mm,
            height=height_mm,
        )
        config = genai_types.GenerateContentConfig(temperature=0.85)

        def _call():
            return client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )

        response = await self._run(_call)
        html = self._strip_code_fences(response.text or "")
        if not html.lower().lstrip().startswith("<!doctype"):
            raise LLMError(f"Freestyle returned non-HTML payload: {html[:200]}")
        return html

    @staticmethod
    async def _run(fn):
        try:
            return await asyncio.to_thread(fn)
        except Exception as e:
            msg = str(e)
            if "RESOURCE_EXHAUSTED" in msg or "429" in msg or "quota" in msg.lower():
                raise RateLimitError(
                    "Gemini rate limit / quota exceeded. Wait ~60s and retry."
                ) from e
            raise LLMError(f"Gemini call failed: {msg}") from e
