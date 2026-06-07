from __future__ import annotations
import asyncio
import re
from pathlib import Path
from app.core.exceptions import ExportError
from app.core.logging import get_logger

log = get_logger(__name__)

_PLACEHOLDER_IMG = (
    b"<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100'></svg>"
)

_PDF_FIT_CSS = """
<style id="cat-pdf-fit">
  @page { size: A4 !important; margin: 0 !important; }
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
        try:
            return await self._render_weasyprint(fitted)
        except Exception as e:
            log.warning(
                "WeasyPrint render failed (%s); trying headless Chromium fallback.", e
            )
            try:
                return await self._render_chromium(fitted)
            except ExportError:
                raise ExportError(f"PDF render failed: {e}") from e

    @staticmethod
    def _url_fetcher(url: str, *args, **kwargs):
      
        from weasyprint import default_url_fetcher

        try:
            return default_url_fetcher(url, *args, **kwargs)
        except Exception as e:
            log.warning("asset fetch failed for %s (%s); using blank placeholder.", url, e)
            return {"string": _PLACEHOLDER_IMG, "mime_type": "image/svg+xml"}

    async def _render_weasyprint(self, html: str) -> bytes:
        def _render() -> bytes:
            try:
                from weasyprint import HTML

                base = self.base_url or str(Path.cwd())
                return HTML(
                    string=html, base_url=base, url_fetcher=self._url_fetcher
                ).write_pdf()
            except Exception as e:
                raise ExportError(f"WeasyPrint render failed: {e}") from e

        return await asyncio.to_thread(_render)

    async def _render_chromium(self, html: str) -> bytes:
        try:
            from playwright.async_api import async_playwright
        except ImportError as e:
            raise ExportError(
                "Playwright not installed (Chromium fallback unavailable). "
                'Run `pip install -e ".[chromium]" && playwright install chromium`.'
            ) from e

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                try:
                    page = await browser.new_page()
                    await page.set_content(html, wait_until="domcontentloaded", timeout=20_000)
                    try:
                        await page.wait_for_load_state("networkidle", timeout=20_000)
                    except Exception:
                        pass
                    try:
                        await page.evaluate("async () => { await document.fonts.ready; }")
                    except Exception:
                        pass
                    return await page.pdf(
                        prefer_css_page_size=True,
                        print_background=True,
                        margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                    )
                finally:
                    await browser.close()
        except ExportError:
            raise
        except Exception as e:
            raise ExportError(f"Chromium render failed: {e}") from e
