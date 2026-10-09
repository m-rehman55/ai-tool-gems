# SEO RULES

## HERMES Global Rules

### NEVER Fabricate

- Facts
- Prices
- Historical prices
- Search volume
- Rankings
- Backlinks
- Reviews
- Ratings
- Authors
- Product features
- Availability
- SEO results

Unknown information must be marked: **UNKNOWN**

Do not silently guess.

---

## Source Priority

1. Official vendor source
2. Official pricing page
3. Official documentation
4. Official product source
5. Official API/data
6. Google Search Central Documentation (https://developers.google.com/search/docs)
7. GitHub/source code
8. Reliable primary business sources
9. Reliable third-party research
10. Community sources for experience/context

Clearly distinguish source-backed facts from assumptions.

---

## Google Search Central Operational Standards (https://developers.google.com/search/docs)

All autonomous agents and content generators must strictly adhere to Google Search Central specifications:
1. **Search Essentials Compliance**: Never generate doorway pages, scraped content, or misleading cloaked text. Provide genuine people-first Information Gain.
2. **Crawling & Indexing Guardrails**: 
   - Maintain a pristine `sitemap.xml` with zero 404s, zero redirects, and exact `<lastmod>` timestamps.
   - Never block essential CSS/JS in `robots.txt`. Permit benevolent search and AI agents (`Googlebot`, `Google-Extended`, `GPTBot`, `PerplexityBot`, `ClaudeBot`).
   - Every indexable page must contain a self-referencing canonical URL.
3. **Search Appearance & High-CTR Engineering**:
   - **Title Links**: Craft concise 50–60 character titles combining primary intent keyword, price anchor in PKR, and brand name to avoid truncations in SERP snippets.
   - **Meta Descriptions**: 140–160 characters with clear value propositions, trust signals (e.g. WhatsApp instant delivery, 7-day warranty), and local payment options (EasyPaisa/JazzCash).
4. **Structured Data Completeness**:
   - Every product page must validate with complete `Product` schema (including `offers`, `aggregateRating`, `review`, and in-stock availability).
   - FAQ sections must implement valid `FAQPage` schema.
   - Navigation must implement valid `BreadcrumbList` schema.
5. **Continuous Verification & Re-Testing**:
   - Multi-layer automated testing (`audit_all.py`, `schema_audit.py`, `audit_complete.py`, `growth_seo_engine.py`, `unittest discover`).
   - 0 errors tolerance before any commit to `main`.

---

## Pakistan Market Exclusivity

AIToolGems is a **100% Pakistan-exclusive marketplace**.

**Requirements:**
- Exclusive PKR currency across all tools and guides
- Pakistan local payment integrations: EasyPaisa, JazzCash, SadaPay, NayaPay, Raast, IBFT
- Local Pakistani delivery speed (5-30 minutes WhatsApp delivery)
- Self-referencing Pakistani canonical URLs
- Localized English & Urdu transactional search intent
- Canonical
- Hreflang
- Metadata
- Product data
- Availability
- Internal links

---

## Change Management

1. Research → Evidence → Opportunity → Proposed change
2. Risk analysis
3. Implementation
4. Tests
5. SEO validation
6. Git diff review
7. Pull Request
8. Human approval (high-risk)
9. Deployment
10. Re-crawl
11. Measurement
12. Learning

---

## Content Rules

- Never keyword stuff
- Never create doorway pages
- Never create thin pages at scale
- Never create duplicate pages for trivial variations
- Never manipulate structured data
- Never fake reviews/ratings/authors/expertise
- Never misrepresent vendor/marketplace policies
- Never hide text
- Never use deceptive redirects
- Never buy spammy links

---

## SEO Quality Gates

Before merging SEO-related code:
- Title
- Meta description
- H1
- Canonical
- Robots
- Sitemap
- Hreflang
- Schema
- Broken links
- Duplicate URLs
- Duplicate titles
- Duplicate descriptions
- HTTP status
- Locale
- Currency
- Internal links
- Images
- Page performance
- Accidental noindex
- Source data
- Freshness

---

## GEO & AEO Invariants

### Generative Engine Optimization (GEO)
- Every page must satisfy Google's Information Gain requirement: include original localized data (PKR pricing, local payment methods like Nayapay/Sadapay/JazzCash, verified delivery guarantees).
- Claims must be grounded with official vendor references, quantitative specs, and precise model entity names.
- Maintain public machine-readable AI context (/llms.txt) and allow reputable generative search crawlers in robots.txt.

### Answer Engine Optimization (AEO)
- Under every question heading (H2/H3), provide a standalone 40–55 word direct answer block before detailed discussion.
- Maintain clean semantic HTML: use <table> for comparisons, <ol> for sequential steps, and validated JSON-LD schema for all entities.
- Target zero-click and voice search intent with clear entity definition sentences.

