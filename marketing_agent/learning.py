"""Explainable, conservative learning rules for organic content."""

from __future__ import annotations

import json

from .config import Settings
from .db import connect, utc_now


MIN_POSTS_PER_GROUP = 3


def _score(row) -> float:
    # Orders dominate, then tracked clicks, then light engagement.
    return float(row["orders"] * 50 + row["clicks"] * 4 + row["reactions"] * 2 + row["forwards"] * 3)


def learn(settings: Settings) -> list[dict[str, object]]:
    with connect(settings.database_path) as connection:
        rows = connection.execute(
            """
            SELECT p.product_id, p.angle, p.variant, COUNT(DISTINCT p.id) AS posts,
              COALESCE(SUM(m.clicks),0) AS clicks, COALESCE(SUM(m.orders),0) AS orders,
              COALESCE(SUM(m.revenue),0) AS revenue, COALESCE(SUM(m.reactions),0) AS reactions,
              COALESCE(SUM(m.forwards),0) AS forwards
            FROM posts p LEFT JOIN metrics m ON m.post_id=p.id
            WHERE p.status='published'
            GROUP BY p.product_id, p.angle, p.variant
            HAVING COUNT(DISTINCT p.id) >= ?
            """,
            (MIN_POSTS_PER_GROUP,),
        ).fetchall()
        ranked = sorted((dict(row) | {"score": _score(row)} for row in rows), key=lambda row: row["score"], reverse=True)
        rules: list[dict[str, object]] = []
        for index, row in enumerate(ranked[:5]):
            confidence = min(0.95, 0.45 + row["posts"] * 0.05)
            key = f"winner:{row['product_id']}:{row['angle']}:{row['variant']}"
            value = {
                "rank": index + 1, "score": row["score"], "clicks": row["clicks"],
                "orders": row["orders"], "revenue": row["revenue"],
                "recommendation": "reuse this angle once more next week; keep the frequency cap",
            }
            connection.execute(
                """
                INSERT INTO learning_rules(rule_key,rule_value,confidence,evidence_count,updated_at)
                VALUES(?,?,?,?,?)
                ON CONFLICT(rule_key) DO UPDATE SET rule_value=excluded.rule_value,
                  confidence=excluded.confidence,evidence_count=excluded.evidence_count,updated_at=excluded.updated_at
                """,
                (key, json.dumps(value, separators=(",", ":")), confidence, row["posts"], utc_now()),
            )
            rules.append({"key": key, "confidence": confidence, "evidence_count": row["posts"], **value})
        return rules


def recommendations(settings: Settings) -> list[dict[str, object]]:
    with connect(settings.database_path) as connection:
        return [
            {"key": row["rule_key"], "value": json.loads(row["rule_value"]),
             "confidence": row["confidence"], "evidence_count": row["evidence_count"]}
            for row in connection.execute("SELECT * FROM learning_rules ORDER BY confidence DESC, evidence_count DESC")
        ]
