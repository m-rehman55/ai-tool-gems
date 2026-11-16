#!/usr/bin/env python3
"""
AI TOOL GEMS — Professional Global Footer Builder
--------------------------------------------------
Builds, synchronizes, and validates the canonical professional footer
across every customer-facing HTML page in the repository.

Features:
- Dual-market payment transparency (PK Domestic Rails & International Inquiries)
- Balanced 5-column architecture (Brand, Marketplace, Popular Tools, Trust & Policies, Concierge)
- Support hours & verified independent marketplace trust signals
- 100% relative path resolution (Depth 0, 1, 2) compatible with GitHub Pages & custom domain
- Injects responsive dark-luxury CSS into styles.css, tool-page.css, and guide.css
"""

from __future__ import annotations
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent

# CSS SYSTEM FROM FOOTER_REMEDIATION_PLAN.md
GLOBAL_FOOTER_CSS = """
/* ==========================================================
   AI TOOL GEMS — GLOBAL FOOTER SYSTEM
   Version: 1.0 (Production Remediation)
   ========================================================== */

footer.site-footer,
.site-footer {
  --footer-bg: #0a0d14;
  --footer-surface: #101622;
  --footer-surface-hover: #172235;
  --footer-accent: #00e5ff;
  --footer-green: #22c55e;
  --footer-text: #f8fafc;
  --footer-muted: #a1adbf;
  --footer-border: rgba(148, 163, 184, 0.17);

  position: relative;
  isolation: isolate;
  overflow: hidden;

  display: block;
  width: 100%;
  margin: 0;
  padding: 0;

  background: var(--footer-bg);
  color: var(--footer-text);

  border-top: 1px solid var(--footer-border);

  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
}

.site-footer,
.site-footer * {
  box-sizing: border-box;
}

.footer-shell {
  width: min(100% - 40px, 1440px);
  margin-inline: auto;
  padding: 52px 0 26px;
}

/* PAYMENT & TRUST STRIP */

.footer-payment {
  display: grid;
  grid-template-columns: minmax(200px, 0.85fr) minmax(0, 2fr) auto;
  align-items: center;
  gap: 26px;
  padding: 22px 28px;
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.065), rgba(34, 197, 94, 0.035)), var(--footer-surface);
  border: 1px solid var(--footer-border);
  border-radius: 18px;
  margin-bottom: 48px;
}

.footer-payment-intro h2 {
  font-size: 17px;
  margin: 0 0 8px;
  color: var(--footer-text);
  font-weight: 700;
}

.footer-payment-intro p {
  font-size: 12px;
  line-height: 1.7;
  color: var(--footer-muted);
  margin: 0;
}

.footer-payment-groups {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.footer-payment-group h3 {
  margin: 0 0 10px;
  font-size: 11px;
  letter-spacing: .07em;
  text-transform: uppercase;
  color: var(--footer-muted);
  font-weight: 700;
}

.payment-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  list-style: none;
  margin: 0;
  padding: 0;
}

.payment-badges li {
  padding: 7px 11px;
  border: 1px solid var(--footer-border);
  border-radius: 8px;
  background: rgba(255, 255, 255, .035);
  font-size: 11px;
  font-weight: 650;
  color: var(--footer-text);
  white-space: nowrap;
}

.payment-inquiry li {
  border-color: rgba(234, 179, 8, .35);
  color: #fde047;
}

.footer-payment-policy {
  color: var(--footer-accent);
  font-size: 12px;
  font-weight: 650;
  text-decoration: none;
  white-space: nowrap;
  transition: color .2s ease, transform .2s ease;
}

/* MAIN 5-COLUMN GRID */

.footer-grid {
  display: grid;
  grid-template-columns: 1.35fr 1fr 1fr 1fr 1.1fr;
  gap: 34px;
  align-items: start;
}

/* COLUMN 1: BRAND */

.footer-brand-link {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: var(--footer-text);
  text-decoration: none;
  margin-bottom: 18px;
}

.footer-brand-link img {
  width: 58px;
  height: 58px;
  object-fit: contain;
}

.footer-brand-link span {
  display: grid;
  gap: 4px;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: .025em;
  line-height: 1.1;
}

.footer-brand-link strong {
  color: var(--footer-accent);
}

.footer-brand-link small {
  font-size: 9px;
  letter-spacing: .12em;
  color: var(--footer-muted);
}

.footer-brand > p {
  max-width: 290px;
  color: var(--footer-muted);
  font-size: 13px;
  line-height: 1.85;
  margin: 0 0 18px;
}

.footer-verification {
  display: grid;
  gap: 9px;
  margin-bottom: 16px;
}

.footer-verification span {
  color: var(--footer-muted);
  font-size: 11.5px;
  line-height: 1.6;
}

.footer-verification span::first-letter {
  color: var(--footer-green);
  font-weight: 700;
}

.footer-text-link {
  display: inline-block;
  color: var(--footer-accent);
  font-size: 12px;
  font-weight: 650;
  text-decoration: none;
  transition: color .2s ease, transform .2s ease;
}

/* NAVIGATION COLUMNS */

.footer-column {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 11px;
  min-width: 0;
}

.footer-column h2 {
  color: var(--footer-text);
  font-size: 14px;
  line-height: 1.4;
  font-weight: 750;
  margin: 0 0 7px;
  letter-spacing: .01em;
}

.footer-column > a {
  display: inline-block;
  color: var(--footer-muted);
  font-size: 12.5px;
  line-height: 1.5;
  text-decoration: none;
  transition: color .2s ease, transform .2s ease;
}

.footer-column > a:hover,
.footer-text-link:hover,
.footer-payment-policy:hover {
  color: var(--footer-accent);
  transform: translateX(3px);
}

/* SUPPORT HOURS BOX */

.footer-hours {
  display: grid;
  gap: 6px;
  width: 100%;
  padding: 13px 15px;
  background: var(--footer-surface);
  border: 1px solid var(--footer-border);
  border-radius: 11px;
  margin-top: 9px;
}

.footer-hours strong {
  color: var(--footer-text);
  font-size: 12px;
}

.footer-hours span {
  color: var(--footer-muted);
  font-size: 11px;
  line-height: 1.55;
}

/* BOTTOM BAR */

.footer-bottom {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 14px 25px;
  align-items: center;
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid var(--footer-border);
}

.footer-legal {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.footer-legal a {
  color: var(--footer-muted);
  font-size: 11.5px;
  text-decoration: none;
  transition: color .2s ease;
}

.footer-legal a:hover {
  color: var(--footer-accent);
}

.footer-bottom > p {
  margin: 0;
  color: var(--footer-muted);
  font-size: 11px;
  line-height: 1.7;
}

.footer-bottom > p:first-of-type {
  text-align: right;
}

.footer-disclaimer {
  grid-column: 1 / -1;
  color: var(--footer-muted);
  font-size: 11px;
  line-height: 1.6;
}

/* INTERACTION & ACCESSIBILITY */

.site-footer a:focus-visible {
  outline: 2px solid var(--footer-accent);
  outline-offset: 4px;
  border-radius: 3px;
}

.site-footer a {
  min-height: 24px;
}

.site-footer a:active {
  opacity: .8;
}

/* RESPONSIVE: TABLET */

@media (max-width: 1100px) {
  .footer-payment {
    grid-template-columns: 1fr 2fr;
  }
  .footer-payment-policy {
    grid-column: 1 / -1;
  }
  .footer-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 36px 28px;
  }
  .footer-brand {
    grid-column: span 3;
  }
}

/* RESPONSIVE: SMALL TABLET */

@media (max-width: 760px) {
  .footer-shell {
    width: min(100% - 32px, 600px);
    padding-top: 36px;
  }
  .footer-payment {
    grid-template-columns: 1fr;
    gap: 20px;
    padding: 18px;
    margin-bottom: 36px;
  }
  .footer-payment-groups {
    grid-template-columns: 1fr;
  }
  .footer-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 32px 20px;
  }
  .footer-brand {
    grid-column: span 2;
  }
  .footer-bottom {
    grid-template-columns: 1fr;
    gap: 16px;
    margin-top: 36px;
  }
  .footer-bottom > p:first-of-type {
    text-align: left;
  }
}

/* RESPONSIVE: MOBILE */

@media (max-width: 480px) {
  .footer-shell {
    width: calc(100% - 28px);
    padding-top: 30px;
  }
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 28px;
  }
  .footer-brand {
    grid-column: auto;
  }
  .footer-column {
    gap: 10px;
  }
  .footer-column h2 {
    font-size: 14px;
    margin-bottom: 4px;
  }
  .footer-column > a {
    font-size: 13px;
    min-height: 32px;
    display: flex;
    align-items: center;
  }
  .footer-legal {
    gap: 14px;
  }
  .footer-legal a {
    font-size: 12px;
    min-height: 32px;
    display: inline-flex;
    align-items: center;
  }
  .payment-badges li {
    padding: 7px 10px;
    font-size: 11px;
  }
}

/* REDUCED MOTION */

@media (prefers-reduced-motion: reduce) {
  .site-footer *,
  .site-footer *::before,
  .site-footer *::after {
    scroll-behavior: auto !important;
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
  }
}
"""

