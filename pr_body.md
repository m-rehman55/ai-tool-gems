### Summary of Changes

1. **GitHub CI/CD Workflow Repairs:**
   - `.github/workflows/auto-blog-publisher.yml`: Added `pull-requests: write` permissions so content candidates are created cleanly without 403 API errors.
   - `.github/workflows/social-content-pack.yml`: Added branch protection fallback to prevent failures when pushing directly to protected `main`.
   - `scripts/update_deployment_allowlist.py`: Exempted `APPROVED_PUBLIC_DATASETS` from universal CSV prohibition.
   - `chatbot-worker/ui_smoke.spec.mjs`: Moved test specification out of public `chatbot/` directory, resolving `Weekly Core Web Vitals & CrUX Telemetry` boundary violations (307 approved files, 0 violations).

2. **Published High-Intent Claude SadaPay Guide:**
   - Target URL: `/guides/claude-pro-sadapay-nayapay-pakistan/`
   - Targeting Bing/GSC #1 commercial query: `how much claude 20$ plan will cost in pkr if we pay through sadapay`.
   - Complete 5-column canonical footer architecture, verified domestic PKR payment rails (EasyPaisa, JazzCash, SadaPay, Bank IBFT), and JSON-LD schema (FAQPage, Article, BreadcrumbList).

3. **Master Overnight Execution Plan Created:**
   - `docs/HERMES_OVERNIGHT_MASTER_EXECUTION_PLAN.md`: Full documentation of GSC schema validation statuses, Bing Webmaster audit, Japanese 404 purge protocol, workflow fixes, and the urgent Google Payments ID verification deadline (Nov 24).

4. **Testing & Quality Assurance:**
   - 239 / 239 unit tests green across all test suites.
   - 136 / 136 HTML pages with 100% valid schema (10,830 / 10,830 points).
   - Strict link graph checker: 100% clean (10,065 internal links, 0 errors).
   - Deployment boundary scan: 307 public files staged, strictly conforming to allowlist.
