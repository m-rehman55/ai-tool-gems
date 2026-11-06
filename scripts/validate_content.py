#!/usr/bin/env python3
"""
AIToolGems Autonomous Pre-Publish Content & Technical Validator
--------------------------------------------------------------
Enforces strict quality, SEO, technical, and anti-cannibalization gates
before any article or update is published to main.
"""

import sys
import json
import re
from pathlib import Path
from html.parser import HTMLParser

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(__file__).resolve().parent.parent

class ArticleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta_desc = ""
        self.canonical = ""
        self.h1_list = []
        self.h2_list = []
        self.links = []
        self.images = []
        self.schemas = []
        self._in_title = False
        self._in_h1 = False
        self._in_h2 = False
        self._in_schema = False
        self._schema_buf = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta" and d.get("name", "").lower() == "description":
            self.meta_desc = d.get("content", "").strip()
        elif tag == "link" and d.get("rel", "").lower() == "canonical":
            self.canonical = d.get("href", "").strip()
        elif tag == "h1":
            self._in_h1 = True
        elif tag == "h2":
            self._in_h2 = True
        elif tag == "a" and "href" in d:
            self.links.append(d["href"])
        elif tag == "img":
            self.images.append(d)
        elif tag == "script" and d.get("type", "").lower() == "application/ld+json":
            self._in_schema = True
            self._schema_buf = []

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "h1":
            self._in_h1 = False
        elif tag == "h2":
            self._in_h2 = False
        elif tag == "script" and self._in_schema:
            self.schemas.append("".join(self._schema_buf))
            self._in_schema = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif self._in_h1:
            self.h1_list.append(data.strip())
        elif self._in_h2:
            self.h2_list.append(data.strip())
        elif self._in_schema:
            self._schema_buf.append(data)


