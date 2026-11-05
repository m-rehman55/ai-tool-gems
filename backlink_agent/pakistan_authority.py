"""Pakistan Digital Authority & Local Citation Opportunity Generator.

Curates legitimate, high-relevance Pakistani authority targets:
- P@SHA (Pakistan IT Industry Association)
- PAFLA (Pakistan Freelancers Association)
- TechJuice & ProPakistani editorial features
- University Computer Science portals (NUST, FAST, LUMS, ITU)

Every opportunity enforces strict Google Search Essentials compliance:
Zero PBNs, zero paid links, zero automated comments.
"""

from __future__ import annotations

import time
from typing import List

from backlink_agent.models import LinkOpportunity, LinkRisk, OpportunityType

PAKISTAN_AUTHORITY_TARGETS = [
    {
        "id": "OPP-PK-01",
        "domain": "pasha.org.pk",
        "target_page": "https://aitoolgems.tech/",
        "type": OpportunityType.LOCAL_DIRECTORY,
        "relevance": "National IT association directory for verified Pakistani software services",
        "method": "Direct organizational membership registration & compliance verification",
        "risk": LinkRisk.LOW_ORGANIC,
        "evidence": "Official member directory indexing verified tech startups",
        "value": "High topical authority in Pakistani software ecosystem",
    },
    {
        "id": "OPP-PK-02",
        "domain": "techjuice.pk",
        "target_page": "https://aitoolgems.tech/prices/",
        "type": OpportunityType.EDITORIAL_FEATURE,
        "relevance": "Technology news portal covering freelance pricing challenges in Pakistan",
        "method": "Editorial outreach sharing original empirical study on USD forex withholding taxes",
        "risk": LinkRisk.MEDIUM_OUTREACH,
        "evidence": "Regular editorial guides on freelance toolkits and local payment rails",
        "value": "Substantive contextual backlinks to the Pakistan AI price list",
    },
    {
        "id": "OPP-PK-03",
        "domain": "pafla.org.pk",
        "target_page": "https://aitoolgems.tech/guides/students/",
        "type": OpportunityType.PARTNERSHIP,
        "relevance": "Freelancers Association of Pakistan educational resource directory",
        "method": "Student & freelancer community discount guide contribution",
        "risk": LinkRisk.LOW_ORGANIC,
        "evidence": "Resource guide pages curated for Pakistani Upwork & Fiverr freelancers",
        "value": "Targeted transactional traffic and grounded institutional relevance",
    },
    {
        "id": "OPP-PK-04",
        "domain": "propakistani.pk",
        "target_page": "https://aitoolgems.tech/tools/chatgpt/",
        "type": OpportunityType.UNLINKED_MENTION,
        "relevance": "Articles discussing ChatGPT Plus subscription pricing and local card declines",
        "method": "Polite outreach providing verified flat PKR pricing data and source reference",
        "risk": LinkRisk.LOW_ORGANIC,
        "evidence": "Historical articles covering ChatGPT availability in Pakistan",
        "value": "High-trust domestic media link reclamation",
    },
]


def get_pakistan_authority_opportunities() -> List[LinkOpportunity]:
    """Return compliant, risk-classified Pakistani authority-building opportunities."""
    opportunities = []
    for t in PAKISTAN_AUTHORITY_TARGETS:
        opp = LinkOpportunity(
            opportunity_id=t["id"],
            domain=t["domain"],
            target_page=t["target_page"],
            opportunity_type=t["type"],
            relevance_assessment=t["relevance"],
            acquisition_method=t["method"],
            risk_classification=t["risk"],
            evidence=t["evidence"],
            projected_value=t["value"],
            created_at=time.time(),
        )
        is_safe, errors = opp.validate_safety()
        if is_safe:
            opportunities.append(opp)
    return opportunities

