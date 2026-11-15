"""Reporting Engine for AI Tool Gems Backlink Agent.

Generates comprehensive markdown and JSON reports detailing pipeline health,
verification classifications, 100-point rubric scores, and security audit traces.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .facts import get_verified_facts
from .models import Prospect, VerificationResult
from .tracker import load_tracker_rows, summarize_tracker


REPORTS_DIR = Path("seo-agent/reports/backlinks")


def generate_pipeline_report(
    rows: Optional[List[Dict[str, str]]] = None,
    verification_results: Optional[List[VerificationResult]] = None,
    out_dir: Path = REPORTS_DIR,
) -> Tuple[str, Dict[str, Any]]:
    """Generates executive Markdown and structured JSON reports."""
    if rows is None:
        rows = load_tracker_rows()

    facts = get_verified_facts()
    today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    date_slug = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    enabled = os.environ.get("BACKLINK_AGENT_ENABLED", "false").lower() == "true"
    mode = os.environ.get("BACKLINK_AGENT_MODE", "report_only").lower()

    summary = summarize_tracker(rows)

    # Score distribution based on 100-point rubric
    prioritize: List[Dict[str, str]] = []
    investigate: List[Dict[str, str]] = []
    reject_skip: List[Dict[str, str]] = []

    for r in rows:
        try:
            score = int(r.get("relevance", "0"))
        except ValueError:
            score = 0
        if score >= 75:
            prioritize.append(r)
        elif score >= 55:
            investigate.append(r)
        else:
            reject_skip.append(r)

    # Verification stats if provided
    verif_counts: Dict[str, int] = {}
    if verification_results:
        for v in verification_results:
            verif_counts[v.classification] = verif_counts.get(v.classification, 0) + 1

    md_lines = [
        "# 🔗 AI Tool Gems Backlink Agent Executive Pipeline Report",
        f"**Generated:** `{today_utc}`  ",
        f"**Agent Mode:** `{mode.upper()}` | **Operational Kill Switch:** `{'ENABLED' if enabled else 'DISABLED (Safe Mode)'}`  ",
        f"**Target Canonical Entity:** `{facts.website_url}` (`{facts.brand_name}`)  ",
        "",
        "## 1. Pipeline Summary",
        f"- **Total Tracked Prospects:** {len(rows)}",
        f"- **Live Confirmed Placements:** {summary['by_link'].get('live', 0)}",
        f"- **Pending / Not Live:** {summary['by_link'].get('not_live', 0)}",
        f"- **Disallowed / Rejected:** {summary['by_link'].get('rejected', 0)}",
        f"- **Discovered by Bing:** Yes: {summary['bing'].get('yes', 0)}, Pending: {summary['bing'].get('pending', 0)}, No: {summary['bing'].get('no', 0)}",
        f"- **Discovered by GSC:** Yes: {summary['gsc'].get('yes', 0)}, Pending: {summary['gsc'].get('pending', 0)}, No: {summary['gsc'].get('no', 0)}",
        "",
        "## 2. 100-Point Rubric Tier Breakdown",
        "- **Tier 1 (Prioritize, Score 75-100):** " + f"{len(prioritize)} targets",
        "- **Tier 2 (Investigate, Score 55-74):** " + f"{len(investigate)} targets",
        "- **Tier 3 (Reject/Skip, Score <55):** " + f"{len(reject_skip)} targets",
        "",
        "### Prioritized Prospects (Score >= 75)",
        "| Domain | Type | Score | Action Status | Link Status | Link Terms |",
        "|---|---|---|---|---|---|",
    ]

    for p in prioritize:
        md_lines.append(
            f"| `{p.get('prospect_domain')}` | {p.get('site_type')} | **{p.get('relevance')}** | {p.get('action_status')} | `{p.get('link_status')}` | {p.get('link_terms')[:30]} |"
        )

    if verification_results:
        md_lines.extend([
            "",
            "## 3. Strict HTML Anchor Verification Audit",
            "| Source Page | Target URL | Classification | Status | Target Found | Rel Tokens |",
            "|---|---|---|---|---|---|",
        ])
        for v in verification_results:
            rel_str = ", ".join(v.rel_tokens) if v.rel_tokens else "none (dofollow)"
            md_lines.append(
                f"| `{v.source_page}` | `{v.target_url}` | **`{v.classification}`** | {v.status_code} | {'✅' if v.target_found else '❌'} | `{rel_str}` |"
            )

    md_lines.extend([
        "",
        "## 4. Security & Safety Firewall",
        "- **SSRF Guard:** Active (HTTPS required, RFC 1918 / loopback / CGNAT / AWS metadata blocked).",
        "- **Truth Grounding:** Active (`verified_facts.yml` enforced; no unverified pricing or payment claims).",
        "- **Outreach Boundary:** Autonomous form submission and email blast strictly disabled; owner review only.",
        "- **Git State Isolation:** Approvals stored locally in `seo-agent/data/`; zero write to `main` branch.",
    ])

    markdown_report = "\n".join(md_lines)

    data_report = {
        "generated_at": today_utc,
        "mode": mode,
        "enabled": enabled,
        "summary": summary,
        "rubric_breakdown": {
            "tier1_prioritize": len(prioritize),
            "tier2_investigate": len(investigate),
            "tier3_reject": len(reject_skip),
        },
        "verification_counts": verif_counts,
        "prospects_count": len(rows),
    }

    # Persist report files
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"backlink_report_{date_slug}.md").write_text(markdown_report, encoding="utf-8")
    (out_dir / f"backlink_report_{date_slug}.json").write_text(json.dumps(data_report, indent=2), encoding="utf-8")

    return markdown_report, data_report
