"""
Verification and Sitemap Extraction for Ping Agent.
Ensures IndexNow key file validity, parses canonical sitemap URLs, and tracks page changes.
"""

import re
import urllib.request
from pathlib import Path
from typing import List, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
SITEMAP_PATH = BASE_DIR / "sitemap.xml"
KEY_FILE = BASE_DIR / "e1a8c47f9d2b4f30a6c8116de5b97042.txt"
INDEXNOW_KEY = "e1a8c47f9d2b4f30a6c8116de5b97042"
HOST = "aitoolgems.tech"


def get_sitemap_urls() -> List[str]:
    """Extracts all canonical URLs from sitemap.xml."""
    if not SITEMAP_PATH.exists():
        return []
    content = SITEMAP_PATH.read_text(encoding="utf-8")
    return re.findall(r"<loc>(.*?)</loc>", content)


def verify_key_setup(remote_check: bool = False, timeout: int = 8) -> Dict[str, Any]:
    """
    Verifies that the IndexNow key file exists locally and is live on production.
    """
    local_exists = KEY_FILE.exists()
    local_content = KEY_FILE.read_text(encoding="utf-8").strip() if local_exists else ""
    key_match = local_content == INDEXNOW_KEY

    status = {
        "key": INDEXNOW_KEY,
        "local_file_exists": local_exists,
        "local_content_matches": key_match,
        "remote_accessible": None,
        "remote_status_code": None
    }

    if remote_check:
        remote_url = f"https://{HOST}/{INDEXNOW_KEY}.txt"
        try:
            req = urllib.request.Request(remote_url, headers={"User-Agent": "Mozilla/5.0 (PingAgent/1.0)"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8").strip()
                status["remote_accessible"] = (body == INDEXNOW_KEY)
                status["remote_status_code"] = resp.status
        except Exception as e:
            status["remote_accessible"] = False
            status["remote_error"] = str(e)

    return status