CANONICAL_FOOTER_TEMPLATE = """<footer class="site-footer" id="site-footer">
  <div class="footer-shell">

    <!-- PAYMENT AND TRUST STRIP -->
    <section class="footer-payment" aria-labelledby="footer-payment-title">
      <div class="footer-payment-intro">
        <h2 id="footer-payment-title">Payment methods</h2>
        <p>Supported domestic payments and verified international arrangements confirmed via WhatsApp concierge.</p>
      </div>

      <div class="footer-payment-groups">
        <div class="footer-payment-group">
          <h3>Pakistan · Supported</h3>
          <ul class="payment-badges">
            <li>EasyPaisa</li>
            <li>JazzCash</li>
            <li>SadaPay</li>
            <li>NayaPay</li>
            <li>Raast</li>
            <li>Bank IBFT</li>
          </ul>
        </div>

        <div class="footer-payment-group">
          <h3>International · Inquiry only</h3>
          <ul class="payment-badges payment-inquiry">
            <li>Wise</li>
            <li>SWIFT Bank Wire</li>
          </ul>
        </div>
      </div>

      <a class="footer-payment-policy" href="{PREFIX}contact.html">Confirm payment options</a>
    </section>

    <!-- MAIN FOOTER GRID -->
    <div class="footer-grid">

      <!-- COLUMN 1: BRAND -->
      <section class="footer-brand" aria-labelledby="footer-brand-title">
        <a class="footer-brand-link" href="{HOME_LINK}">
          <img src="{PREFIX}assets/brand-logo-light.webp" width="64" height="64" loading="lazy" decoding="async" alt="AI Tool Gems logo">
          <span id="footer-brand-title">
            AI TOOL <strong>GEMS</strong>
            <small>PAKISTAN &amp; WORLDWIDE</small>
          </span>
        </a>

        <p>Discover, compare and access digital subscriptions and AI tools through a transparent assisted marketplace.</p>

        <div class="footer-verification">
          <span>✓ Independent marketplace</span>
          <span>✓ Manual order verification</span>
          <span>✓ Product-specific warranty terms</span>
        </div>

        <a href="{PREFIX}product-verification.html" class="footer-text-link">Our verification process →</a>
      </section>

      <!-- COLUMN 2: MARKETPLACE -->
      <nav class="footer-column" aria-label="Marketplace navigation">
        <h2>Marketplace</h2>
        <a href="{PREFIX}tools/">All 65 AI tools directory</a>
        <a href="{PREFIX}prices/">Dual currency price directory</a>
        <a href="{PREFIX}deals/">Current deals</a>
        <a href="{PREFIX}guides/">Guides &amp; Playbooks</a>
        <a href="{PREFIX}blog/">AI Tech Blog</a>
        <a href="{PREFIX}category/ai-chatbots/">AI Chatbots &amp; Assistants</a>
        <a href="{PREFIX}category/ai-coding/">AI Coding &amp; Dev Tools</a>
        <a href="{PREFIX}category/ai-video/">AI Video &amp; Animation</a>
        <a href="{PREFIX}category/ai-design/">AI Design &amp; Image</a>
        <a href="{PREFIX}category/vpn-security/">VPNs &amp; Cybersecurity</a>
      </nav>

      <!-- COLUMN 3: POPULAR TOOLS -->
      <nav class="footer-column" aria-label="Popular subscriptions">
        <h2>Popular subscriptions</h2>
        <a href="{PREFIX}tools/chatgpt/">ChatGPT Plus</a>
        <a href="{PREFIX}tools/claude/">Claude Pro</a>
        <a href="{PREFIX}tools/gemini/">Gemini Pro</a>
        <a href="{PREFIX}tools/canva/">Canva Pro</a>
        <a href="{PREFIX}tools/capcut/">CapCut Pro</a>
        <a href="{PREFIX}tools/midjourney/">Midjourney</a>
        <a href="{PREFIX}tools/cursor/">Cursor AI</a>
        <a href="{PREFIX}tools/copilot/">GitHub Copilot</a>
        <a href="{PREFIX}tools/elevenlabs/">ElevenLabs</a>
        <a href="{PREFIX}tools/nordvpn/">NordVPN</a>
      </nav>

      <!-- COLUMN 4: TRUST & POLICIES -->
      <nav class="footer-column" aria-label="Trust and policies">
        <h2>Trust &amp; policies</h2>
        <a href="{PREFIX}about.html">About us</a>
        <a href="{PREFIX}how-we-review.html">How we review</a>
        <a href="{PREFIX}how-we-price.html">How we price in PKR</a>
        <a href="{PREFIX}how-we-source.html">How we source accounts</a>
        <a href="{PREFIX}product-verification.html">Product verification</a>
        <a href="{PREFIX}correction-policy.html">Correction policy</a>
        <a href="{PREFIX}policies.html#warranty">Replacement warranty</a>
        <a href="{PREFIX}policies.html#refunds">Refund policy</a>
        <a href="{PREFIX}terms-of-service/">Terms of service</a>
      </nav>

      <!-- COLUMN 5: CUSTOMER CONCIERGE -->
      <section class="footer-column footer-support" aria-labelledby="footer-support-title">
        <h2 id="footer-support-title">Customer concierge</h2>
        <a data-whatsapp="help" href="https://wa.me/923236715731?text=Hello%20AI%20Tool%20Gems,%20I%20need%20assistance%20choosing%20a%20premium%20AI%20tool." target="_blank" rel="noopener nofollow">WhatsApp support</a>
        <a href="https://www.whatsapp.com/channel/0029VbDnEgCHLHQOYpDo5c31" target="_blank" rel="noopener" class="wa-channel-footer-link">🟢 WhatsApp channel</a>
        <a href="https://www.instagram.com/aitoolgemspak/" target="_blank" rel="me noopener">Instagram</a>
        <a href="https://www.tiktok.com/@aitoolgems" target="_blank" rel="me noopener">TikTok</a>
        <a href="https://www.facebook.com/people/AI-Tool-Gems-Pakistan/61594432675562/" target="_blank" rel="me noopener">Facebook</a>
        <a href="https://t.me/aitoolgemspak" target="_blank" rel="me noopener">Telegram channel</a>

        <div class="footer-hours">
          <strong>Support hours</strong>
          <span>09:00 AM – 12:00 AM PKT (Daily)</span>
          <span>Assisted WhatsApp concierge support.</span>
        </div>
      </section>

    </div>

    <!-- BOTTOM BAR -->
    <div class="footer-bottom">
      <div class="footer-legal">
        <a href="{PREFIX}privacy-policy/">Privacy policy</a>
        <a href="{PREFIX}terms-of-service/">Terms of service</a>
        <a href="{PREFIX}sitemap.xml">Sitemap</a>
        <a href="{PREFIX}contact.html">Contact</a>
      </div>

      <p>© 2026 AI Tool Gems Pakistan. All rights reserved.</p>

      <p class="footer-disclaimer">Independent digital marketplace. Third-party trademarks belong to their respective owners. No affiliation or endorsement is implied.</p>
    </div>

  </div>
</footer>"""

