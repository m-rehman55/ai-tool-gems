# FOOTER_REMEDIATION_PLAN.md


## Complete Professional Footer Audit, Redesign Blueprint & Production Implementation Plan


Project: AI Tool Gems Pakistan · aitoolgems.tech · Audit date: 16 November 2026


Production architecture blueprint SEO + UX + E-commerce trust


# 1. Executive Summary


The current footer has a significant architectural inconsistency: the homepage has a comprehensive five-column footer, while the directory and individual product pages use a minimal two-line copyright strip.


This creates three problems:

- 

Brand inconsistency: Visitors navigating from the homepage to individual tools encounter a completely different website experience.


- 

Lost conversion opportunities: Product pages do not provide consistent access to customer support, payment information, warranty terms, policies, and related subscriptions.


- 

Underutilized internal navigation: The footer does not provide a consistent site-wide navigation system connecting the marketplace, product catalogue, category pages, guides, and trust documentation.



The recommended solution is a reusable, consistent footer architecture deployed across the entire public website.


The redesign should not simply make the footer bigger. It should make the footer a functional component of the marketplace's:

- 

Conversion funnel.


- 

Customer support system.


- 

Internal linking architecture.


- 

Brand credibility and transparency.


- 

International customer navigation.


- 

Mobile user experience.



Important implementation principle: Every payment method, warranty, security certification, delivery promise, and merchant-verification statement must reflect an actual operational capability. A visual badge must never imply a certification, payment integration, or guarantee that the business cannot substantiate.


For example, a WhatsApp delivery target of 15–30 minutes should only be advertised after operational verification. Likewise, crypto, Binance Pay, and international card acceptance must not appear as active payment methods until they are genuinely supported.


## 2. Live-site findings and evidence-based corrections


I compared the supplied footer structure against the currently indexed public website.


There are several important differences that should influence implementation.


| Area | Finding | Required action |
| --- | --- | --- |
| Homepage trust signals | Already displays local payment rails and replacement warranty information | Reuse the existing verified terminology |
| Domestic payments | EasyPaisa, JazzCash, SadaPay, NayaPay, Raast and local bank IBFT are presented as supported | Display these as domestic payment methods |
| International payments | Wise and SWIFT bank wire are inquiry-only | Label them clearly as inquiry-based |
| International cards | Automated card billing is explicitly unsupported | Do not display cards as accepted |
| Crypto / Binance Pay | No verified active payment integration established | Do not display as accepted payment methods |
| Delivery | Fulfilment is manually verified through WhatsApp | Avoid promising universal 15–30-minute delivery |
| Warranty | Individual products have different replacement periods | Link to actual product-specific warranty terms |
| Security | No verified independent 256-bit security certification established | Use factual HTTPS/security wording, not certification badges |
| Merchant verification | No independent merchant accreditation established | Do not use an unearned Verified Merchant badge |



The current homepage already describes domestic payment support and international inquiry arrangements. It also explains that automated international gateways are not active. AI Tool Gems+1


The live pricing guide further explains that delivery, access type, duration and warranty vary between products. PKR Guide+1


Critical correction: do not introduce inaccurate trust badges.


Domestic payment methods
Supported

EasyPaisa · JazzCash · SadaPay · NayaPay · Raast · Bank IBFT


Wise / SWIFT
Inquiry only

International arrangements confirmed individually.


Crypto / Binance Pay
Unverified

No active acceptance claim.


International card payments
Unsupported

No automated card checkout.


15–30-minute delivery
Not guaranteed

Delivery time depends on verification and provisioning.


This distinction is particularly important because the footer is a site-wide trust component. Any incorrect claim would be repeated across dozens of URLs.


# 3. Root-Cause Analysis & Flaws


## 3.1 Structural inconsistency


The supplied HTML shows two separate footer implementations.


Homepage:

- 

Brand identity.


- 

Five navigation columns.


- 

Company information.


- 

Trust and policy links.


- 

Social media.


- 

Guides and articles.


- 

Copyright and disclaimer.



Product and directory pages:

- 

Copyright.


- 

Independent marketplace disclaimer.



This is not merely a visual design problem.


It is a component architecture problem.


The product detail page is often the most commercially important page in the customer journey. Someone arriving from Google directly on a ChatGPT Plus, Canva Pro or Cursor AI listing should have access to the same navigation and support resources as someone arriving on the homepage.


The current implementation creates unnecessary navigation dead ends.


Recommended correction: Establish one canonical footer component with controlled variations only where genuinely necessary.


## 3.2 Missing payment transparency


Customers should be able to understand the available payment methods without navigating back to the homepage.


Recommended presentation:


| Payment method | Footer treatment |
| --- | --- |
| EasyPaisa | Domestic payment badge |
| JazzCash | Domestic payment badge |
| SadaPay | Domestic payment badge |
| NayaPay | Domestic payment badge |
| Raast | Domestic payment badge |
| Bank IBFT | Domestic payment badge |
| Wise | International inquiry |
| SWIFT | International inquiry |
| USDT | Do not display until operationally verified |
| Binance Pay | Do not display until operationally verified |
| International cards | Explicitly unsupported |



A footer should distinguish between an active payment rail and a payment arrangement that must be discussed with support.


Recommended heading:


Payment methods


Subheading:


Secure, manually verified payment arrangements for Pakistani and international customers.


Do not use payment provider logos without checking brand usage permissions and ensuring that the provider is genuinely supported.


## 3.3 Missing warranty and fulfilment information


A professional digital marketplace should make the following information easy to find:

- 

What happens after ordering?


- 

When is payment confirmed?


- 

How is digital access delivered?


- 

What happens if an account stops working?


- 

How long does replacement coverage last?


- 

What happens if an order cannot be fulfilled?



The homepage already communicates a 7–30-day replacement warranty range and manual WhatsApp verification. These are more defensible than a universal replacement guarantee. AI Tool Gems+1


Recommended trust statements:


| Proposed statement | Recommendation |
| --- | --- |
| Product-specific replacement warranty | Display |
| WhatsApp order verification | Display |
| Delivery after payment confirmation | Display |
| Delivery within 15–30 minutes | Only if guaranteed operationally |
| 100% replacement warranty | Avoid as a blanket promise |
| Verified merchant | Only with independent accreditation |
| 256-bit SSL secured | Avoid unless the exact technical claim is verified |



A good alternative to the requested 256-bit badge is:


HTTPS connection protected


This describes the actual browser connection without suggesting that the marketplace has obtained a separate security certification.


## 3.4 Broken fragment navigation


The supplied homepage contains:
HTML

```
<a href="#finder" data-open-finder>Find my tool</a>
<a href="#how">How it works</a>
```



These links work only when the corresponding IDs exist on the current page.


On a product page:
Plain text/tools/chatgpt-plus/index.html

the first link resolves to:
Plain text/tools/chatgpt-plus/index.html#finder

It does not automatically navigate to the homepage.


Correct root-page version:
HTML

```
<a href="/#finder">Find my tool</a>
<a href="/#how">How it works</a>
```



Correct two-level version:
HTML

```
<a href="../../#finder">Find my tool</a>
<a href="../../#how">How it works</a>
```



However, if the finder depends on JavaScript, its functionality must be verified on the destination page. Navigation to a fragment alone does not guarantee that a modal or application component opens.


## 3.5 Missing product discovery links


A directory footer should help visitors move between commercially relevant products.


Recommended popular product links:

- 

ChatGPT Plus


- 

Claude Pro


- 

Gemini Pro


- 

Canva Pro


- 

CapCut Pro


- 

Midjourney


- 

Cursor AI


- 

GitHub Copilot


- 

ElevenLabs


- 

NordVPN



These should be selected using actual catalogue availability and sales data.


Do not create footer links to products that have been discontinued, are only directory references, or do not have an active purchasable listing.


Also avoid putting all 65 products in the footer. That would create an unnecessarily large navigation block.


A curated group of approximately 8–10 products is sufficient.


## 3.6 Excessive homepage navigation


