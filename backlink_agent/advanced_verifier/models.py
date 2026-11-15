"""Data models for Advanced Backlink Verification and Attribution."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List, Optional


class TargetMatchPolicy:
    """Policy governing destination URL matching flexibility."""

    EXACT_URL = "exact_url"
    ALLOWED_URLS = "allowed_urls"
    ANY_VERIFIED_CANONICAL_ASSET = "any_verified_canonical_asset"


class LinkQualification:
    """Detailed attribution and qualification classifications for backlinks."""

    EDITORIAL_DOFOLLOW = "editorial_dofollow"
    EDITORIAL_NOFOLLOW = "editorial_nofollow"
    USER_GENERATED_UGC = "user_generated_ugc"
    SPONSORED = "sponsored"
    MIXED_QUALIFIED = "mixed_qualified"
    DOMAIN_ASSET_ACCEPTED = "domain_asset_accepted"
    WRONG_TARGET = "wrong_target"
    ANCHOR_MISSING = "anchor_missing"
    SOURCE_NOINDEX = "source_noindex"
    INCONCLUSIVE_SERVER_ERROR = "inconclusive_server_error"
    INCONCLUSIVE_TIMEOUT = "inconclusive_timeout"
    SSRF_BLOCKED = "ssrf_blocked"
    BLOCKED_WAF = "blocked_waf"
    CHALLENGE_REQUIRED = "challenge_required"


@dataclass
class DetailedVerificationResult:
    """Comprehensive, evidence-based backlink audit record."""

    prospect_id: str
    source_page_url: str
    target_asset_url: str
    http_status: int
    final_page_url: str
    redirect_chain: List[str] = field(default_factory=list)
    canonical_url: Optional[str] = None
    is_indexable: bool = True
    noindex_source: Optional[str] = None  # None, meta_robots, x_robots_tag
    anchor_found: bool = False
    actual_anchor_text: str = ""
    actual_href: str = ""
    final_target_destination: str = ""
    target_matches_approved: bool = False
    target_match_policy: str = TargetMatchPolicy.EXACT_URL
    target_match_status: str = ""
    rel_tokens: List[str] = field(default_factory=list)
    qualification: str = LinkQualification.ANCHOR_MISSING
    content_hash: str = ""
    is_live_backlink: bool = False
    error_message: Optional[str] = None
    verified_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def compute_content_hash(self) -> str:
        """Deterministic hash for detecting anchor text or target changes."""
        raw = f"{self.actual_anchor_text}|{self.actual_href}|{self.final_target_destination}|{sorted(self.rel_tokens)}|{self.canonical_url}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prospect_id": self.prospect_id,
            "source_page_url": self.source_page_url,
            "target_asset_url": self.target_asset_url,
            "http_status": self.http_status,
            "final_page_url": self.final_page_url,
            "redirect_chain": self.redirect_chain,
            "canonical_url": self.canonical_url,
            "is_indexable": self.is_indexable,
            "noindex_source": self.noindex_source,
            "anchor_found": self.anchor_found,
            "actual_anchor_text": self.actual_anchor_text,
            "actual_href": self.actual_href,
            "final_target_destination": self.final_target_destination,
            "target_matches_approved": self.target_matches_approved,
            "rel_tokens": self.rel_tokens,
            "qualification": self.qualification,
            "content_hash": self.content_hash,
            "is_live_backlink": self.is_live_backlink,
            "error_message": self.error_message,
            "verified_at": self.verified_at,
        }
