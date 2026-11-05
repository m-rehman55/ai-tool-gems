# BLOCKED INTEGRATIONS & PENDING USER CREDENTIALS
**Status as of**: 2026-11-05  

The following integrations are currently in state `BLOCKED_PENDING_CREDENTIALS`. Their code adapters, data schemas, and fail-safe handling are implemented, but authenticated live execution requires credentials from the user:

---

## 1. Credentials Required to Unblock Integrations

### 1.1 Google PageSpeed Insights & CrUX API
- **Variable**: `PAGESPEED_API_KEY` (or Google Cloud API Key with PageSpeed Insights API enabled).
- **Purpose**: Live automated measurement of LCP, INP, CLS, and CrUX real-user field data across all 96 production pages.
- **Where to acquire**: Google Cloud Console $\to$ APIs & Services $\to$ Enable "PageSpeed Insights API" $\to$ Create API Key.

### 1.2 PostHog Behavioral Intelligence
- **Variables**: `POSTHOG_API_KEY`, `POSTHOG_HOST` (e.g., `https://us.i.posthog.com` or `https://eu.i.posthog.com`).
- **Purpose**: Client-side tracking of user paths, search queries, filter interactions, and WhatsApp order initiation funnels with privacy masking.
- **Where to acquire**: PostHog Dashboard $\to$ Project Settings $\to$ Project API Key.

### 1.3 GA4 Measurement Protocol Secret
- **Variable**: `GA4_API_SECRET`
- **Purpose**: Server-side reporting of confirmed, verified WhatsApp orders into GA4 as verified purchases with PKR revenue.
- **Where to acquire**: Google Analytics $\to$ Admin $\to$ Data Streams $\to$ Select Web Stream $\to$ Measurement Protocol API Secrets $\to$ Create.

### 1.4 Buffer API Key
- **Variable**: `BUFFER_API_KEY`
- **Purpose**: Local execution and testing of social deal publishing and rate-limit backoff.
- **Where to acquire**: Buffer Account $\to$ Settings $\to$ Apps & Access $\to$ API Keys.

### 1.5 Meta Graph API Token
- **Variable**: `META_ACCESS_TOKEN` (currently configured as empty in `.env`).
- **Purpose**: Facebook/Instagram organic engagement tracking and ad account metric ingestion.
- **Where to acquire**: Meta for Developers $\to$ Graph API Explorer $\to$ User/System User Token with `pages_read_engagement`.

### 1.6 Ahrefs / Semrush API Key
- **Variables**: `AHREFS_API_KEY` or `SEMRUSH_API_KEY`.
- **Purpose**: Live backlink profile tracking, referring domain growth, and competitor backlink gap matrix.
- **Where to acquire**: Ahrefs or Semrush Developer Portal.

