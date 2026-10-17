"""
gsc_data.py - Google Search Console Data Ingestion, Export Parser & Historical Archive.
Supports dual data ingestion modes:
1. Live GSC API (OAuth2 via GSCClient) when authorized.
2. Manual CSV/TSV/JSON exports parser (graceful zero-dependency fallback).
Maintains historical datasets with consistent date conventions and retention limits.
"""

from __future__ import annotations

import csv
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("keyword_agent.gsc_data")


@dataclass
class GSCQueryRow:
    query: str
    clicks: int
    impressions: int
    ctr: float  # Percentage: 0.0 - 100.0
    position: float

    @property
    def is_striking_distance(self) -> bool:
        """Positions 4-15 represent prime striking-distance candidates."""
        return 4.0 <= self.position <= 15.0

    @property
    def is_low_ctr_opportunity(self) -> bool:
        """High impressions (>=5) with low CTR (<3.0%) indicate snippet mismatch."""
        return self.impressions >= 5 and self.ctr < 3.0


@dataclass
class GSCPageRow:
    page: str
    clicks: int
    impressions: int
    ctr: float
    position: float


@dataclass
class GSCCountryRow:
    country: str
    clicks: int
    impressions: int
    ctr: float
    position: float


@dataclass
class GSCDeviceRow:
    device: str
    clicks: int
    impressions: int
    ctr: float
    position: float


@dataclass
class GSCDateRow:
    date: str
    clicks: int
    impressions: int
    ctr: float
    position: float


@dataclass
class GSCDataset:
    source: str  # "API", "MANUAL_EXPORT", "NO_DATA"
    status_message: str
    queries: List[GSCQueryRow] = field(default_factory=list)
    pages: List[GSCPageRow] = field(default_factory=list)
    countries: List[GSCCountryRow] = field(default_factory=list)
    devices: List[GSCDeviceRow] = field(default_factory=list)
    dates: List[GSCDateRow] = field(default_factory=list)
    total_clicks: int = 0
    total_impressions: int = 0
    average_ctr: float = 0.0
    average_position: float = 0.0
    date_range: str = "Last 28 Days"
    retrieved_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "status_message": self.status_message,
            "total_clicks": self.total_clicks,
            "total_impressions": self.total_impressions,
            "average_ctr": self.average_ctr,
            "average_position": self.average_position,
            "date_range": self.date_range,
            "retrieved_at": self.retrieved_at,
            "queries_count": len(self.queries),
            "pages_count": len(self.pages),
            "countries_count": len(self.countries),
            "devices_count": len(self.devices),
            "queries": [asdict(q) for q in self.queries[:100]],
            "pages": [asdict(p) for p in self.pages[:50]],
        }


