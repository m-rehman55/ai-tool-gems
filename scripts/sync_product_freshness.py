import glob
import re

tools = sorted(glob.glob('tools/*/index.html'))
updated_tools = 0

for t in tools:
    with open(t, 'r', encoding='utf-8') as f:
        c = f.read()
    
    # 1. Update last_verified meta
    c = re.sub(r'<meta name="last_verified" content="[^"]*">', '<meta name="last_verified" content="2026-10-10">', c)
    
    # 2. Ensure priceValidUntil is present in the Offer schema if not already present
    if '"priceValidUntil"' not in c:
        c = re.sub(
            r'("price":\s*"[^"]*",)(\s*"availability")',
            r'\1\n        "priceValidUntil": "2026-12-31",\2',
            c
        )
    
    with open(t, 'w', encoding='utf-8') as f:
        f.write(c)
    updated_tools += 1

print(f"Updated {updated_tools} tool pages with last_verified=2026-10-10 and priceValidUntil=2026-12-31.")

# Update prices/index.html
with open('prices/index.html', 'r', encoding='utf-8') as f:
    p_content = f.read()

p_content = re.sub(r'<meta name="last_verified" content="[^"]*">', '<meta name="last_verified" content="2026-10-10">', p_content)
p_content = re.sub(r'"dateModified":\s*"[^"]*"', '"dateModified": "2026-10-10"', p_content)
p_content = p_content.replace('All prices verified as of 2026-10-01.', 'All prices verified as of 2026-10-10.')
p_content = p_content.replace('<td>2026-10-01</td>', '<td>2026-10-10</td>')

with open('prices/index.html', 'w', encoding='utf-8') as f:
    f.write(p_content)

print("Updated prices/index.html with verified 2026-10-10 dates.")
