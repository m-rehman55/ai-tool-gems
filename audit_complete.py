#!/usr/bin/env python3
"""
Complete site audit - finds all issues across the website
"""
import json
import re
from pathlib import Path

BASE = Path(r"D:/ai-tool-gems")

def get_all_html_files():
    files = []
    for f in BASE.rglob("*.html"):
        if ".git" not in str(f):
            files.append(f)
    return sorted(files)

def audit_page(page_path: Path):
    """Returns list of issues found on a page"""
    issues = []
    try:
        html = page_path.read_text(encoding="utf-8", errors="replace")
    except:
        return [{"error": "Cannot read file"}]
    
    rel_path = page_path.relative_to(BASE)
    
    # 1. Check JSON-LD blocks
    jsonld_blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    
    for block_num, block in enumerate(jsonld_blocks, 1):
        try:
            data = json.loads(block.strip())
        except json.JSONDecodeError as e:
            issues.append(f"JSON-LD Block {block_num}: Invalid JSON - {e}")
            continue
        
        # Check all @graph items
        def check_schema(obj, path=""):
            if isinstance(obj, dict):
                schema_type = obj.get("@type")
                if isinstance(schema_type, list):
                    schema_type = schema_type[0] if schema_type else "Unknown"
                
                # Product schema checks
                if schema_type == "Product":
                    if "image" not in obj:
                        issues.append(f"Product schema (#{path}): Missing 'image' field")
                    if "name" not in obj:
                        issues.append(f"Product schema (#{path}): Missing 'name' field")
                    if "offers" not in obj:
                        issues.append(f"Product schema (#{path}): Missing 'offers' field")
                    if "brand" not in obj and "description" in obj:
                        # Only flag if it seems like a product page
                        pass  # Brand is optional
                
                # Organization schema checks
                if schema_type in ["Organization", "OnlineStore"]:
                    if "image" not in obj:
                        issues.append(f"{schema_type} schema (#{path}): Missing 'image' field")
                    if "url" not in obj:
                        issues.append(f"{schema_type} schema (#{path}): Missing 'url' field")
                
                # WebPage/WebSite checks
                if schema_type in ["WebPage", "WebSite", "AboutPage", "CollectionPage"]:
                    if "image" not in obj:
                        issues.append(f"{schema_type} schema (#{path}): Missing 'image' field")
                
                # FAQPage checks
                if schema_type == "FAQPage":
                    if "mainEntity" not in obj:
                        issues.append(f"FAQPage schema (#{path}): Missing 'mainEntity' field")
                
                # Check nested objects
                for key, value in obj.items():
                    if key.startswith("@"):
                        continue
                    if isinstance(value, (dict, list)):
                        check_schema(value, f"{path}.{key}" if path else key)
            
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_schema(item, f"{path}[{i}]" if path else f"[item {i}]")
        
        if isinstance(data, list):
            for item in data:
                check_schema(item)
        elif isinstance(data, dict):
            check_schema(data)
    
    # 2. Check for missing alt text
    img_pattern = re.findall(r'<img\s+([^>]*?)>', html, re.IGNORECASE)
    for img_tag in img_pattern:
        alt_match = re.search(r'alt=["\']([^"\']*?)["\']', img_tag, re.IGNORECASE)
        if not alt_match or alt_match.group(1).strip() == "":
            src_match = re.search(r'src=["\']([^"\']+)["\']', img_tag, re.IGNORECASE)
            src = src_match.group(1) if src_match else "unknown"
            issues.append(f"Image missing/empty alt: <img src=\"{src}\">")
    
    return issues

def main():
    print("=" * 60)
    print("🔍 Complete Site Audit - AI Tool Gems")
    print("=" * 60)
    
    all_issues = {}
    
    for page_path in get_all_html_files():
        rel_path = str(page_path.relative_to(BASE))
        issues = audit_page(page_path)
        if issues:
            all_issues[rel_path] = issues
    
    # Print results
    print(f"\nTotal pages checked: {len(get_all_html_files())}")
    print(f"Pages with issues: {len(all_issues)}")
    print("\n" + "=" * 60)
    
    if all_issues:
        for page, issues in sorted(all_issues.items()):
            print(f"\n📄 {page}")
            for issue in issues:
                print(f"   • {issue}")
    else:
        print("\n✅ No issues found!")

if __name__ == "__main__":
    main()
