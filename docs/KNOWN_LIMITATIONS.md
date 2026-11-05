# KNOWN SYSTEM LIMITATIONS & ARCHITECTURAL CONSTRAINTS
**System**: AI Tool Gems (https://aitoolgems.tech/)  
**Date**: 2026-11-05  

---

## 1. Hosting Architecture
- **Static GitHub Pages**: The site is hosted on GitHub Pages (static HTML, CSS, JS). Server-side dynamic code (Python, Node.js) does not run on the web server; it runs in CI/CD (GitHub Actions), local CLI, and background workers.
- **Client-Side SPA Enhancements**: Modal product views and filtering operate via client-side JavaScript (`app.js`). Static pre-rendered pages exist for all 41 tools and 41 guides to guarantee complete search engine crawlability and indexing.

## 2. Assisted Order Fulfillment Model
- **WhatsApp Checkout**: AI Tool Gems uses assisted WhatsApp order confirmation to accommodate domestic Pakistani payment rails (EasyPaisa, JazzCash, SadaPay, Bank IBFT) and manual account provisioning.
- **Purchase Tracking Constraint**: A click to WhatsApp is an `initiate_checkout` or `contact_whatsapp` signal, NOT a confirmed transaction. Confirmed purchases must be imported offline or via server-side confirmation after payment verification.

## 3. Rate Limits & Quotas
- **Google Search Console**: Subject to quota limits on Search Analytics and URL Inspection (2,000 queries per day per property).
- **IndexNow**: Subject to rate limits (maximum 10,000 URLs per key per day).
- **Google Gemini API**: Free tier subject to 15 RPM.
