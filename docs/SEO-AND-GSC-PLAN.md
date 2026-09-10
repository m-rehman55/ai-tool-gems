# AI Tool Gems SEO, GEO, and Google Search Console plan

Last updated: 11 September 2026

## Current implementation

- The homepage targets premium AI tools and digital subscriptions in Pakistan.
- All 20 catalog products have crawlable HTML pages under `/tools/`.
- Each product page has a unique title, description, canonical URL, visible PKR offer details, a WhatsApp conversion link, Product/Offer schema, and BreadcrumbList schema.
- The homepage exposes crawlable product links and ItemList schema.
- About, contact, and consolidated order/policy pages provide trust and merchant information without inventing a physical address or third-party affiliation.
- `sitemap.xml` lists every canonical public page and `robots.txt` permits Google plus named AI-search crawlers while excluding the admin page.
- `llms.txt` identifies the marketplace, policies, contact route, and every product URL.
- Privacy-safe commerce events are pushed to `window.dataLayer` for a future GA4 or GTM installation. No personal data or WhatsApp message text is included.

## Google Search Console ownership

AI Tool Gems should use a **Domain property** so Search Console covers HTTPS, HTTP, `www`, and any future subdomains.

1. Sign in to Google Search Console and choose **Add property**.
2. Select **Domain** and enter `aitoolgems.tech`.
3. Copy Google's unique value beginning with `google-site-verification=`.
4. In the Name.com DNS panel for `aitoolgems.tech`, add a TXT record:
   - Host: `@` (or leave blank if Name.com instructs)
   - Value: the exact Google verification value
   - TTL: Automatic or 300 seconds
5. Keep the TXT record permanently, return to Search Console, and select **Verify**.
6. Open **Sitemaps** and submit `https://aitoolgems.tech/sitemap.xml`.
7. Inspect the homepage and priority product pages such as `/tools/chatgpt/`, `/tools/gemini/`, and `/tools/canva/`. Confirm successful live fetch and matching user/Google canonicals.
8. Request indexing for the homepage and a few priority pages. Let the sitemap handle bulk discovery.

The Google-side ownership and sitemap submission cannot be automated until the owner supplies the generated DNS TXT token or connects OAuth/service-account credentials with Search Console access.

## Next 90 days

### Days 1–30

- Complete Domain-property verification and sitemap submission.
- Connect a GA4/GTM property and map existing `view_item`, `add_to_cart`, `remove_from_cart`, `begin_checkout`, `whatsapp_checkout`, and `finder_start` data-layer events.
- Validate Product and Breadcrumb markup through Google Rich Results Test.
- Confirm every indexed plan description against current vendor terms, especially shared, invitation, educational, long-duration, and license-key listings.

### Days 31–60

- Build substantial category hubs for AI assistants, AI video, design, development, productivity, VPN/security, and entertainment.
- Publish a PKR price-comparison page and original guides for Pakistani students, freelancers, creators, and agencies.
- Create genuine business profiles on suitable platforms and add `sameAs` only after URLs are verified.

### Days 61–90

- Publish evidence-led comparisons such as ChatGPT vs Gemini and Canva vs Adobe.
- Review GSC query/page data weekly, improve pages in positions 4–20, and rewrite low-CTR titles only where impressions justify it.
- Refresh price, availability, terms, and `lastmod` values together.

## Measurement targets

- 24 canonical URLs submitted at launch.
- All product schema pages valid without fabricated ratings or reviews.
- Organic WhatsApp lead rate measured after GA4/GTM connection.
- GSC baseline established after 28 days; future targets should be based on observed Pakistan query data rather than guessed keyword volumes.

## Guardrails

- Do not publish “official,” “authorized,” “highest-rated,” “verified,” or “genuine” claims without retained evidence.
- Do not add AggregateRating until reviews and counts are real, visible, and traceable.
- Do not create a Google Business Profile or LocalBusiness address unless the business is genuinely eligible and the address/service-area facts can be verified.
- Do not invent social profiles, operator credentials, customer testimonials, or a street address.
