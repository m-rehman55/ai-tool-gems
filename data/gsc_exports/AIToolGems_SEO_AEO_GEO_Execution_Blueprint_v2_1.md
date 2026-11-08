# AIToolGems SEO / AEO / GEO Execution Blueprint v2.1
**Date:** 6 November 2026  
**Domain:** https://aitoolgems.tech/  
**Repository inspected:** https://github.com/m-rehman55/ai-tool-gems (main branch)  
**Scope:** 175 canonical parents + 2,902 supplier rows + technical SEO, Google Search/AI reports, analytics, Merchant Center and Ads gates.

> This v2.1 register is rebuilt from the files available in this conversation. The original v2.0 `.xlsx` workbook was not supplied, so this is not a direct patch of that workbook. All 175 rows deliberately stay HOLD / needs_review. A score or research hypothesis is not a publishing approval. Rankings, AI citations and rich results cannot be guaranteed.

## 1. What was actually verified

| Area | Evidence-backed result |
|---|---:|
| Canonical parent tools in master directory | 175 |
| Raw supplier rows | 2,902 |
| Unique supplier listing-name strings | 1,619 |
| Distinct supplier bots | 15 |
| Category silos in master directory | 13 |
| Existing tool directories in GitHub repo | 40 |
| Mapped parent-tool pages in keyword map | 39 |
| Category URLs in repository tree / sitemap | 0 |
| Sitemap URLs | 96 |
| Guide URLs in sitemap | 41 |
| Repeated generic primary-use sentence in source master | 149/175 |
| Missing supplier Product IDs | 126 |
| Missing supplier descriptions | 93 |
| Zero-priced supplier rows | 126 |
| Strict numeric stock rows | 2,688 |
| Strict numeric zero-stock rows | 645 |
| Numeric stock sum (strict numeric cells only) | 126,591 |
| `999 (Invite)` sentinel rows | 97 |
| `In Stock` text-only rows | 117 |
| Invite prefix total if treated as 999 each | 96,903 |
| Headline arithmetic if invite sentinels are added | 223,494 |

### Supplier inventory interpretation

The master directory's 223,494 headline can be reconstructed as **126,591 strict numeric stock + 97 × 999 Invite = 223,494**. That arithmetic is not proof of available fulfilment. `999 (Invite)` is a sentinel/status token, not a verified inventory quantity; `In Stock` is also text-only. Therefore `verified_fulfillable_units` remains blank until a real SKU-level fulfilment check is logged. Supplier `Status=Live` is not proof that the exact offer can be delivered to a customer.

The 2,902 rows are maintained in a separate **private Offer Ledger**. Parent-level summaries cannot decide plan term, price, access, rights, Merchant Center or Ads eligibility. The parent register and per-offer ledger must stay separate.

## 2. Critical architecture corrections

1. **Parent URL ≠ supplier SKU.** Keep one canonical `/tools/<slug>/` page per genuine parent tool. Multiple durations, credit bundles, invite slots, top-ups and account models remain offer-level variants. Do not create a URL for each reseller string.
2. **Category hubs are not present yet.** The repo tree and sitemap show zero `/category/` routes despite 13 master categories. The workbook gives 13 recommended route slugs; each hub stays MISSING / not indexable until it has a distinct selection method, comparison criteria, real current entries, helpful FAQs and unique content.
3. **Noindex is preferable to a low-value indexable page.** A parent row with no verified offer can remain in an editorial directory only if it has real informational value; otherwise keep it out of the sitemap and noindex/omit it. Do not manufacture 175 storefront pages solely from a supplier list.
4. **Use contextual links, not artificial rigid silos.** Category pages should prioritize their vertical but cross-link when the user journey naturally requires it (e.g., video + voice + editing workflows).

## 3. SEO / AEO / GEO — what actually helps

