# SELLABLE_TOOLS_CONVERSION_PLAN.md


Production architecture specification 65-target commercial catalog Owner approval required before commercial launch


Project: AI Tool Gems Pakistan
Domain: https://aitoolgems.tech
Repository: https://github.com/m-rehman55/ai-tool-gems
Target branch: main
Target catalog: 65 sellable products
Target directory-only products: 0
Currency: PKR (primary), USD (reference)
Primary checkout: WhatsApp assisted checkout
Secondary checkout: Cart → WhatsApp
Document: SELLABLE_TOOLS_CONVERSION_PLAN.md


# 1. Executive Summary


## 1.1 Project objective


Convert all 25 existing DIRECTORY tools into commercially sellable ASSISTED products.


The final catalog must contain:


| Metric | Current stated state | Target state |
| --- | --- | --- |
| Total tools | 65 | 65 |
| Sellable products | 40 | 65 |
| Directory-only tools | 25 | 0 |
| Products with PKR prices | 40 | 65 |
| Products with WhatsApp checkout | 40 | 65 |
| Products with cart support | 40 | 65 |
| Products with individual detail pages | Verify existing | 65 |
| Products with Product schema | 40 | 65 |
| Products with valid Offer schema | 40 | 65 |



Important: These are target acceptance criteria, not verified current repository measurements. The first implementation step must inspect the actual main branch and establish the real baseline. Existing repository reports have shown different catalog and profile counts at different stages. Never assume that the current production catalog contains exactly 40 ASSISTED records and 25 DIRECTORY records merely because that is the supplied business specification.


## 1.2 The fundamental architectural decision


The conversion must not be a superficial UI replacement.


Changing:
JavaScript

```
model: "DIRECTORY"
```



to:
JavaScript

```
model: "ASSISTED"
```



does not automatically make a product commercially sellable.


A product is sellable only when all of the following are true:

- 

A legitimate supply and fulfillment method exists.


- 

The exact subscription, license, account or credit package is identified.


- 

The selling price has been verified.


- 

The product duration is unambiguous.


- 

The access type is documented.


- 

The replacement warranty is defined.


- 

The WhatsApp checkout generator works.


- 

The cart recognizes the product.


- 

The product detail page explains what the customer receives.


- 

Product and Offer structured data accurately represent the transaction.


- 

Inventory and fulfillment status are controlled.


- 

The product passes automated and manual tests.



A product that has a price badge but no verified supply is not a sellable product.


## 1.3 Non-negotiable commercial safeguards


Before proceeding, establish these rules:

- 

Never invent a supplier price.


- 

Never present an official USD subscription price as an AI Tool Gems resale price.


- 

Never calculate a final PKR price without a verified supplier cost, exchange-rate source, applicable fees and approved margin.


- 

Never promise a 30-day replacement warranty when the supplier's coverage or the business's operational capability does not support it.


- 

Never describe a shared account as a private account.


- 

Never advertise team invitations as private subscriptions.


- 

Never sell account credentials, keys, credits or subscription access without the necessary authorization and compliance with the relevant provider's terms.


- 

Never publish fake ratings, customer reviews, availability, stock or delivery claims.


- 

Never use an invented AggregateRating to improve search appearance.


- 

Never advertise 24/7 human support unless that support is actually staffed or an accurately described automated support service is available.



Recommended policy: All 25 records may be migrated into the commercial catalog architecture, but a product cannot become publicly purchasable until it passes its individual commercial-readiness gate.


This distinction is essential:


Catalog migration ≠ authorization to sell ≠ verified fulfillment readiness.


# 2. Target Architecture


## 2.1 Final system architecture


The desired architecture should follow this flow:
Plain text                    AI TOOL GEMS
                         |
                         |
                 app.js MASTER CATALOG
                         |
             +-----------+-----------+
             |                       |
        ASSISTED MODEL          VALIDATION ENGINE
             |                       |
             +-----------+-----------+
                         |
               COMMERCIAL PRODUCT DATA
                         |
        +----------------+----------------+
        |                |                |
     Homepage        tools/index.html   Product Pages
        |                |                |
        +----------------+----------------+
                         |
                 PRODUCT DETAIL
                         |
              +----------+----------+
              |                     |
         ADD TO CART           WHATSAPP BUY
              |                     |
              +----------+----------+
                         |
                  CART VALIDATION
                         |
                 WHATSAPP GENERATOR
                         |
                 CUSTOMER CONFIRMATION
                         |
                PAYMENT VERIFICATION
                         |
                 FULFILLMENT SYSTEM
                         |
                DELIVERY CONFIRMATION
                         |
                 WARRANTY TRACKING

## 2.2 Single source of truth


app.js must remain the canonical product-data source.


Do not maintain separate manually written prices in:

- 

Homepage cards.


- 

Individual product pages.


- 

Category pages.


- 

Master catalog tables.


- 

Cart records.


- 

WhatsApp messages.


- 

JSON-LD schema.


- 

Product comparison widgets.



All these interfaces should consume the same canonical product information.


Where static HTML requires server-generated or build-generated content, use a controlled catalog-generation process. Do not introduce a second independently maintained catalog.


## 2.3 Required product lifecycle


Every product must support the following internal lifecycle:
Plain textDIRECTORY
   |
   v
COMMERCIAL_RESEARCH
   |
   v
SUPPLY_VERIFIED
   |
   v
PRICE_VERIFIED
   |
   v
PACKAGE_APPROVED
   |
   v
FULFILLMENT_TESTED
   |
   v
OWNER_APPROVED
   |
   v
ASSISTED_ACTIVE
   |
   v
MONITORING

Failure conditions:
Plain textSUPPLY_UNAVAILABLE
PRICE_EXPIRED
AUTHORIZATION_UNVERIFIED
FULFILLMENT_FAILED
WARRANTY_UNSUPPORTED
TEMPORARILY_UNAVAILABLE
DISCONTINUED

A failed product must not silently remain purchasable.


# 3. The 25-Tool Conversion Inventory


The following is the authoritative migration scope supplied for this project.


| # | Slug | Product | Category |
| --- | --- | --- | --- |
| 1 | bolt-new | Bolt.new | Development |
| 2 | coursera-plus | Coursera Plus | Education |
| 3 | descript | Descript | Video & Audio |
| 4 | firecrawl | Firecrawl | Development |
| 5 | invideo-ai | InVideo AI | Video & Audio |
| 6 | make | Make.com | Productivity |
| 7 | manus-ai | Manus AI | AI Assistants |
| 8 | opus-clip | Opus Clip | Video & Audio |
| 9 | qwen | Qwen | AI Assistants |
| 10 | udemy-personal | Udemy Personal Plan | Education |
| 11 | v0 | v0 by Vercel | Development |
| 12 | windsurf | Windsurf | Development |
| 13 | ahrefs | Ahrefs | SEO & Marketing |
| 14 | chatprd | ChatPRD | Productivity |
| 15 | davinci-resolve | DaVinci Resolve Studio | Video & Audio |
| 16 | domo-ai | Domo AI | Video & Audio |
| 17 | genspark | Genspark | AI Assistants |
| 18 | hailuo-ai | Hailuo AI | Video & Audio |
| 19 | higgsfield | Higgsfield AI | Video & Audio |
| 20 | morphic | Morphic | AI Assistants |
| 21 | notebooklm | NotebookLM | Productivity |
| 22 | quizlet | Quizlet Plus | Education |
| 23 | railway | Railway | Development |
| 24 | skillshare | Skillshare Premium | Education |
| 25 | supabase | Supabase Pro | Development |



Category assignments must be checked against the existing category taxonomy before implementation. Do not create duplicate categories merely because two labels use slightly different wording.


# PHASE 0 — Repository Forensics and Pre-Implementation Audit
Mandatory before code changes

The objective is to ensure that the conversion does not break existing products, checkout, SEO, cart functionality, analytics, category navigation or production indexing.


## 0.1 Repository inspection


Repository:


https://github.com/m-rehman55/ai-tool-gems


Branch:


main


The implementation agent must inspect the repository before modifying anything.


Required inspection:
Bash

```
git status --short
git branch --show-current
git log -5 --oneline
git rev-parse HEAD
```



Verify:

- 

No uncommitted user changes are overwritten.


- 

The correct branch is checked out.


- 

The current production baseline is recorded.


- 

Existing product IDs and URLs are preserved.


- 

Existing ASSISTED products are not accidentally rewritten.


- 

Existing staged/noindex products retain their indexing safeguards until approved.


- 

Existing tests and reports are inspected before changing their assertions.



## 0.2 Required files to inspect


