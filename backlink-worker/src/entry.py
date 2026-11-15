"""Main Cloudflare Python Worker Entrypoint for AI Tool Gems Backlink Agent.

Handles:
- HTTP fetch routes (/health, /telegram/webhook)
- Cron triggers (verification, weekly drafts, health checks)
- Asynchronous queue batch consumption
"""

from __future__ import annotations

import json
from typing import Any

from .approval_worker import WorkerApprovalEngine
from .d1_adapter import D1Adapter
from .health import get_health_status
from .queue_handlers import enqueue_draft_generation, enqueue_verifications, handle_queue_batch

try:
    from workers import Response, WorkerEntrypoint
except ImportError:
    # Local development / test fallback
    class WorkerEntrypoint:
        pass

    class Response:
        def __init__(self, body: str, status: int = 200, headers: dict = None):
            self.body = body
            self.status = status
            self.headers = headers or {}


class Default(WorkerEntrypoint):
    """Cloudflare Python Worker Entrypoint."""

    async def fetch(self, request: Any) -> Any:
        url_str = getattr(request, "url", "http://localhost/")
        method = getattr(request, "method", "GET").upper()
        env = getattr(self, "env", None)
        d1 = D1Adapter(getattr(env, "DB", None))

        # 1. Root diagnostic info
        if method == "GET" and (url_str.endswith("/") or url_str.endswith(":8787")):
            return Response(
                json.dumps({
                    "service": "ai-tool-gems-backlink-agent",
                    "status": "online",
                    "runtime": "cloudflare-workers-python",
                    "endpoints": ["/health", "/telegram/webhook"],
                }),
                headers={"Content-Type": "application/json"},
            )

        # 2. Health check route
        if method == "GET" and "/health" in url_str:
            health = await get_health_status(d1)
            return Response(
                json.dumps(health, indent=2),
                status=200 if health["status"] == "healthy" else 503,
                headers={"Content-Type": "application/json"},
            )

        # 3. Telegram Webhook route
        if method == "POST" and "/telegram/webhook" in url_str:
            owner_chat_id = getattr(env, "TELEGRAM_OWNER_CHAT_ID", "")
            owner_user_id = getattr(env, "TELEGRAM_OWNER_USER_ID", None)

            engine = WorkerApprovalEngine(d1, owner_chat_id, owner_user_id)

            try:
                body_bytes = await request.text()
                update_data = json.loads(body_bytes)
            except Exception:
                return Response(json.dumps({"error": "Malformed JSON"}), status=400)

            reply_text = await engine.handle_update(update_data)

            # Optional: send Telegram reply back to chat if token is configured
            token = getattr(env, "TELEGRAM_BOT_TOKEN", "")
            chat_id = update_data.get("message", {}).get("chat", {}).get("id")
            if token and chat_id:
                try:
                    # In Cloudflare Worker, send response via fetch
                    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
                    send_payload = json.dumps({"chat_id": chat_id, "text": reply_text})
                    # Cloudflare JS fetch or fallback
                    from js import fetch as js_fetch, Headers  # type: ignore
                    headers = Headers.new()
                    headers.set("Content-Type", "application/json")
                    await js_fetch(send_url, method="POST", body=send_payload, headers=headers)
                except Exception:
                    pass  # Keep response clean

            return Response(
                json.dumps({"ok": True, "reply": reply_text}),
                headers={"Content-Type": "application/json"},
            )

        return Response(json.dumps({"error": "Not Found"}), status=404)

    async def scheduled(self, controller: Any, env: Any, ctx: Any) -> None:
        """Executes on Cloudflare Cron Triggers."""
        d1 = D1Adapter(getattr(env, "DB", None))
        queue = getattr(env, "BACKLINK_QUEUE", None)

        # Hard Kill-Switch Check
        enabled = await d1.is_agent_enabled()
        if not enabled:
            return  # Fail closed

        mode = await d1.get_agent_mode()
        if mode != "report_only":
            return  # Safety freeze

        cron = getattr(controller, "cron", "")

        # 1. Verification Cadence (4x daily)
        if cron == "0 1,7,13,19 * * *":
            max_verif = int(getattr(env, "MAX_VERIFICATIONS_PER_RUN", 25))
            await enqueue_verifications(d1, queue, limit=max_verif)

        # 2. Weekly Draft Generation & Executive Cycle (Sunday 08:00 PKT)
        elif cron == "0 3 * * 0":
            max_drafts = int(getattr(env, "MAX_DRAFTS_PER_RUN", 5))
            await enqueue_draft_generation(d1, queue, limit=max_drafts)

        # 3. Health & Audit Heartbeat
        elif cron == "*/30 * * * *":
            await d1.record_audit_event("cron_heartbeat", "cloudflare_cron", None, {"cron": cron})

    async def queue(self, batch: Any, env: Any, ctx: Any) -> None:
        """Consumes messages from Cloudflare Queue."""
        await handle_queue_batch(batch, env, ctx)
