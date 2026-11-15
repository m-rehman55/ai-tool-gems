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

        # 1. Temporary failure check (Never mark removed on 5xx or socket timeout)
        if current_result.qualification in (
            LinkQualification.INCONCLUSIVE_SERVER_ERROR,
            LinkQualification.INCONCLUSIVE_TIMEOUT,
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
                notes=f"Temporary verification error: {current_result.error_message}. Preserving prior status.",
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
                notes=f"Page acquired noindex directive via {current_result.noindex_source}",
            )

        # 3. Check if anchor is missing
        if not current_result.anchor_found:
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
                notes="Anchor tag missing from live page DOM",
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
                notes=f"Anchor text modified from '{previous_snapshot.anchor_text}' to '{current_result.actual_anchor_text}'",
            )

        # 6. Clean link retention
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
            notes=f"Backlink retained cleanly. Active for {days_active} day(s).",
        )
