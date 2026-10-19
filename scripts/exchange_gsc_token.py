"""
Exchange Google OAuth authorization code for permanent refresh token,
update local .env, and update GitHub repository secrets.
"""
import os
import sys
import json
import urllib.parse
import urllib.request
import subprocess
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/exchange_gsc_token.py <code_or_redirect_url>")
        sys.exit(1)

    raw_input = sys.argv[1].strip()
    
    # Extract code if full URL was pasted
    if "code=" in raw_input:
        parsed = urllib.parse.urlparse(raw_input)
        qs = urllib.parse.parse_qs(parsed.query)
        code = qs.get("code", [""])[0]
    else:
        code = raw_input

    if not code:
        print("ERROR: Could not find authorization code.")
        sys.exit(1)

    # Load credentials from .env
    env_path = Path(".env")
    env_lines = env_path.read_text(encoding="utf-8").splitlines()
    env = {}
    for l in env_lines:
        if l.strip() and not l.strip().startswith("#") and "=" in l:
            k, v = l.strip().split("=", 1)
            env[k.strip()] = v.strip()

    client_id = env.get("GSC_CLIENT_ID", "").strip()
    client_secret = env.get("GSC_CLIENT_SECRET", "").strip()

    if not client_id or not client_secret:
        print("ERROR: GSC_CLIENT_ID or GSC_CLIENT_SECRET missing from .env")
        sys.exit(1)

    print(f"Exchanging code with Google OAuth token endpoint...")
    token_url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "http://localhost:8080/",
    }).encode("utf-8")

    req = urllib.request.Request(token_url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            token_data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="ignore")
        print(f"HTTPError {e.code}: {err}")
        sys.exit(1)
    except Exception as e:
        print(f"Exception: {e}")
        sys.exit(1)

    refresh_token = token_data.get("refresh_token")
    access_token = token_data.get("access_token")

    if not refresh_token:
        print("WARNING: No refresh_token returned in response.")
        print("Keys returned:", list(token_data.keys()))
        if "access_token" in token_data:
            print("Access token received successfully.")
    else:
        print(f"SUCCESS: Permanent refresh token obtained (length: {len(refresh_token)})!")

        # 1. Update .env
        new_lines = []
        found_ref = False
        for line in env_lines:
            if line.startswith("GSC_REFRESH_TOKEN="):
                new_lines.append(f"GSC_REFRESH_TOKEN={refresh_token}")
                found_ref = True
            else:
                new_lines.append(line)
        if not found_ref:
            new_lines.append(f"GSC_REFRESH_TOKEN={refresh_token}")
        env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print("Updated .env with GSC_REFRESH_TOKEN.")

        # 2. Update marketing_agent cache
        cache_path = Path("marketing_agent/data/gsc_token.json")
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(token_data, indent=2), encoding="utf-8")
        print("Updated marketing_agent/data/gsc_token.json cache.")

        # 3. Update GitHub Secrets
        try:
            subprocess.run(["gh", "secret", "set", "GSC_CLIENT_ID", "--body", client_id], check=True)
            subprocess.run(["gh", "secret", "set", "GSC_CLIENT_SECRET", "--body", client_secret], check=True)
            subprocess.run(["gh", "secret", "set", "GSC_REFRESH_TOKEN", "--body", refresh_token], check=True)
            print("Successfully updated GitHub Secrets: GSC_CLIENT_ID, GSC_CLIENT_SECRET, GSC_REFRESH_TOKEN!")
        except Exception as e:
            print(f"Notice: GitHub secret update via CLI: {e}")

    # 4. Verify Search Console API with the new access token
    if access_token:
        print("Verifying Search Console API access...")
        sc_req = urllib.request.Request(
            "https://www.googleapis.com/webmasters/v3/sites",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        try:
            with urllib.request.urlopen(sc_req, timeout=10) as sc_resp:
                sites = json.loads(sc_resp.read().decode("utf-8"))
                site_entries = sites.get("siteEntry", [])
                print(f"GSC Connected! Verified properties count: {len(site_entries)}")
                for s in site_entries:
                    print(f"  - {s.get('siteUrl')} (permissionLevel: {s.get('permissionLevel')})")
        except Exception as e:
            print(f"GSC Sites query notice: {e}")

if __name__ == "__main__":
    main()