EXCLUDED_DIRS = {
    '.git', '.gemini', 'brain', 'node_modules', '.venv',
    'reports', 'test-results', 'audit', 'AI_TOOL_GEMS_COMPETITOR_INTELLIGENCE_2026-11-15',
    'data'
}

EXCLUDED_FILES = {
    'admin.html', '404.html', 'googleb36d12ee905644d9.html',
    'gsc_daily_checklist.html', 'privacy.html', 'terms.html'
}


def render_footer(depth: int, rel_path: str) -> str:
    """Renders the canonical footer markup with exact relative path prefixes."""
    if depth == 0:
        prefix = ""
        home_link = "#top" if rel_path == "index.html" else "./"
    elif depth == 1:
        prefix = "../"
        home_link = "../"
    elif depth == 2:
        prefix = "../../"
        home_link = "../../"
    else:
        prefix = "../" * depth
        home_link = prefix

    return CANONICAL_FOOTER_TEMPLATE.format(PREFIX=prefix, HOME_LINK=home_link)


def update_stylesheets() -> None:
    """Ensures GLOBAL_FOOTER_CSS is properly embedded in styles.css, tool-page.css, and guide.css."""
    sheets = ['styles.css', 'tool-page.css', 'guide.css']
    header_mark = "/* ==========================================================\n   AI TOOL GEMS — GLOBAL FOOTER SYSTEM"

    for s in sheets:
        sheet_path = REPO_ROOT / s
        if not sheet_path.exists():
            continue
        content = sheet_path.read_text(encoding='utf-8')

        # If already contains our global footer system, replace the block
        if header_mark in content:
            idx = content.find(header_mark)
            content = content[:idx].rstrip() + "\n\n" + GLOBAL_FOOTER_CSS.strip() + "\n"
        else:
            content = content.rstrip() + "\n\n" + GLOBAL_FOOTER_CSS.strip() + "\n"

        sheet_path.write_text(content, encoding='utf-8')
        print(f"Updated stylesheet: {s}")


