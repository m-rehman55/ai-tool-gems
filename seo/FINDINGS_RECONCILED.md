# FINDINGS RECONCILED

**Timestamp:** 2026-09-30
**Source:** Phases 0-10 audit reports + Level 0 live verification

---

## Reconciliation Summary

| Status | Count |
|--------|-------|
| FIXED | 1 |
| PARTIALLY FIXED | 1 |
| STILL VALID | 28 |
| SUPERSEDED | 0 |
| FALSE POSITIVE | 0 |
| UNKNOWN | 0 |

---

## FIXED

### P2 — Manus orphan page

| Detail | Before | After |
|--------|--------|-------|
| Inbound links | 0 | 9 |
| Status | Orphan | Connected |

**Evidence:** Manus page now has 9 internal links (homepage, products, contact, policies, etc.)

**Note:** Hreflang still broken (en-PK → /tools/manus/ which doesn't exist). Partially fixed only.

---

## PARTIALLY FIXED

### Manus page — hreflang

| Detail | Status |
|--------|--------|
| Internal links | ✅ Fixed |
| Hreflang | ❌ Still broken |
| JP-only product | ⚠️ Verified for JP market |

---

## STILL VALID (28 findings)

### P0 Critical (11)

| Phase | Finding | Status |
|-------|---------|--------|
| 0 | deals hreflang → 404 | STILL VALID |
| 0 | JP thin pages | STILL VALID |
| 0 | Missing canonicals (3) | STILL VALID |
| 1 | 9 broken hreflang targets | STILL VALID |
| 1 | Missing canonicals (3) | STILL VALID |
| 1 | jp/index.html 57.9KB | STILL VALID |
| 1 | No srcset | STILL VALID |
| 3 | No last_verified on any page | STILL VALID |
| 3 | All availability "?" | STILL VALID |
| 6 | PKR/JPY ambiguity | STILL VALID |
| 7 | JP pages thin | STILL VALID |

### P1 High (10)

| Phase | Finding | Status |
|-------|---------|--------|
| 1 | jp/index.html 57.9KB | STILL VALID |
| 3 | JP templates missing 13/20 elements | STILL VALID |
| 4 | Keyword gaps | STILL VALID |
| 5 | No original data assets | STILL VALID |
| 5 | No content decay system | STILL VALID |
| 6 | JP pages under-linked | STILL VALID |
| 6 | JP utility pages thin | STILL VALID |
| 6 | Missing canonical on JP pages | STILL VALID |
| 8 | No GA4 tracking | STILL VALID |
| 8 | No linkable assets as pages | STILL VALID |

### P2 Medium (7)

| Phase | Finding | Status |
|-------|---------|--------|
| 4 | Keyword gaps | STILL VALID |
| 5 | No category pages | STILL VALID |
| 5 | No use-case pages | STILL VALID |
| 6 | No persona pages | STILL VALID |
| 7 | No async/defer scripts | STILL VALID |
| 8 | No backlink/authority system | STILL VALID |
| 10 | No experimentation system | STILL VALID |

---

## SUPERSEDED

None.

## FALSE POSITIVE

None.

## UNKNOWN

None.

---

*Reconciliation complete. All previous findings verified against current live state.*
