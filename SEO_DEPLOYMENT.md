# DEPLOYMENT

## Production Deployment

**System:** GitHub Pages (static HTML)
**Domain:** aitoolgems.tech
**CNAME:** aitoolgems.tech
**Branch:** main

## How It Works

1. Push to `main` branch
2. GitHub Pages auto-deploys from repository
3. CNAME file maps to aitoolgems.tech
4. SSL via GitHub Pages

## Workflow

```
CODE → TEST → BUILD → DEPLOY → LIVE CHECK → SEO CHECK → RESULT
```

## Deployment Steps

1. Create feature branch: `seo/level-X-purpose`
2. Make changes
3. Run tests
4. Commit with meaningful message
5. Push to branch
6. Create PR to main
7. Human review + approve
8. Merge to main
9. GitHub Pages auto-deploys
10. Verify live site
11. Run SEO check
12. Report result

## Daily Auto-Deploy

- `daily-seo-geo-monitor.yml` runs at 7:15 AM Karachi
- Performs SEO audit, pulls GSC/Bing data, sends Telegram report
- Does NOT auto-deploy — only monitors and reports

## Rollback

```bash
git revert <commit>
git push origin main
```

GitHub Pages redeploys automatically.

## Important Files

| File | Purpose |
|------|---------|
| CNAME | Domain mapping |
| robots.txt | Crawl directives |
| sitemap.xml | PK sitemap |
| sitemap-jp.xml | JP sitemap |
| llms.txt | LLM context |
| .github/workflows/ | Automation |
