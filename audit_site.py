#!/usr/bin/env python3
"""
Complete AI Tool Gems — Full Site Audit
Checks: schema image fields, broken links, sitemap vs files, alt texts, etc.
"""
import re
import json
from pathlib import Path
from html.parser import HTMLParser

BASE = Path(r"D:/ai-tool-gems")

# ============================================================
# 1. SCHEMA IMAGE AUDIT — saari pages mein image field check
# ============================================================
def extract_json_ld_blocks(html: str) -> list[dict]:
    """Extract all JSON-LD blocks from HTML."""
    blocks = []
    for match in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL):
        try:
            data = json.loads(match.group(1).strip())
            blocks.append(data)
        except json.JSONDecodeError:
            pass
    return blocks


def find_missing_images(data, path="") -> list[str]:
    """Recursively find missing image fields in structured data."""
    missing = []
    
    def check(obj, p):
        if isinstance(obj, dict):
            # Check known types that SHOULD have image
            schema_type = obj.get("@type")
            if isinstance(schema_type, list):
                schema_type = schema_type[0]
            
            image_required_types = ["Product", "Organization", "WebSite", "WebPage", 
                                     "LocalBusiness", "AboutPage", "ItemList",
                                     "FAQPage", "Person", "Article", "BlogPosting"]
            
            if schema_type in image_required_types and "image" not in obj:
                if not p:
                    p = schema_type
                missing.append(f"{schema_type} (#{p}): missing 'image'")
            
            # Recurse into children
            for key, val in obj.items():
                if key not in ("@context", "@type", "@id"):
                    check(val, f"{p}.{key}" if p else key)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check(item, f"{path}[{i}]")
    
    check(data, "")
    return missing


# ============================================================
# 2. BROKEN LINKS CHECK
# ============================================================
class LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.in_script = False
        self.in_style = False
        
    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.in_script = True
        if tag == "style":
            self.in_style = True
        if tag == "a" and not self.in_script and not self.in_style:
            for name, value in attrs:
                if name == "href" and value:
                    self.links.append(value)
        if tag == "img" and not self.in_script:
            for name, value in attrs:
                if name == "src" and value:
                    self.links.append(("img", value))
    
    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False
        if tag == "style":
            self.in_style = False


def check_links(page_path: Path):
    """Check for broken/missing links in a page."""
    try:
        html = page_path.read_text(encoding="utf-8", errors="replace")
    except:
        return []
    
    parser = LinkExtractor()
    parser.feed(html)
    
    issues = []
    for link in parser.links:
        if isinstance(link, tuple):
            # It's an image
            src = link[1]
            if src.startswith("http"):
                continue  # External
            # Check if local file exists
            full_path = page_path.parent / src
            if not full_path.exists():
                rel_path = src
                issues.append(f"  MISSING IMG: {rel_path}")
        else:
            href = link
            if href.startswith("http"):
                continue  # External
            if href.startswith("#"):
                continue  # Anchor
            if href.startswith("mailto:"):
                continue
            if href.startswith("tel:"):
                continue
            if href.startswith("https://wa.me"):
                continue
            if href.startswith("whatsapp"):
                continue
            # Check if local file/dir exists
            full_path = page_path.parent / href
            if full_path.exists():
                continue
            # Check if it's a route like #products
            if href.startswith("#"):
                continue
            # It might be a directory index
            if href.endswith("/"):
                if not (page_path.parent / href / "index.html").exists():
                    issues.append(f"  BROKEN LINK: {href} (dir index not found)")
            else:
                if not full_path.exists():
                    issues.append(f"  BROKEN LINK: {href}")
    
    return issues


# ============================================================
# 3. ALT TEXT CHECK
# ============================================================
def check_alt_texts(page_path: Path):
    """Check images without alt text."""
    try:
        html = page_path.read_text(encoding="utf-8", errors="replace")
    except:
        return []
    
    issues = []
    # Find all img tags
    for match in re.finditer(r'<img\s+([^>]*)>', html, re.IGNORECASE):
        attrs = match.group(1)
        src_match = re.search(r'src=["\']([^"\']+)["\']', attrs, re.IGNORECASE)
        alt_match = re.search(r'alt=["\']([^"\']*?)["\']', attrs, re.IGNORECASE)
        
        src = src_match.group(1) if src_match else "unknown"
        
        if not alt_match:
            issues.append(f"  MISSING ALT: <img src=\"{src}\">")
        elif alt_match.group(1).strip() == "":
            issues.append(f"  EMPTY ALT: <img src=\"{src}\">")
    
    return issues