The supplied homepage footer includes a very large Guides & Blog column.


It is useful for discovery, but it creates several problems:

- 

Uneven column height.


- 

Excessive mobile scrolling.


- 

Repeated navigation destinations.


- 

Reduced visibility of customer support.


- 

Poor visual hierarchy.



Recommended solution:

- 

Keep 5–7 high-value guide links.


- 

Add one link to the complete guides directory.


- 

Add one link to the blog.


- 

Use product and category links to distribute internal navigation.



## 3.7 UX and accessibility problems


The redesigned footer should address:

- 

Inconsistent spacing between columns.


- 

Small text and insufficient contrast.


- 

Long horizontal link lists on mobile.


- 

Unclear payment status.


- 

Missing hover and keyboard focus indicators.


- 

Insufficient touch-target dimensions.


- 

Excessive animation.


- 

Poor handling of long URLs and international contact text.


- 

Lack of semantic navigation labels.


- 

Duplicate or confusing social links.



Use semantic HTML5 elements, descriptive accessible names and visible focus states.


## 3.8 SEO and internal-linking problems


The footer is part of the website's internal navigation architecture.


However, footer links should be helpful rather than artificially repeated for keyword manipulation.


Avoid:

- 

Repeating identical keyword-rich anchors excessively.


- 

Linking every product to every page.


- 

Adding hundreds of low-value links.


- 

Creating category pages just to increase footer links.


- 

Linking noindex or private pages.


- 

Adding irrelevant international country pages.



The footer should prioritize meaningful destinations:

- 

Marketplace directory.


- 

Commercial product listings.


- 

Major categories.


- 

Pricing directory.


- 

Editorial resources.


- 

Trust and policy pages.


- 

Customer support.



All public footer links should be crawlable standard HTML anchors.


# 4. Ideal Professional Footer Blueprint


## 4.1 Recommended architecture


AI TOOL GEMS
Independent marketplace

Discover. Compare. Upgrade your AI advantage.


Product information, access terms and replacement coverage explained clearly.


PAYMENT METHODS


Pakistan · Supported local payment rails
EasyPaisaJazzCashSadaPayNayaPayRaastBank IBFT

International · Inquiry only
Wise inquirySWIFT inquiry

Marketplace


Directory · Categories · Prices · Deals


Popular tools


ChatGPT · Claude · Canva · Cursor


Trust & policies


Review · Pricing · Warranty · Refund


Customer concierge


WhatsApp · Social · Support hours


Customer support


WhatsApp assistance · Published operating hours


© 2026 AI Tool Gems Pakistan · Privacy · Terms · Sitemap · Disclaimer
Conceptual layout — the production implementation below supplies the actual HTML and CSS.

## 4.2 Section specifications


### Section A: Brand and verification


Column 1:

- 

Logo.


- 

Brand name.


- 

Short marketplace mission.


- 

Independent marketplace statement.


- 

How verification works.


- 

Product-specific replacement warranty explanation.


- 

Link to verification policy.



Recommended copy:


AI Tool Gems helps customers discover and compare digital subscriptions and AI tools. We provide transparent product information, manually verified order arrangements, and clearly documented replacement terms.


Do not imply that every third-party subscription is directly supplied or officially endorsed by its original vendor.


### Section B: Marketplace


Column 2:

- 

All tools.


- 

Price directory.


- 

AI assistants.


- 

AI coding.


- 

AI video and audio.


- 

AI design.


- 

Writing and SEO.


- 

VPN and security.



### Section C: Popular subscriptions


Column 3:

- 

ChatGPT Plus.


- 

Claude Pro.


- 

Gemini Pro.


- 

Canva Pro.


- 

CapCut Pro.


- 

Midjourney.


- 

Cursor AI.


- 

GitHub Copilot.


- 

ElevenLabs.


- 

NordVPN.



Only retain links that correspond to real, active product URLs.


### Section D: Trust and E-E-A-T


Column 4:

- 

About us.


- 

How we review.


- 

How we price.


- 

How we source.


- 

Product verification.


- 

Correction policy.


- 

Replacement warranty.


- 

Refund policy.


- 

Terms of service.



### Section E: Customer concierge


Column 5:

- 

WhatsApp support.


- 

WhatsApp channel.


- 

Instagram.


- 

TikTok.


- 

Facebook.


- 

Telegram.


- 

Published support hours.


- 

International inquiry information.



### Section F: Bottom bar


Include:

- 

Copyright.


- 

Privacy policy.


- 

Terms of service.


- 

Disclaimer.


- 

Sitemap.


- 

Independent marketplace disclosure.



# 5. Production-Ready HTML Templates


## 5.1 Implementation architecture


For a static HTML website, the preferred architecture is:
Plain text/
├── index.html
├── styles.css
├── tool-page.css
├── assets/
│   └── brand-logo-light.webp
├── tools/
│   ├── index.html
│   └── product-slug/
│       └── index.html
├── category/
│   └── category-slug/
│       └── index.html
├── guides/
│   ├── index.html
│   └── guide-slug/
│       └── index.html
├── prices/
├── deals/
├── blog/
├── privacy-policy/
└── terms-of-service/

The exact directory tree must be checked against the repository before deployment. This is an architectural illustration, not a claim that every example directory exists.


### Critical decision: root-relative versus relative paths


For a website deployed at its domain root, such as https://aitoolgems.tech/, root-relative paths are preferable:
HTML

```
<a href="/tools/">All AI tools</a>
<a href="/prices/">Prices</a>
<a href="/privacy-policy/">Privacy policy</a>
```



They work from both root pages and deeply nested pages on the production domain.


However, if the website is deployed under a GitHub Pages project subpath, such as:
Plain texthttps://username.github.io/repository/

root-relative paths point to the domain root rather than the repository subpath.


For your custom domain deployment, root-relative paths are the cleanest production option. If local file:// navigation and project-subpath GitHub Pages compatibility are strict requirements, use the two-template strategy below.


Important: A relative path beginning with ../../ is relative to the current document URL, not to the repository root. The correct number of directory levels must be verified for each page.


## 5.2 Template A — Root-level pages


Use this template for:

- 

index.html


- 

tools/index.html


- 

guides/index.html


- 

Root-level company pages.


- 

Root-level policy pages.



The following template uses the verified brand and social/contact destinations supplied in your existing footer. Product links are intentionally routed through the catalogue until individual product URL slugs have been confirmed against the repository.
HTML

