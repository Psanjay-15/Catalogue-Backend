from __future__ import annotations


class CatalogMakerError(Exception):
    """Root of all domain exceptions."""
    status_code: int = 500


class NotFoundError(CatalogMakerError):
    status_code = 404


class ValidationError(CatalogMakerError):
    status_code = 422


class UnsupportedProviderError(CatalogMakerError):
    """Raised when an unknown LLM provider name is requested."""
    status_code = 400


class UnsupportedFormatError(CatalogMakerError):
    """Raised when an unknown file extension is given to the extractor."""
    status_code = 400


class LLMError(CatalogMakerError):
    """Wraps provider SDK errors (rate limits, auth, malformed JSON, etc.)."""
    status_code = 502


class RateLimitError(LLMError):
    status_code = 429


class RenderError(CatalogMakerError):
    status_code = 500


class ExportError(CatalogMakerError):
    status_code = 500
