# AI Crawler & Search Engine Robots Policy Verification Report
**File:** `robots.txt`  
**Date:** 2026-11-07  
**Verification Method:** `urllib.robotparser.RobotFileParser` automated test harness  
**Status:** **100% VERIFIED & COMPLIANT**  

---

## 1. Executive Summary & Policy Objectives

The `robots.txt` configuration was updated and verified to enforce a modern, nuanced crawling policy:
1. **Permit Search Engines & Real-Time AI Citation Bots:** Allow traditional search engine crawlers (Google, Bing) and AI search agents (OpenAI SearchBot, ChatGPT User browsing, Claude SearchBot, Perplexity) to crawl public content for real-time indexing, retrieval-augmented generation (RAG), and citation grounding.
2. **Block Bulk AI Training Scrapers:** Block crawlers whose primary purpose is ingesting website content to train generative model weights without search attribution (`GPTBot`, `ClaudeBot`, `Google-Extended`).
3. **Protect Internal & Operational Directories:** Prohibit all web and AI crawlers from accessing private or administrative paths (`/admin.html`, `/data/`, `/reports/`, `/scratch/`, `/scripts/`, `/tests/`, `/marketing_agent/`, `/hermes_core/`, `/seo-agent/`, `/.env*`).

---

## 2. Configured Robot Directives

```robots
# ==============================================================================
# AIToolGems robots.txt - Search Central & AI Agent Indexing Policy
# Canonical: https://aitoolgems.tech/robots.txt
# Primary Market: Pakistan | Growth Market: Worldwide / International
# ==============================================================================

# 1. Default Rules for General Web Crawlers
User-agent: *
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

# 2. Search Engine Crawlers (Google & Bing)
User-agent: Googlebot
User-agent: bingbot
User-agent: msnbot
User-agent: BingPreview
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

# 3. AI Search & Live Answer Engine Bots (Allowed for Real-Time Grounding & Citation)
User-agent: OAI-SearchBot
User-agent: ChatGPT-User
User-agent: Claude-SearchBot
User-agent: Claude-User
User-agent: PerplexityBot
User-agent: Perplexity-User
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

# 4. AI Training & Bulk Model Ingestion Bots (Disallowed / Blocked)
User-agent: GPTBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: Google-Extended
Disallow: /

# 5. Sitemaps & Context Feeds
Sitemap: https://aitoolgems.tech/sitemap.xml
```

---

## 3. Empirical Verification Results

A programmatic audit using Python's `urllib.robotparser.RobotFileParser` verified access permissions across 20 test combinations:

| User-Agent | Target URL | Expected Permission | Verified Result |
|---|---|---|---|
| `Googlebot` | `https://aitoolgems.tech/` | **ALLOW** | ✅ PASS |
| `Googlebot` | `https://aitoolgems.tech/tools/chatgpt/` | **ALLOW** | ✅ PASS |
| `Googlebot` | `https://aitoolgems.tech/admin.html` | **DISALLOW** | ✅ PASS |
| `Googlebot` | `https://aitoolgems.tech/data/test.json` | **DISALLOW** | ✅ PASS |
| `bingbot` | `https://aitoolgems.tech/` | **ALLOW** | ✅ PASS |
| `bingbot` | `https://aitoolgems.tech/admin.html` | **DISALLOW** | ✅ PASS |
| `OAI-SearchBot` | `https://aitoolgems.tech/tools/chatgpt/` | **ALLOW** | ✅ PASS |
| `OAI-SearchBot` | `https://aitoolgems.tech/admin.html` | **DISALLOW** | ✅ PASS |
| `ChatGPT-User` | `https://aitoolgems.tech/tools/chatgpt/` | **ALLOW** | ✅ PASS |
| `Claude-SearchBot`| `https://aitoolgems.tech/tools/chatgpt/` | **ALLOW** | ✅ PASS |
| `Claude-User` | `https://aitoolgems.tech/tools/chatgpt/` | **ALLOW** | ✅ PASS |
| `PerplexityBot` | `https://aitoolgems.tech/tools/chatgpt/` | **ALLOW** | ✅ PASS |
| `PerplexityBot` | `https://aitoolgems.tech/admin.html` | **DISALLOW** | ✅ PASS |
| `Perplexity-User`| `https://aitoolgems.tech/tools/chatgpt/` | **ALLOW** | ✅ PASS |
| `GPTBot` | `https://aitoolgems.tech/` | **DISALLOW** | ✅ PASS |
| `GPTBot` | `https://aitoolgems.tech/tools/chatgpt/` | **DISALLOW** | ✅ PASS |
| `ClaudeBot` | `https://aitoolgems.tech/` | **DISALLOW** | ✅ PASS |
| `ClaudeBot` | `https://aitoolgems.tech/tools/chatgpt/` | **DISALLOW** | ✅ PASS |
| `Google-Extended`| `https://aitoolgems.tech/` | **DISALLOW** | ✅ PASS |
| `Google-Extended`| `https://aitoolgems.tech/tools/chatgpt/` | **DISALLOW** | ✅ PASS |

All 20 test vectors passed with 100% adherence to policy specifications.
