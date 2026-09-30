"""
Telegram Real-Data Reporting - FREE-FIRST: Uses free data sources only.

Telegram Real-Data Reporting
"""
Telegram Real-Data Reporting - FREE-FIRST: Uses free data sources only.


TELEGRAM_REAL = {
  "description": "Telegram real-data reporting",
  "distinguish": [
    "VERIFIED DATA",
    "NO DATA",
    "ACCESS_REQUIRED",
    "NOT_AVAILABLE",
    "FAILED"
  ],
  "rule": "Never show ranking_changes = 0 when ranking data was simply unavailable. Instead use ranking_changes = NOT_AVAILABLE with reason."
}

def get_telegram_real_status():
    """
Telegram Real-Data Reporting - FREE-FIRST: Uses free data sources only.
Return Telegram real-data reporting status."""
Telegram Real-Data Reporting - FREE-FIRST: Uses free data sources only.

    return TELEGRAM_REAL

def format_telegram_report(data, source_status):
    """
Telegram Real-Data Reporting - FREE-FIRST: Uses free data sources only.
Format Telegram report with real-data distinctions."""
Telegram Real-Data Reporting - FREE-FIRST: Uses free data sources only.

    return {
        "data": data,
        "source_status": source_status,
        "note": "Distinguish VERIFIED DATA from NOT_AVAILABLE"
    }
