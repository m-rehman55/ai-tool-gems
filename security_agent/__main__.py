"""
security_agent.__main__ - CLI for Security, Compliance & Safety Firewall Agent.
"""

import sys
import argparse
import json
from pathlib import Path

# Fix Windows console encoding if needed
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from security_agent.secrets_scanner import SecretsScanner
from security_agent.html_safety_validator import HtmlSafetyValidator
from security_agent.dependency_checker import DependencyChecker
from security_agent.snapshot_manager import SnapshotManager


def main():
    parser = argparse.ArgumentParser(description="HERMES Agent 15 - Security, Compliance & Safety Firewall")
    subparsers = parser.add_subparsers(dest="command")

    # scan-secrets
    secrets_parser = subparsers.add_parser("scan-secrets", help="Scan repository for exposed credentials & tokens")
    secrets_parser.add_argument("--json", action="store_true", help="Output findings in JSON")

    # validate-html
    html_parser = subparsers.add_parser("validate-html", help="Validate HTML for XSS, SSRF, Traversal, and Prompt Injection")
    html_parser.add_argument("path", help="Path to HTML file to inspect")

    # check-deps
    subparsers.add_parser("check-deps", help="Audit Python environment dependencies with pip check")

    # snapshot
    subparsers.add_parser("snapshot", help="Create an atomic pre-change rollback snapshot")

    # audit
    audit_parser = subparsers.add_parser("audit", help="Run complete security & compliance audit")
    audit_parser.add_argument("--json", action="store_true", help="Output audit report in JSON")

    args = parser.parse_args()
    repo_root = Path.cwd()

    if args.command == "scan-secrets":
        scanner = SecretsScanner()
        report = scanner.scan_directory(repo_root)
        if args.json:
            print(json.dumps({
                "total_files_scanned": report.total_files_scanned,
                "clean": report.clean,
                "findings": [f.__dict__ for f in report.findings]
            }, indent=2))
        else:
            print(f"Scanned {report.total_files_scanned} files.")
            if report.clean:
                print("[PASS] Zero exposed secrets detected across codebase.")
            else:
                print(f"[FAIL] {len(report.findings)} exposed secret finding(s) detected:")
                for f in report.findings:
                    print(f"  * {f.file_path}:{f.line_number} [{f.rule_name}]")

    elif args.command == "validate-html":
        validator = HtmlSafetyValidator()
        res = validator.validate_file(Path(args.path))
        print(f"Target: {args.path}")
        print(f"Status: {'[PASS] SAFE' if res.is_safe else '[FAIL] VIOLATIONS DETECTED'}")
        if res.violations:
            for v in res.violations:
                print(f"  [{v.severity}] {v.rule}: {v.description}")
                print(f"       Snippet: {v.snippet}")

    elif args.command == "check-deps":
        checker = DependencyChecker()
        res = checker.check_dependencies()
        if res.clean:
            print("[PASS] Dependencies clean: No broken requirements or version conflicts.")
        else:
            print("[FAIL] Broken requirements detected:")
            for b in res.broken_dependencies:
                print(f"  * {b}")

    elif args.command == "snapshot":
        mgr = SnapshotManager(repo_root)
        snap = mgr.create_snapshot()
        print(f"[SUCCESS] Rollback snapshot created: {snap.snapshot_id}")
        print(f"          Files archived: {snap.files_count}")
        print(f"          Directory: {snap.snapshot_dir}")

    elif args.command == "audit":
        scanner = SecretsScanner()
        validator = HtmlSafetyValidator()
        checker = DependencyChecker()

        sec_rep = scanner.scan_directory(repo_root)
        html_rep = validator.validate_file(repo_root / "index.html")
        dep_rep = checker.check_dependencies()

        all_clean = sec_rep.clean and html_rep.is_safe and dep_rep.clean

        if args.json:
            print(json.dumps({
                "overall_clean": all_clean,
                "secrets": {"scanned": sec_rep.total_files_scanned, "clean": sec_rep.clean, "count": len(sec_rep.findings)},
                "html": {"is_safe": html_rep.is_safe, "violations": len(html_rep.violations)},
                "dependencies": {"clean": dep_rep.clean, "broken": dep_rep.broken_dependencies}
            }, indent=2))
        else:
            print("=================================================================")
            print("HERMES AGENT 15 -- SECURITY, COMPLIANCE & SAFETY FIREWALL AUDIT")
            print("=================================================================")
            print(f"Secrets Scanning:    {'[PASS] CLEAN' if sec_rep.clean else f'[FAIL] {len(sec_rep.findings)} FINDINGS'}")
            print(f"HTML Safety Guard:   {'[PASS] SAFE' if html_rep.is_safe else f'[FAIL] {len(html_rep.violations)} VIOLATIONS'}")
            print(f"Dependencies Status: {'[PASS] CLEAN' if dep_rep.clean else f'[FAIL] {len(dep_rep.broken_dependencies)} ISSUES'}")
            print(f"Overall Gate Status: {'[PASS] APPROVED' if all_clean else '[BLOCKED]'}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
