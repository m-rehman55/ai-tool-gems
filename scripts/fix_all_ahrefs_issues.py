#!/usr/bin/env python3
"""
Comprehensive Fix Script for All Ahrefs Issues:
1. Remove meta refresh in blog/index.html and upgrade to full Blog hub.
2. Fix external 3XX / 4XX outbound links:
   - openai.com/chatgpt/pricing/ -> chatgpt.com/pricing
   - elevenlabs.io/pricing -> elevenlabs.io/
   - whatsapp.com/channel/ -> www.whatsapp.com/channel/
   - add rel="nofollow noopener" to wa.me and api.whatsapp.com links
3. Expand short meta descriptions to 130-150 characters across all pages.
4. Clean and fix all JSON-LD schemas:
   - Remove 'image' on @graph root
   - Remove 'image' on BreadcrumbList, FAQPage, ItemList
   - Remove '@context' inside @graph nodes
   - Define canonical Organization & WebSite nodes in @graph so all @id references resolve
   - Ensure Article schema has complete author and publisher for Google Rich Results
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

def fix_blog_page():
    print("--- 1. Fixing blog/index.html (Remove meta refresh & enhance) ---")
    blog_file = ROOT / "blog" / "index.html"
    if not blog_file.exists():
        return
    txt = blog_file.read_text(encoding="utf-8")
    # Remove meta http-equiv refresh
    txt = re.sub(r'<meta\s+http-equiv=["\']refresh["\'][^>]*>\s*', '', txt, flags=re.I)
    
    # Update lead text
    txt = txt.replace("Redirecting to our comprehensive Guides &amp; Blog library. If you are not redirected automatically within 2 seconds, click below:",
                      "Welcome to AI Tool Gems Blog. Read our latest Pakistan AI buying guides, pricing breakdowns, tutorials, and developer tool comparisons.")
    
    blog_file.write_text(txt, encoding="utf-8")
    print("Fixed blog/index.html: Removed meta refresh")

def fix_outbound_links():
    print("\n--- 2. Fixing Outbound Links (3XX & 4XX) ---")
    html_files = [f for f in ROOT.glob("**/*.html") if not any(x in str(f) for x in [".git", ".seo-cache"])]
    
    for f in html_files:
        txt = f.read_text(encoding="utf-8")
        orig_txt = txt
        
        # 1. openai pricing redirect
        txt = txt.replace("https://openai.com/chatgpt/pricing/", "https://chatgpt.com/pricing")
        txt = txt.replace("https://openai.com/chatgpt/pricing", "https://chatgpt.com/pricing")
        
        # 2. elevenlabs 403
        txt = txt.replace("https://elevenlabs.io/pricing", "https://elevenlabs.io/")
        
        # 3. whatsapp channel non-www redirect
        txt = txt.replace("https://whatsapp.com/channel/0029VbDnEgCHLHQOYpDo5c31", "https://www.whatsapp.com/channel/0029VbDnEgCHLHQOYpDo5c31")
        
        # 4. wa.me and api.whatsapp.com: ensure rel="nofollow noopener"
        def add_nofollow(m):
            tag = m.group(0)
            if 'wa.me/' in tag or 'api.whatsapp.com' in tag:
                if 'rel=' in tag:
                    # Update rel to include nofollow noopener
                    tag = re.sub(r'rel=["\']([^"\']*)["\']', lambda rm: f'rel="{" ".join(set(rm.group(1).split() + ["nofollow", "noopener"]))}"', tag)
                else:
                    tag = tag[:-1] + ' rel="nofollow noopener">'
            return tag
            
        txt = re.sub(r'<a\s+[^>]*href=["\']https://(?:wa\.me|api\.whatsapp\.com)[^"\']*["\'][^>]*>', add_nofollow, txt)
        
        if txt != orig_txt:
            f.write_text(txt, encoding="utf-8")
            print(f"Fixed outbound links in: {f}")
            
    # Also update content-queue.json if needed
    cq = ROOT / "data" / "seo" / "content-queue.json"
    if cq.exists():
        cq_txt = cq.read_text(encoding="utf-8")
        cq_txt = cq_txt.replace("https://elevenlabs.io/pricing", "https://elevenlabs.io/")
        cq.write_text(cq_txt, encoding="utf-8")
        print("Updated content-queue.json")

def fix_short_meta_descriptions():
    print("\n--- 3. Optimizing Short Meta Descriptions (Target: 130-150 chars) ---")
    
    # Precise dictionary of expanded descriptions (strictly 130-150 chars)
    expanded = {
        "privacy.html": "Privacy policy for AI Tool Gems Pakistan. Learn how we safeguard customer data, order details, and privacy for AI tool subscriptions and payments.",
        "terms.html": "Terms of service for AI Tool Gems Pakistan. Review terms governing account purchases, replacement warranties, PKR payments, and order fulfillment.",
        "contact.html": "Contact AI Tool Gems Pakistan. Get verified support for AI tool orders, payment assistance via EasyPaisa or JazzCash, and rapid 15-minute delivery.",
        "how-we-review.html": "Our review method for AI tools in Pakistan. How we verify PKR pricing, features, delivery speeds, warranties, and local payment methods objectively.",
        "how-we-price.html": "How AI Tool Gems prices digital software and AI subscriptions in Pakistan. Transparent PKR pricing, zero hidden conversion fees, and local support.",
        "how-we-source.html": "How AI Tool Gems sources verified software license keys, team invitations, and AI accounts with strict warranties for Pakistani professionals.",
        "product-verification.html": "Our multi-step verification process for AI subscriptions in Pakistan. We test accounts, validity periods, and fulfillment before buyer delivery.",
        "correction-policy.html": "Correction policy for AI Tool Gems Pakistan. How we maintain transparency, promptly update marketplace PKR pricing, and correct published data.",
        "guides/businesses/index.html": "Complete guide to AI tools for Pakistani businesses. Compare top tools for productivity, CRM, marketing automation, and team billing in PKR.",
        "guides/students/index.html": "Best budget-friendly AI tools for Pakistani students. Compare writing, research, coding, and thesis assistance tools with PKR pricing and discounts.",
        "guides/creators/index.html": "Top AI tools for Pakistani content creators. Produce viral short-form videos, YouTube reels, and high-CTR designs using CapCut, Canva, and Leonardo.",
        "guides/developers/index.html": "Complete guide to AI tools for Pakistani developers. Accelerate coding, debugging, and app development with Replit, Cursor AI, n8n, and Lovable.",
        "guides/productivity/index.html": "Top productivity AI tools in Pakistan. Streamline daily documentation, project management, and automated workflows using Notion AI and smart tools.",
        "guides/ai-tools-pakistan/index.html": "2026 directory of AI tools in Pakistan. Compare verified tools, official features, and PKR payment options via EasyPaisa, JazzCash, and bank transfer.",
        "guides/ai-subscriptions-pakistan/index.html": "Complete AI subscriptions guide for Pakistan. Understand private accounts, team seats, replacement warranties, and safe local payment methods.",
        "guides/ai-tools-pricing/index.html": "AI tools pricing directory for Pakistan. Compare verified PKR subscription costs, duration terms, and warranty coverage across top AI services.",
        "guides/canva/index.html": "Complete Canva Pro Pakistan guide. Explore Canva Pro Edu, brand kits, AI Magic Studio features, and invitation access with EasyPaisa payment in PKR.",
        "guides/capcut/index.html": "CapCut Pro Pakistan guide. Unlock VIP video filters, 4K 60fps export, auto-captions, and background removal with verified PKR pricing and support.",
        "guides/gemini/index.html": "Google Gemini Pro Pakistan guide. Access 18-month invitation seats, multimodal 2M context window, and Google Workspace AI with local payment.",
        "guides/chatgpt-alternatives/index.html": "Best ChatGPT alternatives in Pakistan. Compare Claude 3.5 Sonnet, Google Gemini Pro, and specialized AI coding models with local PKR pricing."
    }
    
    for rel_path, desc in expanded.items():
        f = ROOT / rel_path
        if not f.exists():
            continue
        txt = f.read_text(encoding="utf-8")
        length = len(desc)
        assert 125 <= length <= 152, f"Length {length} invalid for {rel_path}: {desc}"
        txt = re.sub(r'<meta\s+name=["\']description["\']\s+content=["\'][^"\']+["\']',
                     f'<meta name="description" content="{desc}"', txt)
        f.write_text(txt, encoding="utf-8")
        print(f"Updated description ({length} chars) in: {rel_path}")

def fix_schemas():
    print("\n--- 4. Cleaning and Fixing JSON-LD Schemas ---")
    html_files = [f for f in ROOT.glob("**/*.html") if not any(x in str(f) for x in [".git", ".seo-cache"])]

    for f in html_files:
        txt = f.read_text(encoding="utf-8")
        scripts = list(re.finditer(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', txt, re.DOTALL))
        if not scripts:
            continue
            
        modified = False
        new_txt = txt
        
        for m in scripts:
            raw_json = m.group(1).strip()
            try:
                data = json.loads(raw_json)
            except Exception:
                continue
                
            orig_data_str = json.dumps(data, sort_keys=True)
            
            # Helper to clean a node
            def clean_node(node, in_graph=False):
                if not isinstance(node, dict):
                    return
                # Remove inner @context
                if in_graph and "@context" in node:
                    del node["@context"]
                # Remove illegal image
                ntype = node.get("@type")
                if ntype in ["FAQPage", "BreadcrumbList", "ItemList"] and "image" in node:
                    del node["image"]
                # For Article: ensure complete publisher
                if ntype == "Article":
                    pub = node.get("publisher")
                    if isinstance(pub, dict) and ("@id" in pub or "name" not in pub):
                        node["publisher"] = {
                            "@type": "Organization",
                            "@id": "https://aitoolgems.tech/#organization",
                            "name": "AI Tool Gems Pakistan",
                            "url": "https://aitoolgems.tech/",
                            "logo": {
                                "@type": "ImageObject",
                                "url": "https://aitoolgems.tech/assets/brand-logo-light.webp"
                            }
                        }
                # Recurse
                for k, v in list(node.items()):
                    if isinstance(v, dict):
                        clean_node(v, in_graph=in_graph)
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict):
                                clean_node(item, in_graph=in_graph)

            # Clean root
            if isinstance(data, dict):
                if "@graph" in data:
                    if "image" in data:
                        del data["image"]
                    for n in data["@graph"]:
                        clean_node(n, in_graph=True)
                    
                    # Ensure Org & Website nodes exist if referenced
                    graph_ids = {n.get("@id") for n in data["@graph"] if isinstance(n, dict)}
                    needs_org = any("https://aitoolgems.tech/#organization" in json.dumps(n) for n in data["@graph"])
                    needs_site = any("https://aitoolgems.tech/#website" in json.dumps(n) for n in data["@graph"])
                    
                    if needs_org and "https://aitoolgems.tech/#organization" not in graph_ids:
                        data["@graph"].append(ORG_NODE.copy())
                    if needs_site and "https://aitoolgems.tech/#website" not in graph_ids:
                        data["@graph"].append(WEBSITE_NODE.copy())
                else:
                    clean_node(data, in_graph=False)
                    # If single node has unresolved publisher #organization
                    if data.get("publisher") == {"@id": "https://aitoolgems.tech/#organization"}:
                        data["publisher"] = ORG_NODE.copy()
            elif isinstance(data, list):
                for n in data:
                    clean_node(n, in_graph=False)

            new_data_str = json.dumps(data, sort_keys=True)
            if new_data_str != orig_data_str:
                formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
                new_txt = new_txt.replace(m.group(0), f'<script type="application/ld+json">\n{formatted_json}\n</script>')
                modified = True
                
        if modified:
            f.write_text(new_txt, encoding="utf-8")
            print(f"Cleaned schemas in: {f}")

if __name__ == "__main__":
    fix_blog_page()
    fix_outbound_links()
    fix_short_meta_descriptions()
    fix_schemas()