# ============================================================
# 4. SITEMAP VS ACTUAL FILES
# ============================================================
def parse_sitemap(sitemap_path: Path) -> set[str]:
    """Extract URLs from sitemap."""
    if not sitemap_path.exists():
        return set()
    content = sitemap_path.read_text(encoding="utf-8", errors="replace")
    urls = set()
    for match in re.finditer(r'<loc>(.*?)</loc>', content):
        urls.add(match.group(1))
    return urls


def get_html_files() -> set[str]:
    """Get all HTML file URLs based on file structure."""
    urls = set()
    base_url = "https://aitoolgems.tech"
    jp_base_url = "https://aitoolgems.tech/jp"
    
    for html_file in BASE.rglob("*.html"):
        if ".git" in str(html_file):
            continue
        rel = html_file.relative_to(BASE)
        parts = rel.parts
        
        if parts and parts[0] == "jp":
            # Japan site
            url_path = "/".join(parts[1:])  # skip 'jp'
            if url_path.endswith(".html"):
                url_path = url_path[:-5]  # remove .html
            if not url_path.endswith("/"):
                url_path += "/"
            urls.add(f"{jp_base_url}/{url_path}")
        else:
            url_path = "/".join(parts)
            if url_path.endswith(".html"):
                url_path = url_path[:-5]  # remove .html
            if not url_path.endswith("/"):
                url_path += "/"
            urls.add(f"{base_url}/{url_path}")
    
    return urls


