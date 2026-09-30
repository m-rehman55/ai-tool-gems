"""
Paid Services Out of Scope - FREE-FIRST: Uses free data sources only.
Paid Services Out of Scope
"""

PAID_SERVICES = {
  "description": "Paid services out of scope",
  "out_of_scope": [
    "Ahrefs paid",
    "SEMrush",
    "Moz Pro",
    "SEObench paid",
    "Screaming Frog paid",
    "Ahrefs Webmaster",
    "Majestic paid"
  ],
  "rule": "Paid services are out of scope unless user provides access."
}

def get_paid_services_status():
    """Return paid services status."""
    return PAID_SERVICES