Google states that generative AI features are rooted in core Search ranking and quality systems. Retrieval and query fan-out can generate related searches, but Google specifically cautions against producing a separate thin page for every fan-out query. `llms.txt`, special AI markup, fixed word counts and mandatory content chunking are not Google ranking requirements.  
Official guide: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide

Use a **single useful parent page** to answer the relevant related questions:
- What exactly is the official product and developer?
- Which current official plan/model is being discussed?
- What does the exact seller offer include — private, shared, invitation, license, credits, top-up?
- What is the exact customer-facing price, currency, term, expiry and renewal?
- What can the buyer use, and what limitations / device / region restrictions apply?
- What payment rails and delivery SLA are truly supported for this specific offer?
- What is the verified warranty / refund / replacement policy?
- What are the alternatives, and which real use case makes one better?
- What evidence was checked, by whom, and on what date?

### AEO page brief
- H1 targets the verified dominant intent, not every synonym.
- A concise direct answer immediately follows the H1; no mandatory 40–55 word formula.
- Quick facts show source and verification date for official product facts vs marketplace offer facts.
- A fan-out map is an editorial coverage checklist inside the page, not a list of pages to mass-generate.
- Use semantic headings, real HTML tables where comparison benefits the user, descriptive image alt text and visible limitations.
- FAQs answer actual buyer questions; FAQPage schema is not a promise of rich-result display.
- Cite official docs for features and terms; clearly separate official plan claims from third-party reseller offer terms.

### GEO / answer-engine citation readiness
- Keep important page facts in crawlable HTML; do not hide price, term, access, limits, warranty or delivery exclusively behind JS.
- Separate the official software entity from the marketplace seller/offer entity.
- Publish original, privacy-safe evidence: actual setup tests, documented region/activation constraints, measured delivery timing, support resolution statistics, plan comparison methodology.
- Record a reviewer, evidence URL, verification date and change history.
- Don't publish private supplier bots, supplier cost, product IDs, customer identifiers, access credentials, or raw reseller messages into public pages, `llms.txt`, sitemaps, feeds or AI datasets.
- Track citations with a fixed neutral prompt set and dates. A crawler fetch or third-party “AI visibility score” does not guarantee that a model will cite the site.

## 4. Search Console and keyword intelligence

The repository contains a LIVE_API GSC snapshot retrieved 2026-10-24 for **2026-09-24 to 2026-10-22**:
- 28 clicks, 626 impressions, 4.47% average CTR and 32.5 average position.
- Top product-page rows include Gemini (5 clicks / 55 impressions / position 5.82), LinkedIn (3 / 64 / 9.78), ChatGPT (0 / 47 / 19.02), CapCut (0 / 18 / 15.61), Replit (0 / 19 / 6.42), YouTube (0 / 18 / 18.22).
- These are historical URL observations, not search volume. Missing GSC rows are blank, not zero.
- Country and device files are aggregate-level only: Pakistan 20/398; mobile 16/219; desktop 10/349. Do not copy these aggregate facts into each tool row.
- Search Console's Generative AI Performance report rolled out worldwide on 2026-08-31. Check Search AI and Discover AI report in the verified property and export date/page/country/device observations. The report may not appear when the property lacks enough impressions.  
  Search: https://support.google.com/webmasters/answer/16984139  
  Discover: https://support.google.com/webmasters/answer/16983858

Keyword map status remains **HYPOTHESIS_ONLY**. Do not publish volumes, CPC, competition scores or “high-volume” claims without a dated source. Weekly workflow:
1. GSC export: query + page + country + device + date.
2. Group misspellings and intent-equivalent queries into one cluster.
3. Map each cluster to one intended canonical URL.
4. Detect queries where two URLs compete; select the best destination and consolidate if necessary.
5. Inspect high-impression / low-CTR pages for title, snippet, price/offer match and search intent.
6. Inspect positions 8–20 for content gaps, trust evidence and internal-link improvements.
7. Separate branded, non-branded, irrelevant and contaminated queries. Avoid optimising for noisy query IDs or unrelated brand strings.

