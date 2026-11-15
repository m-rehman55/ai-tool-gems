-- Migration: 0001_initial.sql
-- Description: AI Tool Gems Backlink Agent Persistent State Schema for Cloudflare D1
-- Created: 2026-11-15

-- 1. Prospects Table (Authoritative registry of off-page targets)
CREATE TABLE IF NOT EXISTS prospects (
    id TEXT PRIMARY KEY,
    prospect_domain TEXT NOT NULL,
    prospect_url TEXT NOT NULL,
    site_type TEXT,
    relevance INTEGER NOT NULL DEFAULT 0,
    eligibility TEXT,
    link_terms TEXT,
    action_status TEXT NOT NULL DEFAULT 'active',
    source_page TEXT,
    target_url TEXT NOT NULL,
    anchor_text TEXT,
    link_status TEXT NOT NULL DEFAULT 'not_live',
    discovered_by_bing TEXT DEFAULT 'no',
    discovered_by_gsc TEXT DEFAULT 'no',
    referral_activity TEXT DEFAULT 'none',
    last_checked TEXT,
    evidence TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Verification Runs Table (Immutable log of all HTTP anchor checks)
CREATE TABLE IF NOT EXISTS verification_runs (
    id TEXT PRIMARY KEY,
    prospect_id TEXT NOT NULL,
    source_page TEXT NOT NULL,
    target_url TEXT NOT NULL,
    classification TEXT NOT NULL,
    http_status INTEGER,
    target_found INTEGER NOT NULL DEFAULT 0,
    actual_anchor_text TEXT,
    rel_tokens TEXT,
    final_url TEXT,
    redirect_chain TEXT,
    source_noindex INTEGER NOT NULL DEFAULT 0,
    canonical_url TEXT,
    response_bytes INTEGER,
    elapsed_seconds REAL,
    error_message TEXT,
    verified_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prospect_id) REFERENCES prospects(id)
);

-- 3. Drafts Table (White-hat submission drafts awaiting owner approval)
CREATE TABLE IF NOT EXISTS drafts (
    id TEXT PRIMARY KEY,
    prospect_id TEXT NOT NULL,
    target_url TEXT NOT NULL,
    proposed_anchor TEXT NOT NULL,
    pitch_copy TEXT NOT NULL,
    content_sha256 TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending_approval',
    approved_at TEXT,
    approved_by TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prospect_id) REFERENCES prospects(id)
);

-- 4. Job Runs Table (Idempotency and lease management for queues/crons)
CREATE TABLE IF NOT EXISTS job_runs (
    id TEXT PRIMARY KEY,
    job_type TEXT NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT,
    error TEXT
);

