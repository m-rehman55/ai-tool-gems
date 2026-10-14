# AI Tool Gems chatbot Worker

This is the secure backend for the static-site chatbot. It exposes `POST /api/chat`, fetches the canonical public catalog from `app.js`, and returns source links. It works without a model key using deterministic catalog/policy answers; adding `GEMINI_API_KEY` enables concise natural-language responses.

The catalog is refreshed automatically on a request from the public `app.js` source; there is no duplicated public price list. After changing products or policy pages, run `npm.cmd run validate-catalog`, then deploy the Worker so its configuration and tests remain current. Policy and guide links are deliberately public source links; private admin data is never fetched.

## Local test

From this directory:

```powershell
npx wrangler dev
```

Set a local secret only if desired:

```powershell
npx wrangler secret put GEMINI_API_KEY
```

Do not put the key in `vars`, frontend JavaScript, Git, or the static site. The Worker rejects obvious passwords, OTPs, card details, API keys, and other secrets in chat input. It does not implement order lookup or admin actions.

## Deploy and route

```powershell
npx wrangler deploy
```

The production widget calls the free `workers.dev` endpoint configured in `chatbot/widget.js`. A custom `aitoolgems.tech/api/chat` route is not configured because the domain is not hosted as a zone in this Cloudflare account. If DNS is later moved to Cloudflare, the route can be changed to same-origin without exposing any key.

The free tier has quotas and the in-memory rate limiter resets when isolates restart. The widget stores only the current conversation in memory (not localStorage) and sends only a short, secret-filtered context window. Aggregate chatbot event names use the site analytics hook; message text is not tracked. For higher-risk production order data, add a separate authenticated order service; do not extend this public endpoint with admin mutations.

## Browser smoke test

When Playwright and Chromium are available, run the production UI smoke test from the repository root with `npx playwright test chatbot/ui_smoke.spec.mjs`. It covers open, minimize, restore, successful send, network-failure recovery, close/reopen, duplicate-widget protection, and mobile button reachability.
