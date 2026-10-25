import os
import re
import json
from html.parser import HTMLParser

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = None
        self.in_title = False
        self.meta_tags = []
        self.link_tags = []
        self.h1_tags = []
        self.in_h1 = False
        self.current_h1 = ""
        self.images = []
        self.json_ld_scripts = []
        self.in_json_ld = False
        self.current_json_ld = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'title':
            self.in_title = True
            self.title = ""
        elif tag == 'meta':
            self.meta_tags.append(attrs_dict)
        elif tag == 'link':
            self.link_tags.append(attrs_dict)
        elif tag == 'h1':
            self.in_h1 = True
            self.current_h1 = ""
        elif tag == 'img':
            self.images.append(attrs_dict)
        elif tag == 'script':
            if attrs_dict.get('type') == 'application/ld+json':
                self.in_json_ld = True
                self.current_json_ld = ""

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        elif tag == 'h1':
            self.in_h1 = False
            self.h1_tags.append(self.current_h1.strip())
        elif tag == 'script' and self.in_json_ld:
            self.in_json_ld = False
            self.json_ld_scripts.append(self.current_json_ld.strip())

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif self.in_h1:
            self.current_h1 += data
        elif self.in_json_ld:
            self.current_json_ld += data


def audit_bing_guidelines():
    html_files = []
    for root, dirs, files in os.walk(WORKSPACE):
        if any(ignored in root for ignored in ['.git', '.seo-cache', 'node_modules', 'reports', 'scratch', 'brain']):
            continue
        for f in files:
            if f.endswith('.html'):
                html_files.append(os.path.join(root, f))
    
    print(f"Scanning {len(html_files)} HTML pages against Bing Webmaster Guidelines...\n")
    
    issues_by_file = {}
    titles_seen = {}
    
    for fpath in html_files:
        rel_path = os.path.relpath(fpath, WORKSPACE)
        if 'admin.html' in rel_path or 'gsc_daily_checklist' in rel_path:
            continue
            
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        parser = PageParser()
        try:
            parser.feed(content)
        except Exception as e:
            issues_by_file[rel_path] = [f"HTML parsing failure: {e}"]
            continue
            
        issues = []
        
        # 1. Meta Robots
        robots_tags = [m for m in parser.meta_tags if m.get('name', '').lower() == 'robots']
        for r in robots_tags:
            c = r.get('content', '').lower()
            if 'noindex' in c:
                issues.append(f"CRITICAL: Robots meta contains 'noindex': {c}")
                
        # 2. Canonical Tag
        canon_links = [l for l in parser.link_tags if l.get('rel', '').lower() == 'canonical']
        if not canon_links or not canon_links[0].get('href'):
            issues.append("Missing <link rel='canonical'>")
        else:
            canon_href = canon_links[0].get('href')
            if not canon_href.startswith('https://aitoolgems.tech'):
                issues.append(f"Canonical URL does not start with https://aitoolgems.tech: {canon_href}")
                
        # 3. Title Tag
        title_text = parser.title.strip() if parser.title else ""
        if not title_text:
            issues.append("Missing or empty <title> tag")
        else:
            if len(title_text) > 75:
                issues.append(f"Title is overly long for Bing ({len(title_text)} chars): '{title_text}'")
            if title_text in titles_seen:
                issues.append(f"Duplicate title with {titles_seen[title_text]}: '{title_text}'")
            else:
                titles_seen[title_text] = rel_path
                
        # 4. Meta Description
        desc_tags = [m for m in parser.meta_tags if m.get('name', '').lower() == 'description']
        if not desc_tags or not desc_tags[0].get('content', '').strip():
            issues.append("Missing or empty meta description")
        else:
            desc_text = desc_tags[0].get('content', '').strip()
            if len(desc_text) < 40:
                issues.append(f"Meta description too short ({len(desc_text)} chars)")
            elif len(desc_text) > 175:
                issues.append(f"Meta description too long ({len(desc_text)} chars)")
                
        # 5. Heading Hierarchy (H1)
        if len(parser.h1_tags) == 0:
            issues.append("No <h1> tag found on page")
        elif len(parser.h1_tags) > 1:
            issues.append(f"Multiple <h1> tags found ({len(parser.h1_tags)} tags): {parser.h1_tags}")
            
        # 6. Images Alt Text
        missing_alt = [img for img in parser.images if not img.get('alt') or not img.get('alt').strip()]
        if missing_alt:
            issues.append(f"{len(missing_alt)} image(s) missing alt attribute")
            
        # 7. Structured Data (JSON-LD)
        if not parser.json_ld_scripts:
            issues.append("No JSON-LD structured data found")
        else:
            for s_content in parser.json_ld_scripts:
                try:
                    data = json.loads(s_content)
                    if not isinstance(data, dict):
                        issues.append("JSON-LD root is not a dictionary/object")
                except Exception as e:
                    issues.append(f"Invalid JSON-LD syntax: {e}")
                    
        # 8. Unnatural / Keyword-stuffed pattern detection
        awkward_matches = re.findall(
            r'(?:Can I [A-Z][a-z0-9\s]{8,40} using|proceeding to [A-Z][a-z0-9\s]{8,40} or purchasing|finding a reliable [A-Z][a-z0-9\s]{8,40} crucial|Deploying a verified [A-Z][a-z0-9\s]{8,40} workflow)',
            content
        )
        if awkward_matches:
            issues.append(f"Unnatural keyword stuffing / template insertion detected: {awkward_matches[:2]}")

        if issues:
            issues_by_file[rel_path] = issues

    print("=== BING GUIDELINES AUDIT REPORT ===")
    print(f"Total HTML files inspected: {len(html_files)}")
    print(f"Files with issues: {len(issues_by_file)}")
    print("------------------------------------")
    for fpath, issues in sorted(issues_by_file.items()):
        print(f"\n[PAGE] {fpath}:")
        for iss in issues:
            print(f"   [WARN] {iss}")

if __name__ == '__main__':
    audit_bing_guidelines()
