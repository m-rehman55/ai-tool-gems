#!/usr/bin/env python3
"""
SEO Crash Course Follow-up: Add FAQSection + FAQPage schema to all tool pages.
Run: python add_faq_all_tools.py
"""

import os
import re
import json
from pathlib import Path

# ── Tool directories (Pakistan + Japan) ──────────────────────────────────
TOOL_DIRS = [
    Path(r"D:/ai-tool-gems/tools"),
    Path(r"D:/ai-tool-gems/jp/tools"),
]

# ── Sabhi 20 tools ke liye FAQs ──────────────────────────────────────────
TOOL_FAQS = {
    "chatgpt": {
        "price": "Rs. 2,300",
        "faqs": [
            ("Is this ChatGPT Plus account private?",
             "AI Tool Gems lists ChatGPT Plus access intended for the buyer. The exact access type and account conditions are confirmed on WhatsApp before payment."),
            ("What is the delivery time for ChatGPT Plus?",
             "The listed delivery estimate is 15–30 minutes. The exact timing is reconfirmed with the support team on WhatsApp before payment."),
            ("What warranty comes with this listing?",
             "This listing includes a 7-day replacement warranty. Full warranty terms are on the policies page."),
            ("Can I use ChatGPT Plus for commercial work?",
             "ChatGPT Plus can be used for writing, research, coding, file analysis, and image tasks. Review OpenAI's terms for commercial use before uploading confidential data."),
            ("How do I order ChatGPT Plus from AI Tool Gems?",
             "Open the WhatsApp order link on this page, confirm availability and payment details with our support team, then receive access instructions after payment."),
        ],
    },
    "gemini": {
        "price": "Rs. 800",
        "faqs": [
            ("Is Gemini Pro access private or invitation-based?",
             "This Gemini Pro listing is described as invitation access. The exact account arrangement and conditions are confirmed on WhatsApp before payment."),
            ("What is the delivery estimate for Gemini Pro?",
             "The listed delivery estimate is 10–20 minutes. The final timing is reconfirmed on WhatsApp before payment."),
            ("What warranty is included with this listing?",
             "The listing includes an 18-month replacement warranty. Full warranty terms are explained on the policies page."),
            ("Can Gemini Pro be used with Google services?",
             "Gemini integrates with Google's ecosystem. Confirm the exact plan and access terms with our support team before payment, because features and availability can change."),
            ("How do I buy Gemini Pro from AI Tool Gems?",
             "Open the WhatsApp order link on this page, confirm availability, payment, and access details with our support team, then receive instructions after payment."),
        ],
    },
    "veo": {
        "price": "Rs. 2,100",
        "faqs": [
            ("What kind of access does Veo 3 Ultra provide?",
             "This Veo 3 Ultra listing is described as a shared access plan. Confirm the exact account arrangement and usage conditions on WhatsApp before payment."),
            ("Can Veo 3 generate videos from text prompts?",
             "Veo is Google's video generation model. Confirm the current capabilities, limits, and access terms with our support team, because model features can change over time."),
            ("What is the delivery time for Veo 3 Ultra?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact our support team for the current availability and timing."),
            ("Does Veo 3 Ultra support commercial video projects?",
             "Review the account's terms and Google's usage policies before using any generated video for commercial work. Confirm the exact access conditions with our support team."),
            ("How do I order Veo 3 Ultra from AI Tool Gems?",
             "Open the WhatsApp order link on this page, confirm availability and payment details with our support team, then receive access instructions after payment."),
        ],
    },
    "leonardo": {
        "price": "Rs. 1,900",
        "faqs": [
            ("What does Leonardo AI Essential include?",
             "This listing provides Leonardo AI credits for image generation. The exact credit amount and usage terms are confirmed on WhatsApp before payment."),
            ("Can Leonardo AI generate images from text prompts?",
             "Leonardo AI is built for AI image generation and editing. Confirm the current plans, models, and limits with our support team before payment."),
            ("Is Leonardo AI suitable for commercial design work?",
             "Review Leonardo's terms for commercial use and the license attached to generated images. Confirm the exact access conditions with our support team before using outputs commercially."),
            ("What is the delivery estimate for Leonardo AI credits?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact our support team for current availability."),
            ("How do I order Leonardo AI Essential?",
             "Open the WhatsApp order link on this page, confirm the credit amount, payment details, and delivery with our support team, then receive access instructions after payment."),
        ],
    },
    "elevenlabs": {
        "price": "Rs. 3,300",
        "faqs": [
            ("What does ElevenLabs access include?",
             "This ElevenLabs listing provides one month of access for AI voice generation. The exact plan and usage terms are confirmed on WhatsApp before payment."),
            ("Can ElevenLabs clone voices?",
             "ElevenLabs offers voice cloning features. Confirm which plan level and features are included in this listing, and review the consent and usage terms before cloning any voice."),
            ("Is ElevenLabs suitable for YouTube and video narration?",
             "ElevenLabs is commonly used for video narration and voiceovers. Review the commercial use terms and confirm the plan details with our support team before payment."),
            ("What is the delivery time for ElevenLabs?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact our support team for current availability and timing."),
            ("How do I order ElevenLabs from AI Tool Gems?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with our support team, then receive access instructions after payment."),
        ],
    },
    "canva": {
        "price": "Rs. 900",
        "faqs": [
            ("What is Canva Pro Edu access?",
             "This Canva listing is described as an invitation-based Pro plan. The exact seat arrangement and conditions are confirmed on WhatsApp before payment."),
            ("Can Canva Pro be used for commercial design work?",
             "Canva Pro includes premium templates, brand kits, and export options useful for commercial design. Review Canva's license terms for commercial use and confirm the plan details with our support team."),
            ("What is the delivery estimate for Canva Pro?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact our support team for current availability."),
            ("Can multiple people use one Canva Pro invitation?",
             "Invitation-based access depends on the seat arrangement. Confirm how many users the listing supports and how access is shared before payment."),
            ("How do I order Canva Pro Edu from AI Tool Gems?",
             "Open the WhatsApp order link on this page, confirm availability, payment, and access details with our support team, then receive instructions after payment."),
        ],
    },
    "figma": {
        "price": "Rs. 3,000",
        "faqs": [
            ("What is Figma Pro Private access?",
             "This Figma listing is described as private access for two years. The exact account arrangement and conditions are confirmed on WhatsApp before payment."),
            ("Can Figma Pro be used for commercial UI/UX design?",
             "Figma Pro includes features for professional interface design, prototyping, and team collaboration. Review Figma's license terms and confirm the plan details with our support team before payment."),
            ("What is the delivery estimate for Figma Pro?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact our support team for current availability."),
            ("Can I use Figma Pro for client projects?",
             "Figma is widely used for client interface design work. Review the commercial use terms and confirm the account conditions with our support team before using it for client work."),
            ("How do I order Figma Pro Private?",
             "Open the WhatsApp order link on this page, confirm availability, payment details, and access terms with our support team, then receive instructions after payment."),
        ],
    },
    "capcut": {
        "price": "Rs. 900",
        "faqs": [
            ("What does CapCut Pro include?",
             "This CapCut listing provides one month of Pro access for video editing. The exact plan and features are confirmed on WhatsApp before payment."),
            ("Can CapCut Pro remove watermarks?",
             "CapCut Pro includes features that help with watermark-free editing and exports. Confirm the exact export terms and plan details with our support team before payment."),
            ("Is CapCut Pro good for TikTok and Instagram Reels?",
             "CapCut is widely used for short-form video editing on TikTok, Instagram Reels, and YouTube Shorts. Review the export and licensing terms and confirm the plan with our support team."),
            ("What is the delivery time for CapCut Pro?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact our support team for current availability."),
            ("How do I order CapCut Pro from AI Tool Gems?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with our support team, then receive access instructions after payment."),
        ],
    },
    "adobe": {
        "price": "Rs. 1,700",
        "faqs": [
            ("What does this Adobe Creative Cloud listing include?",
             "This listing provides two months of Adobe Creative Cloud access. The exact apps included and account conditions are confirmed on WhatsApp before payment."),
            ("Which Adobe apps are included?",
             "Adobe Creative Cloud includes apps such as Photoshop, Illustrator, Premiere Pro, and others depending on the plan. Confirm the exact apps and plan level with our support team before payment."),
            ("Can Adobe Creative Cloud be used for commercial work?",
             "Adobe Creative Cloud is designed for professional creative work. Review Adobe's license terms for commercial use and confirm the account conditions with our support team before payment."),
            ("What is the delivery estimate for Adobe Creative Cloud?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact our support team for current availability."),
            ("How do I order Adobe Creative Cloud from AI Tool Gems?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with our support team, then receive access instructions after payment."),
        ],
    },
    "lovable": {
        "price": "Rs. 1,600",
        "faqs": [
            ("What is Lovable Pro?",
             "Lovable is an AI-powered development tool for building web applications. This listing provides one month of Pro access. The exact plan and features are confirmed on WhatsApp before payment."),
            ("Can Lovable be used to build production websites?",
             "Lovable is designed to help build web applications with AI assistance. Review the output quality, export options, and licensing terms before using any generated project for production work."),
            ("What is the delivery estimate for Lovable Pro?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact our support team for current availability."),
            ("Is Lovable suitable for beginners?",
             "Lovable is built to make web development more accessible with AI assistance. Confirm the current features and learning curve with our support team before payment."),
            ("How do I order Lovable Pro from AI Tool Gems?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with our support team, then receive access instructions after payment."),
        ],
    },
    "gamma": {
        "price": "Rs. 23,000",
        "faqs": [
            ("What is Gamma Pro?",
             "Gamma is an AI presentation and document tool. This listing provides one year of Pro access. The exact plan and features are confirmed on WhatsApp before payment."),
            ("Can Gamma Pro be used for business presentations?",
             "Gamma is built for creating presentations, documents, and web pages with AI assistance. Review the export options and commercial use terms before using Gamma outputs for business work."),
            ("What is the delivery estimate for Gamma Pro?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact our support team for current availability."),
            ("Can Gamma export to PowerPoint?",
             "Gamma supports export to multiple formats. Confirm the current export options and compatibility with our support team before payment."),
            ("How do I order Gamma Pro from AI Tool Gems?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with our support team, then receive access instructions after payment."),
        ],
    },
    "replit": {
        "price": "Rs. 3,200",
        "faqs": [
            ("What is Replit Core?",
             "Replit Core provides development environment access with AI assistance. This listing includes $40 in credits. The exact plan and usage terms are confirmed on WhatsApp before payment."),
            ("Can Replit be used to build and host web apps?",
             "Replit provides an online development environment with hosting capabilities. Review the hosting terms, resource limits, and export options before using Replit for production projects."),
            ("What is the delivery estimate for Replit Core?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact our support team for current availability."),
            ("Is Replit suitable for learning to code?",
             "Replit is commonly used for learning and experimenting with code in multiple languages. Confirm the current features and plan details with our support team before payment."),
            ("How do I order Replit Core from AI Tool Gems?",
             "Open the WhatsApp order link on this page, confirm the credit amount, payment details, and delivery with our support team, then receive access instructions after payment."),
        ],
    },
    "n8n": {
        "price": "Rs. 7,000",
        "faqs": [
            ("What is n8n Starter?",
             "n8n is a workflow automation platform. This listing provides one year of access. The exact plan and usage terms are confirmed on WhatsApp before payment."),
            ("Can n8n connect to Google, Slack, and other services?",
             "n8n supports many integrations for workflow automation. Confirm the current integrations and plan limits with our support team before payment."),
            ("Is n8n suitable for business automation?",
             "n8n is designed for workflow and business process automation. Review the commercial use terms and confirm the account conditions with our support team before payment."),
            ("What is the delivery estimate for n8n Starter?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact our support team for current availability."),
            ("How do I order n8n Starter from AI Tool Gems?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with our support team, then receive access instructions after payment."),
        ],
    },
    "notion": {
        "price": "Rs. 2,200",
        "faqs": [
            ("What is Notion Business access?",
             "This Notion listing is described as invitation-based Business access for three months. The exact seat arrangement and conditions are confirmed on WhatsApp before payment."),
            ("Can Notion be used for team knowledge management?",
             "Notion is widely used for notes, databases, and team knowledge management. Review the plan terms and confirm the seat arrangement with our support team before payment."),
            ("What is the delivery estimate for Notion Business?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact our support team for current availability."),
            ("Can multiple team members use one Notion Business invitation?",
             "Invitation-based access depends on the seat arrangement. Confirm how many users the listing supports and how access is shared before payment."),
            ("How do I order Notion Business from AI Tool Gems?",
             "Open the WhatsApp order link on this page, confirm availability, payment details, and access terms with our support team, then receive instructions after payment."),
        ],
    },
    "nordvpn": {
        "price": "Rs. 1,800",
        "faqs": [
            ("What does this NordVPN listing include?",
             "This NordVPN listing provides three months of access. The exact plan and account conditions are confirmed on WhatsApp before payment."),
            ("Can NordVPN be used on multiple devices?",
             "NordVPN supports multiple simultaneous connections depending on the plan. Confirm the exact device limit and plan details with our support team before payment."),
            ("Is NordVPN suitable for public Wi-Fi security?",
             "NordVPN is designed to encrypt internet traffic and improve privacy on public networks. Review the service terms and confirm the plan details with our support team before payment."),
            ("What is the delivery estimate for NordVPN?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact our support team for current availability."),
            ("How do I order NordVPN from AI Tool Gems?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with our support team, then receive access instructions after payment."),
        ],
    },
    "surfshark": {
        "price": "Rs. 800",
        "faqs": [
            ("What does this Surfshark VPN listing include?",
             "This Surfshark listing provides two months of shared access. The exact account arrangement and conditions are confirmed on WhatsApp before payment."),
            ("Can Surfshark be used on multiple devices?",
             "Surfshark supports unlimited simultaneous connections on its plans. Confirm the exact plan and account conditions with our support team before payment."),
            ("Is Surfshark suitable for streaming?",
             "Surfshark is commonly used for privacy and accessing content across regions. Review the service terms and confirm the plan details with our support team before payment."),
            ("What is the delivery estimate for Surfshark VPN?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact our support team for current availability."),
            ("How do I order Surfshark VPN from AI Tool Gems?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with our support team, then receive access instructions after payment."),
        ],
    },
    "youtube": {
        "price": "Rs. 1,200",
        "faqs": [
            ("What does this YouTube Premium listing include?",
             "This YouTube Premium listing provides three months of access. The exact plan and account conditions are confirmed on WhatsApp before payment."),
            ("Can YouTube Premium remove ads?",
             "YouTube Premium includes ad-free viewing on YouTube. Confirm the exact plan terms and account conditions with our support team before payment."),
            ("Is YouTube Premium included with YouTube Music?",
             "YouTube Premium typically includes YouTube Music. Confirm the current plan features and account conditions with our support team before payment."),
            ("What is the delivery estimate for YouTube Premium?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact our support team for current availability."),
            ("How do I order YouTube Premium from AI Tool Gems?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with our support team, then receive access instructions after payment."),
        ],
    },
    "netflix": {
        "price": "Rs. 400",
        "faqs": [
            ("What does this Netflix Premium 4K listing include?",
             "This Netflix listing provides one month of access with 4K support. The exact account arrangement and conditions are confirmed on WhatsApp before payment."),
            ("Can Netflix be streamed in 4K?",
             "Netflix supports 4K streaming on compatible plans and devices. Confirm the exact plan, device compatibility, and account conditions with our support team before payment."),
            ("Can multiple people use one Netflix account?",
             "Netflix accounts support multiple profiles and simultaneous streams depending on the plan. Confirm the exact stream limit and account arrangement with our support team before payment."),
            ("What is the delivery estimate for Netflix Premium 4K?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact our support team for current availability."),
            ("How do I order Netflix Premium 4K from AI Tool Gems?",
             "Open the WhatsApp order link on this page, confirm the plan, payment details, and delivery with our support team, then receive access instructions after payment."),
        ],
    },
    "linkedin": {
        "price": "Rs. 1,500",
        "faqs": [
            ("What does this LinkedIn Premium listing include?",
             "This LinkedIn listing provides two months of invitation-based Premium access. The exact account arrangement and conditions are confirmed on WhatsApp before payment."),
            ("Can LinkedIn Premium help with job searching?",
             "LinkedIn Premium includes features such as InMail and insights for job searching and networking. Review the plan features and confirm the account conditions with our support team before payment."),
            ("Can multiple people use one LinkedIn Premium invitation?",
             "Invitation-based access depends on the account arrangement. Confirm how the listing is shared and the terms of use with our support team before payment."),
            ("What is the delivery estimate for LinkedIn Premium?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact our support team for current availability."),
            ("How do I order LinkedIn Premium from AI Tool Gems?",
             "Open the WhatsApp order link on this page, confirm availability, payment details, and access terms with our support team, then receive instructions after payment."),
        ],
    },
    "windows": {
        "price": "Rs. 1,900",
        "faqs": [
            ("What is this Windows 11 Pro Key listing?",
             "This listing provides a Windows 11 Pro license key. The exact key type, edition, and conditions are confirmed on WhatsApp before payment."),
            ("Can I use this key to upgrade from Windows 10?",
             "Windows 11 Pro keys can sometimes be used for upgrades depending on the edition and existing license. Confirm the key type and compatibility with our support team before payment."),
            ("Is this a lifetime license?",
             "This listing is described as a lifetime license key. Review the key type, activation terms, and any regional restrictions with our support team before payment."),
            ("What is the delivery estimate for Windows 11 Pro Key?",
             "The delivery estimate is confirmed on WhatsApp before payment. Contact our support team for current availability."),
            ("How do I order this Windows 11 Pro Key?",
             "Open the WhatsApp order link on this page, confirm the key type, payment details, and delivery with our support team, then receive the key after payment."),
        ],
    },
}


