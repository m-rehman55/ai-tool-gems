#!/usr/bin/env python3
"""
Step 1: Improve content quality on ALL pages (300+ words)
Step 2: Add internal links from homepage to all tool pages
Step 3: Add cross-links between related pages
"""
import re
from pathlib import Path

BASE = Path(r"D:/ai-tool-gems")

# Tool data for content enhancement
TOOL_DATA = {
    "chatgpt": {
        "name": "ChatGPT Plus", "brand": "OpenAI", "category": "AI Assistants",
        "pk_desc": "ChatGPT Plus Pakistan mein advanced AI writing, coding, research aur image generation ke liye. Advanced GPT-4 model ke saath writing, coding, study tasks ke liye best subscription.",
        "jp_desc": "ChatGPT Plusは日本向けAIアシスタント。高度なGPT-4モデルでライティング、コーディング、リサーチ、画像生成をサポート。1か月¥1,697でプロ級AIツールを手に入れよう。",
        "keywords": ["ChatGPT Plus", "OpenAI", "AI writing", "GPT-4", "AI assistant"]
    },
    "gemini": {
        "name": "Gemini Pro", "brand": "Google", "category": "AI Assistants",
        "pk_desc": "Gemini Pro Pakistan mein Google ka advanced AI assistant. Research, documents, code aur everyday tasks ke liye. 18 months invitation plan available.",
        "jp_desc": "Gemini ProはGoogleの最先端AIアシスタント。リサーチ、文書作成、コーディング、日常タスクに対応。18か月Invitation Planで利用可能。",
        "keywords": ["Gemini Pro", "Google AI", "AI assistant", "multimodal"]
    },
    "veo": {
        "name": "Veo 3 Ultra", "brand": "Google DeepMind", "category": "AI Video",
        "pk_desc": "Veo 3 Ultra Pakistan mein cinematic AI video generation ke liye. Realistic motion aur audio-capable workflows ke saath video banao. Unlimited shared plan available.",
        "jp_desc": "Veo 3 Ultraは日本向けAI動画生成ツール。現実的なモーションと音声対応ワークフローでシネマティックな動画を生成。Unlimited共有プランで利用可能。",
        "keywords": ["Veo 3", "AI video", "Google DeepMind", "video generation"]
    },
    "leonardo": {
        "name": "Leonardo AI Essential", "brand": "Leonardo AI", "category": "Design",
        "pk_desc": "Leonardo AI Essential Pakistan mein production-ready digital art aur marketing visuals banane ke liye. 8,500 credits private plan mein available.",
        "jp_desc": "Leonardo AI Essentialは日本向けデジタルアート生成ツール。プロ級のビジュアルやマーケティング素材を8,500クレジットで生成可能。",
        "keywords": ["Leonardo AI", "digital art", "design", "visuals"]
    },
    "elevenlabs": {
        "name": "ElevenLabs", "brand": "ElevenLabs", "category": "AI Voice",
        "pk_desc": "ElevenLabs Pakistan mein realistic AI speech, dubbing aur voice cloning ke liye. Professional voice generation for media workflows.",
        "jp_desc": "ElevenLabsは日本向けAI音声生成ツール。リアルな音声合成、吹き替え、ボイスクローンに対応。メディアワークフローに最適。",
        "keywords": ["ElevenLabs", "AI voice", "speech synthesis", "dubbing"]
    },
    "canva": {
        "name": "Canva Pro Edu", "brand": "Canva", "category": "Design",
        "pk_desc": "Canva Pro Edu Pakistan mein professional design ke liye. Templates, graphics, presentations sab kuch one subscription mein. Best for designers aur marketers.",
        "jp_desc": "Canva Pro Eduは日本向けデザイン subscription。テンプレート、グラフィックス、プレゼンテーションがすべて1つのサブスクリプションに含まれる。",
        "keywords": ["Canva Pro", "design", "templates", "graphics"]
    },
    "figma": {
        "name": "Figma Pro Private", "brand": "Figma", "category": "Design",
        "pk_desc": "Figma Pro Private Pakistan mein UI/UX design ke liye best tool. Collaborative design aur prototyping ke liye professional subscription.",
        "jp_desc": "Figma Pro Privateは日本向けUI/UXデザイン ツール。コラボレーティブデザインとプロトタイピングに最適なプロフェッショナルサブスクリプション。",
        "keywords": ["Figma", "UI/UX", "design", "prototyping"]
    },
    "capcut": {
        "name": "CapCut Pro", "brand": "CapCut", "category": "AI Video",
        "pk_desc": "CapCut Pro Pakistan mein professional video editing ke liye. AI-powered editing tools, effects, aur templates sab kuch available.",
        "jp_desc": "CapCut Proは日本向けプロフェッショナル動画編集ツール。AI搭載編集ツール、エフェクト、テンプレートが充実。",
        "keywords": ["CapCut Pro", "video editing", "AI video"]
    },
    "adobe": {
        "name": "Adobe Creative Cloud", "brand": "Adobe", "category": "Design",
        "pk_desc": "Adobe Creative Cloud Pakistan mein Photoshop, Illustrator, Premiere Pro sab tools ke saath. Professional creative suite for all design needs.",
        "jp_desc": "Adobe Creative Cloudは日本向けクリエイティブスイート。Photoshop、Illustrator、Premiere Proなどプロ向けツールが充実。",
        "keywords": ["Adobe Creative Cloud", "Photoshop", "design", "creative"]
    },
    "lovable": {
        "name": "Lovable Pro", "brand": "Lovable", "category": "Development",
        "pk_desc": "Lovable Pro Pakistan mein AI-powered web development ke liye. Code generation aur deployment sab kuch one platform mein.",
        "jp_desc": "Lovable Proは日本向けAIウェブ開発ツール。コード生成とデプロイメントを1つのプラットフォームで提供。",
        "keywords": ["Lovable Pro", "web development", "AI coding"]
    },
    "gamma": {
        "name": "Gamma Pro", "brand": "Gamma", "category": "Productivity",
        "pk_desc": "Gamma Pro Pakistan mein AI-powered presentations aur documents ke liye. Beautiful slides aur reports banayein AI se.",
        "jp_desc": "Gamma Proは日本向けAIプレゼンテーション生成ツール。美しいスライドとレポートをAIで生成可能。",
        "keywords": ["Gamma Pro", "presentations", "AI documents"]
    },
    "replit": {
        "name": "Replit Core", "brand": "Replit", "category": "Development",
        "pk_desc": "Replit Core Pakistan mein cloud-based coding ke liye best tool. IDE, collaboration aur deployment sab kuch available.",
        "jp_desc": "Replit Coreは日本向けクラウド開発環境。IDE、コラボレーション、デプロイメントが全て1つのプラットフォームに。",
        "keywords": ["Replit Core", "cloud IDE", "coding", "development"]
    },
    "n8n": {
        "name": "n8n Starter", "brand": "n8n", "category": "Development",
        "pk_desc": "n8n Starter Pakistan mein workflow automation ke liye. AI workflows aur integrations banayein bina coding ke.",
        "jp_desc": "n8n Starterは日本向けワークフロー自動化ツール。コードなしでAIワークフローとインテグレーションを構築。",
        "keywords": ["n8n", "workflow automation", "AI integration"]
    },
    "notion": {
        "name": "Notion Business", "brand": "Notion", "category": "Productivity",
        "pk_desc": "Notion Business Pakistan mein team collaboration aur project management ke liye. All-in-one workspace for teams.",
        "jp_desc": "Notion Businessは日本向けチームコラボレーションツール。プロジェクト管理とワークスペースを1つに統合。",
        "keywords": ["Notion Business", "project management", "team collaboration"]
    },
    "nordvpn": {
        "name": "NordVPN", "brand": "Nord Security", "category": "VPN & Security",
        "pk_desc": "NordVPN Pakistan mein secure internet browsing ke liye best VPN. High-speed servers aur privacy protection.",
        "jp_desc": "NordVPNは日本向け最高速度VPN。高速サーバーとプライバシー保護で安全なインターネット閲覧を提供。",
        "keywords": ["NordVPN", "VPN", "security", "privacy"]
    },
    "surfshark": {
        "name": "Surfshark VPN", "brand": "Nord Security", "category": "VPN & Security",
        "pk_desc": "Surfshark VPN Pakistan mein unlimited device VPN ke liye. Affordable aur secure internet protection.",
        "jp_desc": "Surfshark VPNは日本向けデバイス無制限VPN。手頃な価格とセキュリティ保護でインターネットを安全に。",
        "keywords": ["Surfshark VPN", "VPN", "security", "unlimited devices"]
    },
    "youtube": {
        "name": "YouTube Premium", "brand": "Google", "category": "Entertainment",
        "pk_desc": "YouTube Premium Pakistan mein ad-free video watching ke liye. Background play aur YouTube Music included.",
        "jp_desc": "YouTube Premiumは日本向け広告なし動画視聴ツール。背景再生とYouTube Musicが含まれる。",
        "keywords": ["YouTube Premium", "ad-free", "video", "entertainment"]
    },
    "netflix": {
        "name": "Netflix Premium 4K", "brand": "Netflix", "category": "Entertainment",
        "pk_desc": "Netflix Premium 4K Pakistan mein HD/4K streaming ke liye. Unlimited movies aur shows ad-free.",
        "jp_desc": "Netflix Premium 4Kは日本向け4Kストリーミングサービス。広告なしで無制限の映画とテレビ番組を視聴。",
        "keywords": ["Netflix Premium", "4K streaming", "movies", "shows"]
    },
    "linkedin": {
        "name": "LinkedIn Premium", "brand": "Microsoft", "category": "Business",
        "pk_desc": "LinkedIn Premium Pakistan mein professional networking ke liye. Job search aur business insights included.",
        "jp_desc": "LinkedIn Premiumは日本向けプロフェッショナルネットワーキングツール。転職支援とビジネスインサイト付き。",
        "keywords": ["LinkedIn Premium", "networking", "jobs", "business"]
    },
    "windows": {
        "name": "Windows 11 Pro License Key", "brand": "Microsoft", "category": "Software",
        "pk_desc": "Windows 11 Pro License Key Pakistan mein genuine Windows OS ke liye. Best price for professional Windows license.",
        "jp_desc": "Windows 11 Pro License Keyは日本向け正規Windowsライセンス。プロフェッショナル向けWindows OSを最安価格で提供。",
        "keywords": ["Windows 11 Pro", "license key", "Microsoft", "Windows OS"]
    },
    "manus": {
        "name": "Manus AI Pro", "brand": "Manus", "category": "AI Assistants",
        "pk_desc": "Manus AI Pro Pakistan mein autonomous AI agent ke liye. Multi-step task automation with AI.",
        "jp_desc": "Manus AI Proは日本向け自律型AIエージェントツール。多段階タスク自動化をAIで実現。",
        "keywords": ["Manus AI", "AI agent", "automation"]
    },
}

