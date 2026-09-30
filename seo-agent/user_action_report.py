"""
User Action Report - FREE-FIRST: Uses free data sources only.
User Action Report
"""

USER_ACTION_REPORT = {
  "description": "User action report",
  "required_from_user": [
    "TELEGRAM_BOT_TOKEN from @BotFather",
    "TELEGRAM_CHAT_ID from Telegram",
    "Google Search Console access",
    "Google Analytics access (G- ID)"
  ],
  "optional": [
    "Bing Webmaster access",
    "Ahrefs free account",
    "Moz free account",
    "SEOBench free account"
  ]
}

def get_user_action_status():
    """Return user action status."""
    return USER_ACTION_REPORT