def validate_article_file(file_path: Path, expected_slug: str = None) -> tuple[bool, list[str]]:
    errors = []
    warnings = []

    if not file_path.exists():
        return False, [f"File does not exist: {file_path}"]

    html = file_path.read_text(encoding="utf-8")
    
    # 1. Basic Content Integrity
    if len(html.strip()) < 500:
        errors.append("Article content is suspiciously short or empty (<500 chars)")

    if "## " in html:
        errors.append("Raw markdown header syntax (##) leaked into HTML body")
    if "TODO" in html or "PLACEHOLDER" in html or "lorem ipsum" in html.lower():
        errors.append("Placeholder or unfinished template text found")

    # 2. HTML Parsing & Tags
    parser = ArticleParser()
    parser.feed(html)

    # Title check (standard SEO max length 70 characters)
    title = parser.title.strip()
    if not (20 <= len(title) <= 70):
        errors.append(f"Title length ({len(title)} chars) outside 20–70 bounds: '{title}'")

    # Meta description check
    meta = parser.meta_desc
    if not (70 <= len(meta) <= 170):
        errors.append(f"Meta description length ({len(meta)} chars) outside 70–170 bounds: '{meta}'")

    # H1 check
    if len(parser.h1_list) != 1:
        errors.append(f"Article must contain exactly 1 H1; found {len(parser.h1_list)}")

    # Canonical check
    slug = expected_slug or file_path.parent.name
    expected_canonical = f"https://aitoolgems.tech/guides/{slug}/"
    if parser.canonical != expected_canonical:
        errors.append(f"Canonical mismatch: expected '{expected_canonical}', found '{parser.canonical}'")

    # 3. Word Count & Keyword Density
    plain = re.sub(r"<[^>]+>", " ", html).lower()
    words = re.findall(r"\b[a-z0-9_-]+\b", plain)
    total_words = len(words)
    if total_words < 1200:
        errors.append(f"Word count ({total_words}) below 1,200 word in-depth standard")

    # 4. Anti-Stuffing & Excessive Repetition
    freq = {}
    for w in words:
        if len(w) > 4:
            freq[w] = freq.get(w, 0) + 1

    # Check non-topic substantive terms
    topic_tokens = set(re.findall(r"[a-z0-9]+", slug.lower()))
    ignored_entities = {
        "pakistan", "subscription", "delivery", "payment", "easypaisa", "jazzcash",
        "developer", "developers", "pricing", "claude", "sonnet", "cursor", "leonardo",
        "canva", "figma", "capcut", "anthropic", "openai", "google", "replit", "lovable",
        "features", "access", "account", "accounts", "service", "support", "tools",
        "guide", "guides", "verified", "pakistani", "workflow", "workflows"
    } | topic_tokens
    for w, count in freq.items():
        if w not in ignored_entities and count > 28:
            errors.append(f"Suspicious word repetition: '{w}' repeated {count} times (max 28)")

    # 5. Schema Validation
    if not parser.schemas:
        errors.append("Missing JSON-LD structured data")
    else:
        found_types = set()
        for raw in parser.schemas:
            try:
                data = json.loads(raw)
                if "@graph" in data:
                    for item in data["@graph"]:
                        found_types.add(item.get("@type"))
                else:
                    found_types.add(data.get("@type"))
            except Exception as e:
                errors.append(f"Malformed JSON-LD schema: {e}")

        for req in ["Article", "BreadcrumbList", "FAQPage"]:
            if req not in str(found_types):
                errors.append(f"Missing required structured data type: {req}")

    # 6. Internal Link Verification
    for link in parser.links:
        if link.startswith("http://") or link.startswith("https://") or link.startswith("//"):
            continue  # external
        # Strip query and anchor
        clean_link = link.split("#")[0].split("?")[0]
        if not clean_link:
            continue  # anchor only, e.g. #faq
        target = (file_path.parent / clean_link).resolve()
        if not target.exists() and not (target / "index.html").exists():
            errors.append(f"Broken internal link destination: '{link}' from {file_path}")

    # 7. Images alt text
    for img in parser.images:
        if "alt" not in img or not img["alt"].strip():
            errors.append(f"Image tag missing alt text: {img}")

    # 8. Local Pakistan signals & foreign currency exclusion
    if "pakistan" not in plain and "pakistani" not in plain:
        errors.append("Missing Pakistani market localization signal ('Pakistan'/'Pakistani')")

    has_commercial_intent = any(term in plain for term in ["price", "pricing", "buy", "order", "cost", "subscription", "rates", "fee"])
    if has_commercial_intent and ("pkr" not in plain and "rs." not in plain):
        errors.append("Commercial topic missing Pakistani currency (PKR/Rs.) pricing signal")

    has_payment_discussion = any(term in plain for term in ["payment", "pay", "checkout", "mobile wallet"])
    if has_payment_discussion and ("easypaisa" not in plain and "jazzcash" not in plain and "sadapay" not in plain and "bank transfer" not in plain):
        errors.append("Payment-related topic missing verified Pakistani payment route (EasyPaisa/JazzCash/SadaPay/Bank)")

    if any(tok in plain for tok in ["japan", "japanese", "tokyo", "osaka", "kyoto", "jpy", "/jp/"]) or "¥" in html:
        errors.append("Detected foreign currency/Japan contamination in Pakistani content")

    # 9. AI Cliché & Filler Filter (Phase 13 Quality Standard)
    forbidden_cliches = [
        "in today's fast-paced digital landscape",
        "in today's fast-paced world",
        "delve into the world of",
        "it is important to remember that",
        "testament to the power of",
        "game changer in the realm of",
        "revolutionizing the way we",
        "rich tapestry of",
        "beacon of innovation",
    ]
    for c in forbidden_cliches:
        if c in plain:
            errors.append(f"AI_FILLER_DETECTED: Generic AI cliché found: '{c}'. Must be rewritten with substantive analysis.")

    # 10. Visible Review / Verification Date Gate
    has_date = bool(re.search(r"(updated|verified|review\s*date|last\s*reviewed|published)\s*[:•\-&;a-z\s]*(\d{1,2}\s+[A-Za-z]+\s+202[4-6]|[A-Za-z]+\s+\d{1,2},\s*202[4-6]|202[4-6][-\d]*)", html, re.I))
    if not has_date:
        errors.append("MISSING_REVIEW_DATE: Article missing visible review or verification date (e.g., 'Last reviewed & updated: 2026-XX-XX')")

    # 11. Sources & Documentation Citations Gate
    has_sources = bool(re.search(r"(official\s+sources|references|documentation|official\s+provider|data\s+sources|https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", html, re.I))
    if not has_sources:
        errors.append("MISSING_SOURCES: Article missing visible official documentation sources or outbound citations")

    # 12. Canonical Product or Category Link Gate
    has_canonical_link = any(
        re.search(r"(\.\./\.\./tools/[a-z0-9-]+/|/tools/[a-z0-9-]+/|\.\./\.\./#products|\.\./\.\./#categories|/categories/[a-z0-9-]+/)", l)
        for l in parser.links
    )
    if not has_canonical_link:
        errors.append("MISSING_CANONICAL_LINK: Article must contain contextual link to canonical product (/tools/) or category hub")

    is_valid = len(errors) == 0
    return is_valid, errors


