#!/usr/bin/env python3
"""
Generate daily GSC URL Inspection checklist with direct links.
Each link opens GSC URL Inspection for that specific URL.
"""
from pathlib import Path

BASE = Path(r"D:/ai-tool-gems")
OUTPUT = BASE / "gsc_daily_checklist.html"

PK_TOOLS = [
    "chatgpt", "gemini", "veo", "leonardo", "elevenlabs",
    "canva", "figma", "capcut", "adobe", "lovable",
    "gamma", "replit", "n8n", "notion", "nordvpn",
    "surfshark", "youtube", "netflix", "linkedin", "windows"
]

JP_TOOLS = [
    "chatgpt", "gemini", "veo", "leonardo", "elevenlabs",
    "canva", "figma", "capcut", "adobe", "lovable",
    "gamma", "replit", "n8n", "manus", "notion", "nordvpn",
    "surfshark", "youtube", "netflix", "linkedin", "windows"
]

PK_GUIDES = [
    "guides/",
    "guides/ai-tools-price-pakistan/",
    "guides/chatgpt-vs-gemini-pakistan/",
    "guides/canva-vs-figma-pakistan/",
]

JP_GUIDES = [
    "jp/guides/",
    "jp/guides/ai-tools-price-japan/",
    "jp/guides/chatgpt-vs-gemini-japan/",
    "jp/guides/canva-vs-figma-japan/",
]

def gsc_url(base_url):
    """Generate GSC URL Inspection link."""
    return f"https://search.google.com/search-console/url-inspection?q={base_url}"

