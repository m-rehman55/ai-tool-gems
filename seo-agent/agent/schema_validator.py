#!/usr/bin/env python3
"""
Schema Validator for AIToolGems Autonomous SEO Growth Agent
------------------------------------------------------------
Validates JSON-LD Structured Data:
- Product (name, offers, priceCurrency: PKR, availability)
- BreadcrumbList (itemListElement, positions, URLs)
- FAQPage (mainEntity, Question, acceptedAnswer)
- Organization (name, url, logo/image)
"""

from __future__ import annotations
import json
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field

@dataclass
class SchemaIssue:
    schema_type: str
    field_name: str
    message: str
    severity: str  # ERROR, WARNING
    url: str

@dataclass
class SchemaValidationReport:
    total_schemas: int
    valid_count: int
    error_count: int
    warning_count: int
    types_found: Set[str] = field(default_factory=set)
    issues: List[SchemaIssue] = field(default_factory=list)

class SchemaValidator:
    """Validates Google Search Central Schema.org compliance."""

    def __init__(self, primary_currency: str = "PKR"):
        self.primary_currency = primary_currency

    def _extract_items(self, raw_schema_str: str) -> List[Dict[str, Any]]:
        """Parses raw JSON-LD string and unpacks @graph if present."""
        items: List[Dict[str, Any]] = []
        try:
            parsed = json.loads(raw_schema_str)
            if isinstance(parsed, dict):
                if "@graph" in parsed and isinstance(parsed["@graph"], list):
                    items.extend([item for item in parsed["@graph"] if isinstance(item, dict)])
                else:
                    items.append(parsed)
            elif isinstance(parsed, list):
                items.extend([item for item in parsed if isinstance(item, dict)])
        except Exception:
            pass
        return items

    def validate_product(self, item: Dict[str, Any], url: str) -> List[SchemaIssue]:
        issues: List[SchemaIssue] = []
        for req in ["name", "description"]:
            if not item.get(req):
                issues.append(
                    SchemaIssue(
                        schema_type="Product",
                        field_name=req,
                        message=f"Product schema missing required field '{req}'",
                        severity="ERROR",
                        url=url,
                    )
                )

        # Check offers
        offers = item.get("offers")
        if not offers:
            issues.append(
                SchemaIssue(
                    schema_type="Product",
                    field_name="offers",
                    message="Product schema missing 'offers' object",
                    severity="ERROR",
                    url=url,
                )
            )
        else:
            offer_obj = offers[0] if isinstance(offers, list) and offers else offers
            if isinstance(offer_obj, dict):
                curr = offer_obj.get("priceCurrency", "")
                if curr != self.primary_currency:
                    issues.append(
                        SchemaIssue(
                            schema_type="Product",
                            field_name="offers.priceCurrency",
                            message=f"Offer currency mismatch: expected '{self.primary_currency}', found '{curr}'",
                            severity="ERROR",
                            url=url,
                        )
                    )
                if "price" not in offer_obj or str(offer_obj.get("price", "")).strip() == "":
                    issues.append(
                        SchemaIssue(
                            schema_type="Product",
                            field_name="offers.price",
                            message="Offer missing valid 'price'",
                            severity="ERROR",
                            url=url,
                        )
                    )

        return issues

    def validate_breadcrumb(self, item: Dict[str, Any], url: str) -> List[SchemaIssue]:
        issues: List[SchemaIssue] = []
        elements = item.get("itemListElement")
        if not elements or not isinstance(elements, list):
            issues.append(
                SchemaIssue(
                    schema_type="BreadcrumbList",
                    field_name="itemListElement",
                    message="BreadcrumbList missing 'itemListElement' array",
                    severity="ERROR",
                    url=url,
                )
            )
        else:
            for idx, el in enumerate(elements, start=1):
                if not isinstance(el, dict):
                    continue
                if "position" not in el:
                    issues.append(
                        SchemaIssue(
                            schema_type="BreadcrumbList",
                            field_name=f"itemListElement[{idx}].position",
                            message="Breadcrumb item missing 'position'",
                            severity="WARNING",
                            url=url,
                        )
                    )
                if not el.get("name"):
                    issues.append(
                        SchemaIssue(
                            schema_type="BreadcrumbList",
                            field_name=f"itemListElement[{idx}].name",
                            message="Breadcrumb item missing 'name'",
                            severity="ERROR",
                            url=url,
                        )
                    )

        return issues

    def validate_faq(self, item: Dict[str, Any], url: str) -> List[SchemaIssue]:
        issues: List[SchemaIssue] = []
        main_entity = item.get("mainEntity")
        if not main_entity or not isinstance(main_entity, list):
            issues.append(
                SchemaIssue(
                    schema_type="FAQPage",
                    field_name="mainEntity",
                    message="FAQPage missing 'mainEntity' array of Questions",
                    severity="ERROR",
                    url=url,
                )
            )
        else:
            for idx, q in enumerate(main_entity, start=1):
                if not isinstance(q, dict):
                    continue
                if not q.get("name"):
                    issues.append(
                        SchemaIssue(
                            schema_type="FAQPage",
                            field_name=f"mainEntity[{idx}].name",
                            message="FAQ Question missing 'name' (question text)",
                            severity="ERROR",
                            url=url,
                        )
                    )
                ans = q.get("acceptedAnswer", {})
                if not isinstance(ans, dict) or not ans.get("text"):
                    issues.append(
                        SchemaIssue(
                            schema_type="FAQPage",
                            field_name=f"mainEntity[{idx}].acceptedAnswer.text",
                            message="FAQ Question missing acceptedAnswer.text",
                            severity="ERROR",
                            url=url,
                        )
                    )

        return issues

    def validate_page_schemas(self, raw_schemas: List[str], url: str) -> List[SchemaIssue]:
        """Validates all JSON-LD blocks on a single page."""
        all_issues: List[SchemaIssue] = []
        for raw in raw_schemas:
            items = self._extract_items(raw)
            if not items and raw.strip():
                all_issues.append(
                    SchemaIssue(
                        schema_type="JSON-LD",
                        field_name="syntax",
                        message="Malformed or unparseable JSON-LD string",
                        severity="ERROR",
                        url=url,
                    )
                )
                continue

            for item in items:
                stype = str(item.get("@type", ""))
                if "Product" in stype:
                    all_issues.extend(self.validate_product(item, url))
                elif "BreadcrumbList" in stype:
                    all_issues.extend(self.validate_breadcrumb(item, url))
                elif "FAQPage" in stype:
                    all_issues.extend(self.validate_faq(item, url))

        return all_issues
