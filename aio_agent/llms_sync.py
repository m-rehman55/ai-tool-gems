"""
llms_sync.py - Autonomous Knowledge Base Synchronization for LLM Crawlers.
Maintains standard llms.txt and llms-full.txt files to ensure large language models
(Perplexity, ChatGPT Search, Claude, Google Gemini) can ingest the site's complete
product catalog and verified pricing directory in 1 HTTP request.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


@dataclass
class SyncResult:
    tools_synced: int
    guides_synced: int
    llms_txt_updated: bool
    llms_full_txt_updated: bool
    message: str


class LLMsSyncEngine:
    """Synchronizes llms.txt and llms-full.txt with real routes from the repository."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.llms_txt_path = project_dir / "llms.txt"
        self.llms_full_txt_path = project_dir / "llms-full.txt"

    def discover_live_guides(self) -> List[Tuple[str, str, str]]:
        """Scans guides/ for canonical index.html files and extracts title/description."""
        guides_dir = self.project_dir / "guides"
        live_guides: List[Tuple[str, str, str]] = []
        if not guides_dir.exists():
            return live_guides

        for item in sorted(guides_dir.iterdir()):
            if item.is_dir() and (item / "index.html").exists():
                idx = item / "index.html"
                content = idx.read_text(encoding="utf-8")
                slug = item.name
                url = f"https://aitoolgems.tech/guides/{slug}/"

                title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
                title = title_match.group(1).strip() if title_match else slug.replace("-", " ").title()
                # Clean title suffixes
                title = re.sub(r"\s*\|\s*AI Tool Gems.*", "", title).strip()

                desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE)
                desc = desc_match.group(1).strip() if desc_match else f"Comprehensive guide to {slug.replace('-', ' ')} in Pakistan"

                live_guides.append((title, url, desc))

        return live_guides

    def discover_live_tools(self) -> List[Tuple[str, str, str]]:
        """Scans tools/ for canonical tool listings."""
        tools_dir = self.project_dir / "tools"
        live_tools: List[Tuple[str, str, str]] = []
        if not tools_dir.exists():
            return live_tools

        for item in sorted(tools_dir.iterdir()):
            if item.is_dir() and (item / "index.html").exists():
                idx = item / "index.html"
                content = idx.read_text(encoding="utf-8")
                slug = item.name
                url = f"https://aitoolgems.tech/tools/{slug}/"

                title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
                title = title_match.group(1).strip() if title_match else slug.replace("-", " ").title()
                title = re.sub(r"\s*\|\s*AI Tool Gems.*", "", title).strip()

                desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE)
                desc = desc_match.group(1).strip() if desc_match else f"{slug.title()} subscription in Pakistan"

                live_tools.append((title, url, desc))

        return live_tools

    def sync(self) -> SyncResult:
        """Updates llms.txt and llms-full.txt with all live routes."""
        live_guides = self.discover_live_guides()
        live_tools = self.discover_live_tools()

        # Update llms.txt
        if self.llms_txt_path.exists():
            content = self.llms_txt_path.read_text(encoding="utf-8")
            
            # Ensure newly added guides are present
            new_lines = []
            for title, url, desc in live_guides:
                if url not in content:
                    new_lines.append(f"- [{title}]({url}) — {desc}")

            if new_lines:
                # Insert before "Optional" or at end of Editorial Guides
                insert_str = "\n".join(new_lines) + "\n"
                if "## Optional" in content:
                    content = content.replace("## Optional", f"{insert_str}\n## Optional")
                else:
                    content += f"\n{insert_str}"
                self.llms_txt_path.write_text(content, encoding="utf-8")
                llms_txt_updated = True
            else:
                llms_txt_updated = False
        else:
            llms_txt_updated = False

        # Update llms-full.txt
        if self.llms_full_txt_path.exists():
            full_content = self.llms_full_txt_path.read_text(encoding="utf-8")
            full_new_lines = []
            for title, url, desc in live_guides:
                if url not in full_content:
                    full_new_lines.append(f"### {title}\n- URL: {url}\n- Summary: {desc}\n")

            if full_new_lines:
                full_insert = "\n".join(full_new_lines) + "\n"
                full_content += f"\n## Newly Published Guides\n\n{full_insert}"
                self.llms_full_txt_path.write_text(full_content, encoding="utf-8")
                llms_full_updated = True
            else:
                llms_full_updated = False
        else:
            llms_full_updated = False

        return SyncResult(
            tools_synced=len(live_tools),
            guides_synced=len(live_guides),
            llms_txt_updated=llms_txt_updated,
            llms_full_txt_updated=llms_full_updated,
            message=f"Synced {len(live_tools)} tools and {len(live_guides)} guides to machine knowledge files.",
        )
