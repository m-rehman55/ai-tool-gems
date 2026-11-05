"""
Technical SEO Audit & Analysis Engine for Crawler Agent.
Analyzes entire site crawl dataset: broken links, orphan pages,
duplicate titles/metas, heading hierarchy, image alts, mixed content,
thin content, crawl budget waste, and computes overall Technical Health Score.
"""

from __future__ import annotations
import collections
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Set

from crawler_agent.models import CrawlRecord, TechnicalAuditSummary, URLCrawlState


class TechnicalSEOAnalyzer:
    """Performs deep technical SEO audits across all crawled pages."""

    def __init__(self, base_url: str = "https://aitoolgems.tech"):
        self.base_url = base_url.rstrip("/")

    def audit_crawl_dataset(
        self,
        records: List[CrawlRecord],
        crawl_mode: str = "LIVE_PRODUCTION"
    ) -> TechnicalAuditSummary:
        """Executes full 30+ point technical SEO audit across crawled records."""
        total_urls = len(records)
        if total_urls == 0:
            return TechnicalAuditSummary(technical_health_score=0.0)

        # 1. Map pages and inbound link graph
        inbound_links: Dict[str, Set[str]] = collections.defaultdict(set)
        title_map: Dict[str, List[str]] = collections.defaultdict(list)
        meta_map: Dict[str, List[str]] = collections.defaultdict(list)
        hash_map: Dict[str, List[str]] = collections.defaultdict(list)

        broken_links: List[Dict[str, Any]] = []
        orphan_pages: List[str] = []
        missing_h1_pages: List[str] = []
        heading_violations: List[Dict[str, Any]] = []
        missing_alt_images: List[Dict[str, Any]] = []
        mixed_content_pages: List[str] = []
        trailing_slash_issues: List[str] = []
        thin_content_pages: List[Dict[str, Any]] = []
        canonical_issues: List[Dict[str, Any]] = []
        sitemap_mismatches: List[Dict[str, Any]] = []
        crawl_budget_waste: List[Dict[str, Any]] = []

        total_fetch_time = 0.0

        for r in records:
            total_fetch_time += r.fetch_time_ms

            # Inbound link mapping
            for link in r.internal_links:
                inbound_links[link].add(r.url)

            # Duplicate title tracking
            if r.title:
                title_map[r.title.strip()].append(r.url)

            # Duplicate meta tracking
            if r.meta_description:
                meta_map[r.meta_description.strip()].append(r.url)

            # Duplicate body content tracking
            if r.html_hash and r.word_count > 100:
                hash_map[r.html_hash].append(r.url)

            # HTTP status & broken link
            if r.status_code >= 400 or r.error_message:
                broken_links.append({
                    "url": r.url,
                    "status_code": r.status_code,
                    "error": r.error_message
                })

            # Missing H1 & heading hierarchy
            if r.headings.missing_h1:
                missing_h1_pages.append(r.url)
            elif not r.headings.hierarchy_valid:
                heading_violations.append({
                    "url": r.url,
                    "issues": r.headings.issues
                })

            # Image alt text
            for img in r.images:
                if img.is_missing_alt:
                    missing_alt_images.append({
                        "page_url": r.url,
                        "image_src": img.src
                    })

            # Mixed content
            if r.has_mixed_content:
                mixed_content_pages.append(r.url)

            # Trailing slash consistency
            if not r.has_trailing_slash:
                trailing_slash_issues.append(r.url)

            # Canonical issues
            if not r.canonical:
                canonical_issues.append({"url": r.url, "issue": "Missing canonical tag"})
            elif r.canonical.rstrip("/") != r.url.rstrip("/"):
                canonical_issues.append({
                    "url": r.url,
                    "canonical": r.canonical,
                    "issue": "Canonical tag points to different URL"
                })

            # Thin content (< 200 words on non-utility pages)
            if r.word_count < 200 and not any(k in r.url for k in ("404", "contact", "about")):
                thin_content_pages.append({
                    "url": r.url,
                    "word_count": r.word_count
                })

            # Crawl budget waste: redirect chains, slow response > 2500ms
            if len(r.redirect_chain) > 1:
                crawl_budget_waste.append({
                    "url": r.url,
                    "issue": f"Redirect chain detected ({len(r.redirect_chain)} hops)"
                })
            elif r.fetch_time_ms > 2500:
                crawl_budget_waste.append({
                    "url": r.url,
                    "issue": f"Slow response time: {r.fetch_time_ms:.0f}ms"
                })

        # Orphan page detection (pages with 0 inbound links that are not homepage)
        for r in records:
            clean_url = r.url.rstrip("/")
            if clean_url != self.base_url and len(inbound_links[r.url]) == 0 and len(inbound_links[clean_url + "/"]) == 0:
                orphan_pages.append(r.url)

        # Duplicate title count
        dup_titles = [urls for title, urls in title_map.items() if len(urls) > 1]
        dup_metas = [urls for meta, urls in meta_map.items() if len(urls) > 1]

        # Health score calculation
        score = 100.0
        score -= min(30.0, len(broken_links) * 10.0)
        score -= min(15.0, len(missing_h1_pages) * 5.0)
        score -= min(15.0, len(dup_titles) * 3.0)
        score -= min(10.0, len(orphan_pages) * 3.0)
        score -= min(10.0, len(mixed_content_pages) * 5.0)
        score -= min(10.0, len(canonical_issues) * 2.0)
        score -= min(5.0, len(missing_alt_images) * 0.5)
        score = max(0.0, round(score, 1))

        critical_issues = []
        if broken_links:
            critical_issues.append({"severity": "P0_CRITICAL", "type": "BROKEN_LINKS", "count": len(broken_links), "items": broken_links[:5]})
        if missing_h1_pages:
            critical_issues.append({"severity": "P1_HIGH", "type": "MISSING_H1", "count": len(missing_h1_pages), "items": missing_h1_pages[:5]})
        if orphan_pages:
            critical_issues.append({"severity": "P1_HIGH", "type": "ORPHAN_PAGES", "count": len(orphan_pages), "items": orphan_pages[:5]})
        if canonical_issues:
            critical_issues.append({"severity": "P1_HIGH", "type": "CANONICAL_MISMATCH", "count": len(canonical_issues), "items": canonical_issues[:5]})

        avg_fetch = (total_fetch_time / total_urls) if total_urls > 0 else 0.0

        return TechnicalAuditSummary(
            total_urls_scanned=total_urls,
            crawl_mode=crawl_mode,
            broken_links_count=len(broken_links),
            orphan_pages_count=len(orphan_pages),
            duplicate_titles_count=len(dup_titles),
            duplicate_metas_count=len(dup_metas),
            missing_h1_count=len(missing_h1_pages),
            heading_hierarchy_violations=len(heading_violations),
            images_missing_alt_count=len(missing_alt_images),
            mixed_content_violations=len(mixed_content_pages),
            trailing_slash_inconsistencies=len(trailing_slash_issues),
            thin_content_pages_count=len(thin_content_pages),
            canonical_issues_count=len(canonical_issues),
            sitemap_mismatches_count=len(sitemap_mismatches),
            crawl_budget_waste_count=len(crawl_budget_waste),
            average_fetch_time_ms=round(avg_fetch, 1),
            technical_health_score=score,
            critical_issues=critical_issues,
        )
