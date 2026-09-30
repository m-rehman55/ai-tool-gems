# SEO INTERNATIONAL

## Markets

| Market | Locale | Currency | Catalog | Sitemap |
|--------|--------|----------|---------|---------|
| Pakistan | en-PK | PKR | 20 products | sitemap.xml |
| Japan | ja-JP | JPY | 21 products | sitemap-jp.xml |

## hreflang

- en-PK ↔ ja-JP: reciprocal where URLs exist
- x-default: present on all 68 pages
- 9 broken targets returning 404

## HREFLANG Issues

1. Guide pages use wrong URL pattern (/guides/<name>/jp/ instead of /jp/guides/<name>/)
2. deals/ → /deals/jp/ (no JP deals page)
3. Manus JP-only with en-PK hreflang to non-existent /tools/manus/
4. Non-indexable pages have hreflang (unnecessary)

## Market Isolation

- PKR on JP pages: 0 ✅
- JPY on PK pages: "PKR/JPY" reference only (ambiguous) ⚠️
- Sitemaps properly separated ✅
- Canonicals locale-correct ✅

## Future Markets

Adding new markets requires code changes in 24 Python files. No market configuration system exists.

## Target Architecture

Configurable market system:
```json
{
  "en-PK": { "prefix": "", "currency": "PKR", "catalog": "..." },
  "ja-JP": { "prefix": "jp", "currency": "JPY", "catalog": "..." }
}
```
