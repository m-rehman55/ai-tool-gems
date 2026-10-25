#!/usr/bin/env python3
"""
Regenerates llms.txt and llms-full.txt to contain all 40 verified tools
with exact PKR & USD dual pricing, domestic & global payment rails, and
truthful fulfillment terms conforming to Google Search Central and GMC.
"""

from pathlib import Path
import re

BASE = Path(__file__).resolve().parent.parent

# Complete dictionary of 40 products matching app.js
PRODUCTS = [
    {"id": "chatgpt", "name": "ChatGPT Plus", "pkr": 2300, "usd": "8.99", "duration": "1 Month", "access": "Private", "warranty": "7 Days", "desc": "GPT-4o, advanced coding, DALL-E 3 image generation, file analysis & custom GPTs."},
    {"id": "gemini", "name": "Google Gemini Pro", "pkr": 800, "usd": "3.99", "duration": "18 Months", "access": "Invitation", "warranty": "30 Days", "desc": "2TB Google Drive cloud storage, 2M token context, Docs & Gmail integrations."},
    {"id": "veo", "name": "Veo 3 Ultra", "pkr": 2100, "usd": "8.49", "duration": "Unlimited", "access": "Shared", "warranty": "7 Days", "desc": "Text-to-video workflow, audio-capable generation, 1080p output & consistent motion."},
    {"id": "leonardo", "name": "Leonardo AI Essential", "pkr": 1900, "usd": "7.49", "duration": "8,500 Credits", "access": "Private", "warranty": "7 Days", "desc": "PhotoReal & Alchemy pipeline, prompt enhancer, 8,500 credits & commercial use."},
    {"id": "elevenlabs", "name": "ElevenLabs Voice AI", "pkr": 3300, "usd": "12.99", "duration": "1 Month", "access": "Private", "warranty": "7 Days", "desc": "Multilingual voice synthesis, voice cloning, monthly credit allowance & audio dubbing."},
    {"id": "canva", "name": "Canva Pro Edu", "pkr": 900, "usd": "3.99", "duration": "1 Year", "access": "Invitation", "warranty": "30 Days", "desc": "100M+ premium stock assets, Magic Studio AI tools, background removal & brand kits."},
    {"id": "figma", "name": "Figma Pro Private", "pkr": 3000, "usd": "11.99", "duration": "2 Years", "access": "Private", "warranty": "30 Days", "desc": "Unlimited version history, Dev Mode inspection, shared team libraries & prototypes."},
    {"id": "capcut", "name": "CapCut Pro VIP", "pkr": 900, "usd": "3.99", "duration": "1 Month", "access": "Private", "warranty": "7 Days", "desc": "Pro transitions, auto speech-to-text captions, AI background removal & 4K export."},
    {"id": "adobe", "name": "Adobe Creative Cloud", "pkr": 1700, "usd": "6.99", "duration": "2 Months", "access": "Private", "warranty": "7 Days", "desc": "Photoshop, Illustrator, Premiere Pro, After Effects, Firefly credits & 100GB cloud."},
    {"id": "lovable", "name": "Lovable Pro", "pkr": 1600, "usd": "6.49", "duration": "1 Month", "access": "Private", "warranty": "7 Days", "desc": "Full-stack AI web app builder, GitHub export, custom domains & natural language code."},
    {"id": "gamma", "name": "Gamma Pro", "pkr": 23000, "usd": "89.99", "duration": "1 Year", "access": "Private", "warranty": "30 Days", "desc": "Unlimited AI presentation cards, custom branding, deck analytics & PDF/PPT export."},
    {"id": "replit", "name": "Replit Core", "pkr": 3200, "usd": "12.49", "duration": "$40 Credits", "access": "Private", "warranty": "7 Days", "desc": "Autonomous AI code agent, instant cloud IDE environments, hosting & $40 usage credits."},
    {"id": "n8n", "name": "n8n Starter", "pkr": 7000, "usd": "26.99", "duration": "1 Year", "access": "Private", "warranty": "30 Days", "desc": "Visual workflow builder, 400+ app integrations, LangChain AI nodes & custom JavaScript."},
    {"id": "notion", "name": "Notion Business", "pkr": 2200, "usd": "8.99", "duration": "3 Months", "access": "Invitation", "warranty": "30 Days", "desc": "Unlimited team blocks, Notion AI assistant, advanced project boards & custom databases."},
    {"id": "nordvpn", "name": "NordVPN Plus", "pkr": 1800, "usd": "6.99", "duration": "3 Months", "access": "Private", "warranty": "7 Days", "desc": "Ultra-fast 10Gbps encrypted servers, Threat Protection ad blocker & zero-logs policy."},
    {"id": "surfshark", "name": "Surfshark VPN", "pkr": 800, "usd": "3.49", "duration": "2 Months", "access": "Shared", "warranty": "7 Days", "desc": "Unlimited device connections, CleanWeb blocker, global server locations & Bypasser."},
    {"id": "youtube", "name": "YouTube Premium", "pkr": 1200, "usd": "4.99", "duration": "3 Months", "access": "Invitation", "warranty": "30 Days", "desc": "100% ad-free video, background playback, offline downloads & full YouTube Music."},
    {"id": "netflix", "name": "Netflix Premium 4K", "pkr": 400, "usd": "1.99", "duration": "1 Month", "access": "Shared", "warranty": "7 Days", "desc": "4K Ultra HD & HDR streaming, spatial audio, dedicated profile with PIN lock."},
    {"id": "linkedin", "name": "LinkedIn Premium", "pkr": 1500, "usd": "5.99", "duration": "2 Months", "access": "Invitation", "warranty": "7 Days", "desc": "InMail credits, profile viewer analytics, applicant insights & LinkedIn Learning."},
    {"id": "windows", "name": "Windows 11 Pro Key", "pkr": 1900, "usd": "7.99", "duration": "Lifetime", "access": "License Key", "warranty": "7 Days", "desc": "Genuine digital retail activation key, BitLocker encryption, Remote Desktop Host."},
    {"id": "claude", "name": "Claude Pro (3.5 Sonnet)", "pkr": 2200, "usd": "8.99", "duration": "1 Month", "access": "Private", "warranty": "7 Days", "desc": "Claude 3.5 Sonnet & Opus, interactive Artifacts visualizer & 200K token deep context."},
    {"id": "midjourney", "name": "Midjourney v6.1 Pro", "pkr": 2400, "usd": "9.99", "duration": "1 Month", "access": "Private / Discord", "warranty": "7 Days", "desc": "Photorealistic AI art, GPU generation hours, commercial rights & web/Discord access."},
    {"id": "cursor", "name": "Cursor AI Pro", "pkr": 2800, "usd": "10.99", "duration": "1 Month", "access": "Private", "warranty": "7 Days", "desc": "Composer multi-file AI editing, fast tab completions, Claude 3.5 Sonnet inside IDE."},
    {"id": "perplexity", "name": "Perplexity Pro", "pkr": 1400, "usd": "5.49", "duration": "1 Month", "access": "Private", "warranty": "7 Days", "desc": "Pro Search with citations, unlimited document uploads, Claude 3.5 & GPT-4o switcher."},
    {"id": "deepseek", "name": "DeepSeek Unlimited", "pkr": 1100, "usd": "4.49", "duration": "1 Month", "access": "Private Portal", "warranty": "7 Days", "desc": "DeepSeek R1 full reasoning chain, mathematical proofs, logic solving & zero queue."},
    {"id": "grok", "name": "SuperGrok / Grok 2", "pkr": 1800, "usd": "6.99", "duration": "1 Month", "access": "Private", "warranty": "7 Days", "desc": "Real-time news search on X, Flux photorealistic image generator & creative modes."},
    {"id": "runway", "name": "Runway ML Gen-3 Pro", "pkr": 3500, "usd": "13.99", "duration": "1 Month", "access": "Private", "warranty": "7 Days", "desc": "Gen-3 Alpha cinematic video generator, motion brush camera controls & 4K upscaler."},
    {"id": "heygen", "name": "HeyGen AI Avatar Pro", "pkr": 4200, "usd": "16.99", "duration": "1 Month", "access": "Private", "warranty": "7 Days", "desc": "Studio-quality human avatars, 40+ language voice dubbing & script-to-video generator."},
    {"id": "grammarly", "name": "Grammarly Premium", "pkr": 750, "usd": "2.99", "duration": "1 Month", "access": "Private / Shared", "warranty": "7 Days", "desc": "Full sentence rewrites, tone tuner, built-in plagiarism detector & browser extension."},
    {"id": "quillbot", "name": "QuillBot Premium", "pkr": 450, "usd": "1.99", "duration": "1 Month", "access": "Private / Shared", "warranty": "7 Days", "desc": "Unlimited paraphrasing words, 8 custom modes, freeze words & citation generator."},
    {"id": "semrush", "name": "SEMrush Pro", "pkr": 1500, "usd": "5.99", "duration": "1 Month", "access": "Shared", "warranty": "7 Days", "desc": "Keyword Magic tool with PKR metrics, competitor organic audit & backlink analytics."},
    {"id": "allinone", "name": "All-in-One Mega AI Portal", "pkr": 1999, "usd": "7.99", "duration": "1 Month", "access": "Private Portal", "warranty": "30 Days", "desc": "Claude 3.5 + GPT-4o + Gemini 1.5 + Perplexity in 1 portal login. No VPN needed."},
    {"id": "tradingview", "name": "TradingView Pro", "pkr": 3500, "usd": "14.99", "duration": "1 Month", "access": "Private", "warranty": "30 Days", "desc": "Institutional-grade technical charts, custom Pine Script, volume profiles & alerts."},
    {"id": "kling", "name": "Kling AI", "pkr": 4800, "usd": "19.99", "duration": "1 Month", "access": "Private", "warranty": "30 Days", "desc": "1080p full HD cinematic video, 3D camera controls, physics simulation & commercial use."},
    {"id": "freepik", "name": "Freepik Premium", "pkr": 2400, "usd": "9.99", "duration": "1 Month", "access": "Private", "warranty": "30 Days", "desc": "100 daily downloads, 150M+ vectors, PSD templates, stock photos & Pikaso AI."},
    {"id": "spotify", "name": "Spotify Premium", "pkr": 1200, "usd": "4.99", "duration": "3 Months", "access": "Private", "warranty": "30 Days", "desc": "100% ad-free music, 10,000 songs offline downloads, 320kbps audio & personal email setup."},
    {"id": "copilot", "name": "GitHub Copilot", "pkr": 2500, "usd": "9.99", "duration": "1 Month", "access": "Private", "warranty": "30 Days", "desc": "Real-time code autocompletion, Copilot Chat in VS Code & JetBrains, personal GitHub setup."},
    {"id": "suno", "name": "Suno AI", "pkr": 3200, "usd": "12.99", "duration": "1 Month Pro", "access": "Private", "warranty": "30 Days", "desc": "2,500 monthly generation credits (~500 songs), studio vocals & commercial monetization."},
    {"id": "turnitin", "name": "Turnitin Student Account", "pkr": 3600, "usd": "13.99", "duration": "1 Month", "access": "Private", "warranty": "30 Days", "desc": "Strict Non-Repository submission, similarity index percentage & AI detection score."},
    {"id": "office365", "name": "Microsoft Office 365 (1TB)", "pkr": 2200, "usd": "8.99", "duration": "1 Year", "access": "Private", "warranty": "30 Days", "desc": "Full Word, Excel, PowerPoint desktop apps, 1TB OneDrive cloud, 5 devices simultaneously."}
]