## 5. Page-quality and content risk: 149/175 source use-case sentences are generic

The supplied master directory repeats this exact audience/use-case sentence for 149 parent tools:
> Digital creators, developers, freelancers aur agencies apne specific workflow tasks ko automate aur accelerate karne ke liye use karte hain.

This sentence is not enough to write 149 distinct product pages. Replace it only after researching each tool's actual audience and use case from official documentation and verified practical testing. Also re-check model names, product tiers, credit allowances, device limits and current feature descriptions because many models and plan names change.

**Page publication minimum:**
- Unique explanation of the product and the exact tier/offer.
- Official docs and current feature facts.
- Exact local customer offer facts from the offer ledger.
- Verified access and ownership implications.
- A real comparison or use case that distinguishes the tool.
- Known limitations, unsupported regions, caps and exclusions.
- Real warranty/refund and delivery conditions.
- A named reviewer and `content_last_reviewed_at`.
- A concise source list and reproducible evidence.
- Internal links to adjacent tools/guides that genuinely help the buyer.

## 6. Merchant Center vs Google Ads — never merge the gates

### Merchant Center / Shopping
Software subscriptions shown in Shopping need a prepaid annual term of at least 12 months, correct title/term, full-year prepaid price, and landing page that displays and preselects the appropriate term and explains renewal/cancellation. This is necessary, not sufficient. Recurring digital-content subscriptions, streaming content, online gaming currency and various services are unsupported Shopping content.  
Official references:
- https://support.google.com/merchants/answer/7169130
- https://support.google.com/merchants/answer/6150006

Eligibility is **offer/SKU-specific**. A single parent such as Canva, Microsoft 365 or VPN can have multiple offer types: coupon, account upgrade, invite, shared seat, private license, 1-month access or annual prepaid subscription. Only one may meet Merchant Center conditions; the parent brand alone cannot be approved.

### Google Ads
Search Ads policy is separate from Shopping feed eligibility. Google Ads still requires truthful business identity, genuine available offers, accurate payment model, no misleading brand affiliation, no hidden recurring costs and no bait-and-switch. A Merchant Center block does not automatically establish whether a Search Ad may run.  
Official policy: https://support.google.com/adspolicy/answer/6020955

**Current repo evidence:** no Google Ads `AW-` conversion ID or Merchant Center feed exporter was found in inspected repo files. Owner console and external tag/container still need checking.

## 7. Structured data and reviews

Sampled ChatGPT and Veo product pages contain:
- Product / Offer schema with PKR price, availability and seller.
- `shippingDetails` with zero-day handling/transit even though the page says availability and delivery timing are confirmed on WhatsApp.
- AggregateRating `4.9` / `38` and a generic `Verified Pakistani Buyer` review.

Actions:
1. Verify visible price and availability against the exact offer and checkout flow.
2. Remove or correct zero-day physical shipping data on digital delivery pages unless it truthfully describes the offer.
3. Keep review/rating schema only when genuine product-specific reviews are visible to users and supported by original records; otherwise remove it.
4. Only set `priceValidUntil` when there is a real offer expiry date.
5. FAQ content should still be useful to users; do not build an SEO plan around FAQ rich-result appearance.

Reference: https://developers.google.com/search/docs/appearance/structured-data/merchant-listing

## 8. Crawlers and AI access controls

Repository `robots.txt` currently groups `OAI-SearchBot`, `GPTBot`, `ChatGPT-User`, `ClaudeBot`, `PerplexityBot` and `Google-Extended` with `Allow: /` and common disallows. This means:
- OAI-SearchBot currently allowed, GPTBot allowed, ChatGPT-User allowed.
- PerplexityBot currently allowed; Perplexity-User not separately listed.
- ClaudeBot allowed; Claude-SearchBot and Claude-User not explicitly listed.
- Google-Extended allowed.
- Search Console's Search generative AI switch is a separate owner-console setting and cannot be inferred from robots.txt.

