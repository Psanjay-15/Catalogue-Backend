from __future__ import annotations
from typing import Any, List, Optional
from pydantic import BaseModel, Field, field_validator


def _coerce_image_query(v: Any) -> Optional[str]:

    if v is None:
        return None
    if isinstance(v, list):
        v = ", ".join(str(x).strip() for x in v if x is not None and str(x).strip())
    text = str(v).strip()
    return text or None


def _coerce_str(v: Any) -> str:

    if v is None:
        return ""
    return str(v)


def _drop_empty_specs(v: list) -> list:
    return [s for s in v if (s.label.strip() or s.value.strip())]


def _coerce_str_list(v: Any) -> Any:

    if not isinstance(v, list):
        return v
    out: list[str] = []
    for item in v:
        if item is None:
            continue
        if isinstance(item, dict):
            title = str(item.get("title") or item.get("name") or "").strip()
            desc = str(item.get("description") or item.get("value") or "").strip()
            if title and desc:
                text = f"{title} — {desc}"
            elif title or desc:
                text = title or desc
            else:
                text = ", ".join(
                    str(x).strip() for x in item.values() if x is not None and str(x).strip()
                )
        else:
            text = str(item).strip()
        if text:
            out.append(text)
    return out


class Feature(BaseModel):
    title: str
    description: str = ""        #


class Benefit(BaseModel):
    title: str
    description: str = ""        


class Spec(BaseModel):
    label: str = ""             
    value: str = ""

    _coerce_strs = field_validator("label", "value", mode="before")(_coerce_str)


class PricingItem(BaseModel):
    name: str
    description: Optional[str] = None
    price: str = ""               
    highlight: Optional[bool] = False


class Product(BaseModel):
    name: str
    tagline: Optional[str] = None
    description: str = ""
    features: List[str] = Field(default_factory=list)
    specs: List[Spec] = Field(default_factory=list)
    pricing: List[PricingItem] = Field(default_factory=list)
    image_query: Optional[str] = None     

    _coerce_iq = field_validator("image_query", mode="before")(_coerce_image_query)
    _coerce_features = field_validator("features", mode="before")(_coerce_str_list)
    _drop_specs = field_validator("specs", mode="after")(_drop_empty_specs)


class Testimonial(BaseModel):
    quote: str
    author: str
    role: Optional[str] = None
    image_query: Optional[str] = None     

    _coerce_iq = field_validator("image_query", mode="before")(_coerce_image_query)


class FAQItem(BaseModel):
    question: str
    answer: str


class Contact(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None


class Hero(BaseModel):
    headline: str
    subheadline: Optional[str] = None
    tagline: Optional[str] = None
    image_query: Optional[str] = None     

    _coerce_iq = field_validator("image_query", mode="before")(_coerce_image_query)


class CallToAction(BaseModel):
    title: str
    description: Optional[str] = None
    button_text: Optional[str] = None


class Stat(BaseModel):
    """A headline metric, e.g. '70% organic ingredients' or '150+ projects'."""
    value: str                          
    label: str                           
    percent: Optional[int] = None        

    @field_validator("percent", mode="before")
    @classmethod
    def _coerce_percent(cls, v: Any) -> Optional[int]:

        if v is None or v == "":
            return None
        try:
            n = int(v)
        except (TypeError, ValueError):
            return None
        return max(0, min(100, n))


class Catalog(BaseModel):
    brand_name: str
    hero: Optional[Hero] = None
    overview: Optional[str] = None
    about_image_query: Optional[str] = None
    values: List[str] = Field(default_factory=list)
    stats: List[Stat] = Field(default_factory=list)
    products: List[Product] = Field(default_factory=list)
    features: List[Feature] = Field(default_factory=list)
    benefits: List[Benefit] = Field(default_factory=list)
    specifications: List[Spec] = Field(default_factory=list)
    pricing: List[PricingItem] = Field(default_factory=list)
    testimonials: List[Testimonial] = Field(default_factory=list)
    faqs: List[FAQItem] = Field(default_factory=list)
    contact: Optional[Contact] = None
    call_to_action: Optional[CallToAction] = None

    _coerce_iq = field_validator("about_image_query", mode="before")(_coerce_image_query)
    _coerce_values = field_validator("values", mode="before")(_coerce_str_list)
    _drop_specs = field_validator("specifications", mode="after")(_drop_empty_specs)



VALID_STYLES = {"modern", "luxury", "minimal", "corporate", "creative"}
VALID_TEMPLATES = {
    "ai",
    "modern", "luxury", "minimal", "corporate", "creative",
    "showcase", "product-grid", "service", "magazine",
}
VALID_THEMES = {"light", "dark"}
VALID_PAGE_SIZES = {"A4", "A3", "A2", "Letter"}

PAGE_DIMENSIONS_MM: dict[str, tuple[int, int]] = {
    "A4":     (210, 297),
    "A3":     (297, 420),
    "A2":     (420, 594),
    "Letter": (216, 279),
}
