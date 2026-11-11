import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
LOGO_DIR = BASE / "assets" / "product-logos"

DOMAINS = {
    "ahrefs": "ahrefs.com",
    "windsurf": "codeium.com",
    "bolt-new": "bolt.new",
    "descript": "descript.com",
    "supabase": "supabase.com",
    "notebooklm": "notebooklm.google",
    "davinci-resolve": "blackmagicdesign.com",
    "skillshare": "skillshare.com",
    "quizlet": "quizlet.com",
    "v0": "v0.dev",
    "invideo-ai": "invideo.io",
    "make": "make.com",
    "qwen": "alibabacloud.com",
    "udemy-personal": "udemy.com",
}

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

for slug, domain in DOMAINS.items():
    out_file = LOGO_DIR / f"{slug}.png"
    url = f"https://www.google.com/s2/favicons?domain={domain}&sz=256"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            if len(data) > 500:
                with open(out_file, "wb") as f:
                    f.write(data)
                print(f"Downloaded {slug}.png ({len(data)} bytes)")
            else:
                print(f"Warning: {slug} icon too small ({len(data)} bytes)")
    except Exception as e:
        print(f"Error fetching {slug}: {e}")

