# SEO ARCHITECTURE

## Site Architecture

```
/                          → Homepage (PK)
/tools/                    → Product pages (PK)
/tools/[slug]/index.html   → Product detail (PK)
/guides/                   → Guides (PK)
/guides/[slug]/index.html  → Guide detail (PK)
/deals/                    → Deals (PK)
/about.html                → About
/contact.html              → Contact
/policies.html             → Policies
/privacy.html              → Privacy
/terms.html                → Terms
/how-we-review.html        → Review methodology
/jp/                       → Japan homepage
/jp/tools/                 → JP product pages
/jp/guides/                → JP guides
/jp/about.html             → JP About
/jp/contact.html           → JP Contact
```

## Page Types

- Homepage
- Product
- Guide
- Comparison
- Deals
- About
- Contact
- Policies
- Locale pages

## URL Rules

- Clean URLs, no parameters
- No duplicate slugs
- No tracking URLs indexed
- Locale prefix: /jp/ for Japan
- PK: root level
- Trailing slash consistent

## Link Structure

Product ↔ Category
Product ↔ Guide
Product ↔ Comparison
Product ↔ Related Products
Guide ↔ Guide
Guide ↔ Product
Research ↔ Product
Pricing ↔ Product

## Sitemaps

- sitemap.xml (PK)
- sitemap-jp.xml (JP)
- robots.txt
- llms.txt
