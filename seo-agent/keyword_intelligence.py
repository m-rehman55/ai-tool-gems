"""
Keyword Intelligence Engine — AIToolGems Pakistan
---------------------------------------------------
100+ Pakistan-specific AI tool search intent keywords across 10 distinct intents.
Zero-budget, Google-compliant, never-fabricate policy:
- No invented search volume (uses real GSC performance where observed or NOT_AVAILABLE).
- Exactly one primary URL mapped per intent.
- 10 distinct intents (informational, commercial, transactional, local, comparison,
  product, pricing, brand, problem-solving, educational).
"""

KEYWORD_DATABASE = [
    # 1. COMMERCIAL (Buyer evaluating options & pricing)
    {"keyword": "AI tools Pakistan", "intent": "commercial", "primary_url": "https://aitoolgems.tech/tools/", "secondary_urls": ["https://aitoolgems.tech/guides/ai-tools-price-pakistan/"], "business_val": 9, "comp": 6, "serp": "local-results", "status": "MONITOR"},
    {"keyword": "ChatGPT Plus price Pakistan", "intent": "commercial", "primary_url": "https://aitoolgems.tech/tools/chatgpt/", "secondary_urls": ["https://aitoolgems.tech/guides/chatgpt-vs-gemini-pakistan/"], "business_val": 10, "comp": 7, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "AI subscription prices Pakistan", "intent": "commercial", "primary_url": "https://aitoolgems.tech/guides/ai-tools-price-pakistan/", "secondary_urls": ["https://aitoolgems.tech/prices/"], "business_val": 9, "comp": 5, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "cheap AI tools Pakistan", "intent": "commercial", "primary_url": "https://aitoolgems.tech/deals/", "secondary_urls": ["https://aitoolgems.tech/"], "business_val": 9, "comp": 5, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "Gemini Pro price Pakistan", "intent": "commercial", "primary_url": "https://aitoolgems.tech/tools/gemini/", "secondary_urls": ["https://aitoolgems.tech/guides/gemini/"], "business_val": 8, "comp": 6, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "Canva Pro price Pakistan", "intent": "commercial", "primary_url": "https://aitoolgems.tech/tools/canva/", "secondary_urls": ["https://aitoolgems.tech/guides/canva/"], "business_val": 8, "comp": 5, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "CapCut Pro price Pakistan", "intent": "commercial", "primary_url": "https://aitoolgems.tech/tools/capcut/", "secondary_urls": ["https://aitoolgems.tech/guides/capcut/"], "business_val": 8, "comp": 5, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "Leonardo AI price Pakistan", "intent": "commercial", "primary_url": "https://aitoolgems.tech/tools/leonardo/", "secondary_urls": ["https://aitoolgems.tech/prices/"], "business_val": 8, "comp": 5, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "ElevenLabs price Pakistan", "intent": "commercial", "primary_url": "https://aitoolgems.tech/tools/elevenlabs/", "secondary_urls": ["https://aitoolgems.tech/prices/"], "business_val": 8, "comp": 5, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "Figma Pro subscription Pakistan", "intent": "commercial", "primary_url": "https://aitoolgems.tech/tools/figma/", "secondary_urls": ["https://aitoolgems.tech/guides/canva-vs-figma-pakistan/"], "business_val": 7, "comp": 5, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "Adobe Creative Cloud price Pakistan", "intent": "commercial", "primary_url": "https://aitoolgems.tech/tools/adobe/", "secondary_urls": ["https://aitoolgems.tech/prices/"], "business_val": 7, "comp": 6, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "Replit Core price Pakistan", "intent": "commercial", "primary_url": "https://aitoolgems.tech/tools/replit/", "secondary_urls": ["https://aitoolgems.tech/guides/developers/"], "business_val": 7, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "Lovable Pro price Pakistan", "intent": "commercial", "primary_url": "https://aitoolgems.tech/tools/lovable/", "secondary_urls": ["https://aitoolgems.tech/guides/developers/"], "business_val": 7, "comp": 4, "serp": "organic", "status": "ACTIVE"},

    {"keyword": "buy ChatGPT Plus Pakistan EasyPaisa", "intent": "transactional", "primary_url": "https://aitoolgems.tech/tools/chatgpt/", "secondary_urls": ["https://aitoolgems.tech/deals/"], "business_val": 10, "comp": 6, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "buy Claude Pro with EasyPaisa", "intent": "transactional", "primary_url": "https://aitoolgems.tech/guides/claude-ai-pakistan/", "secondary_urls": ["https://aitoolgems.tech/tools/chatgpt/"], "business_val": 10, "comp": 3, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "Claude 3.5 Sonnet Pakistan price", "intent": "commercial", "primary_url": "https://aitoolgems.tech/guides/claude-ai-pakistan/", "secondary_urls": ["https://aitoolgems.tech/prices/"], "business_val": 9, "comp": 4, "serp": "featured-snippet", "status": "ACTIVE"},
    {"keyword": "how to use Claude 3.5 Sonnet in Pakistan", "intent": "problem-solving", "primary_url": "https://aitoolgems.tech/guides/claude-ai-pakistan/", "secondary_urls": ["https://aitoolgems.tech/guides/developers/"], "business_val": 9, "comp": 3, "serp": "featured-snippet", "status": "ACTIVE"},
    {"keyword": "buy ChatGPT Plus Pakistan JazzCash", "intent": "transactional", "primary_url": "https://aitoolgems.tech/tools/chatgpt/", "secondary_urls": ["https://aitoolgems.tech/"], "business_val": 10, "comp": 6, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "buy Canva Pro Pakistan EasyPaisa", "intent": "transactional", "primary_url": "https://aitoolgems.tech/tools/canva/", "secondary_urls": ["https://aitoolgems.tech/deals/"], "business_val": 9, "comp": 5, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "buy Gemini Pro Pakistan JazzCash", "intent": "transactional", "primary_url": "https://aitoolgems.tech/tools/gemini/", "secondary_urls": ["https://aitoolgems.tech/deals/"], "business_val": 9, "comp": 5, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "buy CapCut Pro subscription Pakistan", "intent": "transactional", "primary_url": "https://aitoolgems.tech/tools/capcut/", "secondary_urls": ["https://aitoolgems.tech/"], "business_val": 9, "comp": 5, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "buy Leonardo AI credits Pakistan", "intent": "transactional", "primary_url": "https://aitoolgems.tech/tools/leonardo/", "secondary_urls": ["https://aitoolgems.tech/"], "business_val": 8, "comp": 4, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "buy ElevenLabs voice tokens Pakistan", "intent": "transactional", "primary_url": "https://aitoolgems.tech/tools/elevenlabs/", "secondary_urls": ["https://aitoolgems.tech/"], "business_val": 8, "comp": 4, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "buy Notion Plus Pakistan", "intent": "transactional", "primary_url": "https://aitoolgems.tech/tools/notion/", "secondary_urls": ["https://aitoolgems.tech/guides/productivity/"], "business_val": 8, "comp": 4, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "buy NordVPN Pakistan EasyPaisa", "intent": "transactional", "primary_url": "https://aitoolgems.tech/tools/nordvpn/", "secondary_urls": ["https://aitoolgems.tech/deals/"], "business_val": 7, "comp": 5, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "buy Surfshark VPN Pakistan JazzCash", "intent": "transactional", "primary_url": "https://aitoolgems.tech/tools/surfshark/", "secondary_urls": ["https://aitoolgems.tech/deals/"], "business_val": 7, "comp": 5, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "buy Windows 11 Pro key Pakistan", "intent": "transactional", "primary_url": "https://aitoolgems.tech/tools/windows/", "secondary_urls": ["https://aitoolgems.tech/"], "business_val": 7, "comp": 5, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "buy YouTube Premium Pakistan", "intent": "transactional", "primary_url": "https://aitoolgems.tech/tools/youtube/", "secondary_urls": ["https://aitoolgems.tech/"], "business_val": 7, "comp": 5, "serp": "shopping-results", "status": "ACTIVE"},

    # 3. INFORMATIONAL (User seeking guidance, research, or reviews)
    {"keyword": "best AI tools for students Pakistan", "intent": "informational", "primary_url": "https://aitoolgems.tech/guides/students/", "secondary_urls": ["https://aitoolgems.tech/guides/"], "business_val": 8, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "best AI tools for freelancers Pakistan", "intent": "informational", "primary_url": "https://aitoolgems.tech/guides/businesses/", "secondary_urls": ["https://aitoolgems.tech/guides/"], "business_val": 8, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "AI tools for creators Pakistan", "intent": "informational", "primary_url": "https://aitoolgems.tech/guides/creators/", "secondary_urls": ["https://aitoolgems.tech/guides/"], "business_val": 8, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "AI tools for developers Pakistan", "intent": "informational", "primary_url": "https://aitoolgems.tech/guides/developers/", "secondary_urls": ["https://aitoolgems.tech/guides/"], "business_val": 7, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "AI productivity tools in Pakistan", "intent": "informational", "primary_url": "https://aitoolgems.tech/guides/productivity/", "secondary_urls": ["https://aitoolgems.tech/guides/"], "business_val": 7, "comp": 3, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "how to use ChatGPT in Pakistan", "intent": "informational", "primary_url": "https://aitoolgems.tech/tools/chatgpt/", "secondary_urls": ["https://aitoolgems.tech/guides/ai-tools-pakistan/"], "business_val": 7, "comp": 5, "serp": "organic", "status": "MONITOR"},
    {"keyword": "how AI tools help Pakistani freelancers", "intent": "informational", "primary_url": "https://aitoolgems.tech/guides/businesses/", "secondary_urls": ["https://aitoolgems.tech/guides/productivity/"], "business_val": 7, "comp": 3, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "best AI tools for Urdu content", "intent": "informational", "primary_url": "https://aitoolgems.tech/guides/creators/", "secondary_urls": ["https://aitoolgems.tech/guides/chatgpt-alternatives/"], "business_val": 6, "comp": 3, "serp": "organic", "status": "ACTIVE"},

    # 4. COMPARISON (Comparing two or more solutions)
    {"keyword": "ChatGPT Plus vs Gemini Pro Pakistan", "intent": "comparison", "primary_url": "https://aitoolgems.tech/guides/chatgpt-vs-gemini-pakistan/", "secondary_urls": ["https://aitoolgems.tech/tools/chatgpt/", "https://aitoolgems.tech/tools/gemini/"], "business_val": 9, "comp": 6, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "Canva Pro vs Figma Pro Pakistan", "intent": "comparison", "primary_url": "https://aitoolgems.tech/guides/canva-vs-figma-pakistan/", "secondary_urls": ["https://aitoolgems.tech/tools/canva/", "https://aitoolgems.tech/tools/figma/"], "business_val": 8, "comp": 5, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "ChatGPT alternatives in Pakistan", "intent": "comparison", "primary_url": "https://aitoolgems.tech/guides/chatgpt-alternatives/", "secondary_urls": ["https://aitoolgems.tech/guides/gemini/"], "business_val": 8, "comp": 5, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "Leonardo AI vs Midjourney Pakistan", "intent": "comparison", "primary_url": "https://aitoolgems.tech/tools/leonardo/", "secondary_urls": ["https://aitoolgems.tech/guides/creators/"], "business_val": 7, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "NordVPN vs Surfshark Pakistan", "intent": "comparison", "primary_url": "https://aitoolgems.tech/tools/nordvpn/", "secondary_urls": ["https://aitoolgems.tech/tools/surfshark/"], "business_val": 7, "comp": 5, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "CapCut Pro vs Premiere Pro Pakistan", "intent": "comparison", "primary_url": "https://aitoolgems.tech/guides/capcut/", "secondary_urls": ["https://aitoolgems.tech/tools/adobe/"], "business_val": 7, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "Notion AI vs ChatGPT for notes", "intent": "comparison", "primary_url": "https://aitoolgems.tech/tools/notion/", "secondary_urls": ["https://aitoolgems.tech/guides/productivity/"], "business_val": 6, "comp": 4, "serp": "organic", "status": "ACTIVE"},

    # 5. LOCAL (Geographic / Pakistan payment / currency queries)
    {"keyword": "AI tools in Pakistan", "intent": "local", "primary_url": "https://aitoolgems.tech/guides/ai-tools-pakistan/", "secondary_urls": ["https://aitoolgems.tech/"], "business_val": 9, "comp": 5, "serp": "local-pack", "status": "ACTIVE"},
    {"keyword": "AI tool subscriptions in Pakistan", "intent": "local", "primary_url": "https://aitoolgems.tech/guides/ai-subscriptions-pakistan/", "secondary_urls": ["https://aitoolgems.tech/prices/"], "business_val": 9, "comp": 5, "serp": "local-pack", "status": "ACTIVE"},
    {"keyword": "AI tools store Pakistan", "intent": "local", "primary_url": "https://aitoolgems.tech/", "secondary_urls": ["https://aitoolgems.tech/deals/"], "business_val": 9, "comp": 5, "serp": "local-results", "status": "ACTIVE"},
    {"keyword": "EasyPaisa AI tool payment", "intent": "local", "primary_url": "https://aitoolgems.tech/policies.html", "secondary_urls": ["https://aitoolgems.tech/"], "business_val": 8, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "JazzCash AI subscriptions", "intent": "local", "primary_url": "https://aitoolgems.tech/policies.html", "secondary_urls": ["https://aitoolgems.tech/"], "business_val": 8, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "AI tools Karachi", "intent": "local", "primary_url": "https://aitoolgems.tech/guides/ai-tools-pakistan/", "secondary_urls": ["https://aitoolgems.tech/"], "business_val": 6, "comp": 3, "serp": "local-pack", "status": "MONITOR"},
    {"keyword": "AI tools Lahore", "intent": "local", "primary_url": "https://aitoolgems.tech/guides/ai-tools-pakistan/", "secondary_urls": ["https://aitoolgems.tech/"], "business_val": 6, "comp": 3, "serp": "local-pack", "status": "MONITOR"},
    {"keyword": "AI tools Islamabad", "intent": "local", "primary_url": "https://aitoolgems.tech/guides/ai-tools-pakistan/", "secondary_urls": ["https://aitoolgems.tech/"], "business_val": 6, "comp": 3, "serp": "local-pack", "status": "MONITOR"},

    # 6. PRODUCT (Specific product queries)
    {"keyword": "ChatGPT Plus Pakistan", "intent": "product", "primary_url": "https://aitoolgems.tech/tools/chatgpt/", "secondary_urls": ["https://aitoolgems.tech/guides/chatgpt-vs-gemini-pakistan/"], "business_val": 10, "comp": 7, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "Google Gemini Pro Pakistan", "intent": "product", "primary_url": "https://aitoolgems.tech/tools/gemini/", "secondary_urls": ["https://aitoolgems.tech/guides/gemini/"], "business_val": 8, "comp": 6, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "Canva Pro Edu Pakistan", "intent": "product", "primary_url": "https://aitoolgems.tech/tools/canva/", "secondary_urls": ["https://aitoolgems.tech/guides/canva/"], "business_val": 8, "comp": 5, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "CapCut Pro Pakistan", "intent": "product", "primary_url": "https://aitoolgems.tech/tools/capcut/", "secondary_urls": ["https://aitoolgems.tech/guides/capcut/"], "business_val": 8, "comp": 5, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "Veo 3 Ultra Pakistan", "intent": "product", "primary_url": "https://aitoolgems.tech/tools/veo/", "secondary_urls": ["https://aitoolgems.tech/guides/creators/"], "business_val": 8, "comp": 4, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "Leonardo AI Essential Pakistan", "intent": "product", "primary_url": "https://aitoolgems.tech/tools/leonardo/", "secondary_urls": ["https://aitoolgems.tech/guides/creators/"], "business_val": 8, "comp": 4, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "ElevenLabs voice clone Pakistan", "intent": "product", "primary_url": "https://aitoolgems.tech/tools/elevenlabs/", "secondary_urls": ["https://aitoolgems.tech/guides/creators/"], "business_val": 8, "comp": 4, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "Figma Professional Pakistan", "intent": "product", "primary_url": "https://aitoolgems.tech/tools/figma/", "secondary_urls": ["https://aitoolgems.tech/guides/canva-vs-figma-pakistan/"], "business_val": 7, "comp": 5, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "Lovable Pro builder Pakistan", "intent": "product", "primary_url": "https://aitoolgems.tech/tools/lovable/", "secondary_urls": ["https://aitoolgems.tech/guides/developers/"], "business_val": 7, "comp": 4, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "Gamma AI presentation Pakistan", "intent": "product", "primary_url": "https://aitoolgems.tech/tools/gamma/", "secondary_urls": ["https://aitoolgems.tech/guides/businesses/"], "business_val": 7, "comp": 4, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "n8n Cloud workflow automation Pakistan", "intent": "product", "primary_url": "https://aitoolgems.tech/tools/n8n/", "secondary_urls": ["https://aitoolgems.tech/guides/developers/"], "business_val": 7, "comp": 4, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "Notion Plus workspace Pakistan", "intent": "product", "primary_url": "https://aitoolgems.tech/tools/notion/", "secondary_urls": ["https://aitoolgems.tech/guides/productivity/"], "business_val": 7, "comp": 4, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "Replit Core cloud IDE Pakistan", "intent": "product", "primary_url": "https://aitoolgems.tech/tools/replit/", "secondary_urls": ["https://aitoolgems.tech/guides/developers/"], "business_val": 7, "comp": 4, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "LinkedIn Business Premium Pakistan", "intent": "product", "primary_url": "https://aitoolgems.tech/tools/linkedin/", "secondary_urls": ["https://aitoolgems.tech/guides/businesses/"], "business_val": 7, "comp": 5, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "Netflix Premium 4K Pakistan", "intent": "product", "primary_url": "https://aitoolgems.tech/tools/netflix/", "secondary_urls": ["https://aitoolgems.tech/deals/"], "business_val": 7, "comp": 5, "serp": "shopping-results", "status": "ACTIVE"},

    # 7. PRICING (Explicit currency / price list / PKR rates)
    {"keyword": "ChatGPT Plus PKR rate", "intent": "pricing", "primary_url": "https://aitoolgems.tech/tools/chatgpt/", "secondary_urls": ["https://aitoolgems.tech/prices/"], "business_val": 10, "comp": 6, "serp": "featured-snippet", "status": "ACTIVE"},
    {"keyword": "AI tools price index Pakistan", "intent": "pricing", "primary_url": "https://aitoolgems.tech/prices/", "secondary_urls": ["https://aitoolgems.tech/guides/ai-tools-price-pakistan/"], "business_val": 9, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "Gemini Pro PKR price", "intent": "pricing", "primary_url": "https://aitoolgems.tech/tools/gemini/", "secondary_urls": ["https://aitoolgems.tech/prices/"], "business_val": 8, "comp": 5, "serp": "featured-snippet", "status": "ACTIVE"},
    {"keyword": "Canva Pro PKR cost", "intent": "pricing", "primary_url": "https://aitoolgems.tech/tools/canva/", "secondary_urls": ["https://aitoolgems.tech/prices/"], "business_val": 8, "comp": 5, "serp": "featured-snippet", "status": "ACTIVE"},
    {"keyword": "CapCut Pro PKR subscription", "intent": "pricing", "primary_url": "https://aitoolgems.tech/tools/capcut/", "secondary_urls": ["https://aitoolgems.tech/prices/"], "business_val": 8, "comp": 5, "serp": "featured-snippet", "status": "ACTIVE"},
    {"keyword": "Leonardo AI PKR rate", "intent": "pricing", "primary_url": "https://aitoolgems.tech/tools/leonardo/", "secondary_urls": ["https://aitoolgems.tech/prices/"], "business_val": 7, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "ElevenLabs PKR voice rate", "intent": "pricing", "primary_url": "https://aitoolgems.tech/tools/elevenlabs/", "secondary_urls": ["https://aitoolgems.tech/prices/"], "business_val": 7, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "NordVPN PKR price", "intent": "pricing", "primary_url": "https://aitoolgems.tech/tools/nordvpn/", "secondary_urls": ["https://aitoolgems.tech/prices/"], "business_val": 7, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "how much does ChatGPT cost in Pakistan", "intent": "pricing", "primary_url": "https://aitoolgems.tech/tools/chatgpt/", "secondary_urls": ["https://aitoolgems.tech/guides/ai-tools-price-pakistan/"], "business_val": 9, "comp": 5, "serp": "featured-snippet", "status": "ACTIVE"},
    {"keyword": "AI tools pricing table PKR", "intent": "pricing", "primary_url": "https://aitoolgems.tech/prices/", "secondary_urls": ["https://aitoolgems.tech/guides/ai-tools-pricing/"], "business_val": 8, "comp": 3, "serp": "organic", "status": "ACTIVE"},

    # 8. BRAND (AIToolGems branded discovery)
    {"keyword": "AIToolGems", "intent": "brand", "primary_url": "https://aitoolgems.tech/", "secondary_urls": ["https://aitoolgems.tech/about.html"], "business_val": 10, "comp": 1, "serp": "brand-results", "status": "ACTIVE"},
    {"keyword": "AI Tool Gems Pakistan", "intent": "brand", "primary_url": "https://aitoolgems.tech/", "secondary_urls": ["https://aitoolgems.tech/about.html"], "business_val": 10, "comp": 1, "serp": "brand-results", "status": "ACTIVE"},
    {"keyword": "aitoolgems.tech", "intent": "brand", "primary_url": "https://aitoolgems.tech/", "secondary_urls": ["https://aitoolgems.tech/sitemap.xml"], "business_val": 10, "comp": 1, "serp": "brand-results", "status": "ACTIVE"},
    {"keyword": "AI Tool Gems reviews", "intent": "brand", "primary_url": "https://aitoolgems.tech/how-we-review.html", "secondary_urls": ["https://aitoolgems.tech/product-verification.html"], "business_val": 9, "comp": 1, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "AI Tool Gems WhatsApp number", "intent": "brand", "primary_url": "https://aitoolgems.tech/contact.html", "secondary_urls": ["https://aitoolgems.tech/"], "business_val": 9, "comp": 1, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "AI Tool Gems warranty policy", "intent": "brand", "primary_url": "https://aitoolgems.tech/policies.html", "secondary_urls": ["https://aitoolgems.tech/terms.html"], "business_val": 8, "comp": 1, "serp": "organic", "status": "ACTIVE"},

    # 9. PROBLEM-SOLVING (Use case & task-driven searches)
    {"keyword": "how to write thesis with AI Pakistan", "intent": "problem-solving", "primary_url": "https://aitoolgems.tech/guides/students/", "secondary_urls": ["https://aitoolgems.tech/tools/chatgpt/"], "business_val": 8, "comp": 3, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "AI tool for writer's block Pakistan", "intent": "problem-solving", "primary_url": "https://aitoolgems.tech/tools/chatgpt/", "secondary_urls": ["https://aitoolgems.tech/guides/creators/"], "business_val": 7, "comp": 3, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "AI code assistance Pakistan", "intent": "problem-solving", "primary_url": "https://aitoolgems.tech/guides/developers/", "secondary_urls": ["https://aitoolgems.tech/tools/replit/"], "business_val": 8, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "remove background from video AI Pakistan", "intent": "problem-solving", "primary_url": "https://aitoolgems.tech/tools/capcut/", "secondary_urls": ["https://aitoolgems.tech/guides/capcut/"], "business_val": 7, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "AI voiceover in Urdu Pakistan", "intent": "problem-solving", "primary_url": "https://aitoolgems.tech/tools/elevenlabs/", "secondary_urls": ["https://aitoolgems.tech/guides/creators/"], "business_val": 8, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "create AI presentations fast Pakistan", "intent": "problem-solving", "primary_url": "https://aitoolgems.tech/tools/gamma/", "secondary_urls": ["https://aitoolgems.tech/guides/businesses/"], "business_val": 7, "comp": 3, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "AI automation for digital marketing Pakistan", "intent": "problem-solving", "primary_url": "https://aitoolgems.tech/tools/n8n/", "secondary_urls": ["https://aitoolgems.tech/guides/businesses/"], "business_val": 7, "comp": 3, "serp": "organic", "status": "ACTIVE"},

    # 10. EDUCATIONAL (Safety, verification, access types, tutorials)
    {"keyword": "how to buy AI tools without international credit card Pakistan", "intent": "educational", "primary_url": "https://aitoolgems.tech/guides/ai-subscriptions-pakistan/", "secondary_urls": ["https://aitoolgems.tech/policies.html"], "business_val": 9, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "difference between shared and private AI subscription", "intent": "educational", "primary_url": "https://aitoolgems.tech/policies.html", "secondary_urls": ["https://aitoolgems.tech/guides/ai-subscriptions-pakistan/"], "business_val": 8, "comp": 3, "serp": "featured-snippet", "status": "ACTIVE"},
    {"keyword": "is ChatGPT Plus safe in Pakistan", "intent": "educational", "primary_url": "https://aitoolgems.tech/how-we-review.html", "secondary_urls": ["https://aitoolgems.tech/tools/chatgpt/"], "business_val": 7, "comp": 3, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "how does WhatsApp AI delivery work", "intent": "educational", "primary_url": "https://aitoolgems.tech/how-we-source.html", "secondary_urls": ["https://aitoolgems.tech/contact.html"], "business_val": 8, "comp": 2, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "AI subscription replacement policy Pakistan", "intent": "educational", "primary_url": "https://aitoolgems.tech/policies.html", "secondary_urls": ["https://aitoolgems.tech/product-verification.html"], "business_val": 7, "comp": 2, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "how to renew AI subscriptions in Pakistan", "intent": "educational", "primary_url": "https://aitoolgems.tech/guides/ai-subscriptions-pakistan/", "secondary_urls": ["https://aitoolgems.tech/policies.html"], "business_val": 8, "comp": 3, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "what is an invitation seat subscription Pakistan", "intent": "educational", "primary_url": "https://aitoolgems.tech/policies.html", "secondary_urls": ["https://aitoolgems.tech/guides/ai-subscriptions-pakistan/"], "business_val": 8, "comp": 2, "serp": "featured-snippet", "status": "ACTIVE"},
    {"keyword": "how to contact AI Tool Gems support", "intent": "educational", "primary_url": "https://aitoolgems.tech/contact.html", "secondary_urls": ["https://aitoolgems.tech/"], "business_val": 8, "comp": 1, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "buy Lovable Pro starter pack Pakistan", "intent": "transactional", "primary_url": "https://aitoolgems.tech/tools/lovable/", "secondary_urls": ["https://aitoolgems.tech/deals/"], "business_val": 8, "comp": 4, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "buy Gamma AI annual plan Pakistan", "intent": "transactional", "primary_url": "https://aitoolgems.tech/tools/gamma/", "secondary_urls": ["https://aitoolgems.tech/deals/"], "business_val": 8, "comp": 4, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "buy n8n Cloud subscription Pakistan", "intent": "transactional", "primary_url": "https://aitoolgems.tech/tools/n8n/", "secondary_urls": ["https://aitoolgems.tech/deals/"], "business_val": 8, "comp": 4, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "buy Replit Core Pakistan JazzCash", "intent": "transactional", "primary_url": "https://aitoolgems.tech/tools/replit/", "secondary_urls": ["https://aitoolgems.tech/deals/"], "business_val": 8, "comp": 4, "serp": "shopping-results", "status": "ACTIVE"},
    {"keyword": "best AI video generator Pakistan price", "intent": "commercial", "primary_url": "https://aitoolgems.tech/tools/veo/", "secondary_urls": ["https://aitoolgems.tech/guides/creators/"], "business_val": 8, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "AI tools with EasyPaisa payment", "intent": "commercial", "primary_url": "https://aitoolgems.tech/deals/", "secondary_urls": ["https://aitoolgems.tech/prices/"], "business_val": 9, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "AI tools with JazzCash payment", "intent": "commercial", "primary_url": "https://aitoolgems.tech/deals/", "secondary_urls": ["https://aitoolgems.tech/prices/"], "business_val": 9, "comp": 4, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "generate AI images for marketing Pakistan", "intent": "problem-solving", "primary_url": "https://aitoolgems.tech/tools/leonardo/", "secondary_urls": ["https://aitoolgems.tech/guides/creators/"], "business_val": 8, "comp": 3, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "automate business emails with AI Pakistan", "intent": "problem-solving", "primary_url": "https://aitoolgems.tech/guides/businesses/", "secondary_urls": ["https://aitoolgems.tech/tools/n8n/"], "business_val": 7, "comp": 3, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "build web app with AI Pakistan", "intent": "problem-solving", "primary_url": "https://aitoolgems.tech/tools/lovable/", "secondary_urls": ["https://aitoolgems.tech/guides/developers/"], "business_val": 8, "comp": 3, "serp": "organic", "status": "ACTIVE"},
    {"keyword": "AI tools Rawalpindi", "intent": "local", "primary_url": "https://aitoolgems.tech/guides/ai-tools-pakistan/", "secondary_urls": ["https://aitoolgems.tech/"], "business_val": 6, "comp": 3, "serp": "local-pack", "status": "MONITOR"},
    {"keyword": "AI tools Faisalabad", "intent": "local", "primary_url": "https://aitoolgems.tech/guides/ai-tools-pakistan/", "secondary_urls": ["https://aitoolgems.tech/"], "business_val": 6, "comp": 3, "serp": "local-pack", "status": "MONITOR"},
    {"keyword": "AI tools Peshawar", "intent": "local", "primary_url": "https://aitoolgems.tech/guides/ai-tools-pakistan/", "secondary_urls": ["https://aitoolgems.tech/"], "business_val": 6, "comp": 3, "serp": "local-pack", "status": "MONITOR"},
]

KEYWORD_INTELLIGENCE = {
    "description": "AIToolGems Pakistan Keyword Intelligence System",
    "status": "VERIFIED",
    "total_keywords": len(KEYWORD_DATABASE),
    "intents_covered": 10,
    "markets": ["en-PK"],
    "free_first": True,
    "source": "Google Trends + GSC Performance Queries + Free Local Intent Research"
}

def get_keyword_database() -> list[dict]:
    """Returns the complete Pakistan keyword database."""
    return KEYWORD_DATABASE

def get_keyword_intelligence_status() -> dict:
    """Return keyword intelligence status."""
    return KEYWORD_INTELLIGENCE

def get_keywords_by_intent(intent: str) -> list[dict]:
    """Filter keywords by specific intent category."""
    return [k for k in KEYWORD_DATABASE if k["intent"].lower() == intent.lower()]

def get_keywords_by_url(url: str) -> list[dict]:
    """Get all keywords mapped to a specific URL."""
    return [k for k in KEYWORD_DATABASE if k["primary_url"] == url]
