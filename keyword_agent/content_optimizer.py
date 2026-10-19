"""
content_optimizer.py - On-Page Content, Heading & AEO Direct-Answer Optimization Engine.
Analyzes actual page HTML from disk and crafts actionable, GEO/AEO-aligned optimization briefs.
Adheres strictly to the master rule:
- Safe low-risk fixes vs changes requiring explicit Owner Approval.
- 40-55 word standalone direct-answer blocks for AEO snippet capture.
- Verifies destination internal links exist on disk before recommending.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class AEODirectAnswer:
    heading_question: str
    direct_answer_text: str  # 40-55 words
    entity_name: str
    target_intent: str


@dataclass
class PageOptimizationBrief:
    url: str
    relative_path: str
    current_title: str
    current_h1: str
    current_meta_desc: str
    primary_query: str
    recommended_title: str
    recommended_h1: str
    recommended_meta_desc: str
    suggested_h2_outline: List[str]
    aeo_answers: List[AEODirectAnswer]
    information_gain_additions: List[str]
    verified_internal_links: List[Dict[str, str]]
    semantic_terms: List[str]
    justification: str
    risk_level: str  # "LOW", "MEDIUM", "HIGH"
    requires_approval: bool
    approval_reason: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    def format_markdown(self) -> str:
        aeo_md = "\n".join(
            f"#### ❓ `{a.heading_question}`\n> **{a.entity_name}** {a.direct_answer_text}\n"
            for a in self.aeo_answers
        ) or "_No direct answer blocks required._"

        h2_md = "\n".join(f"- `{h}`" for h in self.suggested_h2_outline)
        info_md = "\n".join(f"- {ig}" for ig in self.information_gain_additions)
        links_md = "\n".join(f"- [{link['anchor']}]({link['url']})" for link in self.verified_internal_links)
        sem_md = ", ".join(f"`{s}`" for s in self.semantic_terms)

        approval_badge = "🚨 **REQUIRES OWNER APPROVAL**" if self.requires_approval else "🟢 **AUTO-APPROVED (LOW RISK)**"

        return f"""### 📄 On-Page Optimization: `{self.url}`
**Status:** {approval_badge}  
**Primary Intent Query:** `{self.primary_query}`  
**Risk Level:** `{self.risk_level}`  
**Approval Gate Reason:** {self.approval_reason}  

---

#### 1. Metadata & Primary Headings
| Element | Current Live Value | Recommended Optimization |
|---------|-------------------|--------------------------|
| **HTML Title** | `{self.current_title}` | `{self.recommended_title}` |
| **Main H1** | `{self.current_h1}` | `{self.recommended_h1}` |
| **Meta Description** | `{self.current_meta_desc}` | `{self.recommended_meta_desc}` |

#### 2. Suggested H2/H3 Heading Hierarchy
{h2_md}

#### 3. AEO (Answer Engine Optimization) Direct-Answer Blocks (40–55 words)
{aeo_md}

#### 4. Proprietary Information Gain Additions (Pakistan Market)
{info_md}

#### 5. Verified Internal Link Targets
{links_md}

#### 6. Semantic & Secondary Keyword Integration
{sem_md}

