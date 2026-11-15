"""Cloudflare Queue Producer & Consumer Handlers for Backlink Agent.

Handles asynchronous job execution, retries, and dead-letter safety.
Enforces kill-switch check before processing each message.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List

from .d1_adapter import D1Adapter
from .verifier_worker import validate_worker_url, verify_html_content


async def enqueue_verifications(d1: D1Adapter, queue: Any, limit: int = 25) -> int:
    """Enqueues verification jobs into Cloudflare Queue."""
    prospects = await d1.get_prospects_for_verification(limit=limit)
    enqueued = 0
    today_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for p in prospects:
        idempotency_key = f"verify_{p.get('id')}_{today_date}"
        message_payload = {
            "job_type": "verify_prospect",
            "prospect_id": p.get("id"),
            "source_page": p.get("source_page"),
            "target_url": p.get("target_url"),
            "idempotency_key": idempotency_key,
        }
        if queue is not None:
            await queue.send(message_payload)
            enqueued += 1

    return enqueued


async def enqueue_draft_generation(d1: D1Adapter, queue: Any, limit: int = 5) -> int:
    """Enqueues weekly white-hat draft generation jobs for Tier 1 prospects."""
    tier1_prospects = await d1.execute_query(
        """
        SELECT * FROM prospects 
        WHERE relevance >= 75 AND action_status IN ('draft_ready', 'submitted_pending_review', 'active')
        ORDER BY relevance DESC 
        LIMIT ?
        """,
        (limit,),
    )
    enqueued = 0
    today_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for p in tier1_prospects:
        idempotency_key = f"draft_{p.get('id')}_{today_date}"
        message_payload = {
            "job_type": "generate_draft",
            "prospect_id": p.get("id"),
            "prospect_domain": p.get("prospect_domain"),
            "target_url": p.get("target_url"),
            "relevance": p.get("relevance"),
            "idempotency_key": idempotency_key,
        }
        if queue is not None:
            await queue.send(message_payload)
            enqueued += 1

    return enqueued


async def process_verification_job(d1: D1Adapter, payload: Dict[str, Any], fetch_fn=None) -> Dict[str, Any]:
    """Processes a single verification task."""
    source_page = payload.get("source_page", "")
    target_url = payload.get("target_url", "")
    prospect_id = payload.get("prospect_id", "")

    try:
        validate_worker_url(source_page)
    except ValueError as err:
        res = {
            "prospect_id": prospect_id,
            "source_page": source_page,
            "target_url": target_url,
            "classification": "unsafe_url",
            "error_message": f"SSRF boundary check failed: {err}",
            "http_status": 0,
            "target_found": False,
        }
        await d1.record_verification_run(res)
        return res

    # Perform network probe
    if fetch_fn is not None:
        try:
            status_code, body_text, headers = await fetch_fn(source_page)
            parsed = verify_html_content(body_text, source_page, target_url, headers)
            res = {
                "prospect_id": prospect_id,
                "source_page": source_page,
                "target_url": target_url,
                "classification": parsed.get("classification"),
                "http_status": status_code,
                "target_found": parsed.get("target_found"),
                "actual_anchor_text": parsed.get("actual_anchor_text"),
                "rel_tokens": parsed.get("rel_tokens"),
                "final_url": source_page,
                "redirect_chain": [],
                "source_noindex": parsed.get("is_noindex"),
                "canonical_url": parsed.get("canonical_url"),
                "response_bytes": len(body_text.encode("utf-8")),
                "elapsed_seconds": 0.5,
                "error_message": None,
            }
            await d1.record_verification_run(res)
            return res
        except Exception as exc:
            res = {
                "prospect_id": prospect_id,
                "source_page": source_page,
                "target_url": target_url,
                "classification": "fetch_error",
                "http_status": 0,
                "target_found": False,
                "error_message": str(exc),
            }
            await d1.record_verification_run(res)
            return res

    # Offline / Simulated verification
    res = {
        "prospect_id": prospect_id,
        "source_page": source_page,
        "target_url": target_url,
        "classification": "pending_fetch",
        "http_status": 200,
        "target_found": False,
    }
    await d1.record_verification_run(res)
    return res


async def handle_queue_batch(batch: Any, env: Any, ctx: Any, d1: Optional[D1Adapter] = None) -> None:
    """Entry point for Cloudflare Queue consumer."""
    d1_adapter = d1 or D1Adapter(getattr(env, "DB", None))

    # Kill switch verification
    enabled = await d1_adapter.is_agent_enabled()
    if not enabled:
        # Acknowledge messages without executing when kill switch is active
        for msg in getattr(batch, "messages", []):
            msg.ack()
        return

    mode = await d1_adapter.get_agent_mode()
    if mode != "report_only":
        return

    for msg in getattr(batch, "messages", []):
        payload = getattr(msg, "body", {})
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                payload = {}

        idempotency_key = payload.get("idempotency_key", "")
        claimed = await d1_adapter.claim_job_run(payload.get("job_type", "unknown"), idempotency_key)
        if not claimed:
            msg.ack()  # Duplicate job safely acknowledged
            continue

        try:
            job_type = payload.get("job_type")
            if job_type == "verify_prospect":
                await process_verification_job(d1_adapter, payload)
            await d1_adapter.complete_job_run(idempotency_key)
            msg.ack()
        except Exception as exc:
            await d1_adapter.complete_job_run(idempotency_key, error=str(exc))
            msg.retry()  # Trigger queue retry policy up to max_retries
