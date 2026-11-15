"""Operational configuration and safety feature flags for HERMES Backlink Agent.

All external submission and outreach capabilities fail closed by default.
"""

from __future__ import annotations

# ==============================================================================
# ABSOLUTE SAFETY FEATURE FLAGS (FAIL CLOSED)
# ==============================================================================
ALLOW_EXTERNAL_SUBMISSIONS = False      # Zero automated form submissions or email outreach
ALLOW_LIVE_TELEGRAM_DISPATCH = False    # Controlled outbox delivery; dry-run simulated by default
ALLOW_READONLY_CRAWL = True             # Permitted read-only HTTPS GET requests with SSRF pinning

# Maximum limits
MAX_NETWORK_TRANSFER_BYTES = 2 * 1024 * 1024        # 2 MB stream cap
MAX_DECOMPRESSED_EXPANSION_BYTES = 4 * 1024 * 1024  # 4 MB expansion cap
SOCKET_TIMEOUT_SECONDS = 12.0
MAX_REDIRECT_HOPS = 5


def is_external_submission_allowed() -> bool:
    """Returns True only if external submissions are explicitly authorized."""
    return ALLOW_EXTERNAL_SUBMISSIONS


def assert_external_submissions_disabled() -> None:
    """Throws RuntimeError if any automated external submission action is attempted."""
    if is_external_submission_allowed():
        raise RuntimeError(
            "CRITICAL VIOLATION: Automated external submissions are enabled! "
            "HERMES operating policy mandates owner-operated manual submissions only."
        )