def collect_customer_facing_html_files() -> List[Tuple[Path, str, int]]:
    """Discovers all customer-facing HTML files and calculates relative depths."""
    results = []
    for root, dirs, files in os.walk(REPO_ROOT):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith('.')]
        for f in files:
            if not f.endswith('.html'):
                continue
            if f in EXCLUDED_FILES:
                continue

            full_p = Path(root) / f
            rel_p = str(full_p.relative_to(REPO_ROOT)).replace('\\', '/')

            # Skip snapshot or temp files
            if 'snapshots' in rel_p or 'scratch' in rel_p:
                continue

            depth = len(rel_p.split('/')) - 1
            results.append((full_p, rel_p, depth))

    results.sort(key=lambda x: (x[2], x[1]))
    return results


def apply_footer_to_file(file_path: Path, rel_path: str, depth: int) -> bool:
    """Replaces or injects the canonical footer in a given HTML file."""
    content = file_path.read_text(encoding='utf-8')
    new_footer = render_footer(depth, rel_path)

    footer_regex = re.compile(r'<footer\b[\s\S]*?</footer>', re.IGNORECASE)

    if footer_regex.search(content):
        updated_content = footer_regex.sub(new_footer, content, count=1)
    else:
        # If no footer exists, inject before </main> or before <script src=... or before </body>
        if '</main>' in content:
            # Place after </main>
            parts = content.split('</main>', 1)
            updated_content = parts[0] + '</main>\n  ' + new_footer + parts[1]
        elif '</body>' in content:
            parts = content.split('</body>', 1)
            updated_content = parts[0] + '  ' + new_footer + '\n</body>' + parts[1]
        else:
            updated_content = content + '\n' + new_footer

    if updated_content != content:
        file_path.write_text(updated_content, encoding='utf-8')
        return True
    return False


def main() -> None:
    print("=" * 60)
    print("🛠️  AI TOOL GEMS — Professional Global Footer Builder")
    print("=" * 60)

    # 1. Update stylesheets
    print("\n[Phase 1] Updating CSS Stylesheets...")
    update_stylesheets()

    # 2. Collect target files
    print("\n[Phase 2] Discovering Customer-Facing Pages...")
    files = collect_customer_facing_html_files()
    print(f"Total candidate files found: {len(files)}")

    depth_counts: Dict[int, int] = {}
    for _, _, d in files:
        depth_counts[d] = depth_counts.get(d, 0) + 1
    for d, count in sorted(depth_counts.items()):
        print(f"  • Depth {d}: {count} files")

    # 3. Apply canonical footer
    print("\n[Phase 3] Applying Canonical Footer Across All Pages...")
    modified_count = 0
    for p, rel_p, depth in files:
        changed = apply_footer_to_file(p, rel_p, depth)
        if changed:
            modified_count += 1

    print(f"\n✅ Finished! Modified {modified_count} / {len(files)} HTML files.")
    print("=" * 60)


if __name__ == '__main__':
    main()
