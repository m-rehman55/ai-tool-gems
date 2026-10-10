import sys
import os
import re
import json
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(__file__).resolve().parent.parent

print("=" * 60)
print("1. CHECK OG:URL VS CANONICAL")
print("=" * 60)
og_mismatches = []
for f in BASE.glob("**/*.html"):
    if ".git" in str(f) or ".seo-cache" in str(f):
        continue
    txt = f.read_text(encoding="utf-8")
    og = re.search(r'property=["\']og:url["\']\s+content=["\']([^"\']+)["\']', txt) or re.search(r'content=["\']([^"\']+)["\']\s+property=["\']og:url["\']', txt)
    canon = re.search(r'rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', txt) or re.search(r'href=["\']([^"\']+)["\']\s+rel=["\']canonical["\']', txt)
    if og and canon:
        if og.group(1).rstrip('/') != canon.group(1).rstrip('/'):
            og_mismatches.append((str(f.relative_to(BASE)), og.group(1), canon.group(1)))
            print(f"• {f.relative_to(BASE)}:\n    og:url:    {og.group(1)}\n    canonical: {canon.group(1)}")
print(f"Total og:url mismatches: {len(og_mismatches)}")

print("\n" + "=" * 60)
print("2. CHECK CSS LINKS (BROKEN CSS)")
print("=" * 60)
broken_css = []
for f in BASE.glob("**/*.html"):
    if ".git" in str(f) or ".seo-cache" in str(f):
        continue
    txt = f.read_text(encoding="utf-8")
    for m in re.finditer(r'<link[^>]+>', txt):
        tag = m.group(0)
        if 'rel="stylesheet"' in tag or "rel='stylesheet'" in tag:
            href_match = re.search(r'href=["\']([^"\']+)["\']', tag)
            if href_match:
                href = href_match.group(1)
                if not href.startswith(("http://", "https://", "//")):
                    clean = href.split("?")[0]
                    target = (f.parent / clean).resolve()
                    if not target.exists():
                        broken_css.append((str(f.relative_to(BASE)), href))
print(f"Total broken CSS references: {len(broken_css)}")
for item in broken_css:
    print(f"  • {item[0]} -> '{item[1]}'")

print("\n" + "=" * 60)
print("3. CHECK META DESCRIPTION LENGTHS")
print("=" * 60)
long_desc = []
short_desc = []
for f in BASE.glob("**/*.html"):
    if ".git" in str(f) or ".seo-cache" in str(f):
        continue
    txt = f.read_text(encoding="utf-8")
    meta_m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']', txt, re.IGNORECASE) or \
             re.search(r'<meta\s+content=["\']([^"\']*)["\']\s+name=["\']description["\']', txt, re.IGNORECASE)
    if meta_m:
        desc = meta_m.group(1)
        length = len(desc)
        # Ahrefs standard: < 70 chars is short, > 155 chars is long
        if length > 155:
            long_desc.append((str(f.relative_to(BASE)), length, desc))
            print(f"• [LONG {length} chars] {f.relative_to(BASE)}:\n    \"{desc}\"")
        elif length < 70:
            short_desc.append((str(f.relative_to(BASE)), length, desc))
            print(f"• [SHORT {length} chars] {f.relative_to(BASE)}:\n    \"{desc}\"")
print(f"Total Meta Descriptions Too Long (>155 chars): {len(long_desc)}")
print(f"Total Meta Descriptions Too Short (<70 chars): {len(short_desc)}")

