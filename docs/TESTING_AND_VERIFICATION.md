# TESTING AND VERIFICATION SPECIFICATION
**Current Baseline**: 165 / 165 Passing Tests (100% Green)  

---

## 1. Test Suite Directory

| Test Suite | Directory | Test Count | Scope & Coverage |
| :--- | :--- | :--- | :--- |
| **Integrity & Regressions** | `tests/test_integrity_and_regressions.py` | 23 | Breadcrumbs, contracts, ads.txt, no exposed API secrets, order toast absence, pricing clarity. |
| **Link Graph & Anchors** | `tests/test_link_graph.py` | 7 | Fragment anchors, internal link graph completeness, orphan page detection, sitemap parity. |
| **UI Interactions & A11y** | `tests/test_ui_interactions.py` | 13 | Viewport overflows, focus traps, WhatsApp buttons, 3D hero stage, modal accessibility. |
| **Auto Blog Safeguards** | `tests/test_auto_blog_publisher.py` | 7 | Title/meta bounds, slug regex, fail-closed approval, payment rail checks, sitemap XML valid. |
| **Japan Safeguards** | `tests/test_japan_safeguards.py` | 3 | Zero Japan tokens in candidate queues, scope guard blocking, sitemap excluding foreign routes. |
| **AIO Agent Suite** | `aio_agent/tests/test_aio_agent.py` | 5 | Grounding scorer, extractability index, 5-branch query fan-out coverage, llms.txt sync. |
| **Ping Agent Suite** | `ping_agent/tests/test_ping_agent.py` | 6 | Local key file verification, sitemap loc extraction, dry-run dispatch, history logging. |
| **Keyword Agent Suite** | `keyword_agent/tests/` | 25 | RE2 regex compliance, intent mapping, GSC CSV parsing, competitor gap matrix, cluster assignment. |
| **SEO Agent Suite** | `seo-agent/tests/` | 43 | Scope guard, decision engine, ICE-R opportunity ranking, technical auditor, workflow steps. |
| **Marketing Agent Suite**| `marketing_agent/tests/test_agent.py` | 33 | Buffer channels discovery, rate limits, caption disclosures, UTM campaign tracking. |

---

## 2. Test Execution Commands

```bash
# Execute entire 165-test suite in sequence:
python -m unittest discover -s tests -v
python -m unittest discover -s aio_agent/tests -v
python -m unittest discover -s ping_agent/tests -v
python -m unittest discover -s keyword_agent/tests -v
python -m unittest discover -s seo-agent/tests -v
python -m unittest discover -s marketing_agent/tests -v
```

---

## 3. Strict Anti-Fake-Testing Rules

1. Tests must never use mock objects to simulate passing of safety firewalls or scope guards.
2. Every bug fix must be accompanied by a regression test that fails before the fix and passes after.
3. Test assertions must inspect real HTML, real XML, or real network responses.
