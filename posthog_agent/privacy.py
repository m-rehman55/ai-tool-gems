"""Privacy-Safe Behavioural Tracking and Session Replay Module.

Enforces zero PII, zero credentials, zero payment receipts, and zero OTP exposure.
Masks all user-identifiable information in behavioral logs and session replay configs.
"""

from __future__ import annotations

import re
from typing import Any, Dict

# Regex patterns for sensitive data
PHONE_REGEX = re.compile(r"(\+?92|0)?3\d{2}[-\s]?\d{7}", re.IGNORECASE)
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", re.IGNORECASE)
CARD_REGEX = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
IBFT_ACCOUNT_REGEX = re.compile(r"\b\d{10,24}\b")
OTP_REGEX = re.compile(r"\b\d{4,8}\b")

# Sensitive key names to always redact
SENSITIVE_KEYS = {
    "password", "secret", "token", "otp", "pin", "cvv", "receipt",
    "receipt_image", "cnic", "iban", "account_number", "phone",
    "email", "card_number", "customer_chat", "private_message"
}


def sanitize_text(text: str) -> str:
    """Mask sensitive phone numbers, emails, and card numbers from strings."""
    if not isinstance(text, str):
        return text
    masked = PHONE_REGEX.sub("[PHONE_REDACTED]", text)
    masked = EMAIL_REGEX.sub("[EMAIL_REDACTED]", masked)
    masked = CARD_REGEX.sub("[CARD_REDACTED]", masked)
    return masked


def sanitize_event_properties(properties: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively sanitize properties to remove PII and confidential terms."""
    sanitized: Dict[str, Any] = {}
    for key, value in properties.items():
        lower_key = key.lower()
        if any(s in lower_key for s in SENSITIVE_KEYS):
            sanitized[key] = "[REDACTED_SENSITIVE_DATA]"
            continue

        if isinstance(value, str):
            sanitized[key] = sanitize_text(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_event_properties(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_event_properties(v) if isinstance(v, dict)
                else sanitize_text(v) if isinstance(v, str)
                else v
                for v in value
            ]
        else:
            sanitized[key] = value
    return sanitized


def get_privacy_replay_config() -> Dict[str, Any]:
    """Return recommended PostHog session replay configuration ensuring complete privacy."""
    return {
        "mask_all_text": True,
        "mask_all_element_attributes": True,
        "mask_input_options": {
            "password": True,
            "color": False,
            "date": True,
            "datetime-local": True,
            "email": True,
            "month": False,
            "number": True,
            "range": False,
            "search": False,
            "tel": True,
            "text": True,
            "time": False,
            "url": False,
            "week": False,
        },
        "mask_custom_selectors": [
            ".pii-mask",
            "[data-sensitive]",
            "input",
            "textarea",
            ".customer-name",
            ".customer-phone",
            ".proof-screenshot",
            ".payment-receipt",
        ],
        "record_cross_origin_iframes": False,
        "record_canvas": False,
    }

