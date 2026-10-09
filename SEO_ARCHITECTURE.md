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
```

## Page Types

- Homepage
- Product (20 tools)
- Guide & Comparison
- Deals
- About
- Contact
- Policies & Legal

## URL Rules

- Clean URLs, no parameters
- No duplicate slugs
- No tracking URLs indexed
- Root level Pakistan URLs
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

- sitemap.xml
- robots.txt
- llms.txt
