"""D1 Database Adapter for Cloudflare Backlink Agent Worker.

Provides dual-mode query execution:
1. Native Cloudflare D1 binding (env.DB.prepare(...)) in Cloudflare Python Worker runtime.
2. Standard library SQLite adapter for local unit testing and offline development.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import sqlite3
from typing import Any, Dict, List, Optional, Tuple
import uuid


class D1Adapter:
    """Manages transactional state in Cloudflare D1 / SQLite."""

    def __init__(self, db_binding: Any = None, sqlite_conn: Optional[sqlite3.Connection] = None):
        self.db = db_binding
        self.conn = sqlite_conn

    async def execute_query(self, query: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
        """Executes a SELECT query and returns rows as dictionaries."""
        if self.conn is not None:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            cols = [d[0] for d in cursor.description] if cursor.description else []
            return [dict(zip(cols, row)) for row in cursor.fetchall()]

        if self.db is not None:
            stmt = self.db.prepare(query)
            if params:
                stmt = stmt.bind(*params)
            res = await stmt.all()
            if hasattr(res, "results"):
                return list(res.results or [])
            return list(res or [])

        raise RuntimeError("No active D1 binding or SQLite connection available.")

    async def execute_first(self, query: str, params: Tuple[Any, ...] = ()) -> Optional[Dict[str, Any]]:
        """Executes a query and returns the first row."""
        rows = await self.execute_query(query, params)
        return rows[0] if rows else None

    async def execute_mutation(self, query: str, params: Tuple[Any, ...] = ()) -> int:
        """Executes an INSERT / UPDATE / DELETE statement and returns rows changed."""
        if self.conn is not None:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            return cursor.rowcount if cursor.rowcount is not None else 0

        if self.db is not None:
            stmt = self.db.prepare(query)
            if params:
                stmt = stmt.bind(*params)
            res = await stmt.run()
            # Cloudflare D1 meta.changes gives rows affected
            meta = getattr(res, "meta", None)
            if meta and hasattr(meta, "changes"):
                return int(meta.changes)
            return 1

        raise RuntimeError("No active D1 binding or SQLite connection available.")

    async def execute_atomic_approval(
        self,
        prospect_id: str,
        draft_id: Optional[str],
        now_utc: str,
        actor: str,
    ) -> Tuple[bool, str]:
        """Atomically transitions prospect and optional draft to approved status in a single transaction.
        Guarantees that both succeed, or neither succeeds (eliminates partial approval drift).
        """
        if self.conn is not None:
            cursor = self.conn.cursor()
            try:
                self.conn.execute("BEGIN IMMEDIATE")
                # 1. Update prospect
                cursor.execute(
                    "UPDATE prospects SET action_status = 'owner_approved_for_manual_submission', updated_at = ? WHERE id = ? AND action_status != 'owner_approved_for_manual_submission'",
                    (now_utc, prospect_id),
                )
                p_rows = cursor.rowcount
                if p_rows == 0:
                    self.conn.rollback()
                    return False, "Prospect already approved or not in pending state"

                # 2. If draft present, update draft
                if draft_id:
                    cursor.execute(
                        "UPDATE drafts SET status = 'approved', approved_at = ?, approved_by = ? WHERE id = ? AND status = 'pending_approval'",
                        (now_utc, actor, draft_id),
                    )
                    d_rows = cursor.rowcount
                    if d_rows == 0:
                        self.conn.rollback()
                        return False, "Draft already approved or not in pending_approval state"

                self.conn.commit()
                return True, "Approved"
            except Exception:
                self.conn.rollback()
                raise

        if self.db is not None:
            # Cloudflare D1 batch transaction
            statements = [
                self.db.prepare(
                    "UPDATE prospects SET action_status = 'owner_approved_for_manual_submission', updated_at = ? WHERE id = ? AND action_status != 'owner_approved_for_manual_submission'"
                ).bind(now_utc, prospect_id)
            ]
            if draft_id:
                statements.append(
                    self.db.prepare(
                        "UPDATE drafts SET status = 'approved', approved_at = ?, approved_by = ? WHERE id = ? AND status = 'pending_approval'"
                    ).bind(now_utc, actor, draft_id)
                )
            results = await self.db.batch(statements)
            for res in results:
                meta = getattr(res, "meta", None)
                changes = getattr(meta, "changes", 1) if meta else 1
                if changes == 0:
                    return False, "Atomic transition failed: conditional state mismatch"
            return True, "Approved"

        raise RuntimeError("No active D1 binding or SQLite connection available.")

    # Core Kill Switch & Control Gates
    async def is_agent_enabled(self) -> bool:
        row = await self.execute_first(
            "SELECT control_value FROM agent_control WHERE control_key = 'enabled'"
        )
        return bool(row and row.get("control_value") == "true")

    async def get_agent_mode(self) -> str:
        row = await self.execute_first(
            "SELECT control_value FROM agent_control WHERE control_key = 'mode'"
        )
        return str(row.get("control_value", "report_only")) if row else "report_only"

    # Prospects & Verification Runs
    async def get_prospects_for_verification(self, limit: int = 25) -> List[Dict[str, Any]]:
        return await self.execute_query(
            """
            SELECT * FROM prospects 
            WHERE source_page IS NOT NULL AND source_page != '' AND action_status != 'rejected'
            ORDER BY last_checked ASC, relevance DESC 
            LIMIT ?
            """,
            (limit,),
        )

    async def record_verification_run(self, run: Dict[str, Any]) -> None:
        now_utc = datetime.now(timezone.utc).isoformat()
        run_id = f"vrun_{int(datetime.now(timezone.utc).timestamp())}_{run.get('prospect_id', 'p')}"

        await self.execute_mutation(
            """
            INSERT INTO verification_runs (
                id, prospect_id, source_page, target_url, classification,
                http_status, target_found, actual_anchor_text, rel_tokens,
                final_url, redirect_chain, source_noindex, canonical_url,
                response_bytes, elapsed_seconds, error_message, verified_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                run.get("prospect_id"),
                run.get("source_page"),
                run.get("target_url"),
                run.get("classification"),
                run.get("http_status", 0),
                1 if run.get("target_found") else 0,
                run.get("actual_anchor_text", ""),
                json.dumps(run.get("rel_tokens", [])),
                run.get("final_url", ""),
                json.dumps(run.get("redirect_chain", [])),
                1 if run.get("source_noindex") else 0,
                run.get("canonical_url"),
                run.get("response_bytes", 0),
                run.get("elapsed_seconds", 0.0),
                run.get("error_message"),
                now_utc,
            ),
        )

        # Update prospect table with verified findings
        new_link_status = "live" if run.get("classification", "").startswith("live_") else run.get("classification")
        today_date = now_utc.split("T")[0]

        await self.execute_mutation(
            """
            UPDATE prospects 
            SET link_status = ?, last_checked = ?, updated_at = ?
            WHERE id = ?
            """,
            (new_link_status, today_date, now_utc, run.get("prospect_id")),
        )

    # Job Queue Idempotency
    async def claim_job_run(self, job_type: str, idempotency_key: str) -> bool:
        """Atomically claims a job. Returns True if claimed; False if already processed or active."""
        now_utc = datetime.now(timezone.utc).isoformat()
        job_id = f"job_{int(datetime.now(timezone.utc).timestamp())}_{idempotency_key[:8]}"
        try:
            await self.execute_mutation(
                """
                INSERT INTO job_runs (id, job_type, idempotency_key, status, started_at)
                VALUES (?, ?, ?, 'running', ?)
                """,
                (job_id, job_type, idempotency_key, now_utc),
            )
            return True
        except Exception:
            return False  # Violates UNIQUE(idempotency_key)

    async def complete_job_run(self, idempotency_key: str, error: Optional[str] = None) -> None:
        now_utc = datetime.now(timezone.utc).isoformat()
        status = "failed" if error else "completed"
        await self.execute_mutation(
            """
            UPDATE job_runs
            SET status = ?, completed_at = ?, error = ?
            WHERE idempotency_key = ?
            """,
            (status, now_utc, error, idempotency_key),
        )

    # Audit Trail
    async def record_audit_event(
        self, event_type: str, actor: str, entity_id: Optional[str], payload: Dict[str, Any]
    ) -> None:
        now_utc = datetime.now(timezone.utc).isoformat()
        event_id = f"evt_{int(datetime.now(timezone.utc).timestamp() * 1000)}_{uuid.uuid4().hex[:8]}"
        await self.execute_mutation(
            """
            INSERT INTO audit_events (id, event_type, actor, entity_id, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (event_id, event_type, actor, entity_id, json.dumps(payload), now_utc),
        )

    # Summaries
    async def get_pipeline_summary(self) -> Dict[str, Any]:
        total_row = await self.execute_first("SELECT count(*) as c FROM prospects")
        live_row = await self.execute_first("SELECT count(*) as c FROM prospects WHERE link_status = 'live'")
        pending_row = await self.execute_first("SELECT count(*) as c FROM prospects WHERE link_status = 'not_live'")
        runs_row = await self.execute_first("SELECT count(*) as c FROM verification_runs")

        return {
            "total_prospects": total_row.get("c", 0) if total_row else 0,
            "live_placements": live_row.get("c", 0) if live_row else 0,
            "pending_prospects": pending_row.get("c", 0) if pending_row else 0,
            "total_verification_runs": runs_row.get("c", 0) if runs_row else 0,
        }
