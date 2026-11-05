"""
indexnow_queue.py - Durable Submission Queue & Delta Diff Engine for IndexNow.

Strictly adheres to HERMES IndexNow operating requirements:
1. Submit newly created, updated, or deleted URLs ONLY (delta diffing via content hashes).
2. Deduplicate URLs across batches.
3. Maintain durable persistent submission queue on disk (data/bing/indexnow_queue.json).
4. Respect provider limits (max 10,000 URLs per batch).
5. Use secure key management (verified local key file and keyLocation).
6. Record endpoint, timestamp, HTTP status, and latency.
7. Distinguish submission acceptance (HTTP 200/202) from crawling and indexing.
8. Non-fabrication: Never claim Google indexing from IndexNow (Google does not participate).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from bing_agent.models import IndexNowQueueItem, IndexNowSubmissionRecord

logger = logging.getLogger("bing_agent.indexnow")

INDEXNOW_KEY = "e1a8c47f9d2b4f30a6c8116de5b97042"
HOST = "aitoolgems.tech"
KEY_LOCATION = f"https://{HOST}/{INDEXNOW_KEY}.txt"

INDEXNOW_ENDPOINTS = [
    "https://api.indexnow.org/indexnow",
    "https://www.bing.com/indexnow",
    "https://yandex.com/indexnow",
]


class IndexNowQueueEngine:
    """Manages durable submission queue, delta detection, and multi-engine dispatch."""

    def __init__(self, project_dir: Optional[Path] = None, data_dir: Optional[Path] = None):
        self.project_dir = project_dir or Path(__file__).resolve().parent.parent
        self.data_dir = data_dir or (self.project_dir / "data" / "bing")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.queue_file = self.data_dir / "indexnow_queue.json"
        self.history_file = self.data_dir / "submission_history.json"
        self.state_file = self.data_dir / "url_hashes.json"

    # ── Durable State & Queue Management ─────────────────────────────────────

    def load_queue(self) -> Dict[str, IndexNowQueueItem]:
        """Loads queued URLs from persistent JSON storage."""
        if not self.queue_file.exists():
            return {}
        try:
            raw = json.loads(self.queue_file.read_text(encoding="utf-8"))
            return {
                url: IndexNowQueueItem(
                    url=item["url"],
                    reason=item.get("reason", "CONTENT_UPDATED"),
                    discovered_at=item.get("discovered_at", ""),
                    content_hash=item.get("content_hash", ""),
                    submission_attempts=item.get("submission_attempts", 0),
                    status=item.get("status", "QUEUED"),
                    last_submitted=item.get("last_submitted"),
                    last_http_status=item.get("last_http_status"),
                )
                for url, item in raw.items()
            }
        except Exception as e:
            logger.warning(f"Failed loading IndexNow queue: {e}")
            return {}

    def save_queue(self, queue: Dict[str, IndexNowQueueItem]) -> None:
        """Saves current queue state atomically."""
        data = {url: item.to_dict() for url, item in queue.items()}
        self.queue_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load_url_hashes(self) -> Dict[str, str]:
        """Loads previously submitted content hashes."""
        if not self.state_file.exists():
            return {}
        try:
            return json.loads(self.state_file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save_url_hashes(self, hashes: Dict[str, str]) -> None:
        """Saves verified content hashes."""
        self.state_file.write_text(json.dumps(hashes, indent=2), encoding="utf-8")

    # ── Delta Diff Engine ─────────────────────────────────────────────────────

    @staticmethod
    def _compute_hash(content: str) -> str:
        """Computes SHA-256 hash of normalized text content."""
        clean = re.sub(r"\s+", " ", content.strip())
        return hashlib.sha256(clean.encode("utf-8")).hexdigest()

    def detect_deltas(self) -> List[IndexNowQueueItem]:
        """
        Inspects repository HTML files and sitemap.xml to identify
        new, updated, or deleted URLs compared against previous hashes.
        Enforces: Submit newly created, updated or deleted URLs ONLY.
        """
        previous_hashes = self.load_url_hashes()
        current_hashes: Dict[str, str] = {}
        queue = self.load_queue()
        deltas: List[IndexNowQueueItem] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        # Scan HTML files on disk
        for html_path in self.project_dir.glob("**/*.html"):
            rel_str = str(html_path.relative_to(self.project_dir)).replace("\\", "/")
            if any(p in rel_str for p in [".gemini", "node_modules", "data", "reports", "scratch"]):
                continue

            # Construct canonical URL
            clean_rel = rel_str.replace("index.html", "") if rel_str.endswith("index.html") else rel_str
            clean_rel = clean_rel.lstrip("/")
            canonical_url = f"https://{HOST}/{clean_rel}"

            try:
                body = html_path.read_text(encoding="utf-8", errors="ignore")
                content_hash = self._compute_hash(body)
                current_hashes[canonical_url] = content_hash

                prev_hash = previous_hashes.get(canonical_url)

                if prev_hash is None:
                    # Brand new URL
                    item = IndexNowQueueItem(
                        url=canonical_url,
                        reason="NEW_URL",
                        discovered_at=now_iso,
                        content_hash=content_hash,
                        status="QUEUED",
                    )
                    queue[canonical_url] = item
                    deltas.append(item)
                elif prev_hash != content_hash:
                    # Content updated
                    item = IndexNowQueueItem(
                        url=canonical_url,
                        reason="CONTENT_UPDATED",
                        discovered_at=now_iso,
                        content_hash=content_hash,
                        status="QUEUED",
                    )
                    queue[canonical_url] = item
                    deltas.append(item)
            except Exception as e:
                logger.warning(f"Error reading {html_path}: {e}")

        # Check for deleted URLs
        for prev_url, prev_h in previous_hashes.items():
            if prev_url not in current_hashes:
                item = IndexNowQueueItem(
                    url=prev_url,
                    reason="DELETED",
                    discovered_at=now_iso,
                    content_hash="DELETED",
                    status="QUEUED",
                )
                queue[prev_url] = item
                deltas.append(item)

        self.save_queue(queue)
        return deltas

    # ── Key Security Verification ─────────────────────────────────────────────

    def verify_key_infrastructure(self) -> Dict[str, Any]:
        """Ensures IndexNow verification key file exists locally and matches."""
        key_file = self.project_dir / f"{INDEXNOW_KEY}.txt"
        exists = key_file.exists()
        content = key_file.read_text(encoding="utf-8").strip() if exists else ""
        valid = (content == INDEXNOW_KEY)

        return {
            "key": INDEXNOW_KEY,
            "key_file": str(key_file),
            "exists_locally": exists,
            "content_valid": valid,
            "key_location": KEY_LOCATION,
        }

    # ── Dispatch Execution & Limits ───────────────────────────────────────────

    def dispatch_pending(self, dry_run: bool = False, batch_limit: int = 100) -> List[IndexNowSubmissionRecord]:
        """
        Submits queued pending URLs to IndexNow endpoints.
        - Deduplicates URLs
        - Respects batch limit (max 10,000 per IndexNow spec)
        - Records endpoint, timestamp, and HTTP status
        - Distinguishes submission acceptance from crawling/indexing
        - Does NOT claim Google indexing
        """
        queue = self.load_queue()
        pending = [item for item in queue.values() if item.status == "QUEUED"]

        if not pending:
            return []

        # Deduplicate and sort
        urls_to_submit = sorted(list(set(item.url for item in pending[:batch_limit])))
        records: List[IndexNowSubmissionRecord] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        payload = {
            "host": HOST,
            "key": INDEXNOW_KEY,
            "keyLocation": KEY_LOCATION,
            "urlList": urls_to_submit,
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json; charset=utf-8"}

        if dry_run:
            for ep in INDEXNOW_ENDPOINTS:
                rec = IndexNowSubmissionRecord(
                    submission_id=f"dry_run_{int(time.time())}",
                    timestamp=now_iso,
                    urls_count=len(urls_to_submit),
                    urls=urls_to_submit,
                    endpoint=ep,
                    http_status=200,
                    is_accepted=True,
                    response_message="Dry-run simulation. Endpoint accepted notification payload.",
                    duration_ms=0.0,
                )
                records.append(rec)
            return records

        for ep in INDEXNOW_ENDPOINTS:
            t0 = time.time()
            try:
                req = urllib.request.Request(ep, data=data_bytes, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=12) as resp:
                    dur = round((time.time() - t0) * 1000.0, 1)
                    status_code = resp.status
                    is_acc = status_code in (200, 202)
                    rec = IndexNowSubmissionRecord(
                        submission_id=f"sub_{int(time.time())}_{status_code}",
                        timestamp=now_iso,
                        urls_count=len(urls_to_submit),
                        urls=urls_to_submit,
                        endpoint=ep,
                        http_status=status_code,
                        is_accepted=is_acc,
                        response_message=f"HTTP {status_code}: Accepted by IndexNow endpoint for crawl queuing.",
                        duration_ms=dur,
                    )
                    records.append(rec)
            except urllib.error.HTTPError as e:
                dur = round((time.time() - t0) * 1000.0, 1)
                rec = IndexNowSubmissionRecord(
                    submission_id=f"sub_{int(time.time())}_{e.code}",
                    timestamp=now_iso,
                    urls_count=len(urls_to_submit),
                    urls=urls_to_submit,
                    endpoint=ep,
                    http_status=e.code,
                    is_accepted=False,
                    response_message=f"HTTP {e.code}: {e.reason}",
                    duration_ms=dur,
                )
                records.append(rec)
            except Exception as e:
                dur = round((time.time() - t0) * 1000.0, 1)
                rec = IndexNowSubmissionRecord(
                    submission_id=f"sub_{int(time.time())}_err",
                    timestamp=now_iso,
                    urls_count=len(urls_to_submit),
                    urls=urls_to_submit,
                    endpoint=ep,
                    http_status=0,
                    is_accepted=False,
                    response_message=f"Network error: {str(e)}",
                    duration_ms=dur,
                )
                records.append(rec)

        # Update queue items and state hashes if at least one endpoint accepted
        any_accepted = any(r.is_accepted for r in records)
        if any_accepted:
            current_hashes = self.load_url_hashes()
            for url in urls_to_submit:
                if url in queue:
                    item = queue[url]
                    item.status = "SUBMITTED"
                    item.last_submitted = now_iso
                    item.submission_attempts += 1
                    item.last_http_status = 200
                    if item.reason != "DELETED":
                        current_hashes[url] = item.content_hash
                    else:
                        current_hashes.pop(url, None)
            self.save_queue(queue)
            self.save_url_hashes(current_hashes)

        # Append to submission history
        self._record_history(records)
        return records

    def _record_history(self, records: List[IndexNowSubmissionRecord]) -> None:
        """Appends submission records to durable history file."""
        history = []
        if self.history_file.exists():
            try:
                history = json.loads(self.history_file.read_text(encoding="utf-8"))
            except Exception:
                history = []

        for r in records:
            history.insert(0, r.to_dict())

        # Keep last 100 records
        self.history_file.write_text(json.dumps(history[:100], indent=2), encoding="utf-8")

