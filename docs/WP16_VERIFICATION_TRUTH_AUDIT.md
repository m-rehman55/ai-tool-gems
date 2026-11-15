# WP16: Advanced Backlink Verification Truth Audit

**Document Version:** 1.0.0  
**Phase:** Phase 4 & 5 (Verification Truth Audit)  
**Verification Date:** 2026-11-15  
**Governing Module:** `backlink_agent.advanced_verifier.verifier`  

---

## 1. Objective & Audit Scope

The purpose of this audit is to guarantee that the verification engine independently inspects the real DOM of external source pages and adheres to the cardinal standard:
> **"Only an independently crawled, indexable, live DOM anchor is an earned backlink."**

This document establishes the ground truth classification rules, evidence extraction standards, and security boundaries enforced by `AdvancedBacklinkVerifier`.

---

## 2. Distinction Between Raw Rel Tokens and Editorial Qualification

A common flaw in rudimentary backlink checkers is conflating the absence of a `rel` attribute with proof of editorial quality. In HERMES:

### 2.1 Raw HTML Token Preservation
The verifier preserves the exact tokens declared in the HTML `<a>` tag:
- Example: `<a href="..." rel="nofollow ugc">` $\to$ `rel_tokens = ["nofollow", "ugc"]`
- Example: `<a href="..." rel="sponsored">` $\to$ `rel_tokens = ["sponsored"]`
- Example: `<a href="...">` $\to$ `rel_tokens = []`

### 2.2 Qualification Mapping Logic
Qualification is computed separately and stored in `qualification`:
- **`editorial_dofollow`:** Evaluated when `rel_tokens` is empty and no indexing restrictions exist. Passes full search equity and PageRank.
- **`editorial_nofollow`:** Evaluated when `nofollow` is present without `ugc` or `sponsored`.
- **`user_generated_ugc`:** Evaluated when `ugc` is present (blogs, forums, user submissions).
- **`sponsored`:** Evaluated when `sponsored` is present (partner or paid listings).
- **`mixed_qualified`:** Evaluated when multiple qualification tokens coexist.
- **`source_noindex`:** Evaluated when the page has `<meta name="robots" content="noindex">` or `X-Robots-Tag: noindex`, regardless of anchor presence. `is_live_backlink` is forced to `False`.

---

## 3. Strict Anchor Target Resolution

A page mentioning "AI Tool Gems" in text does NOT constitute a backlink:
1. **Plain Text Mentions:** If the brand name appears in paragraph or heading text without an enclosing `<a href="...">` tag, the verifier records `anchor_found = False`, `qualification = ANCHOR_MISSING`, and `is_live_backlink = False`.
2. **Anchor to Wrong Destination:** If an anchor links to `aitoolgems.tech/unapproved-subpath` or an external domain, the verifier flags `target_matches_approved = False` and `qualification = WRONG_TARGET`.
3. **Relative URL Resolution:** Relative hrefs (`/tools/chatgpt`, `tools/chatgpt`) are resolved against the source page base URL and compared against the canonical target asset.

---

## 4. Decompression Limits & Safe Stream Caps

To prevent denial-of-service memory exhaustion attacks from malicious or misconfigured external web servers:
- **Network Transfer Cap (`self.max_bytes`):** Capped at 2MB (`2,097,152` bytes).
- **Decompressed Expansion Cap (`self.max_decompressed_bytes`):** If the server delivers `Content-Encoding: gzip` or `deflate`, decompressed stream expansion is capped at 4MB (`4,194,304` bytes). Any stream exceeding 4MB is truncated safely, neutralizing decompression zip bombs.
