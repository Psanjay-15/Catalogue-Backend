from __future__ import annotations
from abc import ABC, abstractmethod
from app.domain.schemas.catalog import Catalog


class LLMProvider(ABC):

    name: str = ""           # 'gemini', 'openai', 'anthropic', 'ollama'
    default_model: str = ""  # e.g. 'gemini-2.5-flash', 'gpt-4o-mini'

    @abstractmethod
    async def refine_catalog(self, raw_text: str, style: str) -> Catalog:
        """Send `raw_text` to the LLM and return a validated `Catalog`.

        Raises:
            LLMError on provider/SDK errors (rate limit, auth, malformed JSON).
            pydantic.ValidationError if the JSON doesn't match the Catalog schema.
        """
        ...

    @abstractmethod
    async def freestyle_html(
        self,
        catalog: Catalog,
        theme: str,
        page_size: str,
        width_mm: int,
        height_mm: int,
        style_hint: str | None = None,
    ) -> str:
        """Ask the LLM to design a complete single-page HTML brochure for `catalog`.

        Returns:
            Raw HTML string starting with <!DOCTYPE html>. No code fences, no commentary.
        """
        ...

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        """Remove ```html ... ``` fences if a model added them by mistake."""
        t = text.strip()
        if t.startswith("```"):
            t = t.split("\n", 1)[1] if "\n" in t else t[3:]
            if t.rstrip().endswith("```"):
                t = t.rstrip()[:-3].rstrip()
        return t
