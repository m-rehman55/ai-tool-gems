"""Durable SQLite Store for Backlink Acquisition Lifecycle and Manual Submissions."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional
import uuid

from .models import (
    LifecycleState,
    LifecycleTransitionRecord,
    ManualSubmissionEvidence,
)

logger = logging.getLogger(__name__)

DEFAULT_LIFECYCLE_DB_PATH = Path("seo-agent/data/backlink_lifecycle.db")


class LocalSQLiteLifecycleStore:
    """Crash-resilient SQLite store for prospect states, manual submission proofs, and audit transitions."""

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS prospect_lifecycle (
        prospect_id TEXT PRIMARY KEY,
        prospect_domain TEXT NOT NULL,
        source_page_url TEXT NOT NULL,
        target_asset_url TEXT NOT NULL,
        prospect_type TEXT NOT NULL,
        current_state TEXT NOT NULL,
        score INTEGER NOT NULL DEFAULT 0,
        priority_tier TEXT,
        draft_id TEXT,
        draft_hash TEXT,
        submission_ref TEXT,
        publication_url TEXT,
        first_verified_at TEXT,
        last_verified_at TEXT,
        retention_days INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_lifecycle_state ON prospect_lifecycle(current_state);
    CREATE INDEX IF NOT EXISTS idx_lifecycle_domain ON prospect_lifecycle(prospect_domain);

    CREATE TABLE IF NOT EXISTS lifecycle_transitions (
        transition_id TEXT PRIMARY KEY,
        prospect_id TEXT NOT NULL,
        from_state TEXT NOT NULL,
        to_state TEXT NOT NULL,
        actor TEXT NOT NULL,
        reason TEXT NOT NULL,
        evidence_json TEXT,
        idempotency_key TEXT UNIQUE,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (prospect_id) REFERENCES prospect_lifecycle(prospect_id)
    );
    CREATE INDEX IF NOT EXISTS idx_transitions_prospect ON lifecycle_transitions(prospect_id);
    CREATE INDEX IF NOT EXISTS idx_transitions_timestamp ON lifecycle_transitions(timestamp);

    CREATE TABLE IF NOT EXISTS manual_submission_evidence (
        submission_id TEXT PRIMARY KEY,
        prospect_id TEXT NOT NULL,
        draft_id TEXT NOT NULL,
        draft_hash TEXT NOT NULL,
        destination TEXT NOT NULL,
        method TEXT NOT NULL,
        evidence_ref TEXT NOT NULL,
        publication_url TEXT,
        notes TEXT,
        submission_date TEXT NOT NULL,
        FOREIGN KEY (prospect_id) REFERENCES prospect_lifecycle(prospect_id)
    );
    CREATE INDEX IF NOT EXISTS idx_submissions_prospect ON manual_submission_evidence(prospect_id);
    """

    def __init__(self, db_path: Path | str | None = None):
        self.db_path = Path(db_path) if db_path is not None else DEFAULT_LIFECYCLE_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.executescript(self.SCHEMA)

    def checkpoint_wal(self) -> Dict[str, Any]:
        """Checkpoints SQLite WAL journal into main DB file."""
        with self._get_connection() as conn:
            cursor = conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            res = cursor.fetchone()
            return {"busy": res[0], "log": res[1], "checkpointed": res[2]}

    def register_discovered_prospect(
        self,
        prospect_id: str,
        prospect_domain: str,
        source_page_url: str,
        target_asset_url: str,
        prospect_type: str,
    ) -> bool:
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT OR IGNORE INTO prospect_lifecycle (
                    prospect_id, prospect_domain, source_page_url, target_asset_url,
                    prospect_type, current_state, score, priority_tier,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, 0, 'unscored', ?, ?)
                """,
                (
                    prospect_id,
                    prospect_domain,
                    source_page_url,
                    target_asset_url,
                    prospect_type,
                    LifecycleState.DISCOVERED,
                    now_iso,
                    now_iso,
                ),
            )
            return cursor.rowcount > 0

    def get_prospect(self, prospect_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM prospect_lifecycle WHERE prospect_id = ?", (prospect_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_transition(self, record: LifecycleTransitionRecord) -> bool:
        """Atomically updates prospect state and appends immutable audit transition."""
        now_iso = datetime.now(timezone.utc).isoformat()
        evidence_str = json.dumps(record.evidence_data or {})

        with self._get_connection() as conn:
            cursor = conn.execute("BEGIN IMMEDIATE")
            # If idempotency key provided and already exists, skip
            if record.idempotency_key:
                existing = conn.execute(
                    "SELECT 1 FROM lifecycle_transitions WHERE idempotency_key = ?",
                    (record.idempotency_key,),
                ).fetchone()
                if existing:
                    return False  # Idempotent duplicate safely ignored

            # Update prospect row
            up_cursor = conn.execute(
                """
                UPDATE prospect_lifecycle
                SET current_state = ?,
                    updated_at = ?
                WHERE prospect_id = ? AND current_state = ?
                """,
                (record.to_state, now_iso, record.prospect_id, record.from_state),
            )
            if up_cursor.rowcount == 0:
                conn.rollback()
                return False  # Prior state did not match (transition conflict)

            # Insert audit record
            conn.execute(
                """
                INSERT INTO lifecycle_transitions (
                    transition_id, prospect_id, from_state, to_state,
                    actor, reason, evidence_json, idempotency_key, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.transition_id,
                    record.prospect_id,
                    record.from_state,
                    record.to_state,
                    record.actor,
                    record.reason,
                    evidence_str,
                    record.idempotency_key,
                    record.timestamp,
                ),
            )
            return True

    def record_manual_submission(self, evidence: ManualSubmissionEvidence) -> str:
        """Records owner manual submission evidence and returns submission_id."""
        evidence.validate_no_secrets()
        sub_id = f"sub_{uuid.uuid4().hex[:10]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO manual_submission_evidence (
                    submission_id, prospect_id, draft_id, draft_hash,
                    destination, method, evidence_ref, publication_url,
                    notes, submission_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sub_id,
                    evidence.prospect_id,
                    evidence.draft_id,
                    evidence.draft_hash,
                    evidence.submission_destination,
                    evidence.submission_method,
                    evidence.evidence_ref,
                    evidence.optional_publication_url,
                    evidence.notes,
                    evidence.submission_date,
                ),
            )
            # Update submission reference on prospect
            conn.execute(
                """
                UPDATE prospect_lifecycle
                SET submission_ref = ?,
                    publication_url = COALESCE(?, publication_url),
                    updated_at = ?
                WHERE prospect_id = ?
                """,
                (sub_id, evidence.optional_publication_url, now_iso, evidence.prospect_id),
            )
        return sub_id

    def update_draft_package(
        self, prospect_id: str, draft_id: str, draft_hash: str
    ) -> None:
        """Associates a prepared draft package and its deterministic hash with a prospect."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE prospect_lifecycle
                SET draft_id = ?,
                    draft_hash = ?,
                    updated_at = ?
                WHERE prospect_id = ?
                """,
                (draft_id, draft_hash, now_iso, prospect_id),
            )

    def update_verification_status(
        self,
        prospect_id: str,
        publication_url: str,
        retention_days: int = 0,
    ) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE prospect_lifecycle
                SET publication_url = ?,
                    first_verified_at = COALESCE(first_verified_at, ?),
                    last_verified_at = ?,
                    retention_days = ?
                WHERE prospect_id = ?
                """,
                (publication_url, now_iso, now_iso, retention_days, prospect_id),
            )

    def get_lifecycle_funnel_counts(self) -> Dict[str, int]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT current_state, COUNT(*) as count FROM prospect_lifecycle GROUP BY current_state"
            )
            counts = {
                LifecycleState.DISCOVERED: 0,
                LifecycleState.EVIDENCE_VERIFIED: 0,
                LifecycleState.SCORED: 0,
                LifecycleState.DRAFT_READY: 0,
                LifecycleState.OWNER_APPROVED: 0,
                LifecycleState.MANUALLY_SUBMITTED: 0,
                LifecycleState.PUBLISHED: 0,
                LifecycleState.BACKLINK_VERIFIED: 0,
                LifecycleState.RETAINED: 0,
                LifecycleState.QUARANTINED: 0,
                LifecycleState.REJECTED: 0,
                LifecycleState.SUBMISSION_FAILED: 0,
                LifecycleState.VERIFICATION_FAILED: 0,
                LifecycleState.VERIFICATION_INCONCLUSIVE: 0,
                LifecycleState.LINK_CHANGED: 0,
                LifecycleState.LINK_REMOVED: 0,
                LifecycleState.EXPIRED: 0,
            }
            for row in cursor.fetchall():
                counts[row["current_state"]] = row["count"]
            return counts
