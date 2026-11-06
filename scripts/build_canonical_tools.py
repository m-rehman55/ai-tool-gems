import csv
import json
import re
from collections import defaultdict

# Master rule table: (Canonical Tool Name, Regex Pattern, Official Publisher/Developer, Official Category)
RULES = [
        # 1. AI Chatbots, LLMs & Multi-Modal Models
        ('ChatGPT / OpenAI', r'(?i)\b(chatgpt|gpt-?4|gpt-?3\.5|codex|zapi codex|chat gpt|openai|gpt pro|gpt plus|gpt go|gpt business)\b', 'OpenAI', 'AI Chatbots, LLMs & Reasoning'),
        ('Claude (Anthropic)', r'(?i)\b(claude|anthropic)\b', 'Anthropic', 'AI Chatbots, LLMs & Reasoning'),
        ('Google Gemini Advanced / Google One AI', r'(?i)\b(gemini|gg ai|google ai|google advance|google one ai)\b', 'Google', 'AI Chatbots, LLMs & Reasoning'),
        ('xAI Grok', r'(?i)\b(grok|xai|supergrok)\b', 'xAI', 'AI Chatbots, LLMs & Reasoning'),
        ('DeepSeek AI', r'(?i)\b(deepseek)\b', 'DeepSeek', 'AI Chatbots, LLMs & Reasoning'),
        ('Perplexity AI', r'(?i)\b(perplexity)\b', 'Perplexity AI', 'AI Chatbots, LLMs & Search'),
        ('Poe (Quora)', r'(?i)\b(poe\.com|poe\b)', 'Quora', 'AI Chatbots & Multi-Model Hub'),
        ('Microsoft Copilot', r'(?i)\b(copilot|co-pilot|github copilot)\b', 'Microsoft', 'AI Assistants & Coding'),
        ('Qwen AI (Alibaba Cloud)', r'(?i)\b(qwen)\b', 'Alibaba Cloud', 'AI Chatbots & LLMs'),
        ('Chinese Unified LLMs (DeepSeek/Qwen/GLM/Kimi)', r'(?i)\b(chinese model)\b', 'Moonshot / Zhipu / Baichuan', 'High-Capacity API Model Aggregator'),
        ('Manus AI', r'(?i)\b(manus)\b', 'Manus AI', 'Autonomous AI Agents'),
        ('Monica AI', r'(?i)\b(monica|monica\.im)\b', 'Monica', 'All-in-One AI Copilot'),
        ('Sider AI', r'(?i)\b(sider)\b', 'Sider', 'Browser AI Sidebar Copilot'),
        ('HARPA AI', r'(?i)\b(harpa)\b', 'HARPA AI', 'AI Web Automation & Chrome Agent'),
        ('You.com AI', r'(?i)\b(you\.com)\b', 'SuSea Inc. (You.com)', 'AI Search & Chatbot'),
        ('Liner AI', r'(?i)\b(liner)\b', 'Liner', 'AI Workspace & Research Copilot'),
        ('FlowUs AI', r'(?i)\b(flowus)\b', 'FlowUs', 'AI Collaborative Workspace'),
        ('Notion & Notion AI', r'(?i)\b(notion)\b', 'Notion Labs, Inc.', 'Productivity & AI Workspace'),
        ('Genspark AI', r'(?i)\b(genspark)\b', 'MainFunc Inc.', 'Autonomous AI Search & Knowledge Agent'),
        ('Morphic AI', r'(?i)\b(morphic)\b', 'Morphic AI', 'AI Generative Search & Research'),
        ('ChatPRD', r'(?i)\b(chatprd)\b', 'Claire Vo', 'AI Product Management & PRD Assistant'),
        ('Antigravity (Google / AGY)', r'(?i)\b(antigravity)\b', 'Google DeepMind', 'Advanced Agentic Coding & Workflow AI'),

        # 2. AI Video Generation, Avatars & Video Editing
        ('OpenAI Sora', r'(?i)\b(sora)\b', 'OpenAI', 'AI Video Generation'),
        ('Google Veo', r'(?i)\b(veo|google veo|veo3|veo4)\b', 'Google DeepMind', 'Generative Cinematic AI Video'),
        ('Runway AI (Gen-2 / Gen-3 Alpha)', r'(?i)\b(runway|runwayml|gen-?2|gen-?3)\b', 'Runway AI, Inc.', 'Cinematic Generative AI Video'),
        ('Pika Labs AI', r'(?i)\b(pika|pika\.art)\b', 'Pika Art, Inc.', 'Generative AI Video & 3D Effects'),
        ('Luma Dream Machine AI', r'(?i)\b(luma|dream machine)\b', 'Luma AI', 'High-Fidelity 3D & AI Video'),
        ('Kling AI (Kuaishou)', r'(?i)\b(kling|klingai)\b', 'Kuaishou Technology', 'Realistic AI Video Generation & Motion'),
        ('MiniMax / Hailuo AI', r'(?i)\b(hailuo|minimax)\b', 'MiniMax Technology', 'Next-Gen Generative AI Video & Voice'),
        ('Higgsfield AI', r'(?i)\b(higgsfield|higg\b|higgfield)\b', 'Higgsfield AI', 'Hyper-Realistic AI Video & Camera Motion'),
        ('Seedance AI (ByteDance)', r'(?i)\b(seedance)\b', 'ByteDance', 'Generative AI Video Animation Engine'),
        ('Domo AI', r'(?i)\b(domo ai|domo stand)\b', 'Domo AI', 'AI Video Style Transfer & Anime Morphing'),
        ('Dreamina AI (ByteDance)', r'(?i)\b(dreamina)\b', 'ByteDance', 'Creative Generative AI Video & Art'),
        ('InVideo AI', r'(?i)\b(invideo)\b', 'InVideo', 'Automated Script-to-Video AI Generator'),
        ('Fliki AI', r'(?i)\b(fliki)\b', 'Fliki Technologies', 'Text-to-Video & AI Voiceover Generator'),
        ('HeyGen AI', r'(?i)\b(heygen)\b', 'HeyGen', 'AI Video Avatars & Studio Translation'),
        ('Synthesia AI', r'(?i)\b(synthesia)\b', 'Synthesia', 'Enterprise AI Video Avatars & Training'),
        ('D-ID AI', r'(?i)\b(d-?id)\b', 'D-ID', 'Talking Heads & AI Digital Avatars'),
        ('Viggle AI', r'(?i)\b(viggle)\b', 'Viggle', 'Character Controllable Video Generation'),
        ('Topview AI', r'(?i)\b(topview)\b', 'Topview AI', 'Viral Ecommerce Product Video Generator'),
        ('Hedra AI (Character-1)', r'(?i)\b(hedra)\b', 'Hedra', 'Conversational AI Video Avatars'),
        ('Vidnoz AI', r'(?i)\b(vidnoz)\b', 'Vidnoz', 'Free & Pro AI Video Generation & Clones'),
        ('PolloAI', r'(?i)\b(polloai)\b', 'Pollo AI', 'All-in-One Multi-Model AI Video Platform'),
        ('Akool AI', r'(?i)\b(akool)\b', 'Akool Inc.', 'Generative Face Swap & Virtual Avatars'),
        ('Muse AI', r'(?i)(muse ai|muse\.ai|muse api|ref muse)', 'Muse AI', 'Next-Gen AI Video Search & Player Cloud'),
        ('CapCut Pro / Teams', r'(?i)\b(capcut)\b', 'ByteDance', 'Short-Form Video Editing & AI Effects'),
        ('DaVinci Resolve / DaVinci AI Video', r'(?i)\b(davinci)\b', 'Blackmagic Design', 'Professional Video Editing, Color Grading & Seedance Video Generation'),
        ('Wondershare Filmora', r'(?i)\b(filmora|wondershare)\b', 'Wondershare', 'Desktop Video Editing & Motion Graphics'),
        ('Descript', r'(?i)\b(descript)\b', 'Descript, Inc.', 'Audio/Video Podcasting & Transcription Editor'),
        ('Artlist.io Max', r'(?i)\b(artlist)\b', 'Artlist Ltd.', 'Royalty-Free Music, SFX, Footage & Plugins'),
        ('Motion Array', r'(?i)\b(motion array)\b', 'Artlist Ltd.', 'Video Templates, Presets & Stock Assets'),
        ('Supercut AI', r'(?i)\b(supercut)\b', 'Supercut AI', 'AI Long-Form to Viral Shorts Clip Generator'),
        ('Pipit Pro AI', r'(?i)\b(pipit)\b', 'ByteDance (Pipit)', 'AI Video Generation & Commercial Ad Optimization'),
        ('Newtake AI', r'(?i)\b(newtake)\b', 'Newtake AI', 'Generative Portrait Video & Scene Animator'),
        ('Dropshot AI', r'(?i)\b(dropshot)\b', 'Dropshot AI', 'AI Visual FX & Sports Highlight Generation'),
        ('Wink Video Retouching (Meitu)', r'(?i)\b(wink)\b', 'Meitu, Inc.', 'AI 4K Video Quality Restoration & Retouching'),
        ('BeautyCam (Meitu)', r'(?i)\b(beautycam)\b', 'Meitu, Inc.', 'AI Portrait Photography & Face Retouching'),
        ('Meitu SVIP / VIP', r'(?i)\b(meitu)\b', 'Meitu, Inc.', 'Mobile & Desktop AI Photo/Video Editor'),
        ('Xingtu (醒图 / ByteDance)', r'(?i)\b(xingtu)\b', 'ByteDance', 'Professional Mobile Photo & Aesthetics Retoucher'),

        # 3. AI Image, Art, UI & Design
        ('Midjourney', r'(?i)\b(midjourney)\b', 'Midjourney, Inc.', 'Photorealistic Text-to-Image AI'),
        ('Canva Pro / Edu / Teams', r'(?i)\b(canva|cavan)\b', 'Canva Pty Ltd', 'Graphic Design, Brand Kits & Magic Studio'),
        ('Adobe Creative Cloud / Acrobat Pro', r'(?i)\b(adobe|photoshop|illustrator|premiere|lightroom|acrobat)\b', 'Adobe Inc.', 'Professional Design, Creative Suite & PDF'),
        ('Figma Pro / Organization', r'(?i)\b(figma)\b', 'Figma, Inc.', 'Collaborative Interface & UI/UX Design Tool'),
        ('Freepik Premium', r'(?i)\b(freepik)\b', 'Freepik Company', 'Vectors, Stock Photos, PSDs & AI Art Suite'),
        ('Envato Elements', r'(?i)\b(envato|elements)\b', 'Envato Pty Ltd', 'Unlimited Digital Creative Asset Subscription'),
        ('Recraft AI', r'(?i)\b(recraft)\b', 'Recraft', 'Infinite Vector & 3D AI Graphic Generator'),
        ('Leonardo.Ai', r'(?i)\b(leonardo|leonardo\.ai)\b', 'Canva (Leonardo.Ai)', 'Production-Ready AI Art & Game Assets'),
        ('Magnific AI', r'(?i)\b(magnific)\b', 'Freepik (Magnific AI)', 'Ultra-High-Resolution AI Image Upscaler'),
        ('Krea AI', r'(?i)\b(krea|krea\.ai)\b', 'Krea AI', 'Real-Time Generative AI Canvas & Video Upscaling'),
        ('Ideogram AI', r'(?i)\b(ideogram)\b', 'Ideogram Inc.', 'Typography-Accurate AI Image Generator'),
        ('OpenArt AI', r'(?i)\b(openart)\b', 'OpenArt Inc.', 'AI Art Studio & Model Fine-Tuning Platform'),
        ('Flora AI', r'(?i)(flora|flora\.ai)', 'Flora AI', 'AI Fashion Design, Outfit Rendering & Virtual Try-On'),
        ('Byflux.ai', r'(?i)byflux', 'Byflux', 'AI Image Processing & Workflow Orchestration'),
        ('LartAI', r'(?i)lartai', 'LartAI', 'Generative Anime, Manga & Digital Art Engine'),
        ('LumiYing AI', r'(?i)lumiying', 'LumiYing', 'Specialized AI Character & Comic Art Creator'),
        ('Cuty AI', r'(?i)\b(cuty)\b', 'Cuty AI', 'AI Portrait Generation & Filter Effects'),
        ('Clipdrop (Jasper)', r'(?i)\b(clipdrop)\b', 'Jasper (Stability AI)', 'AI Image Relighting, Cleanup & Background Swap'),
        ('PhotoRoom Pro', r'(?i)\b(photoroom)\b', 'PhotoRoom', 'AI Product Photography & Background Removal'),
        ('PicsArt Gold', r'(?i)\b(picsart)\b', 'PicsArt, Inc.', 'Creative Photo & Video Editor Mobile Suite'),
        ('Shutterstock', r'(?i)\b(shutterstock)\b', 'Shutterstock, Inc.', 'Stock Photography, Vectors & Footage Library'),
        ('Vecteezy Pro', r'(?i)\b(vecteezy)\b', 'Eezy Inc.', 'Vector Graphics, Stock Photos & Video Footage'),
        ('CorelDRAW Graphics Suite', r'(?i)\b(coreldraw)\b', 'Alludo (Corel)', 'Professional Vector Illustration & Page Layout'),
        ('Autodesk (AutoCAD / 3ds Max / Maya)', r'(?i)\b(autodesk|autocad|3ds max|maya)\b', 'Autodesk, Inc.', '3D CAD, Engineering & VFX Animation Software'),
        ('Meshy AI (3D Generative)', r'(?i)\b(meshy)\b', 'Meshy Inc.', 'Text-to-3D & Image-to-3D Generative AI Engine'),
        ('Magic Patterns', r'(?i)\b(magic patterns|magic pattern)\b', 'Magic Patterns', 'AI Prototyping for UI Components & Design Systems'),
        ('Mobbin UI/UX Library', r'(?i)\b(mobbin)\b', 'Mobbin Design', 'World Largest Mobile & Web UI Design Pattern Archive'),
        ('Framer Pro', r'(?i)\b(framer)\b', 'Framer B.V.', 'Interactive Website Design & React Publishing Platform'),
        ('Renderforest', r'(?i)\b(renderforest)\b', 'Renderforest', 'All-in-One Branding, Mockups, Videos & Websites'),

        # 4. AI Voice, Audio, Speech & Music
        ('ElevenLabs', r'(?i)(elevenlabs|eleven labs|elevanlabs|eleven reader|elevenlab|elevene)', 'ElevenLabs Inc.', 'AI Voice Cloning, Text-to-Speech & Sound FX'),
        ('Suno AI', r'(?i)\b(suno|suno\.ai)\b', 'Suno Inc.', 'Generative AI Full Song & Music Composer'),
        ('Udio AI', r'(?i)\b(udio)\b', 'Udio (Uncharted Labs)', 'High-Fidelity AI Music Generation & Vocals'),
        ('Brain.fm', r'(?i)\b(brain\.fm|brainfm)\b', 'Brain.fm Inc.', 'Science-Backed AI Functional Focus & Sleep Music'),
        ('Voice.ai', r'(?i)\b(voiceai|voice\.ai)\b', 'Voice.ai', 'Real-Time AI Voice Changer & Voice Marketplace'),
        ('LALAL.AI', r'(?i)\b(lalal|lalal\.ai)\b', 'Omnisale GmbH', 'High-Precision AI Vocal & Stem Audio Splitter'),
        ('Murf AI', r'(?i)\b(murf|murf\.ai)\b', 'Murf Inc.', 'Studio-Quality AI Voiceovers for Video & Ads'),
        ('Speechify Premium', r'(?i)\b(speechify)\b', 'Speechify Inc.', 'AI Text-to-Speech Audio Reader with Celebrity Voices'),
        ('Voicemaker AI', r'(?i)\b(voicemaker)\b', 'Voicemaker', 'Commercial AI Voiceover & Audio Synthesis'),
        ('Wispr Flow', r'(?i)\b(wispr|wispr flow)\b', 'Wispr Technologies', 'Ultra-Fast AI Voice Dictation for Mac & Windows'),

        # 5. Developer, Software Engineering & Cloud Infrastructure
        ('Cursor AI Code Editor', r'(?i)\b(cursor|cursor ai|cusor)\b', 'Anysphere', 'AI-First Code Editor Built on VS Code Fork'),
        ('Lovable.dev AI', r'(?i)\b(lovable)\b', 'Lovable', 'Full-Stack Autonomous Web App Builder from Natural Language'),
        ('v0 by Vercel', r'(?i)\b(v0|v0\.dev)\b', 'Vercel, Inc.', 'Generative UI & Full-Stack React Component Engine'),
        ('Bolt.new (StackBlitz)', r'(?i)\b(bolt|bolt\.new)\b', 'StackBlitz', 'In-Browser Full-Stack AI Web Development Sandbox'),
        ('Bilt.me Vibe Coding AI', r'(?i)(bilt\.me|bilt)', 'Bilt.me', 'AI Vibe Coding & Autonomous Fullstack Development Platform'),
        ('Replit Core', r'(?i)\b(replit)\b', 'Replit, Inc.', 'Collaborative Cloud IDE & Deployment Platform'),
        ('Windsurf Editor (Codeium)', r'(?i)\b(windsurf|codeium)\b', 'Codeium (Exafunction)', 'Agentic AI IDE with Cascade Autonomous Flow'),
        ('JetBrains All Products Pack', r'(?i)\b(jetbrains|jetbrain)\b', 'JetBrains s.r.o.', 'Professional IDEs (IntelliJ, PyCharm, WebStorm)'),
        ('GitHub Copilot / Developer Pack', r'(?i)\b(github)\b', 'GitHub (Microsoft)', 'Code Hosting, CI/CD Actions & AI Pair Programming'),
        ('GitKraken Pro', r'(?i)\b(gitkraken)\b', 'Axosoft (GitKraken)', 'Visual Git GUI Client, GitLens & Workspaces'),
        ('Tabnine Pro', r'(?i)\b(tabnine)\b', 'Tabnine Inc.', 'Privacy-Focused Enterprise AI Code Completion'),
        ('Factory AI (Droid)', r'(?i)\b(factory|factory pro)\b', 'Factory', 'Autonomous AI Software Engineering Droids'),
        ('Elser.ai', r'(?i)(elser\.ai|elser)', 'Elser.ai', 'AI Reasoning, Coding & Task Execution Engine'),
        ('Buzzy AI App Builder', r'(?i)\b(buzzy)\b', 'Buzzy AI Pty Ltd', 'No-Code AI Full-Stack Web & Mobile App Creator'),
        ('Railway.app Cloud Platform', r'(?i)\b(railway)\b', 'Railway Corp.', 'Instant Cloud Infrastructure & Database Hosting'),
        ('Supabase Pro', r'(?i)\b(supabase)\b', 'Supabase Inc.', 'Open Source Firebase Alternative (Postgres / Auth / Storage)'),
        ('Amazon Web Services (AWS)', r'(?i)\b(aws|amazon web services)\b', 'Amazon Web Services', 'Cloud Computing, Virtual Servers & S3 Storage'),
        ('Google Cloud Platform (GCP)', r'(?i)\b(google cloud|gcp)\b', 'Google LLC', 'Cloud Compute, Vertex AI & BigQuery Infrastructure'),
        ('Radix .TECH Domain Registrations', r'(?i)(\.tech\b|tech domain)', 'Radix Registry', 'Top-Level Domain Registry for Tech Brands & Developers'),
        ('n8n Automation', r'(?i)\b(n8n)\b', 'n8n GmbH', 'Fair-Code Workflow Automation & AI Agent Chains'),
        ('Gumloop Pro', r'(?i)\b(gumloop)\b', 'Gumloop Inc.', 'Visual Drag-and-Drop AI Workflow Automation Platform'),
        ('Firecrawl AI Crawler', r'(?i)\b(firecrawl)\b', 'Mendable (Firecrawl)', 'Turn Entire Websites into Clean Markdown for LLMs'),
        ('Warp Build CI/CD', r'(?i)\b(warp build)\b', 'Warp Build Inc.', 'High-Speed Cloud Runners for GitHub Actions'),
        ('Jam.dev Bug Reporting', r'(?i)\b(jam team|jam\.dev)\b', 'Jam', 'One-Click Instant Bug Reporting & Developer Diagnostics'),
        ('Resend Email API', r'(?i)\b(resend)\b', 'Resend Inc.', 'Modern Developer-First Email Delivery API'),
        ('Linear App', r'(?i)\b(linear)\b', 'Linear Orbit, Inc.', 'Purpose-Built Issue Tracking & Product Roadmap Tool'),
        ('Airtable Plus / Pro', r'(?i)\b(airtable)\b', 'Formagrid Inc. (Airtable)', 'Relational Database & Low-Code Workflow Platform'),
        ('Customer.io Messaging', r'(?i)\b(customer\.io)\b', 'Customer.io', 'Automated Omnichannel Customer Engagement & Email'),
        ('Intercom Advanced', r'(?i)\b(intercom)\b', 'Intercom, Inc.', 'AI Customer Support & Fin Service Agent Platform'),
        ('Granola AI Notepad', r'(?i)\b(granola)\b', 'Granola Systems', 'AI Meeting Notepad that Enhances Human Notes'),
        ('Proxyscrape Residential Proxies', r'(?i)\b(proxyscrape)\b', 'ProxyScrape', 'High-Anonymity Rotating Residential Proxy Network'),
        ('GPM Login Anti-Detect Browser', r'(?i)\b(gpm login)\b', 'GPM Technologies', 'Anti-Detect Multi-Accounting Browser Profile Isolation'),

        # 6. SEO, Growth, Marketing & Market Intelligence
        ('Semrush Pro / Guru', r'(?i)\b(semrush)\b', 'Semrush Inc.', 'Keyword Research, Backlink Audit & Competitive Intelligence'),
        ('Ahrefs Standard', r'(?i)\b(ahrefs)\b', 'Ahrefs Pte. Ltd.', 'SEO Toolset, Live Web Crawler & Link Graph Index'),
        ('Moz Pro', r'(?i)\b(moz|moz pro)\b', 'Moz (Ziff Davis)', 'Domain Authority, Rank Tracking & On-Page SEO'),
        ('Ubersuggest Pro', r'(?i)\b(ubersuggest)\b', 'Neil Patel Digital', 'SEO Keyword Discovery & Content Opportunities'),
        ('SpyFu Pro', r'(?i)\b(spyfu)\b', 'SpyFu Inc.', 'Competitor PPC & Organic Keyword Research'),
        ('Serpstat', r'(?i)\b(serpstat)\b', 'Serpstat', 'All-in-One SEO Platform & Competitor Analysis'),
        ('Similarweb Pro', r'(?i)\b(similarweb)\b', 'Similarweb Ltd.', 'Website Traffic Analytics & Market Benchmark Intelligence'),
        ('vidIQ Boost', r'(?i)\b(vidiq)\b', 'vidIQ', 'YouTube Video SEO, Keyword Ranking & Channel Growth'),
        ('Helium 10 Platinum', r'(?i)\b(helium 10|helium10)\b', 'Helium 10', 'Amazon Seller Analytics, Keyword Tracker & Product Finder'),
        ('Jungle Scout', r'(?i)\b(jungle scout)\b', 'Jungle Scout', 'Amazon FBA Product Research & Sales Estimator'),
        ('KeywordTool.io Pro', r'(?i)\b(keywordtool|keyword tool)\b', 'Keyword Tool', 'Long-Tail Keyword Discovery for Google, YouTube & Amazon'),
        ('BuzzSumo Pro', r'(?i)\b(buzzsumo)\b', 'Brandwatch (BuzzSumo)', 'Content Performance, Viral Trend & Influencer Discovery'),
        ('PostHog Scale', r'(?i)\b(posthog)\b', 'PostHog, Inc.', 'Product Analytics, Session Replays, Feature Flags & Funnels'),
        ('TradingView Premium', r'(?i)\b(tradingview)\b', 'TradingView Inc.', 'Financial Markets Charting, Technical Screener & Trading'),

        # 7. AI Writing, Paraphrasing, Detection & Presentation
        ('Gamma AI Presentations', r'(?i)\b(gamma)\b', 'Gamma App, Inc.', 'AI Slide Decks, Interactive Webpages & Documentation'),
        ('QuillBot Premium', r'(?i)\b(quillbot)\b', 'Learneo (QuillBot)', 'AI Paraphraser, Grammar Checker & Summarizer'),
        ('Grammarly Premium', r'(?i)\b(grammarly|grammrly)\b', 'Grammarly, Inc.', 'AI Writing Assistant, Tone Tuning & Style Improvement'),
        ('Turnitin Plagiarism Detection', r'(?i)\b(turnitin)\b', 'Advance Publications (Turnitin)', 'Academic Integrity, Plagiarism Check & AI Content Score'),
        ('Jasper AI', r'(?i)\b(jasper|jasper\.ai)\b', 'Jasper AI, Inc.', 'Enterprise Marketing AI Copywriting & Brand Voice'),
        ('Copy.ai Pro', r'(?i)\b(copy\.ai)\b', 'Copy.ai', 'GTM AI Workflows & Automated Content Creation'),
        ('Writesonic / Chatsonic', r'(?i)\b(writesonic)\b', 'Writesonic, Inc.', 'SEO Articles, Marketing Copy & Generative AI Bot'),
        ('Rytr Premium', r'(?i)\b(rytr)\b', 'Copysmith (Rytr)', 'Budget AI Content Writer for Emails & Social Media'),
        ('ZeroGPT Premium', r'(?i)\b(zerogpt)\b', 'ZeroGPT', 'High-Accuracy AI Content & LLM Detection Engine'),
        ('Originality.ai', r'(?i)\b(originality|originality\.ai)\b', 'Originality.ai', 'AI Detector & Plagiarism Checker for Web Publishers'),
        ('HIX.AI Bypass', r'(?i)\b(hix|hix\.ai)\b', 'HIX.AI', 'AI Text Humanizer & Anti-AI Detection Bypasser'),
        ('BypassGPT', r'(?i)\b(bypassgpt)\b', 'BypassGPT', 'Undetectable AI Rewriter & Human Tone Generator'),
        ('StealthWriter Pro', r'(?i)\b(stealthwriter)\b', 'StealthWriter', 'Ninja AI Detection Bypass & Text Humanizer'),
        ('Undetectable AI', r'(?i)\b(underectable|undetectable)\b', 'Undetectable AI', 'AI Content Humanizer & Readability Optimizer'),
        ('Pangram AI Humanizer', r'(?i)\b(pangram)\b', 'Pangram Labs', 'AI Detection Defense & Text Humanization Platform'),
        ('WordHero AI', r'(?i)\b(wordhero)\b', 'WordHero', 'Long-Form Blog & Marketing Copy AI Generator'),
        ('Wordtune Premium', r'(?i)\b(wordtune)\b', 'AI21 Labs', 'Deep Sentence Phrasing & Contextual Re-Writing'),
        ('Rezi AI Resume Builder', r'(?i)\b(rezi)\b', 'Rezi, Inc.', 'ATS-Optimized Resume, Cover Letter & CV Builder'),
        ('Clico AI / Tryclico', r'(?i)\b(tryclico|clico)\b', 'Clico Technologies', 'AI Content Repurposing & Multi-Channel Copywriting'),
        ('Fiesta AI', r'(?i)\b(fiesta)\b', 'Fiesta AI', 'AI Marketing Workflow & Social Lead Generator'),
        ('Ecoboms AI', r'(?i)\b(ecoboms)\b', 'Ecoboms', 'AI Content Assistant & Automated Social Captions'),

        # 8. Productivity, Documents, Operating Systems & Office
        ('Microsoft 365 / Office Suite', r'(?i)\b(office 365|microsoft 365|m365|ms office|ms365|key office|microsoft office)\b', 'Microsoft Corporation', 'Word, Excel, PowerPoint, Outlook & 1TB OneDrive Cloud'),
        ('Microsoft Windows Pro OS', r'(?i)\b(windows 10|windows 11|windows pro|retail online 100-year)\b', 'Microsoft Corporation', 'Official Windows 10/11 Professional Desktop Operating System'),
        ('Zoom Pro / Business', r'(?i)\b(zoom|zoom pro)\b', 'Zoom Video Communications', 'High-Definition Video Conferencing & Team Webinars'),
        ('Slack Pro', r'(?i)\b(slack)\b', 'Salesforce (Slack)', 'Real-Time Team Communication, Channels & Integrations'),
        ('Trello Premium', r'(?i)\b(trello)\b', 'Atlassian (Trello)', 'Kanban Board Project Management & Team Workflows'),
        ('ClickUp Unlimited / Business', r'(?i)\b(clickup)\b', 'ClickUp Inc.', 'All-in-One Task, Doc, Goal & Project Management'),
        ('Monday.com', r'(?i)\b(monday\.com|monday)\b', 'Monday.com Ltd.', 'Work OS for Workflow Tracking & Team Collaboration'),
        ('iLovePDF Premium', r'(?i)\b(ilovepdf|i love pdf)\b', 'iLovePDF', 'PDF Merge, Compress, Split, Sign & Optical Character Conversion'),
        ('Smallpdf Pro', r'(?i)\b(smallpdf)\b', 'Smallpdf GmbH', 'Cloud PDF Editing, Compression & Format Converter'),
        ('CamScanner Premium', r'(?i)\b(camscanner)\b', 'INTSIG Information Co.', 'Mobile Document Scanner, HD OCR & PDF Export'),
        ('Lucidchart Pro', r'(?i)\b(lucidchart)\b', 'Lucid Software Inc.', 'Intelligent Cloud Diagramming & Flowchart Visualization'),
        ('Mural Enterprise', r'(?i)\b(mural)\b', 'Mural', 'Collaborative Digital Whiteboard for Creative Ideation'),
        ('Miro Team', r'(?i)\b(miro)\b', 'Miro (RealtimeBoard)', 'Visual Workspace for Innovation, Brainstorming & Mapping'),
        ('Loom Business', r'(?i)\b(loom)\b', 'Atlassian (Loom)', 'Async Video Messaging & Instant Screen Recording'),
        ('Otter.ai Pro', r'(?i)\b(otter|otter\.ai)\b', 'Otter.ai Inc.', 'AI Meeting Transcription & Automated Action Items'),
        ('Readwise & Reader', r'(?i)\b(readwise)\b', 'Readwise Inc.', 'E-Book Highlight Syncing, Spaced Repetition & Read-Later'),

        # 9. Education, Learning & Self-Improvement
        ('Duolingo Super / Max', r'(?i)\b(duolingo|doulingo)\b', 'Duolingo, Inc.', 'Gamified Foreign Language Learning with AI Roleplay'),
        ('Coursera Plus', r'(?i)\b(coursera)\b', 'Coursera, Inc.', 'Accredited University Degrees, Certificates & 7,000+ Courses'),
        ('Skillshare Premium', r'(?i)\b(skillshare)\b', 'Skillshare, Inc.', 'Creative Video Classes for Design, Video, Art & Freelancing'),
        ('Quizlet Plus', r'(?i)\b(quizlet)\b', 'Quizlet, Inc.', 'Digital Flashcards, Practice Tests & AI Study Guides'),
        ('Scribd / Everand Premium', r'(?i)\b(scribd|everand)\b', 'Scribd, Inc.', 'Unlimited Digital Library of Books, Audiobooks & Documents'),
        ('Chegg Study Pack', r'(?i)\b(chegg)\b', 'Chegg, Inc.', 'Textbook Step-by-Step Solutions & 24/7 Expert Q&A'),
        ('Udemy Personal Plan', r'(?i)\b(udemy)\b', 'Udemy, Inc.', 'On-Demand Technical, Coding & Business Video Courses'),
        ('DataCamp Premium', r'(?i)\b(datacamp)\b', 'DataCamp, Inc.', 'Interactive Python, SQL, R & Data Science Learning'),
        ('Codecademy Pro', r'(?i)\b(codecademy)\b', 'Skillsoft (Codecademy)', 'Interactive Hands-on Web Development & Coding Lessons'),
        ('MasterClass All-Access', r'(?i)\b(masterclass)\b', 'Yanka Industries', 'Cinematic Lessons Taught by World Icons & Celebrities'),
        ('Brilliant.org Premium', r'(?i)\b(brilliant)\b', 'Brilliant Worldwide', 'Interactive STEM, Logic, Math & Computer Science Puzzles'),
        ('ELSA Speak Pro / Premium', r'(?i)\b(elsa speak|elsa)\b', 'ELSA Corp.', 'AI English Pronunciation & Accent Reduction Coach'),
        ('Babbel Lifetime / 1-Year', r'(?i)\b(babbel)\b', 'Lesson Nine GmbH (Babbel)', 'Conversational Language Learning Backed by Linguists'),
        ('Busuu Premium Plus', r'(?i)\b(busuu)\b', 'Chegg (Busuu)', 'Structured Language Learning with Native Speaker Community Feedback'),
        ('StuDocu Premium', r'(?i)\b(studocu)\b', 'StuDocu B.V.', 'University Lecture Summaries, Study Notes & Exam Prep'),
        ('Course Hero Premier', r'(?i)\b(coursehero|course hero)\b', 'Course Hero, Inc.', 'Crowdsourced Course Notes, Study Guides & Homework Q&A'),
        ('Kahoot! Premium', r'(?i)\b(kahoot)\b', 'Kahoot! Group', 'Game-Based Learning & Live Interactive Quizzes'),
        ('Memrise Pro', r'(?i)\b(memrise)\b', 'Memrise Inc.', 'Spaced Repetition Flashcards & Real Native Video Clips'),
        ('Headspace Mindfulness', r'(?i)\b(headspace|head space)\b', 'Headspace Health', 'Guided Meditation, Mindfulness & Sleep Soundscapes'),
        ('Waking Up (Sam Harris)', r'(?i)\b(waking up)\b', 'Waking Up LLC', 'Philosophy, Theory & Practice of Mindful Meditation'),
        ('Lenny PM & Product Toolkit', r'(?i)\b(lenny)\b', 'Lenny Rachitsky', 'Silicon Valley Product Management Frameworks & Resources'),
        ('Kiro AI Education', r'(?i)\b(kiro)\b', 'Kiro AI', 'AI Personalized Tutoring & Academic Course Assistant'),

        # 10. VPN, Privacy & Cybersecurity
        ('ExpressVPN', r'(?i)\b(expressvpn|express vpn)\b', 'Kape Technologies', 'Ultra-Fast Encrypted VPN & Private DNS Network'),
        ('NordVPN', r'(?i)\b(nordvpn|nord vpn)\b', 'Nord Security', 'Double Encryption VPN, Threat Protection & Dedicated IPs'),
        ('Surfshark VPN', r'(?i)\b(surfshark)\b', 'Nord Security (Surfshark)', 'Unlimited Device VPN, CleanWeb Ad Blocker & Antivirus'),
        ('Proton VPN & Unlimited', r'(?i)\b(proton|protonvpn)\b', 'Proton AG', 'Swiss-Based Zero-Logs VPN & Encrypted Mail Ecosystem'),
        ('HMA VPN (HideMyAss)', r'(?i)\b(hma|hide my ass|hidemyass)\b', 'Gen Digital (Avast)', 'Global Server Network VPN with IP Shuffling'),
        ('PureVPN', r'(?i)\b(purevpn)\b', 'Gaditek', 'High-Speed No-Log VPN with Dedicated P2P Servers'),
        ('CyberGhost VPN', r'(?i)\b(cyberghost)\b', 'Kape Technologies', 'Streaming & Torrenting Optimized VPN Network'),
        ('IPVanish VPN', r'(?i)\b(ipvanish)\b', 'Ziff Davis', 'Fast Anonymous VPN with SOCKS5 Proxy Support'),
        ('Hotspot Shield VPN', r'(?i)\b(hotspot shield)\b', 'Aura (Pango)', 'Hydra Protocol High-Speed Gaming & Streaming VPN'),
        ('Private Internet Access (PIA)', r'(?i)\b(pia vpn)\b', 'Kape Technologies', 'Proven No-Logs Open-Source VPN Architecture'),
        ('AdGuard Premium', r'(?i)\b(adguard)\b', 'AdGuard Software Ltd.', 'System-Wide Ad, Tracker & Malware Blocking Solution'),
        ('Avira Prime / Antivirus', r'(?i)\b(avira)\b', 'Gen Digital (Avira)', 'All-in-One Antivirus, System Cleanup & Privacy VPN'),
        ('Kaspersky Total Security', r'(?i)\b(kaspersky)\b', 'Kaspersky Lab', 'Advanced Anti-Malware, Ransomware & Firewall Defense'),
        ('McAfee Total Protection', r'(?i)\b(mcafee)\b', 'McAfee, LLC', 'Identity Monitoring, Web Protection & Antivirus'),
        ('Malwarebytes Premium', r'(?i)\b(malwarebytes)\b', 'Malwarebytes Inc.', 'Real-Time Threat Detection & Zero-Day Exploit Shield'),
        ('Norton VPN / Security', r'(?i)\b(norton)\b', 'Gen Digital (Norton)', 'Bank-Grade WiFi Encryption & Device Security'),

        # 11. Streaming, Entertainment & Cloud Storage
        ('Spotify Premium', r'(?i)\b(spotify)\b', 'Spotify AB', 'Ad-Free On-Demand Music Streaming & 320kbps Audio'),
        ('Apple Music', r'(?i)\b(apple music)\b', 'Apple Inc.', 'Lossless & Spatial Audio Music Streaming (100M+ Songs)'),
        ('Apple iCloud+ Storage', r'(?i)\b(icloud)\b', 'Apple Inc.', 'Secure Cloud Storage, Private Relay & Hide My Email'),
        ('Apple TV+', r'(?i)\b(apple tv)\b', 'Apple Inc.', 'Award-Winning Original Dramas, Comedies & Movies'),
        ('YouTube Premium', r'(?i)\b(youtube|yt premium|ytb premium)\b', 'Google LLC', 'Ad-Free Background Video Playback & YouTube Music'),
        ('Netflix Premium 4K UHD', r'(?i)\b(netflix)\b', 'Netflix, Inc.', '4K HDR Streaming, Spatial Audio & Exclusive Originals'),
        ('Amazon Prime Video', r'(?i)\b(prime video|amazon prime)\b', 'Amazon.com, Inc.', 'Original Series, Hollywood Blockbusters & Prime Benefits'),
        ('Disney+ Hotstar / Premium', r'(?i)\b(disney|disney\+)\b', 'The Walt Disney Company', 'Disney, Pixar, Marvel, Star Wars & National Geographic'),
        ('Crunchyroll Mega Fan', r'(?i)\b(crunchyroll|ᴄʀᴜɴᴄʜʏʀᴏʟʟ)\b', 'Sony Pictures (Crunchyroll)', 'Simulcast Anime Streaming Library & Offline Downloads'),
        ('Tidal HiFi Plus', r'(?i)\b(tidal)\b', 'Block, Inc. (Tidal)', 'Master Quality Authenticated (MQA) Lossless Audio'),
        ('Deezer Premium', r'(?i)\b(deezer)\b', 'Deezer SA', 'High-Fidelity Audio Streaming & Flow Mood Playlists'),
        ('SoundCloud Go+', r'(?i)\b(soundcloud)\b', 'SoundCloud Global Ltd.', 'Independent Underground Music, DJ Sets & Full Catalog'),
        ('Audible Premium Plus', r'(?i)\b(audible)\b', 'Amazon (Audible)', 'World Largest Spoken-Word Audiobook Library'),
        ('iQIYI VIP', r'(?i)\b(iqiyi)\b', 'Baidu (iQIYI)', 'Leading Asian Dramas, Anime & Variety Shows'),
        ('VieON VIP', r'(?i)\b(vieon)\b', 'DatVietVAC Group', 'Premier Vietnamese Films, Live TV Channels & HBO GO'),
        ('FPT Play VIP', r'(?i)\b(fpt play)\b', 'FPT Telecom', 'Vietnamese TV, European Football & Movie Streaming'),
        ('Galaxy Play VIP', r'(?i)\b(galaxy play)\b', 'Galaxy Media & Entertainment', 'Exclusive Vietnamese Blockbusters & Asian Cinema'),
        ('TV360 VIP', r'(?i)\b(tv360)\b', 'Viettel Telecom', 'Live Sports, V-League & Vietnamese Entertainment TV'),
        ('Youku VIP', r'(?i)\b(youku)\b', 'Alibaba Digital Media', 'Chinese Television Dramas, Reality Shows & Cartoons'),
        ('Max (HBO Max)', r'(?i)\b(hbo|max)\b', 'Warner Bros. Discovery', 'HBO Originals, Warner Bros. Pictures & DC Universe'),
        ('Paramount+', r'(?i)\b(paramount)\b', 'Paramount Global', 'Live Sports, Breaking News & Paramount Originals'),

        # 12. Social, Professional Networks, Gaming & Digital Assets
        ('LinkedIn Premium (Career / Business / Sales Nav)', r'(?i)\b(linkedin)\b', 'Microsoft (LinkedIn)', 'Executive Career InMail, Job Insights & B2B Sales Prospecting'),
        ('Discord Nitro & Profile Enhancements', r'(?i)(discord|decor discord|server boost|gift decor|decor is)', 'Discord Inc.', 'HD Screen Streaming, Custom Emojis & Server Boosts'),
        ('Telegram Premium, Stars & Bot Services', r'(?i)(telegram|tele premium|tele star|star telegram|bot tele|tele bot|tele .*? bot|buff .*? bot|users .*? bot|increase .*? bot)', 'Telegram FZ-LLC', '4GB Uploads, Fast Downloads, Transcriptions & Telegram Stars'),
        ('X Premium (Twitter Blue)', r'(?i)\b(twitter|x premium|x blue|account x stock)\b', 'X Corp.', 'Verified Blue Checkmark, Edit Post, Creator Ad Revenue'),
        ('Facebook Meta Growth & Verified', r'(?i)\b(facebook|fanpage|buff .* facebook|increase .* flow)\b', 'Meta Platforms', 'Facebook Page Verification, Fanpage Authority & Followers'),
        ('TikTok Live & Follower Growth', r'(?i)\b(tiktok|tiktokvn)\b', 'ByteDance', 'TikTok Creator Accounts, Live Studio Activation & Cart'),
        ('Reddit Premium', r'(?i)\b(reddit)\b', 'Reddit Inc.', 'Ad-Free Browsing, Monthly Coins & Custom Avatar Gear'),
        ('Locket Widget Gold', r'(?i)\b(locket)\b', 'Locket Camera, Inc.', 'Live Photos Widget on Home Screen with Friends'),
        ('Steam Wallet & Keys', r'(?i)\b(steam)\b', 'Valve Corporation', 'PC Gaming Store, Community Market & Wallet Credits'),
        ('PlayStation Network (PSN)', r'(?i)\b(playstation|psn)\b', 'Sony Interactive Entertainment', 'PlayStation Store Game Codes & PS Plus Subscriptions'),
        ('Xbox Game Pass Ultimate', r'(?i)\b(xbox|game pass)\b', 'Microsoft Corporation', 'Cloud Gaming & 100+ High-End Console/PC Games'),
        ('Roblox & Virtual Gaming Items', r'(?i)\b(roblox|blox fruits)\b', 'Roblox Corporation', 'Virtual In-Game Assets & Roblox Gaming Tokens'),
        ('Apple App Store & iTunes Gift Cards', r'(?i)\b(apple gift|itunes)\b', 'Apple Inc.', 'Digital Store Credit for iOS Apps, Subscriptions & Music'),

        # 13. Infrastructure, Identity, Emails, Banking & Telecom Verification
        ('SMS OTP & Virtual Number Verification', r'(?i)\b(otp|sms|sim|phone number|virtual number|receive sms)\b', 'Global Telecom Aggregators', 'Temporary & Non-VoIP Phone Numbers for 2FA Verification'),
        ('Aged Webmail Accounts (Hotmail / Gmail / Outlook / Edu)', r'(?i)\b(hotmail|outlook|gmail|mail\.tm|yahoo|mail pass|aged gmail|edu mail|beautiful edu|google mail)\b', 'Microsoft / Google / Educational Institutions', 'Aged Clean Webmail & Student Edu Accounts for Registrations'),
        ('Family Plan Region Limit Resolution', r'(?i)(fix .*?family|family .*?limit)', 'Subscription Infrastructure', 'Bypass Family Group Region Restriction & Account Reset'),
        ('PayPal Verified Reseller Accounts', r'(?i)\b(paypal)\b', 'PayPal Holdings, Inc.', 'Digital Wallet & International Payment Processing Account'),
        ('ByBit Verified Accounts & Crypto Cards', r'(?i)bybit', 'ByBit Fintech Ltd.', 'Cryptocurrency Trading & Crypto Debit Card Infrastructure'),
        ('MB Bank Vietnam Account Vouchers', r'(?i)mb bank', 'Military Commercial Joint Stock Bank (MB)', 'Vietnamese Financial Banking Vouchers'),
        ('Highlands Coffee Discount Vouchers', r'(?i)(coffee highlands|highlands coffee)', 'Highlands Coffee Vietnam', 'Retail Food & Beverage Promotional Vouchers'),
        ('OnlyFans Reseller Balance Accounts', r'(?i)onlyfan', 'Fenix International', 'Subscription Content Creator Platform Accounts'),
        ('Administrative & Test Placeholders', r'(?i)\b(api test|test|contact for bulk|cute cute)\b', 'Reseller Bot Management', 'Internal Testing & Custom Sourcing Inquiries')
    ]

def run_analysis():
    csv_path = 'data/suppliers/reseller_products_master.csv'
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    matched_tools = defaultdict(list)
    unmatched_rows = []

    for r in rows:
        name = r.get('Product Name', '').strip()
        if not name:
            continue
        found = False
        for tool_name, pat, dev, cat in RULES:
            if re.search(pat, name):
                matched_tools[tool_name].append(r)
                found = True
                break
        if not found:
            unmatched_rows.append(r)

    print(f'Total CSV rows processed: {len(rows)}')
    print(f'Total Canonical Tools / App Families recognized: {len(matched_tools)}')
    matched_count = sum(len(v) for v in matched_tools.values())
    print(f'Total matched rows: {matched_count} ({matched_count/len(rows)*100:.2f}%)')
    print(f'Total unmatched rows: {len(unmatched_rows)}')

    if unmatched_rows:
        unmatched_names = sorted(set(r['Product Name'].strip() for r in unmatched_rows))
        print(f'Remaining distinct unmatched product names ({len(unmatched_names)}):')
        for n in unmatched_names:
            print('  *', n)

if __name__ == '__main__':
    run_analysis()
