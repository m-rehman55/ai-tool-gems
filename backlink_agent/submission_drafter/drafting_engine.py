"""Submission Drafting Engine coordinating multi-channel draft generators."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union

from backlink_agent.evidence_scoring.models import ScoredOpportunity
from .directory_drafter import DirectorySubmissionDrafter
from .fact_validator import DraftFactValidator
from .github_pr_drafter import GitHubAwesomePRDrafter
from .models import (
    BaseDraft,
    DirectorySubmissionDraft,
    GitHubAwesomePRDraft,
    PublicationPitchDraft,
)
from .publication_pitch_drafter import PublicationPitchDrafter


class SubmissionDraftingEngine:
    """Coordinates drafting across directories, GitHub PRs, and technical publications."""

    def __init__(self, validator: Optional[DraftFactValidator] = None):
        self.validator = validator or DraftFactValidator()
        self.directory_drafter = DirectorySubmissionDrafter(self.validator)
        self.github_drafter = GitHubAwesomePRDrafter(self.validator)
        self.pub_drafter = PublicationPitchDrafter(self.validator)

    def draft_for_opportunity(
        self, opp: ScoredOpportunity
    ) -> Optional[Tuple[Union[DirectorySubmissionDraft, GitHubAwesomePRDraft, PublicationPitchDraft], str]]:
        """Generates a validated draft and returns (draft, draft_hash).

        Only generates drafts for opportunities with action_recommendation == 'draft_ready'.
        """
        # Strict WP14 Draft Eligibility Gate: Only high_priority (score >= 75) can be drafted
        if (
            opp.action_recommendation != "draft_ready"
            or opp.score.priority_tier != "high_priority"
            or opp.score.total_score < 75
        ):
            return None

        p_type = opp.prospect_type
        domain = opp.prospect_domain.lower()

        draft: Optional[BaseDraft] = None

        if p_type == "github_awesome" or "github.com" in domain:
            draft = self.github_drafter.draft_pr(opp)
        elif p_type == "tech_publication" or domain in ("dev.to", "hashnode.com", "medium.com"):
            draft = self.pub_drafter.draft_pitch(opp)
        elif p_type in ("directory_class1", "directory_class2", "directory_class3", "competitor_backlink"):
            draft = self.directory_drafter.draft_submission(opp)
        else:
            # Default to directory package for general aggregator/catalog prospects
            draft = self.directory_drafter.draft_submission(opp)

        if draft is None:
            return None

        draft_hash = draft.calculate_draft_hash()
        return (draft, draft_hash)

    def draft_batch(
        self, opportunities: List[ScoredOpportunity]
    ) -> List[Tuple[BaseDraft, str, ScoredOpportunity]]:
        """Batch generates validated drafts for a list of scored opportunities."""
        results = []
        for opp in opportunities:
            res = self.draft_for_opportunity(opp)
            if res:
                draft, d_hash = res
                results.append((draft, d_hash, opp))
        return results
