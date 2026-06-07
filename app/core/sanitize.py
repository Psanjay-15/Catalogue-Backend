from __future__ import annotations

import re

_SCRIPT_BLOCK_RE = re.compile(r"<script\b[^>]*>.*?</script\s*>", re.IGNORECASE | re.DOTALL)
_SCRIPT_TAG_RE = re.compile(r"</?\s*script\b[^>]*>", re.IGNORECASE)

_ON_ATTR_RE = re.compile(
    r"""\s+on[a-z]+\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)""", re.IGNORECASE
)

_JS_URI_RE = re.compile(
    r"""(\s(?:href|src|xlink:href|action|formaction)\s*=\s*)("|'|)\s*javascript:[^"'>\s]*""",
    re.IGNORECASE,
)


def sanitize_html(html: str | None) -> str:
    """Remove <script>, inline on* handlers, and javascript: URIs from `html`."""
    if not html:
        return html or ""
    html = _SCRIPT_BLOCK_RE.sub("", html)
    html = _SCRIPT_TAG_RE.sub("", html)
    html = _ON_ATTR_RE.sub("", html)
    html = _JS_URI_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}#", html)
    return html
