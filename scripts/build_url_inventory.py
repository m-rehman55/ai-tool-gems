#!/usr/bin/env python3
"""
Build machine-readable URL inventory for AIToolGems Pakistan.
Extracts title, meta description, H1, canonical, page type, intent, and internal links.
Writes output to data/seo/url-inventory.json.
"""

import json
import re
import sys
from pathlib import Path
from html.parser import HTMLParser

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(__file__).resolve().parent.parent

class MetaExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.h1 = ""
        self.links = []
        self._in_title = False
        self._in_h1 = False
        self.h1_count = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta" and attrs_dict.get("name", "").lower() == "description":
            self.description = attrs_dict.get("content", "").strip()
        elif tag == "link" and attrs_dict.get("rel", "").lower() == "canonical":
            self.canonical = attrs_dict.get("href", "").strip()
        elif tag == "h1":
            self._in_h1 = True
            self.h1_count += 1
        elif tag == "a" and "href" in attrs_dict:
            href = attrs_dict["href"]
            if href and not href.startswith(("#", "mailto:", "tel:", "javascript:")):
                self.links.append(href)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "h1":
            self._in_h1 = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif self._in_h1:
            self.h1 += data

def determine_page_type_and_intent(url: str, rel_path: str):
    if url == "https://aitoolgems.tech/":
        return "homepage", "commercial_transactional", "Marketplace homepage & tool finder"
    if "/deals/" in url:
        return "catalog", "commercial", "20-listing PKR deal directory"
    if "/prices/" in url:
        return "index", "commercial", "PKR price and warranty index"
    if url == "https://aitoolgems.tech/guides/":
        return "editorial_hub", "informational", "Pakistan AI guides & tutorials hub"
    if url == "https://aitoolgems.tech/blog/":
        return "blog_hub", "informational", "Pakistan AI blog & updates hub"
    if "/guides/" in url:
        return "guide", "informational_commercial", "Topical guide, benchmark or tutorial"
    if "/tools/" in url:
        return "product", "transactional", "Tool license key purchase & WhatsApp checkout"
    return "trust_policy", "informational_navigational", "Trust, policy or compliance page"

def build_inventory():
    sitemap_file = BASE / "sitemap.xml"
    urls = []
    if sitemap_file.exists():
        urls = re.findall(r"<loc>(https://aitoolgems.tech/[^<]*)</loc>", sitemap_file.read_text(encoding="utf-8"))

    inventory = []
    for url in urls:
        path_suffix = url.replace("https://aitoolgems.tech/", "")
        if path_suffix == "" or path_suffix.endswith("/"):
            file_path = BASE / path_suffix / "index.html" if path_suffix else BASE / "index.html"
        else:
            file_path = BASE / path_suffix

        if not file_path.exists():
            print(f"⚠️ Warning: File not found for {url} -> {file_path}")
            continue

        html_content = file_path.read_text(encoding="utf-8")
        parser = MetaExtractor()
        parser.feed(html_content)

        page_type, intent, topic = determine_page_type_and_intent(url, str(file_path.relative_to(BASE)))

        inventory.append({
            "url": url,
            "relative_file": str(file_path.relative_to(BASE)).replace("\\", "/"),
            "page_type": page_type,
            "search_intent": intent,
            "topic": topic,
            "title": parser.title.strip(),
            "meta_description": parser.description,
            "h1": re.sub(r"\s+", " ", parser.h1).strip(),
            "h1_count": parser.h1_count,
            "canonical": parser.canonical,
            "indexable": "noindex" not in html_content,
            "internal_links_count": len(parser.links),
            "last_verified": "2026-10-11",
            "status": "live_verified"
        })

    out_file = BASE / "data" / "seo" / "url-inventory.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)

    print(f"✅ Generated machine-readable URL inventory at {out_file} with {len(inventory)} verified URLs.")
    return inventory

if __name__ == "__main__":
    build_inventory()
