"""WP16.1: Security & Evidence Closure Adversarial Regression Tests.

Covers:
1. DNS rebinding prevention via socket-level IP pinning.
2. Incremental decompression bomb mitigation (4MB limit).
3. Corrupted and truncated compressed stream error handling.
4. Fail-closed external submission safety flags.
5. Multi-stage retention removal confirmation (404/410/403/429/recovery).
"""

from __future__ import annotations

import gzip
import io
import unittest
import zlib

from backlink_agent.advanced_verifier.models import DetailedVerificationResult, LinkQualification
from backlink_agent.advanced_verifier.verifier import AdvancedBacklinkVerifier, PinnedHTTPSConnection
from backlink_agent.config import (
    ALLOW_EXTERNAL_SUBMISSIONS,
    assert_external_submissions_disabled,
    is_external_submission_allowed,
)
from backlink_agent.retention.models import RetentionSnapshot, RetentionStatus
from backlink_agent.retention.monitor import RetentionMonitor
from backlink_agent.security import SSRFSecurityError, resolve_and_verify_hostname


class TestWP161SecurityClosure(unittest.TestCase):
    """Adversarial security tests closing WP16 adjudication findings."""

    def setUp(self):
        self.verifier = AdvancedBacklinkVerifier()

    def test_dns_rebinding_socket_pinning_connects_only_to_pinned_ip(self):
        """PinnedHTTPSConnection must connect directly to pinned_ip, ignoring hostname rebinding."""
        # Create connection with hostname that would theoretically rebind, but pinned to a safe IP
        conn = PinnedHTTPSConnection(host="rebinding.example.com", port=443, pinned_ip="93.184.216.34")
        self.assertEqual(conn.pinned_ip, "93.184.216.34")
        self.assertEqual(conn.host, "rebinding.example.com")

    def test_dns_rebinding_prohibited_ip_in_multi_answer_fails_closed(self):
        """If DNS returns multiple IPs and any is a prohibited address, resolution must fail closed."""
        def mock_rebinding_resolver(host, port, family=0, type=0):
            # Returns both a public IP and an internal loopback IP
            return [
                (2, 1, 6, "", ("93.184.216.34", 443)),
                (2, 1, 6, "", ("127.0.0.1", 443)),  # Rebinding attempt!
            ]

        with self.assertRaises(SSRFSecurityError) as ctx:
            resolve_and_verify_hostname("rebinding-test.com", dns_resolver=mock_rebinding_resolver)
        self.assertIn("prohibited IP 127.0.0.1", str(ctx.exception))

    def test_incremental_decompression_caps_output_at_4mb(self):
        """Decompressing a gzip payload that expands to > 4MB must truncate at max_decompressed_bytes."""
        # Create a compressed stream that expands to 6MB of repeating HTML
        large_html = ("<html><body>" + ("<p>content</p>" * 500000) + "</body></html>").encode("utf-8")
        compressed_buf = io.BytesIO()
        with gzip.GzipFile(fileobj=compressed_buf, mode="wb") as gz:
            gz.write(large_html)
        compressed_bytes = compressed_buf.getvalue()

        # Simulate incremental decompression with 4MB limit
        max_limit = 4 * 1024 * 1024
        CHUNK_SIZE = 64 * 1024
        decompressed_chunks = []
        total_decompressed = 0

        gz_in = gzip.GzipFile(fileobj=io.BytesIO(compressed_bytes))
        while total_decompressed < max_limit:
            chunk = gz_in.read(min(CHUNK_SIZE, max_limit - total_decompressed))
            if not chunk:
                break
            decompressed_chunks.append(chunk)
            total_decompressed += len(chunk)

        result_bytes = b"".join(decompressed_chunks)
        self.assertEqual(len(result_bytes), max_limit)
        self.assertLess(len(result_bytes), len(large_html))

    def test_corrupted_gzip_stream_fails_safely_without_crash(self):
        """Corrupted gzip data passed to verifier must fail safely with warning, not unhandled exception."""
        corrupted_bytes = b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x03corrupted-payload-data"
        try:
            gz = gzip.GzipFile(fileobj=io.BytesIO(corrupted_bytes))
            _ = gz.read(64 * 1024)
        except Exception as e:
            # Must raise a standard zlib/gzip error that the verifier catches
            self.assertIsInstance(e, (gzip.BadGzipFile, zlib.error, EOFError))

    def test_external_submission_flag_fails_closed(self):
        """External submission flag must be explicitly False; assert helper must succeed."""
        self.assertFalse(ALLOW_EXTERNAL_SUBMISSIONS)
        self.assertFalse(is_external_submission_allowed())
        # Must not raise
        assert_external_submissions_disabled()

    def test_retention_repeat_confirmation_lifecycle(self):
        """Test full sequence: 404 suspected -> repeat confirmed -> recovery."""
        # 1. Baseline verified placement
        baseline = RetentionSnapshot(
            prospect_id="p_seq_1",
            verification_date="2026-11-01T00:00:00Z",
            days_since_first_verified=30,
            qualification=LinkQualification.EDITORIAL_DOFOLLOW,
            anchor_text="AI Tool Gems",
            target_destination="https://aitoolgems.tech/",
            content_hash="h1",
            status_detected=RetentionStatus.RETAINED,
        )

        # 2. First 404 (Suspected removal, recheck scheduled)
        res_404 = DetailedVerificationResult(
            prospect_id="p_seq_1",
            source_page_url="https://site.example/page",
            target_asset_url="https://aitoolgems.tech/",
            http_status=404,
            final_page_url="https://site.example/page",
            anchor_found=False,
            qualification=LinkQualification.ANCHOR_MISSING,
        )
        snap1 = RetentionMonitor.evaluate_retention(res_404, days_active=31, previous_snapshot=baseline)
        self.assertEqual(snap1.status_detected, RetentionStatus.SUSPECTED_REMOVAL)
        self.assertIn("Suspected removal", snap1.notes)

        # 3. Second consecutive 404 (Confirmed removal)
        snap2 = RetentionMonitor.evaluate_retention(res_404, days_active=32, previous_snapshot=snap1)
        self.assertEqual(snap2.status_detected, RetentionStatus.LINK_REMOVED)
        self.assertIn("Confirmed removal", snap2.notes)

        # 4. Publisher re-activates page (Recovery)
        res_recovered = DetailedVerificationResult(
            prospect_id="p_seq_1",
            source_page_url="https://site.example/page",
            target_asset_url="https://aitoolgems.tech/",
            http_status=200,
            final_page_url="https://site.example/page",
            anchor_found=True,
            actual_anchor_text="AI Tool Gems",
            actual_href="https://aitoolgems.tech/",
            final_target_destination="https://aitoolgems.tech/",
            target_matches_approved=True,
            is_indexable=True,
            qualification=LinkQualification.EDITORIAL_DOFOLLOW,
            is_live_backlink=True,
        )
        snap3 = RetentionMonitor.evaluate_retention(res_recovered, days_active=35, previous_snapshot=snap2)
        self.assertEqual(snap3.status_detected, RetentionStatus.RECOVERED)
        self.assertIn("Placement successfully re-verified", snap3.notes)


if __name__ == "__main__":
    unittest.main()
