#!/usr/bin/env python3
"""
SEO: Expand tool page descriptions — add 100+ more words per page.
Japan pages pe priority (current ~500 words vs PK ~950 words).
Content depth course principle: "100 more words than competitor".
"""

import re
from pathlib import Path

BASE = Path(r"D:/ai-tool-gems")

# Per-tool content expansion — additional paragraphs (100+ words each)
# These add real value: use cases, who-should-buy, comparison notes, tips
TOOL_CONTENT_EXPANSION = {
    "chatgpt": [
        "ChatGPT Plus ek general-purpose AI assistant hai jo daily writing, research, coding, aur creative tasks ke liye use hota hai. Is mein file upload, web browsing, aur advanced data analysis bhi shamil hai — jo free version mein often limit hota hai.",
        "Jo log regularly long documents edit karte hain, code debug karte hain, ya research summarize karte hain, unke liye ChatGPT Plus time-saving tool ho sakta hai. Har month ke liye ek private account access milta hai jo personal use ke liye suitable hai.",
        "Ordering se pehle confirm karein ke access type (private vs shared) aur delivery estimate aap ke timeline ke mutabiq hain. AI Tool Gems support team availability aur exact conditions WhatsApp pe confirm karti hai.",
    ],
    "gemini": [
        "Google Gemini Pro ek multimodal AI assistant hai jo text, images, aur Google services ke saath integrate hota hai. Iska faida ye hai ke agar aap Google ecosystem (Docs, Gmail, Drive) use karte hain, toh Gemini naturally fit ho jata hai.",
        "Research tasks, document analysis, aur Google-based workflows ke liye Gemini ek strong option hai. 18-month invitation-based access long-term value deta hai agar account arrange ho jaye.",
        "Gemini ke liye bhi access type aur delivery estimate confirm karna zaroori hai. Market mein conditions change ho sakti hain — WhatsApp se latest status check karein.",
    ],
    "veo": [
        "Google Veo 3 Ultra ek AI video generation model hai jo text prompts se cinematic videos create karta hai. Isme realistic motion, audio-capable workflows, aur high-quality output shamil hain.",
        "Creators, advertisers, aur content teams ke liye Veo ek powerful tool ho sakta hai — khas taur par jab quick video drafts ya concept visualizations chahiye hon. Shared access plan limited users ke liye hai.",
        "Video generation ke results prompt quality aur account conditions par depend karte hain. Ordering se pehle confirm karein ke account type aur usage terms aap ke project ke liye suitable hain.",
    ],
    "canva": [
        "Canva Pro invitation-based access social media posts, pitch decks, presentations, aur branded assets banane ke liye hai. Premium templates, brand kits, aur export options iski key features hain.",
        "Students, startups, aur small teams ke liye Canva Pro ek practical choice hai — khas taur par jab team mein design expertise limited ho. One-year invitation plan long-term stability deta hai.",
        "Invitation-based access ka matlab hai ke seat arrangement confirm karni hogi. Order se pehle WhatsApp se confirm karein ke how many users supported hain aur access kaise share hota hai.",
    ],
    "figma": [
        "Figma Pro private access interface design, prototyping, aur design system collaboration ke liye hai. Professional UI/UX teams ke liye isme advanced features, team libraries, aur developer handoff shamil hain.",
        "Client projects ya product teams ke liye Figma ek industry-standard tool hai. Two-year private access long-term cost savings deta hai agar account properly arranged ho.",
        "Client work ke liye Figma use karne se pehle commercial use terms aur account conditions confirm karein. WhatsApp support current availability confirm karti hai.",
    ],
    "elevenlabs": [
        "ElevenLabs ek AI voice generation platform hai jo realistic speech, dubbing, aur permitted voice cloning workflows ke liya use hota hai. Video narration, podcasts, aur media projects ke liye popular hai.",
        "One-month private access try karne ke liye suitable hai agar aap voice-based content experiment kar rahe hain. Voice cloning features ke liye consent aur usage terms confirm karna zaroori hai.",
        "YouTube aur video narration ke liye ElevenLabs commonly use hota hai. Commercial use terms aur plan details WhatsApp se confirm karein — features plan level par change ho sakte hain.",
    ],
    "adobe": [
        "Adobe Creative Cloud do months ke liye Photoshop, Illustrator, Premiere Pro, After Effects, aur Firefly shamil karta hai. Professional creative work ke liye complete suite hai.",
        "Jo log multi-format creative work karte hain — photo editing, vector design, video, ya animation — unke liye Adobe ecosystem practical hai. Exact apps plan level par depend karte hain.",
        "Commercial creative work ke liye Adobe license terms review karein. WhatsApp se confirm karein ke plan mein kaunse apps shamil hain aur account conditions kya hain.",
    ],
    "capcut": [
        "CapCut Pro ek month ke liye video editing suite hai — TikTok, Instagram Reels, aur YouTube Shorts ke liye optimized. Watermark-free exports, effects, aur quick editing features shamil hain.",
        "Short-form video creators ke liye CapCut ek go-to tool hai. Pro access watermark-free exports aur advanced editing features deta hai jo free version mein limited hoti hain.",
        "Export terms aur plan features confirm karein — khaas taur par agar aap commercial content banate hain. WhatsApp se current plan details verify karein.",
    ],
    "n8n": [
        "n8n Starter ek workflow automation platform hai — AI agents, APIs, aur business logic ko connect karta hai. One-year access long-term automation setup ke liye suitable hai.",
        "Jo log custom workflows, integrations, ya AI-powered automations build karte hain, unke liye n8n powerful option hai. Self-hosted ya cloud — dono options hain.",
        "Automation projects ke liye confirm karein ke plan limitations, integrations, aur usage limits aap ke needs ke mutabiq hain. WhatsApp se exact conditions check karein.",
    ],
    "notion": [
        "Notion Business invitation-based access notes, databases, aur team knowledge management ke liye hai. Three-month access trial ke liye suitable hai agar team setup kar rahi ho.",
        "Teams, startups, aur knowledge-heavy workflows ke liye Notion practical hai. Invitation-based access ka matlab hai ke seat arrangement confirm karni hogi.",
        "Multi-user access ke liye confirm karein ke listing kitne users support karti hai aur access kaise share hota hai. WhatsApp se latest status check karein.",
    ],
    "gamma": [
        "Gamma Pro ek AI presentation aur document tool hai — raw ideas, briefs, aur outlines se interactive presentations, decks, aur web pages banata hai. One-year Pro access long-term value deta hai.",
        "Business presentations, pitching, aur document creation ke liye Gamma useful hai. Export options check karein agar aapko PowerPoint ya other formats chahiye hain.",
        "Export compatibility aur plan features WhatsApp se confirm karein. Gamma ke output quality aur licensing terms project ke liye suitable hona chahiye.",
    ],
    "replit": [
        "Replit Core ek online development environment hai — coding, collaboration, hosting, aur AI assistance shamil hai. $40 credits ke sath one private plan development aur experimentation ke liye suitable hai.",
        "Jo log web apps build karte hain, code experiment karte hain, ya AI-assisted development try karte hain, unke liye Replit useful hai. Hosting capabilities aur resource limits check karein.",
        "Production projects ke liye hosting terms, resource limits, aur export options review karein. WhatsApp se confirm karein ke account conditions aur credits ka correct usage kya hai.",
    ],
    "lovable": [
        "Lovable Pro ek AI-powered development tool hai — web applications build karne ke liye natural language se. One-month Pro access experiment aur prototyping ke liye suitable hai.",
        "Beginners aur experienced builders dono ke liye Lovable accessible hai. Output quality, export options, aur licensing terms commercial use se pehle review karne chahiye.",
        "Production websites ke liye confirm karein ke generated projects ki quality, export compatibility, aur terms suitable hain. WhatsApp se current plan details check karein.",
    ],
    "nordvpn": [
        "NordVPN three months ke liye encrypted browsing, high-speed servers, aur threat protection shamil karta hai. Public Wi-Fi security aur privacy-focused users ke liye practical hai.",
        "Multiple device connections plan ke hisaab se hoti hain. Confirm karein ke kitne simultaneous connections support hain — especially agar aapke paas multiple devices hain.",
        "Service terms aur account conditions WhatsApp se confirm karein. Public network security ke liye NordVPN ek common choice hai, lekin exact plan details verify karein.",
    ],
    "surfshark": [
        "Surfshark two months shared access ke liye reliable privacy, geo-unblocking, aur unlimited device connections shamil hain. Everyday privacy aur content access ke liye popular hai.",
        "Unlimited simultaneous connections ka matlab hai ke multiple devices same account se use kar sakti hain — family ya multi-device users ke liye value hai.",
        "Shared access ke conditions confirm karein — account arrangement, usage terms, aur delivery estimate WhatsApp se verify karein. Streaming usage ke liye terms check karein.",
    ],
    "youtube": [
        "YouTube Premium three months ke liye ad-free viewing, background play on mobile, offline downloads, aur YouTube Music shamil karta hai. Mobile users aur music listeners ke liye value hai.",
        "Ad-free experience aur background play mobile viewing ke liye main benefit hain. YouTube Music included hota hai — ek additional entertainment value.",
        "Plan features aur account conditions confirm karein. WhatsApp se verify karein ke listing exact terms, duration, aur access type kya hai.",
    ],
    "netflix": [
        "Netflix Premium 4K one month ke liye global movies aur series, 4K Ultra HD, aur spatial audio shamil karta hai. Compatible device aur plan details important hain.",
        "4K streaming compatible plans aur devices par depend karta hai. Confirm karein ke aapke device 4K support karte hain aur plan suitable hai.",
        "Multiple profiles aur simultaneous streams plan ke hisaab se hote hain. WhatsApp se confirm karein ke stream limit aur account arrangement kya hai.",
    ],
    "linkedin": [
        "LinkedIn Premium two months invitation-based access ke liye InMail, job search insights, aur professional learning features shamil hain. Job seekers aur professionals ke liye value hai.",
        "InMail aur job search insights LinkedIn Premium ki key features hain. Invitation-based access ka matlab hai ke account arrangement confirm karni hogi.",
        "Account arrangement aur terms of use WhatsApp se confirm karein. Invitation-based listings ke liye check karein ke listing kaise share hoti hai aur terms kya hain.",
    ],
    "windows": [
        "Windows 11 Pro license key ek digital activation key hai — exact key type, edition, aur conditions WhatsApp se confirm karne chahiye. Lifetime license claim verify karni chahiye.",
        "Windows 10 se upgrade ke liye compatibility check karein — key type aur existing license depend karte hain. Regional restrictions bhi confirm karne chahiye.",
        "Lifetime license ka claim review karein — key type, activation terms, aur regional restrictions WhatsApp se confirm karein. Har listing ki exact details verify karein.",
    ],
}

