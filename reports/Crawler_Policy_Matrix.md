# AI Crawler & Search Engine Robots Policy Matrix
**Target File:** `robots.txt`  
**Evaluation Date:** 6 November 2026  
**Policy Standard:** Google Search Central & Major LLM Provider Crawler Specifications  

---

## Crawler Permissions & Policy Matrix

| Crawler User-Agent | Operator | Purpose | Search vs Training | Current Setting | Recommended Setting | Owner Action Required | Status |
|---|---|---|---|---|---|---|---|
| `Googlebot` | Google | Core Google Search indexing | Search Indexing | **Allow: /** | **Allow: /** | None | **Active** |
| `Google-Extended` | Google | Gemini & Vertex AI model training | AI Training | **Allow: /** | Allow or Disallow (Owner choice) | Owner to confirm if Google AI training is permitted | **Configured** |
| `bingbot` / `msnbot` | Microsoft | Bing Search & Copilot indexing | Search Indexing | **Allow: /** | **Allow: /** | None | **Active** |
| `OAI-SearchBot` | OpenAI | ChatGPT Search live search citations | Search Indexing | **Allow: /** | **Allow: /** | None | **Active** |
| `ChatGPT-User` | OpenAI | User-directed live browsing requests in ChatGPT | Real-Time Fetch | **Allow: /** | **Allow: /** | None | **Active** |
| `GPTBot` | OpenAI | OpenAI foundation model training crawler | AI Training | **Allow: /** | Allow or Disallow (Owner choice) | Owner to confirm if OpenAI training is permitted | **Configured** |
| `PerplexityBot` | Perplexity AI | Perplexity index & training | Search & AI | **Allow: /** | **Allow: /** | None | **Active** |
| `Perplexity-User` | Perplexity AI | Live citation fetching during user prompt | Real-Time Fetch | **Allow: /** | **Allow: /** | None | **Active** |
| `ClaudeBot` | Anthropic | Anthropic training data collection | AI Training | **Allow: /** | Allow or Disallow (Owner choice) | Owner to confirm if Anthropic training is permitted | **Configured** |
| `Claude-SearchBot` | Anthropic | Claude Search & direct citation retrieval | Search Indexing | **Allow: /** | **Allow: /** | None | **Active** |
| `Claude-User` | Anthropic | Live web navigation on behalf of Claude user | Real-Time Fetch | **Allow: /** | **Allow: /** | None | **Active** |

---

## Disallowed Admin & Private Paths (All Bots)
- `/admin.html`
- `/marketing_agent/`
- `/.env`
- `/.env.example`
- `/.seo-cache/`
- `/reports/`
- `/scratch/`
