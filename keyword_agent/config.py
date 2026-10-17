"""
config.py - Configuration and environment setup for keyword_agent.
Operates 100% locally with free-only runtime and no external paid APIs.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any


PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PACKAGE_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
GSC_EXPORTS_DIR = DATA_DIR / "gsc_exports"
GSC_HISTORY_DIR = DATA_DIR / "gsc_history"
REPORTS_DIR = PROJECT_DIR / "reports" / "keyword-agent"
DOCS_DIR = PROJECT_DIR / "docs"


def load_env_file(env_path: Path | None = None) -> Dict[str, str]:
    """Dependency-free .env loader."""
    path = env_path or (PROJECT_DIR / ".env")
    loaded: Dict[str, str] = {}
    if not path.exists():
        return loaded
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, val)
            loaded[key] = val
    return loaded


@dataclass(frozen=True)
class AgentSettings:
    project_dir: Path
    site_url: str = "https://aitoolgems.tech"
    market: str = "PK"
    currency: str = "PKR"
    free_tier_only: bool = True
    gsc_client_id: str = ""
    gsc_client_secret: str = ""
    gsc_refresh_token: str = ""
    site_domain: str = "sc-domain:aitoolgems.tech"
    exports_dir: Path = GSC_EXPORTS_DIR
    history_dir: Path = GSC_HISTORY_DIR
    reports_dir: Path = REPORTS_DIR

    @property
    def has_api_credentials(self) -> bool:
        return bool(self.gsc_client_id and self.gsc_client_secret)


def get_agent_settings() -> AgentSettings:
    """Loads settings safely from environment and defaults."""
    load_env_file()
    
    # Ensure all working directories exist
    for d in [GSC_EXPORTS_DIR, GSC_HISTORY_DIR, REPORTS_DIR, DOCS_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    return AgentSettings(
        project_dir=PROJECT_DIR,
        site_url=os.getenv("ATG_SITE_URL", "https://aitoolgems.tech").rstrip("/"),
        market="PK",
        currency="PKR",
        free_tier_only=True,
        gsc_client_id=os.getenv("GSC_CLIENT_ID", "").strip(),
        gsc_client_secret=os.getenv("GSC_CLIENT_SECRET", "").strip(),
        gsc_refresh_token=os.getenv("GSC_REFRESH_TOKEN", "").strip(),
        site_domain=os.getenv("GSC_SITE_DOMAIN", "sc-domain:aitoolgems.tech"),
        exports_dir=GSC_EXPORTS_DIR,
        history_dir=GSC_HISTORY_DIR,
        reports_dir=REPORTS_DIR,
    )
