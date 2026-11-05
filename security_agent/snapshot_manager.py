"""
security_agent.snapshot_manager - Creates and manages atomic rollback snapshots with SHA-256 manifests.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
from typing import Dict, List, Any, Optional


@dataclass
class SnapshotManifest:
    snapshot_id: str
    created_at: str
    files_count: int
    files_checksums: Dict[str, str] = field(default_factory=dict)
    snapshot_dir: str = ""


class SnapshotManager:
    """
    Manages safe rollback snapshots for HERMES operating system before risky deployments.
    """

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent
        self.snapshots_dir = self.repo_root / "data" / "snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def _sha256(self, path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    def create_snapshot(self, paths_to_include: Optional[List[Path]] = None, tag: str = "auto") -> SnapshotManifest:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        snapshot_id = f"snap_{ts}_{tag}"
        target_dir = self.snapshots_dir / snapshot_id
        target_dir.mkdir(parents=True, exist_ok=True)

        if not paths_to_include:
            # Default to critical files
            paths_to_include = [
                self.repo_root / "index.html",
                self.repo_root / "sitemap.xml",
                self.repo_root / "robots.txt",
                self.repo_root / "data" / "seo" / "content-queue.json"
            ]

        checksums: Dict[str, str] = {}
        files_saved = 0

        for p in paths_to_include:
            if p.exists() and p.is_file():
                rel_path = p.relative_to(self.repo_root)
                dest = target_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dest)
                checksums[str(rel_path)] = self._sha256(dest)
                files_saved += 1

        manifest = SnapshotManifest(
            snapshot_id=snapshot_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            files_count=files_saved,
            files_checksums=checksums,
            snapshot_dir=str(target_dir)
        )

        manifest_path = target_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest.__dict__, indent=2), encoding="utf-8")
        return manifest

    def restore_snapshot(self, snapshot_id: str) -> bool:
        target_dir = self.snapshots_dir / snapshot_id
        manifest_path = target_dir / "manifest.json"
        if not manifest_path.exists():
            return False

        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        checksums = manifest_data.get("files_checksums", {})

        for rel_str, expected_hash in checksums.items():
            src = target_dir / rel_str
            dest = self.repo_root / rel_str
            if src.exists():
                actual_hash = self._sha256(src)
                if actual_hash == expected_hash:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dest)
                else:
                    raise ValueError(f"Snapshot integrity corrupted for {rel_str}")
        return True
