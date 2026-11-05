# CONTENT APPROVAL & EDITORIAL GOVERNANCE POLICY
**Standard**: Zero Fabricated Content, Fail-Closed Publishing Gates  

---

## 1. Content Queue & Approval Workflow

1. **Queue Location**: `data/seo/content-queue.json`
2. **Explicit Human Approval Gate**:
   - An article candidate is ONLY eligible for publication if `"approved_for_publishing": true` is explicitly present in the queue file.
   - Any dynamic fallback discovery that synthesizes topic ideas must add them to the queue as `"approved_for_publishing": false` (or omit the flag).
   - **Self-Approval is Strictly Prohibited**: Scripts and agents are forbidden from mutating `"approved_for_publishing"` to `true` autonomously.
3. **Fail-Closed on Queue Exhaustion**:
   - When no pre-approved, unwritten candidates exist, the publisher must terminate gracefully with status `NO_ELIGIBLE_TOPIC` without publishing.

---

## 2. Dynamic AI Generation & Failure Handling

1. **AI Editorial Section**:
   - Guides leverage Google Gemini 2.0 Flash to synthesize deep, localized, original analysis (500+ words) addressing specific Pakistani creator and agency use-cases.
2. **Handling Gemini Generation Failure**:
   - If `GEMINI_API_KEY` is missing, quota is exceeded, or all API attempts fail:
     - The publisher **MUST NOT** proceed to publish a blank or thin templated placeholder guide.
     - The publisher must save the candidate as a draft in `data/seo/drafts/` and flag the task as `BLOCKED_PENDING_CREDENTIALS` or `FAILED`.
     - An alert must be dispatched via Telegram to the owner.

---

## 3. Pull Request Requirement for Content Deployment

1. **No Direct Push to `main`**:
   - Newly generated guides must be committed to a dedicated content branch (e.g., `content/guide-<slug>`).
   - A pull request must be generated automatically via GitHub API or workflow containing:
     - Article title, target keyword, and meta description.
     - Link graph validation report.
     - Schema validation report.
     - Pakistani payment rail compliance certificate.
2. **Production Merge**:
   - Guide goes live on `https://aitoolgems.tech/` only upon PR merge.
