# AI Tool Gems chatbot Worker

This is the secure backend for the static-site chatbot. It exposes `POST /api/chat`, fetches the canonical public catalog from `app.js`, and returns source links. It works without a model key using deterministic catalog/policy answers; adding `GEMINI_API_KEY` enables concise natural-language responses.

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

The free tier has quotas and the in-memory rate limiter resets when isolates restart. For higher-risk production order data, add a separate authenticated order service; do not extend this public endpoint with admin mutations.
