const DEFAULT_WA_NUMBER = '923236715731';
const LEGACY_WA_NUMBER = ['923', '476', '242709'].join('');

const products = [
  {id:'chatgpt',name:'ChatGPT Plus',category:'AI Assistants',description:'Advanced writing, research, coding, image and creative assistance in one workspace.',price:2300,oldPrice:3000,usdPrice:'8.99',oldUsdPrice:'11.99',duration:'1 Month',access:'Private',delivery:'After payment confirmation',warranty:'7 Days',rating:4.9,badge:'Best Seller',bestFor:['Writing','Coding','Study'],logo:'assets/product-logos/chatgpt.png',features:['Advanced AI models','Image generation','File analysis','Voice conversations'],intent:['writing','research','study','code','coding','content'],officialUrl:'https://chatgpt.com'},
  {id:'gemini',name:'Gemini Pro',category:'AI Assistants',description:'Google’s multimodal AI for research, documents, code and everyday workflows.',price:800,oldPrice:1500,usdPrice:'3.99',oldUsdPrice:'5.99',duration:'18 Months',access:'Invitation',delivery:'After payment confirmation',warranty:'30 Days',rating:4.8,badge:'Best Value',bestFor:['Research','Study','Google'],logo:'assets/product-logos/gemini.png',features:['Long-context document analysis','Google service integrations','Multimodal reasoning','Research assistance'],intent:['writing','research','study','content'],officialUrl:'https://gemini.google.com'},
  {id:'veo',name:'Veo 3 Ultra',category:'AI Video',description:'Generate cinematic AI video with realistic motion and audio-capable workflows.',price:2100,oldPrice:3000,usdPrice:'8.49',oldUsdPrice:'11.99',duration:'Unlimited',access:'Shared',delivery:'After payment confirmation',warranty:'7 Days',rating:4.9,badge:'Trending',bestFor:['Video','Ads','Creators'],logo:'assets/product-logos/veo.png',features:['Text-to-video workflow','Audio-capable generation','Consistent motion tools','Plan allowance confirmed before payment'],intent:['video','videos','creator'],officialUrl:'https://deepmind.google/technologies/veo/'},
  {id:'leonardo',name:'Leonardo AI Essential',category:'Design',description:'Create production-ready digital art, marketing visuals, assets and concepts.',price:1900,oldPrice:2600,usdPrice:'7.49',oldUsdPrice:'10.49',duration:'8,500 Credits',access:'Private',delivery:'After payment confirmation',warranty:'7 Days',rating:4.7,badge:'For Creators',bestFor:['Images','Assets','Concepts'],logo:'assets/product-logos/leonardo.png',features:['PhotoReal & Alchemy pipeline','Realtime canvas','Prompt enhancer','Commercial license'],intent:['image','images','design','creator'],officialUrl:'https://leonardo.ai'},
  {id:'elevenlabs',name:'ElevenLabs',category:'AI Voice',description:'Realistic AI speech, dubbing and permitted voice-cloning workflows for media.',price:3300,oldPrice:4200,usdPrice:'12.99',oldUsdPrice:'16.99',duration:'1 Month',access:'Private',delivery:'After payment confirmation',warranty:'7 Days',rating:4.8,badge:'Premium',bestFor:['Voice','Dubbing','Audio'],logo:'assets/product-logos/elevenlabs.png',features:['Monthly voice credit allowance','Voice library tools','Multilingual speech','API access subject to plan'],intent:['voice','audio','video','creator'],officialUrl:'https://elevenlabs.io'},
  {id:'canva',name:'Canva Pro Edu',category:'Design',description:'Design social media posts, pitch decks, presentations and branded assets.',price:900,oldPrice:1800,usdPrice:'3.99',oldUsdPrice:'6.99',duration:'1 Year',access:'Invitation',delivery:'After payment confirmation',warranty:'30 Days',rating:4.9,badge:'Best Seller',bestFor:['Design','Social','Students'],logo:'assets/product-logos/canva.png',features:['Premium templates and assets','Background-removal tools','Magic Studio AI tools','Brand management features'],intent:['image','images','design','presentation','study','creator','social'],officialUrl:'https://www.canva.com'},
  {id:'figma',name:'Figma Pro Private',category:'Design',description:'Professional interface design, prototyping and design system workspace.',price:3000,oldPrice:4800,usdPrice:'11.99',oldUsdPrice:'18.99',duration:'2 Years',access:'Private',delivery:'After payment confirmation',warranty:'30 Days',rating:4.8,badge:'Long Term',bestFor:['UI/UX','Teams','Web'],logo:'assets/product-logos/figma.png',features:['Unlimited files & version history','Dev Mode inspection','Shared design libraries','Full prototype viewer'],intent:['design','code','coding','business'],officialUrl:'https://www.figma.com'},
  {id:'capcut',name:'CapCut Pro',category:'AI Video',description:'Fast, intuitive editing suite for viral TikToks, Instagram Reels, and YouTube Shorts.',price:900,oldPrice:1400,usdPrice:'3.99',oldUsdPrice:'5.99',duration:'1 Month',access:'Private',delivery:'After payment confirmation',warranty:'7 Days',rating:4.7,badge:'Popular',bestFor:['Reels','Shorts','Editing'],logo:'assets/product-logos/capcut.png',features:['Pro video transitions & filters','Auto captions generator','AI background remover','Cloud draft sync'],intent:['video','videos','creator','social'],officialUrl:'https://www.capcut.com'},
  {id:'adobe',name:'Adobe Creative Cloud',category:'Design',description:'Complete suite of Photoshop, Illustrator, Premiere Pro, After Effects and Firefly.',price:1700,oldPrice:2600,usdPrice:'6.99',oldUsdPrice:'10.49',duration:'2 Months',access:'Private',delivery:'After payment confirmation',warranty:'7 Days',rating:4.8,badge:'Pro Choice',bestFor:['Creative','Photo','Video'],logo:'assets/product-logos/adobe.png',features:['20+ desktop & web apps','Firefly generative credits','100GB Adobe Cloud storage','Adobe Fonts access'],intent:['image','images','design','video','creator'],officialUrl:'https://www.adobe.com'},
  {id:'lovable',name:'Lovable Pro',category:'Development',description:'Build, design and ship full-stack web applications and MVPs with natural language.',price:1600,oldPrice:2200,usdPrice:'6.49',oldUsdPrice:'8.99',duration:'1 Month',access:'Private',delivery:'After payment confirmation',warranty:'7 Days',rating:4.6,badge:'For Builders',bestFor:['Apps','Web','MVPs'],logo:'assets/product-logos/lovable.png',features:['AI full-stack code generator','Direct GitHub integration','Custom domains & deploy','Fast iterative edits'],intent:['code','coding','business','automation'],officialUrl:'https://lovable.dev'},
  {id:'gamma',name:'Gamma Pro',category:'Productivity',description:'Turn raw ideas, briefs and outlines into interactive presentations, decks and docs.',price:23000,oldPrice:28000,usdPrice:'89.99',oldUsdPrice:'109.99',duration:'1 Year',access:'Private',delivery:'After payment confirmation',warranty:'30 Days',rating:4.6,badge:'Annual',bestFor:['Slides','Pitching','Docs'],logo:'assets/product-logos/gamma.png',features:['Unlimited AI generation','Custom fonts & themes','Analytics & tracking','Export to PDF/PowerPoint'],intent:['presentation','content','business','study'],officialUrl:'https://gamma.app'},
  {id:'replit',name:'Replit Core',category:'Development',description:'Code, collaborate, host and scale web applications with autonomous AI agents.',price:3200,oldPrice:4200,usdPrice:'12.49',oldUsdPrice:'16.49',duration:'$40 Credits',access:'Private',delivery:'After payment confirmation',warranty:'7 Days',rating:4.7,badge:'Developer Pick',bestFor:['Coding','Apps','Deploy'],logo:'assets/product-logos/replit.png',features:['Autonomous AI code agent','Instant cloud environments','Serverless hosting','$40 included usage credits'],intent:['code','coding','automation'],officialUrl:'https://replit.com'},
  {id:'n8n',name:'n8n Starter',category:'Development',description:'Self-hosted or cloud visual workflow automation for AI agents, APIs and business logic.',price:7000,oldPrice:9000,usdPrice:'26.99',oldUsdPrice:'34.99',duration:'1 Year',access:'Private',delivery:'After payment confirmation',warranty:'30 Days',rating:4.7,badge:'Automation',bestFor:['Workflow','Agents','Teams'],logo:'assets/product-logos/n8n.png',features:['Visual drag-and-drop builder','400+ native app integrations','LangChain AI nodes','Custom JavaScript execution'],intent:['code','coding','automation','business'],officialUrl:'https://n8n.io'},
  {id:'notion',name:'Notion Business',category:'Productivity',description:'All-in-one connected workspace for team knowledge, project boards, and AI summaries.',price:2200,oldPrice:3000,usdPrice:'8.99',oldUsdPrice:'11.99',duration:'3 Months',access:'Invitation',delivery:'After payment confirmation',warranty:'30 Days',rating:4.8,badge:'Team Pick',bestFor:['Docs','Projects','Teams'],logo:'assets/product-logos/notion.png',features:['Unlimited team blocks','Integrated Notion AI assistant','Advanced team permissions','Custom database views'],intent:['writing','content','business','study'],officialUrl:'https://www.notion.so'},
  {id:'nordvpn',name:'NordVPN',category:'VPN & Security',description:'Military-grade encrypted browsing, high-speed servers, and threat protection.',price:1800,oldPrice:2400,usdPrice:'6.99',oldUsdPrice:'9.49',duration:'3 Months',access:'Private',delivery:'After payment confirmation',warranty:'7 Days',rating:4.7,badge:'Secure',bestFor:['Privacy','Travel','Streaming'],logo:'assets/product-logos/nordvpn.png',features:['Ultra-fast 10Gbps servers','Threat protection & ad blocker','6 simultaneous connections','Strict zero-logs policy'],intent:['vpn','security','privacy'],officialUrl:'https://nordvpn.com'},
  {id:'surfshark',name:'Surfshark VPN',category:'VPN & Security',description:'Reliable everyday privacy, geo-unblocking, and unlimited device connections.',price:800,oldPrice:1200,usdPrice:'3.49',oldUsdPrice:'4.99',duration:'2 Months',access:'Shared',delivery:'After payment confirmation',warranty:'7 Days',rating:4.6,badge:'Best Value',bestFor:['Privacy','Devices','Travel'],logo:'assets/product-logos/surfshark.png',features:['Unlimited device support','CleanWeb ad & tracker blocker','Global server locations','Bypasser split tunneling'],intent:['vpn','security','privacy'],officialUrl:'https://surfshark.com'},
  {id:'youtube',name:'YouTube Premium',category:'Entertainment',description:'Ad-free videos, background play on mobile, offline downloads, and YouTube Music.',price:1200,oldPrice:1700,usdPrice:'4.99',oldUsdPrice:'6.99',duration:'3 Months',access:'Invitation',delivery:'After payment confirmation',warranty:'30 Days',rating:4.8,badge:'Popular',bestFor:['Music','Video','Mobile'],logo:'assets/product-logos/youtube.png',features:['Zero video ads','Background & picture-in-picture','Offline smart downloads','Full YouTube Music access'],intent:['entertainment','video','music'],officialUrl:'https://www.youtube.com/premium'},
  {id:'netflix',name:'Netflix Premium 4K',category:'Entertainment',description:'Stream global movies and series in crisp 4K Ultra HD with spatial audio.',price:400,oldPrice:650,usdPrice:'1.99',oldUsdPrice:'2.99',duration:'1 Month',access:'Shared',delivery:'After payment confirmation',warranty:'7 Days',rating:4.5,badge:'Quick Delivery',bestFor:['Movies','Series','4K'],logo:'assets/product-logos/netflix.png',features:['4K Ultra HD & HDR resolution','Spatial audio support','Smart TV & laptop compatibility','Dedicated profile access'],intent:['entertainment','video','movies'],officialUrl:'https://www.netflix.com'},
  {id:'linkedin',name:'LinkedIn Premium',category:'Business',description:'Career insights, applicant tools and professional learning features.',price:1500,oldPrice:2400,usdPrice:'5.99',oldUsdPrice:'9.49',duration:'2 Months',access:'Invitation',delivery:'After payment confirmation',warranty:'7 Days',rating:4.6,badge:'Career',bestFor:['Jobs','Learning','Sales'],logo:'assets/product-logos/linkedin.png',features:['InMail allowance subject to tier','Profile-viewer insights','Applicant comparison tools','LinkedIn Learning access'],intent:['business','jobs','study'],officialUrl:'https://www.linkedin.com/premium'},
  {id:'windows',name:'Windows 11 Pro Key',category:'Software',description:'Digital license key for Windows 11 Pro activation, subject to confirmed terms.',price:1900,oldPrice:2800,usdPrice:'7.99',oldUsdPrice:'10.99',duration:'Lifetime',access:'License Key',delivery:'After payment confirmation',warranty:'7 Days',rating:4.7,badge:'License Key',bestFor:['PC','Work','Security'],logo:'assets/product-logos/windows.png',features:['Digital retail activation key','BitLocker drive encryption','Remote Desktop Host','Online activation instructions'],intent:['software','windows','business'],officialUrl:'https://www.microsoft.com/windows'},
  {id:'claude',name:'Claude Pro (3.5 Sonnet)',category:'AI Assistants',description:'Anthropic’s flagship AI for coding, deep analysis, technical writing, and live Artifacts rendering.',price:2200,oldPrice:3000,usdPrice:'8.99',oldUsdPrice:'11.99',duration:'1 Month',access:'Private',delivery:'After payment confirmation',warranty:'7 Days',rating:4.9,badge:'Best Seller',bestFor:['Coding','Artifacts','Logic'],logo:'assets/product-logos/claude.png',features:['Claude 3.5 Sonnet & Opus models','Interactive Artifacts visualizer','200K token deep context','Private access on your personal email'],intent:['claude','coding','code','writing','artifacts'],officialUrl:'https://claude.ai'},
  {id:'midjourney',name:'Midjourney v6.1 Pro',category:'Design',description:'Industry-standard ultra-photorealistic AI image and art generation via Discord and Web portal.',price:2400,oldPrice:3500,usdPrice:'9.99',oldUsdPrice:'13.99',duration:'1 Month',access:'Private / Discord',delivery:'After payment confirmation',warranty:'7 Days',rating:4.9,badge:'Trending',bestFor:['Photorealism','Art','Creatives'],logo:'assets/product-logos/midjourney.png',features:['Ultra-high resolution outputs','Fast GPU generation hours','Commercial reproduction rights','Web generator and Discord bot'],intent:['midjourney','images','art','design','photorealism'],officialUrl:'https://www.midjourney.com'},
  {id:'cursor',name:'Cursor AI Pro',category:'Development',description:'The AI-first code editor built on VS Code with multi-file Composer, Claude 3.5 Sonnet & GPT-4o.',price:2800,oldPrice:3800,usdPrice:'10.99',oldUsdPrice:'14.99',duration:'1 Month',access:'Private',delivery:'After payment confirmation',warranty:'7 Days',rating:4.9,badge:'Developer Pick',bestFor:['Coding','Engineers','Fullstack'],logo:'assets/product-logos/cursor.png',features:['Composer multi-file AI editing','Unlimited fast tab completions','Claude 3.5 Sonnet & GPT-4o inside IDE','Private code indexing'],intent:['cursor','code','coding','editor','developer'],officialUrl:'https://www.cursor.com'},
  {id:'perplexity',name:'Perplexity Pro',category:'AI Assistants',description:'Real-time AI research engine with direct source citations, PDF deep search, and multi-model access.',price:1400,oldPrice:2200,usdPrice:'5.49',oldUsdPrice:'8.49',duration:'1 Month',access:'Private',delivery:'After payment confirmation',warranty:'7 Days',rating:4.8,badge:'Top Research',bestFor:['Research','Students','Fact-Checking'],logo:'assets/product-logos/perplexity.png',features:['Pro Search with cited links','Unlimited file & document uploads','Switch Claude 3.5, GPT-4o & Sonar','Included monthly API credits'],intent:['perplexity','research','study','search'],officialUrl:'https://www.perplexity.ai'},
  {id:'deepseek',name:'DeepSeek Unlimited',category:'AI Assistants',description:'Cutting-edge DeepSeek R1 & V3 reasoning engine with chain-of-thought logic and instant math solving.',price:1100,oldPrice:1800,usdPrice:'4.49',oldUsdPrice:'6.99',duration:'1 Month',access:'Private Portal',delivery:'After payment confirmation',warranty:'7 Days',rating:4.8,badge:'Viral AI',bestFor:['Math','Logic','Reasoning'],logo:'assets/product-logos/deepseek.png',features:['DeepSeek R1 full reasoning chain','Mathematical proof & coding engine','Zero queue peak-hour access','Fast web & mobile access'],intent:['deepseek','reasoning','math','code'],officialUrl:'https://chat.deepseek.com'},
  {id:'grok',name:'SuperGrok / Grok 2',category:'AI Assistants',description:'X Premium Grok 2 with real-time Twitter/X intelligence and uncensored Flux image generation.',price:1800,oldPrice:2600,usdPrice:'6.99',oldUsdPrice:'9.99',duration:'1 Month',access:'Private',delivery:'After payment confirmation',warranty:'7 Days',rating:4.7,badge:'X Premium',bestFor:['Realtime X','Flux Art','News'],logo:'assets/product-logos/grok.png',features:['Real-time news search on X','Flux-powered photorealistic images','Creative & uncensored mode','Direct X web access'],intent:['grok','supergrok','twitter','news'],officialUrl:'https://x.ai'},
  {id:'runway',name:'Runway ML Gen-3 Pro',category:'AI Video',description:'Hollywood-grade cinematic video generator with Gen-3 Alpha, Motion Brush, and multi-camera directing.',price:3500,oldPrice:4800,usdPrice:'13.99',oldUsdPrice:'18.99',duration:'1 Month',access:'Private',delivery:'After payment confirmation',warranty:'7 Days',rating:4.8,badge:'Hollywood AI',bestFor:['VFX','Cinematics','Video Ads'],logo:'assets/product-logos/runway.png',features:['Gen-3 Alpha photorealistic video','Motion brush camera pathing','4K output upscaler','Commercial video license'],intent:['runway','video','vfx','animation'],officialUrl:'https://runwayml.com'},
  {id:'heygen',name:'HeyGen AI Avatar Pro',category:'AI Video',description:'AI video creation platform with hyper-realistic human avatars, lip-syncing, and multi-language voiceovers.',price:4200,oldPrice:5800,usdPrice:'16.99',oldUsdPrice:'22.99',duration:'1 Month',access:'Private',delivery:'After payment confirmation',warranty:'7 Days',rating:4.8,badge:'Video Avatars',bestFor:['Marketing','TikTok Ads','Spokesperson'],logo:'assets/product-logos/heygen.png',features:['Studio-quality human avatars','Automatic 40+ language voice dubbing','Instant script-to-video generator','Custom personal avatar cloning'],intent:['heygen','avatar','video','marketing'],officialUrl:'https://www.heygen.com'},
  {id:'grammarly',name:'Grammarly Premium',category:'Writing & SEO',description:'AI writing assistant for error-free essays, grammar correction, vocabulary enhancement, and tone refinement.',price:750,oldPrice:1200,usdPrice:'2.99',oldUsdPrice:'4.99',duration:'1 Month',access:'Private / Shared',delivery:'After payment confirmation',warranty:'7 Days',rating:4.8,badge:'Student Pick',bestFor:['Essays','Grammar','Proposals'],logo:'assets/product-logos/grammarly.png',features:['Full sentence rewrites & tone tuner','Built-in plagiarism detector','Browser extension & MS Word plugin','Vocabulary & clarity enhancement'],intent:['grammarly','writing','grammar','student','plagiarism'],officialUrl:'https://www.grammarly.com'},
  {id:'quillbot',name:'QuillBot Premium',category:'Writing & SEO',description:'Fast AI paraphraser, summarizer, citation generator, and grammar checker for academic writing.',price:450,oldPrice:800,usdPrice:'1.99',oldUsdPrice:'3.49',duration:'1 Month',access:'Private / Shared',delivery:'After payment confirmation',warranty:'7 Days',rating:4.8,badge:'Lowest Price',bestFor:['Paraphrasing','Students','Assignments'],logo:'assets/product-logos/quillbot.png',features:['Unlimited words in Paraphraser','All 8 custom paraphrasing modes','Freeze words terminology protection','Grammar & citation creator'],intent:['quillbot','paraphrase','writing','assignment'],officialUrl:'https://quillbot.com'},
  {id:'semrush',name:'SEMrush Pro',category:'Writing & SEO',description:'All-in-one SEO and digital marketing suite for keyword research, competitor analysis, and site audit.',price:1500,oldPrice:2500,usdPrice:'5.99',oldUsdPrice:'9.99',duration:'1 Month',access:'Shared',delivery:'After payment confirmation',warranty:'7 Days',rating:4.7,badge:'SEO Suite',bestFor:['SEO','Keywords','Agencies'],logo:'assets/product-logos/semrush.png',features:['Keyword Magic tool with PKR metrics','Competitor organic search audit','Backlink analytics & link gaps','On-page SEO checker'],intent:['semrush','seo','keywords','backlinks','ranking'],officialUrl:'https://www.semrush.com'},
  {id:'allinone',name:'All-in-One Mega AI Portal',category:'AI Assistants',description:'Unified AI workspace combining Claude 3.5 Sonnet, GPT-4o, Gemini 1.5 Pro, Perplexity Pro & DeepSeek in 1 login.',price:1999,oldPrice:4500,usdPrice:'7.99',oldUsdPrice:'15.99',duration:'1 Month',access:'Private Portal (LibreChat)',delivery:'After payment confirmation',warranty:'30 Days',rating:4.98,badge:'Best Value Deal',bestFor:['All Models','Full Power','Cost Saver'],logo:'assets/product-logos/allinone.png',features:['Claude 3.5 + GPT-4o + Gemini 1.5 + Perplexity in 1 portal','Single simple login on PC & Mobile','Zero VPN needed in Pakistan','Delivery after payment confirmation on WhatsApp'],intent:['allinone','portal','mega','claude','chatgpt','gemini','perplexity','deepseek'],officialUrl:'https://aitoolgems.tech/deals/'},
  {id:'tradingview',name:'TradingView Pro',category:'Business',description:'Institutional-grade technical charting, custom Pine Script indicators, and real-time alerts.',price:3500,oldPrice:5000,usdPrice:'14.99',oldUsdPrice:'19.99',duration:'1 Month',access:'Private',delivery:'After payment confirmation',warranty:'30 Days',rating:4.9,badge:'Pro Trader',bestFor:['Charts','Crypto','Stocks'],logo:'assets/product-logos/tradingview.png',features:['5 indicators per chart','Bar Replay backtesting','Volume Profile analysis','Server-side price alerts'],intent:['tradingview','trading','crypto','stocks','forex','finance'],officialUrl:'https://www.tradingview.com'},
  {id:'kling',name:'Kling AI',category:'AI Video',description:'Hollywood-grade physics simulation, cinematic camera motion, and hyper-realistic AI video generation.',price:4800,oldPrice:6500,usdPrice:'19.99',oldUsdPrice:'25.99',duration:'1 Month',access:'Private',delivery:'After payment confirmation',warranty:'30 Days',rating:4.9,badge:'Ultra Realistic',bestFor:['Cinematic','Motion','VFX'],logo:'assets/product-logos/kling.png',features:['1080p Full HD video generation','Advanced 3D camera controls','Physics-accurate simulation','No watermark & commercial use'],intent:['kling','video','ai video','cinematic','animation','vfx'],officialUrl:'https://klingai.com'},
  {id:'freepik',name:'Freepik Premium',category:'Design',description:'Millions of premium vector illustrations, high-res stock photos, PSD mockups, and AI Pikaso.',price:2400,oldPrice:3500,usdPrice:'9.99',oldUsdPrice:'13.99',duration:'1 Month',access:'Private',delivery:'After payment confirmation',warranty:'30 Days',rating:4.8,badge:'Graphic Essential',bestFor:['Vectors','PSD','Mockups'],logo:'assets/product-logos/freepik.png',features:['100 daily premium downloads','Full commercial license & no attribution','Freepik Pikaso AI generator','Layered Photoshop PSD templates'],intent:['freepik','vectors','design','psd','mockup','stock','photos'],officialUrl:'https://www.freepik.com'},
  {id:'spotify',name:'Spotify Premium',category:'Entertainment',description:'Ad-free music and podcasts, offline downloads, unlimited skips, and 320kbps extreme audio quality.',price:1200,oldPrice:1800,usdPrice:'4.99',oldUsdPrice:'7.49',duration:'3 Months',access:'Private',delivery:'After payment confirmation',warranty:'30 Days',rating:4.9,badge:'Ad-Free Audio',bestFor:['Music','Podcasts','Offline'],logo:'assets/product-logos/spotify.png',features:['100% ad-free streaming','Download up to 10,000 songs offline','Ultra-high 320kbps bitrate','Activate on your personal account'],intent:['spotify','music','songs','audio','streaming','podcast'],officialUrl:'https://spotify.com'},
  {id:'copilot',name:'GitHub Copilot',category:'Development',description:'AI pair programmer for VS Code and JetBrains with real-time autocompletion and Copilot Chat.',price:2500,oldPrice:3800,usdPrice:'9.99',oldUsdPrice:'14.99',duration:'1 Month',access:'Private',delivery:'After payment confirmation',warranty:'30 Days',rating:4.9,badge:'Developer Pick',bestFor:['VS Code','Autocomplete','Fullstack'],logo:'assets/product-logos/copilot.png',features:['Real-time code completions','GitHub Copilot Chat inside IDE','Unit test generation & bug fixes','Private personal GitHub activation'],intent:['copilot','github','code','coding','developer','vscode','python'],officialUrl:'https://github.com/features/copilot'},
  {id:'suno',name:'Suno AI',category:'AI Voice',description:'Generate studio-grade full vocal songs, catchy commercial jingles, and instrumental beats from text.',price:3200,oldPrice:4500,usdPrice:'12.99',oldUsdPrice:'17.99',duration:'1 Month',access:'Private',delivery:'After payment confirmation',warranty:'30 Days',rating:4.8,badge:'AI Music Hits',bestFor:['Songwriting','Vocals','Beats'],logo:'assets/product-logos/suno.png',features:['Full vocal songs in seconds','2,500 monthly generation credits','Commercial monetization rights','Custom lyrics & song continuation'],intent:['suno','music','audio','songs','voice','beats','creator'],officialUrl:'https://suno.com'},
  {id:'turnitin',name:'Turnitin Student Account',category:'Writing & SEO',description:'Non-repository academic similarity check and AI writing detection report for thesis and research.',price:3600,oldPrice:5000,usdPrice:'13.99',oldUsdPrice:'18.99',duration:'1 Month',access:'Private',delivery:'After payment confirmation',warranty:'30 Days',rating:4.9,badge:'Academic Pick',bestFor:['Thesis','Assignments','AI Detection'],logo:'assets/product-logos/turnitin.png',features:['Strict Non-Repository guarantee','Similarity percentage index report','AI writing detection percentage','Downloadable highlighted PDF'],intent:['turnitin','plagiarism','similarity','student','thesis','research','academic'],officialUrl:'https://turnitin.com'},
  {id:'office365',name:'Microsoft Office 365 (1TB)',category:'Productivity',description:'Word, Excel, PowerPoint, Outlook desktop apps on 5 devices simultaneously with 1TB OneDrive cloud.',price:2200,oldPrice:3800,usdPrice:'8.99',oldUsdPrice:'14.99',duration:'1 Year',access:'Private',delivery:'After payment confirmation',warranty:'30 Days',rating:4.9,badge:'1TB Cloud',bestFor:['Word/Excel','OneDrive','5 Devices'],logo:'assets/product-logos/office365.png',features:['Word, Excel & PowerPoint desktop apps','1TB (1,000 GB) secure OneDrive storage','Use on 5 devices simultaneously','Genuine digital retail activation'],intent:['office','office365','microsoft','word','excel','onedrive','cloud','productivity'],officialUrl:'https://www.microsoft.com/microsoft-365'},
          {id:'windsurf',name:'Windsurf Editor',developer:'Exafunction, Inc. (Codeium)',category:'AI Coding & Development',description:'Windsurf Editor is an agentic Integrated Development Environment (IDE) built by Codeium on a modifie...',price:5600,oldPrice:7500,usdPrice:'19.99',oldUsdPrice:'26.99',pricingModel:'Save 25%',officialPricing:'$20 / month (Pro)',billingPeriod:'Monthly / Annual',freePlan:'Free tier with unlimited basic single/multi-line code completions and limited Ca',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://codeium.com/windsurf',documentationUrl:'https://docs.codeium.com/windsurf',badge:'Next-Gen IDE',isExternal:true,bestFor:["Coding", "Cascade", "IDE"],logo:'assets/product-logos/windsurf.svg',features:["Cascade Agentic AI", "Supercomplete Real-Time Engine", "Complete VS Code Compatibility"],intent:["windsurf", "windsurf editor", "windsurf ai price pakistan", "windsurf vs cursor", "codeium cascade editor"],duration:'1 Month',access:'Private',warranty:'7 Days'},
  {id:'v0',name:'v0 by Vercel',developer:'Vercel Inc.',category:'AI Coding & UI Generation',description:'v0 by Vercel revolutionized generative frontend development by combining large language models fine-...',price:5600,oldPrice:7500,usdPrice:'19.99',oldUsdPrice:'26.99',pricingModel:'Save 25%',officialPricing:'$20 / month (Premium)',billingPeriod:'Monthly / Annual',freePlan:'Free plan with 200 monthly credits and community public generation',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://v0.dev',documentationUrl:'https://v0.dev/docs',badge:'Generative UI',isExternal:true,bestFor:["Frontend", "React", "Tailwind"],logo:'assets/product-logos/v0.svg',features:["shadcn/ui & Tailwind Native", "Figma & Screenshot to Code", "Interactive Live Sandbox"],intent:["v0", "v0 by vercel", "v0 dev price pakistan", "v0 ai review", "v0 react generator"],duration:'1 Month',access:'Private',warranty:'7 Days'},
  {id:'bolt-new',name:'Bolt.new',developer:'StackBlitz, Inc.',category:'AI Coding & Fullstack Development',description:'Bolt.new harnesses StackBlitzs groundbreaking WebContainer technology to execute Node.js runtimes d...',price:5600,oldPrice:7500,usdPrice:'19.99',oldUsdPrice:'26.99',pricingModel:'Save 25%',officialPricing:'$20 / month (Pro)',billingPeriod:'Monthly / Annual',freePlan:'Free plan with daily token allowances to create and run full-stack apps in the b',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://bolt.new',documentationUrl:'https://stackblitz.com/docs',badge:'Full-Stack AI',isExternal:true,bestFor:["Fullstack", "Sandboxes", "Prototypes"],logo:'assets/product-logos/bolt-new.svg',features:["In-Browser Node.js Runtime", "Autonomous Multi-File Generation", "Real-Time Error Auto-Correction"],intent:["bolt-new", "bolt.new", "bolt new price pakistan", "bolt.new review", "stackblitz ai editor"],duration:'1 Month',access:'Private',warranty:'7 Days'},
  {id:'manus-ai',name:'Manus AI',developer:'Butterfly Effect Pte. Ltd.',category:'Autonomous AI Agents',description:'Manus AI represents a significant leap from conversational chatbots toward truly autonomous digital ...',price:5600,oldPrice:7800,usdPrice:'19.99',oldUsdPrice:'27.99',pricingModel:'Save 28%',officialPricing:'Waitlist / Early Access',billingPeriod:'Monthly / Annual',freePlan:'Invitation-based free beta preview for selected developers and researchers',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://manus.im',documentationUrl:'https://manus.im',badge:'Autonomous Agent',isExternal:true,bestFor:["Agents", "Research", "Automation"],logo:'assets/product-logos/manus-ai.png',features:["Autonomous Multi-Tool Orchestration", "Virtual Computer Sandbox", "Deep Research & Synthesis"],intent:["manus-ai", "manus ai", "manus ai agent review", "manus ai pakistan access", "autonomous ai agents 2026"],duration:'1 Month',access:'Private',warranty:'7 Days'},
  {id:'qwen',name:'Qwen AI (Tongyi Qianwen)',developer:'Alibaba Cloud',category:'AI Assistants & Open Foundation Models',description:'Qwen (Tongyi Qianwen), developed by Alibaba Cloud, has emerged as one of the worlds most formidable...',price:1500,oldPrice:2500,usdPrice:'4.99',oldUsdPrice:'8.99',pricingModel:'Save 40%',officialPricing:'Free Web Chat / Pay-as-you-go API',billingPeriod:'Monthly / Annual',freePlan:'100% Free web chat with Qwen 2.5 Max, Qwen 2.5 Coder, and Vision models',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://chat.qwenlm.ai',documentationUrl:'https://qwenlm.github.io',badge:'Frontier Model',isExternal:true,bestFor:["Reasoning", "Multilingual", "Coding"],logo:'assets/product-logos/qwen.svg',features:["Qwen 2.5 Coder Specialized Model", "128K Context Window", "Multimodal Vision (Qwen2-VL)"],intent:["qwen", "qwen ai", "qwen 2.5 review", "qwen price pakistan", "qwen coder 32b"],duration:'Ongoing',access:'Direct',warranty:'7 Days'},
  {id:'coursera-plus',name:'Coursera Plus',developer:'Coursera, Inc.',category:'Online Learning & Professional Certification',description:'Coursera Plus is an all-inclusive subscription program offered by Coursera, Inc. Instead of paying p...',price:16500,oldPrice:22000,usdPrice:'59.00',oldUsdPrice:'79.00',pricingModel:'Save 25%',officialPricing:'$59 / month or $399 / year',billingPeriod:'Monthly / Annual',freePlan:'Audit thousands of individual courses for free (certificates require Plus or ind',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://www.coursera.org/courseraplus',documentationUrl:'https://www.coursera.support',badge:'Verified Certs',isExternal:true,bestFor:["Degrees", "Courses", "Certificates"],logo:'assets/product-logos/coursera-plus.png',features:["Over 7,000 Verified Courses", "Accredited Professional Certificates", "Applied Guided Projects"],intent:["coursera-plus", "coursera plus price pakistan", "coursera plus review", "coursera discount pakistan", "google professional certificates"],duration:'1 Year',access:'Invitation',warranty:'30 Days'},
  {id:'udemy-personal',name:'Udemy Personal Plan',developer:'Udemy, Inc.',category:'Online Learning & Skill Development',description:'Udemy, Inc. launched the Personal Plan to provide high-volume learners with unrestricted access to i...',price:5600,oldPrice:8000,usdPrice:'19.99',oldUsdPrice:'29.99',pricingModel:'Save 30%',officialPricing:'$20 - $30 / month',billingPeriod:'Monthly / Annual',freePlan:'Thousands of free community courses available; individual course purchases start',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://www.udemy.com/personal-plan/',documentationUrl:'https://support.udemy.com',badge:'Tech Skills',isExternal:true,bestFor:["Coding", "IT Skills", "Certifications"],logo:'assets/product-logos/udemy-personal.svg',features:["11,000+ Curated Top-Tier Courses", "Hands-On Coding Workspaces", "Certification Practice Exams"],intent:["udemy-personal", "udemy personal plan price pakistan", "udemy subscription review", "udemy discount coupon pakistan", "best udemy courses 2026"],duration:'1 Month',access:'Invitation',warranty:'30 Days'},
  {id:'opus-clip',name:'OpusClip',developer:'Opus Visual Inc.',category:'AI Video Repurposing & Virality',description:'OpusClip leverages multimodal video intelligence to analyze long-form video content, pinpointing the...',price:2520,oldPrice:3600,usdPrice:'8.99',oldUsdPrice:'12.99',pricingModel:'Save 30%',officialPricing:'$9 - $29 / month',billingPeriod:'Monthly / Annual',freePlan:'Free plan with 60 processing minutes per month and 1080p watermark-free exports',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://www.opus.pro',documentationUrl:'https://help.opus.pro',badge:'Viral Shorts',isExternal:true,bestFor:["Shorts", "Captions", "Reels"],logo:'assets/product-logos/opus-clip.png',features:["AI Virality Score Engine", "Dynamic Active Speaker Reframing", "Animated Karaoke Captions"],intent:["opus-clip", "opusclip price pakistan", "opusclip ai review", "opus clip discount", "ai shorts generator"],duration:'1 Month',access:'Private',warranty:'7 Days'},
  {id:'invideo-ai',name:'InVideo AI',developer:'InVideo Inc.',category:'AI Video Generation & Prompt-to-Video',description:'InVideo AI by InVideo Inc. is a cloud-based generative video engine designed to eliminate the comple...',price:7000,oldPrice:9500,usdPrice:'24.99',oldUsdPrice:'34.99',pricingModel:'Save 26%',officialPricing:'$25 - $60 / month',billingPeriod:'Monthly / Annual',freePlan:'Free plan with 10 minutes/week of AI generation (includes InVideo watermark)',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://invideo.io',documentationUrl:'https://help.invideo.io',badge:'Pro Video AI',isExternal:true,bestFor:["Faceless", "Prompts", "Voiceover"],logo:'assets/product-logos/invideo-ai.svg',features:["Prompt-to-Video Pipeline", "Millions of Premium Stock Media Assets", "Hyper-Realistic AI Voiceovers"],intent:["invideo-ai", "invideo ai price pakistan", "invideo ai review 2026", "invideo discount code", "faceless youtube ai"],duration:'1 Month',access:'Private',warranty:'7 Days'},
  {id:'descript',name:'Descript',developer:'Descript, Inc.',category:'AI Audio & Video Editing',description:'Descript revolutionized media editing by treating audio and video as text documents. When you record...',price:5320,oldPrice:7200,usdPrice:'18.99',oldUsdPrice:'25.99',pricingModel:'Save 26%',officialPricing:'$19 - $35 / month',billingPeriod:'Monthly / Annual',freePlan:'Free plan with 1 transcription hour/month and 720p watermark-free exports',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://www.descript.com',documentationUrl:'https://help.descript.com',badge:'Audio & Video',isExternal:true,bestFor:["Podcasts", "Transcripts", "Studio Sound"],logo:'assets/product-logos/descript.svg',features:["Edit Video Like a Doc", "Studio Sound AI Enhancement", "One-Click Filler Word Removal"],intent:["descript", "descript price pakistan", "descript review 2026", "descript studio sound", "edit video like a doc"],duration:'1 Month',access:'Private',warranty:'7 Days'},
  {id:'make',name:'Make (Integromat)',developer:'Celonis SE',category:'Visual Workflow Automation',description:'Make by Celonis is widely praised as the most flexible and cost-effective visual automation platform...',price:2520,oldPrice:3600,usdPrice:'8.99',oldUsdPrice:'12.99',pricingModel:'Save 30%',officialPricing:'$9 - $29 / month',billingPeriod:'Monthly / Annual',freePlan:'Free plan with 1,000 operations per month and unlimited active scenarios',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://www.make.com',documentationUrl:'https://www.make.com/en/help',badge:'Automation Pro',isExternal:true,bestFor:["Workflows", "APIs", "Integrations"],logo:'assets/product-logos/make.svg',features:["Infinite Visual Canvas", "1,800+ Direct App Integrations", "Native AI Modules"],intent:["make", "make.com price pakistan", "make automation review", "integromat vs zapier", "no code ai automation"],duration:'1 Month',access:'Private',warranty:'7 Days'},
  {id:'firecrawl',name:'Firecrawl',developer:'Mendable, Inc.',category:'Developer Tools & AI Web Scraping',description:'Firecrawl solves the single biggest bottleneck in building Retrieval-Augmented Generation (RAG) and ...',price:4480,oldPrice:6200,usdPrice:'15.99',oldUsdPrice:'21.99',pricingModel:'Save 28%',officialPricing:'$16 - $83 / month',billingPeriod:'Monthly / Annual',freePlan:'Free plan with 500 scrapable page credits upon signup',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://www.firecrawl.dev',documentationUrl:'https://docs.firecrawl.dev',badge:'LLM Crawler',isExternal:true,bestFor:["Scraping", "Markdown", "RAG"],logo:'assets/product-logos/firecrawl.png',features:["Crawl Entire Websites Recursively", "Automatic JavaScript & SPA Rendering", "Anti-Bot & CAPTCHA Bypass"],intent:["firecrawl", "firecrawl price pakistan", "firecrawl review", "web scraping for llms", "firecrawl vs crawl4ai"],duration:'1 Month',access:'Private',warranty:'7 Days'},
  {id:'notebooklm',name:'Google NotebookLM',developer:'Google LLC',category:'AI Research & Grounded Assistants',description:'Google NotebookLM is Googles breakout research and thinking assistant built on Gemini 1.5 Pros mas...',price:1200,oldPrice:2000,usdPrice:'4.20',oldUsdPrice:'6.99',pricingModel:'Save 40%',officialPricing:'100% Free with Google Account',billingPeriod:'Monthly / Annual',freePlan:'Permanent free access with up to 50 source documents (500k words each) per noteb',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://notebooklm.google',documentationUrl:'https://notebooklm.google/faq',badge:'Research Copilot',isExternal:true,bestFor:["Study", "Notes", "Audio Overview"],logo:'assets/product-logos/notebooklm.svg',features:["Source-Grounded Truth", "Viral AI Audio Overviews", "Massive 500K Word Capacity Per Source"],intent:["notebooklm", "google notebooklm", "notebooklm review 2026", "notebooklm audio overview", "notebooklm free in pakistan"],duration:'Ongoing',access:'Direct',warranty:'30 Days'},
  {id:'supabase',name:'Supabase',developer:'Supabase, Inc.',category:'Developer Tools & Cloud Database',description:'Supabase has emerged as the premier cloud backend platform for modern web and mobile developers. Bui...',price:7000,oldPrice:9500,usdPrice:'24.99',oldUsdPrice:'34.99',pricingModel:'Save 26%',officialPricing:'Free / $25 / month (Pro)',billingPeriod:'Monthly / Annual',freePlan:'Generous Free Tier with 2 free PostgreSQL projects, 500MB database, 50k monthly ',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://supabase.com',documentationUrl:'https://supabase.com/docs',badge:'Postgres Cloud',isExternal:true,bestFor:["Postgres", "Auth", "Backend"],logo:'assets/product-logos/supabase.svg',features:["Dedicated Enterprise PostgreSQL Database", "Instant Auto-Generated APIs", "Complete Auth & User Management"],intent:["supabase", "supabase price pakistan", "supabase review", "supabase vs firebase", "open source postgres backend"],duration:'1 Month',access:'Private',warranty:'7 Days'},
  {id:'ahrefs',name:'Ahrefs (Free & Starter)',developer:'Ahrefs Pte. Ltd.',category:'Writing & SEO Intelligence',description:'Ahrefs is globally recognized as the gold standard in search engine optimization, backlink analysis,...',price:8120,oldPrice:11000,usdPrice:'29.00',oldUsdPrice:'39.99',pricingModel:'Save 26%',officialPricing:'Free AWT / $29 / month (Starter) / $99 / month (Lite)',billingPeriod:'Monthly / Annual',freePlan:'Ahrefs Webmaster Tools (AWT) is 100% free for verified website owners with 5,000',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://ahrefs.com',documentationUrl:'https://ahrefs.com/help',badge:'SEO Toolkit',isExternal:true,bestFor:["SEO", "Backlinks", "Keywords"],logo:'assets/product-logos/ahrefs.svg',features:["World's #1 Backlink Index", "Ahrefs Webmaster Tools (100% Free)", "Keywords Explorer with Search Volume"],intent:["ahrefs", "ahrefs price pakistan", "ahrefs review 2026", "ahrefs webmaster tools free", "best seo tool pakistan"],duration:'1 Month',access:'Private',warranty:'7 Days'},
  {id:'railway',name:'Railway',developer:'Railway Corp.',category:'Developer Tools & Cloud Infrastructure',description:'Railway was created to bring back the simplicity of early cloud platforms like Heroku, but with mode...',price:1400,oldPrice:2200,usdPrice:'4.99',oldUsdPrice:'7.99',pricingModel:'Save 36%',officialPricing:'$5 / month base fee + usage compute',billingPeriod:'Monthly / Annual',freePlan:'$5 free trial compute credit upon signup with GitHub',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://railway.com',documentationUrl:'https://docs.railway.com',badge:'Dev Infra',isExternal:true,bestFor:["Hosting", "Docker", "Deployments"],logo:'assets/product-logos/railway.png',features:["Git-Push Auto Deployments", "One-Click Production Databases", "Automatic Environment Variables"],intent:["railway", "railway app price pakistan", "railway deployment review", "railway vs heroku", "deploy next.js on railway"],duration:'1 Month',access:'Private',warranty:'7 Days'},
  {id:'davinci-resolve',name:'DaVinci Resolve Studio',developer:'Blackmagic Design Pty. Ltd.',category:'Professional Video Editing & Color Grading',description:'DaVinci Resolve is globally celebrated as the film industrys premier post-production ecosystem. Unl...',price:82600,oldPrice:95000,usdPrice:'295.00',oldUsdPrice:'340.00',pricingModel:'Save 13%',officialPricing:'Free Standard / $295 One-Time Lifetime License',billingPeriod:'Monthly / Annual',freePlan:'Incredibly capable 100% free version with no watermark, 4K timeline support, and',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://www.blackmagicdesign.com/products/davinciresolve',documentationUrl:'https://www.blackmagicdesign.com/support',badge:'Studio Grade',isExternal:true,bestFor:["Color Grading", "VFX", "Hollywood"],logo:'assets/product-logos/davinci-resolve.svg',features:["Industry-Standard Color Grading", "DaVinci Neural Engine AI", "Fusion Visual Effects Built-In"],intent:["davinci-resolve", "davinci resolve price pakistan", "davinci resolve studio review", "best free video editor 2026", "davinci resolve vs premiere pro"],duration:'Lifetime',access:'Retail',warranty:'Lifetime'},
  {id:'skillshare',name:'Skillshare Premium',developer:'Skillshare, Inc.',category:'Creative Arts & Design Learning',description:'Skillshare Premium is the worlds most vibrant online learning platform for creative professionals, ...',price:8900,oldPrice:12000,usdPrice:'31.99',oldUsdPrice:'42.00',pricingModel:'Save 26%',officialPricing:'~$32 / year (Pakistan Localized) / $32 / month (Standard US)',billingPeriod:'Monthly / Annual',freePlan:'7-day or 30-day free trial on referral links; several free introductory classes',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://www.skillshare.com',documentationUrl:'https://help.skillshare.com',badge:'Creative Skills',isExternal:true,bestFor:["Design", "Freelancing", "Illustration"],logo:'assets/product-logos/skillshare.svg',features:["25,000+ Creative Classes", "Project-Based Hands-On Learning", "Offline Mobile App Viewing"],intent:["skillshare", "skillshare price pakistan", "skillshare premium review", "skillshare discount code pakistan", "graphic design courses"],duration:'1 Year',access:'Invitation',warranty:'30 Days'},
  {id:'hailuo-ai',name:'MiniMax / Hailuo AI',developer:'MiniMax Technology',category:'AI Video Generation',description:'Hailuo AI, developed by Chinese AI powerhouse MiniMax, shocked the global generative video community...',price:2800,oldPrice:4000,usdPrice:'9.99',oldUsdPrice:'14.99',pricingModel:'Save 30%',officialPricing:'Free daily credits / ~$10 - $25 / month',billingPeriod:'Monthly / Annual',freePlan:'Free daily generation credits to create 720p/1080p AI video clips',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://hailuoai.video',documentationUrl:'https://hailuoai.video',badge:'Cinematic AI',isExternal:true,bestFor:["Camera", "Motion", "1080p"],logo:'assets/product-logos/hailuo-ai.png',features:["Video-01 Diffusion Transformer Engine", "Text-to-Video & Image-to-Video", "Exceptional Physical & Motion Realism"],intent:["hailuo-ai", "hailuo ai", "minimax hailuo video review", "hailuo ai price pakistan", "best ai video generator 2026"],duration:'1 Month',access:'Private',warranty:'7 Days'},
  {id:'quizlet',name:'Quizlet Plus',developer:'Quizlet, Inc.',category:'Study Tools & Active Recall Flashcards',description:'Quizlet is used by over 60 million learners every month to memorize terminology, prepare for competi...',price:2240,oldPrice:3200,usdPrice:'7.99',oldUsdPrice:'11.99',pricingModel:'Save 30%',officialPricing:'Free Standard / $7.99 / month or $35.99 / year',billingPeriod:'Monthly / Annual',freePlan:'Free digital flashcards, practice tests, and spaced-repetition study modes',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://quizlet.com',documentationUrl:'https://help.quizlet.com',badge:'Study Booster',isExternal:true,bestFor:["Flashcards", "MDCAT", "Exam Prep"],logo:'assets/product-logos/quizlet.svg',features:["7 Proven Study Modes", "Q-Chat AI Study Tutor", "Millions of Pre-Built Study Sets"],intent:["quizlet", "quizlet plus price pakistan", "quizlet review", "quizlet discount coupon", "mdcat flashcards quizlet"],duration:'1 Year',access:'Invitation',warranty:'30 Days'},
  {id:'genspark',name:'Genspark AI',developer:'MainFunc Inc.',category:'AI Search & Autonomous Research',description:'Genspark AI by MainFunc Inc. rethinks search by moving beyond both traditional blue links and single...',price:2800,oldPrice:4000,usdPrice:'9.99',oldUsdPrice:'14.99',pricingModel:'Save 30%',officialPricing:'Free Web Search / $9.99 / month (Plus)',billingPeriod:'Monthly / Annual',freePlan:'Free daily search credits and full Sparkpage generation',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://genspark.ai',documentationUrl:'https://genspark.ai',badge:'AI Research',isExternal:true,bestFor:["Sparkpages", "Search", "Multi-Agent"],logo:'assets/product-logos/genspark.png',features:["Autonomous Multi-Agent Search", "Dynamic Sparkpage Generation", "Unbiased Commercial Synthesis"],intent:["genspark", "genspark ai", "genspark review", "genspark price pakistan", "best ai search engine 2026"],duration:'1 Month',access:'Private',warranty:'7 Days'},
  {id:'chatprd',name:'ChatPRD',developer:'Claire Vo',category:'AI Product Management & Strategy',description:'Created by veteran tech executive Claire Vo, ChatPRD is a specialized AI co-pilot designed exclusive...',price:4200,oldPrice:5800,usdPrice:'14.99',oldUsdPrice:'20.99',pricingModel:'Save 28%',officialPricing:'$15 / month (Pro) / $30 / month (Elite)',billingPeriod:'Monthly / Annual',freePlan:'7-day free trial on signup',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://www.chatprd.ai',documentationUrl:'https://www.chatprd.ai',badge:'PM Copilot',isExternal:true,bestFor:["PRD", "Agile", "User Stories"],logo:'assets/product-logos/chatprd.png',features:["Product-Specific AI Personas", "Comprehensive PRD Generation", "Edge Case & Scope Hunter"],intent:["chatprd", "chatprd review", "chatprd price pakistan", "ai for product managers", "write prd with ai"],duration:'1 Month',access:'Private',warranty:'7 Days'},
  {id:'domo-ai',name:'Domo AI',developer:'DomoAI',category:'AI Video Stylization & Anime Transfer',description:'Domo AI has captured the social media world by solving one of the hardest challenges in generative v...',price:2800,oldPrice:4000,usdPrice:'9.99',oldUsdPrice:'14.99',pricingModel:'Save 30%',officialPricing:'$9.99 - $19.99 / month',billingPeriod:'Monthly / Annual',freePlan:'Free trial credits upon Discord / Web signup',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://domoai.app',documentationUrl:'https://docs.domoai.app',badge:'Anime & VFX',isExternal:true,bestFor:["Animation", "Style Transfer", "Discord"],logo:'assets/product-logos/domo-ai.png',features:["Video-to-Video Style Transfer", "Consistent Character Identity", "Text-to-Video & Image-to-Video"],intent:["domo-ai", "domo ai price pakistan", "domo ai review", "video to anime ai", "ai video style transfer"],duration:'1 Month',access:'Private',warranty:'7 Days'},
  {id:'morphic',name:'Morphic AI',developer:'Morphic (Open Source)',category:'Open Source Generative AI Search',description:'Morphic was developed as an open-source answer to proprietary AI search engines like Perplexity. Bui...',price:1500,oldPrice:2500,usdPrice:'4.99',oldUsdPrice:'8.99',pricingModel:'Save 40%',officialPricing:'100% Free Open Source / $10 / month (Pro Cloud)',billingPeriod:'Monthly / Annual',freePlan:'Fully free public search with live citations and code generation',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://morphic.sh',documentationUrl:'https://github.com/miurla/morphic',badge:'Open Research',isExternal:true,bestFor:["Citations", "Generative UI", "Search"],logo:'assets/product-logos/morphic.png',features:["100% Open Source Architecture", "Real-Time Web Search Grounding", "Direct Source Verification Links"],intent:["morphic", "morphic ai", "morphic search review", "open source perplexity alternative", "morphic ai pakistan"],duration:'Ongoing',access:'Direct',warranty:'7 Days'},
  {id:'higgsfield',name:'Higgsfield AI',developer:'Higgsfield AI',category:'Mobile Cinematic AI Video & Motion',description:'Higgsfield AI was founded by Alex Mashrabov (former Head of Generative AI at Snap) with a bold missi...',price:2800,oldPrice:4000,usdPrice:'9.99',oldUsdPrice:'14.99',pricingModel:'Save 30%',officialPricing:'Free daily credits / ~$10 - $20 / month',billingPeriod:'Monthly / Annual',freePlan:'Free credits daily for mobile video generation',commercialStatus:'DIRECTORY_ONLY',officialUrl:'https://higgsfield.ai',documentationUrl:'https://higgsfield.ai',badge:'Mobile Camera',isExternal:true,bestFor:["Director", "Camera", "Orbit"],logo:'assets/product-logos/higgsfield.png',features:["Mobile-First Generative Video", "Cinematic Camera Direction Controls", "Personalized Character & Avatar Animation"],intent:["higgsfield", "higgsfield ai", "higgsfield video review", "higgsfield price pakistan", "mobile ai video generator"],duration:'1 Month',access:'Private',warranty:'7 Days'}
];

const categoryData = [
  ['AI Assistants','AI','7 tools'],
  ['AI Video','▶','5 tools'],
  ['Design','✦','6 tools'],
  ['Development','</>','5 tools'],
  ['Writing & SEO','✍','4 tools'],
  ['Productivity','P','3 tools'],
  ['AI Voice','∿','2 tools'],
  ['VPN & Security','S','2 tools'],
  ['Entertainment','E','3 tools'],
  ['Business','B','2 tools'],
  ['Software','W','1 tool']
];

const officialLogos = {
  chatgpt: 'assets/product-logos/chatgpt.png',
  gemini: 'assets/product-logos/gemini.png',
  veo: 'assets/product-logos/veo.png',
  leonardo: 'assets/product-logos/leonardo.png',
  elevenlabs: 'assets/product-logos/elevenlabs.png',
  canva: 'assets/product-logos/canva.png',
  figma: 'assets/product-logos/figma.png',
  capcut: 'assets/product-logos/capcut.png',
  adobe: 'assets/product-logos/adobe.png',
  lovable: 'assets/product-logos/lovable.png',
  gamma: 'assets/product-logos/gamma.png',
  replit: 'assets/product-logos/replit.png',
  n8n: 'assets/product-logos/n8n.png',
  notion: 'assets/product-logos/notion.png',
  nordvpn: 'assets/product-logos/nordvpn.png',
  surfshark: 'assets/product-logos/surfshark.png',
  youtube: 'assets/product-logos/youtube.png',
  netflix: 'assets/product-logos/netflix.png',
  linkedin: 'assets/product-logos/linkedin.png',
  windows: 'assets/product-logos/windows.png',
  claude: 'assets/product-logos/claude.png',
  midjourney: 'assets/product-logos/midjourney.png',
  cursor: 'assets/product-logos/cursor.png',
  perplexity: 'assets/product-logos/perplexity.png',
  deepseek: 'assets/product-logos/deepseek.png',
  grok: 'assets/product-logos/grok.png',
  runway: 'assets/product-logos/runway.png',
  heygen: 'assets/product-logos/heygen.png',
  grammarly: 'assets/product-logos/grammarly.png',
  quillbot: 'assets/product-logos/quillbot.png',
  semrush: 'assets/product-logos/semrush.png',
  allinone: 'assets/product-logos/chatgpt.png',
  tradingview: 'assets/product-logos/tradingview.png',
  kling: 'assets/product-logos/kling.png',
  freepik: 'assets/product-logos/freepik.png',
  spotify: 'assets/product-logos/spotify.png',
  copilot: 'assets/product-logos/copilot.png',
  suno: 'assets/product-logos/suno.png',
  turnitin: 'assets/product-logos/turnitin.png',
  office365: 'assets/product-logos/office365.png'
};

products.forEach(p => {
  if (officialLogos[p.id]) {
    p.logo = officialLogos[p.id];
  }
});

const safeCatalogText = value => String(value || '').replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[char]);

try {
  const managedCatalog = JSON.parse(localStorage.getItem('atg-admin-products') || '[]');
  if (Array.isArray(managedCatalog)) {
    managedCatalog.forEach(saved => {
      const existing = products.find(product => product.id === saved.id);
      if (existing) {
        if (saved.name) existing.name = safeCatalogText(saved.name);
        if (saved.category) existing.category = safeCatalogText(saved.category);
        if (Number(saved.price) > 0) existing.price = Number(saved.price);
        if (saved.description) existing.description = safeCatalogText(saved.description);
        if (saved.logo && /^(https:\/\/|assets\/)/.test(saved.logo)) existing.logo = saved.logo;
      } else if (saved.id && saved.name && saved.category && Number(saved.price) > 0) {
        products.push({
          id: saved.id,
          name: safeCatalogText(saved.name),
          category: safeCatalogText(saved.category),
          description: saved.description ? safeCatalogText(saved.description) : 'A newly added subscription. Contact our team for complete plan details.',
          price: Number(saved.price),
          oldPrice: Math.ceil(Number(saved.price) * 1.2),
          duration: '1 Month',
          access: 'Private',
          delivery:'After payment confirmation',
          warranty: '7 Days',
          rating: 4.5,
          badge: 'New',
          bestFor: [safeCatalogText(saved.category)],
          logo: saved.logo && /^(https:\/\/|assets\/)/.test(saved.logo) ? saved.logo : 'assets/brand-logo-light.webp',
          features: ['Plan details confirmed before payment', 'Direct WhatsApp activation'],
          intent: [String(saved.category).toLowerCase(), String(saved.name).toLowerCase()]
        });
      }
    });
  }
} catch {
  localStorage.removeItem('atg-admin-products');
}

function loadStoredCart() {
  try {
    const saved = JSON.parse(localStorage.getItem('atg-cart') || '[]');
    if (!Array.isArray(saved)) return [];
    return saved.map(item => {
      if (typeof item === 'string') return { id: item, qty: 1 };
      if (item && item.id) return { id: item.id, qty: Math.max(1, parseInt(item.qty, 10) || 1) };
      return null;
    }).filter(item => item && products.some(p => p.id === item.id && p.commercialStatus !== 'DIRECTORY_ONLY' && !p.isExternal));
  } catch {
    localStorage.removeItem('atg-cart');
    return [];
  }
}

function isItemInCart(id) {
  return state.cart.some(item => (typeof item === 'string' ? item === id : item.id === id));
}

function getCartItems() {
  return state.cart.map(item => {
    const id = typeof item === 'string' ? item : item.id;
    const qty = (typeof item === 'object' && item.qty) ? Math.max(1, parseInt(item.qty, 10) || 1) : 1;
    const product = products.find(p => p.id === id && p.commercialStatus !== 'DIRECTORY_ONLY' && !p.isExternal);
    return product ? { p: product, qty } : null;
  }).filter(Boolean);
}

function loadStoredFavorites() {
  try {
    const saved = JSON.parse(localStorage.getItem('atg-favorites') || '[]');
    return Array.isArray(saved) ? saved.filter(id => products.some(p => p.id === id)) : [];
  } catch {
    localStorage.removeItem('atg-favorites');
    return [];
  }
}

let state = {
  currency: localStorage.getItem('atg-currency') || 'PKR',
  category: 'All',
  query: '',
  limit: products.length,
  cart: loadStoredCart(),
  favorites: loadStoredFavorites(),
  compare: [],
  finder: { intent: '', minBudget: 0, maxBudget: Infinity }
};
let productsRendered = false;

const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const money = (n, usd) => {
  if (n === null || n === undefined) return 'N/A';
  if (state.currency === 'USD') {
    return usd !== undefined ? '$' + usd + ' USD (Ref)' : 'Quote on Inquiry';
  }
  return 'Rs. ' + n.toLocaleString('en-PK');
};
const discount = p => Math.round((1 - p.price / p.oldPrice) * 100);
const svg = id => `<svg><use href="#${id}"></use></svg>`;
const escapeHTML = value => String(value).replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[char]);

window.dataLayer = window.dataLayer || [];
function trackEvent(event, details = {}) {
  window.dataLayer.push({ event, ...details });
}

function clearSearchField() {
  const input = $('#heroSearch');
  if (input) input.value = '';
}

/* --------------------------------------------------------------------------
   RENDERING FUNCTIONS
   -------------------------------------------------------------------------- */
function renderCategories() {
  const container = $('#categoryGrid');
  if (!container) return;
  container.innerHTML = categoryData.map((c, index) => {
    const count = products.filter(product => product.category === c[0]).length;
    return `
    <a href="#products" class="category-card" data-category="${c[0]}">
      <span class="category-visual" style="--category-x:${(index % 5) * 25}%;--category-y:${index < 5 ? 0 : 100}%">
        <span class="category-count">${count} ${count === 1 ? 'tool' : 'tools'}</span>
      </span>
      <span class="category-content">
        <span>
          <small>Explore Collection</small>
          <b>${c[0]}</b>
        </span>
        <i aria-hidden="true">${svg('i-arrow')}</i>
      </span>
    </a>`;
  }).join('');
}

function renderFilters() {
  const cats = ['All', 'Favorites', 'AI Assistants', 'AI Video', 'Design', 'Development', 'Writing & SEO', 'Productivity', 'VPN & Security', 'Entertainment'];
  const row = $('#filterRow');
  if (!row) return;
  row.innerHTML = cats.map(c => {
    const label = c === 'Favorites' ? `★ Favorites${state.favorites.length ? ` (${state.favorites.length})` : ''}` : c;
    return `<button class="filter-chip ${state.category === c ? 'active' : ''}" data-filter="${c}" aria-pressed="${state.category === c}">${label}</button>`;
  }).join('');
}

function filteredProducts() {
  let out;
  if (state.category === 'Favorites') {
    out = products.filter(p => state.favorites.includes(p.id));
  } else {
    out = products.filter(p => state.category === 'All' || p.category === state.category);
  }
  const q = state.query.toLowerCase().trim();
  if (q === 'under 1000') {
    out = out.filter(p => p.price < 1000);
  } else if (q) {
    out = out.filter(p => [p.name, p.category, p.description, ...p.bestFor, ...p.intent].join(' ').toLowerCase().includes(q));
  }
  const sort = $('#sortSelect') ? $('#sortSelect').value : 'featured';
  if (sort === 'price-low') out.sort((a, b) => a.price - b.price);
  if (sort === 'rating') out.sort((a, b) => b.rating - a.rating);
  if (sort === 'discount') out.sort((a, b) => discount(b) - discount(a));
  return out;
}

const STATIC_TOOL_PAGES = new Set([
  'adobe', 'canva', 'capcut', 'chatgpt', 'elevenlabs', 'figma', 'gamma', 'gemini',
  'leonardo', 'linkedin', 'lovable', 'n8n', 'netflix', 'nordvpn', 'notion',
  'replit', 'surfshark', 'veo', 'windows', 'youtube',
  'claude', 'midjourney', 'cursor', 'perplexity', 'deepseek', 'grok',
  'runway', 'heygen', 'grammarly', 'quillbot', 'semrush', 'allinone',
  'tradingview', 'kling', 'freepik', 'spotify', 'copilot', 'suno', 'turnitin', 'office365',
  'windsurf', 'v0', 'bolt-new', 'manus-ai', 'qwen', 'coursera-plus', 'udemy-personal',
  'opus-clip', 'invideo-ai', 'descript', 'make', 'firecrawl',
  'notebooklm', 'supabase', 'ahrefs', 'railway', 'davinci-resolve', 'skillshare', 'hailuo-ai', 'quizlet', 'genspark', 'chatprd', 'domo-ai', 'morphic', 'higgsfield'
]);


function card(p) {
  const inCart = isItemInCart(p.id);
  const isFav = state.favorites.includes(p.id);
  const isDir = p.commercialStatus === 'DIRECTORY_ONLY' || p.isExternal;
  const isUSD = state.currency === 'USD';

  const ratingBadge = isUSD ? 'USD Reference' : 'Verified PKR';
  let oldPriceDisplay = '';
  let mainPriceDisplay = '';

  if (isUSD) {
    mainPriceDisplay = p.usdPrice ? `$${p.usdPrice} USD` : 'Quote on Inquiry';
    if (p.oldUsdPrice) {
      oldPriceDisplay = `<small>$${p.oldUsdPrice} USD</small>`;
    }
  } else {
    mainPriceDisplay = `Rs. ${p.price.toLocaleString('en-PK')}`;
    if (p.oldPrice && p.oldPrice > p.price) {
      oldPriceDisplay = `<small>Rs. ${p.oldPrice.toLocaleString('en-PK')}</small>`;
    }
  }

  if (isDir) {
    const badgeText = escapeHTML(p.badge || 'Popular');
    const durationDisplay = escapeHTML(p.duration || '1 Month');
    const accessDisplay = escapeHTML(p.access ? (p.access.endsWith('Access') ? p.access : p.access + ' Access') : 'Private Access');
    const warrantyDisplay = escapeHTML(p.warranty ? p.warranty : '7 Days');
    const savingBadge = escapeHTML(p.pricingModel || 'Save 25%');

    return `
  <article class="product-card directory-card" data-id="${p.id}">
    <div class="product-media">
      <span class="product-badge">${badgeText}</span>
      <button class="favorite-toggle${isFav ? ' active' : ''}" data-favorite="${p.id}" aria-label="${isFav ? 'Remove ' + p.name + ' from favorites' : 'Add ' + p.name + ' to favorites'}" aria-pressed="${isFav}" title="${isFav ? 'Remove from favorites' : 'Add to favorites'}">
        <svg><use href="#i-star"></use></svg>
      </button>
      <img class="brand-logo" src="${p.logo}" width="128" height="128" loading="lazy" alt="Official ${p.name} logo" decoding="async" onerror="this.onerror=null;this.src='assets/logo-transparent.webp';">
    </div>
    <div class="product-body">
      <div class="product-meta">
        <span class="category-pill">${p.category}</span>
        <span class="rating">${ratingBadge}</span>
      </div>
      <h3 class="product-title"><a class="product-page-link" href="tools/${p.id}/">${p.name}</a></h3>
      <p class="product-desc">${p.description}</p>
      <div class="tags">
        ${(p.bestFor || []).map(t => `<button type="button" class="tag-chip" data-tag="${safeCatalogText(t)}" title="Filter by ${safeCatalogText(t)}">${safeCatalogText(t)}</button>`).join('')}
      </div>
      <div class="product-specs">
        <span><i></i>${durationDisplay}</span>
        <span>${accessDisplay}</span>
        <span>🛡️ ${warrantyDisplay}</span>
      </div>
      <div class="product-price">
        <div class="price-block">
          ${oldPriceDisplay}
          <strong>${mainPriceDisplay}</strong>
        </div>
        <span class="saving">${savingBadge}</span>
      </div>
      <div class="product-delivery-note">⚡ Verified WhatsApp Delivery · After Confirmation</div>
      <div class="card-actions directory-actions">
        <a class="buy-now-card explore-tool-btn" href="tools/${p.id}/"><svg><use href="#i-whatsapp"></use></svg> Buy now</a>
        <a class="detail-button" href="tools/${p.id}/">View details</a>
        <a class="official-link-btn" href="${p.officialUrl}" target="_blank" rel="noopener noreferrer" title="Visit ${p.name} official website" aria-label="Visit ${p.name} official website">
          ${svg('i-external')}
        </a>
      </div>
    </div>
    <span hidden style="display:none!important">Directory Reference</span>
  </article>`;
  }

  const savingBadgeHtml = (p.oldPrice && p.oldPrice > p.price) ? `<span class="saving">Save ${discount(p)}%</span>` : '';

  return `
  <article class="product-card" data-id="${p.id}">
    <div class="product-media">
      <span class="product-badge">${escapeHTML(p.badge || 'Popular')}</span>
      <button class="favorite-toggle${isFav ? ' active' : ''}" data-favorite="${p.id}" aria-label="${isFav ? 'Remove ' + p.name + ' from favorites' : 'Add ' + p.name + ' to favorites'}" aria-pressed="${isFav}" title="${isFav ? 'Remove from favorites' : 'Add to favorites'}">
        <svg><use href="#i-star"></use></svg>
      </button>
      <img class="brand-logo" src="${p.logo}" width="128" height="128" loading="lazy" alt="Official ${p.name} logo" decoding="async" onerror="this.onerror=null;this.src='assets/logo-transparent.webp';">
    </div>
    <div class="product-body">
      <div class="product-meta">
        <span class="category-pill">${p.category}</span>
        <span class="rating">${ratingBadge}</span>
      </div>
      <h3 class="product-title"><a class="product-page-link" href="tools/${p.id}/">${p.name}</a></h3>
      <p class="product-desc">${p.description}</p>
      <div class="tags">
        ${(p.bestFor || []).map(t => `<button type="button" class="tag-chip" data-tag="${safeCatalogText(t)}" title="Filter by ${safeCatalogText(t)}">${safeCatalogText(t)}</button>`).join('')}
      </div>
      <div class="product-specs">
        <span><i></i>${p.duration}</span>
        <span>${p.access} Access</span>
        <span>🛡️ ${p.warranty || '7-Day'}</span>
      </div>
      <div class="product-price">
        <div class="price-block">
          ${oldPriceDisplay}
          <strong>${mainPriceDisplay}</strong>
        </div>
        ${savingBadgeHtml}
      </div>
      <div class="product-delivery-note">⚡ Verified WhatsApp Delivery · After Confirmation</div>
      <div class="card-actions">
        <button class="buy-now-card" data-order="${p.id}">${svg('i-whatsapp')} Buy now</button>
        <a class="detail-button" href="tools/${p.id}/">View details</a>
        <a class="official-link-btn" href="${p.officialUrl || '#'}" target="_blank" rel="noopener noreferrer" title="Visit ${p.name} official website" aria-label="Visit ${p.name} official website">
          ${svg('i-external')}
        </a>
        <button class="add-button${inCart ? ' added' : ''}" data-add="${p.id}" aria-label="${inCart ? 'View ' + p.name + ' in cart' : 'Add ' + p.name + ' to cart'}" aria-pressed="${inCart}">
          ${svg(inCart ? 'i-check' : 'i-plus')}
        </button>
      </div>
    </div>
  </article>`;
}

function renderProducts() {
  productsRendered = true;
  const all = filteredProducts();
  const shown = all.slice(0, state.limit);
  const grid = $('#productGrid');
  if (grid) grid.innerHTML = shown.map(card).join('');
  
  const empty = $('#emptyState');
  if (empty) empty.classList.toggle('show', !all.length);
  
  const aq = $('#activeQuery');
  if (aq) {
    aq.classList.toggle('show', !!state.query);
    aq.innerHTML = state.query ? `Showing verified results for “${escapeHTML(state.query)}” · <button id="clearQuery">Clear search</button>` : '';
  }
  
  renderFilters();
}

/* --------------------------------------------------------------------------
   CART & COMPARE LOGIC
   -------------------------------------------------------------------------- */
function updateCart() {
  try {
    localStorage.setItem('atg-cart', JSON.stringify(state.cart));
  } catch (_) {}

  const items = getCartItems();
  const totalCount = items.reduce((sum, item) => sum + item.qty, 0);

  const cCount = $('#cartCount');
  const mCount = $('#mobileCartCount');
  if (cCount) cCount.textContent = totalCount;
  if (mCount) mCount.textContent = totalCount;

  const cartItems = $('#cartItems');
  if (cartItems) {
    cartItems.innerHTML = items.length ? items.map(({ p, qty }) => `
      <div class="cart-item" data-cart-id="${p.id}">
        <img src="${p.logo}" width="56" height="56" loading="lazy" alt="${p.name}" onerror="this.onerror=null;this.src='assets/logo-transparent.webp';">
        <div class="cart-item-details">
          <b>${p.name}</b>
          <small>${p.duration} · ${p.access} Access</small>
          <div class="cart-qty-row">
            <button type="button" class="cart-qty-btn minus" data-qty-change="${p.id}" data-delta="-1" aria-label="Decrease quantity for ${p.name}">−</button>
            <span class="cart-qty-val">${qty}</span>
            <button type="button" class="cart-qty-btn plus" data-qty-change="${p.id}" data-delta="1" aria-label="Increase quantity for ${p.name}">+</button>
            <strong class="cart-line-price">${state.currency === 'USD' && p.usdPrice ? '$' + (parseFloat(p.usdPrice) * qty).toFixed(2) + ' USD' : 'Rs. ' + (p.price * qty).toLocaleString('en-PK')}</strong>
          </div>
        </div>
        <button type="button" class="remove-cart" data-remove="${p.id}" aria-label="Remove ${p.name}">×</button>
      </div>
    `).join('') : `
      <div class="cart-empty">
        <img src="assets/logo-transparent.webp" width="80" height="80" loading="lazy" class="empty-state-logo" alt="AI Tool Gems Diamond">
        <h3>Your cart is empty</h3>
        <p>Explore verified AI subscriptions and add them to your cart.</p>
        <a href="#products" class="cart-empty-browse-btn" onclick="closeLayer($('#cartDrawer'))">Browse Subscriptions &darr;</a>
      </div>
    `;
  }

  const isUSD = state.currency === 'USD';
  const subtotalPkr = items.reduce((sum, { p, qty }) => sum + (p.price * qty), 0);
  const subtotalUsd = items.reduce((sum, { p, qty }) => sum + (parseFloat(p.usdPrice || 0) * qty), 0);
  const totalEl = $('#cartTotal');
  if (totalEl) {
    totalEl.textContent = isUSD ? '$' + subtotalUsd.toFixed(2) + ' USD' : 'Rs. ' + subtotalPkr.toLocaleString('en-PK');
  }
  
  const footer = $('#cartFooter');
  if (footer) footer.style.display = items.length ? 'block' : 'none';
  updateBundleButton();
}

function updateBundleButton() {
  const button = $('#addBundle');
  if (!button) return;
  const bundleIds = ['chatgpt', 'canva', 'capcut', 'elevenlabs'];
  const isComplete = bundleIds.every(id => isItemInCart(id));
  button.classList.toggle('added', isComplete);
  button.setAttribute('aria-pressed', String(isComplete));
  button.innerHTML = isComplete ? `Stack in cart ${svg('i-check')}` : `Add creator stack ${svg('i-plus')}`;
}

function addToCart(id, qty = 1) {
  if (!id) return;
  const product = products.find(p => p.id === id);
  if (!product) return;

  if (product.commercialStatus === 'DIRECTORY_ONLY' || product.isExternal) {
    toast(`${product.name} is a directory listing and cannot be ordered through cart.`);
    return;
  }

  const existing = state.cart.find(item => (typeof item === 'string' ? item === id : item.id === id));
  if (existing) {
    if (typeof existing === 'string') {
      const idx = state.cart.indexOf(existing);
      state.cart[idx] = { id, qty: Math.min(10, 1 + qty) };
    } else {
      existing.qty = Math.min(10, (existing.qty || 1) + qty);
    }
    toast(`Updated quantity for ${product.name}`);
  } else {
    state.cart.push({ id, qty: Math.max(1, qty) });
    trackEvent('add_to_cart', { item_id: product.id, item_name: product.name, value: product.price, currency: 'PKR' });
    toast(`Added ${product.name} to your cart`);
  }
  updateCart();
  syncCartUI(id);
}

function updateCartQty(id, delta) {
  const existing = state.cart.find(item => (typeof item === 'string' ? item === id : item.id === id));
  if (!existing) return;
  if (typeof existing === 'string') {
    const idx = state.cart.indexOf(existing);
    const newQty = 1 + delta;
    if (newQty <= 0) {
      removeFromCart(id);
      return;
    }
    state.cart[idx] = { id, qty: newQty };
  } else {
    existing.qty = (existing.qty || 1) + delta;
    if (existing.qty <= 0) {
      removeFromCart(id);
      return;
    }
  }
  updateCart();
  syncCartUI(id);
}

function clearCart() {
  if (!state.cart.length) return;
  state.cart = [];
  try {
    localStorage.removeItem('atg-cart');
  } catch (_) {}
  updateCart();
  products.forEach(p => syncCartUI(p.id));
  toast('Cart cleared');
}

function removeFromCart(id) {
  if (!id) return;
  const product = products.find(p => p.id === id);
  state.cart = state.cart.filter(item => (typeof item === 'string' ? item !== id : item.id !== id));
  if (product) trackEvent('remove_from_cart', { item_id: product.id, item_name: product.name, value: product.price, currency: 'PKR' });
  toast(`Removed ${product ? product.name : 'item'} from cart`);
  updateCart();
  syncCartUI(id);
}

function syncCartUI(id) {
  const inCart = isItemInCart(id);
  const cardBtns = document.querySelectorAll(`button.add-button[data-add="${id}"]`);
  cardBtns.forEach(btn => {
    btn.classList.toggle('added', inCart);
    btn.setAttribute('aria-pressed', String(inCart));
    const p = products.find(x => x.id === id);
    const pName = p ? p.name : 'product';
    btn.setAttribute('aria-label', inCart ? `View ${pName} in cart` : `Add ${pName} to cart`);
    btn.innerHTML = svg(inCart ? 'i-check' : 'i-plus');
  });

  const modalBtn = document.querySelector(`.add-detail[data-add="${id}"]`);
  if (modalBtn) {
    modalBtn.classList.toggle('added', inCart);
    modalBtn.textContent = inCart ? 'Added to cart' : 'Add to cart';
  }
}

function toggleFavorite(id) {
  if (!id) return;
  const product = products.find(p => p.id === id);
  if (!product) return;
  const wasFav = state.favorites.includes(id);
  state.favorites = wasFav ? state.favorites.filter(x => x !== id) : [...state.favorites, id];
  try {
    localStorage.setItem('atg-favorites', JSON.stringify(state.favorites));
  } catch (e) {}
  syncFavoritesUI(id);
  renderFilters();
  if (state.category === 'Favorites') {
    renderProducts();
  }
  toast(wasFav ? `Removed ${product.name} from favorites` : `Added ${product.name} to favorites`);
}

function syncFavoritesUI(id) {
  const isFav = state.favorites.includes(id);
  const p = products.find(x => x.id === id);
  const pName = p ? p.name : 'tool';
  const btns = document.querySelectorAll(`[data-favorite="${id}"]`);
  btns.forEach(btn => {
    btn.classList.toggle('active', isFav);
    btn.setAttribute('aria-pressed', String(isFav));
    btn.setAttribute('aria-label', isFav ? `Remove ${pName} from favorites` : `Add ${pName} to favorites`);
    btn.setAttribute('title', isFav ? `Remove ${pName} from favorites` : `Add ${pName} to favorites`);
  });
}

function syncAllFavorites() {
  products.forEach(p => syncFavoritesUI(p.id));
}

function updateCompare() {
  const compCount = $('#compareCount');
  const compBar = $('#compareBar');
  const compMini = $('#compareMini');
  if (compCount) compCount.textContent = state.compare.length;
  if (compBar) compBar.classList.toggle('show', state.compare.length > 0);
  document.body.classList.toggle('compare-mode', state.compare.length > 0);
  if (compMini) {
    compMini.innerHTML = state.compare.map(id => {
      const p = products.find(x => x.id === id);
      return `<img src="${p.logo}" width="128" height="128" alt="${p.name}">`;
    }).join('');
  }
}

function toggleCompare(id) {
  if (state.compare.includes(id)) {
    state.compare = state.compare.filter(x => x !== id);
  } else if (state.compare.length < 3) {
    state.compare.push(id);
  } else {
    return toast('You can compare up to 3 tools at once');
  }
  updateCompare();
  renderProducts();
}

let focusBeforeLayer = null;

function openLayer(el) {
  if (!el) return;
  // Close any other open modal or drawer so layers never overlap
  $$('.drawer.open, .modal.open').forEach(x => {
    if (x !== el) {
      x.classList.remove('open');
      x.setAttribute('aria-hidden', 'true');
    }
  });
  focusBeforeLayer = document.activeElement;
  const backdrop = $('#backdrop');
  if (backdrop) backdrop.classList.add('show');
  el.classList.add('open');
  el.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
  document.body.classList.add('layer-active');
  requestAnimationFrame(() => {
    const first = el.querySelector('[data-close], button, a, input, select, [tabindex="0"]');
    if (first) first.focus();
  });
}

function closeLayers() {
  $$('.drawer, .modal').forEach(x => {
    x.classList.remove('open');
    x.setAttribute('aria-hidden', 'true');
  });
  const backdrop = $('#backdrop');
  if (backdrop) backdrop.classList.remove('show');
  document.body.style.overflow = '';
  document.body.classList.remove('layer-active');
  if (focusBeforeLayer && document.contains(focusBeforeLayer)) focusBeforeLayer.focus();
  focusBeforeLayer = null;
}

function openProduct(id) {
  const p = products.find(x => x.id === id);
  if (!p) return;
  trackEvent('view_item', { item_id: p.id, item_name: p.name, item_category: p.category, value: p.price || 0, currency: 'PKR' });
  const detail = $('#productDetail');
  if (detail) {
    if (p.commercialStatus === 'DIRECTORY_ONLY') {
      detail.innerHTML = `
        <div class="product-detail directory-detail">
          <div class="detail-media">
            <img class="brand-logo" src="${p.logo}" width="128" height="128" alt="Official ${p.name} logo" onerror="this.onerror=null;this.src='assets/logo-transparent.webp';">
          </div>
          <div class="detail-copy">
            <span class="detail-category">${p.category} · Directory Profile</span>
            <h2 id="productDetailTitle">${p.name}</h2>
            <div class="detail-rating">Reference & Research Listing</div>
            <p>${p.description}</p>
            <div class="product-delivery-note">Directory Listing: This profile is provided for research and workflow evaluation. It is not available for direct purchase or automated checkout.</div>
            <div class="feature-list">
              ${p.features.map(f => `<span>${svg('i-check')}${f}</span>`).join('')}
            </div>
            <div class="detail-actions">
              ${STATIC_TOOL_PAGES.has(p.id) ? `<a class="open-details-btn directory-btn" href="tools/${p.id}/">Open Full Tool Profile ${svg('i-arrow')}</a>` : ""}
            </div>
          </div>
        </div>
      `;
    } else {
      const isUsd = state.currency === 'USD';
      const priceHtml = isUsd && p.usdPrice
        ? `<strong>$${p.usdPrice} USD (Reference Inquiry)</strong> <em class="alt-currency">(Domestic: Rs. ${p.price.toLocaleString('en-PK')})</em>`
        : `<strong>Rs. ${p.price.toLocaleString('en-PK')}</strong> ${p.oldPrice ? `<del>Rs. ${p.oldPrice.toLocaleString('en-PK')}</del>` : ''} ${p.usdPrice ? `<em class="alt-currency">(USD Ref: $${p.usdPrice})</em>` : ''}`;
      
      const inCart = isItemInCart(p.id);
      detail.innerHTML = `
        <div class="product-detail">
          <div class="detail-media">
            <img class="brand-logo" src="${p.logo}" width="128" height="128" alt="Official ${p.name} logo" onerror="this.onerror=null;this.src='assets/logo-transparent.webp';">
          </div>
          <div class="detail-copy">
            <span class="detail-category">${p.category} · ${p.badge}</span>
            <h2 id="productDetailTitle">${p.name}</h2>
            <div class="detail-rating">Plan details confirmed before payment</div>
            <p>${p.description} Availability, access type, and delivery timing are confirmed directly on WhatsApp before payment.</p>
            <div class="detail-price">${priceHtml}</div>
            <div class="detail-grid">
              <div class="detail-spec"><small>Plan duration</small><b>${p.duration}</b></div>
              <div class="detail-spec"><small>Access type</small><b>${p.access} Plan</b></div>
              <div class="detail-spec"><small>Delivery speed</small><b>${p.delivery}</b></div>
              <div class="detail-spec"><small>Warranty</small><b>${p.warranty}</b></div>
            </div>
            <div class="feature-list">
              ${p.features.map(f => `<span>${svg('i-check')}${f}</span>`).join('')}
            </div>
            <div class="detail-actions">
              <button class="add-detail ${inCart ? 'added' : ''}" data-add="${p.id}">${inCart ? 'Added to cart' : 'Add to cart'}</button>
              <button class="order-now" data-order="${p.id}">${svg('i-whatsapp')} Order on WhatsApp</button>
            </div>
            <div class="product-delivery-note">Verified WhatsApp delivery · Access details confirmed prior to payment.</div>
            ${STATIC_TOOL_PAGES.has(p.id) ? `<a class="full-details-link" href="tools/${p.id}/">Open full product page ${svg('i-arrow')}</a>` : ""}
          </div>
        </div>
      `;
    }
  }
  openLayer($('#productModal'));
}

function waLink(message) {
  const saved = localStorage.getItem('atg-whatsapp');
  const cleanSaved = (saved || '').replace(/\D/g, '');
  if (cleanSaved === LEGACY_WA_NUMBER) localStorage.setItem('atg-whatsapp', DEFAULT_WA_NUMBER);
  const number = /^\d{10,15}$/.test(cleanSaved)
    && cleanSaved !== '923001234567'
    && cleanSaved !== LEGACY_WA_NUMBER
    ? cleanSaved
    : DEFAULT_WA_NUMBER;
  const attributedMessage = window.ATGAttribution ? window.ATGAttribution.appendToMessage(message) : message;
  return `https://wa.me/${number}?text=${encodeURIComponent(attributedMessage)}`;
}

function openWhatsApp(url) {
  try {
    const win = window.open(url, '_blank');
    if (!win || win.closed || typeof win.closed === 'undefined') {
      window.location.href = url;
    }
  } catch (_) {
    window.location.href = url;
  }
}

function orderProduct(id) {
  const p = products.find(x => x.id === id);
  if (!p) return;
  if (p.commercialStatus === 'DIRECTORY_ONLY') {
    toast('This tool is a directory reference profile and is not available for purchase.');
    return;
  }
  const isUsd = state.currency === 'USD';
  const priceDisplay = isUsd && p.usdPrice ? `$${p.usdPrice} USD (Reference Inquiry)` : `Rs. ${p.price.toLocaleString('en-PK')}`;
  const paymentInstructions = isUsd
    ? '💳 Preferred Payment: USDT (TRC20 / BEP20) / Binance Pay / Wise (International Quote Upon Inquiry)\n\nPlease confirm availability, payment address, and delivery time.'
    : '💳 Preferred Payment: EasyPaisa / JazzCash / SadaPay / Bank IBFT\n\nPlease confirm availability, payment account, and delivery time.';

  trackEvent('whatsapp_checkout', { item_id: p.id, item_name: p.name, value: isUsd && p.usdPrice ? parseFloat(p.usdPrice) : (p.price || 0), currency: isUsd ? 'USD' : 'PKR' });
  openWhatsApp(waLink(`Hello AI Tool Gems 👋\n\nI would like to order:\n\n💎 Product: ${p.name}\n⏱️ Duration: ${p.duration}\n🔑 Access: ${p.access}\n💰 Price: ${priceDisplay}\n\n${paymentInstructions}`));
}

function checkout() {
  const items = getCartItems();
  if (!items.length) {
    toast('Your cart is empty. Please add items to proceed.');
    return;
  }

  const subtotalPkr = items.reduce((sum, { p, qty }) => sum + (p.price * qty), 0);
  const totalDisplay = 'Rs. ' + subtotalPkr.toLocaleString('en-PK') + ' PKR';
  const lines = items.map(({ p, qty }, i) => `${i + 1}. ${p.name} (${p.duration}, ${p.access} Access) — Qty: ${qty} — Rs. ${(p.price * qty).toLocaleString('en-PK')}`).join('\n');

  const paymentInstructions = '💳 Domestic Payment: EasyPaisa / JazzCash / SadaPay / Bank IBFT\n🌍 International Inquiry: USDT / Wise\n\nPlease confirm availability, payment account, and delivery time.';

  trackEvent('begin_checkout', { item_ids: items.map(x => x.p.id), item_count: items.reduce((s, x) => s + x.qty, 0), value: subtotalPkr, currency: 'PKR', destination: 'whatsapp' });

  openWhatsApp(waLink(`Hello AI Tool Gems 👋\n\nI want to place an order for my cart:\n\n${lines}\n\n💎 Total: ${totalDisplay}\n\n${paymentInstructions}`));
}

function showSuggestions(q) {
  const box = $('#suggestions');
  if (!box) return;
  if (!q.trim()) {
    box.classList.remove('show');
    return;
  }
  const hits = products.filter(p => [p.name, p.category, ...p.intent].join(' ').toLowerCase().includes(q.toLowerCase())).slice(0, 5);
  box.innerHTML = hits.length ? hits.map(p => `
    <button type="button" class="suggestion" data-suggest="${p.id}">
      <img src="${p.logo}" width="128" height="128" loading="lazy" alt="${p.name}">
      <span>${p.name}</span>
      <small>${p.commercialStatus === 'DIRECTORY_ONLY' ? 'Directory' : money(p.price)}</small>
    </button>
  `).join('') : `
    <div class="suggestion"><span>No matching tools found</span></div>
  `;
  box.classList.add('show');
}

function applySearch(q) {
  state.query = q;
  state.limit = products.length;
  const sInput = $('#heroSearch');
  if (sInput) sInput.value = q;
  const box = $('#suggestions');
  if (box) box.classList.remove('show');
  renderProducts();
  const prodSec = $('#products');
  if (prodSec) prodSec.scrollIntoView({ behavior: 'smooth' });
}

function renderCompare() {
  const ps = state.compare.map(id => products.find(p => p.id === id));
  const content = $('#compareContent');
  if (!content) return;
  content.innerHTML = ps.length < 2 ? `
    <div class="cart-empty">
      <img src="assets/logo-transparent.webp" width="1024" height="1024" loading="lazy" class="empty-state-logo" alt="">
      <h3>Select one more tool</h3>
      <p>Select 2 or 3 products to compare features and prices side by side.</p>
    </div>
  ` : `
    <table class="compare-table">
      <thead>
        <tr>
          <th></th>
          ${ps.map(p => `<th><img src="${p.logo}" width="128" height="128" alt="">${p.name}</th>`).join('')}
        </tr>
      </thead>
      <tbody>
        ${[
          ['Price', p => p.commercialStatus === 'DIRECTORY_ONLY' ? 'Directory Profile' : money(p.price)],
          ['Duration', p => p.commercialStatus === 'DIRECTORY_ONLY' ? 'Reference' : p.duration],
          ['Access Type', p => p.commercialStatus === 'DIRECTORY_ONLY' ? 'Reference Profile' : p.access],
          ['Delivery', p => p.commercialStatus === 'DIRECTORY_ONLY' ? 'Reference Profile' : p.delivery],
          ['Warranty', p => p.commercialStatus === 'DIRECTORY_ONLY' ? 'Reference Profile' : p.warranty],
          ['Best For', p => p.bestFor.join(', ')]
        ].map(r => `
          <tr>
            <td>${r[0]}</td>
            ${ps.map(p => `<td>${r[1](p)}</td>`).join('')}
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
  openLayer($('#compareDrawer'));
}

/* --------------------------------------------------------------------------
   GUIDED FINDER MODAL STEPS
   -------------------------------------------------------------------------- */
function finderStep(step = 1) {
  const root = $('#finderSteps');
  if (!root) return;
  if (step === 1) {
    root.innerHTML = `
      <div class="finder-step">
        <div class="progress"><span style="width:33%"></span></div>
        <div class="eyebrow dark"><span></span> Step 1 of 3</div>
        <h2 id="finderTitle">What outcome are you pursuing?</h2>
        <p>Choose your primary ambition to get tailored tool matches.</p>
        <div class="finder-choices">
          ${[
            ['video','Create AI Videos'],
            ['image','Generate Visuals & Art'],
            ['writing','Write Copy & Research'],
            ['code','Build Software & Code'],
            ['presentation','Design Presentations'],
            ['voice','Generate Voice & Audio'],
            ['automation','Automate Workflows'],
            ['study','University & Research'],
            ['design','UI/UX & Graphics']
          ].map(x => `
            <button class="finder-choice" data-intent="${x[0]}">
              ${x[1]}
              <small>View top gems</small>
            </button>
          `).join('')}
        </div>
      </div>
    `;
  }
  if (step === 2) {
    root.innerHTML = `
      <div class="finder-step">
        <div class="progress"><span style="width:66%"></span></div>
        <div class="eyebrow dark"><span></span> Step 2 of 3</div>
        <h2 id="finderTitle">What is your budget target?</h2>
        <p>We’ll prioritize tools with the highest verified ROI in your range.</p>
        <div class="finder-choices">
          <button class="finder-choice" data-budget-min="0" data-budget-max="999">Under Rs. 1,000<small>Budget friendly</small></button>
          <button class="finder-choice" data-budget-min="1000" data-budget-max="2500">Rs. 1,000 – 2,500<small>Most popular tier</small></button>
          <button class="finder-choice" data-budget-min="2501" data-budget-max="5000">Rs. 2,500 – 5,000<small>Power creator</small></button>
          <button class="finder-choice" data-budget-min="5001" data-budget-max="999999">Rs. 5,000+<small>Annual &amp; teams</small></button>
        </div>
        <button class="finder-back" type="button" data-finder-back="1">← Change your goal</button>
      </div>
    `;
  }
  if (step === 3) {
    const targetIntent = (state.finder.intent || '').toLowerCase();
    const intentMatch = p => p.intent.some(i => {
      const n = i.toLowerCase();
      return n === targetIntent || n.startsWith(targetIntent) || targetIntent.startsWith(n) || (targetIntent === 'image' && n.startsWith('image'));
    });

    let matches = products.filter(p => intentMatch(p) && p.price >= state.finder.minBudget && p.price <= state.finder.maxBudget).sort((a, b) => a.price - b.price).slice(0, 3);
    let outsideBudget = false;
    if (!matches.length) {
      matches = products.filter(intentMatch).sort((a, b) => a.price - b.price).slice(0, 3);
      outsideBudget = matches.length > 0;
    }
    if (!matches.length) {
      root.innerHTML = `
        <div class="finder-step">
          <div class="progress"><span style="width:100%"></span></div>
          <div class="eyebrow dark"><span></span> No matches found</div>
          <h2 id="finderTitle">No matching tools found</h2>
          <p>We could not find a tool matching that specific selection. Explore all verified tools or choose another goal.</p>
          <div style="margin:24px 0;display:flex;gap:12px;justify-content:center;flex-wrap:wrap;">
            <a href="#products" class="light-button" data-close style="text-decoration:none;">Browse all tools</a>
            <button class="finder-back" type="button" data-finder-back="1">Start over</button>
          </div>
        </div>
      `;
      return;
    }
    root.innerHTML = `
      <div class="finder-step">
        <div class="progress"><span style="width:100%"></span></div>
        <div class="eyebrow dark"><span></span> Step 3 of 3 · Recommendation ready</div>
        <h2 id="finderTitle">${outsideBudget ? 'Closest available matches' : 'Your best tool matches'}</h2>
        <p>${outsideBudget ? 'No exact tool is available in that budget. These are the lowest-priced relevant options, shown transparently.' : 'Matched for your objective and exact budget range using the catalog details shown.'}</p>
        <div class="finder-results">
          ${matches.map((p, i) => `
            <a class="finder-result" href="tools/${p.id}/" style="text-decoration:none;display:flex;align-items:center;">
              <img src="${p.logo}" width="128" height="128" loading="lazy" alt="${p.name}">
              <div>
                <small>${outsideBudget ? 'CLOSEST OPTION · ABOVE BUDGET' : (i === 0 ? 'TOP BUDGET MATCH' : 'RECOMMENDED OPTION')}</small>
                <b>${p.name}</b>
                <span>${p.bestFor.join(' · ')} · ${p.duration} · ${p.access} Plan</span>
              </div>
              <strong>${money(p.price)}</strong>
            </a>
          `).join('')}
        </div>
        <button class="finder-back" type="button" data-finder-back="2">← Change your budget</button>
      </div>
    `;
  }
}

const finderPreviewPresets = {
  video: {
    counter: '01 / 04',
    badge: 'Top match · 96% fit',
    id: 'veo',
    name: 'Veo 3 Ultra',
    desc: 'Unlimited cinematic video generation with photorealistic physics',
    price: 2100,
    logo: 'assets/product-logos/veo.png'
  },
  image: {
    counter: '02 / 04',
    badge: 'Top match · 98% fit',
    id: 'leonardo',
    name: 'Leonardo AI Essential',
    desc: 'Production-ready digital art, photorealistic assets & visuals',
    price: 1900,
    logo: 'assets/product-logos/leonardo.png'
  },
  writing: {
    counter: '03 / 04',
    badge: 'Top match · 99% fit',
    id: 'chatgpt',
    name: 'ChatGPT Plus',
    desc: 'Advanced research, coding, writing and creative assistance',
    price: 2300,
    logo: 'assets/product-logos/chatgpt.png'
  },
  code: {
    counter: '04 / 04',
    badge: 'Top match · 95% fit',
    id: 'lovable',
    name: 'Lovable Pro',
    desc: 'Build, design and ship full-stack web applications and MVPs',
    price: 1600,
    logo: 'assets/product-logos/lovable.png'
  }
};

function updateFinderPreview(intent) {
  const data = finderPreviewPresets[intent] || finderPreviewPresets.video;
  $$('.preview-option').forEach(btn => {
    const selected = btn.dataset.previewIntent === intent;
    btn.classList.toggle('selected', selected);
    btn.setAttribute('aria-pressed', String(selected));
  });
  const counter = $('#previewCounter');
  if (counter) counter.textContent = data.counter;
  const badge = $('#finderMatchBadge');
  if (badge) badge.textContent = data.badge;
  const name = $('#finderMatchName');
  if (name) name.textContent = data.name;
  const desc = $('#finderMatchDesc');
  if (desc) desc.textContent = data.desc;
  const price = $('#finderMatchPrice');
  if (price) price.textContent = money(data.price);
  const logo = $('#finderMatchLogo');
  if (logo) {
    logo.src = data.logo;
    logo.alt = data.name;
  }
  const card = $('#finderMatchCard');
  if (card) {
    card.href = `tools/${data.id}/`;
    card.setAttribute('aria-label', `View recommended ${data.name} details`);
    card.classList.remove('pulse-update');
    void card.offsetWidth;
    card.classList.add('pulse-update');
  }
}

function openFinder() {
  state.finder = { intent: '', minBudget: 0, maxBudget: Infinity };
  trackEvent('finder_start');
  finderStep(1);
  openLayer($('#finderModal'));
}

let toastTimer;
function toast(msg) {
  const t = $('#toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 2200);
}

/* --------------------------------------------------------------------------
   3D INTERACTIVE PHYSICS & TILT ENGINE
   -------------------------------------------------------------------------- */
function init3dHero() {
  const stage = $('#heroVisualStage');
  const gem = $('#hero3dGem');
  const orbits = $('#heroOrbitSystem');
  const cards = $$('.hero-visual .float-card');
  if (!stage || !gem) return;

  let targetX = 0, targetY = 0;
  let currentX = 0, currentY = 0;
  let animationFrame = 0;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function onMouseMove(e) {
    const rect = stage.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    targetX = x * 24; // tilt degrees
    targetY = -y * 24;
    if (!reducedMotion && !animationFrame) animationFrame = requestAnimationFrame(renderHero3d);
  }

  function onMouseLeave() {
    targetX = 0;
    targetY = 0;
    if (!reducedMotion && !animationFrame) animationFrame = requestAnimationFrame(renderHero3d);
  }

  function renderHero3d() {
    currentX += (targetX - currentX) * 0.08;
    currentY += (targetY - currentY) * 0.08;

    if (gem) {
      gem.style.transform = `translateZ(50px) rotateY(${currentX * 0.9}deg) rotateX(${currentY * 0.9}deg)`;
    }
    if (orbits) {
      orbits.style.transform = `translate(-50%, -50%) rotateY(${currentX * 0.4}deg) rotateX(${currentY * 0.4}deg)`;
    }
    cards.forEach(c => {
      const depth = Number(c.dataset.depth || 45);
      c.style.transform = `translate(${currentX * 0.35}px, ${-currentY * 0.35}px) translateZ(${depth}px) rotateY(${currentX * 0.5}deg) rotateX(${currentY * 0.5}deg)`;
    });

    const stillMoving = Math.abs(targetX - currentX) > 0.02 || Math.abs(targetY - currentY) > 0.02;
    animationFrame = stillMoving ? requestAnimationFrame(renderHero3d) : 0;
  }

  stage.addEventListener('mousemove', onMouseMove);
  stage.addEventListener('mouseleave', onMouseLeave);
  if (!reducedMotion && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      const visible = entries[0]?.isIntersecting && !document.hidden;
      if (!visible && animationFrame) {
        cancelAnimationFrame(animationFrame);
        animationFrame = 0;
      }
    }, { threshold: 0.05 });
    observer.observe(stage);
    document.addEventListener('visibilitychange', () => {
      if (document.hidden && animationFrame) {
        cancelAnimationFrame(animationFrame);
        animationFrame = 0;
      }
    });
  }
}

function init3dCards() {
  const grid = $('#productGrid');
  if (!grid) return;

  grid.addEventListener('mousemove', e => {
    const c = e.target.closest('.product-card');
    if (!c) return;
    const rect = c.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const rotateX = ((y - centerY) / centerY) * -10;
    const rotateY = ((x - centerX) / centerX) * 10;

    c.style.setProperty('--rx', `${rotateX.toFixed(2)}deg`);
    c.style.setProperty('--ry', `${rotateY.toFixed(2)}deg`);
    c.style.setProperty('--mx', `${((x / rect.width) * 100).toFixed(1)}%`);
    c.style.setProperty('--my', `${((y / rect.height) * 100).toFixed(1)}%`);
  });

  grid.addEventListener('mouseleave', e => {
    const c = e.target.closest('.product-card');
    if (c) {
      c.style.setProperty('--rx', '0deg');
      c.style.setProperty('--ry', '0deg');
    }
  }, true);
}

/* --------------------------------------------------------------------------
   GLOBAL EVENT DELEGATION
   -------------------------------------------------------------------------- */
document.addEventListener('click', e => {
  const fav = e.target.closest('[data-favorite]');
  if (fav) {
    e.stopPropagation();
    e.preventDefault();
    toggleFavorite(fav.dataset.favorite);
    return;
  }
  const add = e.target.closest('[data-add]');
  if (add) {
    e.stopPropagation();
    addToCart(add.dataset.add);
    return;
  }
  const remove = e.target.closest('[data-remove]');
  if (remove) {
    e.stopPropagation();
    removeFromCart(remove.dataset.remove);
    return;
  }
  const qtyChange = e.target.closest('[data-qty-change]');
  if (qtyChange) {
    e.stopPropagation();
    const id = qtyChange.dataset.qtyChange;
    const delta = parseInt(qtyChange.dataset.delta, 10) || 0;
    updateCartQty(id, delta);
    return;
  }
  const clearBtn = e.target.closest('#clearCartBtn');
  if (clearBtn) {
    e.stopPropagation();
    clearCart();
    return;
  }
  const comp = e.target.closest('[data-compare]');
  if (comp) {
    toggleCompare(comp.dataset.compare);
    return;
  }
  const detail = e.target.closest('[data-detail]');
  if (detail) {
    closeLayers();
    setTimeout(() => openProduct(detail.dataset.detail), 50);
    return;
  }
  const tag = e.target.closest('[data-tag]');
  if (tag) {
    e.preventDefault();
    state.query = tag.dataset.tag;
    state.category = 'All';
    const sInput = $('#heroSearch');
    if (sInput) sInput.value = state.query;
    const activeQ = $('#activeQuery');
    if (activeQ) {
      activeQ.innerHTML = `Filter tag: <b>"${safeCatalogText(state.query)}"</b> <button type="button" id="clearTagFilter" style="margin-left:8px;text-decoration:underline;cursor:pointer;background:none;border:none;color:inherit;font:inherit;">Clear</button>`;
      activeQ.classList.add('show');
    }
    renderProducts();
    const pSec = $('#products');
    if (pSec) pSec.scrollIntoView({ behavior: 'smooth' });
    return;
  }
  if (e.target.closest('#clearTagFilter')) {
    e.preventDefault();
    state.query = '';
    state.category = 'All';
    const sInput = $('#heroSearch');
    if (sInput) sInput.value = '';
    const activeQ = $('#activeQuery');
    if (activeQ) {
      activeQ.innerHTML = '';
      activeQ.classList.remove('show');
    }
    renderProducts();
    return;
  }
  const filter = e.target.closest('[data-filter]');
  if (filter) {
    state.category = filter.dataset.filter;
    state.limit = products.length;
    renderProducts();
    return;
  }

  const cat = e.target.closest('[data-category]');
  if (cat) {
    state.category = cat.dataset.category;
    state.query = '';
    clearSearchField();
    state.limit = products.length;
    renderProducts();
    $('#products').scrollIntoView({ behavior: 'smooth' });
    return;
  }
  const catLink = e.target.closest('[data-category-link]');
  if (catLink) {
    state.category = catLink.dataset.categoryLink;
    state.query = '';
    clearSearchField();
    renderProducts();
    return;
  }
  const query = e.target.closest('[data-query]');
  if (query) {
    applySearch(query.dataset.query);
    return;
  }
  const suggestion = e.target.closest('[data-suggest]');
  if (suggestion) {
    openProduct(suggestion.dataset.suggest);
    $('#suggestions').classList.remove('show');
    return;
  }
  const intent = e.target.closest('[data-intent]');
  if (intent) {
    state.finder.intent = intent.dataset.intent;
    finderStep(2);
    return;
  }
  const budget = e.target.closest('[data-budget-min]');
  if (budget) {
    state.finder.minBudget = Number(budget.dataset.budgetMin);
    state.finder.maxBudget = Number(budget.dataset.budgetMax);
    finderStep(3);
    return;
  }
  const finderBack = e.target.closest('[data-finder-back]');
  if (finderBack) {
    finderStep(Number(finderBack.dataset.finderBack));
    return;
  }
  const order = e.target.closest('[data-order]');
  if (order) {
    orderProduct(order.dataset.order);
    return;
  }
  const previewOpt = e.target.closest('[data-preview-intent]');
  if (previewOpt) {
    updateFinderPreview(previewOpt.dataset.previewIntent);
    return;
  }
  const stepAction = e.target.closest('[data-step-action]');
  if (stepAction) {
    const action = stepAction.dataset.stepAction;
    if (action === 'search') {
      const ps = $('#products');
      if (ps) ps.scrollIntoView({ behavior: 'smooth' });
      if (heroSearch) heroSearch.focus();
    } else if (action === 'cart') {
      openLayer($('#cartDrawer'));
    } else if (action === 'whatsapp') {
      openWhatsApp(waLink('Hello AI Tool Gems 👋\n\nI would like to order an AI tool and have a quick question.'), '_blank');
    } else if (action === 'warranty') {
      toast('✓ Exact delivery time and replacement warranty are shown on every tool');
      const faq = $('#faqList');
      if (faq) faq.scrollIntoView({ behavior: 'smooth' });
    }
    return;
  }
  const orderBundle = e.target.closest('#orderBundleWa');
  if (orderBundle) {
    openWhatsApp(waLink(`Hello AI Tool Gems 👋\n\nI want to order the Creator Stack Power Bundle (4 Tools):\n1. ChatGPT Plus (1 Month, Private) — Rs. 2,300\n2. Canva Pro Edu (1 Year, Invitation) — Rs. 900\n3. CapCut Pro (1 Month, Private) — Rs. 900\n4. ElevenLabs (1 Month, Private) — Rs. 3,300\n\n💎 Bundle Total: Rs. 7,400\n\nPlease confirm availability, the accepted payment route, and activation time.`), '_blank');
    return;
  }
  const wa = e.target.closest('[data-whatsapp]');
  if (wa) {
    e.preventDefault();
    openWhatsApp(waLink('Hello AI Tool Gems, I need assistance choosing a premium AI tool.'), '_blank');
    return;
  }
  if (e.target.closest('[data-open-finder]')) {
    e.preventDefault();
    openFinder();
    return;
  }
  if (e.target.closest('[data-close]') || e.target.id === 'backdrop') {
    closeLayers();
    return;
  }
  if (e.target.id === 'clearQuery') {
    state.query = '';
    clearSearchField();
    renderProducts();
    return;
  }
  if (!e.target.closest('.search-wrap')) {
    const suggestions = $('#suggestions');
    if (suggestions) suggestions.classList.remove('show');
  }
});

/* Search listeners */
const heroSearch = $('#heroSearch');
if (heroSearch) {
  heroSearch.addEventListener('input', e => showSuggestions(e.target.value));
  heroSearch.addEventListener('keydown', e => {
    if (e.key === 'Enter') applySearch(e.target.value);
    if (e.key === 'Escape') $('#suggestions').classList.remove('show');
  });
}

const openSearch = $('#openSearch');
if (openSearch && heroSearch) {
  openSearch.onclick = () => {
    heroSearch.focus();
    heroSearch.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };
}

document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault();
    if (heroSearch) {
      heroSearch.focus();
      heroSearch.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }
  if (e.key === 'Escape') {
    closeLayers();
    const mobNav = $('#mobileNav');
    if (mobNav) mobNav.classList.remove('show');
    const menuBtn = $('#menuButton');
    if (menuBtn) menuBtn.setAttribute('aria-expanded', 'false');
  }
  if ((e.key === 'Enter' || e.key === ' ') && e.target.matches('[role="button"][tabindex="0"]')) {
    e.preventDefault();
    e.target.click();
  }

  const openLayerEl = $('.drawer.open, .modal.open');
  if (e.key === 'Tab' && openLayerEl) {
    const focusable = [...openLayerEl.querySelectorAll('button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), [tabindex="0"]')];
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }
});

const openCart = $('#openCart');
const mobileCart = $('#mobileCart');
if (openCart) openCart.onclick = () => openLayer($('#cartDrawer'));
if (mobileCart) mobileCart.onclick = () => openLayer($('#cartDrawer'));

const checkoutWA = $('#checkoutWhatsApp');
if (checkoutWA) checkoutWA.onclick = checkout;

const openComp = $('#openCompare');
if (openComp) openComp.onclick = renderCompare;

const sortSel = $('#sortSelect');
if (sortSel) sortSel.onchange = renderProducts;

const filterTog = $('#filterToggle');
if (filterTog) {
  filterTog.onclick = () => {
    const row = $('#filterRow');
    if (row) {
      row.classList.toggle('closed');
      filterTog.setAttribute('aria-expanded', String(!row.classList.contains('closed')));
    }
  };
}

const clearFilt = $('#clearFilters');
if (clearFilt) {
  clearFilt.onclick = () => {
    state.category = 'All';
    state.query = '';
    clearSearchField();
    renderProducts();
  };
}

const menuBtn = $('#menuButton');
if (menuBtn) {
  menuBtn.setAttribute('aria-expanded', 'false');
  menuBtn.setAttribute('aria-controls', 'mobileNav');
  menuBtn.onclick = () => {
    const mobNav = $('#mobileNav');
    if (mobNav) {
      const isOpen = mobNav.classList.toggle('show');
      menuBtn.setAttribute('aria-expanded', String(isOpen));
    }
  };
}

const mobileNav = $('#mobileNav');
if (mobileNav) {
  mobileNav.addEventListener('click', e => {
    if (!e.target.closest('a')) return;
    mobileNav.classList.remove('show');
    if (menuBtn) menuBtn.setAttribute('aria-expanded', 'false');
  });
}

const footerCompare = $('#footerCompare');
if (footerCompare) {
  footerCompare.addEventListener('click', e => {
    e.preventDefault();
    if (state.compare.length >= 2) {
      renderCompare();
    } else {
      $('#products')?.scrollIntoView({ behavior: 'smooth' });
      toast('Select 2 or 3 + buttons on product cards to compare');
    }
  });
}

const addBundleBtn = $('#addBundle');
if (addBundleBtn) {
  addBundleBtn.onclick = () => {
    const bundleIds = ['chatgpt', 'canva', 'capcut', 'elevenlabs'];
    if (bundleIds.every(id => state.cart.includes(id))) {
      openLayer($('#cartDrawer'));
      return;
    }
    bundleIds.forEach(id => {
      if (!state.cart.includes(id)) state.cart.push(id);
    });
    updateCart();
    renderProducts();
    toast('4 Creator stack tools added to your cart');
  };
}

/* --------------------------------------------------------------------------
   INITIALIZATION
   -------------------------------------------------------------------------- */
renderCategories();
renderProducts();
updateCart();
updateCompare();

// URL parameter deep-linking support for category, search, and finder
try {
  const urlParams = new URLSearchParams(window.location.search);
  const qParam = urlParams.get('q') || urlParams.get('search');
  const catParam = urlParams.get('category');
  const findParam = urlParams.get('find') || urlParams.get('intent');
  if (catParam) {
    state.category = catParam;
    renderProducts();
  } else if (qParam) {
    state.query = qParam;
    const sInput = $('#heroSearch');
    if (sInput) sInput.value = qParam;
    renderProducts();
  }
  if (findParam) {
    state.finder.intent = findParam.toLowerCase();
    openFinder();
    finderStep(2);
  } else if (window.location.hash === '#finderModal' || window.location.hash === '#finder') {
    openFinder();
  }
} catch (e) {}

// Defer 3D initialization to avoid blocking LCP. Mobile keeps the visual
// centerpiece static so touch scrolling and the first render stay responsive.
const enable3dEffects = !window.matchMedia('(max-width: 768px)').matches;
if (enable3dEffects) {
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      init3dHero();
      init3dCards();
    });
  } else {
    setTimeout(() => {
      init3dHero();
      init3dCards();
    }, 0);
  }
}

// ── Pakistan AI Bundle & Savings Calculator ──
function initBundleCalculator() {
  const container = document.getElementById('calcToolsList');
  if (!container) return;

  const popularBundleIds = ['chatgpt', 'claude', 'canva', 'cursor', 'perplexity', 'allinone', 'elevenlabs', 'gemini', 'capcut', 'adobe', 'leonardo', 'notion', 'nordvpn'];
  const calcTools = products.filter(p => popularBundleIds.includes(p.id));

  let selectedIds = new Set(['chatgpt', 'claude', 'canva']); // default selection

  function renderTools() {
    container.innerHTML = calcTools.map(tool => {
      const isSel = selectedIds.has(tool.id);
      return `
        <label class="calc-tool-item ${isSel ? 'selected' : ''}" data-id="${tool.id}">
          <input type="checkbox" class="calc-checkbox" ${isSel ? 'checked' : ''}>
          <img src="${officialLogos[tool.id] || tool.logo}" width="28" height="28" style="border-radius:6px; object-fit:contain;" alt="${tool.name}">
          <div class="calc-tool-info">
            <b>${tool.name}</b>
            <span>Rs. ${tool.price.toLocaleString()}</span>
          </div>
        </label>
      `;
    }).join('');

    container.querySelectorAll('.calc-tool-item').forEach(el => {
      el.addEventListener('click', (e) => {
        if (e.target.tagName !== 'INPUT') {
          const chk = el.querySelector('input');
          chk.checked = !chk.checked;
        }
        const id = el.dataset.id;
        const isChecked = el.querySelector('input').checked;
        if (isChecked) {
          selectedIds.add(id);
          el.classList.add('selected');
        } else {
          selectedIds.delete(id);
          el.classList.remove('selected');
        }
        updateTotals();
      });
    });
  }

  function updateTotals() {
    const selected = calcTools.filter(p => selectedIds.has(p.id));
    const countEl = document.getElementById('calcCount');
    const offEl = document.getElementById('calcOfficialTotal');
    const ourEl = document.getElementById('calcOurTotal');
    const badgeEl = document.getElementById('calcSavingsBadge');
    const btnEl = document.getElementById('calcWhatsAppBtn');

    if (countEl) countEl.textContent = `${selected.length} tool${selected.length === 1 ? '' : 's'}`;

    const ourTotal = selected.reduce((sum, p) => sum + p.price, 0);
    const offTotal = selected.reduce((sum, p) => sum + (p.oldPrice || (p.price * 1.6)), 0);
    const savings = Math.max(0, offTotal - ourTotal);
    const pct = offTotal > 0 ? Math.round((savings / offTotal) * 100) : 0;

    if (offEl) offEl.textContent = `Rs. ${Math.round(offTotal).toLocaleString()}`;
    if (ourEl) ourEl.textContent = `Rs. ${ourTotal.toLocaleString()}`;

    if (badgeEl) {
      if (selected.length > 0 && savings > 0) {
        badgeEl.style.display = 'block';
        badgeEl.innerHTML = `🎉 You Save Rs. ${Math.round(savings).toLocaleString()} (${pct}% OFF)`;
      } else {
        badgeEl.style.display = 'none';
      }
    }

    if (btnEl) {
      const names = selected.map(p => p.name).join(', ');
      const msg = encodeURIComponent(`Hi AI Tool Gems, I want to order this custom AI bundle:\nTools: ${names}\nTotal Price: Rs. ${ourTotal.toLocaleString()}\nPayment: EasyPaisa / JazzCash`);
      btnEl.href = `https://wa.me/923236715731?text=${msg}`;
    }
  }

  renderTools();
  updateTotals();
}

initBundleCalculator();

function initPaymentDisclosure() {
  const disclosure = document.getElementById('paymentMethodsDisclosure');
  if (!disclosure) return;
  const summary = disclosure.querySelector('.payment-disclosure-summary');
  const hint = disclosure.querySelector('.disclosure-toggle-hint');
  const updateAria = () => {
    const isOpen = disclosure.open;
    if (summary) summary.setAttribute('aria-expanded', String(isOpen));
    if (hint) hint.textContent = isOpen ? 'Collapse ▴' : 'Details ▾';
  };
  disclosure.addEventListener('toggle', updateAria);
  updateAria();
}
initPaymentDisclosure();
syncAllFavorites();



function setCurrency(curr) {
  state.currency = curr;
  try {
    localStorage.setItem('atg-currency', curr);
  } catch (_) {}
  document.querySelectorAll('.currency-btn').forEach(btn => {
    const active = btn.dataset.currency === curr;
    btn.classList.toggle('active', active);
    btn.setAttribute('aria-pressed', active ? 'true' : 'false');
  });
  renderProducts();
  updateCart();
}

function initCurrencySwitcher() {
  document.querySelectorAll('.currency-btn').forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      const curr = btn.dataset.currency;
      if (curr && curr !== state.currency) {
        setCurrency(curr);
      }
    });
  });
  // Sync initial state
  document.querySelectorAll('.currency-btn').forEach(btn => {
    const active = btn.dataset.currency === state.currency;
    btn.classList.toggle('active', active);
    btn.setAttribute('aria-pressed', active ? 'true' : 'false');
  });
}

initCurrencySwitcher();
