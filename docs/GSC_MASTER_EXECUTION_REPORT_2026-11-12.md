# GSC Master Execution Report — 2026-11-12

- **Branch:** `feat/gsc-full-ranking-execution`
- **Baseline Commit:** `2a43235` (`origin/main`, synced after PRs #47–#52)
- **Status:** Ready for human review & PR approval (not pushed, merged, or deployed)

---

## 1. Executive Summary

This branch executes the prioritized GSC Search Console, AI Overview (AEO/GEO), internal linking, snippet/CTR, and accessibility execution plan across 25 HTML/test files plus this report, leaving `attribution.js`, WhatsApp checkout flows, payment/warranty terms, Cursor AI pricing (`Rs. 2,800`), and unrelated product pages untouched.

Key outcomes verified locally:
- **Resolved `claude subscription pakistan` intent split** between commercial [`tools/claude/index.html`](../tools/claude/index.html) and informational [`guides/claude-ai-pakistan/index.html`](../guides/claude-ai-pakistan/index.html) while preserving test-locked `<title>`, `<meta description>`, `headline`, and `dateModified` (`2026-11-11`) on the guide.
- **Rewrote broken template copy & comparison matrix** in [`guides/elevenlabs-voice-ai-pakistan/index.html`](../guides/elevenlabs-voice-ai-pakistan/index.html) (replacing off-topic image-design criteria and Leonardo/Canva/Adobe comparison rows with authentic voice synthesis, Urdu/English narration benchmarks, and creator audio/video stack rows matching visible FAQ and JSON-LD `FAQPage`).
- **Fixed [`tools/bolt-new/index.html`](../tools/bolt-new/index.html)** from an oversized `79`-char title, typo (`"international international card"`), and reseller-style `<del>Rs. 7,500</del>` markup to an accurate `66`-char Official Vendor Directory listing (`$0` Free / `$20/mo` Pro `~Rs. 5,600`).
- **Cleaned [`guides/ai-tools-price-pakistan/index.html`](../guides/ai-tools-price-pakistan/index.html)** (removed stray `>` before breadcrumbs, refreshed to `12 November 2026`, clarified marketplace vs official vendor USD scope, and added contextual catalog links inside `#categories`).
- **Increased topical inbound links** across all 6 priority discoverability targets from contextual guides and product pages (no nav/footer bloat).
- **Fixed WCAG 2.5.3 Label-in-Name hero accessibility mismatch** in [`index.html`](../index.html) and updated the 4 literal assertions in [`tests/test_ui_interactions.py`](../tests/test_ui_interactions.py).

---

## 2. Modified Files & Scope

| File | Category | Reason |
| :--- | :--- | :--- |
| `tools/claude/index.html` | Intent Split / CTR / AEO | Owns transactional `"Claude Pro Subscription Price in Pakistan (Rs. 2,200)"` title, H1, quick-answer & cross-links guide |
| `guides/claude-ai-pakistan/index.html` | Intent Split / AEO | Shifted H1, `.lead`, `.quick-answer-card` to card declines/access rules; links `../../tools/claude/` |
| `tools/linkedin/index.html` | CTR / AEO Clarity | Updated H1 (`Rs. 1,500 Voucher`), Career/Business/Sales Navigator clarity, `2026-11-12` review date |
| `tools/leonardo/index.html` | Sync / AEO Clarity | Synced OG/Twitter/WebPage meta, clarified private account vs standalone keys & November 2026 date |
| `tools/adobe/index.html` | Sync / AEO Clarity | Synced OG/Twitter/WebPage meta, clarified All Apps bundle includes Illustrator/Photoshop vs single-app/official USD |
| `tools/chatgpt/index.html` | AEO / Fact Hygiene | Synced OG/Twitter/WebPage meta, clarified OpenAI `$20`/`$200 Pro` vs Rs. 2,300 Plus, replaced outdated no-real-time-internet bullet, preserved locked strings |
| `tools/bolt-new/index.html` | Directory Accuracy / CTR | Shortened title (`79`→`66` chars), updated H1 & `.quick-answer`, removed `<del>Rs. 7,500</del>` strikethrough, fixed typo, replaced reseller policy box with vendor notice |
| `guides/elevenlabs-voice-ai-pakistan/index.html` | Content Repair / AEO | Replaced image-generation template bugs & table with authentic voice synthesis, Urdu/English narration & voice/video matrix + synced FAQ schema |
| `guides/ai-tools-price-pakistan/index.html` | Hygiene / Linking | Removed stray `>` before breadcrumbs, updated date/scope note, added contextual catalog links in `#categories` |
| `index.html` | Accessibility (WCAG 2.5.3) | Aligned 4 hero floating card `aria-label` strings with visible card text |
| `tests/test_ui_interactions.py` | Test Alignment | Updated 4 literal `aria-label` assertions in `tests/test_ui_interactions.py` to match [`index.html`](../index.html) |
| `tools/elevenlabs/index.html` | Contextual Linking | Added `../../guides/elevenlabs-voice-ai-pakistan/` hub pill |
| `tools/lovable/index.html` | Contextual Linking | Linked `../bolt-new/` inside related-tools comparison |
| `guides/creators/index.html` | Contextual Linking | Linked ElevenLabs (`tool` + `guide`), Leonardo AI, and Adobe Creative Cloud |
| `guides/best-ai-video-generators-pakistan/index.html` | Contextual Linking | Linked `../elevenlabs-voice-ai-pakistan/` and `../../tools/leonardo/` |
| `guides/heygen-ai-video-pakistan/index.html` | Contextual Linking | Added `../elevenlabs-voice-ai-pakistan/` in Related |
| `guides/developers/index.html` | Contextual Linking | Added `/tools/bolt-new/` in Related |
| `guides/lovable-vs-replit-pakistan/index.html` | Contextual Linking | Added `../../tools/bolt-new/` in Related |
| `guides/cursor-ai-pakistan/index.html` | Contextual Linking | Added `../../tools/bolt-new/` in Related |
| `guides/ai-tools-pakistan/index.html` | Contextual Linking | Linked Claude (`tool` + `guide`), ChatGPT, Bolt.new, Leonardo AI, Adobe |
| `guides/ai-subscriptions-pakistan/index.html` | Contextual Linking | Added `/guides/claude-ai-pakistan/` in Related |
| `guides/deepseek-ai-pakistan/index.html` | Contextual Linking | Added `../claude-ai-pakistan/` in Related |
| `guides/businesses/index.html` | Contextual Linking | Added `/tools/linkedin/` in Related |
| `guides/productivity/index.html` | Contextual Linking | Added `/tools/linkedin/` in Related |
| `guides/canva-vs-figma-pakistan/index.html` | Contextual Linking | Linked Adobe Creative Cloud and Leonardo AI inline |

---

## 3. Claude Intent Split Verification

- **Commercial destination (`/tools/claude/`):** Now directly targets `"Claude Pro Subscription"` pricing/purchase intent (`Title: Claude Pro Subscription Price in Pakistan (Rs. 2,200)`, `H1: Claude Pro Subscription & Price in Pakistan (Rs. 2,200)`, updated description & quick-answer highlighting `Rs. 2,200` / 1-month private account via EasyPaisa, JazzCash, SadaPay, Raast IBFT + `7-day` replacement warranty), while pointing informational readers to `../../guides/claude-ai-pakistan/`.
- **Informational guide (`/guides/claude-ai-pakistan/`):** Kept test-locked `<title>`, `<meta description>`, `headline`, and `dateModified` (`2026-11-11`) intact so existing regression gates pass, while reframing the visible `<h1>` (`Claude Pro in Pakistan: Card Declines, Access Rules & Buying Guide`), `.lead`, and `.quick-answer-card` cleanly around card-decline troubleshooting, access models, and official USD vs assisted PKR tradeoffs, with a natural link (`../../tools/claude/`) for ready buyers.

---

## 4. Before / After Title, Meta Description, H1 & AEO Updates

| Page | Field | Before (`origin/main` `2a43235`) | After (`feat/gsc-full-ranking-execution`) |
| :--- | :--- | :--- | :--- |
| `tools/claude/index.html` | Title | `Claude Pro Price in Pakistan (Rs. 2,200) \| AI Tool Gems` (55c) | `Claude Pro Subscription Price in Pakistan (Rs. 2,200)` (53c) |
| `tools/claude/index.html` | Meta | `Check Claude Pro price in Pakistan. 1 Month private access on personal email for Rs. 2,200 PKR via EasyPaisa, JazzCash, or SadaPay. 7-day warranty.` (147c) | `Order a 1-month private Claude Pro subscription in Pakistan for Rs. 2,200 PKR via EasyPaisa, JazzCash, or SadaPay. Includes 7-day replacement warranty.` (151c) |
| `tools/claude/index.html` | H1 | `Claude Pro Price in Pakistan (Rs. 2,200) \| 1 Month Private Access` | `Claude Pro Subscription & Price in Pakistan (Rs. 2,200)` |
| `guides/claude-ai-pakistan/index.html` | Title / Meta | Locked (`76`c entity-decoded / `139`c) | Preserved for regression locks |
| `guides/claude-ai-pakistan/index.html` | H1 | `Claude Pro in Pakistan: Pricing, Card Declines & Buying Guide` | `Claude Pro in Pakistan: Card Declines, Access Rules & Buying Guide` |
| `tools/linkedin/index.html` | Title / Meta | `LinkedIn Premium Price in Pakistan (Rs. 1,500) \| AI Tool Gems` (61c) / `Check LinkedIn Premium price...` (152c) | Preserved (regression-locked); sharpened `.lead` & `p.quick-answer` for Career/Business/Sales Navigator clarity |
| `tools/linkedin/index.html` | H1 | `LinkedIn Premium Voucher & Subscription Price in Pakistan` | `LinkedIn Premium Cost & Price in Pakistan (Rs. 1,500 Voucher)` |
| `tools/leonardo/index.html` | Title / Meta / H1 | `Leonardo AI Price in Pakistan (Rs. 1,900) \| Essential Plan` (58c) / `155`c / unchanged H1 | Locked tags preserved; synced OG/Twitter/WebPage meta; updated `p.quick-answer` (`8,500` credits private account vs no standalone keys, November 2026) |
| `tools/adobe/index.html` | Title / Meta / H1 | `Adobe Illustrator & Creative Cloud Price in Pakistan (Rs. 1,700)` (64c) / `130`c | Locked tags preserved; synced OG/Twitter/WebPage meta; sharpened `p.quick-answer` (All Apps bundle vs single-app & official Adobe USD) |
| `tools/chatgpt/index.html` | Title / Meta / H1 | `ChatGPT Plus Price in Pakistan (Rs. 2,300) \| Plus vs Pro` (56c) / `153`c | Locked tags preserved; synced OG/Twitter/WebPage meta; clarified OpenAI `$20` Plus vs `$200 Pro` vs `Rs. 2,300`; removed stale no-real-time-internet limitation |
| `tools/bolt-new/index.html` | Title | `Bolt.new - Pricing, Features, Review & Pakistan Availability \| AI Tool Gems` (79c raw) | `Bolt.new in Pakistan: Official Pricing & Review \| AI Tool Gems` (66c raw) |
| `tools/bolt-new/index.html` | Meta | `Explore Bolt.new by StackBlitz, Inc.. Verified review, official pricing ($20 / month (Pro)), key features, limitations, and access in Pakistan.` (143c) | `Bolt.new by StackBlitz costs $0 (Free) or $20/mo Pro (~Rs. 5,600 PKR) directly on bolt.new. Directory guide for Pakistani devs using SadaPay or NayaPay.` (152c) |
| `tools/bolt-new/index.html` | H1 | `Bolt.new Price in Pakistan (Rs. 5,600) & Review (2026)` | `Bolt.new in Pakistan: Official Pricing ($0 / $20 Pro) & Review` |
| `guides/elevenlabs-voice-ai-pakistan/index.html` | Title | `ElevenLabs Voice AI in Pakistan: Pricing, Urdu Support & Guide` (62c) | `ElevenLabs Voice AI in Pakistan: Urdu Support & PKR Pricing` (63c raw) |
| `guides/elevenlabs-voice-ai-pakistan/index.html` | Meta | `Complete guide to ElevenLabs Voice AI in Pakistan. Review character plans in PKR, Urdu voice cloning, and payment via EasyPaisa and JazzCash.` (141c) | `Compare ElevenLabs Voice AI access in Pakistan (Rs. 3,300/mo for 30,000 characters), Urdu & English narration fit, and local PKR billing options.` (149c) |
| `guides/elevenlabs-voice-ai-pakistan/index.html` | H1 | `ElevenLabs Voice AI in Pakistan: Pricing, Urdu Support & Guide` | `ElevenLabs Voice AI in Pakistan: Urdu Support & PKR Pricing` |
| `guides/ai-tools-price-pakistan/index.html` | Title / Meta / H1 | `44`c / `137`c / `AI tools prices in Pakistan: compare 20 current listings.` | Preserved; removed stray `>`, updated date to `12 November 2026`, clarified scope note & added `#categories` contextual links |

---

## 5. Internal Link Deltas (Priority Targets)

Measured across HTML files before vs after edits using static HTML anchor inspection:

| Target URL | Inbound Links Before | Inbound Links After | Distinct Source Files After | New Contextual Sources Added |
| :--- | :---: | :---: | :---: | :--- |
| `/guides/elevenlabs-voice-ai-pakistan/` | 4 | **11** | **8** | `tools/elevenlabs/index.html`, `guides/creators/index.html`, `guides/best-ai-video-generators-pakistan/index.html`, `guides/heygen-ai-video-pakistan/index.html`, `guides/ai-tools-price-pakistan/index.html` |
| `/tools/bolt-new/` | 8 | **14** | **12** | `guides/developers/index.html`, `guides/lovable-vs-replit-pakistan/index.html`, `guides/cursor-ai-pakistan/index.html`, `tools/lovable/index.html`, `guides/ai-tools-pakistan/index.html`, `guides/ai-tools-price-pakistan/index.html` |
| `/guides/claude-ai-pakistan/` | 9 | **15** | **12** | `guides/ai-tools-pakistan/index.html`, `guides/ai-subscriptions-pakistan/index.html`, `guides/deepseek-ai-pakistan/index.html`, `guides/ai-tools-price-pakistan/index.html` |
| `/tools/linkedin/` | 11 | **14** | **10** | `guides/businesses/index.html`, `guides/productivity/index.html`, `guides/ai-tools-price-pakistan/index.html` |
| `/tools/leonardo/` | 20 | **26** | **20** | `guides/creators/index.html`, `guides/best-ai-video-generators-pakistan/index.html`, `guides/ai-tools-pakistan/index.html`, `guides/canva-vs-figma-pakistan/index.html`, `guides/ai-tools-price-pakistan/index.html` |
| `/tools/adobe/` | 23 | **27** | **21** | `guides/creators/index.html`, `guides/ai-tools-pakistan/index.html`, `guides/canva-vs-figma-pakistan/index.html`, `guides/ai-tools-price-pakistan/index.html` |

Zero `/jp/`, `terms.html`, or `privacy.html` references exist in any public HTML file.

---

## 6. Legacy URL Validation-Readiness Table (`/jp/`, `terms.html`, `privacy.html`)

GSC UI recorded 21 non-indexed URLs (including 14 deleted `/jp/` 404s, 5 active `/jp/` Removals, redirect/alternate canonical variants, and legacy `.html` legal paths). On GitHub Pages static hosting:

| Legacy Pattern / Path | Count | Live Repo Status | Sitemap / Internal Links | GSC Validation Readiness |
| :--- | :---: | :--- | :--- | :--- |
| `/jp/*` (retired Japan locale) | 14 (404) / 5 Removals | Removed from site; serves `404.html` (`noindex, follow`) | `0` internal links; excluded by `sitemap.xml` & scope guard tests | Expected `404`; do NOT recreate; click **Validate Fix** only if appropriate once GSC finishes purging legacy `/jp/` URLs |
| `/terms.html` | 1 | Not in repo; canonical page is `/terms-of-service/` | `0` public HTML links (`terms-of-service/` used across public HTML) | Canonical `/terms-of-service/` indexed; legacy `.html` stays 404 (no fake HTML redirect hack needed unless server rules added) |
| `/privacy.html` | 1 | Not in repo; canonical page is `/privacy-policy/` | `0` public HTML links (`privacy-policy/` used across public HTML) | Canonical `/privacy-policy/` indexed; legacy `.html` stays 404 |
| `/tools/bolt-new/` | 1 summary note | Live directory HTML + schema | `14` inbound links; listed in `sitemap.xml` | Already confirmed `URL is on Google` / indexed (`2026-11-10`) via live URL Inspection API |

---

## 7. Accessibility Fix & Test Transparency Note

- **Fix (`index.html` hero floating cards):** Lighthouse flagged `label-content-name-mismatch` because the `aria-label` strings (`"Explore ChatGPT Plus"`, `"Explore Canva Pro"`, etc.) omitted the visible category labels (`"AI assistant"`, `"Design"`, etc.) inside the floating cards. Updated all 4 floating cards to include the full visible text (`"Explore AI assistant ChatGPT Plus"`, `"Explore Design Canva Pro"`, `"Explore Video editing CapCut Pro"`, `"Explore UI / UX Figma Pro"`), satisfying WCAG 2.5.3 Label in Name.
- **Transparency Note (`tests/test_ui_interactions.py`):** Four existing literal substring assertions in [`tests/test_ui_interactions.py`](../tests/test_ui_interactions.py) expected the old shorter `aria-label` strings and were updated to match the WCAG-compliant labels.

---

## 8. QA Verification Results (Post-Final-Edit)

| Check / Suite | Scope | Exact Result | Notes |
| :--- | :--- | :--- | :--- |
| `python -m unittest discover -s tests -v` | `tests/` full suite | **119 run: 117 ok, 1 skipped, 1 pre-existing fail** | **Skipped:** `test_symlink_escape_rejected` (`Symlinks cannot be created without elevated privileges on this host`). **Pre-existing failure (unmodified gitignored local file only):** `test_batch3_technical_and_content_hygiene` on `data/snapshots/snap_20261106_173647_auto/index.html` (`"hasMerchantReturnPolicy"`), identical on clean `origin/main` `2a43235`. Zero tracked repo test failures. |
| `python -m unittest discover -s seo-agent/tests -v` | SEO Agent safety/audit | **43 / 43 OK** | Test-generated side-effect diff on `remediation_learnings.json` reverted cleanly |
| `python -m unittest discover -s keyword_agent/tests -v` | Keyword Agent | **25 / 25 OK** | Clean pass |
| `python -m unittest discover -s marketing_agent/tests -v` | Marketing Agent | **33 / 33 OK** | Clean pass |
| `python -m unittest tests/test_offpage_authority.py -v` | Off-Page Tracker & `/prices/` datasets | **4 / 4 OK** | Verified after edits |
| `python scripts/link_graph_checker.py --strict` | Site link graph | **0 errors** | `129` HTML files, `4,555` links, `1,226` anchors, `461` local assets, `111` sitemap URLs |
| `python audit_all.py` | Technical HTML/SEO audit | **0 errors, 0 warnings** | `131` HTML files clean |
| `python schema_audit.py` | JSON-LD completeness | **130 / 130 (100.0%)** | `6475 / 6475` score |
| `python scripts/build_public_site.py --verify-only` | Public allowlist build | **PASSED** | `409` public files staged, `0` security policy violations |
| `python scripts/validate_content.py guides/elevenlabs-voice-ai-pakistan/index.html` | Content validator | **PASSED** | Clean pre-publish check on rewritten guide |

---

## 9. Live Backlink Verification Status (`seo-agent/data/offpage_authority_tracker.csv`)

Verified live via HTTP probes (`2026-11-12`):

| Channel / Domain | Source URL | Link Status | Notes |
| :--- | :--- | :--- | :--- |
| `github.com` (Repo Entity) | `https://github.com/m-rehman55/ai-tool-gems` | `live` | HTTP 200; 5 links to `aitoolgems.tech` verified; GSC `0` external links yet (pending crawl) |
| `github.com` (Profile Entity) | `https://github.com/m-rehman55` | `live` | HTTP 200; 6 links verified |
| `agentwebmap.com` (`llms.txt` directory) | `https://agentwebmap.com/domain/aitoolgems.tech` | `live` | HTTP 200; 11 anchor mentions verified |
| `dev.to` (Technical Case Study) | `https://dev.to/mrehman55/building-a-machine-readable-ai-tools-pricing-index-for-pakistan-csv-json-llmstxt-1d2f` | `live` | HTTP 200; 5 links to `/prices/` verified |
| `github.com/eudk/awesome-ai-tools` | PR `#944` | `not_live` | `submitted_pending_review` (maintainer merge needed) |
| `startupnetwork.pk` | Listing `#2074` | `not_live` | `submitted_pending_review` (timed out during automated probe) |
| `saashub.com` / `hashnode.com` / `startups.pasha.org.pk` | Manual / blocked | `not_live` | `needs_owner_account` / `draft_ready` / `blocked_tls_error` |

---

## 10. Remaining Post-Approval Actions (For Review & Deploy Phase)

1. **Human Review & Merge:** Review commit on `feat/gsc-full-ranking-execution`, push branch, open/merge PR into `main`, and verify live deployment on `https://aitoolgems.tech/`.
2. **GSC URL Inspection Recrawl Requests (after deploy):** Request indexing for updated URLs:
   - `/tools/claude/`
   - `/tools/bolt-new/`
   - `/tools/chatgpt/`
   - `/tools/adobe/`
   - `/guides/elevenlabs-voice-ai-pakistan/`
   - `/guides/ai-tools-price-pakistan/`
   - `/` (homepage hero WCAG update)
   *(Note: `/guides/claude-ai-pakistan/`, `/tools/linkedin/`, `/tools/leonardo/` already had indexing requests queued in GSC during audit on `2026-11-12`; re-request if needed after live deploy.)*
3. **Off-Page Follow-Up:** Monitor GitHub `awesome-ai-tools` PR `#944` & `startupnetwork.pk` `#2074`, publish ready Hashnode article referencing `/prices/`, and wait for Google to crawl the 4 verified live external backlinks so GSC External Links updates above `0`.