-- 5. Audit Events Table (Immutable compliance trail)
CREATE TABLE IF NOT EXISTS audit_events (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    actor TEXT NOT NULL,
    entity_id TEXT,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Triggers strictly enforcing append-only immutability on audit_events
CREATE TRIGGER IF NOT EXISTS prevent_audit_update
BEFORE UPDATE ON audit_events
BEGIN
    SELECT RAISE(ABORT, 'audit_events is an immutable append-only ledger: UPDATE prohibited');
END;

CREATE TRIGGER IF NOT EXISTS prevent_audit_delete
BEFORE DELETE ON audit_events
BEGIN
    SELECT RAISE(ABORT, 'audit_events is an immutable append-only ledger: DELETE prohibited');
END;

-- 5b. Telegram Processed Updates Table (Atomic update_id claiming for replay & race protection)
CREATE TABLE IF NOT EXISTS telegram_processed_updates (
    update_id INTEGER PRIMARY KEY,
    chat_id TEXT NOT NULL,
    user_id TEXT,
    command TEXT,
    claimed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 6. Agent Control Table (Kill switch and mode gate)
CREATE TABLE IF NOT EXISTS agent_control (
    control_key TEXT PRIMARY KEY,
    control_value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Default Safety Gates (Fail-Closed)
INSERT OR IGNORE INTO agent_control (control_key, control_value, updated_at) VALUES
('enabled', 'false', CURRENT_TIMESTAMP),
('mode', 'report_only', CURRENT_TIMESTAMP);

-- Seed Data: 15 Existing Baseline Prospects from offpage_authority_tracker.csv
INSERT OR IGNORE INTO prospects (
    id, prospect_domain, prospect_url, site_type, relevance, eligibility, link_terms,
    action_status, source_page, target_url, anchor_text, link_status,
    discovered_by_bing, discovered_by_gsc, referral_activity, last_checked, evidence
) VALUES
('p_github_repo', 'github.com', 'https://github.com/m-rehman55/ai-tool-gems', 'Owned Repo Entity', 95, 'Eligible', 'Repo About and README (nofollow)', 'active', 'https://github.com/m-rehman55/ai-tool-gems', 'https://aitoolgems.tech/', 'aitoolgems.tech', 'live', 'pending', 'pending', 'none', '2026-11-12', 'Repo About URL updated to aitoolgems.tech with 5 topics on 2026-11-12; README.md staged'),
('p_github_profile', 'github.com', 'https://github.com/m-rehman55', 'Owned GitHub Profile', 90, 'Eligible', 'Public profile URL (nofollow)', 'active', 'https://github.com/m-rehman55', 'https://aitoolgems.tech/', 'https://aitoolgems.tech/', 'live', 'pending', 'pending', 'none', '2026-11-12', 'GitHub profile Bio Website Company Pakistan updated on 2026-11-12; README live'),
('p_agentwebmap', 'agentwebmap.com', 'https://agentwebmap.com/submit', 'llms.txt Directory', 92, 'Eligible - Account Required', 'Open llms.txt directory (free account gate)', 'active', 'https://agentwebmap.com/domain/aitoolgems.tech', 'https://aitoolgems.tech/llms.txt', 'aitoolgems.tech', 'live', 'pending', 'pending', 'none', '2026-11-12', 'Verified featured listing 60/100 live 2026-11-12'),
('p_eudk_awesome', 'github.com', 'https://github.com/eudk/awesome-ai-tools', 'Curated GitHub Awesome List', 88, 'Eligible (AI Tool Resources & Directories)', 'PR to README.md under AI Tool Resources & Directories', 'submitted_pending_review', '', 'https://aitoolgems.tech/', 'AI Tool Gems', 'not_live', 'no', 'no', 'none', '2026-11-12', 'PR #944 live'),
('p_saashub', 'saashub.com', 'https://www.saashub.com/services/submit', 'SaaS & Software Directory', 84, 'Eligible', 'Editorial listing (non-reciprocal)', 'needs_owner_account', '', 'https://aitoolgems.tech/', 'AI Tool Gems', 'not_live', 'no', 'no', 'none', '2026-11-12', 'HTTP 200 Submit a Product page verified; owner sign-in needed; login/site-rule'),
('p_startupnetwork', 'startupnetwork.pk', 'https://startupnetwork.pk/sign-up/', 'Pakistan Startup Directory', 82, 'Eligible (Pakistan Regional)', 'Regional startup listing', 'submitted_pending_review', '', 'https://aitoolgems.tech/', 'AI Tool Gems Pakistan', 'not_live', 'no', 'no', 'none', '2026-11-12', 'Submitted listing #2074 2026-11-12; under review'),
('p_pasha', 'startups.pasha.org.pk', 'https://startups.pasha.org.pk/', 'Pakistan Industry Directory', 78, 'Hold - TLS Verification Error', 'PASHA Startup Hub', 'blocked_tls_error', '', 'https://aitoolgems.tech/', '', 'not_live', 'no', 'no', 'none', '2026-11-12', 'HTTPS probe failed SSL cert verify failed on 2026-11-12; hold until fixed'),
('p_altftool', 'altftool.com', 'https://www.altftool.com/ai-tools/submit', 'AI Directory', 68, 'Investigate (Editorial Review)', 'Directory submission form', 'backlog_tier2', '', 'https://aitoolgems.tech/', '', 'not_live', 'no', 'no', 'none', '2026-11-12', 'HTTP 200 verified; confirm non-reciprocal terms before submit'),
('p_hooshware', 'hooshware.net', 'https://hooshware.net/submit', 'AI Directory', 66, 'Investigate (Eligibility Check)', 'AI tool/company directory', 'backlog_tier2', '', 'https://aitoolgems.tech/', '', 'not_live', 'no', 'no', 'none', '2026-11-12', 'HTTP 200 verified; verify directory/aggregator fit'),
('p_devto', 'dev.to', 'https://dev.to/', 'Developer Publication', 85, 'Eligible (Technical Case Study)', 'Editorial article citing /prices/ dataset', 'active', 'https://dev.to/mrehman55/building-a-machine-readable-ai-tools-pricing-index-for-pakistan-csv-json-llmstxt-1d2f', 'https://aitoolgems.tech/prices/', 'Pakistan AI Tools Pricing Index', 'live', 'pending', 'pending', 'none', '2026-11-12', 'Published live 2026-11-12'),
('p_hashnode', 'hashnode.com', 'https://hashnode.com/', 'Developer Publication', 83, 'Eligible (Technical Case Study)', 'Developer post citing /prices/ CSV & JSON', 'draft_ready', '', 'https://aitoolgems.tech/prices/', 'AI Tools Price Index Pakistan', 'not_live', 'no', 'no', 'none', '2026-11-12', 'HTTP 200 verified; developer article draft ready in execution pack'),
('p_futuretools', 'futuretools.io', 'https://futuretools.io/submit-a-tool', 'AI Tool Directory', 35, 'Ineligible (No Aggregators)', 'Single AI tools only', 'rejected', '', 'https://aitoolgems.tech/', '', 'rejected', 'no', 'no', 'none', '2026-11-12', 'HTTP 200; excluded because directory sites are ineligible'),
('p_toolpilot', 'toolpilot.ai', 'https://www.toolpilot.ai/pages/submit-your-ai-tool', 'AI Directory', 25, 'Ineligible (Reciprocal Link Rule)', 'Demands reciprocal link exchange', 'rejected', '', 'https://aitoolgems.tech/', '', 'rejected', 'no', 'no', 'none', '2026-11-12', 'HTTP 200; rejected due to reciprocal backlink requirement'),
('p_aitooldiscovery', 'aitooldiscovery.com', 'https://www.aitooldiscovery.com/submit', 'AI Directory', 25, 'Ineligible (Reciprocal Badge Rule)', 'Demands footer badge backlink', 'rejected', '', 'https://aitoolgems.tech/', '', 'rejected', 'no', 'no', 'none', '2026-11-12', 'HTTP 200; rejected due to reciprocal footer badge rule'),
('p_outerspacee', 'github.com', 'https://github.com/OuterSpacee/awesome-ai-tools', 'GitHub Awesome List', 45, 'Ineligible (Category Mismatch)', 'Must match existing README category', 'rejected', '', 'https://aitoolgems.tech/', '', 'rejected', 'no', 'no', 'none', '2026-11-12', 'Checked README & CONTRIBUTING; no Directory/Pricing category');
