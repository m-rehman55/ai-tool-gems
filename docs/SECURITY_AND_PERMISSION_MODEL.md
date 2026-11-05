# SECURITY AND PERMISSION MODEL
**Standard**: Minimum Privilege, Zero Hardcoded Secrets, Fail-Closed Safety  

---

## 1. Secrets Management & Credential Policy

1. **Zero Secret Hardcoding**: No API key, bot token, client secret, or private credentials may ever be committed to git, exposed in frontend JavaScript, printed in logs, or written to markdown reports.
2. **Environment Isolation**:
   - Local: `.env` (strictly included in `.gitignore`).
   - CI/CD: GitHub Actions Secrets (`${{ secrets.* }}`).
   - Validation: Unit test `tests/test_integrity_and_regressions.py::test_no_exposed_api_secrets_in_client_js` enforces frontend scanning.
3. **Redaction in Execution Logs**: All log handlers and Telegram dispatchers must sanitize tokens using regex masking (`[REDACTED_SECRET]`).

---

## 2. API Scope & Minimum Privilege Matrix

| Service | Minimum Required Scopes | Prohibited Dangerous Scopes |
| :--- | :--- | :--- |
| **Google Search Console** | `https://www.googleapis.com/auth/webmasters.readonly` | Write / Site Management / Site Removal scopes |
| **Google Analytics 4** | `https://www.googleapis.com/auth/analytics.readonly` | Edit / Admin management scopes |
| **Bing Webmaster** | Read API Key | Account administration privileges |
| **Google Gemini API** | AI Studio Text Generation Key | Project Billing / IAM management roles |
| **Buffer** | `publish:read`, `publish:write` | Profile deletion permissions |
| **Telegram Bot** | `sendMessage`, `sendPhoto` | Administrator channel alteration rights |
| **GitHub Token** | `contents: write`, `pull-requests: write` | Administration / Repository deletion rights |

---

## 3. Defense Against Autonomous Prompt Injection & Malicious HTML

1. **Untrusted External Content**: When agents scrape competitor pages or ingest external Search Console queries, content must be treated as untrusted data:
   - Must not be concatenated directly into shell commands (Command Injection defense).
   - Must not be passed raw into LLM system prompts without escaping delimiters.
   - Must be sanitized using HTML character entities before inclusion in website templates.
2. **Path Traversal Protection**: Slugs and filenames must match `^[a-z0-9]+(-[a-z0-9]+)*$` and resolve strictly within target subdirectories.
3. **Fail-Closed Execution**: If any security assertion or Scope Guard rule encounters an exception or ambiguous input, the execution terminates immediately (`ABORTED`).

