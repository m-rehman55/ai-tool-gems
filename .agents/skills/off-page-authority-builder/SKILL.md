---
name: off-page-authority-builder
description: Closed-loop off-page backlinks, entity authority, and white-hat digital PR workflow for AI Tool Gems.
---

# Off-Page Authority Builder

Execute white-hat off-page authority growth to resolve Bing Webmaster Tools backlink discovery gaps (`ruleId=110`) without link spam.

## 1. Closed-Loop Weekly Cycle

1. **Discover:** Identify candidate directories, startup hubs, curated awesome lists, developer publications, and PR outlets relevant to AI tools, software pricing, or Pakistan tech.
2. **Qualify (100-Point Rubric):**
   - Topical/regional relevance (0-25)
   - Editorial standards & organic visibility (0-25)
   - Direct brand/tool/dataset fit (0-20)
   - Non-spam / non-reciprocal compliance (0-15)
   - Indexable public profile or citation link (0-15)
   - Decision: **75-100 Prioritize**, **55-74 Investigate**, **<55 Reject/Skip**.
3. **Approve:** Confirm eligibility against live site rules (skip tool-only sites for directories; skip reciprocal link/badge demands; skip broken TLS endpoints).
4. **Publish:** Submit truthful listings, linkable datasets (`/prices/`), GitHub metadata/PRs, or technical write-ups.
5. **Verify:** Open the published `source_page`, confirm HTTP 200 and live `target_url` before setting `link_status=live`.
6. **Measure:** Track `discovered_by_bing`, `discovered_by_gsc`, and `referral_activity` weekly.
7. **Learn:** Double down on cohorts earning verified discovery and referral clicks; prune stagnant targets.

## 2. Hard Guardrails

- **Zero Spam:** Never buy links, join PBNs, run bulk directory blasts, or accept reciprocal footer badges.
- **Entity Hygiene:** Keep `Organization.sameAs` in `index.html` limited to owned official profiles only.
- **Strict Truth:** Never invent prices, metrics, trends, GitHub stars, or mark unverified placements `live`.

## 3. Verification

```bash
python3 scripts/offpage_authority_tracker.py --validate
python3 scripts/offpage_authority_tracker.py --summary
```