```

<footer class="site-footer" id="site-footer">
  <div class="footer-shell">

    <!-- PAYMENT AND TRUST STRIP -->
    <section class="footer-payment"
      aria-labelledby="footer-payment-title">

      <div class="footer-payment-intro">
        <h2 id="footer-payment-title">
          Payment methods
        </h2>
        <p>
          Supported local payments and international
          arrangements confirmed through WhatsApp.
        </p>
      </div>

      <div class="footer-payment-groups">

        <div class="footer-payment-group">
          <h3>Pakistan · Supported</h3>

          <ul class="payment-badges">
            <li>EasyPaisa</li>
            <li>JazzCash</li>
            <li>SadaPay</li>
            <li>NayaPay</li>
            <li>Raast</li>
            <li>Bank IBFT</li>
          </ul>
        </div>

        <div class="footer-payment-group">
          <h3>International · Inquiry only</h3>

          <ul class="payment-badges payment-inquiry">
            <li>Wise</li>
            <li>SWIFT Bank Wire</li>
          </ul>
        </div>

      </div>

      <a class="footer-payment-policy"
        href="/contact.html">
        Confirm payment options
      </a>

    </section>

    <!-- MAIN FOOTER GRID -->
    <div class="footer-grid">

      <!-- COLUMN 1: BRAND -->
      <section class="footer-brand"
        aria-labelledby="footer-brand-title">

        <a class="footer-brand-link" href="/">
          <img
            src="/assets/brand-logo-light.webp"
            width="64"
            height="64"
            loading="lazy"
            decoding="async"
            alt="AI Tool Gems logo">

          <span id="footer-brand-title">
            AI TOOL <strong>GEMS</strong>
            <small>PAKISTAN &amp; WORLDWIDE</small>
          </span>
        </a>

        <p>
          Discover, compare and access digital
          subscriptions and AI tools through a
          transparent assisted marketplace.
        </p>

        <div class="footer-verification">
          <span>✓ Independent marketplace</span>
          <span>✓ Manual order verification</span>
          <span>✓ Product-specific warranty terms</span>
        </div>

        <a href="/product-verification.html"
          class="footer-text-link">
          Our verification process →
        </a>

      </section>

      <!-- COLUMN 2: MARKETPLACE -->
      <nav class="footer-column"
        aria-label="Marketplace navigation">

        <h2>Marketplace</h2>

        <a href="/tools/">All AI tools</a>
        <a href="/prices/">AI tools prices</a>
        <a href="/deals/">Current deals</a>

        <a href="/category/ai-chatbots/">
          AI Chatbots &amp; Assistants
        </a>

        <a href="/category/ai-coding/">
          AI Coding &amp; Development
        </a>

        <a href="/category/ai-video/">
          AI Video &amp; Animation
        </a>

        <a href="/category/ai-design/">
          AI Design &amp; Image
        </a>

        <a href="/category/ai-writing-seo/">
          Writing &amp; SEO
        </a>

        <a href="/category/vpn-security/">
          VPN &amp; Security
        </a>

      </nav>

      <!-- COLUMN 3: POPULAR TOOLS -->
      <nav class="footer-column"
        aria-label="Popular subscriptions">

        <h2>Popular subscriptions</h2>

        <a href="/tools/">
          ChatGPT Plus
        </a>

        <a href="/tools/">
          Claude Pro
        </a>

        <a href="/tools/">
          Gemini Pro
        </a>

        <a href="/tools/">
          Canva Pro
        </a>

        <a href="/tools/">
          CapCut Pro
        </a>

        <a href="/tools/">
          Midjourney
        </a>

        <a href="/tools/">
          Cursor AI
        </a>

        <a href="/tools/">
          GitHub Copilot
        </a>

        <a href="/tools/">
          ElevenLabs
        </a>

        <a href="/tools/">
          NordVPN
        </a>

      </nav>

      <!-- COLUMN 4: TRUST -->
      <nav class="footer-column"
        aria-label="Trust and company information">

        <h2>Trust &amp; policies</h2>

        <a href="/about.html">About us</a>
        <a href="/how-we-review.html">How we review</a>
        <a href="/how-we-price.html">How we price</a>
        <a href="/how-we-source.html">How we source</a>

        <a href="/product-verification.html">
          Product verification
        </a>

        <a href="/correction-policy.html">
          Correction policy
        </a>

        <a href="/policies.html#warranty">
          Replacement warranty
        </a>

        <a href="/policies.html#refunds">
          Refund policy
        </a>

        <a href="/terms-of-service/">
          Terms of service
        </a>

      </nav>

      <!-- COLUMN 5: SUPPORT -->
      <section class="footer-column footer-support"
        aria-labelledby="footer-support-title">

        <h2 id="footer-support-title">
          Customer concierge
        </h2>

        <a
          href="https://wa.me/923236715731?text=Hello%20AI%20Tool%20Gems%2C%20I%20need%20assistance"
          target="_blank"
          rel="noopener noreferrer nofollow">
          WhatsApp support
        </a>

        <a
          href="https://www.whatsapp.com/channel/0029VbDnEgCHLHQOYpDo5c31"
          target="_blank"
          rel="noopener noreferrer">
          WhatsApp channel
        </a>

        <a href="https://www.instagram.com/aitoolgemspak/"
          target="_blank" rel="me noopener noreferrer">
          Instagram
        </a>

        <a href="https://www.tiktok.com/@aitoolgems"
          target="_blank" rel="me noopener noreferrer">
          TikTok
        </a>

        <a href="https://www.facebook.com/people/AI-Tool-Gems-Pakistan/61594432675562/"
          target="_blank" rel="me noopener noreferrer">
          Facebook
        </a>

        <a href="https://t.me/aitoolgemspak"
          target="_blank" rel="me noopener noreferrer">
          Telegram
        </a>

        <div class="footer-hours">
          <strong>Support hours</strong>
          <span>Confirm current availability on WhatsApp.</span>
          <span>Pakistan Standard Time (PKT).</span>
        </div>

      </section>

    </div>

    <!-- FOOTER BOTTOM -->
    <div class="footer-bottom">

      <div class="footer-legal">
        <a href="/privacy-policy/">
          Privacy
        </a>

        <a href="/terms-of-service/">
          Terms
        </a>

        <a href="/sitemap.xml">
          Sitemap
        </a>

        <a href="/contact.html">
          Contact
        </a>
      </div>

      <p>
        © 2026 AI Tool Gems Pakistan.
        All rights reserved.
      </p>

      <p class="footer-disclaimer">
        Independent digital marketplace.
        Third-party trademarks belong to their
        respective owners. No affiliation or
        endorsement is implied.
      </p>

    </div>

  </div>
</footer>

```



Important implementation notes:

- 

The popular product links above are provisional navigation placeholders, not verified individual product destinations. Replace them with their actual product URLs before production.


- 

The category links must be reconciled with the actual category directory. In particular, do not assume ai-writing-seo exists just because the label is useful.


- 

contact.html, product-verification.html, and the other root-level paths should be checked against the current repository before release.


- 

The footer deliberately does not advertise USDT, Binance Pay, international cards, or 256-bit certification.



## 5.3 Template B — Two-level deep subpages


Use this template for:
Plain text/tools/product-slug/index.html
/guides/guide-slug/index.html
/category/category-slug/index.html

For the directory structure above, the document is two directory levels beneath the root.


The relative path to the website root is therefore:
Plain text../../

Rather than duplicating an entirely different footer, keep the same semantic HTML and replace only the navigation path prefix.
HTML

