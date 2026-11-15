"""Advanced Backlink Verification Engine with Multi-Hop SSRF Security and Context Attribution."""

from __future__ import annotations

import io
import logging
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Tuple

from backlink_agent.security import (
    SSRFSecurityError,
    normalize_target_url,
    validate_and_sanitize_url,
)
from backlink_agent.verifier import BacklinkHTMLParser
from .models import DetailedVerificationResult, LinkQualification

logger = logging.getLogger(__name__)

USER_AGENT = "AIToolGems-AdvancedVerifier/2.0 (+https://aitoolgems.tech/llms.txt)"
DEFAULT_TIMEOUT = 12.0
DEFAULT_MAX_BYTES = 2 * 1024 * 1024  # 2 MB limit
DEFAULT_MAX_DECOMPRESSED_BYTES = 4 * 1024 * 1024  # 4 MB decompressed expansion limit
DEFAULT_MAX_REDIRECTS = 5


class AdvancedBacklinkVerifier:
    """Verifies backlink presence, anchor visibility, rel qualifications, canonicals, and indexability."""

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT,
        max_bytes: int = DEFAULT_MAX_BYTES,
        max_decompressed_bytes: int = DEFAULT_MAX_DECOMPRESSED_BYTES,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
    ):
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.max_decompressed_bytes = max_decompressed_bytes
        self.max_redirects = max_redirects

    def verify_html(
        self,
        html_text: str,
        base_url: str,
        target_url: str,
        http_status: int = 200,
        response_headers: Optional[Dict[str, str]] = None,
        prospect_id: str = "",
        redirect_chain: Optional[List[str]] = None,
    ) -> DetailedVerificationResult:
        """Parses HTML DOM and evaluates backlink qualification without making network calls."""
        parser = BacklinkHTMLParser(base_url)
        try:
            parser.feed(html_text)
        except Exception:
            pass  # Evaluate what was successfully parsed

        headers = response_headers or {}
        is_noindex = parser.is_noindex
        noindex_source = "meta_robots" if parser.is_noindex else None

        for k, v in headers.items():
            if k.lower() == "x-robots-tag" and any(tok in v.lower() for tok in ("noindex", "none")):
                is_noindex = True
                noindex_source = "x_robots_tag"
                break

        norm_approved_target = normalize_target_url(target_url)
        target_domain = urllib.parse.urlsplit(norm_approved_target).netloc.lower()

        matching_anchor = None
        wrong_target_anchor = None

        for anchor in parser.anchors:
            norm_anchor = normalize_target_url(anchor.resolved_href)
            if norm_anchor == norm_approved_target:
                matching_anchor = anchor
                break
            anchor_netloc = urllib.parse.urlsplit(norm_anchor).netloc.lower()
            if anchor_netloc == target_domain and not wrong_target_anchor:
                wrong_target_anchor = anchor

        redirects = redirect_chain or [base_url]
        final_url = redirects[-1] if redirects else base_url

        res = DetailedVerificationResult(
            prospect_id=prospect_id,
            source_page_url=base_url,
            target_asset_url=target_url,
            http_status=http_status,
            final_page_url=final_url,
            redirect_chain=redirects,
            canonical_url=parser.canonical_url,
            is_indexable=not is_noindex,
            noindex_source=noindex_source,
        )

        if matching_anchor:
            res.anchor_found = True
            res.actual_anchor_text = matching_anchor.text
            res.actual_href = matching_anchor.raw_href
            res.final_target_destination = matching_anchor.resolved_href
            res.target_matches_approved = True
            res.rel_tokens = matching_anchor.rel_tokens

            tokens_set = set(t.lower() for t in matching_anchor.rel_tokens)
            if is_noindex:
                res.qualification = LinkQualification.SOURCE_NOINDEX
                res.is_live_backlink = False
            elif "sponsored" in tokens_set:
                res.qualification = LinkQualification.SPONSORED
                res.is_live_backlink = True
            elif "ugc" in tokens_set:
                res.qualification = LinkQualification.USER_GENERATED_UGC
                res.is_live_backlink = True
            elif "nofollow" in tokens_set:
                res.qualification = LinkQualification.EDITORIAL_NOFOLLOW
                res.is_live_backlink = True
            else:
                res.qualification = LinkQualification.EDITORIAL_DOFOLLOW
                res.is_live_backlink = True

        elif wrong_target_anchor:
            res.anchor_found = True
            res.actual_anchor_text = wrong_target_anchor.text
            res.actual_href = wrong_target_anchor.raw_href
            res.final_target_destination = wrong_target_anchor.resolved_href
            res.target_matches_approved = False
            res.rel_tokens = wrong_target_anchor.rel_tokens
            res.qualification = LinkQualification.WRONG_TARGET
            res.is_live_backlink = False

        else:
            res.anchor_found = False
            res.qualification = LinkQualification.ANCHOR_MISSING
            res.is_live_backlink = False

        res.content_hash = res.compute_content_hash()
        return res

    def verify_url(
        self, source_page_url: str, target_asset_url: str, prospect_id: str = ""
    ) -> DetailedVerificationResult:
        """Fetches live source page via HTTPS, enforcing multi-hop SSRF validation and 2MB stream cap."""
        # 1. SSRF Pre-flight check
        try:
            current_url = validate_and_sanitize_url(source_page_url)
        except SSRFSecurityError as e:
            res = DetailedVerificationResult(
                prospect_id=prospect_id,
                source_page_url=source_page_url,
                target_asset_url=target_asset_url,
                http_status=0,
                final_page_url=source_page_url,
                qualification=LinkQualification.SSRF_BLOCKED,
                is_live_backlink=False,
                error_message=f"SSRF Check Failed: {e}",
            )
            res.content_hash = res.compute_content_hash()
            return res

        redirect_chain = [current_url]
        hop_count = 0

        # Follow redirects with per-hop SSRF check
        while hop_count < self.max_redirects:
            try:
                req = urllib.request.Request(
                    current_url,
                    headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
                )
                opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)

                class NoRedirect(urllib.request.HTTPRedirectHandler):
                    def redirect_request(self, req, fp, code, msg, headers, newurl):
                        return None  # Handle manually to check SSRF on each hop

                opener = urllib.request.build_opener(NoRedirect)
                with opener.open(req, timeout=self.timeout) as resp:
                    status = resp.status
                    headers = dict(resp.headers)

                    if status in (301, 302, 303, 307, 308):
                        location = resp.headers.get("Location")
                        if not location:
                            break
                        next_url = urllib.parse.urljoin(current_url, location)
                        current_url = validate_and_sanitize_url(next_url)
                        redirect_chain.append(current_url)
                        hop_count += 1
                        continue

                    # Terminal response
                    body_bytes = resp.read(self.max_bytes)

                    # Decompression limit guard: prevent compressed expansion bombs
                    encoding = (headers.get("Content-Encoding") or headers.get("content-encoding") or "").lower()
                    if "gzip" in encoding:
                        import gzip
                        try:
                            gz = gzip.GzipFile(fileobj=io.BytesIO(body_bytes))
                            body_bytes = gz.read(self.max_decompressed_bytes)
                        except Exception as e:
                            logger.warning("Gzip decompression failed for %s: %s", current_url, e)
                    elif "deflate" in encoding:
                        import zlib
                        try:
                            body_bytes = zlib.decompress(body_bytes, 15, self.max_decompressed_bytes)
                        except Exception as e:
                            logger.warning("Deflate decompression failed for %s: %s", current_url, e)

                    html_text = body_bytes.decode("utf-8", errors="replace")

                    return self.verify_html(
                        html_text=html_text,
                        base_url=current_url,
                        target_url=target_asset_url,
                        http_status=status,
                        response_headers=headers,
                        prospect_id=prospect_id,
                        redirect_chain=redirect_chain,
                    )

            except (socket.timeout, TimeoutError) as e:
                res = DetailedVerificationResult(
                    prospect_id=prospect_id,
                    source_page_url=source_page_url,
                    target_asset_url=target_asset_url,
                    http_status=0,
                    final_page_url=current_url,
                    redirect_chain=redirect_chain,
                    qualification=LinkQualification.INCONCLUSIVE_TIMEOUT,
                    is_live_backlink=False,
                    error_message=f"Network Timeout: {e}",
                )
                res.content_hash = res.compute_content_hash()
                return res

            except urllib.error.HTTPError as e:
                status = e.code
                if status >= 500:
                    res = DetailedVerificationResult(
                        prospect_id=prospect_id,
                        source_page_url=source_page_url,
                        target_asset_url=target_asset_url,
                        http_status=status,
                        final_page_url=current_url,
                        redirect_chain=redirect_chain,
                        qualification=LinkQualification.INCONCLUSIVE_SERVER_ERROR,
                        is_live_backlink=False,
                        error_message=f"Server Error HTTP {status}",
                    )
                    res.content_hash = res.compute_content_hash()
                    return res
                else:
                    res = DetailedVerificationResult(
                        prospect_id=prospect_id,
                        source_page_url=source_page_url,
                        target_asset_url=target_asset_url,
                        http_status=status,
                        final_page_url=current_url,
                        redirect_chain=redirect_chain,
                        qualification=LinkQualification.ANCHOR_MISSING,
                        is_live_backlink=False,
                        error_message=f"HTTP Client Error {status}",
                    )
                    res.content_hash = res.compute_content_hash()
                    return res

            except Exception as e:
                res = DetailedVerificationResult(
                    prospect_id=prospect_id,
                    source_page_url=source_page_url,
                    target_asset_url=target_asset_url,
                    http_status=0,
                    final_page_url=current_url,
                    redirect_chain=redirect_chain,
                    qualification=LinkQualification.ANCHOR_MISSING,
                    is_live_backlink=False,
                    error_message=str(e),
                )
                res.content_hash = res.compute_content_hash()
                return res

        # Max redirects exceeded
        res = DetailedVerificationResult(
            prospect_id=prospect_id,
            source_page_url=source_page_url,
            target_asset_url=target_asset_url,
            http_status=0,
            final_page_url=current_url,
            redirect_chain=redirect_chain,
            qualification=LinkQualification.ANCHOR_MISSING,
            is_live_backlink=False,
            error_message="Exceeded max redirect hops",
        )
        res.content_hash = res.compute_content_hash()
        return res