def make_day_html(day_num, title, urls):
    """Generate HTML for one day."""
    items = ""
    for url in urls:
        gsc_link = gsc_url(url)
        items += f"""
        <tr>
            <td>{urls.index(url) + 1}</td>
            <td><a href="{gsc_link}" target="_blank">{url}</a></td>
            <td>☐</td>
        </tr>"""
    
    return f"""
    <div class="day">
        <h2>Day {day_num}: {title}</h2>
        <table>
            <thead>
                <tr><th>#</th><th>URL</th><th>Done</th></tr>
            </thead>
            <tbody>
                {items}
            </tbody>
        </table>
        <p class="count">Total: {len(urls)} URLs</p>
    </div>"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GSC Daily Indexing Checklist</title>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background: #0d1117;
        color: #c9d1d9;
        padding: 24px;
        max-width: 900px;
        margin: 0 auto;
    }}
    h1 {{
        color: #58a6ff;
        font-size: 24px;
        margin-bottom: 8px;
    }}
    .subtitle {{
        color: #8b949e;
        font-size: 14px;
        margin-bottom: 24px;
    }}
    .day {{
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 16px;
    }}
    .day h2 {{
        color: #f0f6fc;
        font-size: 18px;
        margin-bottom: 12px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
    }}
    th, td {{
        text-align: left;
        padding: 8px 12px;
        border-bottom: 1px solid #21262d;
    }}
    th {{
        color: #8b949e;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
    }}
    td {{
        font-size: 14px;
    }}
    a {{
        color: #58a6ff;
        text-decoration: none;
    }}
    a:hover {{
        text-decoration: underline;
    }}
    .count {{
        color: #8b949e;
        font-size: 12px;
        margin-top: 8px;
    }}
    .progress {{
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .progress-bar {{
        width: 200px;
        height: 8px;
        background: #21262d;
        border-radius: 4px;
        overflow: hidden;
    }}
    .progress-fill {{
        height: 100%;
        background: #238636;
        width: 0%;
        transition: width 0.3s;
    }}
    .instructions {{
        background: #1c2333;
        border-left: 3px solid #58a6ff;
        padding: 16px;
        margin-bottom: 24px;
        border-radius: 0 8px 8px 0;
        font-size: 14px;
        line-height: 1.6;
    }}
    .instructions strong {{
        color: #f0f6fc;
    }}
</style>
</head>
<body>
    <h1>📋 GSC Daily Indexing Checklist</h1>
    <p class="subtitle">aitoolgems.tech — 66 URLs to index | 9 days</p>
    
    <div class="instructions">
        <strong>How to use:</strong><br>
        1. Click any URL link → opens GSC URL Inspection<br>
        2. Click "Test Live URL" → wait for results<br>
        3. If "URL is on Google" → mark ✅ Done<br>
        4. If "URL is not on Google" → click "Request Indexing" → mark ✅ Done<br>
        5. Check the ☐ box when done<br>
        <br>
        <strong>Tip:</strong> Do 5-10 URLs per day. Google indexes overnight.
    </div>
    
    <div class="progress">
        <div>
            <strong>Progress</strong><br>
            <span id="done-count">0</span> / 66 done
        </div>
        <div class="progress-bar">
            <div class="progress-fill" id="progress-fill"></div>
        </div>
    </div>
    
    {make_day_html(1, "Core Pages — PK + JP", [
        "https://aitoolgems.tech/",
        "https://aitoolgems.tech/about.html",
        "https://aitoolgems.tech/contact.html",
        "https://aitoolgems.tech/policies.html",
        "https://aitoolgems.tech/privacy.html",
        "https://aitoolgems.tech/terms.html",
        "https://aitoolgems.tech/how-we-review.html",
        "https://aitoolgems.tech/jp/",
        "https://aitoolgems.tech/jp/about.html",
        "https://aitoolgems.tech/jp/contact.html",
        "https://aitoolgems.tech/jp/policies.html",
        "https://aitoolgems.tech/jp/privacy.html",
        "https://aitoolgems.tech/jp/terms.html",
        "https://aitoolgems.tech/jp/how-we-review.html",
    ])}
    
    {make_day_html(2, "Top Tools PK — Batch 1", [
        f"https://aitoolgems.tech/tools/{t}/" for t in PK_TOOLS[:5]
    ])}
    
    {make_day_html(3, "Top Tools PK — Batch 2", [
        f"https://aitoolgems.tech/tools/{t}/" for t in PK_TOOLS[5:10]
    ])}
    
    {make_day_html(4, "Top Tools PK — Batch 3", [
        f"https://aitoolgems.tech/tools/{t}/" for t in PK_TOOLS[10:15]
    ])}
    
    {make_day_html(5, "Top Tools PK — Batch 4", [
        f"https://aitoolgems.tech/tools/{t}/" for t in PK_TOOLS[15:20]
    ])}
    
    {make_day_html(6, "Top Tools JP — Batch 1", [
        f"https://aitoolgems.tech/jp/tools/{t}/" for t in JP_TOOLS[:5]
    ])}
    
    {make_day_html(7, "Top Tools JP — Batch 2", [
        f"https://aitoolgems.tech/jp/tools/{t}/" for t in JP_TOOLS[5:10]
    ])}
    
    {make_day_html(8, "Top Tools JP — Batch 3", [
        f"https://aitoolgems.tech/jp/tools/{t}/" for t in JP_TOOLS[10:15]
    ])}
    
    {make_day_html(9, "Guides — PK + JP", PK_GUIDES + JP_GUIDES)}
    
    <script>
        // Save progress to localStorage
        function updateProgress() {{
            const checks = document.querySelectorAll('input[type="checkbox"]');
            const total = checks.length;
            const done = Array.from(checks).filter(c => c.checked).length;
            document.getElementById('done-count').textContent = done;
            document.getElementById('progress-fill').style.width = (done / total * 100) + '%';
            localStorage.setItem('gsc_progress', JSON.stringify(
                Array.from(checks).map(c => c.checked)
            ));
        }}
        
        // Load saved progress
        window.addEventListener('DOMContentLoaded', () => {{
            const saved = localStorage.getItem('gsc_progress');
            if (saved) {{
                const checks = document.querySelectorAll('input[type="checkbox"]');
                const vals = JSON.parse(saved);
                checks.forEach((c, i) => {{ c.checked = vals[i]; }});
                updateProgress();
            }}
        }});
        
        // Add checkboxes to each row
        document.querySelectorAll('tbody tr').forEach(tr => {{
            const td = tr.querySelector('td:last-child');
            const cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.addEventListener('change', updateProgress);
            td.innerHTML = '';
            td.appendChild(cb);
        }});
        
        updateProgress();
    </script>
</body>
</html>
"""