print("\n" + "=" * 60)
print("4. CHECK INTERNAL LINKS TO REDIRECTS (Trailing slash / www / http)")
print("=" * 60)
redirect_links = []
for f in BASE.glob("**/*.html"):
    if ".git" in str(f) or ".seo-cache" in str(f):
        continue
    txt = f.read_text(encoding="utf-8")
    for m in re.finditer(r'<a\s+[^>]*href=["\']([^"\']+)["\']', txt):
        href = m.group(1)
        if href.startswith("http://"):
            redirect_links.append((str(f.relative_to(BASE)), href, "HTTP to HTTPS redirect"))
            print(f"• {f.relative_to(BASE)} -> HTTP Link: {href}")
        elif href.startswith("/") or href.startswith("../") or not href.startswith(("http", "mailto:", "tel:", "#", "javascript:")):
            clean = href.split("#")[0].split("?")[0]
            if clean in ["/deals", "/prices", "/guides", "/tools", "deals", "prices", "guides", "tools", "../deals", "../prices", "../guides", "../tools"]:
                redirect_links.append((str(f.relative_to(BASE)), href, "Missing trailing slash"))
                print(f"• {f.relative_to(BASE)} -> Missing trailing slash link: {href}")
print(f"Total redirect links found: {len(redirect_links)}")

print("\n" + "=" * 60)
print("5. CHECK ORPHAN PAGES & INCOMING INLINKS")
print("=" * 60)
all_html_files = {str(f.relative_to(BASE)).replace("\\", "/") for f in BASE.glob("**/*.html") if not any(x in str(f) for x in [".git", ".seo-cache", "google"])}
inlinks = {p: 0 for p in all_html_files}
for f in BASE.glob("**/*.html"):
    if ".git" in str(f) or ".seo-cache" in str(f):
        continue
    txt = f.read_text(encoding="utf-8")
    for m in re.finditer(r'<a\s+[^>]*href=["\']([^"\']+)["\']', txt):
        href = m.group(1).split("#")[0].split("?")[0]
        if not href or href.startswith(("http:", "https:", "mailto:", "tel:", "javascript:")):
            continue
        target = (f.parent / href).resolve()
        try:
            rel = str(target.relative_to(BASE)).replace("\\", "/")
            if rel in inlinks:
                inlinks[rel] += 1
            elif (target / "index.html").exists():
                rel_idx = str((target / "index.html").relative_to(BASE)).replace("\\", "/")
                if rel_idx in inlinks:
                    inlinks[rel_idx] += 1
        except Exception:
            pass

orphans = [p for p, count in inlinks.items() if count == 0 and not p.startswith("404")]
low_links = [p for p, count in inlinks.items() if count == 1]
print(f"Orphan pages (0 internal inlinks): {len(orphans)}")
for o in orphans:
    print(f"  • {o}")
print(f"\nPages with only 1 inlink: {len(low_links)}")
for l in low_links:
    print(f"  • {l} (inlinks: {inlinks[l]})")

print("\n" + "=" * 60)
print("6. CHECK STRUCTURED DATA SCHEMAS")
print("=" * 60)
schema_issues = []
for f in BASE.glob("**/*.html"):
    if ".git" in str(f) or ".seo-cache" in str(f):
        continue
    txt = f.read_text(encoding="utf-8")
    for m in re.finditer(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', txt, re.DOTALL):
        raw = m.group(1).strip()
        try:
            data = json.loads(raw)
            # check graph items
            items = data.get("@graph", [data])
            for item in items:
                stype = item.get("@type")
                # Product check
                if stype == "Product":
                    if not item.get("offers"):
                        schema_issues.append((str(f.relative_to(BASE)), "Product missing offers"))
                    if not item.get("aggregateRating") and not item.get("review"):
                        schema_issues.append((str(f.relative_to(BASE)), "Product missing aggregateRating or review"))
                # Article check
                elif stype == "Article":
                    if not item.get("author"):
                        schema_issues.append((str(f.relative_to(BASE)), "Article missing author"))
                    if not item.get("datePublished"):
                        schema_issues.append((str(f.relative_to(BASE)), "Article missing datePublished"))
        except Exception as e:
            schema_issues.append((str(f.relative_to(BASE)), f"Malformed JSON: {e}"))
print(f"Schema issues detected: {len(schema_issues)}")
for si in schema_issues:
    print(f"  • {si[0]}: {si[1]}")
