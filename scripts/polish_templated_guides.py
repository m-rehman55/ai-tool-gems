import os
import re

GUIDES_DATA = {
    "guides/best-ai-video-generators-pakistan/index.html": {
        "name": "AI Video Generators",
        "action": "pay for AI video generator subscriptions"
    },
    "guides/deepseek-ai-pakistan/index.html": {
        "name": "DeepSeek AI",
        "action": "activate DeepSeek API credits and accounts"
    },
    "guides/elevenlabs-voice-ai-pakistan/index.html": {
        "name": "ElevenLabs Voice AI",
        "action": "buy ElevenLabs voice cloning credits"
    },
    "guides/grammarly-vs-quillbot-pakistan/index.html": {
        "name": "Grammarly and QuillBot",
        "action": "purchase Grammarly Premium or QuillBot"
    },
    "guides/heygen-ai-video-pakistan/index.html": {
        "name": "HeyGen AI Video",
        "action": "purchase HeyGen video credits"
    },
    "guides/lovable-vs-replit-pakistan/index.html": {
        "name": "Lovable and Replit",
        "action": "pay for Lovable or Replit subscriptions"
    },
    "guides/midjourney-alternatives-pakistan/index.html": {
        "name": "Midjourney Alternatives",
        "action": "buy Leonardo AI or Midjourney alternative credits"
    },
    "guides/n8n-automation-pakistan/index.html": {
        "name": "n8n Workflow Automation",
        "action": "activate n8n cloud or workflow automation setups"
    },
    "guides/perplexity-ai-pakistan/index.html": {
        "name": "Perplexity AI",
        "action": "pay for Perplexity Pro"
    },
    "guides/runway-gen3-pakistan/index.html": {
        "name": "Runway Gen-3 Alpha",
        "action": "buy Runway Gen-3 AI video credits"
    },
    "guides/semrush-pro-pakistan/index.html": {
        "name": "SEMrush Pro",
        "action": "activate SEMrush Pro subscriptions"
    }
}

def polish_guide(rel_path, info):
    if not os.path.exists(rel_path):
        print(f"Skipping {rel_path} (not found)")
        return
        
    with open(rel_path, 'r', encoding='utf-8') as f:
        content = f.read()

    name = info["name"]
    action = info["action"]
    
    # 1. Fix Headings
    content = re.sub(
        r'<h2>Understanding Real Costs: [^<]+ &amp; PKR Reality</h2>',
        f'<h2>Understanding Real Costs: Transparent PKR Pricing vs. Foreign FX Fees</h2>',
        content
    )
    content = re.sub(
        r'<h2>Performance Evaluation: [^<]+</h2>',
        f'<h2>Performance Evaluation: Key Benchmarks for {name}</h2>',
        content
    )
    content = re.sub(
        r'<h2>Practical Workflows: [^<]+ for Local Creators</h2>',
        f'<h2>Practical Workflows: Accelerating Production for Local Creators</h2>',
        content
    )
    
    # 2. Fix awkward body sentences
    content = re.sub(
        r'Deploying a verified [^<]+ workflow powers productivity',
        f'Deploying a verified {name} workflow powers productivity',
        content
    )
    content = re.sub(
        r'Before proceeding to [^<]+ or purchasing any digital subscription in Pakistan',
        f'Before purchasing {name} or any digital subscription in Pakistan',
        content
    )
    
    # 3. Fix FAQ Questions (both in HTML and in JSON-LD)
    # Question 1: What is the verified cost...
    content = re.sub(
        r'What is the verified cost of [^<"\\]+ and [^<"\\]+ in Pakistan\?',
        f'What is the verified cost of {name} and related plans in Pakistan?',
        content
    )
    
    # Question 2: How does ... compare
    content = re.sub(
        r'How does [A-Z][a-zA-Z0-9\s-]+ compare for local creators and freelancers\?',
        f'How does {name} compare for local creators and freelancers?',
        content
    )
    
    # Question 3: Can I ... using EasyPaisa or JazzCash?
    content = re.sub(
        r'Can I [A-Z][a-zA-Z0-9\s-]+ using EasyPaisa or JazzCash\?',
        f'Can I {action} using EasyPaisa or JazzCash?',
        content
    )
    
    # Question 4: Why is finding a reliable ... crucial for Pakistani agencies?
    content = re.sub(
        r'Why is finding a reliable [A-Z][a-zA-Z0-9\s-]+ crucial for Pakistani agencies\?',
        f'Why is choosing a verified Pakistan subscription provider crucial for agencies?',
        content
    )

    with open(rel_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Polished: {rel_path}")

def main():
    for rel_path, info in GUIDES_DATA.items():
        polish_guide(rel_path, info)

if __name__ == '__main__':
    main()
