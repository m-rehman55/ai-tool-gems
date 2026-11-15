"""Unit tests for WP13 Prospect Discovery Engine."""

from __future__ import annotations

import unittest

from backlink_agent.prospect_discovery import (
    CompetitorGapDiscoverer,
    DirectoryDiscoverer,
    DiscoveredProspect,
    DiscoveryOrchestrator,
    GitHubAwesomeDiscoverer,
    ProspectDeduplicator,
    TechnicalPublicationDiscoverer,
    normalize_url,
)


class TestProspectDiscovery(unittest.TestCase):
    def test_normalize_url(self):
        self.assertEqual(normalize_url("https://www.Dev.to/test/"), "https://dev.to/test")
        self.assertEqual(normalize_url("http://github.com/eudk/awesome-ai-tools/"), "https://github.com/eudk/awesome-ai-tools")
        self.assertEqual(normalize_url("subbazaar.pk/"), "https://subbazaar.pk")

    def test_canonical_identity_differentiates_distinct_github_repos(self):
        p1 = DiscoveredProspect(
            prospect_id="p1",
            source_id="test",
            prospect_domain="github.com",
            prospect_url="https://github.com/eudk/awesome-ai-tools",
            source_page_url="https://github.com/eudk/awesome-ai-tools/blob/main/README.md",
            prospect_type="github_awesome",
        )
        p2 = DiscoveredProspect(
            prospect_id="p2",
            source_id="test",
            prospect_domain="github.com",
            prospect_url="https://github.com/steven2358/awesome-generative-ai",
            source_page_url="https://github.com/steven2358/awesome-generative-ai/blob/main/README.md",
            prospect_type="github_awesome",
        )
        self.assertNotEqual(p1.canonical_identity, p2.canonical_identity)

    def test_deduplicator_filters_duplicate_prospect(self):
        dedup = ProspectDeduplicator()
        p1 = DiscoveredProspect(
            prospect_id="p1",
            source_id="test",
            prospect_domain="saashub.com",
            prospect_url="https://saashub.com",
            source_page_url="https://saashub.com/services/submit",
            prospect_type="directory_class1",
        )
        p2 = DiscoveredProspect(
            prospect_id="p2",
            source_id="test",
            prospect_domain="saashub.com",
            prospect_url="https://www.saashub.com",
            source_page_url="https://saashub.com/services/submit/",
            prospect_type="directory_class1",
        )
        self.assertTrue(dedup.register(p1))
        self.assertFalse(dedup.register(p2))  # Duplicate filtered
        self.assertEqual(dedup.seen_count, 1)

    def test_toxic_pbn_filter_blocks_spam_farms(self):
        gap = CompetitorGapDiscoverer()
        # Verified spam/PBN signatures
        self.assertTrue(gap.is_toxic_pbn("searchwins.shop"))
        self.assertTrue(gap.is_toxic_pbn("solidlinkpro.shop"))
        self.assertTrue(gap.is_toxic_pbn("serpvilo.shop"))
        self.assertTrue(gap.is_toxic_pbn("spammy-directory.site"))
        self.assertTrue(gap.is_toxic_pbn("seo-backlinks-fast.xyz"))
        # Legitimate non-spam domains on .shop and .site must NOT be falsely blocked
        self.assertFalse(gap.is_toxic_pbn("creativetools.shop"))
        self.assertFalse(gap.is_toxic_pbn("ai-portfolio.site"))
        self.assertFalse(gap.is_toxic_pbn("propakistani.pk"))
        self.assertFalse(gap.is_toxic_pbn("techjuice.pk"))
        self.assertFalse(gap.is_toxic_pbn("dev.to"))

    def test_competitor_gap_ingestion_identifies_gaps(self):
        gap = CompetitorGapDiscoverer()
        raw_records = [
            {
                "referring_domain": "techjuice.pk",
                "source_page": "https://techjuice.pk/pakistan-ai-startups-2026/",
                "competitor_domain": "aitoolspak.tech",
                "anchor_text": "AI Tools Pak",
            },
            {
                "referring_domain": "serpvilo.shop",  # Toxic PBN
                "source_page": "http://serpvilo.shop/links/",
                "competitor_domain": "aitoolspak.tech",
            },
            {
                "referring_domain": "existingpartner.com",  # Already links to AI Tool Gems
                "source_page": "https://existingpartner.com/ai/",
                "competitor_domain": "aitoolspak.tech",
            },
        ]
        candidates = gap.ingest_records(raw_records, known_aitoolgems_domains=["existingpartner.com"])
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].prospect_domain, "techjuice.pk")
        self.assertEqual(candidates[0].competitor_domain, "aitoolspak.tech")

    def test_directory_discovery_filters_reciprocal_badge_requirements(self):
        discoverer = DirectoryDiscoverer()
        candidates = discoverer.discover_candidates()
        domains = [c.prospect_domain for c in candidates]
        self.assertIn("saashub.com", domains)
        self.assertIn("startupnetwork.pk", domains)
        self.assertIn("agentwebmap.com", domains)
        self.assertNotIn("toolpilot.ai", domains)  # Rejected due to reciprocal badge rule

    def test_github_awesome_discovery_filters_ineligible_categories(self):
        gh_discoverer = GitHubAwesomeDiscoverer()
        candidates = gh_discoverer.discover_candidates()
        repo_names = [c.metadata.get("repo_name") for c in candidates]
        self.assertIn("eudk/awesome-ai-tools", repo_names)
        self.assertIn("steven2358/awesome-generative-ai", repo_names)
        self.assertNotIn("OuterSpacee/awesome-ai-tools", repo_names)  # Rejected: category mismatch

    def test_technical_publication_discovery_targets_prices_dataset(self):
        pub_discoverer = TechnicalPublicationDiscoverer()
        candidates = pub_discoverer.discover_candidates()
        self.assertGreaterEqual(len(candidates), 3)
        for c in candidates:
            self.assertEqual(c.target_asset_url, "https://aitoolgems.tech/prices/")

    def test_discovery_orchestrator_runs_end_to_end(self):
        orchestrator = DiscoveryOrchestrator()
        competitor_records = [
            {
                "referring_domain": "propakistani.pk",
                "source_page": "https://propakistani.pk/2026/11/ai-tools-subscription-growth/",
                "competitor_domain": "subbazaar.pk",
            }
        ]
        result = orchestrator.run_discovery(competitor_records=competitor_records)
        self.assertGreater(result["raw_discovered_count"], 0)
        self.assertGreater(result["unique_prospects_count"], 0)
        self.assertEqual(result["duplicates_filtered"], 0)
        # Verify propakistani.pk was discovered from competitor gap
        domains = [p.prospect_domain for p in result["prospects"]]
        self.assertIn("propakistani.pk", domains)
        self.assertIn("saashub.com", domains)


if __name__ == "__main__":
    unittest.main()
