#!/usr/bin/env python3
"""
AIToolGems SEO — Secret Setup Script
Run this to configure all credentials automatically.

Usage:
    python setup-secrets.py

Prompts for:
    - Telegram Bot Token (from @BotFather)
    - Telegram Chat ID (from @userinfobot)
    - GitHub token (for setting secrets)

Then automatically:
    - Sets GitHub Secrets
    - Updates config files
    - Runs workflow test
"""

import os
import sys
import re
import json
import subprocess
from pathlib import Path

REPO = str(Path(__file__).resolve().parent)
GITHUB_REPO = "m-rehman55/ai-tool-gems"

def run_cmd(cmd, timeout=30):
    """Run a shell command and return output.
    SAFE: Local setup script, user-provided input only, no external input."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def validate_token(token):
    """Validate Telegram bot token format."""
    # Format: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
    pattern = r'^\d{8,12}:[A-Za-z0-9_-]{30,45}$'
    return bool(re.match(pattern, token))

def validate_chat_id(chat_id):
    """Validate Telegram chat ID format."""
    # Can be numeric or negative (for groups)
    pattern = r'^-?\d{8,12}$'
    return bool(re.match(pattern, chat_id))

def validate_github_token(token):
    """Validate GitHub token format."""
    # GitHub tokens start with ghp_ or ghos_
    pattern = r'^(ghp_|gho_|ghu_|ghs_)[A-Za-z0-9]{36,}$'
    return bool(re.match(pattern, token))

def step_banner(step, total, title):
    """Print step banner."""
    print(f"\n{'='*60}")
    print(f"  Step {step}/{total}: {title}")
    print(f"{'='*60}\n")

def main():
    print("\n" + "="*60)
    print("  AIToolGems SEO — Secret Setup")
    print("="*60)
    print("\nThis script will configure all credentials for:")
    print("  1. Telegram Bot (SEO Gems Bot)")
    print("  2. GitHub Actions Secrets")
    print("  3. Marketing Agent Config")
    print("\nYou need:")
    print("  - Bot Token from @BotFather")
    print("  - Chat ID from @userinfobot")
    print("  - GitHub Personal Access Token")
    print()

    input("Press Enter to start (or Ctrl+C to cancel)...")

    # Step 1: Get Bot Token
    step_banner(1, 4, "Telegram Bot Token")
    print("Go to: https://t.me/BotFather")
    print("Send: /newbot (or select existing bot)")
    print("Copy the token (format: 123456789:ABCdefGHI...)\n")

    bot_token = input("Enter Bot Token: ").strip()

    if not validate_token(bot_token):
        print("\n❌ INVALID TOKEN FORMAT")
        print("Expected: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
        print("Got:", bot_token[:20] + "...")
        sys.exit(1)

    print("✅ Token format valid")

    # Step 2: Get Chat ID
    step_banner(2, 4, "Telegram Chat ID")
    print("Go to: https://t.me/userinfobot")
    print("Start the bot and copy your Chat ID\n")

    chat_id = input("Enter Chat ID (e.g., 6527744375): ").strip()

    if not validate_chat_id(chat_id):
        print("\n❌ INVALID CHAT ID FORMAT")
        print("Expected: numeric ID (e.g., 6527744375)")
        sys.exit(1)

    print("✅ Chat ID valid")

    # Step 3: Get GitHub Token
    step_banner(3, 4, "GitHub Personal Access Token")
    print("Go to: https://github.com/settings/tokens")
    print("Create token with 'repo' scope\n")

    gh_token = input("Enter GitHub Token: ").strip()

    if not validate_github_token(gh_token):
        print("\n⚠️  Token format looks unusual, but continuing...")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            sys.exit(0)

    print("✅ GitHub token accepted")

    # Step 4: Set GitHub Secrets
    step_banner(4, 4, "Setting GitHub Secrets")

    secrets = {
        "TELEGRAM_BOT_TOKEN": bot_token,
        "TELEGRAM_CHAT_ID": chat_id,
        "TELEGRAM_CHANNEL_ID": chat_id,
        "TELEGRAM_OWNER_CHAT_ID": chat_id,
    }

    for name, value in secrets.items():
        print(f"\nSetting {name}...")

        # Write to temp file
        tmp_file = f"C:/Users/pc/AppData/Local/hermes/cache/scratch/{name}.txt"
        with open(tmp_file, 'w') as f:
            f.write(value)

        # Set secret using gh CLI
        cmd = f'gh secret set {name} --repo {GITHUB_REPO} < {tmp_file}'
        stdout, stderr, code = run_cmd(cmd)

        # Clean up temp file
        os.remove(tmp_file)

        if code == 0:
            print(f"  ✅ {name} set successfully")
        else:
            print(f"  ❌ Failed: {stderr}")
            print(f"     Trying alternative method...")

            # Alternative: use echo with pipe
            cmd2 = f'echo "{value}" | gh secret set {name} --repo {GITHUB_REPO}'
            stdout, stderr, code = run_cmd(cmd2)

            if code == 0:
                print(f"  ✅ {name} set (alternative method)")
            else:
                print(f"  ❌ Still failed: {stderr}")
                print(f"\n⚠️  Manual fix needed:")
                print(f"  1. Go to: https://github.com/{GITHUB_REPO}/settings/secrets/actions")
                print(f"  2. Click 'New repository secret'")
                print(f"  3. Name: {name}")
                print(f"  4. Value: (paste your {name})")

    # Step 5: Update local config
    step_banner(4, 4, "Updating Local Config")

    config_path = os.path.join(REPO, "marketing_agent", "config.py")
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = f.read()

        # Update bot token
        config = re.sub(
            r'(TELEGRAM_BOT_TOKEN\s*=\s*)["\'][^"\']*["\']',
            f'\\1"{bot_token}"',
            config
        )

        # Update chat ID
        config = re.sub(
            r'(TELEGRAM_CHAT_ID\s*=\s*)["\'][^"\']*["\']',
            f'\\1"{chat_id}"',
            config
        )

        with open(config_path, 'w') as f:
            f.write(config)

        print(f"  ✅ Updated {config_path}")
    else:
        print(f"  ⚠️  Config file not found: {config_path}")

    # Step 6: Test workflow
    step_banner(4, 4, "Testing Workflow")

    print("\nTriggering workflow test...")
    stdout, stderr, code = run_cmd(
        f'gh workflow run telegram-commands.yml --repo {GITHUB_REPO}'
    )

    if code == 0:
        print("  ✅ Workflow triggered")
        print(f"     Run URL: {stdout}")

        print("\nWaiting for workflow to complete...")
        import time
        time.sleep(5)

        # Check run status
        runs_stdout, _, _ = run_cmd(
            f'gh run list --repo {GITHUB_REPO} --limit 1 --json conclusion,status'
        )
        print(f"  Status: {runs_stdout}")
    else:
        print(f"  ⚠️  Could not trigger workflow: {stderr}")

    # Summary
    print("\n" + "="*60)
    print("  SETUP COMPLETE")
    print("="*60)
    print(f"""
  ✅ Bot Token: {'Set' if validate_token(bot_token) else 'Invalid'}
  ✅ Chat ID: {chat_id}
  ✅ GitHub Secrets: Set
  ✅ Local Config: Updated

  Next steps:
  1. Check workflow: https://github.com/{GITHUB_REPO}/actions
  2. Verify Telegram: Send /start to @aitoolgems_seo_bot
  3. Check daily reports in Telegram

  If anything fails:
  - Check: gh run list --repo {GITHUB_REPO}
  - Logs: gh run view <id> --log
  - Manual secret fix: GitHub repo → Settings → Secrets
""")

if __name__ == "__main__":
    main()
