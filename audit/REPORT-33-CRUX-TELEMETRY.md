# REPORT-33: CORE WEB VITALS & CHROME UX REPORT (CrUX) FIELD TELEMETRY

**Project:** AI Tool Gems (`aitoolgems.tech`)  
**Repository:** `m-rehman55/ai-tool-gems`  
**Execution Date:** 2026-11-09T14:20:00Z  
**Primary Engine:** `scripts/crux_telemetry.py`  
**Automated Schedule:** `.github/workflows/crux-weekly-telemetry.yml`  
**Historical Snapshot Storage:** `data/crux_history/`  
**Governing Issue:** ATG-31-003  

---

## 1. EXECUTIVE SUMMARY & FIELD TELEMETRY STATUS

Phase 33 engineered an enterprise-grade, privacy-safe, and cost-conscious real-user monitoring (RUM) telemetry framework for `aitoolgems.tech`.

### Current Field Telemetry Finding

$$\mathbf{DOMAIN \ STATUS: \quad INSUFFICIENT \ FIELD \ DATA \ (EXPECTED \ NEW \ DOMAIN)}$$

- **Origin Tested:** `https://aitoolgems.tech`
- **Google CrUX API Response:** HTTP 404 (`record not found`)
- **Root Cause:** The Google Chrome UX Report (CrUX) database aggregates real-user telemetry exclusively from Chrome users with telemetry sharing enabled over a rolling **28-day window**. Young domains and newly launched websites do not yet meet Google's minimum sample threshold.
- **Architectural Distinction:**
  - **Laboratory (Synthetic) Data:** Lighthouse audits measure simulated single-device loads on high-speed emulation. Lab CLS is **0.000** and Lab LCP is **0.42s–1.08s**.
  - **Field (Real-World) Data:** CrUX captures real-world interactions (INP), latency across Pakistan telecommunications networks (Jazz, Zong, PTCL, Nayatel), and low-tier Android mobile devices. Field Core Web Vitals cannot be claimed as "Passed" until CrUX aggregates sufficient traffic volume.
  - **Zero Score vs Unavailable:** An unavailable CrUX record is **NOT** a failing score or a performance regression; it represents insufficient sample density.

---

## 2. REUSABLE TELEMETRY ARCHITECTURE

The telemetry pipeline is built upon three modular components:

```mermaid
graph LR
    A["GitHub Actions Workflow<br>(Weekly Mondays 05:00 PKT)"] --> B["scripts/crux_telemetry.py"]
    B -->|Query Origin: https://aitoolgems.tech| C["Google CrUX REST API"]
    C -->|HTTP 200 (Field Metrics)| D["Parse LCP, INP, CLS"]
    C -->|HTTP 404 (Insufficient Traffic)| E["Log INSUFFICIENT_FIELD_DATA<br>(No Failure / Exit 0)"]
    D --> F["data/crux_history/crux_snapshot_YYYY-MM-DD.json"]
    E --> F
    F --> G["Deployment Allowlist Verification<br>(scripts/update_deployment_allowlist.py)"]
```

### 2.1 Polling Engine (`scripts/crux_telemetry.py`)
- **API Target:** `https://chromeuxreport.googleapis.com/v1/records:queryRecord`
- **Profiles Evaluated:** `PHONE` and `DESKTOP` form factors queried independently.
- **Metrics Tracked:**
  - Largest Contentful Paint (LCP)
  - Interaction to Next Paint (INP)
  - Cumulative Layout Shift (CLS)
  - First Contentful Paint (FCP)
  - Time to First Byte (TTFB)
- **Error Handling & Resilience:**
  - Bounded exponential backoff on HTTP 429 (Rate-limiting).
  - Explicit mapping of HTTP 404 to `INSUFFICIENT_FIELD_DATA` without crashing.
  - Offline dry-run switch (`--offline-dry-run`) for continuous integration testing without network flakiness.

### 2.2 Historical Storage Schema
Snapshots are persisted in JSON format within `data/crux_history/`:
```json
{
  "timestamp": "2026-11-09T14:12:00Z",
  "origin": "https://aitoolgems.tech",
  "collection_window": "28-day rolling window",
  "profiles": {
    "PHONE": {
      "status": "INSUFFICIENT_FIELD_DATA",
      "http_code": 404,
      "data": null,
      "error": "Origin not found in CrUX dataset. Domain has insufficient real-user traffic to meet minimum 28-day threshold."
    },
    "DESKTOP": {
      "status": "INSUFFICIENT_FIELD_DATA",
      "http_code": 404,
      "data": null,
      "error": "Origin not found in CrUX dataset."
    }
  }
}
```

### 2.3 Automated Workflow (`.github/workflows/crux-weekly-telemetry.yml`)
- **Cadence:** Weekly on Mondays at 00:00 UTC (05:00 PKT).
- **Security:** Ingests `CRUX_API_KEY` or `PAGESPEED_API_KEY` from repository secrets. Zero credentials committed to version control.
- **Artifact Archiving:** Uploads telemetry JSON snapshot as a GitHub Actions build artifact.

---

## 3. UNIT TEST VERIFICATION

The telemetry engine is verified via `tests/test_crux_telemetry.py`:
- `test_query_crux_api_success`: Simulates mock 200 payload and asserts correct extraction of 75th percentile LCP.
- `test_query_crux_api_insufficient_data`: Simulates mock 404 error and asserts graceful mapping to `INSUFFICIENT_FIELD_DATA`.
- `test_save_snapshot`: Validates atomic file writing to snapshot storage.

**Test Execution:** 3/3 tests passing (0.026s).

---

## 4. NEXT MILESTONES & TRANSITION CRITERIA

1. **Traffic Maturation Window:** The weekly workflow will run autonomously. When daily visitor volume crosses Google's ingestion threshold, the workflow will detect the first valid field data and record initial p75 values for LCP and INP.
2. **Transition to Release Certification:** Once valid CrUX data is logged with LCP $\le 2.5\text{s}$, CLS $\le 0.1$, and INP $\le 200\text{ms}$, the Core Web Vitals condition in the Master Progress Register can be formally upgraded from `CONDITIONALLY VERIFIED` to `UNCONDITIONALLY PASS`.