# Fix the f-string issues - regenerate properly
# Actually let me rewrite this without f-strings in the make_day_html calls

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GSC Daily Indexing Checklist</title>
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background: #0d1117;
        color: #c9d1d9;
        padding: 24px;
        max-width: 900px;
        margin: 0 auto;
    }
    h1 { color: #58a6ff; font-size: 24px; margin-bottom: 8px; }
    .subtitle { color: #8b949e; font-size: 14px; margin-bottom: 24px; }
    .day {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .day h2 { color: #f0f6fc; font-size: 18px; margin-bottom: 12px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid #21262d; }
    th { color: #8b949e; font-weight: 600; font-size: 12px; text-transform: uppercase; }
    td { font-size: 14px; }
    a { color: #58a6ff; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .count { color: #8b949e; font-size: 12px; margin-top: 8px; }
    .progress {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .progress-bar { width: 200px; height: 8px; background: #21262d; border-radius: 4px; overflow: hidden; }
    .progress-fill { height: 100%; background: #238636; width: 0%; transition: width 0.3s; }
    .instructions {
        background: #1c2333;
        border-left: 3px solid #58a6ff;
        padding: 16px;
        margin-bottom: 24px;
        border-radius: 0 8px 8px 0;
        font-size: 14px;
        line-height: 1.6;
    }
    .instructions strong { color: #f0f6fc; }
    .tool-links { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
    .tool-links a {
        background: #21262d;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-family: monospace;
    }
</style>
</head>
<body>
    <h1>📋 GSC Daily Indexing Checklist</h1>
    <p class="subtitle">aitoolgems.tech — 66 URLs to index | 9 days</p>
    
    <div class="instructions">
        <strong>How to use:</strong><br>
        1. Click any URL link → opens GSC URL Inspection<br>
        2. Click "Test Live URL" → wait for results<br>
        3. If "URL is on Google" → mark ✅ Done<br>
        4. If "URL is not on Google" → click "Request Indexing" → mark ✅ Done<br>
        5. Check the ☐ box when done<br>
        <br>
        <strong>Tip:</strong> Do 5-10 URLs per day. Google indexes overnight.
    </div>
    
    <div class="progress">
        <div>
            <strong>Progress</strong><br>
            <span id="done-count">0</span> / 66 done
        </div>
        <div class="progress-bar">
            <div class="progress-fill" id="progress-fill"></div>
        </div>
    </div>
"""

# Generate day sections
day_num = 1

# Day 1: Core pages
core_urls = [
    "https://aitoolgems.tech/",
    "https://aitoolgems.tech/about.html",
    "https://aitoolgems.tech/contact.html",
    "https://aitoolgems.tech/policies.html",
    "https://aitoolgems.tech/privacy.html",
    "https://aitoolgems.tech/terms.html",
    "https://aitoolgems.tech/how-we-review.html",
    "https://aitoolgems.tech/jp/",
    "https://aitoolgems.tech/jp/about.html",
    "https://aitoolgems.tech/jp/contact.html",
    "https://aitoolgems.tech/jp/policies.html",
    "https://aitoolgems.tech/jp/privacy.html",
    "https://aitoolgems.tech/jp/terms.html",
    "https://aitoolgems.tech/jp/how-we-review.html",
]

html += f"""
    <div class="day">
        <h2>Day {day_num}: Core Pages — PK + JP (14 URLs)</h2>
        <div class="tool-links">
"""
for url in core_urls:
    html += f'            <a href="{gsc_url(url)}" target="_blank">{url}</a>\n'
html += """        </div>
        <p class="count">☐ Click each link → Test Live URL → Request Indexing → Mark done</p>
    </div>
"""
day_num += 1

# Days 2-5: PK tools (5 per day)
for batch_start in range(0, 20, 5):
    batch = PK_TOOLS[batch_start:batch_start+5]
    batch_urls = [f"https://aitoolgems.tech/tools/{t}/" for t in batch]
    html += f"""
    <div class="day">
        <h2>Day {day_num}: PK Tools — Batch {batch_start//5 + 1} ({len(batch)} URLs)</h2>
        <div class="tool-links">
"""
    for url in batch_urls:
        html += f'            <a href="{gsc_url(url)}" target="_blank">{url}</a>\n'
    html += """        </div>
        <p class="count">☐ Click each link → Test Live URL → Request Indexing → Mark done</p>
    </div>
"""
    day_num += 1

# Days 6-10: JP tools (5 per day)
for batch_start in range(0, 21, 5):
    batch = JP_TOOLS[batch_start:batch_start+5]
    batch_urls = [f"https://aitoolgems.tech/jp/tools/{t}/" for t in batch]
    html += f"""
    <div class="day">
        <h2>Day {day_num}: JP Tools — Batch {batch_start//5 + 1} ({len(batch)} URLs)</h2>
        <div class="tool-links">
"""
    for url in batch_urls:
        html += f'            <a href="{gsc_url(url)}" target="_blank">{url}</a>\n'
    html += """        </div>
        <p class="count">☐ Click each link → Test Live URL → Request Indexing → Mark done</p>
    </div>
"""
    day_num += 1

# Day 11: Guides (4 PK + 4 JP = 8)
guide_urls = []
for g in PK_GUIDES:
    guide_urls.append(f"https://aitoolgems.tech/{g}")
for g in JP_GUIDES:
    guide_urls.append(f"https://aitoolgems.tech/{g}")

html += f"""
    <div class="day">
        <h2>Day {day_num}: Guides — PK + JP ({len(guide_urls)} URLs)</h2>
        <div class="tool-links">
"""
for url in guide_urls:
    html += f'            <a href="{gsc_url(url)}" target="_blank">{url}</a>\n'
html += """        </div>
        <p class="count">☐ Click each link → Test Live URL → Request Indexing → Mark done</p>
    </div>
"""

html += """
    <script>
        function updateProgress() {
            const checks = document.querySelectorAll('input[type="checkbox"]');
            const total = checks.length;
            const done = Array.from(checks).filter(c => c.checked).length;
            document.getElementById('done-count').textContent = done;
            document.getElementById('progress-fill').style.width = (done / total * 100) + '%';
            localStorage.setItem('gsc_progress', JSON.stringify(
                Array.from(checks).map(c => c.checked)
            ));
        }
        
        window.addEventListener('DOMContentLoaded', () => {
            const saved = localStorage.getItem('gsc_progress');
            if (saved) {
                const checks = document.querySelectorAll('input[type="checkbox"]');
                const vals = JSON.parse(saved);
                checks.forEach((c, i) => { c.checked = vals[i]; });
                updateProgress();
            }
            
            // Add checkboxes to each day
            document.querySelectorAll('.day').forEach(day => {
                const count = day.querySelectorAll('.tool-links a').length;
                const container = document.createElement('div');
                container.style.marginTop = '12px';
                container.innerHTML = `<label><input type="checkbox" onchange="updateProgress()"> Day complete (${count} URLs)</label>`;
                day.appendChild(container);
            });
            
            updateProgress();
        });
    </script>
</body>
</html>
"""

write_html(OUTPUT, html)
print(f"✅ Checklist saved to {OUTPUT}")
print(f"   Total URLs: {7 + 20 + 21 + 8} = 56 tool+guide + 14 core = 70")
print(f"   Open in browser: file:///{OUTPUT}")
