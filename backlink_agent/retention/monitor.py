"""Backlink Retention Monitor managing 7, 30, and 90-day verification milestones."""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional

from backlink_agent.advanced_verifier.models import DetailedVerificationResult, LinkQualification
from .models import RetentionSnapshot, RetentionStatus

logger = logging.getLogger(__name__)


class RetentionMonitor:
    """Evaluates link persistence, tracks anchor/target alterations, and manages retention milestones."""

    @staticmethod
    def evaluate_retention(
        current_result: DetailedVerificationResult,
        days_active: int,
        previous_snapshot: Optional[RetentionSnapshot] = None,
    ) -> RetentionSnapshot:
        now_iso = datetime.now(timezone.utc).isoformat()
        prev_hash = previous_snapshot.content_hash if previous_snapshot else None
        prev_failures = previous_snapshot.consecutive_failures if previous_snapshot else 0

        # 1. Temporary failure check (Never mark removed on 5xx, 429 rate limit, or socket timeout)
        if (
            current_result.qualification in (
                LinkQualification.INCONCLUSIVE_SERVER_ERROR,
                LinkQualification.INCONCLUSIVE_TIMEOUT,
            )
            or current_result.http_status in (429, 500, 502, 503, 504)
        ):
            return RetentionSnapshot(
                prospect_id=current_result.prospect_id,
                verification_date=now_iso,
                days_since_first_verified=days_active,
                qualification=current_result.qualification,
                anchor_text=previous_snapshot.anchor_text if previous_snapshot else "",
                target_destination=previous_snapshot.target_destination if previous_snapshot else "",
                content_hash=prev_hash or current_result.content_hash,
                previous_content_hash=prev_hash,
                status_detected=RetentionStatus.INCONCLUSIVE_TEMPORARY_FAILURE,
                consecutive_failures=prev_failures,
                notes=f"Temporary verification error: {current_result.error_message or f'HTTP {current_result.http_status}'}. Preserving prior status.",
            )

        # 1b. Access Restricted / WAF Check (HTTP 403)
        if current_result.http_status == 403:
            return RetentionSnapshot(
                prospect_id=current_result.prospect_id,
                verification_date=now_iso,
                days_since_first_verified=days_active,
                qualification=current_result.qualification,
                anchor_text=previous_snapshot.anchor_text if previous_snapshot else "",
                target_destination=previous_snapshot.target_destination if previous_snapshot else "",
                content_hash=prev_hash or current_result.content_hash,
                previous_content_hash=prev_hash,
                status_detected=RetentionStatus.INCONCLUSIVE_ACCESS_RESTRICTED,
                consecutive_failures=prev_failures,
                notes="HTTP 403 Access Restricted / WAF challenge; preserving prior verified status.",
            )

        # 1c. HTTP 410 Gone Check (Strong removal evidence; repeat confirmation required for permanent removal)
        if current_result.http_status == 410:
            if previous_snapshot and previous_snapshot.status_detected in (
                RetentionStatus.STRONG_REMOVAL_EVIDENCE,
                RetentionStatus.SUSPECTED_REMOVAL,
            ) and prev_failures >= 1:
                return RetentionSnapshot(
                    prospect_id=current_result.prospect_id,
                    verification_date=now_iso,
                    days_since_first_verified=days_active,
                    qualification=current_result.qualification,
                    anchor_text="",
                    target_destination="",
                    content_hash=current_result.content_hash,
                    previous_content_hash=prev_hash,
                    status_detected=RetentionStatus.LINK_REMOVED,
                    consecutive_failures=prev_failures + 1,
                    notes="HTTP 410 Gone confirmed on repeat verification (Confirmed Removal).",
                )
            else:
                return RetentionSnapshot(
                    prospect_id=current_result.prospect_id,
                    verification_date=now_iso,
                    days_since_first_verified=days_active,
                    qualification=current_result.qualification,
                    anchor_text="",
                    target_destination="",
                    content_hash=current_result.content_hash,
                    previous_content_hash=prev_hash,
                    status_detected=RetentionStatus.STRONG_REMOVAL_EVIDENCE,
                    consecutive_failures=1,
                    notes="Source page returned HTTP 410 Gone. Strong removal evidence; repeat confirmation required.",
                )

        # 2. Check if page became noindex
        if not current_result.is_indexable or current_result.qualification == LinkQualification.SOURCE_NOINDEX:
            return RetentionSnapshot(
                prospect_id=current_result.prospect_id,
                verification_date=now_iso,
                days_since_first_verified=days_active,
                qualification=current_result.qualification,
                anchor_text=current_result.actual_anchor_text,
                target_destination=current_result.final_target_destination,
                content_hash=current_result.content_hash,
                previous_content_hash=prev_hash,
                status_detected=RetentionStatus.NOINDEX_ADDED,
                consecutive_failures=prev_failures,
                notes=f"Page acquired noindex directive via {current_result.noindex_source}",
            )

        # 3. Check if anchor is missing or page returned HTTP 404 (Suspected removal vs confirmed on repeat)
        if not current_result.anchor_found or current_result.http_status == 404:
            if previous_snapshot and previous_snapshot.status_detected in (
                RetentionStatus.SUSPECTED_REMOVAL,
                RetentionStatus.STRONG_REMOVAL_EVIDENCE,
            ) and prev_failures >= 1:
                return RetentionSnapshot(
                    prospect_id=current_result.prospect_id,
                    verification_date=now_iso,
                    days_since_first_verified=days_active,
                    qualification=current_result.qualification,
                    anchor_text="",
                    target_destination="",
                    content_hash=current_result.content_hash,
                    previous_content_hash=prev_hash,
                    status_detected=RetentionStatus.LINK_REMOVED,
                    consecutive_failures=prev_failures + 1,
                    notes=f"Confirmed removal: anchor missing/404 confirmed on repeat check ({current_result.http_status}).",
                )
            else:
                return RetentionSnapshot(
                    prospect_id=current_result.prospect_id,
                    verification_date=now_iso,
                    days_since_first_verified=days_active,
                    qualification=current_result.qualification,
                    anchor_text=previous_snapshot.anchor_text if previous_snapshot else "",
                    target_destination=previous_snapshot.target_destination if previous_snapshot else "",
                    content_hash=current_result.content_hash,
                    previous_content_hash=prev_hash,
                    status_detected=RetentionStatus.SUSPECTED_REMOVAL,
                    consecutive_failures=1,
                    notes=f"Suspected removal: anchor missing or HTTP {current_result.http_status}. Recheck scheduled before confirmed removal.",
                )

        # 4. Check target URL mismatch
        if not current_result.target_matches_approved:
            return RetentionSnapshot(
                prospect_id=current_result.prospect_id,
                verification_date=now_iso,
                days_since_first_verified=days_active,
                qualification=current_result.qualification,
                anchor_text=current_result.actual_anchor_text,
                target_destination=current_result.final_target_destination,
                content_hash=current_result.content_hash,
                previous_content_hash=prev_hash,
                status_detected=RetentionStatus.TARGET_CHANGED,
                consecutive_failures=prev_failures,
                notes=f"Link href target changed to {current_result.final_target_destination}",
            )

        # 5. Check anchor text change
        if previous_snapshot and previous_snapshot.anchor_text and previous_snapshot.anchor_text != current_result.actual_anchor_text:
            return RetentionSnapshot(
                prospect_id=current_result.prospect_id,
                verification_date=now_iso,
                days_since_first_verified=days_active,
                qualification=current_result.qualification,
                anchor_text=current_result.actual_anchor_text,
                target_destination=current_result.final_target_destination,
                content_hash=current_result.content_hash,
                previous_content_hash=prev_hash,
                status_detected=RetentionStatus.ANCHOR_CHANGED,
                consecutive_failures=prev_failures,
                notes=f"Anchor text modified from '{previous_snapshot.anchor_text}' to '{current_result.actual_anchor_text}'",
            )

        # 6. Check recovery (If previously suspected missing, access restricted, or degraded)
        if previous_snapshot and previous_snapshot.status_detected in (
            RetentionStatus.SUSPECTED_REMOVAL,
            RetentionStatus.STRONG_REMOVAL_EVIDENCE,
            RetentionStatus.INCONCLUSIVE_ACCESS_RESTRICTED,
            RetentionStatus.INCONCLUSIVE_TEMPORARY_FAILURE,
            RetentionStatus.ANCHOR_CHANGED,
            RetentionStatus.TARGET_CHANGED,
            RetentionStatus.NOINDEX_ADDED,
            RetentionStatus.LINK_REMOVED,
        ):
            return RetentionSnapshot(
                prospect_id=current_result.prospect_id,
                verification_date=now_iso,
                days_since_first_verified=days_active,
                qualification=current_result.qualification,
                anchor_text=current_result.actual_anchor_text,
                target_destination=current_result.final_target_destination,
                content_hash=current_result.content_hash,
                previous_content_hash=prev_hash,
                status_detected=RetentionStatus.RECOVERED,
                consecutive_failures=0,
                notes="Placement successfully re-verified as healthy (Recovered).",
            )

        # 7. Clean link retention
        return RetentionSnapshot(
            prospect_id=current_result.prospect_id,
            verification_date=now_iso,
            days_since_first_verified=days_active,
            qualification=current_result.qualification,
            anchor_text=current_result.actual_anchor_text,
            target_destination=current_result.final_target_destination,
            content_hash=current_result.content_hash,
            previous_content_hash=prev_hash,
            status_detected=RetentionStatus.RETAINED,
            consecutive_failures=0,
            notes=f"Backlink retained cleanly. Active for {days_active} day(s).",
        )
