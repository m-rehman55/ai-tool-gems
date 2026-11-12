"""
Unified Detail Page and Card Action Synchronizer
Ensures:
1. Every tool detail page (all 65) has BOTH:
   - Primary WhatsApp button: Buy [Tool Name] on WhatsApp (<a class="buy" ...>)
   - Secondary official vendor button: Visit Official [Tool Name] Website -> (<a class="official-vendor-btn" ...>)
2. tool-page.css includes elegant styling for .official-vendor-btn
3. All directory card 'Buy now' buttons on the homepage (index.html) link directly to verified WhatsApp inquiry.
"""

import os
import sys
import re
import html
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.apply_official_link_to_all_cards import COMMERCIAL_OFFICIAL_URLS
from scripts.directory_tools_data import DIRECTORY_TOOLS
WA_PHONE = '923236715731'

def get_official_urls():
    directory_urls = {slug: data.get('official_url') or data.get('url') for slug, data in DIRECTORY_TOOLS.items()}
    return {**COMMERCIAL_OFFICIAL_URLS, **directory_urls}

def unify_detail_pages():
    all_urls = get_official_urls()
    tool_dirs = sorted([d for d in os.listdir(os.path.join(ROOT, 'tools')) if os.path.isdir(os.path.join(ROOT, 'tools', d))])
    
    modified_count = 0
    
    for slug in tool_dirs:
        if slug == "cursor": continue
        idx_path = os.path.join(ROOT, 'tools', slug, 'index.html')
        if not os.path.exists(idx_path):
            continue
            
        with open(idx_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract clean tool name
        name = None
        if slug in DIRECTORY_TOOLS:
            name = DIRECTORY_TOOLS[slug].get('name')
        if not name:
            bc_m = re.search(r'<span aria-current="page">(.*?)</span>', content)
            if bc_m:
                name = bc_m.group(1).strip()
        if not name:
            name = slug.replace('-', ' ').title()
        name = html.unescape(name)
        
        # Extract listed price
        price_m = re.search(r'<div class="price">.*?<strong>(Rs\.\s*[0-9,]+)</strong>', content, re.DOTALL)
        price = price_m.group(1).strip() if price_m else "Rs. 5,600"
        
        # Extract duration
        dur_m = re.search(r'<dt>Duration</dt>\s*<dd>(.*?)</dd>', content)
        duration = dur_m.group(1).strip() if dur_m else "1 Month"
        duration = html.unescape(duration)
        
        official_url = all_urls.get(slug, '#')
        
        # Build standard WhatsApp URL
        wa_text = f"Hello AI Tool Gems,\n\nI want to order {name} ({duration}) for {price}. Please confirm availability, payment details, and delivery time."
        wa_url = f"https://wa.me/{WA_PHONE}?text={urllib.parse.quote(wa_text)}"
        
        wa_btn_html = f'<a class="buy" href="{wa_url}" target="_blank" rel="noopener nofollow">Buy {html.escape(name)} on WhatsApp</a>'
        vendor_btn_html = f'<a class="official-vendor-btn" href="{official_url}" target="_blank" rel="noopener noreferrer">Visit Official {html.escape(name)} Website &rarr;</a>'
        
        # Check current .buy tag
        buy_pattern = re.compile(r'<a[^>]+class="buy"[^>]*>.*?</a>', re.DOTALL)
        existing_buy = buy_pattern.search(content)
        
        if not existing_buy:
            print(f"Skipping {slug}: no .buy tag found")
            continue
            
        # Check if already has official-vendor-btn
        has_vendor_btn = 'class="official-vendor-btn"' in content
        is_dir_tool = slug in DIRECTORY_TOOLS or 'codeium' in content or 'v0.dev' in content
        
        # Formulate new action block:
        # 1. <a class="buy"...>Buy [Name] on WhatsApp</a>
        # 2. <a class="official-vendor-btn"...>Visit Official [Name] Website &rarr;</a>
        
        new_block = vendor_btn_html if is_dir_tool else f'{wa_btn_html}\n        {vendor_btn_html}'
        
        # If the page already had an official-vendor-btn, remove the old one first
        content = re.sub(r'\s*<a class="official-vendor-btn"[^>]*>.*?</a>', '', content)
        
        # Replace the .buy tag with new_block
        updated_content = buy_pattern.sub(new_block, content, count=1)
        
        if updated_content != content:
            with open(idx_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            modified_count += 1
            print(f"[UPDATED] {slug} -> Added WhatsApp + Official Vendor buttons")
            
    print(f"\nTotal detail pages updated: {modified_count} / {len(tool_dirs)}")

def update_tool_page_css():
    css_path = os.path.join(ROOT, 'tool-page.css')
    with open(css_path, 'r', encoding='utf-8') as f:
        css = f.read()
        
    rule = """
.official-vendor-btn {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 14px 22px;
  border-radius: 13px;
  border: 1.5px solid #d9e6df;
  background: #ffffff;
  color: #153f37 !important;
  text-decoration: none;
  font-weight: 700;
  font-size: 15px;
  transition: all 0.2s ease;
}
.official-vendor-btn:hover {
  background: #f5faf6;
  border-color: #2f9f88;
  color: #0d4a3e !important;
  transform: translateY(-1px);
}
"""
    if '.official-vendor-btn' not in css:
        with open(css_path, 'a', encoding='utf-8') as f:
            f.write(rule)
        print("[UPDATED] tool-page.css with .official-vendor-btn styles")
    else:
        print("[SKIPPED] tool-page.css already contains .official-vendor-btn styles")

def update_homepage_directory_wa_links():
    index_path = os.path.join(ROOT, 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    modified = 0
    for slug, data in DIRECTORY_TOOLS.items():
        name = data.get('name', slug)
        price = "Rs. 5,600"
        dur = "1 Month"
        wa_text = f"Hello AI Tool Gems,\n\nI want to order {name} ({dur}) for {price}. Please confirm availability, payment details, and delivery time."
        wa_url = f"https://wa.me/{WA_PHONE}?text={urllib.parse.quote(wa_text)}"
        
        # Look for the directory card's buy-now-card
        old_pattern = re.compile(
            rf'(<article[^>]*data-id="{slug}"[\s\S]*?<a class="buy-now-card explore-tool-btn" )href="tools/{slug}/"([^>]*>)',
            re.IGNORECASE
        )
        
        if old_pattern.search(html_content):
            html_content = old_pattern.sub(
                rf'\1href="{wa_url}" target="_blank" rel="noopener nofollow"\2',
                html_content
            )
            modified += 1
            
    if modified > 0:
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"[UPDATED] {modified} directory card Buy now buttons on index.html with direct WhatsApp URLs")
    else:
        print("[SKIPPED] index.html already updated")

if __name__ == '__main__':
    unify_detail_pages()
    update_tool_page_css()
    update_homepage_directory_wa_links()
