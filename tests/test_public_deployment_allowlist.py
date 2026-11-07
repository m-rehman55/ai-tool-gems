"""
tests/test_public_deployment_allowlist.py - Comprehensive Adversarial & Allowlist Test Suite.

Tests fail-closed behavior of scripts/build_public_site.py against adversarial injections:
1. assets/private.csv
2. assets/supplier-export.json
3. tools/test/.env
4. guides/internal-audit.md
5. blog/customer-data.sqlite
6. category/private.pem
7. assets/backup.zip
8. assets/secrets.log
9. symlinks pointing outside approved directories
10. Legitimate public asset preservation and deterministic manifest generation.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.build_public_site import (
    APPROVED_PUBLIC_DIRS,
    APPROVED_ROOT_FILES,
    PublicSiteSecurityError,
    build_public_site,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestPublicDeploymentAllowlist(unittest.TestCase):
    """Enforces fail-closed public artifact isolation."""

    def setUp(self):
        self.project_dir = REPO_ROOT

    def test_legitimate_build_succeeds_and_generates_manifest(self):
        """Verifies that legitimate production assets build cleanly and generate manifest."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir) / "dist"
            count, manifest = build_public_site(self.project_dir, out_path, clean=True)

            self.assertGreater(count, 50, "Public build should stage customer-facing pages")

            # Verify core storefront files exist
            self.assertTrue((out_path / "index.html").exists())
            self.assertTrue((out_path / "about.html").exists())
            self.assertTrue((out_path / "contact.html").exists())
            self.assertTrue((out_path / "policies.html").exists())
            self.assertTrue((out_path / "sitemap.xml").exists())
            self.assertTrue((out_path / "robots.txt").exists())
            self.assertTrue((out_path / "CNAME").exists())
            self.assertEqual((out_path / "CNAME").read_text(encoding="utf-8").strip(), "aitoolgems.tech")

            # Verify manifest generation
            manifest_file = out_path / "manifest-public-build.json"
            self.assertTrue(manifest_file.exists(), "Manifest file must be generated")
            manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
            self.assertEqual(manifest_data["domain"], "aitoolgems.tech")
            self.assertEqual(manifest_data["total_files"], count)
            self.assertEqual(len(manifest_data["files"]), count)

            # Check that each manifest item has path, size_bytes, and sha256
            for item in manifest_data["files"]:
                self.assertIn("path", item)
                self.assertIn("size_bytes", item)
                self.assertIn("sha256", item)
                self.assertEqual(len(item["sha256"]), 64, "SHA-256 must be 64-char hex")

            # Verify zero private files leaked
            self.assertFalse((out_path / "data").exists(), "data/ directory must never be staged")
            self.assertFalse((out_path / "reports").exists(), "reports/ directory must never be staged")
            self.assertFalse((out_path / "config").exists(), "config/ directory must never be staged")
            self.assertFalse((out_path / "admin.html").exists(), "admin.html must never be staged")

    def test_adversarial_file_injections_fail_closed(self):
        """CRITICAL: Injects prohibited adversarial files and verifies build fails closed."""
        adversarial_cases = [
            ("assets/private.csv", "id,cost,margin\n1,100,50"),
            ("assets/supplier-export.json", '{"supplier": "secret"}'),
            ("tools/test/.env", "API_KEY=leak12345"),
            ("guides/internal-audit.md", "# Internal Audit\nConfidential findings."),
            ("blog/customer-data.sqlite", "SQLite format 3\x00"),
            ("category/private.pem", "-----BEGIN RSA PRIVATE KEY-----"),
            ("assets/backup.zip", "PK\x03\x04fakezipcontent"),
            ("assets/secrets.log", "[ERROR] Leaked token in log"),
        ]

        for rel_path, mock_content in adversarial_cases:
            with self.subTest(injected_file=rel_path):
                with tempfile.TemporaryDirectory() as tmp_proj, tempfile.TemporaryDirectory() as tmp_dist:
                    proj_path = Path(tmp_proj)
                    dist_path = Path(tmp_dist) / "out"

                    # Setup minimal valid project
                    (proj_path / "index.html").write_text("<!doctype html><html></html>", encoding="utf-8")
                    (proj_path / "CNAME").write_text("aitoolgems.tech\n", encoding="utf-8")

                    # Inject the adversarial file
                    bad_file = proj_path / rel_path
                    bad_file.parent.mkdir(parents=True, exist_ok=True)
                    if isinstance(mock_content, bytes):
                        bad_file.write_bytes(mock_content)
                    else:
                        bad_file.write_text(mock_content, encoding="utf-8")

                    # Assert build raises PublicSiteSecurityError
                    with self.assertRaises(PublicSiteSecurityError, msg=f"Builder failed to reject: {rel_path}"):
                        build_public_site(proj_path, dist_path, clean=True)

    def test_symlink_injection_fails_closed(self):
        """CRITICAL: Injects a directory symlink escaping to a private location and verifies rejection."""
        with tempfile.TemporaryDirectory() as tmp_proj, tempfile.TemporaryDirectory() as tmp_dist:
            proj_path = Path(tmp_proj)
            dist_path = Path(tmp_dist) / "out"

            # Setup minimal valid project
            (proj_path / "index.html").write_text("<!doctype html><html></html>", encoding="utf-8")
            (proj_path / "CNAME").write_text("aitoolgems.tech\n", encoding="utf-8")

            # Create an external private folder
            private_target = proj_path / "secret_vault"
            private_target.mkdir(parents=True, exist_ok=True)
            (private_target / "leaked.html").write_text("Secret Content", encoding="utf-8")

            # Create a symlink inside an approved public dir (assets/symlinked)
            assets_dir = proj_path / "assets"
            assets_dir.mkdir(parents=True, exist_ok=True)
            symlink_dest = assets_dir / "symlinked"

            try:
                os.symlink(private_target, symlink_dest, target_is_directory=True)
            except (OSError, NotImplementedError):
                # On Windows without developer mode/admin rights, symlink creation might raise OSError
                self.skipTest("Symlinks cannot be created without elevated privileges on this host")

            # Assert build raises PublicSiteSecurityError
            with self.assertRaises(PublicSiteSecurityError, msg="Builder failed to reject symlink escape"):
                build_public_site(proj_path, dist_path, clean=True)

    def test_cname_tampering_fails_closed(self):
        """Verifies that a tampered or invalid CNAME domain fails closed."""
        with tempfile.TemporaryDirectory() as tmp_proj, tempfile.TemporaryDirectory() as tmp_dist:
            proj_path = Path(tmp_proj)
            dist_path = Path(tmp_dist) / "out"

            (proj_path / "index.html").write_text("<!doctype html><html></html>", encoding="utf-8")
            (proj_path / "CNAME").write_text("attacker-site.com\n", encoding="utf-8")

            with self.assertRaises(PublicSiteSecurityError, msg="Builder failed to reject invalid CNAME domain"):
                build_public_site(proj_path, dist_path, clean=True)


if __name__ == "__main__":
    unittest.main()
