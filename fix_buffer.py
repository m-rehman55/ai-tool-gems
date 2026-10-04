import re
from pathlib import Path
p = Path('D:/ai-tool-gems/marketing_agent/buffer.py')
html = p.read_text(encoding='utf-8')
old = '            except HTTPError as exc:\n                detail = exc.read().decode("utf-8", errors="replace")\n                raise BufferError(f"Buffer API HTTP {exc.code}: {detail[:300]}") from exc'
new = '''            except HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                if exc.code == 429:
                    time.sleep(5)
                    try:
                        with urlopen(request, timeout=30) as response:
                            payload = json.loads(response.read().decode("utf-8"))
                    except HTTPError as exc2:
                        if exc2.code == 429:
                            time.sleep(15)
                            with urlopen(request, timeout=30) as response:
                                payload = json.loads(response.read().decode("utf-8"))
                        else:
                            raise BufferError(f"Buffer API HTTP {exc2.code}: {detail[:300]}") from exc2
                else:
                    raise BufferError(f"Buffer API HTTP {exc.code}: {detail[:300]}") from exc'''
if old in html:
    html = html.replace(old, new)
    p.write_text(html, encoding='utf-8')
    print("Fixed")
else:
    print("Not found")
