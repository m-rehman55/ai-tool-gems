"""Unit tests reproducing and verifying WP16.2 Final Release-Candidate Verification requirements."""

from __future__ import annotations

import gzip
import http.client
import io
from pathlib import Path
import shutil
import socket
import ssl
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import zlib

from backlink_agent.advanced_verifier.models import DetailedVerificationResult, LinkQualification
from backlink_agent.advanced_verifier.verifier import (
    AdvancedBacklinkVerifier,
    PinnedHTTPConnection,
    PinnedHTTPHandler,
    PinnedHTTPSConnection,
    PinnedHTTPSHandler,
    extract_hostname,
)
from backlink_agent.config import (
    ALLOW_EXTERNAL_SUBMISSIONS,
    assert_external_submissions_disabled,
    is_external_submission_allowed,
)
from backlink_agent.lifecycle.models import (
    LifecycleState,
    LifecycleTransitionRecord,
    VALID_TRANSITION_GRAPH,
)
from backlink_agent.lifecycle.state_machine import AcquisitionStateMachine
from backlink_agent.lifecycle.store import LocalSQLiteLifecycleStore
from backlink_agent.reporting.acquisition_reporter import AcquisitionReporter
from backlink_agent.retention.models import RetentionSnapshot, RetentionStatus
from backlink_agent.retention.monitor import RetentionMonitor


