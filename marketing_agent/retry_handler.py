"""Durable, Rate-Limit-Aware HTTP Request and Retry Engine.

Implements:
1. Full Exponential Backoff with Random Jitter.
2. Parsing and compliance with HTTP 'Retry-After' headers (seconds & dates).
3. Idempotency key tracking to prevent accidental duplicate social dispatches.
4. Safe retry on transient 429 (Too Many Requests), 500, 502, 503, 504 errors.
"""

from __future__ import annotations

import email.utils
import hashlib
import json
import logging
import random
import time
from typing import Any, Callable, Dict, Optional, Tuple
from urllib.error import HTTPError, URLError

logger = logging.getLogger("marketing_agent.retry_handler")


def parse_retry_after(header_value: Optional[str]) -> Optional[float]:
    """Parse HTTP 'Retry-After' header (either integer seconds or HTTP-date)."""
    if not header_value:
        return None
    header_clean = header_value.strip()

    # Try integer seconds
    try:
        return max(0.0, float(header_clean))
    except ValueError:
        pass

    # Try HTTP date (RFC 2822 / RFC 7231)
    try:
        dt = email.utils.parsedate_to_datetime(header_clean)
        diff = (dt.timestamp() - time.time())
        return max(0.0, diff)
    except Exception:
        return None


def generate_idempotency_key(action: str, payload: Dict[str, Any]) -> str:
    """Generate SHA-256 idempotency key to prevent duplicate post dispatches."""
    raw = f"{action}:{json.dumps(payload, sort_keys=True)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def execute_with_durable_retry(
    action_name: str,
    func: Callable[[], Any],
    max_attempts: int = 5,
    initial_backoff: float = 2.0,
    max_backoff: float = 60.0,
) -> Any:
    """Execute callable with exponential backoff, jitter, and Retry-After awareness."""
    attempt = 0
    last_error: Optional[Exception] = None

    while attempt < max_attempts:
        attempt += 1
        try:
            return func()
        except HTTPError as exc:
            last_error = exc
            status_code = exc.code

            # Non-retryable client errors (400, 401, 403, 404, 422) - Fail fast
            if status_code not in (429, 500, 502, 503, 504):
                detail = exc.read().decode("utf-8", errors="replace") if hasattr(exc, "read") else ""
                raise RuntimeError(f"HTTP {status_code} on {action_name}: {detail[:250]}") from exc

            # Check for Retry-After header
            retry_after = parse_retry_after(exc.headers.get("Retry-After")) if exc.headers else None
            if retry_after is not None:
                delay = min(max_backoff, max(1.0, retry_after))
                logger.warning(
                    f"[RateLimit] {action_name} received HTTP {status_code}. Server Retry-After: {delay:.1f}s (Attempt {attempt}/{max_attempts})."
                )
            else:
                # Exponential backoff with jitter
                exp_delay = min(max_backoff, initial_backoff * (2 ** (attempt - 1)))
                jitter = random.uniform(0.75, 1.25)
                delay = exp_delay * jitter
                logger.warning(
                    f"[TransientError] {action_name} received HTTP {status_code}. Backing off {delay:.1f}s with jitter (Attempt {attempt}/{max_attempts})."
                )

            if attempt < max_attempts:
                time.sleep(delay)
            else:
                raise RuntimeError(f"Exhausted {max_attempts} attempts on {action_name} due to HTTP {status_code}.") from exc

        except (URLError, TimeoutError, ConnectionError) as exc:
            last_error = exc
            exp_delay = min(max_backoff, initial_backoff * (2 ** (attempt - 1)))
            delay = exp_delay * random.uniform(0.8, 1.2)
            logger.warning(
                f"[NetworkError] {action_name} network timeout: {exc}. Retrying in {delay:.1f}s (Attempt {attempt}/{max_attempts})."
            )
            if attempt < max_attempts:
                time.sleep(delay)
            else:
                raise RuntimeError(f"Exhausted {max_attempts} attempts on {action_name} due to network failure.") from exc

    raise RuntimeError(f"Execution failed for {action_name}: {last_error}")