#### 7. Strategic Justification & Evidence
{self.justification}
"""


class ContentOptimizer:
    """Audits live on-disk HTML and formulates verified content optimizations."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir

    def extract_current_page_elements(self, relative_path: str) -> Dict[str, Any]:
        """Reads target HTML directly from disk and extracts current metadata without inventing."""
        file_path = self.project_dir / relative_path
        if not file_path.exists():
            return {
                "title": "",
                "h1": "",
                "meta_desc": "",
                "headings": [],
                "content_length": 0,
            }

        html = file_path.read_text(encoding="utf-8", errors="ignore")

        # Title
        t_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        title = re.sub(r"\s+", " ", t_match.group(1)).strip() if t_match else ""

        # H1
        h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
        h1 = re.sub(r"<[^>]+>", "", h1_match.group(1)).strip() if h1_match else ""

        # Meta description
        m_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
        meta_desc = m_match.group(1).strip() if m_match else ""

        # H2 headings
        h2_matches = re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.IGNORECASE | re.DOTALL)
        headings = [re.sub(r"<[^>]+>", "", h).strip() for h in h2_matches]

        return {
            "title": title,
            "h1": h1,
            "meta_desc": meta_desc,
            "headings": headings,
            "content_length": len(html),
        }

    def generate_optimization_brief(
        self,
        url: str,
        relative_path: str,
        primary_query: str,
        target_cluster: str,
        opportunity_score: float,
    ) -> PageOptimizationBrief:
        """Generates an evidence-backed optimization brief for a live site route."""
        curr = self.extract_current_page_elements(relative_path)
        tool_name = Path(relative_path).parent.name.title() if "tools/" in relative_path else "AI Tools"

        # Check existing destination links on disk
        verified_links = []
        for candidate_anchor, candidate_url, candidate_file in [
            ("All AI Tools Pricing Pakistan", "https://aitoolgems.tech/prices/", "prices/index.html"),
            ("Special AI Deals & Discounts", "https://aitoolgems.tech/deals/", "deals/index.html"),
            ("How We Review AI Tools in Pakistan", "https://aitoolgems.tech/how-we-review.html", "how-we-review.html"),
            ("ChatGPT Plus Pakistan Guide", "https://aitoolgems.tech/tools/chatgpt/", "tools/chatgpt/index.html"),
            ("Canva Pro EasyPaisa Pakistan", "https://aitoolgems.tech/tools/canva/", "tools/canva/index.html"),
        ]:
            if (self.project_dir / candidate_file).exists() and candidate_url != url:
                verified_links.append({"anchor": candidate_anchor, "url": candidate_url})

        # Formulate GEO/AEO Direct Answer
        aeo_answer = AEODirectAnswer(
            heading_question=f"How to buy {tool_name} subscription in Pakistan with EasyPaisa or JazzCash?",
            direct_answer_text=(
                f"provides direct Pakistani access to official {tool_name} subscriptions using local PKR payment methods. "
                "Customers in Pakistan can pay via EasyPaisa, JazzCash, SadaPay, or Raast without needing an international credit card. "
                "Account access or activation details are delivered via verified WhatsApp support after payment and availability confirmation."
            ),
            entity_name=f"AI Tool Gems Pakistan",
            target_intent="transactional_faq",
        )

        # Content additions for Information Gain
        info_gain = [
            f"Add explicit PKR price badge showing live estimated rate (e.g., 'Rs. 5,600/month').",
            f"Embed step-by-step 3-step checkout guide: Select Tool -> Transfer via EasyPaisa/JazzCash -> WhatsApp Delivery.",
            f"Include hands-on latency and payment compatibility note for Pakistani banks (Meezan, HBL, Bank Alfalah).",
        ]

        # Suggested H2 Hierarchy
        h2_outline = [
            f"{tool_name} Price in Pakistan (2026 PKR Rates)",
            f"How to Pay via EasyPaisa, JazzCash & SadaPay",
            f"Key Features & Comparison for Pakistani Creators",
            f"Frequently Asked Questions (Pakistan)",
        ]

        # Semantic keywords
        semantic = [
            f"{tool_name.lower()} price in pakistan",
            f"buy {tool_name.lower()} pkr",
            f"{tool_name.lower()} easypaisa",
            f"cheap {tool_name.lower()} subscription",
            "pakistan ai tools marketplace",
        ]

        # Titles and H1
        rec_title = f"{tool_name} Price in Pakistan (2026) | Buy via EasyPaisa & JazzCash (PKR)"
        if len(rec_title) > 65:
            rec_title = f"{tool_name} Price in Pakistan | Buy via EasyPaisa (PKR)"

        rec_h1 = f"{tool_name} in Pakistan: PKR Pricing, Features & Instant Local Payment"
        rec_meta = (
            f"Buy official {tool_name} in Pakistan at verified PKR rates. "
            f"Instant payment via EasyPaisa, JazzCash & WhatsApp delivery. 100% money-back guarantee."
        )

        # Safety Gate
        requires_approval = True
        approval_reason = (
            "Modifies public commercial headings and product page content. "
            "Requires human owner review to verify exact PKR rates and copy accuracy."
        )

        return PageOptimizationBrief(
            url=url,
            relative_path=relative_path,
            current_title=curr["title"],
            current_h1=curr["h1"],
            current_meta_desc=curr["meta_desc"],
            primary_query=primary_query,
            recommended_title=rec_title,
            recommended_h1=rec_h1,
            recommended_meta_desc=rec_meta,
            suggested_h2_outline=h2_outline,
            aeo_answers=[aeo_answer],
            information_gain_additions=info_gain,
            verified_internal_links=verified_links[:3],
            semantic_terms=semantic,
            justification=(
                f"Addresses high-intent search query '{primary_query}' with opportunity score {opportunity_score}. "
                "Aligns page structure with Google Search Essentials and AEO snippet requirements."
            ),
            risk_level="MEDIUM",
            requires_approval=requires_approval,
            approval_reason=approval_reason,
        )