def generate_llms_txt():
    lines = [
        "# AI Tool Gems Pakistan & Global Hybrid Marketplace",
        "",
        "> AI Tool Gems is an independent software marketplace for comparing, buying, and activating genuine AI tools, developer software license keys, and digital subscriptions. We provide flat PKR pricing for Pakistani buyers and fixed USD pricing for worldwide clients, with WhatsApp delivery after payment confirmation and verified domestic & global payment rails.",
        "> Full knowledge base: [llms-full.txt](https://aitoolgems.tech/llms-full.txt)",
        "",
        "Last reviewed: 2026-10-24",
        "",
        "## Core pages",
        "",
        "- [Homepage](https://aitoolgems.tech/) — complete marketplace, software license keys, finder, ordering process, and FAQs",
        "- [All Tools Directory](https://aitoolgems.tech/tools/) — complete 2026 directory of 40 verified AI software tools, subscriptions, and license keys",
        "- [Deals](https://aitoolgems.tech/deals/) — current discounted software marketplace directory with bundle savings",
        "- [Price Index](https://aitoolgems.tech/prices/) — full 2026 directory of verified AI tools and subscription rates in PKR and USD",
        "- [About](https://aitoolgems.tech/about.html) — marketplace identity, listing process, and independence disclosure",
        "- [How We Review](https://aitoolgems.tech/how-we-review.html) — listing review method, source policy, access definitions, and corrections process",
        "- [How We Price](https://aitoolgems.tech/how-we-price.html) — pricing transparency, currency conversion, and fee structure",
        "- [How We Source](https://aitoolgems.tech/how-we-source.html) — license sourcing, vendor verification, and quality assurance",
        "- [Product Verification](https://aitoolgems.tech/product-verification.html) — activation testing, account safety, and warranty terms",
        "- [Contact](https://aitoolgems.tech/contact.html) — verified WhatsApp support route (+92 323 6715731)",
        "- [Policies](https://aitoolgems.tech/policies.html) — access, delivery, warranty, refund, privacy, and trademark policies",
        "- [Correction Policy](https://aitoolgems.tech/correction-policy.html) — editorial correction standards and reporting workflow",
        "- [Privacy](https://aitoolgems.tech/privacy-policy/) — website and customer privacy policy",
        "- [Terms](https://aitoolgems.tech/terms-of-service/) — website terms of service and order conditions",
        "",
        "## Editorial Guides",
        "",
        "- [Grammarly vs QuillBot in Pakistan: Best AI Writing Tools (2026)](https://aitoolgems.tech/guides/grammarly-vs-quillbot-pakistan/) — Pakistan-focused Grammarly vs QuillBot Pakistan guide",
        "- [Runway Gen-3 Alpha in Pakistan: AI Video Generator Guide (2026)](https://aitoolgems.tech/guides/runway-gen3-pakistan/) — Pakistan-focused Runway Gen-3 Pakistan guide",
        "- [HeyGen AI Video in Pakistan: Avatar Creation & Pricing Guide (2026)](https://aitoolgems.tech/guides/heygen-ai-video-pakistan/) — Pakistan-focused HeyGen AI video Pakistan guide",
        "- [DeepSeek AI in Pakistan: Pricing, Local Access & Guide (2026)](https://aitoolgems.tech/guides/deepseek-ai-pakistan/) — Pakistan-focused DeepSeek AI Pakistan guide",
        "- [Perplexity AI Pro in Pakistan: Pricing, Search Features & Guide (2026)](https://aitoolgems.tech/guides/perplexity-ai-pakistan/) — Pakistan-focused Perplexity AI Pro Pakistan guide",
        "- [n8n Workflow Automation in Pakistan: Small Business Guide (2026)](https://aitoolgems.tech/guides/n8n-automation-pakistan/) — Pakistan-focused n8n workflow automation Pakistan guide",
        "- [Lovable vs Replit in Pakistan: Best AI App Builder (2026)](https://aitoolgems.tech/guides/lovable-vs-replit-pakistan/) — Pakistan-focused Lovable vs Replit Pakistan guide",
        "- [ElevenLabs Voice AI in Pakistan: Pricing, Urdu Support & Guide](https://aitoolgems.tech/guides/elevenlabs-voice-ai-pakistan/) — Pakistan-focused ElevenLabs voice AI Pakistan guide",
        "- [Top AI Video Generators in Pakistan: CapCut, Veo & Runway (2026)](https://aitoolgems.tech/guides/best-ai-video-generators-pakistan/) — Pakistan-focused AI video generator Pakistan guide",
        "- [Best Midjourney Alternatives in Pakistan: Free & Paid (2026)](https://aitoolgems.tech/guides/midjourney-alternatives-pakistan/) — Pakistan-focused Midjourney alternatives Pakistan guide",
        "- [Guides & Blog Hub](https://aitoolgems.tech/guides/) — Pakistan-focused AI tools guide & blog hub",
        "- [Blog & Guides](https://aitoolgems.tech/blog/) — official AI Tool Gems blog, latest tech tutorials, and developer articles",
        "- [AI Subscriptions Pakistan](https://aitoolgems.tech/guides/ai-subscriptions-pakistan/) — complete buyer's guide to AI tool plans in Pakistan",
        "- [AI Tools Pakistan](https://aitoolgems.tech/guides/ai-tools-pakistan/) — top AI software for Pakistani freelancers and businesses",
        "- [AI Tools Price Pakistan](https://aitoolgems.tech/guides/ai-tools-price-pakistan/) — all 40 current listings compared by PKR & USD price, duration, and access type",
        "- [AI Tools Pricing Guide](https://aitoolgems.tech/guides/ai-tools-pricing/) — comprehensive breakdown of billing cycles and costs",
        "- [AI Tools for Businesses](https://aitoolgems.tech/guides/businesses/) — enterprise and SME AI tool deployment in Pakistan",
        "- [Canva vs Figma Pakistan](https://aitoolgems.tech/guides/canva-vs-figma-pakistan/) — workflow-based Canva Pro and Figma Pro comparison",
        "- [Canva Pro Guide](https://aitoolgems.tech/guides/canva/) — Canva Pro features, templates, and team setup in Pakistan",
        "- [CapCut Pro Guide](https://aitoolgems.tech/guides/capcut/) — CapCut Pro PC and mobile video editing workflow",
        "- [Claude 3.5 Sonnet Pakistan](https://aitoolgems.tech/guides/claude-ai-pakistan/) — complete guide to Claude 3.5 Sonnet & Claude Pro in Pakistan",
        "- [Cursor AI Pakistan](https://aitoolgems.tech/guides/cursor-ai-pakistan/) — complete Cursor AI developer & pricing guide in Pakistan",
        "- [ChatGPT Alternatives](https://aitoolgems.tech/guides/chatgpt-alternatives/) — best LLM and reasoning alternatives to ChatGPT Plus",
        "- [ChatGPT vs Gemini Pakistan](https://aitoolgems.tech/guides/chatgpt-vs-gemini-pakistan/) — task-based ChatGPT Plus and Gemini Pro comparison",
        "- [AI Tools for Creators](https://aitoolgems.tech/guides/creators/) — generative AI stack for YouTubers, TikTokers, and influencers",
        "- [AI Tools for Developers](https://aitoolgems.tech/guides/developers/) — AI coding assistants, IDEs, and automation platforms",
        "- [Google Gemini Guide](https://aitoolgems.tech/guides/gemini/) — Gemini Advanced, 2TB Cloud storage, and Workspace integration",
        "- [AI Tools for Productivity](https://aitoolgems.tech/guides/productivity/) — note-taking, slides, and task automation tools",
        "- [AI Tools for Students](https://aitoolgems.tech/guides/students/) — budget-friendly academic research and design tools",
        "",
        f"## Product Catalog ({len(PRODUCTS)} Verified Listings)",
        "",
    ]

    for p in PRODUCTS:
        lines.append(f"- [{p['name']}](https://aitoolgems.tech/tools/{p['id']}/) — Rs. {p['pkr']:,} PKR (${p['usd']} USD) ({p['duration']}, {p['access']} access, {p['desc'].split('.')[0]}, delivery after payment confirmation on WhatsApp)")

    lines.extend([
        "",
        "## Ordering & Payment Facts",
        "",
        "- Dual-Currency Pricing: Transparent PKR rates for domestic customers in Pakistan; flat USD rates for worldwide/international clients.",
        "- Domestic Payment Rails (Pakistan): EasyPaisa, JazzCash, SadaPay, NayaPay, Raast, and local Pakistani bank transfer (IBFT).",
        "- International Payment Rails (Worldwide): Cryptocurrency (USDT TRC20 / BEP20, Binance Pay) and Wise (TransferWise).",
        "- Delivery Method: Digital credentials, invitation links, or software keys delivered after payment confirmation and manual verification on WhatsApp.",
        "- Warranty: 7-day to 30-day replacement warranty on all listings.",
        "- Direct Human Support: +92 323 6715731.",
        "- Official WhatsApp Channel: https://whatsapp.com/channel/0029VbDnEgCHLHQOYpDo5c31",
        "- Official Telegram Channel: https://t.me/aitoolgemspak",
        "- Official Facebook: https://www.facebook.com/people/AI-Tool-Gems-Pakistan/61594432675562/",
        "- Official Instagram: https://www.instagram.com/aitoolgemspak/",
        "- Official TikTok: https://www.tiktok.com/@aitoolgems",
        "- Independence: AI Tool Gems is an independent marketplace and is not affiliated with listed third-party software brands.",
        "",
        "Sitemap: https://aitoolgems.tech/sitemap.xml",
        ""
    ])

    out = "\n".join(lines)
    (BASE / "llms.txt").write_text(out, encoding="utf-8")
    print(f"Updated llms.txt with {len(PRODUCTS)} products.")

