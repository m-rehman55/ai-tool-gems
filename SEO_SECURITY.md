# SEO SECURITY

## Security-SEO Risks

### Identified
1. No SSL/TLS check
2. No HTTPS enforcement check
3. No XSS protection check
4. No CSRF protection check
5. No content security policy check

### Recommended
1. Enforce HTTPS
2. HSTS headers
3. Content Security Policy
4. X-Content-Type-Options
5. X-Frame-Options
6. Referrer-Policy

## Data Safety

- No credentials in repository ✅
- No API keys in repository ✅
- GSC/Bing tokens in marketing_agent/data/ ⚠️
- Telegram credentials in environment ⚠️

## SEO Security Rules

- Never expose credentials
- Never send secrets to Telegram
- Never expose API keys in code
- Never expose tokens in commits
- Always verify deployment before reporting success

## Production Safety

- SEO firewall blocks dangerous changes
- Mass changes require PR + human approval
- Rollback capability required
- Threshold-based alerts
