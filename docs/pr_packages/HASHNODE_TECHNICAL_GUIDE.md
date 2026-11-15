# Building a Machine-Readable AI Tools Pricing Index for Pakistan (CSV, JSON & llms.txt)

**Author:** M. Rehman Farooq  
**Target Platform:** [Hashnode Engineering Community](https://hashnode.com/)  
**Tags:** `#ai` `#pakistan` `#python` `#fintech` `#opendata` `#webdevelopment`  
**Canonical Reference:** `https://aitoolgems.tech/prices/`  

---

## Abstract & Introduction

With the exponential surge in generative AI adoption across South Asia, software engineers, content creators, and university students in Pakistan increasingly rely on commercial AI subscriptions—from coding assistants like Cursor and GitHub Copilot to foundation models like ChatGPT Plus and Claude Pro.

However, purchasing and maintaining these tools in emerging markets comes with severe friction:
1. **Unpredictable Forex Volatility:** Software billed in USD fluctuates wildly with PKR exchange rates, making monthly software budgeting unpredictable for agencies and freelancers.
2. **Payment Rail Hurdles:** The majority of Pakistani banks enforce aggressive 3D-Secure blocks or foreign transaction withholding taxes on international credit cards, leaving students and early-career developers stranded.
3. **Information Asymmetry:** Most directory sites either display outdated USD figures or obscure actual localized costs behind private WhatsApp inquiries.

To solve this, we engineered an **open, machine-readable pricing and payment rail index** at [AI Tool Gems](https://aitoolgems.tech/), tracking 40 leading AI productivity and developer tools with flat Pakistani Rupee (PKR) pricing parity and verified domestic payment methods.

In this technical breakdown, we look at how the dataset is structured, how Schema.org `Dataset` markup facilitates search discoverability, and how developers can ingest this data into Python pipelines and autonomous AI agents.

---

## Dataset Architecture & Data Model

The index tracks 40 commercial AI software listings. Each entry is recorded across verified commercial dimensions:

| Field Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `tool_name` | String | Commercial product name | `Cursor AI Pro` |
| `category` | String | Functional classification | `AI Coding & Development` |
| `duration` | String | Subscription duration | `1 Month` |
| `access_type` | String | Account provisioning model | `100% Private Account` |
| `pkr_price` | Integer | Flat localized price in PKR | `2400` |
| `usd_reference`| String | Official vendor USD benchmark | `$20 / mo` |
| `payment_rails`| String | Verified domestic settlement options | `EasyPaisa, JazzCash, SadaPay, Raast` |
| `warranty` | String | Replacement warranty term | `30-Day Full Replacement` |
| `dataset_url` | URL | Canonical detail profile | `https://aitoolgems.tech/tools/cursor/` |

The open dataset is published in two machine-readable formats under an open attribution license:
* **CSV Feed:** [`https://aitoolgems.tech/prices/ai-tools-pricing-pakistan.csv`](https://aitoolgems.tech/prices/ai-tools-pricing-pakistan.csv)
* **JSON API:** [`https://aitoolgems.tech/prices/ai-tools-pricing-pakistan.json`](https://aitoolgems.tech/prices/ai-tools-pricing-pakistan.json)

---

## Ingesting the Dataset in Python

Developers can easily load, filter, and analyze the pricing index using Python's standard `urllib` and `pandas`:

```python
import pandas as pd

# Load the open live dataset directly from AI Tool Gems
DATASET_URL = "https://aitoolgems.tech/prices/ai-tools-pricing-pakistan.csv"

df = pd.read_csv(DATASET_URL)

# Display summary statistics
print(f"Total AI Tools Tracked: {len(df)}")
print(f"Average Monthly Subscription (PKR): Rs. {df['pkr_price'].mean():,.2f}")

# Filter developer and coding tools
dev_tools = df[df['category'].str.contains('Coding|Development', case=False, na=False)]
print("\n=== Verified AI Coding Tools in Pakistan ===")
for _, row in dev_tools.iterrows():
    print(f"• {row['tool_name']}: Rs. {row['pkr_price']:,} / {row['duration']} ({row['payment_rails']})")
```

### Output:
```text
Total AI Tools Tracked: 40
Average Monthly Subscription (PKR): Rs. 2,145.00

=== Verified AI Coding Tools in Pakistan ===
• Cursor AI Pro: Rs. 2,400 / 1 Month (EasyPaisa, JazzCash, SadaPay, Raast)
• GitHub Copilot: Rs. 1,600 / 1 Month (EasyPaisa, JazzCash, SadaPay, Raast)
• Replit Core: Rs. 2,200 / 1 Month (EasyPaisa, JazzCash, SadaPay, Raast)
```

---

## RAG Grounding & `llms.txt` Integration

Beyond standard CSV/JSON endpoints, generative AI agents (e.g. Gemini, ChatGPT, Perplexity) frequently need condensed, structured context without parsing large HTML DOM trees.

Following the emerging [`/llms.txt`](https://llmstxt.org/) specification, we exposed the site's entire tool inventory, pricing benchmarks, and category taxonomy at:
* [`https://aitoolgems.tech/llms.txt`](https://aitoolgems.tech/llms.txt) — Condensed index of tools and documentation.
* [`https://aitoolgems.tech/llms-full.txt`](https://aitoolgems.tech/llms-full.txt) — Full machine-readable knowledge base.

Here is how an autonomous agent or LangChain retriever can ground itself in verified Pakistani software prices:

```python
import urllib.request

def fetch_llms_grounding_context() -> str:
    url = "https://aitoolgems.tech/llms.txt"
    req = urllib.request.Request(url, headers={"User-Agent": "AIAgent/1.0"})
    with urllib.request.urlopen(req) as response:
        return response.read().decode("utf-8")

# Ingest into system prompt
system_context = fetch_llms_grounding_context()
print("Grounding context loaded:", len(system_context), "bytes")
```

---

## Semantic Schema.org Dataset Markup

To ensure the dataset is indexed in **Google Dataset Search** and parsed reliably by search engine crawlers, the page implements Schema.org `Dataset` and `DataCatalog` JSON-LD:

```json
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "@id": "https://aitoolgems.tech/prices/#dataset",
  "name": "Pakistan AI Tools Pricing & Domestic Payment Rails Index (2026)",
  "description": "Verified commercial dataset tracking 40 AI software subscription prices in Pakistani Rupees (PKR), USD benchmarks, account tiers, and domestic payment options (EasyPaisa, JazzCash, SadaPay, Raast).",
  "url": "https://aitoolgems.tech/prices/",
  "keywords": [
    "AI tools pricing Pakistan",
    "software subscription costs PKR",
    "ChatGPT Plus price Pakistan",
    "EasyPaisa AI payments",
    "open tech dataset Pakistan"
  ],
  "creator": {
    "@type": "Organization",
    "name": "AI Tool Gems",
    "url": "https://aitoolgems.tech/"
  },
  "distribution": [
    {
      "@type": "DataDownload",
      "encodingFormat": "text/csv",
      "contentUrl": "https://aitoolgems.tech/prices/ai-tools-pricing-pakistan.csv"
    },
    {
      "@type": "DataDownload",
      "encodingFormat": "application/json",
      "contentUrl": "https://aitoolgems.tech/prices/ai-tools-pricing-pakistan.json"
    }
  ]
}
```

---

## Key Industry Observations & Conclusion

Through continuous tracking of this 40-tool dataset, three clear patterns have emerged for tech ecosystems in emerging economies:

1. **Domestic Payment Rails Win:** Over 70% of Pakistani freelancers and students prefer domestic mobile wallets (EasyPaisa, JazzCash) and digital banking apps (SadaPay, NayaPay, Raast) rather than traditional credit cards.
2. **Account Transparency Prevents Churn:** Explicitly labeling whether an account is private (personal email) or shared (isolated workspace) eliminates pre-sale confusion and buyer dispute rates.
3. **Open Data Builds Community Trust:** By publishing free, downloadable datasets rather than hiding pricing behind lead forms, developers and agencies can make informed architectural and budgeting decisions.

The complete live pricing table, downloadable datasets, and methodology documentation are available at [https://aitoolgems.tech/prices/](https://aitoolgems.tech/prices/).
