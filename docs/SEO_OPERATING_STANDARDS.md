# SEO OPERATING STANDARDS & TECHNICAL SEARCH SPECIFICATION
**Standard**: Google Search Central Essentials & Bing Webmaster Guidelines  

---

## 1. Technical SEO & On-Page Architecture

1. **Canonical URLs**:
   - Every indexable page must contain a self-referential `<link rel="canonical">` using absolute HTTPS URL and standard trailing slashes.
   - Example: `<link rel="canonical" href="https://aitoolgems.tech/tools/chatgpt/" />`
2. **Heading Hierarchy**:
   - Exactly one `<h1>` per page matching the page title intent.
   - Logical descending hierarchy (`<h1>` $\to$ `<h2>` $\to$ `<h3>`). No skipped heading tiers.
3. **Internal Linking & Link Graph**:
   - Zero broken links (`404` or `5xx`).
   - Zero orphan indexable pages. Every guide and tool must be reachable within $\le 3$ clicks from the homepage.
   - Contextual, descriptive anchor text. Avoid generic anchors like "click here" or "learn more".
4. **Sitemap & Robots.txt**:
   - `sitemap.xml` must include 100% of indexable canonical URLs and exclude `404.html`, admin pages, and noindex pages.
   - `robots.txt` must explicitly reference `https://aitoolgems.tech/sitemap.xml`.

---

## 2. Core Web Vitals (CWV) Performance Thresholds

All production pages must target the Google 75th percentile thresholds:

| Metric | Target (Good) | Needs Improvement | Poor |
| :--- | :--- | :--- | :--- |
| **Largest Contentful Paint (LCP)** | $\le 2.5\text{ s}$ | $2.5\text{ s} - 4.0\text{ s}$ | $> 4.0\text{ s}$ |
| **Interaction to Next Paint (INP)** | $\le 200\text{ ms}$ | $200\text{ ms} - 500\text{ ms}$ | $> 500\text{ ms}$ |
| **Cumulative Layout Shift (CLS)** | $\le 0.10$ | $0.10 - 0.25$ | $> 0.25$ |
| **First Contentful Paint (FCP)** | $\le 1.8\text{ s}$ | $1.8\text{ s} - 3.0\text{ s}$ | $> 3.0\text{ s}$ |

---

## 3. Structured Data & JSON-LD Rules

1. **Supported Rich Result Types**:
   - `Product` (Tool listings: price in PKR, valid availability, merchant return policy).
   - `BreadcrumbList` (Hierarchical navigation).
   - `FAQPage` (Genuine on-page questions with answers).
   - `Organization` (Publisher identity, logo, brand contact).
2. **Prohibited Schema Tactics**:
   - No fake `Review` or `AggregateRating` when user reviews are absent from visible HTML.
   - No physical shipping attributes for purely digital goods.
   - No schema spamming (irrelevant entity stuffing to manipulate search snippets).

---

## 4. Search Spam & Scaled Content Abuse Defense

In compliance with Google's March 2024 Spam Update:
1. **No Scaled Content Abuse**: No mass programmatic generation of hundreds of thin pages using string interpolation without distinct, high-value editorial analysis.
2. **No Doorway Pages**: Every page must have a distinct value proposition and address unique search intent.
3. **No Hidden Text / Cloaking**: Content served to Googlebot must be 100% identical to content rendered for visitors.
