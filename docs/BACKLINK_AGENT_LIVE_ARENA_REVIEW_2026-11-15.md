# AI Tool Gems — Live Backlink Agent Review & Remediation Plan
**Review date:** 2026-11-15  
**Repository:** https://github.com/m-rehman55/ai-tool-gems  
**Inspected branch:** `main`  
**Observed repository commit in GitHub file results:** `130db6f35b58fc422ae4881bbbac833f9758c529`  
**Scope:** Existing off-page tracker, SOP, Telegram notifier/commands, GitHub Actions schedules, and owner-facing source-of-truth risks.

> This is a live source inspection and adversarial engineering review. It is not an official Claude Code Arena tournament. No GitHub writes, branch creation, PR, deployment, outreach, or account actions were completed.

## 1. Executive verdict

The repository already contains a useful starting system, but it is not yet an autonomous backlink acquisition and verification agent. It is currently a manual prospect tracker plus a weekly SOP, with a generic Telegram notifier and unrelated Telegram bot commands.

**Current readiness: 43/100 (engineering readiness estimate, not an external metric).**
- Existing foundations: 15/20
- Verification correctness: 3/20
- Safe discovery/connectors: 5/15
- Approval and auditability: 5/15
- Reporting/observability: 7/10
- Security/operations: 8/20

This score is deliberately stricter than the earlier written-brief score because the current source code has now been inspected directly.

## 2. Live findings — evidence from repository files

### Critical — false-positive backlink verification
File: `scripts/offpage_authority_tracker.py`

Current `verify_live()` downloads each `source_page`, decodes the body, and returns `True` when:
- HTTP response status is 200; and
- the response body contains the literal string `aitoolgems.tech`.

It does **not** parse anchors or verify:
- a real `<a href>` exists;
- the href resolves to the recorded `target_url`;
- the anchor text matches the recorded `anchor_text`;
- the destination survives redirects and remains the intended URL;
- `rel` tokens (`nofollow`, `sponsored`, `ugc`);
- source-page `noindex` / `X-Robots-Tag`;
- canonical destination or whether the placement has been removed.

Consequently, a plain paragraph mentioning the domain, a footer script, JSON-LD, or unrelated URL can be incorrectly counted as a live backlink. Do not trust current `live` labels as independently verified placements until the new verifier rechecks them.

### Critical — Telegram report data loss
File: `seo-agent/agent/telegram_notifier.py`

`send_message()` currently performs `text[:4000]` for messages longer than 4,000 characters. The comment says split, but the code truncates. This silently drops report details. Implement safe chunking with:
- chunk boundaries at newline/paragraph where possible;
- a hard ceiling below Telegram's message limit (e.g. 3,800 Unicode code points);
- ordered sequential sends;
- explicit partial-failure reporting and message IDs;
- no token leakage in error strings/logs;
- tests for long Unicode messages and failure on chunk N.

Do not blindly retry a `sendMessage` after an ambiguous network timeout: the first request may have succeeded, so retries can duplicate messages. If retrying, make the duplicate risk explicit or use a report/run identifier and owner-visible deduplication.

### Major — Telegram has no backlink approval workflow
Files:
- `marketing_agent/commands.py`
- `marketing_agent/cli.py`
- `.github/workflows/telegram-commands.yml`

The current command handler only implements general marketplace commands. It does not show:
- backlink queue summary;
- prospect detail / evidence display;
- approve/reject/defer actions;
- approval identity validation;
- idempotency or replay protection;
- confirmation receipts;
- an audit trail.

A Telegram approval command must be accepted only from a configured owner chat/user ID, not merely any private chat. Never approve an external submission based on a public channel message or untrusted callback data. The first release should support review/approve of **drafts only**; actual outreach or form submission remains owner-operated unless a later explicit policy enables a specific documented API.

### Major — shared state is committed to `main`
File: `.github/workflows/telegram-commands.yml`

The existing workflow has `contents: write`, checks out `main`, and commits `marketing_agent/data/bot-state.json` to `main`. Do not extend this shared state file to store backlink prospects, private contact data, owner notes, or approvals. Keep backlink state in a dedicated private store or, if using a repository branch, only public non-sensitive evidence and only after confirming repository visibility and access controls. Do not store private outreach data in a public branch/artifact.

