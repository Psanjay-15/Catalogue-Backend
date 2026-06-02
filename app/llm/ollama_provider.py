from __future__ import annotations
import json
import httpx
from app.config import settings
from app.core.exceptions import LLMError
from app.domain.schemas.catalog import Catalog
from app.llm.base import LLMProvider
from app.llm.prompts import (
    SYSTEM_PROMPT,
    build_freestyle_user_prompt,
    build_refine_user_prompt,
)


class OllamaProvider(LLMProvider):
    name = "ollama"
    default_model = "llama3.2:1b"

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or self.default_model
        self.base_url = settings.ollama_base_url.rstrip("/")

    async def refine_catalog(self, raw_text: str, style: str) -> Catalog:
        user_prompt = build_refine_user_prompt(raw_text, style)
        body = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "format": "json",         
            "stream": False,
            "options": {"temperature": 0.6},
        }
        data = await self._post("/api/chat", body)
        payload = data.get("message", {}).get("content", "")
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as e:
            raise LLMError(f"Ollama returned invalid JSON: {e}\nPayload: {payload[:500]}") from e
        return Catalog.model_validate(parsed)

    async def freestyle_html(
        self,
        catalog: Catalog,
        theme: str,
        page_size: str,
        width_mm: int,
        height_mm: int,
    ) -> str:
        prompt = build_freestyle_user_prompt(
            catalog_json=catalog.model_dump_json(indent=2),
            theme=theme,
            page_size=page_size,
            width=width_mm,
            height=height_mm,
        )
        body = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.85},
        }
        data = await self._post("/api/chat", body)
        html = self._strip_code_fences(data.get("message", {}).get("content", ""))
        if not html.lower().lstrip().startswith("<!doctype"):
            raise LLMError(f"Freestyle returned non-HTML payload: {html[:200]}")
        return html

    async def _post(self, path: str, body: dict) -> dict:
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                resp = await client.post(url, json=body)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            raise LLMError(
                f"Ollama call failed at {url}: {e}. "
                f"Is `ollama serve` running and the model `{self.model_name}` pulled?"
            ) from e
