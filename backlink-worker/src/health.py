"""Health Check and Diagnostic Monitor for Cloudflare Backlink Agent."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any, Dict

from .d1_adapter import D1Adapter


async def get_health_status(d1: D1Adapter) -> Dict[str, Any]:
    """Generates health diagnostic snapshot."""
    try:
        enabled = await d1.is_agent_enabled()
        mode = await d1.get_agent_mode()
        summary = await d1.get_pipeline_summary()
        d1_ok = True
    except Exception as exc:
        enabled = False
        mode = "unknown"
        summary = {}
        d1_ok = False

    return {
        "status": "healthy" if d1_ok else "degraded",
        "service": "ai-tool-gems-backlink-agent",
        "runtime": "cloudflare-workers",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "gates": {
            "kill_switch_enabled": enabled,
            "mode": mode,
            "owner_approval_required": True,
            "automated_outreach": False,
        },
        "d1_database": {
            "connected": d1_ok,
            "total_prospects": summary.get("total_prospects", 0),
            "live_placements": summary.get("live_placements", 0),
            "verification_runs": summary.get("total_verification_runs", 0),
        },
    }
