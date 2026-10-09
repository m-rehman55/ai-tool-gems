---
name: geo-aeo-optimizer
description: Standard operating procedure for verifying and optimizing pages for Google SEO, Generative Engine Optimization (GEO), Answer Engine Optimization (AEO), and localized keyword intent.
---

# GEO & AEO Optimization Workflow

Use this skill whenever creating, modifying, or auditing pages to maximize organic search rankings on Google, featured snippet capture, and citations in generative AI engines (Google AI Overviews, Perplexity, ChatGPT Search, Claude).

## 1. Keyword & Intent Discovery
- Identify the primary target query and its search intent (Transactional, Commercial Investigation, Informational, AEO Question, or GEO Prompt).
- Verify localized alignment:
  - For Pakistan (`/`, `/guides/`, `/tools/`): Target queries with PKR pricing, local payment methods (Nayapay, Sadapay, JazzCash, Raast), and local delivery terms.
  - For Japan (`/jp/`): Target queries with JPY pricing, Japanese localization, and Japan-specific purchasing habits. Never cross-contaminate.

## 2. Information Gain & GEO Content Construction
- Ensure the page contains **Information Gain** (proprietary, verified data):
  - Real active prices in PKR/JPY.
  - Verification of payment method compatibility.
  - Hands-on feature breakdowns and delivery speed facts.
- Use explicit quantitative data (e.g., "$20/mo (~5,600 PKR)", "100k context window") to facilitate LLM citation grounding.
- Include concise, quote-ready summary statements for generative search synthesis.

## 3. AEO Direct-Answer Snippet Formulation
- Format all question headings (H2/H3) with an immediate, standalone 40–55 word direct-answer block.
- Follow the formula:
  > **[Entity Name]** [answers the question directly with status/price/feature]. [Secondary sentence providing practical context or qualification].
- Structure comparisons into semantic HTML `<table>` elements with descriptive headers.
- Structure procedural steps into `<ol>` elements.

## 4. Schema Markup & Crawler Validation
- Validate JSON-LD structured data on the page:
  - `FAQPage` for question-and-answer sections.
  - `SoftwareApplication` or `Product` for tools and pricing plans.
  - `BreadcrumbList` for navigation hierarchy.
- Ensure `llms.txt` and `sitemap.xml` / `sitemap-jp.xml` include the URL.
- Verify that `robots.txt` permits benevolent AI crawlers (`Google-Extended`, `GPTBot`, `ClaudeBot`, `PerplexityBot`).

## 5. Verification Commands
Run the repository test suite and offline audit:
```bash
python -m unittest discover -s marketing_agent/tests -v
python -m marketing_agent hermes audit
```
Confirm 0 audit issues before committing or deploying changes.