```

<footer class="site-footer" id="site-footer">
  <div class="footer-shell">

    <!-- PAYMENT STRIP -->
    <section class="footer-payment"
      aria-labelledby="footer-payment-title">

      <div class="footer-payment-intro">
        <h2 id="footer-payment-title">
          Payment methods
        </h2>

        <p>
          Supported Pakistan payment methods and
          international inquiry arrangements.
        </p>
      </div>

      <div class="footer-payment-groups">

        <div class="footer-payment-group">
          <h3>Pakistan · Supported</h3>

          <ul class="payment-badges">
            <li>EasyPaisa</li>
            <li>JazzCash</li>
            <li>SadaPay</li>
            <li>NayaPay</li>
            <li>Raast</li>
            <li>Bank IBFT</li>
          </ul>
        </div>

        <div class="footer-payment-group">
          <h3>International · Inquiry only</h3>

          <ul class="payment-badges payment-inquiry">
            <li>Wise</li>
            <li>SWIFT Bank Wire</li>
          </ul>
        </div>

      </div>

      <a class="footer-payment-policy"
        href="../../contact.html">
        Confirm payment options
      </a>

    </section>

    <!-- FOOTER GRID -->
    <div class="footer-grid">

      <section class="footer-brand">
        <a class="footer-brand-link" href="../../">
          <img
            src="../../assets/brand-logo-light.webp"
            width="64"
            height="64"
            loading="lazy"
            decoding="async"
            alt="AI Tool Gems logo">

          <span>
            AI TOOL <strong>GEMS</strong>
            <small>PAKISTAN &amp; WORLDWIDE</small>
          </span>
        </a>

        <p>
          Discover, compare and access digital
          subscriptions and AI tools through a
          transparent assisted marketplace.
        </p>

        <div class="footer-verification">
          <span>✓ Independent marketplace</span>
          <span>✓ Manual order verification</span>
          <span>✓ Product-specific warranty terms</span>
        </div>

        <a href="../../product-verification.html">
          Our verification process →
        </a>
      </section>

      <nav class="footer-column"
        aria-label="Marketplace navigation">

        <h2>Marketplace</h2>

        <a href="../../tools/">All AI tools</a>
        <a href="../../prices/">AI tools prices</a>
        <a href="../../deals/">Current deals</a>

        <a href="../../category/ai-chatbots/">
          AI Chatbots &amp; Assistants
        </a>

        <a href="../../category/ai-coding/">
          AI Coding &amp; Development
        </a>

        <a href="../../category/ai-video/">
          AI Video &amp; Animation
        </a>

        <a href="../../category/ai-design/">
          AI Design &amp; Image
        </a>

        <a href="../../category/vpn-security/">
          VPN &amp; Security
        </a>

      </nav>

      <nav class="footer-column"
        aria-label="Popular subscriptions">

        <h2>Popular subscriptions</h2>

        <a href="../../tools/">ChatGPT Plus</a>
        <a href="../../tools/">Claude Pro</a>
        <a href="../../tools/">Gemini Pro</a>
        <a href="../../tools/">Canva Pro</a>
        <a href="../../tools/">CapCut Pro</a>
        <a href="../../tools/">Midjourney</a>
        <a href="../../tools/">Cursor AI</a>
        <a href="../../tools/">GitHub Copilot</a>
        <a href="../../tools/">ElevenLabs</a>
        <a href="../../tools/">NordVPN</a>

      </nav>

      <nav class="footer-column"
        aria-label="Trust and policies">

        <h2>Trust &amp; policies</h2>

        <a href="../../about.html">About us</a>
        <a href="../../how-we-review.html">How we review</a>
        <a href="../../how-we-price.html">How we price</a>
        <a href="../../how-we-source.html">How we source</a>

        <a href="../../product-verification.html">
          Product verification
        </a>

        <a href="../../correction-policy.html">
          Correction policy
        </a>

        <a href="../../policies.html#warranty">
          Replacement warranty
        </a>

        <a href="../../policies.html#refunds">
          Refund policy
        </a>

        <a href="../../terms-of-service/">
          Terms of service
        </a>

      </nav>

      <section class="footer-column footer-support">

        <h2>Customer concierge</h2>

        <a
          href="https://wa.me/923236715731?text=Hello%20AI%20Tool%20Gems%2C%20I%20need%20assistance"
          target="_blank"
          rel="noopener noreferrer nofollow">
          WhatsApp support
        </a>

        <a
          href="https://www.whatsapp.com/channel/0029VbDnEgCHLHQOYpDo5c31"
          target="_blank"
          rel="noopener noreferrer">
          WhatsApp channel
        </a>

        <a href="https://www.instagram.com/aitoolgemspak/"
          target="_blank" rel="me noopener noreferrer">
          Instagram
        </a>

        <a href="https://www.tiktok.com/@aitoolgems"
          target="_blank" rel="me noopener noreferrer">
          TikTok
        </a>

        <a href="https://www.facebook.com/people/AI-Tool-Gems-Pakistan/61594432675562/"
          target="_blank" rel="me noopener noreferrer">
          Facebook
        </a>

        <a href="https://t.me/aitoolgemspak"
          target="_blank" rel="me noopener noreferrer">
          Telegram
        </a>

        <div class="footer-hours">
          <strong>Support hours</strong>
          <span>Confirm current availability on WhatsApp.</span>
          <span>Pakistan Standard Time (PKT).</span>
        </div>

      </section>

    </div>

    <!-- BOTTOM BAR -->
    <div class="footer-bottom">

      <div class="footer-legal">
        <a href="../../privacy-policy/">Privacy</a>
        <a href="../../terms-of-service/">Terms</a>
        <a href="../../sitemap.xml">Sitemap</a>
        <a href="../../contact.html">Contact</a>
      </div>

      <p>
        © 2026 AI Tool Gems Pakistan.
        All rights reserved.
      </p>

      <p class="footer-disclaimer">
        Independent digital marketplace.
        Third-party trademarks belong to their
        respective owners.
      </p>

    </div>

  </div>
</footer>

```



### 5.4 Product links: mandatory repository verification


The templates intentionally use /tools/ as the destination for the popular-product labels.


This is a temporary safe fallback, not the final desired experience.


For the final release, each link should lead to the correct individual product page.


For example, the following is illustrative only:
HTML

```
<a href="/tools/chatgpt-plus/">
  ChatGPT Plus
</a>
```



Do not assume that the example slug is correct.


Your catalogue may use different slugs, such as:
Plain texttools/chatgpt/
tools/chatgpt-plus/
tools/openai-chatgpt-plus/

Only one may actually exist.


Required source of truth: the existing product registry and generated product directory, not manually guessed slugs.


The same rule applies to categories, policies and guide links.


# 6. Production CSS Blueprint


## 6.1 Design direction


AI TOOL GEMS
Pakistan & worldwide

# Discover. Compare. Upgrade.


A premium digital marketplace for AI subscriptions and software tools.


SUPPORTED LOCAL PAYMENT RAILS


EasyPaisa


JazzCash


SadaPay


NayaPay


Raast


Bank IBFT


Marketplace


Browse tools · Prices · Categories


Popular tools


ChatGPT · Claude · Canva · Cursor


Trust


Verification · Warranty · Policies


Support


WhatsApp · Social · Assistance


© 2026 AI Tool Gems Pakistan · Privacy · Terms · Sitemap


## 6.2 Design tokens


| Token | Value |
| --- | --- |
| Footer background | #0a0d14 |
| Surface | #101622 |
| Primary accent | #00e5ff |
| Secondary accent | #22c55e |
| Primary text | #f8fafc |
| Secondary text | #94a3b8 |
| Border | rgba(148,163,184,.16) |
| Hover surface | #172235 |
| Maximum content width | 1440px |
| Desktop grid | 5 columns |
| Tablet grid | 2–3 columns |
| Mobile grid | 1 column |



## 6.3 Complete CSS implementation


Add the following to styles.css and, where required, tool-page.css.


Use a single canonical copy in your shared stylesheet rather than allowing different footer implementations to drift apart.
CSS

