"""Command-line interface for HERMES Content Research Agent (AGENT-09)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from content_agent.queue_manager import ContentQueueManager
from content_agent.research import create_research_record

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="HERMES Content & Editorial Intelligence CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("queue", help="Display editorial review queue status")

    res_parser = subparsers.add_parser("research", help="Generate article research record")
    res_parser.add_argument("slug", help="Target guide slug (e.g. cursor-ai-pakistan-guide)")
    res_parser.add_argument("--tool", default="cursor", help="Tool ID")
    res_parser.add_argument("--name", default="Cursor AI", help="Tool display name")
    res_parser.add_argument("--price", type=int, default=5500, help="PKR price")

    app_parser = subparsers.add_parser("approve", help="Explicit editorial approval gate")
    app_parser.add_argument("slug", help="Slug to approve")
    app_parser.add_argument("--by", default="Editorial Lead", help="Approver identity")

    subparsers.add_parser("audit", help="Run comprehensive content & editorial audit")

    args = parser.parse_args()
    mgr = ContentQueueManager()

    if args.command == "queue":
        queue = mgr.load_queue()
        published_slugs = {p.parent.name for p in Path("guides").glob("*/index.html")}
        print(f"\n=== EDITORIAL CONTENT QUEUE ({len(queue)} items) ===")
        print(f"{'Status':<16} {'Approved':<10} {'Slug'}")
        print("-" * 65)
        for item in queue:
            slug = item.get("slug", "")
            is_pub = slug in published_slugs
            is_app = item.get("approved_for_publishing") is True
            status = "PUBLISHED" if is_pub else ("READY_TO_PUB" if is_app else "PENDING_REVIEW")
            print(f"{status:<16} {str(is_app):<10} {slug}")

    elif args.command == "approve":
        success, msg = mgr.approve_candidate(args.slug, args.by)
        print(f"Result: {msg}")

    elif args.command == "research":
        rec = create_research_record(
            slug=args.slug,
            primary_tool=args.tool,
            tool_name=args.name,
            pkr_price=args.price,
            primary_kw=f"{args.name} Pakistan",
            secondary_kws=[
                f"{args.name} price in Pakistan",
                f"buy {args.name} EasyPaisa",
                f"{args.name} subscription PKR",
            ],
            doc_url=f"https://{args.tool}.com",
            features=["Feature 1", "Feature 2"],
        )
        print("\n=== ARTICLE RESEARCH RECORD ===")
        print(json.dumps(rec.to_dict(), indent=2))

    elif args.command == "audit" or not args.command:
        queue = mgr.load_queue()
        published_slugs = {p.parent.name for p in Path("guides").glob("*/index.html")}
        app_count = sum(1 for i in queue if i.get("approved_for_publishing") is True and i.get("slug") not in published_slugs)
        unapp_count = sum(1 for i in queue if i.get("approved_for_publishing") is not True)
        pub_count = sum(1 for i in queue if i.get("slug") in published_slugs)

        print("\n=== HERMES EDITORIAL INTELLIGENCE AUDIT ===")
        print(f"Total Queue Topics:       {len(queue)}")
        print(f"Already Published:        {pub_count}")
        print(f"Approved Pending Publish: {app_count}")
        print(f"Pending Editorial Review: {unapp_count}")
        print(f"Self-Approval Policy:     ENFORCED (Autonomous self-approval blocked)")


if __name__ == "__main__":
    main()

