---
description: Run the AIToolGems Keyword Intelligence, Search Console filter engine, and on-page optimization agent.
---

# Keyword & Search Console Intelligence Workflow

Follow these steps to discover untapped Pakistani keywords, inspect Google Search Console performance, and optimize on-page content:

1. **Check GSC Connection or Import CSVs**:
   Run the GSC setup guide to check connection status or import fresh queries:
   ```bash
   python -m keyword_agent gsc-setup
   ```

2. **Run Full Discovery & Audit**:
   Execute the full keyword clustering, RE2 regex generation, cannibalization collision scan, and daily report:
   ```bash
   python -m keyword_agent audit
   ```

3. **Inspect Generated GSC RE2 Regex Library**:
   View copy-ready regular expressions in:
   [GSC_REGEX_LIBRARY.md](file:///d:/Desktop/AI%20Tools%20Aura/docs/GSC_REGEX_LIBRARY.md)

4. **Generate Page-Specific AEO/GEO Brief**:
   To analyze and optimize a specific tool page (e.g., ChatGPT, Canva, Leonardo):
   ```bash
   python -m keyword_agent optimize-page chatgpt
   ```

5. **Verify All Unit Tests**:
   Run the 13-test regression suite:
   ```bash
   python -m unittest discover -s keyword_agent/tests -v
   ```