### Major — unsafe / incomplete link-fetching boundary
The tracker currently fetches URLs from CSV using `urllib.request.urlopen`. A future verifier must treat CSV values as untrusted:
- accept only `https`;
- reject credentials in URLs, malformed hostnames, localhost, private, loopback, link-local, multicast, reserved and unspecified IP ranges;
- resolve hostnames and reject non-public resolved IPs;
- validate every redirect destination (not only the initial URL);
- cap redirects, response bytes, timeout, and per-host request rate;
- do not fetch `file:`, `ftp:`, `gopher:`, `data:`, or other schemes;
- respect robots.txt and site terms; never bypass CAPTCHA, login, paywall, bot challenge, or 403/429;
- avoid DNS rebinding by pinning or revalidating the resolved destination at connection time where feasible; document residual risk if standard-library networking cannot guarantee it.

Do not describe an SSRF guard as complete unless DNS resolution and redirect handling are tested.

### Major — scoring rubric conflict
File: `.agents/skills/off-page-authority-builder/SKILL.md`

The live SOP has an existing 100-point rubric:
- topical/regional relevance 0–25;
- editorial standards & organic visibility 0–25;
- direct brand/tool/dataset fit 0–20;
- non-spam / non-reciprocal compliance 0–15;
- indexable public profile or citation link 0–15.
Thresholds: 75–100 prioritize; 55–74 investigate; below 55 reject/skip.

Preserve this baseline until there is a versioned calibration dataset. Do not substitute another weighting system without a measured backtest and owner approval. A new rubric version should run in shadow mode first and compare decisions on the same prospect set.

### Major — owner-truth / outdated public claims
Files:
- `AGENTS.md`
- `docs/bing-webmaster/OFFPAGE_BACKLINK_EXECUTION_PACK.md`

The current `AGENTS.md` includes fixed USD pricing and crypto/card payment claims for international customers. This conflicts with the owner's more recent operating policy: Pakistan is the primary commercial market; international inquiries are welcome, but do not invent foreign prices, local offices, payment rails, or checkout capabilities. The old execution pack also says "verified PKR & USD pricing index" and lists payment methods beyond the owner's verified domestic methods.

Before any automated profile or outreach copy is created, use a controlled verified-facts file approved by the owner. At minimum:
- Pakistan: verified PKR offers and owner-confirmed domestic payment options only;
- international: inquiry/quote basis; do not claim a foreign fixed price or payment method unless the owner explicitly verifies it;
- no fake partnerships, offices, local presence, customer counts, rankings, backlink counts, or guarantees;
- distinguish "website lists" from "we sell/provide" and "independent reseller" accurately.

### Major — schedule inventory is inconsistent
Current `.github/workflows/seo-agent-daily.yml` cron is `17 22 * * *` UTC (03:17 PKT). `AGENTS.md` says 07:25 PKT for this workflow. The docs are stale. A new workflow must not duplicate existing jobs without a schedule map and overlap analysis.

The existing Telegram polling workflow runs every 30 minutes. This is periodic polling, not instant 24/7 service. Scheduled GitHub Actions are cloud executions, not a persistent daemon; the laptop can be off, but runs can be delayed or missed.

### Data quality — current tracker is not a verified backlink inventory
File: `seo-agent/data/offpage_authority_tracker.csv`

The CSV contains 15 rows and four rows labelled `live`. The evidence cells are dated 2026-11-12 and include notes such as "featured listing", GitHub profile/repo, and DEV.to article. These are tracker assertions, not proof that the current page still contains the expected anchor. Re-verify each record using the corrected parser before reporting it as live. Preserve the original notes and record new verification evidence separately; do not erase historical evidence.

### Minor — tracker validation needs stricter types
Current validation does `int(row["relevance"])` without a controlled validation error path. A malformed cell can crash validation instead of producing a row-specific error. It also does not validate allowed values for action status, link status, dates, URLs, duplicate prospects, or target-domain consistency. Add schema validation and clear error messages while preserving existing columns or migrating with an explicit schema version.

## 3. Arena-inspired adversarial review

This review uses three independent engineering lenses, then reconciles them. It is not a claim that three external agents or the official Arena tool ran.

| Lens | Strongest concern | Required decision |
|---|---|---|
| Growth / SEO | More prospects are useless if links are irrelevant, noindex, reciprocal, or non-editorial | Quality-first discovery, preserve current rubric, no bulk blasts |
| Reliability / QA | Current verifier can label plain-text mentions as backlinks | Parse anchors, classify rel, test redirect/removal/noindex cases |
| Security / privacy | User-controlled URLs and public workflow state can expose internal endpoints or private contact data | SSRF controls, owner-only approvals, no private data in public artifacts |

