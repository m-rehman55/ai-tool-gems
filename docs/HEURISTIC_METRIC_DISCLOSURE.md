# HEURISTIC METRIC & AUDIT DISCLOSURE POLICY

**Project:** AI Tool Gems (`aitoolgems.tech`)  
**Standard:** Internal Engineering Quality Governance  
**Effective Date:** 2026-11-09  

---

## 1. PURPOSE & PRINCIPLES OF TRANSPARENCY

In compliance with independent audit finding **ATG-31-001**, this document formalizes the operational distinction between **internal algorithmic heuristics** synthesized by our engineering tools and **official external metrics or accreditations** awarded by third parties (such as Google Search Console, W3C, ISO, or Microsoft).

To maintain absolute commercial and technical transparency with users, partners, and search engines, the metrics below are designated as internal benchmarks:

---

## 2. METRIC DEFINITIONS & FORMULAS

### 2.1 AI Overview (AIO) Grounding Score (Current Benchmark: 95.5 / 100)

- **Classification:** **Internal Optimization Heuristic Engine**
- **Generating Module:** `aio_agent` (`python -m aio_agent audit`)
- **Formula:**
  $$\text{AIO Score} = (0.35 \times \text{Extractability}) + (0.35 \times \text{QueryFanOut}) + (0.15 \times \text{SchemaStructure}) + (0.15 \times \text{InformationGain})$$
- **Measurement Criteria:**
  - *Extractability (35%):* HTML tables, bulleted lists, definition terms, concise answers within $\le 300$ characters.
  - *Query Fan-Out (35%):* Coverage of five distinct searcher intents (definition, pricing, alternative comparison, verification, customer review).
  - *Schema Structure (15%):* Presence of valid linked `@graph` JSON-LD entities (`FAQPage`, `HowTo`, `Product`).
  - *Information Gain (15%):* Unique empirical facts, Pakistani local payment rail details, and verified WhatsApp workflow notes.
- **Explicit Disclosure:**
  Google LLC does not publish an external "AIO Score" API. This score measures architectural readiness for retrieval-augmented generation (RAG) and LLM query answering; it is not a guarantee of Google AI Overviews inclusion.

---

### 2.2 Master Website Health Score (Current Benchmark: 99.2 / 100)

- **Classification:** **Internal Engineering Composite Index**
- **Generating Engine:** Master Audit Progress Register (`audit/AUDIT_PROGRESS_REGISTER.md`)
- **Formula:**
  $$\text{Health Score} = \frac{\sum_{i=0}^{30} \text{PhaseScore}_i}{31}$$
  Where each phase represents a normalized 0–100 score across automated QA pass rates, link cleanliness, responsive viewport tests, accessibility audits, and security allowlists.
- **Explicit Disclosure:**
  This score represents an internal engineering composite across 31 continuous audit phases. It does not represent an accredited certification from an external standards body (such as ISO/IEC or W3C).

---

## 3. AUDIT & DASHBOARD IMPLEMENTATION MANDATE

All future automated reports, client-facing dashboards, and pull request summaries referencing these scores must append the clear designation:
> *(Internal Optimization Heuristic Benchmark — Not an official Google rating or external accreditation)*