```

/* ==========================================================
   AI TOOL GEMS — GLOBAL FOOTER SYSTEM
   Version: 1.0
   ========================================================== */

.site-footer {
  --footer-bg: #0a0d14;
  --footer-surface: #101622;
  --footer-surface-hover: #172235;
  --footer-accent: #00e5ff;
  --footer-green: #22c55e;
  --footer-text: #f8fafc;
  --footer-muted: #a1adbf;
  --footer-border: rgba(148, 163, 184, 0.17);

  position: relative;
  isolation: isolate;
  overflow: hidden;

  background: var(--footer-bg);
  color: var(--footer-text);

  border-top: 1px solid var(--footer-border);

  font-family: inherit;
}

.site-footer,
.site-footer * {
  box-sizing: border-box;
}

.footer-shell {
  width: min(100% - 40px, 1440px);
  margin-inline: auto;
  padding: 52px 0 22px;
}

/* PAYMENT STRIP */

.footer-payment {
  display: grid;
  grid-template-columns:
    minmax(180px, 0.85fr)
    minmax(0, 2fr)
    auto;

  align-items: center;
  gap: 26px;

  padding: 22px;

  background:
    linear-gradient(
      135deg,
      rgba(0, 229, 255, 0.065),
      rgba(34, 197, 94, 0.035)
    ),
    var(--footer-surface);

  border: 1px solid var(--footer-border);
  border-radius: 18px;

  margin-bottom: 48px;
}

.footer-payment-intro h2 {
  font-size: 17px;
  margin: 0 0 8px;
  color: var(--footer-text);
}

.footer-payment-intro p {
  font-size: 12px;
  line-height: 1.7;
  color: var(--footer-muted);
  margin: 0;
}

.footer-payment-groups {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.footer-payment-group h3 {
  margin: 0 0 10px;
  font-size: 11px;
  letter-spacing: .07em;
  text-transform: uppercase;
  color: var(--footer-muted);
}

.payment-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;

  list-style: none;
  margin: 0;
  padding: 0;
}

.payment-badges li {
  padding: 8px 11px;

  border: 1px solid var(--footer-border);
  border-radius: 8px;

  background: rgba(255,255,255,.035);

  font-size: 11px;
  font-weight: 650;
  color: var(--footer-text);
  white-space: nowrap;
}

.payment-inquiry li {
  border-color: rgba(234,179,8,.32);
}

.footer-payment-policy {
  color: var(--footer-accent);
  font-size: 12px;
  font-weight: 650;
  text-decoration: none;
}

/* MAIN GRID */

.footer-grid {
  display: grid;

  grid-template-columns:
    1.35fr
    1fr
    1fr
    1fr
    1.1fr;

  gap: 34px;
  align-items: start;
}

/* BRAND */

.footer-brand-link {
  display: inline-flex;
  align-items: center;
  gap: 12px;

  color: var(--footer-text);
  text-decoration: none;

  margin-bottom: 18px;
}

.footer-brand-link img {
  width: 58px;
  height: 58px;
  object-fit: contain;
}

.footer-brand-link span {
  display: grid;
  gap: 4px;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: .025em;
}

.footer-brand-link strong {
  color: var(--footer-accent);
}

.footer-brand-link small {
  font-size: 9px;
  letter-spacing: .12em;
  color: var(--footer-muted);
}

.footer-brand > p {
  max-width: 290px;
  color: var(--footer-muted);
  font-size: 13px;
  line-height: 1.85;
  margin: 0 0 18px;
}

.footer-verification {
  display: grid;
  gap: 9px;
  margin-bottom: 16px;
}

.footer-verification span {
  color: var(--footer-muted);
  font-size: 11px;
  line-height: 1.6;
}

.footer-verification span::first-letter {
  color: var(--footer-green);
}

.footer-text-link {
  display: inline-block;
  color: var(--footer-accent);
  font-size: 12px;
  font-weight: 650;
  text-decoration: none;
}

/* NAVIGATION COLUMNS */

.footer-column {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
  min-width: 0;
}

.footer-column h2 {
  color: var(--footer-text);
  font-size: 14px;
  line-height: 1.4;

  font-weight: 750;
  margin: 0 0 7px;
}

.footer-column > a {
  display: inline-block;

  color: var(--footer-muted);
  font-size: 12px;
  line-height: 1.6;

  text-decoration: none;

  transition:
    color .2s ease,
    transform .2s ease;
}

.footer-column > a:hover,
.footer-text-link:hover,
.footer-payment-policy:hover {
  color: var(--footer-accent);
  transform: translateX(3px);
}

/* SUPPORT */

.footer-hours {
  display: grid;
  gap: 7px;

  width: 100%;
  padding: 13px;

  background: var(--footer-surface);
  border: 1px solid var(--footer-border);
  border-radius: 11px;

  margin-top: 9px;
}

.footer-hours strong {
  color: var(--footer-text);
  font-size: 12px;
}

.footer-hours span {
  color: var(--footer-muted);
  font-size: 11px;
  line-height: 1.6;
}

/* BOTTOM BAR */

.footer-bottom {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 13px 25px;
  align-items: center;

  margin-top: 48px;
  padding-top: 23px;

  border-top: 1px solid var(--footer-border);
}

.footer-legal {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.footer-legal a {
  color: var(--footer-muted);
  font-size: 11px;
  text-decoration: none;
}

.footer-bottom > p {
  margin: 0;
  color: var(--footer-muted);
  font-size: 11px;
  line-height: 1.7;
}

.footer-bottom > p:first-of-type {
  text-align: right;
}

.footer-disclaimer {
  grid-column: 1 / -1;
}

/* INTERACTION AND ACCESSIBILITY */

.site-footer a:focus-visible {
  outline: 2px solid var(--footer-accent);
  outline-offset: 5px;
  border-radius: 3px;
}

.site-footer a {
  min-height: 24px;
}

.site-footer a:active {
  opacity: .8;
}

/* TABLET */

@media (max-width: 1100px) {

  .footer-payment {
    grid-template-columns: 1fr 2fr;
  }

  .footer-payment-policy {
    grid-column: 1 / -1;
  }

  .footer-grid {
    grid-template-columns:
      repeat(3, minmax(0, 1fr));

    gap: 36px 28px;
  }

  .footer-brand {
    grid-column: span 3;
  }

}

/* SMALL TABLET */

@media (max-width: 760px) {

  .footer-shell {
    width: min(100% - 32px, 600px);
    padding-top: 35px;
  }

  .footer-payment {
    grid-template-columns: 1fr;
    gap: 20px;

    padding: 17px;
    margin-bottom: 36px;
  }

  .footer-payment-groups {
    grid-template-columns: 1fr;
  }

  .footer-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 31px 20px;
  }

  .footer-brand {
    grid-column: span 2;
  }

  .footer-bottom {
    grid-template-columns: 1fr;
    gap: 16px;
    margin-top: 35px;
  }

  .footer-bottom > p:first-of-type {
    text-align: left;
  }

}

/* MOBILE */

@media (max-width: 480px) {

  .footer-shell {
    width: calc(100% - 28px);
    padding-top: 30px;
  }

  .footer-grid {
    grid-template-columns: 1fr;
    gap: 27px;
  }

  .footer-brand {
    grid-column: auto;
  }

  .footer-column {
    gap: 10px;
  }

  .footer-column h2 {
    font-size: 14px;
    margin-bottom: 4px;
  }

  .footer-column > a {
    font-size: 13px;
    min-height: 32px;
    display: flex;
    align-items: center;
  }

  .footer-legal {
    gap: 15px;
  }

  .footer-legal a {
    font-size: 12px;
    min-height: 32px;
    display: inline-flex;
    align-items: center;
  }

  .payment-badges li {
    padding: 8px 10px;
    font-size: 11px;
  }

}

/* REDUCED MOTION */

@media (prefers-reduced-motion: reduce) {

  .site-footer *,
  .site-footer *::before,
  .site-footer *::after {
    scroll-behavior: auto !important;
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
  }

}

```



## 6.4 CSS integration rules


Before adding this CSS:

- 

Search styles.css for existing footer selectors.


- 

Search tool-page.css for footer selectors.


- 

Identify conflicting declarations.


- 

Check whether the current footer inherits global a, img, section or footer styles.


- 

Consolidate rather than repeatedly appending overrides.


- 

Confirm the existing site's font family and spacing conventions.


- 

Test against the homepage and an individual product page.



Do not replace the entire existing stylesheet.


The footer should be isolated using .site-footer and .footer-* selectors to avoid affecting the rest of the website.


# 7. Customer Concierge and Trust Content


## 7.1 Support hours


The proposed support schedule is:
Plain text09:00 AM – 12:00 AM PKT

However, publish these hours only after confirming that support coverage is consistently available.


Recommended production copy:
HTML

```

<div class="footer-hours">
  <strong>WhatsApp customer support</strong>

  <span>Operating hours: 09:00 AM – 12:00 AM PKT</span>

  <span>Message us for product availability,
  payment confirmation and order assistance.</span>

  <a
    href="https://wa.me/923236715731"
    target="_blank"
    rel="noopener noreferrer nofollow">
    Chat with our team →
  </a>
</div>

```



Do not use the words "instant assistance" or "24/7 support" unless the response service actually meets those expectations.


## 7.2 Recommended trust badges


Use descriptive text rather than decorative certification graphics.


| Badge | Recommended wording | Condition |
| --- | --- | --- |
| Replacement | Product-specific replacement warranty | Supported by published policy |
| Fulfilment | Manual WhatsApp order verification | Operationally accurate |
| Delivery | Digital delivery after payment confirmation | Operationally accurate |
| Connection | HTTPS connection | Valid HTTPS |
| Merchant | Independently verified merchant | Independent verification required |



Suggested implementation:
HTML

