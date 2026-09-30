"""
Real Page Performance
"""

PERFORMANCE = {
  "description": "Real page performance",
  "status": "PARTIAL",
  "measure": [
    "HTTP status",
    "TTFB",
    "HTML size",
    "JS size",
    "CSS size",
    "image size",
    "compression",
    "caching",
    "Core Web Vitals",
    "mobile/desktop performance"
  ],
  "rule": "Do not invent PageSpeed scores. Store actual test timestamp."
}

def get_performance_status():
    """Return performance status."""
    return PERFORMANCE

def record_performance(url, http_status, html_size, js_size, css_size, image_size):
    """Record performance data."""
    return {
        "url": url,
        "HTTP status": http_status,
        "HTML size": html_size,
        "JS size": js_size,
        "CSS size": css_size,
        "image size": image_size,
        "test_timestamp": "2026-10-01T00:00:00Z"
    }
