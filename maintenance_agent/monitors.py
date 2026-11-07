"""
HERMES Operational Automation & Maintenance Monitors
---------------------------------------------------
Formal specifications and contracts for the 15 continuous operational monitors.
Every monitor is strictly READ-ONLY (Rule K-Invariant):
Monitoring must not automatically change prices, publish content,
alter indexing, or deploy code.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import re
from datetime import datetime, timezone


class MonitorFrequency(str, Enum):
    REAL_TIME = "REAL_TIME"
    EVENT_DRIVEN = "EVENT_DRIVEN_PR_OR_PUSH"
    DAILY = "DAILY"
    BI_WEEKLY = "BI_WEEKLY"
    MONTHLY = "MONTHLY"
    ON_DEMAND = "ON_DEMAND"


class ActionNature(str, Enum):
    READ_ONLY_AUDIT = "READ_ONLY_AUDIT"
    READ_ONLY_ALERT = "READ_ONLY_ALERT"


class MonitorStatus(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    MANUAL_FALLBACK_REQUIRED = "MANUAL_FALLBACK_REQUIRED"


@dataclass
class MonitorDefinition:
    id: str
    name: str
    what_it_checks: str
    frequency: MonitorFrequency
    evidence_source: str
    change_threshold: str
    false_positive_handling: str
    notification_destination: str
    required_owner_action: str
    action_nature: ActionNature = ActionNature.READ_ONLY_AUDIT
    is_automated: bool = True
    manual_alternative_sop: Optional[str] = None

    def validate_invariants(self) -> bool:
        """Enforces Rule K: Monitors must be strictly read-only."""
        assert self.action_nature in (ActionNature.READ_ONLY_AUDIT, ActionNature.READ_ONLY_ALERT), (
            f"Monitor {self.id} violates read-only invariant: {self.action_nature}"
        )
        return True


@dataclass
class MonitorResult:
    monitor_id: str
    status: MonitorStatus
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    findings: List[str] = field(default_factory=list)
    evidence_collected: Dict[str, Any] = field(default_factory=dict)
    owner_action_needed: bool = False
    action_summary: Optional[str] = None
    is_read_only: bool = True


class MonitorRegistry:
    """Central registry of all 15 Phase K operational monitors."""

    def __init__(self):
        self._monitors: Dict[str, MonitorDefinition] = {}
        self._register_default_monitors()

    def register(self, monitor: MonitorDefinition):
        monitor.validate_invariants()
        self._monitors[monitor.id] = monitor

    def get(self, monitor_id: str) -> Optional[MonitorDefinition]:
        return self._monitors.get(monitor_id)

    def all_monitors(self) -> List[MonitorDefinition]:
        return list(self._monitors.values())

    def _register_default_monitors(self):
        # 1. Tool pricing changes
        self.register(MonitorDefinition(
            id="MON-01-PRICING",
            name="Tool Pricing Changes Monitor",
            what_it_checks="Scrapes official vendor pricing pages and public feeds for all 40 catalog tools to detect tier shifts, currency changes, or plan modifications.",
            frequency=MonitorFrequency.BI_WEEKLY,
            evidence_source="Vendor pricing DOM selectors, developer pricing APIs, and archived plan snapshots.",
            change_threshold="Base USD tier change >= $1.00, introduction/removal of plans, or PKR exchange drift >= 5%.",
            false_positive_handling="Filter transient flash discounts (<7 days); check multiple DOM selectors; if blocked by anti-bot 403, flag as FETCH_BLOCKED_MANUAL_CHECK instead of price change.",
            notification_destination="Telegram Bot (@AIToolGemsBot) + reports/maintenance/pricing_drift_<date>.json",
            required_owner_action="Review vendor pricing diff; verify against official invoice; calculate updated PKR estimate; propose PR with updated pricing schema (human approval mandatory).",
            action_nature=ActionNature.READ_ONLY_AUDIT,
            is_automated=True,
            manual_alternative_sop="Manual SOP-01: Navigate to vendor pricing page using standard browser; check Monthly and Annual pricing tabs; record findings in data/catalog/pricing_register.csv."
        ))

        # 2. Product discontinuation
        self.register(MonitorDefinition(
            id="MON-02-DISCONTINUATION",
            name="Product Discontinuation & Sunset Monitor",
            what_it_checks="Checks active availability and sunset status of all 40 catalog tools to detect product shutdowns, end-of-life notices, or corporate acquisitions.",
            frequency=MonitorFrequency.MONTHLY,
            evidence_source="Official vendor status pages, homepage HTTP response codes, release RSS feeds, and GitHub repo archives.",
            change_threshold="HTTP 404/410 across 3 consecutive checks over 48 hours, or explicit shutdown keywords ('discontinued', 'end of life', 'shutting down', 'sunset').",
            false_positive_handling="Multi-day retry to rule out temporary CDN/server downtime; verify DNS records (NXDOMAIN vs 502/503); inspect vendor official social handles.",
            notification_destination="High-priority Telegram Alert + GitHub Issue labeled 'catalogue:sunset'",
            required_owner_action="Mark tool as DISCONTINUED in canonical register; display sunset notice on tool page; remove from primary comparison tables; update sitemap via PR.",
            action_nature=ActionNature.READ_ONLY_ALERT,
            is_automated=True,
            manual_alternative_sop="Manual SOP-02: Visit developer website and blog; search official announcement channels for sunset timelines."
        ))

        # 3. Feature changes
        self.register(MonitorDefinition(
            id="MON-03-FEATURES",
            name="Feature & Capability Drift Monitor",
            what_it_checks="Tracks core model updates, context window expansions, free-tier limits, and API accessibility changes across catalog tools.",
            frequency=MonitorFrequency.MONTHLY,
            evidence_source="Official changelogs, release notes, documentation RSS feeds, and product launch announcements.",
            change_threshold="Changes in core specifications (e.g. context window token bounds, major model version upgrade like GPT-4o to GPT-5, free tier quota reduction).",
            false_positive_handling="Semantic diffing ignoring cosmetic marketing copy; isolate feature keywords ('context window', 'tokens', 'rate limit', 'commercial usage').",
            notification_destination="Telegram Weekly Summary + reports/maintenance/feature_drift_<date>.md",
            required_owner_action="Update tool profile features, comparison grids, and RAG knowledge bases (llms.txt); prepare PR for content refresh.",
            action_nature=ActionNature.READ_ONLY_AUDIT,
            is_automated=True,
            manual_alternative_sop="Manual SOP-03: Inspect vendor documentation changelog and official release notes."
        ))

        # 4. Official URL changes
        self.register(MonitorDefinition(
            id="MON-04-URL-REDIRECTS",
            name="Official URL & Domain Rebrand Monitor",
            what_it_checks="Tests outbound official developer links in catalog tools to detect HTTP redirects (301, 302, 307, 308) or domain rebrands.",
            frequency=MonitorFrequency.BI_WEEKLY,
            evidence_source="Automated HTTP HEAD/GET probes to official_url fields with redirect tracking.",
            change_threshold="Any redirect resulting in a different destination domain or URL path.",
            false_positive_handling="Distinguish protocol upgrades (http to https) and trailing slash normalization from true rebrands; ignore temporary 302 marketing redirects.",
            notification_destination="Telegram Alert + PR draft updating canonical official_url in catalog data",
            required_owner_action="Verify new destination domain is legitimate developer site and not an expired domain takeover; approve URL update PR.",
            action_nature=ActionNature.READ_ONLY_AUDIT,
            is_automated=True,
            manual_alternative_sop="Manual SOP-04: Test official outbound URL in browser; observe final URL bar destination."
        ))

        # 5. Terms updates
        self.register(MonitorDefinition(
            id="MON-05-TERMS",
            name="Vendor Terms & Privacy Policy Monitor",
            what_it_checks="Audits vendor Terms of Service, Privacy Policies, and Acceptable Use Policies for changes affecting commercial rights, data privacy, or Pakistan users.",
            frequency=MonitorFrequency.MONTHLY,
            evidence_source="Vendor /terms, /privacy, and /policies web pages diffed against stored baseline SHA-256 hashes.",
            change_threshold="Text diff >= 10% in word count or addition of clauses mentioning 'Pakistan', 'sanctions', 'resale', 'account sharing', or 'commercial license'.",
            false_positive_handling="Strip dynamic date strings, cookie consent popups, and navigational headers before computing diff hash.",
            notification_destination="Telegram Notification + reports/maintenance/terms_drift_<date>.md",
            required_owner_action="Review legal impact on Pakistani users and concierge fulfillment; update tool disclosure if commercial rights changed.",
            action_nature=ActionNature.READ_ONLY_AUDIT,
            is_automated=True,
            manual_alternative_sop="Manual SOP-05: Use web diffing tool (e.g. Visualping or manual text diff) on vendor terms URLs."
        ))

        # 6. Regional availability
        self.register(MonitorDefinition(
            id="MON-06-REGIONAL-AVAILABILITY",
            name="Pakistan Regional Availability Monitor",
            what_it_checks="Detects geoblocking, Cloudflare 1020 IP bans, SMS verification exclusion (+92 country code), or payment gateway regional blocks affecting Pakistan.",
            frequency=MonitorFrequency.MONTHLY,
            evidence_source="Synthetic probes from Pakistani residential/datacenter vantage points, signup form country dropdowns, and SMS carrier support tables.",
            change_threshold="Cloudflare access denied on PK IP range, removal of Pakistan (+92) from registration options, or checkout country restriction.",
            false_positive_handling="Multi-network verification across at least 2 distinct Pakistani ASNs (e.g. AS9299 PTCL + AS45595 Nayatel); never flag based on single transient failure.",
            notification_destination="High-priority Telegram Alert + reports/maintenance/pakistan_availability_<date>.md",
            required_owner_action="Update 'Pakistan Availability' badge and FAQ on tool page; document VPN requirements if necessary; pause ad campaigns if blocked.",
            action_nature=ActionNature.READ_ONLY_ALERT,
            is_automated=False,
            manual_alternative_sop="Manual SOP-06: Test signup flow from a physical Pakistani internet connection (Nayatel/PTCL); verify +92 SMS reception and checkout availability."
        ))

        # 7. Broken links
        self.register(MonitorDefinition(
            id="MON-07-BROKEN-LINKS",
            name="Broken Links & Structural Link Graph Monitor",
            what_it_checks="Validates 100% of internal links, fragment anchors, local assets, and external references across all 102+ HTML files.",
            frequency=MonitorFrequency.EVENT_DRIVEN,
            evidence_source="scripts/link_graph_checker.py --strict running on push/PR and daily scheduled workflow.",
            change_threshold="Any broken internal link (>0 errors), broken fragment anchor, missing asset, or crawl depth > 2 hops from root.",
            false_positive_handling="Retry external links 3 times with 5s timeout and standard browser User-Agent to avoid anti-bot rejections.",
            notification_destination="GitHub PR CI Failure Status + Telegram Bot Alert on scheduled failure",
            required_owner_action="Fix broken href or anchor target; remove dead link; commit fix to feature branch.",
            action_nature=ActionNature.READ_ONLY_AUDIT,
            is_automated=True,
            manual_alternative_sop="Manual SOP-07: Run 'python scripts/link_graph_checker.py --strict' locally in PowerShell."
        ))

        # 8. Sitemap and indexing changes
        self.register(MonitorDefinition(
            id="MON-08-SITEMAP-INDEXING",
            name="Sitemap Parity & IndexNow Monitor",
            what_it_checks="Verifies XML well-formedness of sitemap.xml, exact parity with indexable HTML pages, <lastmod> date accuracy, and IndexNow submission history.",
            frequency=MonitorFrequency.DAILY,
            evidence_source="scripts/generate_sitemap.py, scripts/link_graph_checker.py, and ping_agent/ping_history.json.",
            change_threshold="Any discrepancy between indexable pages and sitemap.xml, missing canonical tags, invalid XML namespace, or IndexNow HTTP error.",
            false_positive_handling="Strictly exclude noindex and utility pages (404.html, policies.html); ensure URLs use canonical root https://aitoolgems.tech/.",
            notification_destination="GitHub Actions Run Log + Telegram Alert",
            required_owner_action="Re-run 'python scripts/generate_sitemap.py'; commit updated sitemap; verify Search Console sitemap fetch.",
            action_nature=ActionNature.READ_ONLY_AUDIT,
            is_automated=True,
            manual_alternative_sop="Manual SOP-08: Run 'python -m ping_agent verify' and 'python scripts/sitemap_audit.py' locally."
        ))

        # 9. Schema errors
        self.register(MonitorDefinition(
            id="MON-09-SCHEMA",
            name="JSON-LD Structured Data Validator",
            what_it_checks="Verifies JSON-LD syntax, schema completeness (Product, FAQPage, BreadcrumbList, Organization), and strict priceCurrency: PKR rules.",
            frequency=MonitorFrequency.EVENT_DRIVEN,
            evidence_source="schema_audit.py, seo-agent/agent/schema_validator.py, and Google Rich Results Testing rules.",
            change_threshold="Any syntax error (json.loads fail), missing required properties (name, offers, breadcrumbs), or unauthorized foreign currency tokens.",
            false_positive_handling="Deterministic parser ensures zero false positives on JSON structure; strict ontology validation.",
            notification_destination="GitHub PR Check Failure + Telegram Alert",
            required_owner_action="Correct schema markup in HTML file; test with 'python schema_audit.py'; push fix via PR.",
            action_nature=ActionNature.READ_ONLY_AUDIT,
            is_automated=True,
            manual_alternative_sop="Manual SOP-09: Run 'python schema_audit.py' and test URLs in Google Rich Results Test web tool."
        ))

        # 10. Performance regressions
        self.register(MonitorDefinition(
            id="MON-10-PERFORMANCE",
            name="Core Web Vitals & Speed Budget Monitor",
            what_it_checks="Measures live edge Core Web Vitals (LCP, INP, CLS, TTFB), JavaScript bundle budgets (<150 KB), and image dimensions across representative routes.",
            frequency=MonitorFrequency.DAILY,
            evidence_source="tests/test_phase_i_performance_and_quality.py, live edge HTTP probes, and PageSpeed Insights API.",
            change_threshold="LCP > 2.5s, CLS > 0.1, INP > 200ms, TTFB > 600ms, or JS uncompressed bundle increase > 20 KB.",
            false_positive_handling="Execute 3 probe runs and compute median metrics to filter transient edge network or ISP routing jitter.",
            notification_destination="Telegram Alert + reports/maintenance/performance_drift_<date>.md",
            required_owner_action="Inspect bloated CSS/JS asset or uncompressed media; optimize assets (WebP/SVG); defer scripts; test locally.",
            action_nature=ActionNature.READ_ONLY_AUDIT,
            is_automated=True,
            manual_alternative_sop="Manual SOP-10: Run 'python tests/test_phase_i_performance_and_quality.py' and run Chrome DevTools Lighthouse audit."
        ))

        # 11. Search Console changes
        self.register(MonitorDefinition(
            id="MON-11-SEARCH-CONSOLE",
            name="Search Console Impressions & CTR Drift Monitor",
            what_it_checks="Monitors 7-day rolling organic search impressions, clicks, average CTR, average position, and Googlebot crawl anomalies.",
            frequency=MonitorFrequency.DAILY,
            evidence_source="Google Search Console API (searchanalytics.query via keyword_agent/gsc_data.py).",
            change_threshold="Impressions drop >= 20% WoW, clicks drop >= 25% WoW, or new 4xx/5xx coverage errors reported by Googlebot.",
            false_positive_handling="Exclude public holidays (Pakistani Eid holidays cause normal 30% drop); evaluate 7-day rolling averages instead of single-day spikes.",
            notification_destination="Daily GSC Snapshot in seo-agent/reports/<date>/ + Telegram Alert",
            required_owner_action="Investigate affected URLs; check for accidental noindex tags, manual actions, or Google search updates; optimize CTR titles.",
            action_nature=ActionNature.READ_ONLY_AUDIT,
            is_automated=True,
            manual_alternative_sop="Manual SOP-11: Log into Google Search Console UI; inspect Performance tab and Pages indexing report."
        ))

        # 12. Analytics ingestion failures
        self.register(MonitorDefinition(
            id="MON-12-ANALYTICS-INGESTION",
            name="Analytics & Telemetry Ingestion Health Monitor",
            what_it_checks="Verifies GA4 data stream reception, PostHog EU ingestion status, Measurement Protocol purchase imports, and Consent Mode v2 default denial.",
            frequency=MonitorFrequency.DAILY,
            evidence_source="PostHog ingestion telemetry, GA4 Realtime API, and offline conversion import logs.",
            change_threshold="Zero events received over 24 hours with active traffic, Measurement Protocol HTTP 4xx errors, or pending offline orders failing import.",
            false_positive_handling="Correlate with server access logs to confirm traffic baseline before alerting; verify API secret expiration.",
            notification_destination="Telegram Alert + reports/maintenance/analytics_health_<date>.json",
            required_owner_action="Verify GA4_MEASUREMENT_SECRET and POSTHOG_API_KEY in GitHub Secrets; inspect attribution.js execution; reconcile offline ledger.",
            action_nature=ActionNature.READ_ONLY_ALERT,
            is_automated=True,
            manual_alternative_sop="Manual SOP-12: Trigger test event on production site with DevTools Network tab; verify 204 response from GA4/PostHog."
        ))

        # 13. Provider API failures
        self.register(MonitorDefinition(
            id="MON-13-PROVIDER-APIS",
            name="External Provider API & Rate-Limit Monitor",
            what_it_checks="Audits connectivity, authentication, and quotas for Buffer API, Gemini API, IndexNow endpoints, Telegram Bot API, and PostHog EU host.",
            frequency=MonitorFrequency.DAILY,
            evidence_source="Provider Capability Matrix probes, HTTP status codes, and API ping endpoints.",
            change_threshold="HTTP 401/403 (Authentication failure), HTTP 429 (Rate limit exhausted), or connection timeout > 10s.",
            false_positive_handling="Apply exponential backoff with jitter and Retry-After inspection before declaring failure; distinguish transient downtime from revoked credentials.",
            notification_destination="Workflow Annotation + Telegram Alert (or console log if Telegram fails)",
            required_owner_action="Review and verify provider credentials; re-authenticate expired API token in GitHub Secrets / Settings; adjust rate throttles or upgrade quota tier.",
            action_nature=ActionNature.READ_ONLY_ALERT,
            is_automated=True,
            manual_alternative_sop="Manual SOP-13: Test API credentials via curl or Postman against provider status endpoints."
        ))

        # 14. Security alerts
        self.register(MonitorDefinition(
            id="MON-14-SECURITY-ALERTS",
            name="Dependency Vulnerabilities & Secret Leakage Guard",
            what_it_checks="Monitors GitHub Dependabot alerts, CodeQL static analysis, affirmative public allowlist staging, and secret/credential leakage.",
            frequency=MonitorFrequency.REAL_TIME,
            evidence_source="GitHub Security Advisory Database, tests/test_public_repository_boundary.py, ScopeGuard, and SafetyFirewall.",
            change_threshold="Any High or Critical CVE in dependencies, any untracked secret/credential, or attempt to modify protected rules.",
            false_positive_handling="Distinguish dev/test dependencies from production static assets; verify CVE exploitability against static site architecture.",
            notification_destination="GitHub Security Tab + Immediate Telegram Emergency Alert",
            required_owner_action="Update dependency version in requirements.txt; rotate exposed credentials immediately; re-run boundary test.",
            action_nature=ActionNature.READ_ONLY_ALERT,
            is_automated=True,
            manual_alternative_sop="Manual SOP-14: Run 'pip audit' and 'python -m unittest tests/test_public_repository_boundary.py' locally."
        ))

        # 15. PR CI failures
        self.register(MonitorDefinition(
            id="MON-15-PR-CI-FAILURES",
            name="Pull Request CI/CD Pipeline Monitor",
            what_it_checks="Monitors status of all PR checks: 217 unit tests, link graph checker, public allowlist staging, Scope Guard, and CodeQL analysis.",
            frequency=MonitorFrequency.EVENT_DRIVEN,
            evidence_source="GitHub Actions workflow statuses and check suite API on pull_request events.",
            change_threshold="Any non-zero exit code or failed unit test in the CI matrix.",
            false_positive_handling="Distinguish GitHub runner infrastructure timeout from deterministic code regression; re-run flaky network jobs once.",
            notification_destination="GitHub PR Status Check Badges + Telegram Notification",
            required_owner_action="Review CI logs; reproduce failure locally; fix the underlying bug or regression; push commit to feature branch.",
            action_nature=ActionNature.READ_ONLY_ALERT,
            is_automated=True,
            manual_alternative_sop="Manual SOP-15: Run 'python -m unittest discover -s tests -v' and 'python scripts/link_graph_checker.py --strict' locally before pushing."
        ))