OpenAI documents that OAI-SearchBot and GPTBot are independent controls; Search visibility requires OAI-SearchBot. ChatGPT-User is a user-triggered fetcher, not the automatic search crawler.  
https://developers.openai.com/api/docs/bots

Perplexity has separate search and user-triggered agents; verify real requests by their published IPs, not user-agent string alone.  
https://docs.perplexity.ai/guides/bots

Anthropic separates ClaudeBot (training), Claude-SearchBot (search) and Claude-User (user-triggered fetch).  
https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler

Do not change GPTBot, ClaudeBot or Google-Extended training preferences without a deliberate owner decision. Do not assume a robots.txt rule protects confidential files; never put secrets on a public site.

## 9. Indexing and publishing controls

- Google uses XML sitemap, internal links and Search Console to discover regular product/guide/category URLs.
- Google does not participate in IndexNow. IndexNow submissions notify participating engines, not Google: https://indexnow.com/faq
- Google's Indexing API is only for JobPosting and livestream pages that embed BroadcastEvent in VideoObject, not standard product pages or blog posts: https://developers.google.com/search/apis/indexing-api/v3/using-api
- Keep sitemap only to canonical, indexable, useful URLs with 200 responses; update `lastmod` only when content materially changes.
- Never include HOLD, unverified offers, query-string URLs, duplicate variants, non-canonical locale paths, or admin/private resources.
- Test live status, canonical, robots, rendered text and internal link reachability for each release.

## 10. Analytics and lead truth

Repository findings:
- `attribution.js` has GA4 measurement ID `G-NQJCMDCLLP`; several events are present.
- `app.js` fires `begin_checkout` on WhatsApp order initiation but uses custom `item_ids` / `item_count` rather than a full GA4 ecommerce `items[]` payload.
- No verified `purchase` / `refund` flow was found in the inspected attribution code; no consent-mode setup was found in the inspected file; external property configuration was not verified.
- WhatsApp click is an enquiry/checkout start, not a sale.

Recommended event model:
| Event | Trigger |
|---|---|
| `view_item` | Product detail page viewed; include items[] |
| `select_item` | Item selected from directory/category list |
| `add_to_cart` | Item added |
| `begin_checkout` | WhatsApp/order flow opened; include exact items[], value, currency and channel |
| `generate_lead` | A qualified enquiry is created/recorded; do not use every page view |
| `purchase` | Only after payment is confirmed; include unique transaction_id, items[], value, currency |
| `refund` | Actual refund is processed; tie to transaction_id |

Never send customer name, phone, WhatsApp message, email or payment credentials as analytics parameters. Consent Mode defaults/updates must run before analytics or ads measurement commands and reflect the applicable user consent/legal rules.  
References:
- https://developers.google.com/analytics/devguides/collection/ga4/reference/events
- https://developers.google.com/tag-platform/security/guides/consent

## 11. Performance and Core Web Vitals

| Measurement | Verified finding | Action |
|---|---|---|
| Homepage 2026-11-04 | Original mobile PSI score 56; desktop 100 | Optimised comparison copy is not the live site; fix original mobile path |
| ChatGPT page 2026-11-05 | WebSpeed verdict bad; render-blocking request estimate ~450ms; no numeric score returned | Remove/defer blocking JS/CSS and repeat product-template PSI |
| ChatGPT page acceleration | WebSpeed Fast did not outperform original | Do not claim faster result |
| Product/guide/category templates | Not all templates were tested individually | Build template-level PSI / CrUX report |

Good Core Web Vitals at the 75th percentile:
- LCP ≤ 2.5 seconds
- INP ≤ 200 milliseconds
- CLS ≤ 0.1

PSI lab score is not the same as passing field data; track CrUX mobile and desktop separately.  
Reference: https://web.dev/articles/vitals

## 12. v2.1 workbook structure

