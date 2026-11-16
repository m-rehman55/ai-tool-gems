"""Data models for Backlink Agent verification, tracking, and approval."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class Prospect:
    prospect_domain: str
    prospect_url: str
    site_type: str
    relevance: int
    eligibility: str
    link_terms: str
    action_status: str
    source_page: str
    target_url: str
    anchor_text: str
    link_status: str
    discovered_by_bing: str
    discovered_by_gsc: str
    referral_activity: str
    last_checked: str
    evidence: str
    row_index: int = 0

    @classmethod
    def from_row(cls, row: Dict[str, str], row_index: int = 0) -> Prospect:
        relevance_raw = row.get("relevance", "0").strip()
        try:
            relevance = int(relevance_raw)
        except ValueError:
            relevance = -1

        return cls(
            prospect_domain=row.get("prospect_domain", "").strip(),
            prospect_url=row.get("prospect_url", "").strip(),
            site_type=row.get("site_type", "").strip(),
            relevance=relevance,
            eligibility=row.get("eligibility", "").strip(),
            link_terms=row.get("link_terms", "").strip(),
            action_status=row.get("action_status", "").strip(),
            source_page=row.get("source_page", "").strip(),
            target_url=row.get("target_url", "").strip(),
            anchor_text=row.get("anchor_text", "").strip(),
            link_status=row.get("link_status", "").strip(),
            discovered_by_bing=row.get("discovered_by_bing", "").strip(),
            discovered_by_gsc=row.get("discovered_by_gsc", "").strip(),
            referral_activity=row.get("referral_activity", "").strip(),
            last_checked=row.get("last_checked", "").strip(),
            evidence=row.get("evidence", "").strip(),
            row_index=row_index,
        )

    def to_row(self) -> Dict[str, str]:
        return {
            "prospect_domain": self.prospect_domain,
            "prospect_url": self.prospect_url,
            "site_type": self.site_type,
            "relevance": str(self.relevance),
            "eligibility": self.eligibility,
            "link_terms": self.link_terms,
            "action_status": self.action_status,
            "source_page": self.source_page,
            "target_url": self.target_url,
            "anchor_text": self.anchor_text,
            "link_status": self.link_status,
            "discovered_by_bing": self.discovered_by_bing,
            "discovered_by_gsc": self.discovered_by_gsc,
            "referral_activity": self.referral_activity,
            "last_checked": self.last_checked,
            "evidence": self.evidence,
        }


@dataclass
class VerificationResult:
    source_page: str
    target_url: str
    status_code: int = 0
    classification: str = "unknown"
    target_found: bool = False
    actual_anchor_text: str = ""
    rel_tokens: List[str] = field(default_factory=list)
    final_url: str = ""
    redirect_chain: List[str] = field(default_factory=list)
    is_noindex: bool = False
    canonical_url: Optional[str] = None
    response_bytes: int = 0
    elapsed_seconds: float = 0.0
    error_message: Optional[str] = None
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def is_live(self) -> bool:
        return self.classification.startswith("live_")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_page": self.source_page,
            "target_url": self.target_url,
            "status_code": self.status_code,
            "classification": self.classification,
            "target_found": self.target_found,
            "actual_anchor_text": self.actual_anchor_text,
            "rel_tokens": self.rel_tokens,
            "final_url": self.final_url,
            "redirect_chain": self.redirect_chain,
            "is_noindex": self.is_noindex,
            "canonical_url": self.canonical_url,
            "response_bytes": self.response_bytes,
            "elapsed_seconds": round(self.elapsed_seconds, 3),
            "error_message": self.error_message,
            "timestamp_utc": self.timestamp_utc,
            "is_live": self.is_live,
        }


@dataclass
class ApprovalAction:
    prospect_id: str
    action: str  # approve, reject, defer
    actor_chat_id: str
    actor_user_id: Optional[str]
    timestamp_pkt: str
    draft_hash: str
    previous_status: str
    new_status: str
    reason: Optional[str] = None
    update_id: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prospect_id": self.prospect_id,
            "action": self.action,
            "actor_chat_id": self.actor_chat_id,
            "actor_user_id": self.actor_user_id,
            "timestamp_pkt": self.timestamp_pkt,
            "draft_hash": self.draft_hash,
            "previous_status": self.previous_status,
            "new_status": self.new_status,
            "reason": self.reason,
            "update_id": self.update_id,
        }

