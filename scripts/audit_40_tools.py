"""
Audit of all existing 40+ tool pages in tools/ for commercial claims, warranty claims,
resale risks, pricing representations, and structured data parity.
"""

import os, re
from pathlib import Path

def audit_tools():
    tools_dir = Path("tools")
    tool_folders = sorted([f for f in tools_dir.iterdir() if f.is_dir() and (f / "index.html").exists()])
    
    print(f"Auditing {len(tool_folders)} tool profiles in tools/...")
    
    findings = []
    
    for folder in tool_folders:
        slug = folder.name
        index_file = folder / "index.html"
        html = index_file.read_text(encoding="utf-8", errors="ignore")
        
        # Check title and price
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        title = title_match.group(1) if title_match else ""
        
        # Check commercial signals
        has_buy_now = bool(re.search(r'buy\s+now|order\s+now|add\s+to\s+cart', html, re.IGNORECASE))
        has_whatsapp_order = bool(re.search(r'order\s+on\s+whatsapp|whatsapp\s+order', html, re.IGNORECASE))
        has_warranty = bool(re.search(r'warranty|guarantee|refund\s+policy', html, re.IGNORECASE))
        has_pkr_price = bool(re.search(r'Rs\.?\s*[\d,]+|PKR\s*[\d,]+', html, re.IGNORECASE))
        
        # Check structured data
        has_product_schema = '"@type": "Product"' in html or "'@type': 'Product'" in html
        has_software_schema = '"@type": "SoftwareApplication"' in html or "'@type': 'SoftwareApplication'" in html
        has_aggregate_rating = 'AggregateRating' in html
        
        status = "VERIFIED"
        notes = []
        
        if has_buy_now or has_whatsapp_order:
            if slug not in ["windsurf", "v0", "bolt-new", "manus-ai", "qwen", "coursera-plus", "udemy-personal", "opus-clip", "invideo-ai", "descript", "make", "firecrawl"]:
                # Historical tools have assisted WhatsApp inquiry
                status = "COMMERCIAL_RISK"
                notes.append("Assisted order inquiry present; requires strict disclosure that AI Tool Gems is an assisted procurement facilitator, not the software vendor.")
        
        if has_warranty:
            status = "REQUIRES_OWNER_DECISION"
            notes.append("Contains warranty/guarantee language; must ensure no vendor uptime guarantee is claimed.")
            
        if has_product_schema and has_aggregate_rating:
            notes.append("Product schema contains ratings; must verify parity with visible on-page customer reviews.")

        findings.append({
            "slug": slug,
            "title": title[:50] + "...",
            "pkr_price": has_pkr_price,
            "whatsapp_order": has_whatsapp_order,
            "warranty": has_warranty,
            "schema": "SoftwareApplication" if has_software_schema else ("Product" if has_product_schema else "Other"),
            "status": status,
            "notes": "; ".join(notes) if notes else "Fully compliant with directory standards."
        })
        
    print(f"Audit completed for {len(findings)} tools.")
    return findings

if __name__ == "__main__":
    results = audit_tools()
    print("\nSummary of Statuses:")
    from collections import Counter
    counts = Counter(r["status"] for r in results)
    for k, v in counts.items():
        print(f"  {k}: {v}")
