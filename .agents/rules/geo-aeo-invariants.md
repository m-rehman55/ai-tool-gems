# GEO and AEO Operational Invariants

These invariants govern how content, metadata, and structured data are generated, modified, or audited for AIToolGems.

## 1. Generative Engine Optimization (GEO)
- **Information Gain Patent Compliance**: Never produce generic AI summaries that merely rephrase existing top SERP results. Every page must contain primary value: actual verified Pakistani Rupee (PKR) or Japanese Yen (JPY) pricing, local payment method availability (Sadapay, Nayapay, JazzCash, Raast, local cards), and confirmed delivery/warranty specifics.
- **Authoritative Citation Grounding**: Back claims with official documentation, official pricing pages, or developer API specifications.
- **Quantitative & Technical Precision**: State exact entity numbers (e.g., token context windows, monthly fees, benchmark scores) rather than vague descriptors.
- **AI Crawlability**: Keep `/llms.txt` synchronized with the product catalog and ensure benevolent AI crawlers (`GPTBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`) are permitted in `robots.txt`.

## 2. Answer Engine Optimization (AEO)
- **Inverted-Pyramid Direct Answer**: Immediately beneath any question-based heading (H2/H3, such as FAQs or feature comparisons), include a standalone 40–55 word direct-answer block before elaborating.
- **Structured Snippet Formats**:
  - Comparison matrices: Semantic `<table>` with `<thead>` and `<tbody>`.
  - Process workflows: Ordered `<ol>` for chronological steps.
  - Category listings: Unordered `<ul>`.
- **Entity Knowledge Schema**: Every page must have valid JSON-LD (`FAQPage`, `SoftwareApplication`, `Product`, `BreadcrumbList`) and link to authoritative entities via `sameAs`.

## 3. Google Helpful Content & E-E-A-T
- **People-First Intent**: Content must resolve user pain points (e.g. paying for AI subscriptions from Pakistan) rather than search-engine word counts.
- **Strict Locale Separation**: Pakistan (PKR) and Japan (JPY) data, links, canonicals, and schemas must never intermix.