**Reconciled architecture:** extend the existing tracker and reuse the existing Telegram notifier/client, but isolate the backlink package and state. Do not create a second unrelated tracker or a second Telegram bot. Do not add a second overlapping daily workflow until the existing schedules and runtime are reconciled.

## 4. Target system — phased and bounded

### Phase 0 — truth and safety
- Add `backlink_agent/config/verified_facts.yml` or equivalent, owner-approved, with last-reviewed date and evidence references.
- Add kill switch `BACKLINK_AGENT_ENABLED=false` by default.
- Add `BACKLINK_AGENT_MODE=report_only` default.
- No submissions, outreach, website edits, blog edits, PR creation, or social publishing in Phase 0.
- Use the existing tracker as source of truth; do not fork a second CSV/database.

### Phase 1 — verification correctness
- Add a dedicated verifier module using `html.parser.HTMLParser`.
- Resolve relative hrefs against source URL.
- Normalize scheme/host/default port/path and fragment safely; do not strip meaningful query strings.
- Match actual href against target URL, with explicit handling for trailing slash and canonical aliases.
- Capture anchor text, rel tokens, source HTTP status, final source URL, redirect chain, `X-Robots-Tag`, robots meta, canonical, fetch timestamp, response bytes, and error class.
- Classify: `live_follow`, `live_nofollow`, `live_sponsored`, `live_ugc`, `live_mixed`, `removed`, `wrong_target`, `source_noindex`, `blocked_robots`, `blocked_access`, `redirect_error`, `fetch_error`, `unsafe_url`, `unknown`.
- A live link means an actual matching anchor exists. Do not imply a nofollow link passes ranking credit.
- Never overwrite historic evidence; append a verification event to a JSONL/SQLite audit log.

### Phase 2 — discovery
Build small, explicit, compliant adapters only. Candidate sources:
- GitHub API for curated-list repositories, contribution guides, and open issues (API and rate limits);
- public RSS/Atom feeds from relevant Pakistan tech/startup publications;
- manually curated publisher/resource pages;
- public directories only when terms permit and the current rubric qualifies them;
- user-provided exports from Bing Webmaster Tools, GSC, Ahrefs/Semrush (if user has them; do not require paid subscriptions).

Do not scrape Google SERPs, automate account signups, bypass CAPTCHA, scrape behind logins, or infer email addresses. Each adapter must document terms, rate limit, fields collected, source URL, retrieval time, and failure mode. Do not claim complete web coverage.

### Phase 3 — prospect scoring and content fit
- Use the existing 100-point rubric, version `rubric-v1`.
- Match every prospect to one genuine asset: `/prices/`, CSV/JSON dataset, a relevant guide, methodology, or specific tool page.
- Generate a tailored value proposition from verified facts only.
- Reject duplicate domain+target+placement combinations.
- Keep a human-readable reason for every score component.
- A score alone cannot authorize outreach.

### Phase 4 — owner review and Telegram
Commands proposed:
- `/backlinks` — queue summary only;
- `/backlink <id>` — show prospect, score breakdown, evidence, target asset, draft copy, and risk flags;
- `/approve <id>` — approve a draft for owner execution only;
- `/reject <id> <reason>` — reject and record reason;
- `/defer <id> <date>` — defer;
- `/backlink_report` — send current report and evidence link.

Security:
- allow only configured `TELEGRAM_OWNER_CHAT_ID` and, where available, configured Telegram user ID;
- reject group/channel chats;
- constant-time compare where applicable;
- validate command arguments and prospect IDs;
- approvals expire when the draft or evidence changes;
- every decision records update ID, owner identity, timestamp PKT, item ID, version/hash, action, and previous status;
- make command processing idempotent;
- do not expose contact details or private notes in a public artifact;
- do not treat a Telegram approval as approval for paid links, account signup, or mass submissions.

### Phase 5 — cloud schedule and reports
- Reuse an existing workflow slot only after verifying schedule overlap and job runtime.
- GitHub Actions is scheduled cloud execution; not an always-on daemon. Laptop may be off, but schedules can be delayed/missed.
- Add `workflow_dispatch` for manual report-only runs.
- Use least-privilege permissions; report-only job should use `contents: read`.
- Use `concurrency` to prevent overlapping backlink runs.
- Set timeout, max prospects/run, max requests/domain, request timeout, response byte cap, and retry budget.
- Persist only non-sensitive evidence; never store secrets or private outreach data in workflow artifacts.
- Send Telegram report in chunks and attach a full report artifact/link.
- Include run ID, UTC and PKT timestamps, code version, rows scanned, candidates found, deduplicates, scores/reasons, verification classifications, blocked requests, errors, and source coverage limitations.
- If Telegram delivery fails, preserve the report artifact and fail the job visibly; do not mark report delivered.

