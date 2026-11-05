"""
scripts/run_all_tests.py - Complete Ecosystem Test Runner for CI & Local Development.
Discovers and executes all 18 test suites across the HERMES multi-agent operating system.
"""

import sys
import unittest
from pathlib import Path

# Ensure UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

TEST_DIRS = [
    "tests",
    "gsc_agent/tests",
    "crawler_agent/tests",
    "keyword_agent/tests",
    "bing_agent/tests",
    "ga4_agent/tests",
    "posthog_agent/tests",
    "pagespeed_agent/tests",
    "aio_agent/tests",
    "content_agent/tests",
    "backlink_agent/tests",
    "competitor_agent/tests",
    "marketing_agent/tests",
    "merchant_agent/tests",
    "conversion_agent/tests",
    "security_agent/tests",
    "ping_agent/tests",
    "seo-agent/tests"
]

print("=================================================================")
print("🧪 HERMES OMNISCIENT FULL ECOSYSTEM TEST SUITE EXECUTION")
print("=================================================================")

total_ran = 0
total_passed = 0
total_failed = 0
total_errors = 0
failures_list = []

for t_dir in TEST_DIRS:
    if "-" in t_dir:
        suite = unittest.defaultTestLoader.discover(t_dir, pattern="test_*.py")
    else:
        suite = unittest.defaultTestLoader.discover(t_dir, pattern="test_*.py", top_level_dir=".")
    
    runner = unittest.TextTestRunner(verbosity=0, stream=open(Path("nul") if sys.platform == "win32" else Path("/dev/null"), "w"))
    result = runner.run(suite)
    
    status_str = "PASS" if result.wasSuccessful() else "FAIL"
    print(f"  • {t_dir:<26} : {result.testsRun:>3} tests  [{status_str}]")
    
    total_ran += result.testsRun
    total_failed += len(result.failures)
    total_errors += len(result.errors)
    if not result.wasSuccessful():
        for f in result.failures:
            failures_list.append((t_dir, str(f[0]), str(f[1])))
        for e in result.errors:
            failures_list.append((t_dir, str(e[0]), str(e[1])))

total_passed = total_ran - total_failed - total_errors

print("-----------------------------------------------------------------")
print(f"TOTAL TESTS RUN:    {total_ran}")
print(f"TOTAL PASSED:       {total_passed}")
print(f"TOTAL FAILURES:     {total_failed}")
print(f"TOTAL ERRORS:       {total_errors}")
print(f"SUCCESS RATE:       {round((total_passed / total_ran) * 100, 1) if total_ran else 0}%")
print("=================================================================")

if failures_list:
    print("\nFAILURES / ERRORS:")
    for suite, test_name, err in failures_list:
        print(f"\n[{suite}] {test_name}:")
        print(err[:300])
    sys.exit(1)
else:
    print("ALL TEST SUITES ARE 100% GREEN! 🚀")
    sys.exit(0)

