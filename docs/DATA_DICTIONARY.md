# HERMES DATA DICTIONARY & SCHEMA DEFINITIONS
**System**: AI Tool Gems Data Architecture  

---

## 1. Core Data Entities

### 1.1 Tool Product Entity (`data/products/`)
| Field | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `id` | String | Unique kebab-case tool identifier | `chatgpt` |
| `name` | String | Commercial product name | `ChatGPT Plus` |
| `category` | String | Tool functional category | `ai-chatbots` |
| `price_pkr` | Integer | Flat monthly rate in PKR | `2300` |
| `price_usd` | Integer | Reference rate in USD | `10` |
| `access_type` | Enum | Delivery format | `shared`, `private`, `invitation`, `license_key` |
| `payment_rails` | Array[String]| Supported local methods | `["EasyPaisa", "JazzCash", "SadaPay", "Bank IBFT"]` |
| `warranty_days`| Integer | Replacement warranty duration | `7` |
| `official_url` | String | Vendor official website | `https://chatgpt.com` |
| `canonical_url`| String | On-site canonical URL | `https://aitoolgems.tech/tools/chatgpt/` |

---

### 1.2 URL State Machine Record (`data/seo/url_inventory.json`)
Every URL on the website is tracked across lifecycle states:
$$\text{DISCOVERED} \to \text{CRAWLED} \to \text{ANALYZED} \to \text{FIX\_REQUIRED} \to \text{APPROVED} \to \text{DEPLOYED} \to \text{VERIFIED}$$

| Field | Type | Description |
| :--- | :--- | :--- |
| `url` | String | Canonical URL with trailing slash |
| `status_code` | Integer | HTTP response status (200, 301, 404) |
| `title` | String | Document title tag |
| `meta_description`| String | Meta description content |
| `h1` | String | Primary H1 heading text |
| `word_count` | Integer | Body copy word count |
| `indexable` | Boolean | True if robots meta is index, follow and 200 OK |
| `in_sitemap` | Boolean | Present in sitemap.xml |
| `last_crawled` | ISO-8601 | Timestamp of latest crawl |
| `gsc_clicks_7d` | Integer | Recorded 7-day organic search clicks |
| `gsc_impressions_7d`| Integer | Recorded 7-day search impressions |
| `gsc_avg_position` | Float | Average ranking position |

---

### 1.3 Keyword Cluster Record (`data/seo/keyword-map.json`)
| Field | Type | Description |
| :--- | :--- | :--- |
| `cluster_id` | String | Cluster slug name |
| `target_url` | String | Canonical page assigned to cluster |
| `primary_keyword` | String | Main organic ranking keyword |
| `intent` | Enum | `TRANSACTIONAL_PKR`, `COMMERCIAL`, `INFORMATIONAL`, `COMPARISON` |
| `secondary_keywords`| Array[String]| Related supporting search queries |
| `monthly_volume_pk`| Integer | Measured or estimated Pakistan search volume |
| `serp_competitors` | Array[String]| Competing domains ranking for the cluster |