### Phase 6 — learning
- Weekly cohort analysis only after enough verified observations.
- Measure accepted placements, live-link retention, relevant referral sessions, conversions (if attributable), and editorial quality.
- Do not treat DR/DA, number of submissions, or raw backlink count as success.
- Scoring changes are proposed in a versioned report and run in shadow mode; no autonomous self-modification.

## 5. Acceptance tests — release blockers

### Link verification
- Plain-text `aitoolgems.tech` mention with no anchor => not live.
- Anchor to wrong URL => wrong_target.
- Relative href to correct target => recognized.
- `nofollow`, `sponsored`, `ugc`, combinations => classified exactly.
- Anchor removed => removed.
- 301/302 source redirect => final URL and chain recorded.
- Source `noindex` or `X-Robots-Tag: noindex` => noindex status.
- Non-200, timeout, TLS error, malformed HTML => explicit non-live state.
- Target query/fragment normalization behaves as specified.
- Invalid schemes, localhost, private IP, IPv6 loopback, metadata IP, and redirect-to-private => blocked.
- response byte cap and redirect cap enforced.

### Telegram
- Unconfigured bot => safe skip with no secret leakage.
- 4k/8k/20k Unicode messages => all chunks delivered in order or explicit partial failure.
- Simulated failure on second chunk => first message ID retained, failure reported.
- Non-owner private chat => rejected.
- Group chat => rejected.
- Replayed update => no duplicate approval.
- Stale draft/hash => approval rejected.
- Invalid IDs/commands => safe response.

### Workflow
- default run is report-only and disabled until explicitly enabled;
- no write permission in report-only workflow;
- no `main` push;
- no paid API environment variables required;
- no site/blog content changed;
- concurrency and timeout work;
- artifact retention bounded;
- secrets absent from logs/artifacts/Telegram;
- run works with laptop off;
- missed/delayed schedule is reported honestly.

## 6. Existing repository components to reuse

| Component | Current role | Decision |
|---|---|---|
| `scripts/offpage_authority_tracker.py` | CSV validation, summary, weak live check | Keep; replace verifier implementation |
| `seo-agent/data/offpage_authority_tracker.csv` | Existing 15-prospect tracker | Keep as source of truth; add schema migration only if necessary |
| `.agents/skills/off-page-authority-builder/SKILL.md` | Existing 100-point rubric and SOP | Keep rubric; revise verification/approval policy |
| `seo-agent/agent/telegram_notifier.py` | SEO report notifier | Fix chunking; don't truncate |
| `marketing_agent/telegram.py` | Shared Telegram Bot API client | Reuse where compatible; add safe multi-message helper with tests |
| `marketing_agent/commands.py` | General marketplace commands | Add owner-only backlink commands only after secure auth and idempotency |
| `.github/workflows/telegram-commands.yml` | 30-minute polling, cursor commit to main | Do not put backlink private state here |
| `.github/workflows/seo-agent-daily.yml` | Daily HERMES workflow | Do not duplicate; schedule docs need reconciliation |

## 7. Owner decisions still required before activation
1. Confirm the exact Telegram owner chat/user ID to authorize approvals.
2. Confirm whether repository visibility permits any prospect evidence to be stored in Git.
3. Confirm the verified-facts source-of-truth values for international offers and payment methods.
4. Confirm whether the agent may only draft submissions or may later submit to explicitly named free APIs.
5. Confirm the maximum daily request budget and whether public RSS/API sources are acceptable.

Until then, keep `report_only`, disabled, and no-outreach defaults.

## 8. Operational truth
- GitHub connector reads succeeded for the listed files.
- Attempt to create a separate GitHub branch was rejected by GitHub API with HTTP 403 `Resource not accessible by integration`. No repository files were changed and no PR was created.
- The official Claude Code Arena Skill was not executable in this ChatGPT environment. The above review is Arena-inspired, not an official 16-competitor tournament.
- No live network backlink probes were executed in this pass. The current four `live` tracker labels therefore remain unconfirmed by this review.
