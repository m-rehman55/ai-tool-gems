#!/usr/bin/env python3
"""
Integration & Workflow tests for GrowthOrchestrator in seo-agent
---------------------------------------------------------------
"""

import sys
from pathlib import Path
import unittest

AGENT_DIR = Path(__file__).resolve().parent.parent
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

from agent.orchestrator import GrowthOrchestrator

class TestWorkflows(unittest.TestCase):

    def setUp(self):
        self.orchestrator = GrowthOrchestrator(mode="AUDIT", live_crawl=False)

    def test_preflight_passes(self):
        self.assertTrue(self.orchestrator.run_preflight())

    def test_full_autonomous_workflow_audit_mode(self):
        result = self.orchestrator.execute_workflow()
        self.assertEqual(result.get("status"), "COMPLETED")
        self.assertEqual(result.get("mode"), "AUDIT")
        self.assertGreater(result.get("pages_audited", 0), 10)
        self.assertTrue(result.get("scope_passed"))
        self.assertTrue(Path(result.get("report_path")).exists())

if __name__ == "__main__":
    unittest.main()
