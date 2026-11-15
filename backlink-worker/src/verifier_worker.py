"""Cloudflare Worker Backlink Verifier Engine.

Integrates DOM-level HTML anchor parsing, SSRF boundaries, and rel-token
classification within Cloudflare Workers environment.
"""

from __future__ import annotations

import html.parser
import json
import re
import time
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple

# Reusable pure-Python anchor parser matching backlink_agent specifications
USER_AGENT = "AIToolGems-CloudflareVerifier/2.0 (+https://aitoolgems.tech/llms.txt)"
DEFAULT_TIMEOUT = 15
DEFAULT_MAX_BYTES = 2 * 1024 * 1024  # 2MB cap


class AnchorData:
    def __init__(self, raw_href: str, resolved_href: str, text: str, rel_tokens: List[str]):
        self.raw_href = raw_href
        self.resolved_href = resolved_href
        self.text = text.strip()
        self.rel_tokens = rel_tokens


class WorkerAnchorParser(html.parser.HTMLParser):
    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.anchors: List[AnchorData] = []
        self.canonical_url: Optional[str] = None
        self.is_noindex: bool = False
        self._current_anchor: Optional[dict] = None

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        tag_lower = tag.lower()

        if tag_lower == "a":
            href = attr_dict.get("href", "").strip()
            if href and not href.startswith(("javascript:", "mailto:", "tel:", "#")):
                rel_val = attr_dict.get("rel", "").lower()
                rel_tokens = [tok for tok in re.split(r"\s+", rel_val) if tok]
                resolved = urllib.parse.urljoin(self.base_url, href)
                self._current_anchor = {
                    "raw_href": href,
                    "resolved_href": resolved,
                    "text_parts": [],
                    "rel_tokens": rel_tokens,
                }
        elif tag_lower == "meta":
            name = attr_dict.get("name", "").lower()
            content = attr_dict.get("content", "").lower()
            if name in ("robots", "googlebot", "bingbot"):
                if "noindex" in content or "none" in content:
                    self.is_noindex = True
        elif tag_lower == "link":
            rel = attr_dict.get("rel", "").lower()
            if "canonical" in rel:
                href = attr_dict.get("href", "").strip()
                if href:
                    self.canonical_url = urllib.parse.urljoin(self.base_url, href)

    def handle_data(self, data: str):
        if self._current_anchor is not None:
            self._current_anchor["text_parts"].append(data)

    def handle_endtag(self, tag: str):
        if tag.lower() == "a" and self._current_anchor is not None:
            text = " ".join("".join(self._current_anchor["text_parts"]).split())
            self.anchors.append(
                AnchorData(
                    raw_href=self._current_anchor["raw_href"],
                    resolved_href=self._current_anchor["resolved_href"],
                    text=text,
                    rel_tokens=self._current_anchor["rel_tokens"],
                )
            )
            self._current_anchor = None


def normalize_target_url(url: str) -> str:
    if not url:
        return ""
    p = urllib.parse.urlsplit(url.strip())
    scheme = (p.scheme or "https").lower()
    netloc = (p.netloc or "").lower()
    if ":" in netloc:
        host, port = netloc.split(":", 1)
        if port == "443" and scheme == "https":
            netloc = host
        elif port == "80" and scheme == "http":
            netloc = host
    path = p.path or "/"
    path = re.sub(r"/+", "/", path)
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]
    return urllib.parse.urlunsplit((scheme, netloc, path, p.query, ""))


def classify_rel_tokens(rel_tokens: List[str]) -> str:
    tokens = set(t.lower() for t in rel_tokens)
    qualifiers = tokens.intersection({"nofollow", "sponsored", "ugc"})
    if not qualifiers:
        return "live_follow"
    if len(qualifiers) > 1:
        return "live_mixed"
    if "nofollow" in qualifiers:
        return "live_nofollow"
    if "sponsored" in qualifiers:
        return "live_sponsored"
    if "ugc" in qualifiers:
        return "live_ugc"
    return "live_follow"


def verify_html_content(
    html_text: str,
    base_url: str,
    target_url: str,
    response_headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    parser = WorkerAnchorParser(base_url)
    try:
        parser.feed(html_text)
    except Exception:
        pass

    is_noindex = parser.is_noindex
    if response_headers:
        for k, v in response_headers.items():
            if k.lower() == "x-robots-tag" and any(tok in v.lower() for tok in ("noindex", "none")):
                is_noindex = True
                break

    norm_target = normalize_target_url(target_url)
    target_domain = urllib.parse.urlsplit(norm_target).netloc.lower()

    matching_anchor: Optional[AnchorData] = None
    domain_match_anchor: Optional[AnchorData] = None

    for anchor in parser.anchors:
        norm_anchor = normalize_target_url(anchor.resolved_href)
        if norm_anchor == norm_target:
            matching_anchor = anchor
            break
        anchor_domain = urllib.parse.urlsplit(norm_anchor).netloc.lower()
        if anchor_domain == target_domain and not domain_match_anchor:
            domain_match_anchor = anchor

    if matching_anchor:
        rel_class = classify_rel_tokens(matching_anchor.rel_tokens)
        classification = "source_noindex" if is_noindex else rel_class
        return {
            "classification": classification,
            "target_found": True,
            "actual_anchor_text": matching_anchor.text,
            "rel_tokens": matching_anchor.rel_tokens,
            "is_noindex": is_noindex,
            "canonical_url": parser.canonical_url,
        }

    if domain_match_anchor:
        return {
            "classification": "wrong_target",
            "target_found": False,
            "actual_anchor_text": domain_match_anchor.text,
            "rel_tokens": domain_match_anchor.rel_tokens,
            "is_noindex": is_noindex,
            "canonical_url": parser.canonical_url,
        }

    return {
        "classification": "removed",
        "target_found": False,
        "actual_anchor_text": "",
        "rel_tokens": [],
        "is_noindex": is_noindex,
        "canonical_url": parser.canonical_url,
    }


def validate_worker_url(url: str) -> None:
    """Enforces HTTPS and SSRF syntax boundaries."""
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme.lower() != "https":
        raise ValueError(f"Disallowed scheme '{parsed.scheme}': only https is permitted")
    if parsed.username or parsed.password:
        raise ValueError("Embedded credentials in URL are prohibited")
    host = parsed.hostname or ""
    if host.lower() in ("localhost", "metadata", "instance-data", "metadata.google.internal"):
        raise ValueError(f"Forbidden hostname alias '{host}'")
    if host.endswith((".localhost", ".local", ".internal")):
        raise ValueError(f"Forbidden internal host suffix '{host}'")