class GSCDataEngine:
    """Handles GSC data acquisition, parsing, and historical storage."""

    def __init__(
        self,
        exports_dir: Path,
        history_dir: Path,
        site_url: str = "https://aitoolgems.tech",
        auto_extract: bool = True,
    ):
        self.exports_dir = exports_dir
        self.history_dir = history_dir
        self.site_url = site_url
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        if auto_extract:
            self.auto_extract_from_downloads()

    def auto_extract_from_downloads(self) -> List[Path]:
        """Automatically checks standard download directories for new GSC ZIP exports and extracts them."""
        import zipfile
        extracted = []
        candidate_dirs = [
            Path(r"d:\Download"),
            Path.home() / "Downloads",
            Path(r"C:\Users\pc\Downloads"),
        ]
        for d in candidate_dirs:
            if not d.exists():
                continue
            for z in d.glob("*.zip"):
                z_name = z.name.lower()
                if "performance-on-search" in z_name or "aitoolgems" in z_name:
                    try:
                        with zipfile.ZipFile(z, "r") as zip_ref:
                            zip_ref.extractall(self.exports_dir)
                            extracted.append(z)
                            logger.info(f"Auto-extracted GSC export: {z.name}")
                    except Exception as e:
                        logger.warning(f"Failed auto-extracting {z}: {e}")
        return extracted

    @staticmethod
    def _parse_num(val: Any) -> float:
        """Parses integers, floats, and percentages cleanly."""
        if val is None:
            return 0.0
        s = str(val).strip().replace(",", "").replace("%", "")
        try:
            return float(s)
        except ValueError:
            return 0.0

    @staticmethod
    def _parse_ctr(val: Any) -> float:
        """Converts GSC CTR string (e.g. '4.5%' or 0.045) into standard 0.0-100.0 float."""
        if val is None:
            return 0.0
        s = str(val).strip().replace(",", "")
        if s.endswith("%"):
            try:
                return float(s[:-1].strip())
            except ValueError:
                return 0.0
        try:
            num = float(s)
            # If Google API returned decimal format (e.g. 0.045 instead of 4.5)
            if 0.0 < num <= 1.0:
                return round(num * 100.0, 2)
            return round(num, 2)
        except ValueError:
            return 0.0

    def parse_queries_csv(self, file_path: Path) -> List[GSCQueryRow]:
        """Parses a Search Console queries export CSV."""
        rows: List[GSCQueryRow] = []
        if not file_path.exists():
            return rows

        with open(file_path, mode="r", encoding="utf-8-sig", errors="ignore") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                return rows

            # Normalize column indexes
            col_map = {col.strip().lower(): idx for idx, col in enumerate(header)}
            q_idx = col_map.get("top queries") or col_map.get("query") or col_map.get("queries") or 0
            c_idx = col_map.get("clicks") or 1
            i_idx = col_map.get("impressions") or 2
            ctr_idx = col_map.get("ctr") or 3
            p_idx = col_map.get("position") or 4

            for row in reader:
                if not row or len(row) <= q_idx:
                    continue
                q_text = row[q_idx].strip()
                if not q_text:
                    continue
                clicks = int(self._parse_num(row[c_idx])) if len(row) > c_idx else 0
                impressions = int(self._parse_num(row[i_idx])) if len(row) > i_idx else 0
                ctr = self._parse_ctr(row[ctr_idx]) if len(row) > ctr_idx else 0.0
                position = self._parse_num(row[p_idx]) if len(row) > p_idx else 0.0

                rows.append(GSCQueryRow(
                    query=q_text,
                    clicks=clicks,
                    impressions=impressions,
                    ctr=ctr,
                    position=position,
                ))
        return rows

    def parse_pages_csv(self, file_path: Path) -> List[GSCPageRow]:
        """Parses a Search Console pages export CSV."""
        rows: List[GSCPageRow] = []
        if not file_path.exists():
            return rows

        with open(file_path, mode="r", encoding="utf-8-sig", errors="ignore") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                return rows

            col_map = {col.strip().lower(): idx for idx, col in enumerate(header)}
            p_idx = col_map.get("top pages") or col_map.get("page") or col_map.get("pages") or 0
            c_idx = col_map.get("clicks") or 1
            i_idx = col_map.get("impressions") or 2
            ctr_idx = col_map.get("ctr") or 3
            pos_idx = col_map.get("position") or 4

            for row in reader:
                if not row or len(row) <= p_idx:
                    continue
                page_text = row[p_idx].strip()
                if not page_text:
                    continue
                clicks = int(self._parse_num(row[c_idx])) if len(row) > c_idx else 0
                impressions = int(self._parse_num(row[i_idx])) if len(row) > i_idx else 0
                ctr = self._parse_ctr(row[ctr_idx]) if len(row) > ctr_idx else 0.0
                position = self._parse_num(row[pos_idx]) if len(row) > pos_idx else 0.0

                rows.append(GSCPageRow(
                    page=page_text,
                    clicks=clicks,
                    impressions=impressions,
                    ctr=ctr,
                    position=position,
                ))
        return rows

    def parse_countries_csv(self, file_path: Path) -> List[GSCCountryRow]:
        """Parses a Search Console countries export CSV."""
        rows: List[GSCCountryRow] = []
        if not file_path.exists():
            return rows

        with open(file_path, mode="r", encoding="utf-8-sig", errors="ignore") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                return rows

            col_map = {col.strip().lower(): idx for idx, col in enumerate(header)}
            k_idx = col_map.get("country") or col_map.get("top countries") or 0
            c_idx = col_map.get("clicks") or 1
            i_idx = col_map.get("impressions") or 2
            ctr_idx = col_map.get("ctr") or 3
            p_idx = col_map.get("position") or 4

            for row in reader:
                if not row or len(row) <= k_idx:
                    continue
                c_text = row[k_idx].strip()
                if not c_text:
                    continue
                clicks = int(self._parse_num(row[c_idx])) if len(row) > c_idx else 0
                impressions = int(self._parse_num(row[i_idx])) if len(row) > i_idx else 0
                ctr = self._parse_ctr(row[ctr_idx]) if len(row) > ctr_idx else 0.0
                position = self._parse_num(row[p_idx]) if len(row) > p_idx else 0.0

                rows.append(GSCCountryRow(
                    country=c_text,
                    clicks=clicks,
                    impressions=impressions,
                    ctr=ctr,
                    position=position,
                ))
        return rows

    def parse_devices_csv(self, file_path: Path) -> List[GSCDeviceRow]:
        """Parses a Search Console devices export CSV."""
        rows: List[GSCDeviceRow] = []
        if not file_path.exists():
            return rows

        with open(file_path, mode="r", encoding="utf-8-sig", errors="ignore") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                return rows

            col_map = {col.strip().lower(): idx for idx, col in enumerate(header)}
            d_idx = col_map.get("device") or col_map.get("top devices") or 0
            c_idx = col_map.get("clicks") or 1
            i_idx = col_map.get("impressions") or 2
            ctr_idx = col_map.get("ctr") or 3
            p_idx = col_map.get("position") or 4

            for row in reader:
                if not row or len(row) <= d_idx:
                    continue
                dev_text = row[d_idx].strip()
                if not dev_text:
                    continue
                clicks = int(self._parse_num(row[c_idx])) if len(row) > c_idx else 0
                impressions = int(self._parse_num(row[i_idx])) if len(row) > i_idx else 0
                ctr = self._parse_ctr(row[ctr_idx]) if len(row) > ctr_idx else 0.0
                position = self._parse_num(row[p_idx]) if len(row) > p_idx else 0.0

                rows.append(GSCDeviceRow(
                    device=dev_text,
                    clicks=clicks,
                    impressions=impressions,
                    ctr=ctr,
                    position=position,
                ))
        return rows

    def load_dataset(self) -> GSCDataset:
        """
        Discovers and loads GSC data from:
        1. Local manual export CSVs in `exports_dir`
        2. Previous snapshots in `history_dir`
        3. Returns explicit 'NO_DATA' status if none available, without fabricating numbers.
        """
        queries: List[GSCQueryRow] = []
        pages: List[GSCPageRow] = []
        countries: List[GSCCountryRow] = []
        devices: List[GSCDeviceRow] = []
        dates: List[GSCDateRow] = []

        # Find matching CSVs in exports_dir
        for p in self.exports_dir.glob("*.csv"):
            name = p.name.lower()
            if "quer" in name:
                queries.extend(self.parse_queries_csv(p))
            elif "page" in name:
                pages.extend(self.parse_pages_csv(p))
            elif "countr" in name:
                countries.extend(self.parse_countries_csv(p))
            elif "devic" in name:
                devices.extend(self.parse_devices_csv(p))

        # Check for JSON export
        for p in self.exports_dir.glob("*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    for item in data:
                        if "query" in item:
                            queries.append(GSCQueryRow(
                                query=item["query"],
                                clicks=int(item.get("clicks", 0)),
                                impressions=int(item.get("impressions", 0)),
                                ctr=self._parse_ctr(item.get("ctr", 0)),
                                position=self._parse_num(item.get("position", 0)),
                            ))
            except Exception as e:
                logger.warning(f"Failed parsing JSON export {p}: {e}")

        if queries or pages:
            # Google Search Console anonymizes query-level rows for low-volume queries,
            # while Pages, Devices, and Countries reflect full un-anonymized aggregate clicks.
            page_clicks = sum(p.clicks for p in pages)
            query_clicks = sum(q.clicks for q in queries)
            page_imp = sum(p.impressions for p in pages)
            query_imp = sum(q.impressions for q in queries)

            tot_clicks = max(page_clicks, query_clicks)
            tot_imp = max(page_imp, query_imp)
            avg_ctr = round((tot_clicks / tot_imp * 100.0), 2) if tot_imp > 0 else 0.0
            avg_pos = round(sum(q.position for q in queries) / len(queries), 1) if queries else (round(sum(p.position for p in pages) / len(pages), 1) if pages else 0.0)

            dataset = GSCDataset(
                source="MANUAL_EXPORT",
                status_message=f"Loaded {len(queries)} queries and {len(pages)} pages from manual GSC exports.",
                queries=queries,
                pages=pages,
                countries=countries,
                devices=devices,
                dates=dates,
                total_clicks=tot_clicks,
                total_impressions=tot_imp,
                average_ctr=avg_ctr,
                average_position=avg_pos,
            )
            self.save_historical_snapshot(dataset)
            return dataset

        # Check latest historical snapshot
        latest_snapshot = self.get_latest_historical_snapshot()
        if latest_snapshot:
            return latest_snapshot

        # Truly no data available
        return GSCDataset(
            source="NO_DATA",
            status_message=(
                "Google Search Console data unavailable (OAuth token expired / no CSV exports found). "
                "Place Search Console CSV exports into data/gsc_exports/ or re-authenticate."
            ),
        )

    def save_historical_snapshot(self, dataset: GSCDataset) -> Path:
        """Saves daily historical snapshot with retention management."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        snapshot_file = self.history_dir / f"gsc_snapshot_{today}.json"
        snapshot_file.write_text(json.dumps(dataset.to_dict(), indent=2), encoding="utf-8")
        self._prune_snapshots(max_keep=90)
        return snapshot_file

    def get_latest_historical_snapshot(self) -> Optional[GSCDataset]:
        """Loads the most recent saved historical snapshot."""
        snapshots = sorted(self.history_dir.glob("gsc_snapshot_*.json"), reverse=True)
        if not snapshots:
            return None
        try:
            data = json.loads(snapshots[0].read_text(encoding="utf-8"))
            queries = [
                GSCQueryRow(
                    query=q["query"],
                    clicks=q["clicks"],
                    impressions=q["impressions"],
                    ctr=q["ctr"],
                    position=q["position"],
                )
                for q in data.get("queries", [])
            ]
            pages = [
                GSCPageRow(
                    page=p["page"],
                    clicks=p["clicks"],
                    impressions=p["impressions"],
                    ctr=p["ctr"],
                    position=p["position"],
                )
                for p in data.get("pages", [])
            ]
            return GSCDataset(
                source="HISTORICAL_SNAPSHOT",
                status_message=f"Restored from historical snapshot {snapshots[0].name}",
                queries=queries,
                pages=pages,
                total_clicks=data.get("total_clicks", 0),
                total_impressions=data.get("total_impressions", 0),
                average_ctr=data.get("average_ctr", 0.0),
                average_position=data.get("average_position", 0.0),
                retrieved_at=data.get("retrieved_at", ""),
            )
        except Exception as e:
            logger.error(f"Failed to read snapshot {snapshots[0]}: {e}")
            return None

    def _prune_snapshots(self, max_keep: int = 90):
        """Retains up to 90 historical snapshots (~3 months), removing older ones."""
        snapshots = sorted(self.history_dir.glob("gsc_snapshot_*.json"), reverse=True)
        for s in snapshots[max_keep:]:
            try:
                s.unlink()
            except OSError:
                pass

    @staticmethod
    def get_manual_setup_instructions() -> str:
        """Returns step-by-step instructions to export GSC CSV data for free offline analysis."""
        return """### 📥 How to Import Google Search Console Data into AI Tool Gems
1. **Open Google Search Console**: Visit [https://search.google.com/search-console](https://search.google.com/search-console).
2. **Select Property**: Choose `sc-domain:aitoolgems.tech` or `https://aitoolgems.tech`.
3. **Open Performance Report**: Click **Performance** -> **Search results** in the left sidebar.
4. **Set Time Range**: Select **Date: Last 28 days** (or compare previous period).
5. **Download Export**: Click **Export** in the top right corner and choose **Download CSV**.
6. **Place in Project**: Extract the downloaded ZIP file and copy:
   - `Queries.csv`
   - `Pages.csv`
   - `Countries.csv`
   - `Devices.csv`
   into the project directory: `data/gsc_exports/`
7. **Run Analysis**: Execute `python -m keyword_agent gsc-analyze`.
The agent will automatically ingest, parse, segment, and cross-reference these queries against site URLs!
"""