# Guide data
GUIDE_DATA = {
    "ai-tools-price-pakistan": {
        "title": "AI Tools Price in Pakistan 2026",
        "content": "Complete guide to AI tools pricing in Pakistan 2026. Compare ChatGPT Plus, Gemini Pro, Canva Pro, Adobe Creative Cloud prices in PKR. Find best deals and subscription plans for AI tools in Pakistan."
    },
    "chatgpt-vs-gemini-pakistan": {
        "title": "ChatGPT Plus vs Gemini Pro in Pakistan",
        "content": "Compare ChatGPT Plus vs Gemini Pro in Pakistan. Both are top AI assistants. Check pricing, features, and which one is better for your needs. Detailed comparison with PKR prices."
    },
    "canva-vs-figma-pakistan": {
        "title": "Canva Pro vs Figma Pro in Pakistan",
        "content": "Compare Canva Pro vs Figma Pro in Pakistan. Both are design tools but for different needs. Canva for quick designs, Figma for professional UI/UX. Compare prices and features."
    },
}

# JP Guide data
JP_GUIDE_DATA = {
    "ai-tools-price-japan": {
        "title": "AI Tools Price in Japan 2026",
        "content": "Japan AI tools pricing guide 2026. ChatGPT Plus, Gemini Pro, Canva Pro prices in JPY. Best AI subscription deals in Japan."
    },
    "chatgpt-vs-gemini-japan": {
        "title": "ChatGPT Plus vs Gemini Pro in Japan",
        "content": "Compare ChatGPT Plus vs Gemini Pro in Japan. Both AI assistants compared with JPY prices and features."
    },
    "canva-vs-figma-japan": {
        "title": "Canva Pro vs Figma Pro in Japan",
        "content": "Canva Pro vs Figma Pro comparison for Japan users. Design tools compared with JPY pricing."
    },
}


