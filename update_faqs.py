#!/usr/bin/env python3
"""
Add FAQ section + FAQPage schema to all 20 tool pages.
Run: python update_faqs.py
"""

import os
import re
import json
from pathlib import Path

REPO_DIR = Path("D:/ai-tool-gems")
TOOLS_DIR = REPO_DIR / "tools"

# ── All 20 tools ke liye FAQ data ──────────────────────────────────────────

TOOL_FAQS = {
    "chatgpt": {
        "title": "ChatGPT Plus",
        "faqs": [
            ("Is this ChatGPT Plus account private?",
             "AI Tool Gems lists ChatGPT Plus access intended for the buyer. The exact access type and account conditions are confirmed on WhatsApp before payment."),
            ("What is the delivery time for ChatGPT Plus?",
             "The listed delivery estimate is 15–30 minutes. The exact timing is reconfirmed with the support team on WhatsApp before payment."),
            ("What warranty comes with this listing?",
             "This listing includes a 7-day replacement warranty. Full warranty terms are on the policies page."),
            ("Can I use ChatGPT Plus for commercial work?",
             "ChatGPT Plus can be used for writing, research, coding, file analysis, and image tasks. Review OpenAI's terms for commercial use and avoid uploading confidential data until the account's privacy conditions are clear."),
            ("How do I order ChatGPT Plus?",
             "Open the WhatsApp order link on this page, confirm availability and payment details with the support team, then receive access instructions after payment."),
        ],
    },
    "gemini": {
        "title": "Gemini Pro",
        "faqs": [
            ("Is Gemini Pro access private or invitation-based?",
             "This Gemini Pro listing is described as invitation access. The exact account arrangement and conditions are confirmed on WhatsApp before payment."),
            ("What is the delivery estimate for Gemini Pro?",
             "The listed delivery estimate is 10–20 minutes. The final timing is reconfirmed on WhatsApp before payment."),
            ("What warranty is included with this listing?",
             "The listing includes an 18-month replacement warranty. Full warranty terms are explained on the policies page."),
            ("Can Gemini Pro be used with Google services?",
             "Gemini integrates with Google's ecosystem. Confirm the exact plan and access terms with the support team before payment, because features and availability can change."),
            ("How do I buy Gemini Pro from AI Tool Gems?",
             "Open the WhatsApp order link on this page, confirm availability, payment, and access details with the support team, then receive instructions after payment."),
        ],
    },
    "veo": {
        "title": "Veo 3 Ultra",
        "faqs": [
            ("What kind of access does Veo 3 Ultra provide?",
             "This Veo 3 Ultra listing is described as a shared access plan. Confirm the exact account arrangement and usage conditions on WhatsApp before payment."),
            ("Can Veo 3 generate videos from text prompts?",
             "Veo is Google's video generation model. Confirm the current capabilities, limits, and access terms with the support team, because model features can change over time."),
            ("What is the delivery time for Veo 3 Ultra?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact the support team for the current availability and timing."),
            ("Does Veo 3 Ultra support commercial video projects?",
             "Review the account's terms and Google's usage policies before using any generated video for commercial work. Confirm the exact access conditions with the support team."),
            ("How do I order Veo 3 Ultra?",
             "Open the WhatsApp order link on this page, confirm availability and payment details with the support team, then receive access instructions after payment."),
        ],
    },
    "leonardo": {
        "title": "Leonardo AI Essential",
        "faqs": [
            ("What does Leonardo AI Essential include?",
             "This listing provides Leonardo AI credits for image generation. The exact credit amount and usage terms are confirmed on WhatsApp before payment."),
            ("Can Leonardo AI generate images from text prompts?",
             "Leonardo AI is built for AI image generation and editing. Confirm the current plans, models, and limits with the support team before payment."),
            ("Is Leonardo AI suitable for commercial design work?",
             "Review Leonardo's terms for commercial use and the license attached to generated images. Confirm the exact access conditions with the support team before using outputs commercially."),
            ("What is the delivery estimate for Leonardo AI credits?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact the support team for current availability."),
            ("How do I order Leonardo AI Essential?",
             "Open the WhatsApp order link on this page, confirm the credit amount, payment details, and delivery with the support team, then receive access instructions after payment."),
        ],
    },
    "elevenlabs": {
        "title": "ElevenLabs",
        "faqs": [
            ("What does ElevenLabs access include?",
             "This ElevenLabs listing provides one month of access for AI voice generation. The exact plan and usage terms are confirmed on WhatsApp before payment."),
            ("Can ElevenLabs clone voices?",
             "ElevenLabs offers voice cloning features. Confirm which plan level and features are included in this listing, and review the consent and usage terms before cloning any voice."),
            ("Is ElevenLabs suitable for YouTube and video narration?",
             "ElevenLabs is commonly used for video narration and voiceovers. Review the commercial use terms and confirm the plan details with the support team before payment."),
            ("What is the delivery time for ElevenLabs?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact the support team for current availability and timing."),
            ("How do I order ElevenLabs?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with the support team, then receive access instructions after payment."),
        ],
    },
    "canva": {
        "title": "Canva Pro Edu",
        "faqs": [
            ("What is Canva Pro Edu access?",
             "This Canva listing is described as an invitation-based Pro plan. The exact seat arrangement and conditions are confirmed on WhatsApp before payment."),
            ("Can Canva Pro be used for commercial design work?",
             "Canva Pro includes premium templates, brand kits, and export options useful for commercial design. Review Canva's license terms for commercial use and confirm the plan details with the support team."),
            ("What is the delivery estimate for Canva Pro?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact the support team for current availability."),
            ("Can multiple people use one Canva Pro invitation?",
             "Invitation-based access depends on the seat arrangement. Confirm how many users the listing supports and how access is shared before payment."),
            ("How do I order Canva Pro Edu?",
             "Open the WhatsApp order link on this page, confirm availability, payment, and access details with the support team, then receive instructions after payment."),
        ],
    },
    "figma": {
        "title": "Figma Pro Private",
        "faqs": [
            ("What is Figma Pro Private access?",
             "This Figma listing is described as private access for two years. The exact account arrangement and conditions are confirmed on WhatsApp before payment."),
            ("Can Figma Pro be used for commercial UI/UX design?",
             "Figma Pro includes features for professional interface design, prototyping, and team collaboration. Review Figma's license terms and confirm the plan details with the support team before payment."),
            ("What is the delivery estimate for Figma Pro?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact the support team for current availability."),
            ("Can I use Figma Pro for client projects?",
             "Figma is widely used for client interface design work. Review the commercial use terms and confirm the account conditions with the support team before using it for client work."),
            ("How do I order Figma Pro Private?",
             "Open the WhatsApp order link on this page, confirm availability, payment details, and access terms with the support team, then receive instructions after payment."),
        ],
    },
    "capcut": {
        "title": "CapCut Pro",
        "faqs": [
            ("What does CapCut Pro include?",
             "This CapCut listing provides one month of Pro access for video editing. The exact plan and features are confirmed on WhatsApp before payment."),
            ("Can CapCut Pro remove watermarks?",
             "CapCut Pro includes features that help with watermark-free editing and exports. Confirm the exact export terms and plan details with the support team before payment."),
            ("Is CapCut Pro good for TikTok and Instagram Reels?",
             "CapCut is widely used for short-form video editing on TikTok, Instagram Reels, and YouTube Shorts. Review the export and licensing terms and confirm the plan with the support team."),
            ("What is the delivery time for CapCut Pro?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact the support team for current availability."),
            ("How do I order CapCut Pro?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with the support team, then receive access instructions after payment."),
        ],
    },
    "adobe": {
        "title": "Adobe Creative Cloud",
        "faqs": [
            ("What does this Adobe Creative Cloud listing include?",
             "This listing provides two months of Adobe Creative Cloud access. The exact apps included and account conditions are confirmed on WhatsApp before payment."),
            ("Which Adobe apps are included?",
             "Adobe Creative Cloud includes apps such as Photoshop, Illustrator, Premiere Pro, and others depending on the plan. Confirm the exact apps and plan level with the support team before payment."),
            ("Can Adobe Creative Cloud be used for commercial work?",
             "Adobe Creative Cloud is designed for professional creative work. Review Adobe's license terms for commercial use and confirm the account conditions with the support team before payment."),
            ("What is the delivery estimate for Adobe Creative Cloud?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact the support team for current availability."),
            ("How do I order Adobe Creative Cloud?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with the support team, then receive access instructions after payment."),
        ],
    },
    "lovable": {
        "title": "Lovable Pro",
        "faqs": [
            ("What is Lovable Pro?",
             "Lovable is an AI-powered development tool for building web applications. This listing provides one month of Pro access. The exact plan and features are confirmed on WhatsApp before payment."),
            ("Can Lovable be used to build production websites?",
             "Lovable is designed to help build web applications with AI assistance. Review the output quality, export options, and licensing terms before using any generated project for production work."),
            ("What is the delivery estimate for Lovable Pro?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact the support team for current availability."),
            ("Is Lovable suitable for beginners?",
             "Lovable is built to make web development more accessible with AI assistance. Confirm the current features and learning curve with the support team before payment."),
            ("How do I order Lovable Pro?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with the support team, then receive access instructions after payment."),
        ],
    },
    "gamma": {
        "title": "Gamma Pro",
        "faqs": [
            ("What is Gamma Pro?",
             "Gamma is an AI presentation and document tool. This listing provides one year of Pro access. The exact plan and features are confirmed on WhatsApp before payment."),
            ("Can Gamma Pro be used for business presentations?",
             "Gamma is built for creating presentations, documents, and web pages with AI assistance. Review the export options and commercial use terms before using Gamma outputs for business work."),
            ("What is the delivery estimate for Gamma Pro?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact the support team for current availability."),
            ("Can Gamma export to PowerPoint?",
             "Gamma supports export to multiple formats. Confirm the current export options and compatibility with the support team before payment."),
            ("How do I order Gamma Pro?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with the support team, then receive access instructions after payment."),
        ],
    },
    "replit": {
        "title": "Replit Core",
        "faqs": [
            ("What is Replit Core?",
             "Replit Core provides development environment access with AI assistance. This listing includes $40 in credits. The exact plan and usage terms are confirmed on WhatsApp before payment."),
            ("Can Replit be used to build and host web apps?",
             "Replit provides an online development environment with hosting capabilities. Review the hosting terms, resource limits, and export options before using Replit for production projects."),
            ("What is the delivery estimate for Replit Core?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact the support team for current availability."),
            ("Is Replit suitable for learning to code?",
             "Replit is commonly used for learning and experimenting with code in multiple languages. Confirm the current features and plan details with the support team before payment."),
            ("How do I order Replit Core?",
             "Open the WhatsApp order link on this page, confirm the credit amount, payment details, and delivery with the support team, then receive access instructions after payment."),
        ],
    },
    "n8n": {
        "title": "n8n Starter",
        "faqs": [
            ("What is n8n Starter?",
             "n8n is a workflow automation platform. This listing provides one year of access. The exact plan and usage terms are confirmed on WhatsApp before payment."),
            ("Can n8n connect to Google, Slack, and other services?",
             "n8n supports many integrations for workflow automation. Confirm the current integrations and plan limits with the support team before payment."),
            ("Is n8n suitable for business automation?",
             "n8n is designed for workflow and business process automation. Review the commercial use terms and confirm the account conditions with the support team before payment."),
            ("What is the delivery estimate for n8n Starter?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact the support team for current availability."),
            ("How do I order n8n Starter?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with the support team, then receive access instructions after payment."),
        ],
    },
    "notion": {
        "title": "Notion Business",
        "faqs": [
            ("What is Notion Business access?",
             "This Notion listing is described as invitation-based Business access for three months. The exact seat arrangement and conditions are confirmed on WhatsApp before payment."),
            ("Can Notion be used for team knowledge management?",
             "Notion is widely used for notes, databases, and team knowledge management. Review the plan terms and confirm the seat arrangement with the support team before payment."),
            ("What is the delivery estimate for Notion Business?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact the support team for current availability."),
            ("Can multiple team members use one Notion Business invitation?",
             "Invitation-based access depends on the seat arrangement. Confirm how many users the listing supports and how access is shared before payment."),
            ("How do I order Notion Business?",
             "Open the WhatsApp order link on this page, confirm availability, payment details, and access terms with the support team, then receive instructions after payment."),
        ],
    },
    "nordvpn": {
        "title": "NordVPN",
        "faqs": [
            ("What does this NordVPN listing include?",
             "This NordVPN listing provides three months of access. The exact plan and account conditions are confirmed on WhatsApp before payment."),
            ("Can NordVPN be used on multiple devices?",
             "NordVPN supports multiple simultaneous connections depending on the plan. Confirm the exact device limit and plan details with the support team before payment."),
            ("Is NordVPN suitable for public Wi-Fi security?",
             "NordVPN is designed to encrypt internet traffic and improve privacy on public networks. Review the service terms and confirm the plan details with the support team before payment."),
            ("What is the delivery estimate for NordVPN?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact the support team for current availability."),
            ("How do I order NordVPN?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with the support team, then receive access instructions after payment."),
        ],
    },
    "surfshark": {
        "title": "Surfshark VPN",
        "faqs": [
            ("What does this Surfshark VPN listing include?",
             "This Surfshark listing provides two months of shared access. The exact account arrangement and conditions are confirmed on WhatsApp before payment."),
            ("Can Surfshark be used on multiple devices?",
             "Surfshark supports unlimited simultaneous connections on its plans. Confirm the exact plan and account conditions with the support team before payment."),
            ("Is Surfshark suitable for streaming?",
             "Surfshark is commonly used for privacy and accessing content across regions. Review the service terms and confirm the plan details with the support team before payment."),
            ("What is the delivery estimate for Surfshark VPN?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact the support team for current availability."),
            ("How do I order Surfshark VPN?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with the support team, then receive access instructions after payment."),
        ],
    },
    "youtube": {
        "title": "YouTube Premium",
        "faqs": [
            ("What does this YouTube Premium listing include?",
             "This YouTube Premium listing provides three months of access. The exact plan and account conditions are confirmed on WhatsApp before payment."),
            ("Can YouTube Premium remove ads?",
             "YouTube Premium includes ad-free viewing on YouTube. Confirm the exact plan terms and account conditions with the support team before payment."),
            ("Is YouTube Premium included with YouTube Music?",
             "YouTube Premium typically includes YouTube Music. Confirm the current plan features and account conditions with the support team before payment."),
            ("What is the delivery estimate for YouTube Premium?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact the support team for current availability."),
            ("How do I order YouTube Premium?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with the support team, then receive access instructions after payment."),
        ],
    },
    "netflix": {
        "title": "Netflix Premium 4K",
        "faqs": [
            ("What does this Netflix Premium 4K listing include?",
             "This Netflix listing provides one month of access with 4K support. The exact account arrangement and conditions are confirmed on WhatsApp before payment."),
            ("Can Netflix be streamed in 4K?",
             "Netflix supports 4K streaming on compatible plans and devices. Confirm the exact plan, device compatibility, and account conditions with the support team before payment."),
            ("Can multiple people use one Netflix account?",
             "Netflix accounts support multiple profiles and simultaneous streams depending on the plan. Confirm the exact stream limit and account arrangement with the support team before payment."),
            ("What is the delivery estimate for Netflix Premium 4K?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact the support team for current availability."),
            ("How do I order Netflix Premium 4K?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with the support team, then receive access instructions after payment."),
        ],
    },
    "linkedin": {
        "title": "LinkedIn Premium",
        "faqs": [
            ("What does this LinkedIn Premium listing include?",
             "This LinkedIn listing provides two months of invitation-based Premium access. The exact account arrangement and conditions are confirmed on WhatsApp before payment."),
            ("Can LinkedIn Premium help with job searching?",
             "LinkedIn Premium includes features such as InMail and insights for job searching and networking. Review the plan features and confirm the account conditions with the support team before payment."),
            ("Can multiple people use one LinkedIn Premium invitation?",
             "Invitation-based access depends on the account arrangement. Confirm how the listing is shared and the terms of use with the support team before payment."),
            ("What is the delivery estimate for LinkedIn Premium?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact the support team for current availability."),
            ("How do I order LinkedIn Premium?",
             "Open the WhatsApp order link on this page, confirm availability, payment details, and access terms with the support team, then receive instructions after payment."),
        ],
    },
    "windows": {
        "title": "Windows 11 Pro Key",
        "faqs": [
            ("What is this Windows 11 Pro Key listing?",
             "This listing provides a Windows 11 Pro license key. The exact key type, edition, and conditions are confirmed on WhatsApp before payment."),
            ("Can I use this key to upgrade from Windows 10?",
             "Windows 11 Pro keys can sometimes be used for upgrades depending on the edition and existing license. Confirm the key type and compatibility with the support team before payment."),
            ("Is this a lifetime license?",
             "This listing is described as a lifetime license key. Review the key type, activation terms, and any regional restrictions with the support team before payment."),
            ("What is the delivery estimate for Windows 11 Pro Key?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact the support team for current availability."),
            ("How do I order Windows 11 Pro Key?",
             "Open the WhatsApp order link on this page, confirm the key type, payment details, and delivery with the support team, then receive the key after payment."),
        ],
    },
}


