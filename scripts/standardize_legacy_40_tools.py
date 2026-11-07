"""Standardize warranty disclosures across the 40 legacy assisted listings."""
import os
import re
from pathlib import Path

LEGACY_TOOLS = [
    'adobe', 'allinone', 'canva', 'capcut', 'chatgpt', 'claude', 'copilot', 'cursor',
    'deepseek', 'elevenlabs', 'figma', 'freepik', 'gamma', 'gemini', 'grammarly',
    'grok', 'heygen', 'kling', 'leonardo', 'linkedin', 'lovable', 'midjourney',
    'n8n', 'netflix', 'nordvpn', 'notion', 'office365', 'perplexity', 'quillbot',
    'replit', 'runway', 'semrush', 'spotify', 'suno', 'surfshark', 'tradingview',
    'turnitin', 'veo', 'windows', 'youtube'
]

def update_policies_page():
    path = Path("policies.html")
    content = path.read_text(encoding="utf-8")
    
    # Target existing warranty section
    target = '<section class="page-section" id="warranty"><h2>Replacement warranty</h2><p>Replacement coverage applies for the period displayed on the product page and begins when access is delivered. Customers should contact support promptly with the product name and a description of the access issue. Coverage is assessed against the plan details confirmed before payment. It does not cover loss caused by sharing credentials, prohibited account changes, misuse, or violating third-party service rules.</p></section>'
    
    replacement = '''<section class="page-section" id="warranty">
      <h2>Assisted access replacement warranty</h2>
      <p>All assisted subscriptions and license access tiers on AI Tool Gems include an <strong>Assisted Access Replacement Warranty</strong> for the period displayed on the product listing (e.g., 7 Days or 30 Days), commencing at the confirmed credential delivery timestamp. If delivered credentials, workspace invitations, or license keys become invalid or experience premature de-activation during the covered warranty window through no fault of the user, AI Tool Gems will provide concierge replacement access or an agreed remedy as detailed below.</p>
      <p><strong>Independent Concierge Boundary:</strong> This warranty is an assisted procurement service commitment provided independently by AI Tool Gems to assist Pakistani professionals without foreign payment cards. It does not constitute an official software warranty, service level agreement (SLA), uptime guarantee, or corporate endorsement from third-party software developers (such as OpenAI, Anthropic, Adobe, Microsoft, or Google). Platform-wide outages, vendor policy changes, or upstream service maintenance are governed by the respective software provider.</p>
      <p><strong>Remedy &amp; Evidence:</strong> Customers must report access issues to our official WhatsApp support (<a href="https://wa.me/923236715731" rel="noopener nofollow">+92 323 6715731</a>) with their order reference and a screenshot of the authentication error. Support evaluates replacement eligibility and issues working replacement credentials or re-invites within 24–48 business hours. If replacement stock is exhausted, customers may choose store credit toward an alternative AI tool or a prorated refund per our refund policy.</p>
      <p><strong>Exclusions:</strong> Replacement coverage does not apply to: (1) credential loss caused by user account tampering (changing recovery email, passwords, or billing settings on shared accounts); (2) platform account termination resulting from user violation of vendor acceptable use policies; or (3) sharing credentials with unauthorized third parties.</p>
    </section>'''

    if target in content:
        content = content.replace(target, replacement)
        path.write_text(content, encoding="utf-8")
        print("Successfully updated policies.html#warranty")
    else:
        print("WARNING: Target warranty section not found in policies.html")

