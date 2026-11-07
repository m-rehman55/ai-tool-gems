"""
tests/test_public_repository_boundary.py - Regression Test Suite for Public Repository Security Boundary.

Strictly verifies that:
1. No internal operational files (wholesale costs, supplier bots, customer orders, credentials) are tracked in Git.
2. The Git index contains zero private incident reports or support tickets containing sensitive hashes.
3. All files tracked in Git adhere to the public repository security policy.
"""

import os
import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestPublicRepositoryBoundary(unittest.TestCase):
    """Enforces boundaries between the public GitHub repository and private operational data."""

    def setUp(self):
        self.repo_root = REPO_ROOT

    def get_tracked_files(self):
        """Retrieves all files currently tracked by Git in the working branch."""
        res = subprocess.run(
            ["git", "ls-files"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=True
        )
        return [f.strip().replace("\\", "/") for f in res.stdout.splitlines() if f.strip()]

    def test_no_quarantined_operational_paths_tracked_in_git(self):
        """CRITICAL: Ensures private directories are strictly untracked in Git."""
        tracked = self.get_tracked_files()

        prohibited_prefixes = [
            "data/orders",
            "data/suppliers",
            "data/snapshots",
            "data/gsc_history/raw_responses",
            "data/analytics",
            "config",
            "data/wholesale_inventory.json",
            "data/wholesale_cost_reference.json",
        ]

        violations = []
        for path in tracked:
            for prefix in prohibited_prefixes:
                if path == prefix or path.startswith(prefix + "/"):
                    violations.append(path)

        self.assertEqual(
            violations,
            [],
            f"CRITICAL SECURITY VIOLATION: Private operational files tracked in Git:\n" + "\n".join(violations)
        )

    def test_no_credentials_or_secrets_tracked_in_git(self):
        """CRITICAL: Ensures no private keys, certificates, or credentials files are tracked in Git."""
        tracked = self.get_tracked_files()

        secret_patterns = [
            r"\.pem$",
            r"\.key$",
            r"\.pfx$",
            r"\.pkcs12$",
            r"credentials.*\.json$",
            r"client_secrets.*\.json$",
            r".*service_account.*\.json$",
            r"^\.env($|\.(?!example$))",
            r".*\.log$",
            r".*\.sqlite$",
            r".*\.db$",
        ]

        violations = []
        for path in tracked:
            for pattern in secret_patterns:
                if re.search(pattern, path, re.IGNORECASE):
                    violations.append(path)

        self.assertEqual(
            violations,
            [],
            f"CRITICAL SECURITY VIOLATION: Secret or credential files tracked in Git:\n" + "\n".join(violations)
        )

    def test_no_incident_reports_with_commit_hashes_in_public_tree(self):
        """Ensures that support ticket drafts and incident reports detailing purged commit SHAs are not in Git."""
        tracked = self.get_tracked_files()

        incident_reports = [
            "reports/GitHub_Support_Ticket_and_Refs_Report.md",
            "reports/Git_History_Purge_Verification_Report.md",
        ]

        violations = [p for p in tracked if p in incident_reports]
        self.assertEqual(
            violations,
            [],
            f"Incident reports containing historical commit references must not be tracked in public Git:\n"
            + "\n".join(violations)
        )

    def test_gitignore_contains_comprehensive_quarantine_blocks(self):
        """Validates that .gitignore explicitly denies all sensitive operational and credential patterns."""
        gitignore_path = self.repo_root / ".gitignore"
        self.assertTrue(gitignore_path.exists(), ".gitignore must exist")
        content = gitignore_path.read_text(encoding="utf-8")

        required_ignores = [
            "data/orders/",
            "data/wholesale_inventory.json",
            "data/wholesale_cost_reference.json",
            "data/suppliers/",
            "config/",
            "public-site/",
        ]

        for req in required_ignores:
            self.assertIn(
                req,
                content,
                f".gitignore missing mandatory quarantine rule: '{req}'"
            )


if __name__ == "__main__":
    unittest.main()
