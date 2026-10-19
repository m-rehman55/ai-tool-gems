"""
regex_engine.py - Google Search Console RE2-Compliant Advanced Regex Engine.
Generates, validates, and tests copy-ready regular expressions for GSC Performance Filters.
Strictly complies with Google Search Console's RE2 syntax requirements:
- No PCRE backreferences (\1)
- No lookaheads ((?=...)) or lookbehinds ((?<=...))
- Case-insensitivity via (?i)
- Verified against Python standard 're' and RE2 constraints
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class FilterValidationResult:
    is_valid_re2: bool
    error_message: Optional[str] = None
    unsupported_features: List[str] = field(default_factory=list)


@dataclass
class GSCFilterDefinition:
    name: str
    dimension: str  # "Query" or "Page"
    match_type: str  # "Matches regex" or "Doesn't match regex"
    regex: str
    matches_summary: str
    excludes_summary: str
    sample_matching: List[str]
    sample_non_matching: List[str]
    potential_edge_cases: str
    is_re2_validated: bool
    instructions: str
    metrics_to_inspect: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "dimension": self.dimension,
            "match_type": self.match_type,
            "regex": self.regex,
            "matches_summary": self.matches_summary,
            "excludes_summary": self.excludes_summary,
            "sample_matching": self.sample_matching,
            "sample_non_matching": self.sample_non_matching,
            "potential_edge_cases": self.potential_edge_cases,
            "is_re2_validated": self.is_re2_validated,
            "instructions": self.instructions,
            "metrics_to_inspect": self.metrics_to_inspect,
        }

    def format_markdown(self) -> str:
        match_ex = ", ".join(f"`{s}`" for s in self.sample_matching)
        non_ex = ", ".join(f"`{s}`" for s in self.sample_non_matching)
        status_icon = "✅ RE2 Validated" if self.is_re2_validated else "⚠️ Syntax Warning"

        return f"""### 🔍 Filter: {self.name}
- **Dimension:** `{self.dimension}`
- **Filter Mode:** **{self.match_type}**
- **RE2 Compatibility:** {status_icon}
- **Copy-Ready Regex:**
```regex
{self.regex}
```
- **What it Matches:** {self.matches_summary}
- **What it Excludes:** {self.excludes_summary}
- **Example Matches:** {match_ex}
- **Example Excluded:** {non_ex}
- **Edge Cases & False Positives:** {self.potential_edge_cases}
- **How to Apply in GSC:**
  1. Open Search Console -> Performance -> **Search results**.
  2. Click **+ New** at the top filter bar and choose **{self.dimension}**.
  3. Select **Custom (regex)** -> **{self.match_type}**.
  4. Paste the regex above and click **Apply**.
