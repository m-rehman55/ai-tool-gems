# WP16: Advanced Verifier Adversarial Security & Threat Model Report

**Document Version:** 1.0.0  
**Phase:** Phase 4 (Security Adversarial Review)  
**Verification Date:** 2026-11-15  
**Governing Module:** `backlink_agent.advanced_verifier.verifier`, `backlink_agent.security`  

---

## 1. Threat Landscape & Attack Surface

The Advanced Backlink Verifier must fetch untrusted, third-party web pages across the public internet to verify anchor placement. This exposes the system to several attack vectors:
1. **Server-Side Request Forgery (SSRF):** Forcing the agent to query local loopback (`127.0.0.1`), internal intranet subnets (`10.0.0.0/8`, `192.168.0.0/16`), or cloud metadata services (`169.254.169.254`, `metadata.google.internal`) to steal IAM credentials or API tokens.
2. **DNS Rebinding Attacks:** Returning a legitimate public IP during an initial DNS pre-flight check, then resolving to a private internal IP (`127.0.0.1`) when opening the socket.
3. **Decompression Expansion Bombs (Zip Bombs):** Delivering a highly compressed response (e.g. 2MB gzip expanding into 200MB+ in memory) to exhaust RAM and cause Out-Of-Memory (OOM) crashes.
4. **Infinite Redirect Loops:** Causing the worker to hang indefinitely in cyclic `301/302` redirects.
5. **Slowloris / Hang Attacks:** Serving bytes at 1 byte/second to hold worker sockets open indefinitely.

---

## 2. Adversarial Security Controls & Defenses

### 2.1 Multi-Hop SSRF Firewall
- **Scheme Restriction:** Strictly `https://` only. `http://`, `ftp://`, `file://`, and `gopher://` are rejected immediately.
- **Prohibited Subnets Blocked:**
  - IPv4: `0.0.0.0/8`, `10.0.0.0/8`, `100.64.0.0/10` (CGNAT), `127.0.0.0/8` (Loopback), `169.254.0.0/16` (Link-Local / AWS/GCP Metadata), `172.16.0.0/12`, `192.168.0.0/16`, `224.0.0.0/4` (Multicast), `240.0.0.0/4`, `255.255.255.255/32`.
  - IPv6: `::1/128` (Loopback), `fc00::/7` (ULA), `fe80::/10` (Link-Local), `ff00::/8` (Multicast).
  - IPv4-Mapped IPv6: Addressed such as `::ffff:127.0.0.1` and `::ffff:169.254.169.254` are extracted to their underlying IPv4 representations and blocked.
- **Forbidden Hostnames:** `localhost`, `localhost.localdomain`, `metadata.google.internal`, `metadata`, `instance-data`.
- **Per-Hop Redirect Inspection:** Automatic redirects in `urllib` are explicitly disabled. Every intermediate `301/302/303/307/308` redirect is intercepted, and the `Location` header is resolved and sanitized through `validate_and_sanitize_url()` before the next socket is opened.

### 2.2 Decompression & Memory Exhaustion Defenses
- **Network Read Cap (`DEFAULT_MAX_BYTES`):** Capped at 2MB (`2,097,152` bytes). Sockets are closed once 2MB has been read.
- **Decompression Expansion Cap (`DEFAULT_MAX_DECOMPRESSED_BYTES`):** If `Content-Encoding: gzip` or `deflate` is returned, expansion is capped at 4MB (`4,194,304` bytes). Any payload exceeding 4MB decompressed is truncated, neutralizing decompression bomb attacks.

### 2.3 Slowloris & Socket Hang Defenses
- **Socket Timeout (`DEFAULT_TIMEOUT`):** Hard socket timeout of 12.0 seconds enforced on every network hop.
- **Maximum Redirects (`DEFAULT_MAX_REDIRECTS`):** Capped at 5 hops. Exceeding 5 hops breaks out of the loop and fails closed.

---

## 3. Rel Qualification & Attribution Semantics

In alignment with search engine guidelines, raw HTML `rel` tokens are preserved intact while separately calculating qualification:
- `rel=""` (missing or empty) $\to$ `editorial_dofollow` (Standard follow link).
- `rel="nofollow"` $\to$ `editorial_nofollow` (Search engine directive not to pass PageRank).
- `rel="ugc"` $\to$ `user_generated_ugc` (User generated forum/comment placement).
- `rel="sponsored"` $\to$ `sponsored` (Commercial or affiliate placement).
- **Core Standard:** `nofollow`, `ugc`, and `sponsored` placements are **retained as valid brand placements** and marked `is_live_backlink = True`, but categorized under their distinct qualification for granular reporting.
