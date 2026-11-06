"""Unit tests for GitHub Pages Public Deployment Allowlist & Builder."""

import tempfile
import unittest
from pathlib import Path

from scripts.build_public_site import (
    PUBLIC_ALLOWLIST_DIRS,
    PUBLIC_ALLOWLIST_PATTERNS,
    STRICT_EXCLUDE_FILES,
    STRICT_EXCLUDE_PREFIXES,
    build_public_site,
)


class TestPublicDeploymentAllowlist(unittest.TestCase):
    def setUp(self):
        self.project_dir = Path(__file__).resolve().parent.parent

    def test_build_public_site_creates_clean_artifact_without_leaks(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir) / "dist"
            count, files = build_public_site(self.project_dir, out_path, clean=True)

            self.assertGreater(count, 50, "Public site should include all customer-facing files")

            # Check that root pages exist
            self.assertTrue((out_path / "index.html").exists())
            self.assertTrue((out_path / "about.html").exists())
            self.assertTrue((out_path / "contact.html").exists())
            self.assertTrue((out_path / "policies.html").exists())
            self.assertTrue((out_path / "sitemap.xml").exists())
            self.assertTrue((out_path / "robots.txt").exists())
            self.assertTrue((out_path / "CNAME").exists())
            self.assertEqual((out_path / "CNAME").read_text(encoding="utf-8").strip(), "aitoolgems.tech")

            # Check that STRICT_EXCLUDE_FILES do NOT exist
            for forbidden in STRICT_EXCLUDE_FILES:
                self.assertFalse((out_path / forbidden).exists(), f"Forbidden file leaked: {forbidden}")

            # Check that STRICT_EXCLUDE_PREFIXES do NOT exist
            for prefix in STRICT_EXCLUDE_PREFIXES:
                self.assertFalse((out_path / prefix).exists(), f"Forbidden dir leaked: {prefix}")

            # Explicit check for data/ and reports/
            self.assertFalse((out_path / "data").exists(), "data/ directory must never be in public build")
            self.assertFalse((out_path / "reports").exists(), "reports/ directory must never be in public build")
            self.assertFalse((out_path / "admin.html").exists(), "admin.html must never be in public build")


if __name__ == "__main__":
    unittest.main()