- **Metrics to Inspect:** {self.metrics_to_inspect}
"""


class RE2Validator:
    """Validates regular expressions for compatibility with Google Search Console RE2 engine."""

    UNSUPPORTED_PATTERNS = [
        (r"\(\?=", "Lookahead assertion `(?=...)` is not supported in RE2"),
        (r"\(\?!", "Negative lookahead `(?!...)` is not supported in RE2"),
        (r"\(\?<=", "Lookbehind assertion `(?<=...)` is not supported in RE2"),
        (r"\(\?<!", "Negative lookbehind `(?<!...)` is not supported in RE2"),
        (r"\\[1-9]", "Backreferences `\\1` are not supported in RE2"),
        (r"\(\?P=[a-zA-Z0-9_]+\)", "Named backreferences are not supported in RE2"),
        (r"\*\+", "Possessive quantifiers `*+` are not supported in RE2"),
        (r"\+\+", "Possessive quantifiers `++` are not supported in RE2"),
    ]

    @classmethod
    def validate(cls, pattern: str) -> FilterValidationResult:
        unsupported = []
        for pat, desc in cls.UNSUPPORTED_PATTERNS:
            if re.search(pat, pattern):
                unsupported.append(desc)

        if unsupported:
            return FilterValidationResult(
                is_valid_re2=False,
                error_message="Unsupported PCRE feature in RE2",
                unsupported_features=unsupported,
            )

        # Validate compilation in standard Python re
        try:
            re.compile(pattern)
        except re.error as e:
            return FilterValidationResult(
                is_valid_re2=False,
                error_message=f"Regex compile error: {str(e)}",
            )

        return FilterValidationResult(is_valid_re2=True)


class GSCFilterLibrary:
    """Curated, verified library of Search Console regex filters for aitoolgems.tech."""

    def __init__(self):
        self.validator = RE2Validator()

    def get_core_filters(self) -> List[GSCFilterDefinition]:
        raw_defs = [
            # 1. Brand Filter
            {
                "name": "Brand Queries",
                "dimension": "Query",
                "match_type": "Matches regex",
                "regex": r"(?i)(ai\s*tool\s*gems|aitoolgems|ai\s*tools\s*aura)",
                "matches_summary": "All variations of brand name queries (with spaces, without spaces, or legacy brand name).",
                "excludes_summary": "Generic, non-branded AI tool searches.",
                "sample_matching": ["ai tool gems", "aitoolgems", "aitoolgems login", "ai tools aura"],
                "sample_non_matching": ["chatgpt price in pakistan", "buy canva pro", "elevenlabs urdu"],
                "potential_edge_cases": "Does not match separate generic words 'ai tools' unless accompanied by 'gems' or 'aura'.",
                "metrics_to_inspect": "Track brand awareness growth, direct navigational clicks, and brand CTR (should exceed 30%).",
            },
            # 2. Non-Brand Commercial Filter (Pure Organic Discovery)
            {
                "name": "Non-Brand Organic Queries",
                "dimension": "Query",
                "match_type": "Doesn't match regex",
                "regex": r"(?i)(ai\s*tool\s*gems|aitoolgems|ai\s*tools\s*aura)",
                "matches_summary": "Every query that does NOT mention the brand name.",
                "excludes_summary": "Brand navigation searches.",
                "sample_matching": ["buy chatgpt pro pakistan", "canva pro price easypaisa", "claude 3.5 sonnet pkr"],
                "sample_non_matching": ["ai tool gems", "aitoolgems pakistan", "aitoolgems review"],
                "potential_edge_cases": "Ensures no brand equity masks true non-brand organic search growth.",
                "metrics_to_inspect": "Pure non-brand impressions and non-brand click acquisition trends.",
            },
            # 3. Pakistan & Local Currency Transactional Intent
            {
                "name": "Pakistan & Local Payment Intent",
                "dimension": "Query",
                "match_type": "Matches regex",
                "regex": r"(?i)(pakistan|pakistani|pkr|rs\.?|rupees?|easypaisa|jazzcash|sadapay|nayapay|raast|lahore|karachi|islamabad)",
                "matches_summary": "Queries indicating explicit Pakistani geographical presence or local payment method intent.",
                "excludes_summary": "Global international queries with no local payment affinity.",
                "sample_matching": ["chatgpt price in pakistan", "buy canva pro easypaisa", "midjourney pkr", "gemini advanced jazzcash"],
                "sample_non_matching": ["chatgpt api docs", "canva templates free", "figma plugins"],
                "potential_edge_cases": "Matches mentions of major Pakistani cities (Lahore, Karachi, Islamabad) and local wallets.",
                "metrics_to_inspect": "High-intent transactional conversion rate, local SERP rankings, and WhatsApp lead signals.",
            },
            # 4. Commercial & Purchase Intent
            {
                "name": "Commercial & Purchase Intent",
                "dimension": "Query",
                "match_type": "Matches regex",
                "regex": r"(?i)(buy|price|pricing|cost|subscription|subscribe|purchase|plans?|cheap|affordable|discount|deal|license|key|account)",
                "matches_summary": "Queries where user wants to buy, compare prices, or purchase subscriptions.",
                "excludes_summary": "Pure educational or informational troubleshooting searches.",
                "sample_matching": ["buy chatgpt plus", "canva pro cheap subscription", "claude pro pricing pkr", "capcut pro license key"],
                "sample_non_matching": ["what is chatgpt", "how to use figma", "free prompt examples"],
                "potential_edge_cases": "'free trial' might match 'trial' if included; 'cost' matches price investigations.",
                "metrics_to_inspect": "Clicks on commercial pages (/deals/, /prices/, /tools/*/).",
            },
            # 5. Question & AEO (Answer Engine Optimization) Intent
            {
                "name": "Question & AEO Snippet Intent",
                "dimension": "Query",
                "match_type": "Matches regex",
                "regex": r"(?i)^(who|what|when|where|why|which|how|can|does|is|are|best|top)\b",
                "matches_summary": "Natural-language questions and list-based discovery queries suitable for featured snippets and AI overviews.",
                "excludes_summary": "Short-tail keywords without question starters.",
                "sample_matching": ["how to buy chatgpt in pakistan", "can i pay via easypaisa for canva", "which ai tool is best for video editing", "is claude available in pakistan"],
                "sample_non_matching": ["chatgpt plus pkr", "canva pro login", "elevenlabs api"],
                "potential_edge_cases": "Anchored to start of query (^) to capture clear question structure.",
                "metrics_to_inspect": "Rich results, FAQ schema click-throughs, and featured snippet positions (1-3).",
            },
            # 6. Comparison & Alternative Intent
            {
                "name": "Comparison & Alternative Queries",
                "dimension": "Query",
                "match_type": "Matches regex",
                "regex": r"(?i)(vs\.?|versus|alternative|alternatives|compare|comparison|better|or\b)",
                "matches_summary": "Queries comparing two tools or seeking alternatives to expensive AI tools.",
                "excludes_summary": "Single tool searches.",
                "sample_matching": ["chatgpt vs claude", "midjourney alternative", "capcut vs premiere pro", "veo or runway"],
                "sample_non_matching": ["buy chatgpt", "canva pricing", "replit download"],
                "potential_edge_cases": "Word boundary on 'or' prevents false matches inside words like 'creator' or 'generator'.",
                "metrics_to_inspect": "Traffic to /guides/ comparison articles.",
            },
            # 7. AI Chat & LLM Tool Cluster
            {
                "name": "AI Chat & LLM Cluster",
                "dimension": "Query",
                "match_type": "Matches regex",
                "regex": r"(?i)(chatgpt|gpt[- ]?4|gpt[- ]?5|gemini|claude|copilot|perplexity|deepseek)",
                "matches_summary": "Queries targeting conversational LLMs and reasoning engines.",
                "excludes_summary": "Video, design, or dev tool queries.",
                "sample_matching": ["chatgpt plus pakistan", "gemini advanced subscription", "claude 3.5 sonnet", "deepseek r1 pkr"],
                "sample_non_matching": ["canva pro", "elevenlabs voice", "figma license"],
                "potential_edge_cases": "Captures hyphenated and spaced variants like 'gpt-4' or 'gpt 4'.",
                "metrics_to_inspect": "Impressions and CTR on /tools/chatgpt/ and /tools/gemini/.",
            },
            # 8. AI Video & Audio Tool Cluster
            {
                "name": "AI Video & Audio Cluster",
                "dimension": "Query",
                "match_type": "Matches regex",
                "regex": r"(?i)(capcut|elevenlabs|veo|runway|sora|heygen|synthesia|sunoo|midjourney|leonardo)",
                "matches_summary": "Queries targeting generative media, voice cloning, and AI video generators.",
                "excludes_summary": "Text LLMs and productivity software.",
                "sample_matching": ["capcut pro pakistan", "elevenlabs urdu voice", "google veo 3 ultra", "leonardo ai credits"],
                "sample_non_matching": ["cursor ai editor", "chatgpt plus", "nordvpn account"],
                "potential_edge_cases": "Groups top media generation tools.",
                "metrics_to_inspect": "Growth among Pakistani YouTubers and TikTok creators.",
            },
            # 9. Design, Dev & Coding AI Cluster
            {
                "name": "Dev & Design AI Cluster",
                "dimension": "Query",
                "match_type": "Matches regex",
                "regex": r"(?i)(canva|figma|adobe|cursor|replit|notion|gamma|n8n|lovable)",
                "matches_summary": "Queries targeting Pakistani freelancers, developers, and graphic designers.",
                "excludes_summary": "Entertainment or generic chat tools.",
                "sample_matching": ["canva pro lifetime", "figma pro pakistan", "cursor ai pro pkr", "gamma app subscription"],
                "sample_non_matching": ["netflix pakistan", "chatgpt login", "capcut mod apk"],
                "potential_edge_cases": "Ensures tracking of high-ARPU developer and agency software.",
                "metrics_to_inspect": "High average CTR and high commercial conversion intent.",
            },
            # 10. Page Grouping: Product Tool Pages
            {
                "name": "Page Group: Tool Detail Pages",
                "dimension": "Page",
                "match_type": "Matches regex",
                "regex": r"^https?://aitoolgems\.tech/tools/",
                "matches_summary": "All 20 individual tool landing pages (/tools/chatgpt/, /tools/canva/, etc.).",
                "excludes_summary": "Guides, homepage, deals, and policy pages.",
                "sample_matching": ["https://aitoolgems.tech/tools/chatgpt/", "https://aitoolgems.tech/tools/leonardo/"],
                "sample_non_matching": ["https://aitoolgems.tech/", "https://aitoolgems.tech/guides/developers/", "https://aitoolgems.tech/prices/"],
                "potential_edge_cases": "Exact protocol and path prefix matching.",
                "metrics_to_inspect": "Aggregate performance of product catalog.",
            },
            # 11. Page Grouping: Educational Guides & Comparisons
            {
                "name": "Page Group: Educational Guides",
                "dimension": "Page",
                "match_type": "Matches regex",
                "regex": r"^https?://aitoolgems\.tech/guides/",
                "matches_summary": "All in-depth Pakistani buying guides and tool comparison pages.",
                "excludes_summary": "Direct product landing pages and legal policies.",
                "sample_matching": ["https://aitoolgems.tech/guides/ai-tools-price-pakistan/", "https://aitoolgems.tech/guides/chatgpt-vs-gemini-pakistan/"],
                "sample_non_matching": ["https://aitoolgems.tech/tools/gemini/", "https://aitoolgems.tech/about.html"],
                "potential_edge_cases": "Captures top-of-funnel informational and AEO traffic.",
                "metrics_to_inspect": "Informational impressions, organic backlink attraction, and internal link CTR.",
            },
            # 12. Global Tool Comparisons & Alternatives
            {
                "name": "Global Comparisons & Alternatives",
                "dimension": "Query",
                "match_type": "Matches regex",
                "regex": r"(?i)\b(vs|versus|alternative|alternatives|compare|comparison|workflow|for students|for freelancers|for developers|for creators)\b",
                "matches_summary": "Queries comparing tools, seeking alternatives, or finding audience-specific workflows globally.",
                "excludes_summary": "Single-tool transactional queries without comparison intent.",
                "sample_matching": ["chatgpt vs claude for coding", "midjourney alternatives", "ai tools for students", "canva vs figma comparison"],
                "sample_non_matching": ["buy chatgpt plus", "canva pro price", "easypaisa login"],
                "potential_edge_cases": "Matches both Pakistan-based and international comparison searches.",
                "metrics_to_inspect": "High organic CTR, informational impressions, and comparison guide engagement.",
            },
            # 13. Cross-Border & International Inquiries
            {
                "name": "International Inquiries & Cross-Border Access",
                "dimension": "Query",
                "match_type": "Matches regex",
                "regex": r"(?i)\b(international|abroad|overseas|outside pakistan|wise|swift|inquiry|global|worldwide)\b",
                "matches_summary": "Queries from diaspora or international customers seeking cross-border ordering and quotes.",
                "excludes_summary": "Domestic PKR and Pakistani wallet queries.",
                "sample_matching": ["buy ai tools outside pakistan", "international inquiry ai subscriptions", "pay ai tools via wise"],
                "sample_non_matching": ["easypaisa ai tools", "jazzcash canva pro", "lahore ai tools"],
                "potential_edge_cases": "Ensures tracking of manual WhatsApp inquiry volume from non-PK searchers.",
                "metrics_to_inspect": "Inquiry conversions and international traffic to policies.html#payments.",
            },
        ]

        filters: List[GSCFilterDefinition] = []
        for d in raw_defs:
            v_res = self.validator.validate(d["regex"])
            filters.append(GSCFilterDefinition(
                name=d["name"],
                dimension=d["dimension"],
                match_type=d["match_type"],
                regex=d["regex"],
                matches_summary=d["matches_summary"],
                excludes_summary=d["excludes_summary"],
                sample_matching=d["sample_matching"],
                sample_non_matching=d["sample_non_matching"],
                potential_edge_cases=d["potential_edge_cases"],
                is_re2_validated=v_res.is_valid_re2,
                instructions=(
                    f"In GSC -> Search results -> + New -> {d['dimension']} -> Custom (regex) -> "
                    f"{d['match_type']} -> paste pattern."
                ),
                metrics_to_inspect=d["metrics_to_inspect"],
            ))
        return filters

    def test_filter(self, filter_def: GSCFilterDefinition, test_strings: List[str]) -> Tuple[List[str], List[str]]:
        """Tests a regex filter against test strings and returns (matched, non_matched)."""
        pattern = re.compile(filter_def.regex)
        matched = []
        non_matched = []
        for s in test_strings:
            is_match = bool(pattern.search(s))
            if filter_def.match_type == "Doesn't match regex":
                is_match = not is_match
            if is_match:
                matched.append(s)
            else:
                non_matched.append(s)
        return matched, non_matched

    def build_custom_regex(
        self,
        keywords: List[str],
        case_insensitive: bool = True,
        exact_start: bool = False,
        exact_end: bool = False,
    ) -> str:
        """
        Constructs an RE2-safe regex pattern from a list of keyword strings,
        handling whitespace flexibility and special character escaping.
        """
        escaped_parts = []
        for kw in keywords:
            # Escape regex characters except space
            clean = re.sub(r"([.\\+*?\[\^\]$(){}=!<>|:-])", r"\\\1", kw.strip())
            # Replace spaces with \s* to match queries with or without spaces
            flexible = re.sub(r"\s+", r"\\s*", clean)
            if flexible:
                escaped_parts.append(flexible)

        inner = "|".join(escaped_parts)
        prefix = "(?i)" if case_insensitive else ""
        start = "^" if exact_start else ""
        end = "$" if exact_end else ""
        return f"{prefix}{start}(?:{inner}){end}"
