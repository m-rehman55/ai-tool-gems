"""Campaign URLs and privacy-safe source labels."""

from __future__ import annotations

from urllib.parse import urlencode


def tracking_code(platform: str, product_id: str, date_key: str, variant: str) -> str:
    return f"{platform[:2]}-{product_id}-{date_key}-{variant.lower()}"


def product_url(site_url: str, product_id: str, code: str, platform: str = "telegram") -> str:
    params = urlencode({
        "utm_source": platform,
        "utm_medium": "organic_social",
        "utm_campaign": "product_rotation",
        "utm_content": code,
        "src": code,
    })
    return f"{site_url}/tools/{product_id}/?{params}"
