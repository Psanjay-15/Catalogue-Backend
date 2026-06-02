from __future__ import annotations
import hashlib
from typing import Optional


def image_url(query: Optional[str], w: int = 800, h: int = 600, seed: int = 0) -> str:
    if query:
        h_bytes = hashlib.md5(query.lower().strip().encode("utf-8")).digest()
        query_slug = h_bytes.hex()[:4]
        derived = f"{query_slug}{seed}"
    else:
        derived = f"catalog{seed}"
    return f"https://picsum.photos/seed/{derived}/{w}/{h}"