# ── HTML FAQ section builder ───────────────────────────────────────────────

def build_faq_html(faqs: list[tuple[str, str]]) -> str:
    """Build visible FAQ section HTML."""
    items = []
    for q, a in faqs:
        items.append(f'    <div class="faq-item">\n      <h3>{q}</h3>\n      <p>{a}</p>\n    </div>')
    return (
        '  <section class="faq-section">\n'
        '    <h2>Frequently asked questions</h2>\n'
        + "\n".join(items) +
        '\n  </section>\n'
    )


# ── JSON-LD FAQPage schema builder ────────────────────────────────────────

def build_faq_schema(faqs: list[tuple[str, str]]) -> str:
    """Build FAQPage JSON-LD schema."""
    entities = []
    for q, a in faqs:
        entities.append(
            f'    {{\n'
            f'      "@type": "Question",\n'
            f'      "name": {json.dumps(q)},\n'
            f'      "acceptedAnswer": {{\n'
            f'        "@type": "Answer",\n'
            f'        "text": {json.dumps(a)}\n'
            f'      }}\n'
            f'    }}'
        )
    return (
        '{\n'
        '  "@context": "https://schema.org",\n'
        '  "@type": "FAQPage",\n'
        '  "mainEntity": [\n'
        + ",\n".join(entities) +
        '\n  ]\n'
        '}'
    )


