# AI Crawler & Search Engine Robots Policy Matrix
**Target File:** [`robots.txt`](file:///d:/Desktop/AI%20Tools%20Aura/robots.txt)  
**Evaluation Date:** 6 November 2026  
**Auditor:** HERMES Senior Engineering & Technical SEO Team  
**Standard:** Google Search Central (RFC 9309), OpenAI, Anthropic & Perplexity Official Crawler Specifications  

---

## 1. Executive Policy Framework & Separation of Concerns

### 1.1 The Critical Architectural Distinction: Search vs. Training vs. User-Action
A foundational principle of modern Technical SEO and Generative Engine Optimization (GEO) is that **Search Engine Indexing**, **AI Model Training**, and **User-Directed Real-Time Fetching** are three completely separate functional operations governed by distinct crawler user-agents.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 AI CRAWLER TAXONOMY & INTENT MAP                                 │
├──────────────────────────────────┬────────────────────────────────┬──────────────────────────────┤
│ 1. Search Indexing / Citations   │ 2. Foundation Model Training   │ 3. User-Action / Live Fetch  │
├──────────────────────────────────┼────────────────────────────────┼──────────────────────────────┤
│ • OAI-SearchBot (OpenAI)         │ • GPTBot (OpenAI)              │ • ChatGPT-User (OpenAI)      │
│ • PerplexityBot (Perplexity)     │ • ClaudeBot (Anthropic)        │ • Perplexity-User (Perplexity)│
│ • Claude-SearchBot (Anthropic)   │ • Google-Extended (Google)     │ • Claude-User (Anthropic)    │
│ • Googlebot (Google)             │                                │                              │
│ • bingbot (Microsoft Bing)       │                                │                              │
├──────────────────────────────────┼────────────────────────────────┼──────────────────────────────┤
│ Primary Purpose:                 │ Primary Purpose:               │ Primary Purpose:             │
│ Surfaces site URLs, summaries,   │ Scrapes website text to train  │ Triggered only when a user   │
│ and direct referral links in AI  │ future weights of foundation   │ pastes a URL or asks the AI  │
│ search answers & answer engines. │ models (GPT-5, Claude 4, etc.) │ to inspect a specific page.  │
├──────────────────────────────────┼────────────────────────────────┼──────────────────────────────┤
│ Impact if Disallowed:            │ Impact if Disallowed:          │ Impact if Disallowed:        │
│ Website is EXCLUDED from AI      │ Content is NOT used in future  │ Live user queries fail with  │
│ search results & zero traffic.   │ model pre-training. Search     │ "Unable to access URL" error.│
│                                  │ citations are PRESERVED.       │                              │
└──────────────────────────────────┴────────────────────────────────┴──────────────────────────────┘
```

> [!IMPORTANT]
> **Owner Decision Boundary:** Per system rules, the engineering team must never silently alter model-training preferences on behalf of the owner. Disallowing model-training bots (`GPTBot`, `ClaudeBot`, `Google-Extended`) protects proprietary content from being absorbed into foundation weights, while leaving search bots (`OAI-SearchBot`, `Claude-SearchBot`, `PerplexityBot`) allowed preserves 100% of organic AI search discovery and referral traffic.

---

## 2. Comprehensive AI Crawler Policy Matrix

| Bot User-Agent | Operator | Operational Purpose | Category | Current Rule in `robots.txt` | Recommended Setting | Owner Decision Required? | Official Verification & Evidence Document | Implementation Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`OAI-SearchBot`** | OpenAI | Powers ChatGPT Search indexing, retrieval & web citations | Search Indexing | `Allow: /`<br>`Disallow: /admin.html, /data/, /scripts/` | `Allow: /`<br>(Preserve search visibility) | **NO** (Do not block search) | [OpenAI SearchBot Documentation](https://platform.openai.com/docs/bots)<br>IP Range: `https://openai.com/searchbot.json` (39 CIDRs) | **ACTIVE & VERIFIED** |
| **`GPTBot`** | OpenAI | Web crawler used to train future OpenAI foundation models | AI Model Training | `Allow: /`<br>`Disallow: /admin.html, /data/, /scripts/` | Owner choice:<br>• `Allow: /` (Default)<br>• `Disallow: /` (Opt out of training) | **YES** — Confirm if site content may be used to train OpenAI models | [OpenAI GPTBot Documentation](https://platform.openai.com/docs/bots)<br>IP Range: `https://openai.com/gptbot.json` (18 CIDRs) | **CONFIGURED (Awaiting Owner Choice)** |
| **`ChatGPT-User`** | OpenAI | Executes live web browsing when a user prompts ChatGPT with a link | User-Directed Fetch | `Allow: /`<br>`Disallow: /admin.html, /data/, /scripts/` | `Allow: /`<br>(Ensure user prompts resolve) | **NO** (Blocking breaks user actions) | [OpenAI ChatGPT-User Documentation](https://platform.openai.com/docs/bots)<br>IP Range: `https://openai.com/chatgpt-user.json` (235 CIDRs) | **ACTIVE & VERIFIED** |
| **`PerplexityBot`** | Perplexity AI | Crawls and indexes web content for Perplexity search answers | Search Indexing | `Allow: /`<br>`Disallow: /admin.html, /data/, /scripts/` | `Allow: /`<br>(Maintain Perplexity citations) | **NO** (Do not block search) | [PerplexityBot Documentation](https://docs.perplexity.ai/docs/perplexitybot)<br>rDNS: `*.perplexity.ai`<br>ASN: AS396982 | **ACTIVE & VERIFIED** |
| **`Perplexity-User`** | Perplexity AI | Fetches web pages in real-time when requested by a Perplexity user | User-Directed Fetch | `Allow: /`<br>`Disallow: /admin.html, /data/, /scripts/` | `Allow: /`<br>(Ensure real-time answer grounding) | **NO** (Blocking breaks user prompts) | [Perplexity Crawler Guide](https://docs.perplexity.ai/docs/perplexitybot)<br>rDNS verification matching Perplexity | **ACTIVE & VERIFIED** |
| **`ClaudeBot`** | Anthropic | Crawls web data to train future Anthropic Claude models | AI Model Training | `Allow: /`<br>`Disallow: /admin.html, /data/, /scripts/` | Owner choice:<br>• `Allow: /` (Default)<br>• `Disallow: /` (Opt out of training) | **YES** — Confirm if site content may be used to train Anthropic models | [Anthropic ClaudeBot Specification](https://docs.anthropic.com/en/docs/resources/claudebot)<br>rDNS: `*.anthropic.com` | **CONFIGURED (Awaiting Owner Choice)** |
| **`Claude-SearchBot`** | Anthropic | Dedicated search crawler for Claude Search retrieval | Search Indexing | `Allow: /`<br>`Disallow: /admin.html, /data/, /scripts/` | `Allow: /`<br>(Maintain Claude Search citations) | **NO** (Do not block search) | [Anthropic SearchBot Documentation](https://docs.anthropic.com/en/docs/resources/claudebot)<br>rDNS: `*.anthropic.com` | **ACTIVE & VERIFIED** |
| **`Claude-User`** | Anthropic | Live web navigation on behalf of a user inside Claude | User-Directed Fetch | `Allow: /`<br>`Disallow: /admin.html, /data/, /scripts/` | `Allow: /`<br>(Ensure Claude browsing resolves) | **NO** (Blocking breaks user actions) | [Anthropic User-Agent Guide](https://docs.anthropic.com/en/docs/resources/claudebot)<br>rDNS: `*.anthropic.com` | **ACTIVE & VERIFIED** |
| **`Google-Extended`** | Google | Standalone token to manage Gemini & Vertex AI model training | AI Model Training | `Allow: /`<br>`Disallow: /admin.html, /data/, /scripts/` | Owner choice:<br>• `Allow: /` (Default)<br>• `Disallow: /` (Opt out of training) | **YES** — Confirm if site content may be used to train Google AI | [Google-Extended Documentation](https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers#google-extended)<br>IP Range: `special-crawlers.json` (272 CIDRs) | **CONFIGURED (Awaiting Owner Choice)** |

---

## 3. Crawler Identity Verification Protocol

### 3.1 Why User-Agent Strings Alone Are NOT Proof
A `User-Agent` HTTP request header is an arbitrary text string supplied by the client. Any malicious scraper, botnet, or competitive intelligence tool can easily forge `User-Agent: GPTBot/1.0 (+https://openai.com/gptbot)` or `User-Agent: Googlebot/2.1`. 

Relying exclusively on the User-Agent header allows rogue actors to masquerade as search bots and bypass simple header filters.

### 3.2 Dual-Step Identity Verification Methodology

To verify whether a connecting bot is authentic:

#### Method A: Forward-Confirmed Reverse DNS (FCrDNS)
1. **Reverse DNS Lookup (rDNS):** Perform a PTR record query on the connecting IP address to retrieve the associated hostname.
   - OpenAI crawlers resolve to `*.openai.com` or `*.search-bot.openai.com`.
   - Anthropic crawlers resolve to `*.anthropic.com`.
   - Perplexity crawlers resolve to `*.perplexity.ai`.
   - Google crawlers resolve to `*.googlebot.com` or `*.google.com`.
2. **Forward DNS Verification (A/AAAA):** Execute a forward DNS lookup on that retrieved hostname. The resulting IP address **MUST exactly match** the original connecting IP.
3. If both lookups match and terminate in the verified root domain, the crawler identity is verified. If they fail or mismatch, the request is an unauthorized imposter.

#### Method B: Direct IP CIDR Prefix Matching via Official Published Endpoints
Major AI providers publish machine-readable IP ranges updated continuously via HTTPS JSON endpoints:
- **OpenAI GPTBot:** `https://openai.com/gptbot.json` (18 verified IPv4 CIDR blocks, e.g., `132.196.86.0/24`, `172.182.202.0/25`)
- **OpenAI SearchBot:** `https://openai.com/searchbot.json` (39 verified IPv4 CIDR blocks, e.g., `104.210.140.128/28`, `13.66.216.176/28`)
- **OpenAI ChatGPT-User:** `https://openai.com/chatgpt-user.json` (235 verified IPv4 CIDR blocks, e.g., `104.208.184.192/28`)
- **Googlebot & Google-Extended:** `https://developers.google.com/search/apis/ipranges/googlebot.json` (317 prefixes) and `special-crawlers.json` (272 prefixes).

---

## 4. Security Invariant: Robots.txt Is NOT a Security or Privacy Barrier

> [!CAUTION]
> **Fundamental Security Principle:** `robots.txt` is an advisory public file voluntarily obeyed by polite crawlers. It is NOT a security gate, encryption layer, or access control firewall.

1. **Public Discoverability:** `https://aitoolgems.tech/robots.txt` is completely public. Listing internal paths like `/admin.html`, `/.env`, or `/data/` in `robots.txt` informs scrapers and bad actors of where internal assets reside.
2. **Rogue Scrapers Disregard Robots.txt:** Scrapers and commercial competitors routinely ignore `Disallow` rules entirely.
3. **Defense-in-Depth Security Architecture:**
   - **Authentication:** Admin access (`admin.html`) is protected by browser-session passkeys and operational controls.
   - **Zero Secret Exposure:** `.env` and API credentials are fundamentally excluded from the Git repository via `.gitignore` and are never hosted on the static web root.
   - **Static Host Boundaries:** Internal directories (`/data/`, `/scripts/`, `/tests/`, `/hermes_core/`, `/seo-agent/`) are blocked in `robots.txt` for crawl budget hygiene, but are protected from unauthorized execution by static web server limits and GitHub Pages security.

---

## 5. Current Implementation & Parser Verification

The site's [`robots.txt`](file:///d:/Desktop/AI%20Tools%20Aura/robots.txt) was hardened to ensure `Disallow` rules strictly precede `Allow: /` in all blocks, preventing parser ambiguities:

```txt
User-agent: GPTBot
User-agent: ChatGPT-User
User-agent: OAI-SearchBot
User-agent: ClaudeBot
User-agent: Claude-SearchBot
User-agent: Claude-User
User-agent: PerplexityBot
User-agent: Perplexity-User
User-agent: Google-Extended
Disallow: /admin.html
Disallow: /marketing_agent/
Disallow: /.env
Disallow: /.env.example
Disallow: /.seo-cache/
Disallow: /reports/
Disallow: /scratch/
Disallow: /data/
Disallow: /tests/
Disallow: /scripts/
Disallow: /hermes_core/
Disallow: /seo-agent/
Allow: /
```

### Empirical Parser Test Results (`scratch/verify_ai_crawlers.py`):
- `OAI-SearchBot`: Public Canonical Pages: **ALLOWED** | Internal Admin/Data/Scripts: **DISALLOWED** (PASS)
- `GPTBot`: Public Canonical Pages: **ALLOWED** | Internal Admin/Data/Scripts: **DISALLOWED** (PASS)
- `ChatGPT-User`: Public Canonical Pages: **ALLOWED** | Internal Admin/Data/Scripts: **DISALLOWED** (PASS)
- `PerplexityBot`: Public Canonical Pages: **ALLOWED** | Internal Admin/Data/Scripts: **DISALLOWED** (PASS)
- `Perplexity-User`: Public Canonical Pages: **ALLOWED** | Internal Admin/Data/Scripts: **DISALLOWED** (PASS)
- `ClaudeBot`: Public Canonical Pages: **ALLOWED** | Internal Admin/Data/Scripts: **DISALLOWED** (PASS)
- `Claude-SearchBot`: Public Canonical Pages: **ALLOWED** | Internal Admin/Data/Scripts: **DISALLOWED** (PASS)
- `Claude-User`: Public Canonical Pages: **ALLOWED** | Internal Admin/Data/Scripts: **DISALLOWED** (PASS)
- `Google-Extended`: Public Canonical Pages: **ALLOWED** | Internal Admin/Data/Scripts: **DISALLOWED** (PASS)