def generate_llms_full_txt():
    lines = [
        "# AI Tool Gems — Complete Marketplace & AI Assistant Knowledge Base",
        "",
        "> Canonical URL: https://aitoolgems.tech/",
        "> Entity: AI Tool Gems (Independent Digital Software Marketplace)",
        "> Target Markets: Pakistan (Domestic Core) & Worldwide (Global Hybrid Expansion)",
        "> Currencies: Pakistani Rupee (PKR, Rs.) & US Dollar (USD, $)",
        "> Domestic Payment Methods: EasyPaisa, JazzCash, SadaPay, NayaPay, Raast, Bank Transfer (IBFT)",
        "> International Payment Methods: Cryptocurrency (USDT TRC20 / BEP20, Binance Pay), Wise (TransferWise)",
        "> Fulfillment Method: Digital delivery via WhatsApp after payment confirmation and verification",
        "> Customer Support: WhatsApp +92 323 6715731",
        "> Warranty: 7-day to 30-day replacement warranty on all listings",
        "",
        "---",
        "",
        "## About AI Tool Gems",
        "AI Tool Gems (aitoolgems.tech) is an independent digital marketplace designed for freelancers, content creators, software engineers, digital marketing agencies, and global users.",
        "",
        "In Pakistan and many international jurisdictions, acquiring subscriptions to premier AI platforms (such as OpenAI, Google One, Anthropic, Midjourney, Adobe, and ElevenLabs) is hindered by credit card payment declines, withholding taxes, high currency conversion fees, and lack of localized payment options.",
        "",
        "AI Tool Gems solves this challenge by providing verified AI tool subscriptions, private account access, team invitation seats, and software license keys with upfront transparent pricing in PKR & USD, fast assisted WhatsApp delivery, and multi-rail payment support.",
        "",
        "---",
        "",
        f"## Complete Product Catalog & Multi-Currency Pricing ({len(PRODUCTS)} Verified Listings)",
        ""
    ]

    for idx, p in enumerate(PRODUCTS, start=1):
        lines.extend([
            f"### {idx}. {p['name']}",
            f"- URL: https://aitoolgems.tech/tools/{p['id']}/",
            f"- Listed Price: Rs. {p['pkr']:,} PKR / ${p['usd']} USD",
            f"- Duration: {p['duration']}",
            f"- Access Type: {p['access']} Access",
            f"- Delivery Time: Delivery after payment confirmation on WhatsApp",
            f"- Warranty: {p['warranty']} Replacement Warranty",
            f"- Key Features: {p['desc']}",
            f"- Order WhatsApp: https://wa.me/923236715731?text=Hello%20AI%20Tool%20Gems%2C%20I%20want%20to%20order%20{p['name'].replace(' ', '%20')}",
            ""
        ])

    lines.extend([
        "---",
        "",
        "## Ordering & Verification Process",
        "1. Selection: The customer selects a subscription plan from the catalog.",
        "2. WhatsApp Confirmation: Availability, plan duration, access type, and payment rails are confirmed with support on WhatsApp (+92 323 6715731).",
        "3. Manual Verification: The buyer transfers funds using verified domestic rails (EasyPaisa, JazzCash, SadaPay, Bank IBFT) or international rails (Crypto USDT, Binance Pay, Wise) and submits the transaction receipt.",
        "4. Dispatch: Support verifies the transaction and delivers access credentials or license keys directly via WhatsApp.",
        "5. Warranty Coverage: Every order is protected by our 7-day to 30-day replacement warranty.",
        "",
        "## Legal & Editorial Independence",
        "AI Tool Gems is an independent marketplace and is not affiliated with, endorsed by, or sponsored by OpenAI, Google, Anthropic, Microsoft, Adobe, Midjourney, or any other trademark owner listed on the site.",
        "",
        "Sitemap: https://aitoolgems.tech/sitemap.xml",
        ""
    ])

    out = "\n".join(lines)
    (BASE / "llms-full.txt").write_text(out, encoding="utf-8")
    print(f"Updated llms-full.txt with {len(PRODUCTS)} products.")

if __name__ == "__main__":
    generate_llms_txt()
    generate_llms_full_txt()
