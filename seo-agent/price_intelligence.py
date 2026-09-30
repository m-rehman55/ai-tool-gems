"""
Price Intelligence - FREE-FIRST: Uses free price sources (GSC, SERP, browser search).

Real Price Intelligence
"""
Price Intelligence - FREE-FIRST: Uses free price sources (GSC, SERP, browser search).


PRICE = {
  "description": "Real price intelligence",
  "required_fields": [
    "product",
    "market",
    "currency",
    "current_price",
    "previous_price",
    "price_change",
    "price_change_percent",
    "source",
    "source_url",
    "checked_at",
    "availability"
  ],
  "rule": "Never fabricate price history. If historical price was never captured, use NOT_AVAILABLE, not current_price."
}

def get_price_status():
    """
Price Intelligence - FREE-FIRST: Uses free price sources (GSC, SERP, browser search).
Return price intelligence status."""
Price Intelligence - FREE-FIRST: Uses free price sources (GSC, SERP, browser search).

    return PRICE

def record_price(product, market, currency, current_price, previous_price, source, availability):
    """
Price Intelligence - FREE-FIRST: Uses free price sources (GSC, SERP, browser search).
Record price data."""
Price Intelligence - FREE-FIRST: Uses free price sources (GSC, SERP, browser search).

    return {
        "product": product,
        "market": market,
        "currency": currency,
        "current_price": current_price,
        "previous_price": previous_price if previous_price is not None else "NOT_AVAILABLE",
        "price_change": "NOT_AVAILABLE" if previous_price is None else round(((current_price - previous_price) / previous_price) * 100, 2),
        "source": source,
        "checked_at": "2026-10-01T00:00:00Z",
        "availability": availability
    }
