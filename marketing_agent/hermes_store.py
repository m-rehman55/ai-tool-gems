"""Persistent Hermes run and provenance storage."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .hermes_models import ConnectorResult, RunContext, utc_now


SCHEMA = """
CREATE TABLE IF NOT EXISTS hermes_runs (
  run_id TEXT PRIMARY KEY,
  mode TEXT NOT NULL,
  started_at TEXT NOT NULL,
  completed_at TEXT NOT NULL,
  status TEXT NOT NULL,
  report_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS hermes_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,
  metric TEXT NOT NULL,
  value_json TEXT NOT NULL,
  provenance_json TEXT NOT NULL,
  FOREIGN KEY(run_id) REFERENCES hermes_runs(run_id)
);
CREATE INDEX IF NOT EXISTS idx_hermes_records_run ON hermes_records(run_id);
"""


class HermesStore:
    def __init__(self, database_path: Path, snapshot_dir: Path) -> None:
        self.database_path = database_path
        self.snapshot_dir = snapshot_dir

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path)
        try:
            connection.executescript(SCHEMA)
            connection.commit()
        finally:
            connection.close()

    def save(self, context: RunContext, report: dict[str, Any], connectors: list[ConnectorResult]) -> Path:
        self.initialize()
        completed_at = utc_now()
        snapshot = dict(report)
        snapshot["run"] = {"run_id": context.run_id, "mode": context.mode, "repository": context.repository, "started_at": context.started_at, "completed_at": completed_at}
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        path = self.snapshot_dir / f"{context.run_id}.json"
        path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
        connection = sqlite3.connect(self.database_path)
        try:
            connection.execute("INSERT OR REPLACE INTO hermes_runs(run_id, mode, started_at, completed_at, status, report_json) VALUES(?,?,?,?,?,?)", (context.run_id, context.mode, context.started_at, completed_at, report.get("status", "COMPLETED"), json.dumps(snapshot, ensure_ascii=False)))
            connection.execute("DELETE FROM hermes_records WHERE run_id=?", (context.run_id,))
            for connector in connectors:
                for record in connector.records:
                    connection.execute("INSERT INTO hermes_records(run_id, metric, value_json, provenance_json) VALUES(?,?,?,?)", (context.run_id, record.metric, json.dumps(record.value, ensure_ascii=False), json.dumps(record.provenance.__dict__, ensure_ascii=False, default=str)))
            connection.commit()
        finally:
            connection.close()
        return path

    def latest(self) -> dict[str, Any] | None:
        if not self.database_path.exists():
            return None
        connection = sqlite3.connect(self.database_path)
        try:
            row = connection.execute("SELECT report_json FROM hermes_runs ORDER BY completed_at DESC LIMIT 1").fetchone()
        finally:
            connection.close()
        return json.loads(row[0]) if row else None