| Sheet | Purpose |
|---|---|
| Dashboard | Live counts and safe-state summary |
| Register | 175 parents, 100+ fields, source/hypothesis/proof separation, formulas and dropdowns |
| Offer Ledger | All 2,902 raw supplier rows as private internal candidates; no automatic approval |
| Category Map | 13 planned hubs and current missing route status |
| GSC Evidence | 2026-09-24 to 2026-10-22 page, query, country and device observations |
| Technical & AI Controls | Robots, AI reports, Merchant/Ads, GA4, schema, PSI and API status |
| Field Dictionary | Meaning, source, safe default and fill instructions |
| Gates & Workflow | Formula weights, six hard gates, policy logic and release workflow |
| Formula QA | Deterministic tests for CTR, weighted opportunity score, tied RANK.EQ and HOLD/BLOCK release state |

The `Formula QA` sheet runs deterministic examples: CTR 5/100 = 5.00%; weighted score (90, 80, 70, 90, 60) = 80.5; tied ranks for 90, 80, 90 = 1, 3, 1; and safe HOLD / release / block behaviour. These tests do not alter production scores.

The parent register intentionally keeps:
- offer/publication status = HOLD;
- risk status = needs_review;
- merchant and ads gates = HOLD;
- indexing status = not_checked;
- unverified stock = blank;
- no keyword search-volume claims;
- scores blank until evidence is provided;
- release gate formula = HOLD until six gates pass.

### Opportunity score — preserved v2.0 weights
`0.30 × Demand + 0.25 × Readiness + 0.20 × Stock Reliability + 0.15 × Information Gain + 0.10 × Competitive Gap`

The workbook references weight cells instead of embedding magic numbers. CTR is calculated as clicks / impressions; priority rank uses descending `RANK.EQ`. Readiness is derived from six gate results. An unfilled input is blank, not zero.

## 13. 30-day implementation sequence

| Days | Priority | Output |
|---|---|---|
| 1–3 | Fix data truth | Verify supplier row → parent/SKU matches; resolve stock sentinel meaning; confirm exact price/term/access/rights; keep unsupported and high-risk rows HOLD |
| 4–6 | Technical/AI controls | Check Search generative AI setting; separate search vs training crawler preferences; confirm sitemap/robots/canonical and IP verification |
| 7–10 | Analytics + GSC | Refresh GSC 28/90-day data and AI report; QA GA4 ecommerce events, `generate_lead`, purchase reconciliation, Consent Mode |
| 11–14 | Content pilot | Select 5–10 verified parent offers; create original briefs and fan-out maps; correct price/access schema and review proof |
| 15–18 | Performance | Fix mobile homepage and ChatGPT tool template render blocking; measure product, guide and category templates; compare CrUX p75 |
| 19–22 | Category hubs | Build 13 useful hubs, verify no cannibalisation, unique copy, internal linking and 200/canonical/sitemap |
| 23–26 | Merchant / Ads | Review exact offer types and rights; send only eligible annual prepaid software subscription offers to Merchant feed; separately review Search Ads |
| 27–30 | Controlled release | Human approve, PR, tests, live checks, refresh sitemap and IndexNow for participating engines; monitor GSC and leads |

## 14. Master implementation prompt for Antigravity / Codex

