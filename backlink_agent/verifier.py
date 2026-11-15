"""HTML Anchor Parser and Verification Engine for Backlink Agent.

Replaces naïve body-substring tests with rigorous HTML parsing:
- Validates actual <a href> existence
- Resolves relative hrefs to absolute target URLs
- Classifies rel attributes (follow, nofollow, sponsored, ugc, mixed)
- Checks source page <meta name="robots"> and X-Robots-Tag for noindex
- Detects redirects, wrong targets, plain mentions (removed), and SSRF blocks
"""

from __future__ import annotations

import html.parser
import re
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Tuple

from .models import Prospect, VerificationResult
from .security import (
    SSRFSecurityError,
    normalize_target_url,
    validate_and_sanitize_url,
    validate_url_syntax,
)

USER_AGENT = "AIToolGems-Verifier/2.0 (+https://aitoolgems.tech/llms.txt)"
DEFAULT_TIMEOUT = 15
DEFAULT_MAX_BYTES = 2 * 1024 * 1024  # 2 MB limit
DEFAULT_MAX_REDIRECTS = 5


class AnchorData:
    def __init__(self, raw_href: str, resolved_href: str, text: str, rel_tokens: List[str]):
        self.raw_href = raw_href
        self.resolved_href = resolved_href
        self.text = text.strip()
        self.rel_tokens = rel_tokens


class BacklinkHTMLParser(html.parser.HTMLParser):
    """HTML Parser that extracts anchors, rel tokens, canonical link, and robots meta tags."""

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


def classify_rel_tokens(rel_tokens: List[str]) -> str:
    """Classifies rel tokens into follow/nofollow/sponsored/ugc/mixed."""
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


def parse_and_verify_html(
    html_text: str,
    base_url: str,
    target_url: str,
    response_headers: Optional[Dict[str, str]] = None,
) -> Tuple[str, bool, str, List[str], bool, Optional[str]]:
    """Analyzes HTML content against target URL.

    Returns:
        (classification, target_found, actual_anchor_text, rel_tokens, is_noindex, canonical_url)
    """
    parser = BacklinkHTMLParser(base_url)
    try:
        parser.feed(html_text)
    except Exception:
        pass  # Parse what was successfully processed

    # Check X-Robots-Tag in response headers
    is_noindex = parser.is_noindex
    if response_headers:
        for k, v in response_headers.items():
            if k.lower() == "x-robots-tag" and any(token in v.lower() for token in ("noindex", "none")):
                is_noindex = True
                break

    norm_target = normalize_target_url(target_url)
    target_parsed = urllib.parse.urlsplit(norm_target)
    target_domain = target_parsed.netloc.lower()

    matching_anchor: Optional[AnchorData] = None
    domain_match_anchor: Optional[AnchorData] = None

    for anchor in parser.anchors:
        norm_anchor = normalize_target_url(anchor.resolved_href)
        if norm_anchor == norm_target:
            matching_anchor = anchor
            break
        # Check if it points to same domain but different path/target
        anchor_netloc = urllib.parse.urlsplit(norm_anchor).netloc.lower()
        if anchor_netloc == target_domain and not domain_match_anchor:
            domain_match_anchor = anchor

    if matching_anchor:
        rel_class = classify_rel_tokens(matching_anchor.rel_tokens)
        if is_noindex:
            classification = "source_noindex"
        else:
            classification = rel_class
        return (
            classification,
            True,
            matching_anchor.text,
            matching_anchor.rel_tokens,
            is_noindex,
            parser.canonical_url,
        )

    # If anchor not matched
    if domain_match_anchor:
        classification = "wrong_target"
        return (
            classification,
            False,
            domain_match_anchor.text,
            domain_match_anchor.rel_tokens,
            is_noindex,
            parser.canonical_url,
        )

    # Check if target domain is mentioned in text without an anchor
    if target_domain and target_domain in html_text:
        # Plain-text mention exists, but no valid matching anchor
        classification = "removed"
    else:
        classification = "removed"

    return (classification, False, "", [], is_noindex, parser.canonical_url)