# ── Main update function ───────────────────────────────────────────────────

def update_tool_page(tool_dir: Path, faq_data: dict) -> bool:
    """Update a single tool page: add FAQ HTML + FAQPage schema."""
    html_file = tool_dir / "index.html"
    if not html_file.exists():
        print(f"  ✗ {html_file} not found")
        return False

    html = html_file.read_text(encoding="utf-8", errors="replace")

    # ── 1. Add FAQPage schema to existing JSON-LD ─────────────────────────
    # Find the last <script type="application/ld+json">...</script> block
    # and add FAQPage to its @graph array (or create new script if none)

    faq_schema = build_faq_schema(faq_data["faqs"])

    # Pattern: find JSON-LD script blocks
    json_ld_pattern = re.compile(
        r'(<script\s+type=["\']application/ld\+json["\']>)(.*?)(</script>)',
        re.DOTALL
    )

    faq_schema_added = False

    def add_faq_to_json_ld(match):
        nonlocal faq_schema_added
        open_tag = match.group(1)
        content = match.group(2)
        close_tag = match.group(3)

        # Try to parse as JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Invalid JSON — add as separate script
            faq_schema_added = True
            return f'{open_tag}{json.dumps(json.loads(faq_schema), indent=2)}{close_tag}'

        # If it has @graph, add FAQPage to the graph
        if isinstance(data, dict) and "@graph" in data:
            graph = data["@graph"]
            # Check if FAQPage already exists
            has_faq = any(isinstance(node, dict) and node.get("@type") == "FAQPage" for node in graph)
            if not has_faq:
                graph.append(json.loads(faq_schema))
                faq_schema_added = True
                return f'{open_tag}{json.dumps(data, indent=2)}{close_tag}'
            else:
                faq_schema_added = True
                return match.group(0)
        elif isinstance(data, list):
            has_faq = any(isinstance(node, dict) and node.get("@type") == "FAQPage" for node in data)
            if not has_faq:
                data.append(json.loads(faq_schema))
                faq_schema_added = True
                return f'{open_tag}{json.dumps(data, indent=2)}{close_tag}'
            else:
                faq_schema_added = True
                return match.group(0)
        else:
            # Single object — convert to @graph with existing + FAQPage
            graph = [data, json.loads(faq_schema)]
            faq_schema_added = True
            return f'{open_tag}{json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2)}{close_tag}'

    new_html = json_ld_pattern.sub(add_faq_to_json_ld, html)

    if not faq_schema_added:
        # No JSON-LD found — add new script before </head>
        new_script = f'<script type="application/ld+json">\n{faq_schema}\n</script>\n'
        new_html = new_html.replace("</head>", f"{new_script}</head>")
        faq_schema_added = True

    # ── 2. Add visible FAQ HTML section ───────────────────────────────────
    # Add before </main> or </body>
    faq_html = build_faq_html(faq_data["faqs"])

    if "<section class=\"faq-section\">" in new_html:
        # Already has FAQ section — skip
        print(f"  ✓ {tool_dir.name}: FAQ already present, schema updated")
        return True

    if "</main>" in new_html:
        new_html = new_html.replace("</main>", f"{faq_html}</main>")
    elif "</body>" in new_html:
        new_html = new_html.replace("</body>", f"{faq_html}</body>")
    else:
        # Append at end
        new_html = new_html.rstrip() + "\n" + faq_html + "\n"

    # ── 3. Write updated file ─────────────────────────────────────────────
    html_file.write_text(new_html, encoding="utf-8")
    print(f"  ✓ {tool_dir.name}: FAQ section + FAQPage schema added")
    return True


# ── Run for all tools ──────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Adding FAQ section + FAQPage schema to all 20 tool pages")
    print("=" * 60)

    updated = 0
    failed = 0
    already = 0

    for tool_name, faq_data in TOOL_FAQS.items():
        tool_dir = TOOLS_DIR / tool_name
        if not tool_dir.exists():
            print(f"  ✗ {tool_name}: directory not found")
            failed += 1
            continue

        result = update_tool_page(tool_dir, faq_data)
        if result is True:
            # Check if it was already present
            html_file = tool_dir / "index.html"
            html = html_file.read_text(encoding="utf-8", errors="replace")
            if "<section class=\"faq-section\">" in html:
                already += 1
            else:
                updated += 1
        else:
            failed += 1

    print()
    print("=" * 60)
    print(f"Done: {updated} updated, {already} already had FAQs, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
