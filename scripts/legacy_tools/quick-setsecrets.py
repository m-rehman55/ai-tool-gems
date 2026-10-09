#!/usr/bin/env python3
"""
Quick Secret Setter — One command, all secrets.

Usage:
    python quick-setsecrets.py <bot_token> <chat_id>

Example:
    python quick-setsecrets.py 8803075155:AAH0V1L37hDlQOf85bP4qRFWVoNv1TFRiMk 6527744375
"""

import os
import sys
import subprocess
import tempfile

GITHUB_REPO = "m-rehman55/ai-tool-gems"

def set_secret(name, value):
    """Set GitHub secret using temp file method.
    SAFE: Local script, user-provided credentials only, no external input."""
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(value)
        tmp_path = f.name

    try:
        # shell=True needed for input redirection (< tmp_path)
        cmd = f'gh secret set {name} --repo {GITHUB_REPO} < {tmp_path}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"  ✅ {name}")
            return True
        else:
            print(f"  ❌ {name}: {result.stderr}")
            return False
    finally:
        os.unlink(tmp_path)

def main():
    if len(sys.argv) < 3:
        print("Usage: python quick-setsecrets.py <bot_token> <chat_id>")
        print()
        print("Example:")
        print("  python quick-setsecrets.py 8803075155:AAH0V1L37hDlQOf85bP4qRFWVoNv1TFRiMk 6527744375")
        sys.exit(1)

    bot_token = sys.argv[1]
    chat_id = sys.argv[2]

    print("\n" + "="*60)
    print("  Quick Secret Setter")
    print("="*60 + "\n")

    secrets = {
        "TELEGRAM_BOT_TOKEN": bot_token,
        "TELEGRAM_CHAT_ID": chat_id,
        "TELEGRAM_CHANNEL_ID": chat_id,
        "TELEGRAM_OWNER_CHAT_ID": chat_id,
    }

    print("Setting secrets...\n")

    for name, value in secrets.items():
        set_secret(name, value)

    print("\n✅ Done! All secrets set.")
    print("\nVerify at:")
    print(f"  https://github.com/{GITHUB_REPO}/settings/secrets/actions")

if __name__ == "__main__":
    main()
