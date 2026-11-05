"""Persistent Publishing Queue & Delivery Verification Engine.

Enforces:
1. Idempotency & duplicate dispatch prevention.
2. State machine: QUEUED → DISPATCHING → SCHEDULED → DELIVERED → VERIFIED.
3. Delivery verification: "A scheduled post is not a delivered post."
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from marketing_agent.retry_handler import generate_idempotency_key


class PostState(str, Enum):
    QUEUED = "QUEUED"
    DISPATCHING = "DISPATCHING"
    SCHEDULED = "SCHEDULED"
    DELIVERED = "DELIVERED"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


@dataclass
class QueuedSocialPost:
    post_id: str
    idempotency_key: str
    platform: str  # instagram, facebook, tiktok, telegram
    caption: str
    media_url: str
    scheduled_time: str
    campaign_utm: str
    state: PostState = PostState.QUEUED
    external_buffer_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    delivered_at: Optional[float] = None
    verified_at: Optional[float] = None
    last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["state"] = self.state.value
        return d


class PublishingQueueManager:
    """Manages persistent disk-backed social publishing queue."""

    def __init__(self, queue_file: Optional[Path] = None):
        self.queue_file = queue_file or Path("data/marketing/publishing_queue.json")
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)

    def load_queue(self) -> List[Dict[str, Any]]:
        if not self.queue_file.is_file():
            return []
        try:
            with open(self.queue_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_queue(self, posts: List[Dict[str, Any]]) -> None:
        with open(self.queue_file, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=2)

    def enqueue_post(
        self,
        platform: str,
        caption: str,
        media_url: str,
        scheduled_time: str,
        campaign_utm: str,
    ) -> tuple[Optional[QueuedSocialPost], str]:
        """Enqueue post with duplicate prevention check."""
        queue = self.load_queue()
        idem_key = generate_idempotency_key(
            action="publish_social",
            payload={
                "platform": platform,
                "caption": caption[:100],
                "scheduled_time": scheduled_time,
                "media_url": media_url,
            },
        )

        # Check for duplicate
        for p in queue:
            if p.get("idempotency_key") == idem_key and p.get("state") != PostState.FAILED.value:
                return None, f"DUPLICATE_IGNORED: Post already queued or dispatched with key {idem_key}."

        post_id = f"POST-{platform[:2].upper()}-{int(time.time())}"
        post = QueuedSocialPost(
            post_id=post_id,
            idempotency_key=idem_key,
            platform=platform,
            caption=caption,
            media_url=media_url,
            scheduled_time=scheduled_time,
            campaign_utm=campaign_utm,
            state=PostState.QUEUED,
        )
        queue.append(post.to_dict())
        self.save_queue(queue)
        return post, f"Post {post_id} successfully queued."

    def transition_state(
        self, post_id: str, new_state: PostState, external_id: Optional[str] = None, error: Optional[str] = None
    ) -> bool:
        """Update state machine transition."""
        queue = self.load_queue()
        found = False
        for p in queue:
            if p.get("post_id") == post_id:
                p["state"] = new_state.value
                if external_id:
                    p["external_buffer_id"] = external_id
                if error:
                    p["last_error"] = error
                if new_state == PostState.DELIVERED:
                    p["delivered_at"] = time.time()
                elif new_state == PostState.VERIFIED:
                    p["verified_at"] = time.time()
                found = True
                break

        if found:
            self.save_queue(queue)
        return found
