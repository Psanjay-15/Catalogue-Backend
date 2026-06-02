from __future__ import annotations
from functools import lru_cache
from app.core.exceptions import UnsupportedProviderError
from app.llm.anthropic_provider import AnthropicProvider
from app.llm.base import LLMProvider
from app.llm.gemini import GeminiProvider
from app.llm.ollama_provider import OllamaProvider
from app.llm.openai_provider import OpenAIProvider


_REGISTRY: dict[str, type[LLMProvider]] = {
    "gemini":    GeminiProvider,
    "openai":    OpenAIProvider,
    "anthropic": AnthropicProvider,
    "ollama":    OllamaProvider,
}


@lru_cache(maxsize=8)
def get_llm_provider(name: str) -> LLMProvider:
    """Return a cached singleton instance of the named provider.

    Cached so we don't re-create SDK clients on every request. lru_cache
    is process-local — every Uvicorn worker has its own cache, which is
    what we want.
    """
    if name not in _REGISTRY:
        raise UnsupportedProviderError(
            f"Unknown LLM provider '{name}'. Available: {sorted(_REGISTRY)}"
        )
    return _REGISTRY[name]()
