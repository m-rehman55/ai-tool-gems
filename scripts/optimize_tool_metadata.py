#!/usr/bin/env python3
"""
Optimizes titles, meta descriptions, and OG tags across all 20 Pakistan tool pages
for high CTR and exact search intent (Buy, Price in Pakistan, EasyPaisa, JazzCash).
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TOOLS_DIR = BASE / "tools"

def optimize_metadata(html_file: Path) -> bool:
    html = html_file.read_text(encoding="utf-8")
    
    # Extract existing price and product name from title
    # Example: "ChatGPT Plus Pakistan: Rs. 2,300 | AI Tool Gems"
    title_match = re.search(r'<title>([^:]+)\s*Pakistan:\s*Rs\.\s*([\d,]+)\s*\|\s*AI Tool Gems</title>', html)
    if not title_match:
        # Fallback regex
        title_match = re.search(r'<title>([^<|]+?)(?:\s*Pakistan)?:\s*Rs\.\s*([\d,]+).*?</title>', html)
        
    if not title_match:
        print(f"Could not parse title for {html_file.parent.name}")
        return False
        
    tool_name = title_match.group(1).strip()
    price = title_match.group(2).strip()
    
    new_title = f"Buy {tool_name} in Pakistan (Rs. {price}) | EasyPaisa & JazzCash"
    new_desc = f"Buy {tool_name} in Pakistan at lowest price Rs. {price}. Fast WhatsApp delivery (15-30 mins), 7-day warranty. Pay easily with EasyPaisa, JazzCash or SadaPay."
    
    # Update <title>
    html = re.sub(r'<title>.*?</title>', f'<title>{new_title}</title>', html, count=1)
    
    # Update <meta name="description">
    html = re.sub(r'<meta name="description" content=".*?"', f'<meta name="description" content="{new_desc}"', html, count=1)
    
    # Update og:title
    html = re.sub(r'<meta property="og:title" content=".*?"', f'<meta property="og:title" content="{new_title}"', html, count=1)
    
    # Update twitter:title
    html = re.sub(r'<meta name="twitter:title" content=".*?"', f'<meta name="twitter:title" content="{new_title}"', html, count=1)
    
    html_file.write_text(html, encoding="utf-8")
    print(f"Optimized: {tool_name} -> {new_title}")
    return True

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    count = 0
    for f in sorted(TOOLS_DIR.glob("*/index.html")):
        if optimize_metadata(f):
            count += 1
            
    print(f"\nTotal tool pages metadata optimized: {count}/20")

if __name__ == "__main__":
    main()