```text
You are the senior Technical SEO, AEO/GEO, analytics, policy and conversion engineer for
https://aitoolgems.tech/
Repository: https://github.com/m-rehman55/ai-tool-gems
Branch: main

MISSION
Improve search visibility, useful AI citations, qualified leads and confirmed sales through
evidence-led technical/content improvements. Do not promise a ranking or citation outcome.
Do not publish all 175 parents blindly.

REQUIRED FIRST STEP
1. Read AGENTS.md and all current SEO policy, data-model, workflow, trust and schema docs.
2. Inspect all 40 existing tools pages, every guide, app.js, attribution.js, robots.txt,
   sitemap.xml, llms.txt, schema_audit.py, audit_all.py, link_graph_checker.py,
   GSC/keyword/AIO agents and GitHub Actions.
3. Treat the attached v2.1 workbook as the source of truth for status fields and release gates.
4. Preserve all 175 rows at HOLD / needs_review until verified evidence proves otherwise.
5. Keep Offer Ledger supplier rows private. Never publish supplier bots, supplier costs,
   supplier IDs, account credentials, customer information or raw source descriptions.

DATA TRUTH
- 2,902 supplier rows; 1,619 unique listing-name strings; 15 bots.
- Strict numeric stock: 126,591 summed over numeric cells.
- 97 rows use "999 (Invite)" (96,903 when multiplied by 999); this is NOT verified stock.
- 117 rows use text-only "In Stock"; this is NOT quantity.
- 645 strict numeric zero-stock rows; 126 zero-priced; 126 missing Product IDs; 93 missing descriptions.
- Parent catalogue reported 223,494 only by adding invite sentinel prefixes to numeric stock.
- Never claim 223,494 verified fulfilment stock.
- Never translate supplier `Status=Live` into actual customer stock availability.

ARCHITECTURE
- One canonical page per parent tool.
- Variants/credits/durations/invites/top-ups remain offer/SKU rows, not separate doorway pages.
- 13 category hub routes are missing; build useful hubs, not thin link pages.
- Do not publish test placeholders, unsupported/unsafe accounts, or unresolved offers.
- Do not create indexable pages for each keyword variant.

SEARCH / AEO / GEO
- Follow Google core SEO and people-first guidance; no special AI schema, fixed snippet word count,
  mandatory chunking or llms.txt ranking hack.
- Treat fan-out map as an editorial coverage checklist inside a genuinely useful page.
- Publish direct answers, semantic comparison tables, explicit limitations, official citations,
  reviewer/date, and independently verified unique evidence.
- Avoid false claims about official affiliation, model versions, device limits, credits or warranty.
- Keep `llms.txt` optional and public-safe; do not place supplier or customer-private data inside it.
- Verify GSC Search Generative AI and Discover AI report and store date/page/country/device data.

CRAWLERS
- OAI-SearchBot is the ChatGPT Search crawler; GPTBot is a separate training choice.
- PerplexityBot and Perplexity-User are separate.
- ClaudeBot, Claude-SearchBot and Claude-User are separate.
- Keep training controls a human owner decision; do not change those silently.
- Verify crawler IPs using published source lists and logs; user-agent alone is spoofable.

MERCHANT CENTER AND ADS
- Merchant eligibility is offer/SKU-specific.
- Software Shopping subscriptions need prepaid annual terms of at least 12 months and correct landing-page
  price/term/renewal disclosures.
- Streaming/digital content recurring subscriptions, online gaming currency and unsupported services
  are not eligible for Shopping.
- Google Ads Search policy is separate from Shopping; implement separate ads_gate.
- Require rights, available offer, honest brand relationship, clear full price/term and truthful fulfilment.

SCHEMA
- Structured data must match visible facts exactly.
- Remove or correct zero-day parcel shipping data on digital delivery offers.
- Remove AggregateRating/Review unless genuine, visible, product-specific source reviews are evidenced.
- Use priceValidUntil only when a real price expiry exists.
- FAQ text may be useful; do not promise FAQ rich-results eligibility.

ANALYTICS
- GA4 is partially present (G-NQJCMDCLLP), not fully QAed.
- Standardise `items[]` for ecommerce events.
- Track view_item, select_item, add_to_cart, begin_checkout, generate_lead, purchase, refund.
- WhatsApp click is not a purchase.
- purchase only after verified payment with transaction_id and reconciliation to order ledger.
- Do not send PII in analytics events.
- Implement consent defaults/updates based on the applicable region and consent policy.
- Verify Google Ads conversion tracking in the actual owner account; no AW- ID was found in repo scan.

PERFORMANCE
- Homepage original mobile score 56 and desktop 100 from 2026-11-04; do not call accelerated copy score live-site score.
- ChatGPT product page 2026-11-05 verdict was bad; render-blocking estimate ~450ms, no numeric score returned.
- Fix and separately measure homepage, tool, guide and category templates.
- Report CrUX field LCP/INP/CLS p75 separately from Lighthouse lab scores.

RELEASE GATES — ALL REQUIRED
- resale rights PASS
- exact offer truth (price, currency, term, access, stock, delivery, warranty) PASS
- content uniqueness / evidence PASS
- technical canonical / sitemap / HTTP / schema PASS
- analytics / privacy QA PASS
- human approval PASS
If any gate is unresolved, keep HOLD. If any hard gate fails, mark BLOCKED. Do not auto-override.

RELEASE PROCESS
1. Audit and report before code changes.
2. Create a dedicated feature branch and PR.
3. Update the v2.1 register with evidence links and reviewer.
4. Run unit tests, schema audit, link graph checker, sitemap check, page performance tests and
   GA4 DebugView / order reconciliation QA.
5. Recheck production URL status, canonical and visible content.
6. Record deploy_ref, live_url_checked_at and rollback instructions.
7. Never mark a page published or eligible solely because a script generated it.

DELIVERABLES
- Evidence-backed audit report.
- Updated parent register and private offer ledger.
- Offer-level Merchant/Ads eligibility report.
- Category hub content briefs.
- GSC + Generative AI report export and keyword-to-URL map.
- GA4 event QA and purchase reconciliation report.
- Crawler / Search Console control verification.
- PSI / CrUX per-template report.
- PR summary with file list, tests, evidence, risks and rollback notes.
```

