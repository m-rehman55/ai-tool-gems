# INTEGRATION CAPABILITY MATRIX
**Standard**: Official Documentation, Scopes, and Empirical Authentication Checks  
**Status Key**:
- `CONNECTED`: Authenticated and functional.
- `CONFIGURED_PENDING_VERIFICATION`: Credential exists in `.env` / Secrets; needs live call test.
- `BLOCKED_PENDING_CREDENTIALS`: Adapter implemented or designed; awaiting API keys from user.
- `NOT_SUPPORTED`: Feature not exposed by vendor API.

---

| Provider / Tool | Capability | API Available | Credential Configured | Auth Type | Required Scopes / Keys | Current Health Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Google Search Console** | Search Performance (Clicks/Impressions/CTR/Position) | Yes | Yes (`GSC_CLIENT_ID`, `GSC_CLIENT_SECRET`, `GSC_REFRESH_TOKEN`) | OAuth 2.0 Refresh Token | `webmasters.readonly` | `CONFIGURED_PENDING_VERIFICATION` |
| **Google Search Console** | URL Inspection API | Yes | Yes (Using same OAuth client) | OAuth 2.0 | `webmasters.readonly` | `CONFIGURED_PENDING_VERIFICATION` |
| **Google Search Console** | Sitemap Submissions & Status | Yes | Yes | OAuth 2.0 | `webmasters.readonly` | `CONFIGURED_PENDING_VERIFICATION` |
| **Google Search Console** | Temporary URL Removal API | Restricted | No | Service Account / OAuth | Removal API requires specific webmaster permissions | `BLOCKED_PENDING_CREDENTIALS` |
| **Google Analytics 4** | Session & Event Analytics (Traffic/Funnel) | Yes | Yes (`GA4_PROPERTY_ID`) | Service Account / OAuth | `analytics.readonly` | `CONFIGURED_PENDING_VERIFICATION` |
| **Google Analytics 4** | Measurement Protocol (Server-side Purchases) | Yes | No (`GA4_API_SECRET` missing) | API Secret | Measurement Protocol Secret | `BLOCKED_PENDING_CREDENTIALS` |
| **Bing Webmaster Tools** | CRAWL Stats, Query Clicks, Impressions | Yes | Yes (`BING_API_KEY`) | API Key | Bing Webmaster API Key | `CONFIGURED_PENDING_VERIFICATION` |
| **IndexNow Protocol** | Instant URL Submission (Bing, Yandex, Seznam) | Yes | Yes (Key `e1a8c47f9d2b4f30a6c8116de5b97042` hosted at root) | HTTP POST with Key Location | None | `CONNECTED` |
| **Google PageSpeed Insights** | Lighthouse Lab Performance Audit (Mobile & Desktop) | Yes | Public (Can use `PAGESPEED_API_KEY` or rate-limited free tier) | Query Parameter API Key | Google Cloud PSI API enabled | `CONFIGURED_PENDING_VERIFICATION` |
| **Chrome UX Report (CrUX)** | Real-User Field Data (CWV 75th percentile) | Yes | Public (Shares Google Cloud API Key) | Query Parameter API Key | CrUX API enabled | `BLOCKED_PENDING_CREDENTIALS` |
| **Google Merchant Center** | Product Feed Sync & Disapproval Diagnostics | Yes | No | Service Account / OAuth | Content API for Shopping | `BLOCKED_PENDING_CREDENTIALS` |
| **PostHog** | Product Behavioral Analytics & Session Replay | Yes | No (`POSTHOG_API_KEY`, `POSTHOG_HOST` missing) | Project API Key | Ingestion Key | `BLOCKED_PENDING_CREDENTIALS` |
| **Google Gemini API** | Content Research & Editorial Generation | Yes | Yes (`GEMINI_API_KEY` in GitHub Secrets / `.env`) | Header / URL API Key | Google AI Studio Key | `CONFIGURED_PENDING_VERIFICATION` |
| **Buffer** | Social Media Deal Publishing & Queue Management | Yes | In `.env.example` / Secrets (`BUFFER_API_KEY`) | Bearer Token | Buffer Publish API | `CONFIGURED_PENDING_VERIFICATION` |
| **Telegram Bot** | Real-Time Notifications & Approvals | Yes | Yes (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_OWNER_CHAT_ID`, `TELEGRAM_CHANNEL_ID`) | Bot Token | Telegram Bot API | `CONFIGURED_PENDING_VERIFICATION` |
| **Meta Graph API** | Facebook & Instagram Insights / Ads | Partial | Missing (`META_ACCESS_TOKEN` is EMPTY in `.env`) | User / System User Token | `pages_read_engagement`, `ads_read` | `BLOCKED_PENDING_CREDENTIALS` |
| **Ahrefs / Semrush** | Backlink Gap & Competitor Authority | Yes | No | API Token | Ahrefs Web API v3 / Semrush API | `BLOCKED_PENDING_CREDENTIALS` |

---

## Credentials Needed from the User (Priority Order)

To activate all blocked external capabilities, the user can provide the following credentials securely via environment variables or GitHub Secrets:

1. **`PAGESPEED_API_KEY` / `GOOGLE_CLOUD_API_KEY`**: Enables high-quota Google PageSpeed Insights and Chrome UX Report (CrUX) field audits.
2. **`POSTHOG_API_KEY` & `POSTHOG_HOST`**: Enables client-side behavioral event tracking and conversion funnel diagnostics.
3. **`GA4_API_SECRET`**: Enables server-side verified purchase import via GA4 Measurement Protocol.
4. **`BUFFER_API_KEY`**: To test live Buffer publishing queue and rate-limit backoff locally in `.env`.
5. **`META_ACCESS_TOKEN`**: For Instagram/Facebook page insights and campaign verification.
6. **`AHREFS_API_KEY` / `SEMRUSH_API_KEY`**: For live backlink profile monitoring and domain authority audits.
