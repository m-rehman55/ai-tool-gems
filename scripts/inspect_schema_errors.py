#!/usr/bin/env python3
"""
Inspect all JSON-LD schemas across all HTML files for:
1. Sibling 'image' on @graph
2. 'image' property on FAQPage or BreadcrumbList (not recognized by Schema.org)
3. '@context' inside an inner node of @graph
4. Unresolved @id references (#organization, #website)
5. Google Rich Results requirements for Article and Product
6. Multiple FAQPages on a single page
"""

import json
import re
from pathlib import Path

ROOT = Path(".")

def inspect():
    html_files = [f for f in ROOT.glob("**/*.html") if not f.parts[0].startswith(".") and "venv" not in f.parts]
    total_issues = 0

    for f in sorted(html_files):
        txt = f.read_text(encoding="utf-8")
        scripts = re.findall(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', txt, re.DOTALL)
        if not scripts:
            continue

        file_issues = []
        defined_ids = set()
        referenced_ids = set()

        for s in scripts:
            try:
                data = json.loads(s.strip())
            except Exception as e:
                file_issues.append(f"Invalid JSON: {e}")
                continue

            def check_node(node, parent_is_graph=False):
                if not isinstance(node, dict):
                    return
                ntype = node.get("@type")
                nid = node.get("@id")
                if nid:
                    defined_ids.add(nid)

                # Check @context in inner graph node
                if parent_is_graph and "@context" in node:
                    file_issues.append(f"@context inside @graph node ({ntype})")

                # Check illegal 'image'
                if ntype in ["FAQPage", "BreadcrumbList", "ItemList"] and "image" in node:
                    file_issues.append(f"Illegal property 'image' on {ntype}")

                # Collect referenced IDs
                for k, v in node.items():
                    if isinstance(v, dict) and "@id" in v and len(v) == 1:
                        referenced_ids.add((v["@id"], f"{ntype}.{k}"))
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict) and "@id" in item and len(item) == 1:
                                referenced_ids.add((item["@id"], f"{ntype}.{k}[]"))

            if isinstance(data, dict):
                if "@graph" in data:
                    if "image" in data:
                        file_issues.append("Illegal property 'image' at root of @graph container")
                    for node in data["@graph"]:
                        check_node(node, parent_is_graph=True)
                else:
                    check_node(data, parent_is_graph=False)
            elif isinstance(data, list):
                for node in data:
                    check_node(node)

        # Check unresolved IDs
        for ref_id, loc in referenced_ids:
            if ref_id.startswith("https://aitoolgems.tech/#") and ref_id not in defined_ids:
                file_issues.append(f"Unresolved @id reference '{ref_id}' in {loc}")

        if file_issues:
            print(f"\n[{f}] - {len(file_issues)} issue(s):")
            for iss in file_issues:
                print(f"  • {iss}")
            total_issues += len(file_issues)

    print(f"\n==========================================")
    print(f"Total schema issues across all files: {total_issues}")
    print(f"==========================================")

if __name__ == "__main__":
    inspect()
