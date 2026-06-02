from __future__ import annotations
from pathlib import Path
from typing import Union
from app.core.exceptions import ExportError
from app.exporters.base import Exporter


DEFAULT_VIEWPORT = (794, 1123)


class PngExporter(Exporter):
    def __init__(self, viewport: tuple[int, int] = DEFAULT_VIEWPORT) -> None:
        self.viewport_w, self.viewport_h = viewport

    async def export(self, html: str, out_path: Union[str, Path]) -> Path:
        path = Path(out_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            from playwright.async_api import async_playwright
        except ImportError as e:
            raise ExportError(
                "Playwright not installed. Run `pip install playwright && playwright install chromium`."
            ) from e

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                context = await browser.new_context(
                    viewport={"width": self.viewport_w, "height": self.viewport_h},
                    device_scale_factor=2,       
                )
                page = await context.new_page()

                await page.set_content(html, wait_until="domcontentloaded", timeout=20_000)
                try:
                    await page.wait_for_load_state("load", timeout=90_000)
                except Exception:
                    pass
                await page.screenshot(path=str(path), full_page=False)
                await browser.close()
        except Exception as e:
            raise ExportError(f"Playwright screenshot failed: {e}") from e
        return path
