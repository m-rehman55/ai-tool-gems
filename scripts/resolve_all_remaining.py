#!/usr/bin/env python3
"""
Fix remaining schema issues and URL alignments:
1. Wrap contact.html, policies.html, privacy.html, terms.html in @graph with Organization & WebSite nodes.
2. Fix schema 'url' in how-we-price.html, how-we-source.html, product-verification.html, correction-policy.html.
3. Ensure nofollow on any remaining wa.me link.
"""

import json
import re
from pathlib import Path

ROOT = Path(".")

ORG_NODE = {
    "@type": "Organization",
    "@id": "https://aitoolgems.tech/#organization",
    "name": "AI Tool Gems Pakistan",
    "url": "https://aitoolgems.tech/",
    "logo": {
        "@type": "ImageObject",
        "url": "https://aitoolgems.tech/assets/brand-logo-light.webp"
    }
}

WEBSITE_NODE = {
    "@type": "WebSite",
    "@id": "https://aitoolgems.tech/#website",
    "url": "https://aitoolgems.tech/",
    "name": "AI Tool Gems",
    "publisher": {
        "@id": "https://aitoolgems.tech/#organization"
    }
}

def fix_policy_schemas():
    files = ["contact.html", "policies.html", "privacy.html", "terms.html"]
    for fname in files:
        f = ROOT / fname
        if not f.exists():
            continue
        txt = f.read_text(encoding="utf-8")
        m = re.search(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', txt, re.DOTALL)
        if not m:
            continue
        try:
            data = json.loads(m.group(1).strip())
        except Exception:
            continue
            
        # If single object without @graph, wrap in @graph
        if isinstance(data, dict) and "@graph" not in data:
            # remove redundant @context inside node
            if "@context" in data:
                del data["@context"]
            new_data = {
                "@context": "https://schema.org",
                "@graph": [
                    data,
                    ORG_NODE.copy(),
                    WEBSITE_NODE.copy()
                ]
            }
            new_json_str = json.dumps(new_data, indent=2, ensure_ascii=False)
            txt = txt.replace(m.group(0), f'<script type="application/ld+json">\n{new_json_str}\n</script>')
            f.write_text(txt, encoding="utf-8")
            print(f"Wrapped schema in @graph for: {fname}")

def fix_policy_schema_urls():
    files = [
        ("how-we-price.html", "https://aitoolgems.tech/how-we-price.html"),
        ("how-we-source.html", "https://aitoolgems.tech/how-we-source.html"),
        ("product-verification.html", "https://aitoolgems.tech/product-verification.html"),
        ("correction-policy.html", "https://aitoolgems.tech/correction-policy.html")
    ]
    for fname, target_url in files:
        f = ROOT / fname
        if not f.exists():
            continue
        txt = f.read_text(encoding="utf-8")
        txt = re.sub(r'"url":\s*"https://aitoolgems\.tech/[^"/]+/"', f'"url": "{target_url}"', txt)
        f.write_text(txt, encoding="utf-8")
        print(f"Fixed schema url in: {fname} -> {target_url}")

def fix_wa_me_nofollow():
    for f in ROOT.glob("**/*.html"):
        if any(x in str(f) for x in [".git", ".seo-cache"]):
            continue
        txt = f.read_text(encoding="utf-8")
        orig = txt
        
        def replace_wa(m):
            tag = m.group(0)
            if 'wa.me' in tag or 'api.whatsapp.com' in tag:
                if 'rel=' in tag:
                    tag = re.sub(r'rel=["\'][^"\']*["\']', 'rel="noopener nofollow"', tag)
                else:
                    tag = tag[:-1] + ' rel="noopener nofollow">'
            return tag
            
        txt = re.sub(r'<a\s+[^>]*href=["\']https://(?:wa\.me|api\.whatsapp\.com)[^"\']*["\'][^>]*>', replace_wa, txt)
        if txt != orig:
            f.write_text(txt, encoding="utf-8")
            print(f"Ensured nofollow on WhatsApp links in: {f}")

if __name__ == "__main__":
    fix_policy_schemas()
    fix_policy_schema_urls()
    fix_wa_me_nofollow()