| File | Inspection objective |
| --- | --- |
| app.js | Catalog objects, pricing, model, cart, WhatsApp |
| index.html | Homepage product cards and filters |
| tools/index.html | Master catalog and directory listings |
| tools/*/index.html | Existing product detail pages |
| assets/js/* | Cart, checkout and UI dependencies |
| assets/css/* | Existing product and card styling |
| sitemap.xml | Current indexed URL inventory |
| robots.txt | Crawl rules |
| tests/ | Existing test architecture |
| scripts/ | Catalog and sitemap generation |
| .github/workflows/ | CI and deployment automation |
| package.json | Available scripts and dependencies |
| README.md | Existing development instructions |



Do not assume that these files all exist at these exact paths. Discover the actual structure first.


## 0.3 Establish the baseline


Produce:


reports/sellable-tools/baseline_inventory.json


Required contents:
JSON

```
{
  "project": "AI Tool Gems",
  "domain": "https://aitoolgems.tech",
  "branch": "main",
  "baseline_commit": "ACTUAL_GIT_COMMIT",
  "target_sellable_products": 65,
  "target_directory_products": 0,
  "measured": {
    "total_catalog_records": 0,
    "assisted_products": 0,
    "directory_products": 0,
    "missing_prices": 0,
    "missing_detail_pages": 0,
    "missing_whatsapp_checkout": 0,
    "missing_cart_support": 0,
    "missing_product_schema": 0,
    "missing_offer_schema": 0
  },
  "migration_scope": [],
  "known_conflicts": [],
  "approval_required": true
}
```



The zeros above are schema defaults, not claimed measurements. The audit script must populate actual values.


## 0.4 Build a migration manifest


Create:


data/migrations/sellable-tools-conversion.json


Each tool must have a migration record:
JSON

```
{
  "slug": "bolt-new",
  "previous_model": "DIRECTORY",
  "target_model": "ASSISTED",
  "commercial_status": "RESEARCH_REQUIRED",
  "supplier_verified": false,
  "price_verified": false,
  "access_type_verified": false,
  "duration_verified": false,
  "warranty_approved": false,
  "fulfillment_tested": false,
  "owner_approved": false,
  "publicly_purchasable": false,
  "indexing_approved": false
}
```



This file becomes the audit trail for all 25 conversions.


## 0.5 Preflight acceptance criteria


Before proceeding:

- Actual baseline inventory generated.

- All 25 slugs matched against existing catalog records.

- Existing 40 products identified and preserved.

- Existing detail-page URL conflicts identified.

- Existing category taxonomy inspected.

- Cart implementation inspected.

- WhatsApp implementation inspected.

- Existing structured data inspected.

- Sitemap generation mechanism identified.

- Existing tests executed.

- Git working tree protected.

- Migration manifest generated.


# PHASE 1 — Commercial Pricing & Packaging Matrix
Commercial verification required

This is the most important business layer.


A product should not receive an invented price simply to make a card look complete.


The supplied requirements do not include verified supplier quotations, resale authorization, exact subscription packages or the applicable exchange rate. Therefore, assigning 25 supposedly verified PKR prices would create fabricated commercial information.


The matrix below defines the required commercial research and approval fields. Every PENDING field must be resolved using current official plan information and a verified, authorized fulfillment source before activation.


## 1.1 Required pricing model


Every product must have:

- 

Official vendor plan.


- 

Official vendor USD price, when applicable.


- 

Supplier acquisition cost.


- 

Supplier currency.


- 

Supplier quotation date.


- 

Exchange-rate source.


- 

Conversion rate.


- 

Payment and transaction fees.


- 

Operational cost.


- 

Approved selling price in PKR.


- 

Expected gross margin.


- 

Package duration.


- 

Access type.


- 

Replacement warranty.


- 

Fulfillment method.


- 

Stock or capacity status.



### Pricing formula


Use:
CPKR=Csupplier×FXC_{\text{PKR}} =
C_{\text{supplier}} \times FXCPKR​=Csupplier​×FX

Where:

- 

CsupplierC_{\text{supplier}}Csupplier​ = verified acquisition cost.


- 

FXFXFX = approved currency conversion rate.



Then:
Pselling=CPKR+Fpayment+Coperations+MapprovedP_{\text{selling}} =
C_{\text{PKR}}+
F_{\text{payment}}+
C_{\text{operations}}+
M_{\text{approved}}Pselling​=CPKR​+Fpayment​+Coperations​+Mapproved​

Where:

- 

FpaymentF_{\text{payment}}Fpayment​ = payment fees.


- 

CoperationsC_{\text{operations}}Coperations​ = fulfillment and support allocation.


- 

MapprovedM_{\text{approved}}Mapproved​ = approved margin.



Do not automatically apply one markup percentage to all 25 products.


Some products have recurring subscriptions, some have consumption credits, some have fixed licenses and others have usage-based billing.


A 30-day subscription and a 1,000-credit package are not interchangeable pricing units.


## 1.2 Master commercial matrix


The following table establishes the required packaging research for all 25 products.


| # | Product | Official USD price | Verified PKR selling price | Duration | Access type | Warranty |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Bolt.new | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 2 | Coursera Plus | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 3 | Descript | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 4 | Firecrawl | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 5 | InVideo AI | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 6 | Make.com | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 7 | Manus AI | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 8 | Opus Clip | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 9 | Qwen | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 10 | Udemy Personal | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 11 | v0 | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 12 | Windsurf | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 13 | Ahrefs | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 14 | ChatPRD | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 15 | DaVinci Resolve Studio | Verify license | Pending | Verify | Pending | Approve 7/30 |
| 16 | Domo AI | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 17 | Genspark | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 18 | Hailuo AI | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 19 | Higgsfield AI | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 20 | Morphic | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 21 | NotebookLM | Verify eligible offering | Pending | Verify | Pending | Approve 7/30 |
| 22 | Quizlet Plus | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 23 | Railway | Verify plan | Pending | Pending | Pending | Approve 7/30 |
| 24 | Skillshare Premium | Verify plan | Pending | Verify | Pending | Approve 7/30 |
| 25 | Supabase Pro | Verify plan | Pending | Verify | Pending | Approve 7/30 |



### Required access-type definitions


The catalog must distinguish the following:


| Access type | Customer-facing explanation |
| --- | --- |
| PRIVATE_ACCOUNT | Customer receives access through their own authorized account |
| TEAM_INVITE | Customer is invited to an authorized workspace or team |
| SHARED | Shared access, only if explicitly permitted by the provider and disclosed |
| CREDIT | A specified number of usage credits |
| KEY | A genuine, authorized activation or license key |



Do not classify all products as PRIVATE_ACCOUNT by default.


Some providers restrict account sharing, team-seat resale, geographic availability or third-party distribution. The commercial verification process must establish which arrangements are actually permitted.


## 1.3 Product-specific commercial research requirements


The research agent must investigate each product separately.


| Product | Required verification |
| --- | --- |
| Bolt.new | Token/usage limits, subscription period, project access, applicable team restrictions |
| Coursera Plus | Eligible courses, subscription duration, regional eligibility, authorized access arrangement |
| Descript | Editing limits, media transcription, AI credits, export limits |
| Firecrawl | API credits, crawl limits, rate limits, monthly allowance |
| InVideo AI | Generative credits, video export limits, plan restrictions |
| Make.com | Operations allowance, scenario limits, execution scheduling |
| Manus AI | Credits, task allowances, model availability, account eligibility |
| Opus Clip | Processing credits, video length, export limits |
| Qwen | Exact service and plan, model access, API quotas, credit units |
| Udemy Personal | Regional availability, eligible course library, subscription conditions |
| v0 | Message/usage credits, project limits, deployment integration |
| Windsurf | Model usage, request allowances, editor features |
| Ahrefs | Exact plan, reporting limits, keyword credits, seat count and redistribution restrictions |
| ChatPRD | Plan limits, document allowances, AI usage |
| DaVinci Resolve Studio | Genuine license type, activation limits, device restrictions |
| Domo AI | Generation credits, video duration, export limits |
| Genspark | Credits, research limits, AI model access |
| Hailuo AI | Generation credits, output length, video resolution |
| Higgsfield AI | Credit packages, generation limits, output specifications |
| Morphic | Current subscription offering, generation allowance, account access |
| NotebookLM | Available official access and subscription eligibility, audio overview limits |
| Quizlet Plus | Subscription duration, premium features, regional availability |
| Railway | Usage-based billing, included allowance, deployment resources, overage exposure |
| Skillshare Premium | Membership duration, eligible classes and geographic availability |
| Supabase Pro | Organization ownership, compute, storage, bandwidth and billing limits |



Special warning: Railway, Supabase, Firecrawl and Make.com have usage-based or quota-related commercial considerations. A fixed PKR selling price must specify exactly what usage is included and who bears overage costs.


DaVinci Resolve Studio must be treated as a genuine software license, not a generic subscription.


NotebookLM should not be described as a paid standalone product if the actual offer is access to an eligible Google account or a different Google subscription.


## 1.4 Payment methods


Create a shared payment-method configuration rather than embedding payment labels into 65 product records.


Initial supported domestic payment options, subject to current business availability:

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



The UI must only show methods that are currently operational.


Each checkout must communicate:

- 

Product subtotal.


- 

Quantity.


- 

Selected package.


- 

Total PKR amount.


- 

Payment instructions.


- 

Order reference.


- 

WhatsApp support contact.



Never state that a payment has been received merely because a customer submits a WhatsApp message.


## 1.5 Warranty architecture


Create two explicit warranty types:


7-day replacement warranty


Use only for packages approved for seven-day replacement coverage.


30-day replacement warranty


Use only when the supplier agreement and internal support process can support the full coverage period.


Define the warranty precisely:

- 

Start date: verified delivery timestamp.


- 

Covered failure: loss of promised access attributable to the supplied product.


- 

Exclusions: customer misuse, account-sharing violations, policy violations, unauthorized modifications and other clearly disclosed exclusions.


- 

Remedy: replacement or another explicitly approved resolution.


- 

Claim process: WhatsApp order reference and evidence.


- 

Resolution target: a separately published support commitment.



Do not imply that warranty coverage guarantees uninterrupted vendor service.


## 1.6 Required pricing data file


Create:


data/commercial/product-pricing.json


Example:
JSON

```
{
  "bolt-new": {
    "official_plan": null,
    "official_usd_price": null,
    "supplier_cost": null,
    "supplier_currency": "USD",
    "exchange_rate": null,
    "exchange_rate_source": null,
    "quotation_reference": null,
    "quotation_date": null,
    "selling_price_pkr": null,
    "duration_days": null,
    "access_type": null,
    "included_allowance": null,
    "overage_policy": null,
    "warranty_days": null,
    "fulfillment_method": null,
    "authorization_verified": false,
    "price_verified": false,
    "owner_approved": false,
    "publicly_purchasable": false
  }
}
```



The pricing system must reject null values for required fields when publicly_purchasable is true.


# PHASE 2 — app.js Global Catalog Engine Refactor
Core architecture

This phase makes the conversion permanent and prevents the website from developing inconsistent product records.


## 2.1 Canonical product model


Every product must follow one consistent data contract.


Recommended object structure:
JavaScript

```
{
  id: "bolt-new",

  slug: "bolt-new",

  name: "Bolt.new",

  brand: "StackBlitz",

  model: "ASSISTED",

  category: "development",

  subcategory: "ai-web-development",

  description: "AI-powered full-stack development.",

  shortDescription: "Build full-stack applications with AI.",

  commercial: {
    status: "RESEARCH_REQUIRED",

    currency: "PKR",

    price: null,

    originalPrice: null,

    officialUsdPrice: null,

    durationDays: null,

    durationLabel: null,

    packageName: null,

    accessType: null,

    includedAllowance: null,

    supplierVerified: false,

    authorizationVerified: false,

    priceVerified: false,

    ownerApproved: false
  },

  warranty: {
    days: null,

    label: null,

    approved: false,

    termsUrl: null
  },

  fulfillment: {
    type: null,

    deliveryEstimate: null,

    availability: "UNVERIFIED",

    support: "ASSISTED"
  },

  commerce: {
    purchasable: false,

    cartEnabled: false,

    whatsappEnabled: false,

    quantityAllowed: true
  },

  seo: {
    canonical: "https://aitoolgems.tech/tools/bolt-new/",

    indexable: false,

    title: "Bolt.new Price in Pakistan | AI Tool Gems",

    description: "Explore Bolt.new plans, verified PKR pricing and authorized access options."
  },

  urls: {
    detail: "/tools/bolt-new/"
  }
}
```



The null values are intentional. They prevent fabricated commercial claims.


## 2.2 Global catalog definition


Use a dedicated catalog collection for the 25 records.


The following is the complete initial migration definition. These records are intentionally not purchasable until their commercial fields pass verification.
JavaScript

```

const DIRECTORY_TO_ASSISTED_MIGRATION = [
  {
    id: "bolt-new",
    name: "Bolt.new",
    brand: "StackBlitz",
    category: "development",
    subcategory: "ai-web-development",
    shortDescription: "AI-powered full-stack web development.",
    detailPath: "/tools/bolt-new/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "coursera-plus",
    name: "Coursera Plus",
    brand: "Coursera",
    category: "education",
    subcategory: "online-learning",
    shortDescription: "Access eligible professional courses and learning programs.",
    detailPath: "/tools/coursera-plus/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "descript",
    name: "Descript",
    brand: "Descript",
    category: "video-audio",
    subcategory: "video-editing",
    shortDescription: "AI-assisted audio and video editing.",
    detailPath: "/tools/descript/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "firecrawl",
    name: "Firecrawl",
    brand: "Firecrawl",
    category: "development",
    subcategory: "web-data",
    shortDescription: "Web crawling and structured data extraction.",
    detailPath: "/tools/firecrawl/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "invideo-ai",
    name: "InVideo AI",
    brand: "InVideo",
    category: "video-audio",
    subcategory: "ai-video-generation",
    shortDescription: "AI-powered text-to-video creation.",
    detailPath: "/tools/invideo-ai/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "make",
    name: "Make.com",
    brand: "Make",
    category: "productivity",
    subcategory: "workflow-automation",
    shortDescription: "Visual workflow automation and integrations.",
    detailPath: "/tools/make/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "manus-ai",
    name: "Manus AI",
    brand: "Manus",
    category: "ai-assistants",
    subcategory: "autonomous-agents",
    shortDescription: "Autonomous AI research and task execution.",
    detailPath: "/tools/manus-ai/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "opus-clip",
    name: "Opus Clip",
    brand: "OpusClip",
    category: "video-audio",
    subcategory: "video-repurposing",
    shortDescription: "Convert long-form videos into short clips.",
    detailPath: "/tools/opus-clip/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "qwen",
    name: "Qwen",
    brand: "Alibaba",
    category: "ai-assistants",
    subcategory: "large-language-models",
    shortDescription: "Qwen AI models and eligible service offerings.",
    detailPath: "/tools/qwen/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "udemy-personal",
    name: "Udemy Personal Plan",
    brand: "Udemy",
    category: "education",
    subcategory: "online-learning",
    shortDescription: "Eligible professional and technical learning content.",
    detailPath: "/tools/udemy-personal/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "v0",
    name: "v0",
    brand: "Vercel",
    category: "development",
    subcategory: "ai-ui-development",
    shortDescription: "Generate UI components and application interfaces.",
    detailPath: "/tools/v0/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "windsurf",
    name: "Windsurf",
    brand: "Windsurf",
    category: "development",
    subcategory: "ai-code-editor",
    shortDescription: "AI-assisted agentic software development.",
    detailPath: "/tools/windsurf/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "ahrefs",
    name: "Ahrefs",
    brand: "Ahrefs",
    category: "seo-marketing",
    subcategory: "seo-research",
    shortDescription: "SEO keyword and backlink research.",
    detailPath: "/tools/ahrefs/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "chatprd",
    name: "ChatPRD",
    brand: "ChatPRD",
    category: "productivity",
    subcategory: "product-management",
    shortDescription: "AI-assisted product requirements and documentation.",
    detailPath: "/tools/chatprd/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "davinci-resolve",
    name: "DaVinci Resolve Studio",
    brand: "Blackmagic Design",
    category: "video-audio",
    subcategory: "professional-video-editing",
    shortDescription: "Professional video editing and color grading.",
    detailPath: "/tools/davinci-resolve/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "domo-ai",
    name: "Domo AI",
    brand: "DomoAI",
    category: "video-audio",
    subcategory: "ai-video-generation",
    shortDescription: "AI-powered video and visual style transformation.",
    detailPath: "/tools/domo-ai/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "genspark",
    name: "Genspark",
    brand: "Genspark",
    category: "ai-assistants",
    subcategory: "ai-search",
    shortDescription: "AI search and research workspace.",
    detailPath: "/tools/genspark/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "hailuo-ai",
    name: "Hailuo AI",
    brand: "MiniMax",
    category: "video-audio",
    subcategory: "ai-video-generation",
    shortDescription: "AI-generated cinematic video.",
    detailPath: "/tools/hailuo-ai/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "higgsfield",
    name: "Higgsfield AI",
    brand: "Higgsfield",
    category: "video-audio",
    subcategory: "ai-video-generation",
    shortDescription: "AI cinematic motion and character generation.",
    detailPath: "/tools/higgsfield/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "morphic",
    name: "Morphic",
    brand: "Morphic",
    category: "ai-assistants",
    subcategory: "ai-search",
    shortDescription: "AI-powered search and generative answers.",
    detailPath: "/tools/morphic/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "notebooklm",
    name: "NotebookLM",
    brand: "Google",
    category: "productivity",
    subcategory: "ai-research",
    shortDescription: "AI-powered research and Audio Overviews.",
    detailPath: "/tools/notebooklm/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "quizlet",
    name: "Quizlet Plus",
    brand: "Quizlet",
    category: "education",
    subcategory: "study-tools",
    shortDescription: "AI-assisted flashcards and study tools.",
    detailPath: "/tools/quizlet/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "railway",
    name: "Railway",
    brand: "Railway",
    category: "development",
    subcategory: "cloud-deployment",
    shortDescription: "Cloud application and database deployment.",
    detailPath: "/tools/railway/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "skillshare",
    name: "Skillshare Premium",
    brand: "Skillshare",
    category: "education",
    subcategory: "creative-learning",
    shortDescription: "Creative and professional learning classes.",
    detailPath: "/tools/skillshare/",
    commercialStatus: "RESEARCH_REQUIRED"
  },
  {
    id: "supabase",
    name: "Supabase Pro",
    brand: "Supabase",
    category: "development",
    subcategory: "backend-infrastructure",
    shortDescription: "Managed backend, database and application infrastructure.",
    detailPath: "/tools/supabase/",
    commercialStatus: "RESEARCH_REQUIRED"
  }
];

```



This is the migration manifest, not the final commercial catalog object. It must be enriched with approved commercial data before activation.


## 2.3 Integrate with the existing catalog


Do not create a second competing product registry.


Instead, merge the 25 migration definitions into the existing catalog through a controlled migration.


Example:
JavaScript

```
function migrateDirectoryProduct(product, migration) {
  if (product.id !== migration.id) {
    throw new Error("Product identity mismatch");
  }

  return {
    ...product,

    model: "ASSISTED",

    category: migration.category,

    subcategory: migration.subcategory,

    shortDescription: migration.shortDescription,

    detailPath: migration.detailPath,

    commercialStatus: "RESEARCH_REQUIRED",

    commerce: {
      ...product.commerce,
      purchasable: false,
      cartEnabled: false,
      whatsappEnabled: false
    }
  };
}
```



The production implementation must preserve existing fields not explicitly being migrated.


Do not blindly spread an existing DIRECTORY object into an ASSISTED object if its old schema contains incompatible checkout or availability fields. Validate the resulting object against the canonical schema.


## 2.4 Commercial activation guard


Implement a centralized activation function.
JavaScript

```
function isProductCommerciallyReady(product) {
  const commercial = product.commercial || {};
  const warranty = product.warranty || {};
  const fulfillment = product.fulfillment || {};

  return Boolean(
    product.model === "ASSISTED" &&
    commercial.status === "APPROVED" &&
    Number.isFinite(commercial.price) &&
    commercial.price > 0 &&
    commercial.durationLabel &&
    commercial.accessType &&
    commercial.supplierVerified === true &&
    commercial.authorizationVerified === true &&
    commercial.priceVerified === true &&
    commercial.ownerApproved === true &&
    warranty.approved === true &&
    [7, 30].includes(warranty.days) &&
    fulfillment.availability === "AVAILABLE"
  );
}
```



Add a stricter check for usage-based products:
JavaScript

```
function validateUsagePackage(product) {
  if (!product.commercial?.includedAllowance) {
    throw new Error(
      `${product.id}: usage allowance is required`
    );
  }

  if (!product.commercial?.overagePolicy) {
    throw new Error(
      `${product.id}: overage policy is required`
    );
  }

  return true;
}
```



## 2.5 Cart enablement


All 65 products must be recognized by the cart engine, but only approved products should be addable.


The important distinction:

- 

Catalog eligibility: the product exists in the catalog.


- 

Cart eligibility: the product is commercially approved and available.


- 

Checkout eligibility: the current product configuration can be fulfilled.



Example:
JavaScript

```
function canAddToCart(product) {
  return (
    product.model === "ASSISTED" &&
    product.commerce?.cartEnabled === true &&
    product.commerce?.purchasable === true &&
    isProductCommerciallyReady(product)
  );
}
```



When a product is not approved, show:


Currently unavailable — contact our team for information.


Do not show a false purchasable CTA.


## 2.6 Centralized WhatsApp generator


All product and cart checkout messages must use one message generator.
JavaScript

```
function generateProductWhatsAppMessage(product, quantity = 1) {
  if (!canAddToCart(product) && !product.commerce?.whatsappEnabled) {
    throw new Error("Product is not approved for checkout");
  }

  const message = [
    "Hello AI Tool Gems!",
    "",
    "I want to order the following product:",
    `Product: ${product.name}`,
    `Package: ${product.commercial.packageName}`,
    `Duration: ${product.commercial.durationLabel}`,
    `Access: ${product.commercial.accessType}`,
    `Quantity: ${quantity}`,
    `Price: PKR ${product.commercial.price}`,
    `Warranty: ${product.warranty.days} days`,
    "",
    `Product URL: https://aitoolgems.tech${product.detailPath}`,
    "",
    "Please confirm availability and payment instructions."
  ].join("\n");

  return message;
}
```



Production requirements:

- 

Use the actual WhatsApp business number from the existing configuration.


- 

URL-encode the complete message.


- 

Use integer quantities.


- 

Recalculate subtotal from the canonical catalog.


- 

Reject unavailable products.


- 

Never trust a price supplied by local storage or URL parameters.


- 

Avoid exposing internal supplier cost or margin.


- 

Never include customer passwords or sensitive credentials in the message.



## 2.7 Cart subtotal calculation
JavaScript

```
function calculateCartSubtotal(cartItems, catalog) {
  return cartItems.reduce((total, item) => {
    const product = catalog.find(
      product => product.id === item.id
    );

    if (!product || !canAddToCart(product)) {
      throw new Error(
        `Invalid or unavailable product: ${item.id}`
      );
    }

    const quantity = Math.max(
      1,
      Math.floor(Number(item.quantity) || 1)
    );

    return total +
      product.commercial.price * quantity;
  }, 0);
}
```



Never accept a browser-stored product price as authoritative.


## 2.8 Search and category filters


The new category taxonomy must be compatible with the existing filter engine.


Recommended filter values:
JavaScript

```
const PRODUCT_CATEGORIES = [
  "ai-assistants",
  "development",
  "video-audio",
  "education",
  "productivity",
  "seo-marketing"
];
```



Each product should support:

- 

Primary category.


- 

Subcategory.


- 

Brand.


- 

Price.


- 

Duration.


- 

Access type.


- 

Warranty.


- 

Availability.


- 

Search keywords.



Do not hardcode the category list separately in five different UI files.


## 2.9 Global catalog invariants


Add these assertions:
JavaScript

```
function validateCatalog(catalog) {
  const ids = catalog.map(product => product.id);

  if (new Set(ids).size !== ids.length) {
    throw new Error("Duplicate product IDs detected");
  }

  for (const product of catalog) {
    if (!product.id || !product.name) {
      throw new Error("Missing product identity");
    }

    if (product.model === "DIRECTORY") {
      throw new Error(
        `Directory product remains: ${product.id}`
      );
    }

    if (product.model !== "ASSISTED") {
      throw new Error(
        `Unexpected model: ${product.id}`
      );
    }

    if (
      product.commerce?.purchasable &&
      !isProductCommerciallyReady(product)
    ) {
      throw new Error(
        `Unapproved product is purchasable: ${product.id}`
      );
    }
  }

  return true;
}
```



The final production catalog must pass:
JavaScript

```
validateCatalog(PRODUCTS);
```



# PHASE 3 — Homepage UI Cards in index.html


## 3.1 Objective


Every converted product must use the same commercial card architecture as existing ASSISTED products.


Remove the directory-only CTA:


Explore Free Tool ↗


Do not simply replace its text with Buy Now.


The old directory card may have different data attributes, event listeners and markup. The new card must integrate with the existing cart and checkout engines.


## 3.2 Required card layout


Bolt.new
Commercial product

StackBlitz · Development


# PKR —


Approved package pricing displayed here


Duration


Verified package


Access


Verified access type


Warranty


Approved coverage


Buy on WhatsApp


Direct assisted checkout


Add to Cart
Illustrative layout only; no unverified price or warranty is displayed.

## 3.3 Exact card HTML template


The following is the required target markup. The production agent must adapt the classes and event handlers to the existing site's CSS and JavaScript architecture.
HTML

```

<article
  class="product-card assisted-product-card"
  data-product-id="bolt-new"
  data-model="ASSISTED"
  data-category="development"
>
  <div class="product-card__header">

    <span class="product-category">
      Development
    </span>

    <span class="product-model-badge">
      Assisted
    </span>

  </div>

  <h3 class="product-card__title">
    <a href="/tools/bolt-new/">
      Bolt.new
    </a>
  </h3>

  <p class="product-card__description">
    AI-powered full-stack web development.
  </p>

  <div class="product-price">
    <span class="product-price__label">
      Starting from
    </span>

    <strong
      class="product-price__amount"
      data-price-for="bolt-new"
    >
      PKR —
    </strong>
  </div>

  <div class="product-specs">

    <div>
      <span>Duration</span>
      <strong data-duration-for="bolt-new">
        Verify package
      </strong>
    </div>

    <div>
      <span>Access</span>
      <strong data-access-for="bolt-new">
        Verify access
      </strong>
    </div>

    <div>
      <span>Warranty</span>
      <strong data-warranty-for="bolt-new">
        Verify coverage
      </strong>
    </div>

  </div>

  <div class="product-card__actions">

    <a
      class="btn btn-primary"
      href="/tools/bolt-new/"
      data-product-buy="bolt-new"
    >
      View Product
    </a>

    <button
      type="button"
      class="btn btn-secondary"
      data-add-to-cart="bolt-new"
      disabled
    >
      Add to Cart
    </button>

  </div>
</article>

```



The disabled state is intentional until commercial approval.


Once the product is approved, the catalog renderer must populate the price, package information and checkout actions.


## 3.4 Recommended rendering strategy


Use the canonical catalog to generate product cards.
JavaScript

```
function renderProductCard(product) {
  const approved = isProductCommerciallyReady(product);

  const price = approved
    ? `PKR ${product.commercial.price.toLocaleString("en-PK")}`
    : "Pricing under verification";

  const buyLabel = approved
    ? "Buy on WhatsApp"
    : "View Product";

  return `
    <article
      class="product-card assisted-product-card"
      data-product-id="${escapeHTML(product.id)}"
      data-model="ASSISTED"
    >
      <h3>
        <a href="${escapeHTML(product.detailPath)}">
          ${escapeHTML(product.name)}
        </a>
      </h3>

      <p>${escapeHTML(product.shortDescription)}</p>

      <strong>${price}</strong>

      <a href="${escapeHTML(product.detailPath)}">
        ${buyLabel}
      </a>

      <button
        type="button"
        data-add-to-cart="${escapeHTML(product.id)}"
        ${approved ? "" : "disabled"}
      >
        Add to Cart
      </button>
    </article>
  `;
}
```



Use a proven HTML escaping function. Do not interpolate untrusted catalog data into raw HTML without escaping.


## 3.5 Homepage conversion requirements

- 

All 25 products appear in the correct categories.


- 

All 25 cards link to their own detail pages.


- 

All 25 cards use consistent card dimensions.


- 

Price badges are populated only from approved pricing data.


- 

Warranty labels match approved warranty data.


- 

Add to Cart uses the shared cart engine.


- 

Buy on WhatsApp uses the shared message generator.


- 

Mobile layouts remain responsive.


- 

No duplicated product cards.


- 

No Explore Free Tool CTA remains.


- 

Existing 40 products remain functional.



# PHASE 4 — Product Detail Pages
SEO + conversion architecture

All 25 products require their own high-quality, unique detail pages.


The purpose is not simply to create 25 nearly identical landing pages.


Each page must answer the customer's real questions:

- 

What exactly is this product?


- 

What can it do?


- 

Which plan is being offered?


- 

What will the customer receive?


- 

How long will access last?


- 

What is the price in Pakistan?


- 

What are the access restrictions?


- 

What does the warranty cover?


- 

How does WhatsApp ordering work?



## 4.1 URL architecture


Preserve the existing URL structure where possible.


| Product | Canonical URL |
| --- | --- |
| Bolt.new | /tools/bolt-new/ |
| Coursera Plus | /tools/coursera-plus/ |
| Descript | /tools/descript/ |
| Firecrawl | /tools/firecrawl/ |
| InVideo AI | /tools/invideo-ai/ |
| Make.com | /tools/make/ |
| Manus AI | /tools/manus-ai/ |
| Opus Clip | /tools/opus-clip/ |
| Qwen | /tools/qwen/ |
| Udemy Personal | /tools/udemy-personal/ |
| v0 | /tools/v0/ |
| Windsurf | /tools/windsurf/ |
| Ahrefs | /tools/ahrefs/ |
| ChatPRD | /tools/chatprd/ |
| DaVinci Resolve Studio | /tools/davinci-resolve/ |
| Domo AI | /tools/domo-ai/ |
| Genspark | /tools/genspark/ |
| Hailuo AI | /tools/hailuo-ai/ |
| Higgsfield AI | /tools/higgsfield/ |
| Morphic | /tools/morphic/ |
| NotebookLM | /tools/notebooklm/ |
| Quizlet Plus | /tools/quizlet/ |
| Railway | /tools/railway/ |
| Skillshare Premium | /tools/skillshare/ |
| Supabase Pro | /tools/supabase/ |



Do not rename an established URL without a documented migration and appropriate redirect.


## 4.2 Required page architecture


Every page must contain:

- 

Breadcrumb navigation.


- 

Product identity.


- 

Unique H1.


- 

Pakistan-focused commercial introduction.


- 

Product description.


- 

Pricing section.


- 

Package details.


- 

Quick specifications.


- 

Features.


- 

Customer use cases.


- 

Access and activation instructions.


- 

Warranty terms.


- 

WhatsApp checkout.


- 

Add to Cart.


- 

Four unique FAQs.


- 

Related products.


- 

Trust and support information.


- 

Product schema.


- 

Offer schema.


- 

Breadcrumb schema.


- 

FAQ schema where appropriate.


- 

Correct canonical.


- 

Meta description.


- 

Internal links.



## 4.3 Detail-page HTML template
HTML

```

<!DOCTYPE html>
<html lang="en-PK">

<head>
  <meta charset="UTF-8">

  <meta
    name="viewport"
    content="width=device-width, initial-scale=1"
  >

  <title>
    PRODUCT_NAME Price in Pakistan | AI Tool Gems
  </title>

  <meta
    name="description"
    content="Discover PRODUCT_NAME pricing in Pakistan, verified package details, authorized access options and assisted WhatsApp ordering from AI Tool Gems."
  >

  <link
    rel="canonical"
    href="https://aitoolgems.tech/tools/PRODUCT_SLUG/"
  >

</head>

<body>

  <main class="product-detail-page">

    <nav aria-label="Breadcrumb">
      <a href="/">Home</a>
      <span>/</span>
      <a href="/tools/">AI Tools</a>
      <span>/</span>
      <span aria-current="page">
        PRODUCT_NAME
      </span>
    </nav>

    <section class="product-hero">

      <div class="product-identity">

        <span class="product-category">
          CATEGORY_NAME
        </span>

        <h1>
          PRODUCT_NAME Price in Pakistan
        </h1>

        <p class="product-introduction">
          UNIQUE_PRODUCT_INTRODUCTION
        </p>

      </div>

      <div class="product-purchase-panel">

        <h2>Available Package</h2>

        <div class="product-price">
          <span>Price</span>

          <strong data-product-price>
            PKR —
          </strong>
        </div>

        <div class="product-package-details">

          <p>
            Duration:
            <strong data-product-duration>
              Verification pending
            </strong>
          </p>

          <p>
            Access:
            <strong data-product-access>
              Verification pending
            </strong>
          </p>

          <p>
            Replacement:
            <strong data-product-warranty>
              Verification pending
            </strong>
          </p>

        </div>

        <button
          type="button"
          data-buy-product="PRODUCT_SLUG"
          disabled
        >
          Buy on WhatsApp
        </button>

        <button
          type="button"
          data-add-to-cart="PRODUCT_SLUG"
          disabled
        >
          Add to Cart
        </button>

      </div>

    </section>

    <section class="product-description">

      <h2>What Is PRODUCT_NAME?</h2>

      <p>UNIQUE_PRODUCT_DESCRIPTION</p>

      <h2>Key Features</h2>

      <ul>
        <li>VERIFIED_FEATURE_1</li>
        <li>VERIFIED_FEATURE_2</li>
        <li>VERIFIED_FEATURE_3</li>
        <li>VERIFIED_FEATURE_4</li>
      </ul>

      <h2>Who Should Use PRODUCT_NAME?</h2>

      <p>UNIQUE_CUSTOMER_USE_CASES</p>

      <h2>Package and Access Details</h2>

      <p>VERIFIED_PACKAGE_DETAILS</p>

      <h2>How to Order in Pakistan</h2>

      <ol>
        <li>Select the approved package.</li>
        <li>Click Buy on WhatsApp.</li>
        <li>Confirm availability and final price.</li>
        <li>Complete payment using an available method.</li>
        <li>Receive the confirmed delivery instructions.</li>
      </ol>

      <h2>Replacement Warranty</h2>

      <p>APPROVED_WARRANTY_TERMS</p>

    </section>

    <section class="product-specifications">

      <h2>Quick Specifications</h2>

      <table>
        <tbody>
          <tr>
            <th>Product</th>
            <td>PRODUCT_NAME</td>
          </tr>

          <tr>
            <th>Category</th>
            <td>CATEGORY_NAME</td>
          </tr>

          <tr>
            <th>Currency</th>
            <td>PKR</td>
          </tr>

          <tr>
            <th>Duration</th>
            <td>VERIFIED_DURATION</td>
          </tr>

          <tr>
            <th>Access Type</th>
            <td>VERIFIED_ACCESS</td>
          </tr>

          <tr>
            <th>Warranty</th>
            <td>VERIFIED_WARRANTY</td>
          </tr>

          <tr>
            <th>Fulfillment</th>
            <td>VERIFIED_FULFILLMENT</td>
          </tr>
        </tbody>
      </table>

    </section>

    <section class="product-faq">

      <h2>Frequently Asked Questions</h2>

      UNIQUE_FOUR_FAQS

    </section>

    <section class="related-products">

      <h2>Related AI Tools</h2>

      RELATED_PRODUCT_CARDS

    </section>

  </main>

</body>
</html>

```



## 4.4 Content quality requirements


Each product page must contain approximately 300–500 words of genuinely useful, original product-specific content.


Do not count repeated navigation, button labels, schema text or boilerplate warranty language toward this target.


Recommended content allocation:


| Section | Approximate words |
| --- | --- |
| Introduction | 40–60 |
| What the product does | 60–80 |
| Main features | 60–90 |
| Pakistan customer use cases | 50–70 |
| Package and access explanation | 40–60 |
| Ordering and support | 30–50 |
| Total | 280–410 |



The final page should reach the 300–500-word target without filler.


### Product-specific content requirements


The pages must not be generated by replacing only the product name in one generic template.


Examples:

- 

Bolt.new: explain AI-assisted application development, prompting, project generation and deployment workflow.


- 

Coursera Plus: explain eligible learning access, course discovery and professional education.


- 

Descript: explain text-based editing, transcription and audio/video workflows.


- 

Firecrawl: explain crawling, structured web data and developer integrations.


- 

InVideo AI: explain script-to-video workflows and generation allowances.


- 

Make.com: explain visual automation, scenarios, integrations and operations.


- 

Manus AI: explain agentic task execution, research and task-credit limitations.


- 

Opus Clip: explain long-form video repurposing and clipping workflows.


- 

Qwen: distinguish the exact model or API package being supplied.


- 

Udemy Personal: explain membership eligibility and included learning content.


- 

v0: explain UI generation and the exact plan's usage allowances.


- 

Windsurf: explain AI-assisted coding, IDE workflow and model usage.


- 

Ahrefs: explain SEO research, keyword data, backlink analysis and plan limitations.


- 

ChatPRD: explain product documentation and PRD workflows.


- 

DaVinci Resolve Studio: explain the actual license and included professional features.


- 

Domo AI: explain supported AI video and visual transformations.


- 

Genspark: explain AI search, research and generated workspace features.


- 

Hailuo AI: explain video generation, credits and output restrictions.


- 

Higgsfield: explain cinematic generation and available creative workflows.


- 

Morphic: explain the specific current AI search and generative offering.


- 

NotebookLM: explain source-grounded research and Audio Overviews, with exact access eligibility.


- 

Quizlet Plus: explain study sets, flashcards and verified premium features.


- 

Railway: explain cloud deployment, resource usage and billing limitations.


- 

Skillshare: explain creative education and eligible membership access.


- 

Supabase: explain database, authentication, storage and Pro organization billing.



## 4.5 Four-FAQ requirement


Every page needs four unique FAQs.


The FAQs must be specific to the actual commercial offering.


For example, Bolt.new:

- 

What is included in the Bolt.new package?


- 

How long does Bolt.new access last?


- 

Does the package include additional usage credits?


- 

How can customers order Bolt.new in Pakistan?



For Ahrefs:

- 

Which Ahrefs plan is included?


- 

How many users or seats are supported?


- 

Are keyword and backlink research limits included?


- 

What happens if the subscription access stops working?



For Railway:

- 

What Railway resources are included?


- 

Does the package cover usage-based billing?


- 

Who controls the Railway project and organization?


- 

How are additional usage charges handled?



Do not publish FAQ answers that imply features, allowances or warranty coverage that have not been verified.


## 4.6 Product and Offer JSON-LD


The schema must be generated from approved catalog data.


Example:
JSON

```

{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Bolt.new",
  "description": "AI-assisted full-stack web development service. Package specifications and access conditions are subject to the verified offering.",
  "brand": {
    "@type": "Brand",
    "name": "StackBlitz"
  },
  "category": "Development Software",
  "url": "https://aitoolgems.tech/tools/bolt-new/",
  "offers": {
    "@type": "Offer",
    "url": "https://aitoolgems.tech/tools/bolt-new/",
    "priceCurrency": "PKR",
    "price": "APPROVED_NUMERIC_PRICE",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition",
    "seller": {
      "@type": "Organization",
      "name": "AI Tool Gems",
      "url": "https://aitoolgems.tech/"
    }
  }
}

```



APPROVED_NUMERIC_PRICE is a build-time placeholder, not valid production JSON-LD.


The production generator must output a valid numeric value.


### Schema safeguards

- 

Never output an Offer for an unapproved price.


- 

Never output InStock when fulfillment is unavailable.


- 

Use OutOfStock or omit the Offer when appropriate.


- 

Do not fabricate an AggregateRating.


- 

Do not fabricate Review objects.


- 

Do not invent product identifiers or GTINs.


- 

The seller must be AI Tool Gems, not the original software vendor.


- 

Do not imply official vendor affiliation without evidence.



### AggregateRating and Review


These are conditional.


Only include:
JSON

```
{
  "@type": "AggregateRating",
  "ratingValue": "4.8",
  "reviewCount": "25"
}
```



when the values are based on genuine, documented reviews that are eligible for the relevant structured data.


Do not create five-star ratings simply because a page requires an AggregateRating field.


The same rule applies to individual Review objects.


### BreadcrumbList


Use:
JSON

```
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
      "name": "Bolt.new",
      "item": "https://aitoolgems.tech/tools/bolt-new/"
    }
  ]
}
```



### FAQPage


The FAQPage schema may be generated for genuine visible FAQs.


However, Google generally restricts FAQ rich results to authoritative government and health websites. Do not forecast FAQ rich-result eligibility for this commercial marketplace.


The FAQ content must remain visible on the page and match the structured data exactly.


## 4.7 Technical SEO requirements


Every product page must have:

- 

Unique title tag.


- 

Unique meta description.


- 

Self-referencing canonical.


- 

One primary H1.


- 

Logical H2/H3 hierarchy.


- 

Descriptive image alt attributes.


- 

Internal links to related tools.


- 

Links to category pages.


- 

Links to pricing and policies where appropriate.


- 

Crawlable HTML content.


- 

Mobile-friendly layout.


- 

Correct HTTP status.


- 

No accidental noindex.


- 

No duplicate canonical.


- 

No broken resources.



Do not make a page indexable solely because a directory record has become an ASSISTED record.


Commercial readiness, content quality and indexing approval must remain separate decisions.


# PHASE 5 — Master Catalog Directory: tools/index.html


## 5.1 Objective


The master catalog must become a commercial product directory.


It must no longer communicate that these 25 products are merely informational profiles.


Update the interface from:


| Old field | New field |
| --- | --- |
| Directory Profile | Commercial Product |
| Directory | Assisted |
| Explore Free Tool | View Product / Buy Now |
| External vendor link | Internal product detail page |
| No price | Verified PKR package price |
| Informational details | Commercial specifications |
| No cart action | Add to Cart |
| External discovery | Assisted ordering |



## 5.2 Required catalog columns


| Column | Description |
| --- | --- |
| Product | Name and brand |
| Category | Canonical category |
| Model | ASSISTED |
| Package | Verified package name |
| Duration | Actual package duration |
| Access | Verified access type |
| Price | Approved PKR price |
| Warranty | Approved 7/30-day warranty |
| Availability | Verified status |
| Action | Product detail / Buy Now |



Do not show every column on mobile. Use responsive cards or a horizontally scrollable table.


## 5.3 Catalog row template
HTML

```

<tr
  data-product-id="bolt-new"
  data-model="ASSISTED"
>
  <td>
    <a href="/tools/bolt-new/">
      Bolt.new
    </a>
  </td>

  <td>Development</td>

  <td>
    <span class="model-badge">
      Assisted
    </span>
  </td>

  <td data-package="bolt-new">
    Verified package
  </td>

  <td data-duration="bolt-new">
    Verified duration
  </td>

  <td data-access="bolt-new">
    Verified access
  </td>

  <td data-price="bolt-new">
    PKR —
  </td>

  <td data-warranty="bolt-new">
    Verified coverage
  </td>

  <td data-availability="bolt-new">
    Verification pending
  </td>

  <td>
    <a href="/tools/bolt-new/">
      View Product
    </a>

    <button
      data-add-to-cart="bolt-new"
      disabled
    >
      Add to Cart
    </button>
  </td>
</tr>

```



## 5.4 Catalog consistency


The master catalog must be generated from the same product registry as the homepage.


Recommended function:
JavaScript

```
function getSellableCatalog(products) {
  return products.filter(product =>
    product.model === "ASSISTED"
  );
}
```



For the final target:
JavaScript

```
const sellableProducts =
  getSellableCatalog(PRODUCTS);

console.assert(
  sellableProducts.length === 65,
  "Expected 65 ASSISTED products"
);

console.assert(
  PRODUCTS.every(
    product => product.model === "ASSISTED"
  ),
  "DIRECTORY products must not remain"
);
```



The second assertion is valid only after the actual catalog baseline has been reconciled and every legacy profile has been handled.


## 5.5 Important distinction: catalog versus availability


The master directory may list all 65 products, even if an individual package is temporarily unavailable.


However:

- 

The availability label must be truthful.


- 

The purchase CTA must respect the activation guard.


- 

A temporary outage must not erase the product.


- 

A permanently discontinued offering must undergo a separate content and URL decision.



# PHASE 6 — Automated Test Suites & Regression Contracts
Release-blocking quality gates

This phase is essential.


A catalog conversion that passes visual inspection but breaks the cart, WhatsApp checkout or existing 40 products is a failed migration.


## 6.1 Required test files


The following are the target test contracts. Inspect existing test conventions before introducing new files.


| Test file | Responsibility |
| --- | --- |
| tests/test_visible_directory_and_catalogue_completeness.py | Directory elimination and catalog visibility |
| tests/test_cart_and_pricing_integrity.py | Cart calculations and approved pricing |
| tests/test_catalogue_consistency.py | Data consistency across all catalog surfaces |
| tests/test_whatsapp_checkout.py | WhatsApp message and checkout behavior |
| tests/test_product_detail_pages.py | 65 detail pages and metadata |
| tests/test_product_schema.py | Product and Offer JSON-LD |
| tests/test_commercial_readiness.py | Supplier, price and warranty gates |
| tests/test_category_filters.py | Search and category filtering |
| tests/test_sitemap_integrity.py | Sitemap and canonical URLs |
| tests/test_internal_link_graph.py | Internal links and orphan detection |
| tests/test_existing_products_regression.py | Existing 40 products |
| tests/test_mobile_product_cards.py | Responsive UI contracts |



## 6.2 Catalog completeness test


Example:
Pythonimport jsonimport unittestfrom pathlib import Pathclass TestCatalogueCompleteness(unittest.TestCase):    @classmethod    def setUpClass(cls):        cls.catalog_path = Path("data/catalog.json")        with cls.catalog_path.open(            encoding="utf-8"        ) as file:            cls.products = json.load(file)    def test_total_product_count(self):        self.assertEqual(            len(self.products),            65        )    def test_no_directory_products(self):        directory_products = [            product            for product in self.products            if product.get("model") == "DIRECTORY"        ]        self.assertEqual(            directory_products,            []        )    def test_all_products_are_assisted(self):

Adapt the file path and product representation to the actual repository. Do not create data/catalog.json as an independent duplicate catalog if app.js is the canonical source.


## 6.3 Pricing integrity test
Pythonimport unittestdef is_valid_approved_product(product):    commercial = product.get("commercial", {})    warranty = product.get("warranty", {})    fulfillment = product.get("fulfillment", {})    commerce = product.get("commerce", {})    price = commercial.get("price")    return all([        product.get("model") == "ASSISTED",        commercial.get("status") == "APPROVED",        isinstance(price, (int, float)),        not isinstance(price, bool),        price > 0,        commercial.get("priceVerified") is True,        commercial.get("supplierVerified") is True,        commercial.get("authorizationVerified") is True,        commercial.get("ownerApproved") is True,        commercial.get("durationLabel"),        commercial.get("accessType"),        warranty.get("approved") is True,        warranty.get("days") in (7, 30),        fulfillment.get("availability") == "AVAILABLE",        commerce.get("purchasable") is True    ])class TestPricingIntegrity(unittest.TestCase):    def test_unverified_price_cannot_be_purchased(self):        product = {

Production tests must additionally reject:

- 

Negative prices.


- 

NaN.


- 

Infinity.


- 

String prices.


- 

Boolean prices.


- 

Expired quotations.


- 

Missing package durations.


- 

Unsupported access types.


- 

Invalid warranties.


- 

Missing supplier authorization.


- 

Unavailable inventory.



## 6.4 WhatsApp checkout tests


Test the following:

- 

Product-specific message generation.


- 

Correct product ID.


- 

Correct product name.


- 

Correct package.


- 

Correct duration.


- 

Correct price.


- 

Correct warranty.


- 

Correct quantity.


- 

Correct product URL.


- 

Correct WhatsApp business number.


- 

URL encoding.


- 

Unavailable product rejection.


- 

Invalid cart item rejection.


- 

Multiple products in one message.


- 

Correct subtotal.



Example:
JavaScript

```
const message = generateProductWhatsAppMessage(
  approvedBoltProduct,
  2
);

console.assert(message.includes("Bolt.new"));

console.assert(message.includes("PKR"));

console.assert(message.includes("Quantity: 2"));

console.assert(
  message.includes("/tools/bolt-new/")
);
```



Do not test only whether a WhatsApp link exists.


Test the generated message contents.


## 6.5 Catalog consistency test


All surfaces must agree:


| Field | app.js | Homepage | Detail page | Master catalog | Cart | WhatsApp |
| --- | --- | --- | --- | --- | --- | --- |
| Product name | Required | Match | Match | Match | Match | Match |
| Product ID | Required | Match | Match | Match | Match | Match |
| Price | Required | Match | Match | Match | Match | Match |
| Duration | Required | Match | Match | Match | Match | Match |
| Access | Required | Match | Match | Match | Match | Match |
| Warranty | Required | Match | Match | Match | Match | Match |
| Availability | Required | Match | Match | Match | Match | Match |



Use automated assertions to detect discrepancies.


## 6.6 Detail-page test


For each of the 25 slugs:
Pythonfrom pathlib import Pathimport unittestSLUGS = [    "bolt-new",    "coursera-plus",    "descript",    "firecrawl",    "invideo-ai",    "make",    "manus-ai",    "opus-clip",    "qwen",    "udemy-personal",    "v0",    "windsurf",    "ahrefs",    "chatprd",    "davinci-resolve",    "domo-ai",    "genspark",    "hailuo-ai",    "higgsfield",    "morphic",    "notebooklm",    "quizlet",    "railway",    "skillshare",    "supabase"]class TestProductDetailPages(unittest.TestCase):    def test_all_detail_pages_exist(self):

Also validate:

- 

Unique title.


- 

Unique H1.


- 

Canonical.


- 

Correct breadcrumb.


- 

Exactly four visible primary FAQs.


- 

Valid JSON-LD.


- 

No placeholder price.


- 

No accidental empty schema.


- 

No missing internal links.


- 

No duplicate page content.



## 6.7 Schema validation


Use a JSON parser to extract every JSON-LD block.


Test:

- 

Valid JSON.


- 

Valid @context.


- 

Correct Product type.


- 

Correct product name.


- 

Correct URL.


- 

Correct Offer currency.


- 

Numeric price.


- 

Accurate availability.


- 

Valid seller.


- 

Accurate BreadcrumbList.


- 

FAQ content matches the visible page.



For the 25 pages, require Product schema only where the actual offering is a genuine product or qualifying commercial offer. Do not use a Product type merely to force a software service into an inaccurate representation.


Use Google's Rich Results Test and Schema.org Validator during QA.


## 6.8 Regression protection for the original 40 products


This is a release-critical requirement.


The implementation must verify that:

- 

All 40 existing products remain.


- 

Their existing IDs are preserved.


- 

Their existing detail URLs are preserved.


- 

Their prices do not change unexpectedly.


- 

Their cart behavior remains functional.


- 

Their WhatsApp messages remain correct.


- 

Their categories remain valid.


- 

Their Product schema remains valid.


- 

Their canonical URLs remain correct.


- 

Their existing warranties remain unchanged unless separately approved.



Create a baseline comparison:
Plain textreports/sellable-tools/
    baseline_inventory.json
    before_catalog_snapshot.json
    after_catalog_snapshot.json
    catalog_diff.json
    regression_results.json

Any unexpected change to the original 40 products must block release.


## 6.9 Required CI execution


Run the repository's existing tests first, then the new tests.


Example:
Bash

```
python -m unittest discover -s tests -v
```



If the project uses pytest:
Bash

```
pytest -q
```



Run JavaScript validation using the existing project's supported runtime and lint configuration.


Also execute:

- 

HTML validation.


- 

JSON validation.


- 

Broken-link checks.


- 

Mobile UI checks.


- 

Cart tests.


- 

WhatsApp tests.


- 

Schema validation.


- 

Sitemap validation.


- 

Internal-link checks.



Do not introduce a new dependency merely to duplicate an existing validator.


## 6.10 Final regression gate


Release-blocking conditions

- 65 unique catalog products.

- 65 products classified as ASSISTED.

- Zero DIRECTORY records.

- Zero duplicate IDs.

- 25 migration pages present.

- All 40 previous products preserved.

- No invalid product prices.

- No unauthorized fulfillment packages.

- No fake reviews or ratings.

- Cart and WhatsApp tests pass.

- Product schema passes validation.

- Sitemap contains only approved URLs.

- No unintended 404s or broken links.


# PHASE 7 — Sitemaps, Internal Link Graphs, Robots, IndexNow and GSC
Technical SEO release

This phase ensures that the commercial conversion is reflected correctly throughout search-engine discovery and crawling.


Important: 65 products does not automatically mean 65 indexable URLs.


Every page must independently satisfy the site's content quality, canonical, indexing and commercial accuracy requirements.


## 7.1 Sitemap architecture


First inspect the existing sitemap generation process.


Do not replace an existing sitemap architecture blindly.


Recommended structure, if the existing inventory justifies separate files:
Plain text/sitemap.xml
/sitemaps/
    sitemap-static.xml
    sitemap-products.xml
    sitemap-categories.xml
    sitemap-guides.xml
    sitemap-blog.xml

The sitemap index must reference only real, accessible sitemap files.


For the 25 converted products:
Plain texthttps://aitoolgems.tech/tools/bolt-new/
https://aitoolgems.tech/tools/coursera-plus/
https://aitoolgems.tech/tools/descript/
https://aitoolgems.tech/tools/firecrawl/
https://aitoolgems.tech/tools/invideo-ai/
https://aitoolgems.tech/tools/make/
https://aitoolgems.tech/tools/manus-ai/
https://aitoolgems.tech/tools/opus-clip/
https://aitoolgems.tech/tools/qwen/
https://aitoolgems.tech/tools/udemy-personal/
https://aitoolgems.tech/tools/v0/
https://aitoolgems.tech/tools/windsurf/
https://aitoolgems.tech/tools/ahrefs/
https://aitoolgems.tech/tools/chatprd/
https://aitoolgems.tech/tools/davinci-resolve/
https://aitoolgems.tech/tools/domo-ai/
https://aitoolgems.tech/tools/genspark/
https://aitoolgems.tech/tools/hailuo-ai/
https://aitoolgems.tech/tools/higgsfield/
https://aitoolgems.tech/tools/morphic/
https://aitoolgems.tech/tools/notebooklm/
https://aitoolgems.tech/tools/quizlet/
https://aitoolgems.tech/tools/railway/
https://aitoolgems.tech/tools/skillshare/
https://aitoolgems.tech/tools/supabase/

Only add a URL after its indexing approval.


## 7.2 Sitemap generation rules


For each sitemap entry:

- 

Absolute canonical URL.


- 

HTTP 200 response.


- 

Indexable page.


- 

No noindex.


- 

No redirect.


- 

No canonical pointing elsewhere.


- 

No duplicate URL.


- 

No private or administrative page.


- 

Accurate lastmod.



Use lastmod to represent the actual significant modification date.


Do not update every URL's lastmod on every build.


Do not use priority or changefreq as if they were Google ranking controls.


## 7.3 robots.txt


Inspect the current file before making changes.


Do not block important CSS, JavaScript or product assets required to render pages.


A typical structure is:
Plain text
User-agent: *
Allow: /

Sitemap: https://aitoolgems.tech/sitemap.xml


This is an illustrative baseline, not an instruction to overwrite existing production directives.


If private administrative paths exist, protect them through authentication and access control.


robots.txt is not a security mechanism.


A blocked URL can still be discovered and potentially appear in search results without a useful snippet.


For private pages, use proper authorization controls and appropriate noindex handling on accessible responses.


## 7.4 IndexNow


IndexNow can notify participating search engines about changed URLs.


Use it only after:

- 

A page has been published.


- 

The page returns HTTP 200.


- 

Its canonical is correct.


- 

The page is intended to be indexable.


- 

The content has passed quality review.



Create a dedicated submission process:
Plain textPUBLISHED
    |
    v
HTTP 200 VERIFIED
    |
    v
CANONICAL VERIFIED
    |
    v
INDEXABILITY VERIFIED
    |
    v
INDEXNOW SUBMISSION
    |
    v
SUBMISSION LOGGED

Example payload structure:
JSON

```
{
  "host": "aitoolgems.tech",
  "key": "INDEXNOW_KEY",
  "keyLocation": "https://aitoolgems.tech/INDEXNOW_KEY.txt",
  "urlList": [
    "https://aitoolgems.tech/tools/bolt-new/"
  ]
}
```



The key must be genuine, securely generated and hosted according to IndexNow requirements.


Never commit a private API key to a public repository.


Do not interpret an IndexNow acceptance response as confirmation that Google indexed the page.


IndexNow is not a substitute for Google Search Console sitemap submission.


## 7.5 Internal link graph


The 25 products must become discoverable through meaningful internal links.


Recommended graph:
Plain textHomepage
   |
   +---- Development Category
   |         |
   |         +---- Bolt.new
   |         +---- Firecrawl
   |         +---- v0
   |         +---- Windsurf
   |         +---- Railway
   |         +---- Supabase
   |
   +---- Education Category
   |         |
   |         +---- Coursera Plus
   |         +---- Udemy Personal
   |         +---- Quizlet Plus
   |         +---- Skillshare
   |
   +---- Video & Audio Category
   |         |
   |         +---- Descript
   |         +---- InVideo AI
   |         +---- Opus Clip
   |         +---- DaVinci Resolve
   |         +---- Domo AI
   |         +---- Hailuo AI
   |         +---- Higgsfield
   |
   +---- AI Assistants Category
   |         |
   |         +---- Manus AI
   |         +---- Qwen
   |         +---- Genspark
   |         +---- Morphic
   |
   +---- Productivity Category
   |         |
   |         +---- Make.com
   |         +---- ChatPRD
   |         +---- NotebookLM
   |
   +---- SEO & Marketing Category
             |
             +---- Ahrefs

The remaining products must be linked through their correct categories.


### Required internal-link sources

- 

Homepage.


- 

Master catalog.


- 

Relevant category pages.


- 

Related product sections.


- 

Relevant blog articles.


- 

Comparison pages.


- 

Relevant guides.


- 

Breadcrumb navigation.



Avoid irrelevant cross-linking simply to increase link counts.


### Link graph QA


The audit must detect:

- 

Orphan product pages.


- 

Broken internal links.


- 

Redirect chains.


- 

Links to removed /jp/ URLs.


- 

Incorrect category URLs.


- 

Duplicate anchors.


- 

Links to private pages.


- 

Links to noindex pages.


- 

Incorrect product slugs.


- 

Homepage cards linking to external vendors instead of the internal product pages.



The objective is to create a useful discovery graph, not maximize the raw number of links.


## 7.6 Google Search Console workflow


Property:


sc-domain:aitoolgems.tech


The implementation must separate submission from verification.


Recommended workflow:


Step 1 — Publish approved pages


Confirm the deployed HTML is accessible.


Step 2 — Inspect representative URLs


Use URL Inspection for:

- 

One development product.


- 

One education product.


- 

One video product.


- 

One productivity product.


- 

One usage-based product.


- 

One existing ASSISTED product.



Step 3 — Submit the sitemap


Submit the updated sitemap index through Google Search Console.


Step 4 — Request indexing


Request indexing for selected high-priority URLs after verifying the rendered content.


Do not blindly request indexing for all 65 pages repeatedly.


Step 5 — Monitor indexing reports


Track:

- 

Indexed.


- 

Crawled — currently not indexed.


- 

Discovered — currently not indexed.


- 

Duplicate without user-selected canonical.


- 

Alternate page with proper canonical.


- 

Excluded by noindex.


- 

Soft 404.


- 

Not found (404).


- 

Server errors.


- 

Redirect issues.



Step 6 — Inspect actual causes


For each problem URL, investigate:

- 

Page content.


- 

Internal links.


- 

Canonical.


- 

Robots directives.


- 

HTTP response.


- 

Rendering.


- 

Duplicate content.


- 

Crawl frequency.


- 

Discovery source.



Do not treat all unindexed pages as a sitemap problem.


## 7.7 Google Merchant Center implications


The conversion also affects Merchant Center.


Do not assume that every digital software subscription is eligible for Shopping ads or free listings.


Before adding converted products to a feed, verify:

- 

Product eligibility.


- 

Digital goods and software policy requirements.


- 

Accurate product identity.


- 

Accurate availability.


- 

Accurate price.


- 

Business identity and contact information.


- 

Checkout consistency.


- 

Payment transparency.


- 

Refund and replacement policy.


- 

Landing-page compliance.



Do not add all 25 products automatically to the Merchant Center feed.


The feed must contain only eligible, policy-compliant products.


## 7.8 AEO and GEO implications


The product pages should provide clear, factual answers that can be understood by search engines and AI assistants.


Include:

- 

Exact product name.


- 

Vendor identity.


- 

Product category.


- 

What the software does.


- 

Who it is useful for.


- 

Exact package sold by AI Tool Gems.


- 

Verified PKR price.


- 

Duration.


- 

Access arrangement.


- 

Included usage.


- 

Warranty.


- 

Fulfillment conditions.



Keep the distinction between:


Official software capabilities and the package AI Tool Gems actually supplies.


This prevents misleading product descriptions and helps search systems understand the commercial offer.


# PHASE 8 — Commercial Operations, Fulfillment and Warranty


This phase is necessary because the conversion creates 25 new commercial obligations.


## 8.1 Order lifecycle
Plain textCUSTOMER VISITS PRODUCT PAGE
          |
          v
SELECTS PACKAGE
          |
          v
ADDS TO CART / WHATSAPP
          |
          v
ORDER DETAILS CONFIRMED
          |
          v
AVAILABILITY VERIFIED
          |
          v
PAYMENT INSTRUCTIONS SENT
          |
          v
PAYMENT VERIFIED
          |
          v
FULFILLMENT AUTHORIZED
          |
          v
ACCESS DELIVERED
          |
          v
CUSTOMER CONFIRMATION
          |
          v
WARRANTY PERIOD TRACKING

## 8.2 Required order fields


Each order should internally record:
JSON

```
{
  "order_id": "ORDER_REFERENCE",
  "product_id": "bolt-new",
  "package_id": "APPROVED_PACKAGE",
  "quantity": 1,
  "unit_price_pkr": 0,
  "subtotal_pkr": 0,
  "currency": "PKR",
  "customer_contact": null,
  "payment_method": null,
  "payment_status": "PENDING",
  "fulfillment_status": "PENDING",
  "delivery_timestamp": null,
  "warranty_days": null,
  "warranty_expiry": null
}
```



The zero amounts above are illustrative defaults and must never be accepted as a valid commercial order.


## 8.3 Delivery claims


Do not apply one universal delivery promise to all 65 products.


Different products may require:

- 

A license activation.


- 

A team invitation.


- 

Account setup.


- 

Credit allocation.


- 

Vendor approval.


- 

Manual configuration.



The product page must display an accurate fulfillment estimate.


If the actual operating model supports a 5–15-minute WhatsApp delivery estimate for a particular product, it can be displayed after operational verification.


Do not advertise 24/7 delivery as guaranteed if the relevant supplier, team or automated fulfillment process is not available 24/7.


## 8.4 Warranty tracking


Store:

- 

Order reference.


- 

Product.


- 

Package.


- 

Delivery timestamp.


- 

Warranty duration.


- 

Warranty expiry.


- 

Replacement count.


- 

Support case reference.


- 

Resolution.


- 

Evidence.



Calculate:
Warranty Expiry=Delivery Timestamp+Approved Warranty Duration\text{Warranty Expiry}
=
\text{Delivery Timestamp}
+
\text{Approved Warranty Duration}Warranty Expiry=Delivery Timestamp+Approved Warranty Duration

The warranty clock should start when access has actually been delivered, not when the customer merely submits an order.


## 8.5 Customer-facing trust information


Each product detail page should clearly disclose:

- 

AI Tool Gems is the seller of the described package.


- 

The software provider is the original product vendor.


- 

Whether the package is a subscription, license or credit allocation.


- 

What access method the customer receives.


- 

Duration.


- 

Included usage.


- 

Renewal conditions.


- 

Replacement warranty.


- 

Refund and cancellation terms.


- 

Payment methods.


- 

Customer support channel.



Do not imply that AI Tool Gems is officially affiliated with a vendor unless that relationship is verified.


# PHASE 9 — Security, Data Integrity and Performance


## 9.1 Price security


Client-side prices are for display only.


Never trust:

- 

Local storage prices.


- 

URL query parameters.


- 

Hidden HTML fields.


- 

User-submitted totals.


- 

Browser-generated discount amounts.



The authoritative amount must be recalculated from the canonical approved catalog when processing an order.


If the site remains a static WhatsApp-based marketplace, the final human order confirmation must independently verify the price before payment.


## 9.2 WhatsApp security

- 

Encode messages correctly.


- 

Do not place API credentials in the frontend.


- 

Do not expose supplier acquisition prices.


- 

Do not send account passwords in generated messages.


- 

Validate product IDs.


- 

Validate quantities.


- 

Validate price status.


- 

Prevent injection through product descriptions.


- 

Use the official configured WhatsApp business number.



## 9.3 Performance


The new cards and detail pages must not introduce unnecessary performance regressions.


Check:

- 

Largest Contentful Paint.


- 

Interaction to Next Paint.


- 

Cumulative Layout Shift.


- 

Image dimensions.


- 

Responsive image delivery.


- 

Font loading.


- 

JavaScript execution.


- 

Unnecessary third-party scripts.


- 

Duplicate event listeners.


- 

Cart initialization overhead.



Avoid loading all 65 full product-detail descriptions into the homepage if only the card data is required.


Use a compact catalog representation for listing pages.


## 9.4 Accessibility


Every new component must support:

- 

Keyboard navigation.


- 

Accessible button names.


- 

Proper heading structure.


- 

Form labels.


- 

Visible focus indicators.


- 

Sufficient contrast.


- 

Screen-reader-friendly cart updates.


- 

Clear disabled-state explanations.



A disabled purchase button must communicate why the product cannot currently be purchased.


# PHASE 10 — Controlled Implementation and Deployment Strategy
No direct production deployment without approval

The implementation should be executed in small, independently verifiable stages.


Do not convert 25 products, rewrite the catalog, replace the homepage, modify all detail pages and deploy everything in one uncontrolled operation.


## 10.1 Recommended implementation sequence


| Stage | Work | Required result |
| --- | --- | --- |
| 0 | Repository forensics | Verified baseline |
| 1 | Supplier and commercial research | 25 approved commercial records |
| 2 | Catalog schema | One canonical product model |
| 3 | Global catalog migration | 65 ASSISTED records |
| 4 | Cart and WhatsApp integration | Working checkout |
| 5 | Homepage migration | 65 consistent product cards |
| 6 | Detail pages | 25 unique commercial pages |
| 7 | Master catalog | 65 consistent records |
| 8 | Automated testing | All release contracts pass |
| 9 | SEO and indexing | Approved URLs and correct sitemaps |
| 10 | Staging QA | Verified customer journey |
| 11 | Owner approval | Written release authorization |
| 12 | Production deployment | Controlled release |
| 13 | Monitoring | Post-release verification |



## 10.2 Suggested implementation waves


Divide the 25 products into five waves.


Wave 1 — Development infrastructure
5 products
- 

Bolt.new


- 

Firecrawl


- 

v0


- 

Windsurf


- 

Railway



Wave 2 — Education
4 products
- 

Coursera Plus


- 

Udemy Personal


- 

Quizlet Plus


- 

Skillshare Premium



Wave 3 — Video and creative
7 products
- 

Descript


- 

InVideo AI


- 

Opus Clip


- 

DaVinci Resolve Studio


- 

Domo AI


- 

Hailuo AI


- 

Higgsfield AI



Wave 4 — AI and productivity
6 products
- 

Make.com


- 

Manus AI


- 

Qwen


- 

Genspark


- 

Morphic


- 

NotebookLM



Wave 5 — SEO, product and backend
3 products
- 

Ahrefs


- 

ChatPRD


- 

Supabase Pro



These waves are implementation groupings, not assumptions that the products in a particular group are commercially ready.


## 10.3 Wave acceptance gate


A wave cannot advance until:

- All product identities match the migration manifest.

- Supplier arrangements are verified.

- Selling prices are approved.

- Duration and usage limits are confirmed.

- Access arrangements are compliant.

- Warranties are approved.

- Detail pages are complete.

- Product cards are correct.

- Cart integration passes.

- WhatsApp messages pass.

- Structured data is valid.

- Internal links are correct.

- Existing products remain unaffected.

- Owner approval is recorded.


## 10.4 Git workflow


Protect the main branch.


Recommended:
Bash

```
git checkout main

git pull --ff-only origin main

git checkout -b feature/sellable-tools-conversion
```



Keep implementation commits organized:
Plain textfeat: add commercial migration manifest
feat: introduce canonical assisted product schema
feat: migrate 25 directory catalog records
feat: integrate commercial checkout guards
feat: update homepage product cards
feat: create 25 product detail pages
feat: update master catalog directory
test: add commercial readiness contracts
test: add cart and WhatsApp regression coverage
feat: update approved product sitemap
docs: document commercial fulfillment requirements

Before merging:
Bash

```
git status --short
git diff --check
git diff --stat
```



Run all required tests and review the complete diff.


Do not push, merge or deploy without the relevant authorization.


## 10.5 Rollback strategy


Keep a known-good baseline commit.


If a release introduces:

- 

Incorrect prices.


- 

Broken cart behavior.


- 

Missing product pages.


- 

Broken WhatsApp checkout.


- 

Invalid schema.


- 

Unexpected indexing changes.


- 

Existing product regressions.



Immediately disable the affected commercial package or roll back the release.


Do not delete product records to solve temporary supplier or pricing problems.


A rollback must restore the previous functioning customer journey, not merely restore the previous visual design.


# PHASE 11 — Post-Deployment Verification and Monitoring


## 11.1 First 24 hours


Check:


| Area | Verification |
| --- | --- |
| Homepage | All expected cards render |
| Catalog | 65 unique products |
| Directory records | Zero |
| Detail pages | All intended URLs return 200 |
| Cart | Product quantities and subtotals correct |
| WhatsApp | Correct messages and product URLs |
| Pricing | Approved values match every surface |
| Mobile | No layout overflow |
| Schema | No invalid JSON-LD |
| Canonicals | Correct self-referencing URLs |
| Robots | No accidental crawling restrictions |
| Sitemap | Correct approved URL inventory |
| Analytics | Existing tracking still works |



## 11.2 First seven days


Monitor:

- 

Product-page impressions.


- 

Product-page clicks.


- 

Search queries.


- 

Organic CTR.


- 

Search positions.


- 

WhatsApp CTA clicks.


- 

Add-to-cart events.


- 

Cart abandonment.


- 

Completed orders.


- 

Fulfillment success rate.


- 

Warranty claims.


- 

Pricing discrepancies.


- 

Customer questions.



Separate technical metrics from commercial metrics.


An increase in impressions is not proof of successful sales conversion.


## 11.3 First 30 days


Produce a report:


reports/sellable-tools/post-deployment-30-day-report.md


Required sections:

- 

Final product inventory.


- 

Commercial readiness.


- 

Approved price inventory.


- 

Page indexing status.


- 

Search performance.


- 

Product-page CTR.


- 

WhatsApp conversion.


- 

Cart conversion.


- 

Revenue.


- 

Gross margin.


- 

Fulfillment success.


- 

Warranty claims.


- 

Technical errors.


- 

SEO issues.


- 

Recommended next improvements.



Use real analytics and order data. Never fill missing figures with estimates presented as measured results.


# PHASE 12 — Final Master Acceptance Criteria


This is the final definition of done.


## 12.1 Catalog acceptance


| Requirement | Target |
| --- | --- |
| Total catalog products | 65 |
| ASSISTED products | 65 |
| DIRECTORY products | 0 |
| Duplicate product IDs | 0 |
| Missing product identities | 0 |
| Missing approved product URLs | 0 |



## 12.2 Commercial acceptance


| Requirement | Target |
| --- | --- |
| Supplier verification | 65/65 |
| Authorization verification | 65/65 |
| Approved pricing | 65/65 |
| Verified duration | 65/65 |
| Verified access type | 65/65 |
| Approved warranty | 65/65 |
| Fulfillment readiness | 65/65 |
| Purchasable product validation | 65/65 |



These targets refer to the final fully activated commercial catalog. A product still undergoing supplier research must remain unavailable for purchase.


## 12.3 UI acceptance


| Requirement | Target |
| --- | --- |
| Homepage product cards | 65 |
| Product detail pages | 65 |
| Master catalog records | 65 |
| Cart-integrated products | 65 |
| WhatsApp-integrated products | 65 |
| Remaining directory CTAs | 0 |
| Broken internal product links | 0 |



## 12.4 SEO acceptance


| Requirement | Target |
| --- | --- |
| Correct canonical URLs | 100% |
| Valid indexable page metadata | 100% of approved pages |
| Valid Product/Offer schema | 100% of eligible approved offers |
| Duplicate product IDs | 0 |
| Orphan product pages | 0 |
| Broken product links | 0 |
| Accidental noindex on approved pages | 0 |
| Unapproved pages in sitemap | 0 |



Do not use 100% indexing as a release criterion. Google independently determines whether to index pages.


## 12.5 Regression acceptance

- Existing 40 products preserved.

- Existing product prices preserved unless separately approved.

- Existing cart behavior preserved.

- Existing WhatsApp behavior preserved.

- Existing category filters preserved.

- Existing analytics preserved.

- Existing consent configuration preserved.

- Existing robots rules reviewed.

- Existing sitemap architecture preserved where appropriate.

- No unexpected production redirects.

- No unintended deletion of staged pages.

- No changes to private/admin security controls.


# PHASE 13 — Antigravity Execution Instructions


This section is the implementation contract for the coding agent.


The agent must execute the plan as an engineering migration, not as a bulk content-generation exercise.


## 13.1 Master execution prompt


Use the following instructions when providing this document to Antigravity.
Writing

# ANTIGRAVITY MASTER EXECUTION CONTRACT


## AI Tool Gems — 25 Directory-to-Assisted Commercial Conversion


You are the Senior Software Architect, Technical SEO Engineer, E-Commerce Systems Engineer and QA Lead responsible for implementing SELLABLE_TOOLS_CONVERSION_PLAN.md.


Repository:https://github.com/m-rehman55/ai-tool-gems


Target branch:main


Target:

- 

65 total products.


- 

65 ASSISTED

ChatGPT can make mistakes. Check important info.

#### Latest response