# ── Helpers ────────────────────────────────────────────────────────────────

def build_faq_schema_jsonld(faqs):
    """Build FAQPage JSON-LD schema string."""
    main_entities = []
    for q, a in faqs:
        main_entities.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": a,
            },
        })

    faq_page = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": main_entities,
    }
    return json.dumps(faq_page, ensure_ascii=False, indent=2)


def build_visible_faq_html(faqs, tool_name):
    """Build visible FAQ section HTML to insert into page."""
    items_html = ""
    for q, a in faqs:
        items_html += f"""      <div class="faq-item">
        <h3>{q}</h3>
        <p>{a}</p>
      </div>
"""
    return f"""  <section class="faq-section">
    <h2>Frequently asked questions — {tool_name}</h2>
{items_html}  </section>
"""


# ── Page updater ───────────────────────────────────────────────────────────

def update_tool_page(page_path: Path, tool_name: str, faqs: list, price: str):
    """Update a single tool page: add visible FAQ section + FAQPage JSON-LD schema."""
    html = page_path.read_text(encoding="utf-8", errors="replace")

    # Skip if FAQ already exists
    if 'class="faq-section"' in html:
        print(f"  ⚠ {tool_name}: FAQ section already present")
        return False

    # Skip if FAQPage schema already exists
    if '"@type": "FAQPage"' in html:
        print(f"  ⚠ {tool_name}: FAQPage schema already present")
        return False

    # ── 1. Add visible FAQ section ──────────────────────────────────────
    faq_html = build_visible_faq_html(faqs, tool_name)

    # Try inserting before </main>
    if "</main>" in html:
        html = html.replace("</main>", faq_html + "</main>")
    elif "</body>" in html:
        html = html.replace("</body>", faq_html + "</body>")
    else:
        # Fallback: before last </section>
        parts = html.rsplit("</section>", 1)
        if len(parts) == 2:
            html = parts[0] + faq_html + "</section>" + parts[1]
        else:
            print(f"  ✗ {tool_name}: could not find insertion point")
            return False

    # ── 2. Add FAQPage JSON-LD schema ────────────────────────────────────
    faq_schema = build_faq_schema_jsonld(faqs)

    # Find existing JSON-LD script and add FAQPage to @graph
    jsonld_pattern = re.compile(
        r'(<script\s+type=["\']application/ld\+json["\']>)(.*?)(</script>)',
        re.DOTALL
    )

    def add_faq_to_graph(match):
        pre = match.group(1)
        content = match.group(2).strip()
        post = match.group(3)

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return f'{pre}\n{faq_schema}\n{post}'

        if isinstance(data, dict) and "@graph" in data:
            graph = data["@graph"]
            if not any(isinstance(n, dict) and n.get("@type") == "FAQPage" for n in graph):
                graph.append(json.loads(faq_schema))
                return f'{pre}\n{json.dumps(data, ensure_ascii=False, indent=2)}\n{post}'
            return match.group(0)
        elif isinstance(data, list):
            if not any(isinstance(n, dict) and n.get("@type") == "FAQPage" for n in data):
                data.append(json.loads(faq_schema))
                return f'{pre}\n{json.dumps(data, ensure_ascii=False, indent=2)}\n{post}'
            return match.group(0)
        elif isinstance(data, dict):
            graph = [data, json.loads(faq_schema)]
            wrapped = {"@context": "https://schema.org", "@graph": graph}
            return f'{pre}\n{json.dumps(wrapped, ensure_ascii=False, indent=2)}\n{post}'
        else:
            return match.group(0)

    new_html = jsonld_pattern.sub(add_faq_to_graph, html)

    # If no JSON-LD found, add before </head>
    if '"@type": "FAQPage"' not in new_html:
        if "</head>" in new_html:
            new_html = new_html.replace(
                "</head>",
                f'<script type="application/ld+json">\n{faq_schema}\n</script>\n</head>'
            )
        elif "<body>" in new_html:
            new_html = new_html.replace(
                "<body>",
                f'<script type="application/ld+json">\n{faq_schema}\n</script>\n<body>',
                1
            )

    # ── 3. Write back ─────────────────────────────────────────────────────
    page_path.write_text(new_html, encoding="utf-8")
    print(f"  ✓ {tool_name}: FAQ section + FAQPage schema added")
    return True


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("🤖 AI Tool Gems — SEO Crash Course Implementation")
    print("Adding FAQ sections + FAQPage schema to all tool pages")
    print("=" * 60)

    updated = 0
    skipped = 0
    failed = 0

    for tool_dir in TOOL_DIRS:
        if not tool_dir.exists():
            print(f"\n⚠ Directory not found: {tool_dir}")
            continue

        rel_path = tool_dir.relative_to(Path(r"D:/ai-tool-gems"))
        print(f"\n📁 {rel_path}/")

        for tool_name, tool_data in TOOL_FAQS.items():
            page_path = tool_dir / tool_name / "index.html"
            if not page_path.exists():
                print(f"  ✗ {tool_name}: page not found")
                failed += 1
                continue

            success = update_tool_page(page_path, tool_name, tool_data["faqs"], tool_data["price"])
            if success:
                updated += 1
            else:
                skipped += 1

    print("\n" + "=" * 60)
    print(f"✅ Complete!")
    print(f"   Updated: {updated} pages")
    print(f"   Skipped: {skipped} pages (already had FAQ)")
    print(f"   Failed:  {failed} pages")
    print("=" * 60)


if __name__ == "__main__":
    main()
