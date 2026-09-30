"""
Telegram Report Structure - FREE-FIRST: Uses free data sources only.

Telegram Report Structure
"""
Telegram Report Structure - FREE-FIRST: Uses free data sources only.


TELEGRAM_STRUCTURE = {
  "description": "Telegram report structure",
  "sections": [
    "Executive Summary",
    "Google Search Console",
    "Google Analytics",
    "SERP",
    "Competitors",
    "Technical SEO",
    "Content",
    "Authority",
    "Actions",
    "Data Health"
  ],
  "data_health": [
    "GSC",
    "GA4",
    "SERP",
    "Keyword Provider",
    "Backlink Provider",
    "Trends"
  ],
  "statuses": [
    "CONNECTED",
    "ACCESS_REQUIRED",
    "ERROR",
    "PARTIAL"
  ]
}

def get_telegram_structure_status():
    """
Telegram Report Structure - FREE-FIRST: Uses free data sources only.
Return Telegram structure status."""
Telegram Report Structure - FREE-FIRST: Uses free data sources only.

    return TELEGRAM_STRUCTURE

def generate_report(section, data):
    """
Telegram Report Structure - FREE-FIRST: Uses free data sources only.
Generate a Telegram report section."""
Telegram Report Structure - FREE-FIRST: Uses free data sources only.

    return {"section": section, "data": data, "status": "generated"}
