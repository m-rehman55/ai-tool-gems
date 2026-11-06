# Master Catalogue and Supplier Data Quality Review (Phase 2)

**Execution Date:** 6 November 2026  
**Auditor:** HERMES Senior Engineering & Inventory Governance Suite  
**Data Sources:**
- `data/suppliers/reseller_products_master.csv` (2,902 raw supplier rows, 15 supplier bots)
- `AIToolGems_175_Tool_Register_v2_1.csv` & `AIToolGems_SEO_AEO_GEO_Master_Register_v2_1.xlsx` (175 canonical parents)
- Live repository audit (`tools/*/index.html`, `sitemap.xml`)

---

## 1. Revalidation of Baseline Facts (6 November 2026)

Every baseline observation from the Master Workbook v2.1 has been strictly revalidated against empirical datasets:

| Metric / Baseline Observation | Reported Baseline | Revalidated Fact | Verification Status | Empirical Evidence / Root Cause |
|---|---|---|---|---|
| **Canonical Parent Tools** | 175 | **175** | **MATCH 100%** | Seeded in Register v2.1 and Register v2.2 (`CAT-001` to `CAT-175`). |
| **Raw Supplier Rows** | 2,902 | **2,902** | **MATCH 100%** | Confirmed by direct CSV row parsing of `reseller_products_master.csv`. |
| **Unique Listing-Name Strings** | 1,619 | **1,619** | **MATCH 100%** | Exactly 1,619 distinct raw string identifiers across supplier feeds. |
| **Supplier Bots in CSV** | 15 | **15** | **MATCH 100%** | Identified 15 Telegram reseller bots (AI Toolify, Bunnytools, Fat bunny, etc.). |
| **Catalogue Categories** | 13 | **13** | **MATCH 100%** | 13 distinct category taxonomies mapped. |
| **Existing Tool Directories** | 40 | **40** | **MATCH 100%** | 40 physical tool subdirectories located in `tools/`. |
| **Mapped Parent Pages in GSC Map** | 39 | **39** | **MATCH 100%** | 39 tool slugs mapped to live landing pages (`/tools/<slug>/`). |
| **Category URLs in Sitemap** | 0 | **0** | **MATCH 100%** | Zero `/category/` routes indexed; briefs prepared to prevent thin hubs. |
| **Generic Use-Case Descriptions** | 149 / 175 | **149 / 175** | **MATCH 100%** | 149 parent rows in legacy sheets shared identical generic boilerplate. |

---

## 2. Inventory & Stock Interpretation (Demystifying the "223,494" Myth)

A critical mathematical and operational audit was conducted on supplier stock quantities:

### Inventory Distribution Breakdown
- **Strict Numeric Stock Rows:** **`2,688 rows`** (92.6% of supplier inventory).
- **Strict Numeric Stock Units:** **`126,591 units`** in total across all valid numeric entries.
- **Strict Numeric Zero-Stock Rows:** **`645 rows`** (22.2% of all supplier listings have 0 stock).
- **Sentinel `999 (Invite)` Rows:** **`97 rows`** contain the literal text `999 (Invite)`.
- **Text-Only `In Stock` Rows:** **`117 rows`** contain unquantified text `In Stock`.
- **Zero-Priced Rows ($0.00 / USDT 0.0):** **`126 rows`** lack wholesale pricing.
- **Missing Product IDs:** **`126 rows`** have empty product ID identifiers.
- **Missing Descriptions:** **`93 rows`** contain no description text.

### Mathematical Proof of the 223,494 Headline
$$\text{Reconstructed Sum} = 126,591 + (97 \times 999) = 223,494$$

> [!CAUTION]
> **Operational Stock Invalidation Rule:**
> 1. Under no circumstances may `223,494` be published, advertised, or included in schema as available customer inventory.
> 2. `999 (Invite)` is a database sentinel denoting invite-link delivery; it represents zero guaranteed physical units.
> 3. Supplier `Status = Live` does **not** equal order fulfillability. Reseller bots frequently leave abandoned or out-of-stock SKUs marked as "Live".
> 4. `645` supplier rows are strictly zero stock and must never be exposed to customer order flows.

---

## 3. Duplicate Supplier Listings & Cross-Bot Price Arbitrage

Cross-supplier analysis revealed massive redundancy and pricing conflict across the 15 bots:

- **Total Unique Product Names:** 1,619
- **Product Names duplicated across multiple bots:** **737 names** (45.5% of the unique catalog).
- **Total supplier rows involved in duplication:** **2,020 rows** (69.6% of the raw database).

### Extreme Price & Warranty Conflicts on Identical SKUs

| SKU / Product Name | Duplicate Count | Bots Selling | Wholesale Price Range (USDT) | Warranty Discrepancies |
|---|---|---|---|---|
| **API Cursor Pro 6500 Credits 1 mo** | 6 | 6 bots | **$11.77 – $14.13** (+20.0% variance) | "Full warranty" vs "12H warranty" vs "3D warranty" |
| **Apple ID 2FA Gmail** | 7 | 7 bots | **$1.34 – $2.25** (+67.9% variance) | Instant replacement vs no replacement |
| **Zoom Pro 28 Days full warranty** | 7 | 7 bots | **$1.72 – $3.01** (+75.0% variance) | 28 days vs 14 days replacement |
| **Akool Starter 200 cre 1 month** | 6 | 6 bots | **$4.38 – $6.10** (+39.3% variance) | 12-hour warranty vs 30-day warranty |
| **Adobe Full App 4-month package** | 5 | 5 bots | **$26.84 – $53.32** (+98.6% variance) | 2-month warranty vs 4-month warranty |

### Matching & Governance Rules Enforced:
1. **Never auto-approve fuzzy matches:** Parent-to-SKU associations require strict SKU normalization.
2. **Access Model Separation:** Reseller access mechanisms (Shared cookie, Edu invite link, Private login, Token API) must remain explicitly separate from consumer brand editions.
3. **Quarantine Unresolved Offers:** All supplier offers remain in **`HOLD`** until manual procurement verification is conducted.
4. **Safety Block on High-Risk Items:** High-risk supplier products (`CAT-158` to `CAT-175`: phone OTPs, aged accounts, virtual numbers) are permanently classified as **`BLOCKED`**.

