# AI Tool Gems Organic Marketing Agent

This is the safe, free-first implementation of the marketing specification. Phase 1 creates and schedules transparent product posts for an owned Telegram channel, tracks campaign attribution into the website's WhatsApp order message, stores real metrics in SQLite, learns only after enough evidence, and sends an owner report.

It does **not** scrape audiences, auto-DM people, post to groups without permission, invent reach, or use unofficial social APIs. Instagram/Facebook publishing and WhatsApp Cloud reporting are intentionally gated until Telegram has passed the requested three-day test.

## What is implemented

- 20-product catalog with current PKR listing price, duration, access, delivery, and warranty
- balanced product rotation, five audience segments, five content angles, A/B copy variants
- caption hashes and database constraints to block duplicate posts
- `draft → scheduled → published/failed` approval workflow
- official Telegram Bot API posting, one controlled retry, message IDs, subscriber capture
- unique UTM and `src` codes leading to each product page
- website attribution that carries the campaign code into the WhatsApp order message
- manual real-metric input for clicks, orders, revenue, reactions, forwards, and views/impressions
- evidence threshold before declaring a winning angle
- honest daily reports: unknown values stay zero/not captured

Telegram's Bot API supports channel posting and `getChatMemberCount`, but it does not expose the user-only channel view-counter method. See the official [Bot API](https://core.telegram.org/bots/api) and [view-counter API limitation](https://core.telegram.org/method/messages.getMessagesViews). For that reason, view and forward figures are manual imports unless a separately authorized, compliant analytics source is added later.

## Safe setup

1. Copy `.env.example` to `.env`. Never commit `.env`.
2. Create a bot with Telegram's `@BotFather` and add it as an administrator of your own channel with permission to post.
3. Fill credentials one at a time: bot token, channel ID/username, then the owner's chat ID.
4. Initialize and verify:

```powershell
python -m marketing_agent init
python -m marketing_agent test-telegram
```

## Three-day validation

Generate drafts without auto-posting:

```powershell
python -m marketing_agent generate --days 3
python -m marketing_agent list --status draft
```

Review every caption, then approve only the desired IDs:

```powershell
python -m marketing_agent approve 1 2 3
python -m marketing_agent publish-due --dry-run
python -m marketing_agent publish-due
```

Record only actual results. Metrics are incremental, not estimated cumulative snapshots:

```powershell
python -m marketing_agent record --post 1 --clicks 4 --orders 1 --revenue 2300 --source whatsapp
python -m marketing_agent capture-subscribers
python -m marketing_agent learn
python -m marketing_agent report
python -m marketing_agent report --send
```

## Scheduler

Run `python -m marketing_agent tick` every 15 minutes using Windows Task Scheduler, cron, or a private always-on server. It is idempotent: an existing daily campaign is skipped by its unique tracking code. Leave `ATG_AUTO_APPROVE=false` for the test period; then explicitly switch it to `true` only after reviewing the first three days.

Recommended Pakistan-time checkpoints:

- 08:45 — create/review the day's drafts
- 09:15, 13:30, 18:45 — publish due approved posts
- 21:00 — capture real data and send the report

SQLite must live on persistent, private storage. Do not put the database or API tokens in GitHub Pages or a public Git repository. GitHub Actions runners are ephemeral, so this build does not pretend they are a safe persistent database host.

## Phase 2 gate

After three clean days (no duplicate posts, correct links, correct prices, successful reports), add owned Instagram/Facebook page publishing through Meta's official API. Platforms without a supported official publishing API should receive exported drafts for manual approval. No fixed reach or ranking guarantee is made; the system improves measurable conversion signals gradually.