def standardize_tool(slug, dry_run=False):
    fpath = Path("tools") / slug / "index.html"
    if not fpath.exists():
        print(f"Skipping {slug}, not found.")
        return False
        
    html = fpath.read_text(encoding="utf-8", errors="ignore")
    original_html = html
    
    # 1. Determine duration
    dl_dur_m = re.search(r'<dt>Replacement warranty</dt>\s*<dd>(.*?)</dd>', html, re.I)
    if dl_dur_m:
        raw_dur = dl_dur_m.group(1).replace('(Assisted Access)', '').strip()
    else:
        # fallback search
        raw_dur = "30 Days" if slug in ['copilot', 'freepik', 'gemini', 'kling', 'office365', 'spotify', 'suno', 'tradingview', 'turnitin', 'youtube', 'figma', 'gamma', 'n8n', 'notion', 'allinone', 'canva'] else "7 Days"
        
    dur = raw_dur
    
    # 2. Update DL metadata box
    if dl_dur_m:
        old_dl = dl_dur_m.group(0)
        new_dl = f"<dt>Replacement warranty</dt><dd>{dur} (Assisted Access)</dd>"
        html = html.replace(old_dl, new_dl)
        
    # 3. Update Policy note
    old_policy_note_m = re.search(r'<aside class=["\']policy-note["\']>.*?</aside>', html, re.DOTALL)
    if old_policy_note_m:
        old_pn = old_policy_note_m.group(0)
        new_pn = ('<aside class="policy-note"><h2>Clear assisted purchase information</h2>'
                  '<p>AI Tool Gems provides independent payment assistance and concierge access for Pakistani users without foreign payment cards. '
                  'Read our <a href="../../policies.html#access">access-type guide</a>, '
                  '<a href="../../policies.html#warranty">Assisted Access Replacement Warranty</a>, and '
                  '<a href="../../policies.html#refunds">refund policy</a> before ordering. '
                  'For questions, use our <a href="../../contact.html">WhatsApp desk</a> or read '
                  '<a href="../../how-we-review.html">how we review listings</a>.</p></aside>')
        html = html.replace(old_pn, new_pn)

    # 4. Update Why Choose AI Tool Gems bullet
    html = re.sub(
        r'<li>Included <a href=["\'](?:\.\./)*policies\.html#warranty["\']>[^<]*warranty[^<]*</a> &amp; <a href=["\'](?:\.\./)*policies\.html#refunds["\']>refund protection</a></li>',
        '<li>Included <a href="../../policies.html#warranty">Assisted Access Replacement Warranty</a> &amp; <a href="../../policies.html#refunds">refund protection</a></li>',
        html,
        flags=re.I
    )
    
    # 5. Update Key Features warranty bullet if present
    html = re.sub(
        r'<li>Verified <a href=["\'](?:\.\./)*policies\.html#warranty["\']>[^<]*warranty[^<]*</a> included</li>',
        f'<li>Verified <a href="../../policies.html#warranty">{dur} Assisted Access Replacement Warranty</a> included</li>',
        html,
        flags=re.I
    )

    # 6. Standardize FAQ item
    # Look for FAQ item with warranty
    faq_warranty_m = re.search(
        r'(<div class=["\']faq-item["\']>\s*<h3>[^<]*warranty[^<]*\??</h3>\s*<p>)(.*?)(</p>\s*</div>)',
        html,
        flags=re.DOTALL | re.I
    )
    
    std_faq_answer = (
        f"This listing includes an <strong>Assisted Access Replacement Warranty ({dur})</strong>. "
        "If your delivered credentials or access experience invalidation during the covered warranty window, "
        "our WhatsApp desk provides credential replacement or concierge support. This independent service "
        "commitment covers access credentials and does not constitute a software uptime guarantee from the "
        "original developer. Full terms are detailed on our "
        '<a href="../../policies.html#warranty">replacement warranty policy</a>.'
    )
    
    if faq_warranty_m:
        html = html[:faq_warranty_m.start(2)] + std_faq_answer + html[faq_warranty_m.end(2):]
    else:
        # Append before </section> of faq-section if faq-section exists
        faq_sec_m = re.search(r'(<section class=["\']faq-section["\']>.*?)(\s*</section>)', html, re.DOTALL)
        if faq_sec_m:
            faq_item_block = f'''    <div class="faq-item">
      <h3>What warranty comes with this listing?</h3>
      <p>{std_faq_answer}</p>
    </div>'''
            html = html[:faq_sec_m.start(2)] + "\n" + faq_item_block + html[faq_sec_m.start(2):]

    if not dry_run and html != original_html:
        fpath.write_text(html, encoding="utf-8")
        print(f"Standardized {slug} (duration: {dur})")
        return True
    elif dry_run:
        print(f"[DRY-RUN] Would standardize {slug} (duration: {dur})")
        return True
    return False

def main():
    update_policies_page()
    count = 0
    for slug in LEGACY_TOOLS:
        if standardize_tool(slug, dry_run=False):
            count += 1
    print(f"\nCompleted standardization across {count} legacy tools.")

if __name__ == '__main__':
    main()
