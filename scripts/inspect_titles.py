from pathlib import Path
import re

tools_dir = Path("tools")
for tf in sorted(tools_dir.glob("*/index.html")):
    txt = tf.read_text(encoding="utf-8")
    title = re.search(r"<title>(.*?)</title>", txt)
    desc = re.search(r'<meta name="description" content="(.*?)"', txt)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", txt)
    t = title.group(1) if title else "NONE"
    d = desc.group(1) if desc else "NONE"
    h = h1.group(1) if h1 else "NONE"
    print(f"=== {tf.parent.name} ===")
    print(f"TITLE: {t}")
    print(f"DESC:  {d}")
    print(f"H1:    {h}\n")