```

<div class="footer-trust-list"
     aria-label="Marketplace service information">

  <div class="trust-item">
    <span aria-hidden="true">✓</span>
    <span>Manual order verification</span>
  </div>

  <div class="trust-item">
    <span aria-hidden="true">🛡</span>
    <span>Product-specific replacement terms</span>
  </div>

  <div class="trust-item">
    <span aria-hidden="true">⚡</span>
    <span>Digital delivery after confirmation</span>
  </div>

  <div class="trust-item">
    <span aria-hidden="true">🔒</span>
    <span>HTTPS connection</span>
  </div>

</div>

```



## 7.3 Payment bar design rules


Payment badges should have three visual characteristics:

- 

High contrast.


- 

Clear status differentiation.


- 

Consistent sizing.



Use green or cyan accents for supported domestic methods.


Use neutral or amber accents for inquiry-only international arrangements.


Never make an unsupported payment method look available simply because it has a recognizable logo.


# 8. SEO Architecture and Internal Linking Strategy


## 8.1 Footer link hierarchy


The recommended hierarchy is:


Level 1 — Main marketplace


Tools · Prices · Deals


Level 2 — Product categories


Assistants · Coding · Design · Video · SEO · VPN


Level 3 — Individual product pages


Actual catalogue product destinations


Supporting resources


Guides · Blog · Verification · Pricing · Policies


## 8.2 Recommended link distribution


| Footer section | Target links |
| --- | --- |
| Brand and verification | 1–2 |
| Marketplace | 7–9 |
| Popular products | 8–10 |
| Trust and policies | 7–9 |
| Customer concierge | 5–7 |
| Legal bottom bar | 3–5 |



The objective is not to maximize the number of links.


The objective is to make important pages accessible from every commercial entry point.


## 8.3 Anchor text standards


Use natural descriptive anchors:


Good:
HTML

```
<a href="/tools/">Browse all AI tools</a>
<a href="/prices/">Compare AI subscription prices</a>
<a href="/how-we-review.html">How we review products</a>
```



Avoid:
HTML

```
<a href="/tools/">
  Best Cheap AI Tools Pakistan Lowest Price
</a>
```



The second example is unnecessarily optimized and looks unnatural.


## 8.4 Important technical SEO rules

- 

Use standard <a href> elements.


- 

Do not use JavaScript-only footer navigation.


- 

Do not use nofollow on ordinary internal links.


- 

Do not link to private or staged noindex pages.


- 

Do not link to redirected or obsolete product URLs.


- 

Use canonical destination URLs.


- 

Avoid duplicate footer navigation IDs.


- 

Ensure the footer is present in the rendered HTML, not injected only after user interaction.


- 

Keep footer links consistent across all indexable page types.



A footer redesign does not guarantee improved rankings. Its value is improved navigation, crawlable discovery, usability and consistency.


## 8.5 Structured data considerations


Do not add fake organization verification or payment claims through schema markup.


The footer itself does not need a new schema type.


If your website already has appropriate Organization, WebSite or BreadcrumbList schema, preserve it.


Avoid duplicating Organization markup simply because the footer has been redesigned.


# 9. Phased Step-by-Step Implementation Roadmap
Recommended execution order

The migration should be conducted incrementally, with an evidence checkpoint after each phase.


## Phase 0 — Repository and URL inventory
Mandatory prerequisite

Before editing, inspect:
Plain textindex.html
styles.css
tool-page.css
tools/index.html
tools/*/index.html
guides/
category/

Also inspect:

- 

Existing navigation conventions.


- 

Existing footer CSS.


- 

Logo asset locations.


- 

Product URL registry.


- 

Existing category URL registry.


- 

Sitemap.


- 

Internal-link graph.


- 

Staged and noindex page classifications.



Produce:
Plain textFOOTER_AUDIT_INVENTORY.md

It should record:


| Metric | Required output |
| --- | --- |
| Total HTML pages | Actual count |
| Product detail pages | Actual count |
| Category pages | Actual count |
| Guide pages | Actual count |
| Existing footer variations | Actual count |
| Missing footer pages | Actual count |
| Invalid footer links | Actual count |
| Staged/noindex destinations | Actual count |
| Missing CSS imports | Actual count |



Important: Your request describes 65 product detail pages, but the current public homepage search snapshot describes a 40+ commercial marketplace. The catalogue and directory inventory must determine the actual number of pages before the batch migration. AI Tool Gems+1


Do not assume that 65 means 65 purchasable products.


## Phase 1 — CSS integration


Files:
Plain textstyles.css
tool-page.css

Tasks:

- 

Create the canonical footer CSS.


- 

Resolve existing footer styles.


- 

Integrate the new CSS.


- 

Ensure product pages load the correct stylesheet.


- 

Ensure the homepage does not receive duplicate CSS.


- 

Validate responsive breakpoints.


- 

Check global selector conflicts.


- 

Check reduced-motion behavior.


- 

Validate focus visibility.


- 

Verify the existing website layout remains unaffected.



Acceptance criteria:

- 

No horizontal overflow.


- 

No broken page layout.


- 

No duplicate footer CSS systems.


- 

No unexpected global style changes.


- 

Footer is readable at 320px width.



## Phase 2 — Homepage update


File:
Plain textindex.html

Tasks:

- 

Preserve the existing logo and brand identity.


- 

Replace the existing footer with the canonical structure.


- 

Add the payment transparency bar.


- 

Add marketplace navigation.


- 

Add popular subscription links.


- 

Add trust and verification links.


- 

Add customer concierge.


- 

Add legal bottom bar.


- 

Remove or correct broken fragment navigation.


- 

Verify all existing homepage interactions still work.



Do not modify the homepage's 3D catalogue, finder, cart, or other JavaScript features during this footer-only phase.


Acceptance criteria:

- 

Existing homepage functionality remains intact.


- 

Footer links resolve correctly.


- 

Payment information matches actual supported methods.


- 

No unsupported trust claims.



## Phase 3 — Master directory


File:
Plain texttools/index.html

Tasks:

- 

Replace the two-line copyright footer.


- 

Integrate the canonical footer.


- 

Verify the logo path.


- 

Verify all relative paths.


- 

Ensure category and product navigation is correct.


- 

Check directory-specific styles.


- 

Test mobile rendering.



Acceptance criteria:

- 

Footer visually matches homepage.


- 

No broken relative links.


- 

No directory layout regression.


- 

No accidental catalogue functionality changes.



## Phase 4 — Batch migration of product detail pages


Target:
Plain texttools/*/index.html

Do not manually edit 65 files independently.


Use a controlled migration script or shared HTML partial-generation process.


Recommended migration procedure:

- 

Enumerate the real product directories.


- 

Read each existing product HTML file.


- 

Identify the existing footer boundaries.


- 

Verify the correct insertion point.


- 

Determine the relative root prefix.


- 

Replace only the footer.


- 

Preserve existing product-specific scripts.


- 

Preserve schema and metadata.


- 

Preserve canonical URLs.


- 

Preserve product-specific pricing and warranty information.


- 

Validate each modified file.


- 

Compare before-and-after HTML outside the footer.



Never use a broad regular expression that deletes everything between the first opening and closing footer tags without inspecting the document structure.


If the existing pages contain nested footer-like elements, that approach could corrupt the HTML.


Recommended migration output:
Plain textFOOTER_MIGRATION_REPORT.md

Suggested contents:
Plain textTotal pages discovered:       N
Successfully migrated:       N
Skipped:                       0
Failed:                        0
Missing stylesheet:            0
Missing logo:                  0
Broken internal links:         0
Changed non-footer sections:   0

Use the actual results rather than pre-populating expected success counts.


## Phase 5 — Guides, categories and secondary pages


Target directories:
Plain textguides/
category/
prices/
deals/
blog/

Also inspect:
Plain textabout.html
contact.html
how-we-review.html
how-we-price.html
how-we-source.html
product-verification.html
correction-policy.html
policies.html

Tasks:

- 

Apply the appropriate footer path strategy.


- 

Check pages with trailing slashes.


- 

Check index.html pages.


- 

Check root-level HTML pages separately.


- 

Check pages with nested directories deeper than two levels.


- 

Ensure private and staged pages do not accidentally become crawlable through the footer.



A page under:
Plain textguides/subdirectory/topic/index.html

