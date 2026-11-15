"""AI Tool Gems Autonomous Backlink Agent Package.

Provides:
- SSRF-safe URL resolution and HTTPS enforcement (security.py)
- Precise HTML anchor parsing and rel classification (verifier.py)
- Type-safe schema validation and non-destructive tracking (tracker.py)
- Owner-only Telegram approval workflow (approval.py)
- Grounded commercial truth facts loader (facts.py)
- Executive pipeline reporting (reports.py)
"""

from .facts import VerifiedFacts, get_verified_facts
from .models import ApprovalAction, Prospect, VerificationResult
from .security import SSRFSecurityError, is_ip_prohibited, normalize_target_url, validate_and_sanitize_url
from .tracker import load_tracker_rows, summarize_tracker, validate_tracker_data
from .verifier import BacklinkHTMLParser, parse_and_verify_html, verify_prospect_url

__version__ = "2.0.0"