def check_cannibalization(new_slug: str, new_keyword: str) -> tuple[bool, str]:
    """Check against data/seo/keyword-map.json and existing guides to avoid cannibalization
    and ensure existing URLs are improved instead of creating duplicate thin URLs.
    """
    map_file = BASE / "data" / "seo" / "keyword-map.json"
    guides_dir = BASE / "guides"

    # 1. Check existing guides directory to prevent thin duplicate URLs
    if guides_dir.exists():
        existing_guide_slugs = {p.parent.name for p in guides_dir.glob("*/index.html")}
        if new_slug in existing_guide_slugs:
            return False, f"Guide slug '{new_slug}' is already published. Check whether existing URL should be improved instead of creating a new one."

        # Detect near-identical tool guide variations (e.g. {tool}-ai-pakistan-guide when {tool} exists)
        norm_new_base = re.sub(r"-(ai|pro|guide|pakistan)+", "", new_slug).strip("-")
        for exist_slug in existing_guide_slugs:
            norm_exist_base = re.sub(r"-(ai|pro|guide|pakistan)+", "", exist_slug).strip("-")
            if norm_new_base and norm_new_base == norm_exist_base and norm_new_base not in ["ai", "best", "unit"]:
                return False, f"Search intent for '{norm_new_base}' is already served by '/guides/{exist_slug}/'. Improve existing URL rather than creating duplicate '{new_slug}'."

    # 2. Check keyword map
    if map_file.exists():
        kw_data = json.loads(map_file.read_text(encoding="utf-8"))
        norm_new = re.sub(r"[^a-z0-9]", "", new_keyword.lower())

        for entry in kw_data:
            if entry["slug"] == new_slug:
                continue
            existing_kw = entry.get("primary_keyword", "")
            norm_exist = re.sub(r"[^a-z0-9]", "", existing_kw.lower())

            if norm_new == norm_exist:
                return False, f"Exact primary keyword collision with existing entry '{entry['slug']}': '{existing_kw}'. Improve existing URL '/guides/{entry['slug']}/'."

            # Check secondary keywords
            for sec in entry.get("secondary_keywords", []):
                if norm_new == re.sub(r"[^a-z0-9]", "", sec.lower()):
                    return False, f"Keyword conflicts with secondary target in '{entry['slug']}': '{sec}'. Improve existing URL."

    return True, "Passed anti-cannibalization check"


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_content.py <path-to-article-html> [expected-slug]")
        sys.exit(1)

    file_to_check = Path(sys.argv[1]).resolve()
    expected_slug = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"🔍 Validating content file: {file_to_check}")
    ok, issues = validate_article_file(file_to_check, expected_slug)

    if ok:
        print("✅ All pre-publish content, SEO, link, and integrity checks PASSED.")
        sys.exit(0)
    else:
        print(f"❌ Validation FAILED with {len(issues)} issue(s):")
        for iss in issues:
            print(f"  • {iss}")
        sys.exit(1)


if __name__ == "__main__":
    main()