# ============================================================
# MAIN AUDIT
# ============================================================
def main():
    print("=" * 70)
    print("🔍 AI Tool Gems — Complete Site Audit")
    print("=" * 70)
    
    html_files = list(BASE.rglob("*.html"))
    html_files = [f for f in html_files if ".git" not in str(f)]
    html_files.sort()
    
    # -------------------------------------------------------
    # AUDIT 1: Schema Image Check
    # -------------------------------------------------------
    print("\n" + "=" * 70)
    print("📊 AUDIT 1: Schema 'image' Field Check")
    print("=" * 70)
    
    schema_issues = []
    for html_file in html_files:
        try:
            html = html_file.read_text(encoding="utf-8", errors="replace")
        except:
            continue
        
        blocks = extract_json_ld_blocks(html)
        for block in blocks:
            missing = find_missing_images(block)
            for m in missing:
                rel = html_file.relative_to(BASE)
                schema_issues.append(f"{rel}: {m}")
    
    if schema_issues:
        print(f"\n❌ Found {len(schema_issues)} schema image issues:")
        for issue in schema_issues:
            print(f"  {issue}")
    else:
        print("\n✅ No missing 'image' fields in any schema!")
    
    # -------------------------------------------------------
    # AUDIT 2: Broken Links
    # -------------------------------------------------------
    print("\n" + "=" * 70)
    print("🔗 AUDIT 2: Broken Links Check")
    print("=" * 70)
    
    broken_links = []
    for html_file in html_files:
        issues = check_links(html_file)
        if issues:
            rel = html_file.relative_to(BASE)
            for issue in issues:
                broken_links.append(f"{rel}: {issue.strip()}")
    
    if broken_links:
        print(f"\n❌ Found {len(broken_links)} broken links:")
        for issue in broken_links[:30]:  # Show first 30
            print(f"  {issue}")
        if len(broken_links) > 30:
            print(f"  ... and {len(broken_links) - 30} more")
    else:
        print("\n✅ No broken links found!")
    
    # -------------------------------------------------------
    # AUDIT 3: Missing Alt Text
    # -------------------------------------------------------
    print("\n" + "=" * 70)
    print("🖼️  AUDIT 3: Missing/Empty Alt Text")
    print("=" * 70)
    
    alt_issues = []
    for html_file in html_files:
        issues = check_alt_texts(html_file)
        if issues:
            rel = html_file.relative_to(BASE)
            for issue in issues:
                alt_issues.append(f"{rel}: {issue.strip()}")
    
    if alt_issues:
        print(f"\n❌ Found {len(alt_issues)} alt text issues:")
        for issue in alt_issues[:30]:
            print(f"  {issue}")
        if len(alt_issues) > 30:
            print(f"  ... and {len(alt_issues) - 30} more")
    else:
        print("\n✅ All images have alt text!")
    
    # -------------------------------------------------------
    # AUDIT 4: Sitemap vs Actual Files
    # -------------------------------------------------------
    print("\n" + "=" * 70)
    print("🗺️  AUDIT 4: Sitemap vs Actual Files")
    print("=" * 70)
    
    sitemap_urls = parse_sitemap(BASE / "sitemap.xml")
    sitemap_jp_urls = parse_sitemap(BASE / "jp" / "sitemap.xml")
    all_sitemap_urls = sitemap_urls | sitemap_jp_urls
    
    actual_urls = get_html_files()
    
    # Normalize URLs for comparison (remove trailing slash for comparison)
    def normalize(url):
        return url.rstrip("/")
    
    sitemap_norm = {normalize(u) for u in all_sitemap_urls}
    actual_norm = {normalize(u) for u in actual_urls}
    
    missing_from_sitemap = actual_norm - sitemap_norm
    extra_in_sitemap = sitemap_norm - actual_norm
    
    print(f"\n📁 Total HTML files: {len(actual_urls)}")
    print(f"📄 URLs in sitemap: {len(all_sitemap_urls)}")
    
    if missing_from_sitemap:
        print(f"\n❌ {len(missing_from_sitemap)} pages in files but NOT in sitemap:")
        for url in sorted(missing_from_sitemap)[:20]:
            print(f"  MISSING FROM SITEMAP: {url}")
        if len(missing_from_sitemap) > 20:
            print(f"  ... and {len(missing_from_sitemap) - 20} more")
    else:
        print("\n✅ All pages are in sitemap!")
    
    if extra_in_sitemap:
        print(f"\n⚠️  {len(extra_in_sitemap)} URLs in sitemap but files not found:")
        for url in sorted(extra_in_sitemap)[:20]:
            print(f"  EXTRA IN SITEMAP: {url}")
        if len(extra_in_sitemap) > 20:
            print(f"  ... and {len(extra_in_sitemap) - 20} more")
    else:
        print("✅ No orphan sitemap entries!")
    
    # -------------------------------------------------------
    # AUDIT 5: JP Pages - Check for PK references
    # -------------------------------------------------------
    print("\n" + "=" * 70)
    print("🇯🇵 AUDIT 5: JP Pages — Check for PK References")
    print("=" * 70)
    
    jp_html_files = [f for f in html_files if "jp/" in str(f)]
    pk_ref_issues = []
    
    for html_file in jp_html_files:
        try:
            html = html_file.read_text(encoding="utf-8", errors="replace")
        except:
            continue
        
        # Check for Pakistan-specific references that shouldn't be in JP pages
        if re.search(r'/tools/[^/]+/', html) and not re.search(r'jp/tools/', html):
            # Has reference to PK tools (not starting with jp/)
            pass
        
        # Check hreflang
        if 'hreflang="en-PK"' in html:
            pass  # This is OK - it's the alternate link
        
        # Check for PK-specific content that shouldn't be in JP
        if re.search(r'Rs\.\s*\d+', html):
            # Has PKR prices in JP page
            pk_ref_issues.append(f"{html_file.relative_to(BASE)}: contains PKR price (Rs.)")
    
    if pk_ref_issues:
        print(f"\n⚠️  {len(pk_ref_issues)} JP pages with PK references:")
        for issue in pk_ref_issues:
            print(f"  {issue}")
    else:
        print("\n✅ No PK references found in JP pages!")
    
    # -------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------
    print("\n" + "=" * 70)
    print("📋 AUDIT SUMMARY")
    print("=" * 70)
    
    total_issues = len(schema_issues) + len(broken_links) + len(alt_issues)
    print(f"\nTotal Issues Found: {total_issues}")
    print(f"  Schema 'image' missing: {len(schema_issues)}")
    print(f"  Broken links: {len(broken_links)}")
    print(f"  Missing/empty alt text: {len(alt_issues)}")
    
    if total_issues == 0:
        print("\n🎉 All clear! Site looks healthy.")
    else:
        print(f"\n⚠️  {total_issues} issues need attention.")
    
    return total_issues


if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(0 if exit_code == 0 else 1)
