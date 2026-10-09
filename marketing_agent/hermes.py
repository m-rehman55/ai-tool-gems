"""Hermes SEO OS orchestration, reporting, and Telegram delivery."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import Settings
from .hermes_audit import audit_repository, fetch_production
from .hermes_connectors import collect_online
from .hermes_models import ConnectorResult, DataStatus, RunContext
from .hermes_store import HermesStore
from .telegram import TelegramClient, TelegramError


def _store(settings: Settings, root: Path) -> HermesStore:
    database_path = root / "marketing_agent" / "data" / "hermes.db"
    snapshot_dir = root / ".seo-cache" / "hermes"
    return HermesStore(database_path, snapshot_dir)


def _source_status(connectors: list[ConnectorResult]) -> dict[str, str]:
    return {connector.name: connector.status.value for connector in connectors}


def _production_checks(site_url: str) -> dict[str, Any]:
    checks = {}
    for suffix in ("/", "/robots.txt", "/sitemap.xml"):
        checks[suffix] = fetch_production(site_url.rstrip("/") + suffix)
    return checks


def collect_run(settings: Settings, root: Path, online: bool = False) -> dict[str, Any]:
    run_id = f"{datetime.now(settings.timezone).date().isoformat()}-{'online' if online else 'offline'}"
    context = RunContext("ONLINE" if online else "OFFLINE", settings.site_url, str(root), run_id)
    audit = audit_repository(root, settings.site_url)
    connectors: list[ConnectorResult] = []
    production = None
    if online:
        production = _production_checks(settings.site_url)
        connectors = collect_online(settings.site_url)
    else:
        connectors = [ConnectorResult("GSC", DataStatus.NOT_AVAILABLE, "Offline local audit", details={"reason": "Online collection was not requested."}), ConnectorResult("GA4", DataStatus.NOT_AVAILABLE, "Offline local audit", details={"reason": "Online collection was not requested."}), ConnectorResult("SERP", DataStatus.NOT_AVAILABLE, "Offline local audit", details={"reason": "Online collection was not requested."}), ConnectorResult("Keywords", DataStatus.NOT_AVAILABLE, "Offline local audit", details={"reason": "Online collection was not requested."}), ConnectorResult("Backlinks", DataStatus.NOT_AVAILABLE, "Offline local audit", details={"reason": "Online collection was not requested."}), ConnectorResult("Trends", DataStatus.NOT_AVAILABLE, "Offline local audit", details={"reason": "Online collection was not requested."})]
    report = {"status": "COMPLETED", "mode": context.mode, "run_id": run_id, "audit": audit.to_dict(), "production": production, "sources": _source_status(connectors), "connectors": [connector.to_dict() for connector in connectors], "blockers": _blockers(connectors)}
    path = _store(settings, root).save(context, report, connectors)
    report["snapshot"] = str(path)
    return report


def _blockers(connectors: list[ConnectorResult]) -> list[dict[str, Any]]:
    blockers = []
    for connector in connectors:
        if connector.status in {DataStatus.ACCESS_REQUIRED, DataStatus.ERROR, DataStatus.NOT_AVAILABLE, DataStatus.NOT_SUPPORTED}:
            blockers.append({"source": connector.name, "status": connector.status.value, "reason": connector.error or connector.details.get("reason") or connector.details.get("required")})
    return blockers


def _latest(settings: Settings, root: Path) -> dict[str, Any]:
    report = _store(settings, root).latest()
    if not report:
        raise RuntimeError("No Hermes run exists. Run 'python -m marketing_agent hermes audit --offline' first.")
    return report


def format_report(report: dict[str, Any]) -> str:
    audit = report.get("audit", {})
    summary = audit.get("summary", {})
    lines = [
        "AIToolGems HERMES SEO REPORT",
        f"Run: {report.get('run_id', 'unknown')} | Mode: {report.get('mode', 'unknown')}",
        "",
        "LOCAL SEO AUDIT",
        f"Pages: {summary.get('pages', 'NOT_AVAILABLE')} | Pakistan Pages: {summary.get('pk_pages', 'NOT_AVAILABLE')}",
        f"Issues: {summary.get('issues', 'NOT_AVAILABLE')} | P0: {summary.get('p0', 'NOT_AVAILABLE')} | P1: {summary.get('p1', 'NOT_AVAILABLE')} | P2: {summary.get('p2', 'NOT_AVAILABLE')}",
        "",
        "DATA HEALTH",
    ]
    for name, status in report.get("sources", {}).items():
        lines.append(f"{name}: {status}")
    production = report.get("production")
    if production:
        lines.extend(["", "PRODUCTION"])
        for path, check in production.items():
            lines.append(f"{path}: {check.get('status', 'UNKNOWN')}" + (f" ({check.get('http_status')})" if check.get("http_status") else ""))
    blockers = report.get("blockers", [])
    if blockers:
        lines.extend(["", "BLOCKERS"])
        for blocker in blockers:
            lines.append(f"- {blocker['source']}: {blocker['status']} — {blocker['reason']}")
    actions = audit.get("actions", [])
    if actions:
        lines.extend(["", "ACTIONS"])
        for action in actions[:12]:
            lines.append(f"- {action['decision']}: {action['action']} — {action['reason']}")
    return "\n".join(lines)[:3900]


def send_report(settings: Settings, report: dict[str, Any]) -> dict[str, Any]:
    if not settings.owner_reports_ready:
        return {"status": DataStatus.ACCESS_REQUIRED.value, "source": "Telegram", "required": ["TELEGRAM_BOT_TOKEN", "TELEGRAM_OWNER_CHAT_ID"]}
    try:
        result = TelegramClient(settings.telegram_bot_token).send_with_retry(settings.telegram_owner_chat_id, format_report(report))
        return {"status": DataStatus.VERIFIED.value, "source": "Telegram", "message_id": result.get("message_id")}
    except TelegramError as exc:
        return {"status": DataStatus.ERROR.value, "source": "Telegram", "error": str(exc)}


def audit(settings: Settings, root: Path) -> dict[str, Any]:
    return collect_run(settings, root, online=False)


def collect(settings: Settings, root: Path) -> dict[str, Any]:
    return collect_run(settings, root, online=True)


def report(settings: Settings, root: Path, telegram: bool = False) -> dict[str, Any]:
    result = _latest(settings, root)
    result = dict(result)
    if telegram:
        result["telegram"] = send_report(settings, result)
    return result


def run(settings: Settings, root: Path, online: bool = False) -> dict[str, Any]:
    result = collect_run(settings, root, online=online)
    result["telegram"] = send_report(settings, result)
    return result