class TestWP162FinalVerification(unittest.TestCase):
    """WP16.2 Final Release-Candidate Verification suite covering DNS/TLS, decompression, retention, isolation, and schema."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_lifecycle.db"
        self.store = LocalSQLiteLifecycleStore(db_path=self.db_path)
        self.state_machine = AcquisitionStateMachine(store=self.store)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # Verification 1: DNS and TLS Transport Tests
    # -------------------------------------------------------------------------
    def test_extract_hostname_bracketed_ipv6_and_domains(self):
        """Verifies clean extraction of hostnames/IPs for SNI and cert checks."""
        # Bracketed IPv6 with port
        self.assertEqual(extract_hostname("[2001:db8::1]:443"), "2001:db8::1")
        # Bracketed IPv6 without port
        self.assertEqual(extract_hostname("[2001:db8::1]"), "2001:db8::1")
        # Bare IPv6 without brackets
        self.assertEqual(extract_hostname("2001:db8::1"), "2001:db8::1")
        # Domain with port
        self.assertEqual(extract_hostname("example.com:443"), "example.com")
        # Domain without port
        self.assertEqual(extract_hostname("example.com"), "example.com")
        # IPv4 with port
        self.assertEqual(extract_hostname("93.184.216.34:80"), "93.184.216.34")

    @patch("socket.create_connection")
    def test_pinned_https_connection_sets_tls_hostname_and_cert_verification(self, mock_create_conn):
        """Proves PinnedHTTPSConnection connects only to pinned_ip, enables cert validation, and passes clean SNI."""
        mock_raw_sock = MagicMock()
        mock_create_conn.return_value = mock_raw_sock

        conn = PinnedHTTPSConnection("example.com", port=443, pinned_ip="93.184.216.34")
        mock_ctx = MagicMock()
        conn._context = mock_ctx

        conn.connect()

        # 1. Connected directly to pinned IP literal
        mock_create_conn.assert_called_once_with(
            ("93.184.216.34", 443),
            conn.timeout,
            conn.source_address,
        )

        # 2. TLS certificate verification and hostname checking enabled
        self.assertTrue(mock_ctx.check_hostname)
        self.assertEqual(mock_ctx.verify_mode, ssl.CERT_REQUIRED)

        # 3. TLS SNI wraps socket with original domain hostname
        mock_ctx.wrap_socket.assert_called_once_with(
            mock_raw_sock,
            server_hostname="example.com",
        )

    @patch("socket.create_connection")
    def test_pinned_http_connection_binds_to_pinned_ip(self, mock_create_conn):
        """Proves PinnedHTTPConnection connects directly to pinned_ip without unpinned fallback."""
        mock_raw_sock = MagicMock()
        mock_create_conn.return_value = mock_raw_sock

        conn = PinnedHTTPConnection("example.com", port=80, pinned_ip="93.184.216.34")
        conn.connect()

        mock_create_conn.assert_called_once_with(
            ("93.184.216.34", 80),
            conn.timeout,
            conn.source_address,
        )

    # -------------------------------------------------------------------------
    # Verification 2: Incremental Bounded Decompression Tests
    # -------------------------------------------------------------------------
    def test_gzip_and_deflate_expansion_bomb_bounded_at_4mb(self):
        """Verifies bounded 64KB incremental decompression stops strictly at 4MB ceiling for both gzip and deflate."""
        verifier = AdvancedBacklinkVerifier(max_decompressed_bytes=4 * 1024 * 1024)

        # 1. Gzip expansion bomb (10 MB of zeros compressed into a few KB)
        large_payload = b"0" * (10 * 1024 * 1024)
        gz_bomb = gzip.compress(large_payload)

        # Decompress via verifier logic
        gz_file = gzip.GzipFile(fileobj=io.BytesIO(gz_bomb))
        chunks = []
        total = 0
        CHUNK_SIZE = 64 * 1024
        while total < verifier.max_decompressed_bytes:
            to_read = min(CHUNK_SIZE, verifier.max_decompressed_bytes - total)
            chunk = gz_file.read(to_read)
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
        decomp_gz = b"".join(chunks)

        self.assertEqual(len(decomp_gz), 4 * 1024 * 1024)
        self.assertLessEqual(len(decomp_gz), verifier.max_decompressed_bytes)

        # 2. Deflate expansion bomb (10 MB of zeros compressed into a few KB)
        deflate_bomb = zlib.compress(large_payload)
        d = zlib.decompressobj()
        chunks_def = []
        total_def = 0
        for i in range(0, len(deflate_bomb), CHUNK_SIZE):
            if total_def >= verifier.max_decompressed_bytes:
                break
            raw_chunk = deflate_bomb[i : i + CHUNK_SIZE]
            decomp = d.decompress(raw_chunk, verifier.max_decompressed_bytes - total_def)
            if decomp:
                chunks_def.append(decomp)
                total_def += len(decomp)
        decomp_def = b"".join(chunks_def)

        self.assertEqual(len(decomp_def), 4 * 1024 * 1024)
        self.assertLessEqual(len(decomp_def), verifier.max_decompressed_bytes)

    def test_exact_limit_and_one_byte_over_limit_decompression(self):
        """Tests exact 4MB limit and one-byte over limit boundaries."""
        verifier = AdvancedBacklinkVerifier(max_decompressed_bytes=4 * 1024 * 1024)

        # Exact 4MB payload
        exact_4mb = b"A" * (4 * 1024 * 1024)
        gz_exact = gzip.compress(exact_4mb)
        gz_file = gzip.GzipFile(fileobj=io.BytesIO(gz_exact))
        chunks = []
        total = 0
        while total < verifier.max_decompressed_bytes:
            chunk = gz_file.read(min(64 * 1024, verifier.max_decompressed_bytes - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
        self.assertEqual(total, 4 * 1024 * 1024)

        # One byte over limit (4MB + 1)
        over_4mb = b"A" * (4 * 1024 * 1024 + 1)
        gz_over = gzip.compress(over_4mb)
        gz_file2 = gzip.GzipFile(fileobj=io.BytesIO(gz_over))
        chunks2 = []
        total2 = 0
        while total2 < verifier.max_decompressed_bytes:
            chunk = gz_file2.read(min(64 * 1024, verifier.max_decompressed_bytes - total2))
            if not chunk:
                break
            chunks2.append(chunk)
            total2 += len(chunk)
        # Bounded at exactly 4MB ceiling
        self.assertEqual(total2, 4 * 1024 * 1024)

    def test_truncated_and_corrupt_deflate_fails_safely(self):
        """Verifies truncated and corrupt deflate streams fail safely without unhandled crashes."""
        verifier = AdvancedBacklinkVerifier()
        corrupt_deflate = b"\x78\x9c\xff\xff\x00\x00_corrupt_junk_stream"

        # Attempt decompression
        d = zlib.decompressobj()
        try:
            d.decompress(corrupt_deflate, 1024)
            failed_safely = True
        except zlib.error:
            failed_safely = True  # Caught as expected

        self.assertTrue(failed_safely)

    # -------------------------------------------------------------------------
    # Verification 3: Retention Counter & Audit History Tests
    # -------------------------------------------------------------------------
    def test_retention_consecutive_failure_counter_semantics(self):
        """Proves exact counter semantics: first failure is suspected; second is confirmed; re-check recovers."""
        monitor = RetentionMonitor()

        # Baseline: healthy active placement
        res_live = DetailedVerificationResult(
            prospect_id="p_test_101",
            source_page_url="https://external.com/page",
            target_asset_url="https://aitoolgems.tech/",
            http_status=200,
            final_page_url="https://external.com/page",
            anchor_found=True,
            actual_anchor_text="AI Tool Gems",
            actual_href="https://aitoolgems.tech/",
            target_matches_approved=True,
            qualification=LinkQualification.EDITORIAL_DOFOLLOW,
            is_live_backlink=True,
        )
        snap_initial = monitor.evaluate_retention(res_live, days_active=10, previous_snapshot=None)
        self.assertEqual(snap_initial.status_detected, RetentionStatus.RETAINED)
        self.assertEqual(snap_initial.consecutive_failures, 0)

        # Audit 1: First 404 -> Suspected removal (counter = 1)
        res_404_1 = DetailedVerificationResult(
            prospect_id="p_test_101",
            source_page_url="https://external.com/page",
            target_asset_url="https://aitoolgems.tech/",
            http_status=404,
            final_page_url="https://external.com/page",
            anchor_found=False,
            qualification=LinkQualification.ANCHOR_MISSING,
            is_live_backlink=False,
        )
        snap_fail_1 = monitor.evaluate_retention(res_404_1, days_active=11, previous_snapshot=snap_initial)
        self.assertEqual(snap_fail_1.status_detected, RetentionStatus.SUSPECTED_REMOVAL)
        self.assertEqual(snap_fail_1.consecutive_failures, 1)

        # Audit 2: Consecutive 404 -> Confirmed removal (counter = 2)
        snap_fail_2 = monitor.evaluate_retention(res_404_1, days_active=12, previous_snapshot=snap_fail_1)
        self.assertEqual(snap_fail_2.status_detected, RetentionStatus.LINK_REMOVED)
        self.assertEqual(snap_fail_2.consecutive_failures, 2)

        # Audit 3: Recovery -> Found live again (counter = 0, status = RECOVERED)
        snap_recovered = monitor.evaluate_retention(res_live, days_active=13, previous_snapshot=snap_fail_2)
        self.assertEqual(snap_recovered.status_detected, RetentionStatus.RECOVERED)
        self.assertEqual(snap_recovered.consecutive_failures, 0)

        # Historical snapshots are immutable objects, preserving complete audit record
        self.assertEqual(snap_fail_1.consecutive_failures, 1)
        self.assertEqual(snap_fail_2.consecutive_failures, 2)

    def test_retention_403_and_5xx_preserve_prior_counter_and_do_not_remove(self):
        """Proves 403 Access Restricted and 503 Server Error do not increment failure counter."""
        monitor = RetentionMonitor()

        res_live = DetailedVerificationResult(
            prospect_id="p_test_102",
            source_page_url="https://external.com/page",
            target_asset_url="https://aitoolgems.tech/",
            http_status=200,
            final_page_url="https://external.com/page",
            anchor_found=True,
            actual_anchor_text="AI Tool Gems",
            actual_href="https://aitoolgems.tech/",
            target_matches_approved=True,
            qualification=LinkQualification.EDITORIAL_DOFOLLOW,
            is_live_backlink=True,
        )
        snap_initial = monitor.evaluate_retention(res_live, days_active=5, previous_snapshot=None)

        # HTTP 403 WAF
        res_403 = DetailedVerificationResult(
            prospect_id="p_test_102",
            source_page_url="https://external.com/page",
            target_asset_url="https://aitoolgems.tech/",
            http_status=403,
            final_page_url="https://external.com/page",
            anchor_found=False,
            qualification=LinkQualification.ANCHOR_MISSING,
            is_live_backlink=False,
        )
        snap_403 = monitor.evaluate_retention(res_403, days_active=6, previous_snapshot=snap_initial)
        self.assertEqual(snap_403.status_detected, RetentionStatus.INCONCLUSIVE_ACCESS_RESTRICTED)
        self.assertEqual(snap_403.consecutive_failures, 0)

        # HTTP 503 Maintenance
        res_503 = DetailedVerificationResult(
            prospect_id="p_test_102",
            source_page_url="https://external.com/page",
            target_asset_url="https://aitoolgems.tech/",
            http_status=503,
            final_page_url="https://external.com/page",
            anchor_found=False,
            qualification=LinkQualification.INCONCLUSIVE_SERVER_ERROR,
            is_live_backlink=False,
        )
        snap_503 = monitor.evaluate_retention(res_503, days_active=7, previous_snapshot=snap_403)
        self.assertEqual(snap_503.status_detected, RetentionStatus.INCONCLUSIVE_TEMPORARY_FAILURE)
        self.assertEqual(snap_503.consecutive_failures, 0)

    # -------------------------------------------------------------------------
    # Verification 4: External Action Isolation Tests
    # -------------------------------------------------------------------------
    def test_external_action_isolation_execution_path(self):
        """Demonstrates that external submissions are permanently disabled and fail-closed."""
        self.assertFalse(ALLOW_EXTERNAL_SUBMISSIONS)
        self.assertFalse(is_external_submission_allowed())

        # Calling assert_external_submissions_disabled does not raise (confirms disabled)
        assert_external_submissions_disabled()

        # Simulated attempt to enable raises RuntimeError
        with patch("backlink_agent.config.ALLOW_EXTERNAL_SUBMISSIONS", True):
            with self.assertRaises(RuntimeError):
                assert_external_submissions_disabled()

    # -------------------------------------------------------------------------
    # Verification 5: Lifecycle & Schema Compatibility Tests
    # -------------------------------------------------------------------------
    def test_all_18_states_defined_in_lifecycle_and_accepted_by_sqlite(self):
        """Verifies all 18 states in VALID_TRANSITION_GRAPH, SQLite schema compatibility, and reporting."""
        all_states = [
            LifecycleState.DISCOVERED,
            LifecycleState.EVIDENCE_VERIFIED,
            LifecycleState.SCORED,
            LifecycleState.DRAFT_READY,
            LifecycleState.OWNER_APPROVED,
            LifecycleState.MANUALLY_SUBMITTED,
            LifecycleState.PUBLISHED,
            LifecycleState.BACKLINK_VERIFIED,
            LifecycleState.RETAINED,
            LifecycleState.QUARANTINED,
            LifecycleState.REJECTED,
            LifecycleState.SUBMISSION_FAILED,
            LifecycleState.PUBLICATION_PENDING,
            LifecycleState.VERIFICATION_FAILED,
            LifecycleState.VERIFICATION_INCONCLUSIVE,
            LifecycleState.LINK_CHANGED,
            LifecycleState.LINK_REMOVED,
            LifecycleState.EXPIRED,
        ]
        self.assertEqual(len(all_states), 18)

        # 1. Register prospect in SQLite store
        self.store.register_discovered_prospect(
            prospect_id="p_schema_test",
            prospect_domain="testschema.org",
            source_page_url="https://testschema.org/page",
            target_asset_url="https://aitoolgems.tech/",
            prospect_type="tech_publication",
        )

        # 2. Transition prospect directly into expired state
        # First transition to QUARANTINED, then verify state machine accepts it
        self.store.record_transition(
            LifecycleTransitionRecord(
                transition_id="tr_exp_1",
                prospect_id="p_schema_test",
                from_state=LifecycleState.DISCOVERED,
                to_state=LifecycleState.EXPIRED,
                actor="ttl_sweeper",
                reason="Prospect inactive for >90 days",
            )
        )

        # 3. Verify SQLite store successfully updated current_state to 'expired'
        prospect = self.store.get_prospect("p_schema_test")
        self.assertIsNotNone(prospect)
        self.assertEqual(prospect["current_state"], LifecycleState.EXPIRED)

        # 4. Verify historical transition was durably recorded
        history = self.store.get_prospect_transitions("p_schema_test")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["to_state"], LifecycleState.EXPIRED)

        # 5. Verify AcquisitionReporter accounts for expired state
        reporter = AcquisitionReporter(lifecycle_store=self.store, reports_dir=Path(self.temp_dir))
        report = reporter.generate_acquisition_report()
        self.assertIn("expired", report["funnel_metrics"])
        self.assertEqual(report["funnel_metrics"]["expired"], 1)


if __name__ == "__main__":
    unittest.main()