would require a different relative prefix from a page under:
Plain textguides/topic/index.html

Do not apply ../../ indiscriminately.


## Phase 6 — Automated verification
Release gate

Verification must cover five separate areas.


### A. Link graph integrity


Check every footer internal link.


Required checks:

- 

HTTP 200 or valid expected redirect.


- 

Correct trailing slash.


- 

Correct anchor destination.


- 

Correct path depth.


- 

No accidental external-domain links.


- 

No broken product links.


- 

No staged or private destination links.


- 

No malformed WhatsApp URLs.



Expected result:
Plain textFooter internal broken links: 0
Footer external broken links: 0
Invalid fragment targets: 0

### B. HTML validation


Check:

- 

Valid semantic structure.


- 

Proper heading hierarchy.


- 

Correct nesting.


- 

Unique IDs.


- 

Descriptive image alt text.


- 

Valid external-link attributes.


- 

No duplicate footers.



### C. Accessibility


Test:

- 

Keyboard navigation.


- 

Focus visibility.


- 

Screen reader navigation labels.


- 

Contrast ratios.


- 

Touch targets.


- 

Reduced-motion behavior.


- 

Text zoom at 200%.



### D. Visual regression


Test:


| Viewport | Required |
| --- | --- |
| 320 × 640 | Yes |
| 375 × 812 | Yes |
| 390 × 844 | Yes |
| 768 × 1024 | Yes |
| 1024 × 768 | Yes |
| 1366 × 768 | Yes |
| 1440 × 900 | Yes |
| 1920 × 1080 | Yes |



Test at least:

- 

Homepage.


- 

Master directory.


- 

One AI assistant product page.


- 

One AI design product page.


- 

One AI coding product page.


- 

One guide.


- 

One category.


- 

One policy page.



### E. Performance regression


The footer must not damage the existing performance baseline.


Check:

- 

LCP.


- 

CLS.


- 

INP.


- 

Total transferred bytes.


- 

Additional CSS bytes.


- 

Image loading behavior.


- 

Font loading.


- 

Main-thread JavaScript.


- 

Third-party requests.



Avoid adding:

- 

External icon libraries.


- 

Payment logo scripts.


- 

Animation libraries.


- 

New JavaScript frameworks.


- 

Unnecessary web fonts.


- 

Heavy SVG animation systems.



The footer can be implemented entirely with HTML and CSS.


# 10. Automated Footer Verification Script


This is an important part of the implementation. A visually attractive footer with broken links is not production-ready.


The following Python script is designed as a read-only verification utility. It checks local HTML files without modifying the website.


It checks:

- 

All HTML files.


- 

Internal footer links.


- 

Relative paths.


- 

Root-relative paths.


- 

Fragment targets.


- 

Missing local assets.


- 

Missing destinations.


- 

External links for reporting.


- 

Footer coverage.

Pythonfrom pathlib import Pathfrom html.parser import HTMLParserfrom urllib.parse import urlparse, unquoteimport jsonimport reROOT = Path(".").resolve()EXCLUDED_DIRS = {    ".git",    "node_modules",    ".venv",    "__pycache__",    "dist",    "build"}REPORT = {    "html_files": 0,    "footer_pages": 0,    "missing_footer": [],    "broken_internal_links": [],    "broken_assets": [],    "missing_fragments": [],    "external_links": [],    "footer_links_checked": 0}class FooterParser(HTMLParser):    def __init__(self):        super().__init__()        self.in_footer = False        self.footer_depth = 0

### Important script limitations


This is a starting-point verifier, not a replacement for your existing link graph engine.


Before using it as a CI release gate:

- 

Improve footer detection to check for the canonical site-footer class rather than any footer element.


- 

Handle HTML pages with multiple footer elements.


- 

Account for <base href> if used.


- 

Handle fragments in non-HTML resources appropriately.


- 

Add a check for duplicate IDs.


- 

Add HTTP verification for external destinations.


- 

Compare footer link sets against the approved destination registry.


- 

Check whether internal URLs resolve to the intended canonical URL.


- 

Verify that a link's destination is indexable when the link is intended for SEO discovery.


- 

Exclude intentionally private or administrative directories from the crawl.



The script is deliberately read-only. Its job is to identify problems, not repair files automatically.


## 10.1 Recommended regression tests


Create:
Plain texttests/test_footer_integrity.py

Suggested tests:
Pythondef test_every_public_page_has_footer():    passdef test_every_footer_has_canonical_class():    passdef test_no_broken_internal_footer_links():    passdef test_no_missing_footer_assets():    passdef test_no_duplicate_footer_ids():    passdef test_no_broken_fragment_navigation():    passdef test_no_private_pages_linked_from_footer():    passdef test_all_payment_claims_are_approved():    passdef test_product_links_match_catalogue_registry():    passdef test_footer_is_mobile_responsive():    pass

The actual tests should assert against your existing product and page registries rather than maintain a second, manually edited list of destinations.


# 11. Advanced Architecture: One Canonical Footer for the Entire Website


I strongly recommend going one step further.


Your website is static HTML, Vanilla CSS and Vanilla JavaScript. That means you do not need to introduce React, Vue, Next.js or another framework to solve footer inconsistency.


There are three possible approaches.


| Approach | Advantages | Disadvantages |
| --- | --- | --- |
| Duplicate HTML templates | Simple and compatible | Future changes require multiple edits |
| Build-time HTML partials | One source of truth, static output | Requires a build process |
| JavaScript-injected footer | Centralized implementation | Rendering, SEO and accessibility risks |



Recommended Build-time HTML partials, if your current build architecture supports them.


Suggested structure:
Plain textpartials/
    footer.html

assets/
    css/
        footer.css

scripts/
    build-footer.py

tests/
    test-footer-integrity.py

The build process should:

- 

Read the canonical footer partial.


- 

Read the approved URL configuration.


- 

Calculate the correct relative path for each destination.


- 

Inject the footer into public HTML documents.


- 

Preserve all page-specific content.


- 

Write the resulting static HTML.


- 

Run the link-integrity tests.


- 

Produce a migration report.



This approach makes the footer easier to maintain.


### Important deployment rule


Do not make the public website depend on a browser-side fetch such as:
JavaScript

```
fetch("/partials/footer.html")
```



That introduces a runtime dependency and can create a temporary empty footer, rendering delays, or deployment-path problems.


The preferred architecture is:
Plain textCanonical footer partial
          |
          v
Build-time renderer
          |
          v
Static HTML pages
          |
          v
Browser renders complete footer

The browser should receive complete HTML immediately.


If your existing deployment does not have a build pipeline, use the two templates until a controlled build-time partial system is introduced.


# 12. Final Quality Assurance and Release Acceptance Criteria


The redesign should not be considered complete until all the following conditions pass.


## 12.1 Functional acceptance checklist


Release readiness
0/20 passed

Homepage footer replaced with canonical design


index.html


Directory footer upgraded


tools/index.html


All actual product detail pages upgraded


