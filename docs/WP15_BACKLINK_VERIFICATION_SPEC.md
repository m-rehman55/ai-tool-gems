# WP15: Advanced Backlink Verification & Attribution Specification

**Document Version:** 1.0.0  
**Status:** Approved & Implemented  
**Package:** `backlink_agent.advanced_verifier`  
**Governing Standard:** HERMES Autonomous SEO Operating System  

---

## 1. Scope & Objective

The Advanced Backlink Verifier (`AdvancedBacklinkVerifier`) replaces rudimentary string matching with a resilient, security-hardened DOM inspection engine. It independently verifies whether external web pages carry valid, indexable, and search-engine-crawlable hyperlinks pointing to `aitoolgems.tech` or approved target assets.

---

## 2. Multi-Hop SSRF & Security Firewall

Every network hop performed during backlink auditing must pass rigorous security filtering before any connection or socket is opened:
- **Pre-Flight DNS Resolution:** The host must resolve to a valid IP.
- **Prohibited Subnets (RFC IPv4 & IPv6):**
  - Loopback (`127.0.0.0/8`, `::1`)
  - Private Networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `fc00::/7`, `fe80::/10`)
  - Link-Local (`169.254.0.0/16`)
  - Cloud Metadata Services (`169.254.169.254`, `metadata.google.internal`)
  - Broadcast and Multicast (`224.0.0.0/4`, `255.255.255.255`)
- **Per-Hop Redirect Guard:** Standard redirect handlers are disabled. Every `301`, `302`, `303`, `307`, or `308` redirect response is intercepted, its `Location` header is extracted and sanitized, and the target IP is re-verified before the next socket is opened (up to 5 redirects maximum).
- **Stream Capping:** Response bodies are strictly capped at 2MB (`DEFAULT_MAX_BYTES = 2_097_152`) to prevent denial-of-service memory exhaustion attacks.

---

## 3. DOM & Technical Signal Analysis

### 3.1 Strict Anchor Parsing
The parser inspects all `<a>` tags in the HTML body:
- **`href` Normalization:** Relative URLs (`/tool`, `tools/chatgpt`) are resolved against the source page base URL. Trailing slashes and default ports are normalized.
- **Domain & Path Matching:** The resolved href is compared against the target asset URL.
- **Anchor Text & Context:** Exact anchor text is extracted. Text within a 150-character contextual window surrounding the anchor is preserved for semantic relevance analysis.

### 3.2 Rel Attribute Qualification
The engine parses the `rel` attribute tokens (case-insensitive, whitespace-delimited):
- **`editorial_dofollow`:** No `nofollow`, `ugc`, or `sponsored` tokens present. Conveys full PageRank authority.
- **`editorial_nofollow`:** Contains `nofollow` token, but no `ugc` or `sponsored`.
- **`user_generated_ugc`:** Contains `ugc` token (forum posts, blog comments, directory submissions).
- **`sponsored`:** Contains `sponsored` token (paid placements, affiliate partner tags).
- **`mixed_qualified`:** Combines multiple qualification tokens (e.g. `rel="nofollow ugc"`).

### 3.3 Indexability & Robots Directives
A backlink situated on a page that Google cannot index delivers zero search equity. The verifier checks two layers:
1. **`<meta name="robots" content="...">`:** Scans for `noindex`, `none`, or restrictive indexing directives.
2. **`X-Robots-Tag` HTTP Header:** Inspects HTTP response headers for `noindex`, `none`, or crawler-specific exclusion directives (`googlebot: noindex`).
If either indicates `noindex`, the qualification is downgraded to `source_noindex`, and `is_live_backlink` is marked `False`.

### 3.4 Canonical Tag Alignment
The verifier extracts `<link rel="canonical" href="...">`:
- If the canonical URL points to a different domain or path, the discrepancy is recorded (`canonical_matches_source = False`), flagging potential syndication or duplicate content issues.

### 3.5 Cryptographic Content Hashing
Every audit calculates a deterministic SHA-256 hash of the page context (`source_page_url + final_page_url + actual_anchor_text + rel_tokens + is_indexable`). This fingerprint enables instant change detection during subsequent retention audits.

---

## 4. Qualification Decision Matrix

```
                      +-----------------------------+
                      | Fetch & Multi-Hop SSRF Check |
                      +--------------+--------------+
                                     |
               +---------------------+---------------------+
               | Failed (Timeout / 5xx)                    | Success (HTTP 200)
               v                                           v
      INCONCLUSIVE_TIMEOUT /                     +-----------------------+
    INCONCLUSIVE_SERVER_ERROR                    | Inspect Meta & Header |
                                                 +-----------+-----------+
                                                             |
                                      +----------------------+----------------------+
                                      | Contains "noindex"                          | Indexable
                                      v                                             v
                               SOURCE_NOINDEX                             +--------------------+
                                                                          | Find Target Anchor |
                                                                          +---------+----------+
                                                                                    |
                                                          +-------------------------+-------------------------+
                                                          | Not Found                                         | Found
                                                          v                                                   v
                                                    ANCHOR_MISSING                              +---------------------------+
                                                                                                | Inspect 'rel' Attributes  |
                                                                                                +-------------+-------------+
                                                                                                              |
                                                      +------------------------+---------------------+--------+--------+
                                                      | rel=""                 | rel="nofollow"      | rel="ugc"       | rel="sponsored"
                                                      v                        v                     v                 v
                                              EDITORIAL_DOFOLLOW       EDITORIAL_NOFOLLOW     USER_GENERATED_UGC   SPONSORED
```
