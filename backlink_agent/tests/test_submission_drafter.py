"""Unit tests for Submission Drafter, Fact Validator, and Package Generation."""

import unittest

from backlink_agent.evidence_scoring.models import ScoreBreakdown, ScoredOpportunity
from backlink_agent.submission_drafter import (
    DirectorySubmissionDraft,
    DirectorySubmissionDrafter,
    DraftFactValidator,
    GitHubAwesomePRDraft,
    GitHubAwesomePRDrafter,
    PublicationPitchDraft,
    PublicationPitchDrafter,
    SubmissionDraftingEngine,
)


class TestSubmissionDrafter(unittest.TestCase):
    def setUp(self):
        self.validator = DraftFactValidator()
        self.engine = SubmissionDraftingEngine(self.validator)

    def _create_scored_opp(
        self,
        p_id: str,
        domain: str,
        url: str,
        p_type: str,
        action: str = "draft_ready",
        target: str = "https://aitoolgems.tech/",
    ) -> ScoredOpportunity:
        breakdown = ScoreBreakdown(22, 22, 20, 15, 15)
        return ScoredOpportunity(
            prospect_id=p_id,
            prospect_domain=domain,
            source_page_url=url,
            prospect_type=p_type,
            target_asset_url=target,
            score=breakdown,
            action_recommendation=action,
        )

    def test_directory_submission_draft(self):
        opp = self._create_scored_opp(
            "p_dir", "saashub.com", "https://saashub.com/submit", "directory_class1"
        )
        drafter = DirectorySubmissionDrafter(self.validator)
        draft = drafter.draft_submission(opp)

        self.assertIsInstance(draft, DirectorySubmissionDraft)
        self.assertEqual(draft.tool_name, "AI Tool Gems")
        self.assertEqual(draft.website_url, "https://aitoolgems.tech/")
        self.assertIn("fact_pricing_pkr", draft.verified_fact_ids)
        self.assertIn("fact_payment_pakistan_rails", draft.verified_fact_ids)

        draft_hash = draft.calculate_draft_hash()
        self.assertEqual(len(draft_hash), 16)
        # Deterministic
        self.assertEqual(draft_hash, draft.calculate_draft_hash())

    def test_github_pr_draft(self):
        opp = self._create_scored_opp(
            "p_gh",
            "github.com",
            "https://github.com/eudk/awesome-ai-tools",
            "github_awesome",
        )
        drafter = GitHubAwesomePRDrafter(self.validator)
        draft = drafter.draft_pr(opp)

        self.assertIsInstance(draft, GitHubAwesomePRDraft)
        self.assertEqual(draft.repository_name, "eudk/awesome-ai-tools")
        self.assertIn("- [AI Tool Gems](https://aitoolgems.tech/)", draft.proposed_markdown_entry)
        self.assertIn("docs(readme):", draft.commit_message)
        self.assertIn("fact_entity_brand", draft.verified_fact_ids)

    def test_publication_pitch_draft(self):
        opp = self._create_scored_opp(
            "p_pub",
            "dev.to",
            "https://dev.to/new",
            "tech_publication",
            target="https://aitoolgems.tech/prices/",
        )
        drafter = PublicationPitchDrafter(self.validator)
        draft = drafter.draft_pitch(opp)

        self.assertIsInstance(draft, PublicationPitchDraft)
        self.assertEqual(draft.csv_dataset_url, "https://aitoolgems.tech/prices/ai-tools-pricing-pakistan.csv")
        self.assertIn("EasyPaisa", " ".join(draft.article_outline))
        self.assertIn("fact_content_prices_dataset", draft.verified_fact_ids)

    def test_fact_validator_rejects_untrue_copy(self):
        draft = DirectorySubmissionDraft(
            draft_id="bad_1",
            prospect_id="p_bad",
            short_tagline="Free AI tools with Stripe and PayPal automatic checkout.",
            long_description="We support Stripe and PayPal instant checkout.",
        )
        is_valid, violations, _ = self.validator.validate_draft(draft)
        self.assertFalse(is_valid)
        self.assertTrue(any("stripe" in v.lower() or "paypal" in v.lower() for v in violations))

    def test_submission_drafting_engine_routing_and_batch(self):
        opp_dir = self._create_scored_opp("p1", "toolify.ai", "https://toolify.ai/submit", "directory_class2")
        opp_gh = self._create_scored_opp("p2", "github.com", "https://github.com/steven2358/awesome-generative-ai", "github_awesome")
        opp_pub = self._create_scored_opp("p3", "hashnode.com", "https://hashnode.com/post", "tech_publication")
        opp_quarantined = self._create_scored_opp("p4", "spam.link", "https://spam.link", "competitor_backlink", action="quarantine")

        batch = self.engine.draft_batch([opp_dir, opp_gh, opp_pub, opp_quarantined])

        # Quarantined opportunity is filtered out
        self.assertEqual(len(batch), 3)

        draft1, hash1, _ = batch[0]
        draft2, hash2, _ = batch[1]
        draft3, hash3, _ = batch[2]

        self.assertIsInstance(draft1, DirectorySubmissionDraft)
        self.assertIsInstance(draft2, GitHubAwesomePRDraft)
        self.assertIsInstance(draft3, PublicationPitchDraft)

        self.assertEqual(len(hash1), 16)
        self.assertEqual(len(hash2), 16)
        self.assertEqual(len(hash3), 16)


if __name__ == "__main__":
    unittest.main()