def verify_prospect_url(
    source_page: str,
    target_url: str,
    timeout: int = DEFAULT_TIMEOUT,
    max_bytes: int = DEFAULT_MAX_BYTES,
    max_redirects: int = DEFAULT_MAX_REDIRECTS,
    dns_resolver=None,
) -> VerificationResult:
    """Safely probes source_page over HTTPS with strict SSRF controls and verifies target_url."""
    start_time = time.time()
    redirect_chain: List[str] = []
    current_url = source_page

    for redirect_idx in range(max_redirects + 1):
        try:
            sanitized_url, _ = validate_and_sanitize_url(current_url)
        except SSRFSecurityError as err:
            return VerificationResult(
                source_page=source_page,
                target_url=target_url,
                classification="unsafe_url",
                error_message=f"SSRF violation on {current_url}: {err}",
                final_url=current_url,
                redirect_chain=redirect_chain,
                elapsed_seconds=time.time() - start_time,
            )

        # Build custom request preventing automatic unsafe redirect following
        class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
            def http_error_302(self, req, fp, code, msg, headers):
                return fp

            http_error_301 = http_error_302
            http_error_303 = http_error_302
            http_error_307 = http_error_302
            http_error_308 = http_error_302

        opener = urllib.request.build_opener(NoRedirectHandler)
        req = urllib.request.Request(
            sanitized_url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            },
        )

        try:
            with opener.open(req, timeout=timeout) as resp:
                status_code = getattr(resp, "status", 200)
                headers = dict(resp.headers.items()) if hasattr(resp, "headers") else {}

                # Check for redirect status codes
                if status_code in (301, 302, 303, 307, 308):
                    location = headers.get("Location") or headers.get("location")
                    if not location:
                        return VerificationResult(
                            source_page=source_page,
                            target_url=target_url,
                            status_code=status_code,
                            classification="redirect_error",
                            error_message="Redirect status without Location header",
                            final_url=current_url,
                            redirect_chain=redirect_chain,
                            elapsed_seconds=time.time() - start_time,
                        )

                    next_url = urllib.parse.urljoin(current_url, location)
                    redirect_chain.append(next_url)
                    current_url = next_url
                    continue  # Loop to validate next_url and fetch

                # Read body bounded by max_bytes
                content_bytes = bytearray()
                while len(content_bytes) < max_bytes:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    content_bytes.extend(chunk)

                body_text = content_bytes.decode("utf-8", errors="replace")

                if status_code != 200:
                    cls_name = "blocked_access" if status_code in (401, 403, 429) else "fetch_error"
                    return VerificationResult(
                        source_page=source_page,
                        target_url=target_url,
                        status_code=status_code,
                        classification=cls_name,
                        final_url=current_url,
                        redirect_chain=redirect_chain,
                        response_bytes=len(content_bytes),
                        elapsed_seconds=time.time() - start_time,
                        error_message=f"HTTP status {status_code}",
                    )

                classification, found, anchor_text, rel_tokens, is_noindex, canonical = (
                    parse_and_verify_html(body_text, current_url, target_url, headers)
                )

                return VerificationResult(
                    source_page=source_page,
                    target_url=target_url,
                    status_code=status_code,
                    classification=classification,
                    target_found=found,
                    actual_anchor_text=anchor_text,
                    rel_tokens=rel_tokens,
                    final_url=current_url,
                    redirect_chain=redirect_chain,
                    is_noindex=is_noindex,
                    canonical_url=canonical,
                    response_bytes=len(content_bytes),
                    elapsed_seconds=time.time() - start_time,
                )

        except urllib.error.HTTPError as err:
            cls_name = "blocked_access" if err.code in (401, 403, 429) else "fetch_error"
            return VerificationResult(
                source_page=source_page,
                target_url=target_url,
                status_code=err.code,
                classification=cls_name,
                final_url=current_url,
                redirect_chain=redirect_chain,
                elapsed_seconds=time.time() - start_time,
                error_message=f"HTTPError {err.code}: {err.reason}",
            )
        except (socket.timeout, TimeoutError):
            return VerificationResult(
                source_page=source_page,
                target_url=target_url,
                classification="fetch_error",
                final_url=current_url,
                redirect_chain=redirect_chain,
                elapsed_seconds=time.time() - start_time,
                error_message=f"Connection timed out after {timeout}s",
            )
        except Exception as err:
            return VerificationResult(
                source_page=source_page,
                target_url=target_url,
                classification="fetch_error",
                final_url=current_url,
                redirect_chain=redirect_chain,
                elapsed_seconds=time.time() - start_time,
                error_message=f"Network error: {err}",
            )

    return VerificationResult(
        source_page=source_page,
        target_url=target_url,
        classification="redirect_error",
        error_message=f"Exceeded maximum allowed redirects ({max_redirects})",
        final_url=current_url,
        redirect_chain=redirect_chain,
        elapsed_seconds=time.time() - start_time,
    )