## 15. Official references

- Google AI Search optimization: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- Helpful, people-first content: https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- Google spam policies: https://developers.google.com/search/docs/essentials/spam-policies
- Search Generative AI report (Search): https://support.google.com/webmasters/answer/16984139
- Search Generative AI report (Discover): https://support.google.com/webmasters/answer/16983858
- OpenAI crawlers: https://developers.openai.com/api/docs/bots
- Perplexity crawlers: https://docs.perplexity.ai/guides/bots
- Anthropic crawlers: https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler
- Merchant software subscriptions: https://support.google.com/merchants/answer/7169130
- Merchant unsupported content: https://support.google.com/merchants/answer/6150006
- Google Ads Misrepresentation: https://support.google.com/adspolicy/answer/6020955
- Merchant listing/Product schema: https://developers.google.com/search/docs/appearance/structured-data/merchant-listing
- GA4 ecommerce events: https://developers.google.com/analytics/devguides/collection/ga4/reference/events
- Consent Mode: https://developers.google.com/tag-platform/security/guides/consent
- Search Console API: https://developers.google.com/webmaster-tools/v1/searchanalytics/query
- Core Web Vitals: https://web.dev/articles/vitals
- IndexNow FAQ: https://indexnow.com/faq
- Google Indexing API restrictions: https://developers.google.com/search/apis/indexing-api/v3/using-api
- Google Trends API alpha announcement: https://developers.google.com/search/blog/2025/07/trends-api


### Additional risk classification from the last 18 master-directory parents

The final catalogue section is not all ordinary software. In particular, Telegram spam/member-growth bot variants (158), X account stock (159), Facebook/TikTok growth and verification variants (160–161), Reddit clone account (162), OTP/virtual numbers (167), aged webmail accounts (168), family-region restriction bypass (169), PayPal account resale (170), Bybit/crypto-card accounts (171), OnlyFans platform accounts (172), and MB Bank banking voucher (173) stay in enhanced review. These are cautionary review labels based on the source catalogue; they are not legal findings. Exact policy and legal decisions remain offer/region-specific. Coffee discount vouchers (174) require ordinary voucher-region, expiry, and redemption checks. Administrative/test placeholders (175) must not become public products.
