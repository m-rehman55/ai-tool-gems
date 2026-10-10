import glob
import re

tools = sorted(glob.glob('tools/*/index.html'))
print(f"Total tool pages: {len(tools)}")
for t in tools:
    with open(t, 'r', encoding='utf-8') as f:
        c = f.read()
    m_meta = re.search(r'<meta[^>]*name=["\']last_verified["\'][^>]*content=["\']([^"\']+)["\']', c)
    m_schema = re.search(r'"priceValidUntil":\s*"([^"]+)"', c)
    pkr = re.findall(r'Rs\.\s*[\d,]+', c)
    tool_name = t.split('/')[1] if '/' in t else t.split('\\')[1]
    meta_val = m_meta.group(1) if m_meta else "MISSING"
    schema_val = m_schema.group(1) if m_schema else "MISSING"
    print(f"{tool_name:12}: last_verified={meta_val:12} priceValidUntil={schema_val:12} prices={pkr[:2]}")
