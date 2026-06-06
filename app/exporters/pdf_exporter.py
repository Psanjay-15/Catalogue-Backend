from __future__ import annotations
import asyncio
import re
from pathlib import Path
from app.core.exceptions import ExportError
from app.core.logging import get_logger

log = get_logger(__name__)

_PDF_FIT_CSS = """
<style id="cat-pdf-fit">
  @page { margin: 0 !important; }
  html, body { margin: 0 !important; padding: 0 !important; }
  .page {
    margin: 0 !important;
    box-shadow: none !important;
  }
</style>
"""


def inject_pdf_fit(html: str) -> str:

    if not html or "cat-pdf-fit" in html:
        return html or ""
    lower = html.lower()
    idx = lower.rfind("</head>")
    if idx != -1:
        return html[:idx] + _PDF_FIT_CSS + html[idx:]
    m = re.search(r"<body[^>]*>", html, flags=re.IGNORECASE)
    if m:
        return html[: m.end()] + _PDF_FIT_CSS + html[m.end():]
    return _PDF_FIT_CSS + html


class PdfExporter:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url

    async def render(self, html: str) -> bytes:
       
        fitted = inject_pdf_fit(html)
        return await self._render_weasyprint(fitted)

    async def _render_weasyprint(self, html: str) -> bytes:
        def _render() -> bytes:
            try:
                from weasyprint import HTML

                base = self.base_url or str(Path.cwd())
                # No target → write_pdf() returns the PDF as bytes.
                return HTML(string=html, base_url=base).write_pdf()
            except Exception as e:
                raise ExportError(f"PDF render failed (WeasyPrint fallback): {e}") from e

        return await asyncio.to_thread(_render)
