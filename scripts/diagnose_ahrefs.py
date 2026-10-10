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
    if any(x in str(f) for x in [".git", ".seo-cache"]):
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
    if any(x in str(f) for x in [".git", ".seo-cache"]):
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
print("3. CHECK META DESCRIPTION LENGTHS (Target: 120-155 chars)")
print("=" * 60)
long_desc = []
short_desc = []
for f in BASE.glob("**/*.html"):
    if any(x in str(f) for x in [".git", ".seo-cache"]):
        continue
    txt = f.read_text(encoding="utf-8")
    meta_m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']', txt, re.IGNORECASE) or \
             re.search(r'<meta\s+content=["\']([^"\']*)["\']\s+name=["\']description["\']', txt, re.IGNORECASE)
    if meta_m:
        desc = meta_m.group(1)
        length = len(desc)
        if length > 155:
            long_desc.append((str(f.relative_to(BASE)), length, desc))
            print(f"• [LONG {length} chars] {f.relative_to(BASE)}:\n    \"{desc}\"")
        elif length < 120:
            short_desc.append((str(f.relative_to(BASE)), length, desc))
            print(f"• [SHORT {length} chars] {f.relative_to(BASE)}:\n    \"{desc}\"")
print(f"Total Meta Descriptions Too Long (>155 chars): {len(long_desc)}")
print(f"Total Meta Descriptions Too Short (<120 chars): {len(short_desc)}")

print("\n" + "=" * 60)
print("4. CHECK META REFRESH REDIRECTS")
print("=" * 60)
meta_refreshes = []
for f in BASE.glob("**/*.html"):
    if any(x in str(f) for x in [".git", ".seo-cache"]):
        continue
    txt = f.read_text(encoding="utf-8")
    if re.search(r'http-equiv=["\']refresh["\']', txt, re.I):
        meta_refreshes.append(str(f.relative_to(BASE)))
        print(f"• Meta refresh found in: {f.relative_to(BASE)}")
print(f"Total meta refresh redirects: {len(meta_refreshes)}")

print("\n" + "=" * 60)
print("5. CHECK OUTBOUND LINKS (Known 3XX / 4XX Redirects)")
print("=" * 60)
outbound_issues = []
for f in BASE.glob("**/*.html"):
    if any(x in str(f) for x in [".git", ".seo-cache"]):
        continue
    txt = f.read_text(encoding="utf-8")
    for m in re.finditer(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>', txt):
        href = m.group(1)
        tag = m.group(0)
        # Check known redirect URLs
        if "openai.com/chatgpt/pricing" in href:
            outbound_issues.append((str(f.relative_to(BASE)), href, "Redirects to chatgpt.com/pricing"))
        elif "elevenlabs.io/pricing" in href:
            outbound_issues.append((str(f.relative_to(BASE)), href, "Blocks crawlers with 403"))
        elif "whatsapp.com/channel/" in href and "www.whatsapp.com" not in href:
            outbound_issues.append((str(f.relative_to(BASE)), href, "Redirects to www.whatsapp.com/channel/"))
        elif ("wa.me/" in href or "api.whatsapp.com" in href) and not re.search(r'rel=["\'][^"\']*\bnofollow\b', tag):
            outbound_issues.append((str(f.relative_to(BASE)), href, "WhatsApp link missing rel='nofollow'"))
for item in outbound_issues:
    print(f"  • {item[0]}: {item[1]} ({item[2]})")
print(f"Total outbound link issues: {len(outbound_issues)}")

print("\n" + "=" * 60)
print("6. CHECK STRUCTURED DATA SCHEMAS (Schema.org & Google Rich Results)")
print("=" * 60)
schema_issues = []
for f in BASE.glob("**/*.html"):
    if any(x in str(f) for x in [".git", ".seo-cache"]):
        continue
    txt = f.read_text(encoding="utf-8")
    scripts = re.findall(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', txt, re.DOTALL)
    if not scripts:
        continue
    defined_ids = set()
    referenced_ids = set()

    for s in scripts:
        try:
            data = json.loads(s.strip())
        except Exception as e:
            schema_issues.append((str(f.relative_to(BASE)), f"Invalid JSON: {e}"))
            continue

        def audit_node(node, is_graph=False):
            if not isinstance(node, dict):
                return
            ntype = node.get("@type")
            nid = node.get("@id")
            if nid:
                defined_ids.add(nid)
            if is_graph and "@context" in node:
                schema_issues.append((str(f.relative_to(BASE)), f"@context inside graph node {ntype}"))
            if ntype in ["FAQPage", "BreadcrumbList", "ItemList"] and "image" in node:
                schema_issues.append((str(f.relative_to(BASE)), f"Illegal property 'image' on {ntype}"))
            if ntype == "Article":
                pub = node.get("publisher")
                if isinstance(pub, dict) and len(pub) == 1 and "@id" in pub:
                    referenced_ids.add((pub["@id"], "Article.publisher"))
                elif isinstance(pub, dict) and "name" not in pub:
                    schema_issues.append((str(f.relative_to(BASE)), "Article.publisher missing 'name'"))

            for k, v in node.items():
                if isinstance(v, dict) and "@id" in v and len(v) == 1:
                    referenced_ids.add((v["@id"], f"{ntype}.{k}"))

        if isinstance(data, dict):
            if "@graph" in data:
                if "image" in data:
                    schema_issues.append((str(f.relative_to(BASE)), "Illegal property 'image' on @graph container"))
                for n in data["@graph"]:
                    audit_node(n, is_graph=True)
            else:
                audit_node(data, is_graph=False)

    for ref_id, loc in referenced_ids:
        if ref_id.startswith("https://aitoolgems.tech/#") and ref_id not in defined_ids:
            schema_issues.append((str(f.relative_to(BASE)), f"Unresolved {loc} pointing to {ref_id}"))

print(f"Total schema issues detected: {len(schema_issues)}")
for item in schema_issues[:20]:
    print(f"  • {item[0]}: {item[1]}")
if len(schema_issues) > 20:
    print(f"  ... and {len(schema_issues) - 20} more.")

print("\n" + "=" * 60)
print("7. CHECK CSS SIZE (< 100 KB)")
print("=" * 60)
styles_file = BASE / "styles.css"
if styles_file.exists():
    sz = len(styles_file.read_bytes())
    print(f"styles.css size: {sz:,} bytes ({'PASS' if sz < 100000 else 'FAIL'})")
