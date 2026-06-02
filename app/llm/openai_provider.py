from __future__ import annotations
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


class OpenAIProvider(LLMProvider):
    name = "openai"
    default_model = "gpt-4o-mini"

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or self.default_model
        if not settings.openai_api_key:
            raise LLMError("OPENAI_API_KEY not set.")

    def _client(self):
        from openai import AsyncOpenAI
        return AsyncOpenAI(api_key=settings.openai_api_key)

    async def refine_catalog(self, raw_text: str, style: str) -> Catalog:
        client = self._client()
        user_prompt = build_refine_user_prompt(raw_text, style)

        try:
            response = await client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.6,
            )
        except Exception as e:
            self._reraise(e)

        payload = response.choices[0].message.content or ""
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as e:
            raise LLMError(f"OpenAI returned invalid JSON: {e}\nPayload: {payload[:500]}") from e
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
            response = await client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.85,
            )
        except Exception as e:
            self._reraise(e)

        html = self._strip_code_fences(response.choices[0].message.content or "")
        if not html.lower().lstrip().startswith("<!doctype"):
            raise LLMError(f"Freestyle returned non-HTML payload: {html[:200]}")
        return html

    @staticmethod
    def _reraise(e: Exception):
        msg = str(e)
        if "429" in msg or "rate" in msg.lower() or "quota" in msg.lower():
            raise RateLimitError("OpenAI rate limit / quota exceeded.") from e
        raise LLMError(f"OpenAI call failed: {msg}") from e