tools/*/index.html


Guides and category pages upgraded


guides/ and category/


Secondary public pages upgraded


Policies and company pages


Payment methods accurately represented


Domestic vs international inquiry


Warranty language matches actual policies


No universal unsupported guarantees


Support hours verified


No misleading availability claims


Product links resolve to real product URLs


Catalogue registry


All internal links resolve correctly


Link graph


No broken fragment navigation


All page types


No private or staged URLs linked


Indexability checks


Mobile layouts pass


320px–480px


Tablet layouts pass


768px–1024px


Desktop layouts pass


1366px–1920px


Keyboard accessibility passes


WCAG 2.1 AA checks


Existing product functionality preserved


Regression tests


No SEO metadata or schema regression


Before/after comparison


No performance regression


Core Web Vitals


No unapproved payment or security claims


Trust-content review


## 12.2 Final measurable targets


| Metric | Release target |
| --- | --- |
| Public HTML pages with canonical footer | 100% |
| Broken internal footer links | 0 |
| Broken footer images | 0 |
| Invalid fragment links | 0 |
| Unsupported payment claims | 0 |
| Unverified merchant badges | 0 |
| Private pages exposed through footer | 0 |
| Duplicate footer implementations | 0 after migration |
| Horizontal overflow | 0 |
| Accessibility critical violations | 0 |
| Existing product functionality regressions | 0 |



For Core Web Vitals, retain your existing baseline and verify that the redesign does not materially worsen it. Do not treat a Lighthouse score alone as proof of real-user Core Web Vitals performance.


# 13. Recommended Implementation Priorities


Not everything needs to be implemented simultaneously.


| Priority | Work | Reason |
| --- | --- | --- |
| P0 | Standardize footer across pages | Fixes structural inconsistency |
| P0 | Correct all broken internal paths | Protects navigation integrity |
| P0 | Accurate payment information | Customer trust and transparency |
| P0 | Accurate warranty and delivery wording | Prevents misleading claims |
| P1 | Five-column desktop design | Improves professional presentation |
| P1 | Mobile-responsive navigation | Improves usability |
| P1 | Popular product destinations | Improves discovery and conversion |
| P1 | Support information and socials | Improves customer access |
| P2 | Build-time footer partial | Long-term maintainability |
| P2 | Automated regression suite | Prevents future inconsistency |
| P2 | Visual regression automation | Protects design consistency |



## 13.1 My recommended final architecture


For AI Tool Gems, I would implement the following:


## One footer. Every public page.
Recommended architecture
- 

Canonical footer partial


One approved source of footer HTML.


- 

Centralized destination registry


Actual product, category, policy and guide URLs.


- 

Build-time path resolver


Correct paths for root and nested documents.


- 

Shared footer stylesheet


Consistent dark luxury design.


- 

Static HTML generation


No browser-side dependency to display the footer.


- 

Automated integrity verification


Every public page checked before release.



## 13.2 Expected outcome


After implementation:

- 

Homepage, directory and product pages will share a recognizable professional identity.


- 

Customers can access payment information from any product page.


- 

Replacement and fulfilment expectations become more transparent.


- 

Popular subscriptions become easier to discover.


- 

Support remains accessible throughout the customer journey.


- 

Internal navigation becomes more consistent.


- 

Footer maintenance becomes substantially easier.


- 

Future catalogue expansion will not require manually redesigning the footer.



# 14. Instructions for Antigravity / Codex Implementation


The following execution brief should accompany this document when assigning the implementation to Antigravity.
Writing

# EXECUTION TASK: AI TOOL GEMS GLOBAL FOOTER REMEDIATION


## Project


Website: https://aitoolgems.techRepository: https://github.com/m-rehman55/ai-tool-gemsTarget: Existing production website, static HTML5, Vanilla CSS3 and Vanilla JavaScript.


## Objective


Implement the approved global footer redesign described in FOOTER_REMEDIATION_PLAN.md.


The goal is to establish one consistent, accessible, responsive footer across all public pages without damaging existing functionality, SEO, internal linking, performance or product data.


## Phase 0 — Audit Before Editing


Inspect the repository and establish:

- 

Actual number of public HTML pages.


- 

Actual number of product detail pages.


- 

Actual category and guide paths.


- 

All existing footer implementations.


- 

Existing footer-related CSS.


- 

Existing product registry and product URL mappings.


- 

Existing payment and warranty policies.


- 

Public, staged, noindex and private page classifications.



Create FOOTER_AUDIT_INVENTORY.md.


Do not assume the requested 65 product pages exist until the inventory confirms the actual count.


## Phase 1 — Canonical Footer


Create one reusable footer source.


Recommended files:

- 

partials/footer.html


- 

assets/css/footer.css


- 

scripts/build-footer.py (only if compatible with the existing build system).



Do not introduce a new JavaScript framework.


Prefer build-time HTML generation over client-side footer injection.


## Phase 2 — Accurate Content


Use only verified payment methods.


Domestic supported:

- 

EasyPaisa


- 

JazzCash


- 

SadaPay


- 

NayaPay


- 

Raast


- 

Bank IBFT



International inquiry-only:

- 

Wise


- 

SWIFT bank wire



Do not advertise USDT, Binance Pay or international cards as accepted unless independently verified as operational.


Do not invent:

- 

Merchant accreditation.


- 

256-bit security certification.


- 

Guaranteed 15–30-minute delivery.


- 

Universal 100% replacement warranty.


- 

Unverified customer support availability.



Use product-specific warranty and delivery information.


## Phase 3 — URL Registry


Build a verified registry using actual repository paths.


All popular product links must map to existing individual product pages.


Never guess product slugs.


Validate all category, guide, policy and social URLs.


Support both root-level and nested page paths.


## Phase 4 — CSS


Implement the approved design:

- 

Background: #0a0d14


- 

Surface: #101622


- 

Cyan: #00e5ff


- 

Green: #22c55e



Responsive requirements:

- 

Desktop: five columns.


- 

Tablet: two to three columns.


- 

Mobile: structured single-column layout.



Implement keyboard focus, contrast, touch targets and reduced-motion support.


Preserve existing site-wide styles.


## Phase 5 — Migration


Migrate in this order:

- 

Homepage.


- 

Master tools directory.


- 

Product detail pages.


- 

Guides.


- 

Categories.


- 

Prices and deals.


- 

Company and policy pages.



Modify only the footer and necessary stylesheet references.


Preserve product-specific scripts, structured data, metadata, canonical URLs, content and page functionality.


## Phase 6 — Automated QA


Verify:

- 

Every public page has the canonical footer.


- 

All internal footer links resolve.


- 

All logo and asset paths resolve.


- 

All fragments exist.


- 

No private or staged pages are exposed.


- 

Product links match the actual catalogue.


- 

No duplicate IDs.


- 

No HTML validation regressions.


- 

No mobile horizontal overflow.


- 

No keyboard accessibility regressions.


- 

No Core Web Vitals regression.



Run existing project tests and link graph checks.


## Phase 7 — Deliverables


Produce:

- 

FOOTER_AUDIT_INVENTORY.md


- 

FOOTER_MIGRATION_REPORT.md


- 

FOOTER_LINK_AUDIT.json


- 

FOOTER_QA_REPORT.md


- 

Updated canonical footer and stylesheet.


- 

A list of all modified files.


- 

Before/after screenshots for representative page types.



## Strict Safety Rules

- 

Do not push.


- 

Do not create or merge a PR.


- 

Do not deploy.


- 

Do not modify unrelated website functionality.


- 

Do not modify product prices.


- 

Do not change product availability.


- 

Do not change SEO indexing classifications.


- 

Do not introduce fabricated trust claims.


- 

Do not delete existing content.


- 

Do not perform broad, unverified HTML replacements.



Work incrementally.


After every phase, run the relevant tests and report actual results.


If a path, payment method, policy statement or support claim cannot be verified, mark it as requiring owner approval rather than guessing.


Final acceptance requires zero broken internal footer links, zero unintended page regressions and consistent footer coverage across all public pages.


## 15. Final recommendation


The most important decision is to avoid treating this as a simple HTML replacement exercise.


Your footer should become a centrally maintained marketplace component, with a verified product URL registry, accurate payment information and automated checks.


My recommended order is:

- 

Audit actual repository paths and existing footer variations.


- 

Build the canonical footer.


- 

Implement the shared CSS.


- 

Upgrade homepage and directory.


- 

Batch-migrate product pages.


- 

Upgrade guides, categories and policies.


- 

Run link graph, accessibility, visual and performance regression checks.


- 

Release only after all acceptance criteria pass.



One final caution: the supplied footer HTML and the currently indexed homepage have differences in their payment and warranty messaging. The live homepage already documents local Pakistani payment methods, international inquiry-only arrangements and manual fulfilment. Those existing operational facts should take precedence over proposed but unverified badges. AI Tool Gems+2


For the next stage, I can help review Antigravity's implementation report against this plan and identify any missed files, broken links, inaccurate claims or regressions.
ChatGPT can make mistakes. Check important info.

#### Latest response