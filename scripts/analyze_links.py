import glob
import re
from collections import defaultdict

files = sorted(glob.glob('**/*.html', recursive=True))
inbound = defaultdict(set)
outbound = defaultdict(set)
canon_map = {}

for f in files:
    if '.seo-cache' in f or 'google' in f:
        continue
    with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
        c = fp.read()
    m = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', c)
    if not m:
        m = re.search(r'<link[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\']', c)
    canon = m.group(1) if m else f
    canon_map[f] = canon

for f in files:
    if '.seo-cache' in f or 'google' in f:
        continue
    source = canon_map[f]
    with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
        c = fp.read()
    hrefs = re.findall(r'<a[^>]*href=["\']([^"\']+)["\']', c)
    for h in hrefs:
        if h.startswith('#') or h.startswith('mailto:') or h.startswith('tel:') or 'wa.me' in h or 'whatsapp' in h:
            continue
        if h.startswith('http') and not h.startswith('https://aitoolgems.tech'):
            continue
        
        target = h
        if not target.startswith('https://aitoolgems.tech'):
            if target.startswith('/'):
                target = 'https://aitoolgems.tech' + target
            else:
                parts = f.replace('\\', '/').split('/')
                parent_dir = '/'.join(parts[:-1])
                if parent_dir:
                    target = f"https://aitoolgems.tech/{parent_dir}/{target}"
                else:
                    target = f"https://aitoolgems.tech/{target}"
        
        # Clean double slashes in path
        target = re.sub(r'(https://[^/]+)/+', r'\1/', target)
        target = target.replace('/./', '/')
        while '/../' in target:
            target = re.sub(r'/[^/]+/\.\./', '/', target)
        
        # normalize trailing index.html
        if target.endswith('/index.html'):
            target = target[:-10]
        elif target.endswith('index.html'):
            target = target[:-10]
        
        if not target.endswith('/') and not target.endswith('.html'):
            target += '/'
            
        outbound[source].add(target)
        inbound[target].add(source)

all_canonicals = set(canon_map.values())
orphans = [u for u in all_canonicals if len(inbound[u]) == 0]
underlinked = [u for u in all_canonicals if len(inbound[u]) < 3]

print(f"Total evaluated pages: {len(all_canonicals)}")
print(f"Total detected internal links: {sum(len(v) for v in outbound.values())}")
print(f"Orphan pages (0 inbound links): {len(orphans)}")
if orphans:
    for o in orphans:
        print(f"  Orphan: {o}")

print(f"\nUnderlinked pages (< 3 inbound links): {len(underlinked)}")
for u in underlinked:
    print(f"  Underlinked ({len(inbound[u])} in): {u}")
