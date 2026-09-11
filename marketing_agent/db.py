"""SQLite persistence and migrations for the marketing agent."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from .catalog import Product, load_products


SCHEMA_VERSION = 1

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS schema_meta (
  version INTEGER NOT NULL,
  applied_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS products (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  price INTEGER NOT NULL,
  old_price INTEGER NOT NULL,
  duration TEXT NOT NULL,
  access TEXT NOT NULL,
  delivery TEXT NOT NULL,
  warranty TEXT NOT NULL,
  active INTEGER NOT NULL DEFAULT 1,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id TEXT NOT NULL REFERENCES products(id),
  platform TEXT NOT NULL DEFAULT 'telegram',
  segment TEXT NOT NULL,
  angle TEXT NOT NULL,
  variant TEXT NOT NULL,
  caption TEXT NOT NULL,
  caption_hash TEXT NOT NULL,
  tracking_code TEXT NOT NULL UNIQUE,
  target_url TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('draft','approved','scheduled','published','failed','skipped')),
  scheduled_at TEXT NOT NULL,
  published_at TEXT,
  platform_message_id TEXT,
  error TEXT,
  created_at TEXT NOT NULL,
  UNIQUE(platform, caption_hash)
);
CREATE INDEX IF NOT EXISTS idx_posts_due ON posts(status, scheduled_at);
CREATE INDEX IF NOT EXISTS idx_posts_product ON posts(product_id, created_at);
CREATE TABLE IF NOT EXISTS metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER REFERENCES posts(id),
  captured_at TEXT NOT NULL,
  impressions INTEGER NOT NULL DEFAULT 0,
  clicks INTEGER NOT NULL DEFAULT 0,
  orders INTEGER NOT NULL DEFAULT 0,
  revenue INTEGER NOT NULL DEFAULT 0,
  reactions INTEGER NOT NULL DEFAULT 0,
  forwards INTEGER NOT NULL DEFAULT 0,
  subscriber_count INTEGER,
  source TEXT NOT NULL DEFAULT 'manual'
);
CREATE INDEX IF NOT EXISTS idx_metrics_post ON metrics(post_id, captured_at);
CREATE TABLE IF NOT EXISTS learning_rules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  rule_key TEXT NOT NULL UNIQUE,
  rule_value TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 0,
  evidence_count INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reports (
  report_date TEXT PRIMARY KEY,
  body TEXT NOT NULL,
  sent_at TEXT,
  created_at TEXT NOT NULL
);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def connect(path: Path) -> Iterator[sqlite3.Connection]:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _upsert_product(connection: sqlite3.Connection, product: Product) -> None:
    connection.execute(
        """
        INSERT INTO products(id,name,category,price,old_price,duration,access,delivery,warranty,updated_at)
        VALUES(?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
          name=excluded.name, category=excluded.category, price=excluded.price,
          old_price=excluded.old_price, duration=excluded.duration,
          access=excluded.access, delivery=excluded.delivery,
          warranty=excluded.warranty, active=1, updated_at=excluded.updated_at
        """,
        (product.id, product.name, product.category, product.price, product.old_price,
         product.duration, product.access, product.delivery, product.warranty, utc_now()),
    )


def initialize(path: Path) -> None:
    with connect(path) as connection:
        connection.executescript(SCHEMA)
        current = connection.execute("SELECT MAX(version) FROM schema_meta").fetchone()[0]
        if current is None:
            connection.execute(
                "INSERT INTO schema_meta(version, applied_at) VALUES(?, ?)",
                (SCHEMA_VERSION, utc_now()),
            )
        elif current != SCHEMA_VERSION:
            raise RuntimeError(f"Unsupported database schema {current}; expected {SCHEMA_VERSION}")
        for product in load_products():
            _upsert_product(connection, product)


def database_status(path: Path) -> dict[str, int]:
    with connect(path) as connection:
        result = {"products": connection.execute("SELECT COUNT(*) FROM products WHERE active=1").fetchone()[0]}
        for status in ("draft", "approved", "scheduled", "published", "failed"):
            result[status] = connection.execute("SELECT COUNT(*) FROM posts WHERE status=?", (status,)).fetchone()[0]
        result["metrics"] = connection.execute("SELECT COUNT(*) FROM metrics").fetchone()[0]
        return result