# Japan pages ke liye same content (Japanese context mein use hone ke liye)
# Actually, since these are English descriptions, we use them on JP pages too
# as bilingual context — or translate later. For now, add English expansion.


def expand_jp_tool_page(page_path: Path, tool_name: str) -> bool:
    """Expand a Japan tool page description with 100+ more English words.
    Adds content before the closing </section> of product-copy or article.
    """
    html = page_path.read_text(encoding="utf-8", errors="replace")

    if tool_name not in TOOL_CONTENT_EXPANSION:
        print(f"  ✗ {tool_name}: no expansion content available")
        return False

    expansions = TOOL_CONTENT_EXPANSION[tool_name]

    # Find the lead paragraph section and add expansions after it
    # Target: after <p class="lead">...</p> or after the first </section> in product-copy
    lead_pattern = re.compile(
        r'(<p class="lead">.*?</p>)',
        re.DOTALL
    )

    if lead_pattern.search(html):
        # Insert after lead paragraph
        lead_match = lead_pattern.search(html)
        insert_after = lead_match.end()
        new_content = "\n".join(f"      {p}" for p in expansions)
        html = html[:insert_after] + "\n" + new_content + html[insert_after:]
        page_path.write_text(html, encoding="utf-8")
        print(f"  ✓ {tool_name}: +{sum(len(p.split()) for p in expansions)} words added")
        return True

    # Fallback: insert before first </section> in product-copy/article
    section_pattern = re.compile(
        r'(<section class="product-copy">.*?)(</section>)',
        re.DOTALL
    ) | re.compile(
        r'(<article class="product-layout">.*?)(</article>)',
        re.DOTALL
    )

    for pattern in [re.compile(r'(<section class="product-copy">.*?)(</section>)', re.DOTALL),
                    re.compile(r'(<article class="product-layout">.*?)(</article>)', re.DOTALL)]:
        match = pattern.search(html)
        if match:
            insert_after = match.group(1).rfind(">") + 1
            new_content = "\n".join(f"      {p}" for p in expansions)
            html = html[:insert_after] + "\n" + new_content + html[insert_after:]
            page_path.write_text(html, encoding="utf-8")
            print(f"  ✓ {tool_name}: +{sum(len(p.split()) for p in expansions)} words added (fallback)")
            return True

    print(f"  ✗ {tool_name}: could not find insertion point")
    return False


def main():
    print("=" * 70)
    print("📝 SEO: Expand Tool Page Descriptions")
    print("=" * 70)

    target_dirs = [
        (BASE / "jp" / "tools", "JP — priority"),
    ]

    total_added = 0
    for tool_dir, label in target_dirs:
        if not tool_dir.exists():
            print(f"\n⚠ Directory not found: {tool_dir}")
            continue
        print(f"\n📁 {label}/")
        for tool_dir_name in sorted(tool_dir.iterdir()):
            if not tool_dir_name.is_dir():
                continue
            page = tool_dir_name / "index.html"
            if not page.exists():
                print(f"  ✗ {tool_dir_name.name}: page not found")
                continue
            if expand_jp_tool_page(page, tool_dir_name.name):
                total_added += 1

    print("\n" + "=" * 70)
    print(f"✅ Complete!")
    print(f"   Pages expanded: {total_added}")
    print("=" * 70)


if __name__ == "__main__":
    main()