# SEO SCHEMA

## Current Schema Implementation

### Product Pages (Pakistan)
- Product ✅ (Name, Description, Brand, SKU, Image, URL)
- Offer ✅ (Price, Currency in PKR, Availability, Seller, ShippingDetails, MerchantReturnPolicy)
- FAQPage ✅

### Merchant Listings Compliance (Resolved)
- `availability`: Fully specified across all 20 products (`LimitedAvailability`)
- `description`: Unique accurate descriptions across all 20 products
- `brand`: Explicit Brand objects for all tools (OpenAI, Google, Canva, Adobe, etc.)
- `shippingDetails`: Free instant digital delivery (`OfferShippingDetails`)
- `hasMerchantReturnPolicy`: 7-day replacement warranty in PK

### Other Pages
- BreadcrumbList: ✅ Complete across all tool and guide pages
- Organization: OnlineStore / Organization ✅
- WebSite: WebSite with SearchAction ✅
- ItemList: Clean canonical tool URLs ✅

## Schema Rules

- Structured data must represent visible page content
- Never fabricate
- Never mark hidden information as visible
- Validate schema
- Monitor errors
- Avoid unnecessary schema

## Recommended Schema by Page Type

| Page Type | Schema |
|-----------|--------|
| Homepage | Organization, WebSite |
| Product | Product, Offer |
| Comparison | ItemList |
| Guide | Article |
| FAQ page | FAQPage |
| Category | ItemList |
| Research | Article |
