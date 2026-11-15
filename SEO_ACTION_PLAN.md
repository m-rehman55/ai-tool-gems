# **AI Tool Gems — Complete SEO & Technical Implementation Blueprint**

Version 1.0 · 15 November 2026 · Repository implementation specification

| Project detail             | Value                                                                                                           |
| -------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Website                    | [https://aitoolgems.tech/](https://aitoolgems.tech/?utm_source=chatgpt.com)                                     |
| Repository                 | [https://github.com/m-rehman55/ai-tool-gems](https://github.com/m-rehman55/ai-tool-gems?utm_source=chatgpt.com) |
| Business                   | Digital AI subscriptions marketplace and AI tools directory                                                     |
| Primary market             | Pakistan                                                                                                        |
| Secondary market           | Worldwide / international discovery and inquiries                                                               |
| Implementation environment | Antigravity / GitHub / Python-based SEO tooling                                                                 |
| Implementation approach    | Evidence-first, incremental, test-driven                                                                        |
| Production deployment      | Requires explicit owner approval                                                                                |

**Document purpose:** Provide Antigravity with an exhaustive engineering blueprint to investigate, implement, test and validate the SEO and technical improvements identified in the November 2026 audit.

**Important:** This is an implementation specification, not a claim that the changes have already been applied. Actual file paths, existing code, current prices, routing configuration and deployment behaviour must be verified against the checked-out repository before modification.

# **Table of Contents**

1. Executive Summary
2. Important SEO Corrections
3. Project Architecture and Repository Discovery
4. Implementation Safety Rules
5. Complete Technical Audit
6. URL Architecture and Redirect Remediation
7. Indexation and Crawlability
8. Sitemap Implementation
9. Robots.txt Implementation
10. Canonical and Metadata Architecture
11. Structured Data and Schema Implementation
12. Homepage Optimization
13. Product Page Optimization
14. Directory Profile Optimization
15. Category Page Optimization
16. Blog and Guide Optimization
17. Keyword Research and Cannibalization
18. Internal Linking Architecture
19. Image and Media SEO
20. International SEO
21. Business Trust and E-E-A-T
22. AdSense Readiness
23. Core Web Vitals and Performance
24. Automated SEO Testing Architecture
25. Google Search Console Validation
26. Bing and AI Search Visibility
27. HERMES Integration
28. File-by-File Change Register
29. Implementation Phases
30. Acceptance Criteria
31. Rollback Strategy
32. Final Execution Checklist
33. Antigravity Master Execution Instructions

# **1. Executive Summary**

The audit identifies five primary areas requiring attention.

| Issue                                   | Risk                                                         | Priority |
| --------------------------------------- | ------------------------------------------------------------ | -------- |
| Google indexing and validation failures | Important pages may not enter or remain in Google's index    | P0       |
| Product schema and rich-result errors   | Search engines may receive inaccurate commercial information | P0       |
| Internal redirect chains                | Inefficient crawling and unnecessary navigation hops         | P1       |
| Product/blog keyword cannibalization    | Search engines may select the wrong landing page             | P1       |
| Thin and duplicate directory content    | Pages may provide insufficient independent value             | P1       |

## **1.1 Strategic objectives**

The implementation must accomplish the following:

- Make important pages discoverable through crawlable internal links.
- Ensure every indexable URL has a consistent canonical.
- Ensure sitemap entries represent eligible, public URLs.
- Remove unnecessary redirects from internal navigation.
- Correct structured data according to the actual page type.
- Distinguish products sold by AI Tool Gems from free external software listings.
- Separate transactional and informational search intent.
- Improve product descriptions using verified commercial facts.
- Make directory pages independently useful.
- Strengthen business transparency and customer confidence.
- Improve visibility across Google, Bing and AI-powered search experiences.
- Preserve existing website functionality, design and ordering workflows.

## **1.2 Expected implementation outcome**

The completed project should produce:

1. A verified URL inventory.
2. A redirect and internal-link correction register.
3. An indexation eligibility register.
4. A validated sitemap.
5. A structured-data validation report.
6. A keyword-to-page intent map.
7. A content remediation register.
8. Automated regression tests.
9. A reviewed implementation PR.
10. A post-deployment monitoring report.

# **2. Important SEO Corrections**

Before implementation, Antigravity must understand several important distinctions.

## **2.1 Word count is not an indexing requirement**

The recommendation for 400+ words should be treated as a content-quality target only where appropriate.

Google does not require a page to contain 400 words before it can be indexed.

A page with 250 words of original, useful information may be more valuable than a page with 1,000 words of repetitive content.

Use the following quality criteria:

- Does the page answer a genuine user question?
- Does it provide information not already repeated across the website?
- Are product details accurate?
- Does it explain practical use cases?
- Does it include relevant limitations?
- Does it provide useful navigation?
- Does it distinguish itself from similar pages?
- Are factual claims supported by reliable sources?

**Implementation rule:** Never add filler paragraphs simply to satisfy a word-count threshold.

## **2.2 Sitemap HTTP 200 does not mean sitemap correctness**

A sitemap can return HTTP 200 and still contain:

- Duplicate URLs.
- Redirecting URLs.
- Noindex URLs.
- Incorrect canonical URLs.
- Invalid XML.
- URLs returning 404.
- Staged or private pages.
- Incorrect last-modified dates.

Every sitemap URL must be independently validated.

## **2.3 Product schema does not guarantee rich results**

Valid structured data makes a page eligible for supported search enhancements where applicable. It does not guarantee that Google will display rich results.

## **2.4 Ratings must never be fabricated**

Do not create:

- Fake customer reviews.
- Artificial review counts.
- Invented aggregate ratings.
- Supplier ratings presented as customer reviews.
- Testimonials marked up as verified product reviews without evidence.

If genuine eligible reviews are unavailable, omit `aggregateRating` and `review`.

## **2.5 Directory pages are not automatically commercial products**

AI Tool Gems contains two distinct types of listings.

**Commercial listings:**

- AI subscriptions.
- Digital software services.
- Orderable products.
- Verified offers with actual PKR prices.

**Directory/reference listings:**

- Free AI tools.
- External software products.
- Research platforms.
- Tools that visitors explore through their official websites.

Do not give directory listings an AI Tool Gems commercial Offer schema or shopping cart action.

## **2.6 Do not blindly change existing URLs**

A URL that appears inconsistent may already have backlinks, indexed history or internal references.

Before changing a slug:

1. Inspect its history.
2. Inspect backlinks if data is available.
3. Check Search Console impressions and clicks.
4. Check internal links.
5. Check whether the current route is canonical.
6. Establish a justified replacement.
7. Implement a redirect only when appropriate.

# **3. Project Architecture and Repository Discovery**

## **3.1 Known repository structure**

The following paths have been identified in the inspected repository context. Their current contents must be rechecked against the working branch before changes.

| File/path                                                    | Known purpose                    | Planned work                         |
| ------------------------------------------------------------ | -------------------------------- | ------------------------------------ |
| `AGENTS.md`                                                  | Repository instructions          | Read first                           |
| `index.html`                                                 | Homepage                         | Metadata, content, internal links    |
| `app.js`                                                     | Catalogue/application JavaScript | Product data and rendering           |
| `tools/index.html`                                           | Main tools directory             | Directory SEO and navigation         |
| `tools/chatgpt/index.html`                                   | Example commercial product page  | Schema and product template review   |
| `guides/`                                                    | Guide pages                      | Informational intent and linking     |
| `blog/`                                                      | Blog pages                       | Content and cannibalization          |
| `category/`                                                  | Category hierarchy               | Category SEO                         |
| `sitemap.xml`                                                | Sitemap                          | Eligibility and consistency          |
| `robots.txt`                                                 | Crawler directives               | Crawl access validation              |
| `scripts/link_graph_checker.py`                              | Link graph validation            | Extend existing checks               |
| `schema_audit.py`                                            | Schema validation                | Extend JSON-LD checks                |
| `audit_all.py`                                               | Audit entry point                | Integrate compatible checks          |
| `scripts/build_public_site.py`                               | Public staging/build             | Preserve security allowlist          |
| `scripts/validate_content.py`                                | Content validation               | Extend if necessary                  |
| `tests/test_visible_directory_and_catalogue_completeness.py` | Catalogue regression tests       | Add directory/product SEO tests      |
| `.github/workflows/deploy-pages.yml`                         | Deployment workflow              | Preserve release controls            |
| `docs/SEO-AND-GSC-PLAN.md`                                   | SEO/GSC planning                 | Reconcile with actual implementation |

Some documentation names have been referenced by repository instructions, but their exact locations have not all been independently verified:

- `SEO_RULES.md`
- `SEO_ARCHITECTURE.md`
- `SEO_DATA_MODEL.md`
- `SEO_SCHEMA.md`
- `SEO_CONTENT_SYSTEM.md`
- `SEO_TRUST_POLICY.md`

Antigravity must locate these files before assuming their root paths.

## **3.2 Repository discovery commands**

Run these commands before editing:

```
git status --short --branch
git rev-parse HEAD
git remote -v
git branch --show-current
git ls-files
```

Find SEO-related files:

```
git ls-files | grep -Ei \
'(seo|schema|sitemap|redirect|canonical|metadata|content|link_graph)'
```

Find routing and crawler files:

```
git ls-files | grep -Ei \
'(robots\.txt|sitemap.*\.xml|_redirects|netlify\.toml|vercel\.json)'
```

Find product and catalogue sources:

```
git ls-files | grep -Ei \
'(app\.js|catalog|product|category|tools/.*/index\.html)'
```

Windows PowerShell alternative:

```
git status --short --branch
git rev-parse HEAD
git ls-files | Select-String -Pattern "seo|schema|sitemap|redirect|canonical"
```

## **3.3 Create a file discovery register**

Record:

| Field               | Description                            |
| ------------------- | -------------------------------------- |
| File path           | Actual repository path                 |
| File type           | HTML, JS, JSON, Python, XML            |
| Purpose             | What the file controls                 |
| Source of truth     | Whether it contains authoritative data |
| Generated or manual | How it is maintained                   |
| Dependencies        | Which scripts/templates consume it     |
| Public exposure     | Whether it enters the deployed site    |
| Change risk         | Low, medium or high                    |
| Required tests      | Relevant regression tests              |

Do not modify generated files when the correct solution belongs in their generator.

# **4. Implementation Safety Rules**

These rules apply to the entire project.

## **4.1 Preserve existing functionality**

Do not break:

- Homepage design.
- Navigation.
- Search and filters.
- Product sorting.
- Product favorites.
- Comparison functionality.
- Guided finder.
- Bundles and recommendations.
- Cart behaviour.
- WhatsApp ordering.
- Responsive layout.
- Existing product routes.
- Existing animations.
- Existing deployment allowlist.

## **4.2 Commercial truth requirements**

All public pricing and availability must come from approved product records.

The following must never be invented:

- Prices.
- Foreign currency prices.
- Product availability.
- Account type.
- Subscription duration.
- Device limits.
- Warranty terms.
- Activation method.
- Delivery guarantees.
- Official partnerships.
- International offices.
- Payment capabilities.

Pakistan payment methods should be listed only when confirmed as currently supported.

The established payment methods include:

- EasyPaisa.
- JazzCash.
- SadaPay.
- NayaPay.
- Raast.
- Bank IBFT.

Wise/SWIFT should remain inquiry-based if that is still the approved operational policy.

Do not claim PayPal or automated card checkout support unless the business actually implements it.

## **4.3 Keep supplier information private**

Never expose:

- Supplier acquisition prices.
- Supplier Telegram information.
- Supplier credentials.
- Private fulfilment notes.
- API keys.
- Internal inventory.
- Private reports.
- Customer personal information.

The public website must contain only approved customer-facing information.

## **4.4 Git safety**

No direct production deployment.

No direct `main` push.

No unapproved merge.

No unapproved modification to production secrets or deployment permissions.

All implementation changes must be reviewed through a PR.

# **5. Complete Technical SEO Audit**

Antigravity must investigate every public page, not just the homepage and a few sample product pages.

## **5.1 Full website inventory**

Build a complete inventory of:

- Homepage.
- Product pages.
- Directory profiles.
- Category pages.
- Guides.
- Blog posts.
- About page.
- Contact page.
- Privacy policy.
- Terms and conditions.
- Refund policy.
- Other public trust pages.
- Search pages.
- Cart and comparison pages.
- Private/internal pages.

Suggested output:

`reports/seo/SEO_URL_INVENTORY.csv`

Recommended columns:

```
url,page_type,http_status,final_url,canonical_url,indexability,robots_meta,sitemap_status,internal_links,word_count,title,h1,schema_types,priority,notes
```

Every URL must have a classification.

## **5.2 Crawl every page**

For each page, investigate:

1. HTTP response.
2. Redirect chain.
3. Final URL.
4. Canonical.
5. Robots meta.
6. X-Robots-Tag response header.
7. Title.
8. Meta description.
9. H1.
10. H2 hierarchy.
11. Structured data.
12. Internal links.
13. External links.
14. Image alt text.
15. Broken images.
16. Duplicate content.
17. Word count as a diagnostic, not a ranking rule.
18. Mobile rendering.
19. Page performance.
20. Sitemap inclusion.
21. Orphan status.
22. Search intent.
23. CTA behaviour.

Do not mark a page as fixed merely because its HTML source contains a desired tag. Inspect the rendered output too.

## **5.3 Issue classification**

Each finding must have:

- Issue ID.
- URL.
- Exact evidence.
- Source file.
- Root cause.
- User impact.
- SEO impact.
- Recommended correction.
- Risk.
- Required test.
- Status.

Example:

```
issue_id,url,source_file,issue,evidence,root_cause,fix,priority,status
SEO-001,https://aitoolgems.tech/tools/example/,tools/example/index.html,canonical_mismatch,canonical differs from sitemap,incorrect template,correct canonical generation,P0,open
```

Do not report a problem without evidence.

# **6. URL Architecture and Redirect Remediation**

Priority P1

The audit identifies 28+ internal URLs that may pass through redirects.

This number must be independently reproduced.

## **6.1 Redirect inventory**

Create:

`reports/seo/SEO_REDIRECT_INTERNAL_LINK_REGISTER.csv`

Columns:

```
source_file,source_page,anchor_text,original_href,http_status,redirect_hops,final_url,canonical_url,action,status
```

Example:

| Original internal URL | Final destination    | Action                              |
| --------------------- | -------------------- | ----------------------------------- |
| `/old-chatgpt-price/` | `/tools/chatgpt/`    | Update internal href                |
| `/ai-tools`           | `/tools/`            | Update if final canonical confirmed |
| `/old-guide/`         | `/guides/new-guide/` | Update if genuinely equivalent      |

These are examples, not verified live redirects.

## **6.2 Redirect investigation**

For every reported redirect:

1. Locate the source HTML or JavaScript.
2. Find the exact link.
3. Request the original URL.
4. Record status.
5. Follow each redirect.
6. Identify the final URL.
7. Check final canonical.
8. Check whether the destination has equivalent content.
9. Update the internal link.
10. Retain the legacy redirect when external users or backlinks still require it.

## **6.3 Correct implementation example**

Before:

```
<a href="/old-chatgpt-price/">
  ChatGPT Plus
</a>
```

After, if the final canonical route is verified:

```
<a href="/tools/chatgpt/">
  ChatGPT Plus
</a>
```

## **6.4 Redirect requirements**

- Internal links should point directly to final destinations.
- Legacy redirects should generally be single-hop.
- No redirect loops.
- No chains that unnecessarily traverse multiple URLs.
- No redirects from unrelated deleted pages to the homepage.
- No accidental redirect of a product to a different product.
- Preserve legitimate inbound URL compatibility.

## **6.5 Suggested redirect validation script**

If the existing link checker does not support redirect-chain inspection, extend it or create a narrowly scoped utility.

Illustrative Python:

```
from urllib.parse import urljoin, urlparseimport requestsBASE_URL = "https://aitoolgems.tech"def inspect_redirect(url):    absolute_url = urljoin(BASE_URL, url)    response = requests.get(        absolute_url,        allow_redirects=True,        timeout=15,        headers={            "User-Agent": "AI-Tool-Gems-SEO-Audit/1.0"        }    )    history = [        {            "url": item.url,            "status": item.status_code,            "location": item.headers.get("Location")        }        for item in response.history    ]    return {        "original_url": absolute_url,        "redirects": history,        "final_url": response.url,        "final_status": response.status_code,        "redirect_count": len(response.history),        "internal": (            urlparse(response.url).netloc            == urlparse(BASE_URL).netloc        )
```

Production implementation must additionally:

- Respect rate limits.
- Handle network errors.
- Avoid crawling external URLs without permission.
- Cache results.
- Apply retry limits.
- Identify redirects caused by authentication or anti-bot challenges.
- Distinguish permanent and temporary redirects.

Do not use this illustrative script as a replacement for the existing crawler until its coverage is compared.

# **7. Google Indexation and Crawlability**

Priority P0

## **7.1 Indexability decision framework**

Not every public URL should be indexed.

Create an explicit policy:

| Page type                      | Default decision                    | Sitemap     |
| ------------------------------ | ----------------------------------- | ----------- |
| Homepage                       | Index                               | Yes         |
| Commercial product             | Index if useful and genuine         | Yes         |
| Valuable directory profile     | Index if independently useful       | Yes         |
| Valuable category              | Index                               | Yes         |
| Original guide                 | Index                               | Yes         |
| Original blog article          | Index                               | Yes         |
| Contact page                   | Normally index                      | Yes         |
| About page                     | Normally index                      | Yes         |
| Privacy policy                 | Public and crawlable as appropriate | Usually yes |
| Terms page                     | Public and crawlable as appropriate | Usually yes |
| Internal search results        | Usually noindex                     | No          |
| Cart state                     | Usually noindex                     | No          |
| Parameterized comparison state | Usually noindex/canonical strategy  | No          |
| Private/admin page             | Access control first                | No          |
| Staged content                 | Noindex until approved              | No          |
| Genuine 404 page               | Noindex                             | No          |

## **7.2 Page lifecycle**

Use the existing HERMES content lifecycle where possible.

Recommended lifecycle:

```
STAGED_NOINDEX
       |
       v
TRUTH_VERIFIED
       |
       v
OWNER_APPROVED_INDEXABLE
       |
       v
SITEMAP_INCLUDED
       |
       v
LIVE_VALIDATED
       |
       v
SEARCH_CONSOLE_MONITORED
```

A page must not automatically enter the sitemap merely because a file exists.

## **7.3 Investigate Crawled — currently not indexed**

For every affected URL:

1. Open URL Inspection in GSC.
2. Record Google's selected canonical.
3. Record the user-declared canonical.
4. Check last crawl date.
5. Check the live test.
6. Inspect the actual rendered HTML.
7. Check robots restrictions.
8. Check internal link discovery.
9. Check whether the page is included in the sitemap.
10. Inspect content uniqueness.
11. Check whether a similar URL competes with it.
12. Inspect page rendering and resource loading.
13. Check the page's commercial/reference classification.
14. Compare it with indexed pages in the same category.
15. Record the actual suspected root cause.

Do not assume every Crawled — currently not indexed page needs more words.

### **Root-cause classification**

Use these categories:

- `DUPLICATE_CONTENT`
- `NEAR_DUPLICATE_CONTENT`
- `WEAK_INTERNAL_LINKING`
- `INCORRECT_CANONICAL`
- `NOINDEX_DIRECTIVE`
- `ROBOTS_BLOCK`
- `SOFT_404`
- `LOW_UNIQUE_VALUE`
- `INVALID_OR_MISLEADING_SCHEMA`
- `RENDERING_PROBLEM`
- `DISCOVERY_PROBLEM`
- `UNKNOWN_REQUIRES_INVESTIGATION`

## **7.4 Indexation remediation register**

Create:

`reports/seo/SEO_INDEXATION_REMEDIATION.csv`

```
url,gsc_status,last_crawl,google_canonical,user_canonical,sitemap_status,robots_status,content_status,root_cause,fix,validation_status
```

Do not request indexing for hundreds of URLs without correcting the underlying problems.

## **7.5 Important security distinction**

`noindex` is not a security mechanism.

For admin and private pages:

- Require authentication.
- Protect sensitive API endpoints.
- Keep secrets server-side.
- Exclude private files from public deployment.
- Prevent private records from entering public JavaScript.
- Use `noindex` as an additional search instruction only where appropriate.

# **8. Sitemap Implementation**

Priority P0

## **8.1 Sitemap requirements**

The sitemap must contain:

- Absolute HTTPS URLs.
- Preferred hostname.
- Final canonical paths.
- Public pages.
- Indexable pages.
- Pages returning HTTP 200.

It must exclude:

- Redirecting aliases.
- 404 pages.
- Noindex pages.
- Private pages.
- Query-string variants.
- Duplicate URLs.
- Staged content.
- Noncanonical pages.

## **8.2 Example sitemap**

```
<?xml version="1.0" encoding="UTF-8"?>

<urlset
  xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

  <url>
    <loc>https://aitoolgems.tech/</loc>
    <lastmod>2026-11-15</lastmod>
  </url>

  <url>
    <loc>https://aitoolgems.tech/tools/chatgpt/</loc>
    <lastmod>2026-11-15</lastmod>
  </url>

</urlset>
```

This is an illustrative template. Actual sitemap entries must be generated from the verified page inventory.

## **8.3 Sitemap generator logic**

Preferred logic:

```
def should_include_in_sitemap(page):    return all([        page.is_public,        page.is_indexable,        page.is_canonical,        page.http_status == 200,        not page.is_private,        not page.is_staged,        not page.has_query_parameters,    ])
```

Do not duplicate this logic across multiple generators.

## **8.4 Sitemap validation**

Implement these checks:

```
def validate_sitemap_url(page):    assert page.url.startswith("https://")    assert page.http_status == 200    assert page.is_indexable    assert page.is_canonical    assert not page.is_private    assert not page.is_redirect
```

In the real implementation, use the existing page model and proper exceptions rather than Python assertions alone.

## **8.5 Sitemap acceptance criteria**

- XML parses successfully.
- No duplicate `<loc>` values.
- No redirects.
- No 404 URLs.
- No noindex URLs.
- No staged URLs.
- No private URLs.
- Every entry matches its canonical.
- Every URL returns final HTTP 200.
- Lastmod reflects actual content modification.
- Sitemap generation is deterministic.

If the sitemap exceeds the protocol's limits, use sitemap indexes and multiple child sitemaps.

# **9. Robots.txt Implementation**

Priority P1

## **9.1 First inspect the current file**

Do not replace the current `robots.txt` blindly.

Check:

- Googlebot access.
- Bingbot access.
- CSS and JavaScript accessibility.
- Product routes.
- Guide routes.
- Category routes.
- Sitemap declaration.
- Existing AI crawler policies.
- Unintended broad disallow rules.

## **9.2 Conservative example**

```
User-agent: *
Allow: /

Sitemap: https://aitoolgems.tech/sitemap.xml
```

This is not automatically the final file. Existing approved crawler policies must be reconciled before changes.

## **9.3 Important rules**

Avoid:

```
Disallow: /tools/
```

if `/tools/` contains public commercial and directory content.

Avoid blocking essential rendering assets.

Do not use `robots.txt` to protect sensitive files.

Do not disallow a URL that Google needs to crawl to discover its `noindex` directive.

## **9.4 Robots validation checklist**

- Root file returns HTTP 200.
- Correct content type.
- Sitemap URL is correct.
- Important pages are crawlable.
- Important assets are crawlable.
- No unintended wildcard restrictions.
- No conflict between robots and noindex strategy.
- AI crawler rules have owner approval.

# **10. Canonical and Metadata Architecture**

## **10.1 Canonical implementation**

Each indexable page should have one canonical.

Example:

```
<link
  rel="canonical"
  href="https://aitoolgems.tech/tools/chatgpt/"
>
```

Validate:

- HTTPS.
- Preferred hostname.
- Correct trailing slash.
- No query parameters unless explicitly canonical.
- No redirecting canonical.
- No accidental cross-page canonical.
- No canonical to a noindex page.
- Consistency with sitemap.
- Consistency with Open Graph URL.
- Consistency with structured data.

## **10.2 Metadata requirements**

Every indexable page should have:

| Element                | Requirement                      |
| ---------------------- | -------------------------------- |
| Title                  | Unique and descriptive           |
| Meta description       | Accurate and useful              |
| H1                     | One clear primary page heading   |
| Canonical              | One correct canonical            |
| Open Graph title       | Consistent with page             |
| Open Graph description | Accurate                         |
| Open Graph URL         | Matches canonical                |
| Image metadata         | Relevant image where appropriate |
| Language               | Correct document language        |

Do not enforce arbitrary character lengths as a hard failure. Use length as a diagnostic.

## **10.3 Product metadata example**

```
<title>
ChatGPT Plus Price in Pakistan — AI Tool Gems
</title>

<meta
  name="description"
  content="Explore ChatGPT Plus plan details, verified pricing, access information and ordering options in Pakistan."
>

<link
  rel="canonical"
  href="https://aitoolgems.tech/tools/chatgpt/"
>

<meta
  property="og:type"
  content="product"
>

<meta
  property="og:title"
  content="ChatGPT Plus — AI Tool Gems"
>

<meta
  property="og:description"
  content="Explore plan details and ordering information."
>

<meta
  property="og:url"
  content="https://aitoolgems.tech/tools/chatgpt/"
>
```

All commercial information must be populated from current approved records.

## **10.4 Duplicate metadata audit**

Detect:

- Duplicate titles.
- Duplicate descriptions.
- Missing titles.
- Missing descriptions.
- Multiple H1s where unintended.
- Empty H1s.
- Canonical mismatches.
- Duplicate Open Graph URLs.

Do not automatically rewrite all duplicates with a generic template. Determine the correct page intent first.

# **11. Structured Data and Schema Implementation**

Priority P0

This section is particularly important because the website contains both commercial products and third-party software directory listings.

## **11.1 Schema mapping**

| Page type             | Recommended schema                    |
| --------------------- | ------------------------------------- |
| Homepage              | Organization, WebSite                 |
| Commercial product    | Product, Offer                        |
| Directory profile     | SoftwareApplication where appropriate |
| Category              | CollectionPage, ItemList              |
| Guide                 | Article                               |
| Blog post             | BlogPosting or Article                |
| Breadcrumb navigation | BreadcrumbList                        |
| Visible genuine FAQs  | FAQPage where appropriate             |

The choice must be based on what the page actually represents.

## **11.2 Product schema template**

Use this only for a genuine commercial listing sold by AI Tool Gems.

```
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "@id": "https://aitoolgems.tech/tools/PRODUCT-SLUG/#product",
  "name": "VERIFIED PRODUCT NAME",
  "description": "Description matching visible page content.",
  "url": "https://aitoolgems.tech/tools/PRODUCT-SLUG/",
  "brand": {
    "@type": "Brand",
    "name": "OFFICIAL BRAND NAME"
  },
  "offers": {
    "@type": "Offer",
    "url": "https://aitoolgems.tech/tools/PRODUCT-SLUG/",
    "priceCurrency": "PKR",
    "price": "VERIFIED_PRICE",
    "availability": "https://schema.org/InStock"
  }
}
</script>
```

### **Mandatory rules**

1. Price must be numeric.
2. Currency must match the visible price.
3. Availability must match actual fulfilment capability.
4. Product name must match the visible page.
5. URL must match the canonical.
6. Offer must represent a genuine current offer.
7. Do not use a stale price.
8. Do not add invented shipping or delivery information.
9. Do not add unsupported brand relationships.
10. Do not add review data without evidence.

## **11.3 Offer availability**

Possible Schema.org values include:

```
https://schema.org/InStock
https://schema.org/OutOfStock
https://schema.org/PreOrder
https://schema.org/BackOrder
https://schema.org/Discontinued
```

Select only a value that accurately describes the current offer.

If the offer is unavailable or enquiry-only, do not leave an outdated `InStock` Offer on the page.

## **11.4 Price consistency**

The same product price must be consistent across:

- Visible page.
- Product catalogue.
- Product card.
- Structured data.
- Approved feed.
- Merchant information, where applicable.

Example:

```
{
  "priceCurrency": "PKR",
  "price": "2300"
}
```

This is an example of formatting, not approval of a current product price.

If the product price changes, all dependent public representations must be regenerated from the same approved source.

## **11.5 Directory profile schema**

For a third-party software reference page:

```
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "@id": "https://aitoolgems.tech/tools/REFERENCE-SLUG/#software",
  "name": "VERIFIED SOFTWARE NAME",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web",
  "url": "https://OFFICIAL-SOFTWARE-URL/",
  "description": "Accurate description of the software."
}
</script>
```

Do not include `Offer` if AI Tool Gems does not sell that software.

Do not guess application categories, operating systems or features.

## **11.6 Breadcrumb schema**

```
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://aitoolgems.tech/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "AI Tools",
      "item": "https://aitoolgems.tech/tools/"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "ChatGPT Plus",
      "item": "https://aitoolgems.tech/tools/chatgpt/"
    }
  ]
}
</script>
```

The breadcrumb must match actual visible navigation.

## **11.7 Organization schema**

Use only genuine business details.

```
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://aitoolgems.tech/#organization",
  "name": "AI Tool Gems",
  "url": "https://aitoolgems.tech/",
  "logo": "https://aitoolgems.tech/ACTUAL-LOGO-PATH"
}
</script>
```

Do not add:

- Invented postal address.
- Invented telephone number.
- Fake sameAs profiles.
- Unsupported company registration.
- Fake vendor partnerships.
- Fake ratings.

## **11.8 Website schema**

```
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "@id": "https://aitoolgems.tech/#website",
  "url": "https://aitoolgems.tech/",
  "name": "AI Tool Gems",
  "publisher": {
    "@id": "https://aitoolgems.tech/#organization"
  }
}
</script>
```

## **11.9 Article schema**

```
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "VISIBLE ARTICLE TITLE",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://aitoolgems.tech/guides/ARTICLE-SLUG/"
  },
  "datePublished": "ACTUAL-PUBLICATION-DATE",
  "dateModified": "ACTUAL-MODIFICATION-DATE",
  "author": {
    "@type": "Organization",
    "name": "AI Tool Gems"
  },
  "publisher": {
    "@type": "Organization",
    "name": "AI Tool Gems"
  }
}
</script>
```

Use real dates and actual authorship.

## **11.10 FAQ schema**

Only mark up questions and answers visible to users.

Example:

```
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How can I order this subscription?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Follow the ordering instructions displayed on this page."
      }
    }
  ]
}
</script>
```

Do not expect FAQ rich results for every commercial page. Google restricts FAQ rich-result eligibility, and valid markup does not guarantee display.

## **11.11 Schema testing requirements**

For every page:

- Parse every JSON-LD script.
- Validate JSON syntax.
- Validate schema types.
- Check canonical consistency.
- Check product/offer consistency.
- Check currency and price.
- Check availability.
- Check directory listings for accidental Offer markup.
- Check ratings against actual review data.
- Check breadcrumb hierarchy.
- Check article publication dates.
- Detect duplicate entity IDs.

Use:

- Schema.org Validator.
- Google Rich Results Test where applicable.
- Search Console enhancement reports.

# **12. Homepage Optimization**

Priority P1

**Primary file:** `index.html`

Inspect the existing implementation before modifying it.

## **12.1 Metadata**

Create a unique title and description describing:

- AI software subscriptions.
- AI tools discovery.
- Pakistan commercial market.
- Accurate ordering information.

Do not stuff every target keyword into the homepage title.

## **12.2 Homepage content structure**

Recommended hierarchy:

```
H1: Discover AI Tools and Subscriptions with AI Tool Gems

Introduction:
Explain the marketplace, directory and ordering model.

H2: Popular AI Subscriptions
Commercial product cards.

H2: Explore AI Tools
Free and external reference tools.

H2: Browse AI Tool Categories
Category links.

H2: Guides and Comparisons
Informational content.

H2: How Ordering Works
Accurate customer instructions.

H2: Frequently Asked Questions
Visible questions and answers.

H2: About AI Tool Gems
Trust and support information.
```

This is a suggested hierarchy, not an instruction to duplicate sections that already exist.

## **12.3 Featured products**

The audit suggests 12–16 homepage tools.

Implement a curated list only when it improves user discovery.

Rules:

- No duplicate cards.
- No invented popularity rankings.
- No fake bestseller labels.
- No unsupported discount labels.
- Commercial and directory cards must be distinguishable.
- Every card must link to a crawlable URL.
- Avoid JavaScript-only navigation.

## **12.4 Empty search state**

The reported “No matching tools found” message should not appear on initial page load.

Example:

```
<p
  id="noResults"
  class="empty-state"
  hidden
  aria-live="polite"
>
  No matching tools found.
  Try a different keyword or category.
</p>
```

Illustrative JavaScript:

```
const noResults = document.getElementById("noResults");

function updateSearchResults(filteredProducts) {
  if (!noResults) return;

  noResults.hidden = filteredProducts.length !== 0;
}
```

Integrate with the actual existing search function. Do not create a second independent search implementation.

## **12.5 Correct directory CTA**

Commercial:

```
<a href="/tools/chatgpt/">
  View Subscription
</a>
```

Directory:

```
<a
  href="/tools/example/"
  aria-label="Explore Example Tool"
>
  Explore Tool
</a>
```

External official destination:

```
<a
  href="https://official.example/"
  target="_blank"
  rel="noopener noreferrer"
>
  Visit Official Website
</a>
```

Use the actual official destination only after verification.

## **12.6 Homepage acceptance tests**

- Unique title.
- Unique description.
- Correct canonical.
- Correct H1.
- Search empty state hidden initially.
- Search empty state appears when appropriate.
- Commercial cards link correctly.
- Directory cards link correctly.
- No false pricing.
- No duplicate listings.
- Crawlable category navigation.
- Mobile layout works.
- Schema matches visible content.

# **13. Product Page Optimization**

Priority P0

**Target paths:** `tools/<slug>/index.html`

The product pages are important transactional landing pages.

## **13.1 Recommended page structure**

```
Breadcrumbs

H1: [Tool] [Plan] — Pricing and Subscription Details

Product summary

Current verified price

Availability

Subscription specifications

What the customer receives

Who should use this plan

Important limitations

Ordering instructions

Supported payment methods

Frequently asked questions

Related guides

Related products

Verification/update information
```

## **13.2 Product specification table**

Recommended visible fields:

| Field         | Example                      |
| ------------- | ---------------------------- |
| Product       | Actual product name          |
| Plan          | Exact official plan name     |
| Price         | Approved PKR price           |
| Duration      | Verified subscription period |
| Access type   | Verified access arrangement  |
| Activation    | Actual activation method     |
| Delivery      | Verified fulfilment process  |
| Support       | Approved support terms       |
| Availability  | Current state                |
| Last verified | Actual date                  |

Do not display unknown fields as facts.

## **13.3 Content requirements**

Every product page must explain:

- What the product does.
- Which plan is offered.
- What the buyer receives.
- How access is provided.
- Which terms apply.
- How ordering works.
- Which payment methods are accepted.
- What support is available.
- What the product does not include.
- Which guides can help the customer.

Avoid copying the same 300–500-word description across products.

## **13.4 Product H1 examples**

```
ChatGPT Plus: Pricing and Ordering in Pakistan
```

```
Gemini Pro: Plan Details and Subscription Options
```

```
Canva Pro: Subscription Details and Pricing in Pakistan
```

Use official current plan names.

## **13.5 Product FAQs**

Possible questions:

- What does this plan include?
- How long does the subscription last?
- How is access provided?
- Which payment methods are supported?
- How can I contact support?
- What happens if activation fails?
- Is renewal included?
- What limitations should I know?

Only publish answers confirmed by the business.

## **13.6 Product page internal links**

Each product should link to:

- Relevant category.
- Relevant setup guide.
- Relevant comparison article.
- Related product where appropriate.
- Contact/support page.

Avoid irrelevant links solely to increase internal-link counts.

## **13.7 Product page quality gate**

A product page is ready only when:

- Correct product.
- Correct plan.
- Verified current price or enquiry-only status.
- Correct availability.
- Accurate access description.
- Accurate delivery description.
- Accurate policy links.
- Unique useful content.
- Correct canonical.
- Valid Product/Offer schema.
- No fabricated ratings.
- Correct internal links.
- Functional order CTA.

# **14. Directory Profile Optimization**

Priority P1

Directory pages are important because they provide discovery value beyond the commercial catalogue.

## **14.1 Directory page structure**

```
Breadcrumb

H1: [Software Name] — Features, Uses and Alternatives

Introduction

What is [Software]?

Key capabilities

Best use cases

Who should use it?

Who may not need it?

Free plan or pricing information
(Only when verified)

Limitations

Alternatives

Official website

Related AI Tool Gems categories

Last checked date

Sources
```

## **14.2 Directory content differentiation**

For each profile, investigate:

- Product purpose.
- Primary audience.
- Important capabilities.
- Actual free-plan restrictions.
- Usage limits.
- Supported platforms.
- Official pricing.
- Important limitations.
- Alternatives.
- Official documentation.

Use official vendor documentation for product claims.

Do not reproduce marketing descriptions without adding meaningful independent value.

## **14.3 Correct CTA**

For a free/reference listing:

```
<a href="https://OFFICIAL-VERIFIED-URL/">
  Explore Official Tool
</a>
```

For a commercial listing:

```
<a href="/tools/VERIFIED-COMMERCIAL-SLUG/">
  View Subscription
</a>
```

The CTA must reflect the actual commercial status.

## **14.4 Directory schema rules**

- `SoftwareApplication` may be suitable.
- `BreadcrumbList` may be suitable.
- `Product` should only be used where it accurately represents the page.
- Do not generate an AI Tool Gems Offer for a third-party tool merely because the directory lists it.

## **14.5 Directory page acceptance criteria**

- Unique description.
- Useful original information.
- Official URL verified.
- Feature claims verified.
- Free-plan claims verified.
- No fake prices.
- No order CTA for noncommercial listings.
- No incorrect Offer schema.
- Related links are relevant.
- Canonical correct.
- Sitemap status correct.

# **15. Category Page Optimization**

**Target paths:** Existing verified `category/` routes.

## **15.1 Recommended category structure**

```
Breadcrumb

H1: [Category] AI Tools and Subscriptions

Category introduction

How to choose the right tool

Featured tools

Comparison criteria

Relevant guides

Frequently asked questions

Related categories
```

## **15.2 Category page requirements**

- One unique page purpose.
- Useful introduction.
- Real tool listings.
- Crawlable links to child pages.
- Correct canonical.
- Appropriate schema.
- No keyword doorway pages.
- No duplicated category descriptions.

## **15.3 Category schema example**

```
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "@id": "https://aitoolgems.tech/category/EXAMPLE/#page",
  "name": "EXAMPLE AI Tools",
  "url": "https://aitoolgems.tech/category/EXAMPLE/"
}
</script>
```

Only use this example after verifying the actual category URL.

# **16. Blog and Guide Optimization**

Priority P1

## **16.1 Separate search intent**

| Search intent             | Correct landing page |
| ------------------------- | -------------------- |
| Price and purchase        | Product page         |
| Subscription availability | Product page         |
| Setup instructions        | Guide                |
| How-to questions          | Guide                |
| Product comparison        | Comparison article   |
| Free alternatives         | Directory/guide      |
| Category discovery        | Category page        |

## **16.2 Example: ChatGPT Plus**

Commercial page:

```
/tools/chatgpt/
```

Potential guide:

```
/guides/how-to-use-chatgpt-plus/
```

Potential comparison:

```
/guides/chatgpt-plus-vs-gemini/
```

The actual URLs must be checked before creating new pages.

## **16.3 Guide content structure**

```
H1: Clear informational question

Short answer

Detailed explanation

Step-by-step instructions

Real examples

Important limitations

Common mistakes

Sources

Related products

Related guides

Updated information
```

## **16.4 Product/blog cannibalization**

Create:

`reports/seo/SEO_KEYWORD_INTENT_MAP.csv`

Columns:

```
keyword_cluster,query,search_intent,primary_url,secondary_url,current_rank,clicks,impressions,decision
```

For each overlap:

1. Compare query intent.
2. Compare ranking URLs.
3. Compare titles and H1s.
4. Compare page content.
5. Compare backlinks if available.
6. Determine whether the pages genuinely overlap.
7. Decide whether to rewrite, differentiate, consolidate or redirect.
8. Preserve useful existing URLs.

Do not merge pages based only on shared keywords.

## **16.5 Article quality checklist**

- Search intent clear.
- Original information.
- Accurate claims.
- Reliable sources.
- Relevant examples.
- Useful internal links.
- No unnecessary keyword repetition.
- No copied product-page description.
- Correct author/date information.
- Correct canonical.
- Correct article schema.

# **17. Internal Linking Architecture**

Internal linking should establish a clear relationship between commercial pages, reference profiles, categories and educational content.

## **17.1 Recommended hierarchy**

```
Homepage
   |
   +-- Commercial Products
   |      |
   |      +-- Product Pages
   |      |      |
   |      |      +-- Relevant Guides
   |      |      +-- Related Products
   |      |
   |      +-- Product Categories
   |
   +-- AI Tools Directory
   |      |
   |      +-- Directory Profiles
   |      +-- Official Websites
   |
   +-- Guides
   |      |
   |      +-- Comparisons
   |      +-- Tutorials
   |
   +-- Blog
   |
   +-- About / Contact / Policies
```

## **17.2 Crawlable anchor links**

Prefer:

```
<a href="/tools/canva/">
  Canva Pro subscription details
</a>
```

Avoid making important navigation depend exclusively on JavaScript click handlers.

## **17.3 Anchor-text diversity**

Good examples:

- Canva Pro pricing details.
- Compare AI design tools.
- ChatGPT Plus subscription information.
- Guide to using AI writing tools.
- Explore free research tools.

Avoid repetitive exact-match anchors across every page.

## **17.4 Orphan-page detection**

An indexable page should have an appropriate internal discovery path.

Find pages that:

- Exist but have zero incoming internal links.
- Are only reachable through search.
- Are included in sitemap but not linked anywhere.
- Are linked only through broken routes.
- Are linked only through noindex pages.

Not every page requires a homepage link. The objective is a logical crawlable hierarchy.

# **18. Image and Media SEO**

## **18.1 Image requirements**

For every meaningful image:

- Descriptive filename.
- Appropriate format.
- Appropriate dimensions.
- Responsive sizing.
- Useful alt text.
- Correct aspect ratio.
- No unnecessary oversized assets.

Example:

```
<img
  src="/assets/images/chatgpt-plus-plan.webp"
  alt="ChatGPT Plus subscription plan information"
  width="800"
  height="450"
  loading="lazy"
  decoding="async"
>
```

For above-the-fold hero images, do not automatically use lazy loading if it delays the Largest Contentful Paint.

Decorative images should use:

```
alt=""
```

## **18.2 Image duplication**

Check:

- Duplicate image assets.
- Missing images.
- Broken image URLs.
- Incorrect MIME types.
- Oversized images.
- Images with misleading filenames.
- Images without dimensions.

## **18.3 Open Graph images**

Use a relevant, properly sized social-sharing image.

Do not use a product image that implies a different product or plan.

# **19. International SEO**

AI Tool Gems serves Pakistan as its primary commercial market and supports international discovery and legitimate inquiries.

## **19.1 Market strategy**

Primary:

- Pakistan.
- PKR pricing.
- Pakistan-specific ordering information.
- Supported Pakistan payment methods.
- Local customer questions.

International:

- Worldwide discoverability.
- Accurate product information.
- Inquiry access.
- Transparent payment limitations.
- No fabricated country-specific commercial presence.

## **19.2 Avoid artificial country pages**

Do not create:

```
/tools/chatgpt-in-usa/
/tools/chatgpt-in-uk/
/tools/chatgpt-in-canada/
/tools/chatgpt-in-australia/
```

unless each page serves a genuine distinct market need and has real localized information.

Do not create doorway pages with identical content and only a country name changed.

## **19.3 Hreflang**

Do not implement hreflang merely because international visitors exist.

If the website has only one English version, there may be no useful alternate language/region page to connect.

If genuinely localized alternatives are later created:

- Use valid hreflang values.
- Ensure reciprocal annotations.
- Use self-referencing canonical URLs.
- Ensure every localized page is genuinely localized.
- Include an appropriate x-default only where applicable.

## **19.4 Currency**

Do not convert PKR prices into USD, EUR or GBP and display them as actual selling prices unless the business genuinely offers those currencies at those prices.

# **20. Business Trust and E-E-A-T**

## **20.1 Trust pages**

Inspect actual existing routes for:

- About.
- Contact.
- Privacy.
- Terms.
- Refund policy.
- Product verification.
- Pricing methodology.
- Sourcing methodology.
- Review methodology.

Previously referenced filenames include:

```
about.html
contact.html
terms.html
privacy.html
how-we-price.html
how-we-review.html
how-we-source.html
product-verification.html
```

Verify the current repository and deployed routes before using them.

## **20.2 Trust content**

Explain:

- What AI Tool Gems provides.
- How customers place orders.
- How availability is checked.
- How prices are determined.
- What access arrangements mean.
- Which payment methods are supported.
- How support works.
- What refund/replacement terms apply.
- How customer information is handled.
- Whether the marketplace is independent of third-party vendors.

## **20.3 Contact consistency**

Check that contact information is consistent across:

- Homepage.
- Footer.
- Contact page.
- Product pages.
- Policies.
- Structured data.
- Social profiles where officially controlled.

Do not invent a physical business address.

## **20.4 Customer reviews**

If testimonials are displayed:

- Obtain permission where needed.
- Do not fabricate customers.
- Do not fabricate transaction history.
- Do not imply testimonials are independently verified if they are not.
- Do not use fake review schema.

# **21. Google AdSense Readiness**

AdSense readiness should be reviewed independently from technical SEO.

## **21.1 Policy review**

Inspect:

- Original content.
- Clear navigation.
- Contact information.
- About information.
- Privacy policy.
- Accurate business claims.
- Transparent third-party product descriptions.
- Non-deceptive advertising placement.
- No misleading download buttons.
- No forced redirects.
- No artificial traffic manipulation.
- No mass-produced duplicate pages.

## **21.2 Commercial marketplace transparency**

Clearly distinguish:

- AI Tool Gems services.
- Third-party products.
- External official websites.
- Paid subscriptions.
- Free reference tools.
- Customer support.
- Payment and fulfilment terms.

Do not claim AdSense approval is guaranteed.

## **21.3 Consent and analytics**

Preserve the existing Consent Mode v2 implementation.

Do not enable dormant analytics tools or introduce synthetic analytics events without authorization.

Verify that privacy and consent statements match actual implementation.

# **22. Core Web Vitals and Performance**

Priority P2

Technical SEO should include performance, rendering and mobile usability.

## **22.1 Core Web Vitals**

Monitor:

| Metric | What it measures          | Good target   |
| ------ | ------------------------- | ------------- |
| LCP    | Largest Contentful Paint  | ≤ 2.5 seconds |
| INP    | Interaction to Next Paint | ≤ 200 ms      |
| CLS    | Cumulative Layout Shift   | ≤ 0.1         |

These are the standard good thresholds at the 75th percentile.

## **22.2 Investigation**

Inspect:

- Homepage.
- Main directory.
- Major product pages.
- Category pages.
- Guides.
- Mobile and desktop separately.

Investigate:

1. Large images.
2. Render-blocking CSS.
3. Render-blocking JavaScript.
4. Excessive third-party scripts.
5. Font loading.
6. Layout shifts.
7. Slow server responses.
8. Unnecessary JavaScript execution.
9. Long main-thread tasks.
10. Mobile navigation performance.

## **22.3 Performance implementation**

Potential optimizations:

- Convert suitable images to WebP or AVIF.
- Add image dimensions.
- Lazy-load below-the-fold images.
- Preload only critical assets.
- Minimize unnecessary JavaScript.
- Defer noncritical scripts.
- Reduce unused CSS.
- Avoid unnecessary third-party requests.
- Use browser caching appropriately.
- Avoid loading large assets on every page when they are not needed.

Do not introduce aggressive optimization that breaks:

- Search.
- Product filters.
- Cart.
- WhatsApp ordering.
- Product comparison.
- Animations.
- Consent functionality.

## **22.4 Performance tests**

Use:

- PageSpeed Insights.
- Lighthouse.
- Chrome DevTools.
- Search Console Core Web Vitals.

Capture before-and-after results.

Do not claim a performance improvement based only on smaller file sizes. Verify the actual page.

# **23. Automated SEO Testing Architecture**

The existing Python tooling should remain the main validation framework.

The goal is to extend existing scripts rather than create multiple competing SEO auditors.

## **23.1 Existing tools to inspect**

| Tool                            | Proposed responsibility                       |
| ------------------------------- | --------------------------------------------- |
| `scripts/link_graph_checker.py` | Internal links, redirects, fragments, orphans |
| `schema_audit.py`               | Structured-data validation                    |
| `audit_all.py`                  | Combined audit execution                      |
| `scripts/validate_content.py`   | Content structure and quality checks          |
| Existing catalogue tests        | Product/directory consistency                 |
| `scripts/build_public_site.py`  | Public deployment safety                      |

Inspect their current CLI, dependencies, output format and test coverage first.

## **23.2 Proposed test architecture**

```
tests/
    test_seo_metadata.py
    test_seo_canonicals.py
    test_seo_sitemap.py
    test_seo_robots.py
    test_seo_redirects.py
    test_seo_schema.py
    test_seo_product_offers.py
    test_seo_directory_profiles.py
    test_seo_internal_links.py
    test_seo_content_quality.py
    test_seo_indexation_policy.py
```

These are proposed filenames. If equivalent test modules exist, extend those instead.

## **23.3 Metadata tests**

Required checks:

- Missing title.
- Duplicate title.
- Missing description.
- Duplicate description.
- Missing H1.
- Unexpected multiple H1.
- Missing canonical.
- Duplicate canonical.
- Canonical mismatch.
- Open Graph mismatch.

Illustrative Python:

```
from bs4 import BeautifulSoupdef inspect_metadata(html):    soup = BeautifulSoup(html, "html.parser")    titles = soup.find_all("title")    descriptions = soup.find_all(        "meta",        attrs={"name": "description"}    )    canonicals = soup.find_all(        "link",        rel="canonical"    )    return {        "title_count": len(titles),        "description_count": len(descriptions),        "canonical_count": len(canonicals),        "h1_count": len(soup.find_all("h1")),        "title": (            titles[0].get_text(strip=True)            if titles else None        ),        "description": (            descriptions[0].get("content")            if descriptions else None        ),        "canonical": (            canonicals[0].get("href")            if canonicals else None        )    }
```

Production code must handle malformed HTML, missing dependencies and multiple metadata tags safely.

## **23.4 Canonical tests**

Example:

```
def test_indexable_page_has_one_canonical(page):    if not page.is_indexable:        return    assert len(page.canonicals) == 1    assert page.canonicals[0] == page.expected_canonical
```

Use the actual page model and testing conventions.

## **23.5 Sitemap tests**

Example:

```
def test_sitemap_excludes_noindex_pages(sitemap, pages):    sitemap_urls = set(sitemap.urls)    for page in pages:        if not page.is_indexable:            assert page.canonical_url not in sitemap_urls
```

Additional tests must verify:

- Duplicate URLs.
- Redirects.
- 404 responses.
- Private URLs.
- Staged pages.
- Query parameters.
- Canonical mismatch.

## **23.6 Product and directory tests**

```
def test_directory_profiles_are_not_orderable(catalogue):    for item in catalogue:        if item.listing_type == "directory":            assert item.is_orderable is False
```

```
def test_directory_profiles_have_no_commercial_offer(    directory_pages):    for page in directory_pages:        for entity in page.jsonld_entities:            assert entity.get("@type") != "Offer"
```

The second example is intentionally simplified. In production, inspect the entity graph and relationships to distinguish legitimate unrelated entities from a commercial Offer attached to the directory listing.

## **23.7 Offer consistency tests**

```
def test_offer_price_matches_catalogue(page, product):    if not product.is_orderable:        assert page.offer is None        return    assert page.offer["priceCurrency"] == "PKR"    assert str(page.offer["price"]) == str(        product.approved_price    )
```

Do not use an unverified old price as the test fixture.

## **23.8 Rating tests**

```
def test_reviews_require_verified_source(page):    if not page.has_verified_reviews:        assert page.aggregate_rating is None        assert page.review_markup is None
```

## **23.9 Internal redirect tests**

```
def test_internal_links_use_final_urls(link_graph):    for link in link_graph.internal_links:        assert link.href not in link_graph.redirect_sources
```

This test should operate against the known redirect map and avoid falsely failing external or intentionally supported routes.

## **23.10 Test runner**

Use the project's documented commands.

Potential commands:

```
python -m pytest
```

```
python scripts/link_graph_checker.py
```

```
python schema_audit.py
```

```
python audit_all.py
```

The last three commands must be checked against the actual script CLI before execution. Do not assume they all support execution without arguments.

## **23.11 Test reporting**

Each audit should report:

```
Total pages checked:
Indexable pages:
Noindex pages:
Canonical errors:
Sitemap errors:
Redirecting internal links:
Broken internal links:
Orphan pages:
Schema parsing errors:
Product Offer errors:
Directory classification errors:
Metadata errors:
Content quality warnings:
Security/deployment violations:
```

Include exact URLs and file paths for failures.

A summary such as “SEO checks passed” without a URL-level evidence report is insufficient.

# **24. Google Search Console Validation**

The repository's technical changes must be connected to actual Search Console evidence.

## **24.1 Required GSC data**

Collect:

- Search performance.
- Queries.
- Pages.
- Countries.
- Devices.
- Search appearance.
- Indexing status.
- Sitemap status.
- Crawl statistics.
- Core Web Vitals.
- Manual actions.
- Security issues.
- Enhancement reports, where available.

Use the existing authorized GSC integration or read-only access.

Do not introduce new credentials or permissions without approval.

## **24.2 Performance analysis**

Analyze:

| Metric           | Investigation                |
| ---------------- | ---------------------------- |
| Clicks           | Actual search traffic        |
| Impressions      | Search visibility            |
| CTR              | Search result attractiveness |
| Average position | Ranking trend                |
| Query            | Search intent                |
| Page             | Landing-page selection       |
| Country          | Market visibility            |
| Device           | Desktop/mobile differences   |

## **24.3 Query-to-page analysis**

For every important query:

1. Find the ranking page.
2. Check whether it matches the intent.
3. Check competing URLs.
4. Inspect CTR.
5. Inspect position.
6. Inspect impressions.
7. Compare historical performance.
8. Identify whether title or content needs adjustment.

## **24.4 Crawl statistics**

Investigate:

- Total crawl requests.
- Host status.
- Average response time.
- Response code distribution.
- File type distribution.
- Crawl purpose.
- Googlebot type.

Where the Crawl Stats report provides these dimensions, inspect each available breakdown.

For problematic responses, identify the exact URL and root cause.

Do not simply report that Google crawled fewer pages. Explain which URLs produced the change and whether the change is beneficial or harmful.

## **24.5 Post-implementation validation**

For each priority URL:

- Run URL Inspection.
- Inspect declared canonical.
- Inspect Google's selected canonical.
- Check last crawl.
- Run live test.
- Inspect rendered HTML.
- Verify sitemap status.
- Verify indexability.

A live test passing does not prove indexing.

## **24.6 Monitoring intervals**

Suggested operational schedule:

| Time           | Action                                        |
| -------------- | --------------------------------------------- |
| Before release | Capture baseline                              |
| Release day    | Verify changed URLs                           |
| 24–72 hours    | Check technical errors and live accessibility |
| 7 days         | Review crawl and indexing observations        |
| 14 days        | Review priority URL status                    |
| 28 days        | Compare performance and indexation trends     |

These are monitoring intervals, not guaranteed Google processing times.

# **25. Bing and AI Search Visibility**

Google is important, but the website should also maintain technically sound discovery across Bing and AI-powered search experiences.

## **25.1 Bing Webmaster Tools**

Review:

- Sitemap.
- URL inspection.
- Crawl errors.
- Indexation.
- Search performance.
- Backlink information where available.
- Site scan issues.

Keep the canonical and sitemap architecture consistent.

## **25.2 AI search readiness**

Improve the ability of search and answer systems to understand:

- What AI Tool Gems is.
- Which products it sells.
- Which tools are reference listings.
- How customers order.
- Which markets it serves.
- What pricing and fulfilment claims are verified.

## **25.3 Content structure**

Prefer:

- Clear definitions.
- Direct answers.
- Descriptive headings.
- Accurate tables.
- Original comparisons.
- Named sources.
- Updated factual information.
- Consistent entity names.

Avoid:

- Unsupported superlatives.
- Artificial FAQ sections.
- Repetitive keyword stuffing.
- Fake citations.
- Mass-produced location pages.

## **25.4 AI crawler policy**

Review existing crawler directives.

Do not automatically allow or block every AI crawler.

Make the decision based on:

- Business goals.
- Content ownership.
- Privacy.
- Licensing.
- Crawling load.
- Search visibility strategy.

Preserve the existing approved policy unless an explicit change is authorized.

# **26. HERMES Integration**

The SEO remediation should fit the existing HERMES architecture.

It should not create a separate, competing SEO agent system.

## **26.1 Integration objectives**

Connect the implementation with existing:

- Catalogue verification.
- Page lifecycle.
- Sitemap generation.
- Schema validation.
- Internal link graph.
- Content validation.
- Search Console monitoring.
- Reporting.

## **26.2 Suggested logical architecture**

```
                 PUBLIC SITE REPOSITORY
                          |
                          v
                  PAGE INVENTORY
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
      CATALOGUE        CONTENT          ROUTES
      VALIDATION       VALIDATION       VALIDATION
          |               |               |
          +---------------+---------------+
                          |
                          v
                   SEO VALIDATION
                          |
       +------------------+------------------+
       |                  |                  |
       v                  v                  v
    SCHEMA             SITEMAP          LINK GRAPH
    AUDIT              AUDIT             AUDIT
       |                  |                  |
       +------------------+------------------+
                          |
                          v
                   QUALITY GATES
                          |
                          v
                   OWNER APPROVAL
                          |
                          v
                    PUBLIC BUILD
                          |
                          v
                      DEPLOY
                          |
                          v
                   LIVE VALIDATION
                          |
                          v
                    GSC MONITORING
```

## **26.3 Existing lifecycle integration**

Respect the existing page lifecycle:

```
STAGED_NOINDEX
TRUTH_VERIFIED
OWNER_APPROVED_INDEXABLE
SITEMAP_INCLUDED
LIVE_VALIDATED
```

Do not bypass approval gates through an automated SEO agent.

## **26.4 Automation guardrails**

SEO agents may:

- Discover issues.
- Generate reports.
- Suggest content improvements.
- Propose internal link changes.
- Validate schemas.
- Detect duplicate content.
- Recommend keyword mappings.
- Prepare PR changes.

SEO agents must not independently:

- Publish unverified pricing.
- Invent product details.
- Create fake reviews.
- Change production routing.
- Remove important pages.
- Push to main.
- Deploy.
- Modify protected secrets.
- Override owner-approved indexing decisions.

## **26.5 Reporting**

Use existing HERMES report locations and naming conventions.

If an equivalent report already exists, update or reference it instead of creating a duplicate reporting system.

# **27. File-by-File Change Register**

This is the central implementation register for Antigravity.

The exact paths below distinguish known paths from paths that must first be discovered.

| File/path                            | Action                        | Change details                                          | Priority |
| ------------------------------------ | ----------------------------- | ------------------------------------------------------- | -------- |
| `AGENTS.md`                          | Read                          | Understand all operating and safety rules               | P0       |
| `index.html`                         | Inspect / modify if required  | Homepage metadata, content, navigation, empty state     | P1       |
| `app.js`                             | Inspect / modify if required  | Catalogue classification, search state and rendering    | P0       |
| `tools/index.html`                   | Inspect / modify if required  | Directory metadata, introductory content, links         | P1       |
| `tools/chatgpt/index.html`           | Inspect / modify if required  | Product page schema and content                         | P0       |
| Other `tools/*/index.html`           | Inspect / modify              | All commercial and reference profiles                   | P0       |
| `category/`                          | Inspect / modify              | Category introductions, links and schema                | P1       |
| `guides/`                            | Inspect / modify              | Informational intent and contextual links               | P1       |
| `blog/`                              | Inspect / modify              | Content quality and cannibalization                     | P1       |
| `sitemap.xml`                        | Regenerate or update source   | Only eligible canonical URLs                            | P0       |
| `robots.txt`                         | Inspect / modify if required  | Crawl access and sitemap declaration                    | P0       |
| `scripts/link_graph_checker.py`      | Extend                        | Redirect and internal-link validation                   | P1       |
| `schema_audit.py`                    | Extend                        | Page-type and semantic schema validation                | P0       |
| `audit_all.py`                       | Extend                        | Integrate compatible audit modules                      | P1       |
| `scripts/validate_content.py`        | Extend if needed              | Content structure and factual validation                | P1       |
| `scripts/build_public_site.py`       | Inspect                       | Preserve deployment allowlist and public staging safety | P0       |
| Existing catalogue tests             | Extend                        | Product/directory and orderability consistency          | P0       |
| `.github/workflows/deploy-pages.yml` | Inspect only unless necessary | Preserve deployment restrictions                        | P0       |
| `docs/SEO-AND-GSC-PLAN.md`           | Update if needed              | Reflect verified implementation                         | P2       |

### **27.1 Additional reports**

Create only if equivalent reports do not already exist:

```
reports/
    seo/
        SEO_IMPLEMENTATION_FILE_MAP.md
        SEO_REMEDIATION_BASELINE.md
        SEO_REDIRECT_INTERNAL_LINK_REGISTER.csv
        SEO_URL_INDEXATION_REGISTER.csv
        SEO_SCHEMA_VALIDATION_REPORT.md
        SEO_INTENT_CANNIBALIZATION_MAP.csv
        SEO_CONTENT_REMEDIATION_REGISTER.csv
        SEO_FINAL_VALIDATION_REPORT.md
```

Do not create all these reports if the existing HERMES reporting structure already provides equivalent outputs.

# **28. Implementation Phases**

The work should be performed in controlled phases.

## **Phase 0 — Repository baseline**

P0

Tasks:

- Read repository instructions.
- Record branch and commit.
- Record dirty working tree.
- Locate all SEO-related files.
- Identify product catalogue source.
- Identify sitemap generator.
- Identify redirect configuration.
- Identify schema generator.
- Identify public deployment allowlist.
- Identify existing tests.
- Read previous audit reports.
- Avoid repeating audits for which current evidence already exists.

Deliverable:

`SEO_IMPLEMENTATION_FILE_MAP.md`

Exit criteria: Every planned file change has a verified source path and owner.

## **Phase 1 — Complete URL and crawl inventory**

P0

Tasks:

- Crawl every public page.
- Classify every URL.
- Record status codes.
- Record redirect chains.
- Record canonical tags.
- Record robots directives.
- Record sitemap membership.
- Record internal link count.
- Identify orphan pages.
- Identify duplicate metadata.
- Identify missing metadata.
- Identify staged and private URLs.

Deliverable:

`SEO_URL_INDEXATION_REGISTER.csv`

Exit criteria: Every known public URL has an indexability decision.

## **Phase 2 — Redirect and internal link remediation**

P1

Tasks:

- Reproduce the 28+ redirect count.
- Identify exact redirect sources.
- Identify final destinations.
- Check canonical URLs.
- Update internal hrefs.
- Preserve necessary legacy redirects.
- Check redirect loops.
- Check orphan pages.
- Re-run link graph checker.

Deliverable:

`SEO_REDIRECT_INTERNAL_LINK_REGISTER.csv`

Exit criteria: No avoidable internal redirect links remain.

## **Phase 3 — Indexation and sitemap**

P0

Tasks:

- Inspect Crawled — currently not indexed URLs.
- Inspect Discovered — currently not indexed URLs.
- Investigate accidental noindex directives.
- Investigate canonical mismatches.
- Verify robots accessibility.
- Verify sitemap generation.
- Exclude staged/private/noindex pages.
- Validate all sitemap destinations.
- Verify lastmod accuracy.
- Test public deployment output.

Deliverable:

`SEO_INDEXATION_VALIDATION_REPORT.md`

Exit criteria: Sitemap and indexability policy agree.

## **Phase 4 — Structured data**

P0

Tasks:

- Audit all existing JSON-LD blocks.
- Identify schema by page type.
- Correct commercial Product/Offer data.
- Correct directory/reference schemas.
- Add BreadcrumbList where appropriate.
- Add Organization/WebSite where accurate.
- Add Article markup where appropriate.
- Remove fabricated or unsupported ratings.
- Check schema entity IDs.
- Check visible content consistency.
- Add automated tests.

Deliverable:

`SEO_SCHEMA_VALIDATION_REPORT.md`

Exit criteria: No known schema errors or unsupported commercial claims.

## **Phase 5 — Homepage and product pages**

P1

Tasks:

- Correct homepage empty state.
- Improve homepage metadata.
- Verify homepage H1.
- Verify homepage crawlable links.
- Separate directory and commercial CTAs.
- Review all major product pages.
- Verify price and plan details.
- Improve product specifications.
- Improve product FAQs.
- Correct product schema.
- Add relevant contextual links.

Deliverable:

`SEO_PRODUCT_PAGE_REMEDIATION_REPORT.md`

Exit criteria: Priority commercial pages contain accurate, unique and useful information.

## **Phase 6 — Directory and category content**

P1

Tasks:

- Review every directory profile.
- Identify repetitive templates.
- Verify official product links.
- Verify free-plan claims.
- Verify feature claims.
- Add relevant limitations.
- Add genuine alternatives.
- Correct CTA behaviour.
- Correct schema.
- Review category content.
- Check category-to-child links.

Deliverable:

`SEO_DIRECTORY_CONTENT_REMEDIATION_REPORT.md`

Exit criteria: Reference listings provide genuine independent discovery value.

## **Phase 7 — Blog and keyword intent**

P1

Tasks:

- Export important GSC queries.
- Map queries to URLs.
- Identify transactional queries.
- Identify informational queries.
- Identify comparison queries.
- Identify cannibalization candidates.
- Check competing pages.
- Revise page intent where justified.
- Improve contextual internal links.
- Avoid unnecessary URL changes.

Deliverable:

`SEO_INTENT_CANNIBALIZATION_MAP.csv`

Exit criteria: Priority queries have an intentional primary landing page.

## **Phase 8 — Trust, metadata and performance**

P2

Tasks:

- Review About and Contact pages.
- Review policies.
- Verify payment statements.
- Verify fulfilment claims.
- Review trust information.
- Review title and description uniqueness.
- Inspect mobile performance.
- Inspect Core Web Vitals.
- Fix verified performance issues.
- Preserve consent implementation.

Exit criteria: No unsupported business claims and no material regression.

## **Phase 9 — Automated QA**

P0

Tasks:

- Run existing tests.
- Run catalogue tests.
- Run schema tests.
- Run sitemap tests.
- Run canonical tests.
- Run redirect tests.
- Run content validation.
- Run public build validation.
- Inspect complete Git diff.
- Verify private data is not exposed.
- Confirm all failures are resolved or documented.

Exit criteria: All mandatory checks pass.

## **Phase 10 — PR and release**

Tasks:

- Create implementation branch.
- Commit logical changes separately.
- Open PR.
- Attach reports.
- Document tests.
- Document known limitations.
- Request owner review.
- Obtain explicit deployment approval.
- Deploy through approved workflow.
- Validate production pages.
- Record deployed commit SHA.

Exit criteria: Reviewed implementation with reproducible validation evidence.

# **29. Acceptance Criteria**

The project must not be marked complete simply because code changes have been committed.

## **29.1 Technical acceptance**

| Requirement        | Passing condition                           |
| ------------------ | ------------------------------------------- |
| Sitemap            | Valid XML, eligible canonical URLs only     |
| Robots             | No accidental blocking of important pages   |
| Canonicals         | Correct and consistent                      |
| Redirects          | No avoidable internal redirect destinations |
| Internal links     | No broken important links                   |
| Indexability       | Correct page-level decisions                |
| Metadata           | Unique and accurate                         |
| Schema             | Valid and semantically correct              |
| Product pricing    | Matches approved source                     |
| Directory profiles | No fabricated commercial Offers             |
| Reviews            | Genuine and eligible                        |
| Mobile             | No material usability regressions           |
| Performance        | No material regression                      |
| Security           | No private information exposed              |

## **29.2 Content acceptance**

- Product pages explain actual plans and fulfilment.
- Directory profiles offer independent value.
- Category pages provide useful navigation.
- Guides satisfy informational intent.
- Commercial pages satisfy transactional intent.
- No unnecessary duplicated paragraphs.
- No keyword stuffing.
- No unsupported claims.
- No fabricated customer reviews.
- Sources and verification dates are included where appropriate.

## **29.3 Deployment acceptance**

- All existing tests pass.
- All new mandatory tests pass.
- Public staging build succeeds.
- Deployment allowlist remains correct.
- No direct production deployment occurred.
- Owner reviewed the PR.
- Explicit deployment approval obtained.
- Live verification completed.

# **30. Rollback Strategy**

SEO changes can unintentionally damage URLs, indexation and website functionality. Every phase must be reversible.

## **30.1 Before implementation**

Record:

```
git rev-parse HEAD
git status --short --branch
git log -5 --oneline
```

Create a dedicated branch:

```
git switch -c seo/technical-content-remediation
```

## **30.2 Rollback triggers**

Consider rollback if:

- Product routes start returning 404.
- Homepage search stops working.
- WhatsApp ordering breaks.
- Product prices become inconsistent.
- Sitemap contains private URLs.
- Important pages become noindex accidentally.
- Canonicals point to incorrect destinations.
- Deployment exposes private files.
- Structured data introduces incorrect commercial information.
- Mobile functionality materially regresses.

## **30.3 Rollback procedure**

1. Stop further changes.
2. Identify the exact offending commit.
3. Preserve audit logs and test results.
4. Revert only the problematic change.
5. Re-run the complete test suite.
6. Rebuild the public site.
7. Obtain owner approval.
8. Deploy the correction through the approved workflow.
9. Revalidate affected URLs.

Do not reset or overwrite unrelated work.

# **31. Final Execution Checklist**

This is the consolidated checklist Antigravity must use.

## **A. Repository discovery**

- Read `AGENTS.md`.
- Read all applicable SEO architecture documents.
- Read the existing content rules.
- Read the existing schema rules.
- Inspect product data.
- Inspect directory data.
- Inspect sitemap generation.
- Inspect robots configuration.
- Inspect redirects.
- Inspect deployment configuration.
- Inspect test architecture.
- Identify existing equivalent reports.
- Record current branch and SHA.

## **B. Technical SEO**

- Crawl all public pages.
- Identify every URL.
- Record HTTP statuses.
- Record redirect chains.
- Record canonical tags.
- Record noindex directives.
- Record sitemap membership.
- Identify broken links.
- Identify orphan pages.
- Identify duplicate metadata.
- Identify accidental blocking.
- Identify incorrect redirects.
- Verify trailing-slash consistency.

## **C. Sitemap and robots**

- Validate sitemap XML.
- Check duplicate entries.
- Check redirecting URLs.
- Check noindex URLs.
- Check private URLs.
- Check staged URLs.
- Verify canonical consistency.
- Verify lastmod.
- Inspect robots.txt.
- Verify important assets are accessible.
- Verify sitemap declaration.

## **D. Structured data**

- Audit every JSON-LD block.
- Validate JSON.
- Validate Product schema.
- Validate Offer schema.
- Validate price.
- Validate currency.
- Validate availability.
- Validate SoftwareApplication schema.
- Validate BreadcrumbList.
- Validate Organization/WebSite.
- Validate Article.
- Validate visible FAQ content.
- Remove fabricated ratings.
- Check entity IDs.
- Check canonical consistency.

## **E. Homepage**

- Unique title.
- Unique description.
- Correct H1.
- Correct canonical.
- Search empty state initially hidden.
- Empty state correctly appears when needed.
- Commercial cards correctly classified.
- Directory cards correctly classified.
- Featured products verified.
- Internal links crawlable.
- Mobile rendering checked.

## **F. Commercial product pages**

- Verify every product.
- Verify exact plan.
- Verify approved price.
- Verify billing period.
- Verify access type.
- Verify availability.
- Verify fulfilment.
- Verify support terms.
- Verify payment information.
- Improve unique content.
- Add useful FAQs.
- Add relevant internal links.
- Validate Product/Offer schema.

## **G. Directory pages**

- Verify official website.
- Verify features.
- Verify free-plan claims.
- Verify limitations.
- Add distinct useful content.
- Correct CTA.
- Remove accidental commercial offers.
- Verify SoftwareApplication schema where appropriate.
- Verify canonical.
- Verify sitemap eligibility.

## **H. Categories, guides and blogs**

- Unique category introductions.
- Correct category hierarchy.
- Useful child links.
- Clear informational intent.
- Clear transactional intent.
- Keyword-to-URL mapping.
- Cannibalization investigation.
- Useful comparisons.
- Reliable sources.
- Relevant internal links.

## **I. Trust and performance**

- About page.
- Contact page.
- Privacy policy.
- Terms.
- Refund policy.
- Product verification.
- Payment accuracy.
- Delivery accuracy.
- Mobile usability.
- Core Web Vitals.
- Consent implementation.
- AdSense policy review.

## **J. QA and deployment**

- Full test suite.
- Catalogue tests.
- Schema tests.
- Sitemap tests.
- Canonical tests.
- Redirect tests.
- Link graph tests.
- Content validation.
- Public build validation.
- Git diff review.
- No private data exposure.
- PR opened.
- Owner approval obtained.
- Deployment approved.
- Production validation completed.
- GSC monitoring initiated.

# **32. Required Final Reports**

Antigravity must deliver a final evidence package.

| Report                  | Required information                                |
| ----------------------- | --------------------------------------------------- |
| Implementation File Map | Exact files, source of truth, dependencies          |
| Technical Baseline      | Before-change technical measurements                |
| URL Inventory           | Every inspected public URL                          |
| Redirect Register       | Original URL, final URL, source file and correction |
| Indexation Register     | Canonical, robots, sitemap and eligibility          |
| Schema Report           | Errors, corrections and validated entities          |
| Content Report          | Product/directory/category improvements             |
| Cannibalization Map     | Query, intent and preferred URL                     |
| Test Report             | Commands, results and failures                      |
| Deployment Report       | PR, commit, approval and live verification          |

### **Required before/after measurements**

| Metric                     | Before | After  |
| -------------------------- | ------ | ------ |
| Total public URLs          | Record | Record |
| Indexable URLs             | Record | Record |
| Sitemap URLs               | Record | Record |
| Sitemap errors             | Record | Record |
| Canonical errors           | Record | Record |
| Internal redirect links    | Record | Record |
| Broken internal links      | Record | Record |
| Orphan pages               | Record | Record |
| Schema errors              | Record | Record |
| Missing titles             | Record | Record |
| Duplicate titles           | Record | Record |
| Directory Offer violations | Record | Record |
| Automated test failures    | Record | Record |

Do not fill these values with estimates. If a measurement cannot be obtained, mark it `NOT MEASURED` and explain why.

# **33. Antigravity Master Execution Instructions**

The following is the operational instruction to give Antigravity alongside this blueprint.

# MASTER TASK: AI TOOL GEMS COMPLETE SEO & TECHNICAL REMEDIATION

**Website:** [https://aitoolgems.tech/](https://aitoolgems.tech/)\
**Repository:** [https://github.com/m-rehman55/ai-tool-gems](https://github.com/m-rehman55/ai-tool-gems)

You are the Senior Technical SEO Architect, Python QA Engineer, Structured Data Specialist and Repository Engineer responsible for implementing the attached SEO implementation blueprint.

## PRIMARY OBJECTIVE

Implement the verified SEO and technical improvements across the existing AI Tool Gems repository without damaging existing functionality, business logic, website design, catalogue data, ordering workflows or deployment security.

This is an implementation task, not merely an audit or recommendation exercise.

## 1. READ BEFORE WRITING

First inspect:

- AGENTS.md
- Existing SEO architecture and rules
- Product data model
- Directory data model
- Schema implementation
- Sitemap generator
- robots.txt
- Redirect configuration
- Internal link checker
- Existing audit scripts
- Existing tests
- Deployment allowlist
- Previous SEO and HERMES reports

Locate actual files. Never assume paths.

Record the exact Git branch, commit SHA and dirty working tree.

Reuse existing architecture and existing reports wherever possible.

## 2. EXECUTE THE WORK IN PHASES

Follow the blueprint's implementation phases:

1. Repository baseline and discovery.
2. Full URL and crawl inventory.
3. Redirect and internal-link remediation.
4. Indexation, canonical, sitemap and robots.
5. Structured data.
6. Homepage and product pages.
7. Directory and category pages.
8. Blog, guides and keyword cannibalization.
9. Trust and performance.
10. Automated testing.
11. PR preparation.
12. Post-deployment validation after approval.

Do not skip a phase because another phase appears easier.

## 3. VERIFY EVERY FINDING

For every issue, provide:

- Exact URL.
- Exact source file.
- Relevant code or HTML evidence.
- Root cause.
- Recommended correction.
- Actual change.
- Test proving the correction.

Do not report a correction based on an assumption.

The reported 28+ redirects must be independently reproduced.

Do not claim that 400 words is required for indexing. Improve content according to usefulness, originality and factual accuracy.

## 4. PRESERVE BUSINESS RULES

Pakistan is the primary commercial market.

International visitors should be able to discover the website and make legitimate inquiries.

Never invent:

- Prices.
- Foreign currency offers.
- Supplier details.
- Payment methods.
- Product availability.
- Customer reviews.
- Official partnerships.
- Business addresses.
- Delivery guarantees.
- Product features.

Commercial listings and free/reference directory listings must remain separate.

Directory listings must not receive an AI Tool Gems commercial Offer or cart action.

Do not expose private supplier data or credentials.

## 5. IMPLEMENTATION REQUIREMENTS

### Technical SEO

- Correct canonicals.
- Correct sitemap eligibility.
- Correct robots directives.
- Correct redirect destinations.
- Correct internal links.
- Correct HTTP handling.
- Correct indexability lifecycle.

### Schema

- Product and Offer only for genuine commercial offers.
- SoftwareApplication where suitable for reference listings.
- BreadcrumbList where appropriate.
- Organization and WebSite using verified business information.
- Article for genuine editorial pages.
- No fabricated ratings or reviews.

### Content

- Unique homepage content.
- Useful commercial product pages.
- Useful directory profiles.
- Useful category pages.
- Informational guides.
- Clear product/blog search-intent separation.

### Testing

Extend existing Python tests instead of building duplicate audit frameworks.

Test every important change.

## 6. SAFETY RESTRICTIONS

Do not:

- Push directly to main.
- Merge without approval.
- Deploy without approval.
- Change protected secrets.
- Modify live business pricing without verification.
- Publish staged content automatically.
- Change existing URLs without impact analysis.
- Remove necessary redirects.
- Disable existing site functionality.
- Change analytics or consent configuration without authorization.

Use a dedicated branch and reviewed PR.

## 7. DELIVERABLES

Produce or update the equivalent existing reports:

1. SEO_IMPLEMENTATION_FILE_MAP.md
2. SEO_REMEDIATION_BASELINE.md
3. SEO_REDIRECT_INTERNAL_LINK_REGISTER.csv
4. SEO_URL_INDEXATION_REGISTER.csv
5. SEO_SCHEMA_VALIDATION_REPORT.md
6. SEO_INTENT_CANNIBALIZATION_MAP.csv
7. SEO_CONTENT_REMEDIATION_REGISTER.csv
8. SEO_FINAL_VALIDATION_REPORT.md

Do not duplicate reports that already exist.

## 8. FINAL RESPONSE FORMAT

When finished, report:

- Exact branch and starting commit.
- Exact files changed.
- Changes implemented.
- URLs corrected.
- Number of redirects found and corrected.
- Sitemap and canonical results.
- Schema errors before and after.
- Product and directory page results.
- Keyword cannibalization findings.
- Test commands and actual results.
- Any unresolved blockers.
- PR link, if created.
- Deployment status.
- Exact deployed SHA, only if deployment was approved and completed.

Distinguish clearly between:\
PASS, FAIL, BLOCKED, NOT TESTED and REQUIRES OWNER APPROVAL.

Do not claim Google indexing has been fixed merely because the technical implementation passes.

**Start with repository discovery and evidence collection. Proceed phase by phase, preserve existing work, and stop at the approval gates.**

# **Final Engineering Recommendation**

The most important implementation order is:

1. **Fix technical indexation blockers and URL inconsistencies first.**
2. **Correct product and directory schema before adding more content.**
3. **Fix internal redirect links and sitemap eligibility.**
4. **Improve the commercial product pages using verified data.**
5. **Improve directory profiles with genuinely useful information.**
6. **Resolve product/blog intent overlap using GSC query evidence.**
7. **Improve trust, performance and international discoverability.**
8. **Validate everything through automated tests and a reviewed PR.**

For AI Tool Gems, the objective should not simply be to increase the number of indexed pages. It should be to increase the number of **valuable, technically correct, independently useful and commercially relevant pages** that search engines can confidently understand.

The implementation must protect the existing HERMES architecture, catalogue integrity, Pakistan pricing rules, public/private page lifecycle and production deployment safeguards.