"""Telegram message utilities, Unicode-aware chunking, and token sanitization."""

from __future__ import annotations

import re
from typing import List


def split_message_into_chunks(text: str, max_chars: int = 3800) -> List[str]:
    """Splits long text into ordered, safe chunks respecting paragraph/line boundaries.

    Ensures no chunk exceeds max_chars (below Telegram's 4096 limit) and Unicode is preserved.
    """
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    chunks: List[str] = []
    paragraphs = text.split("\n\n")
    current_chunk = ""

    for para in paragraphs:
        if len(para) > max_chars:
            lines = para.split("\n")
            for line in lines:
                if len(line) > max_chars:
                    for i in range(0, len(line), max_chars):
                        sub = line[i : i + max_chars]
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = ""
                        chunks.append(sub)
                else:
                    test_chunk = f"{current_chunk}\n{line}" if current_chunk else line
                    if len(test_chunk) <= max_chars:
                        current_chunk = test_chunk
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = line
        else:
            test_chunk = f"{current_chunk}\n\n{para}" if current_chunk else para
            if len(test_chunk) <= max_chars:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para

    if current_chunk and current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks or [text]


def redact_bot_token(text: str, token: str) -> str:
    """Replaces sensitive bot token with [REDACTED_TOKEN] in error messages and logs."""
    if token and token in text:
        return text.replace(token, "[REDACTED_TOKEN]")
    # Also catch general bot token patterns like bot123456:ABC-DEF
    return re.sub(r"bot\d+:[a-zA-Z0-9_-]+", "bot[REDACTED_TOKEN]", text)
