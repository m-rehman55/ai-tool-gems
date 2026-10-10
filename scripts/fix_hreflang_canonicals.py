import glob
import re

fixed = 0
for f in sorted(glob.glob('**/*.html', recursive=True)):
    if '.seo-cache' in f or 'google' in f:
        continue
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    m_canon = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', c)
    if not m_canon:
        m_canon = re.search(r'<link[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\']', c)
    if not m_canon:
        continue
    canonical = m_canon.group(1)
    
    if canonical.endswith('/'):
        bad_url = canonical + 'index.html'
        if bad_url in c:
            new_c = c.replace(bad_url, canonical)
            with open(f, 'w', encoding='utf-8') as fp:
                fp.write(new_c)
            fixed += 1
            print(f"Fixed {f}: {bad_url} -> {canonical}")

print(f"Total fixed: {fixed}")