def read_html(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except:
        return None


def write_html(path, content):
    path.write_text(content, encoding="utf-8")


def count_words(html):
    # Remove HTML tags and count words
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    return len(text.split())


def get_tool_name_from_path(path):
    """Extract tool name from file path."""
    parts = path.parts
    if "tools" in parts:
        idx = parts.index("tools")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return None


def enhance_tool_page(path):
    """Add comprehensive content to tool pages."""
    html = read_html(path)
    if not html:
        return {"path": str(path), "status": "ERROR"}
    
    tool_name = get_tool_name_from_path(path)
    if not tool_name or tool_name not in TOOL_DATA:
        return {"path": str(path), "status": "SKIP - no data"}
    
    data = TOOL_DATA[tool_name]
    current_words = count_words(html)
    
    # Check if page already has enhanced content
    if "PKR pricing" in html or "掲載価格" in html:
        return {"path": str(path), "status": "✓ Already enhanced", "words": current_words}
    
    # Find the description section and enhance it
    # Add more detail after the main description
    
    # Add comprehensive description if missing
    if data["pk_desc"] not in html and data["jp_desc"] not in html:
        # Determine if PK or JP page
        is_jp = "/jp/" in str(path)
        desc = data["jp_desc"] if is_jp else data["pk_desc"]
        
        # Insert description in appropriate place
        # Find the main description area and add more content
        
        # Add keywords section before FAQ
        keywords_text = ", ".join(data["keywords"])
        
        enhanced_html = html
        
        # Add comprehensive content before FAQ section
        faq_pos = enhanced_html.find("## Frequently asked questions")
        if faq_pos == -1:
            faq_pos = enhanced_html.find("Frequently asked questions")
        
        if faq_pos > 0:
            additional_content = f"""

## About {data['name']}

{data['pk_desc'] if not is_jp else data['jp_desc']}

### Key Features
- Advanced AI-powered tool for professional use
- High performance and reliable service
- Affordable pricing plans available
- Instant delivery after purchase
- 7-day replacement warranty included

### Who Should Use This Tool
- Professionals who need AI assistance daily
- Students and researchers
- Content creators and marketers
- Developers and designers

### Why Choose AI Tool Gems?
- Instant 1-click WhatsApp delivery
- Upfront pricing in PKR/JPY
- 1-on-1 human support
- Clear private/shared plans
- 7-day replacement warranty

### Related Tools
Compare with other AI tools in our catalog before ordering.

### Keywords
{keywords_text}

"""
            enhanced_html = enhanced_html[:faq_pos] + additional_content + enhanced_html[faq_pos:]
        
        write_html(path, enhanced_html)
        return {"path": str(path), "status": "✓ Content enhanced", "words": count_words(enhanced_html)}
    
    return {"path": str(path), "status": "✓ OK", "words": current_words}


def add_internal_links_homepage():
    """Add internal links from homepage to all tool pages."""
    path = BASE / "index.html"
    html = read_html(path)
    if not html:
        return {"path": "index.html", "status": "ERROR"}
    
    # Check if tool links already exist
    if 'href="tools/chatgpt/"' in html:
        return {"path": "index.html", "status": "✓ Already has tool links"}
    
    # Find the section where tools are listed and add links
    # Look for the product cards area
    tool_links = []
    for tool in sorted(TOOL_DATA.keys()):
        tool_links.append(f'<a href="tools/{tool}/">{TOOL_DATA[tool]["name"]}</a>')
    
    # Add links section before FAQ or at end of products section
    links_html = "\n    ".join(tool_links)
    
    # Find a good place to insert - after the product catalog section
    insert_marker = "## Trending 3D gems"
    insert_pos = html.find(insert_marker)
    
    if insert_pos > 0:
        links_section = f'\n\n<!-- Internal Tool Links -->\n<p>{links_html}</p>\n'
        html = html[:insert_pos] + links_section + html[insert_pos:]
        write_html(path, html)
        return {"path": "index.html", "status": "✓ Internal links added", "count": len(tool_links)}
    
    return {"path": "index.html", "status": "⚠ Could not find insert position"}


def add_jp_homepage_links():
    """Add internal links from JP homepage to all JP tool pages."""
    path = BASE / "jp" / "index.html"
    html = read_html(path)
    if not html:
        return {"path": "jp/index.html", "status": "ERROR"}
    
    # Check if tool links already exist
    if 'href="jp/tools/chatgpt/"' in html:
        return {"path": "jp/index.html", "status": "✓ Already has tool links"}
    
    # Build tool links for JP
    tool_links = []
    for tool in sorted(TOOL_DATA.keys()):
        tool_links.append(f'<a href="jp/tools/{tool}/">{TOOL_DATA[tool]["name"]}</a>')
    
    links_html = "\n    ".join(tool_links)
    
    # Find insert position
    insert_marker = "## Trending"
    insert_pos = html.find(insert_marker)
    
    if insert_pos > 0:
        links_section = f'\n\n<!-- Internal Tool Links -->\n<p>{links_html}</p>\n'
        html = html[:insert_pos] + links_section + html[insert_pos:]
        write_html(path, html)
        return {"path": "jp/index.html", "status": "✓ Internal links added", "count": len(tool_links)}
    
    return {"path": "jp/index.html", "status": "⚠ Could not find insert position"}


def main():
    print("=" * 60)
    print("🚀 Step 1: Content Quality Enhancement")
    print("=" * 60)
    
    # Process all tool pages
    results = {"enhanced": 0, "already": 0, "errors": 0, "skipped": 0}
    
    # PK tool pages
    pk_tools_dir = BASE / "tools"
    for tool_dir in sorted(pk_tools_dir.iterdir()):
        if tool_dir.is_dir():
            page = tool_dir / "index.html"
            if page.exists():
                result = enhance_tool_page(page)
                if result["status"].startswith("✓ Content"):
                    results["enhanced"] += 1
                    print(f"  ✓ {result['path']} ({result.get('words', 0)} words)")
                elif result["status"].startswith("✓ Already"):
                    results["already"] += 1
                    print(f"  ○ {result['path']} — already enhanced")
                elif result["status"].startswith("✓ OK"):
                    results["already"] += 1
                    print(f"  ○ {result['path']} — OK ({result.get('words', 0)} words)")
                else:
                    results["errors"] += 1
                    print(f"  ✗ {result['path']}: {result['status']}")
    
    # JP tool pages
    jp_tools_dir = BASE / "jp" / "tools"
    for tool_dir in sorted(jp_tools_dir.iterdir()):
        if tool_dir.is_dir():
            page = tool_dir / "index.html"
            if page.exists():
                result = enhance_tool_page(page)
                if result["status"].startswith("✓ Content"):
                    results["enhanced"] += 1
                    print(f"  ✓ {result['path']} ({result.get('words', 0)} words)")
                elif result["status"].startswith("✓ Already"):
                    results["already"] += 1
                    print(f"  ○ {result['path']} — already enhanced")
                elif result["status"].startswith("✓ OK"):
                    results["already"] += 1
                    print(f"  ○ {result['path']} — OK ({result.get('words', 0)} words)")
                else:
                    results["errors"] += 1
                    print(f"  ✗ {result['path']}: {result['status']}")
    
    print("\n" + "=" * 60)
    print(f"✅ Content enhanced: {results['enhanced']} pages")
    print(f"○ Already good: {results['already']} pages")
    print(f"⚠ Errors: {results['errors']} pages")
    print("=" * 60)
    
    # Step 2: Internal links on homepage
    print("\n" + "=" * 60)
    print("🔗 Step 2: Internal Links on Homepage")
    print("=" * 60)
    
    pk_result = add_internal_links_homepage()
    print(f"  PK Homepage: {pk_result['status']}")
    
    jp_result = add_jp_homepage_links()
    print(f"  JP Homepage: {jp_result['status']}")
    
    print("\n" + "=" * 60)
    print("✅ DONE — Content + Internal Links Enhanced")
    print("=" * 60)


if __name__ == "__main__":
    main()